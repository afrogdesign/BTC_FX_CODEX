from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
    decision = str(payload.get("decision", "WAIT")).upper()
    if decision not in {"LONG", "SHORT", "WAIT", "NO_TRADE"}:
        decision = "WAIT"
    quality = str(payload.get("quality", "C")).upper()
    if quality not in {"A", "B", "C"}:
        quality = "C"
    confidence = float(payload.get("confidence", 0.0))
    confidence = max(0.0, min(1.0, confidence))
    notes = str(payload.get("notes", "")).strip()[:200]
    return {
        "decision": decision,
        "quality": quality,
        "confidence": round(confidence, 2),
        "notes": notes,
    }


def request_ai_advice(
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
    }

    for _ in range(max(1, retry_count)):
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
                continue
            return _normalize_advice(parsed)
        except Exception:  # noqa: BLE001
            continue
    return None
