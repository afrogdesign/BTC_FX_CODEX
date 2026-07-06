from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


FOLLOWUP_PUBLIC_LABEL = "⏱️ 期限切れ・再評価"
FOLLOWUP_SUBJECT_HINT = "⏱️ [期限切れ・再評価] 前回通知の有効期限切れ / 根拠再確認"
FOLLOWUP_SAFETY_BOUNDARY = "report-only / no automatic order / human decides manually"
FOLLOWUP_HUMAN_MESSAGE = (
    "前回通知は有効期限切れです。"
    "保有中の場合は、15分足と1時間足で撤退・建値・損切り確認。"
    "未保有の場合は、前回通知を新規根拠として使わない。"
    f" {FOLLOWUP_SAFETY_BOUNDARY}"
)

FOLLOWUP_REASON_LABELS = {
    "validity_expired": "有効期限切れ",
    "prior_long_bias_lost": "前回ロングのバイアス喪失",
    "prior_long_1h_weakened": "前回ロングの1時間足弱化",
    "prior_long_setup_invalid": "前回ロングの根拠が無効",
    "prior_long_confidence_drop": "前回ロングの信頼度低下",
    "prior_long_support_to_resistance": "前回ロングのサポレジ転換",
    "prior_long_trend_flip_early_down": "前回ロングの早期下向き転換",
    "prior_short_bias_lost": "前回ショートのバイアス喪失",
    "prior_short_1h_weakened": "前回ショートの1時間足弱化",
    "prior_short_setup_invalid": "前回ショートの根拠が無効",
    "prior_short_confidence_drop": "前回ショートの信頼度低下",
    "prior_short_resistance_to_support": "前回ショートのレジサポ転換",
    "prior_short_trend_flip_early_up": "前回ショートの早期上向き転換",
}


def _parse_utc(iso_text: Any) -> datetime | None:
    text = str(iso_text or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        value = datetime.fromisoformat(text)
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _float_value(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _iter_text_values(node: Any) -> list[str]:
    values: list[str] = []
    if isinstance(node, dict):
        for value in node.values():
            values.extend(_iter_text_values(value))
    elif isinstance(node, list):
        for value in node:
            values.extend(_iter_text_values(value))
    elif node is not None:
        values.append(str(node))
    return values


def _candidate_time(payload: dict[str, Any] | None) -> datetime | None:
    if not isinstance(payload, dict):
        return None
    for key in ("notified_at_utc", "timestamp_utc"):
        value = _parse_utc(payload.get(key))
        if value is not None:
            return value
    return None


def _candidate_has_signal(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return bool(str(payload.get("signal_id", "")).strip())


def _select_baseline(
    last_primary_notified: dict[str, Any] | None,
    last_attention_notified: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str]:
    candidates: list[tuple[datetime, dict[str, Any], str]] = []
    for payload, kind in (
        (last_primary_notified, "main"),
        (last_attention_notified, "attention"),
    ):
        if not _candidate_has_signal(payload):
            continue
        ts = _candidate_time(payload)
        if ts is None:
            continue
        candidates.append((ts, payload, kind))
    if not candidates:
        return None, ""
    candidates.sort(key=lambda item: item[0])
    _ts, payload, kind = candidates[-1]
    return payload, kind


def _setup_status(payload: dict[str, Any] | None, side: str) -> str:
    if not isinstance(payload, dict):
        return ""
    setup = payload.get(f"{side}_setup")
    if not isinstance(setup, dict):
        return ""
    return str(setup.get("status", "")).strip().lower()


def _confidence_drop_reason(
    *,
    baseline: dict[str, Any],
    current: dict[str, Any],
    minimum_drop: int,
    side: str,
) -> str | None:
    baseline_confidence = _float_value(baseline.get("confidence"))
    current_confidence = _float_value(current.get("confidence"))
    if baseline_confidence is None or current_confidence is None:
        return None
    if baseline_confidence - current_confidence < float(minimum_drop):
        return None
    return f"prior_{side}_confidence_drop"


def _has_any_text_token(payload: Any, *needles: str) -> bool:
    if payload is None:
        return False
    haystack = " ".join(_iter_text_values(payload)).lower()
    return any(needle in haystack for needle in needles)


def _followup_reason_codes(
    *,
    current: dict[str, Any],
    baseline: dict[str, Any],
    baseline_kind: str,
    confidence_drop_min: int,
) -> list[str]:
    side = str(baseline.get("bias", "")).strip().lower()
    reason_codes: list[str] = ["validity_expired"]

    if side == "long":
        if str(current.get("bias", "")).strip().lower() != "long":
            reason_codes.append("prior_long_bias_lost")
        if str(current.get("signals_1h", "")).strip().lower() in {"wait", "short"}:
            reason_codes.append("prior_long_1h_weakened")
        if _setup_status(current, "long") in {"", "invalid", "none"}:
            reason_codes.append("prior_long_setup_invalid")
        confidence_reason = _confidence_drop_reason(
            baseline=baseline,
            current=current,
            minimum_drop=confidence_drop_min,
            side="long",
        )
        if confidence_reason:
            reason_codes.append(confidence_reason)
        if _has_any_text_token(
            current.get("market_map_flags"),
            "support_to_resistance_flip",
            "support_to_resistance_retest_confirmed",
        ) or _has_any_text_token(current.get("level_flip_state"), "support_to_resistance"):
            reason_codes.append("prior_long_support_to_resistance")
        if _has_any_text_token(current.get("trend_flip_state"), "early_down", "trend_flip_down", "trend_flip_early_down") or _has_any_text_token(
            current.get("market_map_primary_state"),
            "early_down",
            "trend_flip",
            "transition_down",
        ):
            reason_codes.append("prior_long_trend_flip_early_down")
    elif side == "short":
        if str(current.get("bias", "")).strip().lower() != "short":
            reason_codes.append("prior_short_bias_lost")
        if str(current.get("signals_1h", "")).strip().lower() in {"wait", "long"}:
            reason_codes.append("prior_short_1h_weakened")
        if _setup_status(current, "short") in {"", "invalid", "none"}:
            reason_codes.append("prior_short_setup_invalid")
        confidence_reason = _confidence_drop_reason(
            baseline=baseline,
            current=current,
            minimum_drop=confidence_drop_min,
            side="short",
        )
        if confidence_reason:
            reason_codes.append(confidence_reason)
        if _has_any_text_token(
            current.get("market_map_flags"),
            "resistance_to_support_flip",
            "resistance_to_support_retest_confirmed",
        ) or _has_any_text_token(current.get("level_flip_state"), "resistance_to_support"):
            reason_codes.append("prior_short_resistance_to_support")
        if _has_any_text_token(current.get("trend_flip_state"), "early_up", "trend_flip_up", "trend_flip_early_up") or _has_any_text_token(
            current.get("market_map_primary_state"),
            "early_up",
            "trend_flip",
            "transition_up",
        ):
            reason_codes.append("prior_short_trend_flip_early_up")

    if baseline_kind == "attention" and not reason_codes:
        reason_codes.append("validity_expired")

    seen: set[str] = set()
    unique_reason_codes: list[str] = []
    for code in reason_codes:
        if code not in seen:
            seen.add(code)
            unique_reason_codes.append(code)
    return unique_reason_codes


def _reason_labels(reason_codes: list[str]) -> list[str]:
    labels: list[str] = []
    for code in reason_codes:
        label = FOLLOWUP_REASON_LABELS.get(code, code)
        labels.append(label)
    return labels


def build_followup_notification_context(followup_context: dict[str, Any]) -> dict[str, Any]:
    reason_codes = [str(code).strip() for code in followup_context.get("reason_codes", []) if str(code).strip()]
    reason_labels = _reason_labels(reason_codes)
    valid_until = str(followup_context.get("valid_until_utc") or "").strip() or "未記録"
    previous_signal_id = str(followup_context.get("previous_signal_id") or "").strip() or "未記録"
    previous_kind = str(followup_context.get("previous_notification_kind") or "").strip() or "未記録"
    subject_hint = str(followup_context.get("subject_hint") or FOLLOWUP_SUBJECT_HINT).strip()
    human_message = str(followup_context.get("human_message") or FOLLOWUP_HUMAN_MESSAGE).strip()
    return {
        "status_label": "再評価中",
        "status_explanation": "前回通知の有効期限切れを確認し、根拠を再評価します",
        "final_rank_label": "期限切れ・再評価",
        "final_rank_emoji": "⏱️",
        "final_rank_explanation": "前回通知の有効期限切れ / 根拠再確認",
        "execution_label": "再評価",
        "entry_window_label": "前回通知の期限切れを確認",
        "validity_label": f"前回通知の有効期限: {valid_until}",
        "next_condition_label": "前回通知を新規根拠として使わず、次の通常通知で再評価",
        "invalidation_label": "前回通知の有効期限が切れたら再確認",
        "rr_summary_label": "再評価 / 期限切れの確認",
        "active_subject_label": FOLLOWUP_PUBLIC_LABEL,
        "active_headline": subject_hint,
        "reason_labels": reason_labels or ["有効期限切れ"],
        "reason_labels_full": reason_labels or ["有効期限切れ"],
        "followup_previous_signal_id": previous_signal_id,
        "followup_previous_notification_kind": previous_kind,
        "followup_valid_until_utc": valid_until,
        "followup_reason_codes": reason_codes,
        "followup_reason_labels": reason_labels,
        "followup_human_message": human_message,
        "followup_safety_boundary": FOLLOWUP_SAFETY_BOUNDARY,
    }


def evaluate_followup_notification(
    current: dict[str, Any],
    last_primary_notified: dict[str, Any] | None,
    last_attention_notified: dict[str, Any] | None,
    last_followup_notified: dict[str, Any] | None,
    cfg: Any,
) -> dict[str, Any]:
    baseline, baseline_kind = _select_baseline(last_primary_notified, last_attention_notified)
    default_context = {
        "followup_needed": False,
        "followup_kind": "followup",
        "previous_signal_id": "",
        "previous_notification_kind": "",
        "valid_until_utc": "",
        "reason_codes": [],
        "reason_labels": [],
        "subject_hint": FOLLOWUP_PUBLIC_LABEL,
        "human_message": FOLLOWUP_HUMAN_MESSAGE,
        "safety_boundary": FOLLOWUP_SAFETY_BOUNDARY,
        "followup_for_signal_id": "",
        "baseline_timestamp_utc": "",
        "baseline_notified_at_utc": "",
    }
    if baseline is None:
        return default_context

    current_ts = _parse_utc(current.get("timestamp_utc"))
    baseline_ts = _candidate_time(baseline)
    if current_ts is None or baseline_ts is None:
        return default_context

    validity_minutes = int(getattr(cfg, "FOLLOWUP_VALIDITY_MINUTES", 60) or 60)
    cooldown_minutes = int(getattr(cfg, "FOLLOWUP_ALERT_COOLDOWN_MINUTES", 60) or 60)
    confidence_drop_min = int(getattr(cfg, "FOLLOWUP_CONFIDENCE_DROP_MIN", 10) or 10)
    valid_until = baseline_ts + timedelta(minutes=validity_minutes)
    baseline_signal_id = str(baseline.get("signal_id", "")).strip()
    baseline_followup_id = str((last_followup_notified or {}).get("followup_for_signal_id", "")).strip()
    if baseline_followup_id and baseline_followup_id == baseline_signal_id:
        return {
            **default_context,
            "previous_signal_id": baseline_signal_id,
            "previous_notification_kind": baseline_kind,
            "valid_until_utc": valid_until.isoformat().replace("+00:00", "Z"),
            "followup_for_signal_id": baseline_signal_id,
        }

    expired = current_ts > valid_until
    if not expired:
        return {
            **default_context,
            "previous_signal_id": baseline_signal_id,
            "previous_notification_kind": baseline_kind,
            "valid_until_utc": valid_until.isoformat().replace("+00:00", "Z"),
            "followup_for_signal_id": baseline_signal_id,
        }

    reason_codes = _followup_reason_codes(
        current=current,
        baseline=baseline,
        baseline_kind=baseline_kind,
        confidence_drop_min=confidence_drop_min,
    )
    last_followup_ts = _candidate_time(last_followup_notified)
    invalidation_codes = [code for code in reason_codes if code != "validity_expired"]
    cooldown_active = bool(last_followup_ts and current_ts - last_followup_ts < timedelta(minutes=cooldown_minutes))
    if cooldown_active and not invalidation_codes:
        return {
            **default_context,
            "previous_signal_id": baseline_signal_id,
            "previous_notification_kind": baseline_kind,
            "valid_until_utc": valid_until.isoformat().replace("+00:00", "Z"),
            "followup_for_signal_id": baseline_signal_id,
            "reason_codes": reason_codes,
            "reason_labels": _reason_labels(reason_codes),
        }

    reason_labels = _reason_labels(reason_codes)
    subject_hint = FOLLOWUP_SUBJECT_HINT
    human_message = FOLLOWUP_HUMAN_MESSAGE
    return {
        "followup_needed": True,
        "followup_kind": "followup",
        "previous_signal_id": baseline_signal_id,
        "previous_notification_kind": baseline_kind,
        "valid_until_utc": valid_until.isoformat().replace("+00:00", "Z"),
        "reason_codes": reason_codes,
        "reason_labels": reason_labels,
        "subject_hint": subject_hint,
        "human_message": human_message,
        "safety_boundary": FOLLOWUP_SAFETY_BOUNDARY,
        "followup_for_signal_id": baseline_signal_id,
        "baseline_timestamp_utc": baseline_ts.isoformat().replace("+00:00", "Z"),
        "baseline_notified_at_utc": (_candidate_time(baseline) or baseline_ts).isoformat().replace("+00:00", "Z"),
        "baseline_bias": str(baseline.get("bias", "")).strip().lower(),
    }
