from __future__ import annotations

import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.trade.performance_state import load_loss_streak


class PerformanceStateTests(unittest.TestCase):
    def test_load_loss_streak_uses_recent_completed_notified_outcomes(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_win", "timestamp_jst": "2026-03-10T09:05:00+09:00", "was_notified": "true"})
                writer.writerow({"signal_id": "sig_loss1", "timestamp_jst": "2026-03-11T09:05:00+09:00", "was_notified": "true"})
                writer.writerow({"signal_id": "sig_loss2", "timestamp_jst": "2026-03-12T09:05:00+09:00", "was_notified": "true"})

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_win", "evaluation_status": "complete", "outcome": "win"})
                writer.writerow({"signal_id": "sig_loss1", "evaluation_status": "complete", "outcome": "loss"})
                writer.writerow({"signal_id": "sig_loss2", "evaluation_status": "complete", "outcome": "expired"})

            self.assertEqual(load_loss_streak(base_dir=base_dir, fallback_streak=0), 2)

    def test_load_loss_streak_returns_fallback_when_no_history(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            self.assertEqual(load_loss_streak(base_dir=base_dir, fallback_streak=3), 3)


if __name__ == "__main__":
    unittest.main()
