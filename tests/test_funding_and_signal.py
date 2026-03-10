from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.funding import format_funding_pct, funding_rate_label, funding_rate_raw_to_pct
from src.analysis.signal_tier import compute_signal_tier


class FundingAndSignalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = SimpleNamespace(CONFIDENCE_LONG_MIN=65, CONFIDENCE_SHORT_MIN=70)

    def test_funding_rate_conversion_and_label(self) -> None:
        pct = funding_rate_raw_to_pct(0.000037)
        self.assertAlmostEqual(pct, 0.0037, places=6)
        self.assertEqual(format_funding_pct(pct), "+0.0037%")
        label = funding_rate_label(
            funding_rate_pct=pct,
            long_warning_pct=0.05,
            long_prohibited_pct=0.08,
            short_warning_pct=-0.03,
            short_prohibited_pct=-0.05,
        )
        self.assertEqual(label, "ほぼ中立")

    def test_signal_tier_machine_and_ai_confirmed(self) -> None:
        base_result = {
            "bias": "long",
            "prelabel": "ENTRY_OK",
            "primary_setup_status": "ready",
            "confidence": 80,
            "rr_estimate": 2.1,
            "no_trade_flags": [],
            "risk_flags": [],
            "warning_flags": [],
            "agreement_with_machine": "agree",
        }
        self.assertEqual(compute_signal_tier(base_result, self.cfg), "strong_machine")

        ai_confirmed = dict(base_result)
        ai_confirmed["ai_advice"] = {"decision": "LONG", "confidence": 0.75, "quality": "A"}
        self.assertEqual(compute_signal_tier(ai_confirmed, self.cfg), "strong_ai_confirmed")

        not_strong = dict(base_result)
        not_strong["prelabel"] = "SWEEP_WAIT"
        self.assertEqual(compute_signal_tier(not_strong, self.cfg), "normal")


if __name__ == "__main__":
    unittest.main()

