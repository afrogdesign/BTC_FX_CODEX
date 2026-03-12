from __future__ import annotations

from typing import Any


def determine_phase1_activation(
    *,
    bias: str,
    primary_setup_side: str,
    primary_setup_status: str,
    data_quality_flag: str,
    entry_price: float,
    stop_loss_price: float,
) -> dict[str, Any]:
    if primary_setup_side not in {"long", "short"}:
        return {"phase1_active": False, "phase1_activation_reason": "no_directional_setup"}
    if bias == "wait":
        return {"phase1_active": False, "phase1_activation_reason": "bias_wait"}
    if entry_price <= 0 or stop_loss_price <= 0 or abs(entry_price - stop_loss_price) <= 0:
        return {"phase1_active": False, "phase1_activation_reason": "invalid_price_inputs"}
    if data_quality_flag == "partial_missing":
        return {"phase1_active": False, "phase1_activation_reason": "partial_missing_data"}
    if primary_setup_status == "ready":
        return {"phase1_active": True, "phase1_activation_reason": "ready_setup"}
    if primary_setup_status == "watch":
        return {"phase1_active": False, "phase1_activation_reason": "watch_reference_only"}
    return {"phase1_active": False, "phase1_activation_reason": "setup_not_ready"}
