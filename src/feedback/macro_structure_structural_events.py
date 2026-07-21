"""Deterministic, event-time-correct M-EVENT1 structural events."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from typing import Any

from src.feedback.macro_structure_volatility_replay import _atr, confirmed_pivots

METHOD_VERSION = "macro_structure_structural_events.v1"
SCHEMA_VERSION = METHOD_VERSION
BAR_INTERVAL = timedelta(hours=4)
APPROACH_ATR = 0.75
TOUCH_ATR = 0.25
BREACH_ATR = 0.35
REJECTION_ATR = 0.50
RETURN_ATR = 0.10
CLUSTER_BARS = 2
REJECTION_BARS = 2
RECLAIM_BARS = 3
RETEST_BARS = 12
RETEST_RESOLUTION_BARS = 2
PIVOT_EQUALITY_ATR = 0.10
MAX_EVENTS = 48
MAX_PIVOT_EVENTS = 8
MAX_DISPLAYED_EVENTS = 12
MAX_MARKERS = 8


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
            raise ValueError("structural_event_candle_invalid")
        timestamp = _utc(raw.get("timestamp") or raw.get("timestamp_utc"), "structural_event_timestamp_invalid")
        if previous is not None and timestamp <= previous:
            raise ValueError("structural_event_timestamp_order_invalid")
        previous = timestamp
        item = {"timestamp": timestamp, "endpoint": timestamp + BAR_INTERVAL}
        for field in ("open", "high", "low", "close"):
            item[field] = _finite(raw.get(field), "structural_event_candle_non_finite")
        if item["high"] < max(item["open"], item["close"]) or item["low"] > min(item["open"], item["close"]) or item["low"] > item["high"]:
            raise ValueError("structural_event_candle_invalid")
        result.append(item)
    if not result:
        raise ValueError("structural_event_no_4h_candles")
    return result


def _atr_at(candles: list[dict[str, Any]], index: int, current_price: float) -> float:
    value = _atr(candles, max(0, min(index, len(candles) - 1)), 14)
    return value if math.isfinite(value) and value > 0 else max(current_price * 0.001, 1e-9)


def _line_value(line: dict[str, Any], index: int, candles: list[dict[str, Any]]) -> float:
    anchor_timestamp = _utc(line.get("anchor_1_timestamp"), "structural_event_line_geometry_invalid")
    anchor_index = next((i for i, candle in enumerate(candles) if candle["timestamp"] == anchor_timestamp), None)
    if anchor_index is None:
        raise ValueError("structural_event_line_anchor_missing")
    value = _finite(line.get("anchor_1_price"), "structural_event_line_geometry_invalid") + _finite(line.get("slope_per_4h_bar"), "structural_event_line_geometry_invalid") * (index - anchor_index)
    return _finite(value, "structural_event_line_geometry_invalid")


def _object_geometry(obj: dict[str, Any], index: int, candles: list[dict[str, Any]]) -> tuple[float, float]:
    if obj["object_kind"] == "horizontal_zone":
        return obj["low"], obj["high"]
    value = _line_value(obj["line"], index, candles)
    return value, value


def _object_direction(obj: dict[str, Any]) -> tuple[str, str]:
    if obj["object_kind"] == "horizontal_zone":
        expected = "UP" if obj["role"] == "support" else "DOWN"
    else:
        expected = "UP" if obj["kind"] == "ascending_support" else "DOWN"
    return expected, "DOWN" if expected == "UP" else "UP"


def _event_id(object_kind: str, object_id: str, event_type: str, timestamp: str, direction: str, parent: str) -> str:
    raw = f"{METHOD_VERSION}|{object_kind}|{object_id}|{event_type}|{timestamp}|{direction}|{parent}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _payload(event: dict[str, Any]) -> str:
    return json.dumps({key: value for key, value in event.items() if key != "event_id"}, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=lambda value: value.isoformat() if isinstance(value, datetime) else str(value))


def _validate_objects(zones: list[dict[str, Any]], trendline_model: dict[str, Any], cutoff: datetime) -> list[dict[str, Any]]:
    objects: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in zones:
        if not isinstance(raw, dict) or not raw.get("level_id"):
            raise ValueError("structural_event_object_id_invalid")
        object_id = str(raw["level_id"])
        low = _finite(raw.get("low"), "structural_event_zone_geometry_invalid")
        high = _finite(raw.get("high"), "structural_event_zone_geometry_invalid")
        center = _finite(raw.get("center"), "structural_event_zone_geometry_invalid")
        if low > high or center < low or center > high or raw.get("role") not in {"support", "resistance"}:
            raise ValueError("structural_event_zone_geometry_invalid")
        available = _utc(raw.get("last_confirmed_at"), "structural_event_availability_invalid")
        item = {"object_kind": "horizontal_zone", "object_id": object_id, "low": low, "high": high, "center": center, "role": raw["role"], "available_at": available}
        key = ("horizontal_zone", object_id)
        if key in objects and _payload(objects[key]) != _payload(item):
            raise ValueError("structural_event_object_conflict")
        objects[key] = item
    if not isinstance(trendline_model, dict):
        raise ValueError("structural_event_line_model_invalid")
    lines = trendline_model.get("lines")
    displayed = trendline_model.get("displayed_line_ids")
    if not isinstance(lines, list) or not isinstance(displayed, list):
        raise ValueError("structural_event_line_model_invalid")
    by_id: dict[str, dict[str, Any]] = {}
    for line in lines:
        if not isinstance(line, dict) or not line.get("line_id"):
            raise ValueError("structural_event_line_invalid")
        line_id = str(line["line_id"])
        if line_id in by_id and _payload(by_id[line_id]) != _payload(line):
            raise ValueError("structural_event_object_conflict")
        by_id[line_id] = line
    for object_id in displayed:
        if object_id not in by_id:
            raise ValueError("structural_event_line_missing")
        line = by_id[object_id]
        if line.get("state") in {"invalidated", "insufficient"} or line.get("kind") not in {"ascending_support", "descending_resistance"}:
            continue
        available = _utc(line.get("confirmation_timestamp"), "structural_event_line_confirmation_invalid")
        if available > cutoff:
            raise ValueError("structural_event_future_object")
        _finite(line.get("slope_per_4h_bar"), "structural_event_line_geometry_invalid")
        _finite(line.get("anchor_1_price"), "structural_event_line_geometry_invalid")
        anchor_1 = _utc(line.get("anchor_1_timestamp"), "structural_event_line_geometry_invalid")
        anchor_2 = _utc(line.get("anchor_2_timestamp"), "structural_event_line_geometry_invalid")
        span = _finite(line.get("anchor_span_bars"), "structural_event_line_geometry_invalid")
        if span <= 0 or anchor_2 <= anchor_1 or abs((anchor_2 - anchor_1) / BAR_INTERVAL - span) > 1e-9:
            raise ValueError("structural_event_line_geometry_invalid")
        confirmation = _utc(line.get("confirmation_timestamp"), "structural_event_line_confirmation_invalid")
        anchor_1_confirmation = _utc(line.get("anchor_1_confirmation_timestamp"), "structural_event_line_confirmation_invalid")
        anchor_2_confirmation = _utc(line.get("anchor_2_confirmation_timestamp"), "structural_event_line_confirmation_invalid")
        if confirmation != max(anchor_1_confirmation, anchor_2_confirmation):
            raise ValueError("structural_event_line_confirmation_invalid")
        item = {"object_kind": "trendline", "object_id": str(object_id), "kind": line["kind"], "line": line, "available_at": available}
        key = ("trendline", str(object_id))
        if key in objects and _payload(objects[key]) != _payload(item):
            raise ValueError("structural_event_object_conflict")
        objects[key] = item
    return [objects[key] for key in sorted(objects)]


def _available(obj: dict[str, Any], candle: dict[str, Any]) -> bool:
    return candle["endpoint"] >= obj["available_at"]


def _breach(obj: dict[str, Any], candle: dict[str, Any], index: int, candles: list[dict[str, Any]], current_price: float) -> tuple[bool, str, str]:
    low, high = _object_geometry(obj, index, candles)
    _, wrong = _object_direction(obj)
    atr = _atr_at(candles, index, current_price)
    if wrong == "DOWN":
        return candle["close"] < low - BREACH_ATR * atr, "DOWN", "UP"
    return candle["close"] > high + BREACH_ATR * atr, "UP", "DOWN"


def _original_side_return(obj: dict[str, Any], candle: dict[str, Any], index: int, candles: list[dict[str, Any]], current_price: float, break_direction: str) -> bool:
    low, high = _object_geometry(obj, index, candles)
    margin = RETURN_ATR * _atr_at(candles, index, current_price)
    if break_direction == "DOWN":
        return candle["close"] >= low + margin
    if break_direction == "UP":
        return candle["close"] <= high - margin
    raise ValueError("structural_event_break_direction_invalid")


def _contact(obj: dict[str, Any], candle: dict[str, Any], index: int, candles: list[dict[str, Any]], current_price: float) -> bool:
    low, high = _object_geometry(obj, index, candles)
    if obj["object_kind"] == "horizontal_zone":
        return candle["high"] >= low and candle["low"] <= high
    expected, _ = _object_direction(obj)
    wick = candle["low"] if expected == "UP" else candle["high"]
    return abs(wick - low) <= TOUCH_ATR * _atr_at(candles, index, current_price)


def _event(obj: dict[str, Any], event_type: str, status: str, sequence: str, timestamp: datetime, direction: str, price: float, low: float, high: float, distance_atr: float, interaction: int = 0, parent: str = "", related: str = "", reasons: list[str] | None = None) -> dict[str, Any]:
    timestamp = _utc(timestamp, "structural_event_timestamp_invalid")
    values = {"event_type": event_type, "event_status": status, "sequence_status": sequence, "event_timestamp_utc": timestamp.isoformat(), "object_kind": obj["object_kind"], "object_id": obj["object_id"], "related_object_id": related, "parent_event_id": parent, "direction": direction, "price": _finite(price, "structural_event_value_non_finite"), "object_value_low": _finite(low, "structural_event_value_non_finite"), "object_value_high": _finite(high, "structural_event_value_non_finite"), "distance_atr": _finite(distance_atr, "structural_event_value_non_finite"), "interaction_count": interaction, "reason_codes": reasons or []}
    values["event_id"] = _event_id(values["object_kind"], values["object_id"], event_type, values["event_timestamp_utc"], direction, parent)
    return values


def _touch_events(obj: dict[str, Any], candles: list[dict[str, Any]], current_price: float, excluded_indices: set[int] | None = None) -> list[dict[str, Any]]:
    contacts = []
    for index, candle in enumerate(candles):
        if excluded_indices and index in excluded_indices:
            continue
        if not _available(obj, candle):
            continue
        breached, _, _ = _breach(obj, candle, index, candles, current_price)
        if not breached and _contact(obj, candle, index, candles, current_price):
            contacts.append(index)
    clusters: list[list[int]] = []
    for index in contacts:
        if not clusters or index - clusters[-1][-1] >= CLUSTER_BARS:
            clusters.append([index])
        else:
            clusters[-1].append(index)
    events = []
    expected, _ = _object_direction(obj)
    for ordinal, cluster in enumerate(clusters, 1):
        index = cluster[0]
        candle = candles[index]
        low, high = _object_geometry(obj, index, candles)
        price = candle["low"] if expected == "UP" else candle["high"]
        distance = abs(price - (low if expected == "UP" else high)) / _atr_at(candles, index, current_price)
        events.append(_event(obj, "touch", "confirmed", "neutral", candle["endpoint"], expected, price, low, high, distance, interaction=ordinal))
    return events


def _rejection_events(obj: dict[str, Any], touch_events: list[dict[str, Any]], candles: list[dict[str, Any]], current_price: float) -> list[dict[str, Any]]:
    result = []
    expected, wrong = _object_direction(obj)
    for touch in touch_events:
        touch_index = next((i for i, candle in enumerate(candles) if candle["endpoint"].isoformat() == touch["event_timestamp_utc"]), None)
        if touch_index is None:
            continue
        for index in range(touch_index + 1, min(len(candles), touch_index + REJECTION_BARS + 1)):
            candle = candles[index]
            breached, _, _ = _breach(obj, candle, index, candles, current_price)
            if breached:
                break
            low, high = _object_geometry(obj, index, candles)
            atr = _atr_at(candles, index, current_price)
            clean = candle["close"] >= high + REJECTION_ATR * atr if expected == "UP" else candle["close"] <= low - REJECTION_ATR * atr
            if clean:
                result.append(_event(obj, "clean_rejection", "confirmed", "neutral", candle["endpoint"], expected, candle["close"], low, high, abs(candle["close"] - (low if expected == "UP" else high)) / atr, interaction=touch["interaction_count"], parent=touch["event_id"]))
                break
    return result


def _sequence_events(obj: dict[str, Any], candles: list[dict[str, Any]], current_price: float) -> list[dict[str, Any]]:
    expected, wrong = _object_direction(obj)
    result: list[dict[str, Any]] = []
    index = 0
    rearmed = True
    rearm_direction: str | None = None
    while index < len(candles):
        candle = candles[index]
        if not _available(obj, candle):
            index += 1
            continue
        breached, break_direction, _ = _breach(obj, candle, index, candles, current_price)
        if not rearmed or not breached:
            if rearmed is False and not breached and rearm_direction is not None:
                rearmed = _original_side_return(obj, candle, index, candles, current_price, rearm_direction)
            index += 1
            continue
        low, high = _object_geometry(obj, index, candles)
        atr = _atr_at(candles, index, current_price)
        break_event = _event(obj, "break", "confirmed", "pending", candle["endpoint"], break_direction, candle["close"], low, high, abs(candle["close"] - (low if break_direction == "DOWN" else high)) / atr)
        result.append(break_event)
        acceptance_index: int | None = None
        reclaim_index: int | None = None
        for candidate in range(index + 1, min(len(candles), index + RECLAIM_BARS + 1)):
            candidate_candle = candles[candidate]
            candidate_breach, _, _ = _breach(obj, candidate_candle, candidate, candles, current_price)
            low_c, high_c = _object_geometry(obj, candidate, candles)
            if candidate_breach and candidate == index + 1:
                acceptance_index = candidate
                break
            if not candidate_breach and _original_side_return(obj, candidate_candle, candidate, candles, current_price, break_direction):
                reclaim_index = candidate
                break
        if reclaim_index is not None:
            reclaim_candle = candles[reclaim_index]
            low_r, high_r = _object_geometry(obj, reclaim_index, candles)
            break_event["sequence_status"] = "reclaimed"
            result.append(_event(obj, "false_break_reclaim", "confirmed", "reclaimed", reclaim_candle["endpoint"], expected, reclaim_candle["close"], low_r, high_r, 0.0, parent=break_event["event_id"]))
            rearmed = False
            rearm_direction = break_direction
            index = reclaim_index + 1
            continue
        if acceptance_index is not None:
            accept_candle = candles[acceptance_index]
            low_a, high_a = _object_geometry(obj, acceptance_index, candles)
            break_event["sequence_status"] = "accepted"
            acceptance = _event(obj, "closed_candle_acceptance", "confirmed", "accepted", accept_candle["endpoint"], break_direction, accept_candle["close"], low_a, high_a, 0.0, parent=break_event["event_id"])
            result.append(acceptance)
            retest_index = None
            for candidate in range(acceptance_index + 1, min(len(candles), acceptance_index + RETEST_BARS + 1)):
                if _contact(obj, candles[candidate], candidate, candles, current_price):
                    retest_index = candidate
                    break
            if retest_index is not None:
                retest_candle = candles[retest_index]
                low_r, high_r = _object_geometry(obj, retest_index, candles)
                retest = _event(obj, "retest", "confirmed", "accepted", retest_candle["endpoint"], expected, retest_candle["close"], low_r, high_r, 0.0, parent=acceptance["event_id"])
                result.append(retest)
                for candidate in range(retest_index + 1, min(len(candles), retest_index + RETEST_RESOLUTION_BARS + 1)):
                    candidate_candle = candles[candidate]
                    candidate_breach, _, _ = _breach(obj, candidate_candle, candidate, candles, current_price)
                    low_c, high_c = _object_geometry(obj, candidate, candles)
                    atr_c = _atr_at(candles, candidate, current_price)
                    if candidate_breach:
                        result.append(_event(obj, "retest_hold", "confirmed", "accepted", candidate_candle["endpoint"], break_direction, candidate_candle["close"], low_c, high_c, 0.0, parent=retest["event_id"]))
                        break
                    if _original_side_return(obj, candidate_candle, candidate, candles, current_price, break_direction):
                        result.append(_event(obj, "retest_failure", "confirmed", "accepted", candidate_candle["endpoint"], expected, candidate_candle["close"], low_c, high_c, 0.0, parent=retest["event_id"]))
                        break
            rearmed = False
            rearm_direction = break_direction
            index = (retest_index + 1 if retest_index is not None else acceptance_index + 1)
            continue
        available_followups = len(candles) - index - 1
        if available_followups < RECLAIM_BARS:
            # The fixed resolution window has not been observed yet.  Keep
            # this same break event pending and stop this object's scan; no
            # future bar may be inferred from the cutoff.
            return result
        break_event["sequence_status"] = "unresolved"
        rearmed = False
        rearm_direction = break_direction
        index += RECLAIM_BARS + 1
    return result


def _pivot_events(pivots: list[dict[str, Any]], candles: list[dict[str, Any]], current_price: float, cutoff: datetime) -> list[dict[str, Any]]:
    result = []
    previous: dict[str, dict[str, Any]] = {}
    for pivot in pivots:
        if pivot["confirmation_timestamp"] > cutoff:
            continue
        side = pivot["side"]
        prior = previous.get(side)
        previous[side] = pivot
        if prior is None:
            continue
        index = next((i for i, candle in enumerate(candles) if candle["timestamp"] == pivot["pivot_timestamp"]), 0)
        atr = _finite(pivot.get("atr_at_confirmation") or _atr_at(candles, index, current_price), "structural_event_pivot_atr_invalid")
        delta = pivot["price"] - prior["price"]
        if abs(delta) <= PIVOT_EQUALITY_ATR * atr:
            continue
        if side == "high":
            event_type, direction = ("higher_high", "UP") if delta > 0 else ("lower_high", "DOWN")
        else:
            event_type, direction = ("higher_low", "UP") if delta > 0 else ("lower_low", "DOWN")
        result.append(_event({"object_kind": "pivot_structure", "object_id": pivot["pivot_id"]}, event_type, "confirmed", "neutral", pivot["confirmation_timestamp"], direction, pivot["price"], pivot["price"], pivot["price"], abs(delta) / atr, related=prior["pivot_id"]))
    return result


def _sort_key(event: dict[str, Any]) -> tuple[int, int, float, str]:
    return (0 if event["event_status"] == "ongoing" and event["event_type"] == "approach" else 1 if event["sequence_status"] == "pending" else 2, 0 if event["event_status"] == "confirmed" and event["event_type"] != "approach" else 1, -_utc(event["event_timestamp_utc"], "structural_event_timestamp_invalid").timestamp(), event["event_id"])


def _retain(events: list[dict[str, Any]], cutoff: datetime) -> list[dict[str, Any]]:
    pivot_events = [event for event in events if event["object_kind"] == "pivot_structure"]
    pivot_keep = {event["event_id"] for event in sorted(pivot_events, key=lambda item: (item["event_timestamp_utc"], item["event_id"]), reverse=True)[:MAX_PIVOT_EVENTS]}
    candidates = [event for event in events if event["object_kind"] != "pivot_structure" or event["event_id"] in pivot_keep]
    by_id = {event["event_id"]: event for event in events}
    eligible = sorted(candidates, key=lambda item: (-_utc(item["event_timestamp_utc"], "structural_event_timestamp_invalid").timestamp(), item["event_id"]))
    retained_by_id: dict[str, dict[str, Any]] = {}
    for event in eligible:
        chain: list[dict[str, Any]] = []
        cursor: dict[str, Any] | None = event
        chain_ids: set[str] = set()
        while cursor is not None and cursor["event_id"] not in retained_by_id:
            if cursor["event_id"] in chain_ids:
                raise ValueError("structural_event_parent_cycle")
            chain.append(cursor)
            chain_ids.add(cursor["event_id"])
            parent = cursor.get("parent_event_id")
            if not parent:
                cursor = None
            elif parent not in by_id:
                raise ValueError("structural_event_parent_missing")
            else:
                cursor = by_id[parent]
        if len(retained_by_id) + len(chain) <= MAX_EVENTS:
            for item in chain:
                retained_by_id[item["event_id"]] = item
    retained = list(retained_by_id.values())
    return sorted(retained, key=lambda item: (_utc(item["event_timestamp_utc"], "structural_event_timestamp_invalid"), item["event_id"]))


def build_structural_event_model(candles: list[dict[str, Any]], *, cutoff: datetime, current_price: float, zones: list[dict[str, Any]], trendline_model: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalise_candles(candles)
    cutoff = _utc(cutoff, "structural_event_cutoff_invalid")
    current_price = _finite(current_price, "structural_event_current_price_invalid")
    closed = [candle for candle in normalized if candle["endpoint"] <= cutoff]
    if not closed:
        raise ValueError("structural_event_no_closed_4h_candle")
    objects = _validate_objects(zones, trendline_model, cutoff)
    pivots = confirmed_pivots(closed, "4h", left=2, right=2)
    if any(pivot["confirmation_timestamp"] > cutoff for pivot in pivots if pivot["pivot_timestamp"] + BAR_INTERVAL <= cutoff):
        raise ValueError("structural_event_pivot_confirmation_invalid")
    events: list[dict[str, Any]] = []
    latest = closed[-1]
    for obj in objects:
        sequence = _sequence_events(obj, closed, current_price)
        retest_indices = {index for index, candle in enumerate(closed) if any(event["event_type"] == "retest" and event["event_timestamp_utc"] == candle["endpoint"].isoformat() for event in sequence)}
        touches = _touch_events(obj, closed, current_price, excluded_indices=retest_indices)
        events.extend(touches)
        events.extend(_rejection_events(obj, touches, closed, current_price))
        events.extend(sequence)
        low, high = _object_geometry(obj, len(closed) - 1, closed)
        if not (latest["high"] >= low and latest["low"] <= high):
            expected, _ = _object_direction(obj)
            distance = min(abs(latest["close"] - low), abs(latest["close"] - high)) / _atr_at(closed, len(closed) - 1, current_price)
            if distance <= APPROACH_ATR:
                events.append(_event(obj, "approach", "ongoing", "ongoing", latest["endpoint"], expected, latest["close"], low, high, distance, reasons=["latest_closed_bar_only"]))
    events.extend(_pivot_events(pivots, closed, current_price, cutoff))
    by_id: dict[str, str] = {}
    unique: list[dict[str, Any]] = []
    for event in sorted(events, key=lambda item: (item["event_timestamp_utc"], item["event_id"], item["event_type"])):
        payload = _payload(event)
        if event["event_id"] in by_id and by_id[event["event_id"]] != payload:
            raise ValueError("structural_event_id_collision")
        if event["event_id"] not in by_id:
            by_id[event["event_id"]] = payload; unique.append(event)
    retained = _retain(unique, cutoff)
    retained_ids = {event["event_id"] for event in retained}
    if any(event.get("parent_event_id") and event["parent_event_id"] not in retained_ids for event in retained):
        raise ValueError("structural_event_parent_missing")
    current_events = [event for event in retained if event["event_status"] == "ongoing"]
    displayed = sorted(retained, key=_sort_key)[:MAX_DISPLAYED_EVENTS]
    displayed_ids = [event["event_id"] for event in displayed]
    status = "ok" if retained else "insufficient"
    return {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "cutoff_utc": cutoff.isoformat(), "status": status, "objects_evaluated": [{"object_kind": obj["object_kind"], "object_id": obj["object_id"]} for obj in objects], "events": retained, "current_events": current_events, "displayed_event_ids": displayed_ids, "reason_codes": [] if status == "ok" else ["insufficient_structural_event_evidence"]}
