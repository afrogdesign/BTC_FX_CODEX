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
            "system_label": "Ver02",
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
            "ai_advice": None,
            "no_trade_flags": [],
            "risk_flags": [],
        }

        subject = build_summary_subject(payload)
        body = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )
        self.assertTrue(subject.startswith("🟡 好条件接近"))
        self.assertIn("ほぼ中立 (+0.0037%)", body)
        self.assertIn("🟡 好条件接近", body)


if __name__ == "__main__":
    unittest.main()
