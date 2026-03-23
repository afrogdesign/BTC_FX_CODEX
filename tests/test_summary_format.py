from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import build_summary_body, build_summary_subject


class SummaryFormatTest(unittest.TestCase):
    def test_subject_and_body_include_badge_and_funding_display(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "system_label": "Ver02.1",
            "system_mode_label": "API",
            "signal_badge": "🟡 好条件接近",
            "signal_tier": "strong_machine",
            "prelabel": "ENTRY_OK",
            "bias": "long",
            "current_price": 70356.3,
            "confidence": 79,
            "location_risk": 12.0,
            "phase": "pullback",
            "long_display_score": 72,
            "short_display_score": 55,
            "score_gap": 17,
            "market_regime": "uptrend",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "wait",
            "funding_rate_display": "ほぼ中立 (+0.0037%)",
            "funding_rate_label": "ほぼ中立",
            "funding_rate_pct": 0.0037,
            "atr_ratio": 0.85,
            "volume_ratio": 0.75,
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
            "ai_advice": {
                "decision": "LONG",
                "quality": "A",
                "confidence": 0.82,
                "notes": "方向は上向きです。",
            },
            "no_trade_flags": [],
            "risk_flags": [],
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
        self.assertTrue(subject.startswith("🟡 好条件接近"))
        self.assertIn("買い候補がそろい始め", subject)
        self.assertIn("【BTC:70,356】", subject)
        self.assertIn("信頼度79", subject)
        self.assertTrue(subject.endswith("[Ver02.1] [API]"))
        self.assertNotIn("[BTC監視]", subject)
        self.assertIn("ほぼ中立 (+0.0037%)", body)
        self.assertIn("🟡 好条件接近", body)
        self.assertIn("【セットアップ】", body)
        self.assertIn("再検討帯は 70,000.00 - 70,100.00", body)
        self.assertIn("損切り目安は 69,700.00", body)
        self.assertIn("利確目安は TP1 70,800.00 / TP2 71,200.00", body)
        self.assertIn("・ロング: 提案候補。", body)
        self.assertIn("・ショート: 監視継続。", body)
        self.assertNotIn("SWEEP_WAIT", body)
        self.assertNotIn("critical_zone", body)
        self.assertNotIn("RR不足", body)

    def test_attention_subject_and_body_are_clearly_marked(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-15T06:05:00+09:00",
            "system_label": "Ver02.1",
            "system_mode_label": "CLI",
            "notification_kind": "attention",
            "bias": "long",
            "current_price": 70765.2,
            "long_display_score": 59,
            "short_display_score": 38,
            "score_gap": 21,
            "signals_4h": "wait",
            "signals_1h": "wait",
            "signals_15m": "wait",
            "prelabel": "SWEEP_WAIT",
            "confidence": 4,
            "no_trade_flags": ["RR_insufficient", "sweep_incomplete"],
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
        self.assertIn("ロング寄りに傾き始め", subject)
        self.assertIn("【BTC:70,765】", subject)
        self.assertIn("信頼度4", subject)
        self.assertTrue(subject.endswith("[Ver02.1] [CLI]"))
        self.assertNotIn("[BTC監視]", subject)
        self.assertIn("売買推奨メールではなく", body)
        self.assertNotIn("Gap 21", subject)

    def test_wait_case_keeps_numbers_and_translates_internal_terms(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-17T04:05:00+09:00",
            "prelabel": "SWEEP_WAIT",
            "bias": "long",
            "current_price": 73883.0,
            "confidence": 66,
            "phase": "pullback",
            "long_display_score": 90,
            "short_display_score": 41,
            "score_gap": 49,
            "market_regime": "uptrend",
            "signals_4h": "long",
            "signals_1h": "long",
            "signals_15m": "wait",
            "funding_rate_display": "ほぼ中立 (+0.0038%)",
            "atr_ratio": 1.2,
            "volume_ratio": 0.77,
            "support_zones": [{"low": 73349.0, "high": 73683.0, "distance_from_price": 200.0}],
            "resistance_zones": [{"low": 73734.0, "high": 74104.0, "distance_from_price": 0.0}],
            "long_setup": {
                "status": "watch",
                "entry_zone": {"low": 73349.0, "high": 73683.0},
                "stop_loss": 73051.0,
                "tp1": 73734.0,
                "tp2": 74892.0,
            },
            "short_setup": {
                "status": "invalid",
                "entry_zone": {"low": 73734.0, "high": 74104.0},
                "stop_loss": 74557.0,
                "tp1": 73683.0,
                "tp2": 72506.0,
            },
            "ai_advice": {
                "decision": "WAIT_FOR_SWEEP",
                "quality": "B",
                "confidence": 0.78,
                "notes": "上向きでも位置が悪く、いったん振ってからの反発待ちです。",
            },
            "no_trade_flags": ["Critical_zone_warning", "RR_insufficient", "sweep_incomplete"],
            "risk_flags": ["lower_liquidity_close", "sweep_incomplete"],
        }

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

        self.assertIn("相場は上向きです。", body)
        self.assertIn("一度下を試してからの反発待ちです", body)
        self.assertIn("・ロング: 監視継続。再検討帯は 73,349.00 - 73,683.00", body)
        self.assertIn("・ショート: 現状は見送り。再検討帯は 73,734.00 - 74,104.00", body)
        self.assertIn("AI判断は「いったん振ってからの反発待ち」", body)
        self.assertIn("重要な価格帯", body)
        self.assertNotIn("SWEEP_WAIT", body)
        self.assertNotIn("critical_zone", body)

    def test_subject_warns_first_when_ai_is_unavailable(self) -> None:
        payload = {
            "timestamp_jst": "2026-03-17T03:05:00+09:00",
            "system_label": "Ver02.1",
            "system_mode_label": "CLI",
            "prelabel": "SWEEP_WAIT",
            "bias": "long",
            "current_price": 73911.8,
            "confidence": 66,
            "ai_advice": None,
        }

        subject = build_summary_subject(payload)

        self.assertTrue(subject.startswith("⚠️ 機械判定のみ "))
        self.assertIn("上向きだが今は待機", subject)
        self.assertIn("【BTC:73,912】", subject)
        self.assertIn("信頼度66", subject)
        self.assertTrue(subject.endswith("[Ver02.1] [CLI]"))


if __name__ == "__main__":
    unittest.main()
