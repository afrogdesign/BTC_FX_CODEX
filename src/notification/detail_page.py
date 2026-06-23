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
        "invalid": "⛔️",
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


def _active_plan_hero_label(notification_context: dict[str, Any], result: dict[str, Any]) -> str:
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()

    if notification_kind == "attention":
        return "注意報・売買非推奨"

    if trade_gate == "pass" and paper_order_status == "planned":
        return "正式GO・紙トレード記録候補"

    active_label = str(notification_context.get("active_subject_label", "")).strip()
    if active_label:
        return f"{active_label} / 実弾不可・行動計画"

    return "見送り / 実弾不可・行動計画"


def _active_plan_hero_summary(
    notification_context: dict[str, Any],
    display_context: dict[str, Any],
    result: dict[str, Any],
) -> str:
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()

    if notification_kind == "attention":
        return "これは売買推奨ではなく、方向変化や初動を早めに共有する注意通知です。"

    if trade_gate == "pass" and paper_order_status == "planned":
        return "これは正式な執行候補です。ただし現段階では自動売買ではなく、紙トレード記録対象です。"

    active_headline = str(notification_context.get("active_headline", "")).strip()
    if active_headline:
        return active_headline

    return f"{display_context.get('direction_label', '相場は中立です')}。現時点では実弾不可の行動計画として確認します。"


def _active_plan_status_rows(notification_context: dict[str, Any]) -> list[tuple[str, str]]:
    market = notification_context.get("active_market_entry_now", {}) or {}
    limit = notification_context.get("active_limit_retest_entry", {}) or {}
    breakout = notification_context.get("active_breakout_follow_entry", {}) or {}
    counter = notification_context.get("active_countertrend_scalp_entry", {}) or {}
    position = notification_context.get("active_position_management", {}) or {}

    return [
        ("成行", f"long: {market.get('long', 'blocked')} / short: {market.get('short', 'blocked')}"),
        ("指値・戻り待ち", f"long: {limit.get('long', 'blocked')} / short: {limit.get('short', 'blocked')}"),
        ("ブレイク追随", f"long: {breakout.get('long', 'blocked')} / short: {breakout.get('short', 'blocked')}"),
        ("逆方向短期", f"long: {counter.get('long', 'blocked')} / short: {counter.get('short', 'blocked')}"),
        (
            "保有中処理",
            str(
                position.get("if_short_holding")
                or position.get("if_long_holding")
                or "保有中なら主要価格帯で利確・建値撤退・撤退条件を確認"
            ),
        ),
    ]


def _price_position(value: float, chart_min: float, chart_max: float, left: float, width: float) -> float:
    if chart_max <= chart_min:
        return left + width / 2
    ratio = (value - chart_min) / (chart_max - chart_min)
    ratio = max(0.0, min(1.0, ratio))
    return left + ratio * width


def _snapshot_candles(chart_snapshot: dict[str, Any], key: str) -> list[dict[str, Any]]:
    candles = chart_snapshot.get(key, [])
    if not isinstance(candles, list):
        return []
    return [candle for candle in candles if isinstance(candle, dict)]


def _format_candle_time(timestamp_ms: Any, panel_mode: str) -> str:
    try:
        value = float(timestamp_ms)
    except (TypeError, ValueError):
        return ""
    dt = datetime.fromtimestamp(value / 1000.0, tz=timezone.utc).astimezone()
    if panel_mode == "execution":
        return dt.strftime("%H:%M")
    return dt.strftime("%m/%d %H:%M")


def _trim_candles(candles: list[dict[str, Any]], panel_mode: str) -> list[dict[str, Any]]:
    limit = {
        "context": 28,
        "zone": 36,
        "execution": 48,
    }.get(panel_mode, 36)
    if len(candles) <= limit:
        return candles
    return candles[-limit:]


def _panel_price_map_svg(
    *,
    title: str,
    subtitle: str,
    candles: list[dict[str, Any]],
    current_price: float,
    long_setup: dict[str, Any],
    short_setup: dict[str, Any],
    support_zones: list[dict[str, Any]],
    resistance_zones: list[dict[str, Any]],
    width: int,
    height: int,
    origin_y: int,
    panel_mode: str,
) -> str:
    top = origin_y + 26
    bottom = origin_y + height - 38
    left = 30
    right = width - 112
    usable_h = max(bottom - top, 1)
    chart_width = right - left
    candles = _trim_candles(candles, panel_mode)
    show_markers = panel_mode == "execution"
    show_setup_bands = panel_mode in {"zone", "execution"}
    show_background_bands = panel_mode != "execution"
    emphasize_setup = panel_mode == "execution"

    values = [current_price]
    long_entry = long_setup.get("entry_zone") or {}
    short_entry = short_setup.get("entry_zone") or {}
    if show_setup_bands:
        for zone in (long_entry, short_entry):
            values.extend([_safe_float(zone.get("low")), _safe_float(zone.get("high"))])
    if show_markers:
        for setup in (long_setup, short_setup):
            values.extend([_safe_float(setup.get("stop_loss")), _safe_float(setup.get("tp1")), _safe_float(setup.get("tp2"))])
    if show_background_bands:
        for zone in support_zones + resistance_zones:
            values.extend([_safe_float(zone.get("low")), _safe_float(zone.get("high"))])
    for candle in candles:
        values.extend([_safe_float(candle.get("high")), _safe_float(candle.get("low"))])
    values = [value for value in values if value > 0]
    chart_min = min(values) if values else 0.0
    chart_max = max(values) if values else 1.0
    padding = max((chart_max - chart_min) * 0.08, 40.0)
    chart_min -= padding
    chart_max += padding

    def y_for_price(value: float) -> float:
        if chart_max <= chart_min:
            return top + usable_h / 2
        ratio = (chart_max - value) / (chart_max - chart_min)
        ratio = max(0.0, min(1.0, ratio))
        return top + ratio * usable_h

    grid_lines: list[str] = []
    axis_labels: list[str] = []
    for idx in range(5):
        tick_value = chart_min + (chart_max - chart_min) * idx / 4
        y = y_for_price(tick_value)
        grid_lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="price-grid-h" />')
        axis_labels.append(
            f'<text x="{width - 14}" y="{y + 4:.1f}" text-anchor="end" class="price-axis">{_format_price_int(tick_value)}</text>'
        )

    vertical_grid: list[str] = []
    for idx in range(1, 5):
        x = left + chart_width * idx / 5
        vertical_grid.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" class="price-grid-v" />')

    candle_elements: list[str] = []
    time_labels: list[str] = []
    candle_left = left + 6
    candle_width = max(chart_width - 12, 20)
    if candles:
        slot = candle_width / max(len(candles), 1)
        body_width = max(min(slot * 0.82, 15.0), 4.6)
        for idx, candle in enumerate(candles):
            open_price = _safe_float(candle.get("open"))
            high_price = _safe_float(candle.get("high"))
            low_price = _safe_float(candle.get("low"))
            close_price = _safe_float(candle.get("close"))
            if min(open_price, high_price, low_price, close_price) <= 0:
                continue
            center_x = candle_left + slot * idx + slot / 2
            wick_y1 = y_for_price(high_price)
            wick_y2 = y_for_price(low_price)
            body_top = y_for_price(max(open_price, close_price))
            body_bottom = y_for_price(min(open_price, close_price))
            tone = "candle-up" if close_price >= open_price else "candle-down"
            candle_elements.append(
                f'<line x1="{center_x:.1f}" y1="{wick_y1:.1f}" x2="{center_x:.1f}" y2="{wick_y2:.1f}" class="candle-wick {tone}" />'
            )
            candle_elements.append(
                f'<rect x="{center_x - body_width / 2:.1f}" y="{body_top:.1f}" width="{body_width:.1f}" height="{max(body_bottom - body_top, 2.0):.1f}" rx="1.3" class="candle-body {tone}" />'
            )
        label_indexes = sorted({0, len(candles) // 2, len(candles) - 1})
        for idx in label_indexes:
            candle = candles[idx]
            center_x = candle_left + slot * idx + slot / 2
            label = _format_candle_time(candle.get("timestamp"), panel_mode)
            if not label:
                continue
            time_labels.append(
                f'<text x="{center_x:.1f}" y="{origin_y + height - 14:.1f}" text-anchor="middle" class="time-axis-label">{html.escape(label)}</text>'
            )
        time_labels.append(
            f'<line x1="{left}" y1="{bottom:.1f}" x2="{right}" y2="{bottom:.1f}" class="time-axis-line" />'
        )

    background_bands: list[str] = []
    if show_background_bands:
        for zone in resistance_zones:
            low = _safe_float(zone.get("low"))
            high = _safe_float(zone.get("high"))
            background_bands.append(
                f'<rect x="{left}" y="{y_for_price(high):.1f}" width="{chart_width}" height="{max(y_for_price(low) - y_for_price(high), 8):.1f}" class="band-resistance" />'
            )
        for zone in support_zones:
            low = _safe_float(zone.get("low"))
            high = _safe_float(zone.get("high"))
            background_bands.append(
                f'<rect x="{left}" y="{y_for_price(high):.1f}" width="{chart_width}" height="{max(y_for_price(low) - y_for_price(high), 8):.1f}" class="band-support" />'
            )

    setup_elements: list[str] = []
    if show_setup_bands:
        setup_x = left + chart_width * (0.12 if panel_mode == "zone" else 0.16)
        setup_w = chart_width * (0.84 if panel_mode == "zone" else 0.8)
        for side, setup in (("long", long_setup), ("short", short_setup)):
            entry = setup.get("entry_zone") or {}
            low = _safe_float(entry.get("low"))
            high = _safe_float(entry.get("high"))
            if min(low, high) <= 0:
                continue
            band_class = "setup-band-long" if side == "long" else "setup-band-short"
            axis_class = "setup-axis-value-long" if side == "long" else "setup-axis-value-short"
            opacity = "0.34" if emphasize_setup else "0.18"
            y1 = y_for_price(high)
            y2 = y_for_price(low)
            setup_elements.append(
                f'<rect x="{setup_x:.1f}" y="{y1:.1f}" width="{setup_w:.1f}" height="{max(y2 - y1, 10):.1f}" rx="10" class="{band_class}" style="opacity:{opacity};" />'
            )
            setup_elements.append(
                f'<text x="{right + 6:.1f}" y="{y1 + 5:.1f}" class="{axis_class}">{_format_price_int(high)}</text>'
            )
            setup_elements.append(
                f'<text x="{right + 6:.1f}" y="{y2 + 5:.1f}" class="{axis_class}">{_format_price_int(low)}</text>'
            )

    current_y = y_for_price(current_price)
    emphasis_lines: list[str] = [
        f'<line x1="{left}" y1="{current_y:.1f}" x2="{right}" y2="{current_y:.1f}" class="current-price-line" />',
        f'<text x="{right - 6:.1f}" y="{current_y - 6:.1f}" text-anchor="end" class="current-price-box-label">現在値 {_format_price_int(current_price)}</text>',
    ]

    markers: list[str] = []
    if show_markers:
        def marker_line(price: Any, label: str, tone: str, x1_ratio: float, x2_ratio: float, anchor: str) -> str:
            value = _safe_float(price)
            if value <= 0:
                return ""
            y = y_for_price(value)
            x1 = left + chart_width * x1_ratio
            x2 = left + chart_width * x2_ratio
            label_x = x2 + 8 if anchor == "start" else x1 - 8
            return (
                f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" class="marker-line {tone}" />'
                f'<text x="{label_x:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}" class="marker-label {tone}">{html.escape(label)} {_format_price_int(value)}</text>'
            )

        markers.extend(
            [
                marker_line(long_setup.get("stop_loss"), "Long SL", "marker-long", 0.03, 0.16, "start"),
                marker_line(long_setup.get("tp1"), "Long TP1", "marker-long", 0.03, 0.16, "start"),
                marker_line(long_setup.get("tp2"), "Long TP2", "marker-long", 0.03, 0.16, "start"),
                marker_line(short_setup.get("stop_loss"), "Short SL", "marker-short", 0.84, 0.97, "end"),
                marker_line(short_setup.get("tp1"), "Short TP1", "marker-short", 0.84, 0.97, "end"),
                marker_line(short_setup.get("tp2"), "Short TP2", "marker-short", 0.84, 0.97, "end"),
            ]
        )

    return (
        f'<g class="price-map-panel {"price-map-panel-focus" if show_markers else ""}">'
        f'<rect x="0" y="{origin_y}" width="{width}" height="{height}" rx="18" class="price-map-bg" />'
        f'<text x="22" y="{origin_y + 22}" class="chart-title">{html.escape(title)}</text>'
        f'<text x="22" y="{origin_y + 40}" class="chart-subtitle">{html.escape(subtitle)}</text>'
        f"{''.join(grid_lines)}"
        f"{''.join(vertical_grid)}"
        f"{''.join(background_bands)}"
        f"{''.join(candle_elements)}"
        f"{''.join(setup_elements)}"
        f"{''.join(marker for marker in markers if marker)}"
        f"{''.join(emphasis_lines)}"
        f"{''.join(axis_labels)}"
        f"{''.join(time_labels)}"
        "</g>"
    )


def _price_map_svg(result: dict[str, Any]) -> str:
    current_price = _safe_float(result.get("current_price"))
    long_setup = result.get("long_setup", {}) or {}
    short_setup = result.get("short_setup", {}) or {}
    support_zones = result.get("support_zones", [])[:3]
    resistance_zones = result.get("resistance_zones", [])[:3]
    chart_snapshot = result.get("chart_snapshot", {}) if isinstance(result.get("chart_snapshot"), dict) else {}
    width = 860
    panels = [
        _panel_price_map_svg(
            title="4時間足: 大局方向",
            subtitle="大きな流れと主要なサポート / レジスタンスだけを見ます。入る価格の判断は下段です",
            candles=_snapshot_candles(chart_snapshot, "candles_4h"),
            current_price=current_price,
            long_setup=long_setup,
            short_setup=short_setup,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            width=width,
            height=309,
            origin_y=0,
            panel_mode="context",
        ),
        _panel_price_map_svg(
            title="1時間足: 帯の妥当性",
            subtitle="再検討帯が押し目 / 戻りとして自然かを見る段です。TP / SL はここでは見ません",
            candles=_snapshot_candles(chart_snapshot, "candles_1h"),
            current_price=current_price,
            long_setup=long_setup,
            short_setup=short_setup,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            width=width,
            height=309,
            origin_y=329,
            panel_mode="zone",
        ),
        _panel_price_map_svg(
            title="15分足: 入る価格 / SL / TP",
            subtitle="実際に入る価格を見る主役の段です。再検討帯、SL、TP1、TP2 をここに集約しています",
            candles=_snapshot_candles(chart_snapshot, "candles_15m"),
            current_price=current_price,
            long_setup=long_setup,
            short_setup=short_setup,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            width=width,
            height=429,
            origin_y=658,
            panel_mode="execution",
        ),
    ]

    return (
        f'<svg viewBox="0 0 {width} 1097" class="price-map" aria-label="再検討ラインチャート">'
        f"{''.join(panels)}"
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


def _execution_precision_line(result: dict[str, Any], side: str) -> str:
    setup = result.get("long_setup", {}) if side == "long" else result.get("short_setup", {})
    action = str(setup.get("execution_precision_action") or "keep")
    reason = str(setup.get("execution_precision_reason") or "").strip()
    flags = [str(flag) for flag in setup.get("execution_precision_flags", []) if str(flag)]
    action_labels = {
        "keep": "そのまま監視",
        "wait_only": "待機のみ",
        "invalidate_watch": "無効化寄り",
        "allow_breakout_follow": "ブレイク追随候補",
    }
    flag_labels = {
        "short_at_major_support_wait_only": "主要サポート接近",
        "long_at_major_resistance_wait_only": "主要レジスタンス接近",
        "short_invalidated_by_up_break": "上抜け後の支持化",
        "long_invalidated_by_down_break": "下抜け後の抵抗化",
        "breakout_follow_candidate": "ブレイク追随候補",
    }
    flag_text = " / ".join(flag_labels.get(flag, flag) for flag in flags) or "追加注意なし"
    if reason:
        return f"{action_labels.get(action, action)}。{reason}（{flag_text}）"
    return f"{action_labels.get(action, action)}（{flag_text}）"


def _build_wait_reasons(display_context: dict[str, Any], result: dict[str, Any]) -> list[str]:
    reasons = [str(item) for item in display_context.get("wait_reason_labels", []) if str(item).strip()]
    if reasons:
        return reasons
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


def _manual_support_reference_items() -> list[tuple[str, str]]:
    return [
        ("事前生成/検証", "scripts/refresh_current_manual_delivery_app_surface.command"),
        ("ready gate", "refresh-and-check-current-manual-delivery-app-surface --stdout-json"),
        ("確認入口", "local/manual_delivery_app_surface/index.html"),
        ("Dashboard", "local/manual_delivery_app_surface/app-dashboard.html"),
        ("Ready JSON", "local/manual_delivery_app_surface/app-ready.json"),
        ("Snapshot", "local/manual_delivery_app_surface/app-snapshot.json"),
        ("Manifest", "local/manual_delivery_app_surface/app-surface-manifest.json"),
    ]


def build_notification_detail_html(result: dict[str, Any]) -> str:
    display_context = build_display_context(result)
    notification_context = build_notification_context(result)
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    timestamp_jst = str(result.get("timestamp_jst", "")).replace("T", " ")
    subject = str(result.get("summary_subject", "")).strip() or (
        f"{notification_context.get('final_rank_emoji', '')} [{notification_context.get('final_rank_label', '送信なし')}] / "
        f"{display_context.get('direction_compact_label', '中立')}"
    )
    wait_reasons = _build_wait_reasons(display_context, result)
    ai_audit = result.get("ai_audit") if isinstance(result.get("ai_audit"), dict) else {}
    audit_agreement = str(ai_audit.get("agreement", "")).strip().lower()
    audit_reason = sanitize_user_text(ai_audit.get("reason", ""))
    audit_next = sanitize_user_text(ai_audit.get("next_review_focus", ""))
    audit_unique_risks = sanitize_flag_list(ai_audit.get("unique_risks", []))
    funding_display = str(result.get("funding_rate_display") or "").strip() or f"{result.get('funding_rate_label', 'ほぼ中立')} ({_format_pct(result.get('funding_rate_pct', 0.0))})"
    summary_chips = [
        notification_context.get("final_rank_label", "送信なし"),
        notification_context.get("status_label", "中立"),
        display_context.get("entry_quality_label", "内部評価あり"),
    ]
    active_subject_label = str(notification_context.get("active_subject_label", "")).strip()
    if active_subject_label:
        summary_chips.append(active_subject_label)
    summary_chips.append(display_context.get("direction_compact_label", "中立"))
    if notification_context.get("final_rank_emoji"):
        summary_chips[0] = f"{notification_context.get('final_rank_emoji', '')} {summary_chips[0]}".strip()

    def esc(value: Any) -> str:
        return html.escape(str(value or "未記録"))

    def chips_html(items: list[str], class_name: str = "chip") -> str:
        return "".join(f'<span class="{class_name}">{esc(item)}</span>' for item in items if str(item).strip())

    active_hero_label = _active_plan_hero_label(notification_context, result)
    active_hero_summary = _active_plan_hero_summary(notification_context, display_context, result)
    active_status_rows = _active_plan_status_rows(notification_context)
    active_status_rows_html = "".join(
        '<li><span class="emoji">🧭</span><div>'
        f'<strong>{esc(label)}:</strong> {esc(value)}'
        '</div></li>'
        for label, value in active_status_rows
    )
    manual_support_reference_items = _manual_support_reference_items()
    manual_support_reference_list_html = "".join(
        '<li><strong>{label}:</strong> <code>{value}</code></li>'.format(
            label=esc(label),
            value=esc(value),
        )
        for label, value in manual_support_reference_items
    )

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
        ("最終ランク", f"{notification_context.get('final_rank_emoji', '')} {notification_context.get('final_rank_label', '')} / {notification_context.get('final_rank_explanation', '')}".strip(" /")),
        (
            "補足状態",
            f"{notification_context.get('status_label', '')} / {notification_context.get('status_explanation', '')}",
        ),
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
    raw_mail = _raw_mail_text(result, display_context)
    score_compare_html = _score_compare_rows(result)
    price_map_svg = _price_map_svg(result)
    show_ai_audit = audit_agreement in {"caution", "disagree"} or bool(audit_unique_risks)
    ai_audit_headline = "通知判断の再確認を推奨" if audit_agreement == "disagree" else "通知は妥当だが注意点あり"
    ai_audit_unique_risk_html = "".join(f"<li>{esc(reason)}</li>" for reason in audit_unique_risks)
    checklist_items = [
        ("Entry mode", str(notification_context.get("execution_label", "")).strip() or "未記録"),
        (
            "Entry condition",
            " / ".join(
                [
                    str(notification_context.get("entry_window_label", "")).strip(),
                    str(display_context.get("entry_quality_label", "")).strip(),
                    active_hero_summary,
                ]
            ).strip(" /")
            or "未記録",
        ),
        (
            "TP / SL",
            "\n".join(
                [
                    _setup_line(result, "long"),
                    _setup_line(result, "short"),
                ]
            ),
        ),
        (
            "Invalidation / wait",
            " / ".join(str(reason).strip() for reason in display_reasons if str(reason).strip()) or "未記録",
        ),
        ("Timeout / validity", str(notification_context.get("validity_label", "")).strip() or "未記録"),
        ("Safety", "report-only / not FORMAL_GO / no automatic order / human decides manually"),
    ]
    checklist_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">📝 <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in checklist_items
    )

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
    .checklist {{
      display: grid;
      gap: 12px;
      margin-top: 10px;
    }}
    .checklist-item {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px 16px;
      background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
    }}
    .checklist-label {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      color: var(--ink);
      margin-bottom: 6px;
    }}
    .checklist-value {{
      color: var(--muted);
      font-weight: 700;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }}
    .checklist-note {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
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
      padding: 14px 0 6px;
      background: linear-gradient(180deg, #121a2c 0%, #0e1422 100%);
      border-color: #263148;
    }}
    .price-map-wrap h3 {{
      margin: 0 18px 10px;
      color: #eff6ff;
      font-size: 18px;
      font-weight: 800;
    }}
    .price-map-wrap p {{
      margin: 0 18px 14px;
      color: #b9c7dc;
      font-size: 13px;
      line-height: 1.6;
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
    .price-map-panel-focus .price-map-bg {{
      stroke: #385072;
    }}
    .chart-title {{
      fill: #eff6ff;
      font-size: 18px;
      font-weight: 700;
    }}
    .chart-subtitle {{
      fill: #93a4bf;
      font-size: 12px;
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
    .candle-wick {{
      stroke-width: 1.35;
      opacity: 0.92;
    }}
    .candle-body {{
      stroke-width: 0.95;
      opacity: 0.96;
    }}
    .candle-up {{
      fill: rgba(74, 222, 128, 0.62);
      stroke: rgba(74, 222, 128, 0.95);
    }}
    .candle-down {{
      fill: rgba(248, 113, 113, 0.58);
      stroke: rgba(248, 113, 113, 0.94);
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
      stroke-width: 1.7;
    }}
    .setup-band-short {{
      fill: rgba(248, 113, 113, 0.26);
      stroke: #f87171;
      stroke-width: 1.7;
    }}
    .setup-band-text-long {{
      fill: #dcfce7;
      font-size: 14px;
      font-weight: 700;
    }}
    .setup-band-text-short {{
      fill: #fee2e2;
      font-size: 14px;
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
      font-size: 13px;
      font-weight: 500;
    }}
    .setup-callout-text-short {{
      fill: #fecaca;
      font-size: 13px;
      font-weight: 500;
    }}
    .setup-callout-value {{
      fill: #dbe7f7;
      font-size: 13px;
      font-weight: 500;
    }}
    .setup-axis-value-long {{
      fill: #4ade80;
      font-size: 13px;
      font-weight: 700;
    }}
    .setup-axis-value-short {{
      fill: #f87171;
      font-size: 13px;
      font-weight: 700;
    }}
    .price-axis {{
      fill: #9db0ca;
      font-size: 12px;
      font-weight: 500;
    }}
    .time-axis-line {{
      stroke: rgba(148, 163, 184, 0.3);
      stroke-width: 1;
    }}
    .time-axis-label {{
      fill: #8fa2bf;
      font-size: 11px;
      font-weight: 600;
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
      font-size: 12px;
      font-weight: 600;
    }}
    .current-price-box-value {{
      fill: #bfdbfe;
      font-size: 13px;
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
      .price-map-wrap {{ padding: 12px 0 10px; }}
      .panel.price-map-wrap {{ padding-left: 0; padding-right: 0; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <p class="muted">{esc(timestamp_jst)} / signal_id {esc(result.get('signal_id', ''))}</p>
      <div class="hero-kicker">{esc(notification_context.get('final_rank_emoji', ''))} {esc(notification_context.get('final_rank_label', '送信なし'))} / {esc(notification_context.get('status_label', '中立'))}</div>
      <h1>{esc(subject)}</h1>
      <p class="hero-summary">{esc(active_hero_label)}</p>
      <p class="hero-sub">{esc(active_hero_summary)}</p>
      <div>{chips_html(summary_chips)}</div>
      <div class="overview-grid">
        <div class="verdict-card">
          <h2>最初に読む結論</h2>
          <ul class="summary-list">
            <li><span class="emoji">🎯</span><div><strong>Active Plan:</strong> {esc(active_hero_label)}</div></li>
            <li><span class="emoji">🧩</span><div><strong>今の行動:</strong> {esc(active_hero_label)}</div></li>
            {active_status_rows_html}
          </ul>
          <div class="takeaway">まず方向ではなく、実際に取れる行動を確認します。今回は <strong>{esc(active_hero_label)}</strong> です。</div>
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
      <h2>手動アクション確認</h2>
      <div class="panel">
        <p><strong>{esc(active_hero_label)}</strong> を前提に、いま手で確かめる要点だけを並べます。</p>
        <p class="muted">{esc(active_hero_summary)}</p>
        <div class="checklist">{checklist_html}</div>
        <div class="checklist-note">この確認は、判断ソースを見やすくまとめるだけで、売買ロジックは変更しません。</div>
      </div>
    </section>

    <section class="section">
      <h2>3つの数字を丁寧に読む</h2>
      <div class="metric-grid">{''.join(metric_blocks)}</div>
    </section>

    <section class="section">
      <h2>再検討ラインチャート</h2>
      <div class="panel price-map-wrap">
        <h3>4時間足 → 1時間足 → 15分足 の順で見ます</h3>
        <p>上段は大きな流れ、中段は再検討帯の妥当性、下段は実際に入る価格と SL / TP の精度を見る段です。いちばん重要なのは下段の 15 分足です。</p>
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
            <li>上段と中段は「その帯が自然か」を見る段、下段は「その価格で実際に入れるか」を見る段です。</li>
            <li>点線は SL と TP で、15分足ではどこで切るか・利確するかを直接確認できます。</li>
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
          <p><strong>15分足 執行チェック:</strong> {esc(_execution_precision_line(result, 'long'))}</p>
        </div>
        <div class="panel">
          <h3>ショート</h3>
          <p>{esc(_setup_line(result, 'short'))}</p>
          <p><strong>15分足 執行チェック:</strong> {esc(_execution_precision_line(result, 'short'))}</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>待機理由または注意点</h2>
      <div class="reason-grid">{reason_cards_html}</div>
      <ul>{wait_reason_html}</ul>
    </section>

    <section class="section">
      <h2>Ver03-v4 手動確認サポート</h2>
      <div class="panel">
        <p>この公開HTMLレポートは現在の手動取引判断のmain UI。</p>
        <p>通知メールは入口。</p>
        <p>local dashboard / app surface は確認と将来の承認・自動化の土台。</p>
        <p>3つは同じ判断ソースから出します。別判断系にしません。</p>
        <p><strong>安全境界:</strong> report-only / not FORMAL_GO / no automatic order / human decides manually</p>
        <ul>{manual_support_reference_list_html}</ul>
      </div>
    </section>

    {(
      f'''
    <section class="section">
      <h2>AI監査メモ</h2>
      <div class="two-col">
        <div class="panel">
          <h3>{esc(ai_audit_headline)}</h3>
          <p>{esc(audit_reason or '監査理由はありません')}</p>
          <h3>次の確認観点</h3>
          <p>{esc(audit_next or '追加の確認観点はありません')}</p>
        </div>
        <div class="panel">
          <h3>追加リスク</h3>
          <ul>{ai_audit_unique_risk_html or '<li>追加リスクはありません</li>'}</ul>
        </div>
      </div>
    </section>
      '''
      if show_ai_audit
      else ''
    )}

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


def _notification_remote_hosts(cfg: Any) -> list[str]:
    configured = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_SSH_HOST", "maruPro@192.168.50.5")).strip()
    candidates = [
        configured,
        "maruPro@macserver.afrog.jp",
        "maruPro@192.168.50.5",
    ]
    hosts: list[str] = []
    seen: set[str] = set()
    for host in candidates:
        normalized = str(host).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        hosts.append(normalized)
    return hosts


def _notification_ssh_args(cfg: Any) -> list[str]:
    args = ["-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]
    key_path = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_SSH_KEY", "~/.ssh/id_ed25519_afrog_lan")).strip()
    if key_path:
        expanded = str(Path(key_path).expanduser())
        args.extend(["-i", expanded])
    return args


def publish_notification_detail(base_dir: Path, cfg: Any, result: dict[str, Any]) -> dict[str, Any]:
    local_path, public_url = detail_page_paths(base_dir, cfg, result)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(build_notification_detail_html(result), encoding="utf-8")

    remote_root = str(getattr(cfg, "NOTIFICATION_HTML_REMOTE_DIR", "/Volumes/Server_HD2/site/btc-monitor/notifications")).strip()
    system_slug = slugify_label(result.get("system_label"))
    notification_kind = str(result.get("notification_kind", "main")).strip().lower() or "main"
    remote_dir = f"{remote_root.rstrip('/')}/{system_slug}/{notification_kind}"
    publish_errors: list[str] = []
    remote_host_used = ""
    ssh_args = _notification_ssh_args(cfg)
    for remote_host in _notification_remote_hosts(cfg):
        remote_path = f"{remote_dir}/{local_path.name}"
        try:
            subprocess.run(
                ["ssh", *ssh_args, remote_host, "mkdir", "-p", remote_dir],
                check=True,
                capture_output=True,
                text=True,
                timeout=20,
            )
            subprocess.run(
                ["rsync", "-a", "-e", " ".join(["ssh", *ssh_args]), str(local_path), f"{remote_host}:{remote_path}"],
                check=True,
                capture_output=True,
                text=True,
                timeout=20,
            )
            remote_host_used = remote_host
            break
        except Exception as exc:  # noqa: BLE001
            publish_errors.append(f"{remote_host}: {exc}")
    if not remote_host_used:
        raise RuntimeError(" / ".join(publish_errors) or "notification detail publish failed")
    return {
        "detail_page_enabled": True,
        "detail_page_status": "published",
        "detail_page_url": public_url,
        "detail_page_local_path": str(local_path),
        "detail_page_remote_host": remote_host_used,
        "detail_page_published_at_utc": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def append_detail_page_url(body: str, url: str) -> str:
    if not str(url).strip():
        return body
    if str(url) in str(body):
        return body
    base = str(body).rstrip()
    return f"{base}\n\n【詳細ページ】\n{url}\n"
