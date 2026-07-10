from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.feedback.manual_scenario_coverage import build_manual_scenario_coverage
from src.feedback.manual_scenario_normalizer import build_manual_scenarios


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


if __name__ == "__main__":
    unittest.main()
