from __future__ import annotations

import math
from typing import Any, Mapping

P9_READINESS_SCHEMA_VERSION = "p9_readiness.v2"
P9_READINESS_METHOD_VERSION = "p9_readiness_evaluator.v2"
SAFETY_BOUNDARY = "report-only shadow / human approval required / no automatic tuning / no automatic order"
SUPPORTED_MINIMUMS = {
    "classification_cohort_rows_min", "proxy_trial_fact_cohort_rows_min", "accepted_high_medium_actual_min",
    "accepted_actual_associations_min", "notified_accepted_actual_min", "human_confirmed_usefulness_min",
    "metadata_complete_notified_actual_min", "operator_direction_match_rate_min", "ambiguous_notified_actual_rate_max",
}
COUNT_KEYS = {key for key in SUPPORTED_MINIMUMS if key.endswith("_min") and not key.endswith("_rate_min") and not key.endswith("_rate_max")}
RATE_KEYS = {"operator_direction_match_rate_min", "ambiguous_notified_actual_rate_max"}


def _s(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _scope(value: Mapping[str, Any] | None, classifier: str) -> dict[str, Any]:
    if value:
        result = dict(value)
        result.setdefault("minimum_requirements", {})
        result.setdefault("threshold_status", "not_frozen")
        result.setdefault("required_segments", [])
        return result
    return {"claim_id": "current_manual_operator_classifier_generation", "component_field": "classifier_version", "component_version": classifier, "required_segments": [], "minimum_requirements": {}, "threshold_status": "not_frozen"}


def _dimension(state: str, facts: Mapping[str, Any], missing: list[str], claim: Mapping[str, Any]) -> dict[str, Any]:
    return {"state": state, "facts": dict(facts), "missing_requirements": sorted(set(missing)), "claim_scope": dict(claim)}


def _legacy(trial_report: Mapping[str, Any]) -> dict[str, Any]:
    return dict(trial_report.get("p9_readiness", {}))


def _modern_facts(report: Mapping[str, Any]) -> dict[str, Any]:
    actual = dict(report.get("actual_attribution", {}))
    if "accepted_high_medium" not in actual and "accepted_high_medium_actual_associations" not in actual:
        actual["accepted_high_medium"] = report.get("accepted_high_medium_actual", 0)
    return {
        "accepted_actual_associations": int(actual.get("accepted_high_medium_actual_associations", actual.get("accepted_high_medium", 0)) or 0),
        "notified_accepted_actual": int(actual.get("notified_accepted_actual_associations", 0) or 0),
        "unknown_notification_status": int(actual.get("unknown_notification_status_accepted_actual_associations", 0) or 0),
        "human_confirmed": int(actual.get("human_confirmed_usefulness_count", 0) or 0),
        "metadata_complete": int(actual.get("metadata_complete_notified_actual_count", 0) or 0),
        "direction_match_rate": report.get("operator_direction", {}).get("operator_direction_match_rate"),
        "ambiguous_rate": report.get("notification_usefulness", {}).get("ambiguous_notified_actual_rate", report.get("ambiguous_notified_actual_rate")),
    }


def _numeric_requirements(minimums: Mapping[str, Any], facts: Mapping[str, Any]) -> tuple[list[str], bool]:
    missing: list[str] = []
    invalid = False
    actual = {
        "classification_cohort_rows_min": facts.get("classification_cohort_rows", 0),
        "proxy_trial_fact_cohort_rows_min": facts.get("proxy_trial_fact_cohort_rows", 0),
        "accepted_high_medium_actual_min": facts.get("accepted_actual_associations", 0),
        "accepted_actual_associations_min": facts.get("accepted_actual_associations", 0),
        "notified_accepted_actual_min": facts.get("notified_accepted_actual", 0),
        "human_confirmed_usefulness_min": facts.get("human_confirmed", 0),
        "metadata_complete_notified_actual_min": facts.get("metadata_complete", 0),
        "operator_direction_match_rate_min": facts.get("direction_match_rate"),
        "ambiguous_notified_actual_rate_max": facts.get("ambiguous_rate"),
    }
    for key in sorted(minimums):
        value = minimums[key]
        if key not in SUPPORTED_MINIMUMS:
            missing.append("unsupported minimum requirement: " + _s(key)); invalid = True; continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            missing.append("invalid minimum requirement: " + key); invalid = True; continue
        if key in COUNT_KEYS and (not isinstance(value, int) or value < 0):
            missing.append("invalid minimum requirement: " + key); invalid = True; continue
        if key in RATE_KEYS and not (0 <= float(value) <= 1):
            missing.append("invalid minimum requirement: " + key); invalid = True; continue
        observed = actual[key]
        if observed is None:
            missing.append("minimum not met: " + key); continue
        if key.endswith("_max") and float(observed) > float(value): missing.append(f"maximum not met: {key}={value}")
        elif key.endswith("_min") and float(observed) < float(value): missing.append(f"minimum not met: {key}={value}")
    return missing, invalid


def evaluate_readiness(manifest: Mapping[str, Any], trial_report: Mapping[str, Any], cumulative_manifest: Mapping[str, Any], modern_report: Mapping[str, Any], claim_scope: Mapping[str, Any] | None = None, frozen_validation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    generation = manifest.get("generation", {})
    classifier = _s(generation.get("classifier_version"))
    scope = _scope(claim_scope, classifier)
    pointer = manifest.get("cumulative_evidence_pointer", {})
    cohort_counts = pointer.get("cohort_counts", {})
    current_class_rows = sum(int(v or 0) for k, v in cohort_counts.items() if "|classification|" in k and k.endswith(classifier))
    current_proxy_rows = sum(int(v or 0) for k, v in cohort_counts.items() if "|proxy_trial_fact|" in k and k.endswith(classifier))
    missing_evidence: list[str] = []
    if pointer.get("compatibility_status") != "compatible": missing_evidence.append("compatible cumulative evidence manifest")
    missing_evidence.extend(pointer.get("missing_current_component_cohorts", []))
    required_segments = scope.get("required_segments", []) or []
    available_segments = pointer.get("available_segments", []) or []
    missing_evidence.extend("required claim segment: " + _s(x) for x in required_segments if x not in available_segments)
    if not pointer.get("fingerprints_present", True): missing_evidence.append("cumulative evidence fingerprints")
    actual = _modern_facts(modern_report)
    report_actual = modern_report.get("actual_attribution", {})
    actual["classification_cohort_rows"] = current_class_rows
    actual["proxy_trial_fact_cohort_rows"] = current_proxy_rows
    actual_required = bool(scope.get("actual_required", False))
    if actual_required and actual["accepted_actual_associations"] == 0: missing_evidence.append("actual coverage for required claim")
    evidence_state = "baseline_available" if not missing_evidence and (not actual_required or actual["accepted_actual_associations"] > 0) else "collecting"
    if pointer.get("compatibility_status") != "compatible" or not pointer.get("fingerprints_present", True): evidence_state = "blocked_data"
    auto_claims = int(modern_report.get("causality_statement", {}).get("automatic_causal_claims", 0) or 0)
    replacement = modern_report.get("canonical_link_replacement") is True
    modern_valid = bool(modern_report) and not auto_claims and not replacement
    association_state = "baseline_available" if actual["accepted_actual_associations"] > 0 and modern_valid else "collecting" if modern_valid else "blocked_data"
    usefulness_state = "blocked_data" if not modern_valid else "collecting" if actual["notified_accepted_actual"] == 0 else "baseline_available"
    if not modern_valid: missing_evidence.append("valid modern attribution report")
    operational_state = "baseline_available" if manifest.get("operational_health", {}).get("state") == "healthy" else "blocked_data"
    minimums = scope.get("minimum_requirements") or {}
    performance = {"resolved_only_performance": True, "unresolved_rows_excluded": int(manifest.get("rolling_window", {}).get("counts", {}).get("unresolved_rows", 0) or 0), "no_ohlcv_rows_excluded": int(manifest.get("rolling_window", {}).get("counts", {}).get("no_ohlcv_rows", 0) or 0), **actual}
    proposal_missing, invalid_minimum = _numeric_requirements(minimums, actual)
    thresholds = scope.get("threshold_status", "not_frozen")
    if thresholds != "frozen_before_validation": proposal_missing.append("frozen proposal thresholds")
    if not minimums: proposal_missing.append("frozen validation cohort")
    if evidence_state != "baseline_available": proposal_missing.append("compatible current-generation evidence coverage")
    proposal_state = "eligible_for_proposal" if thresholds == "frozen_before_validation" and bool(minimums) and not proposal_missing and not invalid_minimum and evidence_state == "baseline_available" else "collecting"
    validation = frozen_validation or {}
    validation_status = _s(validation.get("validation_status"))
    compatibility = all(validation.get(k) is True for k in ("generation_compatible", "cohort_compatible", "time_split", "claim_scope_match"))
    adoption_state = "rejected" if validation_status in {"rejected", "failed"} else "shadow_validating" if validation_status == "in_progress" and compatibility else "human_approval_required" if validation_status == "passed" and proposal_state == "eligible_for_proposal" and compatibility and validation.get("versions_frozen_before_validation") is True and validation.get("thresholds_frozen_before_validation") is True else "collecting"
    dimensions = {
        "operational_health": _dimension(operational_state, {"daily_state": manifest.get("operational_health", {}).get("state")}, [] if operational_state == "baseline_available" else ["daily operational health"], scope),
        "evidence_coverage": _dimension(evidence_state, {"current_classifier_version": classifier, "current_component_cohorts": sorted(pointer.get("current_component_cohorts", []))}, missing_evidence, scope),
        "actual_association_coverage": _dimension(association_state, {"accepted_actual_associations": actual["accepted_actual_associations"], "actual_proxy_separation": True}, [], scope),
        "notification_usefulness": _dimension(usefulness_state, {"accepted_actual_associations": actual["accepted_actual_associations"], "notified_accepted_actual": actual["notified_accepted_actual"], "unknown_notification_status": actual["unknown_notification_status"], "human_confirmed_usefulness": actual["human_confirmed"], "metadata_complete_notified_actual": actual["metadata_complete"], "operator_direction_match_rate": actual["direction_match_rate"], "ambiguous_notified_actual_rate": actual["ambiguous_rate"]}, ["notified accepted actual evidence"] if usefulness_state == "collecting" else [], scope),
        "proposal_eligibility": _dimension(proposal_state, {"threshold_status": thresholds, "minimum_requirements": minimums, "performance_basis": performance}, proposal_missing, scope),
        "adoption_readiness": _dimension(adoption_state, {"validation_status": validation_status or "not_started", "generation_compatible": validation.get("generation_compatible"), "cohort_compatible": validation.get("cohort_compatible"), "time_split": validation.get("time_split"), "claim_scope_match": validation.get("claim_scope_match")}, [] if adoption_state == "human_approval_required" else ["frozen validation input"], scope),
    }
    if any(dim["state"] == "blocked_data" for dim in dimensions.values()): top = "blocked_data"
    elif adoption_state == "rejected": top = "rejected"
    elif adoption_state == "human_approval_required": top = "human_approval_required"
    elif adoption_state == "shadow_validating": top = "shadow_validating"
    elif proposal_state == "eligible_for_proposal": top = "eligible_for_proposal"
    elif evidence_state == "baseline_available" and usefulness_state == "baseline_available": top = "baseline_available"
    else: top = "collecting"
    return {"schema_version": P9_READINESS_SCHEMA_VERSION, "method_version": P9_READINESS_METHOD_VERSION, "state": top, "dimensions": dimensions, "missing_requirements": sorted(set(missing_evidence + proposal_missing)), "claim_scope": scope, "legacy_readiness_v1": _legacy(trial_report), "migration": {"legacy_thresholds_not_v2": True, "daily_window_is_not_cumulative": True, "current_classifier_version": classifier, "cumulative_classifier_versions": sorted({key.rsplit("|", 1)[-1] for key in cohort_counts if "|classification|" in key}), "global_all_four_class_requirement_removed": True, "practical_false_constant_replaced_by_state_machine": True, "human_approval_required": True}, "production_ready": False, "proposal_approval_status": "not_requested", "safety_boundary": SAFETY_BOUNDARY}
