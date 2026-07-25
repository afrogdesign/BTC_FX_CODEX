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


def _is_successful(manifest: dict[str, Any]) -> bool:
    if str(manifest.get("status", "")).lower() in {"failed", "partial_failure"}:
        return False
    source = manifest.get("source", {})
    return bool(source.get("max_timestamp"))


def scan_daily_directories(daily_root: str | Path, current_date: str | None = None) -> tuple[list[dict[str, Any]], list[str], Path]:
    root = Path(daily_root)
    dirs = sorted((p for p in root.iterdir() if p.is_dir() and DATE_RE.fullmatch(p.name)), key=lambda p: p.name) if root.exists() else []
    if current_date:
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
        if not _is_successful(manifest):
            warnings.append(directory.name + ":cycle_not_successful")
            continue
        accepted.append({"date": directory.name, "path": directory, "manifest": manifest})
    if not accepted:
        raise EvidenceInputError("no_successful_daily_directories")
    return accepted, warnings, accepted[-1]["path"]


def _aggregate_csv(accepted: list[dict[str, Any]], filename: str, logical: str) -> tuple[list[dict[str, str]], dict[str, Any], dict[str, str]]:
    rows: list[dict[str, str]] = []
    source_fingerprints: dict[str, str] = {}
    headers: list[str] | None = None
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
            rows.extend(dict(row) for row in reader)
    joined = b"".join((date.encode() + b":" + fingerprint.encode() + b"\n") for date, fingerprint in sorted(source_fingerprints.items()))
    return rows, {"logical_name": logical, "row_count": len(rows), "fingerprint": _sha(joined)}, source_fingerprints


def _canonical(root: Path, filename: str, logical: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    path = root / "logs/csv" / filename
    if not path.is_file():
        raise EvidenceInputError("missing_canonical_input:" + filename)
    return read_logical_csv(path, logical)


def refresh(root: Path, daily_root: Path, output_root: Path, runtime_generation: str, source_head: str | None = None, current_date: str | None = None) -> dict[str, Any]:
    accepted, warnings, selected = scan_daily_directories(daily_root, current_date)
    generation_head, resolution = _head(root, source_head)
    cutoff = _utc(accepted[-1]["manifest"]["source"]["max_timestamp"])
    classifications, cmeta, cfp = _aggregate_csv(accepted, "manual_operator_classifications.csv", "daily_classifications")
    trials, tmeta, tfp = _aggregate_csv(accepted, "manual_operator_trial_facts.csv", "daily_trial_facts")
    episodes, emeta = _canonical(root, "manual_trade_episodes.csv", "manual_trade_episodes.csv")
    links, lmeta = _canonical(root, "manual_trade_signal_links.csv", "manual_trade_signal_links.csv")
    signals, smeta = _canonical(root, "trades.csv", "trades.csv")
    generation = GenerationIdentity(program="P", runtime_generation=runtime_generation, source_head=generation_head, schema_version="p_cumulative_evidence.v1", method_version="p_cumulative_evidence.v1", cutoff_utc=cutoff, classifier_version="manual_operator_classifier.v4", linker_version="manual_trade_signal_link.v2", p8_evidence_version="manual_operator_trial_evidence.v1")
    inputs = {"classifications": (classifications, cmeta), "trial_facts": (trials, tmeta), "episodes": (episodes, emeta), "links_v2": (links, lmeta), "signal_log": (signals, smeta)}
    files, result = build_bundle(inputs, generation, cutoff)
    formal_rows = classifications + trials
    files.update(build_formal_outputs(formal_rows))
    manifest = result["manifest"]
    manifest.update({"source_head_resolution": resolution, "accepted_daily_directories": [item["date"] for item in accepted], "warnings": sorted(warnings), "per_source_fingerprints": {"classifications": cfp, "trial_facts": tfp, "episodes": {"canonical": emeta["fingerprint"]}, "links_v2": {"canonical": lmeta["fingerprint"]}, "signal_log": {"canonical": smeta["fingerprint"]}}, "lineage": [{"date": item["date"], "logical_directory": "logs/p8_operating_cycles/" + item["date"]} for item in accepted]})
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
