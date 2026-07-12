from __future__ import annotations

import unittest

from main import _attach_side_aware_mtf_action, _attach_structural_priority


class StructuralPriorityIntegrationTests(unittest.TestCase):
    def test_canonical_attachment_is_report_only(self):
        result = {
            "long_display_score": 0,
            "short_display_score": 68,
            "score_factor_breakdown_long": {"ema20_slope_up": 6, "price_above_ema50_4h": 6},
            "score_factor_breakdown_short": {"structure_1h_lh_ll": 12},
            "bias": "short",
            "side_aware_mtf_action": {"execution_context": {"primary_side": "short", "primary_action_class": "B_CHECK_15M"}},
        }
        _attach_structural_priority(result)
        self.assertEqual(result["structural_priority"]["long_points"], 47)
        self.assertEqual(result["structural_priority"]["short_points"], 53)
        self.assertEqual(result["long_display_score"], 0)
        self.assertEqual(result["short_display_score"], 68)

    def test_side_aware_is_attached_before_structural_and_context_is_populated(self):
        result = {
            "signal_id": "integration",
            "bias": "short",
            "long_display_score": 0,
            "short_display_score": 68,
            "score_factor_breakdown_long": {"ema20_slope_up": 6, "price_above_ema50_4h": 6},
            "score_factor_breakdown_short": {"structure_1h_lh_ll": 12},
            "signals_4h": "wait", "signals_1h": "wait", "signals_15m": "wait",
            "trade_execution_gate": "blocked",
        }
        _attach_side_aware_mtf_action(result, previous=None)
        self.assertIn("side_aware_mtf_action", result)
        _attach_structural_priority(result)
        structural = result["structural_priority"]
        self.assertEqual(structural["tactical_context"]["primary_side"], result["side_aware_mtf_action"]["execution_context"]["primary_side"])
        self.assertEqual(structural["tactical_context"]["primary_action_class"], result["side_aware_mtf_action"]["execution_context"]["primary_action_class"])
        self.assertEqual(result["bias"], "short")
        self.assertEqual((result["long_display_score"], result["short_display_score"]), (0, 68))
        self.assertEqual(result["trade_execution_gate"], "blocked")


if __name__ == "__main__":
    unittest.main()
