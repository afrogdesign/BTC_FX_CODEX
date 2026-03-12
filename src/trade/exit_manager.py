from __future__ import annotations

from typing import Any


def _round2(value: float) -> float:
    return round(float(value), 2)


def _empty_plan(reason: str) -> dict[str, Any]:
    return {
        "tp1_price": 0.0,
        "tp2_price": 0.0,
        "breakeven_after_tp1": False,
        "trail_atr_multiplier": 0.0,
        "timeout_hours": 0,
        "exit_rule_version": reason or "phase1_unavailable",
    }


def build_exit_plan(
    *,
    side: str,
    entry_price: float,
    stop_loss_price: float,
    atr: float,
    tp1_rr_multiple: float,
    tp2_rr_multiple: float,
    trail_atr_multiplier: float,
    timeout_hours: int,
    exit_rule_version: str,
) -> dict[str, Any]:
    if side not in {"long", "short"} or entry_price <= 0 or stop_loss_price <= 0:
        return _empty_plan("phase1_invalid_setup")

    stop_distance = abs(entry_price - stop_loss_price)
    if stop_distance <= 0:
        return _empty_plan("phase1_zero_stop_distance")

    direction = 1.0 if side == "long" else -1.0
    tp1_price = entry_price + direction * stop_distance * tp1_rr_multiple
    tp2_price = entry_price + direction * stop_distance * tp2_rr_multiple

    return {
        "tp1_price": _round2(tp1_price),
        "tp2_price": _round2(tp2_price),
        "breakeven_after_tp1": True,
        "trail_atr_multiplier": _round2(trail_atr_multiplier if atr > 0 else 0.0),
        "timeout_hours": int(timeout_hours),
        "exit_rule_version": exit_rule_version,
    }
