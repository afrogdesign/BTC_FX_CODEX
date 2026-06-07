import unittest

from src.trade.active_plan import (
    build_active_trade_plan,
    classify_zone_position,
    rr_for_entry,
)


class ActiveTradePlanTests(unittest.TestCase):
    def _long_setup(self) -> dict[str, object]:
        return {
            "entry_zone": {"low": 60322.42, "high": 60524.08},
            "entry_mid": 60423.25,
            "stop_loss": 60025.57,
            "tp1": 60940.23,
            "tp2": 61377.68,
            "status": "watch",
        }

    def _short_setup(self) -> dict[str, object]:
        return {
            "entry_zone": {"low": 60680.82, "high": 60882.88},
            "entry_mid": 60781.85,
            "stop_loss": 61179.73,
            "tp1": 60264.61,
            "tp2": 59826.94,
            "status": "invalid",
        }

    def test_classify_zone_position(self) -> None:
        self.assertEqual(classify_zone_position("long", 100.0, 90.0, 110.0), "inside_zone")
        self.assertEqual(classify_zone_position("long", 80.0, 90.0, 110.0), "below_zone")
        self.assertEqual(classify_zone_position("long", 120.0, 90.0, 110.0), "above_zone")
        self.assertEqual(classify_zone_position("short", 100.0, 90.0, 110.0), "inside_zone")
        self.assertEqual(classify_zone_position("none", 100.0, 90.0, 110.0), "unknown")
        self.assertEqual(classify_zone_position("long", 0.0, 90.0, 110.0), "unknown")

    def test_rr_for_entry_long_and_short(self) -> None:
        self.assertEqual(rr_for_entry("long", 100.0, 90.0, 120.0), 2.0)
        self.assertEqual(rr_for_entry("short", 100.0, 110.0, 80.0), 2.0)
        self.assertIsNone(rr_for_entry("long", 100.0, 110.0, 120.0))
        self.assertIsNone(rr_for_entry("short", 100.0, 90.0, 80.0))
        self.assertIsNone(rr_for_entry("none", 100.0, 90.0, 120.0))

    def test_20260606_230500_limit_short_and_counter_long(self) -> None:
        plan = build_active_trade_plan(
            current_price=60513.0,
            bias="short",
            market_regime="range",
            long_setup=self._long_setup(),
            short_setup=self._short_setup(),
            confidence_direction_shadow=72.0,
            confidence_execution_shadow=18.0,
            confidence_wait_shadow=59.2,
            risk_flags=["short_into_major_support", "short_at_major_support_wait_only"],
            market_map_flags=["support_to_resistance_flip", "major_resistance_rejection", "trend_flip_early_down"],
            no_trade_flags=[],
            data_quality_flag="ok",
            breakout_up=False,
            breakout_down=False,
            volume_ratio=1.0,
            trigger_volume_ratio_threshold=1.5,
        )

        self.assertIn("ACTIVE_LIMIT_RETEST", plan["primary_action"])
        self.assertIn("ACTIVE_COUNTER_SCALP", plan["primary_action"])
        self.assertEqual(plan["side_plans"]["short"]["market_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["short"]["limit_entry_status"], "allowed")
        self.assertEqual(plan["side_plans"]["long"]["counter_scalp_status"], "conditional")
        self.assertIn("成行ショート不可", plan["headline"])
        self.assertIn("戻り売り待ち", plan["headline"])
        self.assertIn("短期反発帯", plan["headline"])

    def test_short_market_allowed_when_inside_zone_and_rr_ok(self) -> None:
        plan = build_active_trade_plan(
            current_price=60750.0,
            bias="short",
            market_regime="range",
            long_setup=self._long_setup(),
            short_setup=self._short_setup(),
            confidence_direction_shadow=72.0,
            confidence_execution_shadow=30.0,
            confidence_wait_shadow=30.0,
            risk_flags=[],
            market_map_flags=["support_to_resistance_flip"],
            no_trade_flags=[],
            data_quality_flag="ok",
            breakout_up=False,
            breakout_down=False,
            volume_ratio=1.0,
            trigger_volume_ratio_threshold=1.5,
        )

        self.assertEqual(plan["side_plans"]["short"]["market_entry_status"], "allowed")
        self.assertEqual(plan["primary_action"], "ACTIVE_MARKET_SMALL")

    def test_data_quality_not_ok_returns_no_action(self) -> None:
        plan = build_active_trade_plan(
            current_price=60750.0,
            bias="short",
            market_regime="range",
            long_setup=self._long_setup(),
            short_setup=self._short_setup(),
            confidence_direction_shadow=72.0,
            confidence_execution_shadow=30.0,
            confidence_wait_shadow=30.0,
            risk_flags=[],
            market_map_flags=["support_to_resistance_flip"],
            no_trade_flags=[],
            data_quality_flag="partial_missing",
            breakout_up=False,
            breakout_down=False,
            volume_ratio=1.0,
            trigger_volume_ratio_threshold=1.5,
        )

        self.assertEqual(plan["primary_action"], "NO_ACTION")
        self.assertEqual(plan["side_plans"]["long"]["market_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["short"]["market_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["long"]["limit_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["short"]["limit_entry_status"], "blocked")

    def test_fatal_no_trade_blocks_all_entries(self) -> None:
        plan = build_active_trade_plan(
            current_price=60750.0,
            bias="short",
            market_regime="range",
            long_setup=self._long_setup(),
            short_setup=self._short_setup(),
            confidence_direction_shadow=72.0,
            confidence_execution_shadow=30.0,
            confidence_wait_shadow=30.0,
            risk_flags=[],
            market_map_flags=["support_to_resistance_flip"],
            no_trade_flags=["ATR_extreme"],
            data_quality_flag="ok",
            breakout_up=False,
            breakout_down=False,
            volume_ratio=1.0,
            trigger_volume_ratio_threshold=1.5,
        )

        self.assertEqual(plan["primary_action"], "NO_ACTION")
        self.assertEqual(plan["side_plans"]["long"]["market_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["short"]["market_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["long"]["limit_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["short"]["limit_entry_status"], "blocked")
        self.assertEqual(plan["side_plans"]["long"]["counter_scalp_status"], "blocked")
        self.assertEqual(plan["side_plans"]["short"]["counter_scalp_status"], "blocked")

    def test_trend_flip_up_blocks_short_market_but_not_short_limit(self) -> None:
        plan = build_active_trade_plan(
            current_price=60750.0,
            bias="short",
            market_regime="range",
            long_setup=self._long_setup(),
            short_setup=self._short_setup(),
            confidence_direction_shadow=72.0,
            confidence_execution_shadow=30.0,
            confidence_wait_shadow=30.0,
            risk_flags=[],
            market_map_flags=["trend_flip_confirmed_up"],
            no_trade_flags=[],
            data_quality_flag="ok",
            breakout_up=False,
            breakout_down=False,
            volume_ratio=1.0,
            trigger_volume_ratio_threshold=1.5,
        )

        self.assertEqual(plan["side_plans"]["short"]["market_entry_status"], "blocked")
        self.assertIn("short_market_warning_trend_flip_up", plan["side_plans"]["short"]["blockers"])
        self.assertEqual(plan["side_plans"]["short"]["limit_entry_status"], "allowed")


if __name__ == "__main__":
    unittest.main()
