from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from src.feedback.manual_scenario_coverage import build_manual_scenario_coverage
from src.feedback.manual_scenario_normalizer import EVENT_HEADERS, SCENARIO_HEADERS, build_manual_scenarios
from src.feedback.manual_decision_events import DECISION_HEADERS
from src.feedback.manual_trade_episode_builder import EPISODE_HEADERS
from src.feedback.manual_trade_signal_linker import LINK_HEADERS


class ManualScenarioCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, headers: list[str], rows: list[dict[str, str]]) -> Path:
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_report_denominators_and_missing_decisions(self) -> None:
        candidates = self.write("c.csv", ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"], [{"candidate_id": "c1", "source_signal_id": "s1", "timestamp_jst": "2026-07-10T10:00:00+09:00", "candidate_type": "active_limit_retest", "side": "long", "entry_price": "60000"}, {"candidate_id": "c2", "source_signal_id": "s2", "timestamp_jst": "2026-07-10T11:00:00+09:00", "candidate_type": "active_limit_retest", "side": "long", "entry_price": "60010"}])
        scenarios, events = self.root / "s.csv", self.root / "e.csv"
        build_manual_scenarios(candidates=candidates, scenarios_out=scenarios, events_out=events)
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, output_json=self.root / "r.json", output_md=self.root / "r.md", report_date="20260710")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["candidate_to_scenario_compression_ratio"], 2.0)
        self.assertEqual(payload["independent_scenario_rate"], 0.5)
        self.assertEqual(payload["decision_file_status"], "absent")
        self.assertTrue((self.root / "r.md").exists())
        self.assertNotIn("human made no decisions", (self.root / "r.md").read_text(encoding="utf-8").lower())

    def test_invalid_scenario_schema_does_not_write_report(self) -> None:
        candidates = self.write("c.csv", ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side"], [])
        scenarios = self.write("s.csv", ["schema_version"], [])
        events = self.write("e.csv", ["schema_version"], [])
        output = self.root / "report.md"
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, output_md=output)
        self.assertFalse(payload["ok"])
        self.assertFalse(output.exists())

    def test_dry_run_creates_no_outputs(self) -> None:
        candidates = self.write("c.csv", ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"], [{"candidate_id": "c1", "source_signal_id": "s1", "timestamp_jst": "2026-07-10T10:00:00+09:00", "candidate_type": "active_limit_retest", "side": "long", "entry_price": "60000"}])
        scenarios, events = self.root / "s.csv", self.root / "e.csv"
        build_manual_scenarios(candidates=candidates, scenarios_out=scenarios, events_out=events)
        output_json, output_md = self.root / "r.json", self.root / "r.md"
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, output_json=output_json, output_md=output_md, dry_run=True)
        self.assertEqual(payload["exit_code"], 0)
        self.assertFalse(output_json.exists())
        self.assertFalse(output_md.exists())

    def _base(self) -> tuple[Path, Path, Path]:
        candidates = self.write("c.csv", ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"], [{"candidate_id": "c1", "source_signal_id": "s1", "timestamp_jst": "2026-07-10T10:00:00+09:00", "candidate_type": "active_limit_retest", "side": "long", "entry_price": "60000"}])
        scenarios, events = self.root / "s.csv", self.root / "e.csv"
        build_manual_scenarios(candidates=candidates, scenarios_out=scenarios, events_out=events)
        return candidates, scenarios, events

    def test_missing_supplied_outcome_fails(self) -> None:
        candidates, scenarios, events = self._base()
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, intraperiod_outcomes=self.root / "missing.csv", output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["exit_code"], 2)

    def test_missing_supplied_p3_input_fails(self) -> None:
        candidates, scenarios, events = self._base()
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, episodes=self.root / "missing.ep.csv", episode_links=self.root / "missing.link.csv", output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["exit_code"], 2)

    def test_p3_inputs_must_be_supplied_together(self) -> None:
        candidates, scenarios, events = self._base()
        episodes = self.write("episodes.csv", EPISODE_HEADERS, [])
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, episodes=episodes, output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertEqual(payload["exit_code"], 2)

    def test_pending_excludes_no_ohlcv(self) -> None:
        candidates, scenarios, events = self._base()
        with events.open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        row["intraperiod_outcome"] = "no_ohlcv"
        self.write("e2.csv", EVENT_HEADERS, [row])
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=self.root / "e2.csv", output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertEqual(payload["pending_candidate_rows"], 0)
        self.assertEqual(payload["no_ohlcv_candidate_rows"], 1)

    def test_effective_decisions_and_orphan(self) -> None:
        candidates, scenarios, events = self._base()
        with scenarios.open(newline="", encoding="utf-8") as fp:
            scenario_id = next(csv.DictReader(fp))["scenario_id"]
        decisions = self.root / "d.csv"
        rows = [{"schema_version": "manual_decision_event.v1", "decision_event_id": "mde_" + "a" * 24, "event_fingerprint": "f1", "identity_scope": "scenario", "scenario_id": scenario_id, "signal_id": "", "human_action": "skipped", "decision_stage": "entry", "supersedes_decision_event_id": "", "record_status": "active"}, {"schema_version": "manual_decision_event.v1", "decision_event_id": "mde_" + "b" * 24, "event_fingerprint": "f2", "identity_scope": "scenario", "scenario_id": scenario_id, "signal_id": "", "human_action": "watched_no_entry", "decision_stage": "entry", "supersedes_decision_event_id": "mde_" + "a" * 24, "record_status": "correction"}, {"schema_version": "manual_decision_event.v1", "decision_event_id": "mde_" + "c" * 24, "event_fingerprint": "f3", "identity_scope": "scenario", "scenario_id": "scn_" + "c" * 24, "signal_id": "", "human_action": "skipped", "decision_stage": "entry", "supersedes_decision_event_id": "", "record_status": "active"}]
        padded = [{key: row.get(key, "") for key in DECISION_HEADERS} for row in rows]
        with decisions.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=DECISION_HEADERS); writer.writeheader(); writer.writerows(padded)
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, decision_events=decisions, output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertEqual(payload["decision_history_row_count"], 3)
        self.assertEqual(payload["effective_decision_event_count"], 2)
        self.assertEqual(payload["orphan_decision_event_count"], 1)
        self.assertEqual(payload["scenario_decision_coverage_rate"], 1.0)

    def test_report_json_contains_written_true(self) -> None:
        candidates, scenarios, events = self._base()
        output_json, output_md = self.root / "r.json", self.root / "r.md"
        build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, output_json=output_json, output_md=output_md)
        self.assertTrue(json.loads(output_json.read_text(encoding="utf-8"))["report_written"])

    def test_default_output_requires_report_date(self) -> None:
        candidates, scenarios, events = self._base()
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events)
        self.assertEqual(payload["exit_code"], 2)

    def test_explicit_paths_allow_blank_report_date(self) -> None:
        candidates, scenarios, events = self._base()
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertEqual(payload["exit_code"], 0)

    def test_deterministic_report_bytes(self) -> None:
        candidates, scenarios, events = self._base()
        j, m = self.root / "r.json", self.root / "r.md"
        build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, output_json=j, output_md=m, report_date="20260710")
        first = (j.read_bytes(), m.read_bytes())
        build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=events, output_json=j, output_md=m, report_date="20260710")
        self.assertEqual(first, (j.read_bytes(), m.read_bytes()))

    def test_duplicate_scenario_id_fails(self) -> None:
        candidates, scenarios, events = self._base()
        with scenarios.open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        self.write("dup_s.csv", SCENARIO_HEADERS, [row, row])
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=self.root / "dup_s.csv", scenario_events=events, output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertEqual(payload["exit_code"], 2)

    def test_duplicate_event_id_fails(self) -> None:
        candidates, scenarios, events = self._base()
        with events.open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        self.write("dup_e.csv", EVENT_HEADERS, [row, row])
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=self.root / "dup_e.csv", output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertEqual(payload["exit_code"], 2)

    def test_covered_is_not_missing(self) -> None:
        candidates, scenarios, events = self._base()
        with events.open(newline="", encoding="utf-8") as fp:
            event = next(csv.DictReader(fp))
        event["ohlcv_coverage_status"] = "covered"; event["ohlcv_gap_reason"] = "covered"
        covered_events = self.write("covered_e.csv", EVENT_HEADERS, [event])
        _, payload = build_manual_scenario_coverage(candidates=candidates, scenarios=scenarios, scenario_events=covered_events, output_json=self.root / "r.json", output_md=self.root / "r.md")
        self.assertEqual(payload["covered_candidate_rows"], 1)
        self.assertEqual(payload["no_ohlcv_candidate_rows"], 0)

    def test_pair_report_transaction_rolls_back(self) -> None:
        from src.feedback.manual_scenario_coverage import _atomic_text_pair
        report_json = self.root / "report.json"; report_md = self.root / "report.md"
        report_json.write_bytes(b"old-json"); report_md.write_bytes(b"old-md")
        original_replace = Path.replace
        calls = {"count": 0}
        def replace(path: Path, target: Path) -> Path:
            calls["count"] += 1
            if calls["count"] == 4:
                raise OSError("injected second replacement failure")
            return original_replace(path, target)
        with patch.object(Path, "replace", replace):
            with self.assertRaises(OSError):
                _atomic_text_pair(report_json, "new-json", report_md, "new-md")
        self.assertEqual(report_json.read_bytes(), b"old-json")
        self.assertEqual(report_md.read_bytes(), b"old-md")
        self.assertEqual(list(self.root.glob(".p4-*")), [])

    def test_cli_success_and_expected_input_error(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        candidates, _, _ = self._base()
        scenarios, events = self.root / "cli_s.csv", self.root / "cli_e.csv"
        command = [sys.executable, str(repo / "tools" / "log_feedback.py"), "build-manual-scenarios", "--candidates", str(candidates), "--scenarios-out", str(scenarios), "--events-out", str(events), "--stdout-json"]
        success = subprocess.run(command, cwd=repo, text=True, capture_output=True, check=False)
        self.assertEqual(success.returncode, 0)
        self.assertEqual(len(success.stdout.strip().splitlines()), 1)
        self.assertNotIn("Traceback", success.stderr)
        self.assertTrue(json.loads(success.stdout)["ok"])
        bad = subprocess.run([*command[:-1], "--candidates", str(self.root / "missing.csv"), "--stdout-json"], cwd=repo, text=True, capture_output=True, check=False)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(len(bad.stdout.strip().splitlines()), 1)
        self.assertNotIn("Traceback", bad.stderr)


if __name__ == "__main__":
    unittest.main()
