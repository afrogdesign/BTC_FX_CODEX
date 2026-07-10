from __future__ import annotations

import csv
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from src.feedback.manual_scenario_normalizer import (
    EVENT_HEADERS,
    SCENARIO_HEADERS,
    build_manual_scenarios,
    _event_id,
    _hash,
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

    def test_exact_id_formulas_exclude_signal_and_fingerprint(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price", "stop_loss"]
        candidates = self.write("id.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00", stop_loss="59000")])
        scenarios, events = self.root / "s.csv", self.root / "e.csv"
        build_manual_scenarios(candidates=candidates, scenarios_out=scenarios, events_out=events)
        with scenarios.open(newline="", encoding="utf-8") as fp:
            scenario = next(csv.DictReader(fp))
        expected = "scn_" + _hash("BTCUSDT", "long", "limit_retest", "2026-07-10T10:00:00+09:00", "60000", "60000", "59000", "manual_scenario_normalization.v1")[:24]
        self.assertEqual(scenario["scenario_id"], expected)
        with events.open(newline="", encoding="utf-8") as fp:
            event = next(csv.DictReader(fp))
        self.assertEqual(event["scenario_event_id"], "sce_" + _hash("c1", event["candidate_fingerprint"], "new_scenario", "manual_scenario_normalization.v1")[:24])

    def test_outcome_identity_conflict_and_empty_id_fail_closed(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        outcomes = self.write("o.csv", ["candidate_id", "outcome", "first_exit_time"], [{"candidate_id": "c1", "outcome": "tp1_first", "first_exit_time": "2026-07-10T10:30:00+09:00"}, {"candidate_id": "c1", "outcome": "tp1_first", "first_exit_time": "2026-07-10T10:31:00+09:00"}])
        result = build_manual_scenarios(candidates=candidates, intraperiod_outcomes=outcomes, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        self.assertEqual(result["exit_code"], 3)
        empty = self.write("empty.csv", ["candidate_id", "outcome"], [{"candidate_id": "", "outcome": "pending"}])
        self.assertEqual(build_manual_scenarios(candidates=candidates, intraperiod_outcomes=empty, scenarios_out=self.root / "s2.csv", events_out=self.root / "e2.csv")["exit_code"], 2)

    def test_missing_or_malformed_outcome_fails(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        missing = build_manual_scenarios(candidates=candidates, intraperiod_outcomes=self.root / "missing.csv", scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        self.assertEqual(missing["exit_code"], 2)
        malformed = self.write("bad.csv", ["candidate_id", "outcome", "first_exit_time"], [{"candidate_id": "c1", "outcome": "pending", "first_exit_time": "bad"}])
        self.assertEqual(build_manual_scenarios(candidates=candidates, intraperiod_outcomes=malformed, scenarios_out=self.root / "s2.csv", events_out=self.root / "e2.csv")["exit_code"], 2)

    def test_terminal_boundary_before_and_after(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00"), self.candidate("c2", "2026-07-10T10:20:00+09:00"), self.candidate("c3", "2026-07-10T10:31:00+09:00")])
        outcomes = self.write("o.csv", ["candidate_id", "outcome", "first_exit_time"], [{"candidate_id": "c1", "outcome": "tp1_first", "first_exit_time": "2026-07-10T10:30:00+09:00"}])
        result = build_manual_scenarios(candidates=candidates, intraperiod_outcomes=outcomes, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        self.assertEqual(result["scenario_count"], 2)
        with (self.root / "s.csv").open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(rows[0]["terminal_at_jst"], "2026-07-10T10:30:00+09:00")

    def test_not_entered_fallback_and_zone_touch_time(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        outcomes = self.write("o.csv", ["candidate_id", "outcome", "entry_reached_time", "first_exit_time"], [{"candidate_id": "c1", "outcome": "entry_reached", "entry_reached_time": "2026-07-10T10:10:00+09:00", "first_exit_time": ""}])
        build_manual_scenarios(candidates=candidates, intraperiod_outcomes=outcomes, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        with (self.root / "s.csv").open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        self.assertEqual(row["lifecycle_state"], "zone_touched")
        self.assertEqual(row["zone_touched_at_jst"], "2026-07-10T10:10:00+09:00")
        outcomes2 = self.write("o2.csv", ["candidate_id", "outcome"], [{"candidate_id": "c1", "outcome": "not_entered"}])
        build_manual_scenarios(candidates=candidates, intraperiod_outcomes=outcomes2, scenarios_out=self.root / "s2.csv", events_out=self.root / "e2.csv")
        with (self.root / "s2.csv").open(newline="", encoding="utf-8") as fp:
            self.assertTrue(next(csv.DictReader(fp))["terminal_at_jst"])

    def test_latest_blank_does_not_erase_and_resolved_precedes_coverage(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price", "stop_loss"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00", stop_loss="59000"), self.candidate("c2", "2026-07-10T10:10:00+09:00", entry_price="60005", stop_loss="")])
        outcomes = self.write("o.csv", ["candidate_id", "outcome"], [{"candidate_id": "c1", "outcome": "tp1_first"}, {"candidate_id": "c2", "outcome": "no_ohlcv"}])
        result = build_manual_scenarios(candidates=candidates, intraperiod_outcomes=outcomes, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        self.assertEqual(result["exit_code"], 0)
        with (self.root / "s.csv").open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        self.assertEqual(row["scenario_status"], "resolved")
        self.assertEqual(row["invalidation_price"], "59000")

    def test_pending_event_type_is_explicit(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        outcomes = self.write("o.csv", ["candidate_id", "outcome"], [{"candidate_id": "c1", "outcome": "pending"}])
        build_manual_scenarios(candidates=candidates, intraperiod_outcomes=outcomes, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        with (self.root / "e.csv").open(newline="", encoding="utf-8") as fp:
            self.assertEqual(next(csv.DictReader(fp))["event_type"], "pending")

    def test_local_ohlcv_root_causes(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        ohlcv = self.write("ohlcv.csv", ["timestamp", "high", "low"], [{"timestamp": "2026-07-01T00:00:00+09:00", "high": "1", "low": "0"}])
        build_manual_scenarios(candidates=candidates, ohlcv=ohlcv, scenarios_out=self.root / "s.csv", events_out=self.root / "e.csv")
        with (self.root / "e.csv").open(newline="", encoding="utf-8") as fp:
            self.assertEqual(next(csv.DictReader(fp))["ohlcv_gap_reason"], "stale_ohlcv_range")

    def test_existing_schema_reject_and_replace(self) -> None:
        headers = ["candidate_id", "source_signal_id", "timestamp_jst", "candidate_type", "side", "entry_price"]
        candidates = self.write("c.csv", headers, [self.candidate("c1", "2026-07-10T10:00:00+09:00")])
        bad = self.write("s.csv", ["legacy"], [{"legacy": "x"}])
        result = build_manual_scenarios(candidates=candidates, scenarios_out=bad, events_out=self.root / "e.csv")
        self.assertEqual(result["exit_code"], 4)
        self.assertEqual(build_manual_scenarios(candidates=candidates, scenarios_out=bad, events_out=self.root / "e.csv", replace_output=True)["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
