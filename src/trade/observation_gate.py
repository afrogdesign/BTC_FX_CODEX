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


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def determine_phase1_observation_gate(
    *,
    bias: str,
    primary_setup_side: str,
    primary_setup_status: str,
    primary_setup_reason: str,
    prelabel: str,
    data_quality_flag: str,
    no_trade_flags: list[str],
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
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

    if reason == "confidence_below_min":
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
