from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.feedback.macro_structure_history_operation import METHOD_VERSION, OUTPUT_NAMES, SCHEMA_VERSION, build_macro_structure_history


LEVEL_FIELDS = (
    "level_id", "side", "role", "low", "high", "center", "source_timeframes",
    "first_seen_at", "last_confirmed_at", "touch_count", "clean_rejection_count",
    "break_count", "false_break_reclaim_count", "lifecycle", "reliability_score",
    "reliability_band", "distance_from_price_pct", "distance_from_price_atr", "reason_codes",
)


def _level(level_id: str, side: str = "low", role: str = "support", band: str = "medium", lifecycle: str = "active", center: str = "100") -> dict[str, str]:
    return {
        "level_id": level_id, "side": side, "role": role, "low": str(float(center) - 1), "high": str(float(center) + 1),
        "center": center, "source_timeframes": "1h|4h", "first_seen_at": "2026-01-01T00:00:00+00:00",
        "last_confirmed_at": "2026-01-01T00:00:00+00:00", "touch_count": "2", "clean_rejection_count": "1",
        "break_count": "0", "false_break_reclaim_count": "0", "lifecycle": lifecycle, "reliability_score": "0.60" if band == "medium" else "0.85",
        "reliability_band": band, "distance_from_price_pct": "1.0", "distance_from_price_atr": "0.5", "reason_codes": "prior_only",
    }


def _write_run(root: Path, run_id: str, as_of: str, evaluated: str, levels: list[dict[str, str]], *, symbol: str = "BTC_USDT", fingerprint: str | None = None, structure_state: str = "range", price_location: str = "middle", current_price: int = 100, stale_status: str = "current", stale_timeframes: list[str] | None = None, continuity_status: str = "continuous", data_quality_status: str = "ok", result_status: str = "ok", reason_codes: list[str] | None = None) -> Path:
    run = root / run_id
    run.mkdir(parents=True)
    snapshot_id = "macro_snapshot_" + run_id[4:]
    snapshot = {
        "schema_version": "macro_structure_daily_operation.v1", "method_version": "macro_structure_daily_operation.v1",
        "m1_method_version": "macro_structure_volatility_replay.v1", "run_id": run_id, "snapshot_id": snapshot_id,
        "symbol": symbol, "as_of_utc": as_of, "evaluated_at_utc": evaluated, "structure_state": structure_state,
        "price_location": price_location, "location_percentile": 50, "current_price": current_price,
        "nearest_reliable_support": {"level_id": levels[0]["level_id"]} if levels else {},
        "nearest_reliable_resistance": {}, "next_upside_target": {}, "next_downside_target": {},
        "upside_obstruction": {}, "downside_obstruction": {}, "volatility_state": "normal", "expansion_risk": "low",
        "directional_activation": "NONE", "stale_status": stale_status, "stale_timeframes": stale_timeframes or [], "freshness": {"15m": {"status": stale_status}}, "continuity_status": continuity_status,
        "data_quality_status": data_quality_status, "result_status": result_status, "reason_codes": reason_codes or [], "reliability_band_counts": {"high": 0, "medium": 1, "low": 0, "insufficient": 0},
        "input_fingerprints": {"15m": fingerprint or run_id},
    }
    manifest = {
        "schema_version": snapshot["schema_version"], "method_version": snapshot["method_version"], "run_id": run_id,
        "snapshot_id": snapshot_id, "as_of_utc": as_of, "evaluated_at_utc": evaluated,
        "source": "public_ohlcv_only", "report_only": True, "automatic_order_allowed": False,
        "private_actual_trade_input": False, "input_fingerprints": snapshot["input_fingerprints"],
    }
    (run / "macro_structure_snapshot.json").write_text(json.dumps(snapshot, sort_keys=True), encoding="utf-8")
    (run / "macro_structure_snapshot.md").write_text("# fixture\n", encoding="utf-8")
    with (run / "macro_level_reliability.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(LEVEL_FIELDS), lineterminator="\n")
        writer.writeheader(); writer.writerows(levels)
    (run / "run_manifest.json").write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    return run


class MacroStructureHistoryOperationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.output = Path(self.temp.name) / "history"
        self.l1 = _level("L1")
        self.l2 = _level("L2", side="high", role="resistance", band="high", center="110")
        _write_run(self.root, "run_a", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00", [self.l1, self.l2], fingerprint="fp-a")
        _write_run(self.root, "run_a_recheck", "2026-01-01T00:00:00+00:00", "2026-01-01T02:00:00+00:00", [self.l1, self.l2], fingerprint="fp-a")
        changed = _level("L1", side="low", role="resistance", band="high", lifecycle="broken", center="101")
        l3 = _level("L3", side="low", role="support", band="low", center="90")
        _write_run(self.root, "run_b", "2026-01-02T00:00:00+00:00", "2026-01-02T01:00:00+00:00", [changed, l3], fingerprint="fp-b", structure_state="transition", price_location="lower_half", current_price=98)
        reappeared = _level("L2", side="high", role="resistance", band="medium", center="111")
        _write_run(self.root, "run_c", "2026-01-03T00:00:00+00:00", "2026-01-03T01:00:00+00:00", [changed, reappeared], fingerprint="fp-c", structure_state="reversal", price_location="upper_half", current_price=102)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_chronological_checkpoint_continuity_and_reevaluation(self) -> None:
        result = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        self.assertTrue(result["ok"])
        self.assertEqual(result["evaluation_count"], 4)
        self.assertEqual(result["structural_checkpoint_count"], 3)
        history = json.loads((self.output / result["artifact_dir"] / "macro_structure_history.json").read_text())
        self.assertEqual([item["run_id"] for item in history["evaluation_history"]], ["run_a", "run_a_recheck", "run_b", "run_c"])
        self.assertTrue(history["evaluation_history"][0]["canonical"])
        self.assertFalse(history["evaluation_history"][1]["canonical"])
        level_csv = (self.output / result["artifact_dir"] / "macro_level_history.csv").read_text()
        self.assertIn("reliability_band_transition", level_csv)
        self.assertIn("reappeared", level_csv)
        self.assertIn("absent_from_checkpoint", level_csv)
        self.assertIn("geometry_changed", level_csv)
        self.assertIn("medium->high", level_csv)
        self.assertIn("high->medium", level_csv)
        self.assertIn("support->resistance", level_csv)
        changes_csv = (self.output / result["artifact_dir"] / "macro_structure_changes.csv").read_text()
        self.assertIn("snapshot_transition", changes_csv)
        self.assertIn("structure_state", changes_csv)

    def test_direct_child_only_and_symbol_isolation(self) -> None:
        nested = self.root / "nested" / "run_nested"
        _write_run(nested.parent, nested.name, "2026-01-04T00:00:00+00:00", "2026-01-04T01:00:00+00:00", [self.l1])
        result = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        self.assertTrue(result["ok"])
        _write_run(self.root, "run_eth", "2026-01-05T00:00:00+00:00", "2026-01-05T01:00:00+00:00", [self.l1], symbol="ETH_USDT")
        failed = build_macro_structure_history(snapshot_root=self.root, output_root=self.output, symbol="BTC_USDT")
        self.assertFalse(failed["ok"])
        self.assertEqual(failed["error_code"], "source_symbol_mismatch")

    def test_latest_reevaluation_status_is_retained_without_structural_duplication(self) -> None:
        changed = _level("L1", side="low", role="resistance", band="high", lifecycle="broken", center="101")
        reappeared = _level("L2", side="high", role="resistance", band="medium", center="111")
        _write_run(self.root, "run_c_recheck", "2026-01-03T00:00:00+00:00", "2026-01-03T02:00:00+00:00", [changed, reappeared], fingerprint="fp-c", structure_state="reversal", price_location="upper_half", current_price=102, stale_status="stale", stale_timeframes=["15m"], continuity_status="discontinuous", data_quality_status="discontinuous", result_status="insufficient", reason_codes=["stale_ohlcv_15m"])
        result = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        self.assertTrue(result["ok"])
        history = json.loads((self.output / result["artifact_dir"] / "macro_structure_history.json").read_text())
        evaluations = history["evaluation_history"]
        latest_eval = evaluations[-1]
        self.assertEqual(latest_eval["run_id"], "run_c_recheck")
        self.assertEqual(latest_eval["stale_status"], "stale")
        self.assertEqual(latest_eval["continuity_status"], "discontinuous")
        self.assertEqual(latest_eval["data_quality_status"], "discontinuous")
        self.assertEqual(latest_eval["result_status"], "insufficient")
        self.assertEqual(latest_eval["freshness"]["15m"]["status"], "stale")
        self.assertEqual(sum(item["canonical"] for item in evaluations), 3)
        latest = json.loads((self.output / "latest.json").read_text())
        self.assertEqual(latest["history_result_status"], "ok")
        self.assertEqual(latest["latest_snapshot_result_status"], "insufficient")
        self.assertEqual(latest["latest_evaluation_run_id"], "run_c_recheck")
        self.assertEqual(latest["latest_stale_status"], "stale")
        self.assertEqual(latest["latest_continuity_status"], "discontinuous")
        self.assertEqual(latest["latest_structure_state"], "reversal")

    def test_markdown_renders_bounded_history_events(self) -> None:
        changed = _level("L1", side="low", role="resistance", band="high", lifecycle="broken", center="101")
        reappeared = _level("L2", side="high", role="resistance", band="medium", center="111")
        _write_run(self.root, "run_c_recheck", "2026-01-03T00:00:00+00:00", "2026-01-03T02:00:00+00:00", [changed, reappeared], fingerprint="fp-c", structure_state="reversal", price_location="upper_half", current_price=102, stale_status="stale", stale_timeframes=["15m"], reason_codes=["stale_ohlcv_15m"])
        result = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        markdown = (self.output / result["artifact_dir"] / "macro_structure_history.md").read_text()
        for section in ("Latest structural changes", "Reliability upgrades and downgrades", "Role changes", "Lifecycle changes", "Absence from checkpoint/latest", "Reappearances", "Stale or discontinuous evaluations", "Evidence limitations", "Safety boundary"):
            self.assertIn(section, markdown)
        self.assertIn("absent_from_checkpoint", markdown)
        self.assertIn("reappeared", markdown)
        self.assertIn("stale_ohlcv_15m", markdown)
        self.assertIn("retirement_status=not_established", markdown)

    def test_multiple_absences_reappearance_and_final_absence(self) -> None:
        root = Path(self.temp.name) / "absence"
        root.mkdir()
        l1, l2, l3 = _level("L1"), _level("L2"), _level("L3")
        _write_run(root, "run_1", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00", [l1, l2], fingerprint="1")
        _write_run(root, "run_2", "2026-01-02T00:00:00+00:00", "2026-01-02T01:00:00+00:00", [l1, l3], fingerprint="2")
        _write_run(root, "run_3", "2026-01-03T00:00:00+00:00", "2026-01-03T01:00:00+00:00", [l1, l3], fingerprint="3")
        _write_run(root, "run_4", "2026-01-04T00:00:00+00:00", "2026-01-04T01:00:00+00:00", [l1], fingerprint="4")
        _write_run(root, "run_5", "2026-01-05T00:00:00+00:00", "2026-01-05T01:00:00+00:00", [l1, l2], fingerprint="5")
        result = build_macro_structure_history(snapshot_root=root, output_root=self.output)
        with (self.output / result["artifact_dir"] / "macro_level_history.csv").open(newline="", encoding="utf-8") as handle:
            rows = [row for row in csv.DictReader(handle) if row["level_id"] == "L2"]
        self.assertEqual([row["level_status"] for row in rows], ["first_observation", "absent_from_checkpoint", "absent_from_checkpoint", "absent_from_checkpoint", "reappeared"])
        self.assertTrue(all(row["retirement_status"] == "not_established" for row in rows))
        self.assertTrue(all(row["observation_present"] == "False" for row in rows[1:4]))
        self.assertTrue(all(row["reliability_score_delta"] == "" for row in rows[1:4]))
        self.assertTrue(all(row["last_observed_checkpoint_id"] == rows[0]["checkpoint_id"] for row in rows[1:4]))
        with (self.output / result["artifact_dir"] / "macro_structure_changes.csv").open(newline="", encoding="utf-8") as handle:
            changes = list(csv.DictReader(handle))
        self.assertGreaterEqual(sum(row["change_type"] == "absent_from_checkpoint" for row in changes), 3)
        self.assertTrue(any(row["change_type"] == "reappeared" for row in changes))

    def test_level_observation_checkpoint_identity_matches_comparison(self) -> None:
        root = Path(self.temp.name) / "identity"
        root.mkdir()
        l1, l2 = _level("L1"), _level("L2")
        _write_run(root, "run_1", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00", [l1, l2], fingerprint="1")
        _write_run(root, "run_2", "2026-01-02T00:00:00+00:00", "2026-01-02T01:00:00+00:00", [l1], fingerprint="2")
        _write_run(root, "run_3", "2026-01-03T00:00:00+00:00", "2026-01-03T01:00:00+00:00", [l1], fingerprint="3")
        _write_run(root, "run_4", "2026-01-04T00:00:00+00:00", "2026-01-04T01:00:00+00:00", [l1, l2], fingerprint="4")
        result = build_macro_structure_history(snapshot_root=root, output_root=self.output)
        with (self.output / result["artifact_dir"] / "macro_level_history.csv").open(newline="", encoding="utf-8") as handle:
            rows = [row for row in csv.DictReader(handle) if row["level_id"] == "L2"]
        first, absent, reappeared = rows[0], rows[1], rows[-1]
        self.assertEqual(first["previous_checkpoint_id"], "")
        self.assertEqual(first["current_checkpoint_id"], first["last_observed_checkpoint_id"])
        self.assertEqual(absent["previous_checkpoint_id"], first["current_checkpoint_id"])
        self.assertEqual(absent["last_observed_checkpoint_id"], first["current_checkpoint_id"])
        self.assertNotEqual(absent["current_checkpoint_id"], absent["last_observed_checkpoint_id"])
        self.assertEqual(reappeared["level_status"], "reappeared")
        self.assertEqual(reappeared["previous_checkpoint_id"], first["current_checkpoint_id"])
        self.assertEqual(reappeared["current_checkpoint_id"], reappeared["last_observed_checkpoint_id"])

    def test_v2_identity_migrates_alongside_legacy_and_csv_is_auditable(self) -> None:
        legacy = self.output / "history_legacy_v1"
        legacy.mkdir(parents=True)
        legacy_bytes = {}
        for name in OUTPUT_NAMES:
            legacy_bytes[name] = b"legacy-v1\n"
            (legacy / name).write_bytes(legacy_bytes[name])
        (self.output / "latest.json").write_bytes(b'{"history_id":"history_legacy_v1","schema_version":"macro_structure_history_operation.v1"}\n')
        result = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        self.assertTrue(result["ok"])
        self.assertTrue(result["artifact_dir"] != legacy.name)
        artifact = self.output / result["artifact_dir"]
        self.assertEqual(json.loads((artifact / "macro_structure_history.json").read_text())["schema_version"], SCHEMA_VERSION)
        self.assertEqual(json.loads((artifact / "macro_structure_history.json").read_text())["method_version"], METHOD_VERSION)
        self.assertEqual(json.loads((artifact / "run_manifest.json").read_text())["schema_version"], SCHEMA_VERSION)
        self.assertEqual(json.loads((self.output / "latest.json").read_text())["schema_version"], SCHEMA_VERSION)
        self.assertIn(f"schema: `{SCHEMA_VERSION}`", (artifact / "macro_structure_history.md").read_text())
        for name in ("macro_snapshot_history.csv", "macro_level_history.csv", "macro_structure_changes.csv"):
            header = (artifact / name).read_text().splitlines()[0]
            self.assertTrue(header.startswith("schema_version,method_version,"))
        self.assertTrue(all((legacy / name).read_bytes() == legacy_bytes[name] for name in OUTPUT_NAMES))
        before = {name: (artifact / name).read_bytes() for name in OUTPUT_NAMES}
        repeated = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        self.assertEqual(repeated["history_id"], result["history_id"])
        self.assertTrue(all((artifact / name).read_bytes() == before[name] for name in OUTPUT_NAMES))

    def test_snapshot_csv_separates_canonical_and_latest_evaluation(self) -> None:
        changed = _level("L1", side="low", role="resistance", band="high", lifecycle="broken", center="101")
        reappeared = _level("L2", side="high", role="resistance", band="medium", center="111")
        _write_run(self.root, "run_c_recheck", "2026-01-03T00:00:00+00:00", "2026-01-03T02:00:00+00:00", [changed, reappeared], fingerprint="fp-c", structure_state="reversal", price_location="upper_half", current_price=102)
        result = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        with (self.output / result["artifact_dir"] / "macro_snapshot_history.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        row = next(item for item in rows if item["canonical_structural_run_id"] == "run_c")
        self.assertEqual(row["evaluated_at_utc"], "2026-01-03T01:00:00+00:00")
        self.assertEqual(row["latest_evaluation_run_id"], "run_c_recheck")
        self.assertEqual(row["latest_evaluated_at_utc"], "2026-01-03T02:00:00+00:00")

    def test_final_absence_is_explicit_and_not_active(self) -> None:
        root = Path(self.temp.name) / "final-absence"
        root.mkdir()
        l1, l2 = _level("L1"), _level("L2")
        _write_run(root, "run_1", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00", [l1, l2], fingerprint="1")
        _write_run(root, "run_2", "2026-01-02T00:00:00+00:00", "2026-01-02T01:00:00+00:00", [l1], fingerprint="2")
        _write_run(root, "run_3", "2026-01-03T00:00:00+00:00", "2026-01-03T01:00:00+00:00", [l1], fingerprint="3")
        result = build_macro_structure_history(snapshot_root=root, output_root=self.output)
        with (self.output / result["artifact_dir"] / "macro_level_history.csv").open(newline="", encoding="utf-8") as handle:
            rows = [row for row in csv.DictReader(handle) if row["level_id"] == "L2"]
        self.assertEqual(rows[-1]["level_status"], "absent_from_latest")
        self.assertEqual(rows[-1]["observation_present"], "False")

    def test_source_validation_failures_preserve_previous_latest(self) -> None:
        cases = (("blank", "source_level_id_missing"), ("duplicate", "source_level_id_duplicate"), ("manifest_missing", "source_manifest_timestamp_missing"), ("manifest_naive", "invalid_source_manifest_as_of_utc"), ("manifest_mismatch", "source_timestamp_mismatch"))
        for kind, expected in cases:
            with self.subTest(kind=kind):
                root = Path(self.temp.name) / kind
                root.mkdir()
                levels = [_level("L1")]
                run = _write_run(root, "run_valid", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00", levels, fingerprint=kind)
                first = build_macro_structure_history(snapshot_root=root, output_root=self.output / kind)
                latest = (self.output / kind / "latest.json").read_bytes()
                if kind == "blank":
                    _write_run(root, "run_bad", "2026-01-02T00:00:00+00:00", "2026-01-02T01:00:00+00:00", [_level("")], fingerprint="bad")
                elif kind == "duplicate":
                    _write_run(root, "run_bad", "2026-01-02T00:00:00+00:00", "2026-01-02T01:00:00+00:00", [_level("L1"), _level("L1")], fingerprint="bad")
                else:
                    manifest_path = run / "run_manifest.json"
                    manifest = json.loads(manifest_path.read_text())
                    if kind == "manifest_missing":
                        manifest.pop("as_of_utc")
                    elif kind == "manifest_naive":
                        manifest["as_of_utc"] = "2026-01-01T00:00:00"
                    else:
                        manifest["evaluated_at_utc"] = "2026-01-01T02:00:00+00:00"
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                failed = build_macro_structure_history(snapshot_root=root, output_root=self.output / kind)
                self.assertFalse(failed["ok"])
                self.assertEqual(failed["error_code"], expected)
                self.assertEqual(latest, (self.output / kind / "latest.json").read_bytes())

    def test_one_checkpoint_is_insufficient_history_and_repeat_is_idempotent(self) -> None:
        root = Path(self.temp.name) / "one"
        root.mkdir()
        _write_run(root, "run_one", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00", [self.l1])
        first = build_macro_structure_history(snapshot_root=root, output_root=self.output)
        self.assertTrue(first["ok"])
        artifact = self.output / first["artifact_dir"]
        before = {name: (artifact / name).read_bytes() for name in (*OUTPUT_NAMES[:-1], "run_manifest.json")}
        latest_before = (self.output / "latest.json").read_bytes()
        second = build_macro_structure_history(snapshot_root=root, output_root=self.output)
        self.assertEqual(first["history_id"], second["history_id"])
        self.assertEqual(latest_before, (self.output / "latest.json").read_bytes())
        self.assertEqual(before["macro_structure_history.json"], (artifact / "macro_structure_history.json").read_bytes())
        history = json.loads((artifact / "macro_structure_history.json").read_text())
        self.assertEqual(history["structural_checkpoint_count"], 1)
        self.assertEqual(history["result_status"], "insufficient_history")
        self.assertEqual(history["structural_checkpoints"][0]["transition_status"], "no_previous_transition")

    def test_malformed_source_fails_and_preserves_latest(self) -> None:
        first = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        latest = (self.output / "latest.json").read_bytes()
        (self.root / "run_bad").mkdir()
        failed = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        self.assertFalse(failed["ok"])
        self.assertEqual(failed["error_code"], "incomplete_source_run")
        self.assertEqual(latest, (self.output / "latest.json").read_bytes())

    def test_conflicting_existing_history_fails_and_preserves_latest(self) -> None:
        first = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        target = self.output / first["artifact_dir"]
        latest = (self.output / "latest.json").read_bytes()
        (target / "macro_structure_history.md").write_text("conflict\n", encoding="utf-8")
        failed = build_macro_structure_history(snapshot_root=self.root, output_root=self.output)
        self.assertFalse(failed["ok"])
        self.assertEqual(failed["error_code"], "existing_history_conflict")
        self.assertEqual((target / "macro_structure_history.md").read_text(), "conflict\n")
        self.assertEqual(latest, (self.output / "latest.json").read_bytes())

    def test_later_checkpoint_changes_history_identity_without_rewriting_source(self) -> None:
        root = Path(self.temp.name) / "two"
        root.mkdir()
        _write_run(root, "run_1", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00", [self.l1], fingerprint="one")
        _write_run(root, "run_2", "2026-01-02T00:00:00+00:00", "2026-01-02T01:00:00+00:00", [self.l1], fingerprint="two")
        first = build_macro_structure_history(snapshot_root=root, output_root=self.output)
        old_rows = (self.output / first["artifact_dir"] / "macro_snapshot_history.csv").read_text()
        _write_run(root, "run_3", "2026-01-03T00:00:00+00:00", "2026-01-03T01:00:00+00:00", [self.l1], fingerprint="three")
        second = build_macro_structure_history(snapshot_root=root, output_root=self.output)
        self.assertNotEqual(first["history_id"], second["history_id"])
        new_rows = (self.output / second["artifact_dir"] / "macro_snapshot_history.csv").read_text().splitlines()
        self.assertEqual(old_rows.splitlines()[0:3], new_rows[0:3])


if __name__ == "__main__":
    unittest.main()
