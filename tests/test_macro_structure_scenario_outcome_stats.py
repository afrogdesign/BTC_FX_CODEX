from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.feedback.macro_structure_scenario_outcome_stats import (
    METHOD_VERSION,
    ScenarioOutcomeStatsError,
    evaluate_scenario_outcome_stats,
    publish_scenario_outcome_stats,
)

START = datetime(2026, 1, 1, tzinfo=timezone.utc)


def event(event_id: str, event_type: str, hours: int, *, object_id: str = "zone-1", direction: str = "UP") -> dict[str, object]:
    sequence = {"touch": "neutral", "closed_candle_acceptance": "accepted", "false_break_reclaim": "reclaimed", "higher_high": "neutral", "higher_low": "neutral", "lower_high": "neutral", "lower_low": "neutral"}[event_type]
    return {"event_id": event_id, "event_type": event_type, "event_status": "confirmed", "sequence_status": sequence, "event_timestamp_utc": (START + timedelta(hours=hours)).isoformat(), "object_kind": "pivot_structure" if event_type in {"higher_high", "higher_low", "lower_high", "lower_low"} else "horizontal_zone", "object_id": object_id, "related_object_id": "related", "parent_event_id": "", "direction": direction, "reason_codes": []}


def scenario(scenario_id: str = "scenario-1", *, direction: str = "UP", object_id: str = "zone-1") -> dict[str, object]:
    return {"scenario_id": scenario_id, "scenario_type": "boundary_reaction_watch", "scenario_status": "watch", "direction": direction, "trigger_timestamp_utc": START.isoformat(), "primary_object_kind": "horizontal_zone", "primary_object_id": object_id, "related_object_ids": [], "supporting_event_ids": ["touch-0"], "condition_code": "object_holds_expected_side", "next_confirmation_code": "clean_rejection_or_same_direction_pivot", "invalidation_code": "wrong_side_break_or_acceptance", "reason_codes": []}


def artifact(root: Path, hours: int, scenarios: list[dict[str, object]], events: list[dict[str, object]] | None = None, *, artifact_id: str | None = None) -> None:
    folder = root / f"operator_{hours:02d}"
    folder.mkdir()
    payload = {
        "operator_artifact_id": artifact_id or f"artifact-{hours:02d}", "as_of_utc": (START + timedelta(hours=hours)).isoformat(),
        "scenario_model": {"method_version": "macro_structure_scenarios.v1", "status": "ok", "scenarios": scenarios},
        "structural_event_model": {"method_version": "macro_structure_structural_events.v1", "events": events or [event("touch-0", "touch", 0)]},
    }
    if events is not None and not any(item.get("event_id") == "touch-0" for item in events):
        payload["structural_event_model"]["events"] = [event("touch-0", "touch", 0), *events]
    (folder / "macro_structure_operator.json").write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


class ScenarioOutcomeStatsTests(unittest.TestCase):
    def test_first_observation_cohort_horizons_and_order_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"
            root.mkdir()
            s = scenario()
            artifact(root, 0, [s])
            artifact(root, 8, [s], [event("touch-0", "touch", 0), event("confirm", "closed_candle_acceptance", 6)])
            artifact(root, 12, [s])
            artifact(root, 24, [s])
            artifact(root, 48, [s])
            first = evaluate_scenario_outcome_stats(root)
            second = evaluate_scenario_outcome_stats(root)
            self.assertEqual(first, second)
            self.assertEqual([row["horizon_hours"] for row in first["rows"]], [6, 12, 24])
            self.assertEqual(first["rows"][0]["outcome"], "continuation")

    def test_horizon_tolerance_and_immature(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir()
            s = scenario(); artifact(root, 0, [s]); artifact(root, 10, [s])
            result = evaluate_scenario_outcome_stats(root)
            self.assertEqual(result["rows"][0]["selected_cutoff_utc"], (START + timedelta(hours=10)).isoformat())
            self.assertEqual(result["rows"][2]["outcome"], "immature")

    def test_confirmation_invalidation_order_and_same_timestamp(self) -> None:
        for events, expected in (
            ([event("touch-0", "touch", 0), event("c", "closed_candle_acceptance", 4), event("i", "false_break_reclaim", 8)], "continuation"),
            ([event("touch-0", "touch", 0), event("i", "false_break_reclaim", 4), event("c", "closed_candle_acceptance", 8)], "rejection"),
            ([event("touch-0", "touch", 0), event("c", "closed_candle_acceptance", 8), event("i", "false_break_reclaim", 8)], "rejection"),
        ):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "operators"; root.mkdir(); s = scenario(); artifact(root, 0, [s]); artifact(root, 10, [s], events)
                self.assertEqual(evaluate_scenario_outcome_stats(root)["rows"][0]["outcome"], expected)

    def test_pivot_matching_and_opposite_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir()
            s = scenario("pivot", direction="UP")
            s.update(scenario_type="pivot_structure_continuation", primary_object_kind="pivot_structure", primary_object_id="pivot-a", related_object_ids=["pivot-b"], supporting_event_ids=["hh", "hl"])
            artifact(root, 0, [s], [event("hh", "higher_high", 0, object_id="pivot-a"), event("hl", "higher_low", 0, object_id="pivot-b")])
            artifact(root, 10, [s], [event("hh", "higher_high", 0, object_id="pivot-a"), event("hl", "higher_low", 0, object_id="pivot-b"), event("new", "higher_high", 8, object_id="pivot-a")])
            result = evaluate_scenario_outcome_stats(root)
            self.assertEqual(result["rows"][0]["outcome"], "continuation")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); s = scenario("pivot", direction="UP")
            s.update(scenario_type="pivot_structure_continuation", primary_object_kind="pivot_structure", primary_object_id="pivot-a", related_object_ids=["pivot-b"], supporting_event_ids=["hh", "hl"])
            artifact(root, 0, [s], [event("hh", "higher_high", 0, object_id="pivot-a"), event("hl", "higher_low", 0, object_id="pivot-b")])
            artifact(root, 10, [s], [event("hh", "higher_high", 0, object_id="pivot-a"), event("hl", "higher_low", 0, object_id="pivot-b"), event("lh", "lower_high", 4, object_id="pivot-a", direction="DOWN"), event("ll", "lower_low", 8, object_id="pivot-b", direction="DOWN")])
            self.assertEqual(evaluate_scenario_outcome_stats(root)["rows"][0]["outcome"], "rejection")

    def test_conflicting_payload_and_future_event_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); s = scenario(); artifact(root, 0, [s]); artifact(root, 4, [s], [event("touch-0", "touch", 8)])
            with self.assertRaises(ScenarioOutcomeStatsError):
                evaluate_scenario_outcome_stats(root)

    def test_conflicting_event_and_scenario_identity_across_artifacts_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); s = scenario()
            artifact(root, 0, [s], [event("touch-0", "touch", 0)])
            artifact(root, 10, [s], [event("touch-0", "touch", 0, direction="DOWN")])
            with self.assertRaisesRegex(ScenarioOutcomeStatsError, "stats_duplicate_event_conflict"):
                evaluate_scenario_outcome_stats(root)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); first = scenario(); second = scenario(); second["direction"] = "DOWN"
            artifact(root, 0, [first]); artifact(root, 10, [second])
            with self.assertRaisesRegex(ScenarioOutcomeStatsError, "stats_duplicate_scenario_conflict"):
                evaluate_scenario_outcome_stats(root)

    def test_insufficient_and_descriptive_strength(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); s = scenario(); artifact(root, 0, [s])
            for hours in (10, 14, 26, 40, 50, 60, 70):
                artifact(root, hours, [s], [event(f"c{hours}", "closed_candle_acceptance", hours)])
            result = evaluate_scenario_outcome_stats(root)
            self.assertEqual(result["evidence_strength"], "insufficient")
            self.assertEqual(result["mature_row_count"], 3)
            root2 = Path(temp) / "operators2"; root2.mkdir()
            scenarios = [scenario(f"s-{i}") for i in range(20)]
            artifact(root2, 0, scenarios); artifact(root2, 12, scenarios)
            result = evaluate_scenario_outcome_stats(root2)
            self.assertEqual(result["evidence_strength"], "descriptive_only")

    def test_group_threshold_is_independent_of_overall_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir()
            scenarios = [scenario(f"up-{i}", direction="UP") for i in range(10)] + [scenario(f"down-{i}", direction="DOWN") for i in range(10)]
            artifact(root, 0, scenarios); artifact(root, 10, scenarios)
            result = evaluate_scenario_outcome_stats(root)
            self.assertGreaterEqual(result["mature_row_count"], 20)
            for direction in ("UP", "DOWN"):
                group = result["grouped_counts"]["boundary_reaction_watch"][direction]
                self.assertEqual(group["mature_row_count"], 10)
                self.assertEqual(group["evidence_strength"], "insufficient")
                self.assertEqual(sum(group["outcome_counts"].values()), 30)

    def test_group_with_exactly_twenty_mature_rows_is_descriptive_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir()
            scenarios = [scenario(f"up-{i}") for i in range(10)]
            artifact(root, 0, scenarios); artifact(root, 10, scenarios); artifact(root, 12, scenarios)
            result = evaluate_scenario_outcome_stats(root)
            group = result["grouped_counts"]["boundary_reaction_watch"]["UP"]
            self.assertEqual(group["mature_row_count"], 20)
            self.assertEqual(group["evidence_strength"], "descriptive_only")
            self.assertEqual(result["grouped_counts"], evaluate_scenario_outcome_stats(root)["grouped_counts"])

    def test_invalid_scenario_artifact_is_excluded_and_publish_is_atomic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); out = Path(temp) / "out"; out.mkdir()
            folder = root / "operator_bad"; folder.mkdir(); (folder / "macro_structure_operator.json").write_text("{}", encoding="utf-8")
            (out / "latest.json").write_text("prior", encoding="utf-8")
            with self.assertRaises(ScenarioOutcomeStatsError): publish_scenario_outcome_stats(root, out)
            self.assertEqual((out / "latest.json").read_text(encoding="utf-8"), "prior")

    def test_all_missing_scenario_models_publish_insufficient_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); out = Path(temp) / "out"; out.mkdir()
            folder = root / "operator_bad"; folder.mkdir(); (folder / "macro_structure_operator.json").write_text(json.dumps({"operator_artifact_id": "bad", "as_of_utc": START.isoformat()}), encoding="utf-8")
            summary = publish_scenario_outcome_stats(root, out)
            self.assertEqual(summary["source_artifact_count"], 0)
            self.assertEqual(summary["excluded_artifact_count"], 1)
            self.assertEqual(summary["evidence_strength"], "insufficient")
            self.assertTrue((out / "latest.json").is_file())

    def test_identical_publish_reuses_deterministic_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); out = Path(temp) / "out"; out.mkdir(); s = scenario(); artifact(root, 0, [s]); artifact(root, 10, [s])
            first = publish_scenario_outcome_stats(root, out)
            second = publish_scenario_outcome_stats(root, out)
            self.assertEqual(first["artifact_id"], second["artifact_id"])

    def test_output_files_identity_csv_and_banned_words(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operators"; root.mkdir(); out = Path(temp) / "out"; out.mkdir(); s = scenario(); artifact(root, 0, [s]); artifact(root, 12, [s])
            summary = publish_scenario_outcome_stats(root, out)
            self.assertTrue((out / summary["artifact_id"] / "run_manifest.json").is_file())
            with (out / summary["artifact_id"] / "macro_structure_scenario_outcome_rows.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 3)
            text = " ".join(path.read_text(encoding="utf-8").lower() for path in (out / summary["artifact_id"]).iterdir())
            for word in ("probability", "win rate", "buy", "sell", "long", "short", "entry", "stop loss", "take profit", "order permission"):
                self.assertNotIn(word, text)
            self.assertIn("report-only", text); self.assertIn("no automatic order", text); self.assertIn("human decides manually", text)


if __name__ == "__main__":
    unittest.main()
