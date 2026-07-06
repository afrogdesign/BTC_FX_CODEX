from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.big_chance import build_big_chance_markdown, evaluate_big_chance  # noqa: E402


def _value_defense_layer(
    *,
    side: str,
    shallow_low: float,
    shallow_high: float,
    value_low: float,
    value_high: float,
    invalid_low: float,
    invalid_high: float,
    reclaim: float,
    continuation: float,
    lifecycle_state: str = "invalidated",
) -> dict[str, object]:
    return {
        "schema_version": "value_defense_entry_layer.v1",
        "side": side,
        "lifecycle_state": lifecycle_state,
        "market_entry_status": "report_only",
        "shallow_retest_zone": {"low": shallow_low, "high": shallow_high},
        "shallow_retest_risk": "watch_only",
        "value_defense_zone": {"low": value_low, "high": value_high},
        "defense_zone_basis": "htf_context",
        "invalidation_zone": {"low": invalid_low, "high": invalid_high},
        "reclaim_trigger": reclaim,
        "continuation_trigger": continuation,
        "operator_guidance": "report-only / human decides manually",
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }


def _payload(
    *,
    signal_id: str,
    timestamp_jst: str,
    bias: str,
    current_price: float,
    signals_4h: str,
    signals_1h: str,
    signals_15m: str,
    market_map_primary_state: str,
    market_map_flags: list[str],
    level_flip_state: str,
    trend_flip_state: str,
    failed_breakout_state: str,
    transition_direction: str,
    long_zone: tuple[float, float, float, float, float, float, float, float, str] | None,
    short_zone: tuple[float, float, float, float, float, float, float, float, str] | None,
) -> dict[str, object]:
    long_setup = {
        "status": "watch",
        "entry_zone": {"low": 0, "high": 0},
        "stop_loss": 0,
        "tp1": 0,
        "tp2": 0,
    }
    short_setup = {
        "status": "watch",
        "entry_zone": {"low": 0, "high": 0},
        "stop_loss": 0,
        "tp1": 0,
        "tp2": 0,
    }
    if long_zone is not None:
        long_setup["value_defense_entry_layer"] = _value_defense_layer(
            side="long",
            shallow_low=long_zone[0],
            shallow_high=long_zone[1],
            value_low=long_zone[2],
            value_high=long_zone[3],
            invalid_low=long_zone[4],
            invalid_high=long_zone[5],
            reclaim=long_zone[6],
            continuation=long_zone[7],
            lifecycle_state=long_zone[8],
        )
    if short_zone is not None:
        short_setup["value_defense_entry_layer"] = _value_defense_layer(
            side="short",
            shallow_low=short_zone[0],
            shallow_high=short_zone[1],
            value_low=short_zone[2],
            value_high=short_zone[3],
            invalid_low=short_zone[4],
            invalid_high=short_zone[5],
            reclaim=short_zone[6],
            continuation=short_zone[7],
            lifecycle_state=short_zone[8],
        )
    return {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "bias": bias,
        "current_price": current_price,
        "signals_4h": signals_4h,
        "signals_1h": signals_1h,
        "signals_15m": signals_15m,
        "market_map_primary_state": market_map_primary_state,
        "market_map_flags": market_map_flags,
        "level_flip_state": level_flip_state,
        "trend_flip_state": trend_flip_state,
        "failed_breakout_state": failed_breakout_state,
        "transition_direction": transition_direction,
        "long_setup": long_setup,
        "short_setup": short_setup,
        "long_display_score": 54,
        "short_display_score": 71,
        "score_gap": 17,
        "confidence": 62,
        "primary_setup_status": "watch",
        "primary_setup_reason": "trend_watch",
        "signal_tier": "attention",
        "trade_execution_gate": "blocked",
        "phase1_observation_gate": "pass",
        "notification_kind": "attention",
    }


class BigChanceEvaluationTests(unittest.TestCase):
    def test_failed_long_thesis_becomes_short_candidate(self) -> None:
        current = _payload(
            signal_id="20260706_150500",
            timestamp_jst="2026-07-06T15:05:00+09:00",
            bias="long",
            current_price=50_100,
            signals_4h="short",
            signals_1h="wait",
            signals_15m="short",
            market_map_primary_state="early_down_transition",
            market_map_flags=["support_to_resistance_flip", "support_to_resistance_retest_confirmed"],
            level_flip_state="support_to_resistance_confirmed",
            trend_flip_state="trend_flip_early_down",
            failed_breakout_state="failed_long_breakout",
            transition_direction="down",
            long_zone=(47_000, 47_500, 46_800, 47_200, 46_200, 46_600, 46_900, 47_100, "invalidated"),
            short_zone=(52_000, 52_500, 52_600, 53_100, 53_600, 54_000, 52_850, 53_050, "watch"),
        )
        previous = {"signal_id": "20260706_140500", "notification_kind": "attention", "bias": "long"}

        candidate = evaluate_big_chance(current, previous)

        self.assertTrue(candidate["present"])
        self.assertEqual(candidate["side"], "short")
        self.assertEqual(candidate["type"], "long_failed_to_short")
        self.assertEqual(candidate["status"], "follow_through")
        self.assertIn("support_to_resistance_flip", candidate["reason_codes"])
        self.assertIn("trend_flip_early_down", candidate["reason_codes"])
        self.assertEqual(candidate["evidence"]["current_price_position_long"], "above_zones")
        self.assertEqual(candidate["evidence"]["current_price_position_short"], "below_zones")
        self.assertIn("Failed thesis is opportunity", candidate["failed_thesis"]["thesis_summary"])

    def test_failed_short_thesis_becomes_long_candidate(self) -> None:
        current = _payload(
            signal_id="20260706_151500",
            timestamp_jst="2026-07-06T15:15:00+09:00",
            bias="short",
            current_price=60_100,
            signals_4h="long",
            signals_1h="wait",
            signals_15m="long",
            market_map_primary_state="early_up_transition",
            market_map_flags=["resistance_to_support_flip", "resistance_to_support_retest_confirmed"],
            level_flip_state="resistance_to_support_confirmed",
            trend_flip_state="trend_flip_early_up",
            failed_breakout_state="failed_short_breakout",
            transition_direction="up",
            long_zone=(62_000, 62_500, 62_600, 63_100, 63_600, 64_000, 62_850, 63_050, "watch"),
            short_zone=(57_000, 57_500, 56_800, 57_200, 56_200, 56_600, 56_900, 57_100, "invalidated"),
        )
        previous = {"signal_id": "20260706_141500", "notification_kind": "attention", "bias": "short"}

        candidate = evaluate_big_chance(current, previous)

        self.assertTrue(candidate["present"])
        self.assertEqual(candidate["side"], "long")
        self.assertEqual(candidate["type"], "short_failed_to_long")
        self.assertEqual(candidate["status"], "follow_through")
        self.assertIn("resistance_to_support_flip", candidate["reason_codes"])
        self.assertIn("trend_flip_early_up", candidate["reason_codes"])
        self.assertEqual(candidate["evidence"]["current_price_position_long"], "below_zones")
        self.assertEqual(candidate["evidence"]["current_price_position_short"], "above_zones")

    def test_markdown_includes_big_chance_and_safety_boundary(self) -> None:
        current = _payload(
            signal_id="20260706_150500",
            timestamp_jst="2026-07-06T15:05:00+09:00",
            bias="long",
            current_price=50_100,
            signals_4h="short",
            signals_1h="wait",
            signals_15m="short",
            market_map_primary_state="early_down_transition",
            market_map_flags=["support_to_resistance_flip"],
            level_flip_state="support_to_resistance_confirmed",
            trend_flip_state="trend_flip_early_down",
            failed_breakout_state="failed_long_breakout",
            transition_direction="down",
            long_zone=(47_000, 47_500, 46_800, 47_200, 46_200, 46_600, 46_900, 47_100, "invalidated"),
            short_zone=(52_000, 52_500, 52_600, 53_100, 53_600, 54_000, 52_850, 53_050, "watch"),
        )

        candidate = evaluate_big_chance(current, None)
        markdown = build_big_chance_markdown(candidate)

        self.assertIn("## Big Chance / Failed Thesis", markdown)
        self.assertIn("## Safety Boundary", markdown)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", markdown)


if __name__ == "__main__":
    unittest.main()
