from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.feedback.macro_structure_structural_events import METHOD_VERSION, build_structural_event_model


START = datetime(2026, 1, 1, tzinfo=timezone.utc)


def candles(rows: list[tuple[float, float, float, float]]) -> list[dict[str, object]]:
    result = []
    for index, (open_, high, low, close) in enumerate(rows):
        result.append({
            "timestamp_utc": (START + timedelta(hours=4 * index)).isoformat(),
            "open": open_, "high": high, "low": low, "close": close,
        })
    return result


def zone(*, role: str = "support", available: int = 0, level_id: str = "zone-1") -> dict[str, object]:
    return {"level_id": level_id, "low": 99.0, "high": 101.0, "center": 100.0, "role": role, "last_confirmed_at": (START + timedelta(hours=4 * available)).isoformat()}


def model(rows: list[tuple[float, float, float, float]], zones: list[dict[str, object]] | None = None, line_model: dict[str, object] | None = None) -> dict[str, object]:
    data = candles(rows)
    cutoff = START + timedelta(hours=4 * (len(data) - 1) + 4)
    return build_structural_event_model(data, cutoff=cutoff, current_price=100.0, zones=[zone()] if zones is None else zones, trendline_model=line_model or {"lines": [], "displayed_line_ids": []})


class MacroStructureStructuralEventTests(unittest.TestCase):
    def test_deterministic_ids_order_and_parents(self) -> None:
        rows = [(100, 103, 97, 100)] * 4 + [(100, 102, 99, 100)] * 3
        first = model(rows)
        second = model(rows)
        self.assertEqual(first, second)
        ids = {event["event_id"] for event in first["events"]}
        self.assertTrue(all(not event["parent_event_id"] or event["parent_event_id"] in ids for event in first["events"]))
        self.assertEqual(first["method_version"], METHOD_VERSION)

    def test_availability_prevents_backdating_and_approach_is_latest_bar_only(self) -> None:
        rows = [(100, 103, 97, 100)] * 3 + [(100, 102, 100, 100)]
        result = model(rows, [zone(available=3)])
        zone_events = [event for event in result["events"] if event["object_kind"] == "horizontal_zone"]
        self.assertTrue(all(event["event_timestamp_utc"] >= (START + timedelta(hours=12)).isoformat() for event in zone_events))
        approaches = [event for event in result["events"] if event["event_type"] == "approach"]
        self.assertLessEqual(len(approaches), 1)
        if approaches:
            self.assertEqual(approaches[0]["event_status"], "ongoing")
            self.assertEqual(approaches[0]["event_timestamp_utc"], (START + timedelta(hours=20)).isoformat())

    def test_touch_clusters_and_clean_rejection_parent(self) -> None:
        rows = [(97, 98, 96, 97), (100, 101, 99.5, 100), (100, 101, 99.5, 100), (102, 103, 102, 102), (102, 103, 102, 102), (100, 101, 99.5, 100), (103, 104, 102, 103)]
        result = model(rows)
        touches = [event for event in result["events"] if event["event_type"] == "touch"]
        rejections = [event for event in result["events"] if event["event_type"] == "clean_rejection"]
        self.assertEqual(len(touches), 2)
        self.assertEqual([event["interaction_count"] for event in touches], [1, 2])
        self.assertTrue(all(event["parent_event_id"] in {touch["event_id"] for touch in touches} for event in rejections))

    def test_wrong_side_close_break_and_two_bar_acceptance(self) -> None:
        rows = [(100, 103, 97, 100)] * 3 + [(100, 100, 96, 97), (97, 99, 95, 96), (96, 98, 94, 95)]
        events = model(rows)["events"]
        self.assertEqual(len([event for event in events if event["event_type"] == "break"]), 1)
        self.assertEqual(len([event for event in events if event["event_type"] == "closed_candle_acceptance"]), 1)
        self.assertFalse([event for event in events if event["event_type"] == "false_break_reclaim"])

    def test_reclaim_is_mutually_exclusive_with_acceptance(self) -> None:
        rows = [(100, 103, 97, 100)] * 3 + [(100, 100, 96, 97), (97, 100, 96, 100), (100, 103, 99, 101)]
        events = model(rows)["events"]
        self.assertEqual(len([event for event in events if event["event_type"] == "break"]), 1)
        self.assertEqual(len([event for event in events if event["event_type"] == "false_break_reclaim"]), 1)
        self.assertFalse([event for event in events if event["event_type"] == "closed_candle_acceptance"])

    def test_retest_hold_and_failure_are_single_resolution(self) -> None:
        rows = [(100, 103, 97, 100)] * 3 + [(100, 100, 96, 97), (97, 99, 95, 96), (96, 98, 94, 95), (95, 102, 94, 100), (100, 103, 99, 102)]
        events = model(rows)["events"]
        self.assertEqual(len([event for event in events if event["event_type"] == "retest"]), 1)
        resolutions = [event for event in events if event["event_type"] in {"retest_hold", "retest_failure"}]
        self.assertLessEqual(len(resolutions), 1)

    def test_pivot_events_use_confirmation_time_and_ignore_equal_values(self) -> None:
        rows = [(100, 101, 99, 100), (100, 103, 98, 100), (100, 101, 99, 100), (100, 105, 98, 100), (100, 101, 99, 100), (100, 102, 99, 100), (100, 101, 99, 100)]
        result = model(rows, zones=[])
        pivots = [event for event in result["events"] if event["object_kind"] == "pivot_structure"]
        self.assertTrue(all(event["event_timestamp_utc"] <= result["cutoff_utc"] for event in pivots))

    def test_display_ids_are_the_event_list_selection(self) -> None:
        result = model([(100, 103, 97, 100)] * 8)
        retained = {event["event_id"] for event in result["events"]}
        self.assertTrue(set(result["displayed_event_ids"]).issubset(retained))
        self.assertLessEqual(len(result["displayed_event_ids"]), 12)

    def test_insufficient_evidence_is_explicit(self) -> None:
        result = model([(100, 101, 99, 100)] * 3, zones=[])
        self.assertEqual(result["status"], "insufficient")
        self.assertEqual(result["events"], [])
        self.assertEqual(result["displayed_event_ids"], [])

    def test_displayed_trendline_is_same_object_with_original_geometry(self) -> None:
        line = {
            "line_id": "line-1", "kind": "ascending_support", "state": "active",
            "anchor_1_timestamp": START.isoformat(), "anchor_2_timestamp": (START + timedelta(hours=12)).isoformat(),
            "anchor_1_confirmation_timestamp": (START + timedelta(hours=4)).isoformat(),
            "anchor_2_confirmation_timestamp": (START + timedelta(hours=16)).isoformat(),
            "confirmation_timestamp": (START + timedelta(hours=16)).isoformat(),
            "anchor_1_price": 99.0, "anchor_2_price": 100.0, "anchor_span_bars": 3,
            "slope_per_4h_bar": 1 / 3,
        }
        result = model([(100, 103, 97, 100)] * 8, zones=[], line_model={"lines": [line], "displayed_line_ids": ["line-1"]})
        self.assertIn({"object_kind": "trendline", "object_id": "line-1"}, result["objects_evaluated"])


if __name__ == "__main__":
    unittest.main()
