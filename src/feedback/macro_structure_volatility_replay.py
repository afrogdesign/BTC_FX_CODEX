"""Deterministic, event-time, report-only macro structure replay.

This module intentionally depends only on explicit local CSV files.  It is a
diagnostic layer: it never changes scoring, gates, notifications, runtime, or
trading behaviour.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any

METHOD_VERSION = "macro_structure_volatility_replay.v1"
SCHEMA_VERSION = "macro_structure_volatility_replay.v1"
LEVEL_SCHEMA_VERSION = "level_reliability.v1"
SAFETY = "report-only / not FORMAL_GO / human-decided / no automatic order"
EXPECTED_INTERVALS = {"15m": timedelta(minutes=15), "1h": timedelta(hours=1), "4h": timedelta(hours=4)}
MICRO_FIELDS = ("order_flow_imbalance", "aggressive_buy_ratio", "aggressive_sell_ratio", "orderbook_depth_imbalance", "spread_bps", "cvd_slope", "oi_change_pct", "cvd_price_divergence", "orderbook_bias")
ROOT_CAUSES = ("structure_not_established", "reliable_level_missing", "level_reliability_miscalibrated", "rejection_event_missing", "break_acceptance_missing", "false_break_reclaim_missing", "pressure_or_imbalance_unavailable", "pressure_or_imbalance_not_recognized", "travel_corridor_not_recognized", "volatility_regime_misclassified", "precursor_policy_too_strict", "correct_no_signal", "data_unresolved")
EVENT_FIELDS = ("schema_version", "method_version", "event_id", "signal_id", "event_timestamp_utc", "event_timestamp_jst", "event_price", "was_notified", "current_tactical_side", "structural_state", "price_location", "nearest_support_id", "nearest_resistance_id", "next_upside_target_id", "next_downside_target_id", "event_family", "structural_direction", "expansion_risk", "directional_activation", "first_reliable_target", "intervening_obstruction", "volatility_state", "volatility_persistence", "volatility_bars_used", "level_reliability_band", "pressure_evidence_json", "forecast_json", "outcome_1h", "outcome_3h", "outcome_6h", "outcome_12h", "outcome_24h", "upward_excursion", "downward_excursion", "mfe_atr", "mae_atr", "first_material_move_timestamp", "target_touch", "adverse_before_target", "whipsaw", "level_behavior", "large_move_side", "jump_like", "data_quality_status", "reason_codes")
LEVEL_FIELDS = ("schema_version", "method_version", "level_id", "side", "low", "high", "center", "source_timeframes", "first_seen_at", "last_confirmed_at", "touch_count", "clean_rejection_count", "break_count", "false_break_reclaim_count", "median_reaction_atr", "median_hold_hours", "recency_score", "cross_timeframe_confluence", "reliability_score", "reliability_band", "lifecycle", "role", "member_pivot_ids", "member_pivot_timestamps", "member_confirmation_timestamps", "reason_codes")
MISS_FIELDS = ("opportunity_id", "direction", "start_timestamp_utc", "material_move_timestamp_utc", "move_size_atr", "structure_state", "price_location", "nearest_support_id", "nearest_resistance_id", "current_notification_fired", "turning_precursor_fired", "root_cause", "reason_codes", "data_quality_status")


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace("Z", "+00:00")
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _num(value: Any) -> float | None:
    try:
        n = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _parse_structured(value: Any) -> Any:
    text = str(value or "").strip()
    if text.startswith(("[", "{")):
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("malformed_structured_signal") from exc
        if not isinstance(parsed, (list, dict)):
            raise ValueError("malformed_structured_signal")
        return parsed
    return [x.strip() for x in text.replace("|", ",").split(",") if x.strip()] if text else []


def _tokens(value: Any) -> set[str]:
    parsed = _parse_structured(value)
    if isinstance(parsed, dict):
        return {str(key).strip().lower() for key, item in parsed.items() if item}
    return {str(item).strip().lower() for item in parsed if str(item).strip()}


def _signal_tokens(row: dict[str, str]) -> set[str]:
    fields = ("market_map_flags", "warning_flags", "risk_flags", "active_level_role", "level_flip_state", "failed_breakout_state", "trend_flip_state")
    result: set[str] = set()
    for field in fields:
        result.update(_tokens(row.get(field)))
    for field in ("primary_setup_reason", "notification_kind", "primary_setup_status"):
        result.update(str(row.get(field) or "").lower().replace("/", " ").replace(",", " ").split())
    return result


def _micro_value(value: Any, field: str) -> tuple[str, str | None]:
    text = str(value or "").strip().lower()
    if not text:
        return "unavailable", None
    numeric = _num(text)
    if field == "spread_bps":
        if numeric is None or numeric < 0:
            return "unavailable", None
        return ("absent", None) if numeric == 0 else ("present", None)
    if field == "oi_change_pct":
        if numeric is None:
            return "unavailable", None
        return ("absent", None) if numeric == 0 else ("present", None)
    if field in {"order_flow_imbalance", "orderbook_depth_imbalance", "cvd_slope"}:
        if numeric is None:
            return "unavailable", None
        if numeric == 0:
            return "absent", None
        return "present", "UP" if numeric > 0 else "DOWN"
    if field in {"aggressive_buy_ratio", "aggressive_sell_ratio"}:
        if numeric is None or not 0 <= numeric <= 1:
            return "unavailable", None
        if numeric == .5:
            return "absent", None
        if numeric < .5:
            return "absent", None
        return "present", "UP" if field == "aggressive_buy_ratio" else "DOWN"
    if field in {"cvd_price_divergence", "orderbook_bias"}:
        if text in {"bullish", "bid_heavy", "bid", "up"}:
            return "present", "UP"
        if text in {"bearish", "ask_heavy", "ask", "down"}:
            return "present", "DOWN"
        return "absent", None
    return "unavailable", None


def _csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError("input_file_missing")
    with path.open(newline="", encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        if not reader.fieldnames:
            raise ValueError("csv_header_missing")
        return [dict(row) for row in reader]


def _load_ohlcv(path: Path, expected: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = _csv_rows(path)
    required = {"timestamp_utc", "open", "high", "low", "close"}
    if not required.issubset(rows[0].keys() if rows else set()):
        raise ValueError("ohlcv_schema_mismatch")
    interval_values = {str(row.get("interval") or "").strip() for row in rows if str(row.get("interval") or "").strip()}
    if interval_values and interval_values != {expected}:
        raise ValueError("ohlcv_interval_mismatch")
    result = []
    previous: datetime | None = None
    gaps = 0
    for row in rows:
        timestamp = _dt(row.get("timestamp_utc"))
        values = [_num(row.get(key)) for key in ("open", "high", "low", "close")]
        if timestamp is None or any(value is None for value in values):
            raise ValueError("ohlcv_malformed")
        if previous is not None:
            delta = timestamp - previous
            if delta <= timedelta(0):
                raise ValueError("ohlcv_non_monotonic_or_duplicate")
            if delta != EXPECTED_INTERVALS[expected]:
                gaps += 1
        result.append({"timestamp": timestamp, "open": values[0], "high": values[1], "low": values[2], "close": values[3], "volume": _num(row.get("volume")), "interval": expected})
        previous = timestamp
    return result, {"interval": expected, "rows": len(result), "min_timestamp": result[0]["timestamp"].isoformat() if result else "", "max_timestamp": result[-1]["timestamp"].isoformat() if result else "", "gap_count": gaps, "continuity": gaps == 0}


def _load_signals(path: Path) -> list[dict[str, str]]:
    rows = _csv_rows(path)
    required = {"signal_id", "timestamp_utc", "current_price"}
    if not rows or not required.issubset(rows[0].keys()):
        raise ValueError("signals_schema_mismatch")
    result = []
    for row in rows:
        if _dt(row.get("timestamp_utc")) is None or _num(row.get("current_price")) is None:
            raise ValueError("signals_malformed")
        for field in ("market_map_flags", "warning_flags", "risk_flags", "active_level_role", "level_flip_state", "failed_breakout_state", "trend_flip_state"):
            _parse_structured(row.get(field))
        result.append(row)
    return sorted(result, key=lambda row: (_dt(row["timestamp_utc"]), str(row.get("signal_id", ""))))


def _tr(c: dict[str, Any], previous: dict[str, Any] | None) -> float:
    return max(c["high"] - c["low"], abs(c["high"] - previous["close"]), abs(c["low"] - previous["close"])) if previous else c["high"] - c["low"]


def _atr(candles: list[dict[str, Any]], index: int, window: int = 14) -> float:
    start = max(0, index - window + 1)
    values = [_tr(candles[i], candles[i - 1] if i else None) for i in range(start, index + 1)]
    return sum(values) / len(values) if values else 0.0


def confirmed_pivots(candles: list[dict[str, Any]], timeframe: str, left: int = 2, right: int = 2) -> list[dict[str, Any]]:
    """Return pivots with confirmation time, never backdated as an event."""
    pivots = []
    for index in range(left, len(candles) - right):
        window = candles[index - left:index + right + 1]
        high, low = candles[index]["high"], candles[index]["low"]
        if all(high > c["high"] for c in window if c is not candles[index]):
            pivots.append({"pivot_id": f"{timeframe}:H:{candles[index]['timestamp'].isoformat()}", "side": "high", "price": high, "pivot_timestamp": candles[index]["timestamp"], "confirmation_timestamp": candles[index + right]["timestamp"] + EXPECTED_INTERVALS[timeframe], "source_timeframe": timeframe, "atr_at_confirmation": _atr(candles, index + right)})
        if all(low < c["low"] for c in window if c is not candles[index]):
            pivots.append({"pivot_id": f"{timeframe}:L:{candles[index]['timestamp'].isoformat()}", "side": "low", "price": low, "pivot_timestamp": candles[index]["timestamp"], "confirmation_timestamp": candles[index + right]["timestamp"] + EXPECTED_INTERVALS[timeframe], "source_timeframe": timeframe, "atr_at_confirmation": _atr(candles, index + right)})
    return sorted(pivots, key=lambda item: (item["confirmation_timestamp"], item["pivot_timestamp"], item["side"], item["source_timeframe"]))


def _bucket(price: float) -> int:
    return int(math.floor(math.log(price) / math.log(1.0015))) if price > 0 else 0


def build_levels(pivots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    levels: list[dict[str, Any]] = []
    for pivot in pivots:
        tolerance = max(0.30 * (pivot["atr_at_confirmation"] or 0), pivot["price"] * 0.0015)
        candidates = [level for level in levels if level["side"] == pivot["side"] and abs(level["center"] - pivot["price"]) <= tolerance]
        if candidates:
            level = min(candidates, key=lambda item: (abs(item["center"] - pivot["price"]), item["first_confirmed"]))
            level["members"].append(pivot)
            prices = [member["price"] for member in level["members"]]
            level["center"] = median(prices); level["low"] = min(prices); level["high"] = max(prices)
        else:
            initial_side = pivot["side"]
            raw = f"{METHOD_VERSION}|{initial_side}|{_bucket(pivot['price'])}|{pivot['confirmation_timestamp'].isoformat()}|{pivot['source_timeframe']}"
            level = {"level_id": hashlib.sha256(raw.encode()).hexdigest()[:20], "side": initial_side, "low": pivot["price"] - tolerance / 2, "high": pivot["price"] + tolerance / 2, "center": pivot["price"], "first_confirmed": pivot["confirmation_timestamp"], "members": [pivot], "created_tolerance": tolerance}
            levels.append(level)
    return sorted(levels, key=lambda item: (item["first_confirmed"], item["side"], item["level_id"]))


def _closed(candles: list[dict[str, Any]], timestamp: datetime) -> list[dict[str, Any]]:
    return [c for c in candles if c["timestamp"] + EXPECTED_INTERVALS[c["interval"]] <= timestamp]


def _level_state(level: dict[str, Any], candles: list[dict[str, Any]], at: datetime) -> dict[str, Any]:
    bars = [c for c in candles if c["timestamp"] + timedelta(hours=1) <= at and c["timestamp"] >= level["first_confirmed"]]
    lifecycle = _level_events(level, bars, at)
    touches = lifecycle["touch_timestamps"]
    rejections = [item["reaction_atr"] for item in lifecycle["interactions"] if item["kind"] == "clean_rejection"]
    breaks = sum(item["kind"] == "break" for item in lifecycle["interactions"]); reclaims = sum(item["kind"] == "false_break_reclaim" for item in lifecycle["interactions"]); accepted = lifecycle["accepted"]
    eligible = len(rejections) + breaks
    hold = (len(rejections) + reclaims) / eligible if eligible else 0.0
    reaction = min((median(rejections) if rejections else 0.0) / 2.0, 1.0)
    confluence = 1.0 if len({m["source_timeframe"] for m in level["members"]}) >= 2 else .5
    completed = [item["timestamp"] for item in lifecycle["interactions"] if item["kind"] != "break"]
    last = max(completed or touches or [level["first_confirmed"]])
    recency = math.exp(-max(0.0, (at - last).total_seconds() / 86400) / 14)
    score = 100 * (.45 * hold + .20 * reaction + .20 * confluence + .15 * recency)
    band = "high" if score >= 70 and eligible >= 3 else "medium" if score >= 50 and eligible >= 2 else "low"
    role = lifecycle["role"]
    return {"touches": touches, "rejections": rejections, "breaks": breaks, "reclaims": reclaims, "accepted": accepted, "score": score, "band": band, "recency": recency, "reaction": median(rejections) if rejections else 0.0, "role": role, "last_interaction": last}


def _reliability(level: dict[str, Any], state: dict[str, Any], at: datetime) -> dict[str, Any]:
    members = sorted(level["members"], key=lambda m: (m["confirmation_timestamp"], m["pivot_id"]))
    reason = ["prior_only", "single_timeframe" if len({m["source_timeframe"] for m in members}) == 1 else "cross_timeframe_confluence"]
    if state["rejections"]: reason.append("clean_rejection_history")
    if state["reclaims"]: reason.append("false_break_reclaim_history")
    return {"schema_version": LEVEL_SCHEMA_VERSION, "method_version": METHOD_VERSION, "level_id": level["level_id"], "side": level["side"], "low": round(level["low"], 10), "high": round(level["high"], 10), "center": round(level["center"], 10), "source_timeframes": ",".join(sorted({m["source_timeframe"] for m in members})), "first_seen_at": members[0]["confirmation_timestamp"].isoformat(), "last_confirmed_at": members[-1]["confirmation_timestamp"].isoformat(), "touch_count": len(state["touches"]), "clean_rejection_count": len(state["rejections"]), "break_count": state["breaks"], "false_break_reclaim_count": state["reclaims"], "median_reaction_atr": round(state["reaction"], 8), "median_hold_hours": round((at - state["last_interaction"]).total_seconds() / 3600, 6) if state["last_interaction"] else "", "recency_score": round(state["recency"], 8), "cross_timeframe_confluence": 1.0 if len({m["source_timeframe"] for m in members}) >= 2 else .5, "reliability_score": round(state["score"], 8), "reliability_band": state["band"], "lifecycle": "accepted_beyond" if state["accepted"] else "rejected" if state["rejections"] else "touched" if state["touches"] else "active", "role": state["role"], "member_pivot_ids": ",".join(m["pivot_id"] for m in members), "member_pivot_timestamps": ",".join(m["pivot_timestamp"].isoformat() for m in members), "member_confirmation_timestamps": ",".join(m["confirmation_timestamp"].isoformat() for m in members), "reason_codes": ",".join(sorted(reason))}


def _structure(price: float, levels: list[dict[str, Any]], candles4: list[dict[str, Any]], at: datetime, pivots4: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    reliable = [x for x in levels if x["reliability_band"] in {"medium", "high"}]
    below = sorted((x for x in reliable if x.get("role") == "support" and x["low"] <= price), key=lambda x: (max(0.0, price - x["high"]), x["level_id"]))
    above = sorted((x for x in reliable if x.get("role") == "resistance" and x["high"] >= price), key=lambda x: (max(0.0, x["low"] - price), x["level_id"]))
    support, resistance = (below[0] if below else None), (above[0] if above else None)
    if not support or not resistance:
        return {"state": "insufficient", "location": "insufficient", "support": support, "resistance": resistance, "target_up": None, "target_down": None, "obstruction": "insufficient", "range_low": "", "range_high": "", "percentile": ""}
    low, high = support["center"], resistance["center"]
    percentile = (price - low) / (high - low) if high > low else .5
    location = "outside" if percentile < 0 or percentile > 1 else "lower_half" if percentile < .45 else "equilibrium_area" if percentile <= .55 else "upper_half"
    swings = sorted((pivot for pivot in (pivots4 or []) if pivot["confirmation_timestamp"] <= at), key=lambda item: item["confirmation_timestamp"])
    highs = [p["price"] for p in swings if p["side"] == "high"][-2:]; lows = [p["price"] for p in swings if p["side"] == "low"][-2:]
    if len(highs) >= 2 and len(lows) >= 2 and highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        state = "trend_up"
    elif len(highs) >= 2 and len(lows) >= 2 and highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        state = "trend_down"
    elif len(highs) >= 1 and len(lows) >= 1:
        state = "range"
    else:
        state = "transition"
    return {"state": state, "location": location, "support": support, "resistance": resistance, "target_up": resistance, "target_down": support, "obstruction": "none", "range_low": low, "range_high": high, "percentile": round(percentile * 100, 6)}


def _level_events(level: dict[str, Any], candles: list[dict[str, Any]], at: datetime) -> dict[str, Any]:
    """Resolve closed-candle level behaviour without using bars after *at*."""
    bars = [bar for bar in candles if bar["timestamp"] + timedelta(hours=1) <= at]
    touches: list[int] = []; interactions: list[dict[str, Any]] = []; active: dict[str, Any] | None = None; armed = True
    role = level.get("role") or ("support" if level["side"] == "low" else "resistance")
    for index, bar in enumerate(bars):
        if bar["high"] >= level["low"] and bar["low"] <= level["high"]:
            if not touches or index - touches[-1] >= 3:
                touches.append(index)
            armed = True
        atr = _atr(bars, index) or max(level["center"] * .001, 1e-9)
        side = "UP" if bar["close"] >= level["high"] + .10 * atr else "DOWN" if bar["close"] <= level["low"] - .10 * atr else None
        if active is None and touches and touches[-1] >= 0 and index > touches[-1] and index - touches[-1] <= 3:
            rejection_side = "UP" if role == "support" and bar["close"] >= level["center"] + .50 * atr else "DOWN" if role == "resistance" and bar["close"] <= level["center"] - .50 * atr else None
            if rejection_side:
                interactions.append({"kind": "clean_rejection", "timestamp": bar["timestamp"], "side": rejection_side, "reaction_atr": abs(bar["close"] - level["center"]) / atr}); touches[-1] = -10**9
                continue
        if active:
            prior, started = active["side"], active["index"]
            reclaimed = bar["close"] < level["center"] if prior == "UP" else bar["close"] > level["center"]
            if reclaimed and index - started <= 3:
                interactions.append({"kind": "false_break_reclaim", "timestamp": bar["timestamp"], "side": "DOWN" if prior == "UP" else "UP", "reaction_atr": abs(bar["close"] - level["center"]) / atr}); active = None
            elif index == started + 1 and side == prior:
                interactions.append({"kind": "accepted_break", "timestamp": bar["timestamp"], "side": prior, "reaction_atr": abs(bar["close"] - level["center"]) / atr}); role = "support" if prior == "UP" else "resistance"; active = None; armed = False
            elif index - started >= 3:
                active = None
        if side and armed and active is None and not (interactions and interactions[-1]["timestamp"] == bar["timestamp"] and interactions[-1]["kind"] in {"accepted_break", "false_break_reclaim"}):
            active = {"side": side, "index": index}
            interactions.append({"kind": "break", "timestamp": bar["timestamp"], "side": side, "reaction_atr": abs(bar["close"] - level["center"]) / atr})
        if touches and active is None:
            touch_index = touches[-1]
            if index > touch_index and index - touch_index <= 3:
                if role == "support" and bar["close"] >= level["center"] + .50 * atr:
                    interactions.append({"kind": "clean_rejection", "timestamp": bar["timestamp"], "side": "UP", "reaction_atr": abs(bar["close"] - level["center"]) / atr}); touches[-1] = -10**9
                elif role == "resistance" and bar["close"] <= level["center"] - .50 * atr:
                    interactions.append({"kind": "clean_rejection", "timestamp": bar["timestamp"], "side": "DOWN", "reaction_atr": abs(bar["close"] - level["center"]) / atr}); touches[-1] = -10**9
    completed = [item for item in interactions if item["kind"] != "break"]
    latest = completed[-1] if completed else None
    current = bool(latest and bars and latest["timestamp"] == bars[-1]["timestamp"])
    current_approach = bool(bars and bars[-1]["high"] >= level["low"] and bars[-1]["low"] <= level["high"])
    family = "RELIABLE_LEVEL_APPROACH" if current_approach and not current else ""
    if latest and current:
        family = {"clean_rejection": "RELIABLE_LEVEL_REJECTION", "accepted_break": "LEVEL_BREAK_ACCEPTANCE", "false_break_reclaim": "FALSE_BREAK_RECLAIM"}[latest["kind"]] + "_" + latest["side"]
    return {"touches": sum(x >= 0 for x in touches), "touch_timestamps": [bars[x]["timestamp"] for x in touches if x >= 0], "family": family, "activation": latest["side"] if latest and current else None, "rejection": latest["side"] if latest and current and latest["kind"] == "clean_rejection" else None, "break_side": active["side"] if active else None, "accepted": bool(latest and latest["kind"] == "accepted_break"), "reclaim": bool(latest and latest["kind"] == "false_break_reclaim"), "current_kind": latest["kind"] if latest and current else "", "role": role, "interactions": interactions}


def _volatility(candles: list[dict[str, Any]], at: datetime) -> dict[str, Any]:
    closed = _closed(candles, at); trs = [_tr(c, closed[i - 1] if i else None) for i, c in enumerate(closed)]
    if len(closed) < 64:
        return {"state": "insufficient", "persistence": 0, "bars_used": len(closed), "expansion_risk": "insufficient", "atr": _atr(closed, len(closed) - 1) if closed else 0}
    current = sum(trs[-4:]) / 4; reference = sum(trs[-32:]) / 32; trailing = sorted(trs[-64:]); percentile = 100 * (sum(1 for x in trailing if x <= trs[-1]) / len(trailing)); atr = sum(trs[-14:]) / 14
    jump = trs[-1] >= max(3 * atr, closed[-2]["close"] * .01)
    state = "jump_like" if jump else "compressed" if current / reference <= .75 and percentile <= 25 else "expanding" if current / reference >= 1.25 or percentile >= 75 else "ordinary"
    persistence = 1
    for earlier in reversed(trs[:-1]):
        if (state == "compressed" and earlier <= reference * .75) or (state == "expanding" and earlier >= reference * 1.25): persistence += 1
        else: break
    return {"state": state, "persistence": persistence, "bars_used": len(closed), "current_reference_ratio": round(current / reference, 8) if reference else "", "range_percentile": round(percentile, 8), "atr": atr, "expansion_risk": "high" if state in {"expanding", "jump_like"} else "medium" if state == "compressed" else "low"}


def _pressure(signal: dict[str, str], level: dict[str, Any] | None, candles1: list[dict[str, Any]], at: datetime) -> dict[str, Any]:
    bars = [c for c in candles1 if c["timestamp"] + timedelta(hours=1) <= at][-24:]
    groups: dict[str, Any] = {}
    for name in ("repeated_tests", "diminishing_rejection_distance", "close_concentration", "directional_close_imbalance", "opposing_side_failure", "rejection", "break", "closed_candle_acceptance", "false_break_reclaim", "structural_compression", "target_obstruction", "open_corridor"):
        groups[name] = "unavailable"
    if level and bars:
        touches = [b for b in bars if b["high"] >= level["low"] and b["low"] <= level["high"]]
        groups["repeated_tests"] = "present" if len(touches) >= 3 else "absent"
        reactions = [abs(b["close"] - level["center"]) / (_atr(bars, i) or 1) for i, b in enumerate(bars) if b in touches]
        groups["diminishing_rejection_distance"] = "present" if len(reactions) >= 3 and reactions[-3] > reactions[-2] > reactions[-1] else "absent"
        groups["close_concentration"] = "present" if sum(abs(bars[i]["close"] - level["center"]) <= .25 * (_atr(bars, i) or 1) for i in range(max(0, len(bars) - 5), len(bars))) >= 3 else "absent"
        changes = [b["close"] - bars[i - 1]["close"] for i, b in enumerate(bars) if i]
        groups["directional_close_imbalance"] = "present" if len(changes) >= 6 and max(sum(x > 0 for x in changes[-6:]), sum(x < 0 for x in changes[-6:])) >= 4 else "absent"
    directional: dict[str, str] = {}
    for field in MICRO_FIELDS:
        status, side = _micro_value(signal.get(field), field)
        groups[field] = status
        if side and status == "present":
            directional[field] = side
    groups["directional_microstructure"] = directional
    groups["microstructure_status"] = "unavailable" if all(groups[field] == "unavailable" for field in MICRO_FIELDS) else "available"
    return groups


def _turning_fired(signal: dict[str, str]) -> bool:
    """Reuse the existing pure turning classifier without changing it."""
    try:
        from src.feedback.turning_volatility_precursor_replay import classify_precursor_row
        classified = classify_precursor_row(signal)
        combined = classified.get("POLICY_COMBINED_PRECURSOR", {})
        return bool(isinstance(combined, dict) and combined.get("side"))
    except (KeyError, TypeError, ValueError):
        return False


def _outcomes(price: float, at: datetime, atr: float, candles15: list[dict[str, Any]], levels: list[dict[str, Any]], activation: str | None = None, target: dict[str, Any] | None = None, selected_level: dict[str, Any] | None = None, candles1: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    future = [c for c in candles15 if c["timestamp"] + timedelta(minutes=15) > at]
    result: dict[str, Any] = {}
    threshold = max(2 * atr, price * .005)
    for hours in (1, 3, 6, 12, 24):
        count = hours * 4; window = future[:count]
        contiguous = len(window) >= count and all((b["timestamp"] - a["timestamp"]).total_seconds() == 900 for a, b in zip(window, window[1:]))
        if not contiguous:
            result[f"outcome_{hours}h"] = "unresolved"; continue
        up = next((c for c in window if c["high"] - price >= threshold), None); down = next((c for c in window if price - c["low"] >= threshold), None)
        result[f"outcome_{hours}h"] = "whipsaw_both" if up and down else "large_up" if up else "large_down" if down else "balanced_no_expansion"
    ranges = [_tr(c, future[i - 1] if i else None) for i, c in enumerate(future[:4])]
    up_distance = max((c["high"] - price for c in future[:96]), default=0); down_distance = max((price - c["low"] for c in future[:96]), default=0)
    result["large_move_side"] = "UP" if up_distance >= threshold and down_distance < threshold else "DOWN" if down_distance >= threshold and up_distance < threshold else "NONE"
    side = activation if activation in {"UP", "DOWN"} else "UP" if up_distance >= threshold and down_distance < threshold else "DOWN" if down_distance >= threshold and up_distance < threshold else "NONE"
    directional_mfe = up_distance if side == "UP" else down_distance if side == "DOWN" else max(up_distance, down_distance)
    directional_mae = down_distance if side == "UP" else up_distance if side == "DOWN" else min(up_distance, down_distance)
    result["mfe_atr"] = round(directional_mfe / atr, 8) if atr else ""
    result["mae_atr"] = round(directional_mae / atr, 8) if atr else ""
    result["upward_excursion"] = round(up_distance, 8)
    result["downward_excursion"] = round(down_distance, 8)
    first = next((c for c in future[:96] if max(c["high"] - price, price - c["low"]) >= threshold), None)
    result["first_material_move_timestamp"] = first["timestamp"].isoformat() if first else ""
    if target and side == "UP":
        target_bar = next((c for c in future[:96] if c["high"] >= target["center"]), None)
    elif target and side == "DOWN":
        target_bar = next((c for c in future[:96] if c["low"] <= target["center"]), None)
    else:
        target_bar = None
    result["target_touch"] = target_bar["timestamp"].isoformat() if target_bar else "unresolved" if target else "not_available"
    result["adverse_before_target"] = bool(target_bar and ((max((price - c["low"] for c in future[:future.index(target_bar) + 1]), default=0) >= max(atr, price * .002)) if side == "UP" else (max((c["high"] - price for c in future[:future.index(target_bar) + 1]), default=0) >= max(atr, price * .002)))) if target_bar else "unresolved"
    result["whipsaw"] = any(result.get(f"outcome_{hours}h") == "whipsaw_both" for hours in (1, 3, 6, 12, 24))
    behavior_level = selected_level or target
    if not future:
        result["level_behavior"] = "unresolved"
    elif behavior_level is None:
        result["level_behavior"] = "not_tested"
    elif not candles1:
        result["level_behavior"] = "not_tested"
    else:
        future_at = min(at + timedelta(hours=24), candles1[-1]["timestamp"] + timedelta(hours=1))
        lifecycle = _level_events(behavior_level, candles1, future_at)
        recent = [item for item in lifecycle["interactions"] if item["timestamp"] + timedelta(hours=1) > at]
        kinds = {item["kind"] for item in recent}
        if "false_break_reclaim" in kinds:
            result["level_behavior"] = "false_break_reclaim"
        elif "accepted_break" in kinds:
            result["level_behavior"] = "level_break_accept"
        elif "clean_rejection" in kinds:
            result["level_behavior"] = "level_hold_reject"
        elif any(bar["high"] >= behavior_level["low"] and bar["low"] <= behavior_level["high"] for bar in future[:96]):
            result["level_behavior"] = "unresolved"
        else:
            result["level_behavior"] = "not_tested"
    result["jump_like"] = bool(ranges and ranges[0] >= max(3 * atr, price * .01))
    return result


def _episodes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []; active: dict[str, Any] | None = None
    for row in rows:
        side = row.get("large_move_side")
        if side not in {"UP", "DOWN"}:
            active = None; continue
        ts = _dt(row["event_timestamp_utc"])
        if active is None or active["direction"] != side or (ts - active["start"]).total_seconds() >= 3 * 3600:
            active = {"direction": side, "start": ts, "row": row}; result.append(active)
    return result


def _realized_inventory(candles15: list[dict[str, Any]], signal_rows: list[dict[str, str]], events: list[dict[str, Any]], horizon_bars: int = 96, performance_start: datetime | None = None, performance_end: datetime | None = None) -> list[dict[str, Any]]:
    """Discover opportunities from OHLCV, independently of signal rows."""
    ordered = sorted(candles15, key=lambda candle: candle["timestamp"]); inventory: list[dict[str, Any]] = []; last_by_side: dict[str, datetime] = {}
    event_by_signal = {str(event["signal_id"]): event for event in events}; signals = sorted(signal_rows, key=lambda row: _dt(row["timestamp_utc"]))
    for index in range(14, len(ordered)):
        anchor = ordered[index]; at = anchor["timestamp"]; atr = _atr(ordered, index - 1, 14)
        if (performance_start and at < performance_start) or (performance_end and at > performance_end):
            continue
        if not atr or index + 1 >= len(ordered):
            continue
        future = ordered[index:index + horizon_bars]
        if len(future) < horizon_bars or any((right["timestamp"] - left["timestamp"]).total_seconds() != 900 for left, right in zip(future, future[1:])):
            continue
        price = anchor["open"]; threshold = max(2 * atr, price * .005)
        up_bar = next((bar for bar in future if bar["high"] - price >= threshold), None); down_bar = next((bar for bar in future if price - bar["low"] >= threshold), None)
        if not up_bar and not down_bar:
            continue
        if up_bar and down_bar:
            direction = "BOTH"; material = min(up_bar["timestamp"], down_bar["timestamp"]); move = max(up_bar["high"] - price, price - down_bar["low"]); whipsaw = True
        elif up_bar:
            direction = "UP"; material = up_bar["timestamp"]; move = up_bar["high"] - price; whipsaw = False
        else:
            direction = "DOWN"; material = down_bar["timestamp"]; move = price - down_bar["low"]; whipsaw = False
        dedup_sides = ("UP", "DOWN") if direction == "BOTH" else (direction,)
        if any(side in last_by_side and at - last_by_side[side] < timedelta(hours=3) for side in dedup_sides):
            continue
        for side in dedup_sides:
            last_by_side[side] = at
        associated = next((row for row in reversed(signals) if (_dt(row["timestamp_utc"]) or at) <= at and at - (_dt(row["timestamp_utc"]) or at) <= timedelta(hours=3)), None)
        event = event_by_signal.get(str(associated.get("signal_id"))) if associated else None
        opportunity_id = hashlib.sha256(f"{METHOD_VERSION}|opportunity|{direction}|{at.isoformat()}".encode()).hexdigest()[:20]
        inventory.append({"opportunity_id": opportunity_id, "direction": direction, "start_timestamp_utc": at.isoformat(), "material_move_timestamp_utc": material.isoformat(), "move_size_atr": round(move / atr, 8), "jump_like": _tr(anchor, ordered[index - 1]) >= max(3 * atr, price * .01), "whipsaw": whipsaw, "signal_id": str(associated.get("signal_id")) if associated else "", "event": event, "signal": associated, "data_quality_status": "ok"})
    return inventory


def _policy_side(event: dict[str, Any], policy: str, signal: dict[str, str] | None = None) -> str | None:
    def normalize(value: Any) -> str | None:
        token = str(value or "").strip().upper()
        return {"UP": "UP", "LONG": "UP", "BUY": "UP", "BULLISH": "UP", "DOWN": "DOWN", "SHORT": "DOWN", "SELL": "DOWN", "BEARISH": "DOWN", "BOTH": "BOTH"}.get(token)
    family = set(str(event.get("event_family", "")).split("|"))
    if policy == "current_notification":
        return normalize(event.get("current_tactical_side")) if str(event.get("was_notified", "")).lower() in {"1", "true", "yes", "y"} else None
    if policy == "turning_precursor_combined" and signal:
        try:
            from src.feedback.turning_volatility_precursor_replay import classify_precursor_row
            return normalize(classify_precursor_row(signal).get("POLICY_COMBINED_PRECURSOR", {}).get("side"))
        except (KeyError, TypeError, ValueError):
            return None
    if policy == "compression_only":
        return "BOTH" if event.get("volatility_state") == "compressed" else None
    if policy == "reliable_level_pressure":
        pressure = json.loads(event.get("pressure_evidence_json") or "{}")
        activation = event.get("directional_activation")
        supports = [side for field, side in pressure.get("directional_microstructure", {}).items() if field in {"order_flow_imbalance", "aggressive_buy_ratio", "aggressive_sell_ratio", "orderbook_depth_imbalance", "cvd_slope", "cvd_price_divergence", "orderbook_bias"}]
        return activation if activation in {"UP", "DOWN"} and activation in supports and "RELIABLE_LEVEL_APPROACH" in family | {item for item in family if "REJECTION" in item or "ACCEPTANCE" in item or "RECLAIM" in item} else None
    if policy == "reliable_level_rejection" and any("RELIABLE_LEVEL_REJECTION" in item for item in family):
        return "UP" if any(item.endswith("_UP") for item in family) else "DOWN"
    if policy == "reliable_level_break_acceptance" and any("LEVEL_BREAK_ACCEPTANCE" in item for item in family):
        return "UP" if any(item.endswith("_UP") for item in family) else "DOWN"
    if policy == "false_break_reclaim" and any("FALSE_BREAK_RECLAIM" in item for item in family):
        return "UP" if any(item.endswith("_UP") for item in family) else "DOWN"
    if policy == "reliable_level_acceptance_corridor" and any("OPEN_TRAVEL_CORRIDOR" in item for item in family):
        return "UP" if any(item.endswith("_UP") for item in family) else "DOWN"
    return None


def _policy_fired(opportunity: dict[str, Any], policy: str) -> bool:
    event = opportunity.get("event") or {}; family = set(str(event.get("event_family", "")).split("|"))
    if policy == "current_notification":
        return str(event.get("was_notified", "")).lower() in {"1", "true", "yes", "y"}
    if policy == "turning_precursor_combined":
        return bool(opportunity.get("signal") and _turning_fired(opportunity["signal"]))
    if policy == "reliable_level_rejection":
        return any("RELIABLE_LEVEL_REJECTION" in item for item in family)
    if policy == "reliable_level_break_acceptance":
        return any("LEVEL_BREAK_ACCEPTANCE" in item for item in family)
    if policy == "false_break_reclaim":
        return any("FALSE_BREAK_RECLAIM" in item for item in family)
    if policy == "compression_only":
        return event.get("volatility_state") == "compressed"
    if policy == "reliable_level_pressure":
        return _policy_side(event, policy, opportunity.get("signal")) is not None
    if policy == "reliable_level_acceptance_corridor":
        return any("OPEN_TRAVEL_CORRIDOR" in item for item in family)
    return False


def _policy_metrics(opportunities: list[dict[str, Any]], policy: str, episodes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    episodes = episodes if episodes is not None else [{"event": item.get("event") or {}, "signal": item.get("signal"), "outcome": "large_" + item["direction"].lower() if item["direction"] in {"UP", "DOWN"} else "whipsaw_both", "timestamp": item["start_timestamp_utc"], "mfe": item.get("move_size_atr"), "mae": None} for item in opportunities]
    fired = [row for row in _dedup_policy_episodes(episodes, policy) if not (row.get("event") or {}).get("_context_only")]
    resolved = [row for row in fired if row.get("outcome") != "unresolved"]
    sides = {id(row): _policy_side(row["event"], policy, row.get("signal")) for row in resolved}
    correct = [row for row in resolved if sides[id(row)] in {"UP", "DOWN"} and row.get("outcome") == "large_" + str(sides[id(row)]).lower()]
    expansion = [row for row in resolved if row.get("outcome") in {"large_up", "large_down", "whipsaw_both"}]
    false = [row for row in resolved if row.get("outcome") == "balanced_no_expansion"]
    opposite = [row for row in resolved if row.get("outcome") in {"large_up", "large_down"} and row not in correct]
    matched = {row.get("opportunity_id") for row in fired if row.get("opportunity_id") and (sides.get(id(row)) == "BOTH" or row.get("opportunity_direction") == sides.get(id(row)))}
    move_opportunities = [item for item in opportunities if item.get("direction") in {"UP", "DOWN", "BOTH"}]
    leads = [row.get("lead_minutes") for row in correct if row.get("lead_minutes") is not None]
    directional = [row for row in resolved if sides[id(row)] in {"UP", "DOWN"}]
    return {"episodes": len(fired), "resolved_episodes": len(resolved), "directional_precision": round(len(correct) / len(directional), 8) if directional else None, "large_move_recall": round(len(matched) / len(move_opportunities), 8) if move_opportunities else None, "expansion_precision": round(len(expansion) / len(resolved), 8) if resolved else None, "expansion_recall": round(len(matched) / len(move_opportunities), 8) if move_opportunities else None, "false_warning_rate": round(len(false) / len(resolved), 8) if resolved else None, "opposite_move_rate": round(len(opposite) / len(directional), 8) if directional else None, "whipsaw_rate": round(sum(row.get("outcome") == "whipsaw_both" for row in resolved) / len(resolved), 8) if resolved else None, "unresolved_rate": round((len(fired) - len(resolved)) / len(fired), 8) if fired else None, "median_lead_minutes": median(leads) if leads else None, "median_favorable_excursion_atr": median([row["mfe"] for row in correct if row.get("mfe") is not None]) if correct else None, "median_adverse_excursion_atr": median([row["mae"] for row in resolved if row.get("mae") is not None]) if any(row.get("mae") is not None for row in resolved) else None, "burden_per_jst_day": round(len(fired) / max(1, len({(_dt(row["timestamp"]) + timedelta(hours=9)).date() for row in fired})), 8) if fired else 0, "denominators": {"resolved_fired_episodes": len(resolved), "directional_fired_episodes": len(directional), "independent_realized_opportunities": len(move_opportunities)}}


def _dedup_policy_episodes(episodes: list[dict[str, Any]], policy: str, separation: timedelta = timedelta(hours=3)) -> list[dict[str, Any]]:
    """Deduplicate fired snapshots by observable context transitions and separation."""
    result: list[dict[str, Any]] = []; previous: dict[str, Any] | None = None; previous_key: tuple[Any, ...] | None = None
    for row in sorted(episodes, key=lambda item: (str(item.get("timestamp", "")), str((item.get("event") or {}).get("event_id", "")))):
        side = _policy_side(row.get("event") or {}, policy, row.get("signal"))
        if not side:
            previous = None; previous_key = None; continue
        event = row.get("event") or {}; stamp = _dt(row.get("timestamp"))
        key = (side, event.get("event_family", ""), event.get("structural_state", ""), event.get("volatility_state", ""), event.get("price_location", ""))
        # Future replay outcomes and implicit resolution are deliberately excluded.
        # Boundaries are only fired-state resets, observable context transitions,
        # or the declared elapsed-time separation.
        new = previous is None or previous_key != key or stamp is None or _dt(previous.get("timestamp")) is None or stamp - _dt(previous["timestamp"]) >= separation
        if new:
            item = dict(row); item["policy_episode_id"] = hashlib.sha256(f"{METHOD_VERSION}|{policy}|{key}|{row.get('timestamp')}".encode()).hexdigest()[:20]
            result.append(item); previous = item; previous_key = key
    return result


def _split(signals: list[dict[str, str]]) -> dict[str, Any]:
    dates = sorted({(_dt(row["timestamp_utc"]) + timedelta(hours=9)).date().isoformat() for row in signals if _dt(row["timestamp_utc"])})
    if len(dates) >= 5:
        a = max(1, int(len(dates) * .6)); v = max(a + 1, int(len(dates) * .8)); return {"status": "established", "calibration": dates[:a], "validation": dates[a:v], "holdout": dates[v:]}
    if 2 <= len(dates) <= 4:
        a = max(1, int(len(dates) * .7)); return {"status": "established", "calibration": dates[:a], "validation": dates[a:], "holdout": []}
    return {"status": "not_established", "calibration": dates, "validation": [], "holdout": []}


def _policy_episodes(events: list[dict[str, Any]], signals: list[dict[str, str]], opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signal_by_id = {str(row.get("signal_id")): row for row in signals}; result = []
    for event in events:
        timestamp = _dt(event["event_timestamp_utc"]); match = next((item for item in opportunities if timestamp and _dt(item["start_timestamp_utc"]) and timedelta(0) <= _dt(item["start_timestamp_utc"]) - timestamp <= timedelta(hours=3)), None)
        outcome = event.get("outcome_6h", "unresolved")
        result.append({"event": event, "signal": signal_by_id.get(str(event.get("signal_id"))), "outcome": outcome, "timestamp": event["event_timestamp_utc"], "mfe": _num(event.get("mfe_atr")), "mae": _num(event.get("mae_atr")), "opportunity_id": match.get("opportunity_id") if match else "", "opportunity_direction": match.get("direction") if match else "", "lead_minutes": ((_dt(match["material_move_timestamp_utc"]) - timestamp).total_seconds() / 60) if match and timestamp and _dt(match["material_move_timestamp_utc"]) else None})
    return result


def _diagnose_miss(row: dict[str, Any], opportunity: dict[str, Any], current: bool, turning: bool) -> str:
    """Return one root cause only when its positive event-time predicate is unique."""
    pressure = json.loads(row.get("pressure_evidence_json") or "{}") if row else {}
    forecast = json.loads(row.get("forecast_json") or "{}") if row else {}
    family = str(row.get("event_family") or "")
    if opportunity.get("data_quality_status") != "ok" or row.get("data_quality_status") not in {"", "ok"}:
        return "data_unresolved"
    candidates: list[str] = []
    if row.get("structural_state") == "insufficient": candidates.append("structure_not_established")
    elif not row.get("nearest_support_id") and not row.get("nearest_resistance_id"): candidates.append("reliable_level_missing")
    elif row.get("level_reliability_band") == "low": candidates.append("level_reliability_miscalibrated")
    if pressure.get("rejection") == "present" and "RELIABLE_LEVEL_REJECTION" not in family: candidates.append("rejection_event_missing")
    if pressure.get("break") == "present" and pressure.get("closed_candle_acceptance") == "present" and "LEVEL_BREAK_ACCEPTANCE" not in family: candidates.append("break_acceptance_missing")
    if pressure.get("break") == "present" and pressure.get("false_break_reclaim") == "present" and "FALSE_BREAK_RECLAIM" not in family: candidates.append("false_break_reclaim_missing")
    directional = pressure.get("directional_microstructure") or {}
    pressure_setup = row.get("directional_activation") in {"UP", "DOWN"} and any(pressure.get(field) == "present" for field in ("repeated_tests", "diminishing_rejection_distance", "close_concentration", "directional_close_imbalance", "opposing_side_failure"))
    if pressure.get("microstructure_status") == "unavailable" and pressure_setup: candidates.append("pressure_or_imbalance_unavailable")
    if directional and "ORDER_FLOW_PRESSURE" not in family: candidates.append("pressure_or_imbalance_not_recognized")
    corridor_distance = _num(forecast.get("corridor_distance_atr"))
    if row.get("directional_activation") in {"UP", "DOWN"} and row.get("first_reliable_target") and corridor_distance is not None and corridor_distance >= 1.0 and row.get("intervening_obstruction") == "none" and "OPEN_TRAVEL_CORRIDOR" not in family: candidates.append("travel_corridor_not_recognized")
    if row.get("volatility_state") in {"ordinary", "compressed"} and row.get("expansion_risk") == "high": candidates.append("volatility_regime_misclassified")
    precursor = any(token in family for token in ("RELIABLE_LEVEL_REJECTION", "LEVEL_BREAK_ACCEPTANCE", "FALSE_BREAK_RECLAIM", "ORDER_FLOW_PRESSURE"))
    if precursor and not current and not turning: candidates.append("precursor_policy_too_strict")
    candidate_evidence = bool(family) or row.get("directional_activation") in {"UP", "DOWN"} or row.get("volatility_state") == "compressed" or bool(directional) or any(pressure.get(field) == "present" for field in ("repeated_tests", "diminishing_rejection_distance", "close_concentration", "directional_close_imbalance", "opposing_side_failure", "rejection", "break", "closed_candle_acceptance", "false_break_reclaim", "open_corridor"))
    clean_no_candidate = not candidates and not candidate_evidence and row.get("structural_state") not in {"", "insufficient"} and pressure.get("microstructure_status") != "unavailable" and row.get("volatility_state") not in {"", "insufficient"}
    if clean_no_candidate: candidates.append("correct_no_signal")
    return candidates[0] if len(candidates) == 1 and candidates[0] in ROOT_CAUSES else "data_unresolved"


def _gate(events: list[dict[str, Any]], split: dict[str, Any], coverage: dict[str, Any], metrics: dict[str, Any] | None = None, opportunities: list[dict[str, Any]] | None = None, episodes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    reasons = []
    if split["status"] != "established": reasons.append("validation_not_established")
    if len(split.get("validation", [])) < 3: reasons.append("validation_jst_dates_lt_3")
    validation_dates = set(split.get("validation", [])); episodes = [row for row in (episodes or [{"event": event, "timestamp": event.get("event_timestamp_utc"), "outcome": event.get("outcome_6h", "unresolved")} for event in events]) if not (row.get("event") or {}).get("_context_only")]
    v = [row for row in episodes if _dt(row.get("timestamp")) and (_dt(row["timestamp"]) + timedelta(hours=9)).date().isoformat() in validation_dates]
    validation_opportunities = [item for item in (opportunities or []) if _dt(item.get("start_timestamp_utc")) and (_dt(item["start_timestamp_utc"]) + timedelta(hours=9)).date().isoformat() in validation_dates]
    up = sum(item.get("direction") == "UP" for item in validation_opportunities); down = sum(item.get("direction") == "DOWN" for item in validation_opportunities)
    if up < 10: reasons.append("validation_up_resolved_lt_10")
    if down < 10: reasons.append("validation_down_resolved_lt_10")
    location_counts = Counter((row.get("event") or {}).get("price_location") for row in v if (row.get("event") or {}).get("price_location") not in {None, "", "insufficient"} and row.get("outcome") != "unresolved")
    if sum(value >= 10 for value in location_counts.values()) < 2: reasons.append("price_location_groups_lt_2")
    if not coverage.get("continuity_pass"): reasons.append("continuity_or_coverage_failed")
    if not validation_opportunities or not v: reasons.append("no_comparable_opportunities")
    bands = [(row.get("event") or {}).get("level_reliability_band") for row in v]
    calibration = [row for row in episodes if _dt(row.get("timestamp")) and (_dt(row["timestamp"]) + timedelta(hours=9)).date().isoformat() in set(split.get("calibration", []))]
    calibration_share = sum((row.get("event") or {}).get("level_reliability_band") in {"medium", "high"} for row in calibration) / len(calibration) if calibration else None
    validation_share = sum(band in {"medium", "high"} for band in bands) / len(bands) if bands else None
    if calibration_share is None or validation_share is None: reasons.append("level_reliability_calibration_unavailable")
    elif abs(calibration_share - validation_share) > .25: reasons.append("level_reliability_calibration_unstable")
    validation_metrics = {policy: _policy_metrics(validation_opportunities, policy, v) for policy in ("current_notification", "reliable_level_acceptance_corridor")}
    current = validation_metrics["current_notification"]; candidate = validation_metrics["reliable_level_acceptance_corridor"]
    if candidate.get("large_move_recall") is None or current.get("large_move_recall") is None or candidate.get("large_move_recall") <= current.get("large_move_recall"):
        reasons.append("primary_objective_improvement_not_established")
    if candidate.get("false_warning_rate") is not None and current.get("false_warning_rate") is not None and candidate["false_warning_rate"] > current["false_warning_rate"] + .05:
        reasons.append("false_warning_degradation")
    if candidate.get("opposite_move_rate") is not None and current.get("opposite_move_rate") is not None and candidate["opposite_move_rate"] > current["opposite_move_rate"] + .05:
        reasons.append("opposite_move_degradation")
    if validation_opportunities and max(Counter((_dt(item["start_timestamp_utc"]) + timedelta(hours=9)).date().isoformat() for item in validation_opportunities).values(), default=0) > len(validation_opportunities) * .5:
        reasons.append("single_jst_date_concentration")
    candidate_ids = {row.get("opportunity_id") for row in v if row.get("opportunity_id") and _policy_side(row.get("event") or {}, "reliable_level_acceptance_corridor", row.get("signal"))}
    current_ids = {row.get("opportunity_id") for row in v if row.get("opportunity_id") and _policy_side(row.get("event") or {}, "current_notification", row.get("signal"))}
    if len(candidate_ids - current_ids) <= 1: reasons.append("single_opportunity_dependence")
    if any((row.get("event") or {}).get("data_quality_status") != "ok" for row in v): reasons.append("validation_unresolved_data")
    return {"status": "eligible_for_next_design_proposal" if not reasons else "continue_shadow_collection" if split["status"] == "established" else "insufficient_evidence", "reasons": sorted(set(reasons)) or ["all_declared_gate_conditions_pass"], "validation_policy_metrics": validation_metrics, "validation_up_resolved": up, "validation_down_resolved": down}


def _markdown(summary: dict[str, Any]) -> str:
    lines = ["# Macro Structure / Volatility Evidence Replay", "", "## Executive result", f"- Recommendation: `{summary['recommendation_status']}`", "- Report-only; not FORMAL_GO; human-decided; no automatic order.", "", "## Structure coverage", _json(summary.get("coverage", {})), "", "## Reliable-level calibration", _json(summary.get("level_summary", {})), "", "## Midpoint / equilibrium hypothesis", "`descriptive_only` / `not_enabled_as_policy`; equilibrium proximity alone cannot create direction or expansion.", "", "## Expansion and target metrics", _json(summary.get("metrics", {})), "", "## Current notification and precursor comparison", _json(summary.get("baselines", {})), "", "## UP / DOWN and regime splits", _json(summary.get("splits", {})), "", "## Price-location splits", _json(summary.get("location_metrics", {})), "", "## Top missed large moves", _json(summary.get("missed_move_counts", {})), "", "## Top false warnings", _json(summary.get("false_warning_counts", {})), "", "## Walk-forward validation", _json(summary.get("walk_forward", {})), "", "## Proposal gate result", _json(summary.get("recommendation_gate", {})), "", "## Limitations", "Local CSV only; unresolved bars and unavailable microstructure are not favorable evidence. Evidence is descriptive and offline.", "", "## Safety boundary", SAFETY, "", ""]
    return "\n".join(lines)


def _atomic(outputs: dict[Path, bytes], replace: bool) -> None:
    targets = tuple(outputs)
    if any(path.exists() for path in targets) and not replace:
        raise ValueError("existing_output_requires_replace")
    parent = next(iter(targets)).parent; parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".macro-replay-", dir=str(parent))); moved: list[Path] = []; backups: list[tuple[Path, Path]] = []
    try:
        sources = []
        for index, (target, content) in enumerate(outputs.items()):
            source = temp / f"{index}-{target.name}"; source.write_bytes(content); sources.append((target, source))
        try:
            for target, source in sources:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    backup = target.with_name("." + target.name + ".macro-backup"); backup.unlink(missing_ok=True); target.replace(backup); backups.append((target, backup))
                source.replace(target); moved.append(target)
        except Exception as exc:
            for target in moved: target.unlink(missing_ok=True)
            for target, backup in backups:
                if backup.exists(): backup.replace(target)
            raise OSError("output_transaction_failed") from exc
        finally:
            for _, backup in backups: backup.unlink(missing_ok=True)
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def replay_macro_structure_volatility(*, signals: Path, ohlcv_15m: Path, ohlcv_1h: Path, ohlcv_4h: Path, output_events_csv: Path, output_levels_csv: Path, output_misses_csv: Path, output_json: Path, output_md: Path, cutoff_utc: str | None = None, left_window: int = 2, right_window: int = 2, replace_output: bool = False, performance_start_utc: str | None = None, performance_end_utc: str | None = None) -> dict[str, Any]:
    """Run the bounded M1 replay and atomically publish exactly five outputs."""
    signal_rows = _load_signals(signals)
    candles15, meta15 = _load_ohlcv(ohlcv_15m, "15m"); candles1, meta1 = _load_ohlcv(ohlcv_1h, "1h"); candles4, meta4 = _load_ohlcv(ohlcv_4h, "4h")
    cutoff = _dt(cutoff_utc) if cutoff_utc else None
    if cutoff: signal_rows = [row for row in signal_rows if _dt(row["timestamp_utc"]) <= cutoff]
    performance_start = _dt(performance_start_utc); performance_end = _dt(performance_end_utc)
    performance_rows = [row for row in signal_rows if str(row.get("macro_context_only", "")).lower() not in {"1", "true", "yes"} and (performance_start is None or _dt(row["timestamp_utc"]) >= performance_start) and (performance_end is None or _dt(row["timestamp_utc"]) <= performance_end)]
    pivots = confirmed_pivots(candles1, "1h", left_window, right_window) + confirmed_pivots(candles4, "4h", left_window, right_window)
    all_levels = build_levels(pivots); level_rows: dict[str, dict[str, Any]] = {}; events = []
    state_events = []
    for signal in signal_rows:
        at, price = _dt(signal["timestamp_utc"]), _num(signal["current_price"]); assert at is not None and price is not None
        known = [p for p in pivots if p["confirmation_timestamp"] <= at]; levels = build_levels(known)
        for level in levels:
            state = _level_state(level, candles1, at); level_rows[level["level_id"]] = _reliability(level, state, at); level["reliability_band"] = level_rows[level["level_id"]]["reliability_band"]; level["center"] = level_rows[level["level_id"]]["center"]
            level["role"] = state["role"]
        structure = _structure(price, levels, candles4, at, [p for p in known if p["source_timeframe"] == "4h"]); vol = _volatility(candles15, at)
        reliable = [level for level in levels if level.get("reliability_band") in {"medium", "high"}]
        nearest = min(reliable, key=lambda level: (abs(level["center"] - price), level["level_id"])) if reliable else None
        structural_direction = {"trend_up": "UP", "trend_down": "DOWN", "range": "BALANCED"}.get(structure["state"], "NONE")
        pressure = _pressure(signal, nearest, candles1, at); families = []
        lifecycle = _level_events(nearest, candles1, at) if nearest else {"family": "", "activation": None, "touches": 0, "accepted": False, "reclaim": False}
        if lifecycle["family"]:
            families.append(lifecycle["family"])
        elif nearest and lifecycle["touches"]:
            families.append("RELIABLE_LEVEL_APPROACH")
        if vol["state"] == "compressed": families.append("STRUCTURAL_COMPRESSION")
        unavailable = pressure.get("microstructure_status") == "unavailable"
        for field, side in pressure.get("directional_microstructure", {}).items():
            if field in {"order_flow_imbalance", "aggressive_buy_ratio", "aggressive_sell_ratio", "orderbook_depth_imbalance", "cvd_price_divergence", "orderbook_bias"}:
                families.append("ORDER_FLOW_PRESSURE_UP" if side == "UP" else "ORDER_FLOW_PRESSURE_DOWN")
        if pressure.get("spread_bps") == "present": families.append("LIQUIDITY_FRAGILITY")
        activation = lifecycle.get("activation")
        target = structure.get("target_up") if activation == "UP" else structure.get("target_down") if activation == "DOWN" else None
        obstruction = None
        if activation and target:
            lo, hi = sorted((price, target["center"]))
            obstruction = next((level for level in reliable if level["level_id"] != target["level_id"] and lo < level["center"] < hi), None)
            if abs(target["center"] - price) >= 1.0 * (vol.get("atr") or 0) and obstruction is None:
                families.append("OPEN_TRAVEL_CORRIDOR_UP" if activation == "UP" else "OPEN_TRAVEL_CORRIDOR_DOWN")
        if activation == "UP" and pressure.get("repeated_tests") == "present": families.append("REPEATED_TEST_PRESSURE_UP")
        if activation == "DOWN" and pressure.get("repeated_tests") == "present": families.append("REPEATED_TEST_PRESSURE_DOWN")
        pressure["rejection"] = "present" if lifecycle.get("current_kind") == "clean_rejection" else "absent"
        pressure["break"] = "present" if lifecycle.get("break_side") else "absent"
        pressure["closed_candle_acceptance"] = "present" if lifecycle.get("current_kind") == "accepted_break" else "absent"
        pressure["false_break_reclaim"] = "present" if lifecycle.get("current_kind") == "false_break_reclaim" else "absent"
        pressure["target_obstruction"] = "present" if obstruction else "absent" if target else "unavailable"
        pressure["open_corridor"] = "present" if "OPEN_TRAVEL_CORRIDOR_UP" in families or "OPEN_TRAVEL_CORRIDOR_DOWN" in families else "absent"
        outcome = _outcomes(price, at, vol.get("atr", 0), candles15, levels, activation, target, nearest, candles1)
        signal_id = str(signal.get("signal_id")); event_id = hashlib.sha256(f"{METHOD_VERSION}|{signal_id}|{at.isoformat()}".encode()).hexdigest()[:20]
        event = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "event_id": event_id, "signal_id": signal_id, "event_timestamp_utc": at.isoformat(), "event_timestamp_jst": (at + timedelta(hours=9)).isoformat(), "event_price": round(price, 10), "was_notified": str(signal.get("was_notified", "")), "current_tactical_side": str(signal.get("bias") or signal.get("primary_setup_side") or "NONE").upper(), "structural_state": structure["state"], "price_location": structure["location"], "nearest_support_id": structure["support"]["level_id"] if structure.get("support") else "", "nearest_resistance_id": structure["resistance"]["level_id"] if structure.get("resistance") else "", "next_upside_target_id": structure["target_up"]["level_id"] if structure.get("target_up") else "", "next_downside_target_id": structure["target_down"]["level_id"] if structure.get("target_down") else "", "event_family": "|".join(sorted(set(families))), "structural_direction": structural_direction, "expansion_risk": vol["expansion_risk"], "directional_activation": activation or "NONE", "first_reliable_target": target["level_id"] if target else "", "intervening_obstruction": obstruction["level_id"] if obstruction else "none" if target else "insufficient", "volatility_state": vol["state"], "volatility_persistence": vol["persistence"], "volatility_bars_used": vol["bars_used"], "level_reliability_band": level_rows.get(nearest["level_id"], {}).get("reliability_band", "") if nearest else "", "pressure_evidence_json": _json(pressure), "forecast_json": _json({"structural_direction": structural_direction, "volatility_expansion_risk": vol["expansion_risk"], "directional_activation": activation or "NONE", "current_tactical_side": str(signal.get("bias") or "NONE").upper(), "next_regime_candidate": activation or "NONE", "corridor_distance_atr": round(abs(target["center"] - price) / vol["atr"], 8) if target and vol.get("atr") else None}), "data_quality_status": "unresolved" if vol["state"] == "insufficient" or any(meta["gap_count"] for meta in (meta15, meta1, meta4)) else "ok", "reason_codes": "|".join(sorted(set(["equilibrium_descriptive_only"] + (["microstructure_unavailable"] if unavailable else []))))}
        event["_context_only"] = signal not in performance_rows
        event.update(outcome); state_events.append(event)
    state_events.sort(key=lambda row: (row["event_timestamp_utc"], row["event_id"]))
    events = [row for row in state_events if not row.get("_context_only")]
    level_list = sorted(level_rows.values(), key=lambda row: (row["first_seen_at"], row["level_id"]))
    opportunities = _realized_inventory(candles15, performance_rows, events, performance_start=performance_start, performance_end=performance_end)
    misses = []
    for opportunity in opportunities:
        row = opportunity.get("event") or {}; current = _policy_fired(opportunity, "current_notification"); turning = _policy_fired(opportunity, "turning_precursor_combined")
        if current or turning:
            continue
        root = _diagnose_miss(row, opportunity, current, turning)
        misses.append({"opportunity_id": opportunity["opportunity_id"], "direction": opportunity["direction"], "start_timestamp_utc": opportunity["start_timestamp_utc"], "material_move_timestamp_utc": opportunity["material_move_timestamp_utc"], "move_size_atr": opportunity["move_size_atr"], "structure_state": row.get("structural_state", "insufficient"), "price_location": row.get("price_location", "insufficient"), "nearest_support_id": row.get("nearest_support_id", ""), "nearest_resistance_id": row.get("nearest_resistance_id", ""), "current_notification_fired": str(current).lower(), "turning_precursor_fired": str(turning).lower(), "root_cause": root, "reason_codes": root, "data_quality_status": opportunity.get("data_quality_status", "")})
    policy_episodes = _policy_episodes(state_events, signal_rows, opportunities)
    evidence_dates = performance_rows + [{"timestamp_utc": item["start_timestamp_utc"]} for item in opportunities]
    dates = _split(evidence_dates); coverage = {"signals": len(signal_rows), "ohlcv_15m": meta15, "ohlcv_1h": meta1, "ohlcv_4h": meta4, "continuity_pass": all(not m["gap_count"] for m in (meta15, meta1, meta4))}
    notified_count = sum(str(signal.get("was_notified", "")).strip().lower() in {"1", "true", "yes", "y"} for signal in performance_rows)
    turning_count = sum(_turning_fired(signal) for signal in performance_rows)
    policies = ("current_notification", "turning_precursor_combined", "reliable_level_rejection", "reliable_level_break_acceptance", "false_break_reclaim", "compression_only", "reliable_level_pressure", "reliable_level_acceptance_corridor")
    policy_metrics = {policy: _policy_metrics(opportunities, policy, policy_episodes) for policy in policies}
    def split_metrics(key: str) -> dict[str, Any]:
        values = sorted({str((row.get("event") or {}).get(key, "insufficient")) for row in policy_episodes})
        result = {}
        for value in values:
            subset = [row for row in policy_episodes if str((row.get("event") or {}).get(key, "insufficient")) == value]
            ids = {row.get("opportunity_id") for row in subset if row.get("opportunity_id")}
            matched = [item for item in opportunities if item.get("opportunity_id") in ids]
            result[value] = {policy: _policy_metrics(matched, policy, subset) for policy in policies}
        return result
    def direction_metrics(direction: str) -> dict[str, Any]:
        subset = [row for row in policy_episodes if row.get("opportunity_direction") == direction]
        matched = [item for item in opportunities if item["direction"] == direction]
        return {policy: _policy_metrics(matched, policy, subset) for policy in policies}
    split_data = {"direction": {direction: direction_metrics(direction) for direction in ("UP", "DOWN", "BOTH")}, "regime": split_metrics("structural_state"), "volatility_state": split_metrics("volatility_state"), "reliability": split_metrics("level_reliability_band"), "price_location": split_metrics("price_location")}
    gate = _gate(events, dates, coverage, policy_metrics, opportunities, policy_episodes)
    summary = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "generated_at_utc": max((m["max_timestamp"] for m in (meta15, meta1, meta4)), default=""), "input_fingerprints": {"signals": _sha(signals), "ohlcv_15m": _sha(ohlcv_15m), "ohlcv_1h": _sha(ohlcv_1h), "ohlcv_4h": _sha(ohlcv_4h)}, "coverage": coverage, "method_parameters": {"left_window": left_window, "right_window": right_window, "cluster_tolerance": "max(0.30*ATR_confirmation,pivot_price*0.0015)", "material_move": "max(2*ATR_15M,event_price*0.005)", "jump_like": "max(3*ATR_15M,event_price*0.01)", "corridor_minimum_atr": 1.0, "policy_episode_dedup": "per-policy fired-state reset, side/family/structure/volatility/location transition, or 3h separation; future outcomes and implicit resolution excluded"}, "counts": {"signals": len(signal_rows), "events": len(events), "levels": len(level_list), "missed_moves": len(misses), "independent_opportunities": len(opportunities)}, "level_summary": dict(Counter(row["reliability_band"] for row in level_list)), "metrics": policy_metrics, "baselines": policy_metrics, "splits": split_data, "location_metrics": split_data["price_location"], "missed_move_counts": dict(Counter(row["root_cause"] for row in misses)), "false_warning_counts": {policy: metric.get("false_warning_rate") for policy, metric in policy_metrics.items()}, "walk_forward": dates, "recommendation_gate": gate, "recommendation_status": gate["status"], "missed_move_root_causes": dict(Counter(row["root_cause"] for row in misses)), "no_automatic_tuning": True, "safety_boundary": SAFETY}
    csv_bytes = _csv_bytes(events, EVENT_FIELDS); level_bytes = _csv_bytes(level_list, LEVEL_FIELDS); miss_bytes = _csv_bytes(misses, MISS_FIELDS); json_bytes = (json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(); md_bytes = _markdown(summary).encode()
    _atomic({output_events_csv: csv_bytes, output_levels_csv: level_bytes, output_misses_csv: miss_bytes, output_json: json_bytes, output_md: md_bytes}, replace_output)
    return {"ok": True, "exit_code": 0, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "counts": summary["counts"], "recommendation_status": summary["recommendation_status"]}


def _csv_bytes(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> bytes:
    from io import StringIO
    output = StringIO(); writer = csv.DictWriter(output, fieldnames=list(fields), lineterminator="\n"); writer.writeheader(); writer.writerows({field: row.get(field, "") for field in fields} for row in rows); return output.getvalue().encode()
