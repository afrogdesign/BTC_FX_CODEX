"""Deterministic P8 manual-operator trial evidence view.

This module composes the accepted historical replay output and adds only
report-only comparison, exception queue, and readiness views.  It never
changes classifier, gate, notification, or trading behavior.
"""
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
from typing import Any

from src.feedback.manual_operator_historical_replay import (
    METHOD_VERSION as REPLAY_METHOD_VERSION,
    build_manual_operator_historical_replay,
)
from src.feedback.manual_operator_classifier import classify_manual_operator_candidate

SCHEMA_VERSION = "manual_operator_trial_evidence.v1"
METHOD_VERSION = "manual_operator_trial_evidence.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
POLICIES = ("CURRENT_STRICT", "A_ONLY", "A_PLUS_B", "A_PLUS_B_PLUS_C_OBSERVE", "STOP_OVERLAY")
ISSUE_RESOLUTION_METADATA = {
    "P8-ISSUE-002_MAIN_VS_BIG_CHANCE_HIERARCHY": {
        "resolution_confidence": "accepted_implementation",
        "resolution_basis": "accepted_operator_surface.main_vs_big_chance_hierarchy",
    },
    "P8-ISSUE-003_RAW_CLASSIFIER_PAYLOAD_EXPOSED": {
        "resolution_confidence": "accepted_implementation",
        "resolution_basis": "accepted_operator_surface.collapsed_classifier_payload",
    },
    "P8-ISSUE-004_STOP_CARD_SIDE_IDENTITY": {
        "resolution_confidence": "accepted_implementation",
        "resolution_basis": "accepted_operator_surface.side_specific_stop_card_identity",
    },
}

TRIAL_FACT_HEADERS = [
    "schema_version", "trial_fact_id", "scenario_id", "scenario_event_id", "signal_id", "candidate_id",
    "event_timestamp_utc", "side", "setup_family", "market_regime", "operator_class",
    "classifier_method_version", "trade_execution_gate", "phase1b_lite_gate", "opportunity_gate",
    "reason_codes", "warning_codes", "no_trade_flags", "risk_flags", "entry_zone_low", "entry_zone_high",
    "invalidation_price", "tp1_price", "tp2_price", "outcome_status", "intraperiod_outcome",
    "first_exit_reason", "mfe_r", "mae_r", "ohlcv_coverage_status", "ohlcv_gap_reason", "zone_result",
    "direction_result", "comparison_status", "actual_episode_id", "actual_link_confidence",
    "actual_net_pnl_after_fee", "evidence_tier", "issue_flags",
]
QUEUE_HEADERS = [
    "schema_version", "review_item_id", "question_type", "scenario_id", "scenario_event_id", "signal_id",
    "side", "policy_name", "question", "selectable_options", "evidence_tier", "issue_flags",
]


def _dt(value: Any) -> datetime | None:
    text = str(value or "").strip().replace("Z", "+00:00")
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _dec(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        result = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    return result if result.is_finite() else None


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode()).hexdigest()[:24]


def _sha256(path: Path | None) -> str:
    if path is None:
        return "missing"
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return "unreadable"
    return digest.hexdigest()


def _read_csv(path: Path) -> tuple[list[dict[str, str]], str | None]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = [{str(k): str(v or "").strip() for k, v in row.items()} for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid_input"
    return rows, None


def _validate_future_context(path: Path) -> str | None:
    rows, error = _read_csv(path)
    if error:
        return error
    for row in rows:
        event_time = _dt(row.get("event_timestamp_utc") or row.get("event_timestamp_jst"))
        if event_time is None:
            continue
        for key in ("entry_reached_time", "first_exit_time"):
            value = row.get(key, "")
            if value and (_dt(value) is None or _dt(value) < event_time):
                return "future_context_rejected"
    return None


def _status(row: dict[str, str]) -> str:
    outcome = row.get("normalized_outcome_status", "")
    cls = row.get("selected_operator_class", "")
    direction = str(row.get("direction_result", "")).strip().lower()
    if outcome in {"pending", "coverage_missing", "ambiguous", "unknown", "entry_reached_unresolved"}:
        return "unresolved"
    if direction in {"wrong", "wrong_side", "conflict", "opposite"}:
        return "wrong_side"
    if outcome == "resolved_positive":
        if cls in {"STOP_OR_EXIT", "C_WATCH_ZONE"}:
            return "too_defensive"
        return "aligned"
    if outcome == "resolved_negative":
        if cls in {"A_FORMAL", "B_CHECK_15M"}:
            return "too_aggressive"
        return "aligned"
    return "unresolved"


def _issue_flags(row: dict[str, str], status: str, opposite_available: bool) -> list[str]:
    flags: list[str] = []
    if status == "too_defensive":
        flags.append("high_value_missed_opportunity_proxy")
    if status == "too_aggressive":
        flags.append("adverse_entry_proxy")
    if row.get("selected_operator_class") == "STOP_OR_EXIT":
        if row.get("normalized_outcome_status") == "resolved_negative":
            flags.append("stop_useful_proxy")
        elif row.get("normalized_outcome_status") == "resolved_positive":
            flags.append("stop_false_alarm_proxy")
    if row.get("ohlcv_coverage_status") in {"no_ohlcv", "coverage_missing"} or row.get("normalized_outcome_status") == "coverage_missing":
        flags.append("no_ohlcv")
    return sorted(set(flags))


def _counterfactual_classification(class_row: dict[str, str], event_row: dict[str, str]) -> str:
    """Reuse P5's classifier after clearing only global no-trade flags."""
    side = str(class_row.get("side") or event_row.get("side") or "").strip().lower()
    candidate = {
        "candidate_id": class_row.get("candidate_id", event_row.get("candidate_id", "")),
        "source_signal_id": class_row.get("source_signal_id", event_row.get("source_signal_id", "")),
        "timestamp_jst": event_row.get("event_timestamp_jst", ""),
        "candidate_status": class_row.get("candidate_status", event_row.get("candidate_status", "")),
        "side": side,
        "entry_price": class_row.get("entry_price", event_row.get("entry_price", "")),
        "entry_zone_low": class_row.get("entry_zone_low", event_row.get("entry_zone_low", "")),
        "entry_zone_high": class_row.get("entry_zone_high", event_row.get("entry_zone_high", "")),
        "rr_zone_mid_tp1": class_row.get("rr_tp1_used", ""),
        "rr_zone_mid_tp2": class_row.get("rr_tp2_used", ""),
    }
    signal = {
        "signal_id": class_row.get("source_signal_id", event_row.get("source_signal_id", "")),
        "timestamp_jst": event_row.get("event_timestamp_jst", ""),
        "primary_setup_side": class_row.get("primary_setup_side", ""),
        "primary_setup_status": class_row.get("primary_setup_status", ""),
        "confidence_direction_shadow": class_row.get("confidence_direction_shadow", ""),
        "confidence_execution_shadow": class_row.get("confidence_execution_shadow", ""),
        "confidence_wait_shadow": class_row.get("confidence_wait_shadow", ""),
        "trade_execution_gate": class_row.get("trade_execution_gate", ""),
        "phase1b_lite_gate": class_row.get("phase1b_lite_gate", ""),
        "opportunity_gate": class_row.get("opportunity_gate", ""),
        "data_quality_flag": class_row.get("data_quality_flag", ""),
        "no_trade_flags": "",
        "warning_flags": class_row.get("warning_codes", ""),
        "risk_flags": class_row.get("risk_flags", ""),
        "long_rr": class_row.get("rr_tp1_used", "") if side == "long" else "",
        "short_rr": class_row.get("rr_tp1_used", "") if side == "short" else "",
    }
    threshold_fields = ("short_direction_min", "short_execution_min", "short_wait_max", "short_tp1_rr_min", "short_tp2_rr_min", "long_direction_min", "long_execution_min", "long_wait_max", "long_tp1_rr_min", "long_tp2_rr_min")
    thresholds = {key: class_row.get(key, "") for key in threshold_fields}
    try:
        result = classify_manual_operator_candidate({**event_row, "side": side, "grouping_status": event_row.get("grouping_status", "new_scenario")}, candidate, signal, thresholds)
    except (ValueError, KeyError, TypeError):
        return "not_eligible"
    if result.get("classification_status") != "classified":
        return "not_eligible"
    if result.get("operator_class") == "B_CHECK_15M":
        return "counterfactual_B"
    if result.get("operator_class") == "C_WATCH_ZONE":
        return "counterfactual_C"
    return "not_eligible"


def _issue_summary(rows: list[dict[str, str]], key: str, *, status: str, severity: str, confidence: str, tuning: str, resolution_metadata: dict[str, str] | None = None) -> dict[str, Any]:
    affected = [row for row in rows if key in set(filter(None, row.get("issue_flags", "").split(";")))]
    timestamps = sorted(row.get("event_timestamp_utc", "") for row in affected if row.get("event_timestamp_utc"))
    summary = {
        "first_evidence_timestamp": timestamps[0] if timestamps else "",
        "last_evidence_timestamp": timestamps[-1] if timestamps else "",
        "occurrence_count": len(affected),
        "resolved_evidence_count": sum(row.get("outcome_status") in {"resolved_positive", "resolved_negative"} for row in affected),
        "actual_backed_count": sum(row.get("evidence_tier") == "actual_high_medium" for row in affected),
        "affected_side_counts": dict(sorted(Counter(row.get("side", "") for row in affected).items())),
        "affected_regime_counts": dict(sorted(Counter(row.get("market_regime", "") for row in affected).items())),
        "affected_setup_counts": dict(sorted(Counter(row.get("setup_family", "") for row in affected).items())),
        "severity": severity,
        "evidence_confidence": confidence,
        "tuning_eligibility": tuning,
        "status": status,
    }
    if resolution_metadata:
        summary.update(resolution_metadata)
    return summary


def _atomic(outputs: list[tuple[Path, str]]) -> None:
    temps: list[tuple[Path, Path]] = []
    backups: list[tuple[Path, Path]] = []
    replaced: list[Path] = []
    try:
        for target, text in outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=".p8-trial-", dir=target.parent)
            os.close(fd)
            temp = Path(name)
            temp.write_text(text, encoding="utf-8")
            temps.append((target, temp))
        for target, _ in temps:
            if target.exists():
                backup = target.with_name(f".{target.name}.p8-backup")
                backup.unlink(missing_ok=True)
                target.replace(backup)
                backups.append((target, backup))
        for target, temp in temps:
            temp.replace(target)
            replaced.append(target)
    except Exception as exc:
        for target in replaced:
            target.unlink(missing_ok=True)
        for target, backup in backups:
            if backup.exists():
                backup.replace(target)
        raise OSError("output_transaction_failed") from exc
    finally:
        for _, temp in temps:
            temp.unlink(missing_ok=True)
        for _, backup in backups:
            backup.unlink(missing_ok=True)


def _csv_text(headers: list[str], rows: list[dict[str, str]]) -> str:
    from io import StringIO
    stream = StringIO()
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows({key: row.get(key, "") for key in headers} for row in rows)
    return stream.getvalue()


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Manual Operator Trial Evidence", "", "## Purpose", "",
        "Offline comparison of event-time predictions, market-path outcomes, and eligible episode evidence.",
        "", "## Evaluation", json.dumps(report["counts"], ensure_ascii=False, sort_keys=True),
        "", "## Comparison", json.dumps(report["comparison"], ensure_ascii=False, sort_keys=True),
        "", "## Class / Side / Regime / Setup", json.dumps(report["breakdowns"], ensure_ascii=False, sort_keys=True),
        "", "## Actual Evidence", json.dumps(report["actual_evidence"], ensure_ascii=False, sort_keys=True),
        "", "## Review Queue", f"{report['review_queue_size']} exception items require human review.",
        "", "## P9 Readiness", json.dumps(report["p9_readiness"], ensure_ascii=False, sort_keys=True),
        "", "## Limitations",
        "Unresolved, no_ohlcv, low-confidence, and ambiguous evidence are excluded from performance claims.",
        "Actual trade absence does not prove skip, watch, or intent.",
        "No automatic tuning or production recommendation is applied by this report.",
        "", "## Safety Boundary", SAFETY, "",
    ]
    return "\n".join(lines)


def build_manual_operator_trial_evidence(
    *, scenarios: Path, scenario_events: Path, classifications: Path, output_csv: Path,
    output_queue_csv: Path, output_json: Path, output_md: Path, report_date: str,
    decision_events: Path | None = None, trade_episodes: Path | None = None,
    episode_links: Path | None = None, dry_run: bool = False, replace_output: bool = False,
) -> dict[str, Any]:
    if (trade_episodes is None) != (episode_links is None):
        return {"ok": False, "exit_code": 2, "errors": ["optional_actual_inputs_must_be_together"], "report_written": False}
    future_error = _validate_future_context(scenario_events)
    if future_error:
        return {"ok": False, "exit_code": 2, "errors": [future_error], "report_written": False}
    with tempfile.TemporaryDirectory(prefix="p8-replay-") as temp_dir:
        root = Path(temp_dir)
        replay = build_manual_operator_historical_replay(
            scenarios=scenarios, scenario_events=scenario_events, classifications=classifications,
            output_csv=root / "replay.csv", output_json=root / "replay.json", output_md=root / "replay.md",
            report_date=report_date, decision_events=decision_events, trade_episodes=trade_episodes,
            episode_links=episode_links, replace_output=True,
        )
        if not replay.get("ok"):
            return {"ok": False, "exit_code": int(replay.get("exit_code", 2)), "errors": replay.get("errors", ["input_invalid"]), "report_written": False}
        replay_rows, err = _read_csv(root / "replay.csv")
        if err:
            return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
        event_rows, err = _read_csv(scenario_events)
        if err:
            return {"ok": False, "exit_code": 2, "errors": [err], "report_written": False}
        class_by_event: dict[str, dict[str, str]] = {}
        try:
            with classifications.open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    class_by_event[str(row.get("scenario_event_id", ""))] = {str(k): str(v or "").strip() for k, v in row.items()}
        except (OSError, UnicodeError, csv.Error):
            return {"ok": False, "exit_code": 2, "errors": ["invalid_input"], "report_written": False}
        event_by_id = {row.get("scenario_event_id", ""): row for row in event_rows}
        # Use A/B/C selection plus STOP overlay, then deduplicate event identity.
        selected: dict[str, dict[str, str]] = {}
        for row in sorted(replay_rows, key=lambda item: (POLICIES.index(item.get("policy_name", "CURRENT_STRICT")) if item.get("policy_name") in POLICIES else 99, item.get("selected_at_utc", ""), item.get("scenario_event_id", ""))):
            event_id = row.get("selected_scenario_event_id", "")
            if row.get("policy_name") in {"A_PLUS_B_PLUS_C_OBSERVE", "STOP_OVERLAY"} and event_id and event_id not in selected:
                selected[event_id] = row
        rows: list[dict[str, str]] = []
        issue_counts: Counter[str] = Counter()
        comparisons: Counter[str] = Counter()
        class_counts: Counter[str] = Counter()
        side_counts: Counter[str] = Counter()
        regime_counts: Counter[str] = Counter()
        setup_counts: Counter[str] = Counter()
        resolved = unresolved = no_ohlcv = 0
        opposite_by_signal: dict[str, set[str]] = {}
        for event in event_rows:
            opposite_by_signal.setdefault(event.get("source_signal_id", ""), set()).add(event.get("side", ""))
        for event_id, replay_row in sorted(selected.items(), key=lambda item: (item[1].get("selected_at_utc", ""), item[0])):
            cls = class_by_event.get(event_id, {})
            signal_id = event_by_id.get(event_id, {}).get("source_signal_id", "")
            side = replay_row.get("side", "")
            opposite_events = [candidate for candidate in event_rows if candidate.get("source_signal_id") == signal_id and candidate.get("side") not in {side, ""}]
            opposite_levels = []
            for opposite in opposite_events:
                opposite_class = class_by_event.get(opposite.get("scenario_event_id", ""), {})
                opposite_levels.append(_counterfactual_classification(opposite_class, opposite))
            explicit_direction = cls.get("direction_result") or event_by_id.get(event_id, {}).get("direction_result") or cls.get("outcome_direction") or event_by_id.get(event_id, {}).get("outcome_direction")
            comparison_row = dict(replay_row)
            comparison_row["direction_result"] = explicit_direction or ""
            comparison = _status(comparison_row)
            opposite_available = bool(opposite_events)
            flags = _issue_flags(replay_row, comparison, opposite_available)
            global_stop = replay_row.get("selected_operator_class") == "STOP_OR_EXIT" and (
                "stop_no_trade_flag" in set(filter(None, cls.get("reason_codes", "").split(";")))
                or bool(cls.get("no_trade_flags", "").strip())
            )
            for level in opposite_levels:
                issue_counts["opposite_side_exists"] += 1
                if level == "counterfactual_B":
                    issue_counts["opposite_side_counterfactual_B"] += 1
                elif level == "counterfactual_C":
                    issue_counts["opposite_side_counterfactual_C"] += 1
                else:
                    issue_counts["opposite_side_not_eligible"] += 1
            if global_stop and any(level in {"counterfactual_B", "counterfactual_C"} for level in opposite_levels):
                flags.append("P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY")
            flags = sorted(set(flags))
            for flag in flags:
                issue_counts[flag] += 1
            for value in (replay_row.get("normalized_outcome_status", ""),):
                if value == "coverage_missing": no_ohlcv += 1
                elif value in {"resolved_positive", "resolved_negative"}: resolved += 1
                else: unresolved += 1
            if comparison != "unresolved": comparisons[comparison] += 1
            class_counts[replay_row.get("selected_operator_class", "")] += 1
            side_counts[side] += 1
            regime_counts[replay_row.get("market_regime", "")] += 1
            setup_counts[replay_row.get("setup_family", "")] += 1
            evidence = "actual_high_medium" if replay_row.get("actual_episode_id") and replay_row.get("actual_link_confidence") in {"high", "medium"} else "proxy_only"
            row = {key: "" for key in TRIAL_FACT_HEADERS}
            row.update(
                schema_version=SCHEMA_VERSION,
                trial_fact_id="tf_" + _hash(event_id, replay_row.get("policy_name", ""), METHOD_VERSION),
                scenario_id=replay_row.get("scenario_id", ""), scenario_event_id=event_id, signal_id=signal_id,
                candidate_id=event_by_id.get(event_id, {}).get("candidate_id", ""), event_timestamp_utc=replay_row.get("selected_at_utc", ""),
                side=side, setup_family=replay_row.get("setup_family", ""), market_regime=replay_row.get("market_regime", ""),
                operator_class=replay_row.get("selected_operator_class", ""), classifier_method_version=cls.get("classifier_method_version", ""),
                trade_execution_gate=replay_row.get("trade_execution_gate", ""), phase1b_lite_gate=cls.get("phase1b_lite_gate", ""), opportunity_gate=cls.get("opportunity_gate", ""),
                reason_codes=cls.get("reason_codes", ""), warning_codes=cls.get("warning_codes", ""), no_trade_flags=cls.get("no_trade_flags", ""), risk_flags=cls.get("risk_flags", ""),
                outcome_status=replay_row.get("normalized_outcome_status", ""), intraperiod_outcome=replay_row.get("intraperiod_outcome", ""), first_exit_reason=replay_row.get("first_exit_reason", ""),
                mfe_r=replay_row.get("mfe_r", ""), mae_r=replay_row.get("mae_r", ""), ohlcv_coverage_status=replay_row.get("ohlcv_coverage_status", ""), ohlcv_gap_reason=replay_row.get("ohlcv_gap_reason", ""),
                zone_result=("useful" if comparison in {"aligned", "too_defensive"} and replay_row.get("normalized_outcome_status") == "resolved_positive" else ("failed" if comparison == "too_aggressive" else "")),
                direction_result=(explicit_direction or ""), comparison_status=comparison,
                actual_episode_id=replay_row.get("actual_episode_id", ""), actual_link_confidence=replay_row.get("actual_link_confidence", ""), actual_net_pnl_after_fee=replay_row.get("actual_net_pnl_after_fee", ""), evidence_tier=evidence, issue_flags=";".join(flags),
                entry_zone_low=cls.get("entry_zone_low", ""), entry_zone_high=cls.get("entry_zone_high", ""), invalidation_price=cls.get("invalidation_price", ""), tp1_price=cls.get("tp1_price", ""), tp2_price=cls.get("tp2_price", ""),
            )
            rows.append(row)
        queue: list[dict[str, str]] = []
        if episode_links is not None:
            links, _ = _read_csv(episode_links)
            for link in links:
                if link.get("link_confidence") in {"low", "ambiguous"}:
                    queue.append({"schema_version": SCHEMA_VERSION, "review_item_id": "rq_" + _hash(link.get("link_id", ""), "low_link"), "question_type": "ambiguous_actual_trade_link", "scenario_id": "", "scenario_event_id": "", "signal_id": link.get("signal_id", ""), "side": "", "policy_name": "", "question": "この実取引linkは対象通知を根拠にしたか", "selectable_options": "yes;no;unknown", "evidence_tier": link.get("link_confidence", ""), "issue_flags": "low_or_ambiguous_link"})
        for row in rows:
            if "high_value_missed_opportunity_proxy" in row.get("issue_flags", "") and not row.get("actual_episode_id"):
                queue.append({"schema_version": SCHEMA_VERSION, "review_item_id": "rq_" + _hash(row["trial_fact_id"], "intent"), "question_type": "missing_human_intent", "scenario_id": row["scenario_id"], "scenario_event_id": row["scenario_event_id"], "signal_id": row["signal_id"], "side": row["side"], "policy_name": "", "question": "この機会を見送った主因は何か", "selectable_options": "not_seen;trigger_missing;stop_followed;timing;unclear", "evidence_tier": "proxy_only", "issue_flags": "high_value_missed_opportunity_proxy"})
        rows.sort(key=lambda row: (row.get("event_timestamp_utc", ""), row.get("scenario_event_id", ""), row.get("trial_fact_id", "")))
        queue.sort(key=lambda row: (row.get("question_type", ""), row.get("review_item_id", "")))
        actual_rows = [row for row in rows if row.get("evidence_tier") == "actual_high_medium"]
        issue_summary = {
            "P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY": _issue_summary(rows, "P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY", status="open hypothesis", severity="medium", confidence="proxy", tuning="not_eligible"),
            "P8-ISSUE-002_MAIN_VS_BIG_CHANCE_HIERARCHY": _issue_summary(rows, "P8-ISSUE-002_MAIN_VS_BIG_CHANCE_HIERARCHY", status="resolved", severity="medium", confidence="accepted_implementation", tuning="not_eligible", resolution_metadata=ISSUE_RESOLUTION_METADATA["P8-ISSUE-002_MAIN_VS_BIG_CHANCE_HIERARCHY"]),
            "P8-ISSUE-003_RAW_CLASSIFIER_PAYLOAD_EXPOSED": _issue_summary(rows, "P8-ISSUE-003_RAW_CLASSIFIER_PAYLOAD_EXPOSED", status="resolved", severity="medium", confidence="accepted_implementation", tuning="not_eligible", resolution_metadata=ISSUE_RESOLUTION_METADATA["P8-ISSUE-003_RAW_CLASSIFIER_PAYLOAD_EXPOSED"]),
            "P8-ISSUE-004_STOP_CARD_SIDE_IDENTITY": _issue_summary(rows, "P8-ISSUE-004_STOP_CARD_SIDE_IDENTITY", status="resolved", severity="medium", confidence="accepted_implementation", tuning="not_eligible", resolution_metadata=ISSUE_RESOLUTION_METADATA["P8-ISSUE-004_STOP_CARD_SIDE_IDENTITY"]),
        }
        input_paths = {"scenarios": scenarios, "scenario_events": scenario_events, "classifications": classifications, "decision_events": decision_events, "trade_episodes": trade_episodes, "episode_links": episode_links}
        fingerprints = {name: _sha256(path) for name, path in input_paths.items() if path is not None}
        max_event_timestamp = max((row.get("event_timestamp_utc", "") for row in rows if row.get("event_timestamp_utc")), default="")
        class_values = set(class_counts)
        side_values = set(side_counts)
        regime_available = bool(regime_counts) and all(regime_counts)
        setup_available = bool(setup_counts) and all(setup_counts)
        actual_episode_count = len({r.get("actual_episode_id") for r in actual_rows if r.get("actual_episode_id")})
        readiness = {
            "initial": {"resolved_events": resolved, "actual_entry_episodes": actual_episode_count, "class_segmentation_available": {"A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE", "STOP_OR_EXIT"}.issubset(class_values), "side_segmentation_available": {"long", "short"}.issubset(side_values), "regime_segmentation_available": regime_available, "setup_segmentation_available": setup_available, "reproducibility_metadata_available": True, "ready": resolved >= 100 and actual_episode_count >= 30 and {"A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE", "STOP_OR_EXIT"}.issubset(class_values) and {"long", "short"}.issubset(side_values) and regime_available and setup_available},
            "practical": {"resolved_events": resolved, "actual_entry_episodes": actual_episode_count, "validation_window_status": "not_established", "ready": False},
        }
        classifier_method_version = replay.get("classifier_method_version") or next((value.get("classifier_method_version") for value in class_by_event.values() if value.get("classifier_method_version")), "")
        report = {"schema_version": SCHEMA_VERSION, "report_date": report_date, "report_written": False, "safety_boundary": SAFETY, "method_version": METHOD_VERSION, "classifier_method_version": classifier_method_version, "replay_method_version": REPLAY_METHOD_VERSION, "input_fingerprints": fingerprints, "max_evaluated_event_timestamp": max_event_timestamp, "report_cutoff": report_date, "eligible_actual_link_policy": ["high", "medium"], "unresolved_no_ohlcv_separated": True, "input_status": {"scenarios": "provided", "scenario_events": "provided", "classifications": "provided", "actual": "provided" if trade_episodes else "missing"}, "cutoff": report_date, "counts": {"trial_fact_rows": len(rows), "resolved_rows": resolved, "unresolved_rows": unresolved, "no_ohlcv_rows": no_ohlcv, "ambiguous_rows": sum("ambiguous" in r.get("outcome_status", "") for r in rows), "scenario_count": len({r.get("scenario_id") for r in rows if r.get("scenario_id")}), "review_queue_size": len(queue)}, "class_distribution": dict(sorted(class_counts.items())), "comparison": dict(sorted(comparisons.items())), "zone_result_counts": dict(sorted(Counter(r.get("zone_result", "") for r in rows if r.get("zone_result")).items())), "breakdowns": {"side": dict(sorted(side_counts.items())), "regime": dict(sorted(regime_counts.items())), "setup_family": dict(sorted(setup_counts.items()))}, "actual_evidence": {"status": "provided" if trade_episodes else "missing", "eligible_rows": len(actual_rows), "unique_episode_count": actual_episode_count, "high_confidence_rows": sum(r.get("actual_link_confidence") == "high" for r in actual_rows), "medium_confidence_rows": sum(r.get("actual_link_confidence") == "medium" for r in actual_rows)}, "link_confidence_coverage": dict(sorted(Counter(r.get("actual_link_confidence", "") for r in rows if r.get("actual_link_confidence")).items())), "issue_flags": dict(sorted(issue_counts.items())), "issue_summary": issue_summary, "review_queue_size": len(queue), "p9_readiness": readiness, "global_stop_opportunity": {"global_stop_present": sum(r.get("operator_class") == "STOP_OR_EXIT" for r in rows) > 0, "stop_rows": sum(r.get("operator_class") == "STOP_OR_EXIT" for r in rows), "opposite_side_exists": issue_counts.get("opposite_side_exists", 0), "counterfactual_B": issue_counts.get("opposite_side_counterfactual_B", 0), "counterfactual_C": issue_counts.get("opposite_side_counterfactual_C", 0), "not_eligible": issue_counts.get("opposite_side_not_eligible", 0), "issue_001_qualified_rows": issue_counts.get("P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY", 0)}, "no_automatic_tuning": True}
        csv_text = _csv_text(TRIAL_FACT_HEADERS, rows)
        queue_text = _csv_text(QUEUE_HEADERS, queue)
        report["ok"] = True; report["exit_code"] = 0
        json_text = json.dumps(report | {"report_written": True}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        md_text = _markdown(report)
        if dry_run:
            return report
        for path in (output_csv, output_queue_csv, output_json, output_md):
            if path.exists() and not replace_output:
                return {"ok": False, "exit_code": 4, "errors": ["existing_output_schema_mismatch"], "report_written": False}
        try:
            _atomic([(output_csv, csv_text), (output_queue_csv, queue_text), (output_json, json_text), (output_md, md_text)])
        except OSError:
            return {"ok": False, "exit_code": 4, "errors": ["output_transaction_failed"], "report_written": False}
        report["report_written"] = True
        return report


build_manual_operator_trial_report = build_manual_operator_trial_evidence
