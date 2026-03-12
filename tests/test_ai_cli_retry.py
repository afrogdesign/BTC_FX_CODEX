from __future__ import annotations

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

        result = request_ai_advice(
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
        self.assertEqual(run_cli_json_mock.call_count, 2)
        error_log_mock.assert_not_called()

    @patch("src.ai.summary.write_ai_error_log")
    @patch("src.ai.summary.run_cli_text")
    def test_build_summary_body_retries_cli_and_recovers(self, run_cli_text_mock: object, error_log_mock: object) -> None:
        run_cli_text_mock.side_effect = [
            RuntimeError("temporary failure"),
            "CLI summary body",
        ]

        result = build_summary_body(
            provider="cli",
            api_key="",
            model="gpt-5.3-codex",
            cli_command="/tmp/codex_cli_wrapper.py",
            timeout_sec=30,
            retry_count=2,
            base_dir=BASE_DIR,
            result_payload={"bias": "long", "prelabel": "ENTRY_OK", "confidence": 80},
        )

        self.assertEqual(result, "CLI summary body")
        self.assertEqual(run_cli_text_mock.call_count, 2)
        error_log_mock.assert_not_called()

    @patch("src.ai.advice.write_ai_error_log")
    @patch("src.ai.advice.run_cli_json", side_effect=RuntimeError("always fail"))
    def test_request_ai_advice_logs_after_cli_retries_exhausted(self, _run_cli_json_mock: object, error_log_mock: object) -> None:
        result = request_ai_advice(
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
        error_log_mock.assert_called_once()
        self.assertIn("retry_count=2", error_log_mock.call_args.args[2])

    @patch("src.ai.summary.write_ai_error_log")
    @patch("src.ai.summary.run_cli_text", side_effect=RuntimeError("always fail"))
    def test_build_summary_body_falls_back_after_cli_retries_exhausted(self, _run_cli_text_mock: object, error_log_mock: object) -> None:
        result = build_summary_body(
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
        error_log_mock.assert_called_once()
        self.assertIn("retry_count=2", error_log_mock.call_args.args[2])


if __name__ == "__main__":
    import unittest

    unittest.main()
