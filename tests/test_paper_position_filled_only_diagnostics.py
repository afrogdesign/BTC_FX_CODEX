from __future__ import annotations

import unittest

from tools.log_feedback import (
    _paper_position_filled_only_stats,
    _paper_position_filled_rows,
    _paper_position_group_lines,
    _paper_position_non_entered_rows,
)


class PaperPositionFilledOnlyDiagnosticsTests(unittest.TestCase):
    def _row(self, exit_status: str, realized_r: str, **overrides: str) -> dict[str, str]:
        row = {
            "signal_id": f"{exit_status}_{realized_r}",
            "exit_status": exit_status,
            "realized_r": realized_r,
            "side": "long",
            "confidence_wait_shadow": "50",
            "confidence_execution_shadow": "40",
            "mfe_atr": "1.0",
            "mae_atr": "0.5",
            "rr_estimate": "1.5",
            "market_map_flags": "",
            "prelabel": "ENTRY_OK",
        }
        row.update(overrides)
        return row

    def test_paper_position_rows_split_filled_and_non_entered(self) -> None:
        rows = [
            self._row("tp2_hit", "2.0"),
            self._row("sl_hit", "-1.0"),
            self._row("timeout", "0.2"),
            self._row("missed_opportunity", "1.5"),
            self._row("entry_not_reached", "-0.2"),
        ]

        filled = _paper_position_filled_rows(rows)
        non_entered = _paper_position_non_entered_rows(rows)

        self.assertEqual([row["exit_status"] for row in filled], ["tp2_hit", "sl_hit", "timeout"])
        self.assertEqual([row["exit_status"] for row in non_entered], ["missed_opportunity", "entry_not_reached"])

    def test_filled_only_stats_excludes_missed_and_entry_not_reached_from_primary_metrics(self) -> None:
        rows = [
            self._row("tp2_hit", "2.0"),
            self._row("sl_hit", "-1.0"),
            self._row("timeout", "0.0"),
            self._row("missed_opportunity", "5.0"),
            self._row("entry_not_reached", "-5.0"),
        ]

        stats = _paper_position_filled_only_stats(rows)

        self.assertEqual(stats["all_count"], 5)
        self.assertEqual(stats["filled_count"], 3)
        self.assertEqual(stats["non_entered_count"], 2)
        self.assertEqual(stats["missed_opportunity_count"], 1)
        self.assertEqual(stats["entry_not_reached_count"], 1)
        self.assertAlmostEqual(stats["avg_realized_r"], 1.0 / 3.0)
        self.assertAlmostEqual(stats["approx_pf"], 2.0)
        self.assertAlmostEqual(stats["all_avg_realized_r"], 0.2)

    def test_group_lines_report_filled_only_metrics_and_non_entered_counts(self) -> None:
        rows = [
            self._row("tp2_hit", "2.0"),
            self._row("sl_hit", "-1.0"),
            self._row("missed_opportunity", "5.0"),
            self._row("entry_not_reached", "-5.0"),
        ]

        lines = _paper_position_group_lines(
            title="fixture",
            labels=[("all rows", rows)],
        )
        report = "\n".join(lines)

        self.assertIn("all=4件", report)
        self.assertIn("filled=2件", report)
        self.assertIn("filled勝率=50.0%", report)
        self.assertIn("filled平均R=0.50", report)
        self.assertIn("filled簡易PF=2.00", report)
        self.assertIn("missed=1件", report)
        self.assertIn("entry_not_reached=1件", report)


if __name__ == "__main__":
    unittest.main()
