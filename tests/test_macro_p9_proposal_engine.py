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
    _performance_snapshot_dates,
    _rolling_snapshots,
    _split_comparison,
    _write_snapshot_inputs,
    _expand_space,
    _p8_status,
    _validate_champion_manifest,
    candidate_id,
    run_macro_p9_proposal_engine,
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

    def test_split_degradation_uses_metric_direction_for_all_guarded_metrics(self):
        keys = ("directional_precision", "large_move_recall", "false_warning_rate", "opposite_move_rate", "whipsaw_rate", "burden_per_jst_day")
        champion_summary = {"splits": {"reliable_level_acceptance_corridor": {"direction": {"UP": {key: 0.5 for key in keys}}}}}
        challenger = {"directional_precision": 0.4, "large_move_recall": 0.4, "false_warning_rate": 0.6, "opposite_move_rate": 0.6, "whipsaw_rate": 0.6, "burden_per_jst_day": 1.1}
        result = _split_comparison(champion_summary, {"splits": {"reliable_level_acceptance_corridor": {"direction": {"UP": challenger}}}}, "reliable_level_acceptance_corridor", ("direction",), keys)
        self.assertTrue(result["direction"]["UP"]["degradation"])

    def test_split_missing_required_metric_is_unavailable(self):
        keys = ("directional_precision", "large_move_recall")
        summary = {"splits": {"policy": {"direction": {"UP": {"directional_precision": 0.5}}}}}
        result = _split_comparison(summary, summary, "policy", ("direction",), keys)
        self.assertEqual("unavailable", result["direction"]["UP"]["status"])
        self.assertIn("large_move_recall", result["direction"]["UP"]["missing_metrics"])

    def test_concentration_boundary_and_failure(self):
        rows = [{"episode_id": "a", "start_timestamp_utc": "2026-07-19T01:00:00Z"}, {"episode_id": "b", "start_timestamp_utc": "2026-07-19T02:00:00Z"}, {"episode_id": "c", "start_timestamp_utc": "2026-07-20T02:00:00Z"}, {"episode_id": "d", "start_timestamp_utc": "2026-07-20T03:00:00Z"}]
        self.assertTrue(_date_concentration(rows, ["2026-07-19", "2026-07-20"])["pass"])
        rows.append({"episode_id": "e", "start_timestamp_utc": "2026-07-19T03:00:00Z"})
        self.assertFalse(_date_concentration(rows, ["2026-07-19", "2026-07-20"])["pass"])

    def test_rolling_snapshots_do_not_include_future_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "signals.csv").write_text("signal_id,timestamp_utc,timestamp_jst,macro_context_only\na,2026-07-19T01:00:00Z,2026-07-19 10:00:00+09:00,false\nb,2026-07-21T01:00:00Z,2026-07-21 10:00:00+09:00,false\nc,2026-07-22T01:00:00Z,2026-07-22 10:00:00+09:00,false\n")
            self.assertEqual([("2026-07-19", "2026-07-19T01:00:00Z"), ("2026-07-21", "2026-07-21T01:00:00Z"), ("2026-07-22", "2026-07-22T01:00:00Z")], _performance_snapshot_dates(root / "signals.csv"))

    def test_snapshot_date_falls_back_from_utc_at_jst_boundary(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "signals.csv"
            path.write_text("timestamp_utc,timestamp_jst,macro_context_only\n2026-07-19T14:59:00Z,,false\n2026-07-19T15:00:00Z,,false\n")
            self.assertEqual([("2026-07-19", "2026-07-19T14:59:00Z"), ("2026-07-20", "2026-07-19T15:00:00Z")], _performance_snapshot_dates(path))

    def test_snapshot_inputs_are_cutoff_bounded(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = {}
            for name, rows in {
                "signals": "timestamp_utc,macro_context_only\n2026-07-19T01:00:00Z,false\n2026-07-19T02:00:00Z,false\n",
                "ohlcv_15m": "timestamp_utc\n2026-07-19T00:30:00Z\n2026-07-19T01:00:00Z\n",
                "ohlcv_1h": "timestamp_utc\n2026-07-19T00:00:00Z\n2026-07-19T01:00:00Z\n",
                "ohlcv_4h": "timestamp_utc\n2026-07-18T22:00:00Z\n2026-07-19T01:00:00Z\n",
            }.items():
                path = root / f"{name}.csv"
                path.write_text(rows)
                paths[name] = path
            bounded = _write_snapshot_inputs(paths, "2026-07-19T01:00:00Z", root / "bounded")
            self.assertEqual(1, len(bounded["signals"].read_text().splitlines()) - 1)
            self.assertEqual(1, len(bounded["ohlcv_15m"].read_text().splitlines()) - 1)
            self.assertEqual(1, len(bounded["ohlcv_1h"].read_text().splitlines()) - 1)
            self.assertEqual(0, len(bounded["ohlcv_4h"].read_text().splitlines()) - 1)

    def test_rolling_orchestration_reuses_champion_cache_and_handles_runless_candidate(self):
        parameters = {"left_window": 2, "right_window": 2}
        fixed = {"performance_start_utc": "2026-07-18T00:00:00Z", "performance_end_utc": "2026-07-21T00:00:00Z"}
        dates = [("2026-07-19", "2026-07-19T01:00:00Z"), ("2026-07-20", "2026-07-20T01:00:00Z")]
        calls = []

        def fake_run(candidate, paths, values, temp_root):
            calls.append(candidate)
            return {"candidate_id": candidate_id(candidate), "parameters": candidate, "m1": temp_root / "m1", "m3": temp_root / "m3"}

        def fake_record(date, cutoff, paths, run, m1, m3, validation_dates, reasons, status, comparison, pareto, improved):
            return {"snapshot_jst_date": date, "m3_eligible_jst_dates": [date], "m3_validation_jst_dates": [date], "m1_opportunity_id_fingerprint": "same", "m1_guarded_metrics": m1, "m3_guarded_metrics": m3}

        metrics = {"directional_precision": 0.5, "large_move_recall": 0.5, "false_warning_rate": 0.1, "opposite_move_rate": 0.1, "whipsaw_rate": 0.1, "burden_per_jst_day": 1.0, "resolved_up_count": 10, "resolved_down_count": 10}
        with patch("src.feedback.macro_p9_proposal_engine._performance_snapshot_dates", return_value=dates), patch("src.feedback.macro_p9_proposal_engine._write_snapshot_inputs", side_effect=lambda paths, cutoff, root: paths), patch("src.feedback.macro_p9_proposal_engine._run_candidate", side_effect=fake_run), patch("src.feedback.macro_p9_proposal_engine._read_json", return_value={"recommendation": {"validation_dates": ["2026-07-19"]}}), patch("src.feedback.macro_p9_proposal_engine._m1_metrics", return_value=metrics), patch("src.feedback.macro_p9_proposal_engine._m3_metrics", return_value=metrics), patch("src.feedback.macro_p9_proposal_engine._snapshot_record", side_effect=fake_record), patch("src.feedback.macro_p9_proposal_engine._id_fingerprint", return_value="same"), patch("src.feedback.macro_p9_proposal_engine._m1_quality_ok", return_value=True), patch("src.feedback.macro_p9_proposal_engine._m3_quality_ok", return_value=True), patch("src.feedback.macro_p9_proposal_engine._date_concentration", return_value={"pass": True}):
            champion_cache, _ = _rolling_snapshots({"signals": Path("signals.csv")}, parameters, fixed, parameters, Path("rolling-champion"))
            calls.clear()
            _, challenger_snapshots = _rolling_snapshots({"signals": Path("signals.csv")}, {"left_window": 3, "right_window": 2}, fixed, parameters, Path("rolling-challenger"), champion_cache=champion_cache)
        self.assertEqual(2, len(champion_cache))
        self.assertEqual(2, len(challenger_snapshots))
        self.assertEqual([{"left_window": 3, "right_window": 2}, {"left_window": 3, "right_window": 2}], calls)

    def test_lightweight_full_orchestration_fixture_is_cached_and_deterministic(self):
        metrics = {"directional_precision": 0.5, "large_move_recall": 0.5, "false_warning_rate": 0.1, "opposite_move_rate": 0.1, "whipsaw_rate": 0.1, "burden_per_jst_day": 1.0, "resolved_up_count": 10, "resolved_down_count": 10}
        m1_summary = {"schema_version": "macro_structure_volatility_replay.v1", "method_version": "macro_structure_volatility_replay.v1", "recommendation_gate": {"validation_policy_metrics": {"reliable_level_acceptance_corridor": metrics}}, "coverage": {"continuity_pass": True}}
        m3_summary = {"schema_version": "macro_next_regime_replay.v1", "method_version": "macro_next_regime_replay.v1", "recommendation": {"validation_candidate_metrics": {"3h": metrics, "6h": metrics, "12h": metrics, "24h": metrics}, "validation_dates": ["2026-07-19"], "validation_data_quality_pass": True}, "coverage": {"continuity_pass": True}}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = {name: root / f"{name}.csv" for name in ("signals", "ohlcv_15m", "ohlcv_1h", "ohlcv_4h", "m1_events", "m1_levels", "m1_misses", "m3_events", "m3_episodes")}
            for path in paths.values():
                path.write_text("fixture\n")
            m1_json = root / "m1.json"; m3_json = root / "m3.json"; champion_path = root / "champion.json"; space_path = root / "space.json"
            m1_json.write_text("{}"); m3_json.write_text("{}")
            champion_value = champion({"left_window": 2, "right_window": 2, "cutoff_utc": "x", "performance_start_utc": "y", "performance_end_utc": "z"})
            space_value = {"schema_version": SPACE_SCHEMA, "method_version": METHOD_VERSION, "one_at_a_time": [{"parameter": "left_window", "values": [3]}], "combinations": []}
            champion_path.write_text("{}"); space_path.write_text("{}")
            output_paths = {name: root / name for name in ("results.csv", "issues.csv", "report.json", "report.md")}
            calls = []

            def fake_run(candidate, input_paths, fixed, temp_root):
                calls.append((candidate, fixed.get("cutoff_utc")))
                m1_dir = temp_root / "m1"; m3_dir = temp_root / "m3"
                m1_dir.mkdir(parents=True); m3_dir.mkdir(parents=True)
                (m1_dir / "replay.json").write_text("{}")
                (m3_dir / "replay.json").write_text("{}")
                return {"candidate_id": candidate_id(candidate), "parameters": candidate, "m1": m1_dir, "m3": m3_dir}

            def fake_read_json(path):
                if path == champion_path:
                    return champion_value
                if path == space_path:
                    return space_value
                if path == m1_json or (path.name == "replay.json" and path.parent.name == "m1"):
                    return m1_summary
                return m3_summary

            def fake_read_csv(path, required):
                if "opportunity_id" in required:
                    return [{"opportunity_id": "candidate-opportunity", "root_cause": "reliable", "reason": "fixture"}]
                if "level_id" in required:
                    return [{"level_id": "level"}]
                if "record_id" in required:
                    return [{"record_id": "record", "event_id": "event", "signal_id": "signal", "event_timestamp_jst": "2026-07-19 10:00:00+09:00"}]
                if "episode_id" in required:
                    return [{"episode_id": "episode", "policy": "candidate", "start_timestamp_utc": "2026-07-19T01:00:00Z"}]
                return [{"event_id": "event", "signal_id": "signal"}]

            def fake_rolling(input_paths, parameters, fixed, champion_pair, temp_root, champion_cache=None):
                snapshot = {"snapshot_jst_date": "2026-07-19", "m3_eligible_jst_dates": ["2026-07-19"], "m3_validation_jst_dates": ["2026-07-19"], "m1_guarded_metrics": metrics, "m3_guarded_metrics": metrics, "m3_diagnostic_horizons": {}, "validation_date_concentration": {"pass": True}, "m1_quality_status": "pass", "m3_quality_status": "pass", "status": "established", "comparison_eligible": True, "issue_lineage": [{"opportunity_id": f"{candidate_id(parameters)}-opportunity", "root_cause": "reliable", "reason": "fixture", "event_family": "level"}]}
                if champion_cache is None:
                    return [snapshot], []
                return [], [snapshot]

            def execute():
                return run_macro_p9_proposal_engine(signals=paths["signals"], ohlcv_15m=paths["ohlcv_15m"], ohlcv_1h=paths["ohlcv_1h"], ohlcv_4h=paths["ohlcv_4h"], m1_events_csv=paths["m1_events"], m1_levels_csv=paths["m1_levels"], m1_misses_csv=paths["m1_misses"], m1_replay_json=m1_json, m3_events_csv=paths["m3_events"], m3_episodes_csv=paths["m3_episodes"], m3_replay_json=m3_json, champion_manifest=champion_path, proposal_space_manifest=space_path, output_results_csv=output_paths["results.csv"], output_issues_csv=output_paths["issues.csv"], output_json=output_paths["report.json"], output_md=output_paths["report.md"], replace_output=True)

            with patch("src.feedback.macro_p9_proposal_engine._fingerprints", return_value={}), patch("src.feedback.macro_p9_proposal_engine._artifact_signature", return_value={}), patch("src.feedback.macro_p9_proposal_engine._read_json", side_effect=fake_read_json), patch("src.feedback.macro_p9_proposal_engine._read_csv", side_effect=fake_read_csv), patch("src.feedback.macro_p9_proposal_engine._run_candidate", side_effect=fake_run), patch("src.feedback.macro_p9_proposal_engine._rolling_snapshots", side_effect=fake_rolling), patch("src.feedback.macro_p9_proposal_engine._jst_dates", return_value=["2026-07-19"]), patch("src.feedback.macro_p9_proposal_engine._m1_quality_ok", return_value=True), patch("src.feedback.macro_p9_proposal_engine._m3_quality_ok", return_value=True), patch("src.feedback.macro_p9_proposal_engine._data_quality_ok", return_value=True), patch("src.feedback.macro_p9_proposal_engine._m1_metrics", return_value=metrics), patch("src.feedback.macro_p9_proposal_engine._m3_metrics", return_value=metrics), patch("src.feedback.macro_p9_proposal_engine._m3_diagnostics", return_value={}), patch("src.feedback.macro_p9_proposal_engine._date_concentration", return_value={"pass": True}), patch("src.feedback.macro_p9_proposal_engine._split_comparison", return_value={}):
                first = execute()
                first_bytes = {path: path.read_bytes() for path in output_paths.values()}
                calls.clear()
                second = execute()
                self.assertEqual(first, second)
                self.assertEqual(first_bytes, {path: path.read_bytes() for path in output_paths.values()})
            self.assertEqual(2, first["candidate_count"])
            self.assertEqual(4, first["output_count"])
            self.assertEqual(1, sum(1 for candidate, cutoff in calls if candidate == {"left_window": 2, "right_window": 2}))

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
