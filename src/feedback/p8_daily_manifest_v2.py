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
from typing import Any, Mapping

from src.contracts.generation_identity import GenerationIdentity, compare_generation_identities
from src.contracts.operator_semantics import classify_no_trade_tokens
from src.feedback.p9_readiness_v2 import evaluate_readiness

P8_DAILY_MANIFEST_SCHEMA_VERSION = "p8_daily_manifest.v2"
P8_DAILY_MANIFEST_METHOD_VERSION = "p8_daily_manifest_builder.v2"
OUTPUT_NAMES = ("p8_daily_manifest_v2.json", "p8_daily_summary_v2.md", "p9_readiness_v2.json", "p9_readiness_migration_report.md")
SAFETY_BOUNDARY = "report-only shadow / no schedule or notification change / no readiness adoption / no automatic order / human decides manually"

class InputError(ValueError): pass
class IdentityConflict(ValueError): pass
class OutputConflict(OSError): pass

def _s(v: Any) -> str: return "" if v is None else str(v).strip()
def _json(v: Any) -> bytes: return (json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
def _sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def _utc(value: str) -> datetime:
    try: d = datetime.fromisoformat(_s(value).replace("Z", "+00:00"))
    except ValueError as exc: raise InputError("invalid_cutoff_utc") from exc
    if d.tzinfo is None: raise InputError("naive_cutoff_utc")
    return d.astimezone(timezone.utc)
def read_json(path: str | Path, logical: str) -> tuple[dict[str, Any], dict[str, Any]]:
    p = Path(path)
    if not p.is_file(): raise InputError("missing_input")
    try: raw = p.read_bytes(); value = json.loads(raw.decode())
    except (OSError, UnicodeError, json.JSONDecodeError) as exc: raise InputError("invalid_input") from exc
    if not isinstance(value, dict): raise InputError("invalid_input")
    return value, {"logical_name": logical, "fingerprint": _sha(raw)}
def read_csv(path: str | Path, logical: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    p = Path(path)
    if not p.is_file(): raise InputError("missing_input")
    try:
        raw = p.read_bytes(); text = raw.decode(); rows = list(csv.DictReader(text.splitlines()))
    except (OSError, UnicodeError, csv.Error) as exc: raise InputError("invalid_input") from exc
    if not rows and not text.strip(): raise InputError("invalid_input")
    return [dict(row) for row in rows], {"logical_name": logical, "fingerprint": _sha(raw), "row_count": len(rows)}
def _identity_rows(rows: list[Mapping[str, Any]], field: str) -> list[str]:
    seen: dict[str, tuple[str, ...]] = {}; result = []
    for row in rows:
        identity = _s(row.get(field))
        if not identity: continue
        payload = tuple(_s(row.get(k)) for k in sorted(row) if k != field)
        if identity in seen and seen[identity] != payload: raise IdentityConflict("identity_conflict")
        if identity not in seen: seen[identity] = payload; result.append(identity)
    return sorted(set(result))
def _generation(report: Mapping[str, Any], runtime: str, source: str, cutoff: str) -> GenerationIdentity:
    classifier = _s(report.get("classifier_method_version")); method = _s(report.get("method_version"))
    if not classifier: raise InputError("missing_classifier_method_version")
    if not method: raise InputError("missing_trial_method_version")
    return GenerationIdentity(program="P", runtime_generation=runtime, source_head=source, schema_version=P8_DAILY_MANIFEST_SCHEMA_VERSION, method_version=P8_DAILY_MANIFEST_METHOD_VERSION, cutoff_utc=cutoff, classifier_version=classifier, p8_evidence_version=method, readiness_version="p9_readiness.v2")
def _previous(value: Mapping[str, Any]) -> GenerationIdentity:
    try: return GenerationIdentity(**value["generation"])
    except (KeyError, TypeError, ValueError) as exc: raise InputError("invalid_previous_v2_manifest") from exc
def _actual_ids(rows: list[Mapping[str, Any]]) -> list[str]:
    return sorted({ _s(row.get("actual_episode_id")) for row in rows if _s(row.get("evidence_tier")) == "actual_high_medium" and _s(row.get("actual_episode_id")) and _s(row.get("actual_link_confidence")).lower() in {"high", "medium"} })
def _token_status(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    hard: set[str] = set(); advisory: set[str] = set(); unknown: set[str] = set(); unknown_rows = 0
    for row in rows:
        result = classify_no_trade_tokens(row.get("no_trade_flags", "")); hard.update(result.hard_tokens); advisory.update(result.advisory_tokens); unknown.update(result.unknown_tokens); unknown_rows += bool(result.unknown_tokens)
    return {"hard_tokens": sorted(hard), "advisory_tokens": sorted(advisory), "unknown_tokens": sorted(unknown), "rows_with_unknown_tokens": unknown_rows}
def _health(cycle: Mapping[str, Any], trial: Mapping[str, Any], facts: list[Mapping[str, Any]]) -> dict[str, Any]:
    stages = cycle.get("stage_statuses", {}); core = ("candidate_slice", "signal_context_slice", "intraperiod_outcomes", "p4", "p5", "p8")
    warnings = []
    for auxiliary in ("turning_precursor_shadow", "macro_structure_shadow"):
        if _s(cycle.get(auxiliary, {}).get("status")) not in {"", "success", "ok"}: warnings.append(auxiliary + "_not_core_blocker")
    counts = cycle.get("counts", {}); source = cycle.get("source", {})
    valid_counts = all(isinstance(counts.get(key), int) and counts.get(key) >= 0 for key in ("trial_fact_rows", "resolved_rows", "unresolved_rows", "review_queue_size", "no_ohlcv_rows"))
    healthy = bool(_s(cycle.get("schema_version")) and _s(cycle.get("method_version")) and _s(cycle.get("report_date")) and all(stages.get(k) == "ok" for k in core) and source.get("ohlcv_freshness") == "valid" and source.get("interval") == "15m" and cycle.get("no_automatic_tuning") is True and trial.get("ok") is True and valid_counts and all(_s(v) for v in cycle.get("input_fingerprints", {}).values()))
    return {"state": "healthy" if healthy else "failed", "core_stage_statuses": {key: stages.get(key, "") for key in core}, "auxiliary_warnings": sorted(warnings), "checks": {"ohlcv_freshness": source.get("ohlcv_freshness"), "interval": source.get("interval"), "no_automatic_tuning": cycle.get("no_automatic_tuning"), "trial_report_ok": trial.get("ok"), "required_counts_nonnegative": valid_counts}}
def _delta(current: list[str], previous: list[str] | None, first: bool) -> dict[str, list[str]]:
    if first: return {"new": [], "backlog": sorted(current), "resolved": [], "expired": []}
    old = set(previous or []); now = set(current)
    return {"new": sorted(now-old), "backlog": sorted(now & old), "resolved": sorted(old-now), "expired": []}
def _cumulative_pointer(cumulative: Mapping[str, Any], generation: GenerationIdentity, cutoff: datetime, modern: Mapping[str, Any]) -> dict[str, Any]:
    gen = cumulative.get("generation", {}); cohorts = cumulative.get("cohort_counts", {}); needed = [f"P|{generation.runtime_generation}|classification|{generation.classifier_version}", f"P|{generation.runtime_generation}|proxy_trial_fact|{generation.classifier_version}"]
    missing = sorted(set(needed) - set(cohorts)); declared = _s(gen.get("classifier_version")); mismatch = declared != generation.classifier_version and any(f"|{declared}" in key for key in cohorts)
    compatible = gen.get("program") == generation.program and gen.get("runtime_generation") == generation.runtime_generation and cumulative.get("input_status") == "provided" and _s(cumulative.get("run_id")) and _s(cumulative.get("cutoff_utc")) and _utc(cumulative["cutoff_utc"]) <= cutoff and bool(cumulative.get("input_sources")) and bool(cumulative.get("output_fingerprints"))
    return {"logical_name": "accepted_cumulative_evidence_manifest.json", "fingerprint": "", "run_id": cumulative.get("run_id", ""), "schema_version": cumulative.get("schema_version", ""), "method_version": cumulative.get("method_version", ""), "cutoff_utc": cumulative.get("cutoff_utc", ""), "program": gen.get("program", ""), "runtime_generation": gen.get("runtime_generation", ""), "row_counts": cumulative.get("row_counts", {}), "cohort_counts": cohorts, "compatibility_status": "compatible" if compatible else "incompatible", "missing_current_component_cohorts": missing, "current_component_cohorts": sorted(set(needed) - set(missing)), "declared_component_cohort_mismatch": bool(mismatch), "available_segments": [], "fingerprints_present": bool(cumulative.get("input_sources")) and bool(cumulative.get("output_fingerprints"))}
def build_manifest(cycle: Mapping[str, Any], trial: Mapping[str, Any], facts: list[Mapping[str, Any]], queue: list[Mapping[str, Any]], cumulative: Mapping[str, Any], modern: Mapping[str, Any], runtime: str, source: str, cutoff: str, previous: Mapping[str, Any] | None = None, claim_scope: Mapping[str, Any] | None = None, frozen_validation: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    cutoff_dt = _utc(cutoff); generation = _generation(trial, runtime, source, cutoff); health = _health(cycle, trial, facts); current_queue = _identity_rows(queue, "review_item_id"); current_actual = _actual_ids(facts); first = previous is None; comparison = {"status": "first_v2_baseline", "comparable": True, "baseline_reset_required": False, "reason_codes": ()} if first else None
    if previous is not None:
        comparison_obj = compare_generation_identities(_previous(previous), generation, claim_component="classifier_version"); comparison = comparison_obj.to_dict()
    comparable = bool(comparison.get("comparable"))
    qdelta = _delta(current_queue, previous.get("review_queue_delta", {}).get("current_ids", []) if previous else None, first) if comparable else {"new": [], "backlog": current_queue, "resolved": [], "expired": []}
    adelta = _delta(current_actual, previous.get("actual_attribution_delta", {}).get("current_ids", []) if previous else None, first) if comparable else {"new": [], "backlog": [], "resolved": [], "expired": []}
    if not first and not comparable: adelta = {"new": [], "retained": [], "lost": []}
    else: adelta = {"new": adelta["new"], "retained": adelta["backlog"], "lost": adelta["resolved"]}
    cumulative_pointer = _cumulative_pointer(cumulative, generation, cutoff_dt, modern)
    modern_pointer = {"logical_name": "modern_attribution_report.json", "fingerprint": cumulative.get("output_fingerprints", {}).get("modern_attribution_report.json", ""), "baseline_episodes": int(modern.get("baseline_episodes", 0) or 0), "baseline_links": int(modern.get("baseline_links", 0) or 0), "accepted_high_medium_actual": int(modern.get("actual_attribution", {}).get("accepted_high_medium", 0) or 0), "automatic_causal_claims": int(modern.get("causality_statement", {}).get("automatic_causal_claims", 0) or 0), "canonical_link_replacement": modern.get("canonical_link_replacement", False)}
    issue = trial.get("global_stop_opportunity", {}) or {}; issue_status = "not_comparable_generation_change" if not comparable else ("not_applicable_no_stop_population" if int(issue.get("stop_rows", 0) or 0) == 0 else ("applicable_evidence_present" if int(issue.get("issue_001_qualified_rows", 0) or 0) > 0 else "applicable_no_qualified_rows"))
    tokens = _token_status(facts)
    meaningful = []
    if not comparable and not first: meaningful.append({"type":"generation_baseline_reset","reason_codes":comparison.get("reason_codes", [])})
    if not health["state"] == "healthy": meaningful.append({"type":"operational_health_failure"})
    meaningful += [{"type":"new_accepted_actual_episode","episode_id":x} for x in adelta["new"]] + [{"type":"lost_accepted_actual_episode","episode_id":x} for x in adelta["lost"]] + [{"type":"new_review_item","review_item_id":x} for x in qdelta["new"]] + [{"type":"resolved_review_item","review_item_id":x} for x in qdelta["resolved"]] + ([{"type":"unknown_semantic_token","token":x} for x in tokens["unknown_tokens"]])
    manifest = {"schema_version": P8_DAILY_MANIFEST_SCHEMA_VERSION, "method_version": P8_DAILY_MANIFEST_METHOD_VERSION, "report_date": _s(cycle.get("report_date")) or _s(trial.get("report_date")), "cutoff_utc": generation.cutoff_utc, "generation": generation.to_dict(), "operational_health": health, "rolling_window": {"report_date": _s(cycle.get("report_date")), "daily_only": True}, "generation_comparison": comparison, "daily_delta": {"current_actual_ids": current_actual, "current_review_ids": current_queue}, "review_queue_delta": {**qdelta, "current_ids": current_queue}, "actual_attribution_delta": {**adelta, "current_ids": current_actual}, "semantic_token_status": tokens, "cumulative_evidence_pointer": cumulative_pointer, "modern_attribution_pointer": modern_pointer, "issue_applicability": {"issue_001": issue_status}, "legacy_readiness_v1": trial.get("p9_readiness", {}), "p9_readiness_v2": {}, "meaningful_changes": meaningful, "input_sources": {"cycle_manifest":"cycle_manifest.json","trial_report":"manual_operator_trial_evidence.json","trial_facts":"manual_operator_trial_facts.csv","review_queue":"manual_operator_trial_review_queue.csv"}, "input_fingerprints": cycle.get("input_fingerprints", {}), "output_fingerprints": {}, "safety_boundary": SAFETY_BOUNDARY}
    readiness = evaluate_readiness(manifest, trial, cumulative, modern, claim_scope, frozen_validation); manifest["p9_readiness_v2"] = readiness
    run_id = "p8m2_" + _sha(_json({"generation": generation.to_dict(), "cutoff_utc": generation.cutoff_utc, "inputs": sorted(manifest["input_fingerprints"].items())}))[:32]; manifest["run_id"] = run_id
    summary = "\n".join(("# P8 daily manifest v2 summary", "", f"- Full daily shadow report date: `{manifest['report_date']}`.", f"- Operational health: `{health['state']}`.", f"- Generation comparison: `{comparison['status']}`.", f"- Queue backlog: {len(qdelta['backlog'])}; backlog is not a meaningful change.", f"- Accepted actual retained: {len(adelta['retained'])}.", f"- ISSUE-001: `{issue_status}`.", "- Daily evidence and cumulative evidence remain separate.", "- Report-only shadow; no readiness adoption or automatic order.", ""))
    migration = "\n".join(("# P9 readiness v2 migration report", "", "- Legacy readiness v1 is copied unchanged and is not a v2 threshold.", f"- v2 state: `{readiness['state']}`.", "- Daily window is distinct from cumulative evidence.", f"- Current classifier: `{generation.classifier_version}`; cumulative cohort gap is explicit.", "- Global all-four-class requirement is not imposed.", "- Practical false is replaced by a state-machine report.", "- Human approval remains required; no automatic tuning or order.", ""))
    summary_bytes = summary.encode(); readiness_bytes = _json(readiness); migration_bytes = migration.encode()
    manifest["output_fingerprints"] = {"p8_daily_summary_v2.md": _sha(summary_bytes), "p9_readiness_v2.json": _sha(readiness_bytes), "p9_readiness_migration_report.md": _sha(migration_bytes)}
    return manifest, {"p8_daily_manifest_v2.json": _json(manifest), "p8_daily_summary_v2.md": summary_bytes, "p9_readiness_v2.json": readiness_bytes, "p9_readiness_migration_report.md": migration_bytes}
def write_outputs(root: str | Path, files: Mapping[str, bytes], replace: bool = False) -> None:
    dest = Path(root); dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not replace: raise OutputConflict("output_exists")
    stage = Path(tempfile.mkdtemp(prefix=".p8v2-", dir=str(dest.parent))); backup = dest.parent / (dest.name + ".backup")
    try:
        for name, data in files.items(): (stage / name).write_bytes(data)
        if dest.exists(): os.replace(dest, backup)
        os.replace(stage, dest)
        if backup.exists(): shutil.rmtree(backup)
    except Exception:
        if dest.exists() and not stage.exists(): shutil.rmtree(dest)
        if backup.exists() and not dest.exists(): os.replace(backup, dest)
        raise
    finally:
        if stage.exists(): shutil.rmtree(stage, ignore_errors=True)
        if backup.exists(): shutil.rmtree(backup, ignore_errors=True)
