"""Sanitized report-only P7 shadow surface adapter."""
from __future__ import annotations

import hashlib
from typing import Any

from src.feedback.manual_operator_classifier import SAFETY, classify_manual_operator_candidate
from src.storage.csv_logger import build_current_result_candidate_rows, build_current_result_signal_context

SCHEMA_VERSION = "manual_operator_shadow_surface.v1"
METHOD_VERSION = "manual_operator_classifier.v1"
_ORDER = {"STOP_OR_EXIT": 0, "A_FORMAL": 1, "B_CHECK_15M": 2, "C_WATCH_ZONE": 3}
_FIELDS = ("shadow_row_id", "classification_status", "operator_class", "side", "candidate_type", "candidate_status", "required_human_check", "reason_codes", "warning_codes", "trade_execution_gate", "phase1b_lite_gate", "opportunity_gate", "entry_price", "entry_zone_low", "entry_zone_high", "invalidation_price", "tp1_price", "tp2_price")


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode()).hexdigest()[:24]


def _row(result: dict[str, Any], candidate: dict[str, Any], signal: dict[str, Any]) -> dict[str, str]:
    side = str(candidate.get("side") or "").strip().lower()
    timestamp = result.get("timestamp_utc") or result.get("timestamp_jst") or signal.get("timestamp_utc") or signal.get("timestamp_jst") or ""
    event = {
        "scenario_event_id": "", "scenario_id": "", "candidate_id": "", "source_signal_id": candidate.get("source_signal_id") or signal.get("signal_id") or "",
        "event_timestamp_utc": timestamp, "event_timestamp_jst": timestamp, "grouping_status": "new_scenario", "symbol": result.get("symbol") or "", "side": side,
        "setup_family": candidate.get("candidate_type") or "", "candidate_status": candidate.get("candidate_status") or "", "entry_price": candidate.get("entry_price") or "", "entry_zone_low": candidate.get("entry_zone_low") or "", "entry_zone_high": candidate.get("entry_zone_high") or "",
    }
    cand = dict(candidate); cand["timestamp_jst"] = cand.get("timestamp_jst") or timestamp; cand.setdefault("candidate_id", "shadow"); cand.setdefault("candidate_type", candidate.get("candidate_type", "")); cand.setdefault("source_signal_id", event["source_signal_id"])
    sig = {key: (value if value is not None else "") for key, value in dict(signal).items()}; sig["signal_id"] = sig.get("signal_id") or event["source_signal_id"]; sig["timestamp_jst"] = sig.get("timestamp_jst") or timestamp; sig["primary_setup_status"] = sig.get("primary_setup_status") or ""; sig["data_quality_flag"] = sig.get("data_quality_flag") or ""
    classified = classify_manual_operator_candidate(event, cand, sig)
    operator_class = classified.get("operator_class", "")
    row = {field: "" for field in _FIELDS}
    row.update({field: str(classified.get(field, "") or "") for field in _FIELDS if field in classified})
    row["shadow_row_id"] = "shd_" + _hash(timestamp, side, candidate.get("candidate_type", ""), candidate.get("candidate_status", ""), candidate.get("entry_price", ""), candidate.get("entry_zone_low", ""), candidate.get("entry_zone_high", ""))
    row["candidate_type"] = str(candidate.get("candidate_type", "") or "")
    row["candidate_status"] = str(candidate.get("candidate_status", "") or "")
    row["side"] = side
    row["classification_status"] = classified.get("classification_status", "insufficient_evidence")
    row["operator_class"] = operator_class
    row["entry_price"] = str(candidate.get("entry_price", "") or "")
    row["entry_zone_low"] = str(candidate.get("entry_zone_low", "") or "")
    row["entry_zone_high"] = str(candidate.get("entry_zone_high", "") or "")
    row["invalidation_price"] = str(candidate.get("stop_loss", "") or "")
    row["tp1_price"] = str(candidate.get("tp1", "") or "")
    row["tp2_price"] = str(candidate.get("tp2", "") or "")
    return row


def build_manual_operator_shadow_surface(result: dict[str, Any]) -> dict[str, Any]:
    try:
        if not isinstance(result, dict):
            return {"schema_version": SCHEMA_VERSION, "surface_status": "malformed", "classifier_method_version": METHOD_VERSION, "candidate_count": 0, "rows": [], "safety_boundary": SAFETY}
        signal = build_current_result_signal_context(result)
        candidates = build_current_result_candidate_rows(result)
        if not candidates:
            return {"schema_version": SCHEMA_VERSION, "surface_status": "no_current_candidate", "classifier_method_version": METHOD_VERSION, "candidate_count": 0, "rows": [], "safety_boundary": SAFETY}
        rows = [_row(result, candidate, signal) for candidate in candidates]
        rows.sort(key=lambda row: (_ORDER.get(row.get("operator_class", ""), 4), row.get("side", ""), row.get("candidate_type", ""), row.get("shadow_row_id", "")))
        status = "ready" if any(row.get("classification_status") == "classified" for row in rows) else "insufficient_evidence"
        return {"schema_version": SCHEMA_VERSION, "surface_status": status, "classifier_method_version": METHOD_VERSION, "candidate_count": len(rows), "rows": [{field: row.get(field, "") for field in _FIELDS} for row in rows], "safety_boundary": SAFETY}
    except Exception:
        return {"schema_version": SCHEMA_VERSION, "surface_status": "malformed", "classifier_method_version": METHOD_VERSION, "candidate_count": 0, "rows": [], "safety_boundary": SAFETY}
