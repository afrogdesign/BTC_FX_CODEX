from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.codex_cli_wrapper import _build_command, _build_prompt, _extract_json_object, main


class CodexCliWrapperTest(TestCase):
    @patch.dict("os.environ", {}, clear=True)
    @patch("tools.codex_cli_wrapper.shutil.which", return_value=None)
    @patch("tools.codex_cli_wrapper.Path.exists")
    def test_resolve_codex_bin_falls_back_to_common_absolute_path(self, exists_mock: object, _which: object) -> None:
        exists_mock.side_effect = lambda: False
        with patch("tools.codex_cli_wrapper.Path.exists", side_effect=[True, False]):
            from tools.codex_cli_wrapper import _resolve_codex_bin

            self.assertEqual(_resolve_codex_bin(), "/usr/local/bin/codex")

    def test_build_prompt_for_summary_includes_result_payload(self) -> None:
        prompt = _build_prompt(
            {
                "task": "summary",
                "system_prompt": "summary system",
                "result_payload": {"bias": "long", "confidence": 77},
            }
        )
        self.assertIn("通知本文作成担当", prompt)
        self.assertIn('"bias": "long"', prompt)

    def test_build_command_adds_model_and_schema(self) -> None:
        command = _build_command(
            codex_bin="codex",
            prompt="ignored",
            model="gpt-5.3-codex",
            output_path=Path("/tmp/out.txt"),
            schema_path=Path("/tmp/schema.json"),
        )
        self.assertEqual(command[0], "codex")
        self.assertIn("--model", command)
        self.assertIn("gpt-5.3-codex", command)
        self.assertIn("--output-schema", command)

    def test_extract_json_object_reads_embedded_json(self) -> None:
        parsed = _extract_json_object("結果です\n{\"decision\":\"LONG\",\"quality\":\"A\",\"confidence\":0.8,\"notes\":\"ok\"}")
        self.assertEqual(parsed["decision"], "LONG")

    @patch("tools.codex_cli_wrapper._run_codex", return_value='{"decision":"SHORT","quality":"B","confidence":0.7,"notes":"test"}')
    @patch("sys.stdin.read", return_value='{"task":"ai_advice"}')
    def test_main_outputs_normalized_json_for_advice(self, _stdin_read: object, _run_codex: object) -> None:
        with patch("sys.stdout.write") as stdout_write:
            exit_code = main()
        written = "".join(call.args[0] for call in stdout_write.call_args_list)
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(written), {"decision": "SHORT", "quality": "B", "confidence": 0.7, "notes": "test"})
