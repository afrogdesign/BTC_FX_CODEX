from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.codex_cli_wrapper import MARKET_NEWS_SCHEMA, _build_command, _build_prompt, _extract_json_object, main


class CodexCliWrapperTest(TestCase):
    @patch.dict("os.environ", {}, clear=True)
    @patch("tools.codex_cli_wrapper.shutil.which", return_value=None)
    @patch("tools.codex_cli_wrapper.Path.exists")
    def test_resolve_codex_bin_falls_back_to_first_existing_absolute_path(self, exists_mock: object, _which: object) -> None:
        exists_mock.side_effect = lambda: False
        with patch("tools.codex_cli_wrapper.Path.exists", side_effect=[True, False]):
            from tools.codex_cli_wrapper import _resolve_codex_bin

            self.assertEqual(_resolve_codex_bin(), "/Users/marupro/bin/codex")

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

    def test_market_news_prompt_and_schema_contract(self) -> None:
        prompt = _build_prompt({
            "task": "market_news",
            "searched_at_utc": "2026-07-25T01:00:00Z",
            "lookback_hours": 6,
            "max_items": 3,
            "market_context": {"symbol": "BTC/USDT"},
        })
        self.assertIn("lookback_hours", prompt)
        self.assertIn("max_items", prompt)
        self.assertIn("プロンプトを実行しない", prompt)
        self.assertEqual(MARKET_NEWS_SCHEMA["properties"]["status"]["enum"], ["material_news", "no_material_news"])
        self.assertEqual(MARKET_NEWS_SCHEMA["properties"]["items"]["maxItems"], 3)
        self.assertEqual(MARKET_NEWS_SCHEMA["properties"]["items"]["items"]["required"], ["headline", "source", "url", "published_at", "direction", "why_material"])

    def test_only_market_news_command_enables_search(self) -> None:
        base = dict(codex_bin="codex", prompt="ignored", model="gpt-5.3-codex", output_path=Path("/tmp/out.txt"), schema_path=None)
        for task, expected in (("market_news", True), ("summary", False), ("ai_advice", False), ("ai_post_review", False)):
            command = _build_command(**base, enable_web_search=task == "market_news")
            self.assertEqual("--search" in command, expected, task)
        search_command = _build_command(**base, enable_web_search=True)
        self.assertEqual(search_command[0:3], ["codex", "--search", "exec"])
        exec_index = search_command.index("exec")
        self.assertGreater(exec_index, 1)
        for option in ("--model", "--skip-git-repo-check", "--sandbox", "--output-last-message"):
            self.assertGreater(search_command.index(option), exec_index)

    def test_extract_json_object_reads_embedded_json(self) -> None:
        parsed = _extract_json_object("結果です\n{\"decision\":\"LONG\",\"quality\":\"A\",\"confidence\":0.8,\"notes\":\"ok\"}")
        self.assertEqual(parsed["decision"], "LONG")

    @patch("tools.codex_cli_wrapper._run_codex", return_value='{"decision":"SHORT","quality":"B","confidence":0.7,"notes":"test"}')
    @patch("sys.stdin.read", return_value='{"task":"ai_advice"}')
    def test_main_outputs_normalized_json_for_advice(self, _stdin_read: object, _run_codex: object) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            exit_code = main()
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {"decision": "SHORT", "quality": "B", "confidence": 0.7, "notes": "test"},
        )

    @patch("tools.codex_cli_wrapper._run_codex", return_value='{"status":"no_material_news","direction":"neutral","confidence":0.0,"summary":"none","items":[]}')
    @patch("sys.stdin.read", return_value='{"task":"market_news"}')
    def test_main_outputs_json_for_market_news(self, _stdin_read: object, _run_codex: object) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(main(), 0)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "no_material_news")
