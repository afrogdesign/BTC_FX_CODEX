from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from src.trade.active_plan_intraperiod import (
    MIN_OUTCOME_COLUMNS,
    build_active_plan_intraperiod_outcome_rows,
    summarize_intraperiod_entry_reached_outcomes,
    summarize_intraperiod_outcome_coverage,
    summarize_intraperiod_valid_sample_winrate,
    write_active_plan_intraperiod_outcomes,
)


JST = timezone(timedelta(hours=9))


class ActivePlanIntraperiodOutcomeBuilderTests(unittest.TestCase):
    def _candidates(self, rows: list[dict[str, str]]) -> pd.DataFrame:
        return pd.DataFrame(rows)

    def _ohlcv(self, rows: list[dict[str, str]]) -> pd.DataFrame:
        return pd.DataFrame(rows)

    def test_builder_emits_minimum_output_columns(self) -> None:
        candidates = self._candidates(
            [
                {
                    "candidate_id": "cand-1",
                    "source_signal_id": "sig-1",
                    "timestamp_jst": "2026-06-08T09:00:00+09:00",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit_zone_mid",
                    "entry_price": "100",
                    "stop_loss": "95",
                    "tp1": "110",
                    "tp2": "120",
                }
            ]
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "111", "low": "99", "close": "110"},
            ]
        )

        result = build_active_plan_intraperiod_outcome_rows(
            candidates,
            ohlcv,
            now=datetime(2026, 6, 9, 10, 0, tzinfo=JST),
        )

        self.assertEqual(result.columns[: len(MIN_OUTCOME_COLUMNS)].tolist(), MIN_OUTCOME_COLUMNS)
        self.assertEqual(result.loc[0, "candidate_id"], "cand-1")

    def test_builder_preserves_candidate_identity_fields(self) -> None:
        candidates = self._candidates(
            [
                {
                    "candidate_id": "cand-identity",
                    "signal_id": "sig-direct",
                    "timestamp_jst": "2026-06-08T09:00:00+09:00",
                    "candidate_type": "active_breakout",
                    "active_primary_action": "ACTIVE_BREAKOUT_BUY",
                    "side": "long",
                    "entry_mode": "market",
                    "entry_price": "100",
                    "stop_loss": "95",
                    "tp1": "110",
                    "tp2": "120",
                    "strategy_bucket": "bucket-a",
                }
            ]
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
            ]
        )

        result = build_active_plan_intraperiod_outcome_rows(
            candidates,
            ohlcv,
            now=datetime(2026, 6, 8, 9, 30, tzinfo=JST),
            timeout_hours=1.0,
        )

        self.assertEqual(result.loc[0, "candidate_id"], "cand-identity")
        self.assertEqual(result.loc[0, "signal_id"], "sig-direct")
        self.assertEqual(result.loc[0, "timestamp_jst"], "2026-06-08T09:00:00+09:00")
        self.assertEqual(result.loc[0, "candidate_type"], "active_breakout")
        self.assertEqual(result.loc[0, "active_primary_action"], "ACTIVE_BREAKOUT_BUY")
        self.assertEqual(result.loc[0, "strategy_bucket"], "bucket-a")

    def test_builder_long_candidate_entry_then_tp(self) -> None:
        candidates = self._candidates(
            [
                {
                    "candidate_id": "cand-long-tp",
                    "source_signal_id": "sig-long-tp",
                    "timestamp_jst": "2026-06-08T09:00:00+09:00",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit_zone_mid",
                    "entry_price": "100",
                    "stop_loss": "95",
                    "tp1": "110",
                    "tp2": "120",
                }
            ]
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "100.5", "low": "99", "close": "100"},
                {"timestamp_jst": "2026-06-08T09:30:00+09:00", "open": "100", "high": "111", "low": "99.5", "close": "110"},
            ]
        )

        result = build_active_plan_intraperiod_outcome_rows(
            candidates,
            ohlcv,
            now=datetime(2026, 6, 9, 10, 0, tzinfo=JST),
        )

        self.assertEqual(result.loc[0, "outcome"], "tp1_first")
        self.assertEqual(result.loc[0, "entry_reached_time"], "2026-06-08T09:15:00+09:00")
        self.assertEqual(result.loc[0, "first_exit_reason"], "tp1")

    def test_builder_missing_ohlcv_returns_no_ohlcv(self) -> None:
        candidates = self._candidates(
            [
                {
                    "candidate_id": "cand-no-ohlcv",
                    "source_signal_id": "sig-no-ohlcv",
                    "timestamp_jst": "2026-06-08T09:00:00+09:00",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit_zone_mid",
                    "entry_price": "100",
                }
            ]
        )

        result = build_active_plan_intraperiod_outcome_rows(
            candidates,
            None,
            now=datetime(2026, 6, 9, 10, 0, tzinfo=JST),
        )

        self.assertEqual(result.loc[0, "outcome"], "no_ohlcv")
        self.assertEqual(result.loc[0, "entry_reached_time"], "")

    def test_builder_missing_required_candidate_fields_does_not_invent_values(self) -> None:
        candidates = self._candidates(
            [
                {
                    "candidate_id": "cand-missing-fields",
                    "timestamp_jst": "2026-06-08T09:00:00+09:00",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                }
            ]
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "101", "low": "99", "close": "100"},
            ]
        )

        result = build_active_plan_intraperiod_outcome_rows(
            candidates,
            ohlcv,
            now=datetime(2026, 6, 8, 10, 0, tzinfo=JST),
        )

        self.assertEqual(result.loc[0, "outcome"], "pending")
        self.assertEqual(result.loc[0, "signal_id"], "")
        self.assertEqual(result.loc[0, "entry_mode"], "")
        self.assertEqual(result.loc[0, "entry_price"], "")
        self.assertEqual(result.loc[0, "stop_price"], "")
        self.assertEqual(result.loc[0, "tp1_price"], "")
        self.assertEqual(result.loc[0, "tp2_price"], "")

    def test_writer_outputs_csv_without_new_logic(self) -> None:
        candidates = self._candidates(
            [
                {
                    "candidate_id": "cand-writer",
                    "source_signal_id": "sig-writer",
                    "timestamp_jst": "2026-06-08T09:00:00+09:00",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit_zone_mid",
                    "entry_price": "100",
                    "stop_loss": "95",
                    "tp1": "110",
                    "tp2": "120",
                }
            ]
        )
        ohlcv = self._ohlcv(
            [
                {"timestamp_jst": "2026-06-08T09:15:00+09:00", "open": "100", "high": "111", "low": "99", "close": "110"},
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            candidates_path = Path(tmpdir) / "candidates.csv"
            output_path = Path(tmpdir) / "active_plan_candidate_intraperiod_outcomes.csv"
            candidates.to_csv(candidates_path, index=False)

            result = write_active_plan_intraperiod_outcomes(
                candidates_path,
                ohlcv,
                output_path,
                now=datetime(2026, 6, 9, 10, 0, tzinfo=JST),
            )

            written = pd.read_csv(output_path)
            self.assertEqual(result.loc[0, "candidate_id"], "cand-writer")
            self.assertEqual(written.loc[0, "candidate_id"], "cand-writer")
            self.assertEqual(written.loc[0, "outcome"], "tp1_first")

    def test_summarize_intraperiod_outcome_coverage(self) -> None:
        outcomes_df = pd.DataFrame(
            {
                "outcome": [
                    "no_ohlcv",
                    "tp1_first",
                    "sl_first",
                    "timeout",
                    "not_entered",
                ]
            }
        )

        summary = summarize_intraperiod_outcome_coverage(outcomes_df)

        self.assertEqual(summary["total_rows"], 5)
        self.assertEqual(summary["no_ohlcv_rows"], 1)
        self.assertEqual(summary["valid_sample_rows"], 4)
        self.assertEqual(summary["entry_reached_rows"], 3)
        self.assertAlmostEqual(summary["no_ohlcv_rate"], 0.2)
        self.assertAlmostEqual(summary["valid_sample_rate"], 0.8)
        self.assertAlmostEqual(summary["entry_reached_rate"], 0.6)
        self.assertEqual(summary["valid_sample_definition"], "rows excluding outcome == no_ohlcv")

        empty_summary = summarize_intraperiod_outcome_coverage(pd.DataFrame())
        none_summary = summarize_intraperiod_outcome_coverage(None)
        for item in (empty_summary, none_summary):
            self.assertEqual(item["total_rows"], 0)
            self.assertEqual(item["no_ohlcv_rows"], 0)
            self.assertEqual(item["valid_sample_rows"], 0)
            self.assertEqual(item["entry_reached_rows"], 0)
            self.assertEqual(item["no_ohlcv_rate"], 0.0)
            self.assertEqual(item["valid_sample_rate"], 0.0)
            self.assertEqual(item["entry_reached_rate"], 0.0)
            self.assertEqual(item["valid_sample_definition"], "rows excluding outcome == no_ohlcv")

    def test_summarize_intraperiod_valid_sample_winrate(self) -> None:
        outcomes_df = pd.DataFrame(
            {
                "outcome": [
                    "no_ohlcv",
                    "tp1_first",
                    "tp2_first",
                    "sl_first",
                    "timeout",
                    "ambiguous",
                    "entry_reached",
                    "not_entered",
                    "pending",
                ]
            }
        )

        summary = summarize_intraperiod_valid_sample_winrate(outcomes_df)

        self.assertEqual(summary["total_rows"], 9)
        self.assertEqual(summary["no_ohlcv_rows"], 1)
        self.assertEqual(summary["valid_sample_rows"], 8)
        self.assertEqual(summary["entry_reached_rows"], 6)
        self.assertEqual(summary["win_like_rows"], 2)
        self.assertEqual(summary["loss_like_rows"], 1)
        self.assertEqual(summary["unresolved_entry_rows"], 3)
        self.assertEqual(summary["not_entered_rows"], 1)
        self.assertEqual(summary["pending_rows"], 1)
        self.assertAlmostEqual(summary["valid_sample_rate"], 8 / 9)
        self.assertAlmostEqual(summary["entry_reached_rate_of_valid_sample"], 6 / 8)
        self.assertAlmostEqual(summary["win_like_rate_of_entry_reached"], 2 / 6)
        self.assertAlmostEqual(summary["loss_like_rate_of_entry_reached"], 1 / 6)
        self.assertAlmostEqual(summary["unresolved_rate_of_entry_reached"], 3 / 6)
        self.assertEqual(summary["valid_sample_definition"], "rows excluding outcome == no_ohlcv")
        self.assertEqual(
            summary["winrate_definition"],
            "win-like outcomes divided by entry-reached rows; report-only, not profitability",
        )
        self.assertEqual(
            summary["safety_note"],
            "report-only / not FORMAL_GO / no automatic order / human decides manually",
        )

        empty_summary = summarize_intraperiod_valid_sample_winrate(pd.DataFrame())
        none_summary = summarize_intraperiod_valid_sample_winrate(None)
        for item in (empty_summary, none_summary):
            self.assertEqual(item["total_rows"], 0)
            self.assertEqual(item["no_ohlcv_rows"], 0)
            self.assertEqual(item["valid_sample_rows"], 0)
            self.assertEqual(item["entry_reached_rows"], 0)
            self.assertEqual(item["win_like_rows"], 0)
            self.assertEqual(item["loss_like_rows"], 0)
            self.assertEqual(item["unresolved_entry_rows"], 0)
            self.assertEqual(item["not_entered_rows"], 0)
            self.assertEqual(item["pending_rows"], 0)
            self.assertEqual(item["valid_sample_rate"], 0.0)
            self.assertEqual(item["entry_reached_rate_of_valid_sample"], 0.0)
            self.assertEqual(item["win_like_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["loss_like_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["unresolved_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["valid_sample_definition"], "rows excluding outcome == no_ohlcv")
            self.assertEqual(
                item["winrate_definition"],
                "win-like outcomes divided by entry-reached rows; report-only, not profitability",
            )
            self.assertEqual(
                item["safety_note"],
                "report-only / not FORMAL_GO / no automatic order / human decides manually",
            )

    def test_summarize_intraperiod_entry_reached_outcomes(self) -> None:
        outcomes_df = pd.DataFrame(
            {
                "outcome": [
                    "no_ohlcv",
                    "tp1_first",
                    "tp2_first",
                    "sl_first",
                    "timeout",
                    "ambiguous",
                    "entry_reached",
                    "not_entered",
                    "pending",
                ]
            }
        )

        summary = summarize_intraperiod_entry_reached_outcomes(outcomes_df)

        self.assertEqual(summary["entry_reached_rows"], 6)
        self.assertEqual(summary["tp1_first_rows"], 1)
        self.assertEqual(summary["tp2_first_rows"], 1)
        self.assertEqual(summary["sl_first_rows"], 1)
        self.assertEqual(summary["timeout_rows"], 1)
        self.assertEqual(summary["ambiguous_rows"], 1)
        self.assertEqual(summary["open_entry_reached_rows"], 1)
        self.assertEqual(summary["resolved_exit_rows"], 3)
        self.assertEqual(summary["unresolved_entry_rows"], 3)
        self.assertAlmostEqual(summary["tp1_first_rate_of_entry_reached"], 1 / 6)
        self.assertAlmostEqual(summary["tp2_first_rate_of_entry_reached"], 1 / 6)
        self.assertAlmostEqual(summary["sl_first_rate_of_entry_reached"], 1 / 6)
        self.assertAlmostEqual(summary["timeout_rate_of_entry_reached"], 1 / 6)
        self.assertAlmostEqual(summary["ambiguous_rate_of_entry_reached"], 1 / 6)
        self.assertAlmostEqual(summary["open_entry_reached_rate_of_entry_reached"], 1 / 6)
        self.assertAlmostEqual(summary["resolved_exit_rate_of_entry_reached"], 3 / 6)
        self.assertAlmostEqual(summary["unresolved_entry_rate_of_entry_reached"], 3 / 6)
        self.assertEqual(
            summary["entry_reached_definition"],
            "tp1_first, tp2_first, sl_first, timeout, ambiguous, entry_reached",
        )
        self.assertEqual(
            summary["safety_note"],
            "report-only / not FORMAL_GO / no automatic order / human decides manually",
        )

        empty_summary = summarize_intraperiod_entry_reached_outcomes(pd.DataFrame())
        none_summary = summarize_intraperiod_entry_reached_outcomes(None)
        for item in (empty_summary, none_summary):
            self.assertEqual(item["entry_reached_rows"], 0)
            self.assertEqual(item["tp1_first_rows"], 0)
            self.assertEqual(item["tp2_first_rows"], 0)
            self.assertEqual(item["sl_first_rows"], 0)
            self.assertEqual(item["timeout_rows"], 0)
            self.assertEqual(item["ambiguous_rows"], 0)
            self.assertEqual(item["open_entry_reached_rows"], 0)
            self.assertEqual(item["resolved_exit_rows"], 0)
            self.assertEqual(item["unresolved_entry_rows"], 0)
            self.assertEqual(item["tp1_first_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["tp2_first_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["sl_first_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["timeout_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["ambiguous_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["open_entry_reached_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["resolved_exit_rate_of_entry_reached"], 0.0)
            self.assertEqual(item["unresolved_entry_rate_of_entry_reached"], 0.0)
            self.assertEqual(
                item["entry_reached_definition"],
                "tp1_first, tp2_first, sl_first, timeout, ambiguous, entry_reached",
            )
            self.assertEqual(
                item["safety_note"],
                "report-only / not FORMAL_GO / no automatic order / human decides manually",
            )


if __name__ == "__main__":
    unittest.main()
