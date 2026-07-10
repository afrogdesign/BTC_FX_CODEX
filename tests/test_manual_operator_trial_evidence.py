from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.feedback.manual_operator_classifier import OUTPUT_HEADERS
from src.feedback.manual_operator_trial_evidence import TRIAL_FACT_HEADERS, build_manual_operator_trial_evidence
from src.feedback.manual_decision_events import DECISION_HEADERS
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

    def test_resolved_proxy_only_and_schema(self) -> None:
        result = self.build(self.fixtures())
        self.assertTrue(result["ok"])
        self.assertEqual(result["counts"]["resolved_rows"], 1)
        self.assertEqual(result["actual_evidence"]["status"], "missing")
        with (self.root / "facts.csv").open(newline="", encoding="utf-8") as handle:
            self.assertEqual((csv.DictReader(handle).fieldnames or []), TRIAL_FACT_HEADERS)

    def test_actual_optional_and_low_link_queue(self) -> None:
        result = self.build(self.fixtures())
        self.assertEqual(result["actual_evidence"]["status"], "missing")
        self.assertTrue((self.root / "queue.csv").exists())

    def test_unresolved_no_ohlcv_excluded(self) -> None:
        result = self.build(self.fixtures(outcome="no_ohlcv"))
        self.assertEqual(result["counts"]["no_ohlcv_rows"], 1)
        self.assertEqual(result["comparison"], {})

    def test_stop_opposite_side_issue_is_offline(self) -> None:
        result = self.build(self.fixtures(operator="STOP_OR_EXIT", outcome="tp1_first"))
        self.assertTrue(result["no_automatic_tuning"])
        self.assertIn("global_stop_opportunity", result)

    def test_p9_readiness_below_threshold(self) -> None:
        result = self.build(self.fixtures())
        self.assertFalse(result["p9_readiness"]["initial"]["ready"])
        self.assertFalse(result["p9_readiness"]["practical"]["ready"])

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

    def test_future_context_rejected(self) -> None:
        fixtures = self.fixtures()
        with fixtures["events"].open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["event_timestamp_utc"] = "bad"
        fixtures["events"] = self.write("future.csv", EVENT_HEADERS, rows)
        result = self.build(fixtures)
        self.assertFalse(result["ok"])
        self.assertEqual(result["exit_code"], 2)


if __name__ == "__main__":
    unittest.main()
