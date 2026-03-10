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


def compute_signal_tier(result: dict[str, Any], cfg: Any) -> str:
    bias = str(result.get("bias", "wait"))
    if bias not in {"long", "short"}:
        return "normal"

    confidence = int(result.get("confidence", 0))
    confidence_floor = cfg.CONFIDENCE_LONG_MIN if bias == "long" else cfg.CONFIDENCE_SHORT_MIN
    no_trade_flags = result.get("no_trade_flags", [])
    risk_flags = result.get("risk_flags", [])
    warning_flags = result.get("warning_flags", [])
    rr_estimate = _as_float(result.get("rr_estimate"))
    agreement = result.get("agreement_with_machine")
    prelabel = result.get("prelabel")
    primary_status = result.get("primary_setup_status")

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
        return "normal"

    ai_advice = result.get("ai_advice")
    if not isinstance(ai_advice, dict):
        return "strong_machine"

    ai_decision = str(ai_advice.get("decision", "")).upper()
    expected_decision = "LONG" if bias == "long" else "SHORT"
    ai_confidence = _as_float(ai_advice.get("confidence"))
    ai_quality = str(ai_advice.get("quality", "")).upper()

    if ai_decision == expected_decision and ai_confidence >= 0.70 and ai_quality in {"A", "B"}:
        return "strong_ai_confirmed"
    return "strong_machine"

