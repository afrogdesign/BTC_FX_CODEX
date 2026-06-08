from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.log_feedback import build_active_trade_plan_diagnostics_report


class ActiveTradePlanDiagnosticsReportTests(unittest.TestCase):
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

    def _write_trades_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        return self._write_csv(
            base_dir / "logs" / "csv" / "trades.csv",
            [
                "signal_id",
                "timestamp_jst",
                "active_plan_version",
                "active_primary_action",
                "active_market_entry_long",
                "active_market_entry_short",
                "active_limit_retest_long",
                "active_limit_retest_short",
                "active_countertrend_scalp_long",
                "active_countertrend_scalp_short",
            ],
            rows,
        )

    def test_builds_report_with_candidate_and_trade_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s1:short:limit_retest",
                        "timestamp_jst": "2026-06-08T10:00:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                        "candidate_type": "limit_retest",
                        "candidate_status": "allowed",
                        "side": "short",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "rr_current_tp1": "0.8",
                        "rr_zone_mid_tp1": "1.3",
                        "next_condition": "pullback",
                    },
                    {
                        "candidate_id": "s1:long:counter_scalp",
                        "timestamp_jst": "2026-06-08T10:01:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                        "candidate_type": "counter_scalp",
                        "candidate_status": "conditional",
                        "side": "long",
                        "entry_mode": "conditional",
                        "entry_price": "101",
                        "rr_current_tp1": "0.5",
                        "rr_zone_mid_tp1": "0.9",
                        "next_condition": "reversal",
                    },
                    {
                        "candidate_id": "s2:short:market",
                        "timestamp_jst": "2026-06-08T11:00:00+09:00",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "candidate_type": "market",
                        "candidate_status": "allowed",
                        "side": "short",
                        "entry_mode": "market",
                        "entry_price": "99",
                        "rr_current_tp1": "0.7",
                        "rr_zone_mid_tp1": "1.1",
                        "next_condition": "now",
                    },
                ],
            )
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-08T10:00:00+09:00",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                        "active_market_entry_long": "blocked",
                        "active_market_entry_short": "blocked",
                        "active_limit_retest_long": "blocked",
                        "active_limit_retest_short": "allowed",
                        "active_countertrend_scalp_long": "conditional",
                        "active_countertrend_scalp_short": "blocked",
                    },
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-08T11:00:00+09:00",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "active_market_entry_long": "blocked",
                        "active_market_entry_short": "allowed",
                        "active_limit_retest_long": "blocked",
                        "active_limit_retest_short": "allowed",
                        "active_countertrend_scalp_long": "blocked",
                        "active_countertrend_scalp_short": "blocked",
                    },
                    {
                        "signal_id": "s3",
                        "timestamp_jst": "2026-06-08T12:00:00+09:00",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "NO_ACTION",
                    },
                ],
            )

            report = build_active_trade_plan_diagnostics_report(
                base_dir=base_dir,
                report_date="20260608",
            )
            output_path = base_dir / "運用資料" / "reports" / "analysis" / "active_trade_plan_diagnostics_20260608.md"
            self.assertTrue(output_path.exists())
            self.assertIn("# Active Trade Plan 診断", report)
            self.assertIn("## 3. 候補タイプ別件数", report)
            self.assertIn("`limit_retest`: 1 件", report)
            self.assertIn("`counter_scalp`: 1 件", report)
            self.assertIn("`market`: 1 件", report)
            self.assertIn("## 4. side別件数", report)
            self.assertIn("`short`: 2 件", report)
            self.assertIn("`long`: 1 件", report)
            self.assertIn("## 5. candidate_status別件数", report)
            self.assertIn("`allowed`: 2 件", report)
            self.assertIn("`conditional`: 1 件", report)
            self.assertIn("## 6. entry_mode別件数", report)
            self.assertIn("`limit`: 1 件", report)
            self.assertIn("`conditional`: 1 件", report)
            self.assertIn("`market`: 1 件", report)
            self.assertIn("## 7. NO_ACTION 比率", report)
            self.assertIn("`NO_ACTION`: 1 件 (33.3%)", report)
            self.assertIn("s2:short:market", report)
            self.assertEqual(output_path.read_text(encoding="utf-8"), report)

    def test_missing_candidates_is_reported_without_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-08T10:00:00+09:00",
                        "active_primary_action": "NO_ACTION",
                    }
                ],
            )

            report = build_active_trade_plan_diagnostics_report(base_dir=base_dir, report_date="20260608")

        self.assertIn("active_plan_candidates.csv: missing", report)
        self.assertIn("candidate action distribution: active_plan_candidates.csv missing", report)

    def test_report_date_controls_output_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidates_csv(base_dir, [])

            build_active_trade_plan_diagnostics_report(base_dir=base_dir, report_date="20260608")
            output_path = base_dir / "運用資料" / "reports" / "analysis" / "active_trade_plan_diagnostics_20260608.md"
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
