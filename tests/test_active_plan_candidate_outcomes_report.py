from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.storage.csv_logger import ACTIVE_PLAN_CANDIDATE_HEADER
from tools.log_feedback import build_active_plan_candidate_outcomes_report


class ActivePlanCandidateOutcomesReportTests(unittest.TestCase):
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
            base_dir / "logs" / "csv" / "active_plan_candidates.csv",
            ACTIVE_PLAN_CANDIDATE_HEADER,
            rows,
        )

    def _write_trades_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        return self._write_csv(
            base_dir / "logs" / "csv" / "trades.csv",
            [
                "signal_id",
                "timestamp_jst",
                "summary_subject",
                "active_plan_version",
                "active_primary_action",
                "active_trade_plan_json",
            ],
            rows,
        )

    def test_build_report_handles_missing_inputs_without_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)

            report = build_active_plan_candidate_outcomes_report(
                base_dir=base_dir,
                report_date="20260608",
            )
            output_path = base_dir / "運用資料" / "reports" / "analysis" / "active_plan_candidate_outcomes_20260608.md"
            self.assertTrue(output_path.exists())
        self.assertIn("active_plan_candidates.csv: missing", report)
        self.assertIn("trades.csv: missing", report)
        self.assertIn("candidate rows: 0", report)
        self.assertIn("provisional verdict: 候補なし", report)

    def test_header_only_candidates_report_zero_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(base_dir, [])
            self._write_trades_csv(base_dir, [])

            report = build_active_plan_candidate_outcomes_report(
                base_dir=base_dir,
                report_date="20260608",
            )

        self.assertIn("active_plan_candidates.csv: header only", report)
        self.assertIn("candidate rows: 0", report)
        self.assertIn("## 3. 候補タイプ別件数", report)
        self.assertIn("- なし", report)
        self.assertIn("provisional verdict: 候補なし", report)

    def test_multiple_rows_are_aggregated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s1:active_limit_retest:short",
                        "source_signal_id": "s1",
                        "timestamp_jst": "2026-06-08T10:00:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "candidate_type": "active_limit_retest",
                        "candidate_status": "allowed",
                        "side": "short",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "stop_loss": "110",
                        "tp1": "90",
                        "tp2": "80",
                        "rr_current_tp1": "1.0",
                        "rr_zone_mid_tp1": "1.5",
                        "next_condition": "pullback",
                    },
                    {
                        "candidate_id": "s2:active_market_small:short",
                        "source_signal_id": "s2",
                        "timestamp_jst": "2026-06-08T10:01:00+09:00",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "candidate_type": "active_market_small",
                        "candidate_status": "candidate",
                        "side": "short",
                        "entry_mode": "market",
                        "entry_price": "101",
                        "stop_loss": "111",
                        "tp1": "91",
                        "tp2": "81",
                        "rr_current_tp1": "0.8",
                        "rr_zone_mid_tp1": "1.2",
                        "next_condition": "now",
                    },
                    {
                        "candidate_id": "s3:active_counter_scalp:long",
                        "source_signal_id": "s3",
                        "timestamp_jst": "2026-06-08T10:02:00+09:00",
                        "active_primary_action": "ACTIVE_COUNTER_SCALP",
                        "candidate_type": "active_counter_scalp",
                        "candidate_status": "conditional",
                        "side": "long",
                        "entry_mode": "conditional",
                        "entry_price": "102",
                        "stop_loss": "112",
                        "tp1": "92",
                        "tp2": "82",
                        "rr_current_tp1": "0.6",
                        "rr_zone_mid_tp1": "1.1",
                        "next_condition": "reversal",
                    },
                ],
            )
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-08T10:10:00+09:00",
                        "summary_subject": "s1",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "active_trade_plan_json": "{}",
                    },
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-08T10:11:00+09:00",
                        "summary_subject": "s2",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "active_trade_plan_json": "{}",
                    },
                    {
                        "signal_id": "s3",
                        "timestamp_jst": "2026-06-08T10:12:00+09:00",
                        "summary_subject": "s3",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "NO_ACTION",
                        "active_trade_plan_json": "{}",
                    },
                ],
            )

            report = build_active_plan_candidate_outcomes_report(
                base_dir=base_dir,
                report_date="20260608",
                limit=2,
            )

        self.assertIn("candidate rows: 3", report)
        self.assertIn("trade rows: 3", report)
        self.assertIn("`active_limit_retest`: 1 件", report)
        self.assertIn("`active_market_small`: 1 件", report)
        self.assertIn("`active_counter_scalp`: 1 件", report)
        self.assertIn("`allowed`: 1 件", report)
        self.assertIn("`candidate`: 1 件", report)
        self.assertIn("`conditional`: 1 件", report)
        self.assertIn("`short`: 2 件", report)
        self.assertIn("`long`: 1 件", report)
        self.assertIn("`limit`: 1 件", report)
        self.assertIn("`market`: 1 件", report)
        self.assertIn("`conditional`: 1 件", report)
        self.assertIn("candidates with complete entry/tp/sl values: 3/3", report)
        self.assertIn("candidates with followup trade rows: 3/3", report)
        self.assertIn("provisional verdict: 候補あり・後続tradeあり", report)
        self.assertIn("s3:active_counter_scalp:long", report)
        self.assertIn("s2:active_market_small:short", report)

    def test_report_date_controls_output_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(base_dir, [])
            self._write_trades_csv(base_dir, [])

            build_active_plan_candidate_outcomes_report(
                base_dir=base_dir,
                report_date="20260608",
            )
            output_path = base_dir / "運用資料" / "reports" / "analysis" / "active_plan_candidate_outcomes_20260608.md"
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
