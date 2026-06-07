from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.log_feedback import build_active_trade_plan_diagnostics_report


class ActiveTradePlanDiagnosticsTests(unittest.TestCase):
    def _write_trades_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        path = base_dir / "logs" / "csv" / "trades.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "signal_id",
            "timestamp_jst",
            "active_plan_version",
            "active_primary_action",
            "active_subject_label",
            "active_headline",
            "active_market_entry_long",
            "active_market_entry_short",
            "active_limit_retest_long",
            "active_limit_retest_short",
            "active_breakout_follow_long",
            "active_breakout_follow_short",
            "active_countertrend_scalp_long",
            "active_countertrend_scalp_short",
            "active_position_management_long",
            "active_position_management_short",
            "active_trade_plan_json",
        ]
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        return path

    def test_build_active_trade_plan_diagnostics_report_counts_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                        "active_subject_label": "戻り売り待ち・短期反発注意",
                        "active_headline": "下方向優勢。",
                        "active_market_entry_long": "blocked",
                        "active_market_entry_short": "blocked",
                        "active_limit_retest_long": "allowed",
                        "active_limit_retest_short": "allowed",
                        "active_breakout_follow_long": "blocked",
                        "active_breakout_follow_short": "blocked",
                        "active_countertrend_scalp_long": "conditional",
                        "active_countertrend_scalp_short": "blocked",
                        "active_trade_plan_json": "{}",
                    },
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "active_subject_label": "小ロット成行ショート候補",
                        "active_headline": "成行候補。",
                        "active_market_entry_short": "allowed",
                        "active_limit_retest_short": "allowed",
                        "active_trade_plan_json": "{}",
                    },
                    {
                        "signal_id": "s3",
                        "timestamp_jst": "2026-06-07T11:05:00+09:00",
                        "active_plan_version": "active_trade_plan_v1",
                        "active_primary_action": "NO_ACTION",
                        "active_subject_label": "見送り",
                        "active_headline": "見送り。",
                        "active_trade_plan_json": "{}",
                    },
                ],
            )

            report = build_active_trade_plan_diagnostics_report(base_dir=base_dir)

        self.assertIn("# Active Trade Plan 診断", report)
        self.assertIn("集計対象は 3 件", report)
        self.assertIn("`ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP`: 1 件", report)
        self.assertIn("`ACTIVE_MARKET_SMALL`: 1 件", report)
        self.assertIn("`NO_ACTION`: 1 件", report)
        self.assertIn("成行 allowed: long=0 / short=1", report)
        self.assertIn("指値・戻り待ち allowed: long=1 / short=2", report)
        self.assertIn("逆方向短期 conditional: long=1 / short=0", report)
        self.assertIn("s1", report)

    def test_build_active_trade_plan_diagnostics_report_writes_output_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "active_trade_plan_json": "{}",
                    }
                ],
            )
            output_md = base_dir / "運用資料" / "reports" / "analysis" / "active_trade_plan_diagnostics_test.md"

            report = build_active_trade_plan_diagnostics_report(base_dir=base_dir, output_md=output_md)

            self.assertTrue(output_md.exists())
            self.assertEqual(output_md.read_text(encoding="utf-8"), report)

    def test_build_active_trade_plan_diagnostics_report_handles_no_active_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                    }
                ],
            )

            report = build_active_trade_plan_diagnostics_report(base_dir=base_dir)

        self.assertIn("Active Trade Plan の記録はまだありません。", report)
        self.assertIn("active plan rows: 0", report)

    def test_build_active_trade_plan_diagnostics_report_filters_by_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "old",
                        "timestamp_jst": "2026-06-06T09:05:00+09:00",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "active_trade_plan_json": "{}",
                    },
                    {
                        "signal_id": "target",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "active_trade_plan_json": "{}",
                    },
                ],
            )

            report = build_active_trade_plan_diagnostics_report(
                base_dir=base_dir,
                date_from="2026-06-07",
                date_to="2026-06-07",
            )

        self.assertIn("target", report)
        self.assertNotIn("old /", report)
        self.assertIn("active plan rows: 1", report)


if __name__ == "__main__":
    unittest.main()
