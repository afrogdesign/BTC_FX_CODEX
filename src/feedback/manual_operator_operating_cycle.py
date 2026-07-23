"""Deterministic, report-only P8 operating-cycle runner."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.fetcher import FetchConfig, fetch_klines
from src.feedback.manual_operator_classifier import SIGNAL_HEADERS, _identity_rows
from src.feedback.manual_operator_trial_evidence import (
    METHOD_VERSION as TRIAL_METHOD_VERSION,
    build_manual_operator_trial_evidence,
)
from src.feedback.manual_operator_classifier import build_manual_operator_classifier
from src.feedback.manual_scenario_normalizer import (
    CANDIDATE_REQUIRED_HEADERS,
    build_manual_scenarios,
)
from src.trade.active_plan_intraperiod import build_active_plan_intraperiod_outcome_rows

METHOD_VERSION = "manual_operator_operating_cycle.v1"
SCHEMA_VERSION = "manual_operator_operating_cycle.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
OUTPUT_NAMES = (
    "candidate_slice.csv", "signal_context_slice.csv", "intraperiod_outcomes.csv",
    "manual_scenarios.csv", "manual_scenario_events.csv", "manual_operator_classifications.csv",
    "manual_operator_classifications.json", "manual_operator_classifications.md",
    "manual_operator_trial_facts.csv", "manual_operator_trial_review_queue.csv",
    "manual_operator_trial_evidence.json", "manual_operator_trial_evidence.md",
    "cycle_manifest.json", "cycle_summary.md",
)
MACRO_SHADOW_DIR = "macro_structure_shadow"
MACRO_OUTPUT_NAMES = (
    "macro_signal_slice.csv", "macro_structure_volatility_events.csv", "macro_level_reliability.csv",
    "macro_missed_move_diagnostics.csv", "macro_structure_volatility_replay.json",
    "macro_structure_volatility_replay.md", "ohlcv_1h.csv", "ohlcv_4h.csv",
)
INTERVALS = {"15m": timedelta(minutes=15), "1h": timedelta(hours=1), "4h": timedelta(hours=4)}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace("Z", "+00:00")
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], str | None]:
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            headers = list(reader.fieldnames or [])
            rows = [{str(k): str(v or "") for k, v in row.items()} for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return [], [], "invalid_input"
    return rows, headers, None


def _write_csv(path: Path, headers: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in headers} for row in rows)


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _validate_ohlcv(path: Path, expected_interval: str = "15m", strict_continuity: bool = False) -> tuple[pd.DataFrame | None, dict[str, Any], str | None]:
    rows, headers, error = _read_csv(path)
    if error:
        return None, {}, error
    required = {"timestamp_utc", "open", "high", "low", "close"}
    if not required.issubset(headers):
        return None, {}, "ohlcv_schema_mismatch"
    if expected_interval not in INTERVALS:
        return None, {}, "ohlcv_interval_unsupported"
    if rows and "interval" in headers and any(row.get("interval") not in {expected_interval, ""} for row in rows):
        return None, {}, "ohlcv_interval_mismatch"
    parsed: list[datetime] = []
    for row in rows:
        timestamp = _dt(row.get("timestamp_utc") or row.get("timestamp_jst"))
        if timestamp is None:
            return None, {}, "malformed_ohlcv"
        parsed.append(timestamp)
        for field in ("open", "high", "low", "close"):
            try:
                number = float(row.get(field, ""))
            except (TypeError, ValueError):
                return None, {}, "malformed_ohlcv"
            if not pd.notna(number) or number in {float("inf"), float("-inf")}:
                return None, {}, "malformed_ohlcv"
    if parsed != sorted(parsed) or len(parsed) != len(set(parsed)):
        return None, {}, "ohlcv_not_monotonic"
    if strict_continuity and any(later - earlier != INTERVALS[expected_interval] for earlier, later in zip(parsed, parsed[1:])):
        return None, {}, "ohlcv_gap"
    frame = pd.DataFrame(rows)
    metadata = {
        "rows": len(rows),
        "min_timestamp": parsed[0].isoformat() if parsed else "",
        "max_timestamp": parsed[-1].isoformat() if parsed else "",
        "source": rows[0].get("source", "") if rows else "",
        "symbol": rows[0].get("symbol", "") if rows else "",
        "interval": rows[0].get("interval", expected_interval) if rows else expected_interval,
    }
    return frame, metadata, None


def _fetch_ohlcv(path: Path, limit: int, interval: str = "15m") -> None:
    frame = fetch_klines(FetchConfig(base_url="https://contract.mexc.com", symbol="BTC_USDT", timeout_sec=5, retry_count=3, request_interval_sec=0.3), interval=interval, limit=limit)
    if frame is None or frame.empty:
        raise ValueError("public_ohlcv_empty")
    records = frame.to_dict(orient="records")
    from tools.fetch_active_plan_market_data import convert_ohlcv_to_diagnostic_rows
    rows = convert_ohlcv_to_diagnostic_rows(frame, source_label="exchange-auto-public", interval=interval, symbol="BTC_USDT")
    _write_csv(path, ["timestamp_jst", "timestamp_utc", "open", "high", "low", "close", "volume", "source", "interval", "symbol"], rows)


def _slice_inputs(candidates_path: Path, signal_path: Path, ohlcv_meta: dict[str, Any], max_lag: int, stage: Path) -> tuple[dict[str, Any], str | None]:
    candidate_rows, candidate_headers, error = _read_csv(candidates_path)
    if error:
        return {}, error
    if any(field not in candidate_headers for field in CANDIDATE_REQUIRED_HEADERS):
        return {}, "candidate_schema_mismatch"
    low = _dt(ohlcv_meta["min_timestamp"])
    high = _dt(ohlcv_meta["max_timestamp"])
    assert low is not None and high is not None
    selected: list[dict[str, str]] = []
    for row in candidate_rows:
        timestamp = _dt(row.get("timestamp_jst"))
        if timestamp is None:
            return {}, "candidate_timestamp_invalid"
        utc = timestamp.astimezone(timezone.utc)
        if utc > high:
            lag = (utc - high).total_seconds() / 60
            if lag > max_lag:
                return {}, "candidate_ahead_of_ohlcv"
        if utc >= low and utc <= high:
            selected.append(row)
        elif utc > high and (utc - high).total_seconds() / 60 <= max_lag:
            selected.append(row)
    selected.sort(key=lambda row: (_dt(row["timestamp_jst"]).astimezone(timezone.utc).isoformat(), row.get("candidate_id", "")))
    _write_csv(stage / "candidate_slice.csv", candidate_headers, selected)
    ids = {row.get("source_signal_id", "") for row in selected if row.get("source_signal_id", "")}
    signal_rows, signal_headers, error = _read_csv(signal_path)
    if error:
        return {}, error
    if any(field not in signal_headers for field in SIGNAL_HEADERS):
        return {}, "signal_schema_mismatch"
    relevant = [{key: row.get(key, "") for key in SIGNAL_HEADERS} for row in signal_rows if row.get("signal_id", "") in ids]
    missing = ids - {row.get("signal_id", "") for row in relevant}
    if missing:
        return {}, "missing_signal_context"
    indexed, duplicates, error = _identity_rows(relevant, "signal_id", SIGNAL_HEADERS)
    if error:
        return {}, "signal_identity_conflict" if error == "identity_conflict" else error
    signals = sorted(indexed.values(), key=lambda row: (_dt(row.get("timestamp_jst")).isoformat() if _dt(row.get("timestamp_jst")) else "", row.get("signal_id", "")))
    _write_csv(stage / "signal_context_slice.csv", SIGNAL_HEADERS, signals)
    return {"candidate_rows": len(selected), "candidate_signals": len(ids), "signal_rows": len(signals), "signal_duplicates": duplicates, "source_candidate_fingerprint": _sha256(candidates_path), "source_signal_fingerprint": _sha256(signal_path)}, None


def _promote(stage: Path, output_root: Path, names: list[str], replace: bool) -> None:
    existing = [output_root / name for name in names if (output_root / name).exists()]
    if existing and not replace:
        raise OSError("existing_output_schema_mismatch")
    output_root.mkdir(parents=True, exist_ok=True)
    backups: list[tuple[Path, Path]] = []
    replaced: list[Path] = []
    try:
        for name in names:
            target = output_root / name
            source = stage / name
            if target.exists():
                backup = target.with_name("." + target.name + ".p8-cycle-backup")
                backup.unlink(missing_ok=True)
                target.replace(backup)
                backups.append((target, backup))
            source.replace(target)
            replaced.append(target)
    except Exception as exc:
        for target in replaced:
            target.unlink(missing_ok=True)
        for target, backup in backups:
            if backup.exists():
                backup.replace(target)
        raise OSError("output_transaction_failed") from exc
    finally:
        for _, backup in backups:
            backup.unlink(missing_ok=True)


def _stage_ids(path: Path, field: str) -> set[str]:
    rows, _, error = _read_csv(path)
    if error:
        raise ValueError(error)
    return {row.get(field, "") for row in rows if row.get(field, "")}


def _shadow_summary(*, enabled: bool, status: str, output_subdir: str = "turning_precursor_shadow", error_codes: list[str] | None = None, slice_rows: int = 0, replay: dict[str, Any] | None = None) -> dict[str, Any]:
    from src.feedback.turning_volatility_precursor_replay import METHOD_VERSION as turning_method_version
    replay = replay or {}
    metrics = replay.get("metrics", {})
    current = metrics.get("POLICY_CURRENT_NOTIFICATION", {})
    combined = metrics.get("POLICY_COMBINED_PRECURSOR", {})
    validation = combined.get("validation", {})
    actual = replay.get("actual_evidence", {})
    return {
        "enabled": enabled, "status": status, "method_version": turning_method_version if enabled else "",
        "signal_slice_rows": slice_rows, "precursor_episodes": replay.get("episode_rows", 0),
        "resolved_episodes": combined.get("resolved_episodes", 0), "realized_move_opportunities": replay.get("realized_move_opportunities", 0),
        "current_notification_recall": current.get("large_move_recall"), "combined_recall": combined.get("large_move_recall"),
        "combined_precision": combined.get("clean_directional_precision"), "combined_false_rate": combined.get("false_precursor_rate"),
        "combined_opposite_rate": combined.get("opposite_move_rate"), "combined_whipsaw_rate": combined.get("whipsaw_rate"),
        "combined_median_lead_minutes": combined.get("median_lead_minutes"), "validation_status": replay.get("validation_status", "none"),
        "validation_up_resolved": validation.get("UP", 0), "validation_down_resolved": validation.get("DOWN", 0),
        "pinned_case_status": replay.get("pinned_case", {}).get("status", "none"),
        "actual_backed_count": actual.get("actual_backed_count", 0), "recommendation_status": replay.get("recommendation_status", "none"),
        "output_subdir": output_subdir, "error_codes": list(error_codes or []),
    }


def _promote_shadow(stage: Path, output_root: Path, replace: bool) -> None:
    target = output_root / "turning_precursor_shadow"
    if target.exists() and not replace:
        raise OSError("existing_output_schema_mismatch")
    backup = output_root / ".turning_precursor_shadow-backup"
    try:
        if target.exists():
            if backup.exists(): shutil.rmtree(backup)
            target.replace(backup)
        (stage / "turning_precursor_shadow").replace(target)
        if backup.exists(): shutil.rmtree(backup)
    except Exception as exc:
        if target.exists(): shutil.rmtree(target, ignore_errors=True)
        if backup.exists(): backup.replace(target)
        raise OSError("output_transaction_failed") from exc


def _macro_shadow_summary(*, enabled: bool, status: str, error_codes: list[str] | None = None, slice_rows: int = 0, ohlcv: dict[str, dict[str, Any]] | None = None, replay: dict[str, Any] | None = None) -> dict[str, Any]:
    from src.feedback.macro_structure_volatility_replay import METHOD_VERSION as macro_method_version, SCHEMA_VERSION as macro_schema_version
    replay = replay or {}; ohlcv = ohlcv or {}
    metrics = replay.get("metrics", {})
    current = metrics.get("current_notification", {})
    turning = metrics.get("turning_precursor_combined", {})
    corridor = metrics.get("reliable_level_acceptance_corridor", {})
    gate = replay.get("recommendation_gate", {})
    validation = replay.get("walk_forward", {})
    opportunities = replay.get("counts", {}).get("independent_opportunities", 0)
    return {
        "enabled": enabled, "status": status,
        "method_version": macro_method_version if enabled else "", "schema_version": macro_schema_version if enabled else "",
        "signal_slice_rows": slice_rows,
        "ohlcv_15m_rows": int(ohlcv.get("15m", {}).get("rows", 0)), "ohlcv_1h_rows": int(ohlcv.get("1h", {}).get("rows", 0)), "ohlcv_4h_rows": int(ohlcv.get("4h", {}).get("rows", 0)),
        "events": int(replay.get("counts", {}).get("events", 0)), "levels": int(replay.get("counts", {}).get("levels", 0)), "missed_moves": int(replay.get("counts", {}).get("missed_moves", 0)), "independent_opportunities": int(opportunities),
        "recommendation_status": replay.get("recommendation_status", "none"), "recommendation_reasons": list(gate.get("reasons", [])),
        "current_notification_recall": current.get("large_move_recall"), "turning_precursor_recall": turning.get("large_move_recall"), "reliable_level_acceptance_corridor_recall": corridor.get("large_move_recall"),
        "validation_status": validation.get("status", "none"), "validation_up_opportunities": int(gate.get("validation_up_resolved", 0)), "validation_down_opportunities": int(gate.get("validation_down_resolved", 0)),
        "continuity_status": "pass" if replay.get("coverage", {}).get("continuity_pass") else "fail" if enabled else "none",
        "output_subdir": MACRO_SHADOW_DIR, "error_codes": list(error_codes or []),
    }


def _macro_signal_slice(*, signals: Path, ohlcv_15m: Path, coverage: dict[str, dict[str, Any]], output: Path, context_hours: int = 3) -> dict[str, Any]:
    rows, _, error = _read_csv(signals)
    if error:
        raise ValueError(error)
    bounds = []
    for interval in ("15m", "1h", "4h"):
        metadata = coverage[interval]; low = _dt(metadata.get("min_timestamp")); high = _dt(metadata.get("max_timestamp"))
        if low is None or high is None:
            raise ValueError("macro_coverage_missing")
        bounds.append((low + INTERVALS[interval], high + INTERVALS[interval]))
    common_low, common_high = max(low for low, _ in bounds), min(high for _, high in bounds)
    if common_low > common_high:
        raise ValueError("macro_common_coverage_empty")
    ohlcv_rows, _, ohlcv_error = _read_csv(ohlcv_15m)
    if ohlcv_error:
        raise ValueError(ohlcv_error)
    prices = sorted(((_dt(row.get("timestamp_utc")), row.get("close", "")) for row in ohlcv_rows), key=lambda item: item[0] or datetime.min.replace(tzinfo=timezone.utc))
    output_rows: list[dict[str, str]] = []
    for row in rows:
        timestamp = _dt(row.get("timestamp_utc") or row.get("timestamp_jst"))
        if timestamp is None or timestamp > common_high or timestamp < common_low - timedelta(hours=context_hours):
            continue
        eligible = [close for opened, close in prices if opened is not None and opened + INTERVALS["15m"] <= timestamp]
        if not eligible:
            continue
        context_only = timestamp < common_low
        output_rows.append({
            "signal_id": str(row.get("signal_id", "")), "timestamp_utc": timestamp.isoformat(), "current_price": str(eligible[-1]),
            "was_notified": str(row.get("was_notified", "")), "bias": str(row.get("bias") or row.get("primary_setup_side") or ""),
            "market_map_flags": str(row.get("market_map_flags", "")), "warning_flags": str(row.get("warning_flags", "")), "risk_flags": str(row.get("risk_flags", "")),
            "active_level_role": str(row.get("active_level_role", "")), "level_flip_state": str(row.get("level_flip_state", "")), "failed_breakout_state": str(row.get("failed_breakout_state", "")), "trend_flip_state": str(row.get("trend_flip_state", "")),
            "primary_setup_reason": str(row.get("primary_setup_reason", "")), "notification_kind": str(row.get("notification_kind", "")), "primary_setup_status": str(row.get("primary_setup_status", "")), "macro_context_only": "true" if context_only else "false",
        })
    output_rows.sort(key=lambda item: (item["timestamp_utc"], item["signal_id"]))
    headers = list(output_rows[0]) if output_rows else ["signal_id", "timestamp_utc", "current_price", "was_notified", "bias", "market_map_flags", "warning_flags", "risk_flags", "active_level_role", "level_flip_state", "failed_breakout_state", "trend_flip_state", "primary_setup_reason", "notification_kind", "primary_setup_status", "macro_context_only"]
    _write_csv(output, headers, output_rows)
    return {"rows": len(output_rows), "context_rows": sum(item["macro_context_only"] == "true" for item in output_rows), "common_min_timestamp": common_low.isoformat(), "common_max_closed_timestamp": common_high.isoformat()}


def _run_macro_shadow(*, stage: Path, signals: Path, ohlcv_15m: Path, ohlcv_meta: dict[str, Any], ohlcv_limit: int) -> dict[str, Any]:
    from src.feedback.macro_structure_volatility_replay import replay_macro_structure_volatility
    macro_stage = stage / MACRO_SHADOW_DIR; macro_stage.mkdir(parents=True, exist_ok=True)
    try:
        paths = {"1h": macro_stage / "ohlcv_1h.csv", "4h": macro_stage / "ohlcv_4h.csv"}
        for interval, path in paths.items():
            _fetch_ohlcv(path, ohlcv_limit, interval)
        _, meta1, error1 = _validate_ohlcv(paths["1h"], "1h", strict_continuity=True); _, meta4, error4 = _validate_ohlcv(paths["4h"], "4h", strict_continuity=True)
        if error1 or error4:
            raise ValueError(error1 or error4 or "macro_ohlcv_invalid")
        ohlcv = {"15m": {**ohlcv_meta, "fingerprint": _sha256(ohlcv_15m)}, "1h": {**meta1, "fingerprint": _sha256(paths["1h"])}, "4h": {**meta4, "fingerprint": _sha256(paths["4h"])} }
        slice_meta = _macro_signal_slice(signals=signals, ohlcv_15m=ohlcv_15m, coverage=ohlcv, output=macro_stage / "macro_signal_slice.csv")
        replay_macro_structure_volatility(signals=macro_stage / "macro_signal_slice.csv", ohlcv_15m=ohlcv_15m, ohlcv_1h=paths["1h"], ohlcv_4h=paths["4h"], output_events_csv=macro_stage / "macro_structure_volatility_events.csv", output_levels_csv=macro_stage / "macro_level_reliability.csv", output_misses_csv=macro_stage / "macro_missed_move_diagnostics.csv", output_json=macro_stage / "macro_structure_volatility_replay.json", output_md=macro_stage / "macro_structure_volatility_replay.md", replace_output=True, performance_start_utc=slice_meta["common_min_timestamp"], performance_end_utc=slice_meta["common_max_closed_timestamp"])
        if {path.name for path in macro_stage.iterdir()} != set(MACRO_OUTPUT_NAMES):
            raise ValueError("macro_output_set_incomplete")
        replay = json.loads((macro_stage / "macro_structure_volatility_replay.json").read_text(encoding="utf-8"))
        return _macro_shadow_summary(enabled=True, status="success", slice_rows=int(slice_meta["rows"]), ohlcv=ohlcv, replay=replay)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        shutil.rmtree(macro_stage, ignore_errors=True)
        return _macro_shadow_summary(enabled=True, status="failed", error_codes=["macro_structure_shadow_failed"], ohlcv={"15m": ohlcv_meta})


def _promote_macro_shadow(stage: Path, output_root: Path, replace: bool) -> None:
    target = output_root / MACRO_SHADOW_DIR
    if target.exists() and not replace:
        raise OSError("existing_output_schema_mismatch")
    backup = output_root / ".macro_structure_shadow-backup"
    try:
        if target.exists():
            if backup.exists(): shutil.rmtree(backup)
            target.replace(backup)
        (stage / MACRO_SHADOW_DIR).replace(target)
        if backup.exists(): shutil.rmtree(backup)
    except Exception as exc:
        if target.exists(): shutil.rmtree(target, ignore_errors=True)
        if backup.exists(): backup.replace(target)
        raise OSError("output_transaction_failed") from exc


def _refresh_auxiliary_metadata(output_root: Path, report: dict[str, Any], turning: dict[str, Any], macro: dict[str, Any]) -> None:
    manifest_path = output_root / "cycle_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["turning_precursor_shadow"] = turning; manifest["macro_structure_shadow"] = macro
    manifest.setdefault("stage_statuses", {})["turning_precursor_shadow"] = turning["status"]
    manifest["stage_statuses"]["macro_structure_shadow"] = macro["status"]
    temporary = manifest_path.with_name(".cycle_manifest.aux.tmp")
    temporary.write_text(_json_text(manifest), encoding="utf-8"); temporary.replace(manifest_path)
    final_report = dict(report); final_report["turning_precursor_shadow"] = turning; final_report["macro_structure_shadow"] = macro
    summary = output_root / "cycle_summary.md"; temporary = summary.with_name(".cycle_summary.aux.tmp")
    temporary.write_text(_summary_markdown(final_report), encoding="utf-8"); temporary.replace(summary)


def _validate_stage_identity(stage: Path) -> None:
    candidate_ids = _stage_ids(stage / "candidate_slice.csv", "candidate_id")
    outcome_ids = _stage_ids(stage / "intraperiod_outcomes.csv", "candidate_id")
    if not outcome_ids.issubset(candidate_ids):
        raise ValueError("outcome_candidate_identity_mismatch")
    event_rows, _, error = _read_csv(stage / "manual_scenario_events.csv")
    if error:
        raise ValueError(error)
    event_ids = {row.get("scenario_event_id", "") for row in event_rows if row.get("scenario_event_id", "")}
    if any(row.get("candidate_id", "") not in candidate_ids for row in event_rows):
        raise ValueError("scenario_event_candidate_identity_mismatch")
    class_rows, _, error = _read_csv(stage / "manual_operator_classifications.csv")
    if error:
        raise ValueError(error)
    if any(row.get("scenario_event_id", "") not in event_ids for row in class_rows):
        raise ValueError("classification_event_identity_mismatch")
    fact_rows, _, error = _read_csv(stage / "manual_operator_trial_facts.csv")
    if error:
        raise ValueError(error)
    class_event_ids = {row.get("scenario_event_id", "") for row in class_rows}
    if any(row.get("scenario_event_id", "") not in class_event_ids for row in fact_rows):
        raise ValueError("trial_fact_event_identity_mismatch")


def _summary_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = ["# P8 Operating Cycle", "", "## Cycle status", "completed", "", "## Source coverage/freshness", json.dumps(report["source"], sort_keys=True), "", "## Resolved/unresolved/no-OHLCV", json.dumps(counts, sort_keys=True), "", "## A/B/C/STOP", json.dumps(report["class_counts"], sort_keys=True), "", "## Long/Short", json.dumps(report["side_counts"], sort_keys=True), "", "## Comparison results", json.dumps(report["comparison"], sort_keys=True), "", "## Actual-evidence coverage", json.dumps(report["actual_evidence"], sort_keys=True), "", "## Exception queue", str(report["review_queue_size"]), "", "## ISSUE-001", json.dumps(report["issue_001"], sort_keys=True), "", "## P9 readiness", json.dumps(report["p9_readiness"], sort_keys=True), "", "## Turning precursor shadow", json.dumps(report["turning_precursor_shadow"], sort_keys=True), "", "## Macro structure shadow", json.dumps(report["macro_structure_shadow"], sort_keys=True), "", "## Limitations", "Unresolved, no-OHLCV, low-confidence, and ambiguous evidence are excluded from performance claims.", "", "## Safety boundary", SAFETY, "No automatic tuning occurred.", ""]
    return "\n".join(lines)


def run_p8_operating_cycle(*, candidates: Path, signal_context: Path, ohlcv: Path, report_date: str, output_root: Path, decision_events: Path | None = None, actual_episodes: Path | None = None, actual_links: Path | None = None, output_exact_link_csv: Path | None = None, fetch_public_ohlcv: bool = False, ohlcv_limit: int = 500, max_ohlcv_lag_minutes: int = 60, dry_run: bool = False, replace_output: bool = False, include_turning_precursor_shadow: bool = False, include_macro_structure_shadow: bool = False) -> dict[str, Any]:
    if (actual_episodes is None) != (actual_links is None):
        return {"ok": False, "exit_code": 2, "errors": ["optional_actual_inputs_must_be_together"], "report_written": False}
    if not report_date.isdigit() or len(report_date) != 8:
        return {"ok": False, "exit_code": 2, "errors": ["invalid_report_date"], "report_written": False}
    parent = output_root.parent
    parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".p8-cycle-", dir=parent))
    try:
        ohlcv_stage = stage / "ohlcv.csv"
        if fetch_public_ohlcv:
            _fetch_ohlcv(ohlcv_stage, ohlcv_limit)
            ohlcv_input = ohlcv_stage
        else:
            ohlcv_input = ohlcv
            if not ohlcv_input.exists():
                return {"ok": False, "exit_code": 2, "errors": ["missing_ohlcv"], "report_written": False}
        ohlcv_df, ohlcv_meta, error = _validate_ohlcv(ohlcv_input)
        if error or ohlcv_df is None or not ohlcv_meta.get("rows"):
            return {"ok": False, "exit_code": 2, "errors": [error or "ohlcv_empty"], "report_written": False}
        lineage, error = _slice_inputs(candidates, signal_context, ohlcv_meta, max_ohlcv_lag_minutes, stage)
        if error:
            return {"ok": False, "exit_code": 2 if error != "signal_identity_conflict" else 3, "errors": [error], "report_written": False}
        candidate_slice = stage / "candidate_slice.csv"
        outcome_df = build_active_plan_intraperiod_outcome_rows(pd.read_csv(candidate_slice, keep_default_na=False), ohlcv_df, timeout_hours=24.0)
        outcome_df.to_csv(stage / "intraperiod_outcomes.csv", index=False)
        scenarios = stage / "manual_scenarios.csv"; events = stage / "manual_scenario_events.csv"
        p4 = build_manual_scenarios(candidates=candidate_slice, intraperiod_outcomes=stage / "intraperiod_outcomes.csv", scenarios_out=scenarios, events_out=events, replace_output=True)
        if not p4.get("ok"):
            return {"ok": False, "exit_code": int(p4.get("exit_code", 2)), "errors": p4.get("errors", ["p4_failed"]), "report_written": False}
        p5 = build_manual_operator_classifier(scenarios=scenarios, scenario_events=events, candidates=candidate_slice, signal_context=stage / "signal_context_slice.csv", output_csv=stage / "manual_operator_classifications.csv", output_json=stage / "manual_operator_classifications.json", output_md=stage / "manual_operator_classifications.md", report_date=report_date, replace_output=True)
        if not p5.get("ok"):
            return {"ok": False, "exit_code": int(p5.get("exit_code", 2)), "errors": p5.get("errors", ["p5_failed"]), "report_written": False}
        p8 = build_manual_operator_trial_evidence(scenarios=scenarios, scenario_events=events, classifications=stage / "manual_operator_classifications.csv", output_csv=stage / "manual_operator_trial_facts.csv", output_queue_csv=stage / "manual_operator_trial_review_queue.csv", output_json=stage / "manual_operator_trial_evidence.json", output_md=stage / "manual_operator_trial_evidence.md", report_date=report_date, decision_events=decision_events, trade_episodes=actual_episodes, episode_links=actual_links, output_exact_link_csv=(stage / "manual_operator_exact_link_observations.csv") if output_exact_link_csv is not None else None, replace_output=True)
        if not p8.get("ok"):
            return {"ok": False, "exit_code": int(p8.get("exit_code", 2)), "errors": p8.get("errors", ["p8_failed"]), "report_written": False}
        _validate_stage_identity(stage)
        outcome_counts = dict(sorted(Counter(str(row.get("outcome", "")) for row in outcome_df.to_dict(orient="records")).items()))
        shadow = _shadow_summary(enabled=False, status="disabled")
        macro_shadow = _macro_shadow_summary(enabled=False, status="disabled")
        shadow_stage = stage / "turning_precursor_shadow"
        if include_turning_precursor_shadow:
            try:
                from src.feedback.turning_volatility_precursor_replay import build_bounded_signal_slice, replay_turning_volatility_precursors
                shadow_stage.mkdir(parents=True, exist_ok=True)
                slice_meta = build_bounded_signal_slice(signals=signal_context, output=shadow_stage / "turning_signal_slice.csv", min_timestamp=ohlcv_meta["min_timestamp"], max_timestamp=ohlcv_meta["max_timestamp"], context_hours=3)
                replay = replay_turning_volatility_precursors(signals=shadow_stage / "turning_signal_slice.csv", ohlcv=ohlcv_input, output_csv=shadow_stage / "turning_volatility_precursor_events.csv", output_json=shadow_stage / "turning_volatility_precursor_replay.json", output_md=shadow_stage / "turning_volatility_precursor_replay.md", actual_episodes=actual_episodes, actual_links=actual_links, replace_output=True)
                if replay.get("ok"):
                    shadow = _shadow_summary(enabled=True, status="success", slice_rows=int(slice_meta.get("rows", 0)), replay=replay)
                else:
                    shadow = _shadow_summary(enabled=True, status="failed", error_codes=list(replay.get("error_codes", ["turning_precursor_shadow_failed"])), slice_rows=int(slice_meta.get("rows", 0)))
                    shutil.rmtree(shadow_stage, ignore_errors=True)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                shadow = _shadow_summary(enabled=True, status="failed", error_codes=[str(exc) or "turning_precursor_shadow_failed"])
                shutil.rmtree(shadow_stage, ignore_errors=True)
        if include_macro_structure_shadow:
            macro_shadow = _run_macro_shadow(stage=stage, signals=signal_context, ohlcv_15m=ohlcv_input, ohlcv_meta=ohlcv_meta, ohlcv_limit=ohlcv_limit)
        report = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "report_date": report_date, "source": {"candidates": candidates.name, "signal_context": signal_context.name, "ohlcv": ohlcv.name if not fetch_public_ohlcv else "public_fetch", "ohlcv_freshness": "valid", **ohlcv_meta}, "lineage": lineage, "counts": {"candidate_rows": lineage["candidate_rows"], "candidate_signals": lineage["candidate_signals"], "outcome_counts": outcome_counts, **p8.get("counts", {})}, "class_counts": p8.get("class_distribution", {}), "side_counts": p8.get("breakdowns", {}).get("side", {}), "comparison": p8.get("comparison", {}), "actual_evidence": p8.get("actual_evidence", {}), "review_queue_size": p8.get("review_queue_size", 0), "issue_001": p8.get("global_stop_opportunity", {}), "p9_readiness": p8.get("p9_readiness", {}), "input_fingerprints": {"candidates": _sha256(candidates), "signal_context": _sha256(signal_context), "ohlcv": _sha256(ohlcv_input)}, "no_automatic_tuning": True, "safety_boundary": SAFETY}
        report["turning_precursor_shadow"] = shadow
        report["macro_structure_shadow"] = macro_shadow
        manifest = dict(report); manifest["generated_at_utc"] = ohlcv_meta["max_timestamp"]; manifest["stage_statuses"] = {"candidate_slice": "ok", "signal_context_slice": "ok", "intraperiod_outcomes": "ok", "p4": "ok", "p5": "ok", "p8": "ok", "turning_precursor_shadow": shadow["status"], "macro_structure_shadow": macro_shadow["status"]}; manifest["output_fingerprints"] = {}
        for name in OUTPUT_NAMES:
            if name in {"cycle_manifest.json", "cycle_summary.md"}: continue
            manifest["output_fingerprints"][name] = _sha256(stage / name)
        (stage / "cycle_manifest.json").write_text(_json_text(manifest), encoding="utf-8")
        (stage / "cycle_summary.md").write_text(_summary_markdown(report), encoding="utf-8")
        if dry_run:
            return {"ok": True, "exit_code": 0, "dry_run": True, "report_written": False, "counts": report["counts"], "class_counts": report["class_counts"], "issue_001": report["issue_001"], "p9_readiness": report["p9_readiness"], "turning_precursor_shadow": shadow, "macro_structure_shadow": macro_shadow, "safety_boundary": SAFETY}
        try:
            output_names = list(OUTPUT_NAMES)
            if output_exact_link_csv is not None:
                output_names.append("manual_operator_exact_link_observations.csv")
            _promote(stage, output_root, output_names, replace_output)
        except OSError as exc:
            return {"ok": False, "exit_code": 4, "errors": [str(exc)], "report_written": False}
        if shadow["status"] == "success":
            try:
                _promote_shadow(stage, output_root, replace_output)
            except OSError:
                shadow = _shadow_summary(enabled=True, status="failed", error_codes=["turning_precursor_shadow_failed"])
        if macro_shadow["status"] == "success":
            try:
                _promote_macro_shadow(stage, output_root, replace_output)
            except OSError:
                macro_shadow = _macro_shadow_summary(enabled=True, status="failed", error_codes=["macro_structure_shadow_failed"], ohlcv={"15m": ohlcv_meta})
        _refresh_auxiliary_metadata(output_root, report, shadow, macro_shadow)
        warnings = (["turning_precursor_shadow_failed"] if shadow["status"] == "failed" else []) + (["macro_structure_shadow_failed"] if macro_shadow["status"] == "failed" else [])
        return {"ok": True, "exit_code": 0, "report_written": True, "output_root": output_root.name, "outputs": list(OUTPUT_NAMES), "lineage": report["lineage"], "counts": report["counts"], "class_counts": report["class_counts"], "side_counts": report["side_counts"], "comparison": report["comparison"], "issue_001": report["issue_001"], "review_queue_size": report["review_queue_size"], "p9_readiness": report["p9_readiness"], "turning_precursor_shadow": shadow, "macro_structure_shadow": macro_shadow, "warnings": warnings, "safety_boundary": SAFETY}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "exit_code": 2, "errors": [str(exc) or "input_invalid"], "report_written": False}
    finally:
        shutil.rmtree(stage, ignore_errors=True)
