from __future__ import annotations

import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.feedback.macro_operator_hierarchy_shadow import render_macro_operator_hierarchy_shadow


def _write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields or list(rows[0])); writer.writeheader(); writer.writerows(rows)


class MacroOperatorHierarchyShadowTests(unittest.TestCase):
    def _fixture(self, root: Path, tactical: bool = True) -> dict[str, Path]:
        at = "2026-01-01T02:30:00+00:00"; sid = "s1"
        paths = {name: root / f"{name}.csv" for name in ("signals", "tactical", "macro", "levels", "m3", "one", "four")}
        _write(paths["signals"], [{"signal_id": sid, "timestamp_jst": "2026-01-01T11:30:00+09:00", "current_price": "100", "primary_setup_side": "long", "primary_setup_status": "watch", "prelabel": "<script>future-sentinel</script>"}])
        candidate = {"candidate_id": "c1", "source_signal_id": sid, "candidate_type": "limit", "candidate_status": "conditional", "side": "long", "entry_mode": "limit", "entry_price": "99", "entry_zone_low": "98", "entry_zone_high": "100", "stop_loss": "97", "tp1": "102", "tp2": "104", "market_entry_status": "blocked", "limit_entry_status": "allowed", "counter_scalp_status": "blocked", "breakout_status": "blocked", "active_headline": "<b>headline</b>", "next_condition": "wait"}
        _write(paths["tactical"], [candidate] if tactical else [], fields=list(candidate))
        macro = {"schema_version": "macro_structure_volatility_replay.v1", "method_version": "macro_structure_volatility_replay.v1", "event_id": "e1", "signal_id": sid, "event_timestamp_utc": at, "event_price": "100", "nearest_support_id": "support", "nearest_resistance_id": "future", "first_reliable_target": "target", "intervening_obstruction": "none", "structural_state": "range", "structural_direction": "UP", "price_location": "middle", "volatility_state": "ordinary", "expansion_risk": "low", "outcome_3h": "FUTURE_SENTINEL"}
        _write(paths["macro"], [macro])
        level_base = {"schema_version": "level_reliability.v1", "method_version": "macro_structure_volatility_replay.v1", "low": "95", "high": "96", "center": "95.5", "last_confirmed_at": "2026-01-01T01:00:00+00:00", "member_confirmation_timestamps": "2026-01-01T01:00:00+00:00", "reliability_band": "high", "role": "support", "lifecycle": "active"}
        _write(paths["levels"], [{**level_base, "level_id": "target"}, {**level_base, "level_id": "support"}, {**level_base, "level_id": "future", "last_confirmed_at": "2026-01-01T03:00:00+00:00", "member_confirmation_timestamps": "2026-01-01T03:00:00+00:00"}])
        m3 = {"schema_version": "macro_next_regime_replay.v1", "method_version": "macro_next_regime_replay.v1", "record_id": "r1", "event_id": "e1", "signal_id": sid, "event_timestamp_utc": at, "current_tactical_side": "UP", "current_structural_thesis": "UP", "weakening_thesis": "none", "next_regime_side": "DOWN", "status": "activated", "activation_families": "FALSE_BREAK_RECLAIM_DOWN", "reason_codes": "x", "invalidation_reason_codes": "", "first_reliable_target": "target", "intervening_obstruction": "none", "baseline_side": "DOWN", "baseline_status": "watch", "baseline_grade": "none", "baseline_type": "x", "comparison_category": "agreement", "outcome_3h": "FUTURE_SENTINEL"}
        _write(paths["m3"], [m3])
        bars = [{"timestamp_utc": "2026-01-01T00:00:00+00:00", "open": "99", "high": "101", "low": "98", "close": "100", "interval": "1h"}, {"timestamp_utc": "2026-01-01T02:00:00+00:00", "open": "100", "high": "102", "low": "99", "close": "101", "interval": "1h"}]
        _write(paths["one"], bars); _write(paths["four"], [{**bars[0], "interval": "4h"}])
        return paths

    def _render(self, root: Path, tactical: bool = True) -> tuple[dict[str, Path], dict[str, object], list[Path]]:
        paths = self._fixture(root, tactical); outputs = [root / "out.html", root / "out.json", root / "out.md"]
        result = render_macro_operator_hierarchy_shadow(signal_context_csv=paths["signals"], tactical_candidates_csv=paths["tactical"], macro_events_csv=paths["macro"], macro_levels_csv=paths["levels"], next_regime_events_csv=paths["m3"], ohlcv_1h_csv=paths["one"], ohlcv_4h_csv=paths["four"], signal_id="s1", output_html=outputs[0], output_json=outputs[1], output_md=outputs[2], replace_output=True)
        return paths, result, outputs

    def test_event_time_render_joins_and_excludes_future_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, result, outputs = self._render(Path(temp))
            manifest = json.loads(outputs[1].read_text())
            self.assertEqual(result["closed_1h_candle_count"], 1)
            self.assertEqual(result["tactical_candidate_count"], 1)
            self.assertTrue(result["chart_first_confirmation"])
            self.assertIn("nearest_resistance:event_time_geometry_unavailable", manifest["missing_data_flags"])
            self.assertNotIn("future", {row["level_id"] for row in manifest["chart_model"]["macro_overlays"]})
            for output in outputs:
                self.assertNotIn("FUTURE_SENTINEL", output.read_text())
            self.assertIn("&lt;script&gt;future-sentinel&lt;/script&gt;", outputs[0].read_text())

    def test_role_mismatch_deduplicates_safe_target_and_tactical_zones(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); paths = self._fixture(root)
            levels = list(csv.DictReader(paths["levels"].open()))
            for row in levels:
                if row["level_id"] == "support": row["role"] = "resistance"
            _write(paths["levels"], levels)
            outputs = [root / "html" / "out.html", root / "json" / "out.json", root / "md" / "out.md"]
            result = render_macro_operator_hierarchy_shadow(signal_context_csv=paths["signals"], tactical_candidates_csv=paths["tactical"], macro_events_csv=paths["macro"], macro_levels_csv=paths["levels"], next_regime_events_csv=paths["m3"], ohlcv_1h_csv=paths["one"], ohlcv_4h_csv=paths["four"], signal_id="s1", output_html=outputs[0], output_json=outputs[1], output_md=outputs[2], replace_output=True)
            manifest = json.loads(outputs[1].read_text())
            self.assertEqual(result["event_time_safe_macro_overlay_count"], 1)
            self.assertEqual(result["nearest_support_role_mismatch_count"], 1)
            self.assertEqual(result["tactical_entry_zone_count"], 1)
            self.assertEqual(manifest["chart_model"]["macro_overlays"][0]["semantic_labels"], ["target"])
            support = manifest["macro_strip_model"]["references"]["nearest_support"]
            self.assertEqual((support["status"], support["actual_level_role"]), ("reference_role_mismatch", "resistance"))
            self.assertTrue(all(path.exists() for path in outputs))
            self.assertIn('class="tactical-zone"', outputs[0].read_text())

    def test_required_columns_and_tactical_geometry_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); paths = self._fixture(root)
            rows = list(csv.DictReader(paths["tactical"].open())); rows[0]["entry_zone_low"] = "101"; rows[0]["entry_zone_high"] = "100"; _write(paths["tactical"], rows)
            outputs = [root / "out.html", root / "out.json", root / "out.md"]
            with self.assertRaisesRegex(ValueError, "tactical_geometry_invalid"):
                render_macro_operator_hierarchy_shadow(signal_context_csv=paths["signals"], tactical_candidates_csv=paths["tactical"], macro_events_csv=paths["macro"], macro_levels_csv=paths["levels"], next_regime_events_csv=paths["m3"], ohlcv_1h_csv=paths["one"], signal_id="s1", output_html=outputs[0], output_json=outputs[1], output_md=outputs[2], replace_output=True)

    def test_zero_tactical_candidates_and_required_future_level_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); paths, result, outputs = self._render(root, tactical=False)
            self.assertEqual(result["tactical_candidate_count"], 0)
            self.assertIn("no tactical candidate rows", outputs[0].read_text())
            rows = list(csv.DictReader(paths["levels"].open())); rows[0]["last_confirmed_at"] = "2026-01-01T03:00:00+00:00"; _write(paths["levels"], rows)
            with self.assertRaisesRegex(ValueError, "required_level_not_event_time_safe"):
                render_macro_operator_hierarchy_shadow(signal_context_csv=paths["signals"], tactical_candidates_csv=paths["tactical"], macro_events_csv=paths["macro"], macro_levels_csv=paths["levels"], next_regime_events_csv=paths["m3"], ohlcv_1h_csv=paths["one"], signal_id="s1", output_html=outputs[0], output_json=outputs[1], output_md=outputs[2], replace_output=True)

    def test_deterministic_publication_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); _, _, outputs = self._render(root); before = [path.read_bytes() for path in outputs]
            self._render(root); self.assertEqual(before, [path.read_bytes() for path in outputs])
            real_replace = os.replace; calls = {"n": 0}
            def fail(source: object, destination: object) -> None:
                calls["n"] += 1
                if calls["n"] == 5: raise OSError("forced")
                real_replace(source, destination)
            paths = self._fixture(root)
            with patch("src.feedback.macro_operator_hierarchy_shadow.os.replace", side_effect=fail), self.assertRaises(OSError):
                render_macro_operator_hierarchy_shadow(signal_context_csv=paths["signals"], tactical_candidates_csv=paths["tactical"], macro_events_csv=paths["macro"], macro_levels_csv=paths["levels"], next_regime_events_csv=paths["m3"], ohlcv_1h_csv=paths["one"], signal_id="s1", output_html=outputs[0], output_json=outputs[1], output_md=outputs[2], replace_output=True)
            self.assertEqual(before, [path.read_bytes() for path in outputs])


if __name__ == "__main__":
    unittest.main()
