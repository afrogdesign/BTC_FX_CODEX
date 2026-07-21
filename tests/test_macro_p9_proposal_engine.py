import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.feedback.macro_p9_proposal_engine import (
    CHAMPION_SCHEMA,
    METHOD_VERSION,
    SPACE_SCHEMA,
    _atomic,
    _dominates,
    _date_concentration,
    _m1_metrics,
    _rolling_snapshots,
    _expand_space,
    _p8_status,
    _validate_champion_manifest,
    candidate_id,
)


def champion(parameters=None):
    parameters = parameters or {"left_window": 2, "right_window": 2, "cutoff_utc": "x", "performance_start_utc": "y", "performance_end_utc": "z"}
    return {"schema_version": CHAMPION_SCHEMA, "method_version": METHOD_VERSION, "champion_id": candidate_id({"left_window": parameters["left_window"], "right_window": parameters["right_window"]}), "parameters": parameters, "input_fingerprints": {}, "accepted_artifact_fingerprints": {}}


class MacroP9ProposalEngineTests(unittest.TestCase):
    def test_manifest_and_space_versions(self):
        _validate_champion_manifest(champion())
        space = {"schema_version": SPACE_SCHEMA, "method_version": METHOD_VERSION, "one_at_a_time": [{"parameter": "left_window", "values": [1, 3]}], "combinations": []}
        self.assertEqual([{"left_window": 1, "right_window": 2}, {"left_window": 3, "right_window": 2}], _expand_space(space, champion()))

    def test_unknown_parameter_and_bool_fail_closed(self):
        value = champion()
        value["parameters"]["unknown"] = 1
        with self.assertRaises(ValueError):
            _validate_champion_manifest(value)
        value = champion()
        value["parameters"]["left_window"] = True
        with self.assertRaises(ValueError):
            _validate_champion_manifest(value)

    def test_duplicate_and_equivalent_space_fail(self):
        value = champion()
        space = {"schema_version": SPACE_SCHEMA, "method_version": METHOD_VERSION, "one_at_a_time": [{"parameter": "left_window", "values": [1, 1]}], "combinations": []}
        with self.assertRaises(ValueError):
            _expand_space(space, value)
        space["one_at_a_time"] = [{"parameter": "left_window", "values": [2]}]
        with self.assertRaises(ValueError):
            _expand_space(space, value)

    def test_maximum_challengers(self):
        value = champion()
        combinations = [{"parameters": {"left_window": left, "right_window": right}} for left in range(1, 6) for right in range(1, 6) if (left, right) != (2, 2)]
        space = {"schema_version": SPACE_SCHEMA, "method_version": METHOD_VERSION, "one_at_a_time": [], "combinations": combinations}
        self.assertEqual(24, len(_expand_space(space, value)))

    def test_candidate_id_is_deterministic(self):
        self.assertEqual(candidate_id({"left_window": 1, "right_window": 2}), candidate_id({"right_window": 2, "left_window": 1}))
        self.assertNotEqual(candidate_id({"left_window": 1, "right_window": 2}), candidate_id({"left_window": 2, "right_window": 1}))

    def test_pareto_requires_all_metrics_and_strict_improvement(self):
        champion_metrics = {"m1.directional_precision": .5, "m1.large_move_recall": .2, "m1.false_warning_rate": .3, "m1.opposite_move_rate": .2, "m1.whipsaw_rate": .1, "m1.burden_per_jst_day": 2.0, "m3.directional_precision": .5, "m3.opposite_move_rate": .2, "m3.balanced_no_expansion_rate": .2, "m3.whipsaw_rate": .1, "m3.burden_per_jst_day": 2.0}
        improved = dict(champion_metrics, **{"m1.large_move_recall": .3})
        self.assertEqual((True, 1), _dominates(improved, champion_metrics))
        self.assertEqual((False, 0), _dominates(dict(champion_metrics, **{"m1.false_warning_rate": None}), champion_metrics))

    def test_m1_uses_only_reliable_corridor_validation_path(self):
        summary = {"recommendation_gate": {"validation_policy_metrics": {"compression_only": {"large_move_recall": 0.99}, "reliable_level_acceptance_corridor": {key: 0.1 for key in ("directional_precision", "large_move_recall", "false_warning_rate", "opposite_move_rate", "whipsaw_rate", "burden_per_jst_day")}}}}
        self.assertEqual(0.1, _m1_metrics(summary)["large_move_recall"])
        with self.assertRaisesRegex(ValueError, "m1_validation_policy_missing"):
            _m1_metrics({"recommendation_gate": {"validation_policy_metrics": {"compression_only": {}}}})

    def test_concentration_boundary_and_failure(self):
        rows = [{"episode_id": "a", "start_timestamp_utc": "2026-07-19T01:00:00Z"}, {"episode_id": "b", "start_timestamp_utc": "2026-07-19T02:00:00Z"}, {"episode_id": "c", "start_timestamp_utc": "2026-07-20T02:00:00Z"}, {"episode_id": "d", "start_timestamp_utc": "2026-07-20T03:00:00Z"}]
        self.assertTrue(_date_concentration(rows, ["2026-07-19", "2026-07-20"])["pass"])
        rows.append({"episode_id": "e", "start_timestamp_utc": "2026-07-19T03:00:00Z"})
        self.assertFalse(_date_concentration(rows, ["2026-07-19", "2026-07-20"])["pass"])

    def test_rolling_snapshots_do_not_include_future_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "events.csv").write_text("event_id,event_timestamp_utc,event_timestamp_jst\na,2026-07-19T01:00:00Z,2026-07-19 10:00:00+09:00\nb,2026-07-21T01:00:00Z,2026-07-21 10:00:00+09:00\n")
            (root / "episodes.csv").write_text("episode_id,start_timestamp_utc\ne1,2026-07-19T01:00:00Z\ne2,2026-07-21T01:00:00Z\n")
            snapshots = _rolling_snapshots(root / "events.csv", root / "episodes.csv", ["2026-07-19", "2026-07-21"], {"directional_precision": 0.1})
            self.assertEqual(["e1"], snapshots[0]["episode_ids"])

    def test_p8_missing_caps_recommendation_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual("missing", _p8_status(Path(temp) / "facts.csv", Path(temp) / "report.json")["status"])

    def test_atomic_multi_parent_deterministic_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = {root / "a" / "results.csv": b"a\n", root / "b" / "issues.csv": b"b\n", root / "c" / "report.json": b"{}\n", root / "d" / "report.md": b"# x\n"}
            _atomic(paths, True)
            before = {path: path.read_bytes() for path in paths}
            _atomic(paths, True)
            self.assertEqual(before, {path: path.read_bytes() for path in paths})

    def test_atomic_rollback_after_promotion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = {root / "a" / "a": b"old-a", root / "b" / "b": b"old-b", root / "c" / "c": b"old-c", root / "d" / "d": b"old-d"}
            _atomic(paths, True)
            original = {path: path.read_bytes() for path in paths}
            real_replace = __import__("os").replace
            calls = {"count": 0}
            def fail_once(source, target):
                calls["count"] += 1
                if calls["count"] == 7:
                    raise OSError("forced")
                return real_replace(source, target)
            with patch("src.feedback.macro_p9_proposal_engine.os.replace", side_effect=fail_once):
                with self.assertRaises(OSError):
                    _atomic({path: b"new" for path in paths}, True)
            self.assertEqual(original, {path: path.read_bytes() for path in paths})


if __name__ == "__main__":
    unittest.main()
