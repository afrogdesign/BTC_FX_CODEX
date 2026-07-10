from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.feedback.manual_operator_classifier import (
    CANDIDATE_HEADERS,
    EVENT_HEADERS,
    OUTPUT_HEADERS,
    SIGNAL_HEADERS,
    build_manual_operator_classifier,
)
from src.feedback.manual_scenario_normalizer import SCENARIO_HEADERS


class ManualOperatorClassifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, headers: list[str], rows: list[dict[str, str]]) -> Path:
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=headers); writer.writeheader(); writer.writerows(rows)
        return path

    def fixture(self, *, gate: str = "blocked", status: str = "allowed", quality: str = "ok", direction: str = "65", execution: str = "30", wait: str = "40", rr1: str = "1.2", rr2: str = "2.0", setup_status: str = "ready", extra_candidate: dict[str, str] | None = None, extra_signal: dict[str, str] | None = None) -> dict[str, Path]:
        scenario_id = "scn_" + "1" * 24
        event = {key: "" for key in EVENT_HEADERS}; event.update(schema_version="manual_scenario_event.v1", scenario_event_id="sce_" + "1" * 24, scenario_id=scenario_id, candidate_id="c1", candidate_fingerprint="fp", source_signal_id="s1", event_timestamp_utc="2026-07-10T01:00:00Z", event_timestamp_jst="2026-07-10T10:00:00+09:00", grouping_status="new_scenario", symbol="BTCUSDT", side="long", setup_family="limit_retest", candidate_status=status, entry_price="60000", entry_zone_low="59900", entry_zone_high="60100")
        scenario = {key: "" for key in SCENARIO_HEADERS}; scenario.update(schema_version="manual_scenario.v1", scenario_id=scenario_id, symbol="BTCUSDT", side="long", setup_family="limit_retest")
        candidate = {key: "" for key in CANDIDATE_HEADERS}; candidate.update(candidate_id="c1", source_signal_id="s1", timestamp_jst="2026-07-10T10:00:00+09:00", candidate_type="active_limit_retest", candidate_status=status, side="long", entry_price="60000", entry_zone_low="59900", entry_zone_high="60100", rr_zone_mid_tp1=rr1, rr_zone_mid_tp2=rr2)
        signal = {key: "" for key in SIGNAL_HEADERS}; signal.update(signal_id="s1", timestamp_jst="2026-07-10T10:00:00+09:00", market_regime="trend", transition_direction="up", primary_setup_side="long", primary_setup_status=setup_status, confidence_direction_shadow=direction, confidence_execution_shadow=execution, confidence_wait_shadow=wait, trade_execution_gate=gate, data_quality_flag=quality, signal_tier="standard")
        if extra_candidate: candidate.update(extra_candidate)
        if extra_signal: signal.update(extra_signal)
        return {"scenarios": self.write("scenarios.csv", SCENARIO_HEADERS, [scenario]), "events": self.write("events.csv", EVENT_HEADERS, [event]), "candidates": self.write("candidates.csv", CANDIDATE_HEADERS + (["extra"] if extra_candidate and "extra" in extra_candidate else []), [candidate]), "signals": self.write("signals.csv", SIGNAL_HEADERS + (["extra"] if extra_signal and "extra" in extra_signal else []), [signal])}

    def run_classifier(self, fixture: dict[str, Path], **kwargs: object) -> dict[str, object]:
        return build_manual_operator_classifier(scenarios=fixture["scenarios"], scenario_events=fixture["events"], candidates=fixture["candidates"], signal_context=fixture["signals"], output_csv=self.root / "out.csv", output_json=self.root / "out.json", output_md=self.root / "out.md", report_date="20260710", **kwargs)

    def read_rows(self) -> list[dict[str, str]]:
        with (self.root / "out.csv").open(newline="", encoding="utf-8") as fp: return list(csv.DictReader(fp))

    def test_exact_a_b_c_stop_priority(self) -> None:
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(gate="pass"))["class_counts"], "A_FORMAL"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture())["class_counts"], "B_CHECK_15M"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(direction="40"))["class_counts"], "C_WATCH_ZONE"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(gate="pass", quality="bad"))["class_counts"], "STOP_OR_EXIT"), 1)

    def read_after(self, counts: object, key: str) -> int:
        return int(dict(counts)[key])

    def test_ambiguous_event_and_missing_joins(self) -> None:
        fixture = self.fixture()
        with fixture["events"].open(newline="", encoding="utf-8") as fp: row = next(csv.DictReader(fp))
        row["scenario_id"] = ""; row["grouping_status"] = "ambiguous"
        self.write("events.csv", EVENT_HEADERS, [row]).replace(fixture["events"])
        result = self.run_classifier(fixture); self.assertEqual(result["ambiguous_event_rows"], 1); self.assertEqual(self.read_rows()[0]["classification_status"], "ambiguous_grouping")
        fixture = self.fixture(); fixture["events"] = self.write("normal_events.csv", EVENT_HEADERS, [self._normal_event()]); fixture["candidates"] = self.write("missing_candidate.csv", CANDIDATE_HEADERS, []); result = self.run_classifier(fixture); self.assertEqual(self.read_rows()[0]["classification_status"], "insufficient_evidence")

    def _normal_event(self) -> dict[str, str]:
        event = {key: "" for key in EVENT_HEADERS}; event.update(schema_version="manual_scenario_event.v1", scenario_event_id="sce_" + "1" * 24, scenario_id="scn_" + "1" * 24, candidate_id="c1", candidate_fingerprint="fp", source_signal_id="s1", event_timestamp_utc="2026-07-10T01:00:00Z", event_timestamp_jst="2026-07-10T10:00:00+09:00", grouping_status="new_scenario", symbol="BTCUSDT", side="long", setup_family="limit_retest", candidate_status="allowed", entry_price="60000", entry_zone_low="59900", entry_zone_high="60100")
        return event

    def test_b_thresholds_and_long_conservative_rule(self) -> None:
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(direction="59"))["class_counts"], "C_WATCH_ZONE"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(setup_status="watch"))["class_counts"], "C_WATCH_ZONE"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(gate="pass", setup_status="watch"))["class_counts"], "C_WATCH_ZONE"), 1)

    def test_blank_unknown_gate_and_missing_evidence(self) -> None:
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(gate=""))["class_counts"], "C_WATCH_ZONE"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(gate="unknown", direction="40"))["class_counts"], "C_WATCH_ZONE"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(direction=""))["classification_status_counts"], "insufficient_evidence"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(rr1="", rr2=""))["classification_status_counts"], "insufficient_evidence"), 1)

    def test_identity_conflict_and_additional_columns(self) -> None:
        fixture = self.fixture(extra_candidate={"extra": "one"}, extra_signal={"extra": "one"}); first = self.run_classifier(fixture); first_bytes = (self.root / "out.csv").read_bytes()
        fixture = self.fixture(extra_candidate={"extra": "two"}, extra_signal={"extra": "two"}); second = self.run_classifier(fixture); self.assertEqual(first["class_counts"], second["class_counts"]); self.assertEqual(first_bytes, (self.root / "out.csv").read_bytes())
        conflict = self.fixture()
        with conflict["candidates"].open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        row["entry_price"] = "61000"
        conflict["candidates"] = self.write("conflict.csv", CANDIDATE_HEADERS, [row, {**row, "entry_price": "62000"}])
        self.assertEqual(self.run_classifier(conflict)["exit_code"], 3)

    def test_future_and_malformed_input_fail(self) -> None:
        fixture = self.fixture()
        with fixture["signals"].open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        row["timestamp_jst"] = "2026-07-10T11:00:00+09:00"; fixture["signals"] = self.write("future.csv", SIGNAL_HEADERS, [row]); result = self.run_classifier(fixture); self.assertEqual(result["exit_code"], 2); self.assertFalse((self.root / "out.csv").exists())
        fixture = self.fixture()
        with fixture["candidates"].open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        row["entry_price"] = "bad"; fixture["candidates"] = self.write("bad.csv", CANDIDATE_HEADERS, [row]); result = self.run_classifier(fixture); self.assertEqual(result["exit_code"], 2)

    def test_no_outcome_leakage_and_deterministic_bytes(self) -> None:
        fixture = self.fixture(); first = self.run_classifier(fixture); bytes1 = ((self.root / "out.csv").read_bytes(), (self.root / "out.json").read_bytes(), (self.root / "out.md").read_bytes())
        self.assertTrue(json.loads((self.root / "out.json").read_text(encoding="utf-8"))["ok"])
        with fixture["events"].open(newline="", encoding="utf-8") as fp: event = next(csv.DictReader(fp))
        event["intraperiod_outcome"] = "tp1_first"; fixture["events"] = self.write("outcome.csv", EVENT_HEADERS, [event]); second = self.run_classifier(fixture); self.assertEqual(first["class_counts"], second["class_counts"])
        self.assertEqual(bytes1, ((self.root / "out.csv").read_bytes(), (self.root / "out.json").read_bytes(), (self.root / "out.md").read_bytes()))

    def test_dry_run_and_wrong_schema(self) -> None:
        fixture = self.fixture(); result = self.run_classifier(fixture, dry_run=True); self.assertTrue(result["ok"]); self.assertFalse((self.root / "out.csv").exists())
        fixture = self.fixture(); (self.root / "out.csv").write_text("legacy\n", encoding="utf-8"); self.assertEqual(self.run_classifier(fixture)["exit_code"], 4); self.assertEqual(self.run_classifier(fixture, replace_output=True)["exit_code"], 0)

    def test_three_output_rollback(self) -> None:
        fixture = self.fixture(); self.run_classifier(fixture); old = [(self.root / name).read_bytes() for name in ("out.csv", "out.json", "out.md")]
        from src.feedback import manual_operator_classifier as module
        original_replace = Path.replace; calls = {"n": 0}
        def replace(path: Path, target: Path) -> Path:
            calls["n"] += 1
            if calls["n"] == 5: raise OSError("injected")
            return original_replace(path, target)
        with patch.object(Path, "replace", replace): result = self.run_classifier(fixture)
        self.assertEqual(result["exit_code"], 4); self.assertEqual(old, [(self.root / name).read_bytes() for name in ("out.csv", "out.json", "out.md")]); self.assertEqual(list(self.root.glob(".p5-*")) + list(self.root.glob("*.p5-backup")), [])

    def test_direct_cli_json_contract(self) -> None:
        fixture = self.fixture(); repo = Path(__file__).resolve().parents[1]
        command = [sys.executable, str(repo / "tools" / "log_feedback.py"), "build-manual-operator-classifier", "--scenarios", str(fixture["scenarios"]), "--scenario-events", str(fixture["events"]), "--candidates", str(fixture["candidates"]), "--signal-context", str(fixture["signals"]), "--output-csv", str(self.root / "cli.csv"), "--output-json", str(self.root / "cli.json"), "--output-md", str(self.root / "cli.md"), "--date", "20260710", "--stdout-json"]
        result = subprocess.run(command, cwd=repo, text=True, capture_output=True, check=False); self.assertEqual(result.returncode, 0); self.assertEqual(len(result.stdout.strip().splitlines()), 1); self.assertTrue(json.loads(result.stdout)["ok"]); self.assertNotIn("Traceback", result.stderr); self.assertNotIn(str(self.root), result.stdout)

    def test_stop_variants_and_formal_evidence(self) -> None:
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(extra_signal={"no_trade_flags": "risk_high"}))["class_counts"], "STOP_OR_EXIT"), 1)
        self.assertEqual(self.read_after(self.run_classifier(self.fixture(status="invalidated", gate="pass"))["class_counts"], "STOP_OR_EXIT"), 1)
        formal = self.run_classifier(self.fixture(gate="pass")); self.assertEqual(formal["formal_pass_not_a_rows"], 0)
        exceptional = self.run_classifier(self.fixture(gate="pass", setup_status="watch")); self.assertEqual(exceptional["class_counts"]["C_WATCH_ZONE"], 1)

    def test_side_regime_setup_breakdowns_and_zero(self) -> None:
        result = self.run_classifier(self.fixture(extra_signal={"market_regime": "range"}), thresholds={"long_tp1_rr_min": "0", "long_tp2_rr_min": "0"})
        self.assertIn("long", result["side_class_counts"]); self.assertIn("range", result["regime_class_counts"]); self.assertIn("limit_retest", result["setup_family_class_counts"])
        self.assertEqual(self.read_rows()[0]["rr_tp1_used"], "1.2")

    def test_signal_identity_conflict_and_duplicate(self) -> None:
        fixture = self.fixture()
        with fixture["signals"].open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        conflict = {**row, "current_price": "1"}; fixture["signals"] = self.write("signal_conflict.csv", SIGNAL_HEADERS, [row, conflict]); self.assertEqual(self.run_classifier(fixture)["exit_code"], 3)
        fixture = self.fixture(); fixture["signals"] = self.write("signal_dup.csv", SIGNAL_HEADERS, [row, row]); result = self.run_classifier(fixture); self.assertEqual(result["exact_duplicate_signal_rows"], 1)

    def test_missing_entry_is_insufficient_and_cli_error_is_compact(self) -> None:
        fixture = self.fixture()
        with fixture["candidates"].open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        row["entry_price"] = ""; row["entry_zone_low"] = ""; row["entry_zone_high"] = ""; fixture["candidates"] = self.write("no_entry.csv", CANDIDATE_HEADERS, [row])
        with fixture["events"].open(newline="", encoding="utf-8") as fp:
            event = next(csv.DictReader(fp))
        event["entry_price"] = ""; event["entry_zone_low"] = ""; event["entry_zone_high"] = ""; fixture["events"] = self.write("no_entry_event.csv", EVENT_HEADERS, [event])
        self.assertEqual(self.run_classifier(fixture)["classification_status_counts"]["insufficient_evidence"], 1)
        repo = Path(__file__).resolve().parents[1]; result = subprocess.run([sys.executable, str(repo / "tools" / "log_feedback.py"), "build-manual-operator-classifier", "--scenarios", str(self.root / "missing"), "--scenario-events", str(self.root / "missing"), "--candidates", str(self.root / "missing"), "--signal-context", str(self.root / "missing"), "--output-csv", str(self.root / "x.csv"), "--output-json", str(self.root / "x.json"), "--output-md", str(self.root / "x.md"), "--date", "20260710", "--stdout-json"], cwd=repo, text=True, capture_output=True, check=False); self.assertEqual(result.returncode, 2); self.assertEqual(len(result.stdout.strip().splitlines()), 1); self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__": unittest.main()
