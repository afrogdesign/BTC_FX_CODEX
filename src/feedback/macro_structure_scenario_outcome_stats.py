"""Opt-in, local-only outcome counts for immutable macro scenario artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from src.feedback.macro_structure_scenarios import (
    EVENT_TYPES,
    SCENARIO_STATUSES,
    SCENARIO_TYPES,
)

SCHEMA_VERSION = "macro_structure_scenario_outcome_stats.v1"
METHOD_VERSION = SCHEMA_VERSION
HORIZONS = (6, 12, 24)
CADENCE = timedelta(hours=4)
OUTCOMES = ("continuation", "rejection", "indeterminate", "immature")
SAFETY_BOUNDARY = "report-only / human decides manually / no automatic order"


class ScenarioOutcomeStatsError(ValueError):
    """Stable, non-sensitive evaluator or publication failure."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _utc(value: Any, code: str = "stats_timestamp_invalid") -> datetime:
    if not isinstance(value, str):
        raise ScenarioOutcomeStatsError(code)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ScenarioOutcomeStatsError(code) from exc
    if parsed.tzinfo is None:
        raise ScenarioOutcomeStatsError(code)
    return parsed.astimezone(timezone.utc)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _event_payload(event: dict[str, Any]) -> str:
    return _json({key: value for key, value in event.items() if key != "event_id"})


def _artifact_cutoff(raw: dict[str, Any]) -> datetime:
    for key in ("as_of_utc", "evaluated_at_utc", "cutoff_utc"):
        value = raw.get(key)
        if value:
            return _utc(value)
    model = raw.get("structural_event_model")
    if isinstance(model, dict) and model.get("cutoff_utc"):
        return _utc(model["cutoff_utc"])
    raise ScenarioOutcomeStatsError("stats_artifact_cutoff_missing")


def _validate_events(raw: dict[str, Any], cutoff: datetime) -> dict[str, dict[str, Any]]:
    model = raw.get("structural_event_model")
    if not isinstance(model, dict) or model.get("method_version") != "macro_structure_structural_events.v1":
        raise ScenarioOutcomeStatsError("stats_structural_event_model_invalid")
    events = model.get("events")
    if not isinstance(events, list):
        raise ScenarioOutcomeStatsError("stats_structural_events_invalid")
    by_id: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict) or not event.get("event_id") or event.get("event_type") not in EVENT_TYPES:
            raise ScenarioOutcomeStatsError("stats_structural_event_invalid")
        event_id = str(event["event_id"])
        timestamp = _utc(event.get("event_timestamp_utc"))
        if timestamp > cutoff:
            raise ScenarioOutcomeStatsError("stats_future_event_timestamp")
        if event_id in by_id and _event_payload(by_id[event_id]) != _event_payload(event):
            raise ScenarioOutcomeStatsError("stats_duplicate_event_conflict")
        by_id[event_id] = event
    return by_id


def _validate_scenarios(raw: dict[str, Any], cutoff: datetime, events: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    model = raw.get("scenario_model")
    if not isinstance(model, dict) or model.get("method_version") != "macro_structure_scenarios.v1":
        raise ScenarioOutcomeStatsError("stats_scenario_model_invalid")
    scenarios = model.get("scenarios")
    if model.get("status") not in {"ok", "insufficient"} or not isinstance(scenarios, list):
        raise ScenarioOutcomeStatsError("stats_scenario_model_invalid")
    result: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ScenarioOutcomeStatsError("stats_scenario_invalid")
        scenario_id = str(scenario.get("scenario_id", ""))
        if not scenario_id or scenario.get("scenario_type") not in SCENARIO_TYPES:
            raise ScenarioOutcomeStatsError("stats_scenario_invalid")
        if scenario.get("scenario_status") not in SCENARIO_STATUSES or scenario.get("direction") not in {"UP", "DOWN"}:
            raise ScenarioOutcomeStatsError("stats_scenario_invalid")
        cutoff_value = _utc(scenario.get("trigger_timestamp_utc"))
        if cutoff_value > cutoff:
            raise ScenarioOutcomeStatsError("stats_future_scenario_timestamp")
        support = scenario.get("supporting_event_ids")
        if not isinstance(support, list) or any(str(item) not in events for item in support):
            raise ScenarioOutcomeStatsError("stats_scenario_reference_missing")
        primary_kind = scenario.get("primary_object_kind")
        primary_id = str(scenario.get("primary_object_id", ""))
        if primary_kind not in {"horizontal_zone", "trendline", "pivot_structure"} or not primary_id:
            raise ScenarioOutcomeStatsError("stats_scenario_object_invalid")
        payload = _json(scenario)
        if scenario_id in seen and seen[scenario_id] != payload:
            raise ScenarioOutcomeStatsError("stats_duplicate_scenario_conflict")
        seen[scenario_id] = payload
        result.append(scenario)
    return result


def _read_artifact(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ScenarioOutcomeStatsError("stats_artifact_invalid") from exc
    if not isinstance(raw, dict):
        raise ScenarioOutcomeStatsError("stats_artifact_invalid")
    artifact_id = str(raw.get("operator_artifact_id") or raw.get("artifact_id") or "")
    if not artifact_id:
        raise ScenarioOutcomeStatsError("stats_artifact_id_missing")
    if not isinstance(raw.get("scenario_model"), dict) or raw["scenario_model"].get("method_version") != "macro_structure_scenarios.v1":
        raise ScenarioOutcomeStatsError("stats_scenario_model_invalid")
    cutoff = _artifact_cutoff(raw)
    events = _validate_events(raw, cutoff)
    scenarios = _validate_scenarios(raw, cutoff, events)
    return {"artifact_id": artifact_id, "cutoff": cutoff, "events": events, "scenarios": scenarios, "path_name": path.name, "raw": raw}


def _artifact_files(operator_root: Path, max_artifacts: int | None) -> list[Path]:
    if not operator_root.is_dir() or operator_root.is_symlink():
        raise ScenarioOutcomeStatsError("stats_operator_root_invalid")
    paths = sorted(operator_root.glob("operator_*/macro_structure_operator.json"))
    if max_artifacts is not None:
        if max_artifacts <= 0:
            raise ScenarioOutcomeStatsError("stats_max_artifacts_invalid")
        paths = paths[:max_artifacts]
    return paths


def _load_artifacts(operator_root: Path, max_artifacts: int | None) -> tuple[list[dict[str, Any]], int, list[str]]:
    valid: list[dict[str, Any]] = []
    excluded = 0
    reasons: list[str] = []
    for path in _artifact_files(operator_root, max_artifacts):
        try:
            valid.append(_read_artifact(path))
        except ScenarioOutcomeStatsError as exc:
            if exc.code == "stats_scenario_model_invalid":
                excluded += 1
                reasons.append(exc.code)
                continue
            raise
    if not valid:
        return [], excluded, sorted(set(reasons)) or ["stats_no_valid_artifacts"]
    valid.sort(key=lambda item: (item["cutoff"], item["artifact_id"], item["path_name"]))
    by_id: dict[str, str] = {}
    deduped: list[dict[str, Any]] = []
    for artifact in valid:
        payload = _json({"cutoff": artifact["cutoff"].isoformat(), "events": artifact["events"], "scenarios": artifact["scenarios"]})
        prior = by_id.get(artifact["artifact_id"])
        if prior is not None:
            if prior != payload:
                raise ScenarioOutcomeStatsError("stats_duplicate_artifact_conflict")
            excluded += 1
            continue
        by_id[artifact["artifact_id"]] = payload
        deduped.append(artifact)
    by_cutoff: dict[datetime, str] = {}
    for artifact in deduped:
        payload = by_id[artifact["artifact_id"]]
        prior = by_cutoff.get(artifact["cutoff"])
        if prior is not None and prior != payload:
            raise ScenarioOutcomeStatsError("stats_conflicting_same_cutoff")
        by_cutoff[artifact["cutoff"]] = payload
    return deduped, excluded, sorted(set(reasons))


def _sort_event(event: dict[str, Any]) -> tuple[datetime, str]:
    return (_utc(event["event_timestamp_utc"]), str(event["event_id"]))


def _matches(scenario: dict[str, Any], event: dict[str, Any]) -> bool:
    allowed = {(str(scenario["primary_object_kind"]), str(scenario["primary_object_id"]))}
    allowed.update((str(scenario["primary_object_kind"]), str(item)) for item in scenario.get("related_object_ids", []))
    return (str(event.get("object_kind")), str(event.get("object_id"))) in allowed or str(event.get("related_object_id", "")) in {item for _, item in allowed}


def _pivot_pair(events: list[dict[str, Any]], direction: str, *, before: datetime) -> tuple[dict[str, Any], dict[str, Any]] | None:
    if direction == "UP":
        types = {"higher_high", "higher_low"}
    else:
        types = {"lower_high", "lower_low"}
    candidates = [event for event in events if event.get("event_type") in types and _utc(event["event_timestamp_utc"]) <= before]
    first = next((event for event in candidates if event.get("event_type") in types), None)
    second = next((event for event in candidates if event.get("event_type") in types and event.get("event_type") != first.get("event_type")), None) if first else None
    return (first, second) if first and second else None


def _decisive_events(scenario: dict[str, Any], events: Iterable[dict[str, Any]], start: datetime, end: datetime) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    relevant = [event for event in events if start < _utc(event["event_timestamp_utc"]) <= end and _matches(scenario, event)]
    relevant.sort(key=_sort_event)
    direction = scenario["direction"]
    confirmations: list[dict[str, Any]] = []
    invalidations: list[dict[str, Any]] = []
    for event in relevant:
        event_type = event.get("event_type")
        if event_type in {"closed_candle_acceptance", "retest_hold", "clean_rejection"} and event.get("direction") == direction:
            confirmations.append(event)
        elif event_type in {"false_break_reclaim", "retest_failure"} or event_type in {"break", "closed_candle_acceptance"} and event.get("direction") != direction:
            invalidations.append(event)
    pivot_events = [event for event in relevant if event.get("object_kind") == "pivot_structure"]
    same_types = {"higher_high", "higher_low"} if direction == "UP" else {"lower_high", "lower_low"}
    opposite_types = {"lower_high", "lower_low"} if direction == "UP" else {"higher_high", "higher_low"}
    for event in pivot_events:
        if event.get("event_type") in same_types:
            confirmations.append(event)
    for event in pivot_events:
        if event.get("event_type") not in opposite_types:
            continue
        pair = _pivot_pair(pivot_events, "DOWN" if direction == "UP" else "UP", before=_utc(event["event_timestamp_utc"]))
        if pair:
            invalidations.append(max(pair, key=_sort_event))
    confirmations.sort(key=_sort_event)
    invalidations.sort(key=_sort_event)
    return confirmations, invalidations


def _outcome(scenario: dict[str, Any], artifact: dict[str, Any], start: datetime, horizon: int, selected: dict[str, Any] | None) -> dict[str, Any]:
    target = start + timedelta(hours=horizon)
    base = {
        "scenario_id": str(scenario["scenario_id"]), "scenario_type": str(scenario["scenario_type"]), "direction": str(scenario["direction"]),
        "horizon_hours": horizon, "cohort_start_utc": start.isoformat(), "target_utc": target.isoformat(),
        "selected_cutoff_utc": selected["cutoff"].isoformat() if selected else "", "outcome": "immature",
        "decisive_event_id": "", "decisive_event_type": "", "reason_code": "horizon_artifact_missing",
    }
    if selected is None:
        return base
    confirmations, invalidations = _decisive_events(scenario, selected["events"].values(), start, selected["cutoff"])
    if not confirmations and not invalidations:
        base.update(outcome="indeterminate", reason_code="no_decisive_event_by_horizon")
        return base
    first_confirmation = confirmations[0] if confirmations else None
    first_invalidation = invalidations[0] if invalidations else None
    if first_confirmation and first_invalidation:
        c_key, i_key = _sort_event(first_confirmation), _sort_event(first_invalidation)
        if c_key[0] == i_key[0]:
            decisive = first_invalidation
            base.update(outcome="rejection", reason_code="invalidation_before_or_same_timestamp")
        elif c_key < i_key:
            decisive = first_confirmation
            base.update(outcome="continuation", reason_code="confirmation_before_invalidation")
        else:
            decisive = first_invalidation
            base.update(outcome="rejection", reason_code="invalidation_before_or_same_timestamp")
    elif first_confirmation:
        decisive = first_confirmation
        base.update(outcome="continuation", reason_code="confirmation_before_horizon")
    else:
        decisive = first_invalidation
        base.update(outcome="rejection", reason_code="invalidation_before_horizon")
    base.update(decisive_event_id=str(decisive["event_id"]), decisive_event_type=str(decisive["event_type"]))
    return base


def evaluate_scenario_outcome_stats(operator_root: Path, *, max_artifacts: int | None = None) -> dict[str, Any]:
    artifacts, excluded, exclusion_reasons = _load_artifacts(Path(operator_root), max_artifacts)
    cohorts: dict[str, tuple[dict[str, Any], datetime]] = {}
    scenarios_by_id: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        for scenario in artifact["scenarios"]:
            scenario_id = str(scenario["scenario_id"])
            if scenario_id not in cohorts:
                cohorts[scenario_id] = (artifact, artifact["cutoff"])
                scenarios_by_id[scenario_id] = scenario
    rows: list[dict[str, Any]] = []
    for scenario_id in sorted(cohorts):
        cohort_artifact, start = cohorts[scenario_id]
        scenario = scenarios_by_id[scenario_id]
        for horizon in HORIZONS:
            target = start + timedelta(hours=horizon)
            eligible = [item for item in artifacts if item["cutoff"] >= target and item["cutoff"] <= target + CADENCE]
            selected = min(eligible, key=lambda item: (item["cutoff"], item["artifact_id"])) if eligible else None
            rows.append(_outcome(scenario, cohort_artifact, start, horizon, selected))
    rows.sort(key=lambda row: (row["scenario_id"], row["horizon_hours"]))
    mature = [row for row in rows if row["outcome"] != "immature"]
    horizons: dict[str, dict[str, int]] = {}
    for horizon in HORIZONS:
        horizons[str(horizon)] = {outcome: sum(row["outcome"] == outcome for row in rows if row["horizon_hours"] == horizon) for outcome in OUTCOMES}
    grouped: dict[str, dict[str, dict[str, int]]] = {}
    for row in rows:
        grouped.setdefault(row["scenario_type"], {}).setdefault(row["direction"], {outcome: 0 for outcome in OUTCOMES})[row["outcome"]] += 1
    source_ids = [item["artifact_id"] for item in artifacts]
    first_cutoff = artifacts[0]["cutoff"].isoformat() if artifacts else ""
    latest_cutoff = artifacts[-1]["cutoff"].isoformat() if artifacts else ""
    generated_at = latest_cutoff
    summary = {
        "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION,
        "generated_at_utc": generated_at,
        "source_artifact_count": len(artifacts), "excluded_artifact_count": excluded,
        "first_cutoff_utc": first_cutoff, "latest_cutoff_utc": latest_cutoff,
        "total_unique_scenario_count": len(cohorts), "horizons": horizons, "grouped_counts": grouped,
        "mature_row_count": len(mature), "evidence_strength": "descriptive_only" if len(mature) >= 20 else "insufficient",
        "reason_codes": sorted(set(exclusion_reasons)), "safety_boundary": SAFETY_BOUNDARY,
        "source_artifact_ids": source_ids,
    }
    identity_payload = {"schema_version": SCHEMA_VERSION, "sources": source_ids, "summary": summary, "rows": rows}
    artifact_id = hashlib.sha256(_json(identity_payload).encode("utf-8")).hexdigest()[:20]
    summary["artifact_id"] = artifact_id
    return {**summary, "summary": summary, "rows": rows, "artifacts": artifacts}


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["scenario_id", "scenario_type", "direction", "horizon_hours", "cohort_start_utc", "target_utc", "selected_cutoff_utc", "outcome", "decisive_event_id", "decisive_event_type", "reason_code"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)
        handle.flush()
        os.fsync(handle.fileno())


def _write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = ["# Macro structure scenario outcome counts", "", f"- artifact_id: `{summary['artifact_id']}`", f"- source artifacts: `{summary['source_artifact_count']}`", f"- excluded artifacts: `{summary['excluded_artifact_count']}`", f"- mature rows: `{summary['mature_row_count']}`", f"- evidence strength: `{summary['evidence_strength']}`", "", "## Outcome counts", ""]
    for horizon, counts in summary["horizons"].items():
        lines.append(f"- {horizon}H: " + ", ".join(f"{key}={counts[key]}" for key in OUTCOMES))
    lines += ["", f"Safety boundary: {SAFETY_BOUNDARY}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def publish_scenario_outcome_stats(operator_root: Path, output_root: Path, *, max_artifacts: int | None = None) -> dict[str, Any]:
    result = evaluate_scenario_outcome_stats(operator_root, max_artifacts=max_artifacts)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_id = result["artifact_id"]
    temp_dir = Path(tempfile.mkdtemp(prefix=".scenario-stats-", dir=output_root))
    final_dir = output_root / artifact_id
    latest_tmp = output_root / f".latest-{artifact_id}.tmp"
    try:
        (temp_dir / "macro_structure_scenario_outcome_stats.json").write_text(json.dumps(result["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        _write_csv(temp_dir / "macro_structure_scenario_outcome_rows.csv", result["rows"])
        _write_markdown(temp_dir / "macro_structure_scenario_outcome_stats.md", result["summary"])
        manifest = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "artifact_id": artifact_id, "source_artifact_ids": result["summary"]["source_artifact_ids"], "files": ["macro_structure_scenario_outcome_stats.json", "macro_structure_scenario_outcome_rows.csv", "macro_structure_scenario_outcome_stats.md", "run_manifest.json"]}
        (temp_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        if final_dir.exists():
            if not final_dir.is_dir() or any(not (final_dir / name).is_file() for name in ("macro_structure_scenario_outcome_stats.json", "macro_structure_scenario_outcome_rows.csv", "macro_structure_scenario_outcome_stats.md", "run_manifest.json")):
                raise ScenarioOutcomeStatsError("stats_artifact_id_collision")
            try:
                existing = json.loads((final_dir / "macro_structure_scenario_outcome_stats.json").read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise ScenarioOutcomeStatsError("stats_artifact_id_collision") from exc
            if existing != result["summary"]:
                raise ScenarioOutcomeStatsError("stats_artifact_id_collision")
        else:
            os.replace(temp_dir, final_dir)
        latest_tmp.write_text(json.dumps(result["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        os.replace(latest_tmp, output_root / "latest.json")
    except ScenarioOutcomeStatsError:
        raise
    except OSError as exc:
        raise ScenarioOutcomeStatsError("stats_publication_failed") from exc
    finally:
        if latest_tmp.exists():
            latest_tmp.unlink()
        if temp_dir.exists():
            for child in temp_dir.iterdir():
                child.unlink()
            temp_dir.rmdir()
    return result["summary"]
