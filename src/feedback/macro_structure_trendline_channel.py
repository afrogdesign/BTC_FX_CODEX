"""Deterministic, report-only M-LINE1 trendline and channel model."""
from __future__ import annotations

import hashlib
import math
from datetime import datetime, timedelta, timezone
from typing import Any

from src.feedback.macro_structure_volatility_replay import _atr, confirmed_pivots

METHOD_VERSION = "macro_structure_trendline.v1"
SCHEMA_VERSION = "macro_structure_trendline.v1"
PIVOT_METHOD = "confirmed_pivots(candles, '4h', left=2, right=2)"
BAR_INTERVAL = timedelta(hours=4)
MAX_PIVOTS = 12
MAX_CANDIDATES = 3
MIN_ANCHOR_BARS = 3
MAX_ANCHOR_BARS = 120
TOUCH_ATR = 0.25
BREACH_ATR = 0.35
RECENT_BROKEN_BARS = 12


def _finite(value: Any, code: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(code) from exc
    if not math.isfinite(number):
        raise ValueError(code)
    return number


def _utc(value: Any, code: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(code) from exc
    else:
        raise ValueError(code)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalise_candles(candles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    previous: datetime | None = None
    for raw in candles:
        if not isinstance(raw, dict):
            raise ValueError("trendline_candle_invalid")
        timestamp = _utc(raw.get("timestamp") or raw.get("timestamp_utc"), "trendline_timestamp_invalid")
        if previous is not None and timestamp <= previous:
            raise ValueError("trendline_timestamp_order_invalid")
        previous = timestamp
        item = {"timestamp": timestamp, "interval": "4h"}
        for field in ("open", "high", "low", "close"):
            item[field] = _finite(raw.get(field), "trendline_candle_non_finite")
        if item["high"] < max(item["open"], item["close"]) or item["low"] > min(item["open"], item["close"]) or item["low"] > item["high"]:
            raise ValueError("trendline_candle_invalid")
        result.append(item)
    if not result:
        raise ValueError("trendline_no_4h_candles")
    return result


def _fallback_atr(candles: list[dict[str, Any]], index: int, current_price: float) -> float:
    value = _atr(candles, max(0, min(index, len(candles) - 1)), 14)
    return value if math.isfinite(value) and value > 0 else max(current_price * 0.001, 1e-9)


def _line_id(kind: str, first: dict[str, Any], second: dict[str, Any]) -> str:
    raw = f"{METHOD_VERSION}|{kind}|{first['pivot_id']}|{second['pivot_id']}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _channel_id(base_line_id: str, opposite_pivot_id: str) -> str:
    raw = f"macro_structure_channel.v1|{base_line_id}|{opposite_pivot_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _value(line: dict[str, Any], index: int) -> float:
    return line["anchor_1_price"] + line["slope_per_4h_bar"] * (index - line["anchor_1_index"])


def _pivot_index(pivot: dict[str, Any], candles: list[dict[str, Any]]) -> int:
    timestamp = _utc(pivot.get("pivot_timestamp"), "trendline_pivot_timestamp_invalid")
    for index, candle in enumerate(candles):
        if candle["timestamp"] == timestamp:
            return index
    raise ValueError("trendline_pivot_not_in_candles")


def _touches(line: dict[str, Any], candles: list[dict[str, Any]], start: int, cutoff: datetime, current_price: float) -> tuple[list[dict[str, Any]], datetime | None, str | None]:
    candidates: list[dict[str, Any]] = []
    break_timestamp: datetime | None = None
    invalidated = False
    for index in range(start, len(candles)):
        candle = candles[index]
        endpoint = candle["timestamp"] + BAR_INTERVAL
        if endpoint > cutoff:
            continue
        value = _value(line, index)
        atr = _fallback_atr(candles, index, current_price)
        close = candle["close"]
        breach = (close < value - BREACH_ATR * atr) if line["kind"] == "ascending_support" else (close > value + BREACH_ATR * atr)
        if index <= line["anchor_2_index"] and breach:
            invalidated = True
            continue
        if index > line["anchor_2_index"] and endpoint > line["confirmation_timestamp"] and breach:
            if break_timestamp is None:
                break_timestamp = endpoint
            continue
        wick = candle["low"] if line["kind"] == "ascending_support" else candle["high"]
        if abs(wick - value) <= TOUCH_ATR * atr:
            candidates.append({"index": index, "timestamp": endpoint, "price": wick})
    if invalidated:
        return [], None, "invalidated"
    clusters: list[list[dict[str, Any]]] = []
    for touch in candidates:
        if not clusters or touch["index"] - clusters[-1][-1]["index"] >= 2:
            clusters.append([touch])
        else:
            clusters[-1].append(touch)
    representatives = [cluster[0] for cluster in clusters]
    return representatives, break_timestamp, None


def _candidate(kind: str, first: dict[str, Any], second: dict[str, Any], first_index: int, second_index: int, candles: list[dict[str, Any]], cutoff: datetime, current_price: float) -> dict[str, Any]:
    span = second_index - first_index
    slope = (_finite(second["price"], "trendline_price_non_finite") - _finite(first["price"], "trendline_price_non_finite")) / span
    if not math.isfinite(slope):
        raise ValueError("trendline_slope_non_finite")
    line = {
        "line_id": _line_id(kind, first, second), "kind": kind,
        "anchor_1_pivot_id": first["pivot_id"], "anchor_1_timestamp": first["pivot_timestamp"].isoformat(), "anchor_1_price": first["price"], "anchor_1_confirmation_timestamp": first["confirmation_timestamp"].isoformat(),
        "anchor_2_pivot_id": second["pivot_id"], "anchor_2_timestamp": second["pivot_timestamp"].isoformat(), "anchor_2_price": second["price"], "anchor_2_confirmation_timestamp": second["confirmation_timestamp"].isoformat(),
        "confirmation_timestamp": max(first["confirmation_timestamp"], second["confirmation_timestamp"]), "slope_per_4h_bar": slope, "anchor_span_bars": span,
        "anchor_1_index": first_index, "anchor_2_index": second_index,
    }
    touches, break_timestamp, invalid_reason = _touches(line, candles, first_index, cutoff, current_price)
    line["touch_count"] = len(touches)
    line["touch_timestamps"] = [item["timestamp"].isoformat() for item in touches]
    line["break_timestamp"] = break_timestamp.isoformat() if break_timestamp else ""
    line["state"] = invalid_reason or ("broken" if break_timestamp else "tested" if len(touches) >= 3 else "active" if len(touches) == 2 else "insufficient")
    line["current_line_value"] = _value(line, len(candles) - 1)
    distance = current_price - line["current_line_value"]
    atr = _fallback_atr(candles, len(candles) - 1, current_price)
    line["distance_from_price"] = distance
    line["distance_from_price_pct"] = abs(distance) / max(abs(current_price), 1e-12) * 100
    line["distance_from_price_atr"] = distance / atr
    line["confirmation_timestamp"] = line["confirmation_timestamp"].isoformat()
    for key in ("current_line_value", "distance_from_price", "distance_from_price_pct", "distance_from_price_atr"):
        _finite(line[key], "trendline_geometry_non_finite")
    return line


def _state_priority(line: dict[str, Any]) -> tuple[int, int, str, int, float, str]:
    return ({"tested": 3, "active": 2, "broken": 1, "insufficient": 0, "invalidated": -1}.get(line["state"], -1), -line["touch_count"], line["anchor_2_confirmation_timestamp"], -line["anchor_span_bars"], abs(line["distance_from_price_atr"]), line["line_id"])


def _select_display(lines: list[dict[str, Any]], cutoff: datetime, candle_count: int) -> list[str]:
    live = sorted((line for line in lines if line["state"] in {"tested", "active"}), key=_state_priority)
    broken = sorted((line for line in lines if line["state"] == "broken" and line["break_timestamp"] and _utc(line["break_timestamp"], "trendline_break_timestamp_invalid") >= cutoff - RECENT_BROKEN_BARS * BAR_INTERVAL), key=_state_priority)
    selected = ([live[0]] if live else []) + ([broken[0]] if broken else [])
    return [line["line_id"] for line in selected]


def _line_for_kind(lines: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    choices = sorted((line for line in lines if line["kind"] == kind and line["state"] in {"tested", "active"}), key=_state_priority)
    return choices[0] if choices else None


def _channel(base: dict[str, Any], pivots: list[dict[str, Any]], pivot_indices: dict[str, int], candles: list[dict[str, Any]], cutoff: datetime, current_price: float) -> dict[str, Any] | None:
    opposite_side = "high" if base["kind"] == "ascending_support" else "low"
    candidates = []
    for pivot in pivots:
        if pivot["side"] != opposite_side or pivot["confirmation_timestamp"] > cutoff or pivot_indices[pivot["pivot_id"]] < base["anchor_1_index"]:
            continue
        index = pivot_indices[pivot["pivot_id"]]
        residual = pivot["price"] - _value(base, index)
        if (base["kind"] == "ascending_support" and residual > 0) or (base["kind"] == "descending_resistance" and residual < 0):
            candidates.append((abs(residual), residual, pivot, index))
    if not candidates:
        return None
    _, residual, opposite, opposite_index = max(candidates, key=lambda item: (item[0], item[2]["confirmation_timestamp"], item[2]["pivot_id"]))
    confirmation = max(_utc(base["confirmation_timestamp"], "trendline_confirmation_invalid"), opposite["confirmation_timestamp"])
    if confirmation > cutoff:
        return None
    width = abs(residual)
    atr = _fallback_atr(candles, len(candles) - 1, current_price)
    width_atr = width / atr
    if not math.isfinite(width) or not math.isfinite(width_atr) or not 0.75 <= width_atr <= 12:
        return None
    base_value = _value(base, len(candles) - 1)
    if base["kind"] == "ascending_support":
        lower, upper = base_value, base_value + width
        kind = "ascending_channel"
    else:
        lower, upper = base_value - width, base_value
        kind = "descending_channel"
    if not all(math.isfinite(number) for number in (lower, upper)) or lower > upper:
        raise ValueError("trendline_channel_boundary_invalid")
    channel = {
        "channel_id": _channel_id(base["line_id"], opposite["pivot_id"]), "kind": kind, "base_line_id": base["line_id"], "opposite_anchor_pivot_id": opposite["pivot_id"],
        "confirmation_timestamp": confirmation.isoformat(), "lower_value_at_cutoff": lower, "upper_value_at_cutoff": upper, "width_at_cutoff": width, "width_atr": width_atr,
        "current_position_percent": (current_price - lower) / width * 100, "state": base["state"], "opposite_anchor_timestamp": opposite["pivot_timestamp"].isoformat(),
        "opposite_anchor_index": opposite_index,
    }
    if not math.isfinite(channel["current_position_percent"]):
        raise ValueError("trendline_channel_non_finite")
    return channel


def build_trendline_model(candles: list[dict[str, Any]], *, cutoff: datetime, current_price: float) -> dict[str, Any]:
    """Build M-LINE1 from closed, cutoff-bounded 4H candles."""
    normalized = _normalise_candles(candles)
    cutoff = _utc(cutoff, "trendline_cutoff_invalid")
    current_price = _finite(current_price, "trendline_current_price_invalid")
    closed = [c for c in normalized if c["timestamp"] + BAR_INTERVAL <= cutoff]
    if not closed:
        raise ValueError("trendline_no_closed_4h_candle")
    pivots = confirmed_pivots(closed, "4h", left=2, right=2)
    if any(pivot["confirmation_timestamp"] > cutoff for pivot in pivots if pivot["pivot_timestamp"] + BAR_INTERVAL <= cutoff):
        raise ValueError("trendline_pivot_confirmation_inconsistent")
    pivot_indices = {pivot["pivot_id"]: _pivot_index(pivot, closed) for pivot in pivots}
    by_kind: dict[str, list[dict[str, Any]]] = {"ascending_support": [], "descending_resistance": []}
    for side, kind in (("low", "ascending_support"), ("high", "descending_resistance")):
        selected = [pivot for pivot in pivots if pivot["side"] == side and pivot["confirmation_timestamp"] <= cutoff][-MAX_PIVOTS:]
        for first_index, first in enumerate(selected):
            for second in selected[first_index + 1:]:
                i1, i2 = pivot_indices[first["pivot_id"]], pivot_indices[second["pivot_id"]]
                if not MIN_ANCHOR_BARS <= i2 - i1 <= MAX_ANCHOR_BARS:
                    continue
                if kind == "ascending_support" and second["price"] <= first["price"]:
                    continue
                if kind == "descending_resistance" and second["price"] >= first["price"]:
                    continue
                line = _candidate(kind, first, second, i1, i2, closed, cutoff, current_price)
                by_kind[kind].append(line)
        by_kind[kind] = sorted(by_kind[kind], key=_state_priority)[:MAX_CANDIDATES]
    lines = by_kind["ascending_support"] + by_kind["descending_resistance"]
    displayed_line_ids = [line_id for kind in by_kind for line_id in _select_display(by_kind[kind], cutoff, len(closed))]
    channels = []
    for kind in ("ascending_support", "descending_resistance"):
        base = _line_for_kind(lines, kind)
        if base:
            channel = _channel(base, pivots, pivot_indices, closed, cutoff, current_price)
            if channel:
                channels.append(channel)
    displayed_channel_ids = [channel["channel_id"] for channel in channels]
    status = "ok" if displayed_line_ids or displayed_channel_ids else "insufficient"
    return {
        "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "pivot_method": PIVOT_METHOD,
        "cutoff_utc": cutoff.isoformat(), "status": status, "lines": lines, "displayed_line_ids": displayed_line_ids,
        "channels": channels, "displayed_channel_ids": displayed_channel_ids,
        "reason_codes": [] if status == "ok" else ["insufficient_confirmed_4h_evidence"],
    }
