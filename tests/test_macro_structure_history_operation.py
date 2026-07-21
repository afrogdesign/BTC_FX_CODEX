from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.feedback.macro_structure_history_operation import OUTPUT_NAMES, build_macro_structure_history


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


def _write_run(root: Path, run_id: str, as_of: str, evaluated: str, levels: list[dict[str, str]], *, symbol: str = "BTC_USDT", fingerprint: str | None = None, structure_state: str = "range", price_location: str = "middle", current_price: int = 100) -> Path:
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
        "directional_activation": "NONE", "stale_status": "current", "continuity_status": "continuous",
        "data_quality_status": "ok", "result_status": "ok", "reliability_band_counts": {"high": 0, "medium": 1, "low": 0, "insufficient": 0},
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
