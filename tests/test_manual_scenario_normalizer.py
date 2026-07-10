from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.feedback.manual_scenario_normalizer import (
    EVENT_HEADERS,
    SCENARIO_HEADERS,
    build_manual_scenarios,
)


class ManualScenarioNormalizerTests(unittest.TestCase):
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

    def candidate(self, cid: str, ts: str, **extra: str) -> dict[str, str]:
        row = {"candidate_id": cid, "source_signal_id": cid + "-sig", "timestamp_jst": ts, "candidate_type": "active_limit_retest", "side": "long", "entry_price": "60000"}
        row.update(extra)
        return row

    def test_one_candidate_and_deterministic_repeat(self) -> None:
        candidates = self.write("candidates.csv", ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"], [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        scenarios, events = self.root / "scenarios.csv", self.root / "events.csv"
        first = build_manual_scenarios(candidates=candidates, scenarios_out=scenarios, events_out=events)
        bytes1 = (scenarios.read_bytes(), events.read_bytes())
        second = build_manual_scenarios(candidates=candidates, scenarios_out=scenarios, events_out=events)
        self.assertEqual(first["scenario_count"], 1)
        self.assertEqual(second["exit_code"], 0)
        self.assertEqual(bytes1, (scenarios.read_bytes(), events.read_bytes()))

    def test_overlapping_update_groups_and_side_change_does_not(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("candidates.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00"), self.candidate("c2", "2026-07-10T11:00:00+09:00", entry_price="60010"), self.candidate("c3", "2026-07-10T11:30:00+09:00", side="short")])
        result = build_manual_scenarios(candidates=candidates, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        self.assertEqual(result["scenario_count"], 2)

    def test_duplicate_and_conflict(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        duplicate = self.write("dup.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00"), self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        result = build_manual_scenarios(candidates=duplicate, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        self.assertEqual(result["duplicate_candidate_rows"], 1)
        conflict = self.write("conflict.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00"), self.candidate("c1", "2026-07-10T10:00:00+09:00", entry_price="60100")])
        result = build_manual_scenarios(candidates=conflict, scenarios_out=self.root / "s2.csv", events_out=self.root / "e2.csv")
        self.assertEqual(result["exit_code"], 3)

    def test_no_ohlcv_is_coverage_failure(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        outcomes = self.write("o.csv", ["candidate_id", "outcome"], [{"candidate_id": "c1", "outcome": "no_ohlcv"}])
        result = build_manual_scenarios(candidates=candidates, intraperiod_outcomes=outcomes, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        self.assertEqual(result["exit_code"], 0)
        with (self.root / "s.csv").open(newline="", encoding="utf-8") as fp:
            self.assertEqual(next(csv.DictReader(fp))["scenario_status"], "coverage_missing")

    def test_dry_run_does_not_create_outputs(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        scenarios, events = self.root / "s.csv", self.root / "e.csv"
        result = build_manual_scenarios(candidates=candidates, scenarios_out=scenarios, events_out=events, dry_run=True)
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(scenarios.exists())
        self.assertFalse(events.exists())


if __name__ == "__main__":
    unittest.main()
