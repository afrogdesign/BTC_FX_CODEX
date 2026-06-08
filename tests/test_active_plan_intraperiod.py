from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

import pandas as pd

from src.trade.active_plan_intraperiod import evaluate_active_plan_intraperiod_candidate


JST = timezone(timedelta(hours=9))


class ActivePlanIntraperiodTests(unittest.TestCase):
    def _candidate(self, **overrides: str) -> dict[str, str]:
        base = {
            "candidate_id": "cand-1",
            "source_signal_id": "sig-1",
            "timestamp_jst": "2026-06-08T09:00:00+09:00",
            "active_primary_action": "ACTIVE_LIMIT_RETEST",
            "candidate_type": "active_limit_retest",
            "candidate_status": "candidate",
            "side": "long",
            "entry_mode": "limit_zone_mid",
            "entry_price": "100",
            "entry_zone_low": "",
            "entry_zone_high": "",
            "stop_loss": "95",
            "tp1": "110",
            "tp2": "120",
            "active_subject_label": "押し目買い待ち",
            "active_headline": "fixture",
            "next_condition": "",
        }
        base.update(overrides)
        return base

    def _ohlcv(self, rows: list[dict[str, str]]) -> pd.DataFrame:
        return pd.DataFrame(rows)

    def test_long_candidate_reaches_entry_then_tp1(self) -> None:
        candidate = self._candidate(
            candidate_id="long-tp",
            source_signal_id="sig-long-tp",
            entry_price="100",
            entry_zone_low="",
            entry_zone_high="",
            stop_loss="95",
            tp1="110",
            tp2="120",
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "100.5", "low": "98.5", "close": "100"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "100", "high": "111", "low": "99", "close": "110"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(
            candidate,
            ohlcv,
            now=datetime(2026, 6, 9, 10, 0, tzinfo=JST),
        )

        self.assertEqual(result["signal_id"], "sig-long-tp")
        self.assertEqual(result["stop_price"], "95.00")
        self.assertEqual(result["tp1_price"], "110.00")
        self.assertEqual(result["tp2_price"], "120.00")
        self.assertEqual(result["outcome"], "tp1_first")
        self.assertEqual(result["entry_reached_time"], "2026-06-08T09:15:00+09:00")
        self.assertEqual(result["first_exit_time"], "2026-06-08T09:30:00+09:00")
        self.assertEqual(result["first_exit_reason"], "tp1")
        self.assertEqual(result["mfe_price"], "11.00")
        self.assertEqual(result["mae_price"], "1.50")
        self.assertEqual(result["mfe_r"], "2.2000")
        self.assertEqual(result["mae_r"], "0.3000")

    def test_entry_zone_takes_precedence_over_entry_price(self) -> None:
        candidate = self._candidate(
            candidate_id="zone-priority",
            source_signal_id="sig-zone-priority",
            entry_price="150",
            entry_zone_low="99",
            entry_zone_high="101",
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "100.5", "low": "98.5", "close": "100"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(
            candidate,
            ohlcv,
            now=datetime(2026, 6, 8, 9, 30, tzinfo=JST),
            timeout_hours=1.0,
        )

        self.assertEqual(result["outcome"], "entry_reached")
        self.assertEqual(result["entry_reached_time"], "2026-06-08T09:15:00+09:00")

    def test_long_candidate_reaches_entry_then_sl(self) -> None:
        candidate = self._candidate(candidate_id="long-sl", source_signal_id="sig-long-sl")
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "100", "high": "103", "low": "94", "close": "95"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(candidate, ohlcv, now=datetime(2026, 6, 9, 10, 0, tzinfo=JST))

        self.assertEqual(result["outcome"], "sl_first")
        self.assertEqual(result["first_exit_reason"], "sl")

    def test_short_candidate_reaches_entry_then_tp1(self) -> None:
        candidate = self._candidate(
            candidate_id="short-tp",
            source_signal_id="sig-short-tp",
            side="short",
            stop_loss="105",
            tp1="90",
            tp2="80",
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "100", "high": "100", "low": "89", "close": "90"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(candidate, ohlcv, now=datetime(2026, 6, 9, 10, 0, tzinfo=JST))

        self.assertEqual(result["outcome"], "tp1_first")
        self.assertEqual(result["first_exit_reason"], "tp1")

    def test_short_candidate_reaches_entry_then_sl(self) -> None:
        candidate = self._candidate(
            candidate_id="short-sl",
            source_signal_id="sig-short-sl",
            side="short",
            stop_loss="105",
            tp1="90",
            tp2="80",
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "100", "high": "106", "low": "98", "close": "104"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(candidate, ohlcv, now=datetime(2026, 6, 9, 10, 0, tzinfo=JST))

        self.assertEqual(result["outcome"], "sl_first")
        self.assertEqual(result["first_exit_reason"], "sl")

    def test_candidate_never_reaches_entry(self) -> None:
        candidate = self._candidate(candidate_id="never-enter", source_signal_id="sig-never-enter", entry_price="100")
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "98", "high": "99", "low": "97", "close": "98"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "98", "high": "99", "low": "97", "close": "98"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(candidate, ohlcv, now=datetime(2026, 6, 9, 10, 0, tzinfo=JST))

        self.assertEqual(result["outcome"], "not_entered")
        self.assertEqual(result["entry_reached_time"], "")
        self.assertEqual(result["first_exit_reason"], "")

    def test_candidate_entry_reached_then_times_out(self) -> None:
        candidate = self._candidate(candidate_id="entry-timeout", source_signal_id="sig-entry-timeout", entry_price="100")
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "100", "high": "104", "low": "98", "close": "101"},
                {"timestamp_jst": "2026-06-08T09:45:00+09:00", "open": "101", "high": "103", "low": "99", "close": "100"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(candidate, ohlcv, now=datetime(2026, 6, 9, 10, 0, tzinfo=JST), timeout_hours=1.0)

        self.assertEqual(result["outcome"], "timeout")
        self.assertEqual(result["first_exit_reason"], "timeout")
        self.assertEqual(result["first_exit_time"], "2026-06-08T10:00:00+09:00")

    def test_candidate_entry_reached_but_window_incomplete(self) -> None:
        candidate = self._candidate(candidate_id="entry-pending", source_signal_id="sig-entry-pending", entry_price="100")
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(candidate, ohlcv, now=datetime(2026, 6, 8, 9, 30, tzinfo=JST), timeout_hours=1.0)

        self.assertEqual(result["outcome"], "entry_reached")
        self.assertEqual(result["entry_reached_time"], "2026-06-08T09:15:00+09:00")
        self.assertEqual(result["first_exit_time"], "")

    def test_same_bar_tp_sl_ambiguity(self) -> None:
        candidate = self._candidate(candidate_id="ambiguous", source_signal_id="sig-ambiguous", entry_price="100", stop_loss="95", tp1="110", tp2="120")
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "100", "high": "111", "low": "94", "close": "105"},
            ]
        )

        result = evaluate_active_plan_intraperiod_candidate(candidate, ohlcv, now=datetime(2026, 6, 9, 10, 0, tzinfo=JST))

        self.assertEqual(result["outcome"], "ambiguous")
        self.assertEqual(result["first_exit_reason"], "ambiguous")
        self.assertEqual(result["first_exit_time"], "2026-06-08T09:30:00+09:00")

    def test_missing_ohlcv(self) -> None:
        candidate = self._candidate(candidate_id="missing-ohlcv", source_signal_id="sig-missing-ohlcv")

        result = evaluate_active_plan_intraperiod_candidate(candidate, None, now=datetime(2026, 6, 9, 10, 0, tzinfo=JST))

        self.assertEqual(result["outcome"], "no_ohlcv")
        self.assertEqual(result["entry_reached_time"], "")
        self.assertEqual(result["first_exit_reason"], "")


if __name__ == "__main__":
    unittest.main()
