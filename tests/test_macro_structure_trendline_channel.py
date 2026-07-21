from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.feedback.macro_structure_trendline_channel import METHOD_VERSION, _line_for_kind, _state_priority, build_trendline_model


def _candles(*, post_break: bool = False, anchor_breach: bool = False) -> list[dict[str, object]]:
    candles: list[dict[str, object]] = []
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for index in range(32):
        close = 100.0
        low = 96.0
        high = 104.0
        if index in {3, 8, 13, 18}:
            low = 90.0 + (index - 3) * 0.4
        if index in {5, 10, 15}:
            high = 110.0 - (index - 5) * 0.4
        if post_break and index == 11:
            close, low = 88.0, 87.0
        if anchor_breach and index == 7:
            close, low = 85.0, 84.0
        candles.append({
            "timestamp_utc": (start + timedelta(hours=4 * index)).isoformat().replace("+00:00", "Z"),
            "open": 100.0, "high": high, "low": low, "close": close,
        })
    return candles


def _model(**kwargs: object) -> dict[str, object]:
    return build_trendline_model(_candles(**kwargs), cutoff=datetime(2026, 1, 6, tzinfo=timezone.utc), current_price=100.0)


def _rank_line(*, state: str = "active", touch_count: int = 2, confirmation: str = "2026-01-02T00:00:00+00:00", span: int = 10, distance: float = 1.0, line_id: str = "line", kind: str = "ascending_support") -> dict[str, object]:
    return {"state": state, "touch_count": touch_count, "anchor_2_confirmation_timestamp": confirmation, "anchor_span_bars": span, "distance_from_price_atr": distance, "line_id": line_id, "kind": kind}


def _line(model: dict[str, object], kind: str, first: str = "") -> dict[str, object]:
    lines = [item for item in model["lines"] if item["kind"] == kind]
    if first:
        lines = [item for item in lines if item["anchor_1_pivot_id"].endswith(first)]
    if not lines:
        raise AssertionError(f"missing {kind}")
    return lines[0]


class MacroStructureTrendlineChannelTests(unittest.TestCase):
    def test_ranking_state_order_is_explicit(self) -> None:
        lines = [_rank_line(state=state, line_id=state) for state in ("invalidated", "insufficient", "broken", "active", "tested")]
        self.assertEqual([line["state"] for line in sorted(lines, key=_state_priority)], ["tested", "active", "broken", "insufficient", "invalidated"])

    def test_ranking_prefers_touch_count_within_state(self) -> None:
        lines = [_rank_line(touch_count=1, line_id="low"), _rank_line(touch_count=3, line_id="high")]
        self.assertEqual(sorted(lines, key=_state_priority)[0]["line_id"], "high")

    def test_ranking_prefers_newer_confirmation_with_other_ties(self) -> None:
        lines = [_rank_line(confirmation="2026-01-01T00:00:00+00:00", line_id="old"), _rank_line(confirmation="2026-01-03T00:00:00+00:00", line_id="new")]
        self.assertEqual(sorted(lines, key=_state_priority)[0]["line_id"], "new")

    def test_ranking_prefers_larger_span_then_smaller_distance(self) -> None:
        larger = _rank_line(span=20, distance=3.0, line_id="larger")
        smaller = _rank_line(span=10, distance=0.5, line_id="smaller")
        self.assertEqual(sorted([smaller, larger], key=_state_priority)[0]["line_id"], "larger")
        nearer = _rank_line(span=20, distance=0.5, line_id="nearer")
        farther = _rank_line(span=20, distance=2.0, line_id="farther")
        self.assertEqual(sorted([farther, nearer], key=_state_priority)[0]["line_id"], "nearer")

    def test_ranking_uses_line_id_as_final_tie_break(self) -> None:
        lines = [_rank_line(line_id="z-line"), _rank_line(line_id="a-line")]
        self.assertEqual([line["line_id"] for line in sorted(lines, key=_state_priority)], ["a-line", "z-line"])

    def test_top_three_retention_keeps_live_candidates_ahead_of_weak_states(self) -> None:
        lines = [_rank_line(state="invalidated", line_id="invalidated"), _rank_line(state="insufficient", line_id="insufficient"), _rank_line(state="broken", line_id="broken"), _rank_line(state="active", line_id="active"), _rank_line(state="tested", line_id="tested")]
        retained = sorted(lines, key=_state_priority)[:3]
        self.assertEqual([line["state"] for line in retained], ["tested", "active", "broken"])

    def test_channel_base_selection_uses_highest_ranked_live_line(self) -> None:
        lines = [_rank_line(state="active", touch_count=5, line_id="active"), _rank_line(state="tested", touch_count=1, line_id="tested"), _rank_line(state="broken", line_id="broken")]
        self.assertEqual(_line_for_kind(lines, "ascending_support")["line_id"], "tested")

    def test_same_input_has_same_ids_geometry_and_channels(self) -> None:
        first = _model(); second = _model()
        self.assertEqual(first, second)
        self.assertEqual(first["method_version"], METHOD_VERSION)

    def test_confirmation_time_prevents_backdating(self) -> None:
        model = build_trendline_model(_candles(), cutoff=datetime(2026, 1, 2, 12, tzinfo=timezone.utc), current_price=100.0)
        self.assertEqual(model["status"], "insufficient")
        self.assertEqual(model["displayed_line_ids"], [])

    def test_ascending_support_uses_confirmed_higher_lows(self) -> None:
        line = _line(_model(), "ascending_support")
        self.assertGreater(line["anchor_2_price"], line["anchor_1_price"])
        self.assertEqual(line["anchor_1_pivot_id"].split(":")[1], "L")
        self.assertEqual(line["anchor_2_pivot_id"].split(":")[1], "L")

    def test_descending_resistance_uses_confirmed_lower_highs(self) -> None:
        line = _line(_model(), "descending_resistance")
        self.assertLess(line["anchor_2_price"], line["anchor_1_price"])
        self.assertEqual(line["anchor_1_pivot_id"].split(":")[1], "H")
        self.assertEqual(line["anchor_2_pivot_id"].split(":")[1], "H")

    def test_touch_tolerance_clusters_are_deterministic(self) -> None:
        model = _model()
        line = _line(model, "ascending_support")
        self.assertGreaterEqual(line["touch_count"], 2)
        self.assertEqual(line["touch_count"], len(line["touch_timestamps"]))
        self.assertEqual(model, _model())

    def test_close_breach_after_confirmation_is_broken(self) -> None:
        model = _model(post_break=True)
        broken = [line for line in model["lines"] if line["state"] == "broken"]
        self.assertTrue(broken)
        self.assertTrue(all(line["break_timestamp"] for line in broken))

    def test_anchor_period_breach_invalidates_and_hides_candidate(self) -> None:
        model = _model(anchor_breach=True)
        invalidated = [line for line in model["lines"] if line["state"] == "invalidated"]
        self.assertTrue(invalidated)
        self.assertTrue(all(line["line_id"] not in model["displayed_line_ids"] for line in invalidated))

    def test_old_broken_lines_are_not_displayed(self) -> None:
        model = _model(post_break=True)
        displayed = {line_id for line_id in model["displayed_line_ids"]}
        self.assertFalse(any(line["state"] == "broken" and line["line_id"] in displayed for line in model["lines"]))

    def test_channels_are_parallel_deterministic_and_bounded(self) -> None:
        model = _model()
        again = _model()
        self.assertEqual(model["channels"], again["channels"])
        self.assertLessEqual(len(model["channels"]), 2)
        for channel in model["channels"]:
            self.assertGreaterEqual(channel["width_atr"], 0.75)
            self.assertLessEqual(channel["width_atr"], 12)
            self.assertLessEqual(channel["lower_value_at_cutoff"], channel["upper_value_at_cutoff"])

    def test_insufficient_evidence_is_explicit_without_lines(self) -> None:
        candles = _candles()[:8]
        model = build_trendline_model(candles, cutoff=datetime(2026, 1, 3, tzinfo=timezone.utc), current_price=100.0)
        self.assertEqual(model["status"], "insufficient")
        self.assertEqual(model["lines"], [])
        self.assertIn("insufficient_confirmed_4h_evidence", model["reason_codes"])


if __name__ == "__main__":
    unittest.main()
