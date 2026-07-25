from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from typing import Any, Iterable, Mapping

MODERN_ATTRIBUTION_SCHEMA_VERSION = "manual_trade_modern_attribution.v1"
MODERN_LINK_CANDIDATE_VERSION = "manual_trade_signal_attribution_candidate.v3"

CANDIDATE_HEADERS = ("schema_version", "candidate_id", "baseline_link_id", "episode_id", "signal_id", "baseline_link_status", "baseline_link_confidence", "baseline_link_reason", "reason_bucket", "candidate_relation", "notification_kind", "was_notified", "notify_reason_codes", "operator_decision_state", "operator_primary_side", "formal_execution_gate", "formal_blockers", "active_primary_action", "side_aware_primary_class", "side_aware_primary_state", "structural_priority_side", "structural_alignment_state", "modern_metadata_status", "human_basis", "causality_status")
LEDGER_HEADERS = ("schema_version", "ledger_id", "ledger_basis", "signal_id", "episode_id", "notification_kind", "was_notified", "modern_metadata_status", "notify_reason_codes", "operator_decision_state", "operator_primary_side", "formal_execution_gate", "formal_blockers", "p5_operator_classes", "active_primary_action", "side_aware_primary_class", "side_aware_primary_state", "structural_priority_side", "structural_alignment_state", "proxy_outcomes", "actual_link_confidence", "actual_position_side", "entry_latency_minutes", "actual_realized_pnl", "usefulness_category", "human_basis", "causality_status")
QUEUE_HEADERS = ("schema_version", "review_item_id", "question_type", "baseline_link_id", "episode_id", "signal_id", "reason_bucket", "modern_metadata_status", "usefulness_category", "question", "human_basis", "causality_status")
MODERN_FIELDS = ("was_notified", "notify_reason_codes", "notification_kind", "reason_for_notification", "summary_variant", "advice_variant", "trade_execution_gate", "trade_execution_blockers", "active_primary_action", "side_aware_primary_side", "side_aware_primary_class", "side_aware_primary_state", "structural_priority_side", "structural_alignment_state", "operator_decision_state", "operator_decision_primary_side", "followup_for_signal_id")

def _s(value: Any) -> str: return "" if value is None else str(value).strip()
def _hash(*values: Any) -> str: return hashlib.sha256("|".join(_s(v) for v in values).encode()).hexdigest()
def _truth(value: Any) -> str:
    text = _s(value).lower()
    if text in {"1", "true", "yes", "y", "通知", "あり"}: return "true"
    if text in {"0", "false", "no", "n", "未通知", "なし"}: return "false"
    return "unknown" if text else ""
def _csv(headers: Iterable[str], rows: list[Mapping[str, Any]]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(headers), lineterminator="\n")
    writer.writeheader()
    for row in rows: writer.writerow({key: _s(row.get(key)) for key in headers})
    return out.getvalue().encode()
def _metadata(rows: list[Mapping[str, Any]]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        signal = _s(row.get("signal_id"))
        if not signal: continue
        selected = {field: _s(row.get(field)) for field in MODERN_FIELDS}
        selected["human_basis"] = _s(row.get("human_basis"))
        old = indexed.get(signal)
        if old is None: indexed[signal] = selected; continue
        for field, value in selected.items():
            if value and old[field] and value != old[field]: raise ValueError("signal_identity_conflict")
            if value and not old[field]: old[field] = value
    return indexed
def _notification(row: Mapping[str, Any], fallback: Mapping[str, Any] | None = None) -> str:
    for field in ("notification_kind", "summary_variant", "reason_for_notification"):
        value = _s(row.get(field))
        if value: return value
    if fallback is not None:
        value = _s(fallback.get("notification_class"))
        if value: return value
    return ""
def _reason(link: Mapping[str, Any], meta: Mapping[str, Any]) -> str:
    side = _s(link.get("side_compatibility")).lower()
    symbol = _s(link.get("symbol_compatibility")).lower()
    reason = _s(link.get("link_reason")).lower()
    if side in {"conflict", "mismatch", "incompatible"} or "side_conflict" in reason: return "side_conflict"
    if symbol in {"conflict", "mismatch", "incompatible"} or "symbol_conflict" in reason: return "symbol_conflict"
    if reason == "competing_candidate_tie": return "ambiguous_tie"
    if "followup" in reason or "management" in reason or "followup" in _notification(meta, link).lower() or "management" in _notification(meta, link).lower(): return "followup_only"
    signal = _s(link.get("signal_id"))
    if not signal or reason in {"", "no_candidate"} or _s(link.get("link_status")) == "no_candidate": return "no_candidate"
    status, confidence = _s(link.get("link_status")), _s(link.get("link_confidence")).lower()
    if status == "linked" and confidence in {"high", "medium", "low"}: return "linked_" + confidence
    if status == "ambiguous" or confidence == "ambiguous": return "ambiguous_tie"
    return "multiple_signal_candidates"
def _relation(link: Mapping[str, Any]) -> str:
    status = _s(link.get("link_status"))
    if status == "linked": return "preserved_v2_link"
    if status == "ambiguous": return "preserved_v2_ambiguous"
    return "preserved_v2_no_candidate"
def _status(meta: Mapping[str, Any]) -> str:
    values = [_s(meta.get(field)) for field in MODERN_FIELDS if _s(meta.get(field))]
    return "missing" if not values else ("complete" if len(values) == len(MODERN_FIELDS) else "partial")
def _candidate(link: Mapping[str, Any], meta: Mapping[str, Any]) -> dict[str, str]:
    row = {key: "" for key in CANDIDATE_HEADERS}
    row.update({"schema_version": MODERN_LINK_CANDIDATE_VERSION, "candidate_id": "mlc_" + _hash(link.get("link_id"), MODERN_LINK_CANDIDATE_VERSION)[:24], "baseline_link_id": _s(link.get("link_id")), "episode_id": _s(link.get("episode_id")), "signal_id": _s(link.get("signal_id")), "baseline_link_status": _s(link.get("link_status")), "baseline_link_confidence": _s(link.get("link_confidence")), "baseline_link_reason": _s(link.get("link_reason")), "reason_bucket": _reason(link, meta), "candidate_relation": _relation(link), "notification_kind": _notification(meta, link), "was_notified": _truth(meta.get("was_notified")), "notify_reason_codes": _s(meta.get("notify_reason_codes")), "operator_decision_state": _s(meta.get("operator_decision_state")), "operator_primary_side": _s(meta.get("operator_decision_primary_side")), "formal_execution_gate": _s(meta.get("trade_execution_gate")), "formal_blockers": _s(meta.get("trade_execution_blockers")), "active_primary_action": _s(meta.get("active_primary_action")), "side_aware_primary_class": _s(meta.get("side_aware_primary_class")), "side_aware_primary_state": _s(meta.get("side_aware_primary_state")), "structural_priority_side": _s(meta.get("structural_priority_side")), "structural_alignment_state": _s(meta.get("structural_alignment_state")), "modern_metadata_status": _status(meta), "human_basis": _s(meta.get("human_basis")) or "unknown", "causality_status": "not_claimed"})
    return row
def _usefulness(candidate: Mapping[str, Any], episode: Mapping[str, Any] | None, trial: Mapping[str, Any] | None, classification: Mapping[str, Any] | None) -> str:
    accepted = candidate.get("baseline_link_status") == "linked" and candidate.get("baseline_link_confidence") in {"high", "medium"}
    reason = _s(candidate.get("reason_bucket"))
    if not accepted: return "ambiguous"
    if candidate.get("was_notified") != "true": return ""
    if reason == "followup_only": return "management_useful"
    gate = _s(candidate.get("formal_execution_gate")).lower()
    op = _s(candidate.get("operator_decision_state")).lower()
    cls = _s((classification or {}).get("operator_class"))
    if gate == "pass": return "formal_candidate_used"
    if op in {"check_15m", "watch_zone"} or "B_CHECK_15M" in cls or "C_WATCH_ZONE" in cls: return "chart_check_then_entry"
    if "attention" in _s(candidate.get("notification_kind")).lower(): return "attention_then_entry"
    return "ambiguous"
def _aggregate(rows: list[Mapping[str, Any]], identity_field: str, value_field: str) -> dict[str, str]:
    grouped: dict[str, set[str]] = {}
    for row in rows:
        identity = _s(row.get(identity_field)); value = _s(row.get(value_field))
        if identity and value: grouped.setdefault(identity, set()).add(value)
    return {identity: ";".join(sorted(values)) for identity, values in grouped.items()}

def _decimal(value: Any) -> float:
    try: return float(_s(value).replace(",", ""))
    except (TypeError, ValueError): return 0.0

def build_modern_outputs(links: list[Mapping[str, Any]], signals: list[Mapping[str, Any]], episodes: list[Mapping[str, Any]], classifications: list[Mapping[str, Any]], trials: list[Mapping[str, Any]]) -> dict[str, Any]:
    meta = _metadata(signals)
    by_episode = { _s(row.get("episode_id")): row for row in episodes if _s(row.get("episode_id")) }
    by_signal_class = _aggregate(classifications, "source_signal_id", "operator_class")
    by_signal_trial = _aggregate(trials, "signal_id", "outcome_status")
    candidates = [_candidate(link, meta.get(_s(link.get("signal_id")), {field: "" for field in MODERN_FIELDS})) for link in links]
    candidates.sort(key=lambda row: (row["episode_id"], row["baseline_link_id"]))
    ledger: list[dict[str, str]] = []; queue: list[dict[str, str]] = []
    for candidate in candidates:
        sid, eid = candidate["signal_id"], candidate["episode_id"]
        episode = by_episode.get(eid); proxy_outcomes = by_signal_trial.get(sid, ""); classes = by_signal_class.get(sid, "")
        usefulness = _usefulness(candidate, episode, {"outcome_status": proxy_outcomes}, {"operator_class": classes})
        row = {key: "" for key in LEDGER_HEADERS}
        human_basis = _s(candidate.get("human_basis")) or "unknown"
        row.update({"schema_version": MODERN_ATTRIBUTION_SCHEMA_VERSION, "ledger_id": "led_" + _hash(candidate["baseline_link_id"], "actual_episode")[:24], "ledger_basis": "actual_episode", "signal_id": sid, "episode_id": eid, "notification_kind": candidate["notification_kind"], "was_notified": candidate["was_notified"], "notify_reason_codes": candidate["notify_reason_codes"], "operator_decision_state": candidate["operator_decision_state"], "operator_primary_side": candidate["operator_primary_side"], "formal_execution_gate": candidate["formal_execution_gate"], "formal_blockers": candidate["formal_blockers"], "p5_operator_classes": classes, "active_primary_action": candidate["active_primary_action"], "side_aware_primary_class": candidate["side_aware_primary_class"], "side_aware_primary_state": candidate["side_aware_primary_state"], "structural_priority_side": candidate["structural_priority_side"], "structural_alignment_state": candidate["structural_alignment_state"], "proxy_outcomes": proxy_outcomes, "actual_link_confidence": candidate["baseline_link_confidence"], "actual_position_side": _s((episode or {}).get("side")), "entry_latency_minutes": _s(next((link.get("time_delta_minutes") for link in links if _s(link.get("link_id")) == candidate["baseline_link_id"]), "")), "actual_realized_pnl": _s((episode or {}).get("realized_pnl")), "usefulness_category": usefulness, "human_basis": human_basis, "causality_status": "not_claimed", "_accepted_actual": candidate["baseline_link_status"] == "linked" and candidate["baseline_link_confidence"] in {"high", "medium"}})
        row["modern_metadata_status"] = candidate["modern_metadata_status"]
        ledger.append(row)
        if candidate["reason_bucket"] in {"side_conflict", "symbol_conflict", "ambiguous_tie", "no_candidate"}:
            queue.append({"schema_version": MODERN_ATTRIBUTION_SCHEMA_VERSION, "review_item_id": "mar_" + _hash(candidate["baseline_link_id"], candidate["reason_bucket"])[:24], "question_type": "low_or_ambiguous_link", "baseline_link_id": candidate["baseline_link_id"], "episode_id": eid, "signal_id": sid, "reason_bucket": candidate["reason_bucket"], "modern_metadata_status": candidate["modern_metadata_status"], "usefulness_category": usefulness, "question": "Review baseline link attribution", "human_basis": "unknown", "causality_status": "not_claimed"})
        if candidate["modern_metadata_status"] != "complete":
            queue.append({"schema_version": MODERN_ATTRIBUTION_SCHEMA_VERSION, "review_item_id": "mar_" + _hash(candidate["baseline_link_id"], "metadata")[:24], "question_type": "missing_modern_metadata", "baseline_link_id": candidate["baseline_link_id"], "episode_id": eid, "signal_id": sid, "reason_bucket": candidate["reason_bucket"], "modern_metadata_status": candidate["modern_metadata_status"], "usefulness_category": usefulness, "question": "Review modern signal metadata coverage", "human_basis": "unknown", "causality_status": "not_claimed"})
        if candidate["baseline_link_confidence"] in {"high", "medium"} and usefulness in {"formal_candidate_used", "chart_check_then_entry", "attention_then_entry", "management_useful"}:
            queue.append({"schema_version": MODERN_ATTRIBUTION_SCHEMA_VERSION, "review_item_id": "mar_" + _hash(candidate["baseline_link_id"], "human_basis")[:24], "question_type": "human_basis_for_high_medium_actual", "baseline_link_id": candidate["baseline_link_id"], "episode_id": eid, "signal_id": sid, "reason_bucket": candidate["reason_bucket"], "modern_metadata_status": candidate["modern_metadata_status"], "usefulness_category": usefulness, "question": "Confirm human basis for descriptive usefulness", "human_basis": "unknown", "causality_status": "not_claimed"})
    notified = { _s(row.get("signal_id")): row for row in signals if _truth(row.get("was_notified")) == "true" }
    accepted_signals = {row["signal_id"] for row in candidates if row["baseline_link_status"] == "linked" and row["baseline_link_confidence"] in {"high", "medium"}}
    for sid, signal in sorted(notified.items()):
        if sid in accepted_signals: continue
        proxy_outcomes = by_signal_trial.get(sid, "")
        positive = any(value in {"resolved_positive", "positive", "win", "favorable", "success"} for value in proxy_outcomes.lower().split(";"))
        row = {key: "" for key in LEDGER_HEADERS}; row.update({"schema_version": MODERN_ATTRIBUTION_SCHEMA_VERSION, "ledger_id": "led_" + _hash(sid, "notification_without_accepted_actual")[:24], "ledger_basis": "notification_without_accepted_actual", "signal_id": sid, "notification_kind": _notification(signal), "was_notified": "true", "notify_reason_codes": _s(signal.get("notify_reason_codes")), "operator_decision_state": _s(signal.get("operator_decision_state")), "operator_primary_side": _s(signal.get("operator_decision_primary_side")), "formal_execution_gate": _s(signal.get("trade_execution_gate")), "formal_blockers": _s(signal.get("trade_execution_blockers")), "active_primary_action": _s(signal.get("active_primary_action")), "side_aware_primary_class": _s(signal.get("side_aware_primary_class")), "side_aware_primary_state": _s(signal.get("side_aware_primary_state")), "structural_priority_side": _s(signal.get("structural_priority_side")), "structural_alignment_state": _s(signal.get("structural_alignment_state")), "proxy_outcomes": proxy_outcomes, "usefulness_category": "useful_no_entry_proxy" if positive else "no_actual_action", "human_basis": "unknown", "causality_status": "not_claimed"}); ledger.append(row)
    ledger.sort(key=lambda row: row["ledger_id"]); queue.sort(key=lambda row: row["review_item_id"])
    accepted = [row for row in ledger if row["ledger_basis"] == "actual_episode" and row.get("_accepted_actual") is True]
    descriptive = [row for row in ledger if row["ledger_basis"] == "actual_episode" and row.get("_accepted_actual") is not True]
    accepted_all = [row for row in ledger if row["ledger_basis"] == "actual_episode" and row.get("_accepted_actual") is True]
    notified_accepted = [row for row in accepted_all if row.get("was_notified") == "true"]
    not_notified_accepted = [row for row in accepted_all if row.get("was_notified") == "false"]
    unknown_notified_accepted = [row for row in accepted_all if row.get("was_notified") in {"", "unknown"}]
    def _metadata_counts(rows: list[Mapping[str, Any]]) -> dict[str, int]:
        return dict(sorted(Counter(row.get("modern_metadata_status", "missing") for row in rows).items()))
    directions = Counter()
    for row in notified_accepted:
        operator_side = _s(row.get("operator_primary_side")).lower()
        actual_side = _s(row.get("actual_position_side")).lower()
        directions["match" if operator_side in {"long", "short"} and operator_side == actual_side else "mismatch" if operator_side in {"long", "short"} and actual_side in {"long", "short"} else "unknown"] += 1
    comparable = directions["match"] + directions["mismatch"]
    latencies = sorted(float(row["entry_latency_minutes"]) for row in notified_accepted if _s(row.get("entry_latency_minutes")))
    pnls = sorted(_decimal(row["actual_realized_pnl"]) for row in notified_accepted if _s(row.get("actual_realized_pnl")))
    def _percentile(values: list[float], q: float) -> float | None:
        if not values: return None
        index = min(len(values) - 1, int(round((len(values) - 1) * q)))
        return values[index]
    human_confirmed = sum(bool(_s(row.get("human_basis")) and _s(row.get("human_basis")).lower() != "unknown") for row in notified_accepted)
    notification_status = Counter(row.get("was_notified", "") or "unknown" for row in accepted_all)
    report = {"baseline_episodes": len(episodes), "baseline_links": len(links), "reason_bucket_counts": dict(sorted(Counter(row["reason_bucket"] for row in candidates).items())), "confidence_counts": dict(sorted(Counter(_s(row.get("link_confidence")) for row in links).items())), "modern_metadata_coverage": dict(sorted(Counter(row["modern_metadata_status"] for row in candidates).items())), "metadata_coverage": {"accepted_actual_associations": _metadata_counts(accepted_all), "notified_accepted_actual_associations": _metadata_counts(notified_accepted)}, "notification_status_counts": dict(sorted(notification_status.items())), "notification_category_counts": dict(sorted(Counter(row["notification_kind"] or "blank" for row in notified_accepted).items())), "long_short_coverage": dict(sorted(Counter(row["actual_position_side"] or "unknown" for row in notified_accepted).items())), "operator_direction": {"operator_direction_match": directions["match"], "operator_direction_mismatch": directions["mismatch"], "operator_direction_unknown": directions["unknown"], "operator_direction_match_rate": (directions["match"] / comparable if comparable else None)}, "actual_attribution": {"total_actual_episode_ledger_rows": sum(row["ledger_basis"] == "actual_episode" for row in ledger), "accepted_high_medium": len(accepted_all), "accepted_high_medium_actual_associations": len(accepted_all), "notified_accepted_actual_associations": len(notified_accepted), "not_notified_accepted_actual_associations": len(not_notified_accepted), "unknown_notification_status_accepted_actual_associations": len(unknown_notified_accepted), "human_confirmed_usefulness_count": human_confirmed, "metadata_complete_notified_actual_count": sum(row.get("modern_metadata_status") == "complete" for row in notified_accepted), "accepted_high_medium_rows_with_pnl": sum(bool(row["actual_realized_pnl"]) for row in accepted_all), "accepted_actual_pnl_aggregate": sum(_decimal(row["actual_realized_pnl"]) for row in accepted_all), "low_ambiguous_no_candidate_descriptive_rows": len(descriptive), "entry_latency_count": len(latencies), "entry_latency_median_minutes": _percentile(latencies, .5), "entry_latency_p90_minutes": _percentile(latencies, .9), "realized_pnl_count": len(pnls), "realized_pnl_sum": sum(pnls) if pnls else 0, "realized_pnl_median": _percentile(pnls, .5), "positive_pnl_count": sum(v > 0 for v in pnls), "negative_pnl_count": sum(v < 0 for v in pnls), "zero_pnl_count": sum(v == 0 for v in pnls)}, "proxy_only_usefulness": dict(sorted(Counter(row["usefulness_category"] for row in ledger if row["ledger_basis"] == "notification_without_accepted_actual").items())), "notification_kind_breakdown": dict(sorted(Counter(row["notification_kind"] or "blank" for row in candidates).items())), "operator_state_breakdown": dict(sorted(Counter(row["operator_decision_state"] or "blank" for row in candidates).items())), "review_queue_counts": dict(sorted(Counter(row["question_type"] for row in queue).items())), "causality_statement": {"automatic_causal_claims": 0, "status": "not_claimed"}, "canonical_link_replacement": False, "deprecated_aliases": {"accepted_high_medium_actual": "accepted_high_medium_actual_associations"}, "safety_boundary": "report-only / no causal claim / no baseline adoption / no P9 decision / no automatic order"}
    ambiguous_notified = sum(row.get("usefulness_category") == "ambiguous" for row in notified_accepted)
    report["notification_usefulness"] = {"ambiguous_notified_actual_count": ambiguous_notified, "ambiguous_notified_actual_rate": (ambiguous_notified / len(notified_accepted) if notified_accepted else None), "automatic_causal_claims": 0, "causality_status": "not_claimed"}
    report["actual_attribution"]["ambiguous_notified_actual_count"] = ambiguous_notified
    report["actual_attribution"]["ambiguous_notified_actual_rate"] = (ambiguous_notified / len(notified_accepted) if notified_accepted else None)
    report_md = "\n".join(("# Modern attribution report", "", f"- Baseline episodes: {len(episodes)}", f"- Baseline links: {len(links)}", "- Actual attribution and proxy usefulness are separate.", "- Automatic causal claims: 0.", "- Canonical v2 link replacement: false.", "- report-only / human approval required / no automatic order.", ""))
    return {"candidate_csv": _csv(CANDIDATE_HEADERS, candidates), "ledger_csv": _csv(LEDGER_HEADERS, ledger), "queue_csv": _csv(QUEUE_HEADERS, queue), "report": report, "report_md": report_md, "candidates": candidates, "ledger": ledger, "queue": queue}
