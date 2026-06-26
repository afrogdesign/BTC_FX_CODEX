from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.advice import request_ai_advice
from src.ai.summary import build_summary_body


class AiCliRetryTest(TestCase):
    @patch("src.ai.advice.write_ai_error_log")
    @patch("src.ai.advice.run_cli_json")
    def test_request_ai_advice_retries_cli_and_recovers(self, run_cli_json_mock: object, error_log_mock: object) -> None:
        run_cli_json_mock.side_effect = [
            RuntimeError("temporary failure"),
            {
                "decision": "WAIT_FOR_SWEEP",
                "quality": "B",
                "confidence": 0.84,
                "notes": "retry ok",
                "primary_reason": "retry ok",
                "market_interpretation": "range",
                "entry_position_quality": "C",
                "warnings": [],
                "next_condition": "wait",
            },
        ]

        result, provider_used = request_ai_advice(
            provider="cli",
            api_key="",
            model="gpt-5.3-codex",
            cli_command="/tmp/codex_cli_wrapper.py",
            timeout_sec=30,
            retry_count=2,
            base_dir=BASE_DIR,
            machine_payload={"bias": "long"},
            qualitative_payload={"note": "sample"},
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["decision"], "WAIT_FOR_SWEEP")
        self.assertEqual(provider_used, "cli")
        self.assertEqual(run_cli_json_mock.call_count, 2)
        self.assertEqual(result["advice_variant"], "direction_execution_split_v2")
        error_log_mock.assert_not_called()

    def test_build_summary_body_uses_template_layout(self) -> None:
        result, provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="gpt-5.3-codex",
            cli_command="/tmp/codex_cli_wrapper.py",
            timeout_sec=30,
            retry_count=2,
            base_dir=BASE_DIR,
            result_payload={"bias": "long", "prelabel": "ENTRY_OK", "confidence": 80},
        )

        self.assertIn("【結論】", result)
        self.assertIn("方向判断:", result)
        self.assertIn("執行判断:", result)
        self.assertEqual(provider_used, "cli")

    @patch("src.ai.advice.write_ai_error_log")
    @patch("src.ai.advice.run_cli_json", side_effect=RuntimeError("always fail"))
    def test_request_ai_advice_logs_after_cli_retries_exhausted(self, _run_cli_json_mock: object, error_log_mock: object) -> None:
        result, provider_used = request_ai_advice(
            provider="cli",
            api_key="",
            model="gpt-5.3-codex",
            cli_command="/tmp/codex_cli_wrapper.py",
            timeout_sec=30,
            retry_count=2,
            base_dir=BASE_DIR,
            machine_payload={"bias": "long"},
            qualitative_payload={"note": "sample"},
        )

        self.assertIsNone(result)
        self.assertEqual(provider_used, "cli_failed")
        error_log_mock.assert_called_once()
        self.assertIn("retry_count=2", error_log_mock.call_args[0][2])

    def test_build_summary_body_keeps_setup_lines_in_template(self) -> None:
        result, provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="gpt-5.3-codex",
            cli_command="/tmp/codex_cli_wrapper.py",
            timeout_sec=30,
            retry_count=2,
            base_dir=BASE_DIR,
            result_payload={
                "bias": "long",
                "prelabel": "ENTRY_OK",
                "confidence": 80,
                "location_risk": 10,
                "phase": "pullback",
                "long_display_score": 70,
                "short_display_score": 50,
                "score_gap": 20,
                "market_regime": "uptrend",
                "signals_4h": "long",
                "signals_1h": "long",
                "signals_15m": "wait",
                "current_price": 70000,
                "funding_rate_label": "ほぼ中立",
                "funding_rate_pct": 0.0,
                "atr_ratio": 1.0,
                "volume_ratio": 1.0,
                "support_zones": [],
                "resistance_zones": [],
                "long_setup": {},
                "short_setup": {},
                "no_trade_flags": [],
                "risk_flags": [],
            },
        )

        self.assertIn("【結論】", result)
        self.assertIn("【ロング/ショートのセットアップ状況】", result)
        self.assertIn("・ロング:", result)
        self.assertEqual(provider_used, "cli")

    @patch("src.ai.advice._request_ai_advice_via_api")
    @patch("src.ai.advice.write_ai_error_log")
    @patch("src.ai.advice.run_cli_json", side_effect=RuntimeError("401 Unauthorized"))
    def test_request_ai_advice_does_not_fall_back_to_api_when_cli_fails(
        self,
        _run_cli_json_mock: object,
        error_log_mock: object,
        api_request_mock: object,
    ) -> None:
        with patch.dict(os.environ, {"AI_API_USAGE_ALLOWED": "true"}, clear=False):
            result, provider_used = request_ai_advice(
                provider="cli",
                api_key="sk-test",
                model="gpt-5.3-codex",
                cli_command="/tmp/codex_cli_wrapper.py",
                timeout_sec=30,
                retry_count=2,
                base_dir=BASE_DIR,
                machine_payload={"bias": "long"},
                qualitative_payload={"note": "sample"},
            )

        self.assertIsNone(result)
        self.assertEqual(provider_used, "cli_failed")
        api_request_mock.assert_not_called()
        error_log_mock.assert_called_once()

    @patch("src.ai.advice._request_ai_advice_via_api")
    @patch("src.ai.advice.write_ai_error_log")
    def test_request_ai_advice_does_not_fall_back_to_api_when_cli_command_missing(
        self,
        error_log_mock: object,
        api_request_mock: object,
    ) -> None:
        with patch.dict(os.environ, {"AI_API_USAGE_ALLOWED": "true"}, clear=False):
            result, provider_used = request_ai_advice(
                provider="cli",
                api_key="sk-test",
                model="gpt-5.3-codex",
                cli_command="",
                timeout_sec=30,
                retry_count=2,
                base_dir=BASE_DIR,
                machine_payload={"bias": "long"},
                qualitative_payload={"note": "sample"},
            )

        self.assertIsNone(result)
        self.assertEqual(provider_used, "cli_failed")
        api_request_mock.assert_not_called()
        error_log_mock.assert_called_once()

    @patch("src.ai.advice._request_ai_advice_via_api")
    @patch("src.ai.advice.write_ai_error_log")
    def test_request_ai_advice_blocks_api_when_usage_not_allowed(
        self,
        error_log_mock: object,
        api_request_mock: object,
    ) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-env"}, clear=False):
            result, provider_used = request_ai_advice(
                provider="api",
                api_key="sk-test",
                model="gpt-5.3-codex",
                cli_command="/tmp/codex_cli_wrapper.py",
                timeout_sec=30,
                retry_count=2,
                base_dir=BASE_DIR,
                machine_payload={"bias": "long"},
                qualitative_payload={"note": "sample"},
            )

        self.assertIsNone(result)
        self.assertEqual(provider_used, "api_disabled")
        api_request_mock.assert_not_called()
        error_log_mock.assert_called_once()

    @patch("src.ai.advice._request_ai_advice_via_api")
    @patch("src.ai.advice.write_ai_error_log")
    def test_request_ai_advice_reaches_api_only_when_usage_allowed(
        self,
        error_log_mock: object,
        api_request_mock: object,
    ) -> None:
        api_request_mock.return_value = {
            "decision": "WAIT",
            "final_action": "WAIT",
            "quality": "B",
            "confidence": 0.41,
            "notes": "api fallback",
            "primary_reason": "api fallback",
            "market_interpretation": "range",
            "entry_position_quality": "C",
            "warnings": [],
            "next_condition": "wait",
        }

        with patch.dict(os.environ, {"AI_API_USAGE_ALLOWED": "true", "OPENAI_API_KEY": "sk-env"}, clear=False):
            result, provider_used = request_ai_advice(
                provider="api",
                api_key="sk-test",
                model="gpt-5.3-codex",
                cli_command="/tmp/codex_cli_wrapper.py",
                timeout_sec=30,
                retry_count=2,
                base_dir=BASE_DIR,
                machine_payload={"bias": "long"},
                qualitative_payload={"note": "sample"},
            )

        self.assertIsNotNone(result)
        self.assertEqual(result["decision"], "WAIT")
        self.assertEqual(provider_used, "api")
        api_request_mock.assert_called_once()
        error_log_mock.assert_not_called()

    def test_build_summary_body_provider_label_is_preserved(self) -> None:
        result, provider_used = build_summary_body(
            provider="cli",
            api_key="sk-test",
            model="gpt-5.3-codex",
            cli_command="/tmp/codex_cli_wrapper.py",
            timeout_sec=30,
            retry_count=2,
            base_dir=BASE_DIR,
            result_payload={"bias": "long", "prelabel": "ENTRY_OK", "confidence": 80},
        )

        self.assertIn("【結論】", result)
        self.assertEqual(provider_used, "cli")


if __name__ == "__main__":
    import unittest

    unittest.main()
