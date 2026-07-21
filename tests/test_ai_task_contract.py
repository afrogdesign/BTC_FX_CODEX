import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.ai_task_contract import (
    ContractError,
    canonical_diff_command,
    canonical_sha,
    load_json,
    render_prompt,
    validate_report,
    validate_task,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "chatgpt/tasks/examples"
TOOL = ROOT / "tools/ai_task_contract.py"
DIFF_COMMAND = "git diff --check -- chatgpt/specs/active/20260721_ai_task_manifest_acceptance_gate_a1.md chatgpt/tasks/README.md chatgpt/tasks/schemas/task_manifest.schema.json chatgpt/tasks/schemas/task_report.schema.json chatgpt/tasks/examples/implementation_task.example.json chatgpt/tasks/examples/acceptance_task.example.json chatgpt/tasks/examples/task_report.example.json tools/ai_task_contract.py tests/test_ai_task_contract.py"


class TaskContractTests(unittest.TestCase):
    def implementation(self):
        return load_json(EXAMPLES / "implementation_task.example.json")

    def acceptance(self):
        return load_json(EXAMPLES / "acceptance_task.example.json")

    def test_valid_examples_and_canonical_sha_stability(self):
        task = self.implementation()
        self.assertEqual(validate_task(task), canonical_sha(task))
        self.assertEqual(validate_task(self.acceptance()), canonical_sha(self.acceptance()))
        reformatted = json.loads(json.dumps(task, indent=2))
        self.assertEqual(canonical_sha(task), canonical_sha(reformatted))
        report = load_json(EXAMPLES / "task_report.example.json")
        validate_report(task, report, EXAMPLES / "implementation_task.example.json")

    def test_strict_json_duplicate_nonfinite_and_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaises(ContractError):
                load_json(path)
            path.write_text('{"a": NaN}', encoding="utf-8")
            with self.assertRaises(ContractError):
                load_json(path)
        bad = self.implementation()
        bad["unexpected"] = True
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["requirements"][0]["unexpected"] = True
        with self.assertRaises(ContractError):
            validate_task(bad)

    def test_stage_mode_paths_and_heavy_boundaries(self):
        bad = self.implementation()
        bad["mode"] = "REVIEW_ONLY"
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["allowed"]["edit"].append("../outside.py")
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["validation"]["heavy"]["authorized"] = True
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

    def test_foreground_commands_and_sensitive_data(self):
        bad = self.implementation()
        bad["validation"]["unit_tests"] = ["pytest tests &"]
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["goal"] = "use sk-test-secret"
        with self.assertRaises(ContractError):
            validate_task(bad)
        bad = self.implementation()
        bad["goal"] = "contact user@example.com"
        with self.assertRaises(ContractError):
            validate_task(bad)

    def test_renderer_is_compact_and_does_not_expand_prose(self):
        task = self.implementation()
        fresh = render_prompt(task, EXAMPLES / "implementation_task.example.json", "fresh")
        delta = render_prompt(task, EXAMPLES / "implementation_task.example.json", "delta")
        self.assertEqual(fresh.splitlines()[0], "AUTO_SEND")
        self.assertLessEqual(len([line for line in fresh.splitlines() if line.strip()]), 20)
        self.assertLessEqual(len([line for line in delta.splitlines() if line.strip()]), 14)
        self.assertIn("TASK_SHA256:", fresh)
        self.assertIn("manual prompt routing", fresh)
        self.assertNotIn("requirements:", fresh.lower())
        self.assertNotIn("history", fresh.lower())

    def test_report_alignment_mismatches_fail_closed(self):
        task = self.implementation()
        report = load_json(EXAMPLES / "task_report.example.json")
        for field, value in (("work_id", "wrong"), ("task_revision", 2), ("task_sha256", "f" * 64), ("branch", "wrong"), ("base_commit", "1" * 40)):
            bad = copy.deepcopy(report)
            bad[field] = value
            with self.assertRaises(ContractError, msg=field):
                validate_report(task, bad, EXAMPLES / "implementation_task.example.json")
        bad = copy.deepcopy(report)
        bad["changed_files"].append("src/main.py")
        with self.assertRaises(ContractError):
            validate_report(task, bad, EXAMPLES / "implementation_task.example.json")
        bad = copy.deepcopy(report)
        bad["tests"][0]["command"] = "not-listed"
        with self.assertRaises(ContractError):
            validate_report(task, bad, EXAMPLES / "implementation_task.example.json")
        bad = copy.deepcopy(report)
        bad["requirements"]["IO-01"]["status"] = "fail"
        with self.assertRaises(ContractError):
            validate_report(task, bad, EXAMPLES / "implementation_task.example.json")

    def test_subprocess_cli_all_routes(self):
        task_path = EXAMPLES / "implementation_task.example.json"
        report_path = EXAMPLES / "task_report.example.json"
        commands = [
            [sys.executable, str(TOOL), "validate-task", "--task", str(task_path)],
            [sys.executable, str(TOOL), "render-prompt", "--task", str(task_path), "--context", "fresh"],
            [sys.executable, str(TOOL), "render-prompt", "--task", str(task_path), "--context", "delta"],
            [sys.executable, str(TOOL), "validate-report", "--task", str(task_path), "--report", str(report_path)],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(subprocess.run(commands[1], cwd=ROOT, text=True, capture_output=True).stdout.startswith("AUTO_SEND\n"))

    def test_outbox_contract_is_fixed_and_diff_command_is_ordered(self):
        task = self.implementation()
        self.assertEqual(task["report"]["write_once"], True)
        self.assertEqual(canonical_diff_command(task["allowed"]["diff_check"]), DIFF_COMMAND)


if __name__ == "__main__":
    unittest.main()
