from __future__ import annotations

from typing import Any


_MAJOR_WARNING_FLAGS = {
    "Funding_prohibited_long",
    "Funding_prohibited_short",
    "ATR_extreme",
    "Critical_zone_warning",
}


_TIER_RANK = {
    "normal": 0,
    "strong_machine": 1,
}

_TIER_BADGE = {
    "normal": "",
    "strong_machine": "🟡 好条件接近",
}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:  # noqa: BLE001
        return default


def signal_tier_badge(tier: str) -> str:
    return _TIER_BADGE.get(tier, "")


def signal_tier_upgraded(old_tier: str, new_tier: str) -> bool:
    return _TIER_RANK.get(new_tier, -1) > _TIER_RANK.get(old_tier, -1)


def compute_signal_tier(result: dict[str, Any], cfg: Any) -> dict[str, Any]:
    bias = str(result.get("bias", "wait"))
    if bias not in {"long", "short"}:
        return {"tier": "normal", "reason_codes": ["bias_wait"]}

    confidence = int(result.get("confidence", 0))
    confidence_floor = cfg.CONFIDENCE_LONG_MIN if bias == "long" else cfg.CONFIDENCE_SHORT_MIN
    no_trade_flags = result.get("no_trade_flags", [])
    risk_flags = result.get("risk_flags", [])
    warning_flags = result.get("warning_flags", [])
    rr_estimate = _as_float(result.get("rr_estimate"))
    agreement = result.get("agreement_with_machine")
    prelabel = result.get("prelabel")
    primary_status = result.get("primary_setup_status")
    reason_codes: list[str] = []
    combined_warning_flags = [str(flag) for flag in warning_flags] + [str(flag) for flag in risk_flags]
    major_warning_count = sum(1 for flag in combined_warning_flags if flag in _MAJOR_WARNING_FLAGS)
    minor_warning_count = len(combined_warning_flags) - major_warning_count

    strong_machine = (
        prelabel == "ENTRY_OK"
        and primary_status == "ready"
        and confidence >= confidence_floor + 10
        and rr_estimate >= 1.8
        and not no_trade_flags
        and major_warning_count == 0
        and minor_warning_count <= 1
        and agreement == "agree"
    )
    if not strong_machine:
        if prelabel != "ENTRY_OK":
            reason_codes.append("prelabel_not_entry_ok")
        if primary_status != "ready":
            reason_codes.append("primary_setup_not_ready")
        if confidence < confidence_floor + 10:
            reason_codes.append("confidence_buffer_missing")
        if rr_estimate < 1.8:
            reason_codes.append("rr_below_strong_threshold")
        if no_trade_flags:
            reason_codes.append("no_trade_flags_present")
        if major_warning_count:
            reason_codes.append("major_warning_present")
        if minor_warning_count > 1:
            reason_codes.append("minor_warning_limit_exceeded")
        if agreement != "agree":
            reason_codes.append("machine_disagreement")
        return {"tier": "normal", "reason_codes": sorted(set(reason_codes)) or ["strong_machine_not_met"]}

    reason_codes.extend(
        [
            "prelabel_entry_ok",
            "primary_ready",
            "confidence_buffer_met",
            "rr_strong_enough",
            "warning_budget_ok",
            "machine_agree",
        ]
    )

    return {"tier": "strong_machine", "reason_codes": sorted(set(reason_codes))}
