from __future__ import annotations

import json
from typing import Any, Mapping

P9_READINESS_SCHEMA_VERSION = "p9_readiness.v2"
P9_READINESS_METHOD_VERSION = "p9_readiness_evaluator.v2"
SAFETY_BOUNDARY = "report-only shadow / human approval required / no automatic tuning / no automatic order"

def _s(value: Any) -> str:
    return "" if value is None else str(value).strip()

def _scope(value: Mapping[str, Any] | None, classifier: str) -> dict[str, Any]:
    if value:
        return dict(value)
    return {"claim_id": "current_manual_operator_classifier_generation", "component_field": "classifier_version", "component_version": classifier, "required_segments": [], "minimum_requirements": {}, "threshold_status": "not_frozen"}

def _dimension(state: str, facts: Mapping[str, Any], missing: list[str], claim: Mapping[str, Any]) -> dict[str, Any]:
    return {"state": state, "facts": dict(facts), "missing_requirements": sorted(set(missing)), "claim_scope": dict(claim)}

def _legacy(trial_report: Mapping[str, Any]) -> dict[str, Any]:
    return dict(trial_report.get("p9_readiness", {}))

def evaluate_readiness(manifest: Mapping[str, Any], trial_report: Mapping[str, Any], cumulative_manifest: Mapping[str, Any], modern_report: Mapping[str, Any], claim_scope: Mapping[str, Any] | None = None, frozen_validation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    generation = manifest.get("generation", {})
    classifier = _s(generation.get("classifier_version"))
    scope = _scope(claim_scope, classifier)
    missing: list[str] = []
    cumulative_missing = list(manifest.get("cumulative_evidence_pointer", {}).get("missing_current_component_cohorts", []))
    current_cohorts = set(manifest.get("cumulative_evidence_pointer", {}).get("current_component_cohorts", []))
    cumulative_valid = manifest.get("cumulative_evidence_pointer", {}).get("compatibility_status") == "compatible"
    if not cumulative_valid:
        missing.append("compatible cumulative evidence manifest")
    missing.extend(cumulative_missing)
    for segment in scope.get("required_segments", []) or []:
        if segment not in manifest.get("cumulative_evidence_pointer", {}).get("available_segments", []): missing.append("required claim segment: " + _s(segment))
    actual_required = bool(scope.get("actual_required", False))
    accepted_actual = int(manifest.get("modern_attribution_pointer", {}).get("accepted_high_medium_actual", 0) or 0)
    if actual_required and accepted_actual == 0: missing.append("actual coverage for required claim")
    required_fingerprints = bool(manifest.get("cumulative_evidence_pointer", {}).get("fingerprints_present"))
    if not required_fingerprints: missing.append("cumulative evidence fingerprints")
    evidence_state = "baseline_available" if cumulative_valid and not cumulative_missing and all(segment in manifest.get("cumulative_evidence_pointer", {}).get("available_segments", []) for segment in scope.get("required_segments", []) or []) and (not actual_required or accepted_actual > 0) else ("collecting" if cumulative_valid else "blocked_data")
    if not required_fingerprints: evidence_state = "blocked_data"
    auto_claims = int(modern_report.get("causality_statement", {}).get("automatic_causal_claims", 0) or 0)
    replacement = modern_report.get("canonical_link_replacement") is True
    if not modern_report or auto_claims or replacement:
        usefulness_state = "blocked_data"
    elif accepted_actual > 0:
        usefulness_state = "baseline_available"
    else:
        usefulness_state = "collecting"
    op_state = "baseline_available" if manifest.get("operational_health", {}).get("state") == "healthy" else "blocked_data"
    proposal_missing: list[str] = []
    minimums = scope.get("minimum_requirements") or {}
    thresholds = scope.get("threshold_status", "not_frozen")
    supported = {"classification_cohort_rows_min", "proxy_trial_fact_cohort_rows_min", "accepted_high_medium_actual_min"}
    cohort_counts = manifest.get("cumulative_evidence_pointer", {}).get("cohort_counts", {})
    classification_rows = sum(int(value or 0) for key, value in cohort_counts.items() if "|classification|" in key and key.endswith(classifier))
    proxy_rows = sum(int(value or 0) for key, value in cohort_counts.items() if "|proxy_trial_fact|" in key and key.endswith(classifier))
    performance_basis = {"resolved_only_performance": True, "unresolved_rows_excluded": int(manifest.get("rolling_window", {}).get("counts", {}).get("unresolved_rows", 0) or 0), "no_ohlcv_rows_excluded": int(manifest.get("rolling_window", {}).get("counts", {}).get("no_ohlcv_rows", 0) or 0), "accepted_high_medium_actual": accepted_actual, "classification_cohort_rows": classification_rows, "proxy_trial_fact_cohort_rows": proxy_rows}
    if thresholds != "frozen_before_validation": proposal_missing.append("frozen proposal thresholds")
    if not minimums: proposal_missing.append("frozen validation cohort")
    if evidence_state == "collecting": proposal_missing.append("compatible current-generation evidence coverage")
    actual_by_key = {"classification_cohort_rows_min": classification_rows, "proxy_trial_fact_cohort_rows_min": proxy_rows, "accepted_high_medium_actual_min": accepted_actual}
    for key in sorted(minimums):
        value = minimums[key]
        if key not in supported:
            proposal_missing.append("unsupported minimum requirement: " + _s(key))
        elif not isinstance(value, int) or isinstance(value, bool) or value < 0:
            proposal_missing.append("invalid minimum requirement: " + key)
        elif actual_by_key[key] < value:
            proposal_missing.append(f"minimum not met: {key}={value}")
    proposal_state = "collecting"
    if thresholds == "frozen_before_validation" and minimums and evidence_state == "baseline_available" and not proposal_missing:
        proposal_state = "eligible_for_proposal"
    validation = frozen_validation or {}
    validation_status = _s(validation.get("validation_status"))
    if not validation:
        adoption_state = "collecting"
    elif validation_status in {"rejected", "failed"}:
        adoption_state = "rejected"
    elif validation_status == "in_progress" and all(validation.get(key) is True for key in ("generation_compatible", "cohort_compatible", "time_split", "claim_scope_match")):
        adoption_state = "shadow_validating"
    elif validation_status == "passed" and proposal_state == "eligible_for_proposal" and all(validation.get(key) is True for key in ("generation_compatible", "cohort_compatible", "time_split", "claim_scope_match", "versions_frozen_before_validation", "thresholds_frozen_before_validation")):
        adoption_state = "human_approval_required"
    else:
        adoption_state = "collecting"
    dimensions = {
        "operational_health": _dimension(op_state, {"daily_state": manifest.get("operational_health", {}).get("state")}, [] if op_state == "baseline_available" else ["daily operational health"], scope),
        "evidence_coverage": _dimension(evidence_state, {"current_classifier_version": classifier, "current_component_cohorts": sorted(current_cohorts)}, missing, scope),
        "notification_usefulness": _dimension(usefulness_state, {"accepted_high_medium_actual": accepted_actual, "automatic_causal_claims": auto_claims}, ["valid modern attribution report"] if usefulness_state == "blocked_data" else [], scope),
        "proposal_eligibility": _dimension(proposal_state, {"threshold_status": thresholds, "minimum_requirements": minimums, "performance_basis": performance_basis}, proposal_missing, scope),
        "adoption_readiness": _dimension(adoption_state, {"validation_status": validation_status or "not_started"}, [] if adoption_state == "human_approval_required" else ["frozen validation input"], scope),
    }
    if any(d["state"] == "blocked_data" for d in dimensions.values()): top = "blocked_data"
    elif validation_status in {"rejected", "failed"}: top = "rejected"
    elif adoption_state == "human_approval_required": top = "human_approval_required"
    elif adoption_state == "shadow_validating": top = "shadow_validating"
    elif proposal_state == "eligible_for_proposal": top = "eligible_for_proposal"
    elif evidence_state == "baseline_available" and usefulness_state == "baseline_available": top = "baseline_available"
    else: top = "collecting"
    return {"schema_version": P9_READINESS_SCHEMA_VERSION, "method_version": P9_READINESS_METHOD_VERSION, "state": top, "dimensions": dimensions, "missing_requirements": sorted(set(missing + proposal_missing)), "claim_scope": scope, "legacy_readiness_v1": _legacy(trial_report), "migration": {"legacy_thresholds_not_v2": True, "daily_window_is_not_cumulative": True, "current_classifier_version": classifier, "cumulative_classifier_versions": sorted({key.rsplit("|", 1)[-1] for key in manifest.get("cumulative_evidence_pointer", {}).get("cohort_counts", {}) if "|classification|" in key}), "global_all_four_class_requirement_removed": True, "practical_false_constant_replaced_by_state_machine": True, "human_approval_required": True}, "production_ready": False, "proposal_approval_status": "not_requested", "safety_boundary": SAFETY_BOUNDARY}
