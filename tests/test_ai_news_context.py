from __future__ import annotations

import copy
import os
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.news_context import _safe_url, build_web_news_context_status, request_web_news_context


class AiNewsContextTest(TestCase):
    def test_disabled_and_non_notify_status_do_not_call_cli(self) -> None:
        with patch("src.ai.news_context.run_cli_json") as run:
            disabled = request_web_news_context(enabled=False, cli_command="codex", model="m", timeout_sec=5, retry_count=2, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
            skipped = build_web_news_context_status(enabled=True, fetch_status="skipped_non_notify")
        self.assertEqual(disabled["fetch_status"], "disabled")
        self.assertEqual(disabled["attempt_count"], 0)
        self.assertEqual(skipped["fetch_status"], "skipped_non_notify")
        run.assert_not_called()

    def test_material_news_is_sanitized_and_bounded(self) -> None:
        payload = {
            "status": "material_news", "direction": "bullish", "confidence": 4,
            "summary": "summary\x00" * 200,
            "items": [
                {"headline": "A", "source": "S", "url": "https://example.com/a#frag", "published_at": "2026-07-25T00:00:00Z", "direction": "bullish", "why_material": "reason"},
                {"headline": "bad", "source": "S", "url": "javascript:alert(1)", "published_at": "", "direction": "bearish", "why_material": "x"},
                {"headline": "B", "source": "S", "url": "https://example.com/b", "published_at": "2026-07-25T00:01:00Z", "direction": "bearish", "why_material": "x"},
            ],
        }
        with patch("src.ai.news_context.run_cli_json", return_value=payload) as run:
            result = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=2, lookback_hours=6, max_items=2, base_dir=BASE_DIR, result_payload={"current_price": 100, "operator_decision": {"state": "blocked"}, "secret": "must not pass"})
        self.assertEqual(result["fetch_status"], "completed")
        self.assertEqual(result["news_status"], "material_news")
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0]["url"], "https://example.com/a")
        sent = run.call_args.kwargs["payload"]
        self.assertNotIn("secret", sent["market_context"])

    def test_url_safety_uses_raw_value_before_normalization(self) -> None:
        valid = {"headline": "ok", "source": "s", "url": "https://example.com/ok", "published_at": "", "direction": "unknown", "why_material": "x"}
        bad_urls = [
            "",
            "javascript:alert(1)",
            "data:text/plain,x",
            "file:///tmp/a",
            "ftp://example.com/a",
            "https:///missing-host",
            "https://example.com/\nwrapped",
            "https://example.com/\twrapped",
            "https://example.com/" + ("x" * 2048),
        ]
        for url in bad_urls:
            self.assertEqual(_safe_url(url), "")
        items = [dict(valid, url="https://example.com/ok#fragment"), dict(valid, url="https://example.com/ok")]
        payload = {"status": "material_news", "direction": "unknown", "confidence": 0, "summary": "s", "items": items}
        with patch("src.ai.news_context.run_cli_json", return_value=payload):
            result = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=1, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
        self.assertEqual([item["url"] for item in result["items"]], ["https://example.com/ok"])

    def test_invalid_schema_and_status_retry_then_unavailable_once(self) -> None:
        invalid_root = {"status": "material_news", "direction": "unknown", "confidence": 0, "summary": "s", "items": [], "extra": True}
        with patch("src.ai.news_context.run_cli_json", return_value=invalid_root), patch("src.ai.news_context.write_ai_error_log") as log:
            result = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=2, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
        self.assertEqual(result["error_code"], "invalid_schema")
        self.assertEqual(log.call_count, 1)
        invalid_status = {"status": "other", "direction": "unknown", "confidence": 0, "summary": "s", "items": []}
        with patch("src.ai.news_context.run_cli_json", return_value=invalid_status), patch("src.ai.news_context.write_ai_error_log") as log:
            result = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=1, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
        self.assertEqual(result["error_code"], "invalid_status")
        log.assert_called_once()

    def test_material_item_schema_mismatch_retries(self) -> None:
        malformed = {"status": "material_news", "direction": "unknown", "confidence": "bad", "summary": "s", "items": [{"headline": "missing"}]}
        with patch("src.ai.news_context.run_cli_json", return_value=malformed) as run, patch("src.ai.news_context.write_ai_error_log"):
            result = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=2, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
        self.assertEqual(result["fetch_status"], "unavailable")
        self.assertEqual(result["error_code"], "invalid_schema")
        self.assertEqual(run.call_count, 2)

    def test_no_material_news_has_no_items_and_no_retry(self) -> None:
        payload = {"status": "no_material_news", "direction": "neutral", "confidence": 0, "summary": "none", "items": [{"url": "https://example.com"}]}
        with patch("src.ai.news_context.run_cli_json", return_value=payload) as run:
            result = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=3, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
        self.assertEqual(result["items"], [])
        self.assertEqual(run.call_count, 1)

    def test_missing_command_and_retry_recovery(self) -> None:
        missing = request_web_news_context(enabled=True, cli_command="", model="m", timeout_sec=5, retry_count=2, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
        self.assertEqual(missing["error_code"], "cli_command_missing")
        payload = {"status": "no_material_news", "direction": "neutral", "confidence": 0, "summary": "none", "items": []}
        with patch("src.ai.news_context.run_cli_json", side_effect=[RuntimeError("temporary"), payload]) as run:
            recovered = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=2, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload={})
        self.assertEqual(recovered["fetch_status"], "completed")
        self.assertEqual(recovered["attempt_count"], 2)
        self.assertEqual(run.call_count, 2)

    def test_exhausted_failure_is_unavailable_and_logs_minimal_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch("src.ai.news_context.run_cli_json", side_effect=TimeoutError("timed out")), patch("src.ai.news_context.write_ai_error_log") as log:
            result = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=2, lookback_hours=6, max_items=3, base_dir=Path(tmp), result_payload={})
        self.assertEqual(result["fetch_status"], "unavailable")
        self.assertEqual(result["error_code"], "cli_timeout")
        self.assertEqual(result["attempt_count"], 2)
        log.assert_called_once()

    def test_deterministic_fields_are_unchanged(self) -> None:
        core = {"score": 80, "confidence": 0.7, "notify": True, "notification_kind": "main", "trade_execution_gate": "blocked", "operator_decision": {"state": "blocked"}, "active_trade_plan": {"side": "short"}, "entry": 1, "sl": 2, "tp": 3}
        before = copy.deepcopy(core)
        with patch("src.ai.news_context.run_cli_json", side_effect=RuntimeError("bad")), patch("src.ai.news_context.write_ai_error_log"):
            context = request_web_news_context(enabled=True, cli_command="codex", model="m", timeout_sec=5, retry_count=1, lookback_hours=6, max_items=3, base_dir=BASE_DIR, result_payload=core)
        self.assertEqual(core, before)
        self.assertEqual(context["fetch_status"], "unavailable")

    def test_main_attach_gate_and_advice_payload_order(self) -> None:
        import main

        cfg = SimpleNamespace(AI_NEWS_WEB_SEARCH_ENABLED=True, AI_NEWS_LOOKBACK_HOURS=6, AI_NEWS_MAX_ITEMS=3, AI_ADVICE_CLI_COMMAND="codex", OPENAI_ADVICE_MODEL="m", AI_TIMEOUT_SEC=5, AI_RETRY_COUNT=2)
        result = {"score": 80, "confidence": 0.8, "signals_15m": "short", "trade_execution_gate": "blocked", "operator_decision": {"state": "blocked"}, "active_trade_plan": {"side": "short"}, "entry": 1, "sl": 2, "tp": 3, "notification_kind": "main"}
        with patch("main.request_web_news_context", return_value={"schema_version": "web_news_context.v1", "fetch_status": "completed"}) as fetch:
            main._attach_web_news_context(result, cfg=cfg, base_dir=BASE_DIR, notify=True)
        fetch.assert_called_once()
        self.assertIn("web_news_context", result)
        with patch("main.request_web_news_context") as fetch:
            main._attach_web_news_context(result, cfg=cfg, base_dir=BASE_DIR, notify=False)
        fetch.assert_not_called()
        self.assertEqual(result["web_news_context"]["fetch_status"], "skipped_non_notify")

    def test_main_attach_unexpected_error_is_fail_closed(self) -> None:
        import main

        cfg = SimpleNamespace(AI_NEWS_WEB_SEARCH_ENABLED=True, AI_NEWS_LOOKBACK_HOURS=6, AI_NEWS_MAX_ITEMS=3)
        result = {"score": 80, "confidence": 0.8, "operator_decision": {"state": "blocked"}}
        with patch("main.request_web_news_context", side_effect=RuntimeError("unexpected")):
            main._attach_web_news_context(result, cfg=cfg, base_dir=BASE_DIR, notify=True)
        self.assertEqual(result["web_news_context"]["fetch_status"], "unavailable")
        self.assertEqual(result["web_news_context"]["news_status"], "unknown")
        self.assertEqual(result["web_news_context"]["error_code"], "unknown_error")

    def test_config_defaults_and_os_override(self) -> None:
        from config import load_config

        required = {"OPENAI_API_KEY": "", "SMTP_HOST": "host", "SMTP_PORT": "587", "SMTP_USER": "u", "SMTP_PASSWORD": "p", "MAIL_FROM": "f", "MAIL_TO": "t"}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("\n".join(f"{key}={value}" for key, value in required.items()), encoding="utf-8")
            with patch.dict(os.environ, {"AI_NEWS_WEB_SEARCH_ENABLED": "true", "AI_NEWS_LOOKBACK_HOURS": "9", "AI_NEWS_MAX_ITEMS": "2"}, clear=False):
                cfg = load_config(Path(tmp))
        self.assertTrue(cfg.AI_NEWS_WEB_SEARCH_ENABLED)
        self.assertEqual(cfg.AI_NEWS_LOOKBACK_HOURS, 9)
        self.assertEqual(cfg.AI_NEWS_MAX_ITEMS, 2)
