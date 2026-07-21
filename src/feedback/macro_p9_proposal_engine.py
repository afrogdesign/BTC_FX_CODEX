"""Deterministic offline M5 champion/challenger proposal engine."""
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

from src.feedback.macro_next_regime_replay import replay_macro_next_regime
from src.feedback.macro_structure_volatility_replay import replay_macro_structure_volatility

SCHEMA_VERSION = "macro_p9_proposal_engine.v1"
METHOD_VERSION = "macro_p9_proposal_engine.v1"
CHAMPION_SCHEMA = "macro_p9_champion_manifest.v1"
SPACE_SCHEMA = "macro_p9_proposal_space.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
LEVERS = ("left_window", "right_window")
HORIZONS = ("3h", "6h", "12h", "24h")
RECOMMENDATIONS = frozenset({"reject", "continue_shadow_collection", "eligible_for_human_reviewed_proposal"})
M1_SCHEMA = "macro_structure_volatility_replay.v1"
M3_SCHEMA = "macro_next_regime_replay.v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError("input_file_missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("input_schema_invalid") from exc
    if not isinstance(value, dict):
        raise ValueError("input_schema_invalid")
    return value


def _read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError("input_file_missing")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("input_schema_invalid")
        return [dict(row) for row in reader]


def _unique(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        value = str(row.get(key, "")).strip()
        if not value or value in result:
            raise ValueError("duplicate_or_missing_identifier")
        result[value] = row
    return result


def _fingerprints(paths: dict[str, Path]) -> dict[str, str]:
    return {key: _sha(path) for key, path in sorted(paths.items())}


def _require_version(value: dict[str, Any], schema: str, method: str) -> None:
    if value.get("schema_version") != schema or value.get("method_version") != method:
        raise ValueError("incompatible_schema_or_method")


def _validate_champion_manifest(manifest: dict[str, Any]) -> None:
    _require_version(manifest, CHAMPION_SCHEMA, METHOD_VERSION)
    required = {"champion_id", "parameters", "input_fingerprints", "accepted_artifact_fingerprints"}
    if not required.issubset(manifest):
        raise ValueError("champion_manifest_invalid")
    parameters = manifest["parameters"]
    if not isinstance(parameters, dict) or set(parameters) != {"left_window", "right_window", "cutoff_utc", "performance_start_utc", "performance_end_utc"}:
        raise ValueError("champion_manifest_parameters_invalid")
    _validate_parameters(parameters, fixed=True)
    if not isinstance(manifest["input_fingerprints"], dict) or not isinstance(manifest["accepted_artifact_fingerprints"], dict):
        raise ValueError("champion_manifest_fingerprints_invalid")


def _validate_parameters(parameters: dict[str, Any], fixed: bool = False) -> tuple[int, int]:
    expected = set(LEVERS) | ({"cutoff_utc", "performance_start_utc", "performance_end_utc"} if fixed else set())
    if set(parameters) != expected:
        raise ValueError("parameter_set_invalid")
    values: list[int] = []
    for key in LEVERS:
        value = parameters[key]
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError("parameter_value_invalid")
        values.append(value)
    return values[0], values[1]


def _expand_space(space: dict[str, Any], champion: dict[str, Any]) -> list[dict[str, int]]:
    _require_version(space, SPACE_SCHEMA, METHOD_VERSION)
    if set(space) != {"schema_version", "method_version", "one_at_a_time", "combinations"}:
        raise ValueError("proposal_space_invalid")
    generated: list[dict[str, int]] = []
    for entry in space["one_at_a_time"]:
        if not isinstance(entry, dict) or set(entry) != {"parameter", "values"} or entry["parameter"] not in LEVERS:
            raise ValueError("proposal_parameter_invalid")
        values = entry["values"]
        if not isinstance(values, list):
            raise ValueError("proposal_values_invalid")
        for value in values:
            candidate = dict({key: champion["parameters"][key] for key in LEVERS})
            candidate[entry["parameter"]] = value
            _validate_parameters(candidate)
            generated.append(candidate)
    for entry in space["combinations"]:
        if not isinstance(entry, dict) or set(entry) != {"parameters"} or not isinstance(entry["parameters"], dict):
            raise ValueError("proposal_combination_invalid")
        if not entry["parameters"] or not set(entry["parameters"]).issubset(LEVERS):
            raise ValueError("proposal_combination_invalid")
        candidate = dict({key: champion["parameters"][key] for key in LEVERS})
        candidate.update(entry["parameters"])
        _validate_parameters(candidate)
        generated.append(candidate)
    champion_pair = tuple(champion["parameters"][key] for key in LEVERS)
    unique: dict[tuple[int, int], dict[str, int]] = {}
    for candidate in generated:
        pair = tuple(candidate[key] for key in LEVERS)
        if pair == champion_pair:
            raise ValueError("champion_equivalent_candidate")
        if pair in unique:
            raise ValueError("duplicate_candidate")
        unique[pair] = candidate
    if len(unique) > 64:
        raise ValueError("challenger_limit_exceeded")
    return [unique[key] for key in sorted(unique)]


def candidate_id(parameters: dict[str, int]) -> str:
    return "m5_" + hashlib.sha256(_canonical(dict(sorted(parameters.items()))).encode()).hexdigest()[:16]


def _ids(path: Path, keys: tuple[str, ...]) -> tuple[set[str], ...]:
    rows = _read_csv(path, set(keys))
    return tuple(set(_unique(rows, key)) for key in keys)


def _artifact_signature(paths: dict[str, Path]) -> dict[str, Any]:
    signatures: dict[str, Any] = {}
    for name, path in sorted(paths.items()):
        if path.suffix == ".json":
            signatures[name] = {"sha256": _sha(path), "ids": {}}
        else:
            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            keys = [key for key in ("event_id", "signal_id", "record_id", "episode_id", "level_id", "opportunity_id") if rows and key in rows[0]]
            signatures[name] = {"sha256": _sha(path), "ids": {key: sorted({str(row.get(key, "")) for row in rows if row.get(key, "")}) for key in keys}}
    return signatures


def _jst_dates(path: Path) -> list[str]:
    import datetime as _datetime
    rows = _read_csv(path, {"event_timestamp_jst"})
    return sorted({str(row["event_timestamp_jst"])[:10] for row in rows})


M1_GUARDED = ("directional_precision", "large_move_recall", "false_warning_rate", "opposite_move_rate", "whipsaw_rate", "burden_per_jst_day")
M3_GUARDED = ("directional_precision", "opposite_move_rate", "balanced_no_expansion_rate", "whipsaw_rate", "burden_per_jst_day")
M1_SPLIT_DIMENSIONS = ("direction", "regime", "price_location", "volatility_state", "reliability")
M3_SPLIT_DIMENSIONS = ("side", "structural_state", "price_location", "volatility_state", "level_reliability_band")
METRIC_DIRECTIONS = {
    **{key: "higher" for key in ("directional_precision", "large_move_recall")},
    **{key: "lower" for key in ("false_warning_rate", "opposite_move_rate", "whipsaw_rate", "burden_per_jst_day", "balanced_no_expansion_rate")},
}


def _required_dict(value: Any, reason: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(reason)
    return value


def _m1_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    gate = _required_dict(summary.get("recommendation_gate"), "m1_validation_policy_missing")
    policies = _required_dict(gate.get("validation_policy_metrics"), "m1_validation_policy_missing")
    source = _required_dict(policies.get("reliable_level_acceptance_corridor"), "m1_validation_policy_missing")
    if any(key not in source for key in M1_GUARDED):
        raise ValueError("m1_validation_metric_missing")
    return {key: source[key] for key in M1_GUARDED}


def _m3_metrics(summary: dict[str, Any], horizon: str = "3h") -> dict[str, Any]:
    recommendation = _required_dict(summary.get("recommendation"), "m3_validation_metrics_missing")
    validation = _required_dict(recommendation.get("validation_candidate_metrics"), "m3_validation_metrics_missing")
    source = _required_dict(validation.get(horizon), "m3_validation_metrics_missing")
    keys = M3_GUARDED + ("resolved_up_count", "resolved_down_count")
    if any(key not in source for key in keys):
        raise ValueError("m3_validation_metric_missing")
    return {key: source[key] for key in keys}


def _m3_diagnostics(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {horizon: _m3_metrics(summary, horizon) for horizon in ("6h", "12h", "24h")}


def _data_quality_ok(summary: dict[str, Any]) -> bool:
    rec = summary.get("recommendation", {})
    coverage = summary.get("coverage", {})
    if coverage.get("continuity_pass") is False:
        return False
    if rec.get("validation_data_quality_pass") is False:
        return False
    return not any("unresolved" in str(x) for x in rec.get("reason_codes", []))


def _m1_quality_ok(path: Path) -> bool:
    summary = _read_json(path)
    coverage = summary.get("coverage")
    gate = summary.get("recommendation_gate")
    if not isinstance(coverage, dict) or coverage.get("continuity_pass") is not True or not isinstance(gate, dict):
        return False
    try:
        _m1_metrics(summary)
    except ValueError:
        return False
    reasons = gate.get("reasons", [])
    return not any(token in str(reason).lower() for reason in reasons for token in ("continuity", "data_quality", "unresolved"))


def _m3_quality_ok(path: Path) -> bool:
    summary = _read_json(path)
    recommendation = summary.get("recommendation")
    coverage = summary.get("data_quality") or summary.get("coverage")
    if not isinstance(recommendation, dict) or recommendation.get("validation_data_quality_pass") is not True:
        return False
    if isinstance(coverage, dict) and coverage.get("continuity_pass") is False:
        return False
    return not any("unresolved" in str(reason).lower() for reason in recommendation.get("reason_codes", []))


def _row_count(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def _utc(value: str) -> datetime:
    text = str(value or "").strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _date_concentration(episodes: list[dict[str, str]], validation_dates: list[str]) -> dict[str, Any]:
    counts = Counter()
    allowed = set(validation_dates)
    for row in episodes:
        stamp = row.get("start_timestamp_utc") or row.get("event_timestamp_utc") or ""
        if not stamp:
            continue
        date = _utc(stamp).astimezone(timezone(timedelta(hours=9))).date().isoformat()
        if date in allowed:
            counts[date] += 1
    total = sum(counts.values())
    if not total:
        return {"status": "not_established", "validation_dates": sorted(allowed), "max_jst_date": None, "max_date_episode_count": 0, "validation_candidate_episode_count": 0, "ratio": None, "pass": False}
    date, numerator = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    ratio = numerator / total
    return {"status": "established", "validation_dates": sorted(allowed), "max_jst_date": date, "max_date_episode_count": numerator, "validation_candidate_episode_count": total, "ratio": ratio, "pass": ratio <= 0.5}


def _performance_snapshot_dates(signal_path: Path) -> list[tuple[str, str]]:
    rows = _read_csv(signal_path, {"timestamp_utc", "macro_context_only"})
    selected: dict[str, tuple[str, datetime]] = {}
    for row in rows:
        if str(row.get("macro_context_only", "")).strip().lower() == "true":
            continue
        stamp = _utc(row["timestamp_utc"])
        timestamp_jst = str(row.get("timestamp_jst") or "").strip()
        date = (timestamp_jst[:10] if timestamp_jst else _utc(row["timestamp_utc"]).astimezone(timezone(timedelta(hours=9))).date().isoformat())
        if date not in selected or stamp > selected[date][1]:
            selected[date] = (stamp.isoformat().replace("+00:00", "Z"), stamp)
    return [(date, selected[date][0]) for date in sorted(selected)]


def _write_snapshot_inputs(paths: dict[str, Path], cutoff: str, root: Path) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    cutoff_dt = _utc(cutoff)
    result: dict[str, Path] = {}
    with paths["signals"].open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader if _utc(row["timestamp_utc"]) <= cutoff_dt]
    signal_out = root / "signals.csv"
    with signal_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    result["signals"] = signal_out
    for name, seconds in (("ohlcv_15m", 15 * 60), ("ohlcv_1h", 60 * 60), ("ohlcv_4h", 4 * 60 * 60)):
        source = paths[name]
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            kept = []
            for row in reader:
                opened = _utc(row["timestamp_utc"])
                if opened.timestamp() + seconds <= cutoff_dt.timestamp():
                    kept.append(dict(row))
        output = root / f"{name}.csv"
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader(); writer.writerows(kept)
        result[name] = output
    return result


def _id_fingerprint(path: Path, key: str) -> str:
    rows = _read_csv(path, {key})
    values = sorted(str(row[key]) for row in rows)
    return hashlib.sha256(_canonical(values).encode()).hexdigest()


def _snapshot_record(date: str, cutoff: str, paths: dict[str, Path], run: dict[str, Any], m1: dict[str, Any], m3: dict[str, Any], validation_dates: list[str], reasons: list[str], status: str, comparison: bool, pareto: bool, improved: int) -> dict[str, Any]:
    m1_events = run["m1"] / "events.csv"; m1_misses = run["m1"] / "misses.csv"; m3_events = run["m3"] / "events.csv"; m3_episodes = run["m3"] / "episodes.csv"
    candidate_episodes = [row for row in _read_csv(m3_episodes, {"episode_id", "policy", "start_timestamp_utc"}) if row.get("policy") == "candidate"]
    concentration = _date_concentration(candidate_episodes, validation_dates)
    m3_summary = _read_json(run["m3"] / "replay.json")
    m1_quality = _m1_quality_ok(run["m1"] / "replay.json")
    m3_quality = _m3_quality_ok(run["m3"] / "replay.json")
    lineage = [{key: row.get(key, "") for key in ("opportunity_id", "root_cause", "reason_codes")} for row in _read_csv(m1_misses, {"opportunity_id"})]
    return {"snapshot_jst_date": date, "cutoff_utc": cutoff, "input_row_counts": {key: _row_count(path) for key, path in paths.items()}, "input_fingerprints": _fingerprints(paths), "m1_event_count": len(_read_csv(m1_events, {"event_id"})), "m1_independent_opportunity_count": len(_read_csv(m1_misses, {"opportunity_id"})), "m1_opportunity_id_fingerprint": _id_fingerprint(m1_misses, "opportunity_id"), "m3_event_count": len(_read_csv(m3_events, {"record_id"})), "m3_candidate_episode_count": len(candidate_episodes), "m3_eligible_jst_dates": _jst_dates(m3_events), "m3_validation_jst_dates": validation_dates, "m1_guarded_metrics": m1, "m3_guarded_metrics": m3, "m3_diagnostic_horizons": _m3_diagnostics(m3_summary), "m3_resolved_up_count": m3.get("resolved_up_count"), "m3_resolved_down_count": m3.get("resolved_down_count"), "validation_date_concentration": concentration, "m1_quality_status": "pass" if m1_quality else "fail", "m3_quality_status": "pass" if m3_quality else "fail", "_issue_lineage": lineage, "status": status, "comparison_eligible": comparison, "pareto_dominant_vs_champion": pareto, "improved_guarded_metric_count": improved, "reason_codes": sorted(set(reasons))}


def _snapshot_eligible(snapshot: dict[str, Any], date: str | None = None) -> bool:
    if snapshot.get("status") != "established" or snapshot.get("m1_quality_status") != "pass" or snapshot.get("m3_quality_status") != "pass":
        return False
    if date is not None and snapshot.get("snapshot_jst_date") != date:
        return False
    if date is not None and date not in snapshot.get("m3_eligible_jst_dates", []):
        return False
    if not snapshot.get("m3_validation_jst_dates") or not snapshot.get("validation_date_concentration", {}).get("pass", False):
        return False
    if snapshot.get("m3_resolved_up_count", 0) < 10 or snapshot.get("m3_resolved_down_count", 0) < 10:
        return False
    if any(not isinstance(value, (int, float)) for value in _guarded_vector(snapshot.get("m1_guarded_metrics", {}), snapshot.get("m3_guarded_metrics", {})).values()):
        return False
    return True


def _public_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    lineage = snapshot.get("_issue_lineage", [])
    public = {key: value for key, value in snapshot.items() if not key.startswith("_")}
    public["issue_lineage_count"] = len(lineage)
    public["issue_lineage_fingerprint"] = hashlib.sha256(_canonical(lineage).encode()).hexdigest()
    return public


def _candidate_rolling_evidence(rolling: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any], dict[str, Any], dict[str, Any]]:
    latest = sorted(rolling, key=lambda row: row.get("snapshot_jst_date", ""))[-1] if rolling else None
    if not latest or not _snapshot_eligible(latest, latest.get("snapshot_jst_date")):
        return latest, {}, {}, {}
    return latest, latest["m1_guarded_metrics"], latest["m3_guarded_metrics"], latest.get("m3_diagnostic_horizons", {})


def _split_gate(splits: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not splits:
        return False, ["split_required_metric_missing"]
    def visit(value: Any) -> None:
        if not isinstance(value, dict):
            return
        if "status" in value:
            if value.get("status") != "available" or value.get("missing_metrics"):
                reasons.append("split_required_metric_missing")
            if value.get("degradation"):
                reasons.append("split_guarded_metric_degradation")
            return
        for child in value.values():
            visit(child)
    visit(splits)
    return not reasons, sorted(set(reasons))


def _rolling_snapshots(paths: dict[str, Path], parameters: dict[str, int], fixed: dict[str, Any], champion_pair: dict[str, int], temp_root: Path, champion_cache: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    snapshots: list[dict[str, Any]] = []; champion_snapshots: list[dict[str, Any]] = []
    for index, (date, cutoff) in enumerate(_performance_snapshot_dates(paths["signals"])):
        input_root = temp_root / f"snapshot-{index:03d}"
        snapshot_paths = _write_snapshot_inputs(paths, cutoff, input_root)
        try:
            if champion_cache is None:
                champion_run = _run_candidate(champion_pair, snapshot_paths, {**fixed, "cutoff_utc": cutoff, "performance_end_utc": cutoff}, input_root / "champion")
                champion_m1_summary = _read_json(champion_run["m1"] / "replay.json"); champion_m3_summary = _read_json(champion_run["m3"] / "replay.json")
                champion_m1 = _m1_metrics(champion_m1_summary); champion_m3 = _m3_metrics(champion_m3_summary)
                champion_validation_dates = list(champion_m3_summary.get("recommendation", {}).get("validation_dates", []))
                champion_snapshot = _snapshot_record(date, cutoff, snapshot_paths, champion_run, champion_m1, champion_m3, champion_validation_dates, [], "established", False, False, 0)
                champion_snapshot["comparison_eligible"] = _snapshot_eligible(champion_snapshot, date)
                champion_snapshot["_m1_split_summary"] = champion_m1_summary
                champion_snapshot["_m3_split_summary"] = champion_m3_summary
                if not champion_snapshot["comparison_eligible"]:
                    champion_snapshot["reason_codes"] = sorted(set(champion_snapshot.get("reason_codes", []) + ["champion_snapshot_not_eligible"]))
                champion_snapshots.append(champion_snapshot)
            else:
                if index >= len(champion_cache) or champion_cache[index].get("snapshot_jst_date") != date:
                    raise ValueError("champion_cache_mismatch")
                champion_snapshot = champion_cache[index]
                champion_m1 = champion_snapshot["m1_guarded_metrics"]; champion_m3 = champion_snapshot["m3_guarded_metrics"]; champion_validation_dates = champion_snapshot["m3_validation_jst_dates"]
            if champion_cache is None:
                champion_snapshot = champion_snapshots[-1]
            for candidate in (parameters,):
                if candidate == champion_pair:
                    continue
                run = _run_candidate(candidate, snapshot_paths, {**fixed, "cutoff_utc": cutoff, "performance_end_utc": cutoff}, input_root / candidate_id(candidate))
                m1_summary = _read_json(run["m1"] / "replay.json"); m3_summary = _read_json(run["m3"] / "replay.json")
                try:
                    m1 = _m1_metrics(m1_summary); m3 = _m3_metrics(m3_summary)
                    validation_dates = list(m3_summary.get("recommendation", {}).get("validation_dates", []))
                    reasons: list[str] = []
                    if _jst_dates(run["m3"] / "events.csv") != champion_snapshot.get("m3_eligible_jst_dates", []): reasons.append("eligible_date_basis_mismatch")
                    if validation_dates != champion_validation_dates: reasons.append("validation_date_basis_mismatch")
                    if _id_fingerprint(run["m1"] / "misses.csv", "opportunity_id") != champion_snapshot.get("m1_opportunity_id_fingerprint"): reasons.append("independent_opportunity_set_mismatch")
                    numeric = all(isinstance(value, (int, float)) and value is not None for value in _guarded_vector(m1, m3).values())
                    concentration = _date_concentration([row for row in _read_csv(run["m3"] / "episodes.csv", {"episode_id", "policy", "start_timestamp_utc"}) if row.get("policy") == "candidate"], validation_dates)
                    quality = _m1_quality_ok(run["m1"] / "replay.json") and _m3_quality_ok(run["m3"] / "replay.json")
                    if not _snapshot_eligible(champion_snapshot, date):
                        reasons.append("champion_snapshot_not_eligible")
                    m1_splits = _split_comparison(champion_snapshot.get("_m1_split_summary", {}), m1_summary, "reliable_level_acceptance_corridor", M1_SPLIT_DIMENSIONS, M1_GUARDED)
                    m3_splits = _split_comparison(champion_snapshot.get("_m3_split_summary", {}), m3_summary, "candidate", M3_SPLIT_DIMENSIONS, M3_GUARDED)
                    split_ok, split_reasons = _split_gate({"m1": m1_splits, "m3": m3_splits})
                    reasons.extend(split_reasons)
                    comparison = _snapshot_eligible(champion_snapshot, date) and not reasons and split_ok and numeric and quality and m3.get("resolved_up_count", 0) >= 10 and m3.get("resolved_down_count", 0) >= 10 and concentration.get("pass", False)
                    pareto, improved = _dominates(_guarded_vector(m1, m3), _guarded_vector(champion_m1, champion_m3))
                    if not comparison: pareto = False
                    status = "established" if numeric else "not_established"
                    snapshot = _snapshot_record(date, cutoff, snapshot_paths, run, m1, m3, validation_dates, reasons, status, comparison, pareto, improved)
                    snapshot["_champion_m1_metrics"] = champion_m1
                    snapshot["_champion_m3_metrics"] = champion_m3
                    snapshot["_champion_baseline_eligible"] = _snapshot_eligible(champion_snapshot, date)
                    snapshot["m1_split_comparison"] = m1_splits
                    snapshot["m3_split_comparison"] = m3_splits
                    snapshots.append(snapshot)
                except ValueError as exc:
                    snapshots.append({"snapshot_jst_date": date, "cutoff_utc": cutoff, "status": "failed", "comparison_eligible": False, "pareto_dominant_vs_champion": False, "reason_codes": [str(exc)]})
        except (ValueError, OSError) as exc:
            target = champion_snapshots if champion_cache is None else snapshots
            target.append({"snapshot_jst_date": date, "cutoff_utc": cutoff, "status": "failed", "comparison_eligible": False, "pareto_dominant_vs_champion": False, "reason_codes": [str(exc)]})
    return champion_snapshots, snapshots


def _metric_value(value: Any) -> Any:
    if isinstance(value, dict) and "3h" in value:
        return value["3h"]
    return value


def _split_comparison(champion_summary: dict[str, Any], candidate_summary: dict[str, Any], policy: str, dimensions: tuple[str, ...], guarded_metrics: tuple[str, ...] | None = None) -> dict[str, Any]:
    guarded_metrics = guarded_metrics or M1_GUARDED + M3_GUARDED
    def root(summary: dict[str, Any]) -> dict[str, Any]:
        value = summary.get("splits", {})
        if policy and isinstance(value, dict) and policy in value:
            return value[policy]
        return value
    champion_root = root(champion_summary)
    candidate_root = root(candidate_summary)
    result: dict[str, Any] = {}
    for dimension in dimensions:
        left = champion_root.get(dimension, {}) if isinstance(champion_root, dict) else {}
        right = candidate_root.get(dimension, {}) if isinstance(candidate_root, dict) else {}
        if not isinstance(left, dict) or not isinstance(right, dict) or not left or not right:
            result[dimension] = {"__missing_dimension__": {"champion": left, "challenger": right, "degradation": False, "missing_metrics": ["dimension"], "status": "unavailable"}}
            continue
        if policy and isinstance(left, dict):
            left = {key: (value.get(policy) if isinstance(value, dict) and policy in value else value) for key, value in left.items()}
        if policy and isinstance(right, dict):
            right = {key: (value.get(policy) if isinstance(value, dict) and policy in value else value) for key, value in right.items()}
        values = sorted(set(left) | set(right)) if isinstance(left, dict) and isinstance(right, dict) else []
        result[dimension] = {}
        for value in values:
            champion_value = _metric_value(left.get(value)) if isinstance(left, dict) else None
            candidate_value = _metric_value(right.get(value)) if isinstance(right, dict) else None
            degradation = False
            missing_metrics: list[str] = []
            if isinstance(champion_value, dict) and isinstance(candidate_value, dict):
                for key in guarded_metrics:
                    if key not in champion_value or key not in candidate_value or not isinstance(champion_value[key], (int, float)) or not isinstance(candidate_value[key], (int, float)):
                        missing_metrics.append(key)
                    elif METRIC_DIRECTIONS[key] == "higher" and candidate_value[key] < champion_value[key]:
                        degradation = True
                    elif METRIC_DIRECTIONS[key] == "lower" and candidate_value[key] > champion_value[key]:
                        degradation = True
            else:
                missing_metrics = list(guarded_metrics)
            result[dimension][value] = {"champion": champion_value, "challenger": candidate_value, "degradation": degradation, "missing_metrics": missing_metrics, "status": "available" if not missing_metrics else "unavailable"}
    return result


def _issue_rows(candidate_id_value: str, m1_misses: list[dict[str, str]], m1_split: dict[str, Any], candidate_m1: dict[str, Any], champion_m1: dict[str, Any], candidate_m3: dict[str, Any], champion_m3: dict[str, Any], concentration: dict[str, Any], p8: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    def add(category: str, source: str, count: int, affected: str, champion: Any = None, challenger: Any = None, reason: str = "evidence_observed") -> None:
        if count:
            rows.append({"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "candidate_id": candidate_id_value, "issue_category": category, "status": "observed", "evidence_source": source, "evidence_count": count, "affected_metric_split": affected, "champion_value": champion, "candidate_value": challenger, "reason_codes": reason, "actual_backed_count": p8["actual_high_medium_count"], "proposal_eligibility_effect": "diagnostic_only"})
    tokens = " ".join((row.get("root_cause", "") + " " + row.get("reason_codes", "")).lower() for row in m1_misses)
    add("reliable level missed", "m1_missed_move_diagnostics", tokens.count("reliable"), "m1.reliable_level_acceptance_corridor")
    add("rejection/break/acceptance/reclaim event missed", "m1_missed_move_diagnostics", sum(tokens.count(token) for token in ("rejection", "break", "acceptance", "reclaim")), "m1.event_family")
    reliability = sum(1 for value in m1_split.get("reliability", {}).values() if value.get("degradation"))
    add("level reliability unstable", "m1_split_comparison", reliability, "m1.reliability")
    if isinstance(candidate_m1.get("false_warning_rate"), (int, float)) and isinstance(champion_m1.get("false_warning_rate"), (int, float)) and candidate_m1["false_warning_rate"] > champion_m1["false_warning_rate"]:
        add("excessive false warning", "m1_validation_metrics", 1, "m1.false_warning_rate", champion_m1["false_warning_rate"], candidate_m1["false_warning_rate"], "false_warning_degradation")
    if isinstance(candidate_m3.get("opposite_move_rate"), (int, float)) and isinstance(champion_m3.get("opposite_move_rate"), (int, float)) and candidate_m3["opposite_move_rate"] > champion_m3["opposite_move_rate"]:
        add("wrong next-regime side", "m3_validation_metrics", 1, "m3.opposite_move_rate", champion_m3["opposite_move_rate"], candidate_m3["opposite_move_rate"], "opposite_move_degradation")
    if concentration.get("pass") is False:
        add("one-sided or date-concentrated evidence", "m3_validation_candidate_episodes", 1, "validation_date_concentration", None, concentration.get("ratio"), "date_concentration_over_0_50")
    return rows


def _guarded_vector(m1: dict[str, Any], m3: dict[str, Any]) -> dict[str, float | None]:
    return {**{f"m1.{key}": m1.get(key) for key in M1_GUARDED}, **{f"m3.{key}": m3.get(key) for key in M3_GUARDED}}


def _dominates(metrics: dict[str, Any], champion: dict[str, Any]) -> tuple[bool, int]:
    if any(key.startswith(("m1.", "m3.")) for key in metrics):
        current, baseline = metrics, champion
    else:
        current = {f"m1.{key}": value for key, value in metrics.items() if key in M1_GUARDED}
        baseline = {f"m1.{key}": value for key, value in champion.items() if key in M1_GUARDED}
    higher = {"m1.directional_precision", "m1.large_move_recall", "m3.directional_precision"}
    lower = {"m1.false_warning_rate", "m1.opposite_move_rate", "m1.whipsaw_rate", "m1.burden_per_jst_day", "m3.opposite_move_rate", "m3.balanced_no_expansion_rate", "m3.whipsaw_rate", "m3.burden_per_jst_day"}
    all_keys = sorted(higher | lower)
    if any(current.get(key) is None or baseline.get(key) is None or not isinstance(current.get(key), (int, float)) or not isinstance(baseline.get(key), (int, float)) for key in all_keys):
        return False, 0
    improved = 0
    for key in all_keys:
        if key in higher and current[key] < baseline[key]:
            return False, 0
        if key in lower and current[key] > baseline[key]:
            return False, 0
        if current[key] != baseline[key]:
            improved += 1
    return improved > 0, improved


def _candidate_record(cid: str, parameters: dict[str, int], m1: dict[str, Any], m3: dict[str, Any], states: dict[str, bool], reason_codes: list[str], improved: int = 0, diagnostics: dict[str, Any] | None = None, splits: dict[str, Any] | None = None, rolling: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    combined = (m1.get("burden_per_jst_day") or 0) + (m3.get("burden_per_jst_day") or 0)
    comparison = states["comparison_eligible"]
    public_rolling = [_public_snapshot(snapshot) for snapshot in (rolling or [])]
    return {"candidate_id": cid, "parameters_json": _canonical(parameters), "structurally_valid": states["structurally_valid"], "comparison_eligible": comparison, "pareto_dominant": states["pareto_dominant"], "proposal_eligible": states["proposal_eligible"], "valid": comparison, "reason_codes": "|".join(sorted(set(reason_codes))), "m1_validation_3h_json": _canonical(m1), "m3_validation_3h_json": _canonical(m3), "m3_diagnostic_horizons_json": _canonical(diagnostics or {}), "m1_split_comparison_json": _canonical((splits or {}).get("m1", {})), "m3_split_comparison_json": _canonical((splits or {}).get("m3", {})), "rolling_snapshots_json": _canonical(public_rolling), "improved_guarded_metric_count": improved, "combined_burden": combined, "recommendation": "eligible_for_human_reviewed_proposal" if states["proposal_eligible"] else ("continue_shadow_collection" if states["structurally_valid"] else "reject")}


def _p8_status(trial_facts: Path | None, trial_report: Path | None) -> dict[str, Any]:
    result = {"status": "missing", "ready": False, "unique_actual_episode_count": 0, "actual_high_medium_count": 0}
    if not trial_facts or not trial_report or not trial_facts.is_file() or not trial_report.is_file():
        return result
    try:
        report = _read_json(trial_report)
        facts = _read_csv(trial_facts, {"actual_episode_id", "evidence_tier"})
    except ValueError:
        result["status"] = "invalid"
        return result
    practical = report.get("p9_readiness", {}).get("practical", {})
    ids = {row["actual_episode_id"] for row in facts if row["actual_episode_id"]}
    high = {row["actual_episode_id"] for row in facts if row.get("evidence_tier") == "actual_high_medium" and row.get("actual_episode_id")}
    result.update({"status": report.get("actual_evidence", {}).get("status", "missing"), "ready": practical.get("ready") is True, "unique_actual_episode_count": len(ids), "actual_high_medium_count": len(high)})
    return result


def _atomic(outputs: dict[Path, bytes], replace_output: bool) -> None:
    paths = list(outputs)
    if not replace_output and any(path.exists() for path in paths):
        raise ValueError("output_exists_use_replace")
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="macro-p9-stage-", dir=str(paths[0].parent)))
    backup = Path(tempfile.mkdtemp(prefix="macro-p9-backup-", dir=str(paths[0].parent)))
    promoted: list[Path] = []
    try:
        staged: dict[Path, Path] = {}
        for index, (path, payload) in enumerate(sorted(outputs.items(), key=lambda item: str(item[0]))):
            temp = stage / f"{index}-{path.name}"
            temp.write_bytes(payload)
            staged[path] = temp
        for index, path in enumerate(paths):
            if path.exists():
                os.replace(path, backup / f"{index}-{path.name}")
        for path, temp in staged.items():
            os.replace(temp, path)
            promoted.append(path)
    except Exception:
        for path in promoted:
            path.unlink(missing_ok=True)
        for index, path in enumerate(paths):
            old = backup / f"{index}-{path.name}"
            if old.exists():
                os.replace(old, path)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
        shutil.rmtree(backup, ignore_errors=True)


def _csv_bytes(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> bytes:
    from io import StringIO
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    return output.getvalue().encode()


def _run_candidate(parameters: dict[str, int], paths: dict[str, Path], fixed: dict[str, Any], temp_root: Path) -> dict[str, Any]:
    cid = candidate_id(parameters)
    m1dir = temp_root / cid / "m1"; m3dir = temp_root / cid / "m3"
    m1dir.mkdir(parents=True); m3dir.mkdir(parents=True)
    replay_macro_structure_volatility(signals=paths["signals"], ohlcv_15m=paths["ohlcv_15m"], ohlcv_1h=paths["ohlcv_1h"], ohlcv_4h=paths["ohlcv_4h"], output_events_csv=m1dir/"events.csv", output_levels_csv=m1dir/"levels.csv", output_misses_csv=m1dir/"misses.csv", output_json=m1dir/"replay.json", output_md=m1dir/"replay.md", cutoff_utc=fixed["cutoff_utc"], left_window=parameters["left_window"], right_window=parameters["right_window"], performance_start_utc=fixed["performance_start_utc"], performance_end_utc=fixed["performance_end_utc"], replace_output=True)
    replay_macro_next_regime(signals=paths["signals"], macro_events=m1dir/"events.csv", macro_levels=m1dir/"levels.csv", macro_replay_json=m1dir/"replay.json", output_events_csv=m3dir/"events.csv", output_episodes_csv=m3dir/"episodes.csv", output_json=m3dir/"replay.json", output_md=m3dir/"replay.md", replace_output=True)
    return {"candidate_id": cid, "parameters": parameters, "m1": m1dir, "m3": m3dir}


def run_macro_p9_proposal_engine(*, signals: Path, ohlcv_15m: Path, ohlcv_1h: Path, ohlcv_4h: Path, m1_events_csv: Path, m1_levels_csv: Path, m1_misses_csv: Path, m1_replay_json: Path, m3_events_csv: Path, m3_episodes_csv: Path, m3_replay_json: Path, champion_manifest: Path, proposal_space_manifest: Path, output_results_csv: Path, output_issues_csv: Path, output_json: Path, output_md: Path, replace_output: bool = False, p8_trial_facts_csv: Path | None = None, p8_trial_report_json: Path | None = None) -> dict[str, Any]:
    champion = _read_json(champion_manifest)
    _validate_champion_manifest(champion)
    space = _read_json(proposal_space_manifest)
    input_paths = {"signals": signals, "ohlcv_15m": ohlcv_15m, "ohlcv_1h": ohlcv_1h, "ohlcv_4h": ohlcv_4h}
    if _fingerprints(input_paths) != champion["input_fingerprints"]:
        raise ValueError("input_fingerprint_mismatch")
    artifact_paths = {"m1_events": m1_events_csv, "m1_levels": m1_levels_csv, "m1_misses": m1_misses_csv, "m1_replay": m1_replay_json, "m3_events": m3_events_csv, "m3_episodes": m3_episodes_csv, "m3_replay": m3_replay_json}
    declared_artifacts = champion["accepted_artifact_fingerprints"]
    supplied_signature = _artifact_signature(artifact_paths)
    if {key: value["sha256"] for key, value in supplied_signature.items()} != declared_artifacts:
        raise ValueError("accepted_artifact_fingerprint_mismatch")
    _require_version(_read_json(m1_replay_json), M1_SCHEMA, M1_SCHEMA)
    _require_version(_read_json(m3_replay_json), M3_SCHEMA, M3_SCHEMA)
    m1_events = _read_csv(m1_events_csv, {"event_id", "signal_id"})
    _unique(m1_events, "event_id")
    _unique(_read_csv(m1_levels_csv, {"level_id"}), "level_id")
    m1_misses = _read_csv(m1_misses_csv, {"opportunity_id"})
    _unique(m1_misses, "opportunity_id")
    m3_events = _read_csv(m3_events_csv, {"record_id", "event_id", "signal_id"})
    m3_episodes = _read_csv(m3_episodes_csv, {"episode_id", "policy"})
    _unique(m3_events, "record_id")
    _unique(m3_events, "event_id")
    _unique(m3_episodes, "episode_id")
    parameters = champion["parameters"]
    space_candidates = _expand_space(space, champion)
    champion_pair = {key: parameters[key] for key in LEVERS}
    champion_id = candidate_id(champion_pair)
    p8 = _p8_status(p8_trial_facts_csv, p8_trial_report_json)
    with tempfile.TemporaryDirectory(prefix="macro-p9-eval-") as temp:
        temp_root = Path(temp)
        champion_run = _run_candidate(champion_pair, input_paths, parameters, temp_root)
        fresh_artifacts = _artifact_signature({"m1_events": champion_run["m1"] / "events.csv", "m1_levels": champion_run["m1"] / "levels.csv", "m1_misses": champion_run["m1"] / "misses.csv", "m1_replay": champion_run["m1"] / "replay.json", "m3_events": champion_run["m3"] / "events.csv", "m3_episodes": champion_run["m3"] / "episodes.csv", "m3_replay": champion_run["m3"] / "replay.json"})
        comparable = {key: value["sha256"] for key, value in fresh_artifacts.items() if key not in {"m1_replay", "m3_replay"}}
        supplied = {key: value["sha256"] for key, value in supplied_signature.items() if key not in {"m1_replay", "m3_replay"}}
        if comparable != {key: value for key, value in declared_artifacts.items() if key not in {"m1_replay", "m3_replay"}} or {key: value["ids"] for key, value in fresh_artifacts.items() if key not in {"m1_replay", "m3_replay"}} != {key: value["ids"] for key, value in supplied_signature.items() if key not in {"m1_replay", "m3_replay"}}:
            raise ValueError("champion_identity_mismatch")
        fresh_m1 = _read_json(champion_run["m1"] / "replay.json")
        fresh_m3 = _read_json(champion_run["m3"] / "replay.json")
        champion_dates = _jst_dates(champion_run["m3"] / "events.csv")
        if champion_dates != _jst_dates(m3_events_csv):
            raise ValueError("champion_date_basis_mismatch")
        candidate_specs = [(champion_id, parameters, champion_run)] + [(candidate_id(candidate), candidate, None) for candidate in space_candidates]
        rolling_by_cid: dict[str, list[dict[str, Any]]] = {}
        champion_rolling, _ = _rolling_snapshots(input_paths, champion_pair, parameters, champion_pair, temp_root / "rolling-champion")
        rolling_by_cid[champion_id] = champion_rolling
        for candidate in space_candidates:
            cid = candidate_id(candidate)
            _, candidate_rolling = _rolling_snapshots(input_paths, candidate, parameters | candidate, champion_pair, temp_root / f"rolling-{cid}", champion_cache=champion_rolling)
            rolling_by_cid[cid] = candidate_rolling
        champion_m1 = _m1_metrics(fresh_m1)
        champion_m3 = _m3_metrics(fresh_m3)
        champion_diag = _m3_diagnostics(fresh_m3)
        champion_concentration = _date_concentration(_read_csv(champion_run["m3"] / "episodes.csv", {"episode_id", "start_timestamp_utc"}), champion_dates)
        records: list[dict[str, Any]] = []
        issue_rows: list[dict[str, Any]] = []
        for cid, candidate_parameters, run in candidate_specs:
            m1_summary = fresh_m1 if run is None else _read_json(run["m1"] / "replay.json")
            m3_summary = fresh_m3 if run is None else _read_json(run["m3"] / "replay.json")
            rolling = rolling_by_cid.get(cid, [])
            latest, rolling_m1, rolling_m3, rolling_diagnostics = _candidate_rolling_evidence(rolling)
            if cid == champion_id:
                candidate_m1 = _m1_metrics(m1_summary)
                candidate_m3 = _m3_metrics(m3_summary)
                diagnostics = _m3_diagnostics(m3_summary)
            else:
                candidate_m1 = rolling_m1
                candidate_m3 = rolling_m3
                diagnostics = rolling_diagnostics
            reasons: list[str] = []
            structural = True
            if run is not None and _jst_dates(run["m3"] / "events.csv") != champion_dates:
                structural = False; reasons.append("eligible_date_basis_mismatch")
            if cid != champion_id and run is not None:
                base_opportunities = _artifact_signature({"misses": champion_run["m1"] / "misses.csv"})["misses"]["ids"].get("opportunity_id", [])
                run_opportunities = _artifact_signature({"misses": run["m1"] / "misses.csv"})["misses"]["ids"].get("opportunity_id", [])
                if base_opportunities != run_opportunities:
                    structural = False; reasons.append("independent_opportunity_set_mismatch")
            if run is not None and (not _data_quality_ok(m1_summary) or not _data_quality_ok(m3_summary)):
                structural = False; reasons.append("validation_data_quality_or_continuity_failed")
            validation_dates = latest.get("m3_validation_jst_dates", []) if latest else list(m3_summary.get("recommendation", {}).get("validation_dates", []))
            fallback_concentration = _date_concentration([row for row in _read_csv(run["m3"] / "episodes.csv", {"episode_id", "policy", "start_timestamp_utc"}) if row.get("policy") == "candidate"], validation_dates) if run is not None else _date_concentration([], validation_dates)
            concentration = latest.get("validation_date_concentration", fallback_concentration) if latest else fallback_concentration
            rolling_established = bool(rolling and all(_snapshot_eligible(snapshot, snapshot.get("snapshot_jst_date")) for snapshot in rolling))
            latest_eligible = bool(latest and _snapshot_eligible(latest, latest.get("snapshot_jst_date")) and latest.get("comparison_eligible"))
            earlier_degradation = any(_snapshot_eligible(snapshot, snapshot.get("snapshot_jst_date")) and not snapshot.get("comparison_eligible") for snapshot in rolling[:-1])
            comparison = structural and rolling_established and latest_eligible and not earlier_degradation
            for rolling_reason in sorted({reason for snapshot in rolling for reason in snapshot.get("reason_codes", [])}):
                if rolling_reason in {"split_required_metric_missing", "split_guarded_metric_degradation", "champion_snapshot_not_eligible"}:
                    reasons.append(rolling_reason)
            if not rolling_established:
                reasons.append("rolling_comparison_not_established")
            if any(value is None or not isinstance(value, (int, float)) for value in _guarded_vector(candidate_m1, candidate_m3).values()):
                comparison = False; reasons.append("guarded_metric_missing")
            if candidate_m3.get("resolved_up_count", 0) < 10 or candidate_m3.get("resolved_down_count", 0) < 10:
                comparison = False; reasons.append("validation_direction_count_insufficient")
            if not concentration.get("pass", False):
                comparison = False; reasons.append("validation_date_concentration_over_0_50")
            if cid == champion_id:
                m1_splits = {}
                m3_splits = {}
            elif latest:
                m1_splits = latest.get("m1_split_comparison", {})
                m3_splits = latest.get("m3_split_comparison", {})
                split_ok, split_reasons = _split_gate({"m1": m1_splits, "m3": m3_splits})
                if not split_ok:
                    comparison = False
                    reasons.extend(split_reasons)
            else:
                m1_splits = {}
                m3_splits = {}
                comparison = False
                reasons.append("rolling_comparison_not_established")
            same_date_champion_m1 = latest.get("_champion_m1_metrics", {}) if latest and latest.get("_champion_baseline_eligible") and cid != champion_id else {}
            same_date_champion_m3 = latest.get("_champion_m3_metrics", {}) if latest and latest.get("_champion_baseline_eligible") and cid != champion_id else {}
            if cid != champion_id and (not same_date_champion_m1 or not same_date_champion_m3):
                comparison = False
                reasons.append("champion_snapshot_not_eligible")
            dominates, improved = (False, 0) if cid == champion_id else _dominates(_guarded_vector(candidate_m1, candidate_m3), _guarded_vector(same_date_champion_m1, same_date_champion_m3))
            pareto = bool(comparison and dominates)
            if cid != champion_id and not dominates:
                reasons.append("not_pareto_dominant")
            proposal = bool(pareto and p8["ready"] and p8["status"] == "provided" and p8["unique_actual_episode_count"] >= 50 and p8["actual_high_medium_count"] > 0)
            if not proposal:
                reasons.append("p8_actual_evidence_insufficient")
            states = {"structurally_valid": structural, "comparison_eligible": comparison, "pareto_dominant": pareto, "proposal_eligible": proposal}
            rec = _candidate_record(cid, candidate_parameters, candidate_m1, candidate_m3, states, reasons, improved, diagnostics, {"m1": m1_splits, "m3": m3_splits}, rolling)
            rec["validation_date_concentration_json"] = _canonical(concentration)
            rec["m1_split_comparison_json"] = _canonical(m1_splits)
            rec["m3_split_comparison_json"] = _canonical(m3_splits)
            records.append(rec)
            lineage = latest.get("_issue_lineage", []) if latest else []
            issue_rows.extend(_issue_rows(cid, lineage, m1_splits, candidate_m1, same_date_champion_m1, candidate_m3, same_date_champion_m3, concentration, p8))
    dominators = [row for row in records if row["candidate_id"] != champion_id and row["pareto_dominant"]]
    dominators.sort(key=lambda row: (-row["improved_guarded_metric_count"], -(_safe_number(json.loads(row["m1_validation_3h_json"]).get("large_move_recall"), -1)), -(_safe_number(json.loads(row["m3_validation_3h_json"]).get("directional_precision"), -1)), _safe_number(json.loads(row["m1_validation_3h_json"]).get("false_warning_rate"), 999), _safe_number(json.loads(row["m3_validation_3h_json"]).get("opposite_move_rate"), 999), row["combined_burden"], row["candidate_id"]))
    winner = dominators[0]["candidate_id"] if dominators else "none"
    proposal_eligible = bool(winner != "none" and any(row["proposal_eligible"] and row["candidate_id"] == winner for row in records))
    recommendation = "eligible_for_human_reviewed_proposal" if proposal_eligible else "continue_shadow_collection"
    report_reasons = [] if proposal_eligible else ["p8_actual_evidence_insufficient"]
    if p8["status"] != "provided" or not p8["ready"] or p8["unique_actual_episode_count"] < 50 or p8["actual_high_medium_count"] <= 0:
        issue_rows.append({"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "candidate_id": "REPORT_GLOBAL", "issue_category": "actual evidence missing or conflicting", "status": "observed", "evidence_source": "p8_actual_status", "evidence_count": p8["unique_actual_episode_count"], "affected_metric_split": "proposal_eligibility", "champion_value": None, "candidate_value": None, "reason_codes": "p8_actual_evidence_insufficient", "actual_backed_count": p8["actual_high_medium_count"], "proposal_eligibility_effect": "capped_continue_shadow_collection"})
    results_fields = ("candidate_id", "parameters_json", "structurally_valid", "comparison_eligible", "pareto_dominant", "proposal_eligible", "valid", "reason_codes", "m1_validation_3h_json", "m3_validation_3h_json", "m3_diagnostic_horizons_json", "m1_split_comparison_json", "m3_split_comparison_json", "rolling_snapshots_json", "validation_date_concentration_json", "improved_guarded_metric_count", "combined_burden", "recommendation")
    challengers = [row for row in records if row["candidate_id"] != champion_id]
    report = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "primary_gate_horizon": "3h", "champion": {"candidate_id": champion_id, "parameters": champion_pair, "m1_metrics": champion_m1, "m3_metrics": champion_m3, "diagnostic_horizons": champion_diag, "validation_dates": champion_dates, "concentration": champion_concentration}, "counts": {"total_candidates": len(records), "champion_count": 1, "challenger_count": len(challengers), "structurally_valid_challengers": sum(row["structurally_valid"] for row in challengers), "comparison_eligible_challengers": sum(row["comparison_eligible"] for row in challengers), "pareto_dominant_challengers": sum(row["pareto_dominant"] for row in challengers), "proposal_eligible_challengers": sum(row["proposal_eligible"] for row in challengers)}, "expanded_proposal_space": [json.loads(row["parameters_json"]) for row in challengers], "candidate_validation_results": records, "rolling_comparison": {row["candidate_id"]: json.loads(row["rolling_snapshots_json"]) for row in records}, "split_comparisons": {row["candidate_id"]: {"m1": json.loads(row["m1_split_comparison_json"]), "m3": json.loads(row["m3_split_comparison_json"])} for row in records}, "diagnostic_horizons": ["6h", "12h", "24h"], "pareto_ranking": [row["candidate_id"] for row in dominators], "winner": winner, "recommendation": recommendation, "reason_codes": report_reasons, "p8_actual_status": p8, "input_fingerprints": _fingerprints(input_paths), "accepted_artifact_fingerprints": declared_artifacts, "safety_boundary": SAFETY}
    markdown = "# Macro P9 Proposal Engine\n\n## Result\n\n- primary horizon: 3h\n- winner: %s\n- recommendation: %s\n- reason codes: %s\n\n## Rolling comparison\n\n- candidate states: structurally_valid / comparison_eligible / pareto_dominant / proposal_eligible\n- diagnostic horizons: 6h, 12h, 24h; stored only and not used for ranking\n\n## Evidence\n\n- P8/actual status: %s\n- split comparisons and issue diagnosis are evidence-based\n- no production mutation; report-only / not FORMAL_GO / no automatic order / human decides manually\n" % (winner, recommendation, ", ".join(report_reasons) or "none", json.dumps(p8, sort_keys=True))
    issue_fields = ("schema_version", "method_version", "candidate_id", "issue_category", "status", "evidence_source", "evidence_count", "affected_metric_split", "champion_value", "candidate_value", "reason_codes", "actual_backed_count", "proposal_eligibility_effect")
    _atomic({output_results_csv: _csv_bytes(records, results_fields), output_issues_csv: _csv_bytes(issue_rows, issue_fields), output_json: (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(), output_md: markdown.encode()}, replace_output)
    return {"ok": True, "exit_code": 0, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "candidate_count": len(records), "winner": winner, "recommendation": recommendation, "p8_actual_status": p8, "output_count": 4, "structurally_valid_count": sum(row["structurally_valid"] for row in records), "comparison_eligible_count": sum(row["comparison_eligible"] for row in records), "pareto_dominant_count": sum(row["pareto_dominant"] for row in records)}


def _safe_number(value: Any, default: float) -> float:
    return float(value) if isinstance(value, (int, float)) else default
