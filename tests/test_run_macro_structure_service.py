from __future__ import annotations

import fcntl
import json
import plistlib
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import tools.run_macro_structure_service as service


class MacroStructureServiceTests(unittest.TestCase):
    def args(self, root: Path, *extra: str) -> SimpleNamespace:
        parser = service._parser()
        return parser.parse_args(["--repo-root", str(root), *extra])

    def test_three_step_order_shared_time_and_one_fetch_per_timeframe(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            calls: list[tuple[str, str, str]] = []

            def fetch(path: Path, limit: int, interval: str, symbol: str) -> None:
                calls.append((interval, symbol, path.name))
                path.write_text(f"timestamp,open,high,low,close,volume\n2026-01-01T00:00:00+00:00,1,2,0,1,1\n", encoding="utf-8")

            outputs = {
                "run-macro-structure-daily": {"ok": True, "run_id": "run_1", "snapshot_id": "snap_1", "result_status": "ok", "stale_status": "current"},
                "run-macro-structure-history": {"ok": True, "history_id": "history_1", "history_result_status": "ok"},
                "render-macro-structure-operator": {"ok": True, "operator_artifact_id": "operator_1"},
            }
            commands: list[list[str]] = []

            def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                commands.append(argv)
                name = next(item for item in outputs if item in argv)
                return subprocess.CompletedProcess(argv, 0, json.dumps(outputs[name]) + "\n", "")

            fixed = datetime(2026, 1, 2, 16, 10, tzinfo=timezone.utc)
            with patch.object(service, "_fetch_public_ohlcv", side_effect=fetch), patch.object(service, "_utc_now", return_value=fixed), patch.object(service.subprocess, "run", side_effect=run):
                code, result = service.run_service(self.args(root, "--symbol", "ETH_USDT"))

            self.assertEqual(code, 0)
            self.assertEqual([item[0] for item in calls], ["15m", "1h", "4h"])
            self.assertTrue(all(item[1] == "ETH_USDT" for item in calls))
            self.assertEqual([command[2] for command in commands], ["run-macro-structure-daily", "run-macro-structure-history", "render-macro-structure-operator"])
            self.assertEqual(result["evaluation_utc"], "2026-01-02T16:10:00+00:00")
            self.assertTrue(result["ok"])
            self.assertEqual(result["snapshot_run_id"], "run_1")
            daily_15m = commands[0][commands[0].index("--ohlcv-15m") + 1]
            operator_15m = commands[2][commands[2].index("--ohlcv-15m-csv") + 1]
            self.assertEqual(daily_15m, operator_15m)

    def test_failure_stops_later_steps_and_preserves_previous_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            previous = root / "local/reports/macro_structure/run_previous"
            previous.mkdir(parents=True)
            marker = previous / "marker.txt"
            marker.write_text("keep", encoding="utf-8")

            def fetch(path: Path, limit: int, interval: str, symbol: str) -> None:
                path.write_text("valid", encoding="utf-8")

            commands: list[list[str]] = []

            def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                commands.append(argv)
                return subprocess.CompletedProcess(argv, 2, '{"ok":false,"error_code":"snapshot_failed"}\n', "")

            with patch.object(service, "_fetch_public_ohlcv", side_effect=fetch), patch.object(service.subprocess, "run", side_effect=run):
                code, result = service.run_service(self.args(root))
            self.assertNotEqual(code, 0)
            self.assertEqual(len(commands), 1)
            self.assertEqual(result["error_code"], "snapshot_failed")
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
            self.assertEqual(json.loads((root / "logs/runtime/macro_structure_service_last_result.json").read_text())["status"], "failed")

    def test_dry_run_has_no_fetch_or_status_side_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(service, "_fetch_public_ohlcv") as fetch:
                code, result = service.run_service(self.args(root, "--dry-run"))
            self.assertEqual(code, 0)
            fetch.assert_not_called()
            self.assertEqual(result["status"], "dry_run")
            self.assertFalse((root / "logs/runtime/macro_structure_service_last_result.json").exists())

    def test_lock_returns_already_running_without_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock_path = root / "logs/runtime/macro_structure_service.lock"
            lock_path.parent.mkdir(parents=True)
            handle = lock_path.open("a+")
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                with patch.object(service, "_fetch_public_ohlcv") as fetch:
                    code, result = service.run_service(self.args(root))
                self.assertEqual(code, 0)
                self.assertEqual(result["status"], "already_running")
                fetch.assert_not_called()
                self.assertFalse((root / "logs/runtime/macro_structure_service_last_result.json").exists())
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                handle.close()


class MacroStructureServicePlistTests(unittest.TestCase):
    def test_target_plist_contract(self) -> None:
        path = Path(__file__).parents[1] / "deploy/com.afrog.btc-macro-structure.plist"
        data = plistlib.loads(path.read_bytes())
        self.assertEqual(data["Label"], "com.afrog.btc-macro-structure")
        self.assertEqual(data["WorkingDirectory"], "/Users/marupro/CODEX/100_MCP_Server/btc_monitor")
        self.assertEqual(data["ProgramArguments"][0], "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/.venv312/bin/python")
        self.assertEqual(data["ProgramArguments"][1], "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/tools/run_macro_structure_service.py")
        self.assertEqual([(item["Hour"], item["Minute"]) for item in data["StartCalendarInterval"]], [(1, 10), (5, 10), (9, 10), (13, 10), (17, 10), (21, 10)])
        self.assertNotIn("RunAtLoad", data)
        self.assertNotIn("KeepAlive", data)
        self.assertEqual(data["StandardOutPath"], "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/logs/runtime/macro_structure_service.launchd.out")
        self.assertEqual(data["StandardErrorPath"], "/Users/marupro/CODEX/100_MCP_Server/btc_monitor/logs/runtime/macro_structure_service.launchd.err")


if __name__ == "__main__":
    unittest.main()
