from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.storage.csv_logger import ACTIVE_PLAN_CANDIDATE_HEADER, append_active_plan_candidates
from src.trade.active_plan import build_active_trade_plan


class ActivePlanCandidateLoggingTests(unittest.TestCase):
    def _long_setup(self) -> dict[str, object]:
        return {
            "entry_zone": {"low": 60322.42, "high": 60524.08},
            "entry_mid": 60423.25,
            "stop_loss": 60025.57,
            "tp1": 60940.23,
            "tp2": 61377.68,
            "status": "watch",
        }

    def _short_setup(self) -> dict[str, object]:
        return {
            "entry_zone": {"low": 60680.82, "high": 60882.88},
            "entry_mid": 60781.85,
            "stop_loss": 61179.73,
            "tp1": 60264.61,
            "tp2": 59826.94,
            "status": "invalid",
        }

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", newline="", encoding="utf-8") as fp:
            return list(csv.DictReader(fp))

    def _payload_for_limit_and_counter(self) -> dict[str, object]:
        plan = build_active_trade_plan(
            current_price=60513.0,
            bias="short",
            market_regime="range",
            long_setup=self._long_setup(),
            short_setup=self._short_setup(),
            confidence_direction_shadow=72.0,
            confidence_execution_shadow=18.0,
            confidence_wait_shadow=59.2,
            risk_flags=["short_into_major_support", "short_at_major_support_wait_only"],
            market_map_flags=["support_to_resistance_flip", "major_resistance_rejection", "trend_flip_early_down"],
            no_trade_flags=[],
            data_quality_flag="ok",
            breakout_up=False,
            breakout_down=False,
            volume_ratio=1.0,
            trigger_volume_ratio_threshold=1.5,
        )
        return {
            "signal_id": "20260606_230500",
            "timestamp_jst": "2026-06-06T23:05:00+09:00",
            "current_price": 60513.0,
            "active_trade_plan": plan,
            "active_primary_action": plan["primary_action"],
            "active_headline": plan["headline"],
        }

    def _payload_for_market(self) -> dict[str, object]:
        plan = build_active_trade_plan(
            current_price=60750.0,
            bias="short",
            market_regime="range",
            long_setup=self._long_setup(),
            short_setup=self._short_setup(),
            confidence_direction_shadow=72.0,
            confidence_execution_shadow=30.0,
            confidence_wait_shadow=30.0,
            risk_flags=[],
            market_map_flags=["support_to_resistance_flip"],
            no_trade_flags=[],
            data_quality_flag="ok",
            breakout_up=False,
            breakout_down=False,
            volume_ratio=1.0,
            trigger_volume_ratio_threshold=1.5,
        )
        return {
            "signal_id": "20260606_231000",
            "timestamp_jst": "2026-06-06T23:10:00+09:00",
            "current_price": 60750.0,
            "active_trade_plan": plan,
            "active_primary_action": plan["primary_action"],
            "active_headline": plan["headline"],
        }

    def test_limit_retest_and_counter_scalp_candidates_are_logged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            path = append_active_plan_candidates(base_dir, self._payload_for_limit_and_counter())
            rows = self._read_rows(path)

        self.assertEqual(len(rows), 2)
        candidate_ids = {row["candidate_id"] for row in rows}
        self.assertEqual(
            candidate_ids,
            {
                "20260606_230500:short:limit_retest",
                "20260606_230500:long:counter_scalp",
            },
        )

    def test_market_candidate_is_logged_for_active_market_small(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            path = append_active_plan_candidates(base_dir, self._payload_for_market())
            rows = self._read_rows(path)

        self.assertEqual(len(rows), 1)
        market_rows = [row for row in rows if row["candidate_type"] == "market"]
        self.assertEqual(len(market_rows), 1)
        self.assertEqual(market_rows[0]["candidate_id"], "20260606_231000:short:market")
        self.assertEqual(market_rows[0]["candidate_status"], "allowed")

    def test_duplicate_candidate_ids_are_not_appended_twice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            payload = self._payload_for_limit_and_counter()
            path = append_active_plan_candidates(base_dir, payload)
            append_active_plan_candidates(base_dir, payload)
            rows = self._read_rows(path)

        self.assertEqual(len(rows), 2)
        self.assertEqual(
            [row["candidate_id"] for row in rows],
            [
                "20260606_230500:long:counter_scalp",
                "20260606_230500:short:limit_retest",
            ],
        )

    def test_invalid_or_empty_active_trade_plan_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            path = append_active_plan_candidates(
                base_dir,
                {
                    "signal_id": "",
                    "timestamp_jst": "2026-06-06T23:20:00+09:00",
                    "current_price": 60000.0,
                    "active_trade_plan": "",
                },
            )
            rows = self._read_rows(path)
            with path.open("r", newline="", encoding="utf-8") as fp:
                header = next(csv.reader(fp))

        self.assertEqual(rows, [])
        self.assertEqual(header, ACTIVE_PLAN_CANDIDATE_HEADER)


if __name__ == "__main__":
    unittest.main()
