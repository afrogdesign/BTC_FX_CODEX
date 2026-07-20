from __future__ import annotations

import json
import plistlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import run_p8_daily_cycle


class RunP8DailyCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def args(self, *extra: str) -> list[str]:
        return ["--repo-root", str(self.root), "--date", "20260711", *extra]

    @staticmethod
    def completed(stdout: str, returncode: int = 0):
        class Result:
            pass
        result = Result(); result.stdout = stdout; result.stderr = ""; result.returncode = returncode
        return result

    def test_jst_date_and_daily_output_path(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run") as run, patch("builtins.print"):
            run_p8_daily_cycle.main(self.args("--dry-run"))
        self.assertFalse(run.called)
        self.assertFalse((self.root / "logs").exists())

    def test_dry_run_does_not_write_file(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run") as run, patch("builtins.print") as output:
            rc = run_p8_daily_cycle.main(self.args("--dry-run"))
        self.assertEqual(rc, 0); self.assertFalse(run.called); self.assertTrue(output.called)
        self.assertFalse((self.root / "logs/runtime/p8_daily_cycle_last_result.json").exists())

    def test_no_actual_pair_omits_actual_arguments(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed('{"ok":true,"counts":{}}')) as run:
            self.assertEqual(run_p8_daily_cycle.main(self.args()), 0)
        argv = run.call_args.args[0]; self.assertNotIn("--actual-episodes", argv); self.assertNotIn("--actual-links", argv)

    def test_both_actual_files_are_passed(self) -> None:
        episodes = self.root / "logs/csv/manual_trade_episodes.csv"; links = self.root / "logs/csv/manual_trade_signal_links.csv"
        episodes.parent.mkdir(parents=True); episodes.write_text("episode_id\ne1\n"); links.write_text("link_id\nl1\n")
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed('{"ok":true,"counts":{}}')) as run:
            run_p8_daily_cycle.main(self.args())
        argv = run.call_args.args[0]; self.assertIn("--actual-episodes", argv); self.assertIn("--actual-links", argv)

    def test_partial_actual_pair_fails_without_runner(self) -> None:
        episodes = self.root / "logs/csv/manual_trade_episodes.csv"; episodes.parent.mkdir(parents=True); episodes.write_text("episode_id\ne1\n")
        with patch("tools.run_p8_daily_cycle.subprocess.run") as run:
            rc = run_p8_daily_cycle.main(self.args())
        self.assertEqual(rc, 2); self.assertFalse(run.called)
        status = json.loads((self.root / "logs/runtime/p8_daily_cycle_last_result.json").read_text()); self.assertEqual(status["status"], "actual_pair_incomplete")

    def test_success_writes_compact_last_result(self) -> None:
        response = '{"ok":true,"counts":{"trial_fact_rows":2},"p9_readiness":{"initial":{"ready":false}}}'
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed(response)):
            self.assertEqual(run_p8_daily_cycle.main(self.args()), 0)
        status = json.loads((self.root / "logs/runtime/p8_daily_cycle_last_result.json").read_text()); self.assertEqual(status["status"], "success"); self.assertEqual(status["counts"]["trial_fact_rows"], 2)

    def test_failure_writes_compact_failure_result_and_nonzero(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed('{"ok":false,"errors":["candidate_ahead_of_ohlcv"]}', 2)):
            self.assertEqual(run_p8_daily_cycle.main(self.args()), 2)
        status = json.loads((self.root / "logs/runtime/p8_daily_cycle_last_result.json").read_text()); self.assertEqual(status["status"], "failed"); self.assertEqual(status["error_codes"], ["candidate_ahead_of_ohlcv"])

    def test_same_day_rerun_uses_replace_and_date_root(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed('{"ok":true}')) as run:
            run_p8_daily_cycle.main(self.args()); run_p8_daily_cycle.main(self.args())
        for call in run.call_args_list:
            argv = call.args[0]; self.assertIn("--replace-output", argv); self.assertIn("logs/p8_operating_cycles/20260711", argv)

    def test_runner_command_has_no_tuning_or_order_route(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed('{"ok":true}')) as run:
            run_p8_daily_cycle.main(self.args())
        command = " ".join(run.call_args.args[0]); self.assertIn("run-p8-operating-cycle", command)
        for forbidden in ("threshold", "gate", "tuning", "order", "mail", "notification"):
            self.assertNotIn(forbidden, command)

    def test_opt_in_shadow_flag_is_forwarded(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed('{"ok":true,"turning_precursor_shadow":{"enabled":true,"status":"success"}}')) as run:
            self.assertEqual(run_p8_daily_cycle.main(self.args("--include-turning-precursor-shadow")), 0)
        self.assertIn("--include-turning-precursor-shadow", run.call_args.args[0])
        status = json.loads((self.root / "logs/runtime/p8_daily_cycle_last_result.json").read_text())
        self.assertEqual(status["turning_precursor_shadow"]["status"], "success")

    def test_macro_shadow_flag_is_optional_and_coexists_with_turning(self) -> None:
        response = '{"ok":true,"macro_structure_shadow":{"enabled":true,"status":"success"},"turning_precursor_shadow":{"enabled":true,"status":"success"}}'
        with patch("tools.run_p8_daily_cycle.subprocess.run", return_value=self.completed(response)) as run:
            self.assertEqual(run_p8_daily_cycle.main(self.args("--include-turning-precursor-shadow", "--include-macro-structure-shadow")), 0)
        argv = run.call_args.args[0]
        self.assertEqual(argv.count("--include-macro-structure-shadow"), 1)
        self.assertEqual(argv.count("--include-turning-precursor-shadow"), 1)
        status = json.loads((self.root / "logs/runtime/p8_daily_cycle_last_result.json").read_text())
        self.assertEqual(status["macro_structure_shadow"]["status"], "success")

    def test_dry_run_reports_shadow_disabled_or_enabled(self) -> None:
        with patch("tools.run_p8_daily_cycle.subprocess.run") as run, patch("builtins.print") as output:
            run_p8_daily_cycle.main(self.args("--dry-run", "--include-turning-precursor-shadow"))
        run.assert_not_called()
        payload = json.loads(output.call_args.args[0])
        self.assertTrue(payload["turning_precursor_shadow_enabled"])
        self.assertFalse(payload["macro_structure_shadow_enabled"])

    def test_dry_run_reports_macro_shadow_enabled(self) -> None:
        with patch("builtins.print") as output:
            run_p8_daily_cycle.main(self.args("--dry-run", "--include-macro-structure-shadow"))
        payload = json.loads(output.call_args.args[0])
        self.assertTrue(payload["macro_structure_shadow_enabled"])

    def test_plist_contract(self) -> None:
        path = Path(__file__).resolve().parents[1] / "deploy/com.afrog.btc-p8-operating-cycle.plist"
        payload = plistlib.loads(path.read_bytes()); self.assertEqual(payload["Label"], "com.afrog.btc-p8-operating-cycle")
        self.assertEqual(payload["ProgramArguments"], [
            "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/.venv312/bin/python",
            "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/tools/run_p8_daily_cycle.py",
            "--include-turning-precursor-shadow",
        ])
        self.assertEqual(payload["ProgramArguments"].count("--include-turning-precursor-shadow"), 1)
        self.assertTrue(all("/Users/marupro/CODEX/100_MCP_Server/btc_monitor" in value for value in payload["ProgramArguments"][:2]))
        self.assertNotIn("01_active/BTC_FX_CODEX", " ".join(payload["ProgramArguments"]))
        self.assertEqual(payload["StartCalendarInterval"], {"Hour": 11, "Minute": 30}); self.assertNotIn("RunAtLoad", payload); self.assertNotIn("KeepAlive", payload)
        self.assertIn("p8_daily_cycle.launchd.out", payload["StandardOutPath"]); self.assertIn("p8_daily_cycle.launchd.err", payload["StandardErrorPath"])


if __name__ == "__main__":
    unittest.main()
