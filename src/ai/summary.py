from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.ai.cli_provider import run_cli_text, write_ai_error_log


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


def _format_price(value: Any) -> str:
    try:
        price = float(value)
    except Exception:  # noqa: BLE001
        return str(value)
    return f"{price:,.2f}"


def _format_pct(value: Any) -> str:
    try:
        pct = float(value)
    except Exception:  # noqa: BLE001
        return str(value)
    return f"{pct:+.4f}%"


def _signal_intro(result: dict[str, Any]) -> str:
    tier = str(result.get("signal_tier", "normal"))
    badge = str(result.get("signal_badge", "")).strip()
    if not badge:
        return ""
    if tier == "strong_ai_confirmed":
        return f"{badge} 機械判定とAI審査が同方向でそろった強い候補です。"
    return f"{badge} 条件がそろい始めた場面です。崩れないかを確認しながら追跡します。"


def _format_zone_summary(name: str, zones: list[dict[str, Any]]) -> str:
    if not zones:
        return f"{name}は特に抽出できていません。"
    parts = []
    for zone in zones[:2]:
        low = _format_price(zone.get("low"))
        high = _format_price(zone.get("high"))
        distance = _format_price(zone.get("distance_from_price"))
        parts.append(f"{low} - {high}（現在値から {distance} ドル）")
    return f"{name}は " + " / ".join(parts) + " です。"


def _format_setup_levels(name: str, setup: dict[str, Any], side: str) -> str:
    if not isinstance(setup, dict):
        return f"{name}は情報不足です。"
    status = _label_setup(setup.get("status"))
    entry_low = _format_price((setup.get("entry_zone") or {}).get("low"))
    entry_high = _format_price((setup.get("entry_zone") or {}).get("high"))
    stop_loss = _format_price(setup.get("stop_loss"))
    tp1 = _format_price(setup.get("tp1"))
    tp2 = _format_price(setup.get("tp2"))
    if side == "long":
        tp_text = f"TP1 {tp1} → TP2 {tp2}"
    else:
        tp_text = f"TP1 {tp1} → TP2 {tp2}"
    return (
        f"{name}は「{status}」で、エントリー帯は {entry_low} - {entry_high}、"
        f"損切り目安は {stop_loss}、利確候補は {tp_text} です。"
    )


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
    current_price = _format_price(result.get("current_price"))
    funding_display = str(result.get("funding_rate_display", "")).strip()
    if not funding_display:
        funding_label = str(result.get("funding_rate_label", "ほぼ中立"))
        funding_pct = _format_pct(result.get("funding_rate_pct", 0.0))
        funding_display = f"{funding_label} ({funding_pct})"
    atr_ratio = result.get("atr_ratio")
    volume_ratio = result.get("volume_ratio")
    long_setup = result.get("long_setup", {})
    short_setup = result.get("short_setup", {})
    support_text = _format_zone_summary("近いサポート帯", result.get("support_zones", []))
    resistance_text = _format_zone_summary("近いレジスタンス帯", result.get("resistance_zones", []))
    signal_intro = _signal_intro(result)

    body = (
        f"【結論】現在位置の評価は {prelabel} です。位置リスクは {location_risk} で、"
        f"いま入る位置としてはまずこの評価を優先します。信頼度は {confidence} です。\n"
        f"【方向感】方向感は {_label_bias(result.get('bias'))} で、局面は「{_label_phase(result.get('phase'))}」です。\n"
        f"【機械判定】機械判定の点数はロング {long_score}、ショート {short_score} で、差は {gap} です。"
        f"相場環境は「{_label_regime(result.get('market_regime'))}」と見ています。"
        f"時間足ごとの印象は、4時間足が {_label_signal(result.get('signals_4h'))}、"
        f"1時間足が {_label_signal(result.get('signals_1h'))}、"
        f"15分足が {_label_signal(result.get('signals_15m'))} です。\n"
        f"【環境】現在価格は {current_price} USDT、Funding は {funding_display}、ATR比は {atr_ratio}、出来高比は {volume_ratio} です。"
        f"ATR比は値動きの荒さ、出来高比は売買の勢いを見る目安です。"
        f"{support_text} {resistance_text}\n"
        f"【セットアップ】{_format_setup_levels('ロング側', long_setup, 'long')} "
        f"{_format_setup_levels('ショート側', short_setup, 'short')}\n"
        f"【AI】{ai_line}\n"
        f"【注意点】{_format_flags(result.get('no_trade_flags', []))} "
        f"位置フラグ: {', '.join(result.get('risk_flags', [])) or '特になし'}"
    )
    if signal_intro:
        return f"{signal_intro}\n{body}"
    return body

def build_summary_subject(result: dict[str, Any]) -> str:
    jst_ts = str(result.get("timestamp_jst", ""))[:16].replace("T", " ")
    label = str(result.get("system_label", "")).strip()
    label_prefix = f"[{label}] " if label else ""
    badge = str(result.get("signal_badge", "")).strip()
    badge_prefix = f"{badge} " if badge else ""
    current_price = _format_price(result.get("current_price"))
    subject = (
        f"{badge_prefix}{label_prefix}[BTC監視] {jst_ts} {result.get('prelabel', 'RISKY_ENTRY')} / "
        f"{result.get('bias')} / {current_price} / Confidence {result.get('confidence')}"
    )
    ai_advice = result.get("ai_advice")
    if ai_advice is None:
        subject += " ⚠️ AI審査:機械判定のみ"
    return subject


def build_summary_body(
    *,
    provider: str,
    api_key: str,
    model: str,
    cli_command: str,
    timeout_sec: int,
    retry_count: int,
    base_dir: Path,
    result_payload: dict[str, Any],
) -> str:
    provider_name = str(provider or "api").strip().lower()

    if provider_name == "cli":
        if not str(cli_command).strip():
            return _fallback_summary(result_payload)
        try:
            content = run_cli_text(
                command=cli_command,
                timeout_sec=timeout_sec,
                payload={
                    "task": "summary",
                    "model": model,
                    "system_prompt": _load_prompt(base_dir),
                    "result_payload": result_payload,
                },
            )
            return content or _fallback_summary(result_payload)
        except Exception as exc:  # noqa: BLE001
            write_ai_error_log(
                base_dir,
                "ai_summary_error",
                "\n".join(
                    [
                        "provider=cli",
                        f"model={model}",
                        f"timeout_sec={timeout_sec}",
                        f"details={type(exc).__name__}: {exc}",
                    ]
                ),
            )
            return _fallback_summary(result_payload)

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
                body = content.strip()
                signal_intro = _signal_intro(result_payload)
                if signal_intro:
                    return f"{signal_intro}\n{body}"
                return body
            last_error = "response content was empty"
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"
            continue
    if last_error:
        write_ai_error_log(
            base_dir,
            "ai_summary_error",
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
    return _fallback_summary(result_payload)
