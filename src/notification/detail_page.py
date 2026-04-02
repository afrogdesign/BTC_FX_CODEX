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


def _format_price_int(value: Any) -> str:
    try:
        return f"{float(value):,.0f}"
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
    long_setup = result.get("long_setup", {}) or {}
    short_setup = result.get("short_setup", {}) or {}
    support_zones = result.get("support_zones", [])[:3]
    resistance_zones = result.get("resistance_zones", [])[:3]
    values = [current_price]
    long_entry = long_setup.get("entry_zone") or {}
    short_entry = short_setup.get("entry_zone") or {}
    for zone in (long_entry, short_entry):
        values.extend([_safe_float(zone.get("low")), _safe_float(zone.get("high"))])
    for setup in (long_setup, short_setup):
        values.extend(
            [
                _safe_float(setup.get("stop_loss")),
                _safe_float(setup.get("tp1")),
                _safe_float(setup.get("tp2")),
            ]
        )
    for zone in support_zones + resistance_zones:
        values.extend([_safe_float(zone.get("low")), _safe_float(zone.get("high"))])
    values = [value for value in values if value > 0]
    chart_min = min(values) if values else 0.0
    chart_max = max(values) if values else 1.0
    padding = max((chart_max - chart_min) * 0.1, 160.0)
    chart_min -= padding
    chart_max += padding

    width = 860
    height = 440
    top = 36
    bottom = 42
    left = 34
    right = 132
    usable_h = height - top - bottom
    chart_left = left
    chart_right = width - right
    chart_width = chart_right - chart_left

    def y_for_price(value: float) -> float:
        if chart_max <= chart_min:
            return top + usable_h / 2
        ratio = (chart_max - value) / (chart_max - chart_min)
        ratio = max(0.0, min(1.0, ratio))
        return top + ratio * usable_h

    horizontal_grid: list[str] = []
    price_ticks: list[str] = []
    for idx in range(6):
        tick_value = chart_min + (chart_max - chart_min) * idx / 5
        y = y_for_price(tick_value)
        horizontal_grid.append(
            f'<line x1="{chart_left}" y1="{y:.1f}" x2="{chart_right}" y2="{y:.1f}" class="price-grid-h" />'
        )
        price_ticks.append(
            f'<text x="{width - 16}" y="{y + 4:.1f}" text-anchor="end" class="price-axis">{_format_price_int(tick_value)}</text>'
        )

    vertical_grid = []
    for idx in range(1, 5):
        x = chart_left + chart_width * idx / 5
        vertical_grid.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height - bottom}" class="price-grid-v" />'
        )

    background_bands: list[str] = []
    for zone in resistance_zones:
        low = _safe_float(zone.get("low"))
        high = _safe_float(zone.get("high"))
        y1 = y_for_price(high)
        y2 = y_for_price(low)
        background_bands.append(
            f'<rect x="{chart_left}" y="{y1:.1f}" width="{chart_width}" height="{max(y2 - y1, 8):.1f}" class="band-resistance" />'
        )
    for zone in support_zones:
        low = _safe_float(zone.get("low"))
        high = _safe_float(zone.get("high"))
        y1 = y_for_price(high)
        y2 = y_for_price(low)
        background_bands.append(
            f'<rect x="{chart_left}" y="{y1:.1f}" width="{chart_width}" height="{max(y2 - y1, 8):.1f}" class="band-support" />'
        )

    current_y = y_for_price(current_price)
    emphasis_lines: list[str] = [
        f'<line x1="{chart_left}" y1="{current_y:.1f}" x2="{chart_right}" y2="{current_y:.1f}" class="current-price-line" />',
        f'<rect x="{chart_right - 102:.1f}" y="{current_y - 18:.1f}" width="96" height="36" rx="12" class="current-price-box" />',
        f'<text x="{chart_right - 54:.1f}" y="{current_y - 4:.1f}" text-anchor="middle" class="current-price-box-label">現在値</text>',
        f'<text x="{chart_right - 54:.1f}" y="{current_y + 12:.1f}" text-anchor="middle" class="current-price-box-value">{_format_price_int(current_price)}</text>',
    ]

    def setup_band(zone: dict[str, Any], side: str, status: Any, x: float, width_ratio: float) -> list[str]:
        low = _safe_float(zone.get("low"))
        high = _safe_float(zone.get("high"))
        if low <= 0 and high <= 0:
            return []
        y1 = y_for_price(high)
        y2 = y_for_price(low)
        band_width = chart_right - (chart_left + chart_width * x)
        band_x = chart_left + chart_width * x
        label = "LONG 再検討帯" if side == "long" else "SHORT 再検討帯"
        status_label = _setup_status_label(status)
        band_class = "setup-band-long" if side == "long" else "setup-band-short"
        text_class = "setup-band-text-long" if side == "long" else "setup-band-text-short"
        callout_class = "setup-callout-long" if side == "long" else "setup-callout-short"
        callout_text_class = "setup-callout-text-long" if side == "long" else "setup-callout-text-short"
        callout_value_class = "setup-callout-value"
        callout_width = 236
        callout_height = 52
        callout_x = chart_left + 16 if side == "long" else chart_left + 92
        callout_y = y1 - callout_height - 12 if side == "long" else y1 - callout_height - 28
        axis_value_class = "setup-axis-value-long" if side == "long" else "setup-axis-value-short"
        return [
            f'<rect x="{band_x:.1f}" y="{y1:.1f}" width="{band_width:.1f}" height="{max(y2 - y1, 14):.1f}" rx="12" class="{band_class}" />',
            f'<rect x="{callout_x:.1f}" y="{callout_y:.1f}" width="{callout_width}" height="{callout_height}" rx="12" class="{callout_class}" />',
            f'<text x="{callout_x + 14:.1f}" y="{callout_y + 20:.1f}" class="{text_class}">{label}</text>',
            f'<text x="{callout_x + 14:.1f}" y="{callout_y + 38:.1f}" class="{callout_text_class}">{html.escape(status_label)}</text>',
            f'<text x="{callout_x + callout_width - 14:.1f}" y="{callout_y + 38:.1f}" text-anchor="end" class="{callout_value_class}">{_format_price_int(low)} - {_format_price_int(high)}</text>',
            f'<text x="{chart_right + 6:.1f}" y="{y1 + 6:.1f}" class="{axis_value_class}">{_format_price_int(high)}</text>',
            f'<text x="{chart_right + 6:.1f}" y="{y2 + 6:.1f}" class="{axis_value_class}">{_format_price_int(low)}</text>',
        ]

    setup_elements = []
    setup_elements.extend(setup_band(long_entry, "long", long_setup.get("status"), 0.30, 0.58))
    setup_elements.extend(setup_band(short_entry, "short", short_setup.get("status"), 0.30, 0.58))

    def marker_line(
        price: Any,
        label: str,
        tone: str,
        x1_ratio: float,
        x2_ratio: float,
        *,
        label_anchor: str = "start",
        label_offset: float = 8.0,
        label_dy: float = 4.0,
    ) -> str:
        value = _safe_float(price)
        if value <= 0:
            return ""
        y = y_for_price(value)
        x1 = chart_left + chart_width * x1_ratio
        x2 = chart_left + chart_width * x2_ratio
        label_x = x2 + label_offset if label_anchor == "start" else x1 - label_offset
        return (
            f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" class="marker-line {tone}" />'
            f'<text x="{label_x:.1f}" y="{y + label_dy:.1f}" text-anchor="{label_anchor}" class="marker-label {tone}">{html.escape(label)} {_format_price_int(value)}</text>'
        )

    markers = [
        marker_line(long_setup.get("stop_loss"), "Long SL", "marker-long", 0.04, 0.16, label_dy=16),
        marker_line(long_setup.get("tp1"), "Long TP1", "marker-long", 0.04, 0.16, label_dy=-8),
        marker_line(short_setup.get("stop_loss"), "Short SL", "marker-short", 0.84, 0.96, label_anchor="end", label_dy=-8),
        marker_line(short_setup.get("tp1"), "Short TP1", "marker-short", 0.84, 0.96, label_anchor="end", label_dy=16),
    ]

    return (
        f'<svg viewBox="0 0 {width} {height}" class="price-map" aria-label="再検討ラインチャート">'
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="18" class="price-map-bg" />'
        '<text x="24" y="24" class="chart-title">BTCUSDT 再検討ライン</text>'
        '<text x="24" y="44" class="chart-subtitle">ロング / ショートの再検討帯を主役にし、サポートとレジスタンスは背景帯として表示</text>'
        f"{''.join(horizontal_grid)}"
        f"{''.join(vertical_grid)}"
        f"{''.join(background_bands)}"
        f"{''.join(setup_elements)}"
        f"{''.join(marker for marker in markers if marker)}"
        f"{''.join(emphasis_lines)}"
        f"{''.join(price_ticks)}"
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
    .metric-grid {{ grid-template-columns: 1fr; }}
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
      background: linear-gradient(180deg, #121a2c 0%, #0e1422 100%);
      border-color: #263148;
    }}
    .price-map {{
      width: 100%;
      height: auto;
      display: block;
    }}
    .price-map-bg {{
      fill: #0f1728;
      stroke: #263148;
      stroke-width: 1;
    }}
    .chart-title {{
      fill: #eff6ff;
      font-size: 16px;
      font-weight: 700;
    }}
    .chart-subtitle {{
      fill: #93a4bf;
      font-size: 11px;
      font-weight: 500;
    }}
    .price-grid-h {{
      stroke: rgba(148, 163, 184, 0.24);
      stroke-width: 1;
    }}
    .price-grid-v {{
      stroke: rgba(148, 163, 184, 0.16);
      stroke-width: 1;
    }}
    .band-support {{
      fill: rgba(34, 197, 94, 0.14);
    }}
    .band-resistance {{
      fill: rgba(248, 113, 113, 0.14);
    }}
    .setup-band-long {{
      fill: rgba(34, 197, 94, 0.26);
      stroke: #4ade80;
      stroke-width: 2;
    }}
    .setup-band-short {{
      fill: rgba(248, 113, 113, 0.26);
      stroke: #f87171;
      stroke-width: 2;
    }}
    .setup-band-text-long {{
      fill: #dcfce7;
      font-size: 13px;
      font-weight: 700;
    }}
    .setup-band-text-short {{
      fill: #fee2e2;
      font-size: 13px;
      font-weight: 700;
    }}
    .setup-callout-long, .setup-callout-short {{
      stroke-width: 1;
    }}
    .setup-callout-long {{
      fill: rgba(7, 20, 34, 0.92);
      stroke: rgba(74, 222, 128, 0.45);
    }}
    .setup-callout-short {{
      fill: rgba(7, 20, 34, 0.92);
      stroke: rgba(248, 113, 113, 0.45);
    }}
    .setup-callout-text-long {{
      fill: #bbf7d0;
      font-size: 12px;
      font-weight: 500;
    }}
    .setup-callout-text-short {{
      fill: #fecaca;
      font-size: 12px;
      font-weight: 500;
    }}
    .setup-callout-value {{
      fill: #dbe7f7;
      font-size: 12px;
      font-weight: 500;
    }}
    .setup-axis-value-long {{
      fill: #4ade80;
      font-size: 12px;
      font-weight: 700;
    }}
    .setup-axis-value-short {{
      fill: #f87171;
      font-size: 12px;
      font-weight: 700;
    }}
    .price-axis {{
      fill: #9db0ca;
      font-size: 11px;
      font-weight: 500;
    }}
    .current-price-line {{
      stroke: #60a5fa;
      stroke-width: 2.5;
      stroke-dasharray: 5 5;
    }}
    .current-price-label {{
      fill: #bfdbfe;
      font-size: 13px;
      font-weight: 600;
    }}
    .current-price-box {{
      fill: #1d4ed8;
      stroke: #60a5fa;
      stroke-width: 1;
    }}
    .current-price-box-label {{
      fill: #eff6ff;
      font-size: 11px;
      font-weight: 600;
    }}
    .current-price-box-value {{
      fill: #bfdbfe;
      font-size: 11px;
      font-weight: 500;
    }}
    .marker-line {{
      stroke-width: 2;
      stroke-dasharray: 4 4;
    }}
    .marker-label {{
      font-size: 10px;
      font-weight: 500;
    }}
    .marker-long {{
      stroke: #4ade80;
      fill: #bbf7d0;
    }}
    .marker-short {{
      stroke: #f87171;
      fill: #fecaca;
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
      <h2>3つの数字を丁寧に読む</h2>
      <div class="metric-grid">{''.join(metric_blocks)}</div>
    </section>

    <section class="section">
      <h2>再検討ラインチャート</h2>
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
            <li>青い横線が現在価格です。</li>
            <li>緑帯がロング再検討帯、赤帯がショート再検討帯です。</li>
            <li>帯の近くの吹き出しに、`監視継続` や `現状は見送り` などの扱いを出します。</li>
            <li>薄い背景帯はサポートとレジスタンスで、主役は再検討ラインです。</li>
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
      <h2>主要ファクト</h2>
      <div class="fact-grid">{root_cards_html}</div>
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
