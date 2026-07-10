"""Deterministic, report-only replay of P5 classifications over P4 scenarios."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import mean, median
from typing import Any
from zoneinfo import ZoneInfo

from src.feedback.manual_operator_classifier import OUTPUT_HEADERS as CLASSIFICATION_HEADERS
from src.feedback.manual_decision_events import DECISION_HEADERS
from src.feedback.manual_trade_episode_builder import EPISODE_HEADERS
from src.feedback.manual_trade_signal_linker import LINK_HEADERS
from src.feedback.manual_scenario_normalizer import EVENT_HEADERS, EVENT_SCHEMA_VERSION, SCENARIO_HEADERS, SCENARIO_SCHEMA_VERSION

SCHEMA_VERSION = "manual_operator_historical_replay.v1"
REPORT_SCHEMA_VERSION = "manual_operator_historical_replay_report.v1"
METHOD_VERSION = "manual_operator_historical_replay.v1"
POLICIES = ("CURRENT_STRICT", "A_ONLY", "A_PLUS_B", "A_PLUS_B_PLUS_C_OBSERVE", "STOP_OVERLAY")
CLASSES = {"A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE", "STOP_OR_EXIT"}
STATUSES = {"classified", "insufficient_evidence", "ambiguous_grouping"}
REPLAY_HEADERS = [
    "schema_version", "replay_row_id", "replay_method_version", "policy_name", "row_role", "scenario_id",
    "selected_scenario_event_id", "classification_id", "selected_at_utc", "selected_at_jst", "symbol", "side",
    "setup_family", "market_regime", "selected_operator_class", "trade_execution_gate", "selection_reason",
    "intraperiod_outcome", "normalized_outcome_status", "first_exit_reason", "mfe_r", "mae_r",
    "ohlcv_coverage_status", "ohlcv_gap_reason", "scenario_final_status", "scenario_final_lifecycle",
    "scenario_final_proxy_outcome", "later_upgrade_class", "later_upgrade_at_utc", "upgrade_latency_minutes",
    "decision_join_status", "first_effective_human_action", "first_human_checked_at_utc", "actual_join_status",
    "actual_episode_id", "actual_link_confidence", "actual_gross_realized_pnl", "actual_fee_total",
    "actual_net_pnl_after_fee", "source_join_status",
]
SAFETY = "offline historical replay only / not FORMAL_GO / no automatic order / human decides manually"
MISSING_OHLCV = {"no_ohlcv_input", "candidate_timestamp_missing", "candidate_before_ohlcv_start", "candidate_after_ohlcv_end", "candidate_window_gap", "malformed_ohlcv", "stale_ohlcv_range", "unknown_gap"}


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace(" ", "T")
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _utc(value: datetime | None) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if value else ""


def _jst(value: datetime | None) -> str:
    return value.astimezone(ZoneInfo("Asia/Tokyo")).isoformat() if value else ""


def _dec(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        parsed = Decimal(text)
        return parsed if parsed.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode()).hexdigest()


def _read(path: Path, headers: list[str], version: str | None = None) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "missing_input"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            if (reader.fieldnames or []) != headers:
                return [], "input_schema_mismatch"
            rows = [{str(k): str(v or "").strip() for k, v in row.items()} for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"
    if version and any(row.get("schema_version") != version for row in rows):
        return [], "input_schema_mismatch"
    return rows, None


def _normal_outcome(row: dict[str, str]) -> str:
    outcome = row.get("intraperiod_outcome", "").strip().lower()
    gap = row.get("ohlcv_gap_reason", "").strip().lower()
    coverage = row.get("ohlcv_coverage_status", "").strip().lower()
    if outcome in {"tp1_first", "tp2_first"}:
        return "resolved_positive"
    if outcome == "sl_first":
        return "resolved_negative"
    if outcome == "entry_reached":
        return "entry_reached_unresolved"
    if outcome in {"not_entered", "entry_not_reached"}:
        return "not_entered"
    if outcome == "expired":
        return "expired"
    if outcome == "no_ohlcv" or coverage in {"no_ohlcv", "coverage_missing"} or gap in MISSING_OHLCV:
        return "coverage_missing"
    if outcome in {"", "pending", "timeout"}:
        return "pending"
    if outcome == "ambiguous":
        return "ambiguous"
    return "unknown"


def _qualifies(policy: str, row: dict[str, str]) -> tuple[bool, str, str]:
    status = row.get("classification_status", "")
    cls = row.get("operator_class", "")
    if status != "classified":
        return False, "", ""
    if policy == "CURRENT_STRICT":
        return row.get("trade_execution_gate", "").strip().lower() == "pass" and cls != "STOP_OR_EXIT", "entry_candidate", "strict_pass"
    if policy == "A_ONLY":
        return cls == "A_FORMAL", "entry_candidate", "a_formal"
    if policy == "A_PLUS_B":
        return cls in {"A_FORMAL", "B_CHECK_15M"}, "entry_candidate", "a_or_b"
    if policy == "A_PLUS_B_PLUS_C_OBSERVE":
        return cls in {"A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE"}, ("observe_only" if cls == "C_WATCH_ZONE" else "entry_candidate"), "a_b_or_c"
    return cls == "STOP_OR_EXIT", "stop_overlay", "stop_overlay"


def _validate_integrity(scenarios: list[dict[str, str]], events: list[dict[str, str]], classes: list[dict[str, str]]) -> str | None:
    scenario_ids = [row.get("scenario_id", "") for row in scenarios]
    if any(not x for x in scenario_ids) or len(set(scenario_ids)) != len(scenario_ids):
        return "input_schema_mismatch"
    known = set(scenario_ids)
    event_ids = [row.get("scenario_event_id", "") for row in events]
    if any(not x for x in event_ids) or len(set(event_ids)) != len(event_ids):
        return "input_schema_mismatch"
    event_map = {row["scenario_event_id"]: row for row in events}
    for row in events:
        if not row.get("candidate_id") or (row.get("grouping_status") == "ambiguous" and row.get("scenario_id")) or (row.get("grouping_status") != "ambiguous" and row.get("scenario_id") not in known):
            return "input_schema_mismatch"
    ids = [row.get("classification_id", "") for row in classes]
    if any(not x for x in ids) or len(set(ids)) != len(ids):
        return "input_schema_mismatch"
    if len(classes) != len(events):
        return "missing_classification"
    methods = {row.get("classifier_method_version", "") for row in classes}
    snapshots = {tuple(row.get(key, "") for key in ("short_direction_min", "short_execution_min", "short_wait_max", "short_tp1_rr_min", "short_tp2_rr_min", "long_direction_min", "long_execution_min", "long_wait_max", "long_tp1_rr_min", "long_tp2_rr_min")) for row in classes}
    if len(methods) > 1 or len(snapshots) > 1:
        return "mixed_classifier_snapshot"
    for row in classes:
        event = event_map.get(row.get("scenario_event_id"))
        if event is None:
            return "unknown_classification_reference"
        for key in ("scenario_id", "candidate_id", "source_signal_id", "symbol", "side", "setup_family"):
            if row.get(key, "") != event.get(key, ""):
                return "classification_identity_mismatch"
        if row.get("classification_status") not in STATUSES or (row.get("operator_class") and row.get("operator_class") not in CLASSES):
            return "input_schema_mismatch"
    return None


def _validate_optional(path: Path | None, headers: list[str], version: str) -> tuple[list[dict[str, str]], str | None]:
    if path is None:
        return [], None
    return _read(path, headers, version)


def _effective_decisions(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], str | None]:
    ids = [row.get("decision_event_id", "") for row in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        return [], "input_schema_mismatch"
    by_id = {row["decision_event_id"]: row for row in rows}
    superseded: set[str] = set()
    for row in rows:
        status = row.get("record_status", "")
        target = row.get("supersedes_decision_event_id", "")
        if status not in {"active", "correction"} or (status == "active" and target) or (status == "correction" and (not target or target == row["decision_event_id"] or target not in by_id)):
            return [], "invalid_correction_graph"
        if target:
            target_row = by_id[target]
            if target_row.get("supersedes_decision_event_id"):
                return [], "invalid_correction_graph"
            superseded.add(target)
    if len(superseded) != len({row.get("supersedes_decision_event_id") for row in rows if row.get("supersedes_decision_event_id")}):
        return [], "invalid_correction_graph"
    return [row for row in rows if row["decision_event_id"] not in superseded], None


def _row_id(policy: str, role: str, scenario_id: str, event_id: str, classification_id: str) -> str:
    return "rpl_" + _hash(policy, role, scenario_id, event_id, classification_id, METHOD_VERSION)[:24]


def _atomic(outputs: list[tuple[Path, str]]) -> None:
    temps: list[tuple[Path, Path]] = []; backups: list[tuple[Path, Path]] = []; replaced: list[Path] = []
    try:
        for target, text in outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=".p6-", dir=target.parent); os.close(fd)
            temp = Path(name); temp.write_text(text, encoding="utf-8"); temps.append((target, temp))
        for target, _ in temps:
            if target.exists():
                backup = target.with_name("." + target.name + ".p6-backup"); backup.unlink(missing_ok=True); target.replace(backup); backups.append((target, backup))
        for target, temp in temps:
            temp.replace(target); replaced.append(target)
    except Exception as exc:
        for target in replaced: target.unlink(missing_ok=True)
        for target, backup in backups:
            if backup.exists(): backup.replace(target)
        raise OSError("output_transaction_failed") from exc
    finally:
        for _, temp in temps: temp.unlink(missing_ok=True)
        for _, backup in backups: backup.unlink(missing_ok=True)


def _csv_text(rows: list[dict[str, str]]) -> str:
    from io import StringIO
    stream = StringIO(); writer = csv.DictWriter(stream, fieldnames=REPLAY_HEADERS, lineterminator="\n"); writer.writeheader(); writer.writerows({key: row.get(key, "") for key in REPLAY_HEADERS} for row in rows); return stream.getvalue()


def _markdown(payload: dict[str, Any]) -> str:
    lines = ["# Manual Operator Historical Replay", "", "## Purpose", "", "Offline historical replay only.", "", "## Input Status", json.dumps(payload["input_status"], sort_keys=True), "", "## Method and No-Leakage Boundary", "", "Not FORMAL_GO; no automatic order; human decides manually. Existing gates are not replaced or recomputed.", "", "## Policy Definitions", "", "A_ONLY, A_PLUS_B, and A_PLUS_B_PLUS_C_OBSERVE are independent views; C is observation-only and STOP is not an automatic exit.", "", "## Coverage", json.dumps(payload["policy_summaries"], sort_keys=True), "", "## Policy Comparison", ""]
    for policy in POLICIES: lines.append(f"- {policy}: {json.dumps(payload['policy_summaries'].get(policy, {}), sort_keys=True)}")
    lines += ["", "## Duplicate Compression", "- Selected rows are scenario-deduplicated.", "", "## Proxy Outcome Comparison", "- Proxy positive rate is not actual win rate.", "", "## Side Breakdown", json.dumps(payload["side_policy_summaries"], sort_keys=True), "", "## Regime Breakdown", json.dumps(payload["regime_policy_summaries"], sort_keys=True), "", "## Setup-Family Breakdown", json.dumps(payload["setup_family_policy_summaries"], sort_keys=True), "", "## C Observation and Upgrade Review", f"- proxy_c_upgrade_candidate_rows: {payload['proxy_c_upgrade_candidate_rows']}", "", "## STOP Overlay Review", f"- stop_overlay_rows: {payload['policy_summaries'].get('STOP_OVERLAY', {}).get('selected_scenario_rows', 0)}", "", "## Human Decision Evidence", "- Optional and descriptive; manual notes are not included.", "", "## Actual Trade Evidence", "- Actual evidence uses only eligible high/medium links.", "", "## Limitations", "- Unresolved and no-OHLCV rows are excluded from resolved denominators.", "- No production tuning recommendation is made in P6.", "", "## Safety Boundary", SAFETY, ""]
    return "\n".join(lines)


def build_manual_operator_historical_replay(*, scenarios: Path, scenario_events: Path, classifications: Path, output_csv: Path, output_json: Path, output_md: Path, report_date: str, decision_events: Path | None = None, trade_episodes: Path | None = None, episode_links: Path | None = None, dry_run: bool = False, replace_output: bool = False) -> dict[str, Any]:
    if (trade_episodes is None) != (episode_links is None):
        return {"ok": False, "exit_code": 2, "errors": ["optional_actual_inputs_must_be_together"], "report_written": False}
    scenario_rows, err = _read(scenarios, SCENARIO_HEADERS, SCENARIO_SCHEMA_VERSION)
    if err: return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
    event_rows, err = _read(scenario_events, EVENT_HEADERS, EVENT_SCHEMA_VERSION)
    if err: return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
    class_rows, err = _read(classifications, CLASSIFICATION_HEADERS, "manual_operator_classification.v1")
    if err: return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
    err = _validate_integrity(scenario_rows, event_rows, class_rows)
    if err: return {"ok": False, "exit_code": 3 if "conflict" in err else 2, "errors": [err], "report_written": False}
    decision_rows, err = _validate_optional(decision_events, DECISION_HEADERS, "manual_decision_event.v1")
    if err: return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
    effective_decisions, err = _effective_decisions(decision_rows) if decision_rows else ([], None)
    if err: return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
    episode_rows, err = _validate_optional(trade_episodes, EPISODE_HEADERS, "manual_trade_episode.v1")
    if err: return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
    link_rows, err = _validate_optional(episode_links, LINK_HEADERS, "manual_trade_signal_link.v2")
    if err: return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
    for event in event_rows:
        for field in ("mfe_r", "mae_r"):
            if event.get(field) and _dec(event[field]) is None:
                return {"ok": False, "exit_code": 2, "errors": ["invalid_numeric"], "report_written": False}
    events_by_id = {row["scenario_event_id"]: row for row in event_rows}; scenarios_by_id = {row["scenario_id"]: row for row in scenario_rows}; classes_by_event = {row["scenario_event_id"]: row for row in class_rows}
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in class_rows:
        event = events_by_id[row["scenario_event_id"]]
        if event.get("scenario_id"): grouped.setdefault(event["scenario_id"], []).append(row)
    rows: list[dict[str, str]] = []; summaries: dict[str, dict[str, Any]] = {}
    strict_inconsistent = sum(1 for row in class_rows if row.get("trade_execution_gate", "").strip().lower() == "pass" and (row.get("classification_status") != "classified" or row.get("operator_class") == "STOP_OR_EXIT"))
    for policy in POLICIES:
        qualifying = 0; selected: list[dict[str, str]] = []
        for scenario_id, candidates in grouped.items():
            ordered = sorted(candidates, key=lambda row: (row.get("event_timestamp_utc", ""), row.get("scenario_event_id", ""), row.get("classification_id", "")))
            matches = [row for row in ordered if _qualifies(policy, row)[0]]
            qualifying += len(matches)
            if matches: selected.append(matches[0])
        policy_rows: list[dict[str, str]] = []
        for cls in selected:
            event = events_by_id[cls["scenario_event_id"]]; scenario = scenarios_by_id.get(event.get("scenario_id", ""), {})
            _, role, reason = _qualifies(policy, cls); selected_at = _dt(cls.get("event_timestamp_utc")) or _dt(event.get("event_timestamp_utc")); outcome = _normal_outcome(event)
            replay = {key: "" for key in REPLAY_HEADERS}; replay.update(schema_version=SCHEMA_VERSION, replay_row_id=_row_id(policy, role, event.get("scenario_id", ""), event.get("scenario_event_id", ""), cls.get("classification_id", "")), replay_method_version=METHOD_VERSION, policy_name=policy, row_role=role, scenario_id=event.get("scenario_id", ""), selected_scenario_event_id=event.get("scenario_event_id", ""), classification_id=cls.get("classification_id", ""), selected_at_utc=_utc(selected_at), selected_at_jst=_jst(selected_at), symbol=event.get("symbol", ""), side=event.get("side", ""), setup_family=event.get("setup_family", ""), market_regime=cls.get("market_regime", ""), selected_operator_class=cls.get("operator_class", ""), trade_execution_gate=cls.get("trade_execution_gate", ""), selection_reason=reason, intraperiod_outcome=event.get("intraperiod_outcome", ""), normalized_outcome_status=outcome, first_exit_reason=event.get("first_exit_reason", ""), mfe_r=event.get("mfe_r", ""), mae_r=event.get("mae_r", ""), ohlcv_coverage_status=event.get("ohlcv_coverage_status", ""), ohlcv_gap_reason=event.get("ohlcv_gap_reason", ""), scenario_final_status=scenario.get("scenario_status", ""), scenario_final_lifecycle=scenario.get("lifecycle_state", ""), scenario_final_proxy_outcome=scenario.get("proxy_outcome", ""), source_join_status="complete")
            for decision in effective_decisions:
                decision_time = _dt(decision.get("human_checked_at_utc") or decision.get("human_checked_at_jst"));
                if decision.get("scenario_id") == event.get("scenario_id") and decision_time and selected_at and decision_time >= selected_at:
                    replay["decision_join_status"] = "matched"; replay["first_effective_human_action"] = decision.get("human_action", ""); replay["first_human_checked_at_utc"] = _utc(decision_time); break
            if not replay["decision_join_status"] and decision_events is not None: replay["decision_join_status"] = "no_match"
            eligible_links = [link for link in link_rows if link.get("signal_id") == event.get("source_signal_id") and link.get("link_status") == "linked" and link.get("link_confidence") in {"high", "medium"}]
            if eligible_links:
                episode = next((item for item in episode_rows if item.get("episode_id") == eligible_links[0].get("episode_id")), None)
                opened = _dt(episode.get("opened_at_utc")) if episode else None
                if episode and opened and selected_at and opened >= selected_at and episode.get("association_status") == "matched":
                    replay["actual_join_status"] = "matched"; replay["actual_episode_id"] = episode.get("episode_id", ""); replay["actual_link_confidence"] = eligible_links[0].get("link_confidence", ""); replay["actual_gross_realized_pnl"] = episode.get("realized_pnl", ""); replay["actual_fee_total"] = episode.get("fee_total", "")
                else: replay["actual_join_status"] = "excluded"
            elif trade_episodes is not None: replay["actual_join_status"] = "no_match"
            policy_rows.append(replay)
        rows.extend(policy_rows)
        resolved = [r for r in policy_rows if r["normalized_outcome_status"] in {"resolved_positive", "resolved_negative"}]
        pos = sum(r["normalized_outcome_status"] == "resolved_positive" for r in resolved); neg = len(resolved) - pos
        summaries[policy] = {"qualifying_event_rows": qualifying, "selected_scenario_rows": len(policy_rows), "duplicate_event_rows_suppressed": qualifying - len(policy_rows), "scenario_selection_rate": (len(policy_rows) / qualifying if qualifying else 0.0), "entry_candidate_rows": sum(r["row_role"] == "entry_candidate" for r in policy_rows), "observe_only_rows": sum(r["row_role"] == "observe_only" for r in policy_rows), "resolved_proxy_rows": len(resolved), "resolved_positive_rows": pos, "resolved_negative_rows": neg, "proxy_positive_rate": (pos / len(resolved) if resolved else 0.0), "entry_reached_unresolved_rows": sum(r["normalized_outcome_status"] == "entry_reached_unresolved" for r in policy_rows), "not_entered_rows": sum(r["normalized_outcome_status"] == "not_entered" for r in policy_rows), "expired_rows": sum(r["normalized_outcome_status"] == "expired" for r in policy_rows), "coverage_missing_rows": sum(r["normalized_outcome_status"] == "coverage_missing" for r in policy_rows), "pending_rows": sum(r["normalized_outcome_status"] == "pending" for r in policy_rows), "ambiguous_outcome_rows": sum(r["normalized_outcome_status"] == "ambiguous" for r in policy_rows), "unknown_outcome_rows": sum(r["normalized_outcome_status"] == "unknown" for r in policy_rows)}
    rows.sort(key=lambda r: (POLICIES.index(r["policy_name"]), r["selected_at_utc"], r["scenario_id"], r["replay_row_id"]))
    for replay in rows:
        if replay["row_role"] == "observe_only":
            later = [item for item in grouped.get(replay["scenario_id"], []) if item.get("operator_class") in {"A_FORMAL", "B_CHECK_15M"} and (_dt(item.get("event_timestamp_utc")) or datetime.min.replace(tzinfo=timezone.utc)) > (_dt(replay["selected_at_utc"]) or datetime.min.replace(tzinfo=timezone.utc))]
            if later:
                upgrade = sorted(later, key=lambda item: (item.get("event_timestamp_utc", ""), item.get("scenario_event_id", ""), item.get("classification_id", "")))[0]
                replay["later_upgrade_class"] = upgrade.get("operator_class", ""); upgrade_time = _dt(upgrade.get("event_timestamp_utc")); replay["later_upgrade_at_utc"] = _utc(upgrade_time); selected_time = _dt(replay.get("selected_at_utc")); replay["upgrade_latency_minutes"] = str(int((upgrade_time - selected_time).total_seconds() / 60)) if upgrade_time and selected_time else ""
    def breakdown(field: str) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {}
        for replay in rows:
            key = replay.get(field, "")
            result.setdefault(key, {})[replay["policy_name"]] = result.setdefault(key, {}).get(replay["policy_name"], 0) + 1
        return {key: dict(sorted(value.items())) for key, value in sorted(result.items())}
    payload: dict[str, Any] = {"schema_version": REPORT_SCHEMA_VERSION, "report_date": report_date, "report_written": False, "safety_boundary": SAFETY, "scenario_rows": len(scenario_rows), "scenario_event_rows": len(event_rows), "classification_rows": len(class_rows), "assigned_event_rows": sum(bool(r.get("scenario_id")) for r in event_rows), "ambiguous_event_rows": sum(not bool(r.get("scenario_id")) for r in event_rows), "insufficient_classification_rows": sum(r.get("classification_status") == "insufficient_evidence" for r in class_rows), "classifier_method_version": next(iter({r.get("classifier_method_version", "") for r in class_rows}), ""), "threshold_snapshot": {key: class_rows[0].get(key, "") for key in ("short_direction_min", "short_execution_min", "short_wait_max", "short_tp1_rr_min", "short_tp2_rr_min", "long_direction_min", "long_execution_min", "long_wait_max", "long_tp1_rr_min", "long_tp2_rr_min")} if class_rows else {}, "policy_summaries": {policy: summaries.get(policy, {}) for policy in POLICIES}, "side_policy_summaries": breakdown("side"), "regime_policy_summaries": breakdown("market_regime"), "setup_family_policy_summaries": breakdown("setup_family"), "class_policy_summaries": breakdown("selected_operator_class"), "outcome_policy_summaries": breakdown("normalized_outcome_status"), "strict_pass_inconsistent_rows": strict_inconsistent, "proxy_over_suppression_candidate_rows": 0, "proxy_false_positive_candidate_rows": sum(r["normalized_outcome_status"] == "resolved_negative" and r["row_role"] == "entry_candidate" for r in rows), "proxy_c_observation_positive_candidate_rows": sum(r["row_role"] == "observe_only" and r["normalized_outcome_status"] == "resolved_positive" for r in rows), "proxy_c_upgrade_candidate_rows": sum(bool(r.get("later_upgrade_class")) for r in rows), "decision_input_status": "absent" if decision_events is None else "provided", "decision_summary": {"effective_decision_rows": len(effective_decisions)}, "actual_input_status": "absent" if trade_episodes is None else "provided", "actual_summary": {"eligible_linked_rows": sum(bool(r.get("actual_episode_id")) for r in rows)}, "input_status": {"scenarios": "provided", "scenario_events": "provided", "classifications": "provided"}, "errors": []}
    csv_text = _csv_text(rows); payload["ok"] = True; payload["exit_code"] = 0
    json_text = json.dumps(payload | {"report_written": True}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"; md_text = _markdown(payload)
    if dry_run: return payload
    for path, marker in ((output_csv, "schema_version"), (output_json, '"schema_version"'), (output_md, "# Manual Operator Historical Replay")):
        if path.exists() and not replace_output:
            try:
                text = path.read_text(encoding="utf-8")
                from io import StringIO
                if marker not in text or (path == output_csv and (csv.DictReader(StringIO(text)).fieldnames or []) != REPLAY_HEADERS): return {"ok": False, "exit_code": 4, "errors": ["existing_output_schema_mismatch"], "report_written": False}
            except (OSError, UnicodeError): return {"ok": False, "exit_code": 4, "errors": ["existing_output_schema_mismatch"], "report_written": False}
    try: _atomic([(output_csv, csv_text), (output_json, json_text), (output_md, md_text)])
    except OSError: return {"ok": False, "exit_code": 4, "errors": ["output_transaction_failed"], "report_written": False}
    payload["report_written"] = True
    return payload
