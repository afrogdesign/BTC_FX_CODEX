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


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:  # noqa: BLE001
        return default


def _float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:  # noqa: BLE001
        return default


_SWEEP_RECHECK_REASONS = {
    "rr_below_min",
    "entry_zone_not_reached",
    "near_entry_zone_waiting_trigger",
    "inside_entry_zone_with_trigger",
}
_WATCH_SWEEP_MAIN_REASONS = {"status_upgraded", "prelabel_improved", "confidence_jump"}
_WATCH_LOW_EXECUTION_RISK_FLAGS = {"sweep_incomplete", "lower_liquidity_close"}


def _sweep_recheck_wait_case(current: dict[str, Any]) -> bool:
    risk_flags = [str(flag) for flag in current.get("risk_flags", [])]
    prelabel = str(current.get("prelabel", "")).strip()
    status = str(current.get("primary_setup_status", "")).strip()
    reason = str(current.get("primary_setup_reason", "")).strip()
    return (
        prelabel in {"SWEEP_WAIT", "RISKY_ENTRY"}
        and status in {"invalid", "watch"}
        and reason in _SWEEP_RECHECK_REASONS
        and "sweep_incomplete" in risk_flags
        and _float_value(current.get("confidence_execution_shadow", 0.0)) <= 25.0
        and _float_value(current.get("confidence_wait_shadow", 0.0)) >= 60.0
    )


def _watch_sweep_recheck_case(current: dict[str, Any]) -> bool:
    risk_flags = [str(flag) for flag in current.get("risk_flags", [])]
    return (
        str(current.get("prelabel", "")).strip() in {"SWEEP_WAIT", "RISKY_ENTRY"}
        and str(current.get("primary_setup_status", "")).strip() == "watch"
        and str(current.get("primary_setup_reason", "")).strip() in _SWEEP_RECHECK_REASONS
        and "sweep_incomplete" in risk_flags
    )


def _watch_low_execution_recheck_case(current: dict[str, Any]) -> bool:
    risk_flags = {str(flag) for flag in current.get("risk_flags", [])}
    return (
        str(current.get("prelabel", "")).strip() in {"SWEEP_WAIT", "RISKY_ENTRY"}
        and str(current.get("primary_setup_status", "")).strip() == "watch"
        and str(current.get("primary_setup_reason", "")).strip() in _SWEEP_RECHECK_REASONS
        and _WATCH_LOW_EXECUTION_RISK_FLAGS <= risk_flags
        and _float_value(current.get("confidence_execution_shadow", 0.0)) <= 10.0
        and _float_value(current.get("confidence_wait_shadow", 0.0)) >= 45.0
    )


def _attention_reasons(current: dict[str, Any], last_result: dict[str, Any] | None, cfg: Any) -> list[str]:
    bias = str(current.get("bias", "")).lower()
    if bias not in {"long", "short"}:
        return []

    prelabel = str(current.get("prelabel", ""))
    if prelabel not in {"SWEEP_WAIT", "RISKY_ENTRY", "NO_TRADE_CANDIDATE"}:
        return []

    score_min = _int_value(getattr(cfg, "ATTENTION_ALERT_SCORE_MIN", 55), 55)
    gap_min = _int_value(getattr(cfg, "ATTENTION_ALERT_GAP_MIN", 15), 15)
    long_score = _int_value(current.get("long_display_score", 0))
    short_score = _int_value(current.get("short_display_score", 0))
    score_gap = _int_value(current.get("score_gap", 0))

    if bias == "long":
        if long_score < score_min or score_gap < gap_min:
            return []
    else:
        if short_score < score_min or score_gap > -gap_min:
            return []

    prev_bias = str((last_result or {}).get("bias", "wait")).lower()
    prev_long_score = _int_value((last_result or {}).get("long_display_score", 0))
    prev_short_score = _int_value((last_result or {}).get("short_display_score", 0))
    prev_gap = _int_value((last_result or {}).get("score_gap", 0))

    reasons: list[str] = []
    if _bias_upgrade(prev_bias, bias):
        reasons.append("attention_bias_changed")
    if bias == "long":
        if prev_long_score < score_min <= long_score:
            reasons.append("attention_score_crossed")
        if prev_gap < gap_min <= score_gap:
            reasons.append("attention_gap_crossed")
    else:
        if prev_short_score < score_min <= short_score:
            reasons.append("attention_score_crossed")
        if prev_gap > -gap_min >= score_gap:
            reasons.append("attention_gap_crossed")

    if _sweep_recheck_wait_case(current):
        reasons = [reason for reason in reasons if reason not in {"attention_score_crossed", "attention_gap_crossed"}]
    if _watch_low_execution_recheck_case(current):
        reasons = [reason for reason in reasons if reason not in {"attention_score_crossed", "attention_gap_crossed"}]

    if not reasons and not last_result:
        reasons.append("attention_first_detection")
    return sorted(set(reasons))


def should_notify(
    current: dict[str, Any],
    last_result: dict[str, Any] | None,
    last_notified: dict[str, Any] | None,
    last_attention_notified: dict[str, Any] | None,
    cfg: Any,
) -> dict[str, Any]:
    main_reasons: list[str] = []
    suppress_reasons: list[str] = []

    bias = current.get("bias")
    confidence = int(current.get("confidence", 0))
    attention_reasons = _attention_reasons(current, last_result, cfg)
    if bias not in {"long", "short"}:
        return {
            "notify": False,
            "notify_reason_codes": [],
            "suppress_reason_codes": ["bias_wait"],
            "notification_kind": "none",
        }

    prev_status = (last_result or {}).get("primary_setup_status", "none")
    current_status = current.get("primary_setup_status", "none")
    if _status_upgrade(prev_status, current_status):
        main_reasons.append("status_upgraded")

    prev_bias = (last_result or {}).get("bias", "wait")
    if _bias_upgrade(prev_bias, bias):
        main_reasons.append("bias_changed")

    prev_prelabel = (last_result or {}).get("prelabel", "NO_TRADE_CANDIDATE")
    current_prelabel = current.get("prelabel", "NO_TRADE_CANDIDATE")
    if _prelabel_upgrade(prev_prelabel, current_prelabel):
        main_reasons.append("prelabel_improved")

    prev_conf = int((last_notified or {}).get("confidence", confidence))
    if abs(confidence - prev_conf) >= cfg.CONFIDENCE_ALERT_CHANGE:
        main_reasons.append("confidence_jump")

    prev_agreement = (last_notified or {}).get("agreement_with_machine")
    curr_agreement = current.get("agreement_with_machine")
    if prev_agreement in {"agree", "disagree"} and curr_agreement in {"agree", "disagree"}:
        if prev_agreement != curr_agreement:
            main_reasons.append("agreement_changed")

    prev_tier = str((last_notified or {}).get("signal_tier", "normal"))
    curr_tier = str(current.get("signal_tier", "normal"))
    if signal_tier_upgraded(prev_tier, curr_tier):
        main_reasons.append("signal_tier_upgraded")

    no_trade_flags = current.get("no_trade_flags", [])
    risk_flags = [str(flag) for flag in current.get("risk_flags", [])]
    main_blocked = False
    if bias == "long" and confidence < cfg.CONFIDENCE_LONG_MIN:
        suppress_reasons.append("confidence_below_long_min")
        main_blocked = True
    if bias == "short" and confidence < cfg.CONFIDENCE_SHORT_MIN:
        suppress_reasons.append("confidence_below_short_min")
        main_blocked = True
    if current_status == "invalid" and len(no_trade_flags) >= 2 and current_prelabel != "ENTRY_OK":
        suppress_reasons.extend(["primary_setup_invalid", "multiple_no_trade_flags"])
        main_blocked = True
    if _sweep_recheck_wait_case(current):
        suppress_reasons.append("rr_sweep_recheck_wait")
        main_blocked = True
    elif _watch_low_execution_recheck_case(current):
        suppress_reasons.append("watch_low_execution_recheck_wait")
        main_blocked = True
    elif _watch_sweep_recheck_case(current) and set(main_reasons).issubset(_WATCH_SWEEP_MAIN_REASONS):
        suppress_reasons.append("watch_sweep_recheck_wait")
        main_blocked = True

    if not main_blocked and main_reasons:
        last_notified_ts = _parse_utc((last_notified or {}).get("timestamp_utc", ""))
        now_ts = _parse_utc(str(current.get("timestamp_utc", "")))
        if last_notified_ts and now_ts:
            cooldown = timedelta(minutes=cfg.ALERT_COOLDOWN_MINUTES)
            if now_ts - last_notified_ts < cooldown and "signal_tier_upgraded" not in main_reasons:
                suppress_reasons.append("cooldown_active")
            else:
                return {
                    "notify": True,
                    "notify_reason_codes": sorted(set(main_reasons)),
                    "suppress_reason_codes": [],
                    "notification_kind": "main",
                }
        else:
            return {
                "notify": True,
                "notify_reason_codes": sorted(set(main_reasons)),
                "suppress_reason_codes": [],
                "notification_kind": "main",
            }

    if attention_reasons:
        last_attention_ts = _parse_utc((last_attention_notified or {}).get("timestamp_utc", ""))
        now_ts = _parse_utc(str(current.get("timestamp_utc", "")))
        if last_attention_ts and now_ts:
            cooldown = timedelta(minutes=getattr(cfg, "ATTENTION_ALERT_COOLDOWN_MINUTES", 60))
            if now_ts - last_attention_ts < cooldown:
                suppress_reasons.append("attention_cooldown_active")
            else:
                return {
                    "notify": True,
                    "notify_reason_codes": attention_reasons,
                    "suppress_reason_codes": [],
                    "notification_kind": "attention",
                }
        else:
            return {
                "notify": True,
                "notify_reason_codes": attention_reasons,
                "suppress_reason_codes": [],
                "notification_kind": "attention",
            }
    elif _sweep_recheck_wait_case(current):
        suppress_reasons.append("attention_rr_sweep_recheck_wait")
    elif _watch_low_execution_recheck_case(current):
        suppress_reasons.append("attention_watch_low_execution_recheck_wait")

    if not main_reasons and not attention_reasons:
        suppress_reasons.append("no_material_change")
    return {
        "notify": False,
        "notify_reason_codes": [],
        "suppress_reason_codes": sorted(set(suppress_reasons)),
        "notification_kind": "none",
    }
