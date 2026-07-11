from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.feedback.manual_operator_classifier import SIGNAL_HEADERS
from src.feedback.manual_operator_operating_cycle import (
    OUTPUT_NAMES,
    run_p8_operating_cycle,
)
from src.feedback.manual_scenario_normalizer import (
    EVENT_HEADERS,
    SCENARIO_HEADERS,
    CANDIDATE_REQUIRED_HEADERS,
)


class OperatingCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.candidates = self._write("candidates.csv", CANDIDATE_REQUIRED_HEADERS + ["entry_price", "entry_zone_low", "entry_zone_high", "stop_loss", "tp1", "tp2"], [{
            "candidate_id": "c1", "source_signal_id": "s1", "timestamp_jst": "2026-07-10T10:00:00+09:00", "candidate_type": "active_limit_retest", "side": "long", "entry_price": "60000", "entry_zone_low": "59900", "entry_zone_high": "60100", "stop_loss": "59000", "tp1": "61000", "tp2": "62000",
        }])
        signal = {key: "" for key in SIGNAL_HEADERS}; signal.update(signal_id="s1", timestamp_jst="2026-07-10T10:00:00+09:00", primary_setup_side="long", primary_setup_status="ready", nearest_major_support='{"low": 59000, "high": 59500, "mid": 59250, "kind": "support"}', nearest_major_resistance='{"high": 61000, "low": 60500, "mid": 60750, "kind": "resistance"}')
        self.signals = self._write("signals.csv", SIGNAL_HEADERS, [signal])
        self.ohlcv = self._write("ohlcv.csv", ["timestamp_utc", "timestamp_jst", "open", "high", "low", "close", "volume", "source", "interval", "symbol"], [{"timestamp_utc": "2026-07-10T01:00:00+00:00", "timestamp_jst": "2026-07-10T10:00:00+09:00", "open": "60000", "high": "60100", "low": "59900", "close": "60050", "volume": "1", "source": "synthetic", "interval": "15m", "symbol": "BTC_USDT"}])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, name: str, headers: list[str], rows: list[dict[str, str]]) -> Path:
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=headers); writer.writeheader(); writer.writerows(rows)
        return path

    def _fake_stages(self):
        def outcomes(candidates_df, ohlcv_df, **kwargs):
            return pd.DataFrame([{"candidate_id": "c1", "outcome": "tp1_first", "entry_reached_time": "", "first_exit_time": "", "first_exit_reason": "", "intraperiod_outcome": "tp1_first"}])

        def p4(**kwargs):
            scenario = {key: "" for key in SCENARIO_HEADERS}; scenario.update(schema_version="manual_scenario.v1", scenario_id="scn1", symbol="BTCUSDT", side="long", setup_family="limit_retest")
            event = {key: "" for key in EVENT_HEADERS}; event.update(schema_version="manual_scenario_event.v1", scenario_event_id="evt1", scenario_id="scn1", candidate_id="c1", source_signal_id="s1", event_timestamp_utc="2026-07-10T01:00:00Z", event_timestamp_jst="2026-07-10T10:00:00+09:00", grouping_status="new_scenario", side="long", candidate_type="active_limit_retest", candidate_status="allowed", intraperiod_outcome="tp1_first")
            self._write_path(kwargs["scenarios_out"], SCENARIO_HEADERS, [scenario]); self._write_path(kwargs["events_out"], EVENT_HEADERS, [event])
            return {"ok": True, "exit_code": 0}

        def p5(**kwargs):
            headers = ["scenario_event_id", "candidate_id", "source_signal_id", "classifier_method_version", "operator_class", "classification_status"]
            self._write_path(kwargs["output_csv"], headers, [{"scenario_event_id": "evt1", "candidate_id": "c1", "source_signal_id": "s1", "classifier_method_version": "manual_operator_classifier.v1", "operator_class": "C_WATCH_ZONE", "classification_status": "classified"}])
            kwargs["output_json"].write_text("{}\n", encoding="utf-8"); kwargs["output_md"].write_text("summary\n", encoding="utf-8")
            return {"ok": True, "exit_code": 0, "class_counts": {"C_WATCH_ZONE": 1}}

        def p8(**kwargs):
            fact_headers = ["scenario_event_id", "scenario_id", "operator_class", "outcome_status", "signal_id"]
            self._write_path(kwargs["output_csv"], fact_headers, [{"scenario_event_id": "evt1", "scenario_id": "scn1", "operator_class": "C_WATCH_ZONE", "outcome_status": "resolved_positive", "signal_id": "s1"}])
            self._write_path(kwargs["output_queue_csv"], ["review_item_id"], [])
            kwargs["output_json"].write_text("{}\n", encoding="utf-8"); kwargs["output_md"].write_text("summary\n", encoding="utf-8")
            return {"ok": True, "exit_code": 0, "counts": {"trial_fact_rows": 1, "resolved_rows": 1, "unresolved_rows": 0, "no_ohlcv_rows": 0, "scenario_count": 1, "review_queue_size": 0}, "class_distribution": {"C_WATCH_ZONE": 1}, "breakdowns": {"side": {"long": 1}}, "comparison": {"aligned": 1}, "actual_evidence": {"status": "missing", "eligible_rows": 0, "unique_episode_count": 0}, "global_stop_opportunity": {"issue_001_qualified_rows": 0}, "p9_readiness": {"initial": {"ready": False}, "practical": {"ready": False}}}

        return patch("src.feedback.manual_operator_operating_cycle.build_active_plan_intraperiod_outcome_rows", side_effect=outcomes), patch("src.feedback.manual_operator_operating_cycle.build_manual_scenarios", side_effect=p4), patch("src.feedback.manual_operator_operating_cycle.build_manual_operator_classifier", side_effect=p5), patch("src.feedback.manual_operator_operating_cycle.build_manual_operator_trial_evidence", side_effect=p8)

    @staticmethod
    def _write_path(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=headers); writer.writeheader(); writer.writerows(rows)

    def _run(self, **kwargs):
        return run_p8_operating_cycle(candidates=self.candidates, signal_context=self.signals, ohlcv=self.ohlcv, report_date="20260711", output_root=self.root / "out", replace_output=True, **kwargs)

    def test_successful_local_cycle_and_manifest(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]:
            result = self._run()
        self.assertTrue(result["ok"]); self.assertEqual(result["counts"]["candidate_rows"], 1)
        manifest = json.loads((self.root / "out" / "cycle_manifest.json").read_text())
        self.assertIn("input_fingerprints", manifest); self.assertIn("output_fingerprints", manifest)

    def test_current_candidate_and_structured_signal_are_preserved(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        self.assertEqual(next(csv.DictReader((self.root / "out" / "candidate_slice.csv").open()))["candidate_id"], "c1")
        row = next(csv.DictReader((self.root / "out" / "signal_context_slice.csv").open())); self.assertIn('"low": 59000', row["nearest_major_support"])

    def test_only_referenced_signals_and_exact_duplicates(self) -> None:
        with self.signals.open(newline="", encoding="utf-8") as fp: row = next(csv.DictReader(fp))
        self._write("signals_dup.csv", SIGNAL_HEADERS, [row, row]); self.signals = self.root / "signals_dup.csv"
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: result = self._run()
        self.assertEqual(result["counts"]["candidate_signals"], 1); self.assertEqual(result["lineage"]["signal_duplicates"], 1)

    def test_conflicting_signal_identity_fails(self) -> None:
        with self.signals.open(newline="", encoding="utf-8") as fp: row = next(csv.DictReader(fp))
        conflict = dict(row); conflict["primary_setup_status"] = "invalid"; self.signals = self._write("signals_conflict.csv", SIGNAL_HEADERS, [row, conflict])
        result = self._run(); self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 3)

    def test_missing_signal_fails(self) -> None:
        self.signals = self._write("signals_empty.csv", SIGNAL_HEADERS, [])
        result = self._run(); self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 2)

    def test_stale_ohlcv_and_future_candidate_fail(self) -> None:
        self.ohlcv = self._write("old.csv", ["timestamp_utc", "open", "high", "low", "close"], [{"timestamp_utc": "2020-01-01T00:00:00Z", "open": "1", "high": "1", "low": "1", "close": "1"}])
        result = self._run(); self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 2)

    def test_actual_pair_contract(self) -> None:
        result = self._run(actual_episodes=self.root / "episodes.csv"); self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 2)

    def test_dry_run_has_no_output_root(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: result = self._run(dry_run=True)
        self.assertTrue(result["ok"]); self.assertFalse((self.root / "out").exists())

    def test_deterministic_rerun(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        first = {name: (self.root / "out" / name).read_bytes() for name in OUTPUT_NAMES}
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        self.assertEqual(first, {name: (self.root / "out" / name).read_bytes() for name in OUTPUT_NAMES})

    def test_replacement_failure_restores_existing_outputs(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        sentinel = (self.root / "out" / "candidate_slice.csv").read_bytes()
        with patch("src.feedback.manual_operator_operating_cycle._promote", side_effect=OSError("output_transaction_failed")):
            with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: result = self._run()
        self.assertFalse(result["ok"]); self.assertEqual((self.root / "out" / "candidate_slice.csv").read_bytes(), sentinel)

    def test_no_fetch_mode_does_not_call_network(self) -> None:
        with patch("src.feedback.manual_operator_operating_cycle.fetch_klines") as fetch:
            with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        fetch.assert_not_called()

    def test_public_fetch_mode_uses_fetch_path(self) -> None:
        def fake_fetch(path, limit): shutil = __import__("shutil"); shutil.copy(self.ohlcv, path)
        with patch("src.feedback.manual_operator_operating_cycle._fetch_ohlcv", side_effect=fake_fetch) as fetch:
            with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: result = self._run(fetch_public_ohlcv=True)
        self.assertTrue(result["ok"]); fetch.assert_called_once()

    def test_summary_contains_readiness_and_safety(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        summary = (self.root / "out" / "cycle_summary.md").read_text()
        self.assertIn("P9 readiness", summary); self.assertIn("No automatic tuning occurred", summary)

    def test_output_set_is_complete(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        self.assertEqual(set(OUTPUT_NAMES), {path.name for path in (self.root / "out").iterdir()})

    def test_invalid_date_is_compact_error(self) -> None:
        result = run_p8_operating_cycle(candidates=self.candidates, signal_context=self.signals, ohlcv=self.ohlcv, report_date="bad", output_root=self.root / "out")
        self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 2); self.assertNotIn("Traceback", json.dumps(result))

    def test_classification_semantics_are_delegated(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2] as p5, self._fake_stages()[3]: self._run()
        self.assertTrue(p5.called)

    def test_newest_candidate_beyond_lag_fails(self) -> None:
        rows = list(csv.DictReader(self.candidates.open())); rows[0]["timestamp_jst"] = "2026-07-10T12:00:00+09:00"
        self.candidates = self._write("future.csv", self.candidates.read_text().splitlines()[0].split(","), rows)
        result = self._run(); self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 2)

    def test_invalid_ohlcv_schema_fails(self) -> None:
        self.ohlcv = self._write("bad-ohlcv.csv", ["timestamp_utc", "open"], [{"timestamp_utc": "2026-07-10T01:00:00Z", "open": "1"}])
        result = self._run(); self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 2)

    def test_nonmonotonic_ohlcv_fails(self) -> None:
        rows = list(csv.DictReader(self.ohlcv.open())); rows.append(dict(rows[0])); self.ohlcv = self._write("dup-ohlcv.csv", list(rows[0]), rows)
        result = self._run(); self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 2)

    def test_stage_failure_leaves_no_outputs(self) -> None:
        with patch("src.feedback.manual_operator_operating_cycle.build_manual_scenarios", return_value={"ok": False, "exit_code": 2, "errors": ["invalid_input"]}):
            result = self._run()
        self.assertFalse(result["ok"]); self.assertFalse((self.root / "out").exists())

    def test_output_requires_replace(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]:
            result = run_p8_operating_cycle(candidates=self.candidates, signal_context=self.signals, ohlcv=self.ohlcv, report_date="20260711", output_root=self.root / "out")
        self.assertFalse(result["ok"]); self.assertEqual(result["exit_code"], 4)

    def test_manifest_records_freshness(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        manifest = json.loads((self.root / "out" / "cycle_manifest.json").read_text()); self.assertEqual(manifest["source"]["interval"], "15m"); self.assertEqual(manifest["source"]["ohlcv_freshness"], "valid")

    def test_summary_is_privacy_safe(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: self._run()
        summary = (self.root / "out" / "cycle_summary.md").read_text(); self.assertNotIn(str(self.root), summary); self.assertNotIn("nearest_major_support", summary)

    def test_actual_pair_both_is_accepted(self) -> None:
        episodes = self._write("episodes.csv", ["episode_id"], [{"episode_id": "e1"}]); links = self._write("links.csv", ["link_id"], [{"link_id": "l1"}])
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: result = self._run(actual_episodes=episodes, actual_links=links)
        self.assertTrue(result["ok"])

    def test_result_contains_class_side_comparison_metrics(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: result = self._run()
        self.assertIn("class_counts", result); self.assertIn("side_counts", result); self.assertIn("comparison", result)

    def test_report_date_is_part_of_cycle_contract(self) -> None:
        with self._fake_stages()[0], self._fake_stages()[1], self._fake_stages()[2], self._fake_stages()[3]: result = self._run()
        self.assertTrue(result["ok"]); self.assertEqual(result["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
