"""Deterministic P4 scenario coverage report builder."""
from __future__ import annotations

import csv
import json
import os
import tempfile
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from src.feedback.manual_decision_events import DECISION_HEADERS, SCHEMA_VERSION as DECISION_SCHEMA_VERSION
from src.feedback.manual_scenario_normalizer import CANDIDATE_REQUIRED_HEADERS, EVENT_HEADERS, SCENARIO_HEADERS, SCENARIO_SCHEMA_VERSION, EVENT_SCHEMA_VERSION
from src.feedback.manual_trade_episode_builder import EPISODE_HEADERS
from src.feedback.manual_trade_signal_linker import LINK_HEADERS
from src.feedback.manual_actual_trade_importer import TRADE_HEADERS, ORDER_HEADERS, POSITION_HEADERS

SCHEMA_VERSION = "manual_scenario_coverage.v1"
SAFETY = "report-only / not FORMAL_GO / no automatic order / human decides manually"


def _read(path: Path | None, headers: list[str] | None = None, version: str | None = None, required: list[str] | None = None) -> tuple[list[dict[str, str]], str]:
    if path is None or not path.exists():
        return [], "missing"
    try:
        with path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            actual = reader.fieldnames or []
            if headers is not None and actual != headers:
                return [], "input_schema_mismatch"
            if required is not None and any(item not in actual for item in required):
                return [], "input_schema_mismatch"
            rows = [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error):
        return [], "invalid"
    if version and any(row.get("schema_version") != version for row in rows):
        return [], "input_schema_mismatch"
    return rows, "ok"


def _dec(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _atomic_text_pair(json_path: Path, json_text: str, md_path: Path, md_text: str) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    files: list[tuple[Path, str, Path]] = []
    try:
        for path, text in ((json_path, json_text), (md_path, md_text)):
            fd, name = tempfile.mkstemp(prefix=".p4-coverage-", dir=path.parent)
            os.close(fd)
            temp = Path(name)
            temp.write_text(text, encoding="utf-8")
            files.append((path, text, temp))
        backups: list[tuple[Path, Path]] = []
        replaced: list[Path] = []
        try:
            for path, _, _ in files:
                if path.exists():
                    backup = path.with_name(f".{path.name}.p4-backup")
                    backup.unlink(missing_ok=True)
                    path.replace(backup)
                    backups.append((path, backup))
            for path, _, temp in files:
                temp.replace(path)
                replaced.append(path)
        except Exception as exc:
            for path in replaced:
                path.unlink(missing_ok=True)
            for path, backup in backups:
                if backup.exists():
                    backup.replace(path)
            raise OSError("output_io_error") from exc
        finally:
            for _, backup in backups:
                backup.unlink(missing_ok=True)
    finally:
        for _, _, temp in files:
            temp.unlink(missing_ok=True)


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Manual Scenario Coverage Report", "", "## Purpose", "", "Report-only coverage of candidate rows, derived scenarios, proxy evidence, and recorded human decision events.", "", "## Input Status", "", f"- candidates: {payload['input_status']['candidates']}", f"- scenarios: {payload['input_status']['scenarios']}", f"- scenario_events: {payload['input_status']['scenario_events']}", f"- decision_events: {payload['input_status']['decision_events']}", "", "## Candidate-to-Scenario Compression", "", f"- candidate_input_rows: {payload['candidate_input_rows']}", f"- unique_candidate_rows: {payload['unique_candidate_rows']}", f"- assigned_candidate_rows: {payload['assigned_candidate_rows']}", f"- ambiguous_candidate_rows: {payload['ambiguous_candidate_rows']}", f"- scenario_count: {payload['scenario_count']}", f"- candidate_to_scenario_compression_ratio: {payload['candidate_to_scenario_compression_ratio']}", f"- independent_scenario_rate: {payload['independent_scenario_rate']}", f"- source_signal_count: {payload['source_signal_count']}", f"- signals_with_scenario_count: {payload['signals_with_scenario_count']}", f"- signal_to_scenario_coverage_rate: {payload['signal_to_scenario_coverage_rate']}", "", "## OHLCV and Proxy Coverage", "", f"- covered_candidate_rows: {payload['covered_candidate_rows']}", f"- no_ohlcv_candidate_rows: {payload['no_ohlcv_candidate_rows']}", f"- pending_candidate_rows: {payload['pending_candidate_rows']}", f"- resolved_proxy_candidate_rows: {payload['resolved_proxy_candidate_rows']}", f"- scenario_with_covered_evidence_count: {payload['scenario_with_covered_evidence_count']}", f"- scenario_with_resolved_proxy_count: {payload['scenario_with_resolved_proxy_count']}", f"- ohlcv_gap_reason_counts: {json.dumps(payload['ohlcv_gap_reason_counts'], ensure_ascii=False, sort_keys=True)}", "", "## Human Decision Coverage", "", f"- decision_file_status: {payload['decision_file_status']}", f"- decision_event_count: {payload['decision_event_count']}", f"- scenario_with_decision_count: {payload['scenario_with_decision_count']}", f"- signal_only_decision_count: {payload['signal_only_decision_count']}", f"- decision_action_counts: {json.dumps(payload['decision_action_counts'], ensure_ascii=False, sort_keys=True)}", f"- decision_stage_counts: {json.dumps(payload['decision_stage_counts'], ensure_ascii=False, sort_keys=True)}", f"- scenario_decision_coverage_rate: {payload['scenario_decision_coverage_rate']}", "", "## P3 Actual-Evidence Availability", "", f"- scenario_signal_ids_with_high_medium_episode_link: {payload['scenario_signal_ids_with_high_medium_episode_link']}", f"- scenario_count_with_actual_episode_evidence: {payload['scenario_count_with_actual_episode_evidence']}", "", "## Limitations", "", "- Candidate rows are not independent opportunities.", "- Proxy outcomes are not human actions.", "- Exchange evidence does not prove why a human acted.", "- no_ohlcv is excluded from performance outcome counts.", "- This report does not recommend threshold or gate changes.", "- This report makes no profitability claim.", "", "## Safety Boundary", "", SAFETY, ""]
    return "\n".join(lines)


def build_manual_scenario_coverage(*, candidates: Path, scenarios: Path, scenario_events: Path, intraperiod_outcomes: Path | None = None, decision_events: Path | None = None, output_json: Path | None = None, output_md: Path | None = None, episodes: Path | None = None, episode_links: Path | None = None, report_date: str | None = None, dry_run: bool = False) -> tuple[str, dict[str, Any]]:
    scenario_rows, scenario_status = _read(scenarios, SCENARIO_HEADERS, SCENARIO_SCHEMA_VERSION)
    event_rows, event_status = _read(scenario_events, EVENT_HEADERS, EVENT_SCHEMA_VERSION)
    candidate_rows, candidate_status = _read(candidates, required=CANDIDATE_REQUIRED_HEADERS)
    decision_rows, decision_status = _read(decision_events, DECISION_HEADERS, DECISION_SCHEMA_VERSION) if decision_events is not None else ([], "missing")
    outcome_rows, outcome_status = _read(intraperiod_outcomes, required=["candidate_id", "outcome"]) if intraperiod_outcomes is not None else ([], "missing")
    input_status = {"candidates": candidate_status, "scenarios": scenario_status, "scenario_events": event_status, "decision_events": decision_status, "intraperiod_outcomes": outcome_status}
    errors = [status for status in (scenario_status, event_status, candidate_status) if status != "ok"]
    if intraperiod_outcomes is not None and outcome_status != "ok":
        errors.append(outcome_status)
    if decision_events is not None and decision_status not in {"ok", "missing"}:
        errors.append(decision_status)
    if (episodes is None) != (episode_links is None):
        errors.append("input_schema_mismatch")
    if episodes is not None and not episodes.exists():
        errors.append("missing")
    if episode_links is not None and not episode_links.exists():
        errors.append("missing")
    payload: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "ok": not errors, "exit_code": 2 if errors else 0, "dry_run": dry_run, "report_written": False, "errors": errors, "input_status": input_status, "safety_boundary": SAFETY}
    if errors:
        return "", payload
    unique_scenario_ids = [str(row.get("scenario_id", "")).strip() for row in scenario_rows]
    unique_event_ids = [str(row.get("scenario_event_id", "")).strip() for row in event_rows]
    scenario_id_set = {value for value in unique_scenario_ids if value}
    if any(not str(row.get("candidate_id", "")).strip() or not str(row.get("source_signal_id", "")).strip() for row in candidate_rows):
        payload.update(ok=False, exit_code=2, errors=["input_schema_mismatch"])
        return "", payload
    if len(unique_scenario_ids) != len(scenario_id_set) or len(unique_event_ids) != len(set(unique_event_ids)):
        payload.update(ok=False, exit_code=2, errors=["input_schema_mismatch"])
        return "", payload
    if any(row.get("scenario_id") and row.get("scenario_id") not in scenario_id_set for row in event_rows):
        payload.update(ok=False, exit_code=2, errors=["input_schema_mismatch"])
        return "", payload
    decision_ids = [str(row.get("decision_event_id", "")).strip() for row in decision_rows]
    decision_by_id = {row.get("decision_event_id", ""): row for row in decision_rows}
    superseded_ids = {row.get("supersedes_decision_event_id", "") for row in decision_rows if row.get("supersedes_decision_event_id")}
    if len(decision_ids) != len(set(decision_ids)) or any(row.get("supersedes_decision_event_id") == row.get("decision_event_id") or row.get("supersedes_decision_event_id") not in decision_by_id for row in decision_rows if row.get("supersedes_decision_event_id")) or any(sum(1 for row in decision_rows if row.get("supersedes_decision_event_id") == target) > 1 for target in superseded_ids):
        payload.update(ok=False, exit_code=2, errors=["input_schema_mismatch"])
        return "", payload
    unique_ids = {str(row.get("candidate_id", "")).strip() for row in candidate_rows if row.get("candidate_id")}
    assigned = {str(row.get("candidate_id", "")).strip() for row in event_rows if row.get("scenario_id") and row.get("grouping_status") in {"new_scenario", "matched_existing"}}
    ambiguous = sum(1 for row in event_rows if row.get("grouping_status") == "ambiguous")
    source_signals = {str(row.get("source_signal_id", "")).strip() for row in candidate_rows if row.get("source_signal_id")}
    signal_scenarios = {str(row.get("source_signal_id", "")).strip() for row in event_rows if row.get("scenario_id") and row.get("source_signal_id")}
    covered = sum(1 for row in event_rows if row.get("ohlcv_coverage_status") == "covered")
    no_ohlcv = sum(1 for row in event_rows if row.get("intraperiod_outcome") == "no_ohlcv" or row.get("ohlcv_coverage_status") in {"no_ohlcv", "coverage_missing"} or str(row.get("ohlcv_gap_reason", "")).strip())
    resolved = sum(1 for row in event_rows if row.get("intraperiod_outcome") in {"tp1_first", "tp2_first", "sl_first"})
    pending = sum(1 for row in event_rows if row.get("intraperiod_outcome") in {"", "pending", "timeout", "ambiguous", "entry_reached", "no_ohlcv"})
    gaps = Counter(str(row.get("ohlcv_gap_reason", "")) for row in event_rows if row.get("ohlcv_gap_reason"))
    effective_decisions = [row for row in decision_rows if row.get("decision_event_id") not in superseded_ids]
    decisions_by_scenario = {row.get("scenario_id") for row in effective_decisions if row.get("scenario_id") in scenario_id_set}
    orphan_decisions = sum(1 for row in effective_decisions if row.get("scenario_id") and row.get("scenario_id") not in scenario_id_set)
    high_medium_ids: set[str] = set()
    evidence_scenarios: set[str] = set()
    if episodes is not None:
        episode_rows, episode_status = _read(episodes, EPISODE_HEADERS, "manual_trade_episode.v1")
        if episode_status != "ok":
            payload.update(ok=False, exit_code=2, errors=[episode_status])
            return "", payload
    if episode_links is not None:
        link_rows, link_status = _read(episode_links, LINK_HEADERS, "manual_trade_signal_link.v2")
        if link_status != "ok":
            payload.update(ok=False, exit_code=2, errors=[link_status])
            return "", payload
        for link in link_rows:
            if link.get("link_status") == "linked" and link.get("link_confidence") in {"high", "medium"}:
                signal = link.get("signal_id") or link.get("source_signal_id") or ""
                if signal and link.get("episode_id") in {row.get("episode_id") for row in episode_rows}:
                    high_medium_ids.add(signal)
        for row in event_rows:
            if row.get("source_signal_id") in high_medium_ids and row.get("scenario_id"):
                evidence_scenarios.add(row["scenario_id"])
    pending = sum(1 for row in event_rows if row.get("intraperiod_outcome") in {"", "pending", "timeout", "ambiguous", "entry_reached"})
    payload.update({
        "candidate_input_rows": len(candidate_rows), "unique_candidate_rows": len(unique_ids), "duplicate_candidate_rows": max(0, len(candidate_rows) - len(unique_ids)), "candidate_conflict_rows": 0, "assigned_candidate_rows": len(assigned), "ambiguous_candidate_rows": ambiguous, "scenario_count": len(scenario_rows), "candidate_to_scenario_compression_ratio": _ratio(len(assigned), len(scenario_rows)), "independent_scenario_rate": _ratio(len(scenario_rows), len(assigned)), "source_signal_count": len(source_signals), "signals_with_scenario_count": len(signal_scenarios), "signal_to_scenario_coverage_rate": _ratio(len(signal_scenarios), len(source_signals)), "covered_candidate_rows": covered, "no_ohlcv_candidate_rows": no_ohlcv, "pending_candidate_rows": pending, "resolved_proxy_candidate_rows": resolved, "scenario_with_covered_evidence_count": len({row.get("scenario_id") for row in event_rows if row.get("scenario_id") and row.get("ohlcv_coverage_status") == "covered"}), "scenario_with_resolved_proxy_count": len({row.get("scenario_id") for row in event_rows if row.get("scenario_id") and row.get("intraperiod_outcome") in {"tp1_first", "tp2_first", "sl_first"}}), "ohlcv_gap_reason_counts": dict(sorted(gaps.items())), "decision_history_row_count": len(decision_rows), "effective_decision_event_count": len(effective_decisions), "superseded_decision_event_count": len(superseded_ids), "orphan_decision_event_count": orphan_decisions, "decision_event_count": len(effective_decisions), "scenario_with_decision_count": len(decisions_by_scenario), "signal_only_decision_count": sum(1 for row in effective_decisions if row.get("identity_scope") == "signal_only"), "decision_action_counts": dict(sorted(Counter(row.get("human_action", "") for row in effective_decisions).items())), "decision_stage_counts": dict(sorted(Counter(row.get("decision_stage", "") for row in effective_decisions).items())), "scenario_decision_coverage_rate": min(1.0, _ratio(len(decisions_by_scenario), len(scenario_rows))), "decision_file_status": "absent" if decision_status == "missing" else decision_status, "scenario_signal_ids_with_high_medium_episode_link": len({row.get("source_signal_id") for row in event_rows if row.get("source_signal_id") in high_medium_ids}), "scenario_count_with_actual_episode_evidence": len(evidence_scenarios), "report_date": report_date or "", "episode_input_status": "not_provided" if episodes is None else "provided"})
    markdown = _markdown(payload)
    explicit_json = output_json is not None
    explicit_md = output_md is not None
    if (not explicit_json or not explicit_md) and not report_date:
        payload.update(ok=False, exit_code=2, errors=["missing_report_date"])
        return "", payload
    if output_json is None:
        output_json = Path("logs/json") / f"manual_scenario_coverage_{report_date}.json"
    if output_md is None:
        output_md = Path("運用資料/reports/post_eval") / f"manual_scenario_coverage_{report_date}.md"
    if dry_run:
        payload["would_write_outputs"] = [output_json.name, output_md.name]
        return markdown, payload
    payload["report_written"] = True
    try:
        _atomic_text_pair(output_json, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", output_md, markdown)
    except OSError:
        payload.update(ok=False, exit_code=4, errors=["output_io_error"])
        payload["report_written"] = False
        return markdown, payload
    return markdown, payload


def build_manual_scenario_coverage_report(**kwargs: Any) -> tuple[str, dict[str, Any]]:
    return build_manual_scenario_coverage(**kwargs)
