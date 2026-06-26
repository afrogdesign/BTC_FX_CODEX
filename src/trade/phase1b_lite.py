from __future__ import annotations

from typing import Any


_REQUIRED_RISK_FLAGS = {"sweep_incomplete", "lower_liquidity_close"}
_BLOCKING_RISK_FLAGS = {"orderbook_ask_heavy", "ask_wall_close", "long_flush_exhaustion"}
_FATAL_NO_TRADE_FLAGS = {
    "ATR_extreme",
    "Funding_prohibited",
    "Funding_prohibited_long",
    "Funding_prohibited_short",
}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_flags(values: list[str] | tuple[str, ...] | set[str] | str | None) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        parts = values.replace("[", "").replace("]", "").replace('"', "").split(",")
        return {part.strip() for part in parts if part.strip()}
    return {str(value).strip() for value in values if str(value).strip()}


def determine_phase1b_lite_gate(
    *,
    phase1_observation_type: str,
    primary_setup_status: str,
    primary_setup_reason: str,
    prelabel: str,
    data_quality_flag: str,
    no_trade_flags: list[str] | tuple[str, ...] | set[str] | str | None,
    risk_flags: list[str] | tuple[str, ...] | set[str] | str | None,
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
) -> dict[str, Any]:
    blockers: list[str] = []
    normalized_prelabel = str(prelabel or "").strip().upper()
    normalized_risk_flags = _normalize_flags(risk_flags)
    normalized_no_trade_flags = _normalize_flags(no_trade_flags)

    if str(data_quality_flag or "").strip() != "ok":
        blockers.append("data_quality_not_ok")
    if str(phase1_observation_type or "").strip() != "confidence_watch_learning":
        blockers.append("not_confidence_watch_learning")
    if str(primary_setup_status or "").strip() != "watch":
        blockers.append("primary_setup_not_watch")
    if str(primary_setup_reason or "").strip() != "confidence_below_min":
        blockers.append("primary_reason_not_confidence_below_min")
    if normalized_prelabel != "SWEEP_WAIT":
        blockers.append("prelabel_not_sweep_wait")
    if not _REQUIRED_RISK_FLAGS.issubset(normalized_risk_flags):
        blockers.append("required_risk_flags_missing")
    blocking_flags = sorted(normalized_risk_flags & _BLOCKING_RISK_FLAGS)
    if blocking_flags:
        blockers.extend(f"blocking_risk_flag:{flag}" for flag in blocking_flags)
    fatal_flags = sorted(normalized_no_trade_flags & _FATAL_NO_TRADE_FLAGS)
    if fatal_flags:
        blockers.extend(f"fatal_no_trade_flag:{flag}" for flag in fatal_flags)

    direction = _as_float(confidence_direction_shadow)
    execution = _as_float(confidence_execution_shadow)
    wait = _as_float(confidence_wait_shadow)
    if direction < 55.0:
        blockers.append("direction_below_lite_min")
    if execution < 18.0:
        blockers.append("execution_below_lite_min")
    if wait > 85.0:
        blockers.append("wait_above_lite_max")

    trend_up_supporting_flags = normalized_risk_flags - _REQUIRED_RISK_FLAGS - {"trend_flip_confirmed_up"}
    if "trend_flip_confirmed_up" in normalized_risk_flags and not trend_up_supporting_flags:
        blockers.append("standalone_trend_flip_confirmed_up")

    unique_blockers = sorted(set(blockers))
    return {
        "phase1b_lite_gate": "blocked" if unique_blockers else "pass",
        "phase1b_lite_type": "confidence_watch_sweep_lite" if not unique_blockers else "blocked",
        "phase1b_lite_reasons": unique_blockers if unique_blockers else ["confidence_watch_sweep_lite"],
    }
