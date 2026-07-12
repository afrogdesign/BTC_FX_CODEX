from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.analysis.side_aware_mtf_action import evaluate_side_aware_mtf_action


ROOT = Path(__file__).resolve().parents[1]


def payload() -> dict:
    return json.loads((ROOT / "logs/signals/20260712_040500.json").read_text())


class SideAwareMtfActionTests(unittest.TestCase):
    def test_pinned_long_stop_short_armed(self) -> None:
        result = evaluate_side_aware_mtf_action(payload())
        self.assertEqual(result["long"]["action_class"], "STOP_OR_EXIT")
        self.assertEqual(result["short"]["action_class"], "B_CHECK_15M")
        self.assertEqual(result["short"]["state"], "armed")
        self.assertEqual(result["execution_context"]["primary_side"], "short")
        self.assertEqual(result["execution_context"]["chase_status"], "not_late")

    def test_mirrored_short_stop_long_armed(self) -> None:
        current = payload(); current["primary_setup_side"] = "short"; current["primary_setup_status"] = "invalid"; current["primary_setup_reason"] = "thesis_invalidated"; current["active_trade_plan"]["side_plans"]["long"]["counter_scalp_status"] = "conditional"
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["short"]["action_class"], "STOP_OR_EXIT")
        self.assertEqual(result["long"]["action_class"], "B_CHECK_15M")

    def test_both_sides_watch_without_activation(self) -> None:
        current = payload(); current["primary_setup_status"] = "watch"; current["primary_setup_side"] = ""; current["signals_1h"] = "wait"; current["signals_15m"] = "wait"; current["transition_direction"] = ""; current["market_map_primary_state"] = ""; current["trend_flip_state"] = ""; current["level_flip_state"] = ""; current["failed_breakout_state"] = ""; current["market_map_flags"] = []; current["risk_flags"] = []; current["no_trade_flags"] = []; current["active_trade_plan"]["side_plans"]["long"]["zone_position"] = "outside_zone"; current["active_trade_plan"]["side_plans"]["short"]["zone_position"] = "outside_zone"
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["long"]["action_class"], "C_WATCH_ZONE")
        self.assertEqual(result["short"]["action_class"], "C_WATCH_ZONE")

    def test_formal_a_is_preserved(self) -> None:
        current = payload(); current["trade_execution_gate"] = "pass"; current["primary_setup_status"] = "ready"; current["active_trade_plan"]["side_plans"]["long"]["market_entry_status"] = "allowed"; current["no_trade_flags"] = []; current["risk_flags"] = []
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["long"]["action_class"], "A_FORMAL")

    def test_global_fatal_stops_both_sides(self) -> None:
        current = payload(); current["risk_flags"] = ["ATR_extreme"]
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["long"]["action_class"], "STOP_OR_EXIT")
        self.assertEqual(result["short"]["action_class"], "STOP_OR_EXIT")

    def test_trigger_follow_through_and_no_chase(self) -> None:
        current = payload(); current["primary_setup_side"] = "long"; current["primary_setup_status"] = "invalid"; current["signals_15m"] = "short"; current["signals_1h"] = "short"
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["short"]["state"], "follow_through")
        moved = json.loads((ROOT / "logs/signals/20260712_050500.json").read_text())
        moved["primary_setup_side"] = "long"; moved["primary_setup_status"] = "invalid"
        self.assertIn(evaluate_side_aware_mtf_action(moved, previous=payload())["short"]["chase_status"], {"late_no_chase", "tp1_reached_no_chase"})

    def test_malformed_plan_fails_closed(self) -> None:
        current = payload(); current["active_trade_plan"] = "{broken"
        result = evaluate_side_aware_mtf_action(current)
        self.assertFalse(result["present"])
        self.assertEqual(result["long"]["action_class"], "NONE")

    def test_readiness_invalidity_does_not_create_opposite_direction(self) -> None:
        current = payload(); current["primary_setup_side"] = "short"; current["primary_setup_status"] = "invalid"; current["primary_setup_reason"] = "confidence_below_min"; current["market_map_flags"] = []; current["transition_direction"] = ""; current["trend_flip_state"] = ""
        result = evaluate_side_aware_mtf_action(current)
        self.assertNotIn("opposite_thesis_invalid", result["long"]["reason_codes"])

    def test_json_flags_and_direction_terms_are_normalized(self) -> None:
        current = payload(); current["market_map_flags"] = '["CONFIRMED_DOWN"]'; current["trend_flip_state"] = "early_down"; current["no_trade_flags"] = '["short_at_major_support_wait_only"]'; current["risk_flags"] = []
        result = evaluate_side_aware_mtf_action(current)
        self.assertIn(result["short"]["action_class"], {"B_CHECK_15M", "C_WATCH_ZONE"})
        self.assertNotEqual(result["short"]["reason_codes"], ["global_fatal"])

    def test_zone_activation_is_independent_evidence(self) -> None:
        current = payload(); current["primary_setup_side"] = ""; current["primary_setup_status"] = "watch"; current["market_map_flags"] = []; current["risk_flags"] = []; current["no_trade_flags"] = []
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["short"]["action_class"], "B_CHECK_15M")
        self.assertIn("zone_plan_activation", result["short"]["reason_codes"])

    def test_previous_opposite_stop_crossing_keeps_late_side_primary(self) -> None:
        current = json.loads((ROOT / "logs/signals/20260712_050500.json").read_text()); previous = payload()
        result = evaluate_side_aware_mtf_action(current, previous=previous)
        self.assertEqual(result["short"]["state"], "late")
        self.assertEqual(result["execution_context"]["primary_side"], "short")
        self.assertIn(result["short"]["chase_status"], {"late_no_chase", "tp1_reached_no_chase"})

    def test_direction_tokens_are_exact_and_semantic(self) -> None:
        current = payload(); current["market_map_flags"] = ["support_to_resistance_confirmed"]; current["market_map_primary_state"] = ""; current["trend_flip_state"] = ""; current["level_flip_state"] = ""; current["failed_breakout_state"] = ""; current["transition_direction"] = ""; current["primary_setup_side"] = ""; current["primary_setup_status"] = "watch"; current["no_trade_flags"] = []; current["risk_flags"] = []; current["active_trade_plan"]["side_plans"]["long"]["zone_position"] = "outside_zone"; current["active_trade_plan"]["side_plans"]["short"]["zone_position"] = "outside_zone"
        result = evaluate_side_aware_mtf_action(current)
        self.assertNotIn("timeframe_or_transition_support", result["long"]["reason_codes"])
        self.assertIn("timeframe_or_transition_support", result["short"]["reason_codes"])

    def test_pipe_and_json_flags_and_wait_only_are_individual(self) -> None:
        current = payload(); current["no_trade_flags"] = '["long_at_major_resistance_wait_only"]|short_at_major_support_wait_only'; current["market_map_flags"] = []
        result = evaluate_side_aware_mtf_action(current)
        self.assertIn("side_wait_only", result["long"]["reason_codes"])
        self.assertIn("side_wait_only", result["short"]["reason_codes"])

    def test_moved_headline_contains_no_chase_instruction(self) -> None:
        current = json.loads((ROOT / "logs/signals/20260712_050500.json").read_text()); previous = payload()
        result = evaluate_side_aware_mtf_action(current, previous=previous)
        self.assertIn("追いかけ禁止", result["execution_context"]["headline"])

    def test_previous_cross_is_triggered_before_late_conversion(self) -> None:
        current = payload(); previous = payload(); current["current_price"] = 64150; previous["current_price"] = 64500; previous["active_trade_plan"]["side_plans"]["long"]["stop_loss"] = 64200
        result = evaluate_side_aware_mtf_action(current, previous=previous)
        self.assertEqual(result["short"]["state"], "triggered")
        self.assertEqual(result["short"]["trigger_strength"], 1)

    def test_wait_only_zone_non_primary_degrades_to_watch(self) -> None:
        current = payload(); current["active_trade_plan"]["side_plans"]["short"]["counter_scalp_status"] = "blocked"; current["primary_setup_side"] = "long"; current["primary_setup_status"] = "watch"; current["no_trade_flags"] = ["short_at_major_support_wait_only"]
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["short"]["action_class"], "C_WATCH_ZONE")

    def test_wait_only_matching_15m_remains_triggered(self) -> None:
        current = payload(); current["signals_15m"] = "short"; current["primary_setup_side"] = "long"; current["primary_setup_status"] = "watch"
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["short"]["action_class"], "B_CHECK_15M")
        self.assertEqual(result["short"]["state"], "triggered")

    def test_wait_only_previous_cross_remains_triggered(self) -> None:
        current = payload(); previous = payload(); current["current_price"] = 64150; previous["current_price"] = 64500; previous["active_trade_plan"]["side_plans"]["long"]["stop_loss"] = 64200
        result = evaluate_side_aware_mtf_action(current, previous=previous)
        self.assertEqual(result["short"]["action_class"], "B_CHECK_15M")
        self.assertEqual(result["short"]["state"], "triggered")

    def test_wait_only_blocker_is_named_side_only(self) -> None:
        current = payload(); current["no_trade_flags"] = ["long_at_major_resistance_wait_only"]; current["active_trade_plan"]["side_plans"]["short"]["counter_scalp_status"] = "blocked"; current["primary_setup_side"] = ""
        result = evaluate_side_aware_mtf_action(current)
        self.assertIn(result["long"]["action_class"], {"STOP_OR_EXIT", "C_WATCH_ZONE"})
        self.assertEqual(result["short"]["action_class"], "B_CHECK_15M")

    def test_fresh_trigger_outranks_late_candidate(self) -> None:
        current = json.loads((ROOT / "logs/signals/20260712_050500.json").read_text()); previous = payload(); current["signals_15m"] = "long"; current["primary_setup_side"] = ""; current["primary_setup_status"] = "watch"; current["no_trade_flags"] = []
        result = evaluate_side_aware_mtf_action(current, previous=previous)
        self.assertEqual(result["short"]["state"], "late")
        self.assertEqual(result["long"]["state"], "triggered")
        self.assertEqual(result["execution_context"]["primary_side"], "long")

    def test_follow_through_outranks_late_candidate(self) -> None:
        current = json.loads((ROOT / "logs/signals/20260712_050500.json").read_text()); previous = payload(); current["signals_15m"] = "long"; current["signals_1h"] = "long"; current["primary_setup_side"] = ""; current["primary_setup_status"] = "watch"; current["no_trade_flags"] = []
        result = evaluate_side_aware_mtf_action(current, previous=previous)
        self.assertEqual(result["long"]["state"], "follow_through")
        self.assertEqual(result["execution_context"]["primary_side"], "long")

    def test_true_thesis_invalidation_arms_supported_opposite(self) -> None:
        current = payload(); current["primary_setup_reason"] = "thesis_invalidated"; current["primary_setup_status"] = "invalid"; current["active_trade_plan"]["side_plans"]["short"]["zone_position"] = "outside_zone"
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["short"]["action_class"], "B_CHECK_15M")
        self.assertIn("opposite_thesis_invalid", result["short"]["reason_codes"])

    def test_fresh_trigger_outranks_late_opposite(self) -> None:
        current = payload(); current["signals_15m"] = "short"; current["signals_1h"] = "wait"; current["primary_setup_side"] = ""
        previous = payload(); previous["current_price"] = 64500
        result = evaluate_side_aware_mtf_action(current, previous=previous)
        self.assertEqual(result["short"]["state"], "triggered")
        self.assertEqual(result["execution_context"]["primary_side"], "short")


if __name__ == "__main__":
    unittest.main()
