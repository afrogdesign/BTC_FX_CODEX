from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.log_feedback import (
    ACTIVE_PLAN_CANDIDATE_INTRAPERIOD_HEADER,
    build_active_plan_candidate_intraperiod_outcomes,
)


class ActivePlanCandidateIntraperiodOutcomesTests(unittest.TestCase):
    def _write_csv(self, path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        return path

    def _write_candidates_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        return self._write_csv(
            base_dir / "logs" / "csv" / "active_plan_paper_candidates.csv",
            [
                "candidate_id",
                "source_signal_id",
                "timestamp_jst",
                "active_primary_action",
                "candidate_type",
                "candidate_status",
                "side",
                "entry_mode",
                "entry_price",
                "entry_zone_low",
                "entry_zone_high",
                "stop_loss",
                "tp1",
                "tp2",
                "active_subject_label",
                "active_headline",
                "next_condition",
            ],
            rows,
        )

    def _write_ohlcv_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        return self._write_csv(
            base_dir / "logs" / "csv" / "fixture_15m_ohlcv.csv",
            ["timestamp_jst", "open", "high", "low", "close"],
            rows,
        )

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", newline="", encoding="utf-8") as fp:
            return list(csv.DictReader(fp))

    def test_active_plan_candidate_intraperiod_header_is_fixed(self) -> None:
        expected = [
            "candidate_id",
            "source_signal_id",
            "timestamp_jst",
            "active_primary_action",
            "candidate_type",
            "candidate_status",
            "side",
            "entry_mode",
            "entry_price",
            "entry_zone_low",
            "entry_zone_high",
            "stop_loss",
            "tp1",
            "tp2",
            "active_subject_label",
            "active_headline",
            "next_condition",
            "evaluation_status",
            "entry_reached",
            "entry_reached_at_jst",
            "entry_reached_price",
            "first_exit",
            "first_exit_at_jst",
            "first_exit_price",
            "tp1_reached",
            "tp1_reached_at_jst",
            "tp2_reached",
            "tp2_reached_at_jst",
            "sl_reached",
            "sl_reached_at_jst",
            "timeout_reached",
            "timeout_at_jst",
            "mfe",
            "mae",
            "mfe_price",
            "mae_price",
            "max_favorable_at_jst",
            "max_adverse_at_jst",
            "bars_evaluated",
            "evaluation_window_hours",
            "notes",
        ]
        self.assertEqual(ACTIVE_PLAN_CANDIDATE_INTRAPERIOD_HEADER, expected)

    def test_intraperiod_outcomes_scores_long_tp1_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s1:active_limit_retest:long",
                        "source_signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:00:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "candidate_type": "active_limit_retest",
                        "candidate_status": "candidate",
                        "side": "long",
                        "entry_mode": "limit_zone_mid",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                        "active_subject_label": "押し目買い待ち",
                        "active_headline": "long tp fixture",
                    }
                ],
            )
            ohlcv_path = self._write_ohlcv_csv(
                base_dir,
                [
                    {"timestamp_jst": "2026-06-07T09:15:00+09:00", "open": "103", "high": "104", "low": "99", "close": "101"},
                    {"timestamp_jst": "2026-06-07T09:30:00+09:00", "open": "101", "high": "111", "low": "100", "close": "110"},
                ],
            )

            output = build_active_plan_candidate_intraperiod_outcomes(base_dir=base_dir, ohlcv_path=ohlcv_path)
            rows = self._read_rows(output)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["evaluation_status"], "complete")
        self.assertEqual(row["entry_reached"], "true")
        self.assertEqual(row["first_exit"], "tp1")
        self.assertEqual(row["tp1_reached"], "true")
        self.assertEqual(row["sl_reached"], "")
        self.assertEqual(row["mfe"], "11.00")
        self.assertEqual(row["mae"], "1.00")

    def test_intraperiod_outcomes_scores_short_sl_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s2:active_market_small:short",
                        "source_signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:00:00+09:00",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "candidate_type": "active_market_small",
                        "candidate_status": "candidate",
                        "side": "short",
                        "entry_mode": "market",
                        "entry_price": "100",
                        "stop_loss": "105",
                        "tp1": "90",
                        "tp2": "80",
                    }
                ],
            )
            ohlcv_path = self._write_ohlcv_csv(
                base_dir,
                [
                    {"timestamp_jst": "2026-06-07T10:15:00+09:00", "open": "100", "high": "106", "low": "96", "close": "104"},
                ],
            )

            output = build_active_plan_candidate_intraperiod_outcomes(base_dir=base_dir, ohlcv_path=ohlcv_path)
            row = self._read_rows(output)[0]

        self.assertEqual(row["evaluation_status"], "complete")
        self.assertEqual(row["entry_reached"], "true")
        self.assertEqual(row["first_exit"], "sl")
        self.assertEqual(row["sl_reached"], "true")
        self.assertEqual(row["first_exit_price"], "105.00")

    def test_intraperiod_outcomes_marks_limit_not_entered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s3:active_limit_retest:long",
                        "source_signal_id": "s3",
                        "timestamp_jst": "2026-06-07T09:00:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "candidate_type": "active_limit_retest",
                        "candidate_status": "candidate",
                        "side": "long",
                        "entry_mode": "limit_zone_mid",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                    }
                ],
            )
            ohlcv_path = self._write_ohlcv_csv(
                base_dir,
                [
                    {"timestamp_jst": "2026-06-07T09:15:00+09:00", "open": "105", "high": "108", "low": "104", "close": "107"},
                    {"timestamp_jst": "2026-06-08T09:00:00+09:00", "open": "106", "high": "108", "low": "104", "close": "105"},
                ],
            )

            output = build_active_plan_candidate_intraperiod_outcomes(base_dir=base_dir, ohlcv_path=ohlcv_path)
            row = self._read_rows(output)[0]

        self.assertEqual(row["evaluation_status"], "not_entered")
        self.assertEqual(row["entry_reached"], "false")
        self.assertEqual(row["first_exit"], "not_entered")

    def test_intraperiod_outcomes_marks_same_bar_tp_sl_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s4:active_limit_retest:long",
                        "source_signal_id": "s4",
                        "timestamp_jst": "2026-06-07T09:00:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "candidate_type": "active_limit_retest",
                        "candidate_status": "candidate",
                        "side": "long",
                        "entry_mode": "market",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                    }
                ],
            )
            ohlcv_path = self._write_ohlcv_csv(
                base_dir,
                [
                    {"timestamp_jst": "2026-06-07T09:15:00+09:00", "open": "100", "high": "111", "low": "94", "close": "99"},
                ],
            )

            output = build_active_plan_candidate_intraperiod_outcomes(base_dir=base_dir, ohlcv_path=ohlcv_path)
            row = self._read_rows(output)[0]

        self.assertEqual(row["evaluation_status"], "complete")
        self.assertEqual(row["first_exit"], "ambiguous_sl_first")
        self.assertIn("same_bar_tp_sl_ambiguous_conservative_sl", row["notes"])

    def test_intraperiod_outcomes_marks_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s5:active_limit_retest:long",
                        "source_signal_id": "s5",
                        "timestamp_jst": "2026-06-07T09:00:00+09:00",
                        "side": "long",
                        "entry_mode": "market",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                    }
                ],
            )
            ohlcv_path = self._write_ohlcv_csv(
                base_dir,
                [
                    {"timestamp_jst": "2026-06-07T09:15:00+09:00", "open": "100", "high": "104", "low": "98", "close": "101"},
                    {"timestamp_jst": "2026-06-08T09:00:00+09:00", "open": "101", "high": "104", "low": "98", "close": "102"},
                ],
            )

            output = build_active_plan_candidate_intraperiod_outcomes(base_dir=base_dir, ohlcv_path=ohlcv_path)
            row = self._read_rows(output)[0]

        self.assertEqual(row["evaluation_status"], "timeout")
        self.assertEqual(row["first_exit"], "timeout")
        self.assertEqual(row["timeout_reached"], "true")

    def test_intraperiod_outcomes_marks_pending_when_window_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s6:active_limit_retest:long",
                        "source_signal_id": "s6",
                        "timestamp_jst": "2026-06-07T09:00:00+09:00",
                        "side": "long",
                        "entry_mode": "market",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                    }
                ],
            )
            ohlcv_path = self._write_ohlcv_csv(
                base_dir,
                [
                    {"timestamp_jst": "2026-06-07T09:15:00+09:00", "open": "100", "high": "104", "low": "98", "close": "101"},
                ],
            )

            output = build_active_plan_candidate_intraperiod_outcomes(base_dir=base_dir, ohlcv_path=ohlcv_path)
            row = self._read_rows(output)[0]

        self.assertEqual(row["evaluation_status"], "pending")
        self.assertEqual(row["first_exit"], "pending")

    def test_intraperiod_outcomes_marks_no_ohlcv_when_path_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s7:active_limit_retest:long",
                        "source_signal_id": "s7",
                        "timestamp_jst": "2026-06-07T09:00:00+09:00",
                        "side": "long",
                        "entry_mode": "market",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                    }
                ],
            )

            output = build_active_plan_candidate_intraperiod_outcomes(base_dir=base_dir)
            row = self._read_rows(output)[0]

        self.assertEqual(row["evaluation_status"], "no_ohlcv")
        self.assertEqual(row["first_exit"], "no_ohlcv")

    def test_intraperiod_outcomes_accepts_output_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(base_dir, [])
            output_csv = base_dir / "custom" / "intraperiod.csv"

            result = build_active_plan_candidate_intraperiod_outcomes(
                base_dir=base_dir,
                output_csv=output_csv,
            )
            self.assertEqual(result, output_csv)
            self.assertTrue(output_csv.exists())
