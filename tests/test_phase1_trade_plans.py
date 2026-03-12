from __future__ import annotations

import unittest

from src.trade.exit_manager import build_exit_plan
from src.trade.position_sizing import build_position_size_plan


class Phase1TradePlanTests(unittest.TestCase):
    def test_position_sizing_applies_loss_streak_reduction_and_cap(self) -> None:
        plan = build_position_size_plan(
            account_balance=10000,
            entry_price=70000,
            stop_loss_price=69500,
            signal_tier="strong",
            loss_streak=2,
            base_risk_pct=0.5,
            loss_streak_step_pct=0.1,
            min_risk_pct=0.2,
            max_position_size_usd=3000,
        )

        self.assertEqual(plan["risk_percent_applied"], 0.3)
        self.assertEqual(plan["planned_risk_usd"], 30.0)
        self.assertEqual(plan["position_size_usd"], 3000.0)
        self.assertTrue(plan["max_size_capped"])
        self.assertIn("strong_tier_kept_flat", plan["size_reduction_reasons"])
        self.assertIn("loss_streak_risk_reduced", plan["size_reduction_reasons"])

    def test_exit_plan_builds_prices_from_r_multiple(self) -> None:
        plan = build_exit_plan(
            side="long",
            entry_price=70000,
            stop_loss_price=69500,
            atr=180,
            tp1_rr_multiple=1.0,
            tp2_rr_multiple=2.0,
            trail_atr_multiplier=1.5,
            timeout_hours=12,
            exit_rule_version="phase1_v0",
        )

        self.assertEqual(plan["tp1_price"], 70500.0)
        self.assertEqual(plan["tp2_price"], 71000.0)
        self.assertTrue(plan["breakeven_after_tp1"])
        self.assertEqual(plan["trail_atr_multiplier"], 1.5)
        self.assertEqual(plan["timeout_hours"], 12)


if __name__ == "__main__":
    unittest.main()
