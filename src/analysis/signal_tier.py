from __future__ import annotations

from typing import Any


_TIER_RANK = {
    "normal": 0,
    "strong_machine": 1,
    "strong_ai_confirmed": 2,
}

_TIER_BADGE = {
    "normal": "",
    "strong_machine": "🟡 好条件接近",
    "strong_ai_confirmed": "🔥 ゴールデン条件",
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

    strong_machine = (
        prelabel == "ENTRY_OK"
        and primary_status == "ready"
        and confidence >= confidence_floor + 10
        and rr_estimate >= 2.0
        and not no_trade_flags
        and not risk_flags
        and not warning_flags
        and agreement == "agree"
    )
    if not strong_machine:
        if prelabel != "ENTRY_OK":
            reason_codes.append("prelabel_not_entry_ok")
        if primary_status != "ready":
            reason_codes.append("primary_setup_not_ready")
        if confidence < confidence_floor + 10:
            reason_codes.append("confidence_buffer_missing")
        if rr_estimate < 2.0:
            reason_codes.append("rr_below_strong_threshold")
        if no_trade_flags:
            reason_codes.append("no_trade_flags_present")
        if risk_flags:
            reason_codes.append("risk_flags_present")
        if warning_flags:
            reason_codes.append("warning_flags_present")
        if agreement != "agree":
            reason_codes.append("machine_disagreement")
        return {"tier": "normal", "reason_codes": sorted(set(reason_codes)) or ["strong_machine_not_met"]}

    reason_codes.extend(
        [
            "prelabel_entry_ok",
            "primary_ready",
            "confidence_buffer_met",
            "rr_strong_enough",
            "clean_flags",
            "machine_agree",
        ]
    )

    ai_advice = result.get("ai_advice")
    if not isinstance(ai_advice, dict):
        return {"tier": "strong_machine", "reason_codes": sorted(set(reason_codes + ["ai_review_unavailable"]))}

    ai_decision = str(ai_advice.get("decision", "")).upper()
    expected_decision = "LONG" if bias == "long" else "SHORT"
    ai_confidence = _as_float(ai_advice.get("confidence"))
    ai_quality = str(ai_advice.get("quality", "")).upper()

    if ai_decision == expected_decision and ai_confidence >= 0.70 and ai_quality in {"A", "B"}:
        return {
            "tier": "strong_ai_confirmed",
            "reason_codes": sorted(set(reason_codes + ["ai_direction_match", "ai_confidence_confirmed", "ai_quality_confirmed"])),
        }
    if ai_decision != expected_decision:
        reason_codes.append("ai_direction_mismatch")
    if ai_confidence < 0.70:
        reason_codes.append("ai_confidence_low")
    if ai_quality not in {"A", "B"}:
        reason_codes.append("ai_quality_low")
    return {"tier": "strong_machine", "reason_codes": sorted(set(reason_codes))}
