from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.analysis.signal_tier import signal_tier_upgraded


def _parse_utc(iso_text: str) -> datetime | None:
    if not iso_text:
        return None
    try:
        if iso_text.endswith("Z"):
            return datetime.fromisoformat(iso_text.replace("Z", "+00:00"))
        return datetime.fromisoformat(iso_text).astimezone(timezone.utc)
    except ValueError:
        return None


def _status_upgrade(old: str, new: str) -> bool:
    if old == "invalid" and new in {"watch", "ready"}:
        return True
    if old == "watch" and new == "ready":
        return True
    return False


def _bias_upgrade(old: str, new: str) -> bool:
    return old == "wait" and new in {"long", "short"}


_PRELABEL_RANK = {
    "NO_TRADE_CANDIDATE": 0,
    "SWEEP_WAIT": 1,
    "RISKY_ENTRY": 2,
    "ENTRY_OK": 3,
}


def _prelabel_upgrade(old: str, new: str) -> bool:
    return _PRELABEL_RANK.get(new, -1) > _PRELABEL_RANK.get(old, -1)


def should_notify(
    current: dict[str, Any],
    last_result: dict[str, Any] | None,
    last_notified: dict[str, Any] | None,
    cfg: Any,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    bias = current.get("bias")
    confidence = int(current.get("confidence", 0))
    if bias not in {"long", "short"}:
        return False, reasons
    if bias == "long" and confidence < cfg.CONFIDENCE_LONG_MIN:
        return False, reasons
    if bias == "short" and confidence < cfg.CONFIDENCE_SHORT_MIN:
        return False, reasons

    prev_status = (last_result or {}).get("primary_setup_status", "none")
    current_status = current.get("primary_setup_status", "none")
    if _status_upgrade(prev_status, current_status):
        reasons.append("status_upgraded")

    prev_bias = (last_result or {}).get("bias", "wait")
    if _bias_upgrade(prev_bias, bias):
        reasons.append("bias_changed")

    prev_prelabel = (last_result or {}).get("prelabel", "NO_TRADE_CANDIDATE")
    current_prelabel = current.get("prelabel", "NO_TRADE_CANDIDATE")
    if _prelabel_upgrade(prev_prelabel, current_prelabel):
        reasons.append("prelabel_improved")

    prev_conf = int((last_notified or {}).get("confidence", confidence))
    if abs(confidence - prev_conf) >= cfg.CONFIDENCE_ALERT_CHANGE:
        reasons.append("confidence_jump")

    prev_agreement = (last_notified or {}).get("agreement_with_machine")
    curr_agreement = current.get("agreement_with_machine")
    if prev_agreement in {"agree", "disagree"} and curr_agreement in {"agree", "disagree"}:
        if prev_agreement != curr_agreement:
            reasons.append("agreement_changed")

    prev_tier = str((last_notified or {}).get("signal_tier", "normal"))
    curr_tier = str(current.get("signal_tier", "normal"))
    if signal_tier_upgraded(prev_tier, curr_tier):
        reasons.append("signal_tier_upgraded")

    no_trade_flags = current.get("no_trade_flags", [])
    if current_status == "invalid" and len(no_trade_flags) >= 2 and current_prelabel != "ENTRY_OK":
        return False, []

    if not reasons:
        return False, []

    last_notified_ts = _parse_utc((last_notified or {}).get("timestamp_utc", ""))
    now_ts = _parse_utc(str(current.get("timestamp_utc", "")))
    if last_notified_ts and now_ts:
        cooldown = timedelta(minutes=cfg.ALERT_COOLDOWN_MINUTES)
        if now_ts - last_notified_ts < cooldown:
            if "signal_tier_upgraded" not in reasons:
                return False, []

    return True, sorted(set(reasons))
