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
_BLOCKED_TREND_FLAGS = {"standalone_trend_flip_confirmed_up"}
_QUALITY_TREND_FLAGS = {"trend_flip_confirmed_up", *_BLOCKED_TREND_FLAGS}


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


def determine_opportunity_gate(
    *,
    bias: str,
    primary_setup_side: str,
    primary_setup_status: str,
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
) -> dict[str, Any]:
    blockers: list[str] = []
    quality_blockers: list[str] = []
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

    if wait >= 60.0 and execution < 24.0:
        quality_blockers.append("require_execution_for_high_wait")
    if long_side and wait >= 60.0:
        quality_blockers.append("suppress_long_high_wait")
    if long_side and ((normalized_risk | normalized_market) & _QUALITY_TREND_FLAGS):
        quality_blockers.append("suppress_trend_flip_up_strong")

    unique_blockers = sorted(set(blockers))
    unique_quality_blockers = sorted(set(quality_blockers))
    is_formal_candidate = str(trade_execution_gate or "").strip() == "pass"

    if not unique_blockers and is_formal_candidate:
        opportunity_type = "formal_execution_candidate"
        reasons.append("trade_execution_gate_pass")
        reasons.extend(f"formal_candidate_quality_conflict:{blocker}" for blocker in unique_quality_blockers)
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

    unique_reasons = sorted(set(reasons))
    if unique_quality_blockers and not is_formal_candidate:
        return {
            "opportunity_gate": "blocked",
            "opportunity_type": "blocked",
            "opportunity_reasons": unique_quality_blockers,
        }
    return {
        "opportunity_gate": "pass" if opportunity_type != "blocked" and not unique_blockers else "blocked",
        "opportunity_type": opportunity_type if not unique_blockers else "blocked",
        "opportunity_reasons": unique_reasons if opportunity_type != "blocked" and not unique_blockers else unique_blockers,
    }
