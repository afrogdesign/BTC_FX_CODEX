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
        champion_metrics = {"directional_precision": .5, "large_move_recall": .2, "false_warning_rate": .3, "opposite_move_rate": .2, "whipsaw_rate": .1, "burden_per_jst_day": 2.0, "balanced_no_expansion_rate": .2}
        improved = dict(champion_metrics, large_move_recall=.3)
        self.assertEqual((True, 1), _dominates(improved, champion_metrics))
        self.assertEqual((False, 0), _dominates(dict(champion_metrics, false_warning_rate=None), champion_metrics))

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
