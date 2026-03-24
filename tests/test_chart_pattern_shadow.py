from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import load_config
from main import run_cycle
from src.analysis.chart_pattern_shadow import build_chart_pattern_shadow
from src.data.exchange_fetcher import MarketStructureSnapshot
from src.analysis.structure import detect_swings


def _sample_df(length: int = 260, *, trend: float = 1.0) -> pd.DataFrame:
    rows = []
    price = 100.0
    for i in range(length):
        if i < length - 25:
            price += trend * 0.3
        else:
            price -= trend * 0.08
        high = price + 0.6
        low = price - 0.6
        close = price + (0.1 if i % 2 == 0 else -0.05)
        volume = 100 + (i % 7) * 4
        if i >= length - 10:
            volume = 70 + (i % 3) * 2
        if i == length - 1:
            volume = 140
            high += 0.4
        rows.append(
            {
                "timestamp": 1_700_000_000_000 + i * 900_000,
                "open": price - 0.2,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
    return pd.DataFrame(rows)


class ChartPatternShadowTests(unittest.TestCase):
    def test_build_chart_pattern_shadow_returns_wrapper(self) -> None:
        df = _sample_df()
        swings = detect_swings(df, 2)
        cfg = SimpleNamespace(
            WINDOW_MACRO_4H_BARS=240,
            WINDOW_STRUCTURE_1H_BARS=120,
            WINDOW_TRIGGER_15M_BARS=24,
            WINDOW_MICRO_15M_BARS=96,
            PATTERN_FLAG_IMPULSE_ATR_MIN=2.2,
            PATTERN_FLAG_PULLBACK_MIN_RATIO=0.25,
            PATTERN_FLAG_PULLBACK_MAX_RATIO=0.55,
            PATTERN_CONSOLIDATION_BARS_MIN=6,
            PATTERN_CONSOLIDATION_BARS_MAX=20,
            PATTERN_CONTRACTION_RATIO_MAX=0.85,
            PATTERN_EXPANSION_RATIO_MIN=1.15,
            PATTERN_TRIANGLE_FLAT_VARIANCE_ATR_MAX=0.35,
            PATTERN_TRIANGLE_STEP_ATR_MIN=0.15,
            PATTERN_FAILED_BREAKOUT_RETURN_BARS=4,
            PATTERN_FAILED_BREAKOUT_EXCESS_ATR_MIN=0.15,
            PATTERN_FAILED_BREAKOUT_WICK_RATIO_MIN=0.35,
        )
        zones = [
            {"low": 120.0, "high": 121.0, "strength": 6, "source": "4h", "distance_from_price": 2.0},
            {"low": 118.5, "high": 119.2, "strength": 4, "source": "1h", "distance_from_price": 0.5},
            {"low": 117.8, "high": 118.1, "strength": 2, "source": "15m", "distance_from_price": 0.2},
        ]
        result = build_chart_pattern_shadow(
            price=float(df["close"].iloc[-1]),
            atr=1.0,
            df_15m=df,
            swings_15m=swings,
            breakout_up=True,
            breakout_down=False,
            support_zones_all=zones,
            resistance_zones_all=zones,
            raw_missing_fields=["orderbook_bids", "orderbook_asks"],
            cfg=cfg,
        )

        shadow = result["chart_pattern_shadow"]
        self.assertEqual(shadow["version"], "v1")
        self.assertIn("pattern_context", shadow)
        self.assertIn("window_context", shadow)
        self.assertIn("volume_structure", shadow)
        self.assertIn("sr_context", shadow)
        self.assertIn("fallback_context", shadow)
        self.assertEqual(shadow["fallback_context"]["mode"], "price_only_partial")

    def test_run_cycle_keeps_shadow_out_of_ai_payloads(self) -> None:
        required_env = {
            "OPENAI_API_KEY": "x",
            "SMTP_HOST": "smtp",
            "SMTP_PORT": "587",
            "SMTP_USER": "u",
            "SMTP_PASSWORD": "p",
            "MAIL_FROM": "a@example.com",
            "MAIL_TO": "b@example.com",
        }
        df = _sample_df()
        captured: dict[str, object] = {}

        def _capture_advice(**kwargs: object) -> tuple[dict[str, object], str]:
            captured["advice_payload"] = kwargs["machine_payload"]
            return (
                {
                    "decision": "LONG",
                    "quality": "B",
                    "confidence": 0.7,
                    "notes": "stub",
                },
                "api",
            )

        def _capture_summary(**kwargs: object) -> tuple[str, str]:
            captured["summary_payload"] = kwargs["result_payload"]
            return ("summary body", "api")

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, required_env, clear=False):
                cfg = load_config(Path(tmp_dir))
            with patch("main.get_server_time_ms", return_value=1_700_000_000_000), patch(
                "main.fetch_klines", side_effect=[df, df, df]
            ), patch("main.validate_klines", return_value=True), patch(
                "main.fetch_market_structure", return_value=MarketStructureSnapshot(missing_fields=[])
            ), patch("main.fetch_funding_rate", return_value=0.0), patch(
                "main.resend_pending_email", return_value=None
            ), patch("main.cleanup_if_due", return_value=None), patch(
                "main.request_ai_advice", side_effect=_capture_advice
            ), patch(
                "main.build_summary_body", side_effect=_capture_summary
            ), patch(
                "main.should_notify",
                return_value={
                    "notify": False,
                    "notify_reason_codes": [],
                    "suppress_reason_codes": ["no_material_change"],
                    "notification_kind": "none",
                },
            ), patch("main.append_trade_log", return_value=Path(tmp_dir) / "logs" / "csv" / "trades.csv"), patch(
                "main.save_signal_snapshot", return_value=Path(tmp_dir) / "logs" / "signals" / "x.json"
            ), patch("main.save_json", return_value=None):
                result = run_cycle(cfg=cfg, base_dir=Path(tmp_dir))

        self.assertIn("chart_pattern_shadow", result)
        self.assertNotIn("chart_pattern_shadow", captured["advice_payload"])
        self.assertNotIn("chart_pattern_shadow", captured["summary_payload"])


if __name__ == "__main__":
    unittest.main()
