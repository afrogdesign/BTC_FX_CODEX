from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.log_feedback import build_active_plan_candidate_outcomes_report


class ActivePlanCandidateOutcomesReportTests(unittest.TestCase):
    def _write_candidate_outcomes_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        path = base_dir / "logs" / "csv" / "active_plan_candidate_outcomes.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "candidate_id",
            "source_signal_id",
            "timestamp_jst",
            "active_primary_action",
            "candidate_type",
            "candidate_status",
            "side",
            "entry_mode",
            "entry_price",
            "active_subject_label",
            "active_headline",
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
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        return path

    def test_build_active_plan_candidate_outcomes_report_summarizes_candidate_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidate_outcomes_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s1:active_limit_retest:short",
                        "source_signal_id": "s1",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "candidate_type": "active_limit_retest",
                        "side": "short",
                        "active_headline": "戻り売り候補。",
                        "candidate_delta_12h": "120.0",
                        "candidate_delta_24h": "240.0",
                        "candidate_result_12h": "favorable",
                        "candidate_result_24h": "favorable",
                        "tp1_close_reached_24h": "true",
                        "tp2_close_reached_24h": "false",
                        "sl_close_reached_24h": "false",
                    },
                    {
                        "candidate_id": "s2:active_market_small:short",
                        "source_signal_id": "s2",
                        "timestamp_jst": "2026-06-07T10:05:00+09:00",
                        "candidate_type": "active_market_small",
                        "side": "short",
                        "active_headline": "成行候補。",
                        "candidate_delta_12h": "-80.0",
                        "candidate_delta_24h": "-160.0",
                        "candidate_result_12h": "adverse",
                        "candidate_result_24h": "adverse",
                        "tp1_close_reached_24h": "false",
                        "tp2_close_reached_24h": "false",
                        "sl_close_reached_24h": "true",
                    },
                    {
                        "candidate_id": "s3:active_counter_scalp:long",
                        "source_signal_id": "s3",
                        "timestamp_jst": "2026-06-07T11:05:00+09:00",
                        "candidate_type": "active_counter_scalp",
                        "side": "long",
                        "active_headline": "短期反発候補。",
                        "candidate_delta_12h": "0.0",
                        "candidate_delta_24h": "0.0",
                        "candidate_result_12h": "flat",
                        "candidate_result_24h": "flat",
                        "tp1_close_reached_24h": "false",
                        "tp2_close_reached_24h": "false",
                        "sl_close_reached_24h": "false",
                    },
                ],
            )

            report = build_active_plan_candidate_outcomes_report(base_dir=base_dir)

        self.assertIn("# Active Plan 候補別暫定評価", report)
        self.assertIn("集計対象は 3 候補", report)
        self.assertIn("24h favorable は 1 件", report)
        self.assertIn("TP1 close 到達は 1 件", report)
        self.assertIn("SL close 到達は 1 件", report)
        self.assertIn("`active_limit_retest`: count=1 / 24h favorable=100.0%", report)
        self.assertIn("`active_market_small`: count=1 / 24h favorable=0.0%", report)
        self.assertIn("`active_counter_scalp`: count=1 / 24h favorable=0.0%", report)
        self.assertIn("s1:active_limit_retest:short", report)

    def test_build_active_plan_candidate_outcomes_report_writes_output_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidate_outcomes_csv(
                base_dir,
                [
                    {
                        "candidate_id": "s1:active_limit_retest:short",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "candidate_type": "active_limit_retest",
                        "side": "short",
                        "candidate_delta_24h": "100",
                        "candidate_result_24h": "favorable",
                    }
                ],
            )
            output_md = base_dir / "運用資料" / "reports" / "analysis" / "active_plan_candidate_outcomes_test.md"

            report = build_active_plan_candidate_outcomes_report(base_dir=base_dir, output_md=output_md)
            self.assertTrue(output_md.exists())
            self.assertEqual(output_md.read_text(encoding="utf-8"), report)

    def test_build_active_plan_candidate_outcomes_report_handles_no_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidate_outcomes_csv(base_dir, [])

            report = build_active_plan_candidate_outcomes_report(base_dir=base_dir)

        self.assertIn("Active Plan candidate outcomes の記録はまだありません。", report)
        self.assertIn("rows: 0", report)

    def test_build_active_plan_candidate_outcomes_report_filters_by_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_candidate_outcomes_csv(
                base_dir,
                [
                    {
                        "candidate_id": "old:active_limit_retest:short",
                        "timestamp_jst": "2026-06-06T09:05:00+09:00",
                        "candidate_type": "active_limit_retest",
                        "side": "short",
                        "candidate_delta_24h": "100",
                        "candidate_result_24h": "favorable",
                    },
                    {
                        "candidate_id": "target:active_limit_retest:short",
                        "timestamp_jst": "2026-06-07T09:05:00+09:00",
                        "candidate_type": "active_limit_retest",
                        "side": "short",
                        "candidate_delta_24h": "200",
                        "candidate_result_24h": "favorable",
                    },
                ],
            )

            report = build_active_plan_candidate_outcomes_report(
                base_dir=base_dir,
                date_from="2026-06-07",
                date_to="2026-06-07",
            )

        self.assertIn("target:active_limit_retest:short", report)
        self.assertNotIn("old:active_limit_retest:short", report)
        self.assertIn("rows: 1", report)


if __name__ == "__main__":
    unittest.main()
