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
EVENT_FIELDS = ("schema_version", "method_version", "event_id", "signal_id", "event_timestamp_utc", "event_timestamp_jst", "event_price", "was_notified", "current_tactical_side", "structural_state", "price_location", "nearest_support_id", "nearest_resistance_id", "next_upside_target_id", "next_downside_target_id", "event_family", "structural_direction", "expansion_risk", "directional_activation", "first_reliable_target", "intervening_obstruction", "volatility_state", "volatility_persistence", "volatility_bars_used", "level_reliability_band", "pressure_evidence_json", "forecast_json", "outcome_1h", "outcome_3h", "outcome_6h", "outcome_12h", "outcome_24h", "mfe_atr", "mae_atr", "first_material_move_timestamp", "target_touch", "adverse_before_target", "whipsaw", "large_move_side", "jump_like", "data_quality_status", "reason_codes")
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
    center, low, high = level["center"], level["low"], level["high"]
    touches: list[datetime] = []; rejections: list[float] = []; breaks = 0; reclaims = 0; accepted = False; last_touch: datetime | None = None
    for i, bar in enumerate(bars):
        overlap = bar["high"] >= low and bar["low"] <= high
        if overlap and (last_touch is None or bar["timestamp"] - last_touch >= timedelta(hours=3)):
            touches.append(bar["timestamp"]); last_touch = bar["timestamp"]
        atr = _atr(bars, i, 14) or max(center * 0.001, 1e-9)
        upper_break = bar["close"] >= high + .10 * atr
        lower_break = bar["close"] <= low - .10 * atr
        if upper_break or lower_break:
            breaks += 1
            side = "up" if upper_break else "down"
            following = bars[i + 1:i + 3]
            if len(following) >= 2 and all((b["close"] > high if side == "up" else b["close"] < low) for b in following):
                accepted = True
            if i < len(bars) - 3 and any((b["close"] < center if side == "up" else b["close"] > center) for b in bars[i + 1:i + 4]):
                reclaims += 1
        if overlap:
            reactions = [abs(b["close"] - center) / atr for b in bars[i + 1:i + 4] if (b["close"] > center if level["side"] == "low" else b["close"] < center)]
            if reactions:
                rejections.append(max(reactions))
    eligible = len(rejections) + breaks
    hold = (len(rejections) + reclaims) / eligible if eligible else 0.0
    reaction = min((median(rejections) if rejections else 0.0) / 2.0, 1.0)
    confluence = 1.0 if len({m["source_timeframe"] for m in level["members"]}) >= 2 else .5
    last = max(touches) if touches else level["first_confirmed"]
    recency = math.exp(-max(0.0, (at - last).total_seconds() / 86400) / 14)
    score = 100 * (.45 * hold + .20 * reaction + .20 * confluence + .15 * recency)
    band = "high" if score >= 70 and eligible >= 3 else "medium" if score >= 50 and eligible >= 2 else "low"
    role = "support" if level["side"] == "low" or (accepted and level["side"] == "high") else "resistance"
    return {"touches": touches, "rejections": rejections, "breaks": breaks, "reclaims": reclaims, "accepted": accepted, "score": score, "band": band, "recency": recency, "reaction": median(rejections) if rejections else 0.0, "role": role, "last_interaction": last}


def _reliability(level: dict[str, Any], state: dict[str, Any], at: datetime) -> dict[str, Any]:
    members = sorted(level["members"], key=lambda m: (m["confirmation_timestamp"], m["pivot_id"]))
    reason = ["prior_only", "single_timeframe" if len({m["source_timeframe"] for m in members}) == 1 else "cross_timeframe_confluence"]
    if state["rejections"]: reason.append("clean_rejection_history")
    if state["reclaims"]: reason.append("false_break_reclaim_history")
    return {"schema_version": LEVEL_SCHEMA_VERSION, "method_version": METHOD_VERSION, "level_id": level["level_id"], "side": level["side"], "low": round(level["low"], 10), "high": round(level["high"], 10), "center": round(level["center"], 10), "source_timeframes": ",".join(sorted({m["source_timeframe"] for m in members})), "first_seen_at": members[0]["confirmation_timestamp"].isoformat(), "last_confirmed_at": members[-1]["confirmation_timestamp"].isoformat(), "touch_count": len(state["touches"]), "clean_rejection_count": len(state["rejections"]), "break_count": state["breaks"], "false_break_reclaim_count": state["reclaims"], "median_reaction_atr": round(state["reaction"], 8), "median_hold_hours": round((at - state["last_interaction"]).total_seconds() / 3600, 6) if state["last_interaction"] else "", "recency_score": round(state["recency"], 8), "cross_timeframe_confluence": 1.0 if len({m["source_timeframe"] for m in members}) >= 2 else .5, "reliability_score": round(state["score"], 8), "reliability_band": state["band"], "lifecycle": "accepted_beyond" if state["accepted"] else "rejected" if state["rejections"] else "touched" if state["touches"] else "active", "role": state["role"], "member_pivot_ids": ",".join(m["pivot_id"] for m in members), "member_pivot_timestamps": ",".join(m["pivot_timestamp"].isoformat() for m in members), "member_confirmation_timestamps": ",".join(m["confirmation_timestamp"].isoformat() for m in members), "reason_codes": ",".join(sorted(reason))}


def _structure(price: float, levels: list[dict[str, Any]], candles4: list[dict[str, Any]], at: datetime) -> dict[str, Any]:
    reliable = [x for x in levels if x["reliability_band"] in {"medium", "high"}]
    below = sorted((x for x in reliable if x["center"] < price), key=lambda x: (price - x["center"], x["level_id"]))
    above = sorted((x for x in reliable if x["center"] > price), key=lambda x: (x["center"] - price, x["level_id"]))
    support, resistance = (below[0] if below else None), (above[0] if above else None)
    if not support or not resistance:
        return {"state": "insufficient", "location": "insufficient", "support": support, "resistance": resistance, "target_up": None, "target_down": None, "obstruction": "insufficient", "range_low": "", "range_high": "", "percentile": ""}
    low, high = support["center"], resistance["center"]
    percentile = (price - low) / (high - low) if high > low else .5
    location = "outside" if percentile < 0 or percentile > 1 else "lower_half" if percentile < .45 else "equilibrium_area" if percentile <= .55 else "upper_half"
    recent4 = [c for c in candles4 if c["timestamp"] + timedelta(hours=4) <= at]
    highs = [c["high"] for c in recent4[-5:]]; lows = [c["low"] for c in recent4[-5:]]
    state = "range"
    if len(highs) >= 2 and len(lows) >= 2:
        state = "trend_up" if highs[-1] > highs[0] and lows[-1] > lows[0] else "trend_down" if highs[-1] < highs[0] and lows[-1] < lows[0] else "range"
    return {"state": state, "location": location, "support": support, "resistance": resistance, "target_up": above[1] if len(above) > 1 else None, "target_down": below[1] if len(below) > 1 else None, "obstruction": "none" if (above and below) else "insufficient", "range_low": low, "range_high": high, "percentile": round(percentile * 100, 6)}


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
        groups["close_concentration"] = "present" if sum(abs(b["close"] - level["center"]) <= .25 * (_atr(bars, i) or 1) for i, b in enumerate(bars[-5:])) >= 3 else "absent"
        changes = [b["close"] - bars[i - 1]["close"] for i, b in enumerate(bars) if i]
        groups["directional_close_imbalance"] = "present" if len(changes) >= 6 and max(sum(x > 0 for x in changes[-6:]), sum(x < 0 for x in changes[-6:])) >= 4 else "absent"
    for field in MICRO_FIELDS:
        value = str(signal.get(field) or "").strip()
        groups[field] = "unavailable" if not value else "present"
    return groups


def _turning_fired(signal: dict[str, str]) -> bool:
    """Reuse the existing pure turning classifier without changing it."""
    try:
        from src.feedback.turning_volatility_precursor_replay import classify_precursor_row
        classified = classify_precursor_row(signal)
        return any(bool(item.get("fired")) for item in classified.values() if isinstance(item, dict))
    except (KeyError, TypeError, ValueError):
        return False


def _outcomes(price: float, at: datetime, atr: float, candles15: list[dict[str, Any]], levels: list[dict[str, Any]]) -> dict[str, Any]:
    future = [c for c in candles15 if c["timestamp"] > at]
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
    result["mfe_atr"] = round(max(up_distance, down_distance) / atr, 8) if atr else ""
    result["mae_atr"] = ""
    result["first_material_move_timestamp"] = next((c["timestamp"].isoformat() for c in future[:96] if max(c["high"] - price, price - c["low"]) >= threshold), "")
    result["target_touch"] = "unresolved"
    result["adverse_before_target"] = "unresolved"
    result["whipsaw"] = result.get("outcome_12h") == "whipsaw_both"
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


def _split(signals: list[dict[str, str]]) -> dict[str, Any]:
    dates = sorted({_dt(row["timestamp_utc"]).date().isoformat() for row in signals if _dt(row["timestamp_utc"])})
    if len(dates) >= 5:
        a = max(1, int(len(dates) * .6)); v = max(a + 1, int(len(dates) * .8)); return {"status": "established", "calibration": dates[:a], "validation": dates[a:v], "holdout": dates[v:]}
    if 2 <= len(dates) <= 4:
        a = max(1, int(len(dates) * .7)); return {"status": "established", "calibration": dates[:a], "validation": dates[a:], "holdout": []}
    return {"status": "not_established", "calibration": dates, "validation": [], "holdout": []}


def _gate(events: list[dict[str, Any]], split: dict[str, Any], coverage: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    if split["status"] != "established": reasons.append("validation_not_established")
    validation_dates = set(split.get("validation", [])); v = [e for e in events if e["event_timestamp_utc"][:10] in validation_dates]
    if sum(e.get("outcome_6h") in {"large_up", "whipsaw_both"} for e in v) < 10: reasons.append("validation_up_resolved_lt_10")
    if sum(e.get("outcome_6h") in {"large_down", "whipsaw_both"} for e in v) < 10: reasons.append("validation_down_resolved_lt_10")
    if not coverage.get("continuity_pass"): reasons.append("continuity_or_coverage_failed")
    return {"status": "eligible_for_next_design_proposal" if not reasons else "continue_shadow_collection" if split["status"] == "established" else "insufficient_evidence", "reasons": reasons or ["all_declared_gate_conditions_pass"]}


def _markdown(summary: dict[str, Any]) -> str:
    lines = ["# Macro Structure / Volatility Evidence Replay", "", "## Executive result", f"- Recommendation: `{summary['recommendation_status']}`", "- Report-only; not FORMAL_GO; human-decided; no automatic order.", "", "## Structure coverage", _json(summary.get("coverage", {})), "", "## Reliable-level calibration", _json(summary.get("level_summary", {})), "", "## Midpoint / equilibrium hypothesis", "`descriptive_only` / `not_enabled_as_policy`; equilibrium proximity alone cannot create direction or expansion.", "", "## Expansion and target metrics", _json(summary.get("metrics", {})), "", "## Current notification and precursor comparison", _json(summary.get("baselines", {})), "", "## UP / DOWN and regime splits", _json(summary.get("splits", {})), "", "## Price-location splits", _json(summary.get("location_metrics", {})), "", "## Top missed large moves", _json(summary.get("missed_move_counts", {})), "", "## Walk-forward validation", _json(summary.get("walk_forward", {})), "", "## Proposal gate result", _json(summary.get("recommendation_gate", {})), "", "## Limitations", "Local CSV only; unresolved bars and unavailable microstructure are not favorable evidence. Evidence is descriptive and offline.", "", "## Safety boundary", SAFETY, "", ""]
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


def replay_macro_structure_volatility(*, signals: Path, ohlcv_15m: Path, ohlcv_1h: Path, ohlcv_4h: Path, output_events_csv: Path, output_levels_csv: Path, output_misses_csv: Path, output_json: Path, output_md: Path, cutoff_utc: str | None = None, left_window: int = 2, right_window: int = 2, replace_output: bool = False) -> dict[str, Any]:
    """Run the bounded M1 replay and atomically publish exactly five outputs."""
    signal_rows = _load_signals(signals)
    candles15, meta15 = _load_ohlcv(ohlcv_15m, "15m"); candles1, meta1 = _load_ohlcv(ohlcv_1h, "1h"); candles4, meta4 = _load_ohlcv(ohlcv_4h, "4h")
    cutoff = _dt(cutoff_utc) if cutoff_utc else None
    if cutoff: signal_rows = [row for row in signal_rows if _dt(row["timestamp_utc"]) <= cutoff]
    pivots = confirmed_pivots(candles1, "1h", left_window, right_window) + confirmed_pivots(candles4, "4h", left_window, right_window)
    all_levels = build_levels(pivots); level_rows: dict[str, dict[str, Any]] = {}; events = []
    for signal in signal_rows:
        at, price = _dt(signal["timestamp_utc"]), _num(signal["current_price"]); assert at is not None and price is not None
        known = [p for p in pivots if p["confirmation_timestamp"] <= at]; levels = build_levels(known)
        for level in levels:
            state = _level_state(level, candles1, at); level_rows[level["level_id"]] = _reliability(level, state, at); level["reliability_band"] = level_rows[level["level_id"]]["reliability_band"]; level["center"] = level_rows[level["level_id"]]["center"]
        structure = _structure(price, levels, candles4, at); vol = _volatility(candles15, at); target = structure.get("target_up") or structure.get("target_down"); nearest = structure.get("support") or structure.get("resistance")
        structural_direction = {"trend_up": "UP", "trend_down": "DOWN", "range": "BALANCED"}.get(structure["state"], "NONE")
        pressure = _pressure(signal, nearest, candles1, at); families = []
        if nearest: families.append("RELIABLE_LEVEL_APPROACH")
        if nearest and structure["location"] in {"lower_half", "outside"}: families.append("RELIABLE_LEVEL_REJECTION_UP")
        if nearest and structure["location"] in {"upper_half", "outside"}: families.append("RELIABLE_LEVEL_REJECTION_DOWN")
        if vol["state"] == "compressed": families.append("STRUCTURAL_COMPRESSION")
        unavailable = all(pressure.get(field) == "unavailable" for field in MICRO_FIELDS)
        if unavailable: pressure["microstructure_status"] = "unavailable"
        else:
            if pressure.get("order_flow_imbalance") == "present": families.append("ORDER_FLOW_PRESSURE_UP" if (_num(signal.get("order_flow_imbalance")) or 0) > 0 else "ORDER_FLOW_PRESSURE_DOWN")
            if pressure.get("spread_bps") == "present": families.append("LIQUIDITY_FRAGILITY")
        activation = "NONE"; direction = "NONE"
        token_text = " ".join(str(signal.get(k, "")) for k in ("market_map_flags", "warning_flags", "risk_flags", "primary_setup_reason", "level_flip_state", "failed_breakout_state")).lower()
        if "rejection" in token_text:
            activation = "UP" if "support" in token_text or "long" in token_text else "DOWN"; direction = activation; families.append("RELIABLE_LEVEL_REJECTION_UP" if activation == "UP" else "RELIABLE_LEVEL_REJECTION_DOWN")
        elif "accept" in token_text or "break" in token_text:
            activation = "UP" if "up" in token_text or "long" in token_text else "DOWN"; direction = activation; families.append("LEVEL_BREAK_ACCEPTANCE_UP" if activation == "UP" else "LEVEL_BREAK_ACCEPTANCE_DOWN")
        elif "reclaim" in token_text or "failed" in token_text:
            activation = "UP" if "up" in token_text or "long" in token_text else "DOWN"; direction = activation; families.append("FALSE_BREAK_RECLAIM_UP" if activation == "UP" else "FALSE_BREAK_RECLAIM_DOWN")
        if direction and target and vol["state"] != "insufficient" and abs(target["center"] - price) >= max(vol.get("atr", 0), price * .001):
            families.append("OPEN_TRAVEL_CORRIDOR_UP" if direction == "UP" else "OPEN_TRAVEL_CORRIDOR_DOWN")
        if direction == "UP" and pressure.get("repeated_tests") == "present": families.append("REPEATED_TEST_PRESSURE_UP")
        if direction == "DOWN" and pressure.get("repeated_tests") == "present": families.append("REPEATED_TEST_PRESSURE_DOWN")
        outcome = _outcomes(price, at, vol.get("atr", 0), candles15, levels)
        signal_id = str(signal.get("signal_id")); event_id = hashlib.sha256(f"{METHOD_VERSION}|{signal_id}|{at.isoformat()}".encode()).hexdigest()[:20]
        event = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "event_id": event_id, "signal_id": signal_id, "event_timestamp_utc": at.isoformat(), "event_timestamp_jst": (at + timedelta(hours=9)).isoformat(), "event_price": round(price, 10), "was_notified": str(signal.get("was_notified", "")), "current_tactical_side": str(signal.get("bias") or signal.get("primary_setup_side") or "NONE").upper(), "structural_state": structure["state"], "price_location": structure["location"], "nearest_support_id": structure["support"]["level_id"] if structure.get("support") else "", "nearest_resistance_id": structure["resistance"]["level_id"] if structure.get("resistance") else "", "next_upside_target_id": structure["target_up"]["level_id"] if structure.get("target_up") else "", "next_downside_target_id": structure["target_down"]["level_id"] if structure.get("target_down") else "", "event_family": "|".join(sorted(set(families))), "structural_direction": structural_direction, "expansion_risk": vol["expansion_risk"], "directional_activation": activation, "first_reliable_target": target["level_id"] if target else "", "intervening_obstruction": structure["obstruction"], "volatility_state": vol["state"], "volatility_persistence": vol["persistence"], "volatility_bars_used": vol["bars_used"], "level_reliability_band": level_rows.get(nearest["level_id"], {}).get("reliability_band", "") if nearest else "", "pressure_evidence_json": _json(pressure), "forecast_json": _json({"structural_direction": structural_direction, "volatility_expansion_risk": vol["expansion_risk"], "directional_activation": activation, "current_tactical_side": str(signal.get("bias") or "NONE").upper(), "next_regime_candidate": direction if activation != "NONE" else "NONE"}), "data_quality_status": "unresolved" if vol["state"] == "insufficient" or any(meta["gap_count"] for meta in (meta15, meta1, meta4)) else "ok", "reason_codes": "|".join(sorted(set(["equilibrium_descriptive_only"] + (["microstructure_unavailable"] if unavailable else []))))}
        event.update(outcome); events.append(event)
    events.sort(key=lambda row: (row["event_timestamp_utc"], row["event_id"]))
    level_list = sorted(level_rows.values(), key=lambda row: (row["first_seen_at"], row["level_id"]))
    episodes = _episodes(events); misses = []
    for episode in episodes:
        row = episode["row"]; fired = bool(row.get("event_family")); root = "correct_no_signal" if fired else "reliable_level_missing" if not row.get("nearest_support_id") and not row.get("nearest_resistance_id") else "volatility_regime_misclassified" if row.get("volatility_state") == "insufficient" else "precursor_policy_too_strict"
        misses.append({"opportunity_id": hashlib.sha256(f"{episode['direction']}|{episode['start'].isoformat()}".encode()).hexdigest()[:20], "direction": episode["direction"], "start_timestamp_utc": episode["start"].isoformat(), "material_move_timestamp_utc": "", "move_size_atr": "", "structure_state": row.get("structural_state", ""), "price_location": row.get("price_location", ""), "nearest_support_id": row.get("nearest_support_id", ""), "nearest_resistance_id": row.get("nearest_resistance_id", ""), "current_notification_fired": str(row.get("was_notified", "")), "turning_precursor_fired": "false", "root_cause": root, "reason_codes": root, "data_quality_status": row.get("data_quality_status", "")})
    dates = _split(signal_rows); coverage = {"signals": len(signal_rows), "ohlcv_15m": meta15, "ohlcv_1h": meta1, "ohlcv_4h": meta4, "continuity_pass": all(not m["gap_count"] for m in (meta15, meta1, meta4))}
    notified_count = sum(str(signal.get("was_notified", "")).strip().lower() in {"1", "true", "yes", "y"} for signal in signal_rows)
    turning_count = sum(_turning_fired(signal) for signal in signal_rows)
    gate = _gate(events, dates, coverage)
    summary = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "generated_at_utc": max((m["max_timestamp"] for m in (meta15, meta1, meta4)), default=""), "input_fingerprints": {"signals": _sha(signals), "ohlcv_15m": _sha(ohlcv_15m), "ohlcv_1h": _sha(ohlcv_1h), "ohlcv_4h": _sha(ohlcv_4h)}, "coverage": coverage, "method_parameters": {"left_window": left_window, "right_window": right_window, "cluster_tolerance": "max(0.30*ATR_confirmation,pivot_price*0.0015)", "material_move": "max(2*ATR_15M,event_price*0.005)", "jump_like": "max(3*ATR_15M,event_price*0.01)"}, "counts": {"signals": len(signal_rows), "events": len(events), "levels": len(level_list), "missed_moves": len(misses), "independent_opportunities": len(episodes)}, "level_summary": dict(Counter(row["reliability_band"] for row in level_list)), "metrics": {"large_move_up": sum(row.get("large_move_side") == "UP" for row in events), "large_move_down": sum(row.get("large_move_side") == "DOWN" for row in events), "jump_like": sum(bool(row.get("jump_like")) for row in events)}, "baselines": {"current_notification": notified_count, "current_turning_precursor_combined": turning_count, "reliable_level_rejection": sum("RELIABLE_LEVEL_REJECTION" in row.get("event_family", "") for row in events), "reliable_level_break_acceptance": sum("LEVEL_BREAK_ACCEPTANCE" in row.get("event_family", "") for row in events), "false_break_reclaim": sum("FALSE_BREAK_RECLAIM" in row.get("event_family", "") for row in events), "compression_only_diagnostic": sum(row.get("volatility_state") == "compressed" for row in events), "compression_only_preferred": False}, "walk_forward": dates, "recommendation_gate": gate, "recommendation_status": gate["status"], "missed_move_root_causes": dict(Counter(row["root_cause"] for row in misses)), "no_automatic_tuning": True, "safety_boundary": SAFETY}
    csv_bytes = _csv_bytes(events, EVENT_FIELDS); level_bytes = _csv_bytes(level_list, LEVEL_FIELDS); miss_bytes = _csv_bytes(misses, MISS_FIELDS); json_bytes = (json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(); md_bytes = _markdown(summary).encode()
    _atomic({output_events_csv: csv_bytes, output_levels_csv: level_bytes, output_misses_csv: miss_bytes, output_json: json_bytes, output_md: md_bytes}, replace_output)
    return {"ok": True, "exit_code": 0, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "counts": summary["counts"], "recommendation_status": summary["recommendation_status"]}


def _csv_bytes(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> bytes:
    from io import StringIO
    output = StringIO(); writer = csv.DictWriter(output, fieldnames=list(fields), lineterminator="\n"); writer.writeheader(); writer.writerows({field: row.get(field, "") for field in fields} for row in rows); return output.getvalue().encode()
