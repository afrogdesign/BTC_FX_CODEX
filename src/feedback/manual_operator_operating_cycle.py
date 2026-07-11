"""Deterministic, report-only P8 operating-cycle runner."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
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


def _validate_ohlcv(path: Path) -> tuple[pd.DataFrame | None, dict[str, Any], str | None]:
    rows, headers, error = _read_csv(path)
    if error:
        return None, {}, error
    required = {"timestamp_utc", "open", "high", "low", "close"}
    if not required.issubset(headers):
        return None, {}, "ohlcv_schema_mismatch"
    if rows and "interval" in headers and any(row.get("interval") not in {"15m", ""} for row in rows):
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
    frame = pd.DataFrame(rows)
    metadata = {
        "rows": len(rows),
        "min_timestamp": parsed[0].isoformat() if parsed else "",
        "max_timestamp": parsed[-1].isoformat() if parsed else "",
        "source": rows[0].get("source", "") if rows else "",
        "symbol": rows[0].get("symbol", "") if rows else "",
        "interval": rows[0].get("interval", "15m") if rows else "15m",
    }
    return frame, metadata, None


def _fetch_ohlcv(path: Path, limit: int) -> None:
    frame = fetch_klines(FetchConfig(base_url="https://contract.mexc.com", symbol="BTC_USDT", timeout_sec=5, retry_count=3, request_interval_sec=0.3), interval="15m", limit=limit)
    if frame is None or frame.empty:
        raise ValueError("public_ohlcv_empty")
    records = frame.to_dict(orient="records")
    from tools.fetch_active_plan_market_data import convert_ohlcv_to_diagnostic_rows
    rows = convert_ohlcv_to_diagnostic_rows(frame, source_label="exchange-auto-public", interval="15m", symbol="BTC_USDT")
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
    lines = ["# P8 Operating Cycle", "", "## Cycle status", "completed", "", "## Source coverage/freshness", json.dumps(report["source"], sort_keys=True), "", "## Resolved/unresolved/no-OHLCV", json.dumps(counts, sort_keys=True), "", "## A/B/C/STOP", json.dumps(report["class_counts"], sort_keys=True), "", "## Long/Short", json.dumps(report["side_counts"], sort_keys=True), "", "## Comparison results", json.dumps(report["comparison"], sort_keys=True), "", "## Actual-evidence coverage", json.dumps(report["actual_evidence"], sort_keys=True), "", "## Exception queue", str(report["review_queue_size"]), "", "## ISSUE-001", json.dumps(report["issue_001"], sort_keys=True), "", "## P9 readiness", json.dumps(report["p9_readiness"], sort_keys=True), "", "## Limitations", "Unresolved, no-OHLCV, low-confidence, and ambiguous evidence are excluded from performance claims.", "", "## Safety boundary", SAFETY, "No automatic tuning occurred.", ""]
    return "\n".join(lines)


def run_p8_operating_cycle(*, candidates: Path, signal_context: Path, ohlcv: Path, report_date: str, output_root: Path, decision_events: Path | None = None, actual_episodes: Path | None = None, actual_links: Path | None = None, fetch_public_ohlcv: bool = False, ohlcv_limit: int = 500, max_ohlcv_lag_minutes: int = 60, dry_run: bool = False, replace_output: bool = False) -> dict[str, Any]:
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
        p8 = build_manual_operator_trial_evidence(scenarios=scenarios, scenario_events=events, classifications=stage / "manual_operator_classifications.csv", output_csv=stage / "manual_operator_trial_facts.csv", output_queue_csv=stage / "manual_operator_trial_review_queue.csv", output_json=stage / "manual_operator_trial_evidence.json", output_md=stage / "manual_operator_trial_evidence.md", report_date=report_date, decision_events=decision_events, trade_episodes=actual_episodes, episode_links=actual_links, replace_output=True)
        if not p8.get("ok"):
            return {"ok": False, "exit_code": int(p8.get("exit_code", 2)), "errors": p8.get("errors", ["p8_failed"]), "report_written": False}
        _validate_stage_identity(stage)
        outcome_counts = dict(sorted(Counter(str(row.get("outcome", "")) for row in outcome_df.to_dict(orient="records")).items()))
        report = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "report_date": report_date, "source": {"candidates": candidates.name, "signal_context": signal_context.name, "ohlcv": ohlcv.name if not fetch_public_ohlcv else "public_fetch", "ohlcv_freshness": "valid", **ohlcv_meta}, "lineage": lineage, "counts": {"candidate_rows": lineage["candidate_rows"], "candidate_signals": lineage["candidate_signals"], "outcome_counts": outcome_counts, **p8.get("counts", {})}, "class_counts": p8.get("class_distribution", {}), "side_counts": p8.get("breakdowns", {}).get("side", {}), "comparison": p8.get("comparison", {}), "actual_evidence": p8.get("actual_evidence", {}), "review_queue_size": p8.get("review_queue_size", 0), "issue_001": p8.get("global_stop_opportunity", {}), "p9_readiness": p8.get("p9_readiness", {}), "input_fingerprints": {"candidates": _sha256(candidates), "signal_context": _sha256(signal_context), "ohlcv": _sha256(ohlcv_input)}, "no_automatic_tuning": True, "safety_boundary": SAFETY}
        manifest = dict(report); manifest["generated_at_utc"] = ohlcv_meta["max_timestamp"]; manifest["stage_statuses"] = {"candidate_slice": "ok", "signal_context_slice": "ok", "intraperiod_outcomes": "ok", "p4": "ok", "p5": "ok", "p8": "ok"}; manifest["output_fingerprints"] = {}
        for name in OUTPUT_NAMES:
            if name in {"cycle_manifest.json", "cycle_summary.md"}: continue
            manifest["output_fingerprints"][name] = _sha256(stage / name)
        (stage / "cycle_manifest.json").write_text(_json_text(manifest), encoding="utf-8")
        (stage / "cycle_summary.md").write_text(_summary_markdown(report), encoding="utf-8")
        if dry_run:
            return {"ok": True, "exit_code": 0, "dry_run": True, "report_written": False, "counts": report["counts"], "class_counts": report["class_counts"], "issue_001": report["issue_001"], "p9_readiness": report["p9_readiness"], "safety_boundary": SAFETY}
        try:
            _promote(stage, output_root, list(OUTPUT_NAMES), replace_output)
        except OSError as exc:
            return {"ok": False, "exit_code": 4, "errors": [str(exc)], "report_written": False}
        return {"ok": True, "exit_code": 0, "report_written": True, "output_root": output_root.name, "outputs": list(OUTPUT_NAMES), "lineage": report["lineage"], "counts": report["counts"], "class_counts": report["class_counts"], "side_counts": report["side_counts"], "comparison": report["comparison"], "issue_001": report["issue_001"], "review_queue_size": report["review_queue_size"], "p9_readiness": report["p9_readiness"], "safety_boundary": SAFETY}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "exit_code": 2, "errors": [str(exc) or "input_invalid"], "report_written": False}
    finally:
        shutil.rmtree(stage, ignore_errors=True)
