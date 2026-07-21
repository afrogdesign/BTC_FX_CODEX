from __future__ import annotations

import unittest
import math
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from src.feedback import macro_structure_scenarios as scenarios
from src.feedback.macro_structure_scenarios import METHOD_VERSION, build_scenario_model


START = datetime(2026, 1, 1, tzinfo=timezone.utc)
CUTOFF = START + timedelta(hours=40)


def event(event_id: str, event_type: str, timestamp_hours: int, *, object_id: str = "zone-1", object_kind: str = "horizontal_zone", direction: str = "DOWN", sequence_status: str | None = None, parent: str = "", related_object_id: str | None = None) -> dict[str, object]:
    default_sequence = {"approach": "ongoing", "touch": "neutral", "clean_rejection": "neutral", "break": "pending", "closed_candle_acceptance": "accepted", "false_break_reclaim": "reclaimed", "retest": "accepted", "retest_hold": "accepted", "retest_failure": "accepted", "higher_high": "neutral", "higher_low": "neutral", "lower_high": "neutral", "lower_low": "neutral"}[event_type]
    if related_object_id is None and object_kind == "pivot_structure":
        related_object_id = f"previous-{event_id}"
    return {"event_id": event_id, "event_type": event_type, "event_status": "ongoing" if event_type == "approach" else "confirmed", "sequence_status": default_sequence if sequence_status is None else sequence_status, "event_timestamp_utc": (START + timedelta(hours=timestamp_hours)).isoformat(), "object_kind": object_kind, "object_id": object_id, "related_object_id": related_object_id or "", "parent_event_id": parent, "direction": direction, "price": 100.0, "object_value_low": 99.0, "object_value_high": 101.0, "distance_atr": 0.0, "interaction_count": 0, "reason_codes": []}


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
        accepted = build([event("break-1", "break", 8, direction="UP", sequence_status="accepted"), event("accept-1", "closed_candle_acceptance", 12, direction="UP", parent="break-1"), event("retest-1", "retest", 16, direction="UP", parent="accept-1"), event("hold-1", "retest_hold", 20, direction="UP", parent="retest-1")])
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
        result = build([event("touch-0", "touch", 32, direction="UP"), event("touch-1", "clean_rejection", 36, direction="UP", parent="touch-0")])
        scenario = result["scenarios"][0]
        for field in ("condition_code", "condition_text", "next_confirmation_code", "next_confirmation_text", "invalidation_code", "invalidation_text", "supporting_event_ids"):
            self.assertTrue(scenario[field])
        forbidden = ("probability", "win rate", "buy", "sell", "long", "short", "entry", "stop loss", "take profit", "order permission")
        payload = str(result).lower()
        self.assertFalse(any(word in payload for word in forbidden))

    def test_event_vocabulary_status_and_sequence_validation_fail_closed(self) -> None:
        invalid = event("bad", "touch", 20)
        invalid["event_type"] = "unknown"
        with self.assertRaises(ValueError):
            build([invalid])
        for event_type, bad_status in (("approach", "confirmed"), ("touch", "ongoing")):
            invalid = event("bad", event_type, 20)
            invalid["event_status"] = bad_status
            with self.assertRaises(ValueError):
                build([invalid])
        for event_type in ("approach", "touch", "clean_rejection", "break", "closed_candle_acceptance", "false_break_reclaim", "retest", "retest_hold", "retest_failure", "higher_high", "higher_low", "lower_high", "lower_low"):
            invalid = event("bad", event_type, 20, parent="touch-0" if event_type == "clean_rejection" else "")
            invalid["sequence_status"] = "invalid"
            with self.assertRaises(ValueError):
                build([event("touch-0", "touch", 10), invalid] if event_type == "clean_rejection" else [invalid])

    def test_object_and_pivot_constraints_fail_closed(self) -> None:
        invalid = event("pivot", "higher_high", 20, object_kind="horizontal_zone")
        with self.assertRaises(ValueError):
            build([invalid])
        invalid = event("touch", "touch", 20, object_kind="pivot_structure")
        with self.assertRaises(ValueError):
            build([invalid])
        invalid = event("hh", "higher_high", 20, direction="DOWN")
        invalid["object_kind"] = "pivot_structure"
        with self.assertRaises(ValueError):
            build([invalid])
        invalid = event("hh", "higher_high", 20, object_kind="pivot_structure", related_object_id="")
        with self.assertRaises(ValueError):
            build([invalid])

    def test_parent_shape_and_timestamp_constraints_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            build([event("clean", "clean_rejection", 20)])
        with self.assertRaises(ValueError):
            build([event("parent", "break", 10), event("clean", "clean_rejection", 20, parent="parent")], [zone()])
        wrong_object = event("parent", "touch", 10, object_id="other")
        with self.assertRaises(ValueError):
            build([wrong_object, event("clean", "clean_rejection", 20, parent="parent")])
        with self.assertRaises(ValueError):
            build([event("parent", "touch", 20), event("clean", "clean_rejection", 20, parent="parent")])
        with self.assertRaises(ValueError):
            build([event("parent", "touch", 24), event("clean", "clean_rejection", 20, parent="parent")])

    def test_break_resolution_consistency_is_validated(self) -> None:
        pending = event("break", "break", 8, sequence_status="pending")
        with self.assertRaises(ValueError):
            build([pending, event("accept", "closed_candle_acceptance", 12, parent="break")])
        with self.assertRaises(ValueError):
            build([event("break", "break", 8, sequence_status="accepted"), event("reclaim", "false_break_reclaim", 12, parent="break")])
        accepted = [event("break", "break", 8, sequence_status="accepted"), event("accept", "closed_candle_acceptance", 12, parent="break"), event("retest", "retest", 16, parent="accept")]
        with self.assertRaises(ValueError):
            build(accepted + [event("hold", "retest_hold", 20, parent="retest"), event("failure", "retest_failure", 24, parent="retest")])
        with self.assertRaises(ValueError):
            build([event("break", "break", 8, sequence_status="pending"), event("accept", "closed_candle_acceptance", 12, parent="break")])
        self.assertEqual(build([event("break", "break", 8, sequence_status="pending")])["status"], "ok")

    def test_output_validation_rejects_invalid_scenario_fields_and_references(self) -> None:
        result = build([event("break", "break", 40, sequence_status="pending")])
        candidate = deepcopy(result["scenarios"][0])
        objects = {("horizontal_zone", "zone-1")}
        event_map = {"break": event("break", "break", 40, sequence_status="pending")}
        for field, value in (("scenario_status", "invalid"), ("condition_code", "invalid"), ("next_confirmation_code", "invalid"), ("invalidation_code", "invalid")):
            invalid = deepcopy(candidate)
            invalid[field] = value
            with self.assertRaises(ValueError):
                scenarios._validate_candidate(invalid, CUTOFF, objects, event_map)
        invalid = deepcopy(candidate)
        invalid["supporting_event_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            scenarios._validate_candidate(invalid, CUTOFF, objects, event_map)
        invalid = deepcopy(candidate)
        invalid["primary_object_id"] = "missing"
        with self.assertRaises(ValueError):
            scenarios._validate_candidate(invalid, CUTOFF, objects, event_map)

    def test_current_price_rejects_bool_nan_and_infinity(self) -> None:
        for price in (True, math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                build_scenario_model(cutoff=CUTOFF, current_price=price, structure_state="range", price_location="middle", zones=[zone()], trendline_model={"lines": [], "displayed_line_ids": []}, structural_event_model={"method_version": "macro_structure_structural_events.v1", "events": []})

    def test_same_timestamp_precedence_prefers_break_over_touch(self) -> None:
        result = build([event("touch", "touch", 40, direction="UP"), event("break", "break", 40, sequence_status="pending")])
        self.assertEqual([scenario["scenario_type"] for scenario in result["scenarios"]], ["break_resolution_watch"])

    def test_full_same_timestamp_precedence_is_explicit(self) -> None:
        same_timestamp = [
            event("approach", "approach", 20),
            event("touch", "touch", 20),
            event("clean", "clean_rejection", 20),
            event("accept", "closed_candle_acceptance", 20),
            event("retest", "retest", 20),
            event("reclaim", "false_break_reclaim", 20),
            event("failure", "retest_failure", 20),
            event("hold", "retest_hold", 20),
            event("pending", "break", 20, sequence_status="pending"),
        ]
        ordered = [item["event_id"] for item in sorted(same_timestamp, key=scenarios._event_sort_key)]
        self.assertEqual(ordered, ["approach", "touch", "clean", "accept", "retest", "reclaim", "failure", "hold", "pending"])

    def test_pending_break_wins_over_valid_resolution_sequences(self) -> None:
        for resolution in ("retest_failure", "false_break_reclaim", "retest_hold"):
            if resolution == "retest_failure":
                chain = [event("root", "break", 4, sequence_status="accepted"), event("accept", "closed_candle_acceptance", 8, parent="root"), event("retest", "retest", 12, parent="accept"), event("resolution", resolution, 40, parent="retest")]
            elif resolution == "retest_hold":
                chain = [event("root", "break", 4, sequence_status="accepted"), event("accept", "closed_candle_acceptance", 8, parent="root"), event("retest", "retest", 12, parent="accept"), event("resolution", resolution, 40, parent="retest")]
            else:
                chain = [event("root", "break", 4, sequence_status="reclaimed"), event("resolution", resolution, 40, parent="root")]
            result = build(chain + [event("pending", "break", 40, sequence_status="pending")])
            self.assertEqual(result["scenarios"][0]["scenario_type"], "break_resolution_watch")

    def test_resolution_precedes_retest_and_acceptance_and_selected_family_follows(self) -> None:
        events = [
            event("root", "break", 4, sequence_status="accepted"),
            event("accept", "closed_candle_acceptance", 8, parent="root"),
            event("retest", "retest", 12, parent="accept"),
            event("hold", "retest_hold", 40, parent="retest"),
            event("older-root", "break", 20, sequence_status="accepted"),
            event("older-accept", "closed_candle_acceptance", 24, parent="older-root"),
        ]
        result = build(events)
        self.assertEqual(result["scenarios"][0]["scenario_type"], "accepted_break_continuation")
        self.assertEqual(scenarios._latest_state_priority(event("hold", "retest_hold", 40)), 7)
        self.assertGreater(scenarios._latest_state_priority(event("hold", "retest_hold", 40)), scenarios._latest_state_priority(event("retest", "retest", 40)))
        self.assertGreater(scenarios._latest_state_priority(event("hold", "retest_hold", 40)), scenarios._latest_state_priority(event("accept", "closed_candle_acceptance", 40)))

    def test_nonpending_root_does_not_override_semantic_resolution(self) -> None:
        events = [event("root", "break", 32, sequence_status="accepted"), event("accept", "closed_candle_acceptance", 36, parent="root"), event("retest", "retest", 40, parent="accept")]
        result = build(events)
        self.assertEqual(result["scenarios"][0]["scenario_type"], "accepted_break_continuation")
        self.assertLess(scenarios._latest_state_priority(event("root", "break", 40, sequence_status="accepted")), scenarios._latest_state_priority(event("retest", "retest", 40)))

    def test_same_precedence_uses_ascending_event_id_tiebreak(self) -> None:
        first = event("hold-a", "retest_hold", 20)
        second = event("hold-z", "retest_hold", 20)
        self.assertEqual([item["event_id"] for item in sorted([second, first], key=scenarios._event_sort_key)], ["hold-a", "hold-z"])
        invalid = event("bad", "touch", 20)
        invalid["event_type"] = "unknown"
        with self.assertRaises(ValueError):
            scenarios._latest_state_priority(invalid)


if __name__ == "__main__":
    unittest.main()
