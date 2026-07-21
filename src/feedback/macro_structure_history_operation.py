"""Deterministic, report-only chronological rollup of M-OPS1 artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

METHOD_VERSION = "macro_structure_history_operation.v2"
SCHEMA_VERSION = "macro_structure_history_operation.v2"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
OUTPUT_NAMES = (
    "macro_structure_history.json",
    "macro_structure_history.md",
    "macro_snapshot_history.csv",
    "macro_level_history.csv",
    "macro_structure_changes.csv",
    "run_manifest.json",
)
LEVEL_FIELDS = (
    "level_id", "side", "role", "low", "high", "center", "source_timeframes",
    "first_seen_at", "last_confirmed_at", "touch_count", "clean_rejection_count",
    "break_count", "false_break_reclaim_count", "lifecycle", "reliability_score",
    "reliability_band", "distance_from_price_pct", "distance_from_price_atr", "reason_codes",
)
CSV_FIELDS = (
    "schema_version", "method_version", "symbol", "checkpoint_index", "checkpoint_id", "level_status", *LEVEL_FIELDS,
    "reliability_score_delta", "reliability_band_transition", "role_transition",
    "lifecycle_transition", "touch_count_delta", "clean_rejection_count_delta",
    "break_count_delta", "false_break_reclaim_count_delta", "geometry_changed",
    "previous_checkpoint_id", "current_checkpoint_id", "last_observed_checkpoint_id",
    "observation_present", "retirement_status",
)
SNAPSHOT_FIELDS = (
    "schema_version", "method_version", "symbol", "checkpoint_index", "checkpoint_id", "as_of_utc", "evaluated_at_utc",
    "structure_state", "price_location", "location_percentile", "current_price",
    "nearest_reliable_support_id", "nearest_reliable_resistance_id",
    "next_upside_target_id", "next_downside_target_id", "upside_obstruction",
    "downside_obstruction", "volatility_state", "expansion_risk", "directional_activation",
    "stale_status", "continuity_status", "data_quality_status", "reliability_band_counts",
    "previous_checkpoint_id", "transition_status", "canonical_structural_run_id",
    "latest_evaluation_run_id", "latest_evaluated_at_utc",
)
SNAPSHOT_CHANGE_FIELDS = (
    "structure_state", "price_location", "location_percentile", "current_price",
    "nearest_reliable_support_id", "nearest_reliable_resistance_id", "next_upside_target_id",
    "next_downside_target_id", "upside_obstruction", "downside_obstruction", "volatility_state",
    "expansion_risk", "directional_activation", "stale_status", "continuity_status",
    "data_quality_status", "reliability_band_counts",
)
CHANGE_FIELDS = (
    "schema_version", "method_version", "symbol", "checkpoint_index", "checkpoint_id", "previous_checkpoint_id", "change_type", "level_id",
    "field", "previous_value", "current_value",
)
REQUIRED_INPUT_FILES = (
    "macro_structure_snapshot.json", "macro_structure_snapshot.md",
    "macro_level_reliability.csv", "run_manifest.json",
)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _compact_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"invalid_source_{field}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid_source_{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"invalid_source_{field}")
    return parsed.astimezone(timezone.utc)


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _delta(current: Any, previous: Any) -> float | str:
    a, b = _number(current), _number(previous)
    return round(a - b, 10) if a is not None and b is not None else ""


def _stable_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _text(value)


def _read_source(run_dir: Path, symbol: str) -> dict[str, Any]:
    if run_dir.name[:4] != "run_" or not run_dir.is_dir():
        raise ValueError("invalid_source_run")
    paths = {name: run_dir / name for name in REQUIRED_INPUT_FILES}
    if not all(path.is_file() for path in paths.values()):
        raise ValueError("incomplete_source_run")
    try:
        snapshot = json.loads(paths[REQUIRED_INPUT_FILES[0]].read_text(encoding="utf-8"))
        manifest = json.loads(paths[REQUIRED_INPUT_FILES[3]].read_text(encoding="utf-8"))
        with paths[REQUIRED_INPUT_FILES[2]].open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = set(reader.fieldnames or [])
            rows = list(reader)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        raise ValueError("invalid_source_run") from exc
    if not isinstance(snapshot, dict) or not isinstance(manifest, dict):
        raise ValueError("invalid_source_run")
    run_id = _text(snapshot.get("run_id"))
    snapshot_id = _text(snapshot.get("snapshot_id"))
    if run_id != run_dir.name or run_id != _text(manifest.get("run_id")):
        raise ValueError("source_run_identity_mismatch")
    if not snapshot_id or snapshot_id != _text(manifest.get("snapshot_id")):
        raise ValueError("source_snapshot_identity_mismatch")
    if _text(snapshot.get("symbol")) != symbol:
        raise ValueError("source_symbol_mismatch")
    if not _text(snapshot.get("schema_version")) or not _text(snapshot.get("method_version")) or not _text(snapshot.get("m1_method_version")):
        raise ValueError("source_version_missing")
    if _text(manifest.get("schema_version")) != _text(snapshot.get("schema_version")) or _text(manifest.get("method_version")) != _text(snapshot.get("method_version")):
        raise ValueError("source_version_mismatch")
    if not _text(manifest.get("as_of_utc")) or not _text(manifest.get("evaluated_at_utc")):
        raise ValueError("source_manifest_timestamp_missing")
    as_of = _utc(snapshot.get("as_of_utc"), "as_of_utc")
    evaluated = _utc(snapshot.get("evaluated_at_utc"), "evaluated_at_utc")
    if _utc(manifest.get("as_of_utc"), "manifest_as_of_utc") != as_of:
        raise ValueError("source_timestamp_mismatch")
    if _utc(manifest.get("evaluated_at_utc"), "manifest_evaluated_at_utc") != evaluated:
        raise ValueError("source_timestamp_mismatch")
    if _text(manifest.get("source")) != "public_ohlcv_only" or manifest.get("report_only") is not True:
        raise ValueError("source_boundary_invalid")
    if manifest.get("automatic_order_allowed") is not False or manifest.get("private_actual_trade_input") is not False:
        raise ValueError("source_boundary_invalid")
    if not set(LEVEL_FIELDS).issubset(fieldnames):
        raise ValueError("source_level_schema_invalid")
    level_ids = [_zone_id(row.get("level_id")) for row in rows]
    if any(not level_id for level_id in level_ids):
        raise ValueError("source_level_id_missing")
    if len(level_ids) != len(set(level_ids)):
        raise ValueError("source_level_id_duplicate")
    fingerprints = snapshot.get("input_fingerprints")
    if not isinstance(fingerprints, dict) or not fingerprints:
        raise ValueError("source_fingerprint_missing")
    if manifest.get("input_fingerprints") not in (None, fingerprints):
        raise ValueError("source_fingerprint_mismatch")
    source_hash = hashlib.sha256(b"".join((run_dir / name).read_bytes() for name in REQUIRED_INPUT_FILES)).hexdigest()
    structural_key = {
        "symbol": symbol,
        "as_of_utc": as_of.isoformat(),
        "m1_method_version": _text(snapshot.get("m1_method_version")),
        "input_fingerprints": fingerprints,
    }
    checkpoint_id = "checkpoint_" + hashlib.sha256(_compact_json_bytes(structural_key)).hexdigest()[:20]
    return {
        "run_id": run_id, "snapshot_id": snapshot_id, "snapshot": snapshot, "manifest": manifest,
        "levels": rows, "as_of": as_of, "evaluated": evaluated, "checkpoint_id": checkpoint_id,
        "source_hash": source_hash, "structural_key": structural_key,
    }


def _discover(snapshot_root: Path, symbol: str) -> list[dict[str, Any]]:
    if not snapshot_root.is_dir():
        raise ValueError("snapshot_root_missing")
    runs = [entry for entry in snapshot_root.iterdir() if entry.is_dir() and entry.name.startswith("run_")]
    if not runs:
        raise ValueError("no_complete_source_runs")
    records = [_read_source(run_dir, symbol) for run_dir in sorted(runs, key=lambda path: path.name)]
    return sorted(records, key=lambda item: (item["as_of"], item["evaluated"], item["run_id"]))


def _checkpoint_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        groups.setdefault(record["checkpoint_id"], []).append(record)
    canonical = sorted((min(group, key=lambda item: (item["evaluated"], item["run_id"])) for group in groups.values()), key=lambda item: (item["as_of"], item["evaluated"], item["run_id"]))
    return canonical, records


def _zone_id(value: Any) -> str:
    return _text(value)


def _level_row(level: dict[str, Any], checkpoint: dict[str, Any], previous: dict[str, Any] | None, status: str, previous_checkpoint_id: str, current_checkpoint_id: str, *, observation_present: bool = True, last_observed_checkpoint_id: str = "") -> dict[str, Any]:
    row = {field: _text(level.get(field)) for field in LEVEL_FIELDS}
    prior = previous or {}
    row.update({
        "symbol": checkpoint["snapshot"]["symbol"], "checkpoint_index": checkpoint["index"],
        "checkpoint_id": checkpoint["checkpoint_id"], "level_status": status,
        "reliability_score_delta": _delta(level.get("reliability_score"), prior.get("reliability_score")) if observation_present else "",
        "reliability_band_transition": f"{_text(prior.get('reliability_band'))}->{_text(level.get('reliability_band'))}" if observation_present and previous and prior.get("reliability_band") != level.get("reliability_band") else "",
        "role_transition": f"{_text(prior.get('role'))}->{_text(level.get('role'))}" if observation_present and previous and prior.get("role") != level.get("role") else "",
        "lifecycle_transition": f"{_text(prior.get('lifecycle'))}->{_text(level.get('lifecycle'))}" if observation_present and previous and prior.get("lifecycle") != level.get("lifecycle") else "",
        "touch_count_delta": _delta(level.get("touch_count"), prior.get("touch_count")) if observation_present else "",
        "clean_rejection_count_delta": _delta(level.get("clean_rejection_count"), prior.get("clean_rejection_count")) if observation_present else "",
        "break_count_delta": _delta(level.get("break_count"), prior.get("break_count")) if observation_present else "",
        "false_break_reclaim_count_delta": _delta(level.get("false_break_reclaim_count"), prior.get("false_break_reclaim_count")) if observation_present else "",
        "geometry_changed": bool(observation_present and previous and any(_stable_value(level.get(field)) != _stable_value(prior.get(field)) for field in ("low", "high", "center", "source_timeframes"))),
        "previous_checkpoint_id": previous_checkpoint_id, "current_checkpoint_id": current_checkpoint_id,
        "last_observed_checkpoint_id": last_observed_checkpoint_id or current_checkpoint_id,
        "observation_present": observation_present, "retirement_status": "not_established",
    })
    return row


def _snapshot_row(record: dict[str, Any], index: int, previous: dict[str, Any] | None, latest_evaluation: dict[str, Any]) -> dict[str, Any]:
    snapshot = record["snapshot"]
    def nested_id(name: str) -> str:
        value = snapshot.get(name) or {}
        return _text(value.get("level_id")) if isinstance(value, dict) else ""
    row = {
        "symbol": snapshot["symbol"], "checkpoint_index": index, "checkpoint_id": record["checkpoint_id"],
        "as_of_utc": record["as_of"].isoformat(), "evaluated_at_utc": record["evaluated"].isoformat(),
        "structure_state": _text(snapshot.get("structure_state")), "price_location": _text(snapshot.get("price_location")),
        "location_percentile": snapshot.get("location_percentile", ""), "current_price": snapshot.get("current_price", ""),
        "nearest_reliable_support_id": nested_id("nearest_reliable_support"), "nearest_reliable_resistance_id": nested_id("nearest_reliable_resistance"),
        "next_upside_target_id": nested_id("next_upside_target"), "next_downside_target_id": nested_id("next_downside_target"),
        "upside_obstruction": _stable_value(snapshot.get("upside_obstruction", "")), "downside_obstruction": _stable_value(snapshot.get("downside_obstruction", "")),
        "volatility_state": _text(snapshot.get("volatility_state")), "expansion_risk": _text(snapshot.get("expansion_risk")),
        "directional_activation": _text(snapshot.get("directional_activation")), "stale_status": _text(snapshot.get("stale_status")),
        "continuity_status": _text(snapshot.get("continuity_status")), "data_quality_status": _text(snapshot.get("data_quality_status")),
        "reliability_band_counts": snapshot.get("reliability_band_counts", {}),
        "previous_checkpoint_id": previous["checkpoint_id"] if previous else "", "transition_status": "continued" if previous else "no_previous_transition",
        "canonical_structural_run_id": record["run_id"], "latest_evaluation_run_id": latest_evaluation["run_id"],
        "latest_evaluated_at_utc": latest_evaluation["evaluated"].isoformat(),
    }
    return row


def _csv_bytes(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> bytes:
    from io import StringIO
    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=list(fields), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: _stable_value(row.get(field, "")) for field in fields})
    return out.getvalue().encode("utf-8")


def _change_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in rows:
        if row["level_status"] == "first_observation":
            continue
        for field, transition in (("reliability_band", row["reliability_band_transition"]), ("role", row["role_transition"]), ("lifecycle", row["lifecycle_transition"])):
            if transition:
                before, after = transition.split("->", 1)
                changes.append({"symbol": row["symbol"], "checkpoint_index": row["checkpoint_index"], "checkpoint_id": row["checkpoint_id"], "previous_checkpoint_id": row["previous_checkpoint_id"], "change_type": "level_transition", "level_id": row["level_id"], "field": field, "previous_value": before, "current_value": after})
        if row["level_status"] in {"absent_from_checkpoint", "absent_from_latest", "reappeared"}:
            changes.append({"symbol": row["symbol"], "checkpoint_index": row["checkpoint_index"], "checkpoint_id": row["checkpoint_id"], "previous_checkpoint_id": row["previous_checkpoint_id"], "change_type": row["level_status"], "level_id": row["level_id"], "field": "level_id", "previous_value": row["level_id"], "current_value": row["level_id"]})
        if row["geometry_changed"]:
            changes.append({"symbol": row["symbol"], "checkpoint_index": row["checkpoint_index"], "checkpoint_id": row["checkpoint_id"], "previous_checkpoint_id": row["previous_checkpoint_id"], "change_type": "level_transition", "level_id": row["level_id"], "field": "geometry", "previous_value": "changed", "current_value": "changed"})
    return changes


def _snapshot_change_rows(snapshot_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for index, current in enumerate(snapshot_rows):
        previous = snapshot_rows[index - 1] if index else None
        if previous is None:
            changes.append({"symbol": current["symbol"], "checkpoint_index": current["checkpoint_index"], "checkpoint_id": current["checkpoint_id"], "previous_checkpoint_id": "", "change_type": "no_previous_transition", "level_id": "", "field": "snapshot", "previous_value": "", "current_value": ""})
            continue
        for field in SNAPSHOT_CHANGE_FIELDS:
            before, after = _stable_value(previous.get(field)), _stable_value(current.get(field))
            if before != after:
                changes.append({"symbol": current["symbol"], "checkpoint_index": current["checkpoint_index"], "checkpoint_id": current["checkpoint_id"], "previous_checkpoint_id": current["previous_checkpoint_id"], "change_type": "snapshot_transition", "level_id": "", "field": field, "previous_value": before, "current_value": after})
    return changes


def _evaluation_fields(record: dict[str, Any], canonical_run_id: str) -> dict[str, Any]:
    snapshot = record["snapshot"]
    return {
        "run_id": record["run_id"], "snapshot_id": record["snapshot_id"], "checkpoint_id": record["checkpoint_id"],
        "as_of_utc": record["as_of"].isoformat(), "evaluated_at_utc": record["evaluated"].isoformat(),
        "canonical_structural_run_id": canonical_run_id, "is_canonical_structural_source": record["run_id"] == canonical_run_id, "canonical": record["run_id"] == canonical_run_id,
        "stale_status": snapshot.get("stale_status", ""), "stale_timeframes": snapshot.get("stale_timeframes", []),
        "freshness": snapshot.get("freshness", {}), "continuity_status": snapshot.get("continuity_status", ""),
        "data_quality_status": snapshot.get("data_quality_status", ""), "result_status": snapshot.get("result_status", ""),
        "reason_codes": snapshot.get("reason_codes", []),
    }


def _event_lines(events: list[dict[str, Any]], formatter: Any) -> list[str]:
    bounded = events[-10:]
    return [formatter(event) for event in bounded] if bounded else ["- none"]


def _markdown(history: dict[str, Any]) -> str:
    latest = history["structural_checkpoints"][-1] if history["structural_checkpoints"] else {}
    changes = history.get("structure_changes", [])
    levels = history.get("level_history", [])
    evaluations = history.get("evaluation_history", [])
    snapshot_changes = [row for row in changes if row.get("change_type") == "snapshot_transition"]
    reliability = [row for row in changes if row.get("field") == "reliability_band"]
    roles = [row for row in changes if row.get("field") == "role"]
    lifecycles = [row for row in changes if row.get("field") == "lifecycle"]
    absences = [row for row in changes if row.get("change_type") in {"absent_from_checkpoint", "absent_from_latest"}]
    reappearances = [row for row in changes if row.get("change_type") == "reappeared"]
    stale = [row for row in evaluations if row.get("stale_status") == "stale" or row.get("continuity_status") == "discontinuous" or row.get("data_quality_status") == "discontinuous"]
    lines = [
        "# Macro Structure Chronological History", "", f"- schema: `{history['schema_version']}`", f"- method: `{history['method_version']}`", f"- symbol: `{history['symbol']}`", f"- evaluations: `{history['evaluation_count']}`", f"- structural checkpoints: `{history['structural_checkpoint_count']}`", f"- first cutoff: `{history.get('first_as_of_utc', '')}`", f"- latest cutoff: `{history.get('latest_as_of_utc', '')}`", "", "## Latest structural changes", "", f"- canonical structural run: `{latest.get('canonical_structural_run_id', '')}`", f"- latest evaluation run: `{latest.get('latest_evaluation_run_id', '')}`", f"- latest structure: `{latest.get('structure_state', '')}`", f"- latest location: `{latest.get('price_location', '')}`", *_event_lines(snapshot_changes, lambda row: f"- {row['field']}: `{row['previous_value']}` -> `{row['current_value']}`"), "", "## Reliability upgrades and downgrades", *_event_lines(reliability, lambda row: f"- level `{row['level_id']}` at checkpoint `{row['checkpoint_id']}`: `{row['previous_value']}` -> `{row['current_value']}`"), "", "## Role changes", *_event_lines(roles, lambda row: f"- level `{row['level_id']}`: `{row['previous_value']}` -> `{row['current_value']}` at `{row['checkpoint_id']}`"), "", "## Lifecycle changes", *_event_lines(lifecycles, lambda row: f"- level `{row['level_id']}`: `{row['previous_value']}` -> `{row['current_value']}` at `{row['checkpoint_id']}`"), "", "## Absence from checkpoint/latest", *_event_lines(absences, lambda row: f"- `{row['change_type']}`: level `{row['level_id']}` at `{row['checkpoint_id']}`"), "", "## Reappearances", *_event_lines(reappearances, lambda row: f"- level `{row['level_id']}` reappeared at `{row['checkpoint_id']}`"), "", "## Stale or discontinuous evaluations", *_event_lines(stale, lambda row: f"- run `{row['run_id']}` at `{row['evaluated_at_utc']}`: stale=`{row['stale_status']}`, continuity=`{row['continuity_status']}`, data_quality=`{row['data_quality_status']}`, reasons=`{','.join(row.get('reason_codes', []))}`"), "", "## Evidence limitations", "", "A missing level is not permanent retirement; each absence has `retirement_status=not_established` unless an accepted source field establishes retirement.", "", "## Safety boundary", "", SAFETY, ""]
    return "\n".join(lines)


def _publish(output_root: Path, history_id: str, files: dict[str, bytes], latest: dict[str, Any]) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    target = output_root / history_id
    stage = Path(tempfile.mkdtemp(prefix=".macro-history-", dir=output_root))
    try:
        for name, content in files.items():
            (stage / name).write_bytes(content)
        if target.exists():
            if not target.is_dir() or not all((target / name).is_file() for name in OUTPUT_NAMES):
                raise OSError("incomplete_existing_history")
            if any((target / name).read_bytes() != (stage / name).read_bytes() for name in OUTPUT_NAMES):
                raise OSError("existing_history_conflict")
            shutil.rmtree(stage)
        else:
            stage.replace(target)
        latest_stage = output_root / ".latest.json.tmp"
        latest_stage.write_bytes(_compact_json_bytes(latest))
        latest_stage.replace(output_root / "latest.json")
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def build_macro_structure_history(*, snapshot_root: Path = Path("local/reports/macro_structure"), output_root: Path = Path("local/reports/macro_structure/history"), symbol: str = "BTC_USDT") -> dict[str, Any]:
    try:
        records = _discover(snapshot_root, symbol)
        canonical, evaluations = _checkpoint_records(records)
        evaluations_by_checkpoint: dict[str, list[dict[str, Any]]] = {}
        for record in evaluations:
            evaluations_by_checkpoint.setdefault(record["checkpoint_id"], []).append(record)
        canonical_by_checkpoint = {record["checkpoint_id"]: record for record in canonical}
        latest_evaluation_by_checkpoint = {
            checkpoint_id: max(group, key=lambda item: (item["evaluated"], item["run_id"]))
            for checkpoint_id, group in evaluations_by_checkpoint.items()
        }
        for index, record in enumerate(canonical):
            record["index"] = index
        snapshot_rows = [_snapshot_row(record, index, canonical[index - 1] if index else None, latest_evaluation_by_checkpoint[record["checkpoint_id"]]) for index, record in enumerate(canonical)]
        level_rows: list[dict[str, Any]] = []
        prior_levels: dict[str, dict[str, Any]] = {}
        last_observed_levels: dict[str, dict[str, Any]] = {}
        prior_checkpoint_id = ""
        for index, record in enumerate(canonical):
            current_levels = {_zone_id(row.get("level_id")): row for row in record["levels"] if _zone_id(row.get("level_id"))}
            previous_ids = set(prior_levels)
            current_ids = set(current_levels)
            for level_id in sorted(current_ids):
                previous = last_observed_levels.get(level_id)
                status = "reappeared" if previous is not None and level_id not in prior_levels else "first_observation" if previous is None else "continued"
                previous_observation_checkpoint_id = "" if status == "first_observation" else previous.get("_last_observed_checkpoint_id", prior_checkpoint_id)
                level_rows.append(_level_row(current_levels[level_id], record, previous, status, previous_observation_checkpoint_id, record["checkpoint_id"], last_observed_checkpoint_id=record["checkpoint_id"]))
            for level_id in sorted(set(last_observed_levels) - current_ids):
                status = "absent_from_latest" if index == len(canonical) - 1 else "absent_from_checkpoint"
                last_observed_checkpoint_id = last_observed_levels[level_id]["_last_observed_checkpoint_id"]
                level_rows.append(_level_row(last_observed_levels[level_id], record, None, status, last_observed_checkpoint_id, record["checkpoint_id"], observation_present=False, last_observed_checkpoint_id=last_observed_checkpoint_id))
            for level in current_levels.values():
                level["_last_observed_checkpoint_id"] = record["checkpoint_id"]
            last_observed_levels.update(current_levels)
            prior_levels = current_levels
            prior_checkpoint_id = record["checkpoint_id"]
        changes = _snapshot_change_rows(snapshot_rows) + _change_rows(level_rows)
        for rows in (snapshot_rows, level_rows, changes):
            for row in rows:
                row["schema_version"] = SCHEMA_VERSION
                row["method_version"] = METHOD_VERSION
        source_digest = hashlib.sha256("".join(f"{item['run_id']}:{item['source_hash']}" for item in evaluations).encode()).hexdigest()
        history_id = "history_" + hashlib.sha256(f"{SCHEMA_VERSION}|{METHOD_VERSION}|{symbol}|{source_digest}".encode()).hexdigest()[:20]
        evaluation_history = [_evaluation_fields(item, canonical_by_checkpoint[item["checkpoint_id"]]["run_id"]) for item in evaluations]
        structural_checkpoints = []
        for row in snapshot_rows:
            canonical_record = canonical_by_checkpoint[row["checkpoint_id"]]
            latest_evaluation = latest_evaluation_by_checkpoint[row["checkpoint_id"]]
            structural_checkpoints.append({
                **row, "canonical_structural_run_id": canonical_record["run_id"],
                "latest_evaluation_run_id": latest_evaluation["run_id"],
                "latest_evaluated_at_utc": latest_evaluation["evaluated"].isoformat(),
                "latest_evaluation": _evaluation_fields(latest_evaluation, canonical_record["run_id"]),
                "levels": [level for level in level_rows if level["checkpoint_id"] == row["checkpoint_id"]],
            })
        history = {
            "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "history_id": history_id, "symbol": symbol,
            "source_run_count": len(evaluations), "evaluation_count": len(evaluations), "structural_checkpoint_count": len(canonical),
            "result_status": "insufficient_history" if len(canonical) == 1 else "ok",
            "first_as_of_utc": canonical[0]["as_of"].isoformat(), "latest_as_of_utc": canonical[-1]["as_of"].isoformat(),
            "latest_evaluated_at_utc": latest_evaluation_by_checkpoint[canonical[-1]["checkpoint_id"]]["evaluated"].isoformat(), "source_digest": source_digest,
            "evaluation_history": evaluation_history, "structural_checkpoints": structural_checkpoints,
            "level_history": level_rows, "structure_changes": changes,
            "safety_boundary": SAFETY,
        }
        files = {
            "macro_structure_history.json": _json_bytes(history), "macro_structure_history.md": _markdown(history).encode("utf-8"),
            "macro_snapshot_history.csv": _csv_bytes(snapshot_rows, SNAPSHOT_FIELDS), "macro_level_history.csv": _csv_bytes(level_rows, CSV_FIELDS),
            "macro_structure_changes.csv": _csv_bytes(changes, CHANGE_FIELDS),
        }
        canonical_latest_record = canonical[-1]["snapshot"]
        latest_evaluation = latest_evaluation_by_checkpoint[canonical[-1]["checkpoint_id"]]
        latest_snapshot = latest_evaluation["snapshot"]
        latest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "history_id": history_id, "artifact_dir": history_id, "symbol": symbol, "source_run_count": len(evaluations), "evaluation_count": len(evaluations), "structural_checkpoint_count": len(canonical), "first_as_of_utc": history["first_as_of_utc"], "latest_as_of_utc": history["latest_as_of_utc"], "history_result_status": history["result_status"], "latest_snapshot_result_status": latest_snapshot.get("result_status", ""), "canonical_structural_run_id": canonical[-1]["run_id"], "latest_evaluation_run_id": latest_evaluation["run_id"], "latest_evaluated_at_utc": latest_evaluation["evaluated"].isoformat(), "latest_structure_state": canonical_latest_record.get("structure_state", ""), "latest_price_location": canonical_latest_record.get("price_location", ""), "latest_stale_status": latest_snapshot.get("stale_status", ""), "latest_stale_timeframes": latest_snapshot.get("stale_timeframes", []), "latest_freshness": latest_snapshot.get("freshness", {}), "latest_continuity_status": latest_snapshot.get("continuity_status", ""), "latest_data_quality_status": latest_snapshot.get("data_quality_status", ""), "latest_snapshot_reason_codes": latest_snapshot.get("reason_codes", []), "latest_reliability_band_counts": canonical_latest_record.get("reliability_band_counts", {}), "source_digest": source_digest, "safety_boundary": SAFETY}
        manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "history_id": history_id, "symbol": symbol, "source_run_count": len(evaluations), "evaluation_count": len(evaluations), "structural_checkpoint_count": len(canonical), "source_digest": source_digest, "source_runs": [item["run_id"] for item in evaluations], "outputs": list(OUTPUT_NAMES), "source": "public_mops1_artifacts_only", "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
        files["run_manifest.json"] = _json_bytes(manifest)
        _publish(output_root, history_id, files, latest)
        return {"ok": True, "exit_code": 0, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "history_id": history_id, "artifact_dir": history_id, "symbol": symbol, "source_run_count": len(evaluations), "evaluation_count": len(evaluations), "structural_checkpoint_count": len(canonical), "history_result_status": history["result_status"], "latest_snapshot_result_status": latest_snapshot.get("result_status", ""), "canonical_structural_run_id": canonical[-1]["run_id"], "latest_evaluation_run_id": latest_evaluation["run_id"], "latest_evaluated_at_utc": latest_evaluation["evaluated"].isoformat(), "latest_as_of_utc": history["latest_as_of_utc"], "latest_structure_state": canonical_latest_record.get("structure_state", ""), "latest_stale_status": latest_snapshot.get("stale_status", ""), "latest_continuity_status": latest_snapshot.get("continuity_status", ""), "latest_data_quality_status": latest_snapshot.get("data_quality_status", ""), "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
    except (OSError, ValueError) as exc:
        return {"ok": False, "exit_code": 2, "error_code": str(exc), "report_written": False, "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False, "safety_boundary": SAFETY}
