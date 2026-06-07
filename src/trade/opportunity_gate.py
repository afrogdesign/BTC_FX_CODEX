from __future__ import annotations

from typing import Any


_FATAL_NO_TRADE_FLAGS = {
    "ATR_extreme",
    "Funding_prohibited",
    "Funding_prohibited_long",
    "Funding_prohibited_short",
}
_MARKET_MAP_OPPORTUNITY_FLAGS = {
    "support_to_resistance_flip",
    "failed_breakout_down_reversal",
    "resistance_to_support_flip",
}
_SHORT_CONTINUATION_FLAGS = {
    "failed_breakout_down_reversal",
    "support_to_resistance_flip",
}
_LOW_EXEC_ALLOWED_FLAGS = {
    "support_to_resistance_flip",
    "trend_flip_confirmed_down",
}
_PRICE_DISTANCE_SETUP_REASONS = {
    "entry_zone_not_reached",
    "near_entry_zone_waiting_trigger",
}
_BLOCKED_TREND_FLAGS = {"standalone_trend_flip_confirmed_up"}
_QUALITY_TREND_FLAGS = {"trend_flip_confirmed_up", *_BLOCKED_TREND_FLAGS}
_SOFT_RISK_PREFIX = "soft_risk:"


def _normalize_flags(values: list[str] | tuple[str, ...] | set[str] | str | None) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        parts = values.replace("[", "").replace("]", "").replace('"', "").split(",")
        return {part.strip() for part in parts if part.strip()}
    return {str(value).strip() for value in values if str(value).strip()}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _quality_guard_reasons(*, execution: float, wait: float, long_side: bool, trend_flags: set[str]) -> tuple[str | None, str | None]:
    hard_reasons: list[str] = []
    soft_reasons: list[str] = []
    if wait >= 60.0 and execution < 24.0:
        hard_reasons.append("require_execution_for_high_wait")
    if long_side and wait >= 60.0:
        target = hard_reasons if hard_reasons else soft_reasons
        target.append("suppress_long_high_wait")
    if long_side and trend_flags:
        target = hard_reasons if hard_reasons else soft_reasons
        target.append("suppress_trend_flip_up_strong")
    hard_reason = "+".join(hard_reasons) if hard_reasons else None
    soft_reason = f"{_SOFT_RISK_PREFIX}{'+'.join(soft_reasons)}" if soft_reasons else None
    return hard_reason, soft_reason


def _has_distance_value(value: Any) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    if raw.lower() in {"none", "nan", "null"}:
        return False
    return True


def _entry_wait_price_recheck_reasons(
    *,
    side: str,
    setup_reason: str,
    execution_precision_action: str,
    direction: float,
    execution: float,
    wait: float,
    risk_flags: set[str],
    market_flags: set[str],
    nearest_support_distance: Any,
    nearest_resistance_distance: Any,
) -> tuple[list[str], list[str]]:
    blocking_reasons: list[str] = []
    non_blocking_reasons: list[str] = []
    side_value = str(side or "").strip()
    long_side = side_value == "long"
    short_side = side_value == "short"
    setup_reason_value = str(setup_reason or "").strip()
    precision_action = str(execution_precision_action or "").strip()
    combined_flags = set(risk_flags) | set(market_flags)

    high_wait_keep = (
        execution >= 24.0
        or setup_reason_value == "near_entry_zone_waiting_trigger"
        or (precision_action and precision_action != "wait_only")
        or (short_side and bool(combined_flags & _SHORT_CONTINUATION_FLAGS))
    )
    if wait >= 60.0 and not high_wait_keep:
        blocking_reasons.append("entry_recheck_required_high_wait")

    if short_side and execution < 20.0:
        blocking_reasons.append("entry_recheck_required_short_low_execution")

    low_exec_keep = (
        direction >= 70.0
        and wait < 60.0
        and short_side
        and bool(combined_flags & _LOW_EXEC_ALLOWED_FLAGS)
    )
    if execution < 24.0 and not low_exec_keep:
        blocking_reasons.append("entry_recheck_required_low_execution")

    has_resistance_flip_pair = "resistance_to_support_flip" in combined_flags and "resistance_to_support_retest_confirmed" in combined_flags
    trend_flip_confirmed_up_only = "trend_flip_confirmed_up" in combined_flags and not (
        combined_flags - {"trend_flip_confirmed_up"}
    )
    long_keep = (
        execution >= 28.0
        or wait < 55.0
        or has_resistance_flip_pair
        or ("major_support_rejection" in combined_flags and not trend_flip_confirmed_up_only)
    )
    if long_side and not long_keep:
        blocking_reasons.append("entry_recheck_required_long_weakness")

    trend_flip_up_keep = (
        execution >= 30.0
        and wait < 55.0
        and ("resistance_to_support_flip" in combined_flags or "major_support_rejection" in combined_flags)
        and "long_into_major_resistance" not in combined_flags
    )
    if long_side and "trend_flip_confirmed_up" in combined_flags and not trend_flip_up_keep:
        blocking_reasons.append("entry_recheck_required_trend_flip_up")

    if setup_reason_value in _PRICE_DISTANCE_SETUP_REASONS:
        if not (_has_distance_value(nearest_support_distance) or _has_distance_value(nearest_resistance_distance)):
            non_blocking_reasons.append("price_distance_missing")

    return sorted(set(blocking_reasons)), sorted(set(non_blocking_reasons))


def determine_opportunity_gate(
    *,
    bias: str,
    primary_setup_side: str,
    primary_setup_status: str,
    primary_setup_reason: str = "",
    data_quality_flag: str,
    no_trade_flags: list[str] | tuple[str, ...] | set[str] | str | None,
    risk_flags: list[str] | tuple[str, ...] | set[str] | str | None,
    market_map_flags: list[str] | tuple[str, ...] | set[str] | str | None,
    phase1_observation_gate: str,
    phase1_observation_type: str,
    phase1b_lite_gate: str,
    phase1b_lite_type: str,
    trade_execution_gate: str,
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
    execution_precision_action: str = "",
    nearest_support_distance: Any = None,
    nearest_resistance_distance: Any = None,
) -> dict[str, Any]:
    blockers: list[str] = []
    reasons: list[str] = []
    opportunity_type = "blocked"

    normalized_no_trade = _normalize_flags(no_trade_flags)
    normalized_risk = _normalize_flags(risk_flags)
    normalized_market = _normalize_flags(market_map_flags)

    if str(data_quality_flag or "").strip() != "ok":
        blockers.append("data_quality_not_ok")
    if str(bias or "").strip() not in {"long", "short"} or str(primary_setup_side or "").strip() not in {"long", "short"}:
        blockers.append("no_directional_setup")
    if str(primary_setup_status or "").strip() not in {"ready", "watch"}:
        blockers.append("setup_status_not_watch_or_ready")
    fatal_flags = sorted(normalized_no_trade & _FATAL_NO_TRADE_FLAGS)
    blockers.extend(f"fatal_no_trade_flag:{flag}" for flag in fatal_flags)

    direction = _as_float(confidence_direction_shadow)
    execution = _as_float(confidence_execution_shadow)
    wait = _as_float(confidence_wait_shadow)
    long_side = str(bias or "").strip() == "long" or str(primary_setup_side or "").strip() == "long"
    if direction < 45.0:
        blockers.append("direction_shadow_too_low")
    if wait > 92.0:
        blockers.append("wait_shadow_extreme")

    if normalized_risk & _BLOCKED_TREND_FLAGS:
        blockers.extend(sorted(normalized_risk & _BLOCKED_TREND_FLAGS))

    hard_quality_reason, soft_quality_reason = _quality_guard_reasons(
        execution=execution,
        wait=wait,
        long_side=long_side,
        trend_flags=(normalized_risk | normalized_market) & _QUALITY_TREND_FLAGS,
    )

    if hard_quality_reason:
        blockers.append(hard_quality_reason)

    unique_blockers = sorted(set(blockers))
    is_formal_candidate = str(trade_execution_gate or "").strip() == "pass"

    if not unique_blockers and is_formal_candidate:
        opportunity_type = "formal_execution_candidate"
        reasons.append("trade_execution_gate_pass")
        if soft_quality_reason:
            reasons.append(f"formal_candidate_quality_conflict:{soft_quality_reason}")
    elif not unique_blockers and str(phase1b_lite_gate or "").strip() == "pass":
        opportunity_type = str(phase1b_lite_type or "").strip() or "phase1b_lite"
        reasons.append("phase1b_lite_gate_pass")
    elif not unique_blockers and str(phase1_observation_gate or "").strip() == "pass":
        opportunity_type = str(phase1_observation_type or "").strip() or "phase1_observation"
        reasons.append("phase1_observation_gate_pass")

    market_hits = sorted(normalized_market & _MARKET_MAP_OPPORTUNITY_FLAGS)
    if not unique_blockers and market_hits and direction >= 50.0 and execution >= 12.0:
        if opportunity_type == "blocked":
            opportunity_type = "market_map_opportunity"
        reasons.extend(f"market_map:{flag}" for flag in market_hits)

    if not unique_blockers and market_hits and not is_formal_candidate and opportunity_type != "blocked":
        primary_side = str(primary_setup_side or "").strip()
        bias_side = str(bias or "").strip()
        side = primary_side if primary_side in {"long", "short"} else bias_side
        recheck_blockers, recheck_reasons = _entry_wait_price_recheck_reasons(
            side=side,
            setup_reason=str(primary_setup_reason or "").strip(),
            execution_precision_action=str(execution_precision_action or "").strip(),
            direction=direction,
            execution=execution,
            wait=wait,
            risk_flags=normalized_risk,
            market_flags=normalized_market,
            nearest_support_distance=nearest_support_distance,
            nearest_resistance_distance=nearest_resistance_distance,
        )
        blockers.extend(recheck_blockers)
        reasons.extend(recheck_reasons)
        unique_blockers = sorted(set(blockers))

    if not unique_blockers and soft_quality_reason and not is_formal_candidate and opportunity_type != "blocked":
        reasons.append(soft_quality_reason)

    unique_reasons = sorted(set(reasons))
    return {
        "opportunity_gate": "pass" if opportunity_type != "blocked" and not unique_blockers else "blocked",
        "opportunity_type": opportunity_type if not unique_blockers else "blocked",
        "opportunity_reasons": unique_reasons if opportunity_type != "blocked" and not unique_blockers else unique_blockers,
    }
