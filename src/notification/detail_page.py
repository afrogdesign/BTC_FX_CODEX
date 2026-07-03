from __future__ import annotations

import json
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
from src.notification.intraperiod_breakout import build_intraperiod_breakout_alert_candidate


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

CURRENT_MANUAL_SUPPORT_HEADER = "内部確認・検証情報"

_VISIBLE_STATUS_LABELS = {
    "blocked": "見送り",
    "allowed": "監視可",
    "conditional": "条件付き",
    "pass": "通過",
    "ready": "準備済み",
    "watch": "監視継続",
    "invalid": "無効",
    "none": "なし",
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


def _humanize_visible_status_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "未記録"
    for raw, label in _VISIBLE_STATUS_LABELS.items():
        text = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(raw)}(?![A-Za-z0-9_])", label, text, flags=re.IGNORECASE)
    return text


def _sentence_join(parts: list[str]) -> str:
    sentences = [str(part).strip().strip("。") for part in parts if str(part).strip()]
    if not sentences:
        return "未記録"
    return "。".join(sentences) + "。"


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
        (
            "成行",
            f"ロング: {_humanize_visible_status_text(market.get('long', 'blocked'))} / ショート: {_humanize_visible_status_text(market.get('short', 'blocked'))}",
        ),
        (
            "指値・戻り待ち",
            f"ロング: {_humanize_visible_status_text(limit.get('long', 'blocked'))} / ショート: {_humanize_visible_status_text(limit.get('short', 'blocked'))}",
        ),
        (
            "ブレイク追随",
            f"ロング: {_humanize_visible_status_text(breakout.get('long', 'blocked'))} / ショート: {_humanize_visible_status_text(breakout.get('short', 'blocked'))}",
        ),
        (
            "逆方向短期",
            f"ロング: {_humanize_visible_status_text(counter.get('long', 'blocked'))} / ショート: {_humanize_visible_status_text(counter.get('short', 'blocked'))}",
        ),
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
    right = width - 162
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
    overlay_elements: list[str] = []
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
            opacity = "0.24" if emphasize_setup else "0.12"
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
            text_class = "setup-band-text-long" if side == "long" else "setup-band-text-short"
            text_x = setup_x + 10 if side == "long" else setup_x + setup_w - 10
            text_anchor = "start" if side == "long" else "end"
            text_y = max(top + 18, min(bottom - 8, y1 + 16))
            if panel_mode == "execution":
                setup_elements.append(
                    f'<text x="{text_x:.1f}" y="{text_y:.1f}" text-anchor="{text_anchor}" class="{text_class}">浅い再検討帯</text>'
                )

        if panel_mode in {"zone", "execution"}:
            lane_x_map = {
                "long": left + chart_width * 0.08,
                "short": left + chart_width * 0.58,
            }
            lane_w = chart_width * 0.34

            def _layer_zone(value: Any) -> tuple[float, float] | None:
                if not isinstance(value, dict):
                    return None
                low = _safe_float(value.get("low"))
                high = _safe_float(value.get("high"))
                if min(low, high) <= 0:
                    return None
                return low, high

            def _overlay_zone_rect(
                *,
                zone: tuple[float, float] | None,
                x: float,
                width_value: float,
                rect_class: str,
                label_class: str,
                label: str,
                text_anchor: str,
                text_x: float,
                show_label: bool,
            ) -> None:
                if zone is None:
                    return
                low, high = zone
                y1 = y_for_price(high)
                y2 = y_for_price(low)
                overlay_elements.append(
                    f'<rect x="{x:.1f}" y="{y1:.1f}" width="{width_value:.1f}" height="{max(y2 - y1, 10):.1f}" rx="9" class="{rect_class}" />'
                )
                if show_label:
                    overlay_elements.append(
                        f'<text x="{text_x:.1f}" y="{max(top + 18, min(bottom - 8, y1 + 16)):.1f}" text-anchor="{text_anchor}" class="{label_class}">{html.escape(label)}</text>'
                    )

            def _overlay_trigger_line(
                *,
                price: Any,
                x1: float,
                x2: float,
                line_class: str,
                label_class: str,
                label: str,
                text_anchor: str,
                text_x: float,
                text_y: float,
                show_label: bool,
            ) -> None:
                value = _safe_float(price)
                if value <= 0:
                    return
                y = y_for_price(value)
                overlay_elements.append(
                    f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" class="{line_class}" />'
                )
                if show_label:
                    overlay_elements.append(
                        f'<text x="{text_x:.1f}" y="{text_y:.1f}" text-anchor="{text_anchor}" class="{label_class}">{html.escape(label)} {_format_price_int(value)}</text>'
                    )

            for side, setup in (("long", long_setup), ("short", short_setup)):
                layer = setup.get("value_defense_entry_layer")
                if not isinstance(layer, dict) or layer.get("schema_version") != "value_defense_entry_layer.v1":
                    continue
                lane_x = lane_x_map[side]
                lane_text_x = lane_x + 8 if side == "long" else lane_x + lane_w - 8
                lane_anchor = "start" if side == "long" else "end"
                value_class = "value-defense-band-long" if side == "long" else "value-defense-band-short"
                value_text_class = "value-defense-band-text-long" if side == "long" else "value-defense-band-text-short"
                invalidation_class = "invalidation-band-long" if side == "long" else "invalidation-band-short"
                invalidation_text_class = "invalidation-band-text-long" if side == "long" else "invalidation-band-text-short"
                trigger_class = "value-defense-trigger-long" if side == "long" else "value-defense-trigger-short"
                trigger_text_class = "value-defense-trigger-text-long" if side == "long" else "value-defense-trigger-text-short"
                show_band_labels = False
                show_trigger_labels = False

                _overlay_zone_rect(
                    zone=_layer_zone(layer.get("value_defense_zone")),
                    x=lane_x,
                    width_value=lane_w,
                    rect_class=value_class,
                    label_class=value_text_class,
                    label="本命防衛ゾーン",
                    text_anchor=lane_anchor,
                    text_x=lane_text_x,
                    show_label=show_band_labels,
                )
                _overlay_zone_rect(
                    zone=_layer_zone(layer.get("invalidation_zone")),
                    x=lane_x,
                    width_value=lane_w,
                    rect_class=invalidation_class,
                    label_class=invalidation_text_class,
                    label="無効化",
                    text_anchor=lane_anchor,
                    text_x=lane_text_x,
                    show_label=show_band_labels,
                )

                trigger_specs = [
                    ("回収条件", layer.get("reclaim_trigger"), max(top + 28, min(bottom - 24, top + 44))),
                    ("継続条件", layer.get("continuation_trigger"), max(top + 44, min(bottom - 10, top + 60))),
                ]
                for label, price, text_y in trigger_specs:
                    _overlay_trigger_line(
                        price=price,
                        x1=lane_x,
                        x2=lane_x + lane_w,
                        line_class=trigger_class,
                        label_class=trigger_text_class,
                        label=label,
                        text_anchor=lane_anchor,
                        text_x=lane_text_x,
                        text_y=text_y,
                        show_label=show_trigger_labels,
                    )

    current_y = y_for_price(current_price)
    current_label_y = max(top + 10, min(bottom - 4, current_y + 4))
    emphasis_lines: list[str] = [
        f'<line x1="{left}" y1="{current_y:.1f}" x2="{right}" y2="{current_y:.1f}" class="current-price-line" />',
        f'<text x="{left - 8:.1f}" y="{current_label_y:.1f}" text-anchor="end" class="current-price-label">現在値 {_format_price_int(current_price)}</text>',
    ]

    markers: list[str] = []
    if show_markers:
        def marker_spec(price: Any, label: str, tone: str, x1_ratio: float, x2_ratio: float, anchor: str) -> dict[str, Any] | None:
            value = _safe_float(price)
            if value <= 0:
                return None
            y = y_for_price(value)
            x1 = left + chart_width * x1_ratio
            x2 = left + chart_width * x2_ratio
            return {
                "line": f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" class="marker-line {tone}" />',
                "y": y,
                "label_x": x2 + 10 if anchor == "start" else x1 - 10,
                "anchor": anchor,
                "tone": tone,
                "text": f"{label} {_format_price_int(value)}",
            }

        def stack_marker_specs(
            specs: list[dict[str, Any]],
            *,
            top_limit: float,
            bottom_limit: float,
            min_gap: float = 18.0,
        ) -> list[dict[str, Any]]:
            if not specs:
                return []
            ordered = sorted(specs, key=lambda item: float(item["y"]))
            adjusted: list[dict[str, Any]] = []
            for spec in ordered:
                y = float(spec["y"])
                if adjusted and y < adjusted[-1]["y"] + min_gap:
                    y = adjusted[-1]["y"] + min_gap
                adjusted.append({**spec, "y": y})
            overflow = adjusted[-1]["y"] - bottom_limit
            if overflow > 0:
                adjusted = [{**spec, "y": float(spec["y"]) - overflow} for spec in adjusted]
            underflow = top_limit - adjusted[0]["y"]
            if underflow > 0:
                adjusted = [{**spec, "y": float(spec["y"]) + underflow} for spec in adjusted]
            return adjusted

        long_specs = [
            spec
            for spec in (
                marker_spec(long_setup.get("stop_loss"), "Long SL", "marker-long", 0.03, 0.16, "start"),
                marker_spec(long_setup.get("tp1"), "Long TP1", "marker-long", 0.03, 0.16, "start"),
                marker_spec(long_setup.get("tp2"), "Long TP2", "marker-long", 0.03, 0.16, "start"),
            )
            if spec is not None
        ]
        short_specs = [
            spec
            for spec in (
                marker_spec(short_setup.get("stop_loss"), "Short SL", "marker-short", 0.84, 0.97, "end"),
                marker_spec(short_setup.get("tp1"), "Short TP1", "marker-short", 0.84, 0.97, "end"),
                marker_spec(short_setup.get("tp2"), "Short TP2", "marker-short", 0.84, 0.97, "end"),
            )
            if spec is not None
        ]
        markers.extend(
            f'{spec["line"]}<text x="{float(spec["label_x"]):.1f}" y="{float(spec["y"]) + 4:.1f}" text-anchor="{spec["anchor"]}" class="marker-label {spec["tone"]}">{html.escape(str(spec["text"]))}</text>'
            for spec in stack_marker_specs(long_specs, top_limit=top + 8, bottom_limit=bottom - 8)
            + stack_marker_specs(short_specs, top_limit=top + 8, bottom_limit=bottom - 8)
        )

    return (
        f'<g class="price-map-panel {"price-map-panel-focus" if show_markers else ""}">'
        f'<rect x="0" y="{origin_y}" width="{width}" height="{height}" rx="18" class="price-map-bg" />'
        f'<text x="22" y="{origin_y + 22}" class="chart-title">{html.escape(title)}</text>'
        f'<text x="22" y="{origin_y + 40}" class="chart-subtitle">{html.escape(subtitle)}</text>'
        f"{''.join(grid_lines)}"
        f"{''.join(vertical_grid)}"
        f"{''.join(background_bands)}"
        f"{''.join(overlay_elements)}"
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
            subtitle="再検討帯が押し目 / 戻りとして自然かを見る段です。利確 / 損切りはここでは見ません",
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


def _value_defense_entry_layer_zone_text(value: Any) -> str:
    if not isinstance(value, dict):
        return "抽出なし"
    low = _format_price(value.get("low"))
    high = _format_price(value.get("high"))
    if low == "未記録" or high == "未記録":
        return "抽出なし"
    return f"{low} - {high}"


def _value_defense_entry_layer_block(result: dict[str, Any], side: str) -> str:
    setup = result.get("long_setup", {}) if side == "long" else result.get("short_setup", {})
    layer = setup.get("value_defense_entry_layer")
    if not isinstance(layer, dict) or not layer or layer.get("schema_version") != "value_defense_entry_layer.v1":
        return ""

    side_label = "ロング" if side == "long" else "ショート"
    lines = [
        ("浅い再検討帯", _value_defense_entry_layer_zone_text(layer.get("shallow_retest_zone"))),
        ("浅い再検討リスク", str(layer.get("shallow_retest_risk") or "未記録")),
        ("本命防衛ゾーン", _value_defense_entry_layer_zone_text(layer.get("value_defense_zone"))),
        ("無効化", _value_defense_entry_layer_zone_text(layer.get("invalidation_zone"))),
        ("回収条件", _format_price(layer.get("reclaim_trigger"))),
        ("継続条件", _format_price(layer.get("continuation_trigger"))),
        ("局面", str(layer.get("lifecycle_state") or "未記録")),
        ("運用メモ", str(layer.get("operator_guidance") or "未記録")),
        ("安全境界", str(layer.get("safety_boundary") or "report-only / not FORMAL_GO / no automatic order / human decides manually")),
    ]
    list_html = "".join(
        f"<li><strong>{html.escape(str(label))}:</strong> {html.escape(str(value))}</li>"
        for label, value in lines
    )
    return (
        '<div class="panel">'
        f"<h3>{html.escape(side_label)} / 本命防衛ゾーン</h3>"
        "<p>浅い再検討帯と本命防衛ゾーンを分けて見る補助欄です。売買指示ではありません。</p>"
        f"<ul>{list_html}</ul>"
        "</div>"
    )


def _value_defense_chart_card(result: dict[str, Any], side: str) -> str:
    setup = result.get("long_setup", {}) if side == "long" else result.get("short_setup", {})
    layer = setup.get("value_defense_entry_layer")
    if not isinstance(layer, dict) or not layer or layer.get("schema_version") != "value_defense_entry_layer.v1":
        return ""

    side_label = "ロング" if side == "long" else "ショート"
    tone = "long" if side == "long" else "short"
    items = [
        ("浅い再検討帯", _value_defense_entry_layer_zone_text(layer.get("shallow_retest_zone"))),
        ("本命防衛ゾーン", _value_defense_entry_layer_zone_text(layer.get("value_defense_zone"))),
        ("無効化", _value_defense_entry_layer_zone_text(layer.get("invalidation_zone"))),
        ("回収条件", _format_price(layer.get("reclaim_trigger"))),
        ("継続条件", _format_price(layer.get("continuation_trigger"))),
    ]
    rows_html = "".join(
        '<div class="value-defense-card-row">'
        f'<span class="value-defense-card-key">{html.escape(label)}</span>'
        f'<span class="value-defense-card-value">{html.escape(value)}</span>'
        "</div>"
        for label, value in items
    )
    return (
        f'<div class="value-defense-chart-card {tone}">'
        f'<div class="value-defense-card-head"><span class="value-defense-card-pill {tone}">{side_label}</span><strong>Value Defense</strong></div>'
        f"{rows_html}"
        "</div>"
    )


def _value_defense_chart_dashboard(result: dict[str, Any]) -> str:
    cards = "".join(
        card for card in (
            _value_defense_chart_card(result, "long"),
            _value_defense_chart_card(result, "short"),
        ) if card
    )
    if not cards:
        return ""
    return f'<div class="value-defense-dashboard">{cards}</div>'


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


def _major_turning_point_opportunity_items(
    result: dict[str, Any],
    display_context: dict[str, Any],
    notification_context: dict[str, Any],
    active_hero_summary: str,
    display_reasons: list[str],
) -> list[tuple[str, str]]:
    wait_reasons = [str(reason).strip() for reason in display_reasons if str(reason).strip()]
    return [
        ("相場環境", _label_regime(result.get("market_regime"))),
        ("今の局面", _label_phase(result.get("phase"))),
        (
            "時間軸の揃い方",
            _sentence_join(
                [
                    f"4時間足 {_label_signal(result.get('signals_4h'))}",
                    f"1時間足 {_label_signal(result.get('signals_1h'))}",
                    f"15分足 {_label_signal(result.get('signals_15m'))}",
                ]
            ),
        ),
        (
            "ロング/ショートの傾き",
            _sentence_join(
                [
                    f"ロング {result.get('long_display_score')}",
                    f"ショート {result.get('short_display_score')}",
                    f"スコア差 {result.get('score_gap')}",
                ]
            ),
        ),
        (
            "入る条件の確認",
            _sentence_join(
                [
                    _humanize_visible_status_text(notification_context.get("execution_label", "")).strip() or "未記録",
                    str(notification_context.get("entry_window_label", "")).strip() or "未記録",
                    str(display_context.get("entry_quality_label", "")).strip() or "未記録",
                    active_hero_summary or "未記録",
                ]
            ),
        ),
        (
            "無効化・待機理由",
            _sentence_join(
                [
                    str(notification_context.get("invalidation_label", "")).strip() or "未記録",
                    str(notification_context.get("next_condition_label", "")).strip() or "未記録",
                    "、".join(wait_reasons) or "未記録",
                ]
            ),
        ),
        (
            "価格帯の確認",
            _sentence_join(
                [
                    f"現在価格 {_format_price(result.get('current_price'))}",
                    _zone_summary("近いサポート帯", result.get("support_zones", [])),
                    _zone_summary("近いレジスタンス帯", result.get("resistance_zones", [])),
                    _setup_line(result, "long"),
                    _setup_line(result, "short"),
                ]
            ),
        ),
        (
            "見る順番",
            "大転換は 4h → 1h → 15m の順で根拠を確認します。15分足だけの反応で決め打ちしません。"
            "スコア差が小さいときは大転換候補とダマシ注意を取り違えやすいので、主要サポート・レジスタンス付近では反転・ブレイク・失敗の3択を確認します。"
            "入る条件・無効化条件・次の確認点がそろうまでは、決め打ちしません。",
        ),
        ("安全境界", "report-only / not FORMAL_GO / no automatic order / human decides manually"),
    ]


def _breakout_inversion_items(result: dict[str, Any]) -> list[tuple[str, str]]:
    flags = {str(flag).strip() for flag in result.get("breakout_inversion_flags", []) if str(flag).strip()}
    for setup_key in ("short_setup", "long_setup"):
        setup = result.get(setup_key, {})
        if isinstance(setup, dict):
            flags.update(
                str(flag).strip()
                for flag in setup.get("execution_precision_flags", [])
                if str(flag).strip()
            )

    items: list[tuple[str, str]] = []
    upside_flags = {
        "upside_breakout_follow_watch",
        "short_invalidation_watch",
        "short_invalidated_by_up_break",
    }
    downside_flags = {
        "downside_breakdown_follow_watch",
        "long_invalidation_watch",
        "long_invalidated_by_down_break",
    }
    if flags & upside_flags:
        items.append(
            (
                "上抜け追随候補",
                _sentence_join(
                    [
                        "ショート根拠は弱まりつつあります",
                        "15分足で上に維持できるか確認",
                        "すぐ下に戻るならダマシ注意",
                    ]
                ),
            )
        )
    if flags & downside_flags:
        items.append(
            (
                "下抜け追随候補",
                _sentence_join(
                    [
                        "ロング根拠は弱まりつつあります",
                        "15分足で下に維持できるか確認",
                        "すぐ上に戻るならダマシ注意",
                    ]
                ),
            )
        )
    return items


def _intraperiod_breakout_items(result: dict[str, Any]) -> list[tuple[str, str]]:
    candidate = result.get("intraperiod_breakout_alert_candidate")
    if not isinstance(candidate, dict):
        candidate = build_intraperiod_breakout_alert_candidate(result)
    if str(candidate.get("status", "")).strip() != "candidate":
        return []

    side = str(candidate.get("side", "none")).strip()
    reason_codes = {str(code).strip() for code in candidate.get("reason_codes", []) if str(code).strip()}
    items: list[tuple[str, str]] = []

    if side in {"upside", "both"}:
        value_parts = [
            "ショート方向は損失リスクが高いので、15分足で上に維持できるか確認",
            "すぐ下に戻るならダマシ注意",
        ]
        if "upside_macd_confirmed" in reason_codes:
            value_parts.append("MACDは上方向の勢いを補強")
        items.append(("上抜け初動の可能性", _sentence_join(value_parts)))

    if side in {"downside", "both"}:
        value_parts = [
            "ロング方向は損失リスクが高いので、15分足で下に維持できるか確認",
            "すぐ上に戻るならダマシ注意",
        ]
        if "downside_macd_confirmed" in reason_codes:
            value_parts.append("MACDは下方向の勢いを補強")
        items.append(("下抜け初動の可能性", _sentence_join(value_parts)))

    items.append(("安全境界", str(candidate.get("safety_boundary", "report-only / not FORMAL_GO / no automatic order / human decides manually"))))
    return items


def _momentum_confirmation_items(result: dict[str, Any]) -> list[tuple[str, str]]:
    flags = {str(flag).strip() for flag in result.get("momentum_confirmation_flags", []) if str(flag).strip()}
    items: list[tuple[str, str]] = []
    upside_flags = {
        "upside_momentum_confirmed",
        "upside_ema_supportive",
        "upside_rsi_has_room",
        "upside_volume_confirmed",
        "short_countertrend_risk",
    }
    downside_flags = {
        "downside_momentum_confirmed",
        "downside_ema_supportive",
        "downside_rsi_has_room",
        "downside_volume_confirmed",
        "long_countertrend_risk",
    }
    if flags & upside_flags:
        items.append(
            (
                "上抜け後の勢い確認",
                _sentence_join(
                    [
                        "ショート方向は危険",
                        "15分足で上に維持できるか確認",
                        "すぐ下に戻るならダマシ注意",
                    ]
                ),
            )
        )
    if flags & downside_flags:
        items.append(
            (
                "下抜け後の勢い確認",
                _sentence_join(
                    [
                        "ロング方向は危険",
                        "15分足で下に維持できるか確認",
                        "すぐ上に戻るならダマシ注意",
                    ]
                ),
            )
        )
    return items


def _major_turning_point_diagnostic_evidence(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    direct_evidence = result.get("major_turning_point_diagnostic")
    if isinstance(direct_evidence, dict):
        return direct_evidence
    for container in (
        notification_context or {},
        display_context or {},
        result.get("app_contract") if isinstance(result.get("app_contract"), dict) else {},
        result.get("app_contract_data") if isinstance(result.get("app_contract_data"), dict) else {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict):
            evidence = container.get("major_turning_point_diagnostic")
            if isinstance(evidence, dict):
                return evidence
    return None


def _major_turning_point_diagnostic_value(value: Any) -> str:
    if value is None:
        return "not recorded"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, (list, tuple)):
        if not value:
            return "none"
        return ", ".join(str(item) for item in value)
    text = str(value).strip()
    return text or "not recorded"


def _major_turning_point_diagnostic_row_text(row: dict[str, Any]) -> str:
    fields = (
        ("diagnostic_label", "diagnostic_label"),
        ("candidate_id", "candidate_id"),
        ("signal_id", "signal_id"),
        ("timestamp_jst", "timestamp_jst"),
        ("candidate_type", "candidate_type"),
        ("active_primary_action", "active_primary_action"),
        ("side", "side"),
        ("entry_mode", "entry_mode"),
        ("outcome", "outcome"),
        ("first_exit_reason", "first_exit_reason"),
        ("entry_reached_time", "entry_reached_time"),
        ("mfe_r", "mfe_r"),
        ("mae_r", "mae_r"),
    )
    return " / ".join(f"{label}: {_major_turning_point_diagnostic_value(row.get(key))}" for label, key in fields)


def _major_turning_point_diagnostic_items(
    result: dict[str, Any],
    notification_context: dict[str, Any],
    display_context: dict[str, Any],
) -> tuple[list[tuple[str, str]], list[dict[str, Any]], str]:
    evidence = _major_turning_point_diagnostic_evidence(result, notification_context, display_context)
    if not isinstance(evidence, dict) or not evidence:
        return [], [], ""
    counts = evidence.get("counts") if isinstance(evidence.get("counts"), dict) else {}
    representative_rows = evidence.get("representative_rows")
    rows: list[dict[str, Any]] = [row for row in representative_rows if isinstance(row, dict)] if isinstance(
        representative_rows, list
    ) else []
    items = [
        ("Summary status", _major_turning_point_diagnostic_value(evidence.get("summary_status"))),
        ("Total rows", _major_turning_point_diagnostic_value(evidence.get("total_rows"))),
        ("potential_missed_turn", _major_turning_point_diagnostic_value(counts.get("potential_missed_turn"))),
        ("potential_fakeout", _major_turning_point_diagnostic_value(counts.get("potential_fakeout"))),
        ("bad_entry_timing", _major_turning_point_diagnostic_value(counts.get("bad_entry_timing"))),
        ("inconclusive", _major_turning_point_diagnostic_value(counts.get("inconclusive"))),
        ("Safety boundary", _major_turning_point_diagnostic_value(evidence.get("safety_boundary"))),
        ("Note", _major_turning_point_diagnostic_value(evidence.get("note"))),
    ]
    rows_html = "".join(
        "<div class=\"checklist-item\">"
        f"<div class=\"checklist-label\">🧾 <span>Representative row {idx}</span></div>"
        f"<div class=\"checklist-value\">{html.escape(_major_turning_point_diagnostic_row_text(row))}</div>"
        "</div>"
        for idx, row in enumerate(rows[:5], 1)
    )
    return items, rows, rows_html


def _safe_config_schema_audit_html(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> str:
    evidence: dict[str, Any] | None = None
    for container in (
        result,
        notification_context or {},
        display_context or {},
        result.get("app_contract") if isinstance(result.get("app_contract"), dict) else {},
        result.get("app_contract_data") if isinstance(result.get("app_contract_data"), dict) else {},
    ):
        if isinstance(container, dict) and isinstance(container.get("safe_config_schema_audit"), dict):
            evidence = container["safe_config_schema_audit"]
            break
    if not isinstance(evidence, dict) or not evidence:
        return ""

    def _value(key: str) -> str:
        value = evidence.get(key)
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value)

    rows = [
        ("command", _value("command")),
        ("stdout JSON command", _value("stdout_json_command")),
        ("schema_version", _value("schema_version")),
        ("contract_only", _value("contract_only")),
        ("command_executed_by_app", _value("command_executed_by_app")),
        ("reads_env_values", _value("reads_env_values")),
        ("reads_dotenv_values", _value("reads_dotenv_values")),
        ("calls_private_endpoints", _value("calls_private_endpoints")),
        ("calls_order_endpoints", _value("calls_order_endpoints")),
        ("live_trading_allowed", _value("live_trading_allowed")),
        ("secret_values_exposed", _value("secret_values_exposed")),
        ("safety boundary", _value("safety_boundary")),
    ]
    rows_html = "".join(
        f"<li><strong>{html.escape(label)}:</strong> {html.escape(value)}</li>" for label, value in rows
    )
    return f"""
        <h3>Safe Config Schema Audit</h3>
        <p>local/report-only の静的監査サポートです。<code>tools/safe_config_schema_audit.py</code> は実行しません。</p>
        <p><strong>安全境界:</strong> local/report-only / no load_config / no .env / no os.environ / no secret/API key exposure / no exchange/private/account/order endpoint access / no FORMAL_GO / no automatic order</p>
        <p>app surface は契約にある安全な診断情報だけを表示し、結果を推測しません。</p>
        <ul>{rows_html}</ul>
    """


def _operator_triage_summary_html(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> str:
    evidence: dict[str, Any] | None = None
    for container in (
        result,
        notification_context or {},
        display_context or {},
        result.get("app_contract") if isinstance(result.get("app_contract"), dict) else {},
        result.get("app_contract_data") if isinstance(result.get("app_contract_data"), dict) else {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict) and isinstance(container.get("operator_triage_summary"), dict):
            evidence = container["operator_triage_summary"]
            break
    if not isinstance(evidence, dict) or not evidence:
        return ""

    def _value(key: str, subkey: str | None = None) -> str:
        direct_key = f"{key}_{subkey}" if subkey else key
        value = evidence.get(direct_key)
        if value is None and subkey is not None:
            nested = evidence.get(key)
            if isinstance(nested, dict):
                value = nested.get(subkey)
            nested_container = evidence.get("evidence")
            if value is None and isinstance(nested_container, dict):
                nested = nested_container.get(key)
                if isinstance(nested, dict):
                    value = nested.get(subkey)
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        if value is None:
            return "not recorded"
        text = str(value).strip()
        return text or "not recorded"

    rows = [
        ("summary_status", _value("summary_status")),
        ("all_evidence_present", _value("all_evidence_present")),
        ("all_evidence_ready", _value("all_evidence_ready")),
        ("operator_status_diagnostic present", _value("operator_status_diagnostic", "present")),
        ("operator_status_diagnostic ready", _value("operator_status_diagnostic", "ready")),
        ("safe_config_schema_audit present", _value("safe_config_schema_audit", "present")),
        ("safe_config_schema_audit ready", _value("safe_config_schema_audit", "ready")),
        ("intraperiod_review_stdout_json present", _value("intraperiod_review_stdout_json", "present")),
        ("intraperiod_review_stdout_json ready", _value("intraperiod_review_stdout_json", "ready")),
        ("manual_action_checklist_surface present", _value("manual_action_checklist_surface", "present")),
        ("manual_action_checklist_surface ready", _value("manual_action_checklist_surface", "ready")),
        ("safety_boundary", _value("safety_boundary")),
        ("note", _value("note")),
    ]
    rows_html = "".join(
        f"<li><strong>{html.escape(label)}:</strong> {html.escape(value)}</li>" for label, value in rows
    )
    return f"""
        <h3>Operator Triage Summary</h3>
        <p>local/report-only の表示です。既存の契約データだけを使い、app surface はこの診断を実行しません。</p>
        <p><strong>安全境界:</strong> report-only / not FORMAL_GO / no automatic order / human decides manually</p>
        <ul>{rows_html}</ul>
    """


def _integrated_evidence_overview_html(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> str:
    evidence: dict[str, Any] | None = None
    for container in (
        result,
        notification_context or {},
        display_context or {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict) and isinstance(container.get("integrated_evidence_overview"), dict):
            evidence = container["integrated_evidence_overview"]
            break
    if not isinstance(evidence, dict) or not evidence:
        return ""

    def _value(key: str, subkey: str | None = None) -> str:
        direct_key = f"{key}_{subkey}" if subkey else key
        value = evidence.get(direct_key)
        if value is None and subkey is not None:
            nested = evidence.get(key)
            if isinstance(nested, dict):
                value = nested.get(subkey)
            nested_container = evidence.get("evidence")
            if value is None and isinstance(nested_container, dict):
                nested = nested_container.get(key)
                if isinstance(nested, dict):
                    value = nested.get(subkey)
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            return "none" if not value else ", ".join(str(item) for item in value)
        if value is None:
            return "not recorded"
        text = str(value).strip()
        return text or "not recorded"

    def _list_value(key: str) -> str:
        for candidate in (
            evidence.get(key),
            result.get(f"integrated_evidence_overview_{key}"),
            result.get(key),
        ):
            if isinstance(candidate, list):
                return "none" if not candidate else ", ".join(str(item) for item in candidate)
            if isinstance(candidate, tuple):
                return "none" if not candidate else ", ".join(str(item) for item in candidate)
        return "not recorded"

    def _hint_value(field: str) -> str:
        for candidate in (
            evidence.get(field),
            result.get(f"integrated_evidence_overview_{field}"),
            result.get(field),
        ):
            if candidate is None:
                continue
            if isinstance(candidate, bool):
                return str(candidate).lower()
            if isinstance(candidate, list):
                return "none" if not candidate else ", ".join(str(item) for item in candidate)
            if isinstance(candidate, tuple):
                return "none" if not candidate else ", ".join(str(item) for item in candidate)
            text = str(candidate).strip()
            return text or "not recorded"
        return "not recorded"

    rows = [
        ("summary_status", _value("summary_status")),
        ("all_evidence_present", _value("all_evidence_present")),
        ("all_evidence_ready", _value("all_evidence_ready")),
        ("operator_hint_status", _hint_value("operator_hint_status")),
        ("operator_hint_reason", _hint_value("operator_hint_reason")),
        ("operator_hint_next_action", _hint_value("operator_hint_next_action")),
        ("evidence_keys", _list_value("evidence_keys")),
        ("missing_evidence_keys", _list_value("missing_evidence_keys")),
        ("not_ready_evidence_keys", _list_value("not_ready_evidence_keys")),
        ("execution_required_keys", _list_value("execution_required_keys")),
        ("intraperiod_review_stdout_json present", _value("intraperiod_review_stdout_json", "present")),
        ("intraperiod_review_stdout_json ready_or_valid", _value("intraperiod_review_stdout_json", "ready_or_valid")),
        ("intraperiod_review_stdout_json execution_required", _value("intraperiod_review_stdout_json", "execution_required")),
        ("operator_status_diagnostic present", _value("operator_status_diagnostic", "present")),
        ("operator_status_diagnostic ready_or_valid", _value("operator_status_diagnostic", "ready_or_valid")),
        ("operator_status_diagnostic execution_required", _value("operator_status_diagnostic", "execution_required")),
        ("safe_config_schema_audit present", _value("safe_config_schema_audit", "present")),
        ("safe_config_schema_audit ready_or_valid", _value("safe_config_schema_audit", "ready_or_valid")),
        ("safe_config_schema_audit execution_required", _value("safe_config_schema_audit", "execution_required")),
        ("operator_triage_summary present", _value("operator_triage_summary", "present")),
        ("operator_triage_summary ready_or_valid", _value("operator_triage_summary", "ready_or_valid")),
        ("operator_triage_summary execution_required", _value("operator_triage_summary", "execution_required")),
        ("manual_action_checklist_surface present", _value("manual_action_checklist_surface", "present")),
        ("manual_action_checklist_surface ready_or_valid", _value("manual_action_checklist_surface", "ready_or_valid")),
        ("manual_action_checklist_surface execution_required", _value("manual_action_checklist_surface", "execution_required")),
        ("safety_boundary", _value("safety_boundary")),
        ("note", _value("note")),
    ]
    rows_html = "".join(
        f"<li><strong>{html.escape(label)}:</strong> {html.escape(value)}</li>" for label, value in rows
    )
    return f"""
        <h3>Integrated Evidence Overview</h3>
        <p>local/report-only の表示です。既存の契約/検証データだけを使い、app surface はこの概要を実行しません。</p>
        <p><strong>安全境界:</strong> report-only / not FORMAL_GO / no automatic order / human decides manually</p>
        <ul>{rows_html}</ul>
    """


def _evidence_quality_summary_html(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> str:
    evidence: dict[str, Any] | None = None
    for container in (
        result,
        notification_context or {},
        display_context or {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict) and isinstance(container.get("evidence_quality_summary"), dict):
            evidence = container["evidence_quality_summary"]
            break
    if not isinstance(evidence, dict) or not evidence:
        return ""

    def _value(key: str) -> str:
        value = evidence.get(key)
        if value is None:
            return "n/a"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
        if isinstance(value, (list, tuple)):
            return "n/a" if not value else ", ".join(str(item) for item in value)
        text = str(value).strip()
        return text or "n/a"

    rows = [
        ("valid_sample_definition", _value("valid_sample_definition")),
        ("total_rows", _value("total_rows")),
        ("no_ohlcv_rows", _value("no_ohlcv_rows")),
        ("valid_sample_rows", _value("valid_sample_rows")),
        ("entry_reached_rows", _value("entry_reached_rows")),
        ("win_like_rows", _value("win_like_rows")),
        ("loss_like_rows", _value("loss_like_rows")),
        ("unresolved_entry_rows", _value("unresolved_entry_rows")),
        ("potential_fakeout", _value("potential_fakeout")),
        ("potential_missed_turn", _value("potential_missed_turn")),
        ("bad_entry_timing", _value("bad_entry_timing")),
        ("safety_note", _value("safety_note")),
    ]
    rows_html = "".join(
        f"<li><strong>{html.escape(label)}:</strong> {html.escape(value)}</li>" for label, value in rows
    )
    return f"""
        <h3>Evidence quality summary</h3>
        <p>local/report-only の表示です。既存の evidence quality 集計だけを使い、app surface はこの概要を実行しません。</p>
        <p><strong>安全境界:</strong> report-only / not FORMAL_GO / no automatic order / human decides manually</p>
        <ul>{rows_html}</ul>
    """


def _ohlcv_source_coverage_summary_html(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> str:
    evidence: dict[str, Any] | None = None
    for container in (
        result,
        notification_context or {},
        display_context or {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
        result.get("manual_delivery_app_surface_validation")
        if isinstance(result.get("manual_delivery_app_surface_validation"), dict)
        else {},
        result.get("current_manual_delivery_app_surface_validation")
        if isinstance(result.get("current_manual_delivery_app_surface_validation"), dict)
        else {},
    ):
        if isinstance(container, dict) and isinstance(container.get("ohlcv_source_coverage_summary"), dict):
            evidence = container["ohlcv_source_coverage_summary"]
            break
    if not isinstance(evidence, dict) or not evidence:
        return ""

    def _value(key: str) -> str:
        value = evidence.get(key)
        if value is None:
            return "n/a"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
        if isinstance(value, (list, tuple)):
            return "n/a" if not value else ", ".join(str(item) for item in value)
        text = str(value).strip()
        return text or "n/a"

    rows = [
        ("candidate_rows", _value("candidate_rows")),
        ("ohlcv_input_rows", _value("ohlcv_input_rows")),
        ("ohlcv_valid_rows", _value("ohlcv_valid_rows")),
        ("candidate_timestamp_rows", _value("candidate_timestamp_rows")),
        ("missing_candidate_timestamp_rows", _value("missing_candidate_timestamp_rows")),
        ("window_covered_rows", _value("window_covered_rows")),
        ("window_missing_rows", _value("window_missing_rows")),
        ("no_global_ohlcv_risk_rows", _value("no_global_ohlcv_risk_rows")),
        ("window_missing_rate", _value("window_missing_rate")),
        ("ohlcv_start", _value("ohlcv_start")),
        ("ohlcv_end", _value("ohlcv_end")),
        ("candidate_timestamp_min", _value("candidate_timestamp_min")),
        ("candidate_timestamp_max", _value("candidate_timestamp_max")),
        ("candidate_max_after_ohlcv_end_hours", _value("candidate_max_after_ohlcv_end_hours")),
        ("stale_threshold_hours", _value("stale_threshold_hours")),
        ("ohlcv_range_freshness_status", _value("ohlcv_range_freshness_status")),
        ("freshness_note", _value("freshness_note")),
        ("coverage_note", _value("coverage_note")),
        ("safety_note", _value("safety_note")),
    ]
    warning_html = ""
    if str(evidence.get("ohlcv_range_freshness_status", "")).strip() == "stale_before_latest_candidate":
        warning_text = (
            "report-only / not FORMAL_GO / no automatic order / human decides manually; "
            "stale_before_latest_candidate; old OHLCV coverage can make no_ohlcv dominate; "
            f"candidate_max_after_ohlcv_end_hours: {_value('candidate_max_after_ohlcv_end_hours')}"
        )
        warning_html = (
            "<p class=\"warning warning-stale\"><strong>OHLCV stale coverage warning:</strong> "
            f"{html.escape(warning_text)}</p>"
        )
    rows_html = "".join(
        f"<li><strong>{html.escape(label)}:</strong> {html.escape(value)}</li>" for label, value in rows
    )
    return f"""
        <h3>OHLCV source coverage summary</h3>
        <p>local/report-only の表示です。candidate timestamp と OHLCV coverage だけを見て、app surface はこの概要を実行しません。</p>
        <p><strong>安全境界:</strong> report-only / not FORMAL_GO / no automatic order / human decides manually</p>
        {warning_html}
        <ul>{rows_html}</ul>
    """


def _post_eval_recommendation_payload(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    malformed_seen = False
    for container in (
        result,
        notification_context or {},
        display_context or {},
        result.get("app_surface_validation") if isinstance(result.get("app_surface_validation"), dict) else {},
        result.get("app_surface_validation_data") if isinstance(result.get("app_surface_validation_data"), dict) else {},
    ):
        if not isinstance(container, dict):
            continue
        for key in ("post_eval_recommendations", "post_eval_recommendation_summary"):
            value = container.get(key)
            if value is None:
                continue
            if isinstance(value, dict):
                return value
            malformed_seen = True
    if malformed_seen:
        return {"_malformed": True}
    return None


def _post_eval_recommendation_status_html(
    result: dict[str, Any],
    notification_context: dict[str, Any] | None = None,
    display_context: dict[str, Any] | None = None,
) -> str:
    payload = _post_eval_recommendation_payload(result, notification_context, display_context)
    if payload is None:
        return ""
    if not isinstance(payload, dict) or payload.get("_malformed"):
        return """
    <section class="section">
      <h2>Post-Eval Recommendation Status</h2>
      <div class="panel">
        <p>post-eval recommendation payload is unavailable or malformed.</p>
        <p class="muted">report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually</p>
      </div>
    </section>
    """

    def _scrub_sensitive_text(value: Any) -> str:
        text = str(value or "")
        patterns = (
            r"uid_[A-Za-z0-9][A-Za-z0-9_-]*",
            r"\baccount[-_][A-Za-z0-9][A-Za-z0-9_-]*\b",
            r"OPENAI_API_KEY",
            r"SMTP_PASSWORD",
            r"automatic_order_allowed=true",
            r"send_email",
            r"Gmail",
            r"private/order",
            r"smtp",
        )
        for pattern in patterns:
            text = re.sub(pattern, "[redacted]", text, flags=re.IGNORECASE)
        return text

    def _value(*keys: str, default: Any = "未記録") -> str:
        for key in keys:
            value = payload.get(key)
            if value is None:
                continue
            if isinstance(value, bool):
                return str(value).lower()
            if isinstance(value, (list, tuple)):
                if not value:
                    return "none"
                return ", ".join(_scrub_sensitive_text(item) for item in value)
            if isinstance(value, dict):
                if not value:
                    return "none"
                order = {
                    "priority_counts": ("high", "medium", "low", "unknown"),
                    "confidence_counts": ("actual_backed", "proxy_backed", "insufficient", "unknown"),
                }.get(key, ())
                formatted_items: list[str] = []
                seen: set[str] = set()
                if order:
                    for ordered_key in order:
                        if ordered_key in value:
                            formatted_items.append(f"{ordered_key}={_scrub_sensitive_text(value[ordered_key])}")
                            seen.add(ordered_key)
                for dict_key in sorted(k for k in value.keys() if k not in seen):
                    formatted_items.append(f"{dict_key}={_scrub_sensitive_text(value[dict_key])}")
                items = ", ".join(formatted_items)
                return items
            text = _scrub_sensitive_text(value).strip()
            if text:
                return text
        if isinstance(default, bool):
            return str(default).lower()
        if isinstance(default, (list, tuple)):
            return "none" if not default else ", ".join(str(item) for item in default)
        return _scrub_sensitive_text(default)

    schema_version = _value("schema_version", default="post_eval_recommendations.v1")
    report_date = _value("report_date")
    candidate_count = _value("candidate_count", default="0")
    top_recommendation_codes = _value("top_recommendation_codes", default="none")
    priority_counts = _value("priority_counts", default="none")
    confidence_counts = _value("confidence_counts", default="none")
    report_path = _value("report_path")
    output_csv_path = _value("output_csv_path")
    safety_boundary = _value("safety_boundary")
    note = _value("note", default="")
    human_approval_required = _value("human_approval_required", "required_human_approval", default="true")

    return f"""
    <section class="section">
      <h2>Post-Eval Recommendation Status</h2>
      <div class="panel">
        <p>report-only recommendation status</p>
        <p><strong>human approval is required before production wording/config/threshold/gate/runtime changes.</strong></p>
        <p>does not authorize manual or automatic entry</p>
        <p>does not change notification sending behavior</p>
        <ul>
          <li><strong>schema_version:</strong> {html.escape(schema_version)}</li>
          <li><strong>report_date:</strong> {html.escape(report_date)}</li>
          <li><strong>candidate_count:</strong> {html.escape(candidate_count)}</li>
          <li><strong>top_recommendation_codes:</strong> {html.escape(top_recommendation_codes)}</li>
          <li><strong>priority_counts:</strong> {html.escape(priority_counts)}</li>
          <li><strong>confidence_counts:</strong> {html.escape(confidence_counts)}</li>
          <li><strong>report_path:</strong> {html.escape(report_path)}</li>
          <li><strong>output_csv_path:</strong> {html.escape(output_csv_path)}</li>
          <li><strong>safety_boundary:</strong> {html.escape(safety_boundary)}</li>
          <li><strong>human_approval_required:</strong> {html.escape(human_approval_required)}</li>
        </ul>
        {f'<p class="muted">{html.escape(note)}</p>' if str(note).strip() else ''}
      </div>
    </section>
    """


def _runtime_startup_status_path(base_dir: Path) -> Path:
    return base_dir / "logs" / "runtime" / "startup_status.json"


def _read_runtime_startup_status(base_dir: Path) -> dict[str, Any] | None:
    path = _runtime_startup_status_path(base_dir)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {"available": False}
    if not isinstance(raw, dict):
        return {"available": False}
    report_times = raw.get("report_times")
    report_times_list = [str(item).strip() for item in report_times if str(item).strip()] if isinstance(report_times, list) else []
    timestamp_utc = str(raw.get("timestamp_utc", "")).strip()
    pid = raw.get("pid")
    timezone_name = str(raw.get("timezone", "")).strip()
    next_report_time = str(raw.get("next_report_time", "")).strip()
    if not timestamp_utc or pid is None or not timezone_name or not next_report_time or not report_times_list:
        return {"available": False}
    return {
        "available": True,
        "timestamp_utc": timestamp_utc,
        "pid": pid,
        "timezone": timezone_name,
        "next_report_time": next_report_time,
        "report_times_count": len(report_times_list),
    }


def _runtime_startup_status_html(base_dir: Path | None) -> str:
    if base_dir is None:
        return ""
    status = _read_runtime_startup_status(base_dir)
    if status is None:
        return ""
    if not status.get("available"):
        return """
    <section class="section">
      <h2>Runtime startup status</h2>
      <div class="panel">
        <p>startup_status.json は利用不可です。</p>
      </div>
    </section>
    """
    return f"""
    <section class="section">
      <h2>Runtime startup status</h2>
      <div class="panel">
        <ul>
          <li><strong>timestamp_utc:</strong> {html.escape(str(status.get('timestamp_utc', '未記録')))}</li>
          <li><strong>pid:</strong> {html.escape(str(status.get('pid', '未記録')))}</li>
          <li><strong>timezone:</strong> {html.escape(str(status.get('timezone', '未記録')))}</li>
          <li><strong>next_report_time:</strong> {html.escape(str(status.get('next_report_time', '未記録')))}</li>
          <li><strong>report_times count:</strong> {html.escape(str(status.get('report_times_count', '未記録')))}</li>
        </ul>
      </div>
    </section>
    """


def build_notification_detail_html(result: dict[str, Any], base_dir: Path | None = None) -> str:
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
    value_defense_chart_dashboard_html = _value_defense_chart_dashboard(result)
    show_ai_audit = audit_agreement in {"caution", "disagree"} or bool(audit_unique_risks)
    ai_audit_headline = "通知判断の再確認を推奨" if audit_agreement == "disagree" else "通知は妥当だが注意点あり"
    ai_audit_unique_risk_html = "".join(f"<li>{esc(reason)}</li>" for reason in audit_unique_risks)
    runtime_startup_status_html = _runtime_startup_status_html(base_dir)
    safe_config_schema_audit_html = _safe_config_schema_audit_html(result, notification_context, display_context)
    operator_triage_summary_html = _operator_triage_summary_html(result, notification_context, display_context)
    integrated_evidence_overview_html = _integrated_evidence_overview_html(result, notification_context, display_context)
    evidence_quality_summary_html = _evidence_quality_summary_html(result, notification_context, display_context)
    ohlcv_source_coverage_summary_html = _ohlcv_source_coverage_summary_html(result, notification_context, display_context)
    post_eval_recommendation_status_html = _post_eval_recommendation_status_html(result, notification_context, display_context)
    major_turning_point_diagnostic_items, major_turning_point_diagnostic_rows, major_turning_point_diagnostic_rows_html = _major_turning_point_diagnostic_items(
        result,
        notification_context,
        display_context,
    )
    checklist_items = [
        ("行動種別", _humanize_visible_status_text(notification_context.get("execution_label", "")).strip() or "未記録"),
        (
            "入る条件",
            _sentence_join(
                [
                    str(notification_context.get("entry_window_label", "")).strip(),
                    str(display_context.get("entry_quality_label", "")).strip(),
                    active_hero_summary,
                ]
            ),
        ),
        (
            "利確 / 損切り",
            "\n".join(
                [
                    _setup_line(result, "long"),
                    _setup_line(result, "short"),
                ]
            ),
        ),
        (
            "無効化 / 待機理由",
            _sentence_join(str(reason).strip() for reason in display_reasons if str(reason).strip()),
        ),
        ("有効期限", _humanize_visible_status_text(notification_context.get("validity_label", "")).strip() or "未記録"),
        ("安全境界", "report-only / not FORMAL_GO / no automatic order / human decides manually"),
    ]
    checklist_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">📝 <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in checklist_items
    )
    major_turning_point_items = _major_turning_point_opportunity_items(
        result,
        display_context,
        notification_context,
        active_hero_summary,
        display_reasons,
    )
    major_turning_point_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">🔁 <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in major_turning_point_items
    )
    breakout_inversion_items = _breakout_inversion_items(result)
    breakout_inversion_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">🧭 <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in breakout_inversion_items
    )
    intraperiod_breakout_items = _intraperiod_breakout_items(result)
    intraperiod_breakout_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">⏱ <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in intraperiod_breakout_items
    )
    momentum_confirmation_items = _momentum_confirmation_items(result)
    momentum_confirmation_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">⚡ <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in momentum_confirmation_items
    )
    value_defense_entry_layer_html = "".join(
        block
        for block in (
            _value_defense_entry_layer_block(result, "long"),
            _value_defense_entry_layer_block(result, "short"),
        )
        if block
    )
    value_defense_entry_layer_section_html = (
        f"""
    <section class="section">
      <h2>Value Defense Entry Layer</h2>
      <p>既存の再検討帯は浅い再検討帯、本命は本命防衛ゾーンとして分けて見ます。ここは売買指示ではなく、どの深さを本命に置くかを見る補助欄です。</p>
      <div class="two-col">
        {value_defense_entry_layer_html}
      </div>
    </section>
    """
        if value_defense_entry_layer_html
        else ""
    )
    major_turning_point_diagnostic_html = (
        '<div class="checklist">'
        + "".join(
            '<div class="checklist-item">'
            f'<div class="checklist-label">📈 <span>{esc(label)}</span></div>'
            f'<div class="checklist-value">{esc(value)}</div>'
            "</div>"
            for label, value in major_turning_point_diagnostic_items
        )
        + (f'<div class="checklist-item"><div class="checklist-label">🧾 <span>Representative rows</span></div><div class="checklist-value">{"none" if not major_turning_point_diagnostic_rows_html else major_turning_point_diagnostic_rows_html}</div></div>' if major_turning_point_diagnostic_items else "")
        + "</div>"
    ) if major_turning_point_diagnostic_items else ""

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
      fill: rgba(34, 197, 94, 0.18);
      stroke: rgba(74, 222, 128, 0.82);
      stroke-width: 1.35;
    }}
    .setup-band-short {{
      fill: rgba(248, 113, 113, 0.18);
      stroke: rgba(248, 113, 113, 0.82);
      stroke-width: 1.35;
    }}
    .setup-band-text-long {{
      fill: #dcfce7;
      font-size: 12px;
      font-weight: 700;
    }}
    .setup-band-text-short {{
      fill: #fee2e2;
      font-size: 12px;
      font-weight: 700;
    }}
    .value-defense-band-long {{
      fill: rgba(14, 165, 233, 0.1);
      stroke: rgba(125, 211, 252, 0.72);
      stroke-width: 1.15;
      stroke-dasharray: 4 4;
    }}
    .value-defense-band-short {{
      fill: rgba(251, 191, 36, 0.1);
      stroke: rgba(253, 224, 71, 0.72);
      stroke-width: 1.15;
      stroke-dasharray: 4 4;
    }}
    .invalidation-band-long {{
      fill: rgba(220, 38, 38, 0.09);
      stroke: rgba(252, 165, 165, 0.78);
      stroke-width: 1.05;
    }}
    .invalidation-band-short {{
      fill: rgba(29, 78, 216, 0.09);
      stroke: rgba(147, 197, 253, 0.78);
      stroke-width: 1.05;
    }}
    .value-defense-band-text-long, .value-defense-band-text-short,
    .invalidation-band-text-long, .invalidation-band-text-short {{
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .value-defense-band-text-long {{
      fill: #dbeafe;
    }}
    .value-defense-band-text-short {{
      fill: #fef3c7;
    }}
    .invalidation-band-text-long {{
      fill: #fecaca;
    }}
    .invalidation-band-text-short {{
      fill: #bfdbfe;
    }}
    .value-defense-trigger-long, .value-defense-trigger-short {{
      stroke-width: 1.1;
      stroke-dasharray: 6 5;
    }}
    .value-defense-trigger-long {{
      stroke: rgba(186, 230, 253, 0.92);
    }}
    .value-defense-trigger-short {{
      stroke: rgba(253, 230, 138, 0.92);
    }}
    .value-defense-trigger-text-long, .value-defense-trigger-text-short {{
      font-size: 11px;
      font-weight: 700;
    }}
    .value-defense-trigger-text-long {{
      fill: #e0f2fe;
    }}
    .value-defense-trigger-text-short {{
      fill: #fef3c7;
    }}
    .value-defense-dashboard {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 12px 18px 4px;
    }}
    .value-defense-chart-card {{
      border: 1px solid rgba(71, 85, 105, 0.66);
      border-radius: 16px;
      padding: 12px 14px;
      background: linear-gradient(180deg, rgba(10, 16, 28, 0.96) 0%, rgba(12, 20, 34, 0.96) 100%);
    }}
    .value-defense-chart-card.long {{
      box-shadow: inset 0 0 0 1px rgba(125, 211, 252, 0.09);
    }}
    .value-defense-chart-card.short {{
      box-shadow: inset 0 0 0 1px rgba(253, 224, 71, 0.08);
    }}
    .value-defense-card-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
      color: #eff6ff;
      font-size: 13px;
      font-weight: 800;
    }}
    .value-defense-card-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 54px;
      height: 24px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.04em;
    }}
    .value-defense-card-pill.long {{
      background: rgba(14, 165, 233, 0.16);
      color: #dbeafe;
    }}
    .value-defense-card-pill.short {{
      background: rgba(245, 158, 11, 0.14);
      color: #fef3c7;
    }}
    .value-defense-card-row {{
      display: grid;
      grid-template-columns: 92px 1fr;
      gap: 10px;
      align-items: baseline;
      padding: 6px 0;
      border-top: 1px solid rgba(71, 85, 105, 0.28);
    }}
    .value-defense-card-row:first-of-type {{
      border-top: 0;
      padding-top: 0;
    }}
    .value-defense-card-key {{
      color: #9fb0c8;
      font-size: 11px;
      font-weight: 700;
    }}
    .value-defense-card-value {{
      color: #eef6ff;
      font-size: 12px;
      font-weight: 800;
      text-align: right;
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
      fill: #dbeafe;
      font-size: 13px;
      font-weight: 700;
      paint-order: stroke fill;
      stroke: rgba(15, 23, 42, 0.9);
      stroke-width: 3;
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
      .value-defense-dashboard {{ grid-template-columns: 1fr; }}
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

    {f'''
    <section class="section">
      <h2>上抜け・下抜けの見落とし確認</h2>
      <div class="panel">
        <p class="muted">ブレイクが出たあとに、反対側の根拠がまだ残っていないかだけを見ます。</p>
        <div class="checklist">{breakout_inversion_html}</div>
      </div>
    </section>
    ''' if breakout_inversion_items else ''}

    {f'''
    <section class="section">
      <h2>15分足 早期注意</h2>
      <div class="panel">
        <p class="muted">report-only / not FORMAL_GO / no automatic order / human decides manually の候補表示です。</p>
        <div class="checklist">{intraperiod_breakout_html}</div>
      </div>
    </section>
    ''' if intraperiod_breakout_items else ''}

    {f'''
    <section class="section">
      <h2>勢い確認</h2>
      <div class="panel">
        <p class="muted">report-only / human decides manually の補助確認です。ブレイク後の勢いだけを見ます。</p>
        <div class="checklist">{momentum_confirmation_html}</div>
      </div>
    </section>
    ''' if momentum_confirmation_items else ''}

    <section class="section">
      <h2>大転換チャンス確認</h2>
      <div class="panel">
        <p><strong>{esc(active_hero_label)}</strong> を見ながら、大転換候補とダマシ注意を取り違えないための確認を先に置きます。</p>
        <p class="muted">大転換は「方向」だけで決めず、4h → 1h → 15m の順で根拠を見ます。15分足だけで決め打ちしません。</p>
        <div class="checklist">{major_turning_point_html}</div>
        <div class="checklist-note">これは転換の決め打ちではなく、条件成立まで人間確認を続けるための表示です。</div>
      </div>
    </section>

    {f'''
    <section class="section">
      <h2>大転換チャンス診断</h2>
      <div class="panel">
        <p>local/report-only の表示です。post-hoc diagnostic support であり、実行はしません。</p>
        <p>does not confirm a major turn / does not authorize manual or automatic entry です。</p>
        <p><strong>安全境界:</strong> report-only / not FORMAL_GO / no automatic order / human decides manually</p>
        <div class="checklist">{major_turning_point_diagnostic_html}</div>
        <div class="checklist-note">これは候補の見直し用です。大転換の確定ではなく、失敗・ダマシ・タイミングの見直し候補を人間が確認します。</div>
      </div>
    </section>
    ''' if major_turning_point_diagnostic_items else ''}

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
        {value_defense_chart_dashboard_html}
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
            <li>水色 / 金色の細い帯が本命防衛ゾーン、淡い危険帯が無効化です。</li>
            <li>上段と中段は「その帯が自然か」を見る段、下段は「その価格で実際に入れるか」を見る段です。</li>
            <li>点線は SL と TP で、15分足ではどこで切るか・利確するかを直接確認できます。</li>
            <li>Value Defense の詳しい数字は、チャート下のカードでまとめて確認します。</li>
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

    {value_defense_entry_layer_section_html}

    <section class="section">
      <h2>待機理由または注意点</h2>
      <div class="reason-grid">{reason_cards_html}</div>
      <ul>{wait_reason_html}</ul>
    </section>

    <details class="section internal-diagnostics">
      <summary><strong>{CURRENT_MANUAL_SUPPORT_HEADER}</strong> - 検証 / 運用確認だけに使うブロック</summary>
      <div class="panel">
        <p>このブロックは検証と運用確認用です。売買判断の主導線には置きません。</p>
        <p><strong>安全境界:</strong> report-only / not FORMAL_GO / no automatic order / human decides manually</p>
        <p>local dashboard / app surface / runtime contract / manual delivery reference をまとめて確認します。</p>
        <p>通知メールと公開HTMLは同じ判断ソースから出しますが、ここは内部確認だけに使います。</p>
        <h3>Intraperiod JSON 契約</h3>
        <p>local/report-only の手動確認向けに、<code>build-active-plan-intraperiod-review --stdout-json</code> と <code>active_plan_intraperiod_review.v1</code> の app contract exposure を案内します。</p>
        <p>app surface / ready gate validation は <code>intraperiod_review_stdout_json</code> の契約露出を確認し、<strong>app contract</strong> と <strong>ready gate</strong> の整合だけを見ます。</p>
        <p>負荷や実行は行わず、<strong>report-only / not FORMAL_GO / no automatic order / human decides manually</strong> を維持します。</p>
        <p>negative boundary: no exchange fetch / no daily-sync wiring / no secret/API key reading / no automatic order / no FORMAL_GO</p>
        {safe_config_schema_audit_html}
        {operator_triage_summary_html}
        {integrated_evidence_overview_html}
        {evidence_quality_summary_html}
        {ohlcv_source_coverage_summary_html}
        {post_eval_recommendation_status_html}
        {runtime_startup_status_html}
        <ul>{manual_support_reference_list_html}</ul>
      </div>
    </details>

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
    local_path.write_text(build_notification_detail_html(result, base_dir=base_dir), encoding="utf-8")

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
