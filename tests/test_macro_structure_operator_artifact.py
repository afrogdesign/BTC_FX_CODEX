from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.feedback.macro_structure_operator_artifact import render_macro_structure_operator


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _zone(level_id: str, role: str, center: float, band: str = "medium") -> dict[str, object]:
    return {
        "level_id": level_id, "side": "low" if role == "support" else "high", "role": role,
        "low": center - 1, "high": center + 1, "center": center, "source_timeframes": "1h,4h",
        "first_seen_at": "2026-01-01T00:00:00+00:00", "last_confirmed_at": "2026-01-01T00:45:00+00:00",
        "touch_count": 2, "clean_rejection_count": 1, "break_count": 0, "false_break_reclaim_count": 0,
        "lifecycle": "accepted", "reliability_score": 62.5, "reliability_band": band,
        "distance_from_price_pct": abs(center - 104) / 104 * 100, "distance_from_price_atr": abs(center - 104),
        "reason_codes": ["prior_only"],
    }


def _make_inputs(root: Path) -> tuple[Path, Path, Path]:
    snapshot_root = root / "snapshot"
    history_root = root / "history"
    run = snapshot_root / "run_fixture"
    history = history_root / "history_fixture"
    run.mkdir(parents=True)
    history.mkdir(parents=True)
    snap = {
        "schema_version": "macro_structure_daily_operation.v1", "method_version": "macro_structure_daily_operation.v1",
        "run_id": "run_fixture", "snapshot_id": "snapshot_fixture", "symbol": "BTC_USDT",
        "as_of_utc": "2026-01-02T01:00:00+00:00", "as_of_jst": "2026-01-02T10:00:00+09:00",
        "evaluated_at_utc": "2026-01-02T02:00:00+00:00", "evaluated_at_jst": "2026-01-02T11:00:00+09:00",
        "current_price": 199.0, "structure_state": "transition", "price_location": "upper_half", "location_percentile": 60,
        "support_zones": [_zone("level_support", "support", 100)], "resistance_zones": [_zone("level_resistance", "resistance", 110)],
        "nearest_reliable_support": _zone("level_support", "support", 100), "nearest_reliable_resistance": _zone("level_resistance", "resistance", 110),
        "next_upside_target": _zone("level_resistance", "resistance", 110), "next_downside_target": _zone("level_support", "support", 100),
        "upside_obstruction": "insufficient", "downside_obstruction": "insufficient", "volatility_state": "stable",
        "expansion_risk": "low", "directional_activation": "NONE", "stale_status": "current", "stale_timeframes": [],
        "freshness": {"15m": {"status": "current"}}, "continuity_status": "continuous", "data_quality_status": "ok", "result_status": "ok",
        "reason_codes": [], "reliability_band_counts": {"high": 0, "medium": 2, "low": 0, "insufficient": 0},
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }
    _write_json(run / "macro_structure_snapshot.json", snap)
    _write_json(run / "run_manifest.json", {"schema_version": snap["schema_version"], "method_version": snap["method_version"], "run_id": "run_fixture", "snapshot_id": "snapshot_fixture", "as_of_utc": snap["as_of_utc"], "evaluated_at_utc": snap["evaluated_at_utc"], "source": "public_ohlcv_only", "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False})
    (run / "macro_structure_snapshot.md").write_text("# fixture\n", encoding="utf-8")
    level_fields = ["level_id", "side", "role", "low", "high", "center", "lifecycle", "reliability_band", "reliability_score"]
    with (run / "macro_level_reliability.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=level_fields); writer.writeheader()
        for item in (snap["support_zones"][0], snap["resistance_zones"][0]): writer.writerow({field: item[field] for field in level_fields})
    _write_json(snapshot_root / "latest.json", {"run_id": "run_fixture", "snapshot_id": "snapshot_fixture", "artifact_dir": "run_fixture", "symbol": "BTC_USDT"})

    evaluation = {"run_id": "run_fixture", "snapshot_id": "snapshot_fixture", "checkpoint_id": "checkpoint_fixture", "as_of_utc": snap["as_of_utc"], "evaluated_at_utc": snap["evaluated_at_utc"], "stale_status": "current", "continuity_status": "continuous", "data_quality_status": "ok", "result_status": "ok", "reason_codes": []}
    hist = {"schema_version": "macro_structure_history_operation.v2", "method_version": "macro_structure_history_operation.v2", "history_id": "history_fixture", "symbol": "BTC_USDT", "result_status": "insufficient_history", "source_run_count": 1, "evaluation_count": 1, "structural_checkpoint_count": 1, "first_as_of_utc": snap["as_of_utc"], "latest_as_of_utc": snap["as_of_utc"], "latest_evaluated_at_utc": snap["evaluated_at_utc"], "source_digest": "digest", "evaluation_history": [evaluation], "structural_checkpoints": [{"checkpoint_id": "checkpoint_fixture", "canonical_structural_run_id": "run_fixture", "latest_evaluation_run_id": "run_fixture", "latest_evaluation": evaluation}], "structure_changes": [], "level_history": [], "safety_boundary": snap["safety_boundary"]}
    _write_json(history / "macro_structure_history.json", hist)
    _write_json(history / "run_manifest.json", {"schema_version": hist["schema_version"], "method_version": hist["method_version"], "history_id": "history_fixture", "symbol": "BTC_USDT", "source_runs": ["run_fixture"], "source": "public_mops1_artifacts_only", "report_only": True, "automatic_order_allowed": False, "private_actual_trade_input": False})
    (history / "macro_structure_history.md").write_text("# fixture\n", encoding="utf-8")
    (history / "macro_snapshot_history.csv").write_text("fixture\n", encoding="utf-8")
    (history / "macro_level_history.csv").write_text("fixture\n", encoding="utf-8")
    (history / "macro_structure_changes.csv").write_text("fixture\n", encoding="utf-8")
    _write_json(history_root / "latest.json", {"history_id": "history_fixture", "artifact_dir": "history_fixture", "symbol": "BTC_USDT"})

    ohlcv = root / "ohlcv_15m.csv"
    with ohlcv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "open", "high", "low", "close", "interval", "symbol"]); writer.writeheader()
        for index in range(100):
            close = 100 + index
            writer.writerow({"timestamp_utc": (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=15 * index)).isoformat().replace("+00:00", "Z"), "open": close, "high": close + 1, "low": close - 1, "close": close, "interval": "15m", "symbol": "BTC_USDT"})
    return snapshot_root, history_root, ohlcv


def _make_rich_inputs(root: Path) -> tuple[Path, Path, Path]:
    snapshot_root, history_root, ohlcv = _make_inputs(root)
    final_dir = snapshot_root / "run_fixture"
    snapshot_path = final_dir / "macro_structure_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    support_near = _zone("level_support_near", "support", 198, "high")
    support_far = _zone("level_support_far", "support", 180, "medium")
    resistance_near = _zone("level_resistance_near", "resistance", 200, "high")
    resistance_far = _zone("level_resistance_far", "resistance", 220, "medium")
    weak = _zone("level_weak", "support", 170, "low")
    snapshot["support_zones"] = [support_near, support_far, weak]
    snapshot["resistance_zones"] = [resistance_near, resistance_far]
    snapshot["nearest_reliable_support"] = support_near
    snapshot["nearest_reliable_resistance"] = resistance_near
    snapshot["next_upside_target"] = resistance_far
    snapshot["next_downside_target"] = "insufficient"
    snapshot["upside_obstruction"] = resistance_near
    snapshot["downside_obstruction"] = "insufficient"
    _write_json(snapshot_path, snapshot)
    base_manifest = json.loads((final_dir / "run_manifest.json").read_text(encoding="utf-8"))
    run_specs = [
        ("run_early", "snapshot_early", "checkpoint_early", "2026-01-01T23:00:00+00:00", "2026-01-01T23:30:00+00:00"),
        ("run_mid", "snapshot_mid", "checkpoint_mid", "2026-01-02T00:00:00+00:00", "2026-01-02T00:30:00+00:00"),
        ("run_recheck", "snapshot_recheck", "checkpoint_final", "2026-01-02T01:00:00+00:00", "2026-01-02T01:30:00+00:00"),
        ("run_fixture", "snapshot_fixture", "checkpoint_final", "2026-01-02T01:00:00+00:00", "2026-01-02T02:00:00+00:00"),
    ]
    for run_id, snapshot_id, checkpoint_id, as_of, evaluated in run_specs:
        target = snapshot_root / run_id
        if target != final_dir:
            shutil.copytree(final_dir, target)
        item = json.loads((target / "macro_structure_snapshot.json").read_text(encoding="utf-8"))
        item.update({"run_id": run_id, "snapshot_id": snapshot_id, "as_of_utc": as_of, "as_of_jst": datetime.fromisoformat(as_of).astimezone(timezone(timedelta(hours=9))).isoformat(), "evaluated_at_utc": evaluated, "evaluated_at_jst": datetime.fromisoformat(evaluated).astimezone(timezone(timedelta(hours=9))).isoformat()})
        _write_json(target / "macro_structure_snapshot.json", item)
        manifest = dict(base_manifest); manifest.update({"run_id": run_id, "snapshot_id": snapshot_id, "as_of_utc": as_of, "evaluated_at_utc": evaluated})
        _write_json(target / "run_manifest.json", manifest)
    evaluations = []
    for run_id, snapshot_id, checkpoint_id, as_of, evaluated in run_specs:
        evaluations.append({"run_id": run_id, "snapshot_id": snapshot_id, "checkpoint_id": checkpoint_id, "as_of_utc": as_of, "evaluated_at_utc": evaluated, "stale_status": "stale" if run_id == "run_recheck" else "current", "continuity_status": "discontinuous" if run_id == "run_recheck" else "continuous", "data_quality_status": "discontinuous" if run_id == "run_recheck" else "ok", "result_status": "ok", "reason_codes": ["stale_ohlcv_15m"] if run_id == "run_recheck" else []})
    changes = [
        {"change_type": "snapshot_transition", "field": "structure_state", "checkpoint_id": "checkpoint_mid", "level_id": "", "previous_value": "transition", "current_value": "reversal"},
        {"change_type": "level_transition", "field": "reliability_band", "checkpoint_id": "checkpoint_mid", "level_id": "level_support_near", "previous_value": "medium", "current_value": "high"},
        {"change_type": "level_transition", "field": "role", "checkpoint_id": "checkpoint_mid", "level_id": "level_support_far", "previous_value": "resistance", "current_value": "support"},
        {"change_type": "level_transition", "field": "lifecycle", "checkpoint_id": "checkpoint_mid", "level_id": "level_resistance_near", "previous_value": "forming", "current_value": "accepted"},
        {"change_type": "level_transition", "field": "geometry", "checkpoint_id": "checkpoint_mid", "level_id": "level_resistance_far", "previous_value": "changed", "current_value": "changed"},
        {"change_type": "absent_from_latest", "field": "level_id", "checkpoint_id": "checkpoint_final", "level_id": "level_absent", "previous_value": "level_absent", "current_value": "level_absent"},
        {"change_type": "reappeared", "field": "level_id", "checkpoint_id": "checkpoint_final", "level_id": "level_reappeared", "previous_value": "level_reappeared", "current_value": "level_reappeared"},
    ]
    history_dir = history_root / "history_fixture"
    history = json.loads((history_dir / "macro_structure_history.json").read_text(encoding="utf-8"))
    history.update({"result_status": "ok", "source_run_count": 4, "evaluation_count": 4, "structural_checkpoint_count": 3, "first_as_of_utc": run_specs[0][3], "latest_as_of_utc": run_specs[-1][3], "latest_evaluated_at_utc": run_specs[-1][4], "evaluation_history": evaluations, "structural_checkpoints": [{"checkpoint_id": "checkpoint_early", "canonical_structural_run_id": "run_early", "latest_evaluation_run_id": "run_early"}, {"checkpoint_id": "checkpoint_mid", "canonical_structural_run_id": "run_mid", "latest_evaluation_run_id": "run_mid"}, {"checkpoint_id": "checkpoint_final", "canonical_structural_run_id": "run_recheck", "latest_evaluation_run_id": "run_fixture"}], "structure_changes": changes})
    _write_json(history_dir / "macro_structure_history.json", history)
    manifest = json.loads((history_dir / "run_manifest.json").read_text(encoding="utf-8")); manifest.update({"source_runs": [spec[0] for spec in run_specs], "source_run_count": 4, "evaluation_count": 4, "structural_checkpoint_count": 3}); _write_json(history_dir / "run_manifest.json", manifest)
    _write_json(history_root / "latest.json", {"history_id": "history_fixture", "artifact_dir": "history_fixture", "symbol": "BTC_USDT"})
    return snapshot_root, history_root, ohlcv


def _make_4h_csv(root: Path, *, invalid: bool = False) -> Path:
    path = root / "ohlcv_4h.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "open", "high", "low", "close", "interval", "symbol"])
        writer.writeheader()
        for index in range(4):
            start = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=4 * index)
            writer.writerow({"timestamp_utc": start.isoformat().replace("+00:00", "Z"), "open": 100 + index, "high": 102 + index, "low": 99 + index, "close": 101 + index, "interval": "1h" if invalid else "4h", "symbol": "BTC_USDT"})
        writer.writerow({"timestamp_utc": "2026-01-02T01:00:00Z", "open": 200, "high": 201, "low": 199, "close": 200, "interval": "4h", "symbol": "BTC_USDT"})
    return path


class MacroStructureOperatorArtifactTests(unittest.TestCase):
    def test_valid_4h_input_is_primary_and_excludes_future_candles(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); ohlcv_4h = _make_4h_csv(root); output = root / "operator"
            result = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, ohlcv_4h_csv=ohlcv_4h, output_root=output)
            artifact = output / result["artifact_dir"]
            html_text = (artifact / "macro_structure_operator.html").read_text(encoding="utf-8")
            model = json.loads((artifact / "macro_structure_operator.json").read_text(encoding="utf-8"))
            self.assertTrue(result["ok"])
            self.assertLess(html_text.index("4H Macro Structure Chart"), html_text.index("Supplemental 15m manual-confirmation view"))
            self.assertIn("1H+4H", html_text)
            self.assertEqual(model["chart_model_4h"]["candle_count"], 4)
            self.assertNotIn("2026-01-02T01:00:00Z", html_text)
            self.assertIn("ohlcv_4h_fingerprint", model)
            self.assertIn("report-only", html_text)
            self.assertIn("no automatic order", html_text)

    def test_invalid_4h_fails_closed_and_preserves_latest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); valid_4h = _make_4h_csv(root); output = root / "operator"
            valid = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, ohlcv_4h_csv=valid_4h, output_root=output)
            latest_before = (output / "latest.json").read_bytes()
            invalid_4h = _make_4h_csv(root, invalid=True)
            invalid = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, ohlcv_4h_csv=invalid_4h, output_root=output)
            self.assertTrue(valid["ok"])
            self.assertEqual(invalid["error_code"], "ohlcv_interval_invalid")
            self.assertEqual((output / "latest.json").read_bytes(), latest_before)

    def test_without_4h_preserves_15m_chart_model_and_supplemental_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            result = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            html_text = (output / result["artifact_dir"] / "macro_structure_operator.html").read_text(encoding="utf-8")
            model = json.loads((output / result["artifact_dir"] / "macro_structure_operator.json").read_text(encoding="utf-8"))
            self.assertTrue(result["ok"])
            self.assertEqual(model["chart_model"]["timeframe"], "15m")
            self.assertNotIn("chart_model_4h", model)
            self.assertIn("Supplemental 15m manual-confirmation view", html_text)
    def test_empty_optional_references_are_absent_but_displayed_zones_stay_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            snap_path = snapshot / "run_fixture" / "macro_structure_snapshot.json"
            data = json.loads(snap_path.read_text(encoding="utf-8"))
            data.update({
                "nearest_reliable_support": {}, "nearest_reliable_resistance": {},
                "next_upside_target": {}, "next_downside_target": {},
                "upside_obstruction": None, "downside_obstruction": "NONE",
                "result_status": "insufficient", "reliability_band_counts": {"high": 1, "medium": 1, "low": 0, "insufficient": 0},
            })
            _write_json(snap_path, data)
            result = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertTrue(result["ok"])
            model = json.loads((output / result["artifact_dir"] / "macro_structure_operator.json").read_text(encoding="utf-8"))
            self.assertEqual({item["level_id"] for item in model["chart_model"]["overlays"]}, {"level_support", "level_resistance"})
            self.assertEqual(model["zones"]["displayed_support_count"], 1)
            self.assertEqual(model["zones"]["displayed_resistance_count"], 1)
            self.assertEqual(model["source_trace_map"]["references"], {})

    def test_empty_displayed_zone_and_nonempty_partial_optional_reference_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            snap_path = snapshot / "run_fixture" / "macro_structure_snapshot.json"
            data = json.loads(snap_path.read_text(encoding="utf-8"))
            data["support_zones"] = [{}]
            _write_json(snap_path, data)
            self.assertEqual(render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)["error_code"], "zone_evidence_invalid")
            data["support_zones"] = [_zone("level_support", "support", 100)]
            data["nearest_reliable_resistance"] = {"level_id": "partial"}
            _write_json(snap_path, data)
            self.assertEqual(render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)["error_code"], "zone_evidence_invalid")

    def test_low_optional_reference_is_not_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            snap_path = snapshot / "run_fixture" / "macro_structure_snapshot.json"
            data = json.loads(snap_path.read_text(encoding="utf-8")); data["next_upside_target"] = _zone("low_target", "resistance", 120, "low")
            _write_json(snap_path, data)
            result = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertTrue(result["ok"])
            model = json.loads((output / result["artifact_dir"] / "macro_structure_operator.json").read_text(encoding="utf-8"))
            self.assertNotIn("low_target", {item["level_id"] for item in model["chart_model"]["overlays"]})

    def test_complete_chart_first_artifact_is_deterministic_and_report_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            first = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            second = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertTrue(first["ok"]); self.assertEqual(first["operator_artifact_id"], second["operator_artifact_id"])
            artifact = output / first["artifact_dir"]
            self.assertEqual(sorted(path.name for path in artifact.iterdir()), sorted(("macro_structure_operator.html", "macro_structure_operator.json", "macro_structure_operator.md", "run_manifest.json")))
            html_text = (artifact / "macro_structure_operator.html").read_text(encoding="utf-8")
            self.assertLess(html_text.index('id="status"'), html_text.index('id="chart"'))
            self.assertIn("tactical Entry / SL / TP overlays are not included", html_text)
            model = json.loads((artifact / "macro_structure_operator.json").read_text(encoding="utf-8"))
            self.assertEqual(model["schema_version"], "macro_structure_operator_artifact.v2")
            self.assertEqual(model["selected_history_id"], "history_fixture")
            self.assertEqual(model["selected_structural_checkpoint_id"], "checkpoint_fixture")
            self.assertEqual(model["zones"]["displayed_support_count"], 1)
            self.assertEqual(model["chart_model"]["candle_count"], 96)
            self.assertIn("level_support", html_text)
            self.assertIn("source_timeframes", html_text)
            self.assertIn("data_quality=ok", html_text)
            self.assertIn("macro_structure_operator_artifact.v2", (artifact / "run_manifest.json").read_text(encoding="utf-8"))

    def test_source_boundary_and_price_mismatch_fail_closed_without_latest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            valid = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            latest_before = (output / "latest.json").read_bytes()
            ohlcv.write_text(ohlcv.read_text(encoding="utf-8").replace(",199,200,198,199,", ",299,300,298,299,"), encoding="utf-8")
            invalid = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertTrue(valid["ok"]); self.assertEqual(invalid["error_code"], "snapshot_price_ohlcv_mismatch"); self.assertEqual((output / "latest.json").read_bytes(), latest_before)

    def test_v1_directory_is_preserved_and_v2_conflict_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            legacy = output / "operator_legacy_v1"; legacy.mkdir(parents=True)
            for name in ("macro_structure_operator.html", "macro_structure_operator.json", "macro_structure_operator.md", "run_manifest.json"):
                (legacy / name).write_bytes(b"legacy")
            first = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            latest_before = (output / "latest.json").read_bytes()
            artifact = output / first["artifact_dir"]
            (artifact / "macro_structure_operator.html").write_bytes(b"conflict")
            conflict = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertEqual(conflict["error_code"], "existing_operator_conflict")
            self.assertEqual((artifact / "macro_structure_operator.html").read_bytes(), b"conflict")
            self.assertEqual((output / "latest.json").read_bytes(), latest_before)
            self.assertEqual((legacy / "run_manifest.json").read_bytes(), b"legacy")

    def test_jst_mismatch_and_malformed_displayed_evidence_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            snap_path = snapshot / "run_fixture" / "macro_structure_snapshot.json"
            data = json.loads(snap_path.read_text(encoding="utf-8")); data["as_of_jst"] = "2026-01-02T01:00:00+00:00"; _write_json(snap_path, data)
            invalid_jst = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertEqual(invalid_jst["error_code"], "snapshot_jst_mismatch")
            data["as_of_jst"] = "2026-01-02T10:00:00+09:00"; data["support_zones"][0]["center"] = "not-a-number"; _write_json(snap_path, data)
            invalid_zone = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertEqual(invalid_zone["error_code"], "zone_evidence_invalid")

    def test_snapshot_must_be_latest_structural_checkpoint_and_final_eval(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_inputs(root); output = root / "operator"
            history_path = history / "history_fixture" / "macro_structure_history.json"
            data = json.loads(history_path.read_text(encoding="utf-8"))
            data["structural_checkpoints"] = [{"checkpoint_id": "checkpoint_fixture", "latest_evaluation_run_id": "run_fixture"}, {"checkpoint_id": "checkpoint_later", "latest_evaluation_run_id": "run_later"}]
            _write_json(history_path, data)
            invalid = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertEqual(invalid["error_code"], "history_current_snapshot_not_latest_checkpoint")
            data["structural_checkpoints"] = []
            _write_json(history_path, data)
            empty = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertEqual(empty["error_code"], "history_checkpoint_missing")

    def test_rich_history_fixture_charts_all_reliable_zones_and_categories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); snapshot, history, ohlcv = _make_rich_inputs(root); output = root / "operator"
            result = render_macro_structure_operator(snapshot_root=snapshot, history_root=history, ohlcv_15m_csv=ohlcv, output_root=output)
            self.assertTrue(result["ok"])
            model = json.loads((output / result["artifact_dir"] / "macro_structure_operator.json").read_text(encoding="utf-8"))
            self.assertEqual(model["selected_structural_checkpoint_id"], "checkpoint_final")
            self.assertEqual(len(model["chart_model"]["overlays"]), 4)
            self.assertNotIn("level_weak", {item["level_id"] for item in model["chart_model"]["overlays"]})
            self.assertTrue(all(item["role"] in {"support", "resistance"} for item in model["chart_model"]["overlays"]))
            categories = model["chronological_changes"]["categories"]
            for category in ("reliability_changes", "role_changes", "lifecycle_changes", "geometry_changes", "absent_from_latest", "reappearances", "stale_or_discontinuous_evaluations"):
                self.assertTrue(categories[category], category)
            self.assertIn("level_support_far", model["source_trace_map"]["zones"])
            self.assertNotIn("level_support_far", model["source_trace_map"]["references"])
            html_text = (output / result["artifact_dir"] / "macro_structure_operator.html").read_text(encoding="utf-8")
            self.assertIn("reliability_changes", html_text)
            self.assertIn("absent_from_latest", html_text)
            self.assertIn("stale_or_discontinuous_evaluations", html_text)


if __name__ == "__main__":
    unittest.main()
