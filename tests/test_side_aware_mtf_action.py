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
        current = payload(); current["primary_setup_side"] = "short"; current["primary_setup_status"] = "invalid"
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["short"]["action_class"], "STOP_OR_EXIT")
        self.assertEqual(result["long"]["action_class"], "B_CHECK_15M")

    def test_both_sides_watch_without_activation(self) -> None:
        current = payload(); current["primary_setup_status"] = "watch"; current["primary_setup_side"] = ""; current["signals_1h"] = "wait"; current["signals_15m"] = "wait"; current["transition_direction"] = ""
        result = evaluate_side_aware_mtf_action(current)
        self.assertEqual(result["long"]["action_class"], "C_WATCH_ZONE")
        self.assertEqual(result["short"]["action_class"], "C_WATCH_ZONE")

    def test_formal_a_is_preserved(self) -> None:
        current = payload(); current["trade_execution_gate"] = "pass"; current["primary_setup_status"] = "ready"; current["active_trade_plan"]["side_plans"]["long"]["market_entry_status"] = "allowed"
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


if __name__ == "__main__":
    unittest.main()
