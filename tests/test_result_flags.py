from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.result_flags import assemble_result_flags, derive_additional_risk_flags


class ResultFlagsTest(unittest.TestCase):
    def test_position_risk_is_not_promoted_into_no_trade_flags(self) -> None:
        result = assemble_result_flags(
            bias="short",
            score_no_trade_flags=["RR_insufficient_short"],
            score_warning_flags=["ATR_warning"],
            long_setup_flags=["RR_insufficient"],
            short_setup_flags=["Funding_warning"],
            position_risk_flags=["upper_liquidity_close", "bid_wall_close"],
            critical_zone=True,
        )

        self.assertEqual(result["no_trade_flags"], ["RR_insufficient_short", "Funding_warning"])
        self.assertEqual(result["risk_flags"], ["upper_liquidity_close", "bid_wall_close"])
        self.assertEqual(result["warning_flags"], ["ATR_warning", "Critical_zone_warning"])

    def test_wait_bias_keeps_only_score_level_blockers_at_top_level(self) -> None:
        result = assemble_result_flags(
            bias="wait",
            score_no_trade_flags=["volatile_regime"],
            score_warning_flags=[],
            long_setup_flags=["RR_insufficient"],
            short_setup_flags=["Funding_prohibited"],
            position_risk_flags=["upper_liquidity_close"],
            critical_zone=False,
        )

        self.assertEqual(result["no_trade_flags"], ["volatile_regime"])
        self.assertEqual(result["risk_flags"], ["upper_liquidity_close"])

    def test_market_map_flags_are_promoted_to_risk_flags(self) -> None:
        result = derive_additional_risk_flags(
            bias="long",
            market_regime="uptrend",
            transition_direction="up",
            primary_setup_status="watch",
            primary_setup_reason="entry_zone_not_reached",
            risk_flags=[],
            long_factor_breakdown={},
            market_map_flags=["failed_breakout_down_reversal"],
        )

        self.assertIn("failed_breakout_down_reversal", result)
        self.assertIn("long_reversal_risk", result)


if __name__ == "__main__":
    unittest.main()
