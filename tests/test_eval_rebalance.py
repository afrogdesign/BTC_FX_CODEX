from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import types
from unittest.mock import patch
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


class _MiniSeries(list):
    def tolist(self) -> list[float]:
        return list(self)

    def max(self) -> float:
        return max(float(value) for value in self)

    def min(self) -> float:
        return min(float(value) for value in self)


class _MiniILoc:
    def __init__(self, rows: list[dict[str, float]]) -> None:
        self._rows = rows

    def __getitem__(self, key: object) -> object:
        if isinstance(key, slice):
            return _MiniDataFrame(self._rows[key])
        return self._rows[int(key)]


class _MiniDataFrame:
    def __init__(self, rows: list[dict[str, float]]) -> None:
        self._rows = [dict(row) for row in rows]
        self.iloc = _MiniILoc(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    @property
    def empty(self) -> bool:
        return not self._rows

    def __getitem__(self, key: str) -> _MiniSeries:
        return _MiniSeries(row[key] for row in self._rows)

    def head(self, n: int) -> "_MiniDataFrame":
        return _MiniDataFrame(self._rows[:n])

    def copy(self) -> "_MiniDataFrame":
        return _MiniDataFrame(self._rows)

    def itertuples(self, index: bool = False) -> object:
        for row in self._rows:
            yield SimpleNamespace(**row)


sys.modules.setdefault("pandas", types.SimpleNamespace(DataFrame=_MiniDataFrame))

from backtest.evaluator import evaluate_signals, summarize_evaluated_signals
from config import load_config
from src.analysis.breakout import previous_breakout_levels
from src.analysis.confidence import compute_confidence
from src.analysis.position_risk import evaluate_position_risk
from src.analysis.rr import build_setup
from src.analysis.scoring import compute_scores


class EvalRebalanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = SimpleNamespace(
            LONG_SHORT_DIFF_THRESHOLD=8,
            SHORT_LONG_DIFF_THRESHOLD=9,
            CONFIDENCE_LONG_MIN=45,
            CONFIDENCE_SHORT_MIN=55,
            MIN_RR_RATIO=1.10,
            MIN_ACCEPTABLE_ATR_RATIO=0.25,
            MAX_ACCEPTABLE_ATR_RATIO=2.4,
            FUNDING_SHORT_WARNING=-0.04,
            FUNDING_SHORT_PROHIBITED=-0.07,
            FUNDING_LONG_WARNING=0.06,
            FUNDING_LONG_PROHIBITED=0.10,
            POSITION_RISK_HIGH_THRESHOLD=80.0,
            POSITION_RISK_MEDIUM_THRESHOLD=55.0,
            TRIGGER_VOLUME_RATIO=1.15,
            BREAKOUT_LOOKBACK_BARS=20,
            SL_ATR_MULTIPLIER=1.5,
        )

    def test_breakout_levels_exclude_current_bar(self) -> None:
        df = _MiniDataFrame(
            [{"high": 100.0, "low": 90.0} for _ in range(20)] + [{"high": 120.0, "low": 80.0}]
        )
        recent_high, recent_low = previous_breakout_levels(df, 20)
        self.assertEqual(recent_high, 100.0)
        self.assertEqual(recent_low, 90.0)

    def test_funding_warning_hits_raw_score(self) -> None:
        base_inputs = {
            "market_regime": "uptrend",
            "ema_alignment_4h": "bullish",
            "ema20_slope_4h": "up",
            "structure_4h": "hh_hl",
            "structure_1h": "hh_hl",
            "price": 100.0,
            "ema50_4h": 95.0,
            "rsi_15m": 50.0,
            "volume_ratio": 1.20,
            "atr_ratio": 1.0,
            "rr_long": 1.5,
            "rr_short": 1.5,
            "near_support": True,
            "near_resistance": False,
            "breakout_up": True,
            "breakout_down": False,
            "in_range_center": False,
            "transition_direction": "up",
            "signals_15m": "long",
        }
        control = compute_scores(
            {
                **base_inputs,
                "funding_rate": 0.0,
            },
            self.cfg,
        )
        result = compute_scores(
            {
                **base_inputs,
                "funding_rate": 0.07,
            },
            self.cfg,
        )
        self.assertIn("Funding_warning_long", result["warning_flags"])
        self.assertEqual(control["long_raw_score"] - result["long_raw_score"], 4.0)

    def test_confidence_uses_major_minor_warning_budget(self) -> None:
        base_inputs = {
            "bias": "short",
            "long_display_score": 40,
            "short_display_score": 70,
            "signals_4h": "short",
            "signals_1h": "short",
            "signals_15m": "short",
            "market_regime": "downtrend",
            "phase": "breakout",
            "rr_estimate": 1.15,
            "opposite_gap_atr": 1.0,
            "critical_zone": False,
        }
        control = compute_confidence(
            {
                **base_inputs,
                "score_warning_flags": [],
                "position_risk_flags": [],
            },
            self.cfg,
        )
        confidence = compute_confidence(
            {
                **base_inputs,
                "score_warning_flags": ["Funding_warning_short"],
                "position_risk_flags": ["bid_wall_close", "sweep_incomplete"],
            },
            self.cfg,
        )
        self.assertEqual(control - confidence, 9)

    def test_warning_gate_and_near_zone_ready(self) -> None:
        support_zones = [{"low": 99.0, "high": 100.0}]
        resistance_zones = [{"low": 103.0, "high": 104.0}]
        setup, _ = build_setup(
            side="long",
            price=100.04,
            atr=1.0,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            sl_atr_multiplier=1.5,
            min_rr_ratio=1.0,
            confidence=80,
            confidence_min=45,
            atr_ratio=1.0,
            atr_ratio_min=0.25,
            atr_ratio_max=2.4,
            funding_rate=0.0,
            funding_warning=999.0,
            funding_prohibited=999.0,
            trigger_ready=True,
            warning_count=2,
        )
        self.assertEqual(setup["status"], "ready")
        self.assertEqual(setup["status_reason_code"], "near_entry_zone_with_trigger")

        invalid_setup, _ = build_setup(
            side="long",
            price=100.04,
            atr=1.0,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            sl_atr_multiplier=1.5,
            min_rr_ratio=1.0,
            confidence=80,
            confidence_min=45,
            atr_ratio=1.0,
            atr_ratio_min=0.25,
            atr_ratio_max=2.4,
            funding_rate=0.0,
            funding_warning=999.0,
            funding_prohibited=999.0,
            trigger_ready=True,
            warning_count=3,
        )
        self.assertEqual(invalid_setup["status"], "invalid")

    def test_position_risk_directional_liquidation(self) -> None:
        common = {
            "atr": 10.0,
            "liquidity_info": {"liquidity_above": None, "liquidity_below": None, "liquidity_swept_recently": True},
            "oi_cvd_info": {"oi_state": None, "cvd_price_divergence": None},
            "orderbook_info": {"orderbook_bid_wall_price": None, "orderbook_ask_wall_price": None, "orderbook_bias": None},
            "high_threshold": 80.0,
            "medium_threshold": 55.0,
        }
        strong = evaluate_position_risk(
            bias="long",
            price=100.0,
            liquidation_info={"largest_liquidation_price": 95.0},
            **common,
        )
        weak = evaluate_position_risk(
            bias="long",
            price=100.0,
            liquidation_info={"largest_liquidation_price": 105.0},
            **common,
        )
        self.assertGreater(strong["location_risk"], weak["location_risk"])

    def test_backtest_fill_and_missed_opportunity_summary(self) -> None:
        signal = {
            "timestamp": 1,
            "price": 100.0,
            "bias": "long",
            "phase": "breakout",
            "confidence": 80,
            "market_regime": "uptrend",
            "long_display_score": 70,
            "short_display_score": 40,
            "score_gap": 30,
            "primary_setup_side": "long",
            "primary_setup_status": "ready",
            "long_setup": {
                "status": "ready",
                "entry_zone": {"low": 99.5, "high": 100.5},
                "entry_mid": 100.0,
                "stop_loss": 99.0,
                "tp1": 101.0,
                "tp2": 102.0,
            },
            "short_setup": {"status": "watch"},
            "profile": "rebalanced",
        }
        filled_df = _MiniDataFrame(
            [
                {"timestamp": 1, "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0},
                {"timestamp": 2, "open": 100.0, "high": 100.4, "low": 99.8, "close": 100.2, "volume": 1.0},
                {"timestamp": 3, "open": 100.2, "high": 101.1, "low": 100.1, "close": 101.0, "volume": 1.0},
                {"timestamp": 4, "open": 101.0, "high": 102.1, "low": 100.8, "close": 102.0, "volume": 1.0},
            ]
        )
        evaluated = evaluate_signals([signal], filled_df)
        self.assertTrue(evaluated[0]["filled"])
        self.assertEqual(evaluated[0]["result"], "tp2")

        missed_df = _MiniDataFrame(
            [
                {"timestamp": 1, "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0},
                {"timestamp": 2, "open": 101.2, "high": 101.4, "low": 101.1, "close": 101.3, "volume": 1.0},
                {"timestamp": 3, "open": 101.4, "high": 101.8, "low": 101.3, "close": 101.7, "volume": 1.0},
            ]
        )
        missed_eval = evaluate_signals([signal], missed_df)
        self.assertFalse(missed_eval[0]["filled"])
        self.assertTrue(missed_eval[0]["missed_opportunity"])

        summary = summarize_evaluated_signals(evaluated + missed_eval, "rebalanced")
        self.assertEqual(summary["ready_signals"], 2)
        self.assertEqual(summary["filled_trades"], 1)
        self.assertEqual(summary["missed_ready_trades"], 1)
        self.assertEqual(summary["missed_opportunity_count"], 1)

    def test_config_defaults_and_baseline_profile(self) -> None:
        required_env = {
            "OPENAI_API_KEY": "x",
            "SMTP_HOST": "smtp",
            "SMTP_PORT": "587",
            "SMTP_USER": "u",
            "SMTP_PASSWORD": "p",
            "MAIL_FROM": "a@example.com",
            "MAIL_TO": "b@example.com",
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, required_env, clear=False):
                cfg = load_config(Path(tmp_dir))
        self.assertEqual(cfg.BREAKOUT_LOOKBACK_BARS, 20)
        self.assertAlmostEqual(cfg.TRIGGER_VOLUME_RATIO, 1.15)
        self.assertEqual(cfg.SHORT_LONG_DIFF_THRESHOLD, 9)


if __name__ == "__main__":
    unittest.main()
