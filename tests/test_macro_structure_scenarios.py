from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.feedback.macro_structure_scenarios import METHOD_VERSION, build_scenario_model


START = datetime(2026, 1, 1, tzinfo=timezone.utc)
CUTOFF = START + timedelta(hours=40)


def event(event_id: str, event_type: str, timestamp_hours: int, *, object_id: str = "zone-1", object_kind: str = "horizontal_zone", direction: str = "DOWN", sequence_status: str = "neutral", parent: str = "") -> dict[str, object]:
    return {"event_id": event_id, "event_type": event_type, "event_status": "ongoing" if event_type == "approach" else "confirmed", "sequence_status": sequence_status, "event_timestamp_utc": (START + timedelta(hours=timestamp_hours)).isoformat(), "object_kind": object_kind, "object_id": object_id, "related_object_id": "", "parent_event_id": parent, "direction": direction, "price": 100.0, "object_value_low": 99.0, "object_value_high": 101.0, "distance_atr": 0.0, "interaction_count": 0, "reason_codes": []}


def zone(level_id: str = "zone-1", role: str = "support") -> dict[str, object]:
    return {"level_id": level_id, "low": 99.0, "high": 101.0, "center": 100.0, "role": role, "last_confirmed_at": START.isoformat()}


def build(events: list[dict[str, object]], zones: list[dict[str, object]] | None = None) -> dict[str, object]:
    return build_scenario_model(cutoff=CUTOFF, current_price=100.0, structure_state="range", price_location="middle", zones=[zone()] if zones is None else zones, trendline_model={"lines": [], "displayed_line_ids": []}, structural_event_model={"schema_version": "macro_structure_structural_events.v1", "method_version": "macro_structure_structural_events.v1", "events": events})


class MacroStructureScenarioTests(unittest.TestCase):
    def test_pending_break_creates_watch_without_acceptance_wording(self) -> None:
        result = build([event("break-1", "break", 40, sequence_status="pending")])
        scenario = result["scenarios"][0]
        self.assertEqual(scenario["scenario_type"], "break_resolution_watch")
        self.assertEqual(scenario["scenario_status"], "watch")
        self.assertNotIn("accepted", scenario["condition_text"].lower())

    def test_acceptance_and_retest_use_root_break_direction(self) -> None:
        events = [event("break-1", "break", 8, direction="DOWN", sequence_status="accepted"), event("accept-1", "closed_candle_acceptance", 12, direction="DOWN", parent="break-1"), event("retest-1", "retest", 16, direction="UP", parent="accept-1")]
        result = build(events)
        scenario = result["scenarios"][0]
        self.assertEqual(scenario["scenario_type"], "accepted_break_continuation")
        self.assertEqual(scenario["direction"], "DOWN")

    def test_hold_and_failed_break_families(self) -> None:
        accepted = build([event("break-1", "break", 8, direction="UP", sequence_status="accepted"), event("accept-1", "closed_candle_acceptance", 12, direction="UP", parent="break-1"), event("hold-1", "retest_hold", 20, direction="UP", parent="accept-1")])
        self.assertEqual(accepted["scenarios"][0]["scenario_type"], "accepted_break_continuation")
        failed = build([event("break-1", "break", 8, direction="DOWN", sequence_status="reclaimed"), event("reclaim-1", "false_break_reclaim", 16, direction="UP", parent="break-1")])
        self.assertEqual(failed["scenarios"][0]["scenario_type"], "failed_break_reversal")
        self.assertEqual(failed["scenarios"][0]["direction"], "UP")

    def test_retest_failure_suppresses_older_acceptance(self) -> None:
        events = [event("break-1", "break", 4, direction="DOWN", sequence_status="accepted"), event("accept-1", "closed_candle_acceptance", 8, direction="DOWN", parent="break-1"), event("retest-1", "retest", 12, direction="UP", parent="accept-1"), event("failure-1", "retest_failure", 20, direction="UP", parent="retest-1")]
        result = build(events)
        self.assertEqual([scenario["scenario_type"] for scenario in result["scenarios"]], ["failed_break_reversal"])

    def test_boundary_reaction_and_newer_break_suppression(self) -> None:
        boundary = build([event("touch-1", "touch", 36, direction="UP")])
        self.assertEqual(boundary["scenarios"][0]["scenario_type"], "boundary_reaction_watch")
        suppressed = build([event("touch-1", "touch", 20, direction="UP"), event("break-1", "break", 36, direction="DOWN", sequence_status="pending")])
        self.assertEqual([scenario["scenario_type"] for scenario in suppressed["scenarios"]], ["break_resolution_watch"])

    def test_pivot_pairs_require_recent_matching_events(self) -> None:
        up = [event("hh-1", "higher_high", 28, object_id="pivot-high", object_kind="pivot_structure", direction="UP"), event("hl-1", "higher_low", 32, object_id="pivot-low", object_kind="pivot_structure", direction="UP")]
        result = build(up)
        self.assertEqual(result["scenarios"][0]["scenario_type"], "pivot_structure_continuation")
        stale = build([event("hh-1", "higher_high", -60, object_id="pivot-high", object_kind="pivot_structure", direction="UP"), event("hl-1", "higher_low", 32, object_id="pivot-low", object_kind="pivot_structure", direction="UP")])
        self.assertEqual(stale["status"], "insufficient")

    def test_global_direction_conflict_and_bounds_are_deterministic(self) -> None:
        events = [event("up-break", "break", 40, object_id="zone-up", direction="UP", sequence_status="pending"), event("down-break", "break", 39, object_id="zone-down", direction="DOWN", sequence_status="pending")]
        first = build(events, [zone("zone-up", "resistance"), zone("zone-down", "support")])
        second = build(events, [zone("zone-up", "resistance"), zone("zone-down", "support")])
        self.assertEqual(first, second)
        self.assertLessEqual(len(first["scenarios"]), 3)
        self.assertEqual(len({scenario["direction"] for scenario in first["scenarios"]}), 1)
        self.assertGreaterEqual(first["suppressed_candidate_count"], 1)

    def test_insufficient_and_references_are_explicit(self) -> None:
        result = build([])
        self.assertEqual(result["status"], "insufficient")
        self.assertEqual(result["reason_codes"], ["insufficient_current_structural_evidence"])
        self.assertEqual(result["method_version"], METHOD_VERSION)
        with self.assertRaises(ValueError):
            build([event("future", "touch", 44)])

    def test_missing_parent_and_event_collision_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            build([event("child", "retest", 20, parent="missing")])
        first = event("same", "touch", 20)
        second = event("same", "touch", 24)
        with self.assertRaises(ValueError):
            build([first, second])

    def test_scenarios_have_structured_condition_confirmation_and_invalidation(self) -> None:
        result = build([event("touch-1", "clean_rejection", 36, direction="UP")])
        scenario = result["scenarios"][0]
        for field in ("condition_code", "condition_text", "next_confirmation_code", "next_confirmation_text", "invalidation_code", "invalidation_text", "supporting_event_ids"):
            self.assertTrue(scenario[field])
        forbidden = ("probability", "win rate", "buy", "sell", "long", "short", "entry", "stop loss", "take profit", "order permission")
        payload = str(result).lower()
        self.assertFalse(any(word in payload for word in forbidden))


if __name__ == "__main__":
    unittest.main()
