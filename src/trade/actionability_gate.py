from __future__ import annotations

from typing import Any


ACTIONABILITY_SAFETY = "report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually"


def compute_actionability_gate_v1(
    *,
    active_plan_label: str,
    source_readiness: str,
    pending_caveat: str,
    side: str,
    entry_mode: str,
    tp_plan: str,
    sl_or_invalidation: str,
    timeout_or_wait_limit: str,
) -> dict[str, Any]:
    normalized_label = str(active_plan_label).strip()
    normalized_source_readiness = str(source_readiness).strip()
    normalized_pending_caveat = str(pending_caveat).strip()
    context_fields = (
        str(side).strip(),
        str(entry_mode).strip(),
        str(tp_plan).strip(),
        str(sl_or_invalidation).strip(),
        str(timeout_or_wait_limit).strip(),
    )

    if normalized_label == "NO_ACTION":
        return {
            "actionability_label": "NO_ACTION",
            "actionability_reasons": ["active_plan_no_action"],
            "human_action": "do_nothing",
            "actionability_safety": ACTIONABILITY_SAFETY,
        }
    if normalized_source_readiness != "ready":
        return {
            "actionability_label": "AUTO_REJECT",
            "actionability_reasons": [f"source_not_ready:{normalized_source_readiness or 'unknown'}"],
            "human_action": "do_nothing",
            "actionability_safety": ACTIONABILITY_SAFETY,
        }
    if (
        "diagnostic=no_intraperiod_evidence" in normalized_pending_caveat
        or "action=do_not_use_as_trade_trigger" in normalized_pending_caveat
    ):
        return {
            "actionability_label": "AUTO_REJECT",
            "actionability_reasons": ["no_intraperiod_evidence"],
            "human_action": "do_nothing",
            "actionability_safety": ACTIONABILITY_SAFETY,
        }
    if normalized_label == "NO_ACTION_REVIEW_REQUIRED":
        return {
            "actionability_label": "REVIEW_REQUIRED",
            "actionability_reasons": ["no_action_review_required"],
            "human_action": "review_only",
            "actionability_safety": ACTIONABILITY_SAFETY,
        }
    if any("review_required" in field for field in context_fields):
        return {
            "actionability_label": "REVIEW_REQUIRED",
            "actionability_reasons": ["manual_context_review_required"],
            "human_action": "review_only",
            "actionability_safety": ACTIONABILITY_SAFETY,
        }
    if "action=reduce_confidence" in normalized_pending_caveat:
        return {
            "actionability_label": "REVIEW_REQUIRED",
            "actionability_reasons": ["pending_coverage_review_required"],
            "human_action": "review_only",
            "actionability_safety": ACTIONABILITY_SAFETY,
        }
    if normalized_label.startswith("ACTIVE_"):
        return {
            "actionability_label": "ACTIONABLE_COPY_READY",
            "actionability_reasons": ["deterministic_checks_passed"],
            "human_action": "manual_copy_review",
            "actionability_safety": ACTIONABILITY_SAFETY,
        }
    return {
        "actionability_label": "REVIEW_REQUIRED",
        "actionability_reasons": ["unknown_active_plan_label"],
        "human_action": "review_only",
        "actionability_safety": ACTIONABILITY_SAFETY,
    }
