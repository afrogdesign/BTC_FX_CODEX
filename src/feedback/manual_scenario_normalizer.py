"""Deterministic, report-only normalization of Active Plan candidates.

This module deliberately treats candidates as market evidence.  It never
turns a candidate or proxy outcome into a human action or trading decision.
"""
from __future__ import annotations

import csv
import hashlib
import os
import tempfile
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

SCENARIO_SCHEMA_VERSION = "manual_scenario.v1"
EVENT_SCHEMA_VERSION = "manual_scenario_event.v1"
METHOD_VERSION = "manual_scenario_normalization.v1"
SCENARIO_HEADERS = [
    "schema_version", "scenario_id", "symbol", "side", "setup_family", "scenario_status",
    "lifecycle_state", "initial_candidate_id", "latest_candidate_id", "initial_signal_id",
    "latest_signal_id", "detected_at_utc", "detected_at_jst", "last_updated_at_utc",
    "last_updated_at_jst", "entry_zone_low", "entry_zone_high", "invalidation_price",
    "tp1_price", "tp2_price", "candidate_event_count", "source_signal_count",
    "zone_touched_at_utc", "zone_touched_at_jst", "terminal_at_utc", "terminal_at_jst",
    "proxy_outcome", "proxy_outcome_status", "ohlcv_coverage_status", "scenario_method_version",
    "max_update_gap_minutes", "max_scenario_age_hours", "zone_tolerance_bps", "invalidation_tolerance_bps",
]
EVENT_HEADERS = [
    "schema_version", "scenario_event_id", "scenario_id", "candidate_id", "candidate_fingerprint",
    "source_signal_id", "event_timestamp_utc", "event_timestamp_jst", "event_type", "grouping_status",
    "symbol", "side", "candidate_type", "setup_family", "active_primary_action", "candidate_status",
    "entry_mode", "entry_price", "entry_zone_low", "entry_zone_high", "invalidation_price", "tp1_price",
    "tp2_price", "next_condition", "intraperiod_outcome", "entry_reached_time", "first_exit_time",
    "first_exit_reason", "mfe_r", "mae_r", "ohlcv_coverage_status", "ohlcv_gap_reason", "reason_codes",
    "scenario_method_version",
]
SCENARIO_EVENT_HEADERS = EVENT_HEADERS
CANDIDATE_REQUIRED_HEADERS = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side"]
OUTCOME_REQUIRED_HEADERS = ["candidate_id", "outcome"]
JST = ZoneInfo("Asia/Tokyo")
SETUP_FAMILY_MAP = {
    "active_limit_retest": "limit_retest",
    "active_market_small": "market_entry",
    "active_breakout_follow": "breakout_follow",
    "active_counter_scalp": "counter_scalp",
}
RESOLVED_OUTCOMES = {"tp1_first", "tp2_first", "sl_first"}
MISSING_OHLCV_CATEGORIES = {
    "no_ohlcv_input", "candidate_timestamp_missing", "candidate_before_ohlcv_start",
    "candidate_after_ohlcv_end", "candidate_window_gap", "malformed_ohlcv",
    "stale_ohlcv_range", "unknown_gap",
}


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()


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


def _utc(value: datetime | None) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if value else ""


def _jst(value: datetime | None) -> str:
    return value.astimezone(JST).isoformat() if value else ""


def _decimal(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _decimal_text(value: Any) -> str:
    parsed = _decimal(value)
    return "" if parsed is None else format(parsed, "f")


def _symbol(value: Any) -> str | None:
    text = str(value or "").strip().replace("-", "").replace("_", "").upper()
    if not text:
        return "BTCUSDT"
    if text in {"BTCUSDT", "BTCUSDC", "BTCUSD"}:
        return "BTCUSDT"
    return None


def _setup_family(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in SETUP_FAMILY_MAP:
        return SETUP_FAMILY_MAP[raw]
    return "_".join(raw.replace("-", "_").replace("/", "_").split())


def _zone(row: dict[str, Any]) -> tuple[Decimal, Decimal] | None:
    price = _decimal(row.get("entry_price"))
    low = _decimal(row.get("entry_zone_low"))
    high = _decimal(row.get("entry_zone_high"))
    if price is not None and low is None and high is None:
        return price, price
    if low is None or high is None:
        return None
    return (min(low, high), max(low, high))


def _read_csv(path: Path, required: list[str]) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            actual = reader.fieldnames or []
            if any(name not in actual for name in required):
                return [], "input_schema_mismatch"
            return [dict(row) for row in reader], None
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"


def _read_outcomes(path: Path | None) -> tuple[dict[str, dict[str, str]], int, str | None]:
    if path is None:
        return {}, 0, None
    if not path.exists():
        return {}, 0, "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            if any(name not in (reader.fieldnames or []) for name in OUTCOME_REQUIRED_HEADERS):
                return {}, 0, "input_schema_mismatch"
            rows = [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return {}, 0, "invalid_input"
    result: dict[str, dict[str, str]] = {}
    fingerprints: dict[str, tuple[tuple[str, str], ...]] = {}
    conflicts = 0
    for row in rows:
        cid = str(row.get("candidate_id", "")).strip()
        normalized = {str(key): str(value or "").strip() for key, value in row.items()}
        if not cid:
            return {}, 0, "invalid_input"
        for key in ("entry_reached_time", "first_exit_time", "timestamp_jst"):
            if normalized.get(key) and _dt(normalized[key]) is None:
                return {}, 0, "invalid_input"
        if normalized.get("outcome", "").lower() in RESOLVED_OUTCOMES and not normalized.get("first_exit_time"):
            return {}, 0, "invalid_input"
        fingerprint = tuple(sorted(normalized.items()))
        if cid in result and fingerprints[cid] != fingerprint:
            conflicts += 1
        else:
            result[cid] = normalized
            fingerprints[cid] = fingerprint
    if conflicts:
        return result, conflicts, "candidate_identity_conflict"
    return result, 0, None


def _read_ohlcv(path: Path) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            fields = reader.fieldnames or []
            if not any(name in fields for name in ("timestamp", "timestamp_jst", "timestamp_utc")):
                return [], "input_schema_mismatch"
            if "high" not in fields or "low" not in fields:
                return [], "input_schema_mismatch"
            return [dict(row) for row in reader], None
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"


def _write_csv_temp(path: Path, headers: list[str], rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".p4-", suffix=".csv", dir=path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        with temp.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=headers, lineterminator="\n")
            writer.writeheader()
            writer.writerows({key: row.get(key, "") for key in headers} for row in rows)
        return temp
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def _transactional_replace(paths_rows: list[tuple[Path, list[str], list[dict[str, Any]]]]) -> None:
    temps: list[tuple[Path, Path]] = []
    backups: list[tuple[Path, Path]] = []
    replaced: list[Path] = []
    try:
        for path, headers, rows in paths_rows:
            temp = _write_csv_temp(path, headers, rows)
            temps.append((path, temp))
        for path, _ in temps:
            if path.exists():
                backup = path.with_name(f".{path.name}.p4-backup")
                backup.unlink(missing_ok=True)
                path.replace(backup)
                backups.append((path, backup))
        for path, temp in temps:
            temp.replace(path)
            replaced.append(path)
    except Exception as exc:
        for path in replaced:
            path.unlink(missing_ok=True)
        for path, backup in backups:
            if backup.exists():
                backup.replace(path)
        for _, temp in temps:
            temp.unlink(missing_ok=True)
        raise OSError("output_transaction_failed") from exc
    finally:
        for _, temp in temps:
            temp.unlink(missing_ok=True)
        for _, backup in backups:
            backup.unlink(missing_ok=True)


def _validate_existing_output(path: Path, headers: list[str], replace_output: bool) -> str | None:
    if not path.exists():
        return None
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            actual = csv.DictReader(fp).fieldnames or []
    except (OSError, UnicodeError, csv.Error):
        return "output_schema_mismatch"
    if actual != headers and not replace_output:
        return "output_schema_mismatch"
    return None


def _candidate_normalize(row: dict[str, str]) -> tuple[dict[str, Any] | None, str | None]:
    cid = str(row.get("candidate_id", "")).strip()
    signal = str(row.get("source_signal_id", "")).strip()
    timestamp = _dt(row.get("timestamp_jst"))
    side = str(row.get("side", "")).strip().lower()
    zone = _zone(row)
    symbol = _symbol(row.get("symbol"))
    if not cid or not signal or not str(row.get("candidate_type", "")).strip() or timestamp is None or side not in {"long", "short"} or zone is None:
        return None, "invalid_input"
    if symbol is None:
        return None, "invalid_input"
    numeric_fields = ("entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2")
    for field in numeric_fields:
        if str(row.get(field, "")).strip() and _decimal(row.get(field)) is None:
            return None, "invalid_input"
    low, high = zone
    normalized = dict(row)
    normalized.update({
        "candidate_id": cid, "source_signal_id": signal, "timestamp": timestamp, "side": side,
        "symbol": symbol, "setup_family": _setup_family(row.get("candidate_type")),
        "entry_price": _decimal_text(row.get("entry_price")), "entry_zone_low": format(low, "f"),
        "entry_zone_high": format(high, "f"), "invalidation_price": _decimal_text(row.get("invalidation_price") or row.get("stop_loss")),
        "tp1_price": _decimal_text(row.get("tp1") or row.get("tp1_price")),
        "tp2_price": _decimal_text(row.get("tp2") or row.get("tp2_price")),
    })
    return normalized, None


def _fingerprint(row: dict[str, Any]) -> str:
    fields = ("source_signal_id", "timestamp", "candidate_type", "side", "symbol", "setup_family", "entry_price", "entry_zone_low", "entry_zone_high", "invalidation_price", "tp1_price", "tp2_price")
    return _hash(*(row.get(field, "") for field in fields))[:32]


def _compatible(a: dict[str, Any], b: dict[str, Any], zone_bps: int, inv_bps: int) -> bool:
    if (a["symbol"], a["side"], a["setup_family"]) != (b["symbol"], b["side"], b["setup_family"]):
        return False
    a_low, a_high = Decimal(a["entry_zone_low"]), Decimal(a["entry_zone_high"])
    b_low, b_high = Decimal(b["entry_zone_low"]), Decimal(b["entry_zone_high"])
    tolerance = max(a_low, a_high, b_low, b_high) * Decimal(zone_bps) / Decimal(10000)
    if max(a_low - tolerance, b_low - tolerance) > min(a_high + tolerance, b_high + tolerance):
        return False
    ia, ib = _decimal(a.get("invalidation_price")), _decimal(b.get("invalidation_price"))
    if ia is not None and ib is not None:
        inv_tol = max(abs(ia), abs(ib)) * Decimal(inv_bps) / Decimal(10000)
        if abs(ia - ib) > inv_tol:
            return False
    return True


def _scenario_id(events: list[dict[str, Any]]) -> str:
    first = events[0]
    timestamp = _jst(first["timestamp"] if isinstance(first.get("timestamp"), datetime) else _dt(first.get("event_timestamp_jst") or first.get("timestamp")))
    return "scn_" + _hash(first["symbol"], first["side"], first["setup_family"], timestamp, first.get("entry_zone_low", ""), first.get("entry_zone_high", ""), first.get("invalidation_price", ""), METHOD_VERSION)[:24]


def _event_id(row: dict[str, Any]) -> str:
    return "sce_" + _hash(row.get("candidate_id"), row.get("candidate_fingerprint"), row.get("grouping_status"), METHOD_VERSION)[:24]


def _diagnose_ohlcv(candidate: dict[str, Any], ohlcv: list[dict[str, str]] | None) -> tuple[str, str]:
    if ohlcv is None:
        return "", ""
    if not ohlcv:
        return "no_ohlcv", "no_ohlcv_input"
    timestamp = candidate["timestamp"]
    parsed = []
    for row in ohlcv:
        ts = _dt(row.get("timestamp") or row.get("timestamp_jst") or row.get("timestamp_utc"))
        high, low = _decimal(row.get("high")), _decimal(row.get("low"))
        if ts is None or high is None or low is None:
            return "no_ohlcv", "malformed_ohlcv"
        parsed.append((ts, high, low))
    parsed.sort()
    if timestamp < parsed[0][0]:
        return "no_ohlcv", "candidate_before_ohlcv_start"
    if timestamp > parsed[-1][0]:
        age = timestamp - parsed[-1][0]
        return "no_ohlcv", "stale_ohlcv_range" if age > timedelta(hours=24) else "candidate_after_ohlcv_end"
    window_end = timestamp + timedelta(hours=24)
    if not any(timestamp <= ts <= window_end for ts, _, _ in parsed):
        return "no_ohlcv", "candidate_window_gap"
    return "covered", "covered"


def _outcome_terminal_boundary(candidate: dict[str, Any], outcome: dict[str, str], max_age_hours: int) -> datetime | None:
    name = str(outcome.get("outcome", "")).strip().lower()
    if name not in RESOLVED_OUTCOMES and name not in {"not_entered", "entry_not_reached", "expired"}:
        return None
    explicit = _dt(outcome.get("first_exit_time"))
    if explicit is not None:
        return explicit
    if name in {"not_entered", "entry_not_reached", "expired"}:
        return candidate["timestamp"] + timedelta(hours=max_age_hours)
    return None


def _group_terminal_boundary(group: list[dict[str, Any]], outcomes: dict[str, dict[str, str]], max_age_hours: int) -> datetime | None:
    boundaries = [_outcome_terminal_boundary(item, outcomes.get(item["candidate_id"], {}), max_age_hours) for item in group]
    valid = [value for value in boundaries if value is not None]
    return min(valid) if valid else None


def build_manual_scenarios(*, candidates: Path, intraperiod_outcomes: Path | None = None, scenarios_out: Path | None = None, events_out: Path | None = None, max_update_gap_minutes: int = 360, max_scenario_age_hours: int = 24, zone_tolerance_bps: int = 25, invalidation_tolerance_bps: int = 50, ohlcv: Path | None = None, dry_run: bool = False, replace_output: bool = False) -> dict[str, Any]:
    scenarios_path = scenarios_out or Path("logs/csv/manual_scenarios.csv")
    events_path = events_out or Path("logs/csv/manual_scenario_events.csv")
    summary: dict[str, Any] = {
        "ok": False, "exit_code": 2, "schema_version": SCENARIO_SCHEMA_VERSION, "event_schema_version": EVENT_SCHEMA_VERSION,
        "method_version": METHOD_VERSION, "dry_run": dry_run, "scenario_count": 0, "candidate_input_rows": 0,
        "unique_candidate_rows": 0, "duplicate_candidate_rows": 0, "candidate_conflict_rows": 0, "assigned_candidate_rows": 0,
        "ambiguous_candidate_rows": 0, "orphan_outcome_count": 0, "errors": [], "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }
    if max_update_gap_minutes <= 0 or max_scenario_age_hours <= 0 or zone_tolerance_bps < 0 or invalidation_tolerance_bps < 0:
        summary["errors"] = ["invalid_parameters"]
        return summary
    raw_rows, error = _read_csv(candidates, CANDIDATE_REQUIRED_HEADERS)
    if error:
        summary["errors"] = [error]
        return summary
    summary["candidate_input_rows"] = len(raw_rows)
    normalized: list[dict[str, Any]] = []
    by_id: dict[str, str] = {}
    for raw in raw_rows:
        row, row_error = _candidate_normalize(raw)
        if row_error:
            summary["errors"] = [row_error]
            return summary
        assert row is not None
        fp = _fingerprint(row)
        if row["candidate_id"] in by_id:
            if by_id[row["candidate_id"]] == fp:
                summary["duplicate_candidate_rows"] += 1
                continue
            summary["candidate_conflict_rows"] += 1
            summary["errors"] = ["candidate_identity_conflict"]
            summary["exit_code"] = 3
            return summary
        by_id[row["candidate_id"]] = fp
        row["candidate_fingerprint"] = fp
        normalized.append(row)
    summary["unique_candidate_rows"] = len(normalized)
    outcomes, outcome_conflicts, outcome_error = _read_outcomes(intraperiod_outcomes)
    if outcome_error:
        summary["errors"] = [outcome_error]
        summary["exit_code"] = 3 if outcome_error == "candidate_identity_conflict" else 2
        return summary
    summary["orphan_outcome_count"] = sum(1 for cid in outcomes if cid not in by_id)
    ohlcv_rows: list[dict[str, str]] | None = None
    if ohlcv is not None:
        ohlcv_rows, ohlcv_error = _read_ohlcv(ohlcv)
        if ohlcv_error:
            summary["errors"] = [ohlcv_error]
            return summary
    normalized.sort(key=lambda row: (row["timestamp"], row["candidate_id"]))
    for path, headers in ((scenarios_path, SCENARIO_HEADERS), (events_path, EVENT_HEADERS)):
        output_error = _validate_existing_output(path, headers, replace_output)
        if output_error:
            summary["errors"] = [output_error]
            summary["exit_code"] = 4
            return summary
    scenarios: list[list[dict[str, Any]]] = []
    events: list[dict[str, Any]] = []
    for candidate in normalized:
        matches: list[int] = []
        for index, group in enumerate(scenarios):
            latest = group[-1]
            terminal_boundary = _group_terminal_boundary(group, outcomes, max_scenario_age_hours)
            if terminal_boundary is not None and candidate["timestamp"] > terminal_boundary:
                continue
            age = candidate["timestamp"] - group[0]["timestamp"]
            gap = candidate["timestamp"] - latest["timestamp"]
            if gap >= timedelta(0) and gap <= timedelta(minutes=max_update_gap_minutes) and age <= timedelta(hours=max_scenario_age_hours) and _compatible(candidate, latest, zone_tolerance_bps, invalidation_tolerance_bps):
                matches.append(index)
        event_type = "updated" if len(matches) == 1 else "detected"
        grouping = "matched_existing" if len(matches) == 1 else "new_scenario"
        scenario_id = ""
        reasons: list[str] = []
        if len(matches) > 1:
            grouping = "ambiguous"
            reasons.append("ambiguous_grouping")
            summary["ambiguous_candidate_rows"] += 1
        elif len(matches) == 1:
            scenario_id = _scenario_id(scenarios[matches[0]])
            scenarios[matches[0]].append(candidate)
            summary["assigned_candidate_rows"] += 1
        else:
            scenarios.append([candidate])
            scenario_id = _scenario_id([candidate])
            summary["assigned_candidate_rows"] += 1
        coverage, gap_reason = _diagnose_ohlcv(candidate, ohlcv_rows)
        outcome = outcomes.get(candidate["candidate_id"], {})
        if str(outcome.get("outcome", "")).strip().lower() == "no_ohlcv" and ohlcv_rows is None:
            coverage, gap_reason = "no_ohlcv", "no_ohlcv_input"
        outcome_name = str(outcome.get("outcome", "")).strip().lower()
        if grouping == "ambiguous":
            event_type = "ambiguous_grouping"
        elif outcome_name == "no_ohlcv":
            event_type = "coverage_missing"
        elif outcome_name == "entry_reached":
            event_type = "zone_touched"
        elif outcome_name in RESOLVED_OUTCOMES:
            event_type = "proxy_resolved"
        elif outcome_name in {"not_entered", "entry_not_reached", "expired"}:
            event_type = "expired_without_touch"
        elif outcome_name in {"", "pending", "timeout", "ambiguous"}:
            event_type = "pending"
        event: dict[str, Any] = {
            "schema_version": EVENT_SCHEMA_VERSION, "scenario_event_id": "", "scenario_id": scenario_id,
            "candidate_id": candidate["candidate_id"], "candidate_fingerprint": candidate["candidate_fingerprint"],
            "source_signal_id": candidate["source_signal_id"], "event_timestamp_utc": _utc(candidate["timestamp"]),
            "event_timestamp_jst": _jst(candidate["timestamp"]), "event_type": event_type, "grouping_status": grouping,
            "symbol": candidate["symbol"], "side": candidate["side"], "candidate_type": candidate.get("candidate_type", ""),
            "setup_family": candidate["setup_family"], "active_primary_action": candidate.get("active_primary_action", ""),
            "candidate_status": candidate.get("candidate_status", ""), "entry_mode": candidate.get("entry_mode", ""),
            "entry_price": candidate.get("entry_price", ""), "entry_zone_low": candidate.get("entry_zone_low", ""),
            "entry_zone_high": candidate.get("entry_zone_high", ""), "invalidation_price": candidate.get("invalidation_price", ""),
            "tp1_price": candidate.get("tp1_price", ""), "tp2_price": candidate.get("tp2_price", ""),
            "next_condition": candidate.get("next_condition", ""), "intraperiod_outcome": outcome.get("outcome", ""),
            "entry_reached_time": outcome.get("entry_reached_time", ""), "first_exit_time": outcome.get("first_exit_time", ""),
            "first_exit_reason": outcome.get("first_exit_reason", ""), "mfe_r": outcome.get("mfe_r", ""), "mae_r": outcome.get("mae_r", ""),
            "ohlcv_coverage_status": coverage, "ohlcv_gap_reason": gap_reason, "reason_codes": ";".join(reasons),
            "scenario_method_version": METHOD_VERSION,
        }
        event["scenario_event_id"] = _event_id(event)
        events.append(event)
    scenario_rows: list[dict[str, Any]] = []
    for group in scenarios:
        first, last = group[0], group[-1]
        scenario_id = _scenario_id(group)
        group_events = [event for event in events if event["scenario_id"] == scenario_id]
        outcomes_seen = [str(e.get("intraperiod_outcome", "")).strip().lower() for e in group_events]
        resolved = next((value for value in outcomes_seen if value in RESOLVED_OUTCOMES), "")
        expired = next((value for value in outcomes_seen if value in {"not_entered", "entry_not_reached", "expired"}), "")
        no_ohlcv = any(
            e.get("intraperiod_outcome") == "no_ohlcv"
            or e.get("ohlcv_coverage_status") in {"no_ohlcv", "coverage_missing"}
            or e.get("ohlcv_gap_reason") in MISSING_OHLCV_CATEGORIES
            for e in group_events
        )
        lifecycle = "detected" if len(group) == 1 else "updated"
        if "entry_reached" in outcomes_seen:
            lifecycle = "zone_touched"
        status = "active"
        if resolved: status, lifecycle = "resolved", "proxy_resolved"
        elif expired: status, lifecycle = "expired", "expired_without_touch"
        elif no_ohlcv: status, lifecycle = "coverage_missing", "coverage_missing"
        elif any(value in {"pending", "timeout", "ambiguous", ""} for value in outcomes_seen): lifecycle = "pending"
        touched_times = [_dt(outcomes.get(item["candidate_id"], {}).get("entry_reached_time")) for item in group]
        touched_time = min((value for value in touched_times if value is not None), default=None)
        terminal_boundary = _group_terminal_boundary(group, outcomes, max_scenario_age_hours)
        latest_values: dict[str, str] = {}
        for field in ("entry_zone_low", "entry_zone_high", "invalidation_price", "tp1_price", "tp2_price"):
            latest_values[field] = next((str(item.get(field, "")).strip() for item in reversed(group) if str(item.get(field, "")).strip()), "")
        row = {"schema_version": SCENARIO_SCHEMA_VERSION, "scenario_id": scenario_id, "symbol": first["symbol"], "side": first["side"], "setup_family": first["setup_family"], "scenario_status": status, "lifecycle_state": lifecycle, "initial_candidate_id": first["candidate_id"], "latest_candidate_id": last["candidate_id"], "initial_signal_id": first["source_signal_id"], "latest_signal_id": last["source_signal_id"], "detected_at_utc": _utc(first["timestamp"]), "detected_at_jst": _jst(first["timestamp"]), "last_updated_at_utc": _utc(last["timestamp"]), "last_updated_at_jst": _jst(last["timestamp"]), "entry_zone_low": latest_values["entry_zone_low"], "entry_zone_high": latest_values["entry_zone_high"], "invalidation_price": latest_values["invalidation_price"], "tp1_price": latest_values["tp1_price"], "tp2_price": latest_values["tp2_price"], "candidate_event_count": str(len(group)), "source_signal_count": str(len({x["source_signal_id"] for x in group})), "zone_touched_at_utc": _utc(touched_time), "zone_touched_at_jst": _jst(touched_time), "terminal_at_utc": _utc(terminal_boundary), "terminal_at_jst": _jst(terminal_boundary), "proxy_outcome": resolved, "proxy_outcome_status": "resolved" if resolved else ("expired" if expired else ("coverage_missing" if no_ohlcv else "pending")), "ohlcv_coverage_status": "no_ohlcv" if no_ohlcv else ("covered" if ohlcv_rows is not None else ""), "scenario_method_version": METHOD_VERSION, "max_update_gap_minutes": str(max_update_gap_minutes), "max_scenario_age_hours": str(max_scenario_age_hours), "zone_tolerance_bps": str(zone_tolerance_bps), "invalidation_tolerance_bps": str(invalidation_tolerance_bps)}
        scenario_rows.append(row)
    scenario_rows.sort(key=lambda row: (row["detected_at_utc"], row["scenario_id"]))
    events.sort(key=lambda row: (row["event_timestamp_utc"], row["candidate_id"], row["scenario_event_id"]))
    summary["scenario_count"] = len(scenario_rows)
    summary["ok"] = True
    summary["exit_code"] = 0
    summary["scenarios_out"] = scenarios_path.name
    summary["events_out"] = events_path.name
    summary["output_written"] = False
    if dry_run:
        summary["would_write_outputs"] = [scenarios_path.name, events_path.name]
        return summary
    try:
        _transactional_replace([(scenarios_path, SCENARIO_HEADERS, scenario_rows), (events_path, EVENT_HEADERS, events)])
    except OSError:
        summary.update(ok=False, exit_code=4, errors=["output_io_error"])
        return summary
    summary["output_written"] = True
    return summary


def normalize_manual_scenarios(**kwargs: Any) -> dict[str, Any]:
    """Compatibility name for callers that use the verb from the spec."""
    return build_manual_scenarios(**kwargs)
