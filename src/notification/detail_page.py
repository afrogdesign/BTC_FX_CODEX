from __future__ import annotations

import html
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.presentation.sanitize import (
    CONFIDENCE_METRIC_LABELS,
    build_display_context,
    build_notification_context,
    sanitize_flag_list,
    sanitize_user_text,
)


_SETUP_STATUS_LABELS = {
    "ready": "条件付きで検討",
    "watch": "監視継続",
    "invalid": "現状は見送り",
    "none": "未形成",
}

_REGIME_LABELS = {
    "uptrend": "上昇基調",
    "downtrend": "下降基調",
    "range": "レンジ",
    "volatile": "値動きが荒い状態",
    "transition": "転換帯",
}

_PHASE_LABELS = {
    "trend_following": "トレンド継続",
    "pullback": "押し目・戻り待ち",
    "breakout": "ブレイク局面",
    "range": "レンジ局面",
    "reversal_risk": "反転注意",
}

_SIGNAL_LABELS = {
    "long": "ロング優勢",
    "short": "ショート優勢",
    "wait": "様子見",
}


def _format_price(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value or "未記録")


def _format_pct(value: Any) -> str:
    try:
        return f"{float(value):+.4f}%"
    except (TypeError, ValueError):
        return str(value or "未記録")


def _setup_status_label(value: Any) -> str:
    return _SETUP_STATUS_LABELS.get(str(value or "").lower(), "未形成")


def _label_regime(value: Any) -> str:
    return _REGIME_LABELS.get(str(value or "").lower(), str(value or "未記録"))


def _label_phase(value: Any) -> str:
    return _PHASE_LABELS.get(str(value or "").lower(), str(value or "未記録"))


def _label_signal(value: Any) -> str:
    return _SIGNAL_LABELS.get(str(value or "").lower(), str(value or "未記録"))


def _metric_hint(metric_key: str, value: Any) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return "未記録"
    if metric_key == "direction":
        if score >= 80:
            return "かなり強い"
        if score >= 60:
            return "強め"
        if score >= 40:
            return "中くらい"
        return "弱め"
    if metric_key == "execution":
        if score >= 70:
            return "今も入りやすい"
        if score >= 40:
            return "条件つき"
        return "今は入りにくい"
    if score >= 70:
        return "かなり待ち寄り"
    if score >= 40:
        return "待ち優先"
    return "待機圧力は低め"


def _metric_help(metric_key: str) -> str:
    if metric_key == "direction":
        return "相場の向きそのものが、どれだけはっきりしているかを表します。高いほど方向判断に迷いが少ない状態です。"
    if metric_key == "execution":
        return "今この価格で実際に入る条件がどれだけ整っているかを表します。方向が合っていても、ここが低いなら飛びつきは不利です。"
    return "今は待ったほうがよい圧力の強さです。高いほど、方向は見えていてもタイミングはまだという意味になります。"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _status_emoji(status_code: str) -> str:
    return {
        "actionable": "✅",
        "monitor": "👀",
        "attention": "🚨",
        "invalid": "🛑",
        "neutral": "🧭",
    }.get(str(status_code), "🧭")


def _metric_emoji(metric_key: str, score: float) -> str:
    if metric_key == "direction":
        return "🧭" if score >= 40 else "🌫️"
    if metric_key == "execution":
        return "⚡" if score >= 60 else "⛔"
    return "⏸️" if score >= 40 else "🟢"


def _metric_bar_tone(metric_key: str, score: float) -> str:
    if metric_key == "direction":
        return "var(--bar-direction)"
    if metric_key == "execution":
        return "var(--bar-execution)"
    return "var(--bar-wait)"


def _metric_reading_point(metric_key: str, score: float) -> str:
    if metric_key == "direction":
        if score >= 80:
            return "「方向そのもの」には迷いがかなり少ないです。"
        if score >= 60:
            return "方向感は見えており、向きの判断には使えます。"
        return "方向感はまだ弱く、向きの断定は危険です。"
    if metric_key == "execution":
        if score >= 70:
            return "今の価格でも仕掛けやすい側です。"
        if score >= 40:
            return "条件は半分そろい。飛びつきはまだ慎重です。"
        return "方向が合っていても、入る場所としては不利です。"
    if score >= 70:
        return "今は無理に触ると精度が落ちやすい帯です。"
    if score >= 40:
        return "待ち優先で、条件がもう一段ほしい状態です。"
    return "待機圧力は低めで、待ち理由はそこまで強くありません。"


def _sparkline_svg(points: list[tuple[str, float]]) -> str:
    width = 300
    height = 96
    left = 14
    right = 14
    top = 16
    bottom = 26
    usable_w = width - left - right
    usable_h = height - top - bottom
    count = max(len(points), 1)
    step = usable_w / max(count - 1, 1)
    coords: list[tuple[float, float, str, float]] = []
    for idx, (label, raw_score) in enumerate(points):
        score = _clamp(raw_score)
        x = left + idx * step
        y = top + (100.0 - score) / 100.0 * usable_h
        coords.append((x, y, label, score))
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y, _label, _score in coords)
    circles = "".join(
        (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" class="spark-dot" />'
            f'<text x="{x:.1f}" y="{height - 8}" text-anchor="middle" class="spark-label">{html.escape(label)}</text>'
        )
        for x, y, label, _score in coords
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" class="sparkline" aria-label="3指標バランス">'
        '<line x1="14" y1="16" x2="286" y2="16" class="spark-grid" />'
        '<line x1="14" y1="43" x2="286" y2="43" class="spark-grid" />'
        '<line x1="14" y1="70" x2="286" y2="70" class="spark-grid" />'
        f'<polyline points="{polyline}" class="spark-line" />'
        f"{circles}"
        "</svg>"
    )


def _score_compare_rows(result: dict[str, Any]) -> str:
    rows: list[str] = []
    for label, key, tone in (
        ("ロング", "long_display_score", "var(--score-long)"),
        ("ショート", "short_display_score", "var(--score-short)"),
    ):
        score = _clamp(_safe_float(result.get(key)))
        rows.append(
            '<div class="score-row">'
            f'<div class="score-row-head"><span>{html.escape(label)}</span><strong>{score:.0f}</strong></div>'
            '<div class="score-track">'
            f'<div class="score-fill" style="width:{score:.1f}%; background:{tone};"></div>'
            "</div>"
            "</div>"
        )
    return "".join(rows)


def _reason_emoji(reason: str) -> str:
    text = str(reason)
    if "流動性" in text or "Sweep" in text:
        return "🌊"
    if "RR" in text or "利益" in text:
        return "📏"
    if "重要" in text or "ノイズ" in text:
        return "⚠️"
    if "板" in text:
        return "🧱"
    if "Funding" in text:
        return "💸"
    return "🔎"


def _reason_cards_html(reasons: list[str]) -> str:
    cards: list[str] = []
    for reason in reasons:
        cards.append(
            '<div class="reason-card">'
            f'<div class="reason-icon">{html.escape(_reason_emoji(reason))}</div>'
            f'<div class="reason-text">{html.escape(reason)}</div>'
            "</div>"
        )
    return "".join(cards)


def _price_position(value: float, chart_min: float, chart_max: float, left: float, width: float) -> float:
    if chart_max <= chart_min:
        return left + width / 2
    ratio = (value - chart_min) / (chart_max - chart_min)
    ratio = max(0.0, min(1.0, ratio))
    return left + ratio * width


def _price_map_svg(result: dict[str, Any]) -> str:
    current_price = _safe_float(result.get("current_price"))
    support_zones = result.get("support_zones", [])[:3]
    resistance_zones = result.get("resistance_zones", [])[:3]
    values = [current_price]
    for zone in support_zones + resistance_zones:
        values.extend([_safe_float(zone.get("low")), _safe_float(zone.get("high"))])
    chart_min = min(values) if values else 0.0
    chart_max = max(values) if values else 1.0
    padding = max((chart_max - chart_min) * 0.08, 120.0)
    chart_min -= padding
    chart_max += padding

    width = 860
    height = 220
    left = 72
    usable_w = width - left - 40

    zone_elements: list[str] = []
    y_positions = [62, 102, 142]
    for idx, zone in enumerate(resistance_zones):
        low = _safe_float(zone.get("low"))
        high = _safe_float(zone.get("high"))
        x1 = _price_position(low, chart_min, chart_max, left, usable_w)
        x2 = _price_position(high, chart_min, chart_max, left, usable_w)
        y = y_positions[idx]
        zone_elements.append(
            f'<rect x="{x1:.1f}" y="{y}" width="{max(x2 - x1, 6):.1f}" height="20" rx="10" class="zone-resistance" />'
            f'<text x="{x1:.1f}" y="{y - 8}" class="zone-caption">R{idx + 1} {_format_price(low)} - {_format_price(high)}</text>'
        )
    for idx, zone in enumerate(support_zones):
        low = _safe_float(zone.get("low"))
        high = _safe_float(zone.get("high"))
        x1 = _price_position(low, chart_min, chart_max, left, usable_w)
        x2 = _price_position(high, chart_min, chart_max, left, usable_w)
        y = y_positions[idx] + 26
        zone_elements.append(
            f'<rect x="{x1:.1f}" y="{y}" width="{max(x2 - x1, 6):.1f}" height="20" rx="10" class="zone-support" />'
            f'<text x="{x1:.1f}" y="{y + 38}" class="zone-caption">S{idx + 1} {_format_price(low)} - {_format_price(high)}</text>'
        )

    current_x = _price_position(current_price, chart_min, chart_max, left, usable_w)
    ticks: list[str] = []
    for idx in range(5):
        tick_value = chart_min + (chart_max - chart_min) * idx / 4
        tick_x = _price_position(tick_value, chart_min, chart_max, left, usable_w)
        ticks.append(
            f'<line x1="{tick_x:.1f}" y1="26" x2="{tick_x:.1f}" y2="194" class="price-grid" />'
            f'<text x="{tick_x:.1f}" y="212" text-anchor="middle" class="price-axis">{_format_price(tick_value)}</text>'
        )

    return (
        f'<svg viewBox="0 0 {width} {height}" class="price-map" aria-label="価格帯マップ">'
        '<rect x="0" y="0" width="860" height="220" rx="18" class="price-map-bg" />'
        f"{''.join(ticks)}"
        '<line x1="72" y1="110" x2="820" y2="110" class="price-midline" />'
        f"{''.join(zone_elements)}"
        f'<line x1="{current_x:.1f}" y1="24" x2="{current_x:.1f}" y2="188" class="price-current-line" />'
        f'<circle cx="{current_x:.1f}" cy="110" r="8" class="price-current-dot" />'
        f'<text x="{current_x:.1f}" y="20" text-anchor="middle" class="price-current-label">現在値 {_format_price(current_price)}</text>'
        "</svg>"
    )


def _zone_summary(name: str, zones: list[dict[str, Any]]) -> str:
    if not zones:
        return f"{name}: 目立つ価格帯は抽出なし"
    parts: list[str] = []
    for zone in zones[:2]:
        low = _format_price(zone.get("low"))
        high = _format_price(zone.get("high"))
        distance = _format_price(zone.get("distance_from_price"))
        parts.append(f"{low} - {high}（現在値から {distance} ドル）")
    return f"{name}: " + " / ".join(parts)


def _setup_line(result: dict[str, Any], side: str) -> str:
    setup = result.get("long_setup", {}) if side == "long" else result.get("short_setup", {})
    label = "ロング" if side == "long" else "ショート"
    return (
        f"{label}: {_setup_status_label(setup.get('status'))}。"
        f" 再検討帯 {_format_price((setup.get('entry_zone') or {}).get('low'))} - {_format_price((setup.get('entry_zone') or {}).get('high'))}"
        f" / 損切り目安 {_format_price(setup.get('stop_loss'))}"
        f" / TP1 {_format_price(setup.get('tp1'))}"
        f" / TP2 {_format_price(setup.get('tp2'))}"
    )


def _build_wait_reasons(display_context: dict[str, Any], result: dict[str, Any]) -> list[str]:
    reasons = [str(item) for item in display_context.get("wait_reason_labels", []) if str(item).strip()]
    if reasons:
        return reasons
    ai_advice = result.get("ai_advice")
    if isinstance(ai_advice, dict):
        return sanitize_flag_list(ai_advice.get("warnings", []))
    return ["大きな待機理由は出ていません"]


def _raw_mail_text(result: dict[str, Any], display_context: dict[str, Any]) -> str:
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    lines = [
        "【結論】",
        f"方向判断: {display_context.get('direction_label', '')}",
        f"いまの扱い: {display_context.get('action_label', '')}",
        f"{metric_labels['direction']}: {result.get('confidence_direction_shadow', '')}",
        f"{metric_labels['execution']}: {result.get('confidence_execution_shadow', '')}",
        f"{metric_labels['wait']}: {result.get('confidence_wait_shadow', '')}",
        f"位置評価: {display_context.get('entry_quality_label', '')}",
    ]
    return "\n".join(lines)


def build_notification_detail_html(result: dict[str, Any]) -> str:
    display_context = build_display_context(result)
    notification_context = build_notification_context(result)
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    timestamp_jst = str(result.get("timestamp_jst", "")).replace("T", " ")
    subject = str(result.get("summary_subject", "")).strip() or (
        f"[{notification_context.get('status_label', '中立')}] {notification_context.get('execution_label', '見送り')} / "
        f"{display_context.get('direction_compact_label', '中立')}"
    )
    wait_reasons = _build_wait_reasons(display_context, result)
    ai_advice = result.get("ai_advice") if isinstance(result.get("ai_advice"), dict) else {}
    ai_reason = sanitize_user_text(ai_advice.get("primary_reason") or ai_advice.get("notes") or "")
    ai_next = sanitize_user_text(ai_advice.get("next_condition", ""))
    ai_warnings = sanitize_flag_list(ai_advice.get("warnings", []))
    funding_display = str(result.get("funding_rate_display") or "").strip() or f"{result.get('funding_rate_label', 'ほぼ中立')} ({_format_pct(result.get('funding_rate_pct', 0.0))})"
    summary_chips = [
        notification_context.get("status_label", "中立"),
        notification_context.get("execution_label", "見送り"),
        display_context.get("direction_compact_label", "中立"),
        display_context.get("entry_quality_label", "内部評価あり"),
    ]

    def esc(value: Any) -> str:
        return html.escape(str(value or "未記録"))

    def chips_html(items: list[str], class_name: str = "chip") -> str:
        return "".join(f'<span class="{class_name}">{esc(item)}</span>' for item in items if str(item).strip())

    metric_points = [
        ("方向", _clamp(_safe_float(result.get("confidence_direction_shadow")))),
        ("実行", _clamp(_safe_float(result.get("confidence_execution_shadow")))),
        ("待機", _clamp(_safe_float(result.get("confidence_wait_shadow")))),
    ]
    balance_svg = _sparkline_svg(metric_points)

    metric_blocks: list[str] = []
    for key, value in (
        ("direction", result.get("confidence_direction_shadow")),
        ("execution", result.get("confidence_execution_shadow")),
        ("wait", result.get("confidence_wait_shadow")),
    ):
        score = _clamp(_safe_float(value))
        metric_blocks.append(
            '<div class="metric-card">'
            f'<div class="metric-head"><div class="metric-label">{_metric_emoji(key, score)} {esc(metric_labels[key])}</div><div class="metric-value">{score:.1f} / 100</div></div>'
            '<div class="metric-track">'
            f'<div class="metric-fill" style="width:{score:.1f}%; background:{_metric_bar_tone(key, score)};"></div>'
            "</div>"
            f'<div class="metric-hint">意味: {esc(_metric_hint(key, value))}</div>'
            f'<p class="metric-help">{esc(_metric_help(key))}</p>'
            f'<p class="metric-reading"><strong>読むポイント:</strong> {esc(_metric_reading_point(key, score))}</p>'
            "</div>"
        )

    root_cards = [
        ("ステータス", f"{notification_context.get('status_label', '')} / {notification_context.get('status_explanation', '')}"),
        ("執行判断", notification_context.get("execution_label", "")),
        ("現値帯の扱い", notification_context.get("entry_window_label", "")),
        ("有効目安", notification_context.get("validity_label", "")),
        ("方向判断", display_context.get("direction_label", "")),
        ("位置評価", display_context.get("entry_quality_label", "")),
        ("総合判断", _label_signal(result.get("bias"))),
        ("相場環境", _label_regime(result.get("market_regime"))),
        ("局面", _label_phase(result.get("phase"))),
        (
            "時間軸",
            f"4時間足 {_label_signal(result.get('signals_4h'))} / 1時間足 {_label_signal(result.get('signals_1h'))} / 15分足 {_label_signal(result.get('signals_15m'))}",
        ),
        (
            "スコア差",
            f"ロング {result.get('long_display_score')} / ショート {result.get('short_display_score')} / 差 {result.get('score_gap')}",
        ),
    ]
    root_cards_html = "".join(
        '<div class="fact-card">'
        f"<h3>{esc(label)}</h3>"
        f"<p>{esc(value)}</p>"
        "</div>"
        for label, value in root_cards
    )

    display_reasons = notification_context.get("reason_labels_full", wait_reasons)
    wait_reason_html = "".join(f"<li>{esc(reason)}</li>" for reason in display_reasons)
    reason_cards_html = _reason_cards_html(display_reasons)
    ai_warning_html = "".join(f"<li>{esc(reason)}</li>" for reason in ai_warnings)
    raw_mail = _raw_mail_text(result, display_context)
    score_compare_html = _score_compare_rows(result)
    status_emoji = _status_emoji(str(notification_context.get("status_code", "")))
    price_map_svg = _price_map_svg(result)

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(subject)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --paper: #ffffff;
      --ink: #10212b;
      --muted: #60707c;
      --line: #d8dfe6;
      --accent: #0f766e;
      --accent-soft: #dff7f2;
      --warn: #b45309;
      --danger: #b42318;
      --info: #2f6fed;
      --amber: #d97706;
      --bar-direction: linear-gradient(90deg, #67b7ff 0%, #2f6fed 100%);
      --bar-execution: linear-gradient(90deg, #ff8d7a 0%, #b42318 100%);
      --bar-wait: linear-gradient(90deg, #ffd36b 0%, #d97706 100%);
      --score-long: linear-gradient(90deg, #34d399 0%, #0f766e 100%);
      --score-short: linear-gradient(90deg, #fb923c 0%, #ea580c 100%);
      --sky: #e0f2fe;
      --shadow: 0 10px 30px rgba(16, 33, 43, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #d8f3ff 0%, transparent 32%),
        linear-gradient(180deg, #f6fbff 0%, var(--bg) 45%, #eef2f6 100%);
      line-height: 1.75;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 56px; }}
    .hero, .section {{
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid rgba(216, 223, 230, 0.9);
      border-radius: 22px;
      box-shadow: var(--shadow);
      margin-bottom: 18px;
    }}
    .hero {{
      padding: 28px;
      background:
        linear-gradient(135deg, rgba(224, 242, 254, 0.92) 0%, rgba(255,255,255,0.96) 48%, rgba(223,247,242,0.96) 100%);
    }}
    .section {{ padding: 22px; }}
    h1, h2, h3 {{ margin: 0 0 10px; line-height: 1.4; }}
    h1 {{ font-size: 30px; letter-spacing: 0.01em; }}
    h2 {{ font-size: 21px; }}
    h3 {{ font-size: 15px; color: var(--muted); }}
    p {{ margin: 0 0 10px; }}
    .muted {{ color: var(--muted); font-size: 14px; }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 12px;
      border-radius: 999px;
      border: 1px solid rgba(15, 118, 110, 0.12);
      background: rgba(255,255,255,0.84);
      color: var(--ink);
      font-size: 13px;
      font-weight: 700;
      margin: 0 8px 8px 0;
    }}
    .hero-grid, .fact-grid, .metric-grid, .two-col, .overview-grid, .reason-grid {{
      display: grid;
      gap: 14px;
    }}
    .hero-grid {{ grid-template-columns: 1.4fr 1fr; margin-top: 18px; }}
    .overview-grid {{ grid-template-columns: 1.2fr 0.8fr; margin-top: 16px; }}
    .fact-grid {{ grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }}
    .metric-grid {{ grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}
    .two-col {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .reason-grid {{ grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
      background: #fbfdfe;
    }}
    .fact-card {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
      background: linear-gradient(180deg, #ffffff 0%, #f9fbfc 100%);
    }}
    .fact-card p {{ font-size: 18px; font-weight: 700; margin: 0; }}
    .metric-card {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }}
    .metric-head {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .metric-label {{ font-size: 28px; color: var(--ink); font-weight: 800; }}
    .metric-value {{ font-size: 20px; font-weight: 800; line-height: 1.1; }}
    .metric-track {{
      width: 100%;
      height: 16px;
      border-radius: 999px;
      background: #e8edf2;
      overflow: hidden;
      margin-bottom: 12px;
      border: 1px solid #e3e8ee;
    }}
    .metric-fill {{
      height: 100%;
      border-radius: 999px;
      box-shadow: inset 0 -1px 0 rgba(255,255,255,0.35);
    }}
    .metric-hint {{ color: var(--muted); font-weight: 700; margin: 2px 0 8px; }}
    .metric-help {{ margin-bottom: 6px; }}
    .metric-reading {{
      color: #1d4d3f;
      font-weight: 700;
      margin: 0;
    }}
    ul {{ margin: 8px 0 0; padding-left: 22px; }}
    li {{ margin-bottom: 8px; }}
    .mail-block {{
      white-space: pre-wrap;
      font-family: "SFMono-Regular", Menlo, monospace;
      font-size: 13px;
      background: #0f172a;
      color: #dbeafe;
      border-radius: 18px;
      padding: 18px;
      overflow-wrap: anywhere;
    }}
    .strong {{
      border-left: 4px solid var(--accent);
      padding-left: 12px;
      margin-top: 12px;
      font-weight: 700;
    }}
    .hero-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      font-weight: 800;
      padding: 9px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,0.9);
      border: 1px solid rgba(16, 33, 43, 0.08);
      margin-bottom: 10px;
    }}
    .hero-summary {{
      font-size: 28px;
      font-weight: 900;
      line-height: 1.45;
      margin: 0 0 10px;
    }}
    .hero-sub {{
      font-size: 17px;
      color: var(--muted);
      margin-bottom: 16px;
    }}
    .verdict-card {{
      border-radius: 20px;
      border: 1px solid rgba(15, 118, 110, 0.14);
      background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(233, 247, 245, 0.95) 100%);
      padding: 18px;
    }}
    .verdict-card h2 {{ margin-bottom: 12px; }}
    .summary-list {{
      list-style: none;
      padding: 0;
      margin: 14px 0 0;
    }}
    .summary-list li {{
      display: flex;
      gap: 10px;
      align-items: flex-start;
      margin-bottom: 10px;
    }}
    .emoji {{
      font-size: 20px;
      line-height: 1;
      width: 24px;
      text-align: center;
      flex: 0 0 24px;
    }}
    .balance-panel {{
      border-radius: 20px;
      border: 1px solid rgba(47, 111, 237, 0.14);
      background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
      padding: 18px;
    }}
    .sparkline {{
      width: 100%;
      height: auto;
      display: block;
      margin-top: 10px;
    }}
    .spark-grid {{
      stroke: #d7dfeb;
      stroke-width: 1;
    }}
    .spark-line {{
      fill: none;
      stroke: #2f6fed;
      stroke-width: 4;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .spark-dot {{
      fill: #ffffff;
      stroke: #2f6fed;
      stroke-width: 3;
    }}
    .spark-label {{
      fill: #60707c;
      font-size: 11px;
      font-weight: 700;
    }}
    .score-row {{
      margin-top: 14px;
    }}
    .score-row-head {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 6px;
      font-weight: 800;
    }}
    .score-track {{
      width: 100%;
      height: 14px;
      border-radius: 999px;
      background: #e8edf2;
      overflow: hidden;
    }}
    .score-fill {{
      height: 100%;
      border-radius: 999px;
    }}
    .reason-card {{
      display: grid;
      grid-template-columns: 54px 1fr;
      gap: 12px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      background: linear-gradient(180deg, #fffdf7 0%, #ffffff 100%);
    }}
    .reason-icon {{
      width: 54px;
      height: 54px;
      border-radius: 16px;
      display: grid;
      place-items: center;
      font-size: 26px;
      background: #fff6df;
      border: 1px solid #f0e1b2;
    }}
    .reason-text {{
      font-size: 16px;
      font-weight: 800;
      line-height: 1.55;
    }}
    .takeaway {{
      margin-top: 18px;
      padding: 16px 18px;
      border-left: 5px solid var(--accent);
      border-radius: 16px;
      background: rgba(223, 247, 242, 0.78);
      font-size: 22px;
      font-weight: 900;
      line-height: 1.6;
    }}
    .price-map-wrap {{
      padding: 10px 0 0;
    }}
    .price-map {{
      width: 100%;
      height: auto;
      display: block;
    }}
    .price-map-bg {{
      fill: #fbfdff;
      stroke: #d8dfe6;
      stroke-width: 1;
    }}
    .price-grid {{
      stroke: #e3e9f0;
      stroke-width: 1;
    }}
    .price-midline {{
      stroke: #c8d3df;
      stroke-dasharray: 6 6;
      stroke-width: 2;
    }}
    .zone-support {{
      fill: rgba(15, 118, 110, 0.22);
      stroke: #0f766e;
      stroke-width: 1.5;
    }}
    .zone-resistance {{
      fill: rgba(180, 35, 24, 0.18);
      stroke: #b42318;
      stroke-width: 1.5;
    }}
    .zone-caption {{
      fill: #51616d;
      font-size: 12px;
      font-weight: 700;
    }}
    .price-axis {{
      fill: #60707c;
      font-size: 11px;
      font-weight: 700;
    }}
    .price-current-line {{
      stroke: #2f6fed;
      stroke-width: 3;
    }}
    .price-current-dot {{
      fill: #ffffff;
      stroke: #2f6fed;
      stroke-width: 4;
    }}
    .price-current-label {{
      fill: #1e3a8a;
      font-size: 13px;
      font-weight: 800;
    }}
    .price-list p {{ margin-bottom: 8px; }}
    @media (max-width: 820px) {{
      .hero-grid, .two-col, .overview-grid {{ grid-template-columns: 1fr; }}
      .metric-label {{ font-size: 24px; }}
      .metric-value {{ font-size: 18px; }}
      .hero-summary {{ font-size: 22px; }}
      .takeaway {{ font-size: 18px; }}
      .wrap {{ padding: 16px 12px 42px; }}
      .hero, .section {{ border-radius: 18px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <p class="muted">{esc(timestamp_jst)} / signal_id {esc(result.get('signal_id', ''))}</p>
      <div class="hero-kicker">{status_emoji} {esc(notification_context.get('status_label', '中立'))} / {esc(notification_context.get('execution_label', '見送り'))}</div>
      <h1>{esc(subject)}</h1>
      <p class="hero-summary">{status_emoji} {esc(display_context.get('direction_label', ''))}。ただし今回の行動は「{esc(notification_context.get('execution_label', ''))}」です。</p>
      <p class="hero-sub">方向とタイミングを分けて読むため、まずは「入っていいか」を先に判断できる構成にしています。</p>
      <div>{chips_html(summary_chips)}</div>
      <div class="overview-grid">
        <div class="verdict-card">
          <h2>最初に読む結論</h2>
          <ul class="summary-list">
            <li><span class="emoji">🎯</span><div><strong>今の行動:</strong> {esc(notification_context.get('execution_label', ''))}</div></li>
            <li><span class="emoji">🪜</span><div><strong>現値帯の扱い:</strong> {esc(notification_context.get('entry_window_label', ''))}</div></li>
            <li><span class="emoji">🕒</span><div><strong>有効目安:</strong> {esc(notification_context.get('validity_label', ''))}</div></li>
            <li><span class="emoji">🔁</span><div><strong>次に見る条件:</strong> {esc(notification_context.get('next_condition_label', '次回更新で再評価'))}</div></li>
            <li><span class="emoji">🧯</span><div><strong>無効化目安:</strong> {esc(notification_context.get('invalidation_label', '主要価格帯の反応崩れで無効寄り'))}</div></li>
          </ul>
          <div class="takeaway">要するに、方向とタイミングは別物です。今回は <strong>{esc(display_context.get('direction_compact_label', '中立'))}</strong> ですが、<strong>{esc(notification_context.get('execution_label', '見送り'))}</strong> が先です。</div>
        </div>
        <div class="balance-panel">
          <h2>ひと目で分かるバランス</h2>
          <p><strong>方向の正しさ</strong> と <strong>今の入りやすさ</strong> と <strong>待つ圧力</strong> を折れ線で重ねています。</p>
          {balance_svg}
          <div class="score-row-head" style="margin-top:16px;"><span>ロング / ショート比較</span><strong>スコア</strong></div>
          {score_compare_html}
        </div>
      </div>
    </section>

    <section class="section">
      <h2>主要ファクト</h2>
      <div class="fact-grid">{root_cards_html}</div>
    </section>

    <section class="section">
      <h2>3つの数字を丁寧に読む</h2>
      <div class="metric-grid">{''.join(metric_blocks)}</div>
    </section>

    <section class="section">
      <h2>価格帯マップ</h2>
      <div class="panel price-map-wrap">
        {price_map_svg}
      </div>
      <div class="two-col" style="margin-top:14px;">
        <div class="panel price-list">
          <p><strong>現在価格:</strong> {esc(_format_price(result.get('current_price')))}</p>
          <p><strong>Funding:</strong> {esc(funding_display)}</p>
          <p><strong>ATR比 / 出来高比:</strong> {esc(result.get('atr_ratio'))} / {esc(result.get('volume_ratio'))}</p>
        </div>
        <div class="panel">
          <h3>図の読み方</h3>
          <ul>
            <li>青い縦線が現在価格です。</li>
            <li>緑帯がサポート、赤帯がレジスタンスです。</li>
            <li>現在値と帯の位置関係で、次にぶつかりやすい価格帯を直感で見ます。</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>ロング / ショートの再検討ライン</h2>
      <div class="two-col">
        <div class="panel">
          <h3>ロング</h3>
          <p>{esc(_setup_line(result, 'long'))}</p>
        </div>
        <div class="panel">
          <h3>ショート</h3>
          <p>{esc(_setup_line(result, 'short'))}</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>待機理由または注意点</h2>
      <div class="reason-grid">{reason_cards_html}</div>
      <ul>{wait_reason_html}</ul>
    </section>

    <section class="section">
      <h2>AI補足の読み解き</h2>
      <div class="two-col">
        <div class="panel">
          <h3>補足判断</h3>
          <p>{esc(ai_reason or '補足判断はありません')}</p>
          <h3>次の確認条件</h3>
          <p>{esc(ai_next or '次条件の指定はありません')}</p>
        </div>
        <div class="panel">
          <h3>注意</h3>
          <ul>{ai_warning_html or '<li>追加の注意表示はありません</li>'}</ul>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>元メールの要点</h2>
      <div class="mail-block">{esc(raw_mail)}</div>
    </section>
  </div>
</body>
</html>
"""


def slugify_label(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "unknown"
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "unknown"


def detail_page_enabled(cfg: Any, result: dict[str, Any]) -> bool:
    if not bool(getattr(cfg, "NOTIFICATION_HTML_ENABLED", False)):
        return False
    if str(result.get("notification_kind", "main")).lower() == "attention":
        return bool(getattr(cfg, "NOTIFICATION_HTML_INCLUDE_ATTENTION", True))
    return True


def detail_page_paths(base_dir: Path, cfg: Any, result: dict[str, Any]) -> tuple[Path, str]:
    local_dir_raw = str(getattr(cfg, "NOTIFICATION_HTML_LOCAL_DIR", "logs/notifications_html")).strip() or "logs/notifications_html"
    local_root = Path(local_dir_raw)
    if not local_root.is_absolute():
        local_root = base_dir / local_root
    system_slug = slugify_label(result.get("system_label"))
    notification_kind = str(result.get("notification_kind", "main")).strip().lower() or "main"
    signal_id = str(result.get("signal_id", "")).strip() or datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    local_path = local_root / system_slug / notification_kind / f"{signal_id}.html"
    public_base = str(getattr(cfg, "NOTIFICATION_HTML_PUBLIC_BASE_URL", "https://server.afrog.jp/btc-monitor/notifications")).rstrip("/")
    public_url = f"{public_base}/{system_slug}/{notification_kind}/{signal_id}.html"
    return local_path, public_url


def publish_notification_detail(base_dir: Path, cfg: Any, result: dict[str, Any]) -> dict[str, Any]:
    local_path, public_url = detail_page_paths(base_dir, cfg, result)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(build_notification_detail_html(result), encoding="utf-8")

    remote_host = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_SSH_HOST", "maruPro@macserver.afrog.jp")).strip()
    remote_root = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_DIR", "/Volumes/Server_HD2/site/btc-monitor/notifications")).strip()
    system_slug = slugify_label(result.get("system_label"))
    notification_kind = str(result.get("notification_kind", "main")).strip().lower() or "main"
    remote_dir = f"{remote_root.rstrip('/')}/{system_slug}/{notification_kind}"
    remote_path = f"{remote_dir}/{local_path.name}"

    subprocess.run(
        ["ssh", remote_host, "mkdir", "-p", remote_dir],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    subprocess.run(
        ["rsync", "-a", str(local_path), f"{remote_host}:{remote_path}"],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return {
        "detail_page_enabled": True,
        "detail_page_status": "published",
        "detail_page_url": public_url,
        "detail_page_local_path": str(local_path),
        "detail_page_published_at_utc": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def append_detail_page_url(body: str, url: str) -> str:
    if not str(url).strip():
        return body
    if str(url) in str(body):
        return body
    base = str(body).rstrip()
    return f"{base}\n\n【詳細ページ】\n{url}\n"
