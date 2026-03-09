from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_prompt(base_dir: Path) -> str:
    prompt_path = base_dir / "prompts" / "summary_prompt.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "日本語で簡潔な相場サマリーを作成してください。"


def _fallback_summary(result: dict[str, Any]) -> str:
    ai_advice = result.get("ai_advice")
    ai_line = "AI審査: 機械判定のみ（エラーまたは未実行）"
    if isinstance(ai_advice, dict):
        ai_line = (
            f"AI審査: decision={ai_advice.get('decision')} "
            f"quality={ai_advice.get('quality')} "
            f"confidence={ai_advice.get('confidence')}"
        )
    return (
        f"【結論】bias={result.get('bias')} / phase={result.get('phase')} / confidence={result.get('confidence')}\n"
        f"【機械判定】long={result.get('long_display_score')} short={result.get('short_display_score')} "
        f"gap={result.get('score_gap')} regime={result.get('market_regime')} "
        f"signals=({result.get('signals_4h')},{result.get('signals_1h')},{result.get('signals_15m')})\n"
        f"【環境】funding={result.get('funding_rate')} atr_ratio={result.get('atr_ratio')} volume_ratio={result.get('volume_ratio')}\n"
        f"【Setup】long={result.get('long_setup', {}).get('status')} short={result.get('short_setup', {}).get('status')}\n"
        f"【AI】{ai_line}\n"
        f"【リスク】flags={','.join(result.get('no_trade_flags', [])) or 'none'}"
    )


def build_summary_subject(result: dict[str, Any]) -> str:
    jst_ts = str(result.get("timestamp_jst", ""))[:16].replace("T", " ")
    subject = f"[BTC監視] {jst_ts} {result.get('bias')} / Confidence {result.get('confidence')}"
    ai_advice = result.get("ai_advice")
    if ai_advice is None:
        subject += " ⚠️ AI審査:機械判定のみ"
    return subject


def build_summary_body(
    *,
    api_key: str,
    model: str,
    timeout_sec: int,
    retry_count: int,
    base_dir: Path,
    result_payload: dict[str, Any],
) -> str:
    if not api_key:
        return _fallback_summary(result_payload)

    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=timeout_sec)
    prompt = _load_prompt(base_dir)
    for _ in range(max(1, retry_count)):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(result_payload, ensure_ascii=False)},
                ],
            )
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception:  # noqa: BLE001
            continue
    return _fallback_summary(result_payload)
