from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from src.feedback.macro_structure_health_status import _evaluation_time, check_macro_structure_health


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "logs/runtime/macro_structure_service_last_result.json"
SNAPSHOT_LATEST = ROOT / "local/reports/macro_structure/latest.json"
HISTORY_LATEST = ROOT / "local/reports/macro_structure/history/latest.json"
OPERATOR_LATEST = ROOT / "local/reports/macro_structure/operator/latest.json"
PLIST = ROOT / "deploy/com.afrog.btc-macro-structure.plist"
_RUNTIME_SEED = json.loads(RUNTIME.read_text())
SNAPSHOT_RUN_ID = _RUNTIME_SEED["snapshot_run_id"]
SNAPSHOT_ID = _RUNTIME_SEED["snapshot_id"]
HISTORY_ID = _RUNTIME_SEED["history_id"]
OPERATOR_ID = _RUNTIME_SEED["operator_artifact_id"]
SNAPSHOT = ROOT / "local/reports/macro_structure" / SNAPSHOT_RUN_ID
HISTORY = ROOT / "local/reports/macro_structure/history" / HISTORY_ID
OPERATOR = ROOT / "local/reports/macro_structure/operator" / OPERATOR_ID
DEFAULT_EVALUATION = (datetime.fromisoformat(_RUNTIME_SEED["evaluation_utc"]) + timedelta(minutes=10)).isoformat()


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
        snapshot_latest = json.loads(SNAPSHOT_LATEST.read_text())
        snapshot_latest["symbol"] = "BTC_USDT"
        (self.snapshot_root / "latest.json").write_text(json.dumps(snapshot_latest))
        shutil.copy2(HISTORY_LATEST, self.history_root / "latest.json")
        shutil.copy2(OPERATOR_LATEST, self.operator_root / "latest.json")
        runtime = json.loads(self.runtime.read_text())
        runtime["snapshot_result_status"] = "insufficient"
        self.runtime.write_text(json.dumps(runtime))
        for path, key in (
            (self.snapshot_root / SNAPSHOT.name / "macro_structure_snapshot.json", "result_status"),
            (self.snapshot_root / "latest.json", "result_status"),
            (self.history_root / "latest.json", "latest_snapshot_result_status"),
            (self.operator_root / OPERATOR.name / "macro_structure_operator.json", "snapshot_result_status"),
            (self.operator_root / "latest.json", "snapshot_result_status"),
        ):
            value = json.loads(path.read_text())
            if path.name == "macro_structure_operator.json":
                value["source_status"][key] = "insufficient"
            else:
                value[key] = "insufficient"
            path.write_text(json.dumps(value))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_health(self, evaluation: str = DEFAULT_EVALUATION) -> dict:
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

    def set_failed_runtime(self, stage: str, *, pre_staging: bool = False) -> None:
        data = json.loads(self.runtime.read_text())
        data.update(status="failed", ok=False, error_code=f"{stage}_failed")
        if pre_staging:
            data["steps"] = []
            data.pop("public_input_fingerprints", None)
            for field in ("snapshot_run_id", "snapshot_id", "history_id", "operator_artifact_id"):
                data.pop(field, None)
            data.pop("snapshot_result_status", None)
            data.pop("history_result_status", None)
        else:
            names = ["snapshot", "history", "operator"]
            failed_index = names.index(stage)
            data["steps"] = [
                {"name": name, "status": "failed" if index == failed_index else "success", "return_code": 2 if index == failed_index else 0}
                for index, name in enumerate(names[: failed_index + 1])
            ]
        self.runtime.write_text(json.dumps(data))

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
        self.assertEqual(payload["evaluation_utc"], DEFAULT_EVALUATION)
        self.assertTrue(payload["report_only"])
        self.assertFalse(payload["private_actual_trade_input"])
        self.assertFalse(payload["automatic_order_allowed"])
        self.assertEqual(payload["displayed_support_count"], 5)
        self.assertIsInstance(payload["displayed_resistance_count"], int)
        self.assertEqual(payload["operator_result_status"], "ok")
        self.assertEqual(payload["latest_evaluated_at_utc"], _RUNTIME_SEED["evaluation_utc"])
        self.assertTrue(payload["latest_evaluated_at_jst"].endswith("+09:00"))
        self.assertTrue(payload["operator_html_path"].endswith(f"/{OPERATOR_ID}/macro_structure_operator.html"))
        self.assertNotIn("None", payload["operator_html_path"])
        self.assertNotIn(str(ROOT), json.dumps(payload))
        self.assertEqual(payload["runtime_stdout_path"], "logs/runtime/macro_structure_service.launchd.out")
        self.assertEqual(payload["runtime_stderr_path"], "logs/runtime/macro_structure_service.launchd.err")
        self.assertEqual(payload["runtime_status_path"], "runtime.json")
        self.assertTrue(all(key in payload["public_input_fingerprints"] for key in ("15m", "1h", "4h")))
        expected = {
            "snapshot:latest.json", "history:latest.json", "operator:latest.json",
            "snapshot:run_manifest.json", "history:run_manifest.json", "operator:run_manifest.json",
            "input:runtime_status", "input:plist", "input:public:15m", "input:public:1h", "input:public:4h",
        }
        self.assertTrue(expected.issubset(payload["source_fingerprints"]))
        self.assertEqual(len(payload["source_fingerprints"]), len(set(payload["source_fingerprints"])))

    def test_stale_is_degraded(self) -> None:
        data = json.loads(self.runtime.read_text())
        data["stale_status"] = "stale"
        self.runtime.write_text(json.dumps(data))
        for path, key in (
            (self.snapshot_root / SNAPSHOT.name / "macro_structure_snapshot.json", "stale_status"),
            (self.snapshot_root / "latest.json", "stale_status"),
            (self.history_root / "latest.json", "latest_stale_status"),
            (self.operator_root / "latest.json", "stale_status"),
        ):
            value = json.loads(path.read_text())
            value[key] = "stale"
            path.write_text(json.dumps(value))
        result = self.run_health()
        self.assertEqual(result["health_state"], "degraded")
        self.assertEqual(result["exit_code"], 2)

    def test_failed_runtime_is_failed(self) -> None:
        data = json.loads(self.runtime.read_text())
        self.set_failed_runtime("operator")
        result = self.run_health()
        self.assertEqual(result["health_state"], "failed")
        self.assertEqual(result["exit_code"], 3)
        payload = self.read_health(result)
        self.assertEqual(payload["operator_result_status"], "failed")
        self.assertEqual(payload["snapshot_run_id"], SNAPSHOT_RUN_ID)
        self.assertEqual(payload["history_id"], HISTORY_ID)

    def test_overdue_precedes_failed(self) -> None:
        data = json.loads(self.runtime.read_text())
        self.set_failed_runtime("operator")
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

    def test_pre_staging_failure_is_failed_without_fingerprints(self) -> None:
        self.set_failed_runtime("input", pre_staging=True)
        result = self.run_health()
        self.assertEqual(result["health_state"], "failed")
        payload = self.read_health(result)
        self.assertEqual(payload["first_failed_step"], None)
        self.assertEqual(payload["operator_result_status"], "not_run")
        self.assertNotIn("input:public:15m", payload["source_fingerprints"])

    def test_snapshot_and_history_early_failures_are_failed(self) -> None:
        self.set_failed_runtime("snapshot")
        snapshot_result = self.run_health()
        self.assertEqual(snapshot_result["health_state"], "failed")
        snapshot_payload = self.read_health(snapshot_result)
        self.assertEqual(snapshot_payload["first_failed_step"], "snapshot")
        self.assertEqual(snapshot_payload["operator_result_status"], "not_run")

        self.temp.cleanup()
        self.setUp()
        self.set_failed_runtime("history")
        history_result = self.run_health()
        self.assertEqual(history_result["health_state"], "failed")
        history_payload = self.read_health(history_result)
        self.assertEqual(history_payload["first_failed_step"], "history")
        self.assertEqual(history_payload["operator_result_status"], "not_run")
        self.assertEqual(history_payload["snapshot_run_id"], SNAPSHOT_RUN_ID)

    def test_invalid_failed_prefix_and_success_ok_are_inconsistent(self) -> None:
        data = json.loads(self.runtime.read_text())
        data.update(status="failed", ok=False, error_code="bad_order", steps=[{"name": "history", "status": "failed", "return_code": 2}])
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(result["health_state"], "inconsistent")

        self.temp.cleanup()
        self.setUp()
        data = json.loads(self.runtime.read_text())
        data["ok"] = False
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(result["health_state"], "inconsistent")

    def test_partial_public_fingerprints_are_inconsistent(self) -> None:
        self.set_failed_runtime("snapshot")
        data = json.loads(self.runtime.read_text())
        data["public_input_fingerprints"].pop("4h")
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(result["health_state"], "inconsistent")

    def test_detailed_latest_pointer_identity_mismatches_are_inconsistent(self) -> None:
        cases = (
            ("snapshot_root", "run_id", "wrong_run", "snapshot_latest_run_id_mismatch"),
            ("snapshot_root", "snapshot_id", "wrong_snapshot", "snapshot_latest_snapshot_id_mismatch"),
            ("snapshot_root", "symbol", "ETH_USDT", "snapshot_latest_symbol_mismatch"),
            ("history_root", "history_id", "wrong_history", "history_latest_history_id_mismatch"),
            ("operator_root", "operator_artifact_id", "wrong_operator", "operator_latest_operator_artifact_id_mismatch"),
            ("operator_root", "selected_snapshot_run_id", "wrong_run", "operator_latest_selected_snapshot_run_mismatch"),
            ("operator_root", "selected_snapshot_id", "wrong_snapshot", "operator_latest_selected_snapshot_id_mismatch"),
            ("operator_root", "selected_history_id", "wrong_history", "operator_latest_selected_history_id_mismatch"),
        )
        for root_attr, key, value, error_code in cases:
            with self.subTest(key=key):
                path = getattr(self, root_attr) / "latest.json"
                current = json.loads(path.read_text())
                current[key] = value
                path.write_text(json.dumps(current))
                result = self.run_health()
                self.assertEqual(result["health_state"], "inconsistent")
                self.assertEqual(self.read_health(result)["error_code"], error_code)
                self.tearDown()
                self.setUp()

    def test_runtime_status_and_time_integrity_are_inconsistent(self) -> None:
        cases = (
            ("snapshot_result_status", "ok", "runtime_snapshot_result_status_mismatch"),
            ("stale_status", "stale", "runtime_stale_status_mismatch"),
            ("continuity_status", "discontinuous", "runtime_continuity_status_mismatch"),
            ("data_quality_status", "warning", "runtime_data_quality_status_mismatch"),
        )
        for key, value, error_code in cases:
            with self.subTest(key=key):
                data = json.loads(self.runtime.read_text())
                data[key] = value
                self.runtime.write_text(json.dumps(data))
                result = self.run_health()
                self.assertEqual(result["health_state"], "inconsistent")
                self.assertEqual(self.read_health(result)["error_code"], error_code)
                self.tearDown()
                self.setUp()
        data = json.loads(self.runtime.read_text())
        data["started_at_utc"], data["finished_at_utc"] = data["finished_at_utc"], data["started_at_utc"]
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(self.read_health(result)["error_code"], "runtime_time_order")

    def test_failed_pipeline_exposes_only_completed_stage_ids(self) -> None:
        self.set_failed_runtime("snapshot")
        payload = self.read_health(self.run_health())
        self.assertEqual(payload["snapshot_result_status"], "failed")
        self.assertEqual(payload["history_result_status"], "not_run")
        self.assertEqual(payload["operator_result_status"], "not_run")
        self.assertIsNone(payload.get("snapshot_run_id"))
        self.assertIsNone(payload.get("history_id"))
        self.assertIsNone(payload.get("operator_artifact_id"))
        self.assertNotIn("operator_html_path", payload)

        self.tearDown()
        self.setUp()
        self.set_failed_runtime("history")
        payload = self.read_health(self.run_health())
        self.assertEqual(payload["snapshot_run_id"], SNAPSHOT_RUN_ID)
        self.assertIsNone(payload.get("history_id"))
        self.assertIsNone(payload.get("operator_artifact_id"))

        self.tearDown()
        self.setUp()
        self.set_failed_runtime("operator")
        payload = self.read_health(self.run_health())
        self.assertEqual(payload["history_id"], HISTORY_ID)
        self.assertEqual(payload["operator_result_status"], "failed")
        self.assertIsNone(payload.get("operator_artifact_id"))
        self.assertNotIn("operator_html_path", payload)

    def test_already_running_is_unavailable_without_artifact_ids(self) -> None:
        data = json.loads(self.runtime.read_text())
        data.update(status="already_running", ok=False, steps=[], error_code=None)
        data.pop("snapshot_run_id", None)
        data.pop("snapshot_id", None)
        data.pop("history_id", None)
        data.pop("operator_artifact_id", None)
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        payload = self.read_health(result)
        self.assertEqual(result["health_state"], "unavailable")
        self.assertEqual(payload["error_code"], "runtime_completed_result_unavailable")
        self.assertNotIn("snapshot_run_id", payload)
        self.assertNotIn("history_id", payload)
        self.assertNotIn("operator_artifact_id", payload)

    def test_manifest_source_and_success_step_contracts_are_strict(self) -> None:
        cases = (
            ("snapshot_root", SNAPSHOT.name, "wrong_source", "snapshot_manifest_source_mismatch"),
            ("history_root", HISTORY.name, "wrong_source", "history_manifest_source_mismatch"),
            ("operator_root", OPERATOR.name, "wrong_source", "operator_manifest_source_mismatch"),
        )
        for root_attr, artifact_name, value, error_code in cases:
            with self.subTest(path=artifact_name):
                path = getattr(self, root_attr) / artifact_name / "run_manifest.json"
                manifest = json.loads(path.read_text())
                manifest["source"] = value
                path.write_text(json.dumps(manifest))
                result = self.run_health()
                self.assertEqual(self.read_health(result)["error_code"], error_code)
                self.tearDown()
                self.setUp()
        data = json.loads(self.runtime.read_text())
        data["steps"][0]["return_code"] = 1
        self.runtime.write_text(json.dumps(data))
        result = self.run_health()
        self.assertEqual(self.read_health(result)["error_code"], "runtime_success_return_code")

    def test_explicit_evaluation_precision_is_preserved(self) -> None:
        value = _evaluation_time("2026-01-02T16:10:23.456789+00:00")
        self.assertEqual(value.isoformat(), "2026-01-02T16:10:23.456789+00:00")

    def test_latest_pointer_and_manifest_changes_change_health_id(self) -> None:
        first = self.run_health()
        ids = [first["health_artifact_id"]]
        for root, name in ((self.snapshot_root, "snapshot"), (self.history_root, "history"), (self.operator_root, "operator")):
            pointer = root / "latest.json"
            data = json.loads(pointer.read_text())
            data[f"audit_{name}"] = True
            pointer.write_text(json.dumps(data))
            ids.append(self.run_health()["health_artifact_id"])
            data.pop(f"audit_{name}")
            pointer.write_text(json.dumps(data))
        manifest = self.snapshot_root / SNAPSHOT_RUN_ID / "run_manifest.json"
        data = json.loads(manifest.read_text())
        data["audit_manifest"] = True
        manifest.write_text(json.dumps(data))
        ids.append(self.run_health()["health_artifact_id"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_midnight_schedule_calculation(self) -> None:
        from src.feedback.macro_structure_health_status import _scheduled
        last, upcoming = _scheduled(datetime.fromisoformat("2026-07-21T15:30:00+00:00"))
        self.assertEqual(last.isoformat(), "2026-07-21T12:10:00+00:00")
        self.assertEqual(upcoming.isoformat(), "2026-07-21T16:10:00+00:00")

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
