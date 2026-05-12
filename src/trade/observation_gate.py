from __future__ import annotations

from typing import Any


_FATAL_NO_TRADE_FLAGS = {
    "ATR_extreme",
    "Funding_prohibited",
    "Funding_prohibited_long",
    "Funding_prohibited_short",
}

_WATCH_LEARNING_REASONS = {
    "entry_zone_not_reached",
    "inside_entry_zone_with_trigger",
    "near_entry_zone_waiting_trigger",
}
_CONFIDENCE_WATCH_LEARNING_PRELABELS = {"SWEEP_WAIT", "RISKY_ENTRY"}
_CONFIDENCE_WATCH_REQUIRED_FLAGS = {"sweep_incomplete", "lower_liquidity_close"}
_CONFIDENCE_WATCH_BLOCKING_FLAGS = {"orderbook_ask_heavy", "ask_wall_close", "long_flush_exhaustion"}
_COUNTER_LONG_SHORT_WATCH_REASONS = {"entry_zone_not_reached", "confidence_below_min"}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def is_confidence_watch_learning_candidate(
    *,
    primary_setup_status: str,
    primary_setup_reason: str,
    prelabel: str,
    risk_flags: list[str],
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
) -> bool:
    normalized_prelabel = str(prelabel or "").strip().upper()
    if primary_setup_status != "watch":
        return False
    if str(primary_setup_reason or "").strip() != "confidence_below_min":
        return False
    if normalized_prelabel not in _CONFIDENCE_WATCH_LEARNING_PRELABELS:
        return False
    normalized_flags = {str(flag).strip() for flag in risk_flags if str(flag).strip()}
    if not _CONFIDENCE_WATCH_REQUIRED_FLAGS.issubset(normalized_flags):
        return False
    if normalized_flags & _CONFIDENCE_WATCH_BLOCKING_FLAGS:
        return False
    direction = _as_float(confidence_direction_shadow)
    execution = _as_float(confidence_execution_shadow)
    wait = _as_float(confidence_wait_shadow)
    return direction >= 55.0 and execution >= 18.0 and wait <= 85.0


def is_counter_long_short_watch_candidate(
    *,
    bias: str,
    primary_setup_side: str,
    primary_setup_status: str,
    primary_setup_reason: str,
    secondary_setup_status: str,
    risk_flags: list[str],
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
) -> bool:
    normalized_flags = {str(flag).strip() for flag in risk_flags if str(flag).strip()}
    if str(bias or "").strip() != "long":
        return False
    if str(primary_setup_side or "").strip() != "long":
        return False
    if str(primary_setup_status or "").strip() != "watch":
        return False
    if str(primary_setup_reason or "").strip() not in _COUNTER_LONG_SHORT_WATCH_REASONS:
        return False
    if str(secondary_setup_status or "").strip() not in {"watch", "ready"}:
        return False
    if "long_reversal_risk" not in normalized_flags:
        return False
    direction = _as_float(confidence_direction_shadow)
    execution = _as_float(confidence_execution_shadow)
    wait = _as_float(confidence_wait_shadow)
    return direction >= 55.0 and execution >= 15.0 and wait <= 90.0


def determine_phase1_observation_gate(
    *,
    bias: str,
    primary_setup_side: str,
    primary_setup_status: str,
    primary_setup_reason: str,
    prelabel: str,
    data_quality_flag: str,
    no_trade_flags: list[str],
    risk_flags: list[str],
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
    secondary_setup_status: str = "",
) -> dict[str, Any]:
    blockers: list[str] = []
    observation_type = "blocked"

    if data_quality_flag != "ok":
        blockers.append("data_quality_not_ok")
    if bias not in {"long", "short"} or primary_setup_side not in {"long", "short"}:
        blockers.append("no_directional_setup")
    normalized_prelabel = str(prelabel or "").strip().upper()
    if normalized_prelabel == "NO_TRADE_CANDIDATE":
        blockers.append("no_trade_candidate")

    fatal_flags = sorted(set(str(flag) for flag in no_trade_flags if str(flag) in _FATAL_NO_TRADE_FLAGS))
    if fatal_flags:
        blockers.extend(fatal_flags)

    reason = str(primary_setup_reason or "").strip()
    direction = _as_float(confidence_direction_shadow)
    execution = _as_float(confidence_execution_shadow)
    wait = _as_float(confidence_wait_shadow)

    if not blockers and is_counter_long_short_watch_candidate(
        bias=bias,
        primary_setup_side=primary_setup_side,
        primary_setup_status=primary_setup_status,
        primary_setup_reason=reason,
        secondary_setup_status=secondary_setup_status,
        risk_flags=risk_flags,
        confidence_direction_shadow=direction,
        confidence_execution_shadow=execution,
        confidence_wait_shadow=wait,
    ):
        observation_type = "counter_long_short_watch"
    elif reason == "confidence_below_min":
        if not blockers and is_confidence_watch_learning_candidate(
            primary_setup_status=primary_setup_status,
            primary_setup_reason=reason,
            prelabel=normalized_prelabel,
            risk_flags=risk_flags,
            confidence_direction_shadow=direction,
            confidence_execution_shadow=execution,
            confidence_wait_shadow=wait,
        ):
            observation_type = "confidence_watch_learning"
        else:
            blockers.append("confidence_below_min")
    elif not blockers and reason == "rr_below_min" and direction >= 35.0:
        observation_type = "direction_rr_learning"
    elif (
        not blockers
        and primary_setup_status == "watch"
        and reason in _WATCH_LEARNING_REASONS
        and execution >= 20.0
        and wait <= 75.0
    ):
        observation_type = "setup_watch_learning"
    elif not blockers:
        if reason == "rr_below_min":
            blockers.append("direction_confidence_too_low")
        elif primary_setup_status == "watch":
            blockers.append("watch_conditions_not_met")
        else:
            blockers.append("setup_not_observable")

    unique_blockers = sorted(set(blockers))
    return {
        "phase1_observation_gate": "pass" if observation_type != "blocked" else "blocked",
        "phase1_observation_type": observation_type,
        "phase1_observation_reasons": unique_blockers if observation_type == "blocked" else [observation_type],
    }
