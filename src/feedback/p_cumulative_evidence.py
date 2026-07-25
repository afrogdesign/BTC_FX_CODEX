from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.contracts.generation_identity import GenerationIdentity, LEGACY_UNVERSIONED

EVIDENCE_SCHEMA_VERSION = "p_cumulative_evidence.v1"
EVIDENCE_METHOD_VERSION = "p_cumulative_evidence.v1"
EVIDENCE_MANIFEST_VERSION = "p_evidence_manifest.v1"
SAFETY_BOUNDARY = "report-only / no canonical input replacement / no causal claim / no baseline adoption / no P9 decision / no automatic order"

EVIDENCE_HEADERS = (
    "schema_version", "evidence_id", "evidence_kind", "source_identity", "source_logical_name",
    "event_timestamp_utc", "signal_id", "scenario_event_id", "candidate_id", "episode_id", "link_id",
    "side", "setup_family", "market_regime", "operator_class", "formal_execution_gate",
    "notification_kind", "operator_decision_state", "proxy_outcome", "actual_link_confidence",
    "actual_realized_pnl", "evidence_basis", "human_basis", "causality_status", "component_version",
    "runtime_generation", "source_head", "cohort_key", "cutoff_utc",
)

OUTPUT_NAMES = (
    "evidence_manifest.json", "evidence_facts.csv", "evidence_summary.md",
    "modern_link_candidates_v3.csv", "notification_usefulness_ledger.csv",
    "modern_attribution_review_queue.csv", "modern_attribution_report.json",
    "modern_attribution_report.md",
)

class EvidenceInputError(ValueError):
    pass

class EvidenceIdentityConflict(ValueError):
    pass

class EvidenceOutputConflict(OSError):
    pass

def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()

def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

def _sha256(data: bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def _parse_cutoff(value: str) -> datetime:
    text = _text(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise EvidenceInputError("invalid_cutoff_utc") from exc
    if parsed.tzinfo is None:
        raise EvidenceInputError("naive_cutoff_utc")
    return parsed.astimezone(timezone.utc)

def _timestamp(row: Mapping[str, Any]) -> tuple[str, datetime]:
    for key in ("event_timestamp_utc", "timestamp_utc", "opened_at_utc", "closed_at_utc", "entry_timestamp_utc", "selected_at_utc", "event_timestamp_jst", "timestamp_jst", "opened_at_jst", "closed_at_jst", "entry_timestamp_jst", "created_at_utc", "evaluated_at_utc"):
        raw = _text(row.get(key))
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00").replace(" ", "T"))
        except ValueError as exc:
            raise EvidenceInputError("malformed_event_timestamp") from exc
        if dt.tzinfo is None:
            raise EvidenceInputError("naive_event_timestamp")
        utc = dt.astimezone(timezone.utc)
        return utc.isoformat().replace("+00:00", "Z"), utc
    raise EvidenceInputError("missing_event_timestamp")

def read_logical_csv(path: str | Path, logical_name: str | None = None) -> tuple[list[dict[str, str]], dict[str, Any]]:
    p = Path(path)
    if not p.is_file():
        raise EvidenceInputError("missing_input")
    try:
        raw = p.read_bytes()
        with io.StringIO(raw.decode("utf-8")) as fp:
            reader = csv.DictReader(fp)
            if not reader.fieldnames:
                raise EvidenceInputError("missing_input_headers")
            rows = [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error) as exc:
        raise EvidenceInputError("invalid_input") from exc
    return rows, {"logical_name": logical_name or p.name, "row_count": len(rows), "fingerprint": _sha256(raw), "headers": list(reader.fieldnames)}

def _source_id(kind: str, row: Mapping[str, Any]) -> str:
    field = {"classification": "classification_id", "proxy_trial_fact": "trial_fact_id", "actual_episode": "episode_id", "actual_link": "link_id"}.get(kind, "signal_id")
    return _text(row.get(field))

def _value(row: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = _text(row.get(key))
        if value:
            return value
    return ""

def _component(kind: str, row: Mapping[str, Any]) -> str:
    keys = {"classification": ("classifier_method_version",), "proxy_trial_fact": ("classifier_method_version",), "actual_episode": ("association_method_version",), "actual_link": ("link_method_version",), "decision_event": ("evaluation_trace_version",)}[kind]
    return _value(row, *keys) or LEGACY_UNVERSIONED

def _fact(kind: str, row: Mapping[str, Any], source: str, generation: GenerationIdentity, cutoff: str) -> tuple[dict[str, str], datetime]:
    identity = _source_id(kind, row)
    if not identity and kind == "decision_event":
        raise EvidenceInputError("blank_signal_id")
    if not identity:
        raise EvidenceInputError("missing_required_identity")
    stamp, dt = _timestamp(row)
    if dt > _parse_cutoff(cutoff):
        raise EvidenceInputError("future_event_timestamp")
    component = _component(kind, row)
    evidence_id = "ev_" + _sha256(kind + "|" + identity)
    actual_pnl = _value(row, "realized_pnl", "actual_realized_pnl", "actual_net_pnl_after_fee") if kind == "actual_episode" else ""
    basis = "proxy" if kind == "proxy_trial_fact" else ("actual" if kind in {"actual_episode", "actual_link"} else "descriptive")
    fact = {key: "" for key in EVIDENCE_HEADERS}
    values = {
        "schema_version": EVIDENCE_SCHEMA_VERSION, "evidence_id": evidence_id, "evidence_kind": kind,
        "source_identity": identity, "source_logical_name": source, "event_timestamp_utc": stamp,
        "signal_id": _value(row, "signal_id", "source_signal_id"), "scenario_event_id": _value(row, "scenario_event_id"),
        "candidate_id": _value(row, "candidate_id"), "episode_id": _value(row, "episode_id", "actual_episode_id"),
        "link_id": _value(row, "link_id"), "side": _value(row, "side", "position_side"),
        "setup_family": _value(row, "setup_family"), "market_regime": _value(row, "market_regime"),
        "operator_class": _value(row, "operator_class"), "formal_execution_gate": _value(row, "trade_execution_gate", "formal_execution_gate"),
        "notification_kind": _value(row, "notification_kind", "summary_variant", "reason_for_notification", "notification_class"),
        "operator_decision_state": _value(row, "operator_decision_state"), "proxy_outcome": _value(row, "outcome_status", "intraperiod_outcome", "proxy_outcome"),
        "actual_link_confidence": _value(row, "actual_link_confidence", "link_confidence"), "actual_realized_pnl": actual_pnl,
        "evidence_basis": basis, "human_basis": "unknown", "causality_status": "not_claimed", "component_version": component,
        "runtime_generation": generation.runtime_generation, "source_head": generation.source_head,
        "cohort_key": "|".join((generation.program, generation.runtime_generation, kind, component)), "cutoff_utc": cutoff,
    }
    fact.update(values)
    return fact, dt

def _csv_bytes(headers: tuple[str, ...] | list[str], rows: list[Mapping[str, Any]]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(headers), lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _text(row.get(key)) for key in headers})
    return out.getvalue().encode("utf-8")

def _dedupe_facts(facts: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    seen: dict[str, tuple[str, ...]] = {}
    result = []
    duplicates = 0
    for fact in facts:
        payload = tuple(fact[key] for key in EVIDENCE_HEADERS if key != "evidence_id")
        old = seen.get(fact["evidence_id"])
        if old is not None:
            if old != payload:
                raise EvidenceIdentityConflict("identity_conflict")
            duplicates += 1
            continue
        seen[fact["evidence_id"]] = payload
        result.append(fact)
    return sorted(result, key=lambda row: (row["event_timestamp_utc"], row["evidence_kind"], row["evidence_id"])), duplicates

def build_evidence_facts(inputs: Mapping[str, tuple[list[dict[str, str]], Mapping[str, Any]]], generation: GenerationIdentity, cutoff_utc: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    cutoff = _parse_cutoff(cutoff_utc)
    kinds = (("classifications", "classification"), ("trial_facts", "proxy_trial_fact"), ("episodes", "actual_episode"), ("links_v2", "actual_link"), ("signal_log", "decision_event"), ("exact_observations", "exact_observation"), ("active_plan_candidates", "active_plan_candidate"), ("signal_outcomes", "signal_outcome"))
    facts: list[dict[str, str]] = []
    rows_count: dict[str, int] = {}
    blank_counts: dict[str, int] = {}
    duplicate_count = 0
    for name, kind in kinds:
        entry = inputs.get(name)
        if entry is None:
            if name in {"classifications", "trial_facts", "episodes", "links_v2", "signal_log"}:
                raise EvidenceInputError("missing_input")
            continue
        rows, meta = entry
        rows_count[name] = len(rows)
        blanks = 0
        for row in rows:
            if not _source_id(kind, row):
                blanks += 1
                if kind == "decision_event":
                    continue
            fact, _ = _fact(kind, row, str(meta["logical_name"]), generation, cutoff.isoformat().replace("+00:00", "Z"))
            facts.append(fact)
        blank_counts[name] = blanks
    facts, duplicate_count = _dedupe_facts(facts)
    return facts, {"row_counts": rows_count, "blank_identity_counts": blank_counts, "exact_duplicate_counts": {"evidence_facts": duplicate_count}}

def build_summary(facts: list[dict[str, str]], generation: GenerationIdentity, cutoff_utc: str, input_meta: Mapping[str, Any]) -> str:
    kinds = Counter(row["evidence_kind"] for row in facts)
    links = Counter(row["actual_link_confidence"] or "blank" for row in facts if row["evidence_kind"] in {"actual_link", "actual_episode"})
    cohorts = Counter(row["cohort_key"] for row in facts)
    return "\n".join(("# P cumulative evidence summary", "", "- This is full-period evidence, not daily 5-day health.", f"- Generation: `{generation.runtime_generation}` / source `{generation.source_head}`.", f"- Cutoff: `{cutoff_utc}`.", f"- Actual episode/link baseline rows: {sum(row['evidence_kind']=='actual_episode' for row in facts)} / {sum(row['evidence_kind']=='actual_link' for row in facts)}.", f"- Evidence kinds: `{json.dumps(dict(sorted(kinds.items())), sort_keys=True)}`.", f"- Actual link confidence: `{json.dumps(dict(sorted(links.items())), sort_keys=True)}`.", f"- Cohorts: `{json.dumps(dict(sorted(cohorts.items())), sort_keys=True)}`.", "- Proxy, actual, and descriptive evidence remain separate; actual PnL is never proxy PnL.", "- Baseline candidate only; H2 human adoption is not recorded.", "- report-only / not FORMAL_GO / no automatic order.", "- Input fingerprints are recorded in the manifest without absolute paths.", ""))

def build_bundle(inputs: Mapping[str, tuple[list[dict[str, str]], Mapping[str, Any]]], generation: GenerationIdentity, cutoff_utc: str) -> tuple[dict[str, bytes], dict[str, Any]]:
    facts, stats = build_evidence_facts(inputs, generation, cutoff_utc)
    from src.feedback.manual_trade_modern_attribution import build_modern_outputs
    modern = build_modern_outputs(inputs["links_v2"][0], inputs["signal_log"][0], inputs["episodes"][0], inputs["classifications"][0], inputs["trial_facts"][0])
    files: dict[str, bytes] = {
        "evidence_facts.csv": _csv_bytes(EVIDENCE_HEADERS, facts),
        "evidence_summary.md": build_summary(facts, generation, cutoff_utc, inputs).encode("utf-8"),
        "modern_link_candidates_v3.csv": modern["candidate_csv"],
        "notification_usefulness_ledger.csv": modern["ledger_csv"],
        "modern_attribution_review_queue.csv": modern["queue_csv"],
        "modern_attribution_report.json": _json_bytes(modern["report"]),
        "modern_attribution_report.md": modern["report_md"].encode("utf-8"),
    }
    fingerprints = {name: _sha256(data) for name, data in sorted(files.items())}
    manifest = {"schema_version": EVIDENCE_MANIFEST_VERSION, "method_version": EVIDENCE_METHOD_VERSION, "generation": generation.to_dict(), "cutoff_utc": cutoff_utc, "input_sources": [{"logical_name": meta["logical_name"], "row_count": meta["row_count"], "fingerprint": meta["fingerprint"]} for _, meta in sorted(inputs.values(), key=lambda x: x[1]["logical_name"])], "input_status": "provided", **stats, "cohort_counts": dict(sorted(Counter(row["cohort_key"] for row in facts).items())), "evidence_basis_counts": dict(sorted(Counter(row["evidence_basis"] for row in facts).items())), "actual_link_confidence_counts": dict(sorted(Counter(row["actual_link_confidence"] or "blank" for row in facts if row["evidence_kind"] in {"actual_episode", "actual_link"}).items())), "output_fingerprints": fingerprints, "safety_boundary": SAFETY_BOUNDARY}
    manifest_pre = _json_bytes(manifest)
    run_id = "p_ev_" + _sha256(_json_bytes({"generation": generation.to_dict(), "cutoff_utc": cutoff_utc, "inputs": [(m["logical_name"], m["fingerprint"]) for _, m in sorted(inputs.values(), key=lambda x: x[1]["logical_name"])]}))[:32]
    manifest["run_id"] = run_id
    files["evidence_manifest.json"] = _json_bytes(manifest)
    return {name: files[name] for name in OUTPUT_NAMES}, {"run_id": run_id, "manifest": manifest, "modern": modern}

def write_bundle(output_root: str | Path, files: Mapping[str, bytes], run_id: str) -> None:
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    history = root / "history" / run_id
    if history.exists():
        for name, data in files.items():
            target = history / name
            if not target.is_file() or target.read_bytes() != data:
                raise EvidenceOutputConflict("history_identity_conflict")
    else:
        history.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=".history-", dir=str(history.parent)))
        try:
            for name, data in files.items(): (stage / name).write_bytes(data)
            os.replace(stage, history)
        finally:
            if stage.exists(): shutil.rmtree(stage, ignore_errors=True)
    latest_parent = root
    stage = Path(tempfile.mkdtemp(prefix=".latest-", dir=str(latest_parent)))
    backup = root / ".latest-backup"
    try:
        for name, data in files.items(): (stage / name).write_bytes(data)
        old = root / "latest"
        if backup.exists(): shutil.rmtree(backup)
        if old.exists(): os.replace(old, backup)
        os.replace(stage, old)
        if backup.exists(): shutil.rmtree(backup)
    except Exception:
        if (root / "latest").exists() and not stage.exists(): shutil.rmtree(root / "latest")
        if backup.exists() and not (root / "latest").exists(): os.replace(backup, root / "latest")
        raise
    finally:
        if stage.exists(): shutil.rmtree(stage, ignore_errors=True)
        if backup.exists(): shutil.rmtree(backup, ignore_errors=True)
