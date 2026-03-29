from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import build_summary_body, build_summary_subject


class SummaryFormatTest(unittest.TestCase):
    def test_ready_case_separates_direction_and_execution(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "API",
            "prelabel": "ENTRY_OK",
            "bias": "long",
            "current_price": 70356.3,
            "confidence": 79,
            "phase": "pullback",
            "long_display_score": 72,
            "short_display_score": 55,
            "score_gap": 17,
            "market_regime": "uptrend",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "long",
            "funding_rate_display": "ほぼ中立 (+0.0037%)",
            "atr_ratio": 0.85,
            "volume_ratio": 1.21,
            "support_zones": [{"low": 69900.0, "high": 70010.0, "distance_from_price": 346.3}],
            "resistance_zones": [{"low": 70450.0, "high": 70600.0, "distance_from_price": 93.7}],
            "long_setup": {
                "status": "ready",
                "entry_zone": {"low": 70000.0, "high": 70100.0},
                "stop_loss": 69700.0,
                "tp1": 70800.0,
                "tp2": 71200.0,
            },
            "short_setup": {
                "status": "watch",
                "entry_zone": {"low": 70600.0, "high": 70700.0},
                "stop_loss": 70900.0,
                "tp1": 70000.0,
                "tp2": 69500.0,
            },
            "primary_setup_status": "ready",
            "primary_setup_reason": "inside_entry_zone_with_trigger",
            "risk_flags": [],
            "no_trade_flags": [],
            "ai_advice": {
                "decision": "LONG",
                "quality": "A",
                "confidence": 0.82,
                "primary_reason": "上方向は維持だが断定ではなく条件付きで見る局面。",
                "next_condition": "出来高維持を確認",
                "warnings": [],
            },
        }

        subject = build_summary_subject(payload)
        body, provider_used = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertEqual(provider_used, "api")
        self.assertIn("上方向バイアス", subject)
        self.assertIn("条件付きで検討", subject)
        self.assertIn("総合強度79", subject)
        self.assertIn("方向判断: 相場は上方向バイアスです", body)
        self.assertIn("いまの扱い: ロングは条件付きで検討", body)
        self.assertIn("位置評価: 位置条件は悪くない", body)
        self.assertIn("【ロング/ショートのセットアップ状況】", body)

    def test_attention_subject_and_body_are_wait_first(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-15T06:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "CLI",
            "notification_kind": "attention",
            "bias": "short",
            "current_price": 70765.2,
            "long_display_score": 38,
            "short_display_score": 59,
            "score_gap": -21,
            "signals_4h": "wait",
            "signals_1h": "short",
            "signals_15m": "wait",
            "prelabel": "SWEEP_WAIT",
            "primary_setup_status": "watch",
            "primary_setup_reason": "near_entry_zone_waiting_trigger",
            "confidence": 41,
            "risk_flags": ["upper_liquidity_close"],
            "no_trade_flags": ["sweep_incomplete"],
        }

        subject = build_summary_subject(payload)
        body, provider_used = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )
        self.assertEqual(provider_used, "api")
        self.assertTrue(subject.startswith("👀 [注意報]"))
        self.assertIn("下方向バイアス", subject)
        self.assertIn("上側流動性回収待ち", body)
        self.assertIn("方向判断: 相場は下方向バイアスです", body)
        self.assertNotIn("入る条件がかなりそろっています", body)

    def test_machine_only_subject_warns_and_body_hides_internal_codes(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-17T03:05:00+09:00",
            "system_label": "Ver02.3",
            "system_mode_label": "CLI",
            "prelabel": "SWEEP_WAIT",
            "bias": "short",
            "primary_setup_status": "watch",
            "primary_setup_reason": "near_entry_zone_waiting_trigger",
            "current_price": 73911.8,
            "confidence": 66,
            "risk_flags": ["bid_wall_close", "upper_liquidity_close"],
            "no_trade_flags": ["sweep_incomplete"],
            "long_setup": {"status": "invalid", "entry_zone": {"low": 73349.0, "high": 73683.0}, "stop_loss": 73051.0, "tp1": 73734.0, "tp2": 74892.0},
            "short_setup": {"status": "watch", "entry_zone": {"low": 73734.0, "high": 74104.0}, "stop_loss": 74557.0, "tp1": 73683.0, "tp2": 72506.0},
            "ai_advice": None,
        }

        subject = build_summary_subject(payload)
        body, _provider_used = build_summary_body(
            provider="cli",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )

        self.assertTrue(subject.startswith("⚠️ 機械判定のみ "))
        self.assertIn("下方向バイアス", body)
        self.assertIn("上側流動性回収待ち", body)
        self.assertIn("近い買い板があり短期ノイズに注意", body)
        self.assertIn("上側流動性が近く先に振られやすい", body)
        self.assertNotIn("bid_wall_close", body)
        self.assertNotIn("upper_liquidity_close", body)
