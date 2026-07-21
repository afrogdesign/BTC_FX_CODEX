"""Deterministic offline M5 champion/challenger proposal engine."""
from __future__ import annotations

import csv
import gc
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
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


def _validation_metrics(summary: dict[str, Any], policy: str) -> dict[str, Any]:
    rec = summary.get("recommendation", {})
    if not isinstance(rec, dict) or not rec:
        rec = summary.get("recommendation_gate", {})
    source = rec.get("validation_candidate_metrics" if policy == "candidate" else "validation_baseline_metrics")
    if not isinstance(source, dict):
        source = rec.get("validation_policy_metrics", {})
    if policy == "candidate" and isinstance(source, dict) and "3h" in source:
        return source["3h"]
    if policy == "baseline" and isinstance(source, dict) and "3h" in source:
        return source["3h"]
    metrics = summary.get("metrics", {})
    candidates = [value for key, value in metrics.items() if key not in {"current_notification"} and isinstance(value, dict)]
    return candidates[0] if candidates else {}


def _m1_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    source = _validation_metrics(summary, "candidate")
    return {key: source.get(key) for key in ("directional_precision", "large_move_recall", "false_warning_rate", "opposite_move_rate", "whipsaw_rate", "burden_per_jst_day")}


def _m3_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    source = summary.get("recommendation", {}).get("validation_candidate_metrics", {}).get("3h", {})
    return {key: source.get(key) for key in ("directional_precision", "opposite_move_rate", "balanced_no_expansion_rate", "whipsaw_rate", "burden_per_jst_day", "resolved_up_count", "resolved_down_count")}


def _data_quality_ok(summary: dict[str, Any]) -> bool:
    rec = summary.get("recommendation", {})
    return bool(summary.get("coverage", {}).get("continuity_pass", True)) and bool(rec.get("validation_data_quality_pass", True)) and not any("unresolved" in str(x) for x in rec.get("reason_codes", []))


def _dominates(metrics: dict[str, Any], champion: dict[str, Any]) -> tuple[bool, int]:
    higher = {"directional_precision", "large_move_recall"}
    lower = {"false_warning_rate", "opposite_move_rate", "whipsaw_rate", "burden_per_jst_day", "balanced_no_expansion_rate"}
    all_keys = set(higher | lower)
    if any(metrics.get(key) is None or champion.get(key) is None for key in all_keys):
        return False, 0
    improved = 0
    for key in all_keys:
        if key in higher and metrics[key] < champion[key]:
            return False, 0
        if key in lower and metrics[key] > champion[key]:
            return False, 0
        if metrics[key] != champion[key]:
            improved += 1
    return improved > 0, improved


def _candidate_record(cid: str, parameters: dict[str, int], m1: dict[str, Any], m3: dict[str, Any], valid: bool, reason_codes: list[str], improved: int = 0) -> dict[str, Any]:
    combined = (m1.get("burden_per_jst_day") or 0) + (m3.get("burden_per_jst_day") or 0)
    return {"candidate_id": cid, "parameters_json": _canonical(parameters), "valid": valid, "reason_codes": "|".join(sorted(set(reason_codes))), "m1_validation_3h_json": _canonical(m1), "m3_validation_3h_json": _canonical(m3), "improved_guarded_metric_count": improved, "combined_burden": combined, "recommendation": "continue_shadow_collection" if valid else "reject"}


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
    champion = _read_json(champion_manifest); _validate_champion_manifest(champion)
    space = _read_json(proposal_space_manifest)
    input_paths = {"signals": signals, "ohlcv_15m": ohlcv_15m, "ohlcv_1h": ohlcv_1h, "ohlcv_4h": ohlcv_4h}
    if _fingerprints(input_paths) != champion["input_fingerprints"]:
        raise ValueError("input_fingerprint_mismatch")
    artifact_paths = {"m1_events": m1_events_csv, "m1_levels": m1_levels_csv, "m1_misses": m1_misses_csv, "m1_replay": m1_replay_json, "m3_events": m3_events_csv, "m3_episodes": m3_episodes_csv, "m3_replay": m3_replay_json}
    declared_artifacts = champion["accepted_artifact_fingerprints"]
    supplied_signature = _artifact_signature(artifact_paths)
    if {key: value["sha256"] for key, value in supplied_signature.items()} != declared_artifacts:
        raise ValueError("accepted_artifact_fingerprint_mismatch")
    m1summary = _read_json(m1_replay_json); m3summary = _read_json(m3_replay_json)
    _require_version(m1summary, M1_SCHEMA, M1_SCHEMA); _require_version(m3summary, M3_SCHEMA, M3_SCHEMA)
    _unique(_read_csv(m1_events_csv, {"event_id", "signal_id"}), "event_id"); _unique(_read_csv(m1_levels_csv, {"level_id"}), "level_id"); _unique(_read_csv(m1_misses_csv, {"opportunity_id"}), "opportunity_id")
    m3_events = _read_csv(m3_events_csv, {"record_id", "event_id", "signal_id"}); m3_episodes = _read_csv(m3_episodes_csv, {"episode_id", "policy"})
    _unique(m3_events, "record_id"); _unique(m3_events, "event_id"); _unique(m3_episodes, "episode_id")
    parameters = champion["parameters"]
    space_candidates = _expand_space(space, champion)
    champion_pair = {key: parameters[key] for key in LEVERS}
    with tempfile.TemporaryDirectory(prefix="macro-p9-eval-") as temp:
        temp_root = Path(temp)
        champion_run = _run_candidate(champion_pair, input_paths, parameters, temp_root)
        fresh_artifacts = _artifact_signature({"m1_events": champion_run["m1"]/"events.csv", "m1_levels": champion_run["m1"]/"levels.csv", "m1_misses": champion_run["m1"]/"misses.csv", "m1_replay": champion_run["m1"]/"replay.json", "m3_events": champion_run["m3"]/"events.csv", "m3_episodes": champion_run["m3"]/"episodes.csv", "m3_replay": champion_run["m3"]/"replay.json"})
        fresh_hashes = {key: value["sha256"] for key, value in fresh_artifacts.items()}
        comparable_hashes = {key: value for key, value in fresh_hashes.items() if key not in {"m1_replay", "m3_replay"}}
        declared_comparable_hashes = {key: value for key, value in declared_artifacts.items() if key not in {"m1_replay", "m3_replay"}}
        if comparable_hashes != declared_comparable_hashes:
            raise ValueError("champion_fingerprint_mismatch")
        supplied_ids = {key: value["ids"] for key, value in supplied_signature.items() if key not in {"m1_replay", "m3_replay"}}
        fresh_ids = {key: value["ids"] for key, value in fresh_artifacts.items() if key not in {"m1_replay", "m3_replay"}}
        if fresh_ids != supplied_ids:
            raise ValueError("champion_identity_mismatch")
        fresh_m1 = _read_json(champion_run["m1"]/"replay.json"); fresh_m3 = _read_json(champion_run["m3"]/"replay.json")
        if _jst_dates(champion_run["m3"]/"events.csv") != _jst_dates(m3_events_csv):
            raise ValueError("champion_date_basis_mismatch")
        records: list[dict[str, Any]] = []
        all_runs = [champion_run]
        for candidate in space_candidates:
            all_runs.append(_run_candidate(candidate, input_paths, parameters | candidate, temp_root))
            gc.collect()
        champion_m1 = _m1_metrics(fresh_m1); champion_m3 = _m3_metrics(fresh_m3)
        champion_dates = _jst_dates(champion_run["m3"]/"events.csv")
        for run in all_runs:
            cid = run["candidate_id"]
            candidate_m1 = _m1_metrics(_read_json(run["m1"]/"replay.json")); candidate_m3 = _m3_metrics(_read_json(run["m3"]/"replay.json"))
            valid = True; reasons: list[str] = []
            if _jst_dates(run["m3"]/"events.csv") != champion_dates:
                valid = False; reasons.append("eligible_date_basis_mismatch")
            if cid != candidate_id(champion_pair):
                base_ids = _artifact_signature({"misses": champion_run["m1"]/"misses.csv"})["misses"]["ids"].get("opportunity_id", [])
                run_ids = _artifact_signature({"misses": run["m1"]/"misses.csv"})["misses"]["ids"].get("opportunity_id", [])
                if base_ids != run_ids:
                    valid = False; reasons.append("independent_opportunity_set_mismatch")
            if not _data_quality_ok(_read_json(run["m1"]/"replay.json")) or not _data_quality_ok(_read_json(run["m3"]/"replay.json")):
                valid = False; reasons.append("validation_data_quality_or_continuity_failed")
            if cid != candidate_id(champion_pair):
                dominates, improved = _dominates({**candidate_m1, **{f"m3_{k}": v for k, v in candidate_m3.items()}}, {**champion_m1, **{f"m3_{k}": v for k, v in champion_m3.items()}}) if False else (False, 0)
                all_current = {"directional_precision": candidate_m1.get("directional_precision"), "large_move_recall": candidate_m1.get("large_move_recall"), "false_warning_rate": candidate_m1.get("false_warning_rate"), "opposite_move_rate": candidate_m1.get("opposite_move_rate"), "whipsaw_rate": candidate_m1.get("whipsaw_rate"), "burden_per_jst_day": candidate_m1.get("burden_per_jst_day"), "balanced_no_expansion_rate": candidate_m3.get("balanced_no_expansion_rate")}
                all_champion = {"directional_precision": champion_m1.get("directional_precision"), "large_move_recall": champion_m1.get("large_move_recall"), "false_warning_rate": champion_m1.get("false_warning_rate"), "opposite_move_rate": champion_m1.get("opposite_move_rate"), "whipsaw_rate": champion_m1.get("whipsaw_rate"), "burden_per_jst_day": champion_m1.get("burden_per_jst_day"), "balanced_no_expansion_rate": champion_m3.get("balanced_no_expansion_rate")}
                dominates, improved = _dominates(all_current, all_champion)
                if not dominates:
                    reasons.append("not_pareto_dominant")
            else:
                improved = 0
            if candidate_m3.get("resolved_up_count", 0) < 10 or candidate_m3.get("resolved_down_count", 0) < 10:
                reasons.append("validation_direction_count_insufficient")
            rec = _candidate_record(cid, run["parameters"], candidate_m1, candidate_m3, valid, reasons, improved)
            rec["recommendation"] = "reject" if not valid else "continue_shadow_collection"
            records.append(rec)
    champion_id = candidate_id(champion_pair)
    valid_dominators = [row for row in records if row["candidate_id"] != champion_id and row["valid"] and "not_pareto_dominant" not in row["reason_codes"] and "validation_direction_count_insufficient" not in row["reason_codes"]]
    valid_dominators.sort(key=lambda row: (-row["improved_guarded_metric_count"], -json.loads(row["m1_validation_3h_json"]).get("large_move_recall", -1), -json.loads(row["m3_validation_3h_json"]).get("directional_precision", -1), json.loads(row["m1_validation_3h_json"]).get("false_warning_rate", 999), json.loads(row["m3_validation_3h_json"]).get("opposite_move_rate", 999), row["combined_burden"], row["candidate_id"]))
    winner = valid_dominators[0]["candidate_id"] if valid_dominators else "none"
    p8 = _p8_status(p8_trial_facts_csv, p8_trial_report_json)
    proposal_eligible = bool(winner != "none" and p8["ready"] and p8["status"] == "provided" and p8["unique_actual_episode_count"] >= 50 and p8["actual_high_medium_count"] > 0)
    recommendation = "eligible_for_human_reviewed_proposal" if proposal_eligible else "continue_shadow_collection"
    reasons = [] if proposal_eligible else ["p8_actual_evidence_insufficient"]
    results_fields = ("candidate_id", "parameters_json", "valid", "reason_codes", "m1_validation_3h_json", "m3_validation_3h_json", "improved_guarded_metric_count", "combined_burden", "recommendation")
    issue_rows = [{"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "candidate_id": row["candidate_id"], "issue_category": "actual evidence missing or conflicting", "status": "observed" if not proposal_eligible else "cleared", "evidence_count": p8["unique_actual_episode_count"], "affected_metric_split": "proposal_eligibility", "reason_codes": "|".join(reasons), "actual_backed_count": p8["actual_high_medium_count"], "proposal_eligibility_effect": "capped_continue_shadow_collection" if not proposal_eligible else "none"} for row in records]
    report = {"schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "primary_gate_horizon": "3h", "champion": {"candidate_id": champion_id, "parameters": champion_pair}, "expanded_proposal_space": [row["parameters_json"] for row in records if row["candidate_id"] != champion_id], "candidate_validation_results": records, "pareto_ranking": [row["candidate_id"] for row in valid_dominators], "diagnostic_horizons": ["6h", "12h", "24h"], "winner": winner, "recommendation": recommendation, "reason_codes": reasons, "p8_actual_status": p8, "input_fingerprints": _fingerprints(input_paths), "accepted_artifact_fingerprints": declared_artifacts, "safety_boundary": SAFETY}
    markdown = "# Macro P9 Proposal Engine\n\n## Result\n\n- primary horizon: 3h\n- winner: %s\n- recommendation: %s\n- reason codes: %s\n\n## Candidates\n\n- count: %d\n- diagnostic horizons: 6h, 12h, 24h; not used for ranking\n\n## Evidence\n\n- P8/actual status: %s\n- accepted artifacts and fresh raw bundle are fingerprinted\n- no production mutation; report-only / not FORMAL_GO / no automatic order / human decides manually\n" % (winner, recommendation, ", ".join(reasons) or "none", len(records), json.dumps(p8, sort_keys=True))
    _atomic({output_results_csv: _csv_bytes(records, results_fields), output_issues_csv: _csv_bytes(issue_rows, ("schema_version", "method_version", "candidate_id", "issue_category", "status", "evidence_count", "affected_metric_split", "reason_codes", "actual_backed_count", "proposal_eligibility_effect")), output_json: (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(), output_md: markdown.encode()}, replace_output)
    return {"ok": True, "exit_code": 0, "schema_version": SCHEMA_VERSION, "method_version": METHOD_VERSION, "candidate_count": len(records), "winner": winner, "recommendation": recommendation, "p8_actual_status": p8, "output_count": 4}
