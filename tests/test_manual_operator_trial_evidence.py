from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.feedback.manual_operator_classifier import OUTPUT_HEADERS
from src.feedback.manual_operator_trial_evidence import EXACT_OBSERVATION_HEADERS, ISSUE_RESOLUTION_METADATA, TRIAL_FACT_HEADERS, _counterfactual_classification, _issue_flags, _status, build_manual_operator_trial_evidence
from src.feedback.manual_decision_events import DECISION_HEADERS
from src.feedback.manual_trade_episode_builder import EPISODE_HEADERS
from src.feedback.manual_trade_signal_linker import LINK_HEADERS
from src.feedback.manual_scenario_normalizer import EVENT_HEADERS, SCENARIO_HEADERS


class TrialEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, headers: list[str], rows: list[dict[str, str]]) -> Path:
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def fixtures(self, *, operator: str = "A_FORMAL", outcome: str = "tp1_first") -> dict[str, Path]:
        scenario_id = "scn_" + "1" * 24
        event_id = "sce_" + "1" * 24
        scenario = {key: "" for key in SCENARIO_HEADERS}
        scenario.update(schema_version="manual_scenario.v1", scenario_id=scenario_id, symbol="BTCUSDT", side="long", setup_family="limit_retest", scenario_status="resolved", lifecycle_state="proxy_resolved", proxy_outcome=outcome)
        event = {key: "" for key in EVENT_HEADERS}
        event.update(schema_version="manual_scenario_event.v1", scenario_event_id=event_id, scenario_id=scenario_id, candidate_id="cand1", source_signal_id="sig1", event_timestamp_utc="2026-07-10T00:00:00Z", event_timestamp_jst="2026-07-10T09:00:00+09:00", grouping_status="new_scenario", symbol="BTCUSDT", side="long", setup_family="limit_retest", intraperiod_outcome=outcome, first_exit_reason=outcome)
        classification = {key: "" for key in OUTPUT_HEADERS}
        classification.update(schema_version="manual_operator_classification.v1", classification_id="opc_" + "1" * 24, classifier_method_version="manual_operator_classifier.v1", scenario_event_id=event_id, scenario_id=scenario_id, candidate_id="cand1", source_signal_id="sig1", event_timestamp_utc=event["event_timestamp_utc"], event_timestamp_jst=event["event_timestamp_jst"], symbol="BTCUSDT", side="long", setup_family="limit_retest", classification_status="classified", operator_class=operator, trade_execution_gate="pass" if operator == "A_FORMAL" else "blocked", primary_setup_status="ready", primary_setup_side="long", short_direction_min="55", short_execution_min="18", short_wait_max="75", short_tp1_rr_min="0.8", short_tp2_rr_min="1.5", long_direction_min="60", long_execution_min="22", long_wait_max="70", long_tp1_rr_min="1.0", long_tp2_rr_min="1.8")
        return {"scenarios": self.write("scenarios.csv", SCENARIO_HEADERS, [scenario]), "events": self.write("events.csv", EVENT_HEADERS, [event]), "classifications": self.write("classifications.csv", OUTPUT_HEADERS, [classification])}

    def build(self, fixtures: dict[str, Path], **kwargs: object) -> dict[str, object]:
        return build_manual_operator_trial_evidence(scenarios=fixtures["scenarios"], scenario_events=fixtures["events"], classifications=fixtures["classifications"], output_csv=self.root / "facts.csv", output_queue_csv=self.root / "queue.csv", output_json=self.root / "report.json", output_md=self.root / "report.md", report_date="20260710", **kwargs)

    def actual_inputs(self, confidence: str = "high") -> tuple[Path, Path]:
        episode = {key: "" for key in EPISODE_HEADERS}
        episode.update(schema_version="manual_trade_episode.v1", episode_id="ep1", position_id="pos1", symbol="BTCUSDT", side="long", opened_at_utc="2026-07-10T00:30:00Z", closed_at_utc="2026-07-10T01:30:00Z", status="closed", realized_pnl="10", fee_total="2", association_status="matched")
        link = {key: "" for key in LINK_HEADERS}
        link.update(schema_version="manual_trade_signal_link.v2", link_id="ln1", episode_id="ep1", signal_id="sig1", position_side="long", link_confidence=confidence, link_status="linked", side_compatibility="match", symbol_compatibility="match")
        return self.write("episodes.csv", EPISODE_HEADERS, [episode]), self.write("links.csv", LINK_HEADERS, [link])

    def paired_fixtures(self, *, short_direction: str = "80", stop_cause: str = "global") -> dict[str, Path]:
        scenarios, events, classifications = [], [], []
        for index, side in enumerate(("long", "short")):
            scenario_id = f"scn_{side}_{index:023d}"
            event_id = f"sce_{side}_{index:023d}"
            scenario = {key: "" for key in SCENARIO_HEADERS}
            scenario.update(schema_version="manual_scenario.v1", scenario_id=scenario_id, symbol="BTCUSDT", side=side, setup_family="limit_retest", scenario_status="resolved", lifecycle_state="proxy_resolved", proxy_outcome="tp1_first")
            event = {key: "" for key in EVENT_HEADERS}
            event.update(schema_version="manual_scenario_event.v1", scenario_event_id=event_id, scenario_id=scenario_id, candidate_id=f"cand_{side}", source_signal_id="sig_pair", event_timestamp_utc=f"2026-07-10T00:0{index}:00Z", event_timestamp_jst=f"2026-07-10T09:0{index}:00+09:00", grouping_status="new_scenario", symbol="BTCUSDT", side=side, candidate_type="limit", candidate_status="allowed", setup_family="limit_retest", entry_price="100", intraperiod_outcome="tp1_first", first_exit_reason="tp1_first")
            classification = {key: "" for key in OUTPUT_HEADERS}
            classification.update(schema_version="manual_operator_classification.v1", classification_id=f"opc_{side}_{index:023d}", classifier_method_version="manual_operator_classifier.v1", scenario_event_id=event_id, scenario_id=scenario_id, candidate_id=event["candidate_id"], source_signal_id="sig_pair", event_timestamp_utc=event["event_timestamp_utc"], event_timestamp_jst=event["event_timestamp_jst"], symbol="BTCUSDT", side=side, setup_family="limit_retest", classification_status="classified", operator_class="STOP_OR_EXIT", trade_execution_gate="blocked", primary_setup_status="ready" if side == "long" else "watch", primary_setup_side=side, candidate_status="allowed", entry_price="100", rr_tp1_used="2", confidence_direction_shadow=short_direction if side == "short" else "80", confidence_execution_shadow="80", confidence_wait_shadow="20", data_quality_flag="ok", no_trade_flags="global_stop" if stop_cause == "global" else "", reason_codes="stop_no_trade_flag" if stop_cause == "global" else ("stop_data_quality" if stop_cause == "quality" else f"stop_candidate_{stop_cause}"), short_direction_min="55", short_execution_min="18", short_wait_max="75", short_tp1_rr_min="0.8", short_tp2_rr_min="1.5", long_direction_min="60", long_execution_min="22", long_wait_max="70", long_tp1_rr_min="1.0", long_tp2_rr_min="1.8")
            if stop_cause == "quality":
                classification["data_quality_flag"] = "bad"
            if stop_cause in {"invalidated", "cancelled", "expired"}:
                classification["candidate_status"] = stop_cause
                event["candidate_status"] = stop_cause
            scenarios.append(scenario); events.append(event); classifications.append(classification)
        return {"scenarios": self.write("paired-scenarios.csv", SCENARIO_HEADERS, scenarios), "events": self.write("paired-events.csv", EVENT_HEADERS, events), "classifications": self.write("paired-classes.csv", OUTPUT_HEADERS, classifications)}

    def readiness_fixtures(self, *, event_count: int = 100, actual_count: int = 30, method: str = "manual_operator_classifier.v1") -> tuple[dict[str, Path], tuple[Path, Path]]:
        scenarios, events, classifications = [], [], []
        base = datetime(2026, 7, 10, tzinfo=timezone.utc)
        class_names = ("A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE", "STOP_OR_EXIT")
        actual_indices = []
        for index in range(event_count):
            side = "long" if index % 2 == 0 else "short"
            operator = class_names[index % len(class_names)]
            if operator in {"A_FORMAL", "B_CHECK_15M"} and len(actual_indices) < actual_count:
                actual_indices.append(index)
            stamp = base + timedelta(minutes=index)
            scenario_id = f"scn_{index:024x}"[-28:]
            event_id = f"sce_{index:024x}"[-28:]
            signal_id = f"sig_{index:024x}"
            scenario = {key: "" for key in SCENARIO_HEADERS}; scenario.update(schema_version="manual_scenario.v1", scenario_id=scenario_id, symbol="BTCUSDT", side=side, setup_family="limit_retest", scenario_status="resolved", lifecycle_state="proxy_resolved", proxy_outcome="tp1_first")
            event = {key: "" for key in EVENT_HEADERS}; event.update(schema_version="manual_scenario_event.v1", scenario_event_id=event_id, scenario_id=scenario_id, candidate_id=f"cand_{index}", source_signal_id=signal_id, event_timestamp_utc=stamp.isoformat().replace("+00:00", "Z"), event_timestamp_jst=stamp.astimezone(timezone(timedelta(hours=9))).isoformat(), grouping_status="new_scenario", symbol="BTCUSDT", side=side, candidate_type="limit", candidate_status="allowed", setup_family="limit_retest", entry_price="100", intraperiod_outcome="tp1_first", first_exit_reason="tp1_first")
            classification = {key: "" for key in OUTPUT_HEADERS}; classification.update(schema_version="manual_operator_classification.v1", classification_id=f"opc_{index:024x}", classifier_method_version=method, scenario_event_id=event_id, scenario_id=scenario_id, candidate_id=event["candidate_id"], source_signal_id=signal_id, event_timestamp_utc=event["event_timestamp_utc"], event_timestamp_jst=event["event_timestamp_jst"], symbol="BTCUSDT", side=side, market_regime="trend", setup_family="limit_retest", classification_status="classified", operator_class=operator, trade_execution_gate="pass" if operator == "A_FORMAL" else "blocked", primary_setup_status="ready", primary_setup_side=side, candidate_status="allowed", entry_price="100", rr_tp1_used="2", confidence_direction_shadow="80", confidence_execution_shadow="80", confidence_wait_shadow="20", data_quality_flag="ok", short_direction_min="55", short_execution_min="18", short_wait_max="75", short_tp1_rr_min="0.8", short_tp2_rr_min="1.5", long_direction_min="60", long_execution_min="22", long_wait_max="70", long_tp1_rr_min="1.0", long_tp2_rr_min="1.8")
            scenarios.append(scenario); events.append(event); classifications.append(classification)
        fixtures = {"scenarios": self.write("readiness-scenarios.csv", SCENARIO_HEADERS, scenarios), "events": self.write("readiness-events.csv", EVENT_HEADERS, events), "classifications": self.write("readiness-classes.csv", OUTPUT_HEADERS, classifications)}
        episodes, links = [], []
        for episode_index, event_index in enumerate(actual_indices):
            stamp = base + timedelta(minutes=event_index, seconds=30)
            episode = {key: "" for key in EPISODE_HEADERS}; episode.update(schema_version="manual_trade_episode.v1", episode_id=f"ep_{episode_index}", position_id=f"pos_{episode_index}", symbol="BTCUSDT", side="long" if event_index % 2 == 0 else "short", opened_at_utc=stamp.isoformat().replace("+00:00", "Z"), closed_at_utc=(stamp + timedelta(minutes=10)).isoformat().replace("+00:00", "Z"), status="closed", realized_pnl="1", fee_total="0", association_status="matched")
            link = {key: "" for key in LINK_HEADERS}; link.update(schema_version="manual_trade_signal_link.v2", link_id=f"ln_{episode_index}", episode_id=episode["episode_id"], signal_id=f"sig_{event_index:024x}", link_confidence="high", link_status="linked", side_compatibility="match", symbol_compatibility="match")
            episodes.append(episode); links.append(link)
        return fixtures, (self.write("readiness-episodes.csv", EPISODE_HEADERS, episodes), self.write("readiness-links.csv", LINK_HEADERS, links))

    def test_resolved_proxy_only_and_schema(self) -> None:
        result = self.build(self.fixtures())
        self.assertTrue(result["ok"])
        self.assertEqual(result["counts"]["resolved_rows"], 1)
        self.assertEqual(result["actual_evidence"]["status"], "missing")
        with (self.root / "facts.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual((reader.fieldnames or []), TRIAL_FACT_HEADERS)
            row = next(reader)
        self.assertEqual(row["outcome_status"], "resolved_positive")
        self.assertEqual(row["comparison_status"], "aligned")

    def test_issue_lifecycle_alignment_preserves_evidence_and_readiness(self) -> None:
        result = self.build(self.fixtures())
        self.assertEqual(result["counts"], {"trial_fact_rows": 1, "resolved_rows": 1, "unresolved_rows": 0, "no_ohlcv_rows": 0, "ambiguous_rows": 0, "scenario_count": 1, "review_queue_size": 0})
        self.assertEqual(result["actual_evidence"], {"status": "missing", "eligible_rows": 0, "unique_episode_count": 0, "high_confidence_rows": 0, "medium_confidence_rows": 0})
        self.assertEqual(result["global_stop_opportunity"], {"global_stop_present": False, "stop_rows": 0, "opposite_side_exists": 0, "counterfactual_B": 0, "counterfactual_C": 0, "not_eligible": 0, "issue_001_qualified_rows": 0})
        self.assertFalse(result["p9_readiness"]["initial"]["ready"])
        self.assertFalse(result["p9_readiness"]["practical"]["ready"])
        issue_summary = result["issue_summary"]
        issue_001 = issue_summary["P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY"]
        self.assertEqual(issue_001["status"], "open hypothesis")
        self.assertEqual(issue_001["evidence_confidence"], "proxy")
        self.assertEqual(issue_001["occurrence_count"], 0)
        self.assertEqual(issue_001["resolved_evidence_count"], 0)
        self.assertEqual(issue_001["actual_backed_count"], 0)
        for key, basis in ISSUE_RESOLUTION_METADATA.items():
            issue = issue_summary[key]
            self.assertEqual(issue["status"], "resolved")
            self.assertEqual(issue["occurrence_count"], 0)
            self.assertEqual(issue["resolved_evidence_count"], 0)
            self.assertEqual(issue["actual_backed_count"], 0)
            self.assertEqual(issue["resolution_confidence"], "accepted_implementation")
            self.assertEqual(issue["resolution_basis"], basis["resolution_basis"])
            self.assertTrue(issue["resolution_basis"])

    def test_resolved_negative_keeps_outcome_separate_from_comparison(self) -> None:
        self.build(self.fixtures(outcome="sl_first"))
        with (self.root / "facts.csv").open(newline="", encoding="utf-8") as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["outcome_status"], "resolved_negative")
        self.assertEqual(row["comparison_status"], "too_aggressive")

    def test_comparison_precedence_for_classes_and_outcomes(self) -> None:
        for cls, outcome, expected in (
            ("A_FORMAL", "tp1_first", "aligned"),
            ("B_CHECK_15M", "tp1_first", "aligned"),
            ("C_WATCH_ZONE", "tp1_first", "too_defensive"),
            ("STOP_OR_EXIT", "tp1_first", "too_defensive"),
            ("A_FORMAL", "sl_first", "too_aggressive"),
            ("B_CHECK_15M", "sl_first", "too_aggressive"),
            ("C_WATCH_ZONE", "sl_first", "aligned"),
            ("STOP_OR_EXIT", "sl_first", "aligned"),
        ):
            row = {"selected_operator_class": cls, "normalized_outcome_status": "resolved_positive" if outcome == "tp1_first" else "resolved_negative"}
            self.assertEqual(_status(row), expected)
        self.assertEqual(_status({"selected_operator_class": "A_FORMAL", "normalized_outcome_status": "resolved_negative", "direction_result": ""}), "too_aggressive")

    def test_wrong_side_requires_explicit_direction_evidence(self) -> None:
        base = {"selected_operator_class": "A_FORMAL", "normalized_outcome_status": "resolved_positive", "direction_result": ""}
        self.assertNotEqual(_status(base), "wrong_side")
        base["direction_result"] = "wrong_side"
        self.assertEqual(_status(base), "wrong_side")
        base["normalized_outcome_status"] = "pending"
        self.assertEqual(_status(base), "unresolved")

    def test_stop_proxy_flags_are_explicit(self) -> None:
        self.assertIn("stop_useful_proxy", _issue_flags({"selected_operator_class": "STOP_OR_EXIT", "normalized_outcome_status": "resolved_negative"}, "aligned", False))
        self.assertIn("stop_false_alarm_proxy", _issue_flags({"selected_operator_class": "STOP_OR_EXIT", "normalized_outcome_status": "resolved_positive"}, "too_defensive", False))

    def test_counterfactual_requires_evidence_and_separates_b_c(self) -> None:
        event = {"side": "short", "entry_price": "100", "candidate_status": "allowed", "event_timestamp_utc": "2026-07-10T00:00:00Z", "event_timestamp_jst": "2026-07-10T09:00:00+09:00", "grouping_status": "new_scenario"}
        evidence = {"side": "short", "primary_setup_side": "short", "primary_setup_status": "watch", "candidate_status": "allowed", "data_quality_flag": "ok", "trade_execution_gate": "blocked", "entry_price": "100", "confidence_direction_shadow": "80", "confidence_execution_shadow": "80", "confidence_wait_shadow": "20", "rr_tp1_used": "2", "short_direction_min": "55", "short_execution_min": "18", "short_wait_max": "75", "short_tp1_rr_min": "0.8", "short_tp2_rr_min": "1.5"}
        self.assertEqual(_counterfactual_classification(evidence, event), "counterfactual_B")
        evidence["confidence_direction_shadow"] = "10"
        self.assertEqual(_counterfactual_classification(evidence, event), "counterfactual_C")
        evidence["primary_setup_side"] = "long"
        self.assertEqual(_counterfactual_classification(evidence, event), "not_eligible")

    def test_actual_optional_and_low_link_queue(self) -> None:
        fixtures = self.fixtures()
        episodes, links = self.actual_inputs("high")
        result = self.build(fixtures, trade_episodes=episodes, episode_links=links)
        self.assertEqual(result["actual_evidence"]["eligible_rows"], 1)
        episodes, links = self.actual_inputs("low")
        result = self.build(fixtures, trade_episodes=episodes, episode_links=links, replace_output=True)
        self.assertEqual(result["actual_evidence"]["eligible_rows"], 0)
        with (self.root / "queue.csv").open(newline="", encoding="utf-8") as handle:
            self.assertTrue(any(row["question_type"] == "ambiguous_actual_trade_link" for row in csv.DictReader(handle)))

    def test_exact_link_observation_is_separate_and_non_policy(self) -> None:
        fixtures = self.fixtures(operator="C_WATCH_ZONE")
        episodes, links = self.actual_inputs("high")
        result = self.build(fixtures, trade_episodes=episodes, episode_links=links, output_exact_link_csv=self.root / "exact.csv")
        self.assertEqual(result["counts"]["trial_fact_rows"], 1)
        self.assertEqual(result["actual_evidence"]["eligible_rows"], 1)
        self.assertEqual(result["exact_link_observations"]["eligible_rows"], 1)
        with (self.root / "exact.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle); self.assertEqual(reader.fieldnames, EXACT_OBSERVATION_HEADERS); row = next(reader)
        self.assertEqual(row["operator_class"], "C_WATCH_ZONE")
        self.assertEqual(row["observation_basis"], "exact_signal_side_candidate_link")
        self.assertEqual(row["causality_status"], "not_claimed")
        self.assertEqual(row["policy_denominator_eligible"], "false")
        self.assertEqual(row["p9_readiness_eligible"], "false")
        self.assertNotIn("mfe", row); self.assertNotIn("mae", row); self.assertNotIn("comparison_status", row)

    def test_exact_link_observation_omitted_preserves_existing_callers(self) -> None:
        result = self.build(self.fixtures())
        self.assertEqual(result["exact_link_observations"]["status"], "omitted")
        self.assertFalse((self.root / "exact.csv").exists())

    def test_unresolved_no_ohlcv_excluded(self) -> None:
        result = self.build(self.fixtures(outcome="no_ohlcv"))
        self.assertEqual(result["counts"]["no_ohlcv_rows"], 1)
        self.assertEqual(result["comparison"], {})

    def test_stop_opposite_side_issue_is_offline(self) -> None:
        result = self.build(self.fixtures(operator="STOP_OR_EXIT", outcome="tp1_first"))
        self.assertTrue(result["no_automatic_tuning"])
        self.assertIn("global_stop_opportunity", result)

    def test_paired_global_stop_counterfactual_b_is_qualified(self) -> None:
        result = self.build(self.paired_fixtures())
        opportunity = result["global_stop_opportunity"]
        self.assertGreaterEqual(opportunity["opposite_side_exists"], 1)
        self.assertGreaterEqual(opportunity["counterfactual_B"], 1)
        self.assertEqual(opportunity["counterfactual_C"], 0)
        self.assertGreaterEqual(opportunity["issue_001_qualified_rows"], 1)
        self.assertTrue(result["no_automatic_tuning"])
        with (self.root / "facts.csv").open(newline="", encoding="utf-8") as handle:
            self.assertTrue(any("P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY" in row["issue_flags"] for row in csv.DictReader(handle)))

    def test_paired_global_stop_counterfactual_c_is_qualified(self) -> None:
        result = self.build(self.paired_fixtures(short_direction="10"))
        opportunity = result["global_stop_opportunity"]
        self.assertGreaterEqual(opportunity["counterfactual_C"], 1)
        self.assertGreaterEqual(opportunity["issue_001_qualified_rows"], 1)

    def test_non_global_stop_causes_are_not_issue_001(self) -> None:
        for cause in ("quality", "invalidated", "cancelled", "expired"):
            result = self.build(self.paired_fixtures(stop_cause=cause), replace_output=True)
            self.assertEqual(result["global_stop_opportunity"]["issue_001_qualified_rows"], 0, cause)

    def test_opposite_side_counters_are_independent(self) -> None:
        result = self.build(self.paired_fixtures())
        opportunity = result["global_stop_opportunity"]
        self.assertEqual(opportunity["opposite_side_exists"], opportunity["counterfactual_B"] + opportunity["counterfactual_C"] + opportunity["not_eligible"])

    def test_blank_quality_and_unsupported_gate_never_become_b(self) -> None:
        event = {"side": "short", "entry_price": "100", "candidate_status": "allowed", "event_timestamp_utc": "2026-07-10T00:00:00Z", "event_timestamp_jst": "2026-07-10T09:00:00+09:00", "grouping_status": "new_scenario"}
        evidence = {"side": "short", "primary_setup_side": "short", "primary_setup_status": "watch", "candidate_status": "allowed", "data_quality_flag": "", "trade_execution_gate": "blocked", "entry_price": "100", "confidence_direction_shadow": "80", "confidence_execution_shadow": "80", "confidence_wait_shadow": "20", "rr_tp1_used": "2", "short_direction_min": "55", "short_execution_min": "18", "short_wait_max": "75", "short_tp1_rr_min": "0.8", "short_tp2_rr_min": "1.5"}
        self.assertNotEqual(_counterfactual_classification(evidence, event), "counterfactual_B")
        evidence["data_quality_flag"] = "ok"; evidence["trade_execution_gate"] = "unknown"
        self.assertNotEqual(_counterfactual_classification(evidence, event), "counterfactual_B")

    def test_p9_readiness_below_threshold(self) -> None:
        result = self.build(self.fixtures())
        self.assertFalse(result["p9_readiness"]["initial"]["ready"])
        self.assertFalse(result["p9_readiness"]["practical"]["ready"])
        self.assertEqual(result["p9_readiness"]["practical"]["validation_window_status"], "not_established")

    def test_p9_initial_readiness_exact_boundary_and_below_boundaries(self) -> None:
        fixtures, actual = self.readiness_fixtures(event_count=100, actual_count=30)
        result = self.build(fixtures, trade_episodes=actual[0], episode_links=actual[1])
        self.assertTrue(result["p9_readiness"]["initial"]["ready"])
        self.assertFalse(result["p9_readiness"]["practical"]["ready"])
        fixtures, actual = self.readiness_fixtures(event_count=99, actual_count=30)
        self.assertFalse(self.build(fixtures, trade_episodes=actual[0], episode_links=actual[1], replace_output=True)["p9_readiness"]["initial"]["ready"])
        fixtures, actual = self.readiness_fixtures(event_count=100, actual_count=29)
        self.assertFalse(self.build(fixtures, trade_episodes=actual[0], episode_links=actual[1], replace_output=True)["p9_readiness"]["initial"]["ready"])

    def test_classifier_version_is_read_from_input(self) -> None:
        fixtures, actual = self.readiness_fixtures(event_count=1, actual_count=0, method="manual_operator_classifier.test.v9")
        result = self.build(fixtures, trade_episodes=actual[0], episode_links=actual[1])
        self.assertEqual(result["classifier_method_version"], "manual_operator_classifier.test.v9")

    def test_reproducibility_metadata_is_deterministic(self) -> None:
        result = self.build(self.fixtures())
        self.assertEqual(len(result["input_fingerprints"]), 3)
        self.assertEqual(result["replay_method_version"], "manual_operator_historical_replay.v1")
        self.assertEqual(result["eligible_actual_link_policy"], ["high", "medium"])
        self.assertTrue(result["unresolved_no_ohlcv_separated"])

    def test_dry_run_does_not_write(self) -> None:
        result = self.build(self.fixtures(), dry_run=True)
        self.assertFalse(result["report_written"])
        self.assertFalse((self.root / "facts.csv").exists())

    def test_deterministic_rerun_and_privacy(self) -> None:
        self.build(self.fixtures())
        first = tuple((self.root / name).read_bytes() for name in ("facts.csv", "queue.csv", "report.json", "report.md"))
        self.build(self.fixtures(), replace_output=True)
        second = tuple((self.root / name).read_bytes() for name in ("facts.csv", "queue.csv", "report.json", "report.md"))
        self.assertEqual(first, second)
        report = (self.root / "report.json").read_text(encoding="utf-8")
        self.assertNotIn(str(self.root), report)
        self.assertNotIn("manual_note", report)

    def test_atomic_rollback_preserves_all_outputs(self) -> None:
        fixtures = self.fixtures()
        self.build(fixtures)
        before = tuple((self.root / name).read_bytes() for name in ("facts.csv", "queue.csv", "report.json", "report.md"))
        original_replace = Path.replace
        calls = {"count": 0}

        def fail_second_replace(path: Path, target: Path) -> Path:
            calls["count"] += 1
            if calls["count"] == 2:
                raise OSError("injected replacement failure")
            return original_replace(path, target)

        with patch("src.feedback.manual_operator_trial_evidence.Path.replace", side_effect=fail_second_replace):
            result = self.build(fixtures, replace_output=True)
        self.assertEqual(result["exit_code"], 4)
        after = tuple((self.root / name).read_bytes() for name in ("facts.csv", "queue.csv", "report.json", "report.md"))
        self.assertEqual(before, after)
        self.assertEqual(list(self.root.glob(".p8-backup*")), [])

    def test_future_context_rejected(self) -> None:
        fixtures = self.fixtures()
        with fixtures["events"].open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["event_timestamp_utc"] = "bad"
        fixtures["events"] = self.write("future.csv", EVENT_HEADERS, rows)
        result = self.build(fixtures)
        self.assertFalse(result["ok"])
        self.assertEqual(result["exit_code"], 2)

    def test_outcome_timestamp_before_event_is_rejected(self) -> None:
        fixtures = self.fixtures()
        with fixtures["events"].open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["first_exit_time"] = "2026-07-09T23:59:00Z"
        fixtures["events"] = self.write("before-event.csv", EVENT_HEADERS, rows)
        result = self.build(fixtures)
        self.assertFalse(result["ok"])
        self.assertEqual(result["errors"], ["future_context_rejected"])


if __name__ == "__main__":
    unittest.main()
