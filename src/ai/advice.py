from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.ai.cli_provider import run_cli_json, write_ai_error_log
from src.presentation.sanitize import (
    ADVICE_VARIANT,
    build_display_context,
    sanitize_flag_list,
    sanitize_user_text,
)

AI_AUDIT_VARIANT = "notification_audit_v1"


def _load_prompt(base_dir: Path) -> str:
    prompt_path = base_dir / "prompts" / "advice_prompt.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "JSONのみで decision/quality/confidence/notes を返してください。"


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
        return None
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            chunk = text[start : end + 1]
            try:
                parsed = json.loads(chunk)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return None
        return None


def _normalize_advice(payload: dict[str, Any]) -> dict[str, Any]:
    decision = str(payload.get("decision") or payload.get("final_action", "WAIT")).upper()
    if decision not in {"LONG", "SHORT", "WAIT", "NO_TRADE", "WAIT_FOR_SWEEP", "WAIT_FOR_BREAK_RETEST"}:
        decision = "WAIT"
    quality = str(payload.get("quality", payload.get("entry_position_quality", "C"))).upper()
    if quality not in {"A", "B", "C"}:
        quality = {"GOOD": "A", "OK": "B", "BAD": "C"}.get(quality, "C")
    confidence_raw = float(payload.get("confidence", 0.0))
    confidence = confidence_raw / 100.0 if confidence_raw > 1 else confidence_raw
    confidence = max(0.0, min(1.0, confidence))
    notes = sanitize_user_text(payload.get("notes") or payload.get("primary_reason", ""))[:200]
    primary_reason = sanitize_user_text(payload.get("primary_reason", notes))[:200]
    market_interpretation = sanitize_user_text(payload.get("market_interpretation", ""))[:200]
    next_condition = sanitize_user_text(payload.get("next_condition", ""))[:200]
    warnings = sanitize_flag_list(payload.get("warnings", []) if isinstance(payload.get("warnings"), list) else [])
    verdict = str(payload.get("verdict", "")).strip().lower()
    if verdict not in {"appropriate", "borderline", "likely_noise"}:
        if decision in {"LONG", "SHORT"} and quality in {"A", "B"} and confidence >= 0.65:
            verdict = "appropriate"
        elif decision in {"WAIT", "NO_TRADE", "WAIT_FOR_SWEEP", "WAIT_FOR_BREAK_RETEST"}:
            verdict = "borderline"
        else:
            verdict = "likely_noise"
    agreement = str(payload.get("agreement", "")).strip().lower()
    if agreement not in {"agree", "caution", "disagree"}:
        if verdict == "appropriate":
            agreement = "agree"
        elif verdict == "borderline":
            agreement = "caution"
        else:
            agreement = "disagree"
    reason = sanitize_user_text(payload.get("reason") or primary_reason or notes)[:200]
    unique_risks = sanitize_flag_list(
        payload.get("unique_risks", []) if isinstance(payload.get("unique_risks"), list) else []
    )
    next_review_focus = sanitize_user_text(payload.get("next_review_focus", next_condition))[:200]
    return {
        "verdict": verdict,
        "agreement": agreement,
        "reason": reason,
        "unique_risks": unique_risks,
        "next_review_focus": next_review_focus,
        "audit_variant": AI_AUDIT_VARIANT,
        "decision": decision,
        "final_action": decision,
        "quality": quality,
        "confidence": round(confidence, 2),
        "notes": notes,
        "primary_reason": primary_reason,
        "market_interpretation": market_interpretation,
        "entry_position_quality": str(payload.get("entry_position_quality", "")).strip()[:50],
        "warnings": warnings,
        "next_condition": next_condition,
        "advice_variant": ADVICE_VARIANT,
    }


def _request_ai_advice_via_api(
    *,
    api_key: str,
    model: str,
    timeout_sec: int,
    retry_count: int,
    base_dir: Path,
    machine_payload: dict[str, Any],
    qualitative_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not api_key:
        return None

    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=timeout_sec)
    system_prompt = _load_prompt(base_dir)
    user_payload = {
        "machine": machine_payload,
        "qualitative": qualitative_payload,
        "display_context": build_display_context(machine_payload),
    }

    last_error: str | None = None
    for attempt in range(1, max(1, retry_count) + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                ],
            )
            content = response.choices[0].message.content or ""
            parsed = _extract_json(content)
            if parsed is None:
                last_error = f"response was not valid JSON: {content[:500]}"
                continue
            return _normalize_advice(parsed)
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"
            continue
    if last_error:
        write_ai_error_log(
            base_dir,
            "ai_advice_error",
            "\n".join(
                [
                    "provider=api",
                    f"model={model}",
                    f"timeout_sec={timeout_sec}",
                    f"retry_count={retry_count}",
                    f"last_attempt={attempt}",
                    f"details={last_error}",
                ]
            ),
        )
    return None


def request_ai_advice(
    *,
    provider: str,
    api_key: str,
    model: str,
    cli_command: str,
    timeout_sec: int,
    retry_count: int,
    base_dir: Path,
    machine_payload: dict[str, Any],
    qualitative_payload: dict[str, Any],
) -> tuple[dict[str, Any] | None, str]:
    provider_name = str(provider or "api").strip().lower()

    if provider_name == "cli":
        if not str(cli_command).strip():
            write_ai_error_log(base_dir, "ai_advice_error", "provider=cli\nreason=AI_ADVICE_CLI_COMMAND is empty")
            api_result = _request_ai_advice_via_api(
                api_key=api_key,
                model=model,
                timeout_sec=timeout_sec,
                retry_count=retry_count,
                base_dir=base_dir,
                machine_payload=machine_payload,
                qualitative_payload=qualitative_payload,
            )
            return api_result, "api" if api_result is not None else "cli"
        last_error: str | None = None
        for attempt in range(1, max(1, retry_count) + 1):
            try:
                parsed = run_cli_json(
                    command=cli_command,
                    timeout_sec=timeout_sec,
                    payload={
                        "task": "ai_advice",
                        "model": model,
                        "system_prompt": _load_prompt(base_dir),
                        "machine": machine_payload,
                        "qualitative": qualitative_payload,
                        "display_context": build_display_context(machine_payload),
                    },
                )
                return _normalize_advice(parsed), "cli"
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}: {exc}"
                continue
        if last_error:
            write_ai_error_log(
                base_dir,
                "ai_advice_error",
                "\n".join(
                    [
                        "provider=cli",
                        f"model={model}",
                        f"timeout_sec={timeout_sec}",
                        f"retry_count={retry_count}",
                        f"last_attempt={attempt}",
                        f"details={last_error}",
                    ]
                ),
            )
        api_result = _request_ai_advice_via_api(
            api_key=api_key,
            model=model,
            timeout_sec=timeout_sec,
            retry_count=retry_count,
            base_dir=base_dir,
            machine_payload=machine_payload,
            qualitative_payload=qualitative_payload,
        )
        return api_result, "api" if api_result is not None else "cli"

    api_result = _request_ai_advice_via_api(
        api_key=api_key,
        model=model,
        timeout_sec=timeout_sec,
        retry_count=retry_count,
        base_dir=base_dir,
        machine_payload=machine_payload,
        qualitative_payload=qualitative_payload,
    )
    return api_result, "api" if api_result is not None else provider_name
