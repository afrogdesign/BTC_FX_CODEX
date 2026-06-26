from __future__ import annotations

import unittest

from src.trade.opportunity_gate import determine_opportunity_gate


class OpportunityGateTests(unittest.TestCase):
    def test_formal_candidate_with_hard_quality_reason_is_blocked(self) -> None:
        result = determine_opportunity_gate(
            bias="short",
            primary_setup_side="short",
            primary_setup_status="ready",
            primary_setup_reason="ready",
            data_quality_flag="ok",
            no_trade_flags=[],
            risk_flags=[],
            market_map_flags=[],
            phase1_observation_gate="blocked",
            phase1_observation_type="",
            phase1b_lite_gate="blocked",
            phase1b_lite_type="",
            trade_execution_gate="pass",
            confidence_direction_shadow=70,
            confidence_execution_shadow=20,
            confidence_wait_shadow=65,
        )

        self.assertEqual(result["opportunity_gate"], "blocked")
        self.assertEqual(result["opportunity_type"], "blocked")
        self.assertIn("require_execution_for_high_wait", result["opportunity_reasons"])
        self.assertNotIn("trade_execution_gate_pass", result["opportunity_reasons"])

    def test_formal_candidate_with_soft_quality_reason_remains_pass_with_conflict_reason(self) -> None:
        result = determine_opportunity_gate(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="ready",
            primary_setup_reason="ready",
            data_quality_flag="ok",
            no_trade_flags=[],
            risk_flags=[],
            market_map_flags=[],
            phase1_observation_gate="blocked",
            phase1_observation_type="",
            phase1b_lite_gate="blocked",
            phase1b_lite_type="",
            trade_execution_gate="pass",
            confidence_direction_shadow=70,
            confidence_execution_shadow=30,
            confidence_wait_shadow=65,
        )

        self.assertEqual(result["opportunity_gate"], "pass")
        self.assertEqual(result["opportunity_type"], "formal_execution_candidate")
        self.assertIn("trade_execution_gate_pass", result["opportunity_reasons"])
        self.assertIn(
            "formal_candidate_quality_conflict:soft_risk:suppress_long_high_wait",
            result["opportunity_reasons"],
        )

    def test_non_formal_candidate_with_hard_quality_reason_stays_blocked(self) -> None:
        result = determine_opportunity_gate(
            bias="short",
            primary_setup_side="short",
            primary_setup_status="watch",
            primary_setup_reason="entry_zone_not_reached",
            data_quality_flag="ok",
            no_trade_flags=[],
            risk_flags=["support_to_resistance_flip"],
            market_map_flags=["support_to_resistance_flip"],
            phase1_observation_gate="blocked",
            phase1_observation_type="",
            phase1b_lite_gate="blocked",
            phase1b_lite_type="",
            trade_execution_gate="blocked",
            confidence_direction_shadow=70,
            confidence_execution_shadow=20,
            confidence_wait_shadow=65,
        )

        self.assertEqual(result["opportunity_gate"], "blocked")
        self.assertEqual(result["opportunity_type"], "blocked")
        self.assertIn("require_execution_for_high_wait", result["opportunity_reasons"])


if __name__ == "__main__":
    unittest.main()
