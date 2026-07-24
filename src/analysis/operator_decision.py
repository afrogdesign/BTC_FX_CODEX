from __future__ import annotations

from typing import Any


def build_operator_decision(result: dict[str, Any]) -> dict[str, Any]:
    """Build the display-only, fail-closed operator decision contract."""
    bias = str(result.get("bias", "wait")).lower()
    if bias not in {"long", "short"}:
        bias = "wait"
    action = result.get("side_aware_mtf_action") if isinstance(result.get("side_aware_mtf_action"), dict) else {}
    execution = action.get("execution_context") if isinstance(action.get("execution_context"), dict) else {}
    side_aware_side = str(execution.get("primary_side", "")).lower()
    signal_15m = str(result.get("signals_15m", "")).lower()
    signals_4h = str(result.get("signals_4h", "")).lower()
    signals_1h = str(result.get("signals_1h", "")).lower()
    market_map = result.get("market_map") if isinstance(result.get("market_map"), dict) else {}
    conflicts = {str(item) for item in market_map.get("market_map_conflicts", [])}
    flags = {str(item) for item in market_map.get("flags", [])}
    opposite = "opposite_15m_signal_conflict" in conflicts
    family_conflict = "market_map_direction_conflict" in conflicts or (bool(flags & {"failed_breakout_up_reversal", "major_support_rejection", "resistance_to_support_flip", "resistance_to_support_retest_confirmed", "trend_flip_early_up", "trend_flip_confirmed_up"}) and bool(flags & {"failed_breakout_down_reversal", "major_resistance_rejection", "support_to_resistance_flip", "support_to_resistance_retest_confirmed", "trend_flip_early_down", "trend_flip_confirmed_down"}))
    score_vs_side = bias in {"long", "short"} and side_aware_side in {"long", "short"} and bias != side_aware_side
    score_vs_15m = bias in {"long", "short"} and signal_15m in {"long", "short"} and bias != signal_15m and not (signals_4h == bias and signals_1h == bias)
    direction_conflict = bool(score_vs_side or score_vs_15m or family_conflict or opposite)
    primary_side = side_aware_side if side_aware_side in {"long", "short"} else signal_15m
    if primary_side not in {"long", "short"}:
        primary_side = bias if bias in {"long", "short"} and not direction_conflict else "none"
    gate_blocked = str(result.get("trade_execution_gate", "")).lower() == "blocked"
    no_trade = bool(result.get("no_trade_flags"))
    action_class = str(execution.get("primary_action_class", "")).upper()
    hard_block = gate_blocked or no_trade or action_class == "STOP_OR_EXIT"
    blocked = hard_block or direction_conflict
    reasons: list[str] = []
    if gate_blocked: reasons.append("trade_execution_gate_blocked")
    if score_vs_side: reasons.append("score_vs_execution_side_conflict")
    if score_vs_15m: reasons.append("score_vs_15m_signal_conflict")
    if family_conflict: reasons.append("market_map_direction_conflict")
    if opposite: reasons.append("opposite_15m_signal_conflict")
    if action_class == "STOP_OR_EXIT": reasons.append("operator_stop_or_exit")
    if hard_block: state = "blocked"
    elif direction_conflict: state = "direction_conflict"
    elif action_class == "B_CHECK_15M": state = "check_15m"
    elif action_class == "C_WATCH_ZONE": state = "watch_zone"
    elif action_class == "A_FORMAL": state = "conditional_candidate"
    else: state = "wait"
    return {"schema_version": "operator_decision.v1", "state": state, "primary_side": primary_side, "score_bias": bias, "new_entry_blocked": blocked, "direction_conflict": direction_conflict, "reason_codes": reasons}
