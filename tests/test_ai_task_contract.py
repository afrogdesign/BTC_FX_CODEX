import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.ai_task_contract import ContractError, canonical_diff_command, canonical_sha, load_json, render_prompt, validate_report, validate_task

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "chatgpt/tasks/examples"
TOOL = ROOT / "tools/ai_task_contract.py"


class TaskContractTests(unittest.TestCase):
    def implementation(self):
        return load_json(EXAMPLES / "implementation_task.example.json")

    def acceptance(self):
        return load_json(EXAMPLES / "acceptance_task.example.json")

    def report(self):
        return load_json(EXAMPLES / "task_report.example.json")

    def test_parent_v1_shapes_and_examples(self):
        task = self.implementation()
        self.assertEqual(task["schema_version"], "1.0")
        self.assertEqual(set(task["repo"]), {"working_dir", "expected_branch", "expected_base_commit"})
        self.assertIsInstance(task["contract_refs"][0], dict)
        self.assertEqual(set(task["allowed"]), {"read", "edit", "inspect"})
        self.assertEqual(set(task["autonomy"]), {"helper_design", "cache_design", "fixture_design", "execution_order", "obvious_in_scope_bugfix", "remove_redundant_validation"})
        self.assertEqual(set(task["validation"]), {"unit_tests", "fixture_e2e", "diff_check_files", "heavy"})
        self.assertEqual(set(task["commit"]), {"enabled", "message", "push"})
        self.assertEqual(validate_task(task), canonical_sha(task))
        self.assertEqual(validate_task(self.acceptance()), canonical_sha(self.acceptance()))
        validate_report(task, self.report())

    def test_invalid_utf8_non_object_duplicate_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_bytes(b"\xff\xfe")
            with self.assertRaises(ContractError):
                load_json(path)
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(ContractError):
                load_json(path)
            path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaises(ContractError):
                load_json(path)
            path.write_text('{"a": NaN}', encoding="utf-8")
            with self.assertRaises(ContractError):
                load_json(path)

    def test_nested_unknown_and_invalid_types_fail_as_contract_errors(self):
        bad = self.implementation()
        bad["requirements"][0]["extra"] = True
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["validation"]["fixture_e2e"] = None
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["commit"] = "bad"
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["repo"]["expected_base_commit"] = True
        with self.assertRaises(ContractError):
            validate_task(bad)

    def test_paths_refs_inspect_runtime_and_stage_rules(self):
        bad = self.implementation()
        bad["contract_refs"][0]["clauses"] = []
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["allowed"]["inspect"] = ["full_repo"]
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["allowed"]["edit"].append("../outside.py")
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["repo"]["working_dir"] = "/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor"
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.acceptance()
        bad["allowed"]["edit"] = ["tools/x.py"]
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.acceptance()
        bad["validation"]["heavy"]["max_full_runs"] = 2
        with self.assertRaises(ContractError):
            validate_task(bad)

    def test_foreground_and_sensitive_rejection(self):
        bad = self.implementation()
        bad["validation"]["unit_tests"] = ["pytest tests &"]
        with self.assertRaises(ContractError):
            validate_task(bad)
        for key in ("raw_row", "raw_rows"):
            bad = self.implementation()
            bad[key] = "private"
            with self.assertRaises(ContractError):
                validate_task(bad)
        bad = self.implementation()
        bad["goal"] = "use sk-test-secret"
        with self.assertRaises(ContractError):
            validate_task(bad)

    def test_sha_and_renderer_limits(self):
        task = self.implementation()
        reformatted = json.loads(json.dumps(task, indent=2))
        self.assertEqual(canonical_sha(task), canonical_sha(reformatted))
        fresh = render_prompt(task, EXAMPLES / "implementation_task.example.json", "fresh")
        delta = render_prompt(task, EXAMPLES / "implementation_task.example.json", "delta")
        self.assertTrue(fresh.startswith("AUTO_SEND\n"))
        self.assertLessEqual(len([x for x in fresh.splitlines() if x.strip()]), 20)
        self.assertLessEqual(len([x for x in delta.splitlines() if x.strip()]), 14)
        self.assertIn("TASK_SHA256:", fresh)
        self.assertNotIn("requirements:", fresh.lower())
        self.assertNotIn("history", fresh.lower())

    def test_report_null_notes_and_mismatch_regressions(self):
        task = self.implementation()
        report = self.report()
        self.assertIsNone(report["notes"])
        for field, value in (("work_id", "wrong"), ("task_revision", 2), ("task_sha256", "f" * 64), ("branch", "wrong"), ("base_commit", "1" * 40)):
            bad = copy.deepcopy(report)
            bad[field] = value
            with self.assertRaises(ContractError, msg=field):
                validate_report(task, bad)
        for field, value in (("authorized", True), ("planned_work_units", 2), ("full_runs", 1)):
            bad = copy.deepcopy(report)
            bad["heavy_validation"][field] = value
            with self.assertRaises(ContractError, msg=field):
                validate_report(task, bad)
        bad = copy.deepcopy(report)
        bad["commit"]["message"] = "wrong"
        with self.assertRaises(ContractError):
            validate_report(task, bad)

    def test_push_alignment_and_partial_subset(self):
        task = self.implementation()
        report = self.report()
        partial = copy.deepcopy(report)
        partial["status"] = "partial"
        partial["tests"] = [partial["tests"][0]]
        partial["requirements"]["IO-01"]["status"] = "not_run"
        partial["commit"] = None
        validate_report(task, partial)
        bad = copy.deepcopy(report)
        bad["push"] = {"remote": "origin", "branch": "other", "commit": report["commit"]["hash"]}
        with self.assertRaises(ContractError):
            validate_report(task, bad)
        checkpoint = copy.deepcopy(task)
        checkpoint["stage"] = "checkpoint"; checkpoint["mode"] = "CHECKPOINT_PUSH"; checkpoint["commit"]["push"] = True; checkpoint["allowed"]["edit"] = []
        checkpoint_report = copy.deepcopy(report)
        checkpoint_report["work_id"] = checkpoint["work_id"] = "BTCFX-CHECKPOINT"
        checkpoint_report["task_sha256"] = canonical_sha(checkpoint)
        checkpoint_report["changed_files"] = []
        checkpoint_report["push"] = {"remote": "origin", "branch": "Ver04-v2", "commit": checkpoint_report["commit"]["hash"]}
        validate_report(checkpoint, checkpoint_report)

    def test_done_command_rules_and_cli_success_outputs(self):
        task_path = EXAMPLES / "implementation_task.example.json"
        report_path = EXAMPLES / "task_report.example.json"
        result = subprocess.run([sys.executable, str(TOOL), "validate-task", "--task", str(task_path)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0); self.assertIn("BTCFX-EXAMPLE-A1-IMPLEMENTATION", result.stdout)
        for context in ("fresh", "delta"):
            result = subprocess.run([sys.executable, str(TOOL), "render-prompt", "--task", str(task_path), "--context", context], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0); self.assertTrue(result.stdout.startswith("AUTO_SEND\n"))
        result = subprocess.run([sys.executable, str(TOOL), "validate-report", "--task", str(task_path), "--report", str(report_path)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0); self.assertIn("BTCFX-EXAMPLE-A1-IMPLEMENTATION", result.stdout); self.assertIn(canonical_sha(self.implementation()), result.stdout)
        bad = self.report(); bad["tests"] = bad["tests"] + [bad["tests"][0]]
        with self.assertRaises(ContractError):
            validate_report(self.implementation(), bad)

    def test_diff_command_order(self):
        task = self.implementation()
        self.assertEqual(canonical_diff_command(task["validation"]["diff_check_files"]), "git diff --check -- " + " ".join(task["validation"]["diff_check_files"]))


if __name__ == "__main__":
    unittest.main()
