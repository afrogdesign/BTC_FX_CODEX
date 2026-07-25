"""Deterministically refresh the report-only current-generation P evidence bank."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contracts.generation_identity import GenerationIdentity
from src.feedback.formal_gate_semantic_impact import build_outputs as build_formal_outputs
from src.feedback.p_cumulative_evidence import EvidenceIdentityConflict, EvidenceInputError, EvidenceOutputConflict, build_bundle, read_logical_csv, write_bundle

DATE_RE = re.compile(r"^\d{8}$")
REQUIRED_DAILY = ("cycle_manifest.json", "manual_operator_classifications.csv", "manual_operator_trial_facts.csv", "manual_operator_trial_evidence.json", "manual_operator_trial_review_queue.csv")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc(value: str) -> str:
    text = str(value).strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise EvidenceInputError("cutoff_not_timezone_aware")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _head(root: Path, override: str | None) -> tuple[str, str]:
    if override:
        value, method = override.strip(), "explicit_override"
    else:
        value = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        method = "git"
    if not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise EvidenceInputError("invalid_source_head")
    return value.lower(), method


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceInputError("invalid_cycle_manifest") from exc


CORE_STAGES = ("candidate_slice", "signal_context_slice", "intraperiod_outcomes", "p4", "p5", "p8")

def _is_successful(manifest: dict[str, Any]) -> bool:
    if str(manifest.get("status", "")).lower() in {"failed", "partial_failure"}:
        return False
    source = manifest.get("source", {})
    stages = manifest.get("stage_statuses", {})
    return bool(_utc(source.get("max_timestamp", ""))) and all(stages.get(key) == "ok" for key in CORE_STAGES) and bool(_s(manifest.get("report_date")))

def _s(value: Any) -> str:
    return "" if value is None else str(value).strip()


def scan_daily_directories(daily_root: str | Path, current_date: str | None = None) -> tuple[list[dict[str, Any]], list[str], Path]:
    root = Path(daily_root)
    dirs = sorted((p for p in root.iterdir() if p.is_dir() and DATE_RE.fullmatch(p.name)), key=lambda p: p.name) if root.exists() else []
    if current_date:
        if not DATE_RE.fullmatch(current_date) or not any(p.name == current_date for p in dirs):
            raise EvidenceInputError("selected_current_date_missing:" + str(current_date))
        dirs = [p for p in dirs if p.name <= current_date]
    if not dirs:
        raise EvidenceInputError("no_daily_directories")
    accepted: list[dict[str, Any]] = []
    warnings: list[str] = []
    for directory in dirs:
        missing = [name for name in REQUIRED_DAILY if not (directory / name).is_file()]
        if missing:
            if directory == dirs[-1]:
                raise EvidenceInputError("selected_current_directory_incomplete:" + directory.name)
            warnings.append(directory.name + ":incomplete:" + ",".join(missing))
            continue
        manifest = _read_manifest(directory / "cycle_manifest.json")
        if _s(manifest.get("report_date")) != directory.name:
            if directory == dirs[-1]:
                raise EvidenceInputError("selected_current_report_date_mismatch:" + directory.name)
            warnings.append(directory.name + ":report_date_mismatch")
            continue
        if not _is_successful(manifest):
            if directory == dirs[-1]:
                raise EvidenceInputError("selected_current_cycle_not_successful:" + directory.name)
            warnings.append(directory.name + ":cycle_not_successful")
            continue
        accepted.append({"date": directory.name, "path": directory, "manifest": manifest})
    if not accepted:
        raise EvidenceInputError("no_successful_daily_directories")
    return accepted, warnings, accepted[-1]["path"]


def _row_time(row: dict[str, str], fields: tuple[str, ...]) -> datetime:
    raw = next((_s(row.get(field)) for field in fields if _s(row.get(field))), "")
    if not raw:
        raise EvidenceInputError("missing_event_timestamp:" + fields[0])
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00").replace(" ", "T"))
    except ValueError as exc:
        raise EvidenceInputError("malformed_event_timestamp") from exc
    if parsed.tzinfo is None:
        raise EvidenceInputError("naive_event_timestamp")
    return parsed.astimezone(timezone.utc)

def _snapshot_identity(kind: str, row: dict[str, str]) -> tuple[str, str, str]:
    if kind == "classification":
        return kind, _s(row.get("classifier_method_version")), _s(row.get("classification_id"))
    return "proxy_trial_fact", _s(row.get("classifier_method_version")), _s(row.get("trial_fact_id"))

def _snapshot_anchors(kind: str, row: dict[str, str]) -> tuple[str, ...]:
    fields = ("classification_id", "source_signal_id", "signal_id", "candidate_id", "event_timestamp_utc", "side", "classifier_method_version") if kind == "classification" else ("trial_fact_id", "scenario_id", "scenario_event_id", "signal_id", "candidate_id", "event_timestamp_utc", "side", "setup_family", "classifier_method_version")
    return tuple(_s(row.get(field)) for field in fields)

def _row_payload(row: dict[str, str]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _collapse_snapshots(accepted: list[dict[str, Any]], filename: str, logical: str, kind: str, cutoff: datetime) -> tuple[list[dict[str, str]], dict[str, Any], dict[str, str], dict[str, Any]]:
    rows: list[dict[str, str]] = []
    source_fingerprints: dict[str, str] = {}
    headers: list[str] | None = None
    selected: dict[tuple[str, str, str], dict[str, Any]] = {}
    exact_duplicates = 0; revisions = 0; superseded = 0; revised_ids: set[tuple[str, str, str]] = set()
    for item in accepted:
        path = item["path"] / filename
        data = path.read_bytes()
        source_fingerprints[item["date"]] = _sha(data)
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise EvidenceInputError("invalid_csv_schema:" + logical)
            if headers is None: headers = list(reader.fieldnames)
            elif list(reader.fieldnames) != headers: raise EvidenceInputError("incompatible_csv_schema:" + logical)
            daily_rows = sorted((dict(row) for row in reader), key=_row_payload)
            for row in daily_rows:
                value = dict(row)
                if _row_time(value, ("event_timestamp_utc",)) > cutoff:
                    raise EvidenceInputError("future_daily_event_timestamp:" + logical)
                identity = _snapshot_identity(kind, value)
                if not identity[1] or not identity[2]:
                    raise EvidenceInputError("missing_snapshot_identity:" + logical)
                anchors = _snapshot_anchors(kind, value)
                prior = selected.get(identity)
                if prior is not None:
                    anchor_fields = ("classification_id", "source_signal_id", "signal_id", "candidate_id", "event_timestamp_utc", "side", "classifier_method_version") if kind == "classification" else ("trial_fact_id", "scenario_id", "scenario_event_id", "signal_id", "candidate_id", "event_timestamp_utc", "side", "setup_family", "classifier_method_version")
                    differing = [field for field, old, new in zip(anchor_fields, prior["anchors"], anchors) if old != new]
                    if differing:
                        raise EvidenceInputError("snapshot_immutable_anchor_conflict:%s:%s:%s:%s:%s" % (logical, "|".join(identity), prior["date"], item["date"], ",".join(differing)))
                    if prior["payload"] == _row_payload(value):
                        exact_duplicates += 1
                    else:
                        revisions += 1; superseded += 1; revised_ids.add(identity)
                selected[identity] = {"row": value, "date": item["date"], "first_date": prior["first_date"] if prior is not None else item["date"], "revision_count": (prior["revision_count"] + 1 if prior is not None and prior["payload"] != _row_payload(value) else (prior["revision_count"] if prior is not None else 0)), "anchors": anchors, "payload": _row_payload(value)}
    rows = [selected[key]["row"] for key in sorted(selected)]
    selected_bytes = ("\n".join(_row_payload(row) for row in rows) + "\n").encode()
    meta = {"logical_name": logical, "row_count": len(rows), "fingerprint": _sha(selected_bytes), "headers": headers or []}
    identities = [{"component_version": key[1], "source_identity": key[2], "first_source_date": selected[key]["first_date"], "latest_source_date": selected[key]["date"], "revision_count": selected[key]["revision_count"]} for key in sorted(selected)]
    stats = {"snapshot_exact_duplicate_count": exact_duplicates, "snapshot_revised_identity_count": len(revised_ids), "snapshot_superseded_row_count": superseded, "selected_snapshot_row_count": len(rows), "snapshot_lineage": {logical: {"source_dates": sorted(source_fingerprints), "first_accepted_date": accepted[0]["date"], "latest_accepted_date": accepted[-1]["date"], "selected_row_count": len(rows), "identities": identities}}}
    return rows, meta, source_fingerprints, stats


def _canonical(root: Path, filename: str, logical: str, cutoff: datetime) -> tuple[list[dict[str, str]], dict[str, Any]]:
    path = root / "logs/csv" / filename
    if not path.is_file():
        raise EvidenceInputError("missing_canonical_input:" + filename)
    raw = path.read_bytes()
    try:
        reader = csv.DictReader(raw.decode("utf-8").splitlines())
        if not reader.fieldnames:
            raise EvidenceInputError("missing_input_headers:" + logical)
        rows = [dict(row) for row in reader]
    except (UnicodeError, csv.Error) as exc:
        raise EvidenceInputError("invalid_input:" + logical) from exc
    fields = {"manual_trade_episodes.csv": ("opened_at_utc", "closed_at_utc", "created_at_utc"), "manual_trade_signal_links.csv": ("entry_timestamp_utc", "created_at_utc", "entry_timestamp_jst", "created_at_jst"), "trades.csv": ("timestamp_utc", "created_at_utc")}[filename]
    selected = []
    excluded = 0
    for row in rows:
        timestamp = _row_time(row, fields)
        if timestamp <= cutoff:
            selected.append(row)
        else:
            excluded += 1
    selected_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in selected) + "\n").encode()
    meta = {"logical_name": logical, "row_count": len(selected), "fingerprint": _sha(selected_bytes), "raw_fingerprint": _sha(raw), "selected_fingerprint": _sha(selected_bytes), "included_row_count": len(selected), "excluded_after_cutoff_count": excluded, "lineage": "logs/csv/" + filename}
    return selected, meta


def refresh(root: Path, daily_root: Path, output_root: Path, runtime_generation: str, source_head: str | None = None, current_date: str | None = None) -> dict[str, Any]:
    accepted, warnings, selected = scan_daily_directories(daily_root, current_date)
    generation_head, resolution = _head(root, source_head)
    cutoff = _utc(accepted[-1]["manifest"]["source"]["max_timestamp"])
    cutoff_dt = datetime.fromisoformat(cutoff.replace("Z", "+00:00"))
    classifications, cmeta, cfp, cstats = _collapse_snapshots(accepted, "manual_operator_classifications.csv", "daily_classifications", "classification", cutoff_dt)
    trials, tmeta, tfp, tstats = _collapse_snapshots(accepted, "manual_operator_trial_facts.csv", "daily_trial_facts", "proxy_trial_fact", cutoff_dt)
    episodes, emeta = _canonical(root, "manual_trade_episodes.csv", "manual_trade_episodes.csv", cutoff_dt)
    links, lmeta = _canonical(root, "manual_trade_signal_links.csv", "manual_trade_signal_links.csv", cutoff_dt)
    signals, smeta = _canonical(root, "trades.csv", "trades.csv", cutoff_dt)
    generation = GenerationIdentity(program="P", runtime_generation=runtime_generation, source_head=generation_head, schema_version="p_cumulative_evidence.v1", method_version="p_cumulative_evidence.v1", cutoff_utc=cutoff, classifier_version="manual_operator_classifier.v4", linker_version="manual_trade_signal_link.v2", p8_evidence_version="manual_operator_trial_evidence.v1")
    inputs = {"classifications": (classifications, cmeta), "trial_facts": (trials, tmeta), "episodes": (episodes, emeta), "links_v2": (links, lmeta), "signal_log": (signals, smeta)}
    files, result = build_bundle(inputs, generation, cutoff)
    formal_rows = classifications
    files.update(build_formal_outputs(formal_rows))
    manifest = result["manifest"]
    manifest.update({"source_head_resolution": resolution, "accepted_daily_directories": [item["date"] for item in accepted], "warnings": sorted(warnings), "snapshot_policy": "latest_accepted_snapshot_as_of_cutoff", "snapshot_exact_duplicate_count": {"classifications": cstats["snapshot_exact_duplicate_count"], "trial_facts": tstats["snapshot_exact_duplicate_count"]}, "snapshot_revised_identity_count": {"classifications": cstats["snapshot_revised_identity_count"], "trial_facts": tstats["snapshot_revised_identity_count"]}, "snapshot_superseded_row_count": {"classifications": cstats["snapshot_superseded_row_count"], "trial_facts": tstats["snapshot_superseded_row_count"]}, "selected_snapshot_row_count": {"classifications": cstats["selected_snapshot_row_count"], "trial_facts": tstats["selected_snapshot_row_count"]}, "snapshot_lineage": {**cstats["snapshot_lineage"], **tstats["snapshot_lineage"]}, "per_source_fingerprints": {"classifications": cfp, "trial_facts": tfp, "episodes": emeta, "links_v2": lmeta, "signal_log": smeta}, "lineage": [{"date": item["date"], "logical_directory": "logs/p8_operating_cycles/" + item["date"]} for item in accepted]})
    manifest["output_fingerprints"] = {name: _sha(data) for name, data in sorted(files.items()) if name != "evidence_manifest.json"}
    contract = dict(manifest); contract.pop("manifest_contract_fingerprint", None); contract["output_fingerprints"] = dict(manifest["output_fingerprints"])
    manifest["manifest_contract_fingerprint"] = _sha((json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode())
    files["evidence_manifest.json"] = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    write_bundle(output_root, files, result["run_id"])
    current_v4_classification = sum(row.get("classifier_method_version", "").strip() == "manual_operator_classifier.v4" for row in classifications)
    current_v4_trial = sum(row.get("classifier_method_version", "").strip() == "manual_operator_classifier.v4" for row in trials)
    return {"run_id": result["run_id"], "manifest": manifest, "current_v4_classification_rows": current_v4_classification, "current_v4_proxy_trial_rows": current_v4_trial, "accepted_daily_directory_count": len(accepted), "formal": json.loads(files["formal_gate_semantic_impact.json"])}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Refresh current-generation P evidence")
    p.add_argument("--repo-root", default=str(ROOT)); p.add_argument("--daily-root", default="logs/p8_operating_cycles"); p.add_argument("--output-root", default="local/reports/p_evidence/p_current_generation"); p.add_argument("--runtime-generation", default="Ver04-v5"); p.add_argument("--source-head"); p.add_argument("--current-date"); p.add_argument("--stdout-json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv); root = Path(args.repo_root).resolve()
    try:
        result = refresh(root, root / args.daily_root, root / args.output_root, args.runtime_generation, args.source_head, args.current_date)
        if args.stdout_json: print(json.dumps({"ok": True, "run_id": result["run_id"], "accepted_daily_directory_count": result["accepted_daily_directory_count"], "current_v4_classification_rows": result["current_v4_classification_rows"], "current_v4_proxy_trial_rows": result["current_v4_proxy_trial_rows"], "formal_gate_semantic_impact": result["formal"]["counts"]}, sort_keys=True, separators=(",", ":")))
        return 0
    except EvidenceIdentityConflict as exc:
        if args.stdout_json: print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")))
        return 3
    except EvidenceOutputConflict as exc:
        if args.stdout_json: print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")))
        return 4
    except (EvidenceInputError, ValueError, OSError) as exc:
        if args.stdout_json: print(json.dumps({"ok": False, "error": str(exc)}, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
