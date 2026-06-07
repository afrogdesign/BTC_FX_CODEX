from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.log_feedback import build_active_trade_plan_effectiveness_report


class ActiveTradePlanEffectivenessTests(unittest.TestCase):
    def _write_csv(self, path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        return path

    def _write_trades_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        return self._write_csv(
            base_dir / "logs" / "csv" / "trades.csv",
            [
                "signal_id",
                "timestamp_jst",
                "active_primary_action",
                "active_subject_label",
                "active_headline",
                "active_trade_plan_json",
            ],
            rows,
        )

    def _write_outcomes_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        return self._write_csv(
            base_dir / "logs" / "csv" / "signal_outcomes.csv",
            [
                "signal_id",
                "timestamp_jst",
                "evaluation_status",
                "outcome",
                "direction_outcome",
                "tp1_hit_first",
                "signal_based_MFE_12h",
                "signal_based_MAE_12h",
                "signal_based_MFE_24h",
                "signal_based_MAE_24h",
            ],
            rows,
        )

    def test_build_active_trade_plan_effectiveness_report_groups_by_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_trades_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "active_subject_label": "戻り売り待ち",
                        "active_headline": "戻り売り待ち。",
                        "active_trade_plan_json": "{}",
                    },
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "active_subject_label": "小ロット成行ショート候補",
                        "active_headline": "成行候補。",
                        "active_trade_plan_json": "{}",
                    },
                    {
                        "signal_id": "s3",
                        "timestamp_jst": "2026-06-07T11:05:00+09:00",
                        "active_primary_action": "NO_ACTION",
                        "active_subject_label": "見送り",
                        "active_headline": "見送り。",
                        "active_trade_plan_json": "{}",
                    },
                ],
            )
            self._write_outcomes_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "tp1_hit_first": "true",
                        "signal_based_MFE_24h": "420.5",
                        "signal_based_MAE_24h": "110.0",
                    },
                    {
                        "signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "evaluation_status": "complete",
                        "outcome": "loss",
                        "direction_outcome": "wrong",
                        "tp1_hit_first": "false",
                        "signal_based_MFE_24h": "80.0",
                        "signal_based_MAE_24h": "260.0",
                    },
                    {
                        "signal_id": "s3",
                        "timestamp_jst": "2026-06-07T11:05:00+09:00",
                        "evaluation_status": "complete",
                        "outcome": "expired",
                        "direction_outcome": "correct",
                        "tp1_hit_first": "false",
                        "signal_based_MFE_24h": "50.0",
                        "signal_based_MAE_24h": "70.0",
                    },
                ],
            )

            report = build_active_trade_plan_effectiveness_report(base_dir=base_dir)

        self.assertIn("# Active Trade Plan 有効性検証", report)
        self.assertIn("Active Plan 対象は 3 件", report)
        self.assertIn("outcome 評価済みは 3 件", report)
        self.assertIn("direction 正解率は 66.7%", report)
        self.assertIn("TP1先行率は 33.3%", report)
        self.assertIn("`ACTIVE_LIMIT_RETEST`: count=1 / evaluated=1 / direction=100.0%", report)
        self.assertIn("`ACTIVE_MARKET_SMALL`: count=1 / evaluated=1 / direction=0.0%", report)
        self.assertIn("MFE24h=420.50 / MAE24h=110.00", report)
        self.assertIn("s1", report)

    def test_build_active_trade_plan_effectiveness_report_writes_output_md(self) -> None:
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
            self._write_outcomes_csv(
                base_dir,
                [
                    {
                        "signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "direction_outcome": "correct",
                        "tp1_hit_first": "true",
                        "signal_based_MFE_24h": "100",
                        "signal_based_MAE_24h": "50",
                    }
                ],
            )
            output_md = base_dir / "運用資料" / "reports" / "analysis" / "active_trade_plan_effectiveness_test.md"

            report = build_active_trade_plan_effectiveness_report(base_dir=base_dir, output_md=output_md)

            self.assertTrue(output_md.exists())
            self.assertEqual(output_md.read_text(encoding="utf-8"), report)

    def test_build_active_trade_plan_effectiveness_report_handles_missing_outcomes(self) -> None:
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
            self._write_outcomes_csv(base_dir, [])

            report = build_active_trade_plan_effectiveness_report(base_dir=base_dir)

        self.assertIn("Active Plan 対象は 1 件", report)
        self.assertIn("outcome 評価済みは 0 件", report)
        self.assertIn("direction 正解率は 0.0%", report)

    def test_build_active_trade_plan_effectiveness_report_filters_by_date(self) -> None:
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
            self._write_outcomes_csv(
                base_dir,
                [
                    {
                        "signal_id": "old",
                        "timestamp_jst": "2026-06-06T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "direction_outcome": "wrong",
                        "tp1_hit_first": "false",
                        "signal_based_MFE_24h": "10",
                        "signal_based_MAE_24h": "200",
                    },
                    {
                        "signal_id": "target",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "direction_outcome": "correct",
                        "tp1_hit_first": "true",
                        "signal_based_MFE_24h": "300",
                        "signal_based_MAE_24h": "60",
                    },
                ],
            )

            report = build_active_trade_plan_effectiveness_report(
                base_dir=base_dir,
                date_from="2026-06-07",
                date_to="2026-06-07",
            )

        self.assertIn("target", report)
        self.assertNotIn("old /", report)
        self.assertIn("joined rows: 1", report)

    def test_build_active_trade_plan_effectiveness_report_handles_no_active_rows(self) -> None:
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
            self._write_outcomes_csv(base_dir, [])

            report = build_active_trade_plan_effectiveness_report(base_dir=base_dir)

        self.assertIn("Active Trade Plan と outcome を結合できるデータはまだありません。", report)
        self.assertIn("joined rows: 0", report)


if __name__ == "__main__":
    unittest.main()
