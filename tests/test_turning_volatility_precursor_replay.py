from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.feedback.turning_volatility_precursor_replay import (
    EVENT_FIELDS,
    replay_turning_volatility_precursors,
    classify_precursor_row,
)


class TurningVolatilityPrecursorReplayTests(unittest.TestCase):
    def _row(self, signal_id: str, timestamp: str, *, bias: str = "long", flags: str = "long_into_major_resistance,major_resistance_rejection", price: str = "100") -> dict[str, str]:
        return {"signal_id": signal_id, "timestamp_utc": timestamp, "timestamp_jst": timestamp, "was_notified": "false", "current_price": price, "bias": bias, "phase": "reversal_risk", "market_regime": "transition", "market_map_flags": flags, "active_level_role": "", "level_flip_state": "resistance_to_support_flip", "failed_breakout_state": "", "trend_flip_state": "early_down", "location_risk": "80", "confidence_wait_shadow": "80", "cvd_price_divergence": "bearish" if bias == "long" else "bullish", "orderbook_bias": "ask_heavy" if bias == "long" else "bid_heavy", "primary_setup_status": "invalid", "primary_setup_reason": "", "atr_15m_value": "1", "market_map_primary_state": "", "warning_flags": "", "risk_flags": "", "notify_reason_codes": "", "suppress_reason_codes": "", "long_display_score": "81", "short_display_score": "19"}

    def test_short_and_mirrored_long_precursors(self) -> None:
        down = classify_precursor_row(self._row("d", "2026-07-01T00:00:00Z"))
        up = classify_precursor_row(self._row("u", "2026-07-01T01:00:00Z", bias="short", flags="short_into_major_support,major_support_rejection", price="100"))
        self.assertEqual(down["POLICY_LEVEL_REJECTION"]["side"], "DOWN")
        self.assertEqual(up["POLICY_LEVEL_REJECTION"]["side"], "UP")
        self.assertEqual(down["POLICY_FAILED_FLIP_GUARD"]["side"], "DOWN")

    def test_both_conflict_is_reported(self) -> None:
        row = self._row("both", "2026-07-01T00:00:00Z", bias="both", flags="long_into_major_resistance,major_resistance_rejection,short_into_major_support,major_support_rejection")
        result = classify_precursor_row(row)
        self.assertEqual(result["POLICY_COMBINED_PRECURSOR"]["side"], "BOTH")

    def test_no_future_leakage_and_outcome_ordering(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); signals = root / "signals.csv"; ohlcv = root / "ohlcv.csv"
            row = self._row("20260711_220501", "2026-07-12T00:05:00Z")
            with signals.open("w", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
            with ohlcv.open("w", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_utc", "open", "high", "low", "close", "interval"]); writer.writeheader()
                for i in range(20):
                    writer.writerow({"timestamp_utc": f"2026-07-12T{1+i//4:02d}:{(i%4)*15:02d}:00Z", "open": 100, "high": 100, "low": 100, "close": 100, "interval": "15m"})
            result = replay_turning_volatility_precursors(signals=signals, ohlcv=ohlcv, output_csv=root / "events.csv", output_json=root / "report.json", output_md=root / "report.md", replace_output=True)
            self.assertTrue(result["ok"])
            report = json.loads((root / "report.json").read_text())
            self.assertEqual(report["pinned_case"]["status"], "caught_before_move" if report["pinned_case"]["status"] == "caught_before_move" else "failed")
            row_text = (root / "events.csv").read_text(); self.assertNotIn("outcome_", row_text.splitlines()[1].split(",")[0])

    def test_episode_dedup_and_deterministic_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); signals = root / "signals.csv"; ohlcv = root / "ohlcv.csv"
            rows = [self._row(str(i), f"2026-07-01T0{i}:00:00Z") for i in range(2)]
            with signals.open("w", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
            with ohlcv.open("w", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_utc", "open", "high", "low", "close", "interval"]); writer.writeheader()
                for i in range(20): writer.writerow({"timestamp_utc": f"2026-07-02T{i:02d}:00:00Z", "open": 100, "high": 100, "low": 100, "close": 100, "interval": "15m"})
            args = dict(signals=signals, ohlcv=ohlcv, output_csv=root / "events.csv", output_json=root / "report.json", output_md=root / "report.md", replace_output=True)
            first = replay_turning_volatility_precursors(**args); first_bytes = tuple(path.read_bytes() for path in (args["output_csv"], args["output_json"], args["output_md"]))
            second = replay_turning_volatility_precursors(**args); second_bytes = tuple(path.read_bytes() for path in (args["output_csv"], args["output_json"], args["output_md"]))
            self.assertTrue(first["ok"] and second["ok"]); self.assertEqual(first_bytes, second_bytes)
            self.assertLessEqual(json.loads((root / "report.json").read_text())["episode_rows"], len(rows) * 5)

    def test_actual_pair_fail_closed_and_privacy_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); result = replay_turning_volatility_precursors(signals=root / "missing.csv", ohlcv=root / "missing.csv", output_csv=root / "e.csv", output_json=root / "j.json", output_md=root / "m.md", actual_episodes=root / "episodes.csv", replace_output=True)
            self.assertFalse(result["ok"]); self.assertIn("actual_pair_incomplete", result["error_codes"]); self.assertNotIn("/Users/", json.dumps(result))

    def test_invalid_ohlcv_is_unresolved_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); signals = root / "signals.csv"; signals.write_text("signal_id,timestamp_utc,timestamp_jst,bias,current_price\n")
            result = replay_turning_volatility_precursors(signals=signals, ohlcv=root / "missing.csv", output_csv=root / "e.csv", output_json=root / "j.json", output_md=root / "m.md")
            self.assertFalse(result["ok"]); self.assertFalse((root / "e.csv").exists())

    def test_distant_first_ohlcv_bar_is_unresolved_not_future_leak(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); signals = root / "signals.csv"; ohlcv = root / "ohlcv.csv"
            row = self._row("gap", "2026-07-01T00:00:00Z")
            with signals.open("w", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
            with ohlcv.open("w", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_utc", "open", "high", "low", "close", "interval"]); writer.writeheader()
                for i in range(20): writer.writerow({"timestamp_utc": f"2026-07-02T{i:02d}:00:00Z", "open": 100, "high": 110, "low": 90, "close": 100, "interval": "15m"})
            result = replay_turning_volatility_precursors(signals=signals, ohlcv=ohlcv, output_csv=root / "events.csv", output_json=root / "report.json", output_md=root / "report.md", replace_output=True)
            self.assertTrue(result["ok"])
            self.assertIn(",unresolved,unresolved,unresolved,", (root / "events.csv").read_text())


if __name__ == "__main__":
    unittest.main()
