"""Offline event-time operator hypothesis classifier for P5.

This module consumes contemporaneous evidence only.  It does not recompute
production gates and it never authorizes an order.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from src.feedback.manual_scenario_normalizer import EVENT_HEADERS, EVENT_SCHEMA_VERSION, SCENARIO_HEADERS, SCENARIO_SCHEMA_VERSION

SCHEMA_VERSION = "manual_operator_classification.v1"
REPORT_SCHEMA_VERSION = "manual_operator_classifier_report.v1"
METHOD_VERSION = "manual_operator_classifier.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
JST = ZoneInfo("Asia/Tokyo")
CLASSES = ("STOP_OR_EXIT", "A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE")
STATUS_VALUES = ("classified", "insufficient_evidence", "ambiguous_grouping")
ALLOWED_GROUPING = {"new_scenario", "matched_existing", "ambiguous"}
CANDIDATE_HEADERS = [
    "candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "candidate_status", "side",
    "entry_mode", "entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2",
    "rr_current_tp1", "rr_current_tp2", "rr_zone_mid_tp1", "rr_zone_mid_tp2", "market_entry_status",
    "limit_entry_status", "counter_scalp_status", "breakout_status", "next_condition",
]
SIGNAL_HEADERS = [
    "signal_id", "timestamp_jst", "current_price", "bias", "market_regime", "transition_direction",
    "primary_setup_side", "primary_setup_status", "confidence_direction_shadow", "confidence_execution_shadow",
    "confidence_wait_shadow", "prelabel", "trade_execution_gate", "trade_execution_blockers",
    "phase1b_lite_gate", "phase1b_lite_type", "phase1b_lite_reasons", "opportunity_gate", "opportunity_type",
    "opportunity_reasons", "signal_tier", "data_quality_flag", "no_trade_flags", "warning_flags", "risk_flags",
    "long_rr", "short_rr", "trend_flip_state", "active_level_role", "level_flip_state", "failed_breakout_state",
    "nearest_major_support", "nearest_major_resistance",
]
CANDIDATE_NUMERIC_FIELDS = frozenset({
    "entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2",
    "rr_current_tp1", "rr_current_tp2", "rr_zone_mid_tp1", "rr_zone_mid_tp2",
})
SIGNAL_NUMERIC_FIELDS = frozenset({
    "current_price", "confidence_direction_shadow", "confidence_execution_shadow", "confidence_wait_shadow",
    "long_rr", "short_rr", "nearest_major_support", "nearest_major_resistance",
})
OUTPUT_HEADERS = [
    "schema_version", "classification_id", "classifier_method_version", "scenario_event_id", "scenario_id",
    "candidate_id", "source_signal_id", "event_timestamp_utc", "event_timestamp_jst", "symbol", "side",
    "setup_family", "market_regime", "transition_direction", "classification_status", "operator_class",
    "priority_rank", "reason_codes", "warning_codes", "required_human_check", "trade_execution_gate",
    "trade_execution_blockers", "phase1b_lite_gate", "phase1b_lite_type", "opportunity_gate", "opportunity_type",
    "prelabel", "signal_tier", "primary_setup_status", "primary_setup_side", "candidate_status", "entry_mode",
    "entry_price", "entry_zone_low", "entry_zone_high", "invalidation_price", "tp1_price", "tp2_price",
    "rr_tp1_used", "rr_tp2_used", "confidence_direction_shadow", "confidence_execution_shadow",
    "confidence_wait_shadow", "data_quality_flag", "no_trade_flags", "risk_flags", "source_join_status",
    "short_direction_min", "short_execution_min", "short_wait_max", "short_tp1_rr_min", "short_tp2_rr_min",
    "long_direction_min", "long_execution_min", "long_wait_max", "long_tp1_rr_min", "long_tp2_rr_min",
]
REASON_FUTURE = "future_context_rejected"
_SENSITIVE = re.compile(r"(?:/private/|file://|api[_-]?key|secret|password|uid_|account[_-])", re.I)


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace(" ", "T")
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=JST)
    return parsed


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _jst(value: datetime) -> str:
    return value.astimezone(JST).isoformat()


def _dec(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        parsed = Decimal(text)
        return parsed if parsed.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def _dec_text(value: Any) -> str:
    parsed = _dec(value)
    if parsed is None:
        return ""
    normalized = parsed.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


def _tokens(value: Any) -> tuple[str, ...]:
    if isinstance(value, (list, tuple, set)):
        return tuple(sorted({str(token).strip().lower() for token in value if str(token).strip()}))
    text = str(value or "").strip()
    if not text:
        return ()
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return tuple(sorted({str(token).strip().lower() for token in parsed if str(token).strip()}))
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
    return tuple(sorted({token.strip().lower() for token in re.split(r"[;,|]", text) if token.strip()}))


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode()).hexdigest()


def _read_csv(path: Path, required: list[str], version: str | None = None, exact: list[str] | None = None) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            fields = reader.fieldnames or []
            if exact is not None and fields != exact:
                return [], "input_schema_mismatch"
            if any(item not in fields for item in required):
                return [], "input_schema_mismatch"
            rows = [{str(key): str(value or "").strip() for key, value in row.items()} for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"
    if version and any(row.get("schema_version") != version for row in rows):
        return [], "input_schema_mismatch"
    return rows, None


def _fingerprint(row: dict[str, str], fields: list[str]) -> str:
    values = []
    for field in fields:
        value = row.get(field, "")
        if field in {"timestamp_jst", "event_timestamp_jst", "event_timestamp_utc"}:
            parsed = _dt(value)
            value = _jst(parsed) if parsed else value
        elif field in CANDIDATE_NUMERIC_FIELDS or field in SIGNAL_NUMERIC_FIELDS:
            value = _dec_text(value) if value else ""
        elif field in {"no_trade_flags", "warning_flags", "risk_flags", "trade_execution_blockers", "phase1b_lite_reasons", "opportunity_reasons"}:
            value = ";".join(_tokens(value))
        else:
            value = str(value or "").strip().lower()
        values.append(value)
    return _hash(*values)[:32]


def _identity_rows(rows: list[dict[str, str]], identity_field: str, fields: list[str]) -> tuple[dict[str, dict[str, str]], int, str | None]:
    result: dict[str, dict[str, str]] = {}
    fingerprints: dict[str, str] = {}
    duplicates = 0
    for row in rows:
        identity = row.get(identity_field, "").strip()
        if not identity:
            return {}, duplicates, "input_schema_mismatch"
        if "timestamp_jst" in fields and row.get("timestamp_jst") and _dt(row.get("timestamp_jst")) is None:
            return {}, duplicates, "invalid_timestamp"
        numeric_fields = (CANDIDATE_NUMERIC_FIELDS | SIGNAL_NUMERIC_FIELDS) & set(fields)
        if any(row.get(field, "") and _dec(row.get(field)) is None for field in numeric_fields):
            return {}, duplicates, "invalid_numeric"
        fp = _fingerprint(row, fields)
        if identity in result:
            if fingerprints[identity] == fp:
                duplicates += 1
                continue
            return {}, duplicates, "identity_conflict"
        result[identity] = row
        fingerprints[identity] = fp
        row["_normalized_fingerprint"] = fp
    return result, duplicates, None


def _validate_event_inputs(scenarios: list[dict[str, str]], events: list[dict[str, str]]) -> str | None:
    scenario_ids = [row.get("scenario_id", "") for row in scenarios]
    if any(not value for value in scenario_ids) or len(set(scenario_ids)) != len(scenario_ids):
        return "input_schema_mismatch"
    known = set(scenario_ids)
    event_ids = [row.get("scenario_event_id", "") for row in events]
    if any(not value for value in event_ids) or len(set(event_ids)) != len(event_ids):
        return "input_schema_mismatch"
    candidate_ids: set[str] = set()
    for row in events:
        grouping = row.get("grouping_status", "")
        sid = row.get("scenario_id", "")
        if grouping not in ALLOWED_GROUPING:
            return "input_schema_mismatch"
        if grouping == "ambiguous" and sid:
            return "input_schema_mismatch"
        if grouping != "ambiguous" and (not sid or sid not in known):
            return "input_schema_mismatch"
        if not row.get("candidate_id") or row["candidate_id"] in candidate_ids:
            return "input_schema_mismatch"
        candidate_ids.add(row["candidate_id"])
    return None


def _threshold_defaults() -> dict[str, Decimal]:
    return {
        "short_direction_min": Decimal("55"), "short_execution_min": Decimal("18"), "short_wait_max": Decimal("75"),
        "short_tp1_rr_min": Decimal("0.8"), "short_tp2_rr_min": Decimal("1.5"), "long_direction_min": Decimal("60"),
        "long_execution_min": Decimal("22"), "long_wait_max": Decimal("70"), "long_tp1_rr_min": Decimal("1.0"), "long_tp2_rr_min": Decimal("1.8"),
    }


def _threshold_text(value: Decimal) -> str:
    return format(value, "f")


def _rr_values(candidate: dict[str, str], signal: dict[str, str], side: str) -> tuple[Decimal | None, Decimal | None]:
    zone_tp1 = str(candidate.get("rr_zone_mid_tp1", "")).strip()
    zone_tp2 = str(candidate.get("rr_zone_mid_tp2", "")).strip()
    tp1 = _dec(zone_tp1) if zone_tp1 else (_dec(candidate.get("rr_current_tp1")) if str(candidate.get("rr_current_tp1", "")).strip() else None)
    tp2 = _dec(zone_tp2) if zone_tp2 else (_dec(candidate.get("rr_current_tp2")) if str(candidate.get("rr_current_tp2", "")).strip() else None)
    if side == "long":
        tp1 = tp1 if tp1 is not None else _dec(signal.get("long_rr"))
    else:
        tp1 = tp1 if tp1 is not None else _dec(signal.get("short_rr"))
    return tp1, tp2


def _missing_shadow(signal: dict[str, str]) -> bool:
    return any(_dec(signal.get(field)) is None for field in ("confidence_direction_shadow", "confidence_execution_shadow", "confidence_wait_shadow"))


def _base_row(event: dict[str, str], candidate: dict[str, str], signal: dict[str, str], status: str, operator_class: str = "", reasons: tuple[str, ...] = (), warning: tuple[str, ...] = (), required_check: str = "") -> dict[str, str]:
    event_dt = _dt(event.get("event_timestamp_utc") or event.get("event_timestamp_jst"))
    side = event.get("side", "").lower()
    tp1, tp2 = _rr_values(candidate, signal, side)
    row = {key: "" for key in OUTPUT_HEADERS}
    row.update({
        "schema_version": SCHEMA_VERSION, "classifier_method_version": METHOD_VERSION,
        "scenario_event_id": event.get("scenario_event_id", ""), "scenario_id": event.get("scenario_id", ""),
        "candidate_id": event.get("candidate_id", ""), "source_signal_id": event.get("source_signal_id", ""),
        "event_timestamp_utc": _utc(event_dt) if event_dt else "", "event_timestamp_jst": _jst(event_dt) if event_dt else "",
        "symbol": event.get("symbol", ""), "side": side, "setup_family": event.get("setup_family", ""),
        "market_regime": signal.get("market_regime", ""), "transition_direction": signal.get("transition_direction", ""),
        "classification_status": status, "operator_class": operator_class,
        "priority_rank": str(CLASSES.index(operator_class) + 1) if operator_class in CLASSES else "",
        "reason_codes": ";".join(sorted(set(reasons))), "warning_codes": ";".join(sorted(set(warning))), "required_human_check": required_check,
        "trade_execution_gate": signal.get("trade_execution_gate", ""), "trade_execution_blockers": ";".join(_tokens(signal.get("trade_execution_blockers"))),
        "phase1b_lite_gate": signal.get("phase1b_lite_gate", ""), "phase1b_lite_type": signal.get("phase1b_lite_type", ""),
        "opportunity_gate": signal.get("opportunity_gate", ""), "opportunity_type": signal.get("opportunity_type", ""),
        "prelabel": signal.get("prelabel", ""), "signal_tier": signal.get("signal_tier", ""),
        "primary_setup_status": signal.get("primary_setup_status", ""), "primary_setup_side": signal.get("primary_setup_side", ""),
        "candidate_status": candidate.get("candidate_status", event.get("candidate_status", "")), "entry_mode": candidate.get("entry_mode", event.get("entry_mode", "")),
        "entry_price": candidate.get("entry_price", event.get("entry_price", "")), "entry_zone_low": candidate.get("entry_zone_low", event.get("entry_zone_low", "")),
        "entry_zone_high": candidate.get("entry_zone_high", event.get("entry_zone_high", "")), "invalidation_price": candidate.get("stop_loss", event.get("invalidation_price", "")),
        "tp1_price": candidate.get("tp1", event.get("tp1_price", "")), "tp2_price": candidate.get("tp2", event.get("tp2_price", "")),
        "rr_tp1_used": _threshold_text(tp1) if tp1 is not None else "", "rr_tp2_used": _threshold_text(tp2) if tp2 is not None else "",
        "confidence_direction_shadow": signal.get("confidence_direction_shadow", ""), "confidence_execution_shadow": signal.get("confidence_execution_shadow", ""), "confidence_wait_shadow": signal.get("confidence_wait_shadow", ""),
        "data_quality_flag": signal.get("data_quality_flag", ""), "no_trade_flags": ";".join(_tokens(signal.get("no_trade_flags"))), "risk_flags": ";".join(_tokens(signal.get("risk_flags"))),
        "source_join_status": "complete" if candidate and signal else "incomplete",
    })
    row["warning_codes"] = ";".join(_tokens(signal.get("warning_flags")))
    return row


def _classify(event: dict[str, str], candidate: dict[str, str], signal: dict[str, str], thresholds: dict[str, Decimal]) -> dict[str, str]:
    if event.get("grouping_status") == "ambiguous":
        return _base_row(event, candidate, signal, "ambiguous_grouping", reasons=("ambiguous_scenario_assignment",))
    if not candidate or not signal:
        return _base_row(event, candidate, signal, "insufficient_evidence", reasons=("missing_candidate_context" if not candidate else "missing_signal_context",))
    event_dt = _dt(event.get("event_timestamp_utc") or event.get("event_timestamp_jst"))
    candidate_dt = _dt(candidate.get("timestamp_jst"))
    signal_dt = _dt(signal.get("timestamp_jst"))
    if event_dt is None or candidate_dt is None or signal_dt is None:
        return _base_row(event, candidate, signal, "insufficient_evidence", reasons=("missing_timestamp",))
    if candidate_dt > event_dt or signal_dt > event_dt:
        raise ValueError("future_context")
    quality = signal.get("data_quality_flag", "").strip().lower()
    no_trade = _tokens(signal.get("no_trade_flags"))
    candidate_status = candidate.get("candidate_status", event.get("candidate_status", "")).strip().lower()
    stop_reasons: list[str] = []
    if quality and quality != "ok":
        stop_reasons.append("stop_data_quality")
    if no_trade:
        stop_reasons.append("stop_no_trade_flag")
    if candidate_status in {"invalidated", "cancelled", "expired"}:
        stop_reasons.append("stop_candidate_" + candidate_status)
    if stop_reasons:
        return _base_row(event, candidate, signal, "classified", "STOP_OR_EXIT", reasons=tuple(sorted(set(stop_reasons))), required_check="human_review_only")
    side = event.get("side", "").strip().lower()
    setup_status = signal.get("primary_setup_status", "").strip().lower()
    setup_side = signal.get("primary_setup_side", "").strip().lower()
    gate = signal.get("trade_execution_gate", "").strip().lower()
    a_ok = gate == "pass" and quality == "ok" and not no_trade and setup_status == "ready" and setup_side == side
    if a_ok:
        return _base_row(event, candidate, signal, "classified", "A_FORMAL", reasons=("formal_gate_pass", "formal_data_quality_ok", "formal_setup_ready", "formal_side_match"), required_check="confirm_15m_before_manual_action")
    if _missing_shadow(signal):
        return _base_row(event, candidate, signal, "insufficient_evidence", reasons=("missing_required_shadow_metric",))
    direction = _dec(signal.get("confidence_direction_shadow")); execution = _dec(signal.get("confidence_execution_shadow")); wait = _dec(signal.get("confidence_wait_shadow"))
    tp1, tp2 = _rr_values(candidate, signal, side)
    if tp1 is None and tp2 is None:
        return _base_row(event, candidate, signal, "insufficient_evidence", reasons=("missing_required_rr",))
    direction_min = thresholds[f"{side}_direction_min"] if side in {"long", "short"} else Decimal("0")
    execution_min = thresholds[f"{side}_execution_min"] if side in {"long", "short"} else Decimal("0")
    wait_max = thresholds[f"{side}_wait_max"] if side in {"long", "short"} else Decimal("0")
    rr_ok = (tp1 is not None and tp1 >= thresholds[f"{side}_tp1_rr_min"]) or (tp2 is not None and tp2 >= thresholds[f"{side}_tp2_rr_min"])
    eligible = candidate_status in {"allowed", "conditional", "armed", "watch"}
    entry_defined = bool(candidate.get("entry_price") or candidate.get("entry_zone_low") or candidate.get("entry_zone_high") or event.get("entry_price") or event.get("entry_zone_low"))
    non_gate_b = bool(quality == "ok" and not no_trade and entry_defined and direction is not None and execution is not None and wait is not None and direction >= direction_min and execution >= execution_min and wait <= wait_max and rr_ok and eligible and setup_side == side and (side != "long" or setup_status == "ready") and (side != "short" or setup_status in {"ready", "watch"}))
    if non_gate_b and (gate == "blocked" or (gate == "pass" and not a_ok)):
        reasons = ("b_shadow_thresholds_pass", "b_rr_threshold_pass", "b_setup_eligible", "b_side_match")
        if gate == "blocked": reasons += ("b_formal_gate_not_pass",)
        else: reasons += ("formal_evidence_incomplete",)
        return _base_row(event, candidate, signal, "classified", "B_CHECK_15M", reasons=reasons, required_check="check_15m_trigger_then_human_decides")
    if side in {"long", "short"} and setup_side and setup_side != side:
        return _base_row(event, candidate, signal, "insufficient_evidence", reasons=("side_mismatch",), required_check="human_review_only")
    if entry_defined and eligible and side in {"long", "short"} and setup_side == side:
        reasons = []
        if direction < direction_min: reasons.append("c_wait_direction_below_threshold")
        if execution < execution_min: reasons.append("c_wait_execution_below_threshold")
        if wait > wait_max: reasons.append("c_wait_pressure_above_threshold")
        if not rr_ok: reasons.append("c_wait_rr_below_threshold")
        if setup_status != "ready": reasons.append("c_wait_setup_not_ready")
        return _base_row(event, candidate, signal, "classified", "C_WATCH_ZONE", reasons=tuple(reasons or ["c_wait_formal_or_b_evidence_incomplete"]), required_check="watch_zone_and_wait_for_upgrade")
    return _base_row(event, candidate, signal, "insufficient_evidence", reasons=("missing_entry_definition",))


def classify_manual_operator_candidate(
    event: dict[str, str],
    candidate: dict[str, str],
    signal: dict[str, str],
    thresholds: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Pure single-candidate adapter shared by P5 batch and P7 shadow surface."""
    resolved = _threshold_defaults()
    for key, value in (thresholds or {}).items():
        parsed = value if isinstance(value, Decimal) else _dec(value)
        if parsed is not None and key in resolved:
            resolved[key] = parsed
    return _classify(dict(event), dict(candidate), dict(signal), resolved)


def _atomic_three(paths_text: list[tuple[Path, str]]) -> None:
    temps: list[tuple[Path, Path]] = []
    backups: list[tuple[Path, Path]] = []
    replaced: list[Path] = []
    try:
        for path, text in paths_text:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=".p5-", dir=path.parent)
            os.close(fd)
            temp = Path(name); temp.write_text(text, encoding="utf-8"); temps.append((path, temp))
        for path, _ in temps:
            if path.exists():
                backup = path.with_name(f".{path.name}.p5-backup"); backup.unlink(missing_ok=True); path.replace(backup); backups.append((path, backup))
        for path, temp in temps:
            temp.replace(path); replaced.append(path)
    except Exception as exc:
        for path in replaced: path.unlink(missing_ok=True)
        for path, backup in backups:
            if backup.exists(): backup.replace(path)
        raise OSError("output_transaction_failed") from exc
    finally:
        for _, temp in temps: temp.unlink(missing_ok=True)
        for _, backup in backups: backup.unlink(missing_ok=True)


def _markdown(payload: dict[str, Any]) -> str:
    lines = ["# Manual Operator Classifier Report", "", "## Purpose", "", "Offline hypothesis only. This is not FORMAL_GO; no automatic order is created and a human decides manually.", "", "## Input Status", "", f"- scenario_event_input_rows: {payload['scenario_event_input_rows']}", f"- candidate_context_rows: {payload['candidate_context_rows']}", f"- signal_context_rows: {payload['signal_context_rows']}", "", "## Method and No-Leakage Boundary", "", "Event-time evidence only. Outcome, actual trade, and human decision evidence are not classifier inputs. A/B/C/STOP does not replace existing gates.", "", "## Threshold Snapshot", ""]
    for key, value in payload["thresholds"].items(): lines.append(f"- {key}: {value}")
    lines += ["", "## Classification Coverage", "", f"- classified_rows: {payload['classified_rows']}", f"- insufficient_evidence_rows: {payload['insufficient_evidence_rows']}", f"- ambiguous_event_rows: {payload['ambiguous_event_rows']}", "", "## Class Distribution", ""]
    for name in (*CLASSES, "insufficient_evidence"): lines.append(f"- {name}: {payload['class_counts'].get(name, payload['insufficient_evidence_rows'] if name == 'insufficient_evidence' else 0)}")
    lines += ["", "## Side Breakdown", json.dumps(payload["side_class_counts"], ensure_ascii=False, sort_keys=True), "", "## Regime Breakdown", json.dumps(payload["regime_class_counts"], ensure_ascii=False, sort_keys=True), "", "## Setup-Family Breakdown", json.dumps(payload["setup_family_class_counts"], ensure_ascii=False, sort_keys=True), "", "## Existing Gate Comparison", f"- formal_gate_pass_rows: {payload['formal_gate_pass_rows']}", f"- formal_pass_not_a_rows: {payload['formal_pass_not_a_rows']}", "- B thresholds are comparison values, not production settings.", "", "## Warnings and Risks", f"- warning_token_counts: {json.dumps(payload['warning_token_counts'], sort_keys=True)}", f"- risk_token_counts: {json.dumps(payload['risk_token_counts'], sort_keys=True)}", f"- no_trade_token_counts: {json.dumps(payload['no_trade_token_counts'], sort_keys=True)}", "", "## Limitations", "- No P5 profitability evaluation exists.", "- Outcome, actual trade, and human decision evidence are not classifier inputs.", "- This report does not modify gates, thresholds, notifications, runtime, or orders.", "", "## Safety Boundary", SAFETY, ""]
    return "\n".join(lines)


def build_manual_operator_classifier(*, scenarios: Path, scenario_events: Path, candidates: Path, signal_context: Path, output_csv: Path, output_json: Path, output_md: Path, report_date: str, thresholds: dict[str, Any] | None = None, dry_run: bool = False, replace_output: bool = False) -> dict[str, Any]:
    threshold_values = _threshold_defaults()
    for key, value in (thresholds or {}).items():
        parsed = _dec(value)
        if parsed is None or ("rr" not in key and not Decimal("0") <= parsed <= Decimal("100")) or ("rr" in key and parsed < 0):
            return {"ok": False, "exit_code": 2, "errors": ["invalid_threshold"], "report_written": False, "safety_boundary": SAFETY}
        if key in threshold_values: threshold_values[key] = parsed
    scenario_rows, error = _read_csv(scenarios, [], SCENARIO_SCHEMA_VERSION, SCENARIO_HEADERS)
    if error: return {"ok": False, "exit_code": 2, "errors": [error], "report_written": False, "safety_boundary": SAFETY}
    event_rows, error = _read_csv(scenario_events, [], EVENT_SCHEMA_VERSION, EVENT_HEADERS)
    if error: return {"ok": False, "exit_code": 2, "errors": [error], "report_written": False, "safety_boundary": SAFETY}
    error = _validate_event_inputs(scenario_rows, event_rows)
    if error: return {"ok": False, "exit_code": 2, "errors": [error], "report_written": False, "safety_boundary": SAFETY}
    candidate_rows, error = _read_csv(candidates, CANDIDATE_HEADERS)
    if error: return {"ok": False, "exit_code": 2, "errors": [error], "report_written": False, "safety_boundary": SAFETY}
    signal_rows, error = _read_csv(signal_context, SIGNAL_HEADERS)
    if error: return {"ok": False, "exit_code": 2, "errors": [error], "report_written": False, "safety_boundary": SAFETY}
    candidates_by_id, candidate_dupes, error = _identity_rows(candidate_rows, "candidate_id", CANDIDATE_HEADERS)
    if error: return {"ok": False, "exit_code": 3 if error == "identity_conflict" else 2, "errors": [error], "report_written": False, "safety_boundary": SAFETY}
    signals_by_id, signal_dupes, error = _identity_rows(signal_rows, "signal_id", SIGNAL_HEADERS)
    if error: return {"ok": False, "exit_code": 3 if error == "identity_conflict" else 2, "errors": [error], "report_written": False, "safety_boundary": SAFETY}
    rows: list[dict[str, str]] = []
    formal_pass = 0
    for event in event_rows:
        candidate = candidates_by_id.get(event.get("candidate_id", ""), {})
        signal = signals_by_id.get(event.get("source_signal_id", ""), {})
        if event.get("side", "").strip().lower() not in {"long", "short"}:
            return {"ok": False, "exit_code": 2, "errors": ["invalid_side"], "report_written": False, "safety_boundary": SAFETY}
        if candidate and candidate.get("source_signal_id", "") != event.get("source_signal_id", ""):
            return {"ok": False, "exit_code": 2, "errors": ["source_signal_mismatch"], "report_written": False, "safety_boundary": SAFETY}
        if _dt(event.get("event_timestamp_utc") or event.get("event_timestamp_jst")) is None or (candidate and _dt(candidate.get("timestamp_jst")) is None) or (signal and _dt(signal.get("timestamp_jst")) is None):
            return {"ok": False, "exit_code": 2, "errors": ["invalid_timestamp"], "report_written": False, "safety_boundary": SAFETY}
        try:
            row = classify_manual_operator_candidate(event, candidate, signal, threshold_values)
        except ValueError as exc:
            if str(exc) == "future_context":
                return {"ok": False, "exit_code": 2, "errors": ["future_context"], "report_written": False, "safety_boundary": SAFETY}
            raise
        rows.append(row)
        for key, value in threshold_values.items():
            row[key] = _threshold_text(value)
        if signal.get("trade_execution_gate", "").strip().lower() == "pass": formal_pass += 1
    rows.sort(key=lambda row: (row.get("event_timestamp_utc", ""), row.get("scenario_event_id", ""), row.get("classification_id", "")))
    threshold_order = tuple(_threshold_text(threshold_values[key]) for key in threshold_values)
    for row in rows:
        candidate_fp = candidates_by_id.get(row.get("candidate_id", ""), {}).get("_normalized_fingerprint", "")
        signal_fp = signals_by_id.get(row.get("source_signal_id", ""), {}).get("_normalized_fingerprint", "")
        row["classification_id"] = "opc_" + _hash(row.get("scenario_event_id"), candidate_fp, signal_fp, METHOD_VERSION, *threshold_order)[:24]
    rows.sort(key=lambda row: (row.get("event_timestamp_utc", ""), row.get("scenario_event_id", ""), row.get("classification_id", "")))
    class_counts = {name: sum(1 for row in rows if row.get("operator_class") == name) for name in CLASSES}
    status_counts = dict(sorted(Counter(row.get("classification_status", "") for row in rows).items()))
    side_counts = {side: {name: sum(1 for row in rows if row.get("side") == side and row.get("operator_class") == name) for name in CLASSES} for side in sorted({row.get("side", "") for row in rows})}
    regime_counts = {regime: {name: sum(1 for row in rows if row.get("market_regime") == regime and row.get("operator_class") == name) for name in CLASSES} for regime in sorted({row.get("market_regime", "") for row in rows})}
    setup_counts = {setup: {name: sum(1 for row in rows if row.get("setup_family") == setup and row.get("operator_class") == name) for name in CLASSES} for setup in sorted({row.get("setup_family", "") for row in rows})}
    warning_counts = dict(sorted(Counter(token for row in rows for token in _tokens(row.get("warning_codes"))).items()))
    risk_counts = dict(sorted(Counter(token for row in rows for token in _tokens(row.get("risk_flags"))).items()))
    no_trade_counts = dict(sorted(Counter(token for row in rows for token in _tokens(row.get("no_trade_flags"))).items()))
    payload: dict[str, Any] = {"schema_version": REPORT_SCHEMA_VERSION, "report_date": report_date, "report_written": False, "safety_boundary": SAFETY, "scenario_event_input_rows": len(event_rows), "assigned_event_rows": sum(1 for row in event_rows if row.get("grouping_status") != "ambiguous"), "ambiguous_event_rows": sum(1 for row in event_rows if row.get("grouping_status") == "ambiguous"), "candidate_context_rows": len(candidates_by_id), "signal_context_rows": len(signals_by_id), "exact_duplicate_candidate_rows": candidate_dupes, "exact_duplicate_signal_rows": signal_dupes, "candidate_conflict_rows": 0, "signal_conflict_rows": 0, "complete_join_rows": sum(1 for row in rows if row.get("source_join_status") == "complete"), "insufficient_evidence_rows": sum(1 for row in rows if row.get("classification_status") == "insufficient_evidence"), "classified_rows": sum(1 for row in rows if row.get("classification_status") == "classified"), "class_counts": dict(sorted(class_counts.items())), "classification_status_counts": status_counts, "side_class_counts": side_counts, "regime_class_counts": regime_counts, "setup_family_class_counts": setup_counts, "formal_gate_pass_rows": formal_pass, "a_formal_rows": class_counts["A_FORMAL"], "formal_pass_not_a_rows": formal_pass - class_counts["A_FORMAL"], "b_check_15m_rows": class_counts["B_CHECK_15M"], "c_watch_zone_rows": class_counts["C_WATCH_ZONE"], "stop_or_exit_rows": class_counts["STOP_OR_EXIT"], "thresholds": {key: _threshold_text(value) for key, value in sorted(threshold_values.items())}, "warning_token_counts": warning_counts, "risk_token_counts": risk_counts, "no_trade_token_counts": no_trade_counts, "dry_run": dry_run, "errors": []}
    payload["ok"] = True
    payload["exit_code"] = 0
    csv_text = _serialize_csv(rows)
    json_text = json.dumps(payload | {"report_written": True}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    md_text = _markdown(payload)
    if dry_run:
        payload["ok"] = True; payload["exit_code"] = 0
        return payload
    existing_error = _validate_outputs(output_csv, output_json, output_md, replace_output)
    if existing_error: return {"ok": False, "exit_code": 4, "errors": [existing_error], "report_written": False, "safety_boundary": SAFETY}
    try:
        _atomic_three([(output_csv, csv_text), (output_json, json_text), (output_md, md_text)])
    except OSError:
        return {"ok": False, "exit_code": 4, "errors": ["output_transaction_failed"], "report_written": False, "safety_boundary": SAFETY}
    payload["report_written"] = True
    payload["ok"] = True
    payload["exit_code"] = 0
    return payload


def _serialize_csv(rows: list[dict[str, str]]) -> str:
    from io import StringIO
    stream = StringIO(); writer = csv.DictWriter(stream, fieldnames=OUTPUT_HEADERS, lineterminator="\n"); writer.writeheader(); writer.writerows({key: row.get(key, "") for key in OUTPUT_HEADERS} for row in rows); return stream.getvalue()


def _validate_outputs(csv_path: Path, json_path: Path, md_path: Path, replace_output: bool) -> str | None:
    if csv_path.exists():
        try:
            with csv_path.open(newline="", encoding="utf-8") as fp:
                if (csv.DictReader(fp).fieldnames or []) != OUTPUT_HEADERS and not replace_output: return "existing_output_schema_mismatch"
        except (OSError, UnicodeError, csv.Error): return "existing_output_schema_mismatch"
    if json_path.exists():
        try:
            existing = json.loads(json_path.read_text(encoding="utf-8"))
            if existing.get("schema_version") != REPORT_SCHEMA_VERSION and not replace_output: return "existing_output_schema_mismatch"
        except (OSError, UnicodeError, json.JSONDecodeError): return "existing_output_schema_mismatch"
    if md_path.exists() and not replace_output:
        try:
            if "# Manual Operator Classifier Report" not in md_path.read_text(encoding="utf-8"):
                return "existing_output_schema_mismatch"
        except (OSError, UnicodeError):
            return "existing_output_schema_mismatch"
    return None
