from __future__ import annotations

from typing import Any


def _round2(value: float) -> float:
    return round(float(value), 2)


def _empty_plan(reason: str) -> dict[str, Any]:
    return {
        "risk_percent_applied": 0.0,
        "planned_risk_usd": 0.0,
        "position_size_usd": 0.0,
        "max_size_capped": False,
        "size_reduction_reasons": [reason] if reason else [],
    }


def build_position_size_plan(
    *,
    account_balance: float,
    entry_price: float,
    stop_loss_price: float,
    signal_tier: str,
    loss_streak: int,
    base_risk_pct: float,
    loss_streak_step_pct: float,
    min_risk_pct: float,
    max_position_size_usd: float,
) -> dict[str, Any]:
    if account_balance <= 0 or entry_price <= 0 or stop_loss_price <= 0:
        return _empty_plan("invalid_inputs")

    stop_distance = abs(entry_price - stop_loss_price)
    if stop_distance <= 0:
        return _empty_plan("zero_stop_distance")

    size_reduction_reasons: list[str] = []
    applied_risk_pct = max(base_risk_pct - max(loss_streak, 0) * loss_streak_step_pct, min_risk_pct)

    if signal_tier == "strong":
        size_reduction_reasons.append("strong_tier_kept_flat")
    if loss_streak > 0:
        size_reduction_reasons.append("loss_streak_risk_reduced")

    planned_risk_usd = account_balance * (applied_risk_pct / 100.0)
    raw_position_size_usd = planned_risk_usd * entry_price / stop_distance
    position_size_usd = raw_position_size_usd
    max_size_capped = False

    if max_position_size_usd > 0 and position_size_usd > max_position_size_usd:
        position_size_usd = max_position_size_usd
        max_size_capped = True
        size_reduction_reasons.append("max_position_size_capped")

    return {
        "risk_percent_applied": _round2(applied_risk_pct),
        "planned_risk_usd": _round2(planned_risk_usd),
        "position_size_usd": _round2(position_size_usd),
        "max_size_capped": max_size_capped,
        "size_reduction_reasons": size_reduction_reasons,
    }
