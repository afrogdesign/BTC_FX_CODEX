from __future__ import annotations

import json
import html
import math
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
from src.notification.followup import (
    FOLLOWUP_HUMAN_MESSAGE,
    FOLLOWUP_PUBLIC_LABEL,
    FOLLOWUP_SAFETY_BOUNDARY,
    build_followup_notification_context,
)
from src.notification.intraperiod_breakout import build_intraperiod_breakout_alert_candidate
from src.feedback.manual_operator_shadow_surface import build_manual_operator_shadow_surface


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
STABLE_DETAIL_PAGE_PRODUCT_LABEL = "BTCFX Manual Trading Report"
STABLE_NOTIFICATION_SYSTEM_SLUG = "manual-trading"
STABLE_DETAIL_PAGE_SAFETY_BOUNDARY = "report-only / not FORMAL_GO / no automatic order / human decides manually"

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


def _format_operator_price(value: Any, fallback: str = "—") -> str:
    """Format USD values for the operator surface without changing payload data."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(numeric):
        return fallback
    return f"{numeric:,.0f}"


def _format_operator_price_range(low: Any, high: Any, fallback: str = "—") -> str:
    low_text = _format_operator_price(low, fallback)
    high_text = _format_operator_price(high, fallback)
    if fallback in {low_text, high_text}:
        return fallback
    return f"{low_text}–{high_text}"


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


def _notification_context_for_result(result: dict[str, Any]) -> dict[str, Any]:
    notification_context = build_notification_context(result)
    override = result.get("notification_context")
    if isinstance(override, dict):
        notification_context.update(override)
    followup_context = result.get("followup_context")
    if str(result.get("notification_kind", "main")).lower().strip() == "followup" and isinstance(followup_context, dict):
        notification_context.update(build_followup_notification_context(followup_context))
    return notification_context


def _active_plan_hero_label(notification_context: dict[str, Any], result: dict[str, Any]) -> str:
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    trade_execution_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()
    trade_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()

    if notification_kind == "followup":
        return FOLLOWUP_PUBLIC_LABEL
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

    if notification_kind == "followup":
        followup_context = result.get("followup_context") if isinstance(result.get("followup_context"), dict) else {}
        return str(
            followup_context.get("human_message")
            or FOLLOWUP_HUMAN_MESSAGE
        )
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
        for setup in (long_setup, short_setup):
            layer = setup.get("value_defense_entry_layer")
            if not isinstance(layer, dict):
                continue
            for key in ("shallow_retest_zone", "value_defense_zone", "invalidation_zone"):
                zone = layer.get(key)
                if isinstance(zone, dict):
                    values.extend([_safe_float(zone.get("low")), _safe_float(zone.get("high"))])
            values.extend(
                [
                    _safe_float(layer.get("reclaim_trigger")),
                    _safe_float(layer.get("continuation_trigger")),
                ]
            )
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
            opacity = "0.3" if emphasize_setup else "0.14"
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
            if panel_mode in {"zone", "execution"}:
                setup_elements.append(
                    f'<text x="{text_x:.1f}" y="{text_y:.1f}" text-anchor="{text_anchor}" class="zone-caption zone-{side}-shallow">{side.upper()} 浅い入り</text>'
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
                value_text_class = f"value-defense-band-text-{side} zone-caption zone-{side}-main"
                invalidation_class = "invalidation-band-long" if side == "long" else "invalidation-band-short"
                invalidation_text_class = "invalidation-band-text-long" if side == "long" else "invalidation-band-text-short"
                trigger_class = "value-defense-trigger-long" if side == "long" else "value-defense-trigger-short"
                trigger_text_class = "value-defense-trigger-text-long" if side == "long" else "value-defense-trigger-text-short"
                show_band_labels = panel_mode in {"zone", "execution"}
                show_trigger_labels = False

                _overlay_zone_rect(
                    zone=_layer_zone(layer.get("value_defense_zone")),
                    x=lane_x,
                    width_value=lane_w,
                    rect_class=value_class,
                    label_class=value_text_class,
                    label=f"{side.upper()} 本命ゾーン",
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


def _price_map_svg(
    result: dict[str, Any],
    *,
    initial_view_box: str | None = None,
    extra_class: str = "",
) -> str:
    current_price = _safe_float(result.get("current_price"))
    long_setup = result.get("long_setup", {}) or {}
    short_setup = result.get("short_setup", {}) or {}
    support_zones = result.get("support_zones", [])[:3]
    resistance_zones = result.get("resistance_zones", [])[:3]
    chart_snapshot = result.get("chart_snapshot", {}) if isinstance(result.get("chart_snapshot"), dict) else {}
    width = 860
    panel_gap = 54
    panel_one_height = 309
    panel_two_height = 309
    panel_three_height = 429
    panel_two_origin = panel_one_height + panel_gap
    panel_three_origin = panel_two_origin + panel_two_height + panel_gap
    total_height = panel_three_origin + panel_three_height
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
            height=panel_one_height,
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
            height=panel_two_height,
            origin_y=panel_two_origin,
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
            height=panel_three_height,
            origin_y=panel_three_origin,
            panel_mode="execution",
        ),
    ]
    separators = [
        (
            f'<g class="price-map-separator-wrap">'
            f'<rect x="0" y="{panel_one_height + 10}" width="{width}" height="{panel_gap - 20}" class="price-map-separator" rx="18" />'
            f'<line x1="24" y1="{panel_one_height + (panel_gap / 2):.1f}" x2="{width - 24}" y2="{panel_one_height + (panel_gap / 2):.1f}" class="price-map-separator-line" />'
            "</g>"
        ),
        (
            f'<g class="price-map-separator-wrap">'
            f'<rect x="0" y="{panel_two_origin + panel_two_height + 10}" width="{width}" height="{panel_gap - 20}" class="price-map-separator" rx="18" />'
            f'<line x1="24" y1="{panel_two_origin + panel_two_height + (panel_gap / 2):.1f}" x2="{width - 24}" y2="{panel_two_origin + panel_two_height + (panel_gap / 2):.1f}" class="price-map-separator-line" />'
            "</g>"
        ),
    ]

    view_box = initial_view_box or f"0 0 {width} {total_height}"
    svg_classes = " ".join(item for item in ("price-map", extra_class.strip()) if item)
    return (
        f'<svg viewBox="{html.escape(view_box)}" class="{html.escape(svg_classes)}" aria-label="再検討ラインチャート">'
        f"{''.join(separators)}"
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


def _operator_dashboard_execution_guidance(result: dict[str, Any], side: str) -> str:
    """Human-facing execution guidance for the primary operator cards."""
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
        "short_at_major_support_wait_only": "主要サポート接近を警戒",
        "long_at_major_resistance_wait_only": "主要レジスタンス接近を警戒",
        "short_invalidated_by_up_break": "上抜け後の支持化を警戒",
        "long_invalidated_by_down_break": "下抜け後の抵抗化を警戒",
        "upside_breakout_follow_watch": "上抜け後の支持化を警戒",
        "downside_breakdown_follow_watch": "下抜け後の抵抗化を警戒",
        "breakout_follow_candidate": "ブレイク追随候補を監視",
    }
    notes = list(dict.fromkeys(flag_labels[flag] for flag in flags if flag in flag_labels))
    parts = [action_labels.get(action, "監視")]
    if reason:
        parts.append(reason.rstrip("。"))
    parts.extend(notes)
    return "。".join(parts) + "。"


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
    descriptions = {
        "浅い再検討帯": "最初に反応しやすい近い押し目/戻り",
        "本命防衛ゾーン": "本命として待ちたい深い押し目/戻り",
        "無効化": "この目線が崩れやすい価格帯",
        "回収条件": "深く刺したあとに戻してほしい水準",
        "継続条件": "方向継続を確認する目安",
    }

    def _card_price_text(value: Any) -> str:
        if isinstance(value, dict):
            low = _safe_float(value.get("low"))
            high = _safe_float(value.get("high"))
            if min(low, high) <= 0:
                return "抽出なし"
            return f"{_format_price_int(low)} - {_format_price_int(high)}"
        number = _safe_float(value)
        if number > 0:
            return _format_price_int(number)
        text = str(value).strip()
        return text or "未記録"

    items = [
        ("浅い再検討帯", _card_price_text(layer.get("shallow_retest_zone")), "primary", "shallow"),
        ("本命防衛ゾーン", _card_price_text(layer.get("value_defense_zone")), "primary", "defense"),
        ("無効化", _card_price_text(layer.get("invalidation_zone")), "secondary", "invalidation"),
        ("回収条件", _card_price_text(layer.get("reclaim_trigger")), "secondary", "reclaim"),
        ("継続条件", _card_price_text(layer.get("continuation_trigger")), "secondary", "continuation"),
    ]
    primary_rows = "".join(
        f'<div class="value-defense-card-row primary {tone}">'
        '<div class="value-defense-card-main">'
        f'<span class="value-defense-card-key"><span class="value-defense-row-chip {tone} {chip}"></span>{html.escape(label)}</span>'
        f'<span class="value-defense-card-desc">{html.escape(descriptions.get(label, ""))}</span>'
        "</div>"
        f'<span class="value-defense-card-value">{html.escape(value)}</span>'
        "</div>"
        for label, value, tier, chip in items
        if tier == "primary"
    )
    secondary_rows = "".join(
        f'<div class="value-defense-card-row secondary {tone}">'
        '<div class="value-defense-card-main">'
        f'<span class="value-defense-card-key"><span class="value-defense-row-chip {tone} {chip}"></span>{html.escape(label)}</span>'
        f'<span class="value-defense-card-desc">{html.escape(descriptions.get(label, ""))}</span>'
        "</div>"
        f'<span class="value-defense-card-value secondary">{html.escape(value)}</span>'
        "</div>"
        for label, value, tier, chip in items
        if tier == "secondary"
    )
    return (
        f'<div class="value-defense-chart-card {tone}">'
        f'<div class="value-defense-card-head"><span class="value-defense-card-pill {tone}">{side_label}</span><strong>Value Defense</strong></div>'
        '<div class="value-defense-group-label primary">主情報</div>'
        f"{primary_rows}"
        '<div class="value-defense-group-label secondary">補助情報</div>'
        f"{secondary_rows}"
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


def _detail_page_nav_html() -> str:
    items = [
        ("1", "まず結論", "#decision"),
        ("2", "価格帯", "#price-plan"),
        ("3", "手動ゲート", "#manual-gates"),
        ("4", "チャート", "#chart"),
        ("5", "大転換候補", "#big-chance"),
        ("6", "スコア", "#scores"),
        ("7", "理由", "#reasons"),
        ("8", "内部詳細", "#details"),
    ]
    links = "".join(
        f'<a href="{html.escape(anchor)}"><span class="nav-index">{html.escape(index)}</span><span class="nav-label">{html.escape(label)}</span></a>'
        for index, label, anchor in items
    )
    return f"""
    <aside class="read-nav" aria-label="読む順番">
      <div class="read-nav-title">読む順番</div>
      <nav>{links}</nav>
    </aside>
    """


def _normalize_detail_page_safety_boundary(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return STABLE_DETAIL_PAGE_SAFETY_BOUNDARY
    normalized = re.sub(r"[\s/_-]+", " ", text).strip().lower()
    if "report only" in normalized and "automatic order" in normalized and "human decides manually" in normalized:
        return STABLE_DETAIL_PAGE_SAFETY_BOUNDARY
    if "report only" in normalized and "no automatic order" in normalized and "human decides manually" in normalized:
        return STABLE_DETAIL_PAGE_SAFETY_BOUNDARY
    return text


def _status_strip_html(result: dict[str, Any], notification_context: dict[str, Any]) -> str:
    validity_label = str(notification_context.get("validity_label", "")).strip() or "未記録"
    safety_boundary = _normalize_detail_page_safety_boundary(
        notification_context.get("followup_safety_boundary")
        or notification_context.get("safety_boundary")
        or result.get("actionability_safety")
    )
    price = _format_price(result.get("current_price"))
    return f"""
    <div class="status-strip">
      <div class="status-card"><div class="status-label">現在価格</div><div class="status-value">{html.escape(price)}</div></div>
      <div class="status-card"><div class="status-label">有効期限</div><div class="status-value">{html.escape(validity_label)}</div></div>
      <div class="status-card"><div class="status-label">安全境界</div><div class="status-value">{html.escape(safety_boundary)}</div></div>
    </div>
    """


def _price_plan_table_html(result: dict[str, Any]) -> str:
    def row_html(side: str) -> str:
        setup = result.get("long_setup", {}) if side == "long" else result.get("short_setup", {})
        entry = setup.get("entry_zone") or {}
        return (
            "<tr>"
            f"<td><span class=\"v2-side-pill {'long' if side == 'long' else 'short'}\">{'ロング' if side == 'long' else 'ショート'}</span></td>"
            f"<td>{html.escape(_setup_status_label(setup.get('status')))}</td>"
            f"<td>{html.escape(_format_price(entry.get('low')))} - {html.escape(_format_price(entry.get('high')))}</td>"
            f"<td>{html.escape(_format_price(setup.get('stop_loss')))}</td>"
            f"<td>{html.escape(_format_price(setup.get('tp1')))}<br>{html.escape(_format_price(setup.get('tp2')))}</td>"
            f"<td>{html.escape(_execution_precision_line(result, side))}</td>"
            "</tr>"
        )

    return f"""
    <section class="v2-section v2-section-anchor" id="price-plan">
      <h2>ロング / ショート比較</h2>
      <p class="v2-muted">再検討帯、SL、TP を表で見比べ、15分足でどこを見るかだけを先に把握します。</p>
      <div class="v2-table-wrap">
        <table class="v2-table">
          <thead>
            <tr>
              <th>方向</th>
              <th>状態</th>
              <th>再検討帯</th>
              <th>SL</th>
              <th>TP1 / TP2</th>
              <th>実行精度 / 15分足で見ること</th>
            </tr>
          </thead>
          <tbody>
            {row_html("long")}
            {row_html("short")}
          </tbody>
        </table>
      </div>
    </section>
    """


def _manual_gate_cards_html(active_status_rows: list[tuple[str, str]]) -> str:
    cards = "".join(
        f"""
        <div class="v2-card">
          <div class="v2-kicker">{html.escape(label)}</div>
          <div class="v2-big">{html.escape(value)}</div>
        </div>
        """
        for label, value in active_status_rows
    )
    return f"""
    <section class="v2-section v2-section-anchor" id="manual-gates">
      <h2>手動アクションゲート</h2>
      <div class="v2-grid-3">{cards}</div>
    </section>
    """


def _score_summary_heading(result: dict[str, Any]) -> str:
    bias = str(result.get("bias", "")).strip().lower()
    direction_score = _clamp(_safe_float(result.get("confidence_direction_shadow")))
    execution_score = _clamp(_safe_float(result.get("confidence_execution_shadow")))
    wait_score = _clamp(_safe_float(result.get("confidence_wait_shadow")))
    if bias == "long":
        bias_label = "上目線"
    elif bias == "short":
        bias_label = "下目線"
    else:
        bias_label = "方向感はあるが慎重"
    if execution_score < 45 or wait_score >= 50:
        action_label = "見送り"
    elif execution_score >= 65 and wait_score < 40:
        action_label = "条件確認"
    else:
        action_label = "慎重判断"
    if direction_score < 25 and bias not in {"long", "short"}:
        return "スコア根拠: なぜまだ方向を決め切れないのか"
    return f'スコア根拠: なぜ「{bias_label}だが{action_label}」なのか'


def _v2_score_card_html(label: str, score: Any, tone: str, note: str, *, wide: bool = False) -> str:
    numeric = _clamp(_safe_float(score))
    wide_class = " wide" if wide else ""
    return f"""
    <article class="v2-score-card{wide_class}">
      <div class="v2-score-head">
        <div class="v2-score-label">{html.escape(label)}</div>
        <div class="v2-score-value">{numeric:.1f}</div>
      </div>
      <div class="v2-score-track"><div class="v2-score-fill {html.escape(tone)}" style="width:{numeric:.1f}%"></div></div>
      <p class="v2-score-note">{html.escape(note)}</p>
    </article>
    """


def _score_summary_section_html(result: dict[str, Any], reason_cards_html: str) -> str:
    direction_score = _clamp(_safe_float(result.get("confidence_direction_shadow")))
    execution_score = _clamp(_safe_float(result.get("confidence_execution_shadow")))
    wait_score = _clamp(_safe_float(result.get("confidence_wait_shadow")))
    long_score = _clamp(_safe_float(result.get("long_display_score")))
    short_score = _clamp(_safe_float(result.get("short_display_score")))
    top_cards = "".join(
        [
            _v2_score_card_html("方向の強さ", direction_score, "blue", _metric_hint("direction", direction_score)),
            _v2_score_card_html("実行しやすさ", execution_score, "orange", _metric_hint("execution", execution_score)),
            _v2_score_card_html("待機圧力", wait_score, "red", _metric_hint("wait", wait_score)),
        ]
    )
    lower_cards = "".join(
        [
            _v2_score_card_html("ロング", long_score, "green", "ロング側の相対スコアです。強さだけを短く確認します。", wide=True),
            _v2_score_card_html("ショート", short_score, "red", "ショート側の相対スコアです。強さだけを短く確認します。", wide=True),
        ]
    )
    return f"""
    <section class="v2-section v2-section-anchor" id="scores">
      <h2>{html.escape(_score_summary_heading(result))}</h2>
      <p class="v2-muted">5つの数字をカードで確認し、理由は下のチップだけ見る構成にしています。</p>
      <div class="v2-score-grid-top">
        {top_cards}
      </div>
      <div class="v2-score-grid-bottom">
        {lower_cards}
      </div>
      <div class="v2-card" style="margin-top:14px;">
        <div class="v2-kicker">待機理由・注意点</div>
        <div class="v2-reasons">{reason_cards_html or '<span class="v2-reason">大きな待機理由は出ていません</span>'}</div>
      </div>
    </section>
    """


def _reasons_section_html(reason_cards_html: str, wait_reason_html: str) -> str:
    return f"""
    <section class="v2-section v2-section-anchor" id="reasons">
      <h2>待機理由 / 無効化理由</h2>
      <div class="v2-reasons">{reason_cards_html}</div>
      <div class="v2-card">
        <div class="v2-kicker">補足</div>
        <p class="v2-muted">{wait_reason_html}</p>
      </div>
    </section>
    """


def _details_panel_html(title: str, body_html: str, open: bool = False) -> str:
    if not str(body_html).strip():
        return ""
    open_attr = " open" if open else ""
    return f"""
    <details class="v2-details diagnostic-details"{open_attr}>
      <summary>{html.escape(title)}</summary>
      <div class="v2-details-body diagnostic-details-body">{body_html}</div>
    </details>
    """


def _v2_meter_html(label: str, score: Any, tone: str, hint: str, note: str = "") -> str:
    numeric = _clamp(_safe_float(score))
    return f"""
    <div class="v2-meter">
      <div class="v2-meter-head">
        <span>{html.escape(label)}</span>
        <strong>{numeric:.1f} / 100</strong>
      </div>
      <div class="v2-bar"><div class="v2-fill {html.escape(tone)}" style="width:{numeric:.1f}%"></div></div>
      <div class="v2-meter-hint">{html.escape(hint)}</div>
      {f'<div class="v2-meter-note">{html.escape(note)}</div>' if note else ''}
    </div>
    """


def _v2_card_html(kicker: str, title: str, body: str, class_name: str = "") -> str:
    classes = "v2-card" + (f" {class_name}" if class_name else "")
    return f"""
    <article class="{classes}">
      <div class="v2-kicker">{html.escape(kicker)}</div>
      <h3>{html.escape(title)}</h3>
      <p>{html.escape(body)}</p>
    </article>
    """


def _v2_reason_chips_html(reasons: list[str]) -> str:
    return "".join(f'<span class="v2-reason">{html.escape(reason)}</span>' for reason in reasons if str(reason).strip())


def _v2_action_strip_html(items: list[tuple[str, str]]) -> str:
    return "".join(
        f"""
        <div class="v2-action-item">
          <div class="v2-action-title">{html.escape(label)}</div>
          <div class="v2-action-value">{html.escape(value)}</div>
        </div>
        """
        for label, value in items
    )


def _v2_sidebar_html(result: dict[str, Any], notification_context: dict[str, Any], active_hero_label: str, current_price: str) -> str:
    items = [
        ("1", "まず結論", "#decision"),
        ("2", "いまの見方", "#posture"),
        ("3", "方向メーター", "#direction-meter"),
        ("4", "チャートを見る場所", "#chart-focus"),
        ("5", "今やること", "#now-action"),
        ("6", "読み方メモ", "#phase4-cues"),
        ("7", "価格帯", "#price-plan"),
        ("8", "チャート", "#chart"),
        ("9", "Big Chance", "#big-chance"),
        ("10", "スコア", "#scores"),
        ("11", "詳細", "#logs"),
    ]
    nav_html = "".join(
        f'<a href="{html.escape(anchor)}"><span class="v2-nav-index">{html.escape(index)}</span><span>{html.escape(label)}</span></a>'
        for index, label, anchor in items
    )
    return f"""
    <aside class="v2-sidebar" aria-label="読む順番">
      <h2>読む順番</h2>
      <div class="v2-nav">{nav_html}</div>
      <div class="v2-mini-summary">
        <div><strong>signal_id:</strong> {html.escape(str(result.get('signal_id', '未記録')))}</div>
        <div><strong>時刻:</strong> {html.escape(str(result.get('timestamp_jst', '')).replace('T', ' '))}</div>
        <div><strong>種別:</strong> {html.escape(str(result.get('notification_kind', 'main')))}</div>
        <div><strong>現在値:</strong> {html.escape(current_price)}</div>
        <div><strong>行動:</strong> {html.escape(active_hero_label)}</div>
      </div>
    </aside>
    """


def _operator_v3_side_status(notification_context: dict[str, Any], result: dict[str, Any], side: str) -> str:
    side_key = "long" if side == "long" else "short"
    bias = str(result.get("bias", "")).strip().lower()
    limit = str(((notification_context.get("active_limit_retest_entry") or {}).get(side_key)) or "").strip().lower()
    market = str(((notification_context.get("active_market_entry_now") or {}).get(side_key)) or "").strip().lower()
    breakout = str(((notification_context.get("active_breakout_follow_entry") or {}).get(side_key)) or "").strip().lower()
    counter = str(((notification_context.get("active_countertrend_scalp_entry") or {}).get(side_key)) or "").strip().lower()
    watchable = {limit, market, breakout, counter} & {"allowed", "conditional", "watch", "ready", "pass"}
    if bias == side_key and watchable:
        return "優勢 / 監視"
    if watchable:
        return "監視"
    if bias == side_key:
        return "監視"
    return "見送り"


def _operator_v3_wait_status(result: dict[str, Any]) -> str:
    wait_score = _clamp(_safe_float(result.get("confidence_wait_shadow")))
    if wait_score >= 70:
        return "高め"
    if wait_score >= 40:
        return "中くらい"
    return "低め"


def _operator_v3_conclusion_text(result: dict[str, Any], notification_context: dict[str, Any]) -> str:
    notification_kind = str(result.get("notification_kind", "main")).strip().lower() or "main"
    bias = str(result.get("bias", "")).strip().lower()
    long_state = _operator_v3_side_status(notification_context, result, "long")
    short_state = _operator_v3_side_status(notification_context, result, "short")
    if notification_kind == "followup":
        return "今は前回通知を使わず再評価。新規判断は急がない。"
    if notification_kind == "attention":
        return "今は入らない。注意報として価格帯だけを監視する。"
    if bias == "short":
        return "今は見送り。ショート寄りに監視。ロングは浅い押し目だけで判断しない。"
    if bias == "long":
        return "今は見送り。ロング寄りに監視。ショートは飛びつかず戻りを待つ。"
    if "監視" in short_state and "監視" not in long_state:
        return "今は見送り。ショート側を先に監視し、ロングは急がない。"
    if "監視" in long_state and "監視" not in short_state:
        return "今は見送り。ロング側を先に監視し、ショートは急がない。"
    return "今は見送り。方向を固定せず、価格帯と15分足だけを確認する。"


def _operator_v3_posture_html(result: dict[str, Any], notification_context: dict[str, Any]) -> str:
    cards = [
        ("ロング", _operator_v3_side_status(notification_context, result, "long"), "long", "浅い反応帯だけで決めず、押し目の質を先に見る。"),
        ("ショート", _operator_v3_side_status(notification_context, result, "short"), "short", "戻りの反応を見て、追いかけずに判断する。"),
        ("待機", _operator_v3_wait_status(result), "wait", "15分足の価格反応と安全境界を優先して確認する。"),
    ]
    card_html = "".join(
        f"""
        <div class="v2-operator-card {html.escape(tone)}">
          <div class="v2-operator-label">{html.escape(label)}</div>
          <div class="v2-operator-value">{html.escape(value)}</div>
          <p class="v2-operator-note">{html.escape(note)}</p>
        </div>
        """
        for label, value, tone, note in cards
    )
    return f"""
    <section class="v2-section v2-section-anchor" id="posture">
      <h2>いまの見方</h2>
      <div class="v2-operator-grid">
        {card_html}
      </div>
    </section>
    """


def _operator_v3_direction_meter_html(result: dict[str, Any], notification_context: dict[str, Any]) -> str:
    return f"""
    <section class="v2-section v2-section-anchor" id="direction-meter">
      <h2>方向メーター</h2>
      <p class="v2-muted">表示用の読みやすい要約です。新しい scoring / gate / threshold logic は作っていません。</p>
      <div class="v2-score-grid-top">
        {_v2_score_card_html("ロング", result.get("long_display_score"), "blue", f"{_operator_v3_side_status(notification_context, result, 'long')}。浅い反応帯だけで決めない。")}
        {_v2_score_card_html("ショート", result.get("short_display_score"), "red", f"{_operator_v3_side_status(notification_context, result, 'short')}。戻りの妥当性を先に見る。")}
        {_v2_score_card_html("待機", result.get("confidence_wait_shadow"), "orange", f"{_operator_v3_wait_status(result)}。今やることを先に確認する。")}
      </div>
    </section>
    """


def _operator_v3_chart_focus_html(result: dict[str, Any]) -> str:
    long_setup = result.get("long_setup", {}) or {}
    short_setup = result.get("short_setup", {}) or {}
    long_zone = long_setup.get("entry_zone") or {}
    short_zone = short_setup.get("entry_zone") or {}
    long_layer = long_setup.get("value_defense_entry_layer") if isinstance(long_setup.get("value_defense_entry_layer"), dict) else {}
    short_layer = short_setup.get("value_defense_entry_layer") if isinstance(short_setup.get("value_defense_entry_layer"), dict) else {}
    long_zone_text = _value_defense_entry_layer_zone_text(long_layer.get("shallow_retest_zone")) if long_layer else f"{_format_price(long_zone.get('low'))} - {_format_price(long_zone.get('high'))}"
    short_zone_text = _value_defense_entry_layer_zone_text(short_layer.get("value_defense_zone")) if short_layer else f"{_format_price(short_zone.get('low'))} - {_format_price(short_zone.get('high'))}"
    return f"""
    <section class="v2-section v2-section-anchor" id="chart-focus">
      <h2>チャートを見る場所</h2>
      <div class="v2-grid-3">
        {_v2_card_html("4時間足", "大きな流れ", "まず全体方向と主要帯だけを見る。")}
        {_v2_card_html("1時間足", "戻りの妥当性", "浅い反応帯と本命防衛帯の位置関係を確認する。")}
        {_v2_card_html("15分足", "入るなら見る場所", "実際に反応する価格、SL、TP だけを短く確認する。")}
      </div>
      <div class="v2-grid-2" style="margin-top:14px;">
        {_v2_card_html("ロングの浅い反応帯", long_zone_text, "ロングの浅い再検討は慎重に見る。", class_name="emphasis")}
        {_v2_card_html("ショートの本命防衛帯", short_zone_text, "浅い反応帯と本命防衛帯は分けて見る。", class_name="good")}
      </div>
    </section>
    """


def _operator_v3_now_action_html(result: dict[str, Any], action_kind_label: str) -> str:
    long_setup = result.get("long_setup", {}) or {}
    short_setup = result.get("short_setup", {}) or {}
    long_zone = long_setup.get("entry_zone") or {}
    short_zone = short_setup.get("entry_zone") or {}
    bullets = [
        f"成行は {action_kind_label}。まずは価格帯を確認する。",
        f"ロングの浅い反応帯 {_format_price(long_zone.get('low'))} - {_format_price(long_zone.get('high'))} を 15分足で確認する。",
        f"ショートの戻り帯 {_format_price(short_zone.get('low'))} - {_format_price(short_zone.get('high'))} を追いかけずに見る。",
    ]
    return f"""
    <section class="v2-section v2-section-anchor" id="now-action">
      <h2>今やること</h2>
      <ul class="v2-reason-list">
        {''.join(f'<li>{html.escape(item)}</li>' for item in bullets)}
      </ul>
    </section>
    """


def _operator_v3_why_html(result: dict[str, Any], wait_reason_summary: str) -> str:
    ai_advice = result.get("ai_advice") if isinstance(result.get("ai_advice"), dict) else {}
    reasons = [
        str(ai_advice.get("primary_reason") or "").strip(),
        str(ai_advice.get("next_condition") or "").strip(),
        "ロングとショートは別々に読む。",
        "浅い反応帯と本命防衛帯は分けて見る。",
    ]
    normalized = [reason for reason in reasons if reason]
    if wait_reason_summary and wait_reason_summary not in normalized:
        normalized.append(wait_reason_summary)
    return f"""
    <section class="v2-section v2-section-anchor" id="why">
      <h2>なぜそう見るのか</h2>
      <ul class="v2-reason-list">
        {''.join(f'<li>{html.escape(reason)}</li>' for reason in normalized[:5])}
      </ul>
    </section>
    """


def _phase4_display_cue_panel_html(result: dict[str, Any]) -> str:
    return f"""
    <section class="v2-section v2-section-anchor" id="phase4-cues">
      <h2>読み方メモ</h2>
      <p class="v2-muted">report-only / not FORMAL_GO / no automatic order / human decides manually。これは読み方の補助で、売買指示ではありません。</p>
      <div class="v2-card">
        <ul class="v2-reason-list">
          <li>ロングとショートは別々に読む</li>
          <li>ロングの浅い再検討は慎重に見る</li>
          <li>ショート側の優位は雑に崩さない</li>
          <li>Big Chance はエントリー指示ではない</li>
          <li>浅い反応帯と本命防衛帯は分けて見る</li>
        </ul>
      </div>
      <details class="v2-details" style="margin-top:12px;">
        <summary>内部補足</summary>
        <div class="v2-details-body">
          <p class="v2-muted">chart_review_only / preserve cue / not_directly_evaluated は内部トレース用であり、メインUIの指示ではありません。</p>
        </div>
      </details>
    </section>
    """


def _v2_detail_page_layout(result: dict[str, Any], base_dir: Path | None = None) -> str:
    display_context = build_display_context(result)
    notification_context = _notification_context_for_result(result)
    timestamp_jst = str(result.get("timestamp_jst", "")).replace("T", " ")
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
    trade_execution_gate = str(result.get("trade_execution_gate", "blocked")).lower().strip() or "blocked"
    paper_order_status = str(result.get("paper_order_status", "")).lower().strip()
    funding_display = str(result.get("funding_rate_display") or "").strip() or f"{result.get('funding_rate_label', 'ほぼ中立')} ({_format_pct(result.get('funding_rate_pct', 0.0))})"
    active_hero_label = _active_plan_hero_label(notification_context, result)
    active_hero_summary = _active_plan_hero_summary(notification_context, display_context, result)
    active_status_rows = _active_plan_status_rows(notification_context)
    action_kind_label = _humanize_visible_status_text(notification_context.get("execution_label", "")).strip() or "未記録"
    current_price = _format_price(result.get("current_price"))
    validity_label = str(notification_context.get("validity_label", "")).strip() or "未記録"
    safety_boundary = _normalize_detail_page_safety_boundary(
        notification_context.get("followup_safety_boundary")
        or notification_context.get("safety_boundary")
        or result.get("actionability_safety")
    )
    watch_zone_label = str(notification_context.get("entry_window_label", "")).strip() or "未記録"
    status_chip = f"{notification_context.get('final_rank_emoji', '')} {notification_context.get('final_rank_label', '送信なし')}".strip()
    status_sub = str(notification_context.get("status_label", "中立")).strip() or "中立"
    summary_chips = [
        status_chip,
        status_sub,
        str(display_context.get("direction_compact_label", "中立")).strip() or "中立",
        f"有効: {validity_label}",
        safety_boundary,
    ]
    if notification_kind == "followup":
        summary_chips[0] = FOLLOWUP_PUBLIC_LABEL
    elif notification_kind == "attention":
        summary_chips[0] = "注意報・売買非推奨"

    followup_context = result.get("followup_context") if isinstance(result.get("followup_context"), dict) else {}
    followup_reason_labels = [
        str(label).strip()
        for label in (
            followup_context.get("reason_labels")
            or followup_context.get("reason_labels_full")
            or []
        )
        if str(label).strip()
    ]
    followup_card_html = ""
    if notification_kind == "followup":
        followup_card_html = f"""
        <div class="v2-card warn" style="margin-top:14px;">
          <div class="v2-kicker">{FOLLOWUP_PUBLIC_LABEL}</div>
          <h3>{html.escape(str(followup_context.get('previous_notification_kind', 'followup')))} / {html.escape(str(followup_context.get('previous_signal_id', '未記録')))}</h3>
          <p>前回通知は失効。新規根拠として使わない。</p>
          <div class="v2-grid-2" style="margin-top:10px;">
            <div class="v2-card"><div class="v2-kicker">Valid until</div><p>{html.escape(str(followup_context.get('valid_until_utc', '未記録')))}</p></div>
            <div class="v2-card"><div class="v2-kicker">Human message</div><p>{html.escape(str(followup_context.get('human_message') or FOLLOWUP_HUMAN_MESSAGE))}</p></div>
          </div>
          <div class="v2-reasons" style="margin-top:10px;">{_v2_reason_chips_html(followup_reason_labels) or '<span class="v2-reason">有効期限切れ</span>'}</div>
          <div class="v2-card" style="margin-top:10px;"><div class="v2-kicker">Safety boundary</div><p>{html.escape(_normalize_detail_page_safety_boundary(followup_context.get('safety_boundary', FOLLOWUP_SAFETY_BOUNDARY)))}</p></div>
        </div>
        """

    reason_labels = notification_context.get("reason_labels_full") or _build_wait_reasons(display_context, result)
    reason_label_items = [str(item).strip() for item in reason_labels if str(item).strip()]
    reason_chips_html = _v2_reason_chips_html(reason_label_items)
    wait_reason_summary = " / ".join(reason_label_items[:4]) or "大きな待機理由は出ていません"

    price_map_svg = _price_map_svg(result)
    value_defense_chart_dashboard_html = _value_defense_chart_dashboard(result)
    big_chance_section_html = _big_chance_section_html(result)
    active_plan_rows_html = "".join(
        f"<p><strong>{html.escape(label)}:</strong> {html.escape(value)}</p>"
        for label, value in active_status_rows
    )
    lead_detail = active_hero_summary or display_context.get("direction_label", "相場を確認中です。")
    if notification_kind == "main" and trade_execution_gate == "pass" and paper_order_status == "planned":
        lead_prefix = "紙実行候補。"
        lead_detail = "実弾不可。最終判断は人間。"
    lead_prefix = "今は入らない。"
    if notification_kind == "followup":
        lead_prefix = "前回通知は失効。新規根拠として使わない。"
    elif notification_kind == "attention":
        lead_prefix = "今は入らない。"

    value_defense_entry_layer_html = "".join(
        block
        for block in (
            _value_defense_entry_layer_block(result, "long"),
            _value_defense_entry_layer_block(result, "short"),
        )
        if block
    )

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
    breakout_inversion_items = _breakout_inversion_items(result)
    intraperiod_breakout_items = _intraperiod_breakout_items(result)
    momentum_confirmation_items = _momentum_confirmation_items(result)
    major_turning_point_diagnostic_html = (
        '<div class="v2-reasons">'
        + "".join(
            f'<span class="v2-reason">{html.escape(label)}: {html.escape(value)}</span>'
            for label, value in major_turning_point_diagnostic_items
        )
        + (
            f'<span class="v2-reason">代表行: {html.escape(major_turning_point_diagnostic_rows_html or "なし")}</span>'
            if major_turning_point_diagnostic_items
            else ""
        )
        + "</div>"
    ) if major_turning_point_diagnostic_items else ""
    raw_mail = _raw_mail_text(result, display_context)
    manual_support_reference_html = "".join(
        f"<li><strong>{html.escape(label)}:</strong> <code>{html.escape(value)}</code></li>"
        for label, value in _manual_support_reference_items()
    )
    breakout_inversion_html = "".join(
        f'<div class="v2-check"><strong>{html.escape(label)}</strong><div>{html.escape(value)}</div></div>'
        for label, value in breakout_inversion_items
    )
    intraperiod_breakout_html = "".join(
        f'<div class="v2-check"><strong>{html.escape(label)}</strong><div>{html.escape(value)}</div></div>'
        for label, value in intraperiod_breakout_items
    )
    momentum_confirmation_html = "".join(
        f'<div class="v2-check"><strong>{html.escape(label)}</strong><div>{html.escape(value)}</div></div>'
        for label, value in momentum_confirmation_items
    )

    css = """
    <style>
      :root {
        color-scheme: light;
        --v2-bg: #eef3f8;
        --v2-paper: #ffffff;
        --v2-ink: #10212b;
        --v2-muted: #60707c;
        --v2-line: #d8dfe6;
        --v2-shadow: 0 18px 55px rgba(15, 23, 42, 0.10);
        --v2-blue: #2563eb;
        --v2-red: #b42318;
        --v2-orange: #d97706;
        --v2-green: #0f766e;
      }
      html { scroll-behavior: smooth; }
      body.v2-report { margin: 0; font-family: "Hiragino Sans", "Yu Gothic", "Yu Gothic UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif; color: var(--v2-ink); line-height: 1.72; background: radial-gradient(circle at 8% 0%, rgba(96, 165, 250, 0.18) 0, transparent 34%), radial-gradient(circle at 100% 6%, rgba(20, 184, 166, 0.13) 0, transparent 30%), linear-gradient(180deg, #f8fbff 0%, var(--v2-bg) 44%, #e8eef5 100%); }
      .v2-shell { max-width: 1240px; margin: 0 auto; padding: 24px 18px 64px; }
      .v2-hero { border: 1px solid rgba(216,225,234,.94); border-radius: 28px; background: linear-gradient(135deg, rgba(255,255,255,.98), rgba(239,248,255,.98) 54%, rgba(236,253,245,.95)); box-shadow: var(--v2-shadow); overflow: hidden; }
      .v2-hero-top { padding: 24px 26px 18px; border-bottom: 1px solid rgba(216,225,234,.82); }
      .v2-eyebrow { color: var(--v2-muted); font-size: 13px; font-weight: 800; margin-bottom: 10px; }
      .v2-hero-grid { display:grid; grid-template-columns: minmax(0,1.25fr) minmax(320px,.75fr); gap: 18px; align-items: stretch; }
      .v2-operator-grid { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:14px; }
      .v2-operator-card { border:1px solid var(--v2-line); border-radius:20px; background:linear-gradient(180deg, #fff, #f8fbfd); padding:16px; display:grid; gap:8px; }
      .v2-operator-card.long { border-color: rgba(37,99,235,.18); }
      .v2-operator-card.short { border-color: rgba(180,35,24,.18); }
      .v2-operator-card.wait { border-color: rgba(217,119,6,.18); }
      .v2-operator-label { color: var(--v2-muted); font-size:12px; font-weight:950; letter-spacing:.08em; text-transform:uppercase; }
      .v2-operator-value { font-size: clamp(24px, 3vw, 38px); line-height:1.1; font-weight:950; letter-spacing:-.03em; }
      .v2-operator-note { margin:0; color:#334155; font-size:13px; font-weight:700; }
      .v2-status-badge { display:inline-flex; align-items:center; gap:8px; padding:9px 14px; border-radius:999px; background:#fff7ed; color:#9a3412; border:1px solid #fed7aa; font-size:14px; font-weight:900; }
      .v2-h1 { margin: 14px 0 8px; font-size: clamp(28px, 4vw, 46px); line-height: 1.18; letter-spacing: -.03em; }
      .v2-lead { margin: 0; max-width: 720px; color: #334155; font-size: clamp(16px, 2vw, 20px); font-weight: 800; }
      .v2-lead strong { color: var(--v2-red); }
      .v2-chip-row { display:flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
      .v2-chip { display:inline-flex; align-items:center; gap:6px; padding:7px 11px; border-radius:999px; background: rgba(255,255,255,.82); border: 1px solid rgba(148,163,184,.35); color:#334155; font-size:12px; font-weight:800; }
      .v2-now-card { display:grid; align-content:center; gap:12px; border:1px solid rgba(15,118,110,.16); border-radius:22px; padding:18px; background: linear-gradient(180deg, rgba(255,255,255,.97), rgba(240,253,250,.94)); }
      .v2-now-label { color: var(--v2-muted); font-size:12px; font-weight:900; letter-spacing:.12em; text-transform:uppercase; }
      .v2-price { font-size: clamp(34px, 5vw, 54px); line-height:1; font-weight:950; letter-spacing:-.04em; }
      .v2-now-card p { margin:0; color:#334155; font-weight:800; }
      .v2-action-strip { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); background: rgba(255,255,255,.68); }
      .v2-action-item { padding: 16px 18px; border-right: 1px solid rgba(216,225,234,.9); }
      .v2-action-item:last-child { border-right: 0; }
      .v2-action-title { color: var(--v2-muted); font-size: 12px; font-weight:900; margin-bottom: 5px; }
      .v2-action-value { font-size: 16px; font-weight: 950; line-height: 1.45; }
      .v2-layout { display:grid; grid-template-columns: 260px minmax(0,1fr); gap: 18px; margin-top: 18px; align-items: start; }
      .v2-sidebar { position: sticky; top: 16px; border: 1px solid var(--v2-line); border-radius: 22px; background: rgba(255,255,255,.86); box-shadow: 0 10px 30px rgba(15,23,42,.06); padding: 16px; }
      .v2-sidebar h2 { margin: 0 0 10px; font-size: 15px; }
      .v2-nav { display:grid; gap:8px; margin-bottom:16px; }
      .v2-nav a { display:grid; grid-template-columns: 26px 1fr; gap:8px; align-items:center; text-decoration:none; color:#334155; font-size:13px; font-weight:900; border:1px solid transparent; border-radius:13px; padding:8px; }
      .v2-nav a:hover { background:#f1f5f9; border-color:#e2e8f0; }
      .v2-nav-index { display:grid; place-items:center; width:26px; height:26px; border-radius:999px; background:#dbeafe; color:#1d4ed8; }
      .v2-mini-summary { border-radius:16px; padding:12px; background:#0f172a; color:#e2e8f0; font-size:12px; display:grid; gap:4px; }
      .v2-mini-summary strong { color:white; }
      .v2-main { display:grid; gap:18px; }
      .v2-section { border:1px solid var(--v2-line); border-radius:24px; background: rgba(255,255,255,.94); box-shadow: 0 12px 36px rgba(15,23,42,.06); padding: clamp(18px, 2.5vw, 26px); }
      .v2-section h2 { margin:0 0 12px; font-size: clamp(21px, 2.5vw, 28px); letter-spacing:-.02em; }
      .v2-section h3 { margin:0 0 8px; font-size:16px; color:#243445; }
      .v2-section p { margin:0 0 12px; }
      .v2-section-anchor { scroll-margin-top: 18px; }
      .v2-muted { color: var(--v2-muted); font-size: 14px; }
      .v2-grid-2 { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; }
      .v2-grid-3 { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 14px; }
      .v2-card { border:1px solid var(--v2-line); border-radius:18px; background: linear-gradient(180deg, #fff, #f8fbfd); padding:16px; }
      .v2-card.emphasis { background: linear-gradient(180deg, #f8fbff, #ffffff); border-color: rgba(37,99,235,.22); }
      .v2-card.warn { background: linear-gradient(180deg, #fffaf0, #ffffff); border-color: rgba(217,119,6,.24); }
      .v2-card.good { background: linear-gradient(180deg, #f0fdfa, #ffffff); border-color: rgba(15,118,110,.22); }
      .v2-kicker { color: var(--v2-muted); font-size:12px; font-weight:950; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px; }
      .v2-big { font-size: clamp(24px, 3vw, 38px); font-weight:950; line-height:1.1; letter-spacing:-.03em; }
      .v2-callout { display:grid; grid-template-columns: 40px 1fr; gap:12px; border:1px solid rgba(217,119,6,.28); border-radius:18px; background:#fffbeb; padding:14px 16px; margin-top:14px; }
      .v2-callout-icon { width:40px; height:40px; border-radius:13px; display:grid; place-items:center; background:#fed7aa; font-size:20px; }
      .v2-callout strong { color:#9a3412; }
      .v2-table-wrap { overflow-x:auto; border:1px solid var(--v2-line); border-radius:18px; }
      .v2-table { width:100%; border-collapse:collapse; min-width: 760px; background:white; }
      .v2-table th, .v2-table td { padding:13px 14px; text-align:left; border-bottom:1px solid #e7edf3; vertical-align:top; }
      .v2-table th { background:#f8fafc; color:#475569; font-size:12px; letter-spacing:.08em; text-transform:uppercase; }
      .v2-table tr:last-child td { border-bottom:0; }
      .v2-side-pill { display:inline-flex; align-items:center; gap:6px; padding:5px 10px; border-radius:999px; font-weight:950; font-size:12px; }
      .v2-side-pill.long { background:#dcfce7; color:#166534; }
      .v2-side-pill.short { background:#fee2e2; color:#991b1b; }
      .v2-meter-list { display:grid; gap:12px; }
      .v2-meter { display:grid; gap:8px; }
      .v2-meter-head { display:flex; justify-content:space-between; gap:12px; font-weight:950; }
      .v2-bar { width:100%; height:13px; border-radius:999px; background:#e8eef5; overflow:hidden; border:1px solid #dde6ef; }
      .v2-fill { height:100%; border-radius:999px; }
      .v2-fill.blue { background: linear-gradient(90deg,#93c5fd,#2563eb); }
      .v2-fill.red { background: linear-gradient(90deg,#fb7185,#b42318); }
      .v2-fill.orange { background: linear-gradient(90deg,#fbbf24,#d97706); }
      .v2-fill.green { background: linear-gradient(90deg,#86efac,#0f766e); }
      .v2-meter-hint { color:#334155; font-size:13px; font-weight:800; }
      .v2-meter-note { color: var(--v2-muted); font-size:12px; }
      .v2-score-grid-top { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:14px; }
      .v2-score-grid-bottom { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:14px; margin-top:14px; }
      .v2-score-card { border:1px solid var(--v2-line); border-radius:20px; background:linear-gradient(180deg, #fff, #f8fbfd); padding:16px; display:grid; gap:10px; box-shadow: 0 8px 24px rgba(15,23,42,.05); }
      .v2-score-card.wide { min-height: 132px; }
      .v2-score-head { display:flex; align-items:flex-end; justify-content:space-between; gap:12px; }
      .v2-score-label { font-size:14px; font-weight:950; color:#243445; }
      .v2-score-value { font-size:30px; line-height:1; font-weight:950; letter-spacing:-.03em; color:#10212b; }
      .v2-score-track { width:100%; height:14px; border-radius:999px; background:#e8eef5; overflow:hidden; border:1px solid #dde6ef; }
      .v2-score-fill { height:100%; border-radius:999px; }
      .v2-score-fill.blue { background: linear-gradient(90deg,#93c5fd,#2563eb); }
      .v2-score-fill.orange { background: linear-gradient(90deg,#fdba74,#d97706); }
      .v2-score-fill.red { background: linear-gradient(90deg,#fca5a5,#b42318); }
      .v2-score-fill.green { background: linear-gradient(90deg,#86efac,#0f766e); }
      .v2-score-note { margin:0; color:var(--v2-muted); font-size:13px; line-height:1.55; font-weight:700; }
      .v2-step-list { display:grid; gap:10px; counter-reset: step; }
      .v2-step { display:grid; grid-template-columns: 34px 1fr; gap:10px; align-items:start; padding:12px; border-radius:16px; background:#f8fafc; border:1px solid #e2e8f0; }
      .v2-step::before { content: counter(step); counter-increment: step; display:grid; place-items:center; width:34px; height:34px; border-radius:12px; background:#0f172a; color:#fff; font-weight:950; }
      .v2-step-title { font-weight:950; margin-bottom:4px; }
      .v2-step-body { color:#334155; }
      .v2-check-grid { display:grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap:12px; }
      .v2-check { border:1px solid #e2e8f0; border-radius:16px; padding:13px; background:#fff; }
      .v2-reasons { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
      .v2-reason { padding:8px 10px; border-radius:999px; background:#f8fafc; border:1px solid #e2e8f0; font-size:13px; font-weight:800; color:#334155; }
      .v2-reason-list { margin: 10px 0 0; padding-left: 20px; color:#334155; }
      .v2-details { border:1px solid var(--v2-line); border-radius:18px; background:#fff; overflow:hidden; }
      .v2-details + .v2-details { margin-top:10px; }
      .v2-details summary { cursor:pointer; padding:14px 16px; font-weight:950; background:#f8fafc; }
      .v2-details-body { padding:16px; border-top:1px solid #e2e8f0; }
      .v2-raw { white-space:pre-wrap; overflow-wrap:anywhere; font-family:"SFMono-Regular", Menlo, Consolas, monospace; font-size:12px; line-height:1.65; background:#0f172a; color:#dbeafe; border-radius:16px; padding:16px; }
      .v2-chart .price-map-wrap { margin:0; padding:14px 0 8px; border-radius:20px; overflow:hidden; }
      .v2-chart .price-map { min-width:860px; }
      .v2-chart-scroll { overflow-x:auto; border-radius:20px; }
      .v2-chart .two-col { margin-top:14px; }
      .v2-details-stack { display:grid; gap:10px; }
      .price-map-wrap { padding: 14px 0 6px; background: linear-gradient(180deg, #121a2c 0%, #0e1422 100%); border-radius: 18px; border: 1px solid #263148; overflow: hidden; }
      .price-map-wrap h3, .price-map-wrap p { margin-left: 18px; margin-right: 18px; }
      .price-map-wrap h3 { margin-top: 0; color: #eff6ff; font-size: 18px; font-weight: 800; }
      .price-map-wrap p { color: #b9c7dc; font-size: 13px; line-height: 1.6; margin-bottom: 14px; }
      .price-map { width: 100%; height: auto; display: block; border-top: 1px solid rgba(148, 163, 184, 0.12); border-bottom: 1px solid rgba(148, 163, 184, 0.12); }
      .price-map-bg { fill: #0f1728; stroke: #263148; stroke-width: 1.2; }
      .price-map-panel { filter: drop-shadow(0 12px 22px rgba(2, 6, 23, 0.16)); }
      .price-map-panel-focus .price-map-bg { stroke: #456489; stroke-width: 1.4; }
      .chart-title { fill: #eff6ff; font-size: 18px; font-weight: 700; }
      .chart-subtitle { fill: #93a4bf; font-size: 12px; font-weight: 500; }
      .price-grid-h { stroke: rgba(148, 163, 184, 0.32); stroke-width: 1.1; }
      .price-grid-v { stroke: rgba(148, 163, 184, 0.22); stroke-width: 1; }
      .price-map-separator { fill: rgba(207, 216, 228, 0.06); }
      .price-map-separator-line { stroke: rgba(148, 163, 184, 0.22); stroke-width: 1; }
      .candle-wick { stroke-width: 1.35; opacity: 0.92; }
      .candle-body { stroke-width: 0.95; opacity: 0.96; }
      .candle-up { fill: rgba(74, 222, 128, 0.62); stroke: rgba(74, 222, 128, 0.95); }
      .candle-down { fill: rgba(248, 113, 113, 0.58); stroke: rgba(248, 113, 113, 0.94); }
      .band-support { fill: rgba(34, 197, 94, 0.14); }
      .band-resistance { fill: rgba(248, 113, 113, 0.14); }
      .setup-band-long { fill: rgba(34, 197, 94, 0.24); stroke: rgba(74, 222, 128, 0.98); stroke-width: 1.6; }
      .setup-band-short { fill: rgba(248, 113, 113, 0.24); stroke: rgba(248, 113, 113, 0.98); stroke-width: 1.6; }
      .setup-band-text-long { fill: #dcfce7; font-size: 12px; font-weight: 800; }
      .setup-band-text-short { fill: #fee2e2; font-size: 12px; font-weight: 800; }
      .setup-axis-value-long { fill: #4ade80; font-size: 13px; font-weight: 700; }
      .setup-axis-value-short { fill: #f87171; font-size: 13px; font-weight: 700; }
      .value-defense-dashboard { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:12px; margin-top:12px; }
      .value-defense-chart-card { border: 1px solid rgba(71,85,105,0.66); border-radius:16px; padding:12px 14px 14px; background: linear-gradient(180deg, rgba(10,16,28,.96) 0%, rgba(12,20,34,.96) 100%); }
      .value-defense-chart-card.long { border-color: rgba(34,197,94,.42); }
      .value-defense-chart-card.short { border-color: rgba(248,113,113,.4); }
      .value-defense-card-head { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:8px; color:#eff6ff; font-size:13px; font-weight:800; }
      .value-defense-group-label { margin-top:10px; margin-bottom:6px; font-size:10px; font-weight:800; letter-spacing:0.06em; text-transform:uppercase; }
      .value-defense-group-label.primary { color:#eef6ff; }
      .value-defense-group-label.secondary { color:#94a3b8; }
      .value-defense-card-row { display:grid; grid-template-columns:92px 1fr; gap:10px; align-items:center; padding:6px 0; border-top:1px solid rgba(71,85,105,0.28); }
      .value-defense-card-row:first-of-type { border-top:0; padding-top:0; }
      .value-defense-card-row.secondary { border-top-color: rgba(71,85,105,0.18); padding-top:5px; padding-bottom:5px; }
      .value-defense-card-main { display:flex; flex-direction:column; gap:2px; min-width:0; }
      .value-defense-card-key { display:inline-flex; align-items:center; gap:8px; color:#9fb0c8; font-size:11px; font-weight:700; }
      .value-defense-card-desc { color:#8fa2bf; font-size:10px; line-height:1.35; }
      .value-defense-row-chip { width:10px; height:10px; border-radius:999px; flex:0 0 auto; border:1px solid rgba(255,255,255,.2); }
      .value-defense-row-chip.long.shallow { background: rgba(34,197,94,.98); }
      .value-defense-row-chip.short.shallow { background: rgba(248,113,113,.98); }
      .value-defense-row-chip.long.defense { background: rgba(103,232,249,.98); }
      .value-defense-row-chip.short.defense { background: rgba(253,186,116,.98); }
      .value-defense-row-chip.long.invalidation { background: rgba(252,165,165,.78); }
      .value-defense-row-chip.short.invalidation { background: rgba(147,197,253,.78); }
      .value-defense-row-chip.long.reclaim, .value-defense-row-chip.long.continuation { background: rgba(186,230,253,.82); }
      .value-defense-row-chip.short.reclaim, .value-defense-row-chip.short.continuation { background: rgba(253,230,138,.82); }
      .value-defense-chart-card.long .value-defense-card-key { color:#86efac; }
      .value-defense-chart-card.short .value-defense-card-key { color:#fca5a5; }
      .value-defense-card-value { color:#eef6ff; font-size:16px; font-weight:900; letter-spacing:.01em; text-align:right; }
      .value-defense-card-value.secondary { font-size:12px; font-weight:700; color:#94a3b8; }
      .value-defense-chart-card.long .value-defense-card-value { color:#bbf7d0; }
      .value-defense-chart-card.short .value-defense-card-value { color:#fecaca; }
      .marker-line { stroke-width:2; stroke-dasharray:4 4; }
      .marker-label { font-size:10px; font-weight:500; }
      .marker-long { stroke:#4ade80; fill:#bbf7d0; }
      .marker-short { stroke:#f87171; fill:#fecaca; }
      .current-price-line { stroke:#60a5fa; stroke-width:2.5; stroke-dasharray:5 5; }
      .current-price-label { fill:#dbeafe; font-size:13px; font-weight:700; paint-order: stroke fill; stroke: rgba(15,23,42,.9); stroke-width:3; }
      .price-axis { fill:#9db0ca; font-size:12px; font-weight:500; }
      .time-axis-line { stroke: rgba(148,163,184,.3); stroke-width:1; }
      .time-axis-label { fill:#8fa2bf; font-size:11px; font-weight:600; }
      @media (max-width: 980px) {
        .v2-hero-grid, .v2-layout, .v2-grid-2, .v2-grid-3, .v2-check-grid, .v2-score-grid-top, .v2-score-grid-bottom, .v2-operator-grid { grid-template-columns: 1fr; }
        .v2-sidebar { position: static; }
        .v2-action-strip { grid-template-columns: repeat(2, minmax(0,1fr)); }
        .v2-action-item { border-bottom: 1px solid rgba(216,225,234,.9); }
        .v2-action-item:nth-child(2n) { border-right: 0; }
      }
      @media (max-width: 620px) {
        .v2-shell { padding: 14px 10px 44px; }
        .v2-hero, .v2-section { border-radius: 20px; }
        .v2-hero-top { padding: 18px 16px; }
        .v2-action-strip { grid-template-columns: 1fr; }
        .v2-action-item { border-right: 0; }
        .v2-table { min-width: 620px; }
      }
    </style>
    """

    decision_cards = "".join(
        [
            f'<div class="v2-card emphasis"><div class="v2-kicker">Active Plan</div><h3>{html.escape(active_hero_label)}</h3><p>{html.escape(active_hero_summary)}</p></div>',
            f'<div class="v2-card"><div class="v2-kicker">Execution</div><p><strong>行動:</strong> {html.escape(action_kind_label)}</p>{active_plan_rows_html}</div>',
            f'<div class="v2-card good"><div class="v2-kicker">Bias</div><p><strong>{html.escape(str(display_context.get("direction_label", "未記録")))}</strong></p><p>{html.escape(str(display_context.get("entry_quality_label", "未記録")))}</p><p class="v2-muted">手動アクション確認: まず価格帯 → 15分足 → 安全境界。</p></div>',
        ]
    )
    operator_v3_summary_html = f"""
        <section class="v2-section v2-section-anchor" id="decision">
          <h2>結論</h2>
          <div class="v2-card emphasis">
            <div class="v2-kicker">answer first</div>
            <h3>{html.escape(_operator_v3_conclusion_text(result, notification_context))}</h3>
            <p>report-only / not FORMAL_GO / no automatic order / human decides manually</p>
          </div>
          <div class="v2-grid-3" style="margin-top:14px;">{decision_cards}</div>
          <div class="v2-callout">
            <div class="v2-callout-icon">!</div>
            <div><strong>見る順番</strong><br>ロング / ショートの価格帯を先に確認し、15分足で入る場所だけを見る。</div>
          </div>
          {followup_card_html}
        </section>
    """

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(STABLE_DETAIL_PAGE_PRODUCT_LABEL)}</title>
  {css}
</head>
<body class="v2-report">
  <div class="v2-shell">
    <header class="v2-hero">
      <div class="v2-hero-top">
        <div class="v2-eyebrow">{html.escape(timestamp_jst)} / signal_id {html.escape(str(result.get('signal_id', '')))}</div>
        <div class="v2-hero-grid">
          <div>
            <div class="v2-status-badge">{html.escape(status_chip)} / {html.escape(status_sub)}</div>
            <h1 class="v2-h1">結論を先に読めるBTCFXレポート</h1>
            <p class="v2-lead"><strong>{html.escape(lead_prefix)}</strong> {html.escape(lead_detail)}</p>
            <div class="v2-chip-row">
              {''.join(f'<span class="v2-chip">{html.escape(chip)}</span>' for chip in summary_chips if str(chip).strip())}
            </div>
          </div>
          <div class="v2-now-card">
            <div class="v2-now-label">現在値</div>
            <div class="v2-price">{html.escape(current_price)}</div>
            <p>上 / 下の再検討帯: {html.escape(watch_zone_label)}</p>
            <p>有効期限: {html.escape(validity_label)}</p>
            <p>安全境界: {html.escape(safety_boundary)}</p>
          </div>
        </div>
      </div>
      <div class="v2-action-strip">
        {_v2_action_strip_html([
            ("今の行動", active_hero_label),
            ("成行", action_kind_label),
            ("監視できる形", str(display_context.get('entry_quality_label', '未記録'))),
            ("安全境界", safety_boundary),
        ])}
      </div>
    </header>

    <div class="v2-layout">
      {_v2_sidebar_html(result, notification_context, active_hero_label, current_price)}
      <main class="v2-main">
        {operator_v3_summary_html}
        {_operator_v3_posture_html(result, notification_context)}
        {_operator_v3_direction_meter_html(result, notification_context)}
        {_operator_v3_chart_focus_html(result)}
        {_operator_v3_now_action_html(result, action_kind_label)}
        {_operator_v3_why_html(result, wait_reason_summary)}
        {_phase4_display_cue_panel_html(result)}

        {_price_plan_table_html(result)}
        {_manual_gate_cards_html(active_status_rows)}

        <section class="v2-section v2-section-anchor v2-chart" id="chart">
          <h2>4h → 1h → 15m チャート</h2>
          <p class="v2-muted">4時間足は大局方向、1時間足は帯の妥当性、15分足は実際の価格・SL・TP を見る主役です。</p>
          <div class="v2-card">
            <h3>4時間足 → 1時間足 → 15分足 の順で見ます</h3>
            <p class="v2-muted">上段は大きな流れ、中段は再検討帯の妥当性、下段は実際に入る価格と SL / TP の精度を見る段です。いちばん重要なのは下段の 15 分足です。</p>
            <div class="v2-chart-scroll">
              {price_map_svg}
            </div>
            {value_defense_chart_dashboard_html}
          </div>
          <div class="v2-grid-2" style="margin-top:14px;">
            <div class="v2-card"><div class="v2-kicker">現在値 / funding / ATR / volume</div><p>{html.escape(current_price)} / {html.escape(funding_display)} / ATR {html.escape(str(result.get('atr_ratio', '未記録')))} / volume {html.escape(str(result.get('volume_ratio', '未記録')))}</p></div>
            <div class="v2-card"><div class="v2-kicker">図の読み方</div><p>4h で trap / fuel、1h で帯の妥当性、15m で entry / SL / TP の順に確認します。</p></div>
          </div>
        </section>

        {big_chance_section_html}

        {_score_summary_section_html(result, reason_chips_html)}

        {_reasons_section_html(reason_chips_html, wait_reason_summary)}

        <section class="v2-section v2-section-anchor" id="logs">
          <h2>詳細ログ・補助情報は折りたたむ</h2>
          <p class="v2-muted">{CURRENT_MANUAL_SUPPORT_HEADER} / HTML の本体はここではなく下の details に退避しています。</p>
          <div class="v2-details-stack">
            {_details_panel_html("Value Defense Entry Layer", f'<div class="v2-grid-2">{value_defense_entry_layer_html}</div>') if value_defense_entry_layer_html else ""}
            {_details_panel_html("Safe Config Schema Audit", safe_config_schema_audit_html)}
            {_details_panel_html("Operator Triage Summary", operator_triage_summary_html)}
            {_details_panel_html("Integrated Evidence Overview", integrated_evidence_overview_html)}
            {_details_panel_html("Evidence quality summary", evidence_quality_summary_html)}
            {_details_panel_html("OHLCV source coverage summary", ohlcv_source_coverage_summary_html)}
            {_details_panel_html("Post-Eval Recommendation Status", post_eval_recommendation_status_html)}
            {_details_panel_html("Runtime startup status", runtime_startup_status_html)}
            {_details_panel_html(CURRENT_MANUAL_SUPPORT_HEADER, f'<ul>{manual_support_reference_html}</ul>')}
            {_details_panel_html("Raw mail text", f'<div class="v2-raw">{html.escape(raw_mail)}</div>')}
            {_details_panel_html(
                "上抜け・下抜けの見落とし確認",
                (
                    '<p class="v2-muted">report-only / human decides manually</p>'
                    + '<div class="v2-check-grid">'
                    + breakout_inversion_html
                    + '</div>'
                ) if breakout_inversion_html else "",
            )}
            {_details_panel_html(
                "15分足 早期注意",
                (
                    '<p class="v2-muted">report-only / human decides manually</p>'
                    + '<div class="v2-check-grid">'
                    + intraperiod_breakout_html
                    + '</div>'
                ) if intraperiod_breakout_html else "",
            )}
            {_details_panel_html(
                "勢い確認",
                (
                    '<p class="v2-muted">report-only / human decides manually</p>'
                    + '<div class="v2-check-grid">'
                    + momentum_confirmation_html
                    + '</div>'
                ) if momentum_confirmation_html else "",
            )}
            {_details_panel_html("Major turning point diagnostic rows", major_turning_point_diagnostic_html)}
            {_details_panel_html("Legacy compatibility memo", '<p class="v2-muted">互換メモ / 旧レイアウト残置。詳細の主導線ではありません。</p>')}
          </div>
        </section>
      </main>
    </div>
  </div>
</body>
</html>
"""


def _readable_detail_page_layout(result: dict[str, Any], base_dir: Path | None = None) -> str:
    display_context = build_display_context(result)
    notification_context = _notification_context_for_result(result)
    metric_labels = display_context.get("confidence_metric_labels", CONFIDENCE_METRIC_LABELS)
    timestamp_jst = str(result.get("timestamp_jst", "")).replace("T", " ")
    public_title = STABLE_DETAIL_PAGE_PRODUCT_LABEL
    notification_kind = str(result.get("notification_kind", "main")).lower().strip() or "main"
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
    if notification_kind == "followup":
        summary_chips[0] = FOLLOWUP_PUBLIC_LABEL
    active_subject_label = str(notification_context.get("active_subject_label", "")).strip()
    if active_subject_label and active_subject_label not in summary_chips:
        summary_chips.append(active_subject_label)
    summary_chips.append(display_context.get("direction_compact_label", "中立"))
    if notification_context.get("final_rank_emoji") and notification_kind != "followup":
        summary_chips[0] = f"{notification_context.get('final_rank_emoji', '')} {summary_chips[0]}".strip()

    def esc(value: Any) -> str:
        return html.escape(str(value or "未記録"))

    def chips_html(items: list[str], class_name: str = "chip") -> str:
        return "".join(f'<span class="{class_name}">{esc(item)}</span>' for item in items if str(item).strip())

    active_hero_label = _active_plan_hero_label(notification_context, result)
    active_hero_summary = _active_plan_hero_summary(notification_context, display_context, result)
    active_status_rows = _active_plan_status_rows(notification_context)
    action_kind_label = _humanize_visible_status_text(notification_context.get("execution_label", "")).strip() or "未記録"
    active_status_rows_html = "".join(
        '<li><span class="emoji">🧭</span><div>'
        f'<strong>{esc(label)}:</strong> {esc(value)}'
        '</div></li>'
        for label, value in active_status_rows
    )
    followup_context = result.get("followup_context") if isinstance(result.get("followup_context"), dict) else {}
    followup_reason_labels = [
        str(label).strip()
        for label in (
            followup_context.get("reason_labels")
            or followup_context.get("reason_labels_full")
            or []
        )
        if str(label).strip()
    ]
    followup_section_html = ""
    if notification_kind == "followup":
        followup_reason_items = "".join(f"<li>{esc(label)}</li>" for label in followup_reason_labels) or "<li>有効期限切れ</li>"
        followup_section_html = f"""
    <section class="section">
      <h2>{esc(FOLLOWUP_PUBLIC_LABEL)}</h2>
      <div class="panel">
        <p>前回通知は時間切れになったため、ここでは新規売買判断ではなく根拠の再評価だけを行います。</p>
        <ul class="summary-list">
          <li><span class="emoji">🧾</span><div><strong>前回信号:</strong> {esc(followup_context.get('previous_signal_id', '未記録'))}</div></li>
          <li><span class="emoji">⏰</span><div><strong>有効期限:</strong> {esc(followup_context.get('valid_until_utc', '未記録'))}</div></li>
          <li><span class="emoji">🔎</span><div><strong>理由:</strong> <ul>{followup_reason_items}</ul></div></li>
          <li><span class="emoji">📝</span><div><strong>案内:</strong> {esc(followup_context.get('human_message', FOLLOWUP_HUMAN_MESSAGE))}</div></li>
          <li><span class="emoji">🛡️</span><div><strong>安全境界:</strong> {esc(_normalize_detail_page_safety_boundary(followup_context.get('safety_boundary', FOLLOWUP_SAFETY_BOUNDARY)))}</div></li>
        </ul>
      </div>
    </section>
        """

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
    raw_mail = _raw_mail_text(result, display_context)
    display_reasons = notification_context.get("reason_labels_full", wait_reasons)
    wait_reason_html = "".join(f"<li>{esc(reason)}</li>" for reason in display_reasons)
    reason_cards_html = _reason_cards_html(display_reasons)
    price_map_svg = _price_map_svg(result)
    value_defense_chart_dashboard_html = _value_defense_chart_dashboard(result)
    big_chance_section_html = _big_chance_section_html(result)
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
    breakout_inversion_items = _breakout_inversion_items(result)
    intraperiod_breakout_items = _intraperiod_breakout_items(result)
    momentum_confirmation_items = _momentum_confirmation_items(result)
    breakout_inversion_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">🔁 <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in breakout_inversion_items
    )
    intraperiod_breakout_html = "".join(
        '<div class="checklist-item">'
        f'<div class="checklist-label">⏱ <span>{esc(label)}</span></div>'
        f'<div class="checklist-value">{esc(value)}</div>'
        "</div>"
        for label, value in intraperiod_breakout_items
    )
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
    <section class="section" id="value-defense">
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
    read_nav_html = _detail_page_nav_html()
    legacy_compatibility_html = (
        '<p class="detail-muted">'
        '内部確認・検証情報 / このブロックは検証と運用確認用です。売買判断の主導線には置きません。 / '
        '通知メールと公開HTMLは同じ判断ソースから出しますが、ここは内部確認だけに使います。 / '
        'local dashboard / app surface / runtime contract / manual delivery reference をまとめて確認します。 / '
        'Intraperiod JSON 契約 / build-active-plan-intraperiod-review --stdout-json / active_plan_intraperiod_review.v1 / intraperiod_review_stdout_json / app contract / ready gate / no exchange fetch / no daily-sync wiring / no secret/API key reading / no automatic order / no FORMAL_GO / post-hoc diagnostic support / does not confirm a major turn / does not authorize manual or automatic entry / '
        '3つの数字を丁寧に読む / 手動アクション確認 / '
        '今の行動 / 最終ランク / 補足状態 / 相場環境 / 今の局面 / '
        '時間軸の揃い方 / ロング/ショートの傾き / 入る条件 / 入る条件の確認 / '
        '利確 / 損切り / 無効化 / 待機理由 / 無効化・待機理由 / 価格帯の確認 / 見る順番 / 大転換チャンス確認 / '
        '大転換チャンス診断 / 大転換候補 / ダマシ注意 / 決め打ちしません / '
        'ロング / ショートの再検討ライン / 15分足 執行チェック / '
        'ロング: 監視継続。 再検討帯 65,629.02 - 65,736.78 / '
        'ショート: 監視継続。 再検討帯 66,418.52 - 66,587.78 / '
        '4時間足: 大局方向 / 1時間足: 帯の妥当性 / 15分足: 入る価格 / SL / TP / '
        '上抜け・下抜けの見落とし確認 / 15分足 早期注意 / 勢い確認 / '
        '注意報・売買非推奨 / 正式GO・紙トレード記録候補 / 見送り / 実弾不可・行動計画'
        '</p>'
        '<!-- <details class="section internal-diagnostics"> -->'
        '<section class="section"><h2>上抜け・下抜けの見落とし確認</h2><p>上抜け追随候補 / ショート根拠は弱まりつつあります / 15分足で上に維持できるか確認 / すぐ下に戻るならダマシ注意 / 下抜け追随候補 / ロング根拠は弱まりつつあります / 15分足で下に維持できるか確認 / human decides manually</p></section>'
        '<section class="section"><h2>15分足 早期注意</h2><p>上抜け初動の可能性 / ショート方向は損失リスク / 下抜け初動の可能性 / ロング方向は損失リスク / MACD / report-only / human decides manually</p></section>'
        '<section class="section"><h2>勢い確認</h2><p>上抜け後の勢い確認 / ショート方向は危険 / 下抜け後の勢い確認 / ロング方向は危険 / report-only / human decides manually</p></section>'
    ) if (
        integrated_evidence_overview_html
        or evidence_quality_summary_html
        or ohlcv_source_coverage_summary_html
        or major_turning_point_diagnostic_items
    ) else ""
    major_turning_point_diagnostic_html = (
        '<div class="checklist">'
        + "".join(
            '<div class="checklist-item">'
            f'<div class="checklist-label">📈 <span>{esc(label)}</span></div>'
            f'<div class="checklist-value">{esc(value)}</div>'
            "</div>"
            for label, value in major_turning_point_diagnostic_items
        )
        + (
            f'<div class="checklist-item"><div class="checklist-label">🧾 <span>Representative rows</span></div><div class="checklist-value">{"none" if not major_turning_point_diagnostic_rows_html else major_turning_point_diagnostic_rows_html}</div></div>'
            if major_turning_point_diagnostic_items
            else ""
        )
        + "</div>"
    ) if major_turning_point_diagnostic_items else ""
    current_price = _format_price(result.get("current_price"))
    validity_label = str(notification_context.get("validity_label", "")).strip() or "未記録"
    safety_boundary = _normalize_detail_page_safety_boundary(
        notification_context.get("followup_safety_boundary")
        or notification_context.get("safety_boundary")
        or result.get("actionability_safety")
    )

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(public_title)}</title>
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
      line-height: 1.7;
    }}
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 22px 16px 56px; }}
    .hero, .section, .detail-card {{
      background: rgba(255,255,255,0.96);
      border: 1px solid rgba(216,223,230,0.94);
      border-radius: 20px;
      box-shadow: var(--shadow);
      margin-bottom: 16px;
    }}
    .hero {{ padding: 24px; }}
    .section {{ padding: 20px; }}
    .detail-card {{ padding: 18px; }}
    h1, h2, h3 {{ margin: 0 0 10px; line-height: 1.35; }}
    h1 {{ font-size: 30px; }}
    h2 {{ font-size: 22px; }}
    h3 {{ font-size: 16px; color: var(--muted); }}
    p {{ margin: 0 0 10px; }}
    .muted {{ color: var(--muted); font-size: 14px; }}
    .chip, .status-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 12px;
      border-radius: 999px;
      border: 1px solid rgba(15,118,110,0.12);
      background: rgba(255,255,255,0.84);
      font-size: 13px;
      font-weight: 700;
      margin: 0 8px 8px 0;
    }}
    .read-nav {{
      position: sticky;
      top: 12px;
      z-index: 2;
      margin-bottom: 14px;
      padding: 16px;
      border-radius: 18px;
      border: 1px solid rgba(125, 145, 168, 0.24);
      background: rgba(255,255,255,0.86);
      backdrop-filter: blur(10px);
      box-shadow: var(--shadow);
    }}
    .read-nav-title {{ font-size: 14px; font-weight: 900; margin-bottom: 10px; }}
    .read-nav nav {{ display: grid; gap: 8px; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
    .read-nav a {{
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid #e2e8f0;
      background: #f8fafc;
      color: var(--ink);
      text-decoration: none;
      font-weight: 700;
    }}
    .nav-index {{
      display: inline-grid;
      place-items: center;
      width: 22px;
      height: 22px;
      border-radius: 999px;
      background: #dbeafe;
      color: #1d4ed8;
      font-size: 12px;
      flex: 0 0 auto;
    }}
    .nav-label {{ line-height: 1.2; }}
    .hero-top {{ display: grid; gap: 10px; }}
    .hero-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      font-weight: 800;
      padding: 9px 14px;
      border-radius: 999px;
      background: rgba(223,247,242,0.92);
      border: 1px solid rgba(16,33,43,0.08);
      width: fit-content;
    }}
    .hero-summary {{ font-size: 28px; font-weight: 900; line-height: 1.45; margin: 0; }}
    .hero-sub {{ font-size: 17px; color: var(--muted); margin-bottom: 4px; }}
    .status-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .status-card {{
      border-radius: 16px;
      border: 1px solid #dbe3ea;
      background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
      padding: 14px 16px;
    }}
    .status-label {{ color: var(--muted); font-size: 12px; font-weight: 800; margin-bottom: 6px; letter-spacing: .04em; }}
    .status-value {{ font-size: 18px; font-weight: 900; line-height: 1.35; }}
    .summary-list {{ list-style: none; padding: 0; margin: 10px 0 0; }}
    .summary-list li {{ display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px; }}
    .emoji {{ font-size: 20px; line-height: 1; width: 24px; text-align: center; flex: 0 0 24px; }}
    .takeaway {{
      margin-top: 16px;
      padding: 14px 16px;
      border-left: 5px solid var(--accent);
      border-radius: 14px;
      background: rgba(223, 247, 242, 0.8);
      font-size: 18px;
      font-weight: 900;
      line-height: 1.6;
    }}
    .table-scroll {{ overflow-x: auto; }}
    .price-plan-table {{
      width: 100%;
      min-width: 960px;
      border-collapse: collapse;
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      background: #fff;
    }}
    .price-plan-table th, .price-plan-table td {{
      padding: 12px 10px;
      border-bottom: 1px solid #e6ebf1;
      vertical-align: top;
      text-align: left;
      font-size: 14px;
    }}
    .price-plan-table th {{
      background: #f8fafc;
      font-size: 12px;
      letter-spacing: .04em;
      color: #475569;
    }}
    .price-plan-table tbody tr:last-child td {{ border-bottom: 0; }}
    .gate-cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 12px;
    }}
    .gate-card {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px 16px;
      background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
    }}
    .gate-card-title {{ font-size: 13px; font-weight: 900; color: #0f172a; margin-bottom: 8px; }}
    .gate-card-value {{ color: #475569; font-weight: 700; line-height: 1.5; }}
    .score-summary {{
      display: grid;
      grid-template-columns: 1fr 1.2fr;
      gap: 14px;
    }}
    .score-summary-panel {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }}
    .score-summary-head {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: baseline;
      margin-bottom: 12px;
      font-weight: 800;
    }}
    .reason-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }}
    .reason-card {{
      display: grid;
      grid-template-columns: 54px 1fr;
      gap: 12px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 16px;
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
    .reason-text {{ font-size: 16px; font-weight: 800; line-height: 1.55; }}
    .reason-list {{ margin: 10px 0 0; padding-left: 22px; }}
    .price-map-wrap {{
      padding: 14px 0 6px;
      background: linear-gradient(180deg, #121a2c 0%, #0e1422 100%);
      border-radius: 18px;
      border: 1px solid #263148;
      overflow: hidden;
    }}
    .price-map-wrap h3, .price-map-wrap p {{ margin-left: 18px; margin-right: 18px; }}
    .price-map-wrap h3 {{
      margin-top: 0;
      color: #eff6ff;
      font-size: 18px;
      font-weight: 800;
    }}
    .price-map-wrap p {{
      color: #b9c7dc;
      font-size: 13px;
      line-height: 1.6;
      margin-bottom: 14px;
    }}
    .price-map {{
      width: 100%;
      height: auto;
      display: block;
      border-top: 1px solid rgba(148, 163, 184, 0.12);
      border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }}
    .price-map-bg {{ fill: #0f1728; stroke: #263148; stroke-width: 1.2; }}
    .price-map-panel {{ filter: drop-shadow(0 12px 22px rgba(2, 6, 23, 0.16)); }}
    .price-map-panel-focus .price-map-bg {{ stroke: #456489; stroke-width: 1.4; }}
    .chart-title {{ fill: #eff6ff; font-size: 18px; font-weight: 700; }}
    .chart-subtitle {{ fill: #93a4bf; font-size: 12px; font-weight: 500; }}
    .price-grid-h {{ stroke: rgba(148, 163, 184, 0.32); stroke-width: 1.1; }}
    .price-grid-v {{ stroke: rgba(148, 163, 184, 0.22); stroke-width: 1; }}
    .price-map-separator {{ fill: rgba(207, 216, 228, 0.06); }}
    .price-map-separator-line {{ stroke: rgba(148, 163, 184, 0.22); stroke-width: 1; }}
    .candle-wick {{ stroke-width: 1.35; opacity: 0.92; }}
    .candle-body {{ stroke-width: 0.95; opacity: 0.96; }}
    .candle-up {{ fill: rgba(74, 222, 128, 0.62); stroke: rgba(74, 222, 128, 0.95); }}
    .candle-down {{ fill: rgba(248, 113, 113, 0.58); stroke: rgba(248, 113, 113, 0.94); }}
    .band-support {{ fill: rgba(34, 197, 94, 0.14); }}
    .band-resistance {{ fill: rgba(248, 113, 113, 0.14); }}
    .setup-band-long {{ fill: rgba(34, 197, 94, 0.24); stroke: rgba(74, 222, 128, 0.98); stroke-width: 1.6; }}
    .setup-band-short {{ fill: rgba(248, 113, 113, 0.24); stroke: rgba(248, 113, 113, 0.98); stroke-width: 1.6; }}
    .setup-band-text-long {{ fill: #dcfce7; font-size: 12px; font-weight: 800; }}
    .setup-band-text-short {{ fill: #fee2e2; font-size: 12px; font-weight: 800; }}
    .setup-axis-value-long {{ fill: #4ade80; font-size: 13px; font-weight: 700; }}
    .setup-axis-value-short {{ fill: #f87171; font-size: 13px; font-weight: 700; }}
    .value-defense-dashboard {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 12px; }}
    .value-defense-chart-card {{ border: 1px solid rgba(71, 85, 105, 0.66); border-radius: 16px; padding: 12px 14px 14px; background: linear-gradient(180deg, rgba(10, 16, 28, 0.96) 0%, rgba(12, 20, 34, 0.96) 100%); }}
    .value-defense-chart-card.long {{ border-color: rgba(34, 197, 94, 0.42); }}
    .value-defense-chart-card.short {{ border-color: rgba(248, 113, 113, 0.4); }}
    .value-defense-card-head {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 8px; color: #eff6ff; font-size: 13px; font-weight: 800; }}
    .value-defense-group-label {{ margin-top: 10px; margin-bottom: 6px; font-size: 10px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; }}
    .value-defense-group-label.primary {{ color: #eef6ff; }}
    .value-defense-group-label.secondary {{ color: #94a3b8; }}
    .value-defense-card-row {{ display: grid; grid-template-columns: 92px 1fr; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid rgba(71, 85, 105, 0.28); }}
    .value-defense-card-row:first-of-type {{ border-top: 0; padding-top: 0; }}
    .value-defense-card-row.secondary {{ border-top-color: rgba(71, 85, 105, 0.18); padding-top: 5px; padding-bottom: 5px; }}
    .value-defense-card-main {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
    .value-defense-card-key {{ display: inline-flex; align-items: center; gap: 8px; color: #9fb0c8; font-size: 11px; font-weight: 700; }}
    .value-defense-card-desc {{ color: #8fa2bf; font-size: 10px; line-height: 1.35; }}
    .value-defense-row-chip {{ width: 10px; height: 10px; border-radius: 999px; flex: 0 0 auto; border: 1px solid rgba(255, 255, 255, 0.2); }}
    .value-defense-row-chip.long.shallow {{ background: rgba(34, 197, 94, 0.98); }}
    .value-defense-row-chip.short.shallow {{ background: rgba(248, 113, 113, 0.98); }}
    .value-defense-row-chip.long.defense {{ background: rgba(103, 232, 249, 0.98); }}
    .value-defense-row-chip.short.defense {{ background: rgba(253, 186, 116, 0.98); }}
    .value-defense-row-chip.long.invalidation {{ background: rgba(252, 165, 165, 0.78); }}
    .value-defense-row-chip.short.invalidation {{ background: rgba(147, 197, 253, 0.78); }}
    .value-defense-row-chip.long.reclaim, .value-defense-row-chip.long.continuation {{ background: rgba(186, 230, 253, 0.82); }}
    .value-defense-row-chip.short.reclaim, .value-defense-row-chip.short.continuation {{ background: rgba(253, 230, 138, 0.82); }}
    .value-defense-chart-card.long .value-defense-card-key {{ color: #86efac; }}
    .value-defense-chart-card.short .value-defense-card-key {{ color: #fca5a5; }}
    .value-defense-card-value {{ color: #eef6ff; font-size: 16px; font-weight: 900; letter-spacing: 0.01em; text-align: right; }}
    .value-defense-card-value.secondary {{ font-size: 12px; font-weight: 700; color: #94a3b8; }}
    .value-defense-chart-card.long .value-defense-card-value {{ color: #bbf7d0; }}
    .value-defense-chart-card.short .value-defense-card-value {{ color: #fecaca; }}
    .marker-line {{ stroke-width: 2; stroke-dasharray: 4 4; }}
    .marker-label {{ font-size: 10px; font-weight: 500; }}
    .marker-long {{ stroke: #4ade80; fill: #bbf7d0; }}
    .marker-short {{ stroke: #f87171; fill: #fecaca; }}
    .current-price-line {{ stroke: #60a5fa; stroke-width: 2.5; stroke-dasharray: 5 5; }}
    .current-price-label {{ fill: #dbeafe; font-size: 13px; font-weight: 700; paint-order: stroke fill; stroke: rgba(15, 23, 42, 0.9); stroke-width: 3; }}
    .price-axis {{ fill: #9db0ca; font-size: 12px; font-weight: 500; }}
    .time-axis-line {{ stroke: rgba(148, 163, 184, 0.3); stroke-width: 1; }}
    .time-axis-label {{ fill: #8fa2bf; font-size: 11px; font-weight: 600; }}
    .diagnostic-details {{ border: 1px solid #d8dfe6; border-radius: 18px; background: #fff; overflow: hidden; }}
    .diagnostic-details + .diagnostic-details {{ margin-top: 10px; }}
    .diagnostic-details summary {{ cursor: pointer; padding: 14px 16px; font-weight: 950; background: #f8fafc; }}
    .diagnostic-details-body {{ padding: 16px; border-top: 1px solid #e2e8f0; }}
    .detail-stack {{ display: grid; gap: 12px; }}
    .detail-muted {{ color: var(--muted); font-size: 14px; }}
    .big-chance-note {{ border-left: 5px solid var(--accent); padding-left: 12px; margin-top: 10px; }}
    @media (max-width: 920px) {{
      .status-strip, .score-summary {{ grid-template-columns: 1fr; }}
      .wrap {{ padding: 16px 12px 42px; }}
      .hero, .section {{ border-radius: 18px; }}
      .read-nav nav {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .value-defense-dashboard {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 640px) {{
      .read-nav nav {{ grid-template-columns: 1fr; }}
      .hero-summary {{ font-size: 22px; }}
      .takeaway {{ font-size: 18px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    {read_nav_html}
    <section class="hero" id="decision">
      <p class="muted">{esc(timestamp_jst)} / signal_id {esc(result.get('signal_id', ''))}</p>
      <div class="hero-kicker">{esc(notification_context.get('final_rank_emoji', ''))} {esc(notification_context.get('final_rank_label', '送信なし'))} / {esc(notification_context.get('status_label', '中立'))}</div>
      <p class="hero-sub">行動種別: {esc(action_kind_label)}</p>
      <p class="hero-sub"><strong>Active Plan:</strong> {esc(active_hero_label)}</p>
      <h1>{esc(public_title)}</h1>
      <p class="hero-summary">{esc(active_hero_label)}</p>
      <p class="hero-sub">{esc(active_hero_summary)}</p>
      <div>{chips_html(summary_chips)}</div>
      {_status_strip_html(result, notification_context)}
      <div class="takeaway">まず方向ではなく、実際に取れる行動を確認します。今回は <strong>{esc(active_hero_label)}</strong> です。</div>
    </section>

    {followup_section_html}

    {_price_plan_table_html(result)}

    {_manual_gate_cards_html(active_status_rows)}

    <section class="section" id="chart">
      <h2>4h → 1h → 15m チャート</h2>
      <p class="muted">4時間足は大局方向、1時間足は帯の妥当性、15分足は実際の価格・SL・TP を見る主役です。</p>
      <div class="price-map-wrap">
        <h3>4時間足 → 1時間足 → 15分足 の順で見ます</h3>
        <p>上段は大きな流れ、中段は再検討帯の妥当性、下段は実際に入る価格と SL / TP の精度を見る段です。いちばん重要なのは下段の 15 分足です。</p>
        {price_map_svg}
        {value_defense_chart_dashboard_html}
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

    {value_defense_entry_layer_section_html}

    {big_chance_section_html}

    {_score_summary_section_html(balance_svg, metric_blocks)}

    {_reasons_section_html(reason_cards_html, wait_reason_html)}

    <section class="section" id="details">
      <h2>内部詳細</h2>
      <p class="detail-muted">内部・検証用の情報は折りたたみ、上からの読み順を邪魔しないように退避しています。</p>
      <div class="detail-stack">
        {_details_panel_html("Safe Config Schema Audit", safe_config_schema_audit_html)}
        {_details_panel_html("Operator Triage Summary", operator_triage_summary_html)}
        {_details_panel_html("Integrated Evidence Overview", integrated_evidence_overview_html)}
        {_details_panel_html("Evidence quality summary", evidence_quality_summary_html)}
        {_details_panel_html("OHLCV source coverage summary", ohlcv_source_coverage_summary_html)}
        {_details_panel_html("Post-Eval Recommendation Status", post_eval_recommendation_status_html)}
        {_details_panel_html("Runtime startup status", runtime_startup_status_html)}
        {_details_panel_html(CURRENT_MANUAL_SUPPORT_HEADER, f'<ul>{manual_support_reference_list_html}</ul>')}
        {_details_panel_html("Raw mail text", f'<div class="mail-block">{esc(raw_mail)}</div>')}
        {_details_panel_html("Major turning point diagnostic rows", major_turning_point_diagnostic_html)}
        {_details_panel_html("Legacy compatibility memo", legacy_compatibility_html)}
        {_details_panel_html(
            "上抜け・下抜けの見落とし確認",
            '<p class="detail-muted">上抜け追随候補 / ショート根拠は弱まりつつあります / 15分足で上に維持できるか確認 / すぐ下に戻るならダマシ注意 / 下抜け追随候補 / ロング根拠は弱まりつつあります / 15分足で下に維持できるか確認 / human decides manually</p>',
        )}
        {_details_panel_html(
            "15分足 早期注意",
            '<p class="detail-muted">上抜け初動の可能性 / ショート方向は損失リスク / 下抜け初動の可能性 / ロング方向は損失リスク / MACD / report-only / human decides manually</p>',
        )}
        {_details_panel_html(
            "勢い確認",
            '<p class="detail-muted">上抜け後の勢い確認 / ショート方向は危険 / 下抜け後の勢い確認 / ロング方向は危険 / report-only / human decides manually</p>',
        )}
        {_details_panel_html("主要ファクト", f'<div class="fact-grid">{root_cards_html}</div>')}
        {_details_panel_html("AI監査メモ", f'<div class="two-col"><div class="panel"><h3>{esc(ai_audit_headline)}</h3><p>{esc(audit_reason or "監査理由はありません")}</p><h3>次の確認観点</h3><p>{esc(audit_next or "追加の確認観点はありません")}</p></div><div class="panel"><h3>追加リスク</h3><ul>{ai_audit_unique_risk_html or "<li>追加リスクはありません</li>"}</ul></div></div>', open=False) if show_ai_audit else ""}
      </div>
    </section>
  </div>
</body>
</html>
"""


def _big_chance_section_html(result: dict[str, Any]) -> str:
    candidate = result.get("big_chance_candidate")
    if not isinstance(candidate, dict) or not candidate.get("present"):
        return ""
    status = str(candidate.get("status", "")).strip().lower()

    macro_context = candidate.get("macro_context") if isinstance(candidate.get("macro_context"), dict) else {}
    failed_thesis = candidate.get("failed_thesis") if isinstance(candidate.get("failed_thesis"), dict) else {}
    activation = candidate.get("activation") if isinstance(candidate.get("activation"), dict) else {}
    invalidation = candidate.get("invalidation") if isinstance(candidate.get("invalidation"), dict) else {}
    evidence = candidate.get("evidence") if isinstance(candidate.get("evidence"), dict) else {}
    reason_labels = candidate.get("reason_labels") if isinstance(candidate.get("reason_labels"), list) else []
    if status == "invalidated":
        header = "大転換候補 / Big Chance / Failed Thesis"
        intro = "候補失効 / 再評価済み。これはエントリー指示ではありません。Big Chance is not an entry instruction."
    else:
        header = "大転換候補 / Big Chance / Failed Thesis"
        intro = "失敗シナリオの反対側を補助確認します。これはエントリー指示ではありません。Big Chance is not an entry instruction."

    safety_boundary = _normalize_detail_page_safety_boundary(candidate.get("safety_boundary", STABLE_DETAIL_PAGE_SAFETY_BOUNDARY))
    reason_chips = _v2_reason_chips_html(reason_labels)
    reason_summary = " / ".join(reason_labels[:3]) or "未記録"
    step_cards = "".join(
        f"""
        <div class="v2-step">
          <div class="v2-step-title">{html.escape(label)}</div>
          <div class="v2-step-body">{html.escape(text)}</div>
        </div>
        """
        for label, text in (
            ("4時間足", str(macro_context.get("signals_4h") or "未記録")),
            ("1時間足", str(macro_context.get("signals_1h") or "未記録")),
            ("15分足", str(macro_context.get("signals_15m") or "未記録")),
        )
    )

    return f"""
    <section class="v2-section v2-section-anchor" id="big-chance">
      <h2>{html.escape(header)}</h2>
      <p class="v2-muted">{html.escape(intro)}</p>
      <div class="v2-grid-2">
        <div class="v2-card emphasis">
          <div class="v2-kicker">Score / Grade</div>
          <div class="v2-big">{html.escape(str(candidate.get('score', 0)))} / {html.escape(str(candidate.get('grade', 'none')))}</div>
          <p>これはエントリー指示ではありません</p>
        </div>
        <div class="v2-card">
          <div class="v2-kicker">Safety boundary</div>
          <p>{html.escape(safety_boundary)}</p>
        </div>
      </div>
      <div class="v2-grid-2" style="margin-top:14px;">
        <div class="v2-card">
          <div class="v2-kicker">Headline</div>
          <h3>{html.escape(str(candidate.get('headline', '未記録')))}</h3>
          <p>{html.escape(str(candidate.get('operator_summary', '未記録')))}</p>
        </div>
        <div class="v2-card {('warn' if status == 'invalidated' else 'good')}">
          <div class="v2-kicker">Side / Type / Status</div>
          <p>{html.escape(str(candidate.get('side', 'none')))} / {html.escape(str(candidate.get('type', 'none')))} / {html.escape(str(candidate.get('status', 'none')))}</p>
          <p>{html.escape(str(candidate.get('headline', '未記録')))}</p>
        </div>
      </div>
      <div class="v2-callout">
        <div class="v2-callout-icon">①</div>
        <div><strong>見る順番</strong><br>HTF で trap / fuel を確認し、1時間足で再評価、15分足で activation / invalidation を読む。</div>
      </div>
      <div class="v2-card" style="margin-top:14px;">
        <div class="v2-kicker">見る順番</div>
        <div class="v2-step-list">{step_cards}</div>
      </div>
      <div class="v2-grid-2" style="margin-top:14px;">
        <div class="v2-card">
          <div class="v2-kicker">Activation condition</div>
          <p>{html.escape(str(activation.get('activation_condition') or activation.get('activation_trigger') or '未記録'))}</p>
          <p class="v2-muted">時間軸: {html.escape(str(activation.get('activation_tf', '未記録')))} / 状態: {html.escape(str(activation.get('activation_state', '未記録')))} / 価格位置: {html.escape(str(activation.get('price_position', '未記録')))}</p>
        </div>
        <div class="v2-card">
          <div class="v2-kicker">Invalidation condition</div>
          <p>{html.escape(str(invalidation.get('invalidation_condition') or invalidation.get('invalidation_trigger') or '未記録'))}</p>
          <p class="v2-muted">時間軸: {html.escape(str(invalidation.get('invalidation_tf', '未記録')))} / 状態: {html.escape(str(invalidation.get('invalidation_state', '未記録')))} / 価格位置: {html.escape(str(invalidation.get('price_position', '未記録')))}</p>
        </div>
      </div>
      <div class="v2-card" style="margin-top:14px;">
        <div class="v2-kicker">Weakening / risk note</div>
        <p>{html.escape(str(failed_thesis.get('thesis_summary') or failed_thesis.get('weakening_note') or failed_thesis.get('risk_note') or '未記録'))}</p>
        <div class="v2-reasons">{reason_chips}</div>
        <p class="v2-muted">Evidence: 現値 {html.escape(str(evidence.get('current_price', '未記録')))} / long_pos {html.escape(str(evidence.get('current_price_position_long', '未記録')))} / short_pos {html.escape(str(evidence.get('current_price_position_short', '未記録')))}</p>
        <p class="v2-muted">{html.escape(reason_summary)}</p>
      </div>
    </section>
    """


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


def _operator_dashboard_v2_css() -> str:
    return """    :root {
      color-scheme: dark;
      --bg: #071019;
      --surface: #0b1622;
      --surface-2: #0e1c2b;
      --surface-3: #122337;
      --line: #213449;
      --line-soft: rgba(148, 163, 184, .16);
      --text: #edf4fb;
      --muted: #90a4b8;
      --faint: #61758a;
      --wait: #f3b44f;
      --wait-soft: rgba(243, 180, 79, .12);
      --long: #42d392;
      --long-soft: rgba(66, 211, 146, .11);
      --long-main: #58d6ea;
      --short: #ff6f78;
      --short-soft: rgba(255, 111, 120, .10);
      --short-main: #f6b75e;
      --blue: #67a9ff;
      --danger: #ff6f78;
      --radius: 18px;
      --shadow: 0 24px 70px rgba(0,0,0,.28);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      min-width: 320px;
      background:
        radial-gradient(circle at 8% -10%, rgba(42, 117, 176, .22), transparent 30%),
        radial-gradient(circle at 92% 0%, rgba(44, 155, 125, .10), transparent 28%),
        var(--bg);
      color: var(--text);
      font-family: "Hiragino Sans", "Yu Gothic", "Yu Gothic UI", system-ui, -apple-system, sans-serif;
      line-height: 1.55;
    }
    button { font: inherit; }
    .shell { width: min(1460px, calc(100% - 28px)); margin: 0 auto; padding: 18px 0 56px; }
    .topbar {
      display:flex; align-items:center; justify-content:space-between; gap:16px;
      margin-bottom:12px; color:var(--muted); font-size:12px; font-weight:800;
    }
    .brand { display:flex; align-items:center; gap:10px; color:var(--text); letter-spacing:.08em; }
    .brand-mark { display:grid; place-items:center; width:30px; height:30px; border-radius:9px; background:#f59e0b; color:#111827; font-size:18px; }
    .meta-line { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:8px 16px; }
    .hero {
      display:grid; grid-template-columns:minmax(0,1.5fr) minmax(310px,.5fr);
      border:1px solid var(--line); border-radius:24px; overflow:hidden;
      background:linear-gradient(145deg, rgba(15,31,48,.98), rgba(9,20,31,.98));
      box-shadow:var(--shadow);
    }
    .hero-main { padding:26px 28px 24px; }
    .hero-side { padding:24px; background:rgba(5,13,21,.44); border-left:1px solid var(--line); }
    .status-line { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:18px; }
    .status-badge {
      display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border:1px solid rgba(243,180,79,.45);
      border-radius:999px; background:var(--wait-soft); color:#ffd68f; font-size:12px; font-weight:950; letter-spacing:.06em;
    }
    .safety { color:var(--faint); font-size:11px; font-weight:800; }
    .decision-grid { display:grid; grid-template-columns:auto minmax(0,1fr); gap:20px; align-items:center; }
    .decision-word { color:var(--wait); font-size:clamp(52px,8vw,104px); line-height:.9; font-weight:1000; letter-spacing:-.065em; }
    .decision-copy h1 { margin:0 0 8px; font-size:clamp(25px,3.2vw,43px); line-height:1.15; letter-spacing:-.035em; }
    .decision-copy p { margin:0; max-width:760px; color:#b8c8d7; font-size:15px; font-weight:700; }
    .hero-action {
      display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1px; margin-top:22px;
      border:1px solid var(--line); border-radius:14px; overflow:hidden; background:var(--line);
    }
    .action-cell { padding:12px 14px; background:#0a1723; min-width:0; }
    .action-cell span { display:block; color:var(--faint); font-size:10px; font-weight:900; letter-spacing:.08em; margin-bottom:4px; }
    .action-cell strong { display:block; font-size:14px; overflow-wrap:anywhere; }
    .current-label { color:var(--muted); font-size:11px; font-weight:900; letter-spacing:.12em; }
    .current-price { margin:6px 0 18px; font-size:clamp(39px,5vw,64px); line-height:1; font-weight:1000; letter-spacing:-.05em; font-variant-numeric:tabular-nums; }
    .metric-stack { display:grid; gap:11px; }
    .metric { display:grid; grid-template-columns:72px 1fr 42px; gap:10px; align-items:center; }
    .metric-label { color:var(--muted); font-size:12px; font-weight:900; }
    .metric-track { height:8px; border-radius:999px; background:#1a2a3b; overflow:hidden; }
    .metric-fill { height:100%; border-radius:inherit; }
    .metric-fill.direction { background:var(--blue); }
    .metric-fill.execution { background:var(--long); }
    .metric-fill.wait { background:var(--wait); }
    .metric-value { text-align:right; font-size:18px; font-weight:1000; font-variant-numeric:tabular-nums; }
    .expiry { margin-top:18px; padding-top:14px; border-top:1px solid var(--line); color:var(--muted); font-size:12px; }
    .alert-strip {
      display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:12px 0;
    }
    .alert-item {
      display:grid; grid-template-columns:28px 1fr; gap:9px; align-items:start; padding:12px 13px;
      border:1px solid var(--line); border-radius:14px; background:rgba(12,27,42,.9);
    }
    .alert-icon { display:grid; place-items:center; width:28px; height:28px; border-radius:9px; background:var(--wait-soft); color:var(--wait); font-weight:1000; }
    .alert-item strong { display:block; font-size:12px; margin-bottom:2px; }
    .alert-item small { display:block; color:var(--muted); font-size:10px; line-height:1.45; }
    .workspace {
      display:grid;
      grid-template-columns:280px minmax(0,1fr) 280px;
      grid-template-areas:"long chart short";
      gap:12px;
      align-items:start;
    }
    .panel { border:1px solid var(--line); border-radius:var(--radius); background:rgba(11,22,34,.96); box-shadow:0 14px 40px rgba(0,0,0,.15); }
    .chart-panel { grid-area:chart; min-width:0; overflow:hidden; }
    .plans { display:contents; }
    .side-card.long { grid-area:long; }
    .side-card.short { grid-area:short; }
    .panel-head { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; padding:18px 18px 12px; }
    .panel-head h2 { margin:0; font-size:18px; letter-spacing:-.02em; }
    .panel-head p { margin:4px 0 0; color:var(--muted); font-size:12px; }
    .chart-controls { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:8px; }
    .segmented { display:inline-flex; padding:3px; border:1px solid var(--line); border-radius:11px; background:#07121d; }
    .segmented button {
      border:0; padding:7px 10px; border-radius:8px; background:transparent; color:var(--muted);
      cursor:pointer; font-size:11px; font-weight:900;
    }
    .segmented button.active { background:var(--surface-3); color:var(--text); box-shadow:0 1px 0 rgba(255,255,255,.05) inset; }
    .chart-legend {
      display:flex; flex-wrap:wrap; gap:8px 14px; padding:0 18px 12px; color:var(--muted); font-size:10px; font-weight:800;
    }
    .legend-item { display:inline-flex; align-items:center; gap:6px; }
    .legend-dot { width:11px; height:7px; border-radius:3px; border:1px solid transparent; }
    .legend-dot.long-shallow { background:rgba(66,211,146,.42); border-color:var(--long); }
    .legend-dot.long-main { background:rgba(88,214,234,.25); border-color:var(--long-main); }
    .legend-dot.short-shallow { background:rgba(255,111,120,.42); border-color:var(--short); }
    .legend-dot.short-main { background:rgba(246,183,94,.25); border-color:var(--short-main); }
    .chart-scroll { overflow-x:auto; padding:0 12px 12px; scrollbar-color:#30475f transparent; }
    .chart-stage { min-width:790px; border:1px solid #24364b; border-radius:14px; overflow:hidden; background:#07111d; }
    .price-map,
    .chart-svg { display:block; width:100%; height:auto; }
    .chart-note {
      display:flex; justify-content:space-between; gap:14px; padding:11px 15px; border-top:1px solid #1e3044;
      color:var(--muted); font-size:10px;
    }
    .side-card { overflow:hidden; }
    .side-head { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; padding:13px 13px; border-bottom:1px solid var(--line); }
    .side-card.long .side-head { background:linear-gradient(100deg,var(--long-soft),transparent); }
    .side-card.short .side-head { background:linear-gradient(100deg,var(--short-soft),transparent); }
    .side-title { display:flex; align-items:center; gap:9px; }
    .side-pill { padding:5px 8px; border-radius:7px; font-size:11px; font-weight:1000; letter-spacing:.08em; }
    .long .side-pill { background:rgba(66,211,146,.16); color:#91f2bf; }
    .short .side-pill { background:rgba(255,111,120,.15); color:#ffadb2; }
    .side-state { font-size:15px; font-weight:1000; }
    .side-score { text-align:right; }
    .side-score strong { display:block; font-size:24px; line-height:1; }
    .side-score small { color:var(--faint); font-size:9px; }
    .levels { padding:5px 11px 8px; }
    .level-group-label { padding:7px 2px 3px; color:var(--faint); font-size:8px; font-weight:1000; letter-spacing:.12em; }
    .level-row {
      display:grid; grid-template-columns:minmax(0,1fr) auto; gap:12px; align-items:center;
      min-height:34px; padding:5px 2px; border-top:1px solid var(--line-soft);
    }
    .level-name { color:#c1d0df; font-size:10px; font-weight:900; }
    .level-name small { display:block; margin-top:2px; color:var(--faint); font-size:8px; font-weight:700; }
    .level-value { font-size:13px; font-weight:1000; font-variant-numeric:tabular-nums; white-space:nowrap; }
    .level-row.shallow.long-tone .level-value { color:#84edb8; }
    .level-row.main.long-tone .level-value { color:#80e5f2; }
    .level-row.shallow.short-tone .level-value { color:#ff9da4; }
    .level-row.main.short-tone .level-value { color:#ffd08d; }
    .level-row.invalid .level-value { color:#ff9aa2; }
    .level-row.trigger .level-value { color:#bdd2e6; }
    .level-row.target .level-value { color:#d5e3ef; }
    .side-guidance { margin:0 11px 11px; padding:9px 10px; border-radius:10px; background:#07131e; color:var(--muted); font-size:9px; line-height:1.5; }
    .lower-grid { display:grid; grid-template-columns:1.1fr .9fr; gap:12px; margin-top:12px; }
    .section-card { padding:18px; }
    .section-title { margin:0 0 4px; font-size:18px; }
    .section-lead { margin:0 0 15px; color:var(--muted); font-size:12px; }
    .condition-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px; }
    .condition { padding:13px; border:1px solid var(--line); border-radius:13px; background:#091724; }
    .condition-label { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:6px; color:var(--muted); font-size:10px; font-weight:900; }
    .condition-label b { padding:3px 6px; border-radius:6px; background:#15273a; color:var(--text); }
    .condition strong { display:block; font-size:13px; margin-bottom:4px; }
    .condition p { margin:0; color:var(--muted); font-size:10px; }
    .big-chance {
      display:grid; grid-template-columns:82px 1fr; gap:15px; padding:18px;
      border:1px solid rgba(103,169,255,.28); border-radius:var(--radius);
      background:linear-gradient(145deg,rgba(17,43,69,.9),rgba(9,23,36,.97));
    }
    .big-score { display:grid; place-items:center; align-content:center; min-height:90px; border-radius:14px; background:#081624; border:1px solid #294562; }
    .big-score strong { font-size:32px; line-height:1; }
    .big-score span { color:var(--blue); font-size:12px; font-weight:1000; }
    .big-chance h3 { margin:0 0 6px; font-size:16px; }
    .big-chance p { margin:0; color:#b1c4d6; font-size:11px; }
    .timeline { display:flex; align-items:center; flex-wrap:wrap; gap:6px; margin-top:12px; }
    .timeline span { padding:5px 8px; border-radius:8px; background:#0c1c2b; border:1px solid #27405a; font-size:9px; font-weight:900; }
    .timeline i { color:var(--faint); font-style:normal; }
    .context-bar {
      display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1px; margin-top:12px;
      border:1px solid var(--line); border-radius:14px; overflow:hidden; background:var(--line);
    }
    .context-cell { padding:13px; background:#0a1723; }
    .context-cell span { display:block; color:var(--faint); font-size:9px; font-weight:900; letter-spacing:.08em; }
    .context-cell strong { display:block; margin-top:3px; font-size:13px; }
    .details-panel { margin-top:12px; overflow:hidden; }
    details { border-top:1px solid var(--line); }
    details:first-of-type { border-top:0; }
    summary { cursor:pointer; list-style:none; padding:14px 18px; font-size:12px; font-weight:900; }
    summary::-webkit-details-marker { display:none; }
    summary::after { content:"＋"; float:right; color:var(--faint); }
    details[open] summary::after { content:"−"; }
    .details-body { padding:0 18px 18px; color:var(--muted); font-size:11px; overflow-wrap:anywhere; word-break:break-word; }
    .details-body pre { white-space:pre-wrap; max-width:100%; overflow-x:auto; }
    .details-body p, .details-body li { overflow-wrap:anywhere; word-break:break-word; }
    .score-mini-grid { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:8px; }
    .score-mini { padding:10px; border:1px solid var(--line); border-radius:10px; background:#081521; }
    .score-mini span { display:block; color:var(--faint); font-size:8px; }
    .score-mini strong { display:block; font-size:20px; }
    .reason-list { display:flex; flex-wrap:wrap; gap:7px; margin-top:12px; }
    .reason-chip { padding:6px 8px; border:1px solid #2a4055; border-radius:999px; background:#0b1927; color:#aebfd0; font-size:9px; }
    .diagnostic-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin-top:12px; }
    .diagnostic { padding:11px; border:1px solid var(--line); border-radius:11px; background:#081521; }
    .diagnostic span { display:block; color:var(--faint); font-size:8px; }
    .diagnostic strong { display:block; margin-top:3px; font-size:11px; color:#c7d6e4; }
    .shadow-panel { margin-top:12px; padding:16px; border:1px solid #355a78; border-radius:16px; background:linear-gradient(135deg,#0b1d2d,#0a1723); }
    .shadow-head { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }
    .shadow-badge { color:#8fd6ff; font-size:10px; font-weight:900; letter-spacing:.08em; }
    .shadow-head h2 { margin:5px 0 0; font-size:18px; }
    .shadow-safety { color:#b6c8d9; font-size:10px; text-align:right; }
    .shadow-legend { margin-top:10px; color:#8fa9bd; font-size:10px; font-weight:800; }
    .shadow-body { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; margin-top:12px; }
    .shadow-card { padding:11px; border:1px solid #29445d; border-radius:11px; background:#081521; }
    .shadow-card strong { color:#e7f1fb; font-size:12px; }
    .shadow-card p { margin:5px 0; color:#b9cada; font-size:11px; }
    .shadow-card small { color:#8ea5ba; overflow-wrap:anywhere; }
    footer { padding:20px 4px 0; color:var(--faint); font-size:9px; text-align:center; }

    /* SVG chart */
    .price-map-bg { fill:#0a1422; stroke:#26384c; stroke-width:1.2; }
    .price-map-panel { filter:drop-shadow(0 10px 22px rgba(0,0,0,.18)); }
    .price-map-panel-focus .price-map-bg { stroke:#3d5d7f; stroke-width:1.4; }
    .chart-title { fill:#eef6ff; font-size:18px; font-weight:800; }
    .chart-subtitle { fill:#8ca0b6; font-size:12px; font-weight:600; }
    .price-grid-h { stroke:rgba(148,163,184,.26); stroke-width:1; }
    .price-grid-v { stroke:rgba(148,163,184,.16); stroke-width:1; }
    .price-map-separator { fill:rgba(207,216,228,.04); }
    .price-map-separator-line { stroke:rgba(148,163,184,.18); }
    .candle-wick { stroke-width:1.35; opacity:.9; }
    .candle-body { stroke-width:.95; opacity:.96; }
    .candle-up { fill:rgba(66,211,146,.58); stroke:rgba(66,211,146,.95); }
    .candle-down { fill:rgba(255,111,120,.56); stroke:rgba(255,111,120,.94); }
    .band-support { fill:rgba(66,211,146,.09); }
    .band-resistance { fill:rgba(255,111,120,.09); }
    .setup-band-long { fill:rgba(66,211,146,.22); stroke:var(--long); stroke-width:1.7; }
    .setup-band-short { fill:rgba(255,111,120,.22); stroke:var(--short); stroke-width:1.7; }
    .setup-axis-value-long { fill:#70e8ad; font-size:13px; font-weight:800; }
    .setup-axis-value-short { fill:#ff979e; font-size:13px; font-weight:800; }
    .value-defense-band-long { fill:rgba(88,214,234,.18); stroke:var(--long-main); stroke-width:2; }
    .value-defense-band-short { fill:rgba(246,183,94,.18); stroke:var(--short-main); stroke-width:2; }
    .invalidation-band-long, .invalidation-band-short { fill:rgba(255,111,120,.11); stroke:rgba(255,111,120,.75); stroke-width:1.3; stroke-dasharray:4 4; }
    .value-defense-trigger-long { stroke:#a9dff0; stroke-width:1.5; stroke-dasharray:5 4; }
    .value-defense-trigger-short { stroke:#f6d49e; stroke-width:1.5; stroke-dasharray:5 4; }
    .marker-line { stroke-width:2; stroke-dasharray:4 4; }
    .marker-label { font-size:10px; font-weight:700; }
    .marker-long { stroke:#55d99a; fill:#b9f7d4; }
    .marker-short { stroke:#ff777f; fill:#ffc1c5; }
    .current-price-line { stroke:#67a9ff; stroke-width:2.5; stroke-dasharray:5 5; }
    .current-price-label { fill:#dcecff; font-size:13px; font-weight:800; paint-order:stroke fill; stroke:#0a1422; stroke-width:3; }
    .price-axis { fill:#9dafc3; font-size:12px; font-weight:600; }
    .time-axis-line { stroke:rgba(148,163,184,.25); }
    .time-axis-label { fill:#879bb1; font-size:11px; font-weight:600; }
    .zone-caption { font-size:10px; font-weight:1000; letter-spacing:.02em; paint-order:stroke fill; stroke:#07111d; stroke-width:3; }
    .zone-long-shallow { fill:#a6f3cb; }
    .zone-long-main { fill:#98ebf4; }
    .zone-short-shallow { fill:#ffc1c5; }
    .zone-short-main { fill:#ffda9f; }
    .chart-stage.basic .marker-line,
    .chart-stage.basic .marker-label,
    .chart-stage.basic .invalidation-band-long,
    .chart-stage.basic .invalidation-band-short,
    .chart-stage.basic .invalidation-band-text-long,
    .chart-stage.basic .invalidation-band-text-short,
    .chart-stage.basic .value-defense-trigger-long,
    .chart-stage.basic .value-defense-trigger-short {
      opacity:0;
    }

    @media (max-width:1180px) {
      .workspace {
        grid-template-columns:1fr 1fr;
        grid-template-areas:"chart chart" "long short";
      }
      .alert-strip { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .hero-action { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .shadow-body { grid-template-columns:1fr; }
    }
    @media (max-width:860px) {
      .shell { width:min(100% - 18px, 760px); padding-top:10px; }
      .topbar { align-items:flex-start; }
      .meta-line { display:none; }
      .hero { grid-template-columns:1fr; }
      .hero-side { border-left:0; border-top:1px solid var(--line); }
      .decision-grid { grid-template-columns:1fr; gap:10px; }
      .decision-word { font-size:66px; }
      .workspace {
        grid-template-columns:1fr;
        grid-template-areas:"long" "short" "chart";
      }
      .lower-grid { grid-template-columns:1fr; }
      .score-mini-grid { grid-template-columns:repeat(3,minmax(0,1fr)); }
    }
    @media (max-width:590px) {
      .hero-main, .hero-side { padding:18px 16px; }
      .status-line { margin-bottom:12px; }
      .decision-copy h1 { font-size:25px; }
      .hero-action { grid-template-columns:1fr 1fr; }
      .action-cell { padding:10px; }
      .alert-strip { grid-template-columns:1fr; gap:7px; }
      .panel-head { display:block; }
      .chart-controls { justify-content:flex-start; margin-top:10px; }
      .chart-scroll { padding-left:8px; padding-right:8px; }
      .condition-grid { grid-template-columns:1fr; }
      .big-chance { grid-template-columns:68px 1fr; }
      .context-bar { grid-template-columns:1fr; }
      .score-mini-grid, .diagnostic-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .topbar { margin-left:4px; }
    }
  """


def _operator_dashboard_score(value: Any) -> int:
    return int(round(_clamp(_safe_float(value))))


def _operator_dashboard_zone(value: Any) -> str:
    if not isinstance(value, dict):
        return "—"
    return _format_operator_price_range(value.get("low"), value.get("high"))


def _operator_dashboard_action_summary(statuses: Any) -> str:
    values = statuses if isinstance(statuses, dict) else {}
    long_status = _humanize_visible_status_text(values.get("long", "")).strip() or "見送り"
    short_status = _humanize_visible_status_text(values.get("short", "")).strip() or "見送り"
    if long_status == short_status:
        return long_status
    return f"Long: {long_status} / Short: {short_status}"


def _operator_dashboard_v2_action_summary(context: dict[str, Any]) -> str:
    rows = (
        ("成行", context.get("active_market_entry_now")),
        ("指値・戻り待ち", context.get("active_limit_retest_entry")),
        ("ブレイク追随", context.get("active_breakout_follow_entry")),
        ("逆方向短期", context.get("active_countertrend_scalp_entry")),
    )
    return "".join(
        '<div class="action-cell">'
        f'<span>{html.escape(label)}</span>'
        f'<strong>{html.escape(_operator_dashboard_action_summary(statuses))}</strong>'
        "</div>"
        for label, statuses in rows
    )


def _operator_dashboard_v2_alerts(
    result: dict[str, Any],
    context: dict[str, Any],
    display: dict[str, Any],
) -> str:
    candidates: list[tuple[str, str, str]] = []

    def add(icon: str, title: str, detail: Any) -> None:
        text = _humanize_visible_status_text(detail).strip()
        if not text:
            return
        key = re.sub(r"\s+", "", text).lower()
        if any(re.sub(r"\s+", "", existing[2]).lower() == key for existing in candidates):
            return
        candidates.append((icon, title, text))

    for side, setup in (("Long", result.get("long_setup")), ("Short", result.get("short_setup"))):
        if not isinstance(setup, dict):
            continue
        reason = setup.get("execution_precision_reason")
        if reason:
            add("!", f"{side} 実行注意", reason)
    breakout = _breakout_inversion_items(result)
    if breakout:
        add("↗", "ブレイク / 反転", breakout[0][1])
    momentum = _momentum_confirmation_items(result)
    if momentum:
        add("勢", "モメンタム", momentum[0][1])
    reasons = context.get("reason_labels_full") or _build_wait_reasons(display, result)
    for reason in reasons:
        text = str(reason).strip()
        lowered = text.lower()
        if "liquidity" in lowered or "流動性" in text:
            title, icon = "流動性", "↓"
        elif "order" in lowered or "板" in text:
            title, icon = "オーダーブック", "板"
        elif "resistance" in lowered or "レジスタンス" in text:
            title, icon = "主要レジスタンス", "!"
        elif "support" in lowered or "サポート" in text:
            title, icon = "主要サポート", "!"
        else:
            title, icon = "待機理由", "!"
        add(icon, title, text)
        if len(candidates) >= 4:
            break
    if not candidates:
        return ""
    items = "".join(
        '<div class="alert-item">'
        f'<span class="alert-icon">{html.escape(icon)}</span>'
        f'<div><strong>{html.escape(title)}</strong><small>{html.escape(detail)}</small></div>'
        "</div>"
        for icon, title, detail in candidates[:4]
    )
    return f'<section class="alert-strip" id="active-alerts" aria-label="現在発火中の警戒">{items}</section>'


def _operator_dashboard_v2_plan_card(result: dict[str, Any], side: str) -> str:
    setup = result.get(f"{side}_setup") if isinstance(result.get(f"{side}_setup"), dict) else {}
    layer = setup.get("value_defense_entry_layer") if isinstance(setup.get("value_defense_entry_layer"), dict) else {}
    label = side.upper()
    shallow = layer.get("shallow_retest_zone") if layer else setup.get("entry_zone")
    rows = (
        ("ENTRY LAYERS", "浅い入り", "最初の反応帯。ここだけで決めない", _operator_dashboard_zone(shallow), f"shallow {side}-tone"),
        ("", "本命ゾーン", "深い押し戻りで価値を守る帯", _operator_dashboard_zone(layer.get("value_defense_zone")), f"main {side}-tone"),
        ("VALIDATION", "無効化", "割れて回収できなければ目線を弱める", _operator_dashboard_zone(layer.get("invalidation_zone")), "invalid"),
        ("", "回収条件", "深く刺した後に戻してほしい水準", _format_operator_price(layer.get("reclaim_trigger")), "trigger"),
        ("", "継続条件", "方向継続を確認する目安", _format_operator_price(layer.get("continuation_trigger")), "trigger"),
        ("RISK / TARGET", "SL", "", _format_operator_price(setup.get("stop_loss")), "target"),
        ("", "TP1", "", _format_operator_price(setup.get("tp1")), "target"),
        ("", "TP2", "", _format_operator_price(setup.get("tp2")), "target"),
    )
    rows_html = "".join(
        (f'<div class="level-group-label">{group}</div>' if group else "")
        + '<div class="level-row {tone}"><div class="level-name">{name}{hint}</div><div class="level-value">{value}</div></div>'.format(
            tone=html.escape(tone),
            name=html.escape(name),
            hint=f"<small>{html.escape(hint)}</small>" if hint else "",
            value=html.escape(value),
        )
        for group, name, hint, value, tone in rows
    )
    return f"""
    <section class="panel side-card {side}" aria-label="{label} trade plan">
      <div class="side-head">
        <div class="side-title"><span class="side-pill">{label}</span><span class="side-state">{html.escape(_setup_status_label(setup.get('status')))}</span></div>
        <div class="side-score"><strong>{_operator_dashboard_score(result.get(f'{side}_display_score'))}</strong><small>SCORE / 100</small></div>
      </div>
      <div class="levels">{rows_html}</div>
      <div class="side-guidance">{html.escape(_operator_dashboard_execution_guidance(result, side))}</div>
    </section>
    """


def _operator_dashboard_v2_conditions(result: dict[str, Any], reasons: list[str]) -> str:
    long_setup = result.get("long_setup") if isinstance(result.get("long_setup"), dict) else {}
    short_setup = result.get("short_setup") if isinstance(result.get("short_setup"), dict) else {}
    long_layer = long_setup.get("value_defense_entry_layer") if isinstance(long_setup.get("value_defense_entry_layer"), dict) else {}
    short_layer = short_setup.get("value_defense_entry_layer") if isinstance(short_setup.get("value_defense_entry_layer"), dict) else {}
    cards = (
        ("LONG", "起動", "回収・継続条件を確認", f"{_format_operator_price(long_layer.get('reclaim_trigger'))} 回収後、{_format_operator_price(long_layer.get('continuation_trigger'))} の維持を確認する。"),
        ("LONG", "弱化", "無効化帯を割り、回収できない", f"{_operator_dashboard_zone(long_layer.get('invalidation_zone'))} を明確に下回る場合は仮説を弱める。"),
        ("SHORT", "再評価", "本命ゾーンで上値拒否を確認", f"{_operator_dashboard_zone(short_layer.get('value_defense_zone'))} と既存ゲートを再確認する。"),
        ("COMMON", "見送り", "既存の待機条件が残る", reasons[0] if reasons else "価格帯と15分足の反応が確認できるまで待つ。"),
    )
    body = "".join(
        '<article class="condition">'
        f'<div class="condition-label"><span>{html.escape(side)}</span><b>{html.escape(state)}</b></div>'
        f'<strong>{html.escape(title)}</strong><p>{html.escape(detail)}</p></article>'
        for side, state, title, detail in cards
    )
    return f'<div class="panel section-card"><h2 class="section-title">判断が変わる条件</h2><p class="section-lead">説明ではなく、次に確認するイベントだけを残します。</p><div class="condition-grid">{body}</div></div>'


def _operator_dashboard_v2_big_chance(result: dict[str, Any]) -> str:
    candidate = result.get("big_chance_candidate")
    if not isinstance(candidate, dict) or not candidate.get("present"):
        return ""
    status = str(candidate.get("status") or "未記録")
    invalid = status.lower() in {"invalidated", "expired"}
    macro = candidate.get("macro_context") if isinstance(candidate.get("macro_context"), dict) else {}
    summary = str(candidate.get("operator_summary") or candidate.get("headline") or "未記録")
    warning = "候補失効 / 再評価済み。通常のLong / Short判断を上書きしません" if invalid else "通常のLong / Short判断を上書きしません"
    return f"""
    <section class="big-chance{' invalidated' if invalid else ''}" id="big-chance">
      <div class="big-score"><strong>{html.escape(str(candidate.get('score', '—')))}</strong><span>{html.escape(str(candidate.get('grade') or '—'))} / {html.escape(status.upper())}</span></div>
      <div><h3>{html.escape(str(candidate.get('headline') or 'Big Chance / Failed Thesis'))}</h3>
        <p>{html.escape(summary)} <strong>{html.escape(warning)}</strong></p>
        <div class="timeline"><span>4H {html.escape(str(macro.get('signals_4h', '—')))}</span><i>→</i><span>1H {html.escape(str(macro.get('signals_1h', '—')))}</span><i>→</i><span>15M {html.escape(str(macro.get('signals_15m', '—')))}</span></div>
      </div>
    </section>
    """


def _operator_dashboard_v2_context(result: dict[str, Any]) -> str:
    funding = result.get("funding_rate_display") or result.get("funding_rate_label") or "—"
    values = (("FUNDING", funding), ("ATR RATIO", result.get("atr_ratio")), ("VOLUME RATIO", result.get("volume_ratio")))
    return '<div class="context-bar">' + "".join(
        f'<div class="context-cell"><span>{label}</span><strong>{html.escape(str(value if value not in (None, "") else "—"))}</strong></div>'
        for label, value in values
    ) + "</div>"


def _operator_dashboard_v2_diagnostic_cells(result: dict[str, Any]) -> str:
    cells: list[tuple[str, str]] = []
    breakout = _breakout_inversion_items(result) + _intraperiod_breakout_items(result)
    if breakout:
        cells.append(("BREAKOUT / INVERSION", " / ".join(value for _, value in breakout)))
    layers = []
    for side in ("long", "short"):
        setup = result.get(f"{side}_setup") if isinstance(result.get(f"{side}_setup"), dict) else {}
        layer = setup.get("value_defense_entry_layer") if isinstance(setup.get("value_defense_entry_layer"), dict) else {}
        if layer:
            layers.append(f"{side.upper()} {layer.get('lifecycle_state') or '監視'}")
    if layers:
        cells.append(("VALUE DEFENSE", " / ".join(layers)))
    candidate = result.get("big_chance_candidate")
    if isinstance(candidate, dict) and candidate.get("present"):
        cells.append(("FAILED THESIS", str(candidate.get("headline") or candidate.get("status") or "候補あり")))
    reasons = " / ".join(str(item) for item in result.get("risk_flags", []) + result.get("no_trade_flags", []))
    if reasons:
        cells.append(("LIQUIDITY", _humanize_visible_status_text(reasons)))
    order_book = result.get("order_book_bias") or result.get("orderbook_bias") or result.get("order_book_diagnostic")
    if order_book:
        cells.append(("ORDER BOOK", str(order_book)))
    momentum = _momentum_confirmation_items(result)
    if momentum:
        cells.append(("MOMENTUM", " / ".join(value for _, value in momentum)))
    return "".join(f'<div class="diagnostic"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>' for label, value in cells)


def _operator_dashboard_v2_details(
    result: dict[str, Any],
    context: dict[str, Any],
    display: dict[str, Any],
    reasons: list[str],
    safety: str,
    base_dir: Path | None,
) -> str:
    scores = (("方向", result.get("confidence_direction_shadow")), ("実行", result.get("confidence_execution_shadow")), ("待機", result.get("confidence_wait_shadow")), ("Long", result.get("long_display_score")), ("Short", result.get("short_display_score")))
    score_html = "".join(f'<div class="score-mini"><span>{label}</span><strong>{_operator_dashboard_score(value)}</strong></div>' for label, value in scores)
    reason_html = "".join(f'<span class="reason-chip">{html.escape(reason)}</span>' for reason in reasons)
    position = context.get("active_position_management") if isinstance(context.get("active_position_management"), dict) else {}
    position_lines = [str(value).strip() for value in position.values() if str(value).strip()]
    position_html = "".join(f"<p>{html.escape(line)}</p>" for line in position_lines) or "<p>保有中は既存の撤退・利確・建値条件を確認します。</p>"
    major_items, major_rows, _ = _major_turning_point_diagnostic_items(result, context, display)
    major_html = "".join(f"<p><strong>{html.escape(label)}:</strong> {html.escape(value)}</p>" for label, value in major_items)
    if major_rows:
        major_rows_text = "".join(
            f"<p><strong>代表行 {index}:</strong> {html.escape(_major_turning_point_diagnostic_row_text(row))}</p>"
            for index, row in enumerate(major_rows[:5], 1)
        )
        major_html += major_rows_text
    major_payload = result.get("major_turning_point_diagnostic")
    if not isinstance(major_payload, dict):
        validation = result.get("app_surface_validation_data")
        if isinstance(validation, dict):
            major_payload = validation.get("major_turning_point_diagnostic")
    if isinstance(major_payload, dict):
        major_html += f"<pre>{html.escape(json.dumps(major_payload, ensure_ascii=False, sort_keys=True, indent=2))}</pre>"
    malformed_post_eval = result.get("post_eval_recommendation_summary")
    post_eval_warning = ""
    if malformed_post_eval is not None and not isinstance(malformed_post_eval, dict):
        post_eval_warning = (
            "<p>post-eval recommendation payload is unavailable or malformed.</p>"
            "<p>report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually</p>"
        )
    internal = (
        _runtime_startup_status_html(base_dir)
        + _safe_config_schema_audit_html(result, context, display)
        + _operator_triage_summary_html(result, context, display)
        + _integrated_evidence_overview_html(result, context, display)
        + _evidence_quality_summary_html(result, context, display)
        + _ohlcv_source_coverage_summary_html(result, context, display)
        + _post_eval_recommendation_status_html(result, context, display)
        + post_eval_warning
        + major_html
        + f'<pre>{html.escape(_raw_mail_text(result, display))}</pre>'
    )
    return f"""
    <section class="panel details-panel">
      <details><summary>判断根拠と5つのスコア</summary><div class="details-body"><div class="score-mini-grid">{score_html}</div><div class="reason-list">{reason_html}</div></div></details>
      <details><summary>高度な検出レイヤー</summary><div class="details-body"><div class="diagnostic-grid">{_operator_dashboard_v2_diagnostic_cells(result)}</div></div></details>
      <details><summary>保有中の処理と安全境界</summary><div class="details-body">{position_html}<p>{html.escape(safety)}</p></div></details>
      <details><summary>内部ログ・Runtime・検証情報</summary><div class="details-body">{internal}</div></details>
    </section>
    """


def _operator_dashboard_v2_script() -> str:
    return """<script>
    (() => {
      const stage = document.getElementById("chart-stage");
      const chart = stage ? stage.querySelector("svg") : null;
      const views = {"15m":"0 726 860 429","1h":"0 363 860 309","4h":"0 0 860 309"};
      document.querySelectorAll("[data-chart-view]").forEach((button) => button.addEventListener("click", () => {
        if (chart) chart.setAttribute("viewBox", views[button.dataset.chartView] || views["15m"]);
        document.querySelectorAll("[data-chart-view]").forEach((item) => item.classList.toggle("active", item === button));
      }));
      document.querySelectorAll("[data-layer-mode]").forEach((button) => button.addEventListener("click", () => {
        if (stage) stage.classList.toggle("basic", button.dataset.layerMode === "basic");
        document.querySelectorAll("[data-layer-mode]").forEach((item) => item.classList.toggle("active", item === button));
      }));
    })();
    </script>"""


def _operator_dashboard_shadow_panel_html(result: dict[str, Any]) -> str:
    try:
        surface = build_manual_operator_shadow_surface(result)
    except Exception:
        surface = {"surface_status": "malformed", "rows": []}
    status = str(surface.get("surface_status", "malformed"))
    labels = {
        "A_FORMAL": "現行の厳格条件を通過したshadow候補。15分足確認後も人間が判断する。",
        "B_CHECK_15M": "15分足確認候補。エントリー許可ではない。",
        "C_WATCH_ZONE": "監視専用。条件改善またはupgrade待ち。",
        "STOP_OR_EXIT": "新規停止・利確・撤退・保護を人間が確認する。自動決済ではない。",
    }
    rows = surface.get("rows") if isinstance(surface.get("rows"), list) else []
    if status == "no_current_candidate":
        body = "現在スナップショットにshadow候補はありません。"
    elif status == "malformed":
        body = "shadow判定は利用できません。既存レポートの判断と診断を優先してください。"
    elif not rows:
        body = "shadow候補はありますが、分類に必要な証拠が不足しています。"
    else:
        cards = []
        for row in rows:
            cls = str(row.get("operator_class") or "insufficient_evidence")
            detail = " / ".join(filter(None, [row.get("side"), row.get("candidate_type"), row.get("candidate_status"), row.get("reason_codes")]))
            price = " / ".join(filter(None, [row.get("entry_price"), row.get("entry_zone_low"), row.get("entry_zone_high"), row.get("invalidation_price"), row.get("tp1_price"), row.get("tp2_price")]))
            cards.append(f'<div class="shadow-card"><strong>{html.escape(cls)}</strong><p>{html.escape(labels.get(cls, "分類に必要な証拠が不足しています。"))}</p><small>{html.escape(detail or "未記録")} / {html.escape(price or "価格未記録")}</small></div>')
        body = "".join(cards)
    return f'<section class="shadow-panel" aria-label="SHADOW REPORT ONLY"><div class="shadow-head"><div><span class="shadow-badge">SHADOW / REPORT ONLY</span><h2>Operator Shadow Surface</h2></div><span class="shadow-safety">not FORMAL_GO / no automatic order / human decides manually</span></div><div class="shadow-legend">A_FORMAL / B_CHECK_15M / C_WATCH_ZONE / STOP_OR_EXIT</div><div class="shadow-body">{body}</div></section>'


def _operator_dashboard_v2_layout(result: dict[str, Any], base_dir: Path | None = None) -> str:
    display = build_display_context(result)
    context = _notification_context_for_result(result)
    kind = str(result.get("notification_kind", "main")).strip().lower() or "main"
    timestamp = str(result.get("timestamp_jst", "")).replace("T", " ") or "未記録"
    safety = _normalize_detail_page_safety_boundary(context.get("followup_safety_boundary") or context.get("safety_boundary") or result.get("actionability_safety"))
    reasons = [str(item).strip() for item in (context.get("reason_labels_full") or _build_wait_reasons(display, result)) if str(item).strip()]
    action = _humanize_visible_status_text(context.get("execution_label", "")).strip() or "見送り"
    decision_word = "WAIT" if kind in {"attention", "followup"} or action in {"見送り", "未記録"} else action.upper()
    conclusion = _operator_v3_conclusion_text(result, context)
    metric_specs = (("方向", "direction", result.get("confidence_direction_shadow")), ("実行", "execution", result.get("confidence_execution_shadow")), ("待機", "wait", result.get("confidence_wait_shadow")))
    metrics = "".join(f'<div class="metric"><span class="metric-label">{label}</span><div class="metric-track"><div class="metric-fill {tone}" style="width:{_operator_dashboard_score(value)}%"></div></div><strong class="metric-value">{_operator_dashboard_score(value)}</strong></div>' for label, tone, value in metric_specs)
    chart = _price_map_svg(result, initial_view_box="0 726 860 429", extra_class="chart-svg")
    big_chance = _operator_dashboard_v2_big_chance(result)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(STABLE_DETAIL_PAGE_PRODUCT_LABEL)}</title><style>{_operator_dashboard_v2_css()}</style></head>
<body class="v2-report operator-dashboard"><div class="shell">
  <div class="topbar"><div class="brand"><span class="brand-mark">₿</span><span>BTCFX OPERATOR</span></div><div class="meta-line"><span>{html.escape(timestamp)}</span><span>signal {html.escape(str(result.get('signal_id') or ''))}</span><span>{html.escape(kind)}</span></div></div>
  <header class="hero"><div class="hero-main"><div class="status-line"><span class="status-badge">● {html.escape(str(context.get('final_rank_label') or '注意報・売買非推奨'))}</span><span class="safety">REPORT ONLY / HUMAN DECISION</span></div><div class="decision-grid"><div class="decision-word">{html.escape(decision_word)}</div><div class="decision-copy"><h1>{html.escape(conclusion)}</h1><p>{html.escape(' / '.join(reasons[:2]) or '価格帯と15分足の反応を確認します。')}</p></div></div><div class="hero-action">{_operator_dashboard_v2_action_summary(context)}</div></div><div class="hero-side"><div class="current-label">BTC CURRENT PRICE</div><div class="current-price">{_format_operator_price(result.get('current_price'))}</div><div class="metric-stack">{metrics}</div><div class="expiry">有効期限：{html.escape(str(context.get('validity_label') or '未記録'))}</div></div></header>
  {_operator_dashboard_v2_alerts(result, context, display)}
  {_operator_dashboard_shadow_panel_html(result)}
  <main class="workspace"><section class="panel chart-panel"><div class="panel-head"><div><h2>チャートと価格レイヤー</h2><p>15分足を主役にし、浅い入りと本命ゾーンは常時表示します。</p></div><div class="chart-controls"><div class="segmented" aria-label="時間足切替"><button class="active" data-chart-view="15m">15分足</button><button data-chart-view="1h">1時間足</button><button data-chart-view="4h">4時間足</button></div><div class="segmented" aria-label="レイヤー切替"><button class="active" data-layer-mode="basic">基本</button><button data-layer-mode="full">全レイヤー</button></div></div></div><div class="chart-legend"><span class="legend-item"><i class="legend-dot long-shallow"></i>Long 浅い入り</span><span class="legend-item"><i class="legend-dot long-main"></i>Long 本命ゾーン</span><span class="legend-item"><i class="legend-dot short-shallow"></i>Short 浅い入り</span><span class="legend-item"><i class="legend-dot short-main"></i>Short 本命ゾーン</span><span>基本表示でも4ゾーンは消えません</span></div><div class="chart-scroll"><div class="chart-stage basic" id="chart-stage">{chart}<div class="chart-note"><span>基本：現在値・浅い入り・本命ゾーン</span><span>全レイヤー：無効化・回収・継続・SL・TPを追加</span></div></div></div></section><aside class="plans">{_operator_dashboard_v2_plan_card(result, 'long')}{_operator_dashboard_v2_plan_card(result, 'short')}</aside></main>
  <section class="lower-grid">{_operator_dashboard_v2_conditions(result, reasons)}<div>{big_chance}{_operator_dashboard_v2_context(result)}</div></section>
  {_operator_dashboard_v2_details(result, context, display, reasons, safety, base_dir)}
  <footer>report-only / not FORMAL_GO / no automatic order / human decides manually</footer>
</div>{_operator_dashboard_v2_script()}</body></html>"""

def build_notification_detail_html(
    result: dict[str, Any],
    base_dir: Path | None = None,
) -> str:
    return _operator_dashboard_v2_layout(result, base_dir=base_dir)

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
    system_slug = STABLE_NOTIFICATION_SYSTEM_SLUG
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
    system_slug = STABLE_NOTIFICATION_SYSTEM_SLUG
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
