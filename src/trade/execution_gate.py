from __future__ import annotations

from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def determine_trade_execution_gate(
    *,
    phase1_active: bool,
    primary_setup_status: str,
    primary_setup_reason: str,
    data_quality_flag: str,
    no_trade_flags: list[str],
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
) -> dict[str, Any]:
    blockers: list[str] = []
    if not phase1_active:
        blockers.append("phase1_inactive")
    if primary_setup_status != "ready":
        blockers.append("setup_not_ready")
    if primary_setup_reason == "rr_below_min":
        blockers.append("rr_below_min")
    if data_quality_flag != "ok":
        blockers.append("data_quality_not_ok")
    if no_trade_flags:
        blockers.append("no_trade_flags_present")
    if _as_float(confidence_execution_shadow) <= 20.0:
        blockers.append("execution_shadow_too_low")
    if _as_float(confidence_wait_shadow) >= 60.0:
        blockers.append("wait_pressure_too_high")

    unique_blockers = sorted(set(blockers))
    return {
        "trade_execution_gate": "blocked" if unique_blockers else "pass",
        "trade_execution_blockers": unique_blockers,
    }
