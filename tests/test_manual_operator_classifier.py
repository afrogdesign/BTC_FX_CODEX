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
    ADVISORY_NO_TRADE_TOKENS,
    CANDIDATE_HEADERS,
    EVENT_HEADERS,
    OUTPUT_HEADERS,
    SIGNAL_HEADERS,
    build_manual_operator_classifier,
    classify_manual_operator_candidate,
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

    def test_advisory_tokens_are_c_only_when_prerequisites_hold(self) -> None:
        for token in sorted(ADVISORY_NO_TRADE_TOKENS):
            with self.subTest(token=token):
                result = self.run_classifier(self.fixture(extra_signal={"no_trade_flags": token}))
                self.assertEqual(result["class_counts"].get("C_WATCH_ZONE"), 1)
                self.assertEqual(result["class_counts"].get("A_FORMAL", 0), 0)
                self.assertEqual(result["class_counts"].get("B_CHECK_15M", 0), 0)
                self.assertIn("c_watch_no_trade_advisory", self.read_rows()[0]["reason_codes"])
        result = self.run_classifier(self.fixture(extra_signal={"no_trade_flags": "short_at_major_support_wait_only", "confidence_direction_shadow": ""}))
        self.assertEqual(result["classification_status_counts"].get("insufficient_evidence"), 1)

    def test_hard_unknown_and_mixed_no_trade_tokens_remain_stop(self) -> None:
        for value in ("volatile_regime", "unknown_token", "breakout_follow_candidate;unknown_token", "breakout_follow_candidate;volatile_regime"):
            with self.subTest(value=value):
                result = self.run_classifier(self.fixture(extra_signal={"no_trade_flags": value}))
                self.assertEqual(result["class_counts"].get("STOP_OR_EXIT"), 1)
                self.assertEqual(result["class_counts"].get("C_WATCH_ZONE", 0), 0)

    def test_classifier_method_version_v2_and_advisory_id_change(self) -> None:
        self.run_classifier(self.fixture())
        with (self.root / "out.csv").open(newline="", encoding="utf-8") as fp:
            normal = next(csv.DictReader(fp)); normal_id = normal["classification_id"]
        self.assertEqual(normal["classifier_method_version"], "manual_operator_classifier.v2")
        self.run_classifier(self.fixture(extra_signal={"no_trade_flags": "breakout_follow_candidate"}))
        with (self.root / "out.csv").open(newline="", encoding="utf-8") as fp:
            advisory = next(csv.DictReader(fp)); advisory_id = advisory["classification_id"]
        self.assertEqual(advisory["classifier_method_version"], "manual_operator_classifier.v2")
        self.assertNotEqual(normal_id, advisory_id)

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

    def test_zero_rr_is_present_and_does_not_fallback(self) -> None:
        result = self.run_classifier(self.fixture(rr1="0", rr2="0", extra_candidate={"rr_current_tp1": "9", "rr_current_tp2": "9"}))
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(self.read_rows()[0]["rr_tp1_used"], "0")
        self.assertEqual(self.read_rows()[0]["rr_tp2_used"], "0")

    def test_nonfinite_numeric_and_threshold_fail_closed(self) -> None:
        for value in ("NaN", "Infinity", "-Infinity"):
            self.assertEqual(self.run_classifier(self.fixture(extra_candidate={"entry_price": value}))["exit_code"], 2)
        self.assertEqual(self.run_classifier(self.fixture(), thresholds={"long_direction_min": "NaN"})["exit_code"], 2)
        self.assertEqual(self.run_classifier(self.fixture(), thresholds={"long_direction_min": "Infinity"})["exit_code"], 2)

    def test_join_side_and_b_contracts(self) -> None:
        fixture = self.fixture()
        with fixture["candidates"].open(newline="", encoding="utf-8") as fp:
            candidate = next(csv.DictReader(fp))
        candidate["source_signal_id"] = "other"
        fixture["candidates"] = self.write("mismatch.csv", CANDIDATE_HEADERS, [candidate])
        self.assertEqual(self.run_classifier(fixture)["exit_code"], 2)
        fixture = self.fixture()
        with fixture["events"].open(newline="", encoding="utf-8") as fp:
            event = next(csv.DictReader(fp))
        event["side"] = ""
        fixture["events"] = self.write("bad-side.csv", EVENT_HEADERS, [event])
        self.assertEqual(self.run_classifier(fixture)["exit_code"], 2)
        self.assertEqual(self.run_classifier(self.fixture(quality=""))["class_counts"].get("B_CHECK_15M", 0), 0)
        self.assertEqual(self.run_classifier(self.fixture(setup_status="invalid", gate="blocked"))["class_counts"].get("B_CHECK_15M", 0), 0)

    def test_output_snapshot_and_required_markdown_sections(self) -> None:
        result = self.run_classifier(self.fixture(extra_signal={"warning_flags": "a,b", "risk_flags": "r|r", "no_trade_flags": "[\"n1\", \"n2\"]"}))
        self.assertTrue(result["ok"])
        with (self.root / "out.csv").open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        for field in ("short_direction_min", "short_execution_min", "short_wait_max", "short_tp1_rr_min", "short_tp2_rr_min", "long_direction_min", "long_execution_min", "long_wait_max", "long_tp1_rr_min", "long_tp2_rr_min"):
            self.assertTrue(row[field])
        self.assertEqual(result["warning_token_counts"], {"a": 1, "b": 1})
        self.assertEqual(result["risk_token_counts"], {"r": 1})
        self.assertEqual(result["no_trade_token_counts"], {"n1": 1, "n2": 1})
        markdown = (self.root / "out.md").read_text(encoding="utf-8")
        for section in ("Purpose", "Input Status", "Method and No-Leakage Boundary", "Threshold Snapshot", "Classification Coverage", "Class Distribution", "Side Breakdown", "Regime Breakdown", "Setup-Family Breakdown", "Existing Gate Comparison", "Warnings and Risks", "Limitations", "Safety Boundary"):
            self.assertIn(f"## {section}", markdown)
        for statement in ("not FORMAL_GO", "no automatic order", "human decides manually", "A/B/C/STOP does not replace existing gates"):
            self.assertIn(statement, markdown)

    def test_blank_quality_is_c_and_non_ok_quality_is_stop(self) -> None:
        blank = self.run_classifier(self.fixture(quality=""))
        self.assertEqual(blank["class_counts"].get("C_WATCH_ZONE"), 1)
        self.assertEqual(blank["class_counts"].get("STOP_OR_EXIT", 0), 0)
        non_ok = self.run_classifier(self.fixture(quality="stale", extra_signal={"no_trade_flags": "manual_review"}))
        self.assertEqual(non_ok["class_counts"].get("STOP_OR_EXIT"), 1)
        self.assertIn("stop_data_quality", self.read_rows()[0]["reason_codes"])
        self.assertIn("stop_no_trade_flag", self.read_rows()[0]["reason_codes"])

    def test_scalar_numeric_fields_validate_and_normalize(self) -> None:
        for field in ("stop_loss", "tp1", "tp2"):
            first = self.fixture(extra_candidate={field: "1"})
            self.assertEqual(self.run_classifier(first)["exit_code"], 0)
            with first["candidates"].open(newline="", encoding="utf-8") as fp:
                row = next(csv.DictReader(fp))
            row[field] = "1.0"
            first["candidates"] = self.write(f"{field}-dup.csv", CANDIDATE_HEADERS, [row, {**row, field: "1.00"}])
            self.assertEqual(self.run_classifier(first)["exit_code"], 0)
            malformed = self.fixture(extra_candidate={field: "not-a-number"})
            self.assertEqual(self.run_classifier(malformed)["exit_code"], 2)

    def test_structured_major_levels_validate_and_canonicalize(self) -> None:
        support = '{"low":1,"high":2,"mid":1.5,"kind":"support","sources":["15m"]}'
        resistance = '{"low":3,"high":4,"mid":3.5,"kind":"resistance","source":"15m"}'
        fixture = self.fixture(extra_signal={"nearest_major_support": support, "nearest_major_resistance": resistance})
        self.assertEqual(self.run_classifier(fixture)["exit_code"], 0)
        with fixture["signals"].open(newline="", encoding="utf-8") as fp:
            row = next(csv.DictReader(fp))
        reordered = '{"sources":["15m"],"kind":"support","mid":1.5,"high":2,"low":1}'
        fixture["signals"] = self.write("structured-duplicate.csv", SIGNAL_HEADERS, [row, {**row, "nearest_major_support": reordered}])
        duplicate = self.run_classifier(fixture)
        self.assertEqual(duplicate["exit_code"], 0)
        self.assertEqual(duplicate["exact_duplicate_signal_rows"], 1)

        for field in ("nearest_major_support", "nearest_major_resistance"):
            with self.subTest(field=field, form="legacy_scalar"):
                self.assertEqual(self.run_classifier(self.fixture(extra_signal={field: "1.00"}))["exit_code"], 0)
            with self.subTest(field=field, form="blank"):
                self.assertEqual(self.run_classifier(self.fixture(extra_signal={field: ""}))["exit_code"], 0)
            for invalid in ("{bad", "[]", '"level"', '{"low":NaN}', '{"low":2,"high":1}', '{"kind":"support"}'):
                with self.subTest(field=field, invalid=invalid):
                    self.assertEqual(self.run_classifier(self.fixture(extra_signal={field: invalid}))["exit_code"], 2)

    def test_structured_major_level_metadata_does_not_change_classification(self) -> None:
        first = self.fixture(extra_signal={"nearest_major_support": '{"low":1,"high":2,"mid":1.5,"kind":"support"}'})
        second = self.fixture(extra_signal={"nearest_major_support": '{"kind":"support","mid":1.5,"high":2,"low":1}'})
        self.assertEqual(self.run_classifier(first)["class_counts"], self.run_classifier(second)["class_counts"])
        self.assertEqual(self.read_rows()[0]["operator_class"], "B_CHECK_15M")

    def test_ambiguous_missing_context_and_token_forms(self) -> None:
        fixture = self.fixture()
        with fixture["events"].open(newline="", encoding="utf-8") as fp:
            event = next(csv.DictReader(fp))
        event["grouping_status"] = "ambiguous"; event["scenario_id"] = ""
        fixture["events"] = self.write("ambiguous.csv", EVENT_HEADERS, [event])
        fixture["candidates"] = self.write("none-candidate.csv", CANDIDATE_HEADERS, [])
        self.assertEqual(self.run_classifier(fixture)["classification_status_counts"].get("ambiguous_grouping"), 1)
        fixture = self.fixture(); fixture["events"] = self.write("ambiguous2.csv", EVENT_HEADERS, [event]); fixture["signals"] = self.write("none-signal.csv", SIGNAL_HEADERS, [])
        self.assertEqual(self.run_classifier(fixture)["classification_status_counts"].get("ambiguous_grouping"), 1)
        forms = ("a;b", "b,a", "a|b", '["b", "a"]')
        outputs = []
        for index, form in enumerate(forms):
            fixture = self.fixture(extra_signal={"warning_flags": form})
            outputs.append(self.run_classifier(fixture)["exact_duplicate_signal_rows"])
            with fixture["signals"].open(newline="", encoding="utf-8") as fp:
                row = next(csv.DictReader(fp))
            fixture["signals"] = self.write(f"tokens-{index}.csv", SIGNAL_HEADERS, [row, {**row, "warning_flags": "a;b"}])
            self.assertEqual(self.run_classifier(fixture)["exit_code"], 0)
        self.assertEqual(outputs, [0, 0, 0, 0])

    def test_setup_side_mismatch_reason(self) -> None:
        result = self.run_classifier(self.fixture(extra_signal={"primary_setup_side": "short"}))
        self.assertEqual(result["classification_status_counts"].get("insufficient_evidence"), 1)
        self.assertEqual(self.read_rows()[0]["reason_codes"], "side_mismatch")

    def test_public_single_candidate_helper_matches_batch(self) -> None:
        for kwargs in ({"gate": "pass"}, {"gate": "blocked"}, {"gate": "blocked", "direction": "40"}, {"gate": "pass", "quality": "bad"}, {"gate": "blocked", "rr1": "", "rr2": ""}):
            fixture = self.fixture(**kwargs); result = self.run_classifier(fixture)
            with fixture["events"].open(newline="", encoding="utf-8") as fp: event = next(csv.DictReader(fp))
            with fixture["candidates"].open(newline="", encoding="utf-8") as fp: candidate = next(csv.DictReader(fp))
            with fixture["signals"].open(newline="", encoding="utf-8") as fp: signal = next(csv.DictReader(fp))
            copies = (dict(event), dict(candidate), dict(signal)); direct = classify_manual_operator_candidate(event, candidate, signal); batch = self.read_rows()[0]
            for key in ("classification_status", "operator_class", "reason_codes", "required_human_check", "warning_codes", "trade_execution_gate", "phase1b_lite_gate", "opportunity_gate", "entry_price", "entry_zone_low", "entry_zone_high", "invalidation_price", "tp1_price", "tp2_price"):
                self.assertEqual(direct.get(key, ""), batch.get(key, ""), key)
            self.assertEqual((event, candidate, signal), copies)


if __name__ == "__main__": unittest.main()
