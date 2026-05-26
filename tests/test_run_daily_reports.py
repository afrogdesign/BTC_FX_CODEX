from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools import run_daily_reports


class RunDailyReportsTest(unittest.TestCase):
    def test_build_steps_uses_existing_paper_diagnostics_command_for_redesign_output(self) -> None:
        args = run_daily_reports._build_parser().parse_args(["--date", "20260526"])
        with patch("tools.run_daily_reports._build_log_feedback_commands", return_value={
            "daily-sync",
            "build-paper-opportunity-diagnostics-report",
            "build-market-map-effectiveness-report",
            "build-operational-focus-report",
            "build-report-hub",
        }):
            steps, dates = run_daily_reports._build_steps(args)

        self.assertEqual(dates["date"], "20260526")
        redesign = [step for step in steps if step.name == "paper-entry-sl-wait-redesign"][0]
        self.assertIsNotNone(redesign.argv)
        self.assertIn("build-paper-opportunity-diagnostics-report", redesign.argv)
        self.assertIn("運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md", redesign.argv)

    def test_dry_run_prints_commands_without_writing_runtime_files(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp_base = Path(tmpdir)
            with patch("tools.run_daily_reports.BASE_DIR", tmp_base), patch(
                "tools.run_daily_reports._build_log_feedback_commands",
                return_value={"daily-sync", "build-operational-focus-report", "build-report-hub"},
            ), patch("builtins.print") as mocked_print:
                rc = run_daily_reports.main(["--date", "20260526", "--dry-run", "--skip-heavy"])

        self.assertEqual(rc, 0)
        self.assertTrue(mocked_print.called)
        self.assertFalse((tmp_base / "logs" / "runtime" / "daily_reports_last_result.json").exists())

    def test_skip_heavy_skip_ai_runs_minimum_steps_and_writes_result(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp_base = Path(tmpdir)

            def fake_run(argv, cwd, capture_output, text, encoding):
                self.assertEqual(cwd, tmp_base)
                if argv[2] == "daily-sync":
                    self.assertIn("--max-new-ai-reviews", argv)
                    self.assertIn("0", argv)

                class Result:
                    returncode = 0
                    stdout = "ok\n"
                    stderr = ""

                return Result()

            with patch("tools.run_daily_reports.BASE_DIR", tmp_base), patch(
                "tools.run_daily_reports._build_log_feedback_commands",
                return_value={"daily-sync", "build-operational-focus-report", "build-report-hub"},
            ), patch("tools.run_daily_reports.subprocess.run", side_effect=fake_run):
                rc = run_daily_reports.main(["--date", "20260526", "--skip-heavy", "--skip-ai"])

            self.assertEqual(rc, 0)
            result = json.loads((tmp_base / "logs" / "runtime" / "daily_reports_last_result.json").read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "success")
            self.assertEqual([step["name"] for step in result["steps"]], ["daily-sync", "operational-focus", "report-hub"])


if __name__ == "__main__":
    unittest.main()
