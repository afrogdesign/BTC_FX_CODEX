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

    @staticmethod
    def health_result(state: str = "healthy", exit_code: int = 0) -> dict[str, object]:
        return {"ok": exit_code == 0, "exit_code": exit_code, "report_written": True, "health_state": state, "health_artifact_id": "health_1"}

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
                "render-macro-structure-operator": {"ok": True, "operator_artifact_id": "operator_1", "latest_entry_status": "available", "latest_entry_id": "entry_1", "latest_entry_method_version": "macro_structure_latest_entry.v1"},
                "check-macro-structure-health": {"ok": True, "exit_code": 0, "report_written": True, "health_state": "healthy_insufficient", "health_artifact_id": "health_1"},
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
            self.assertEqual([command[2] for command in commands[:3]], ["run-macro-structure-daily", "run-macro-structure-history", "render-macro-structure-operator"])
            self.assertEqual(commands[3][2], "check-macro-structure-health")
            self.assertEqual(result["evaluation_utc"], "2026-01-02T16:10:00+00:00")
            self.assertTrue(result["ok"])
            self.assertEqual(result["snapshot_run_id"], "run_1")
            daily_15m = commands[0][commands[0].index("--ohlcv-15m") + 1]
            operator_15m = commands[2][commands[2].index("--ohlcv-15m-csv") + 1]
            self.assertEqual(daily_15m, operator_15m)
            daily_4h = commands[0][commands[0].index("--ohlcv-4h") + 1]
            ops_4h = commands[2][commands[2].index("--ohlcv-4h-csv") + 1]
            self.assertEqual(daily_4h, ops_4h)
            self.assertEqual(result["operator_latest_entry_status"], "available")
            self.assertEqual(result["operator_latest_entry_id"], "entry_1")
            self.assertEqual(result["operator_latest_entry_method_version"], "macro_structure_latest_entry.v1")

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
                if "check-macro-structure-health" in argv:
                    return subprocess.CompletedProcess(argv, 3, '{"ok":false,"exit_code":3,"report_written":true,"health_state":"failed","health_artifact_id":"health_failed"}\n', "")
                return subprocess.CompletedProcess(argv, 2, '{"ok":false,"error_code":"snapshot_failed"}\n', "")

            with patch.object(service, "_fetch_public_ohlcv", side_effect=fetch), patch.object(service.subprocess, "run", side_effect=run):
                code, result = service.run_service(self.args(root))
            self.assertNotEqual(code, 0)
            self.assertEqual(len(commands), 2)
            self.assertEqual(result["error_code"], "snapshot_failed")
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
            self.assertEqual(json.loads((root / "logs/runtime/macro_structure_service_last_result.json").read_text())["status"], "failed")

    def test_failed_history_retains_successful_snapshot_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def fetch(path: Path, limit: int, interval: str, symbol: str) -> None:
                path.write_text("valid", encoding="utf-8")
            outputs = [
                {"ok": True, "run_id": "run_1", "snapshot_id": "snap_1", "result_status": "insufficient", "stale_status": "current", "continuity_status": "continuous", "data_quality_status": "ok"},
                {"ok": False, "error_code": "history_failed"},
            ]
            def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                if "check-macro-structure-health" in argv:
                    return subprocess.CompletedProcess(argv, 3, '{"ok":false,"exit_code":3,"report_written":true,"health_state":"failed","health_artifact_id":"health_failed"}\n', "")
                return subprocess.CompletedProcess(argv, 0 if outputs[0].get("ok") else 2, json.dumps(outputs.pop(0)) + "\n", "")
            with patch.object(service, "_fetch_public_ohlcv", side_effect=fetch), patch.object(service.subprocess, "run", side_effect=run):
                code, result = service.run_service(self.args(root))
            self.assertNotEqual(code, 0)
            self.assertEqual(result["snapshot_run_id"], "run_1")
            self.assertEqual(result["snapshot_id"], "snap_1")
            self.assertEqual(result["snapshot_result_status"], "insufficient")
            self.assertEqual(result["stale_status"], "current")
            self.assertEqual(result["continuity_status"], "continuous")
            self.assertEqual(result["data_quality_status"], "ok")
            self.assertNotIn("history_id", result)

    def test_failed_operator_retains_snapshot_and_history_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def fetch(path: Path, limit: int, interval: str, symbol: str) -> None:
                path.write_text("valid", encoding="utf-8")
            outputs = [
                {"ok": True, "run_id": "run_1", "snapshot_id": "snap_1", "result_status": "insufficient", "stale_status": "current", "continuity_status": "continuous", "data_quality_status": "ok"},
                {"ok": True, "history_id": "history_1", "history_result_status": "insufficient_history"},
                {"ok": False, "error_code": "zone_evidence_invalid"},
            ]
            def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                if "check-macro-structure-health" in argv:
                    return subprocess.CompletedProcess(argv, 3, '{"ok":false,"exit_code":3,"report_written":true,"health_state":"failed","health_artifact_id":"health_failed"}\n', "")
                value = outputs.pop(0)
                return subprocess.CompletedProcess(argv, 0 if value.get("ok") else 2, json.dumps(value) + "\n", "")
            with patch.object(service, "_fetch_public_ohlcv", side_effect=fetch), patch.object(service.subprocess, "run", side_effect=run):
                code, result = service.run_service(self.args(root))
            self.assertNotEqual(code, 0)
            self.assertEqual(result["snapshot_run_id"], "run_1")
            self.assertEqual(result["history_id"], "history_1")
            self.assertEqual(result["history_result_status"], "insufficient_history")
            self.assertEqual(result["error_code"], "zone_evidence_invalid")
            self.assertEqual(result["steps"][-1]["name"], "operator")

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

    def test_health_is_called_once_after_final_status_and_core_exit_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            events: list[str] = []

            def fetch(path: Path, limit: int, interval: str, symbol: str) -> None:
                path.write_text("valid", encoding="utf-8")

            core = {
                "run-macro-structure-daily": {"ok": True, "run_id": "run_1", "snapshot_id": "snap_1", "result_status": "ok", "stale_status": "current", "continuity_status": "continuous", "data_quality_status": "ok"},
                "run-macro-structure-history": {"ok": True, "history_id": "history_1", "history_result_status": "ok"},
                "render-macro-structure-operator": {"ok": True, "operator_artifact_id": "operator_1"},
            }

            def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                if "check-macro-structure-health" in argv:
                    events.append("health")
                    return subprocess.CompletedProcess(argv, 2, json.dumps(self.health_result("degraded", 2)) + "\n", "")
                events.append("core")
                name = next(key for key in core if key in argv)
                return subprocess.CompletedProcess(argv, 0, json.dumps(core[name]) + "\n", "")

            original_atomic = service._atomic_json

            def atomic(path: Path, payload: dict[str, object]) -> None:
                events.append("status")
                original_atomic(path, payload)

            with patch.object(service, "_fetch_public_ohlcv", side_effect=fetch), patch.object(service.subprocess, "run", side_effect=run), patch.object(service, "_atomic_json", side_effect=atomic):
                code, result = service.run_service(self.args(root))
            self.assertEqual(code, 0)
            self.assertEqual(events.count("health"), 1)
            self.assertLess(events.index("status"), events.index("health"))
            self.assertEqual(result["health_generation"]["status"], "published")
            self.assertEqual(result["health_generation"]["health_state"], "degraded")
            persisted = json.loads((root / "logs/runtime/macro_structure_service_last_result.json").read_text())
            self.assertNotIn("health_generation", persisted)
            self.assertEqual(persisted["status"], "success")

    def test_health_generation_failure_does_not_change_core_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            def fetch(path: Path, limit: int, interval: str, symbol: str) -> None:
                path.write_text("valid", encoding="utf-8")

            def run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                if "check-macro-structure-health" in argv:
                    return subprocess.CompletedProcess(argv, 0, "not-json\n", "")
                if "run-macro-structure-daily" in argv:
                    value = {"ok": True, "run_id": "run_1", "snapshot_id": "snap_1", "result_status": "ok", "stale_status": "current", "continuity_status": "continuous", "data_quality_status": "ok"}
                elif "run-macro-structure-history" in argv:
                    value = {"ok": True, "history_id": "history_1", "history_result_status": "ok"}
                else:
                    value = {"ok": True, "operator_artifact_id": "operator_1"}
                return subprocess.CompletedProcess(argv, 0, json.dumps(value) + "\n", "")

            with patch.object(service, "_fetch_public_ohlcv", side_effect=fetch), patch.object(service.subprocess, "run", side_effect=run):
                code, result = service.run_service(self.args(root))
            self.assertEqual(code, 0)
            self.assertEqual(result["health_generation"]["status"], "failed")
            self.assertEqual(result["health_generation"]["error_code"], "health_compact_json_missing")
            persisted = json.loads((root / "logs/runtime/macro_structure_service_last_result.json").read_text())
            self.assertEqual(persisted["status"], "success")
            self.assertNotIn("health_generation", persisted)

    def test_already_running_does_not_invoke_health(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock_path = root / "logs/runtime/macro_structure_service.lock"
            lock_path.parent.mkdir(parents=True)
            handle = lock_path.open("a+")
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                with patch.object(service, "_fetch_public_ohlcv") as fetch, patch.object(service.subprocess, "run") as run:
                    code, result = service.run_service(self.args(root))
                self.assertEqual(code, 0)
                self.assertEqual(result["status"], "already_running")
                fetch.assert_not_called()
                run.assert_not_called()
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                handle.close()

    def test_dry_run_lists_one_health_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(service, "_fetch_public_ohlcv") as fetch, patch.object(service.subprocess, "run") as run:
                code, result = service.run_service(self.args(root, "--dry-run"))
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "dry_run")
            self.assertEqual(result["health_command"][2], "check-macro-structure-health")
            self.assertEqual(result["health_output_root"], "local/reports/macro_structure/health")
            fetch.assert_not_called()
            run.assert_not_called()


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
