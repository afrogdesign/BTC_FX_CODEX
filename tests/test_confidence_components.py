from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import AppConfig
from src.analysis.confidence import compute_confidence, compute_confidence_details


class ConfidenceComponentsTest(unittest.TestCase):
    def test_confidence_details_preserve_main_score(self) -> None:
        cfg = AppConfig(data={"CONFIDENCE_LONG_MIN": 45, "CONFIDENCE_SHORT_MIN": 55})
        inputs = {
            "bias": "short",
            "long_display_score": 48,
            "short_display_score": 74,
            "signals_4h": "short",
            "signals_1h": "short",
            "signals_15m": "wait",
            "market_regime": "downtrend",
            "phase": "pullback",
            "rr_estimate": 1.6,
            "opposite_gap_atr": 1.2,
            "critical_zone": False,
            "score_warning_flags": [],
            "position_risk_flags": ["upper_liquidity_close"],
            "prelabel": "ENTRY_OK",
        }
        details = compute_confidence_details(inputs, cfg)
        self.assertEqual(details["confidence"], compute_confidence(inputs, cfg))
        self.assertTrue(details["confidence_components"])
        self.assertGreater(details["confidence_direction_shadow"], details["confidence_execution_shadow"])

