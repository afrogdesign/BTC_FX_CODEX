"""Pure report-only side-aware multi-timeframe operator action evaluation."""
from __future__ import annotations

import json
from typing import Any


SCHEMA_VERSION = "side_aware_mtf_action.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
SIDES = ("long", "short")


def _tokens(value: Any) -> set[str]:
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return {str(item).strip().strip("'\"").lower() for item in parsed if str(item).strip()}
            except json.JSONDecodeError:
                pass
        value = text.replace("[", "").replace("]", "")
    if isinstance(value, list):
        return {str(item).strip().strip("'\"").lower() for item in value if str(item).strip()}
    if isinstance(value, str):
        return {item.strip().strip("'\"").lower() for item in value.replace("|", ",").split(",") if item.strip()}
    return set()


def _number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed and abs(parsed) != float("inf") else None


def _plan(value: Any) -> dict[str, Any] | None:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return None
    if not isinstance(value, dict) or not isinstance(value.get("side_plans"), dict):
        return None
    return value


def _matches_side(value: Any, side: str) -> bool:
    terms = {
        "long": {"long", "buy", "up", "early_up", "confirmed_up"},
        "short": {"short", "sell", "down", "early_down", "confirmed_down"},
    }[side]
    semantic = {
        "long": {"resistance_to_support_flip", "resistance_to_support_confirmed", "resistance_to_support_retest_confirmed", "trend_flip_early_up", "trend_flip_confirmed_up", "failed_breakout_up_reversal", "major_support_rejection"},
        "short": {"support_to_resistance_flip", "support_to_resistance_confirmed", "support_to_resistance_retest_confirmed", "trend_flip_early_down", "trend_flip_confirmed_down", "failed_breakout_down_reversal", "major_resistance_rejection"},
    }
    return bool(_tokens(value) & (terms | semantic[side]))


def _progress(side: str, plan: dict[str, Any], current_price: float | None) -> str:
    entry, tp1 = _number(plan.get("entry_mid")), _number(plan.get("tp1"))
    if entry is None or tp1 is None or current_price is None:
        return "unknown"
    denominator = (tp1 - entry) if side == "long" else (entry - tp1)
    numerator = (current_price - entry) if side == "long" else (entry - current_price)
    if denominator <= 0:
        return "unknown"
    ratio = round(numerator / denominator, 2)
    if ratio >= 1:
        return "tp1_reached_no_chase"
    if ratio >= .70:
        return "late_no_chase"
    return "not_late"


def _side_result(side: str, current: dict[str, Any], plan: dict[str, Any], global_fatal: bool, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    other = "short" if side == "long" else "long"
    flags = _tokens(current.get("no_trade_flags")) | _tokens(current.get("risk_flags"))
    setup_side = str(current.get("primary_setup_side", "")).strip().lower()
    setup_reason = str(current.get("primary_setup_reason", "")).strip().lower()
    readiness_only = any(token in setup_reason for token in ("confidence_below_min", "setup_not_ready", "entry_zone_not_reached", "near_entry_zone_waiting_trigger", "rr_below_min"))
    setup_invalid = setup_side == side and str(current.get("primary_setup_status", "")).strip().lower() in {"invalid", "expired"} and not readiness_only
    opposite_invalid = setup_side == other and str(current.get("primary_setup_status", "")).strip().lower() in {"invalid", "expired"} and not readiness_only
    market_status = str(plan.get("market_entry_status", "")).strip().lower()
    limit_status = str(plan.get("limit_entry_status", "")).strip().lower()
    counter_status = str(plan.get("counter_scalp_status", "")).strip().lower()
    supported = any(value in {"allowed", "conditional"} for value in (market_status, limit_status, counter_status))
    price = _number(current.get("current_price"))
    stop = _number(plan.get("stop_loss"))
    crossed = bool(stop is not None and price is not None and ((side == "long" and price <= stop) or (side == "short" and price >= stop)))
    side_wait = f"{side}_at_major_resistance_wait_only" in flags or f"{side}_at_major_support_wait_only" in flags
    signals_15m, signals_1h = current.get("signals_15m"), current.get("signals_1h")
    match_15m, match_1h = _matches_side(signals_15m, side), _matches_side(signals_1h, side)
    transition = any(_matches_side(current.get(key), side) for key in ("transition_direction", "trend_flip_state", "level_flip_state", "failed_breakout_state", "market_map_primary_state", "market_map_flags"))
    in_zone = str(plan.get("zone_position", "")).strip().lower() == "inside_zone"
    next_condition = bool(str(plan.get("next_condition", "")).strip())
    zone_activation = supported and in_zone and next_condition
    previous_cross = False
    if isinstance(previous, dict):
        prior_plan = _plan(previous.get("active_trade_plan"))
        prior_side = (prior_plan or {}).get("side_plans", {}).get(other) if prior_plan else None
        prior_price, current_price = _number(previous.get("current_price")), _number(current.get("current_price"))
        prior_stop = _number(prior_side.get("stop_loss")) if isinstance(prior_side, dict) else None
        if prior_price is not None and current_price is not None and prior_stop is not None:
            previous_cross = (side == "short" and prior_price > prior_stop >= current_price) or (side == "long" and prior_price < prior_stop <= current_price)
    reasons: list[str] = []
    fresh_trigger = bool(match_15m or previous_cross)
    if global_fatal:
        reasons.append("global_fatal")
        action, state = "STOP_OR_EXIT", "invalidated"
    elif crossed:
        reasons.append("own_invalidation_crossed")
        action, state = "STOP_OR_EXIT", "invalidated"
    elif setup_invalid:
        reasons.append("own_primary_setup_invalid")
        action, state = "STOP_OR_EXIT", "invalidated"
    elif side_wait and setup_side == side and not fresh_trigger:
        reasons.append("side_wait_only")
        action, state = "STOP_OR_EXIT", "invalidated"
    elif str(current.get("trade_execution_gate", "")).strip().lower() == "pass" and setup_side == side and market_status == "allowed":
        reasons.append("existing_formal_gate_pass")
        action, state = "A_FORMAL", "triggered"
    elif supported:
        activation = zone_activation or previous_cross or match_15m or match_1h or transition or opposite_invalid
        if activation:
            reasons.append("previous_opposite_stop_crossed" if previous_cross else "opposite_thesis_invalid" if opposite_invalid else "zone_plan_activation" if zone_activation else "timeframe_or_transition_support")
            action = "B_CHECK_15M"
            state = "follow_through" if match_15m and match_1h else "triggered" if match_15m or previous_cross else "armed"
        else:
            reasons.append("plan_zone_watch")
            action, state = "C_WATCH_ZONE", "watch"
        if side_wait:
            reasons.append("side_wait_only")
            if not fresh_trigger and counter_status != "conditional":
                action, state = "C_WATCH_ZONE", "watch"
            elif action == "C_WATCH_ZONE":
                state = "watch"
    else:
        action, state = "NONE", "dormant"
        reasons.append("no_existing_side_plan")
    chase = _progress(side, plan, price)
    if action in {"A_FORMAL", "B_CHECK_15M"} and chase in {"late_no_chase", "tp1_reached_no_chase"}:
        state = "late"
        reasons.append(chase)
    trigger_strength = 2 if match_15m and match_1h else 1 if (previous_cross or match_15m) else 0
    return {
        "action_class": action, "state": state, "plan_support": supported,
        "zone": {"low": plan.get("entry_zone_low", ""), "high": plan.get("entry_zone_high", ""), "mid": plan.get("entry_mid", "")},
        "invalidation": plan.get("stop_loss", ""), "tp1": plan.get("tp1", ""), "tp2": plan.get("tp2", ""),
        "next_condition": plan.get("next_condition", ""), "chase_status": chase, "trigger_strength": trigger_strength, "reason_codes": reasons,
    }


def _empty(signal_id: Any = "") -> dict[str, Any]:
    side = {"action_class": "NONE", "state": "dormant", "plan_support": False, "zone": {}, "invalidation": "", "tp1": "", "tp2": "", "next_condition": "", "chase_status": "unknown", "reason_codes": ["malformed_active_plan"]}
    return {"schema_version": SCHEMA_VERSION, "present": False, "signal_id": signal_id or "", "structural_context": {}, "tactical_context": {}, "execution_context": {"primary_side": "", "primary_action_class": "NONE", "primary_state": "dormant", "headline": "判定材料不足", "next_condition": "", "chase_status": "unknown", "reason_codes": ["malformed_active_plan"]}, "long": dict(side), "short": dict(side), "safety_boundary": SAFETY}


def evaluate_side_aware_mtf_action(current: dict, previous: dict | None = None) -> dict:
    """Classify existing Long and Short plans without changing formal execution semantics."""
    if not isinstance(current, dict):
        return _empty()
    active_plan = _plan(current.get("active_trade_plan"))
    if active_plan is None:
        return _empty(current.get("signal_id"))
    side_plans = active_plan["side_plans"]
    if any(not isinstance(side_plans.get(side), dict) for side in SIDES):
        return _empty(current.get("signal_id"))
    flags = _tokens(current.get("no_trade_flags")) | _tokens(current.get("risk_flags"))
    data_quality = str(current.get("data_quality_flag", "")).strip().lower()
    global_fatal = data_quality in {"invalid", "failed", "error"} or "atr_extreme" in flags or "funding_prohibited" in flags or {"funding_prohibited_long", "funding_prohibited_short"}.issubset(flags)
    long = _side_result("long", current, side_plans["long"], global_fatal, previous=previous)
    short = _side_result("short", current, side_plans["short"], global_fatal, previous=previous)
    previous_plan = _plan(previous.get("active_trade_plan")) if isinstance(previous, dict) else None
    if previous_plan is not None:
        for side, value in (("long", long), ("short", short)):
            prior_side_plan = previous_plan["side_plans"].get(side)
            if isinstance(prior_side_plan, dict):
                prior_chase = _progress(side, prior_side_plan, _number(current.get("current_price")))
                if prior_chase in {"late_no_chase", "tp1_reached_no_chase"}:
                    value["chase_status"] = prior_chase
                    if value["action_class"] in {"A_FORMAL", "B_CHECK_15M"}:
                        value["state"] = "late"
                    value["reason_codes"].append(prior_chase)
    priority = {"A_FORMAL": 5, "B_CHECK_15M": 4, "C_WATCH_ZONE": 3, "STOP_OR_EXIT": 2, "NONE": 1}
    state_priority = {"follow_through": 5, "triggered": 4, "late": 3, "armed": 2, "watch": 1, "invalidated": 0, "dormant": 0}
    candidates = [(side, value) for side, value in (("long", long), ("short", short))]
    primary_side, primary = max(candidates, key=lambda item: (priority[item[1]["action_class"]], int(item[1].get("trigger_strength", 0)), state_priority.get(item[1]["state"], 0), int(item[1]["plan_support"]), item[0] == "short"))
    if primary["action_class"] in {"NONE", "STOP_OR_EXIT"}:
        primary_side = ""
    primary_chase = primary["chase_status"] if primary_side else "unknown"
    headline = "判定材料不足" if not primary_side else f"{primary_side.upper()} {primary['action_class']}"
    if primary_side and primary_chase in {"late_no_chase", "tp1_reached_no_chase"}:
        headline += " / 追いかけ禁止"
    return {
        "schema_version": SCHEMA_VERSION, "present": True, "signal_id": current.get("signal_id", ""),
        "structural_context": {key: current.get(key, "") for key in ("signals_4h", "long_display_score", "short_display_score", "bias", "market_regime", "phase")},
        "tactical_context": {key: current.get(key, "") for key in ("signals_1h", "market_map_primary_state", "transition_direction", "trend_flip_state", "level_flip_state", "failed_breakout_state")},
        "execution_context": {"signals_15m": current.get("signals_15m", ""), "current_price": current.get("current_price", ""), "primary_side": primary_side, "primary_action_class": primary["action_class"] if primary_side else "NONE", "primary_state": primary["state"] if primary_side else "dormant", "headline": headline, "next_condition": primary.get("next_condition", "") if primary_side else "", "chase_status": primary_chase, "reason_codes": primary.get("reason_codes", []) if primary_side else []},
        "long": long, "short": short, "safety_boundary": SAFETY,
    }
