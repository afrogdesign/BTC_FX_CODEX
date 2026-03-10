from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_prompt(base_dir: Path) -> str:
    prompt_path = base_dir / "prompts" / "summary_prompt.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "日本語で簡潔な相場サマリーを作成してください。"


def _label_bias(value: Any) -> str:
    mapping = {
        "long": "ロング寄り",
        "short": "ショート寄り",
        "wait": "様子見",
        "no_trade": "見送り",
    }
    return mapping.get(str(value).lower(), str(value))


def _label_phase(value: Any) -> str:
    mapping = {
        "trend_follow": "トレンド継続を狙う場面",
        "pullback": "押し目・戻り待ちの場面",
        "breakout": "ブレイク狙いの場面",
        "range": "レンジ気味の場面",
        "reversal_risk": "反転に注意したい場面",
        "wait": "様子見の場面",
    }
    return mapping.get(str(value).lower(), str(value))


def _label_signal(value: Any) -> str:
    mapping = {
        "long": "ロング優勢",
        "short": "ショート優勢",
        "wait": "様子見",
    }
    return mapping.get(str(value).lower(), str(value))


def _label_regime(value: Any) -> str:
    mapping = {
        "uptrend": "上昇基調",
        "downtrend": "下降基調",
        "range": "レンジ",
        "volatile": "値動きが荒い状態",
        "transition": "転換帯",
    }
    return mapping.get(str(value).lower(), str(value))


def _label_setup(value: Any) -> str:
    mapping = {
        "ready": "条件がかなり揃っている",
        "watch": "監視したい段階",
        "invalid": "条件不足",
    }
    return mapping.get(str(value).lower(), str(value))


def _label_ai_decision(value: Any) -> str:
    mapping = {
        "LONG": "ロング寄り",
        "SHORT": "ショート寄り",
        "WAIT": "様子見",
        "NO_TRADE": "見送り",
        "WAIT_FOR_SWEEP": "Sweep待ち",
        "WAIT_FOR_BREAK_RETEST": "ブレイク後の押し戻り待ち",
    }
    return mapping.get(str(value).upper(), str(value))


def _label_ai_quality(value: Any) -> str:
    mapping = {
        "A": "強め",
        "B": "中くらい",
        "C": "控えめ",
    }
    return mapping.get(str(value).upper(), str(value))


def _format_flags(flags: list[Any]) -> str:
    if not flags:
        return "大きな注意フラグはありません。"
    mapping = {
        "RR_insufficient": "利益幅に対して損切り幅のバランスが弱めです。",
        "RR_insufficient_long": "ロング側は利益幅が不足気味です。",
        "RR_insufficient_short": "ショート側は利益幅が不足気味です。",
        "Critical_zone_warning": "重要ゾーンの近くで値動きが不安定になりやすいです。",
    }
    parts = [mapping.get(str(flag), str(flag)) for flag in flags]
    return " ".join(parts)


def _fallback_summary(result: dict[str, Any]) -> str:
    ai_advice = result.get("ai_advice")
    ai_line = "AI審査は今回は使わず、機械判定を中心に整理しています。"
    if isinstance(ai_advice, dict):
        ai_line = (
            f"AI審査では {_label_ai_decision(ai_advice.get('decision'))} の見方で、"
            f"強さは {_label_ai_quality(ai_advice.get('quality'))}、"
            f"AI信頼度は {ai_advice.get('confidence')} です。"
        )
        notes = str(ai_advice.get("notes", "")).strip()
        if notes:
            ai_line += f" 補足: {notes}"

    prelabel = result.get("prelabel", "RISKY_ENTRY")
    location_risk = result.get("location_risk")
    long_score = result.get("long_display_score")
    short_score = result.get("short_display_score")
    gap = result.get("score_gap")
    confidence = result.get("confidence")
    funding = result.get("funding_rate")
    atr_ratio = result.get("atr_ratio")
    volume_ratio = result.get("volume_ratio")
    long_setup = _label_setup(result.get("long_setup", {}).get("status"))
    short_setup = _label_setup(result.get("short_setup", {}).get("status"))

    return (
        f"【結論】現在位置の評価は {prelabel} です。位置リスクは {location_risk} で、"
        f"方向感は {_label_bias(result.get('bias'))} です。"
        f"局面は「{_label_phase(result.get('phase'))}」で、信頼度は {confidence} です。\n"
        f"【機械判定】機械判定の点数はロング {long_score}、ショート {short_score} で、差は {gap} です。"
        f"相場環境は「{_label_regime(result.get('market_regime'))}」と見ています。"
        f"時間足ごとの印象は、4時間足が {_label_signal(result.get('signals_4h'))}、"
        f"1時間足が {_label_signal(result.get('signals_1h'))}、"
        f"15分足が {_label_signal(result.get('signals_15m'))} です。\n"
        f"【環境】Funding は {funding}、ATR比は {atr_ratio}、出来高比は {volume_ratio} です。"
        f"ATR比は値動きの荒さ、出来高比は売買の勢いを見る目安です。\n"
        f"【セットアップ】ロング側は「{long_setup}」、ショート側は「{short_setup}」です。\n"
        f"【AI】{ai_line}\n"
        f"【注意点】{_format_flags(result.get('no_trade_flags', []))} "
        f"位置フラグ: {', '.join(result.get('risk_flags', [])) or '特になし'}"
    )


def _write_ai_error_log(base_dir: Path, title: str, details: str) -> None:
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = base_dir / "logs" / "errors" / f"{ts}_{title}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(details, encoding="utf-8")


def build_summary_subject(result: dict[str, Any]) -> str:
    jst_ts = str(result.get("timestamp_jst", ""))[:16].replace("T", " ")
    label = str(result.get("system_label", "")).strip()
    label_prefix = f"[{label}] " if label else ""
    subject = (
        f"{label_prefix}[BTC監視] {jst_ts} {result.get('prelabel', 'RISKY_ENTRY')} / "
        f"{result.get('bias')} / Confidence {result.get('confidence')}"
    )
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
    last_error: str | None = None
    for attempt in range(1, max(1, retry_count) + 1):
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
            last_error = "response content was empty"
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"
            continue
    if last_error:
        _write_ai_error_log(
            base_dir,
            "ai_summary_error",
            "\n".join(
                [
                    f"model={model}",
                    f"timeout_sec={timeout_sec}",
                    f"retry_count={retry_count}",
                    f"last_attempt={attempt}",
                    f"details={last_error}",
                ]
            ),
        )
    return _fallback_summary(result_payload)
