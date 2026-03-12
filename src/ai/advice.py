from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.ai.cli_provider import run_cli_json, write_ai_error_log


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
    notes = str(payload.get("notes") or payload.get("primary_reason", "")).strip()[:200]
    return {
        "decision": decision,
        "final_action": decision,
        "quality": quality,
        "confidence": round(confidence, 2),
        "notes": notes,
        "primary_reason": str(payload.get("primary_reason", notes)).strip()[:200],
        "market_interpretation": str(payload.get("market_interpretation", "")).strip()[:200],
        "entry_position_quality": str(payload.get("entry_position_quality", "")).strip()[:50],
        "warnings": payload.get("warnings", []) if isinstance(payload.get("warnings"), list) else [],
        "next_condition": str(payload.get("next_condition", "")).strip()[:200],
    }

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
) -> dict[str, Any] | None:
    provider_name = str(provider or "api").strip().lower()

    if provider_name == "cli":
        if not str(cli_command).strip():
            write_ai_error_log(base_dir, "ai_advice_error", "provider=cli\nreason=AI_ADVICE_CLI_COMMAND is empty")
            return None
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
                },
            )
            return _normalize_advice(parsed)
        except Exception as exc:  # noqa: BLE001
            write_ai_error_log(
                base_dir,
                "ai_advice_error",
                "\n".join(
                    [
                        "provider=cli",
                        f"model={model}",
                        f"timeout_sec={timeout_sec}",
                        f"details={type(exc).__name__}: {exc}",
                    ]
                ),
            )
            return None

    if not api_key:
        return None

    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=timeout_sec)
    system_prompt = _load_prompt(base_dir)
    user_payload = {
        "machine": machine_payload,
        "qualitative": qualitative_payload,
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
                    f"provider={provider_name}",
                    f"model={model}",
                    f"timeout_sec={timeout_sec}",
                    f"retry_count={retry_count}",
                    f"last_attempt={attempt}",
                    f"details={last_error}",
                ]
            ),
        )
    return None
