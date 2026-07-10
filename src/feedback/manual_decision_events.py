"""Append-only local recorder for human decision events (P4).

The recorder stores observations of human action only; it does not infer a
result and is intentionally independent from notification and gate logic.
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

SCHEMA_VERSION = "manual_decision_event.v1"
DECISION_HEADERS = [
    "schema_version", "decision_event_id", "event_fingerprint", "identity_scope", "scenario_id", "signal_id",
    "mail_timestamp_jst", "human_checked_at_utc", "human_checked_at_jst", "decision_stage", "human_action",
    "human_side", "observed_price", "planned_entry_price", "planned_sl_price", "planned_tp1_price",
    "planned_tp2_price", "reason_codes", "manual_note", "source", "recorded_at_utc",
    "supersedes_decision_event_id", "record_status",
]
DECISION_EVENT_HEADERS = DECISION_HEADERS
ALLOWED_ACTIONS = {"entered", "watched_no_entry", "skipped", "exited", "took_profit", "adjusted_stop", "cancelled_plan"}
ALLOWED_STAGES = {"entry", "management", "exit"}
ALLOWED_SIDES = {"long", "short", "none"}
ALLOWED_REASONS = {"trigger_confirmed", "trigger_missing", "bad_setup", "late", "risk_too_high", "side_unclear", "defensive_subject", "zone_not_reached", "scenario_invalidated", "profit_protection", "manual_override", "other"}
JST = ZoneInfo("Asia/Tokyo")
_SENSITIVE = re.compile(r"(?:source_uid_hash|uid_|account-|OPENAI_API_KEY|SMTP_PASSWORD|/private/|Users/[^/]+/|file://)", re.I)


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace(" ", "T")
    if not text:
        return None
    try:
        result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=JST)
    return result


def _jst(value: datetime) -> str:
    return value.astimezone(JST).isoformat()


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _dec(value: Any) -> str | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return ""
    try:
        return format(Decimal(text), "f")
    except (InvalidOperation, ValueError):
        return None


def _hash(parts: list[str]) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _read_existing(path: Path) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], None
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            if (reader.fieldnames or []) != DECISION_HEADERS:
                return [], "existing_output_schema_mismatch"
            rows = [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return [], "existing_output_schema_mismatch"
    ids: set[str] = set()
    for row in rows:
        if row.get("schema_version") != SCHEMA_VERSION or not row.get("decision_event_id") or row["decision_event_id"] in ids:
            return [], "existing_output_schema_mismatch"
        ids.add(row["decision_event_id"])
    for row in rows:
        status = row.get("record_status", "")
        target = row.get("supersedes_decision_event_id", "")
        if status not in {"active", "correction"} or (status == "active" and target) or (status == "correction" and not target):
            return [], "existing_output_schema_mismatch"
        target_row = next((item for item in rows if item.get("decision_event_id") == target), None) if target else None
        if target and (target == row.get("decision_event_id") or target not in ids or target_row and target_row.get("supersedes_decision_event_id") or sum(1 for item in rows if item.get("supersedes_decision_event_id") == target) > 1):
            return [], "existing_output_schema_mismatch"
    return rows, None


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".p4-decision-", suffix=".csv", dir=path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        with temp.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=DECISION_HEADERS, lineterminator="\n")
            writer.writeheader()
            writer.writerows({key: row.get(key, "") for key in DECISION_HEADERS} for row in rows)
        temp.replace(path)
    except Exception as exc:
        temp.unlink(missing_ok=True)
        raise OSError("output_io_error") from exc


def _scenario_check(scenarios: Path, scenario_id: str, signal_id: str, scenario_events: Path | None = None) -> str:
    try:
        with scenarios.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            fields = reader.fieldnames or []
            from src.feedback.manual_scenario_normalizer import SCENARIO_HEADERS
            if fields != SCENARIO_HEADERS:
                return "input_schema_mismatch"
            rows = [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return "invalid_input"
    if any(row.get("schema_version") != "manual_scenario.v1" or not row.get("scenario_id") for row in rows) or len({row.get("scenario_id") for row in rows}) != len(rows):
        return "input_schema_mismatch"
    matches = [row for row in rows if row.get("scenario_id") == scenario_id]
    match = matches[0] if len(matches) == 1 else None
    if match is None:
        return "unknown_scenario"
    event_rows: list[dict[str, str]] = []
    if scenario_events is not None:
        try:
            with scenario_events.open(newline="", encoding="utf-8") as fp:
                event_reader = csv.DictReader(fp)
                from src.feedback.manual_scenario_normalizer import EVENT_HEADERS
                if (event_reader.fieldnames or []) != EVENT_HEADERS:
                    return "input_schema_mismatch"
                event_rows = [dict(row) for row in event_reader]
        except (OSError, UnicodeError, csv.Error):
            return "invalid_input"
        known_scenarios = {item.get("scenario_id") for item in rows}
        if any(row.get("schema_version") != "manual_scenario_event.v1" or not row.get("scenario_event_id") or not row.get("candidate_id") for row in event_rows) or len({row.get("scenario_event_id") for row in event_rows}) != len(event_rows) or len({row.get("candidate_id") for row in event_rows}) != len(event_rows):
            return "input_schema_mismatch"
        if any((row.get("scenario_id") and row.get("scenario_id") not in known_scenarios) or (row.get("grouping_status") == "ambiguous" and row.get("scenario_id")) or (row.get("grouping_status") != "ambiguous" and not row.get("scenario_id")) for row in event_rows):
            return "input_schema_mismatch"
    if signal_id:
        valid_signals = {match.get("initial_signal_id", ""), match.get("latest_signal_id", "")}
        if scenario_events is not None:
            valid_signals.update(row.get("source_signal_id", "") for row in event_rows if row.get("scenario_id") == scenario_id and row.get("grouping_status") != "ambiguous")
        if signal_id not in valid_signals:
            return "signal_not_in_scenario"
    return "checked"


def record_manual_decision(*, scenario_id: str = "", signal_id: str = "", human_checked_at_jst: str, decision_stage: str, human_action: str, human_side: str, reason_codes: list[str] | None = None, reason_code: list[str] | None = None, mail_timestamp_jst: str = "", observed_price: Any = "", planned_entry_price: Any = "", planned_sl_price: Any = "", planned_tp1_price: Any = "", planned_tp2_price: Any = "", manual_note: str = "", source: str = "manual_local", supersedes_decision_event_id: str = "", output_csv: Path | None = None, scenarios: Path | None = None, scenario_events: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    output = output_csv or Path("logs/csv/manual_decision_events.csv")
    summary: dict[str, Any] = {"ok": False, "exit_code": 2, "schema_version": SCHEMA_VERSION, "dry_run": dry_run, "event_written": False, "duplicate_event": False, "errors": [], "output_csv": output.name, "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"}
    scenario_id, signal_id = str(scenario_id or "").strip(), str(signal_id or "").strip()
    if not scenario_id and not signal_id:
        summary["errors"] = ["missing_identity"]
        return summary
    checked = _dt(human_checked_at_jst)
    if checked is None:
        summary["errors"] = ["invalid_timestamp"]
        return summary
    if mail_timestamp_jst and _dt(mail_timestamp_jst) is None:
        summary["errors"] = ["invalid_timestamp"]
        return summary
    action, stage, side = str(human_action).strip().lower(), str(decision_stage).strip().lower(), str(human_side).strip().lower()
    if action not in ALLOWED_ACTIONS or stage not in ALLOWED_STAGES or side not in ALLOWED_SIDES:
        summary["errors"] = ["invalid_value"]
        return summary
    if action == "entered" and (stage != "entry" or side not in {"long", "short"}):
        summary["errors"] = ["inconsistent_action"]
        return summary
    if action in {"watched_no_entry", "skipped", "cancelled_plan"} and stage != "entry":
        summary["errors"] = ["inconsistent_action"]
        return summary
    if action in {"exited", "took_profit"} and stage not in {"exit", "management"}:
        summary["errors"] = ["inconsistent_action"]
        return summary
    if action == "adjusted_stop" and stage != "management":
        summary["errors"] = ["inconsistent_action"]
        return summary
    raw_reasons = list(reason_codes or []) + list(reason_code or [])
    reasons = sorted({str(value).strip().lower() for value in raw_reasons if str(value).strip()})
    if any(value not in ALLOWED_REASONS for value in reasons):
        summary["errors"] = ["invalid_reason_code"]
        return summary
    note = " ".join(str(manual_note or "").splitlines()).strip()
    if len(note) > 280 or _SENSITIVE.search(note) or _SENSITIVE.search(str(source)):
        summary["errors"] = ["privacy_validation_failed"]
        return summary
    prices: dict[str, str] = {}
    for field, value in (("observed_price", observed_price), ("planned_entry_price", planned_entry_price), ("planned_sl_price", planned_sl_price), ("planned_tp1_price", planned_tp1_price), ("planned_tp2_price", planned_tp2_price)):
        parsed = _dec(value)
        if parsed is None:
            summary["errors"] = ["invalid_numeric"]
            return summary
        prices[field] = parsed
    scenario_validation = "not_checked"
    if scenarios is not None and scenario_id:
        scenario_validation = _scenario_check(scenarios, scenario_id, signal_id, scenario_events)
        if scenario_validation not in {"checked"}:
            summary["errors"] = [scenario_validation]
            return summary
    elif scenario_id and not re.fullmatch(r"scn_[0-9a-f]{24}", scenario_id):
        summary["errors"] = ["invalid_scenario_id"]
        return summary
    scope = "scenario" if scenario_id else "signal_only"
    supersedes = str(supersedes_decision_event_id or "").strip()
    fingerprint_parts = [scope, scenario_id, signal_id, str(mail_timestamp_jst or "").strip(), _jst(checked), stage, action, side, prices["observed_price"], prices["planned_entry_price"], prices["planned_sl_price"], prices["planned_tp1_price"], prices["planned_tp2_price"], ";".join(reasons), note, str(source or "").strip(), supersedes, "active" if not supersedes else "correction"]
    fingerprint = _hash(fingerprint_parts)
    event_id = "mde_" + _hash([scope, scenario_id, signal_id, _jst(checked), stage, action, side, supersedes])[:24]
    rows, read_error = _read_existing(output)
    if read_error:
        summary["errors"] = [read_error]
        summary["exit_code"] = 4
        return summary
    existing = next((row for row in rows if row.get("decision_event_id") == event_id), None)
    if existing:
        if existing.get("event_fingerprint") == fingerprint:
            summary.update(ok=True, exit_code=0, duplicate_event=True, scenario_validation=scenario_validation)
        else:
            summary.update(exit_code=3, errors=["event_identity_conflict"])
        return summary
    if supersedes:
        target = next((row for row in rows if row.get("decision_event_id") == supersedes), None)
        already_superseded = any(row.get("supersedes_decision_event_id") == supersedes for row in rows)
        if target is None or target.get("supersedes_decision_event_id") or already_superseded or supersedes == event_id:
            summary["errors"] = ["invalid_correction_target"]
            summary["exit_code"] = 3
            return summary
    row = {"schema_version": SCHEMA_VERSION, "decision_event_id": event_id, "event_fingerprint": fingerprint, "identity_scope": scope, "scenario_id": scenario_id, "signal_id": signal_id, "mail_timestamp_jst": _jst(_dt(mail_timestamp_jst)) if mail_timestamp_jst else "", "human_checked_at_utc": _utc(checked), "human_checked_at_jst": _jst(checked), "decision_stage": stage, "human_action": action, "human_side": side, **prices, "reason_codes": ";".join(reasons), "manual_note": note, "source": str(source or "").strip(), "recorded_at_utc": _utc(datetime.now(timezone.utc)), "supersedes_decision_event_id": supersedes, "record_status": "correction" if supersedes else "active"}
    rows.append(row)
    rows.sort(key=lambda value: (value.get("human_checked_at_utc", ""), value.get("decision_event_id", "")))
    summary.update(ok=True, exit_code=0, scenario_validation=scenario_validation, decision_event_id=event_id)
    if dry_run:
        summary["would_write"] = True
        return summary
    try:
        _write(output, rows)
    except OSError:
        summary.update(ok=False, exit_code=4, errors=["output_io_error"])
        return summary
    summary["event_written"] = True
    return summary


def record_manual_decision_event(**kwargs: Any) -> dict[str, Any]:
    return record_manual_decision(**kwargs)
