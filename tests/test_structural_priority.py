from __future__ import annotations

import json
import unittest

from src.analysis.structural_priority import build_structural_priority


def payload(long=None, short=None, **extra):
    return {"score_factor_breakdown_long": long or {}, "score_factor_breakdown_short": short or {}, **extra}


class StructuralPriorityTests(unittest.TestCase):
    def test_full_long_and_short_alignment(self):
        long = {"regime_uptrend": 15, "ema_alignment_bullish": 12, "ema20_slope_up": 6, "price_above_ema50_4h": 6, "structure_4h_hh_hl": 14, "structure_1h_hh_hl": 12}
        short = {"regime_downtrend": 15, "ema_alignment_bearish": 12, "ema20_slope_down": 6, "price_below_ema50_4h": 6, "structure_4h_lh_ll": 14, "structure_1h_lh_ll": 12}
        self.assertEqual(build_structural_priority(payload(long))['long_points'], 90)
        self.assertEqual(build_structural_priority(payload(short=short))['long_points'], 10)

    def test_mixed_and_partial_expected_points(self):
        long = {"regime_uptrend": 15, "ema_alignment_bullish": 12, "ema20_slope_up": 6, "price_above_ema50_4h": 6, "structure_4h_hh_hl": 14}
        short = {"structure_1h_lh_ll": 12}
        self.assertEqual(build_structural_priority(payload(long, short))['long_points'], 70)
        self.assertEqual(build_structural_priority(payload({}, short))['long_points'], 40)
        partial = payload({"ema20_slope_up": 6, "price_above_ema50_4h": 6}, short)
        self.assertEqual(build_structural_priority(partial)['long_points'], 47)

    def test_no_evidence_is_neutral_and_no_tactical_fallback(self):
        out = build_structural_priority({"long_display_score": 0, "short_display_score": 100})
        self.assertFalse(out["present"])
        self.assertEqual((out["long_points"], out["short_points"], out["primary_side"]), (50, 50, ""))
        self.assertIn("insufficient", out["priority_label"])

    def test_serialized_breakdown_and_malformed_input(self):
        out = build_structural_priority(payload(json.dumps({"ema20_slope_up": 6}), "not-json"))
        self.assertTrue(out["present"])
        self.assertEqual(out["components"]["4h"]["long"], 6)

    def test_turning_is_exact_and_symmetric(self):
        out = build_structural_priority(payload({}, {}, market_map_flags=["support_to_resistance_confirmed"]))
        self.assertEqual(out["turning_watch"]["direction"], "short")
        bug = build_structural_priority(payload({}, {}, market_map_flags=["support_to_resistance_confirmed_extra"]))
        self.assertEqual(bug["turning_watch"]["direction"], "none")

    def test_alignment_respects_neutral_band(self):
        out = build_structural_priority(payload({"ema20_slope_up": 6, "price_above_ema50_4h": 6}, {"structure_1h_lh_ll": 12}, side_aware_mtf_action={"execution_context": {"primary_side": "short"}}))
        self.assertEqual(out["long_points"], 47)
        self.assertEqual(out["alignment_state"], "neutral")


if __name__ == "__main__":
    unittest.main()
