from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.log_feedback import ACTIVE_PLAN_CANDIDATE_OUTCOME_HEADER, build_active_plan_candidate_outcomes


class ActivePlanCandidateOutcomesTests(unittest.TestCase):
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
                "rr_current_tp1",
                "rr_current_tp2",
                "rr_zone_mid_tp1",
                "rr_zone_mid_tp2",
                "market_entry_status",
                "limit_entry_status",
                "counter_scalp_status",
                "breakout_status",
                "active_subject_label",
                "active_headline",
                "next_condition",
            ],
            rows,
        )

    def _write_outcomes_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        return self._write_csv(
            base_dir / "logs" / "csv" / "signal_outcomes.csv",
            [
                "signal_id",
                "timestamp_jst",
                "forward_price_12h",
                "forward_price_24h",
                "direction_outcome",
                "tp1_hit_first",
                "outcome",
                "evaluation_status",
            ],
            rows,
        )

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", newline="", encoding="utf-8") as fp:
            return list(csv.DictReader(fp))

    def test_active_plan_candidate_outcome_header_contains_expected_columns(self) -> None:
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
            "rr_current_tp1",
            "rr_current_tp2",
            "rr_zone_mid_tp1",
            "rr_zone_mid_tp2",
            "active_subject_label",
            "active_headline",
            "next_condition",
            "outcome_evaluation_status",
            "outcome_forward_price_12h",
            "outcome_forward_price_24h",
            "candidate_delta_12h",
            "candidate_delta_24h",
            "candidate_result_12h",
            "candidate_result_24h",
            "tp1_close_reached_24h",
            "tp2_close_reached_24h",
            "sl_close_reached_24h",
            "outcome_direction_outcome",
            "outcome_tp1_hit_first",
            "outcome_outcome",
        ]
        self.assertEqual(ACTIVE_PLAN_CANDIDATE_OUTCOME_HEADER, expected)

    def test_build_active_plan_candidate_outcomes_scores_long_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s1:active_limit_retest:long",
                        "source_signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "candidate_type": "active_limit_retest",
                        "candidate_status": "candidate",
                        "side": "long",
                        "entry_mode": "limit_zone_mid",
                        "entry_price": "60423.25",
                        "stop_loss": "60025.57",
                        "tp1": "60940.23",
                        "tp2": "61377.68",
                        "active_subject_label": "押し目買い待ち",
                        "active_headline": "押し目買い候補。",
                    }
                ],
            )
            self._write_outcomes_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "forward_price_12h": "60700.00",
                        "forward_price_24h": "61000.00",
                        "direction_outcome": "correct",
                        "tp1_hit_first": "true",
                        "outcome": "win",
                        "evaluation_status": "complete",
                    }
                ],
            )

            output_csv = build_active_plan_candidate_outcomes(base_dir=base_dir)
            rows = self._read_rows(output_csv)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["candidate_id"], "s1:active_limit_retest:long")
        self.assertEqual(row["candidate_delta_12h"], "276.75")
        self.assertEqual(row["candidate_delta_24h"], "576.75")
        self.assertEqual(row["candidate_result_12h"], "favorable")
        self.assertEqual(row["candidate_result_24h"], "favorable")
        self.assertEqual(row["tp1_close_reached_24h"], "true")
        self.assertEqual(row["tp2_close_reached_24h"], "false")
        self.assertEqual(row["sl_close_reached_24h"], "false")
        self.assertEqual(row["outcome_evaluation_status"], "complete")

    def test_build_active_plan_candidate_outcomes_scores_short_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s2:active_market_small:short",
                        "source_signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "candidate_type": "active_market_small",
                        "candidate_status": "candidate",
                        "side": "short",
                        "entry_mode": "market",
                        "entry_price": "60750.00",
                        "stop_loss": "61179.73",
                        "tp1": "60264.61",
                        "tp2": "59826.94",
                        "active_subject_label": "小ロット成行ショート候補",
                        "active_headline": "成行候補。",
                    }
                ],
            )
            self._write_outcomes_csv(
                base_dir,
                [
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "forward_price_12h": "60400.00",
                        "forward_price_24h": "60100.00",
                        "direction_outcome": "correct",
                        "tp1_hit_first": "true",
                        "outcome": "win",
                        "evaluation_status": "complete",
                    }
                ],
            )

            output_csv = build_active_plan_candidate_outcomes(base_dir=base_dir)
            rows = self._read_rows(output_csv)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["candidate_delta_12h"], "350.00")
        self.assertEqual(row["candidate_delta_24h"], "650.00")
        self.assertEqual(row["candidate_result_24h"], "favorable")
        self.assertEqual(row["tp1_close_reached_24h"], "true")
        self.assertEqual(row["tp2_close_reached_24h"], "false")
        self.assertEqual(row["sl_close_reached_24h"], "false")

    def test_build_active_plan_candidate_outcomes_handles_missing_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s1:active_limit_retest:long",
                        "source_signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "side": "long",
                        "entry_price": "60423.25",
                    }
                ],
            )
            self._write_outcomes_csv(base_dir, [])

            output_csv = build_active_plan_candidate_outcomes(base_dir=base_dir)
            rows = self._read_rows(output_csv)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["candidate_delta_24h"], "0.00")
        self.assertEqual(rows[0]["candidate_result_24h"], "flat")
        self.assertEqual(rows[0]["outcome_evaluation_status"], "")

    def test_build_active_plan_candidate_outcomes_filters_by_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "old:active_limit_retest:long",
                        "source_signal_id": "old",
                        "timestamp_jst": "2026-06-06T09:05:00+09:00",
                        "side": "long",
                        "entry_price": "60000",
                    },
                    {
                        "candidate_id": "target:active_limit_retest:long",
                        "source_signal_id": "target",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "side": "long",
                        "entry_price": "60000",
                    },
                ],
            )
            self._write_outcomes_csv(
                base_dir,
                [
                    {"signal_id": "old", "forward_price_24h": "59000"},
                    {"signal_id": "target", "forward_price_24h": "61000"},
                ],
            )

            output_csv = build_active_plan_candidate_outcomes(
                base_dir=base_dir,
                date_from="2026-06-07",
                date_to="2026-06-07",
            )
            rows = self._read_rows(output_csv)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_signal_id"], "target")

    def test_build_active_plan_candidate_outcomes_accepts_output_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(base_dir, [])
            self._write_outcomes_csv(base_dir, [])
            output_csv = base_dir / "custom" / "candidate_outcomes.csv"

            result_path = build_active_plan_candidate_outcomes(base_dir=base_dir, output_csv=output_csv)
            self.assertEqual(result_path, output_csv)
            self.assertTrue(output_csv.exists())


if __name__ == "__main__":
    unittest.main()
