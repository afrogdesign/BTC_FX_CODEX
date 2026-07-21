from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.feedback.macro_structure_health_status import check_macro_structure_health


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "logs/runtime/macro_structure_service_last_result.json"
SNAPSHOT = ROOT / "local/reports/macro_structure/run_bc49b15e01e3c2d49d64"
SNAPSHOT_LATEST = ROOT / "local/reports/macro_structure/latest.json"
HISTORY = ROOT / "local/reports/macro_structure/history/history_e0fa3fd0ebc25b781c5f"
HISTORY_LATEST = ROOT / "local/reports/macro_structure/history/latest.json"
OPERATOR = ROOT / "local/reports/macro_structure/operator/operator_128b44f88c8a1e02b350"
OPERATOR_LATEST = ROOT / "local/reports/macro_structure/operator/latest.json"
PLIST = ROOT / "deploy/com.afrog.btc-macro-structure.plist"


class MacroStructureHealthStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.runtime = base / "runtime.json"
        self.snapshot_root = base / "snapshot"
        self.history_root = base / "history"
        self.operator_root = base / "operator"
        self.output_root = base / "health"
        self.plist = base / "service.plist"
        shutil.copy2(RUNTIME, self.runtime)
        shutil.copy2(PLIST, self.plist)
        shutil.copytree(SNAPSHOT, self.snapshot_root / SNAPSHOT.name)
        shutil.copytree(HISTORY, self.history_root / HISTORY.name)
        shutil.copytree(OPERATOR, self.operator_root / OPERATOR.name)
        shutil.copy2(SNAPSHOT_LATEST, self.snapshot_root / "latest.json")
        shutil.copy2(HISTORY_LATEST, self.history_root / "latest.json")
        shutil.copy2(OPERATOR_LATEST, self.operator_root / "latest.json")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_health(self, evaluation: str = "2026-07-22T00:20:00+09:00") -> dict:
        return check_macro_structure_health(
            runtime_status=self.runtime,
            snapshot_root=self.snapshot_root,
            history_root=self.history_root,
            operator_root=self.operator_root,
            plist=self.plist,
            output_root=self.output_root,
            evaluation_time_utc=evaluation,
        )

    def read_health(self, summary: dict) -> dict:
        return json.loads((self.output_root / summary["artifact_dir"] / "macro_structure_health.json").read_text())

    def test_coherent_healthy_insufficient_and_contract_fields(self) -> None:
        result = self.run_health()
        self.assertEqual(result["health_state"], "healthy_insufficient")
        self.assertEqual(result["exit_code"], 0)
        self.assertTrue(result["ok"])
        payload = self.read_health(result)
        self.assertEqual(payload["schema_version"], "macro_structure_health_status.v1")
        self.assertEqual(payload["method_version"], "macro_structure_health_status.v1")
        self.assertEqual(payload["snapshot_result_status"], "insufficient")
        self.assertEqual(payload["stale_status"], "current")
        self.assertEqual(payload["continuity_status"], "continuous")
        self.assertEqual(payload["data_quality_status"], "ok")
        self.assertEqual(payload["evaluation_jst"], "2026-07-22T00:20:00+09:00")
        self.assertTrue(payload["report_only"])
        self.assertFalse(payload["private_actual_trade_input"])
        self.assertFalse(payload["automatic_order_allowed"])
        self.assertEqual(payload["displayed_support_count"], 5)
        self.assertEqual(payload["displayed_resistance_count"], 0)
        self.assertTrue(all(key in payload["public_input_fingerprints"] for key in ("15m", "1h", "4h")))

    def test_stale_is_degraded(self) -> None:
        data = json.loads(self.runtime.read_text())
        data["stale_status"] = "stale"
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(result["health_state"], "degraded")
        self.assertEqual(result["exit_code"], 2)

    def test_failed_runtime_is_failed(self) -> None:
        data = json.loads(self.runtime.read_text())
        data["status"] = "failed"
        data["steps"][2]["status"] = "failed"
        data["steps"][2]["return_code"] = 2
        data["error_code"] = "operator_failed"
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(result["health_state"], "failed")
        self.assertEqual(result["exit_code"], 3)

    def test_overdue_precedes_failed(self) -> None:
        data = json.loads(self.runtime.read_text())
        data["status"] = "failed"
        data["steps"][2]["status"] = "failed"
        data["steps"][2]["return_code"] = 2
        self.runtime.write_text(json.dumps(data))
        result = self.run_health("2026-07-22T08:00:00+09:00")
        self.assertEqual(result["health_state"], "overdue")
        self.assertEqual(result["exit_code"], 2)

    def test_missing_runtime_publishes_unavailable(self) -> None:
        self.runtime.unlink()
        result = self.run_health()
        self.assertEqual(result["health_state"], "unavailable")
        self.assertEqual(result["exit_code"], 3)
        payload = self.read_health(result)
        self.assertEqual(payload["error_code"], "runtime_status_unavailable")

    def test_identity_mismatch_is_inconsistent(self) -> None:
        data = json.loads(self.runtime.read_text())
        data["history_id"] = "history_wrong"
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(result["health_state"], "inconsistent")
        self.assertEqual(self.read_health(result)["error_code"], "history_latest_id_mismatch")

    def test_schedule_mismatch_is_inconsistent(self) -> None:
        data = __import__("plistlib").loads(self.plist.read_bytes())
        data["StartCalendarInterval"] = data["StartCalendarInterval"][:-1]
        self.plist.write_bytes(__import__("plistlib").dumps(data))
        result = self.run_health()
        self.assertEqual(result["health_state"], "inconsistent")
        self.assertEqual(self.read_health(result)["error_code"], "plist_schedule_mismatch")

    def test_midnight_schedule_calculation(self) -> None:
        result = self.run_health("2026-07-22T00:30:00+09:00")
        payload = self.read_health(result)
        self.assertEqual(payload["last_scheduled_jst"], "2026-07-21T21:10:00+09:00")
        self.assertEqual(payload["next_scheduled_jst"], "2026-07-22T01:10:00+09:00")

    def test_repeat_is_byte_identical(self) -> None:
        first = self.run_health()
        files = {p.name: p.read_bytes() for p in (self.output_root / first["artifact_dir"]).iterdir()}
        second = self.run_health()
        self.assertEqual(first["health_artifact_id"], second["health_artifact_id"])
        for name, content in files.items():
            self.assertEqual(content, (self.output_root / first["artifact_dir"] / name).read_bytes())

    def test_conflict_preserves_previous_latest(self) -> None:
        first = self.run_health()
        latest_before = (self.output_root / "latest.json").read_bytes()
        target = self.output_root / first["artifact_dir"] / "macro_structure_health.json"
        target.write_text("conflict\n")
        second = self.run_health()
        self.assertFalse(second["report_written"])
        self.assertEqual(second["error_code"], "existing_health_conflict")
        self.assertEqual(latest_before, (self.output_root / "latest.json").read_bytes())

    def test_jst_and_source_paths_are_auditable(self) -> None:
        result = self.run_health()
        payload = self.read_health(result)
        self.assertEqual(payload["runtime_status_path"], "runtime.json")
        self.assertNotIn(str(ROOT), json.dumps(payload))
        self.assertIn("snapshot", payload["contract_checks"])


if __name__ == "__main__":
    unittest.main()
