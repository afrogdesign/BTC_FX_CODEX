from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.feedback.macro_next_regime_replay import (
    _episode_rows,
    _forecast,
    _gate,
    _horizons,
    baseline_evidence_key,
    candidate_evidence_key,
    baseline_adapter,
    replay_macro_next_regime,
)


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def _event(signal_id: str, at: str, **overrides: object) -> dict[str, object]:
    row = {"schema_version": "macro_structure_volatility_replay.v1", "method_version": "macro_structure_volatility_replay.v1", "event_id": "event-" + signal_id, "signal_id": signal_id, "event_timestamp_utc": at, "event_timestamp_jst": at, "directional_activation": "UP", "event_family": "RELIABLE_LEVEL_REJECTION_UP", "first_reliable_target": "level-1", "intervening_obstruction": "none", "data_quality_status": "ok", "current_tactical_side": "SHORT", "structural_direction": "trend_down", "structural_state": "transition", "price_location": "upper_half", "volatility_state": "ordinary", "expansion_risk": "medium", "level_reliability_band": "high", "outcome_3h": "large_up", "outcome_6h": "large_up", "outcome_12h": "large_up", "outcome_24h": "unresolved", "first_material_move_timestamp": "2026-01-01T01:00:00+00:00"}
    row.update(overrides); return row


class MacroNextRegimeReplayTests(unittest.TestCase):
    def test_burden_uses_common_explicit_eligible_dates(self) -> None:
        def episode(policy: str, day: int) -> dict[str, object]:
            return {"policy": policy, "start_timestamp_utc": f"2026-01-0{day}T00:00:00+00:00", "side": "UP", "outcome_3h": "large_up", "outcome_6h": "large_up", "outcome_12h": "large_up", "outcome_24h": "large_up", "first_material_move_timestamp": "", "data_quality_status": "ok"}
        dates = {"2026-01-01", "2026-01-02", "2026-01-03"}
        candidate, baseline = _horizons([episode("candidate", 1)], dates, "eligible_performance_event_dates"), _horizons([episode("baseline", 2), episode("baseline", 2)], dates, "eligible_performance_event_dates")
        self.assertEqual(candidate["3h"]["burden_per_jst_day"], round(1 / 3, 8))
        self.assertEqual(baseline["3h"]["burden_per_jst_day"], round(2 / 3, 8))
        for metrics in (candidate, baseline):
            for horizon in metrics.values(): self.assertEqual((horizon["burden_jst_day_count"], horizon["burden_date_basis"]), (3, "eligible_performance_event_dates"))

    def test_gate_audits_zero_episode_validation_event_quality(self) -> None:
        def episode(policy: str, day: int) -> dict[str, object]:
            return {"policy": policy, "start_timestamp_utc": f"2026-01-0{day}T00:00:00+00:00", "side": "UP", "outcome_3h": "large_up", "outcome_6h": "large_up", "outcome_12h": "large_up", "outcome_24h": "large_up", "first_material_move_timestamp": "", "data_quality_status": "ok"}
        eligible = [{"event_timestamp_utc": f"2026-01-0{day}T00:00:00+00:00", "data_quality_status": "ok"} for day in range(1, 5)] + [{"event_timestamp_utc": "2026-01-05T00:00:00+00:00", "data_quality_status": ""}]
        gate = _gate([episode("candidate", 4), episode("baseline", 4)], eligible, True)
        self.assertEqual(gate["validation_dates"], ["2026-01-04", "2026-01-05"])
        self.assertEqual(gate["validation_eligible_event_count"], 2)
        self.assertFalse(gate["validation_data_quality_pass"])
        self.assertEqual(gate["validation_data_quality_status_counts"], {"missing": 1, "ok": 1})
        self.assertEqual(gate["validation_data_quality_issue_event_count"], 1)
        self.assertIn("validation_data_quality_unresolved", gate["reason_codes"])
        for policy in ("validation_candidate_metrics", "validation_baseline_metrics"):
            self.assertEqual(gate[policy]["3h"]["burden_jst_day_count"], 2)
            self.assertEqual(gate[policy]["3h"]["burden_date_basis"], "eligible_validation_event_dates")

    def test_candidate_owned_failed_thesis_is_non_directional_watch(self) -> None:
        signal = {"failed_breakout_state": "failed_long_breakout"}
        event = _event("a", "2026-01-01T00:00:00+00:00", directional_activation="NONE", event_family="")
        absent = _forecast(signal, event, {"level-1"}, {})
        present = _forecast(signal, event, {"level-1"}, {"present": True, "side": "short", "status": "active", "grade": "A"})
        self.assertEqual((absent["status"], absent["next_regime_side"], absent["weakening_thesis"]), ("watch", "NONE", "explicit_failed_thesis"))
        self.assertEqual((present["status"], present["next_regime_side"], present["weakening_thesis"]), ("watch", "NONE", "explicit_failed_thesis"))

    def test_gate_uses_eligible_event_dates_and_candidate_only_concentration(self) -> None:
        def episode(policy: str, day: int, ident: str) -> dict[str, object]:
            return {"policy": policy, "start_timestamp_utc": f"2026-01-0{day}T00:00:00+00:00", "side": "UP", "outcome_3h": "large_up", "outcome_6h": "large_up", "outcome_12h": "large_up", "outcome_24h": "large_up", "first_material_move_timestamp": "", "data_quality_status": "ok", "episode_id": ident}
        eligible = [{"event_timestamp_utc": f"2026-01-0{day}T00:00:00+00:00"} for day in range(1, 6)]
        gate = _gate([episode("candidate", 5, "c"), episode("baseline", 4, "b1"), episode("baseline", 5, "b2")], eligible, True)
        self.assertEqual(gate["eligible_event_jst_dates"], [f"2026-01-0{day}" for day in range(1, 6)])
        self.assertEqual(gate["validation_dates"], ["2026-01-04", "2026-01-05"])
        self.assertEqual(gate["validation_date_basis"], "eligible_performance_events")
        self.assertEqual(gate["primary_gate_horizon"], "3h")
        self.assertIn("single_jst_date_concentration", gate["reason_codes"])
        self.assertEqual(set(gate["validation_candidate_metrics"]), {"3h", "6h", "12h", "24h"})
        self.assertEqual(set(gate["validation_baseline_metrics"]), {"3h", "6h", "12h", "24h"})

    def test_baseline_concentration_does_not_trigger_candidate_reason(self) -> None:
        def episode(policy: str, day: int, ident: str) -> dict[str, object]:
            return {"policy": policy, "start_timestamp_utc": f"2026-01-0{day}T00:00:00+00:00", "side": "UP", "outcome_3h": "large_up", "outcome_6h": "large_up", "outcome_12h": "large_up", "outcome_24h": "large_up", "first_material_move_timestamp": "", "data_quality_status": "ok", "episode_id": ident}
        eligible = [{"event_timestamp_utc": f"2026-01-0{day}T00:00:00+00:00"} for day in range(1, 6)]
        gate = _gate([episode("candidate", 4, "c1"), episode("candidate", 5, "c2"), episode("baseline", 5, "b1"), episode("baseline", 5, "b2")], eligible, True)
        self.assertNotIn("single_jst_date_concentration", gate["reason_codes"])

    def test_baseline_alone_does_not_create_candidate_watch_or_weakening(self) -> None:
        forecast = _forecast({}, _event("a", "2026-01-01T00:00:00+00:00", directional_activation="NONE", event_family=""), {"level-1"}, {"present": True, "side": "short", "status": "armed", "grade": "C"})
        self.assertEqual((forecast["status"], forecast["next_regime_side"], forecast["weakening_thesis"]), ("none", "NONE", "none"))

    def test_matching_activation_requires_target_and_clear_corridor(self) -> None:
        good = _forecast({}, _event("a", "2026-01-01T00:00:00+00:00"), {"level-1"}, {})
        self.assertEqual((good["status"], good["next_regime_side"]), ("activated", "UP"))
        self.assertEqual(_forecast({}, _event("a", "2026-01-01T00:00:00+00:00", first_reliable_target=""), {"level-1"}, {})["status"], "armed")
        self.assertEqual(_forecast({}, _event("a", "2026-01-01T00:00:00+00:00", intervening_obstruction="level-1"), {"level-1"}, {})["status"], "none")
        self.assertEqual(_forecast({}, _event("a", "2026-01-01T00:00:00+00:00", event_family="RELIABLE_LEVEL_REJECTION_DOWN"), {"level-1"}, {})["status"], "none")
        self.assertEqual(_forecast({}, _event("a", "2026-01-01T00:00:00+00:00", first_reliable_target="unknown"), {"level-1"}, {})["status"], "none")

    def test_auxiliary_and_mixed_directional_families_fail_closed_without_replay_abort(self) -> None:
        auxiliary = _forecast({}, _event("a", "2026-01-01T00:00:00+00:00", event_family="REPEATED_TEST_PRESSURE_UP"), {"level-1"}, {})
        self.assertEqual((auxiliary["status"], auxiliary["next_regime_side"]), ("none", "NONE"))
        mixed = _forecast({}, _event("a", "2026-01-01T00:00:00+00:00", event_family="RELIABLE_LEVEL_REJECTION_UP|RELIABLE_LEVEL_REJECTION_DOWN|RELIABLE_LEVEL_APPROACH"), {"level-1"}, {})
        self.assertEqual((mixed["status"], mixed["next_regime_side"]), ("none", "NONE"))
        self.assertIn("directional_family_conflict", mixed["invalidation_reason_codes"])

    def test_forecast_fields_are_separate_and_outcomes_do_not_change_episode(self) -> None:
        event = _event("a", "2026-01-01T00:00:00+00:00")
        forecast = _forecast({"bias": "short"}, event, {"level-1"}, {})
        self.assertEqual(forecast["current_tactical_side"], "DOWN")
        self.assertEqual(forecast["current_structural_thesis"], "TREND_DOWN")
        self.assertEqual(forecast["next_regime_side"], "UP")
        records = [{"event": event, "forecast": forecast}, {"event": {**event, "event_timestamp_utc": "2026-01-01T01:00:00+00:00", "outcome_3h": "large_down"}, "forecast": forecast}]
        self.assertEqual(len(_episode_rows(records, "candidate")), 1)

    def test_episode_boundaries_use_start_time_and_pre_outcome_evidence_only(self) -> None:
        event = _event("a", "2026-01-01T00:00:00+00:00")
        forecast = _forecast({}, event, {"level-1"}, {})
        def record(hours: int, **changes: object) -> dict[str, object]:
            return {"event": {**event, "signal_id": f"a{hours}", "event_id": f"e{hours}", "event_timestamp_utc": (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=hours)).isoformat(), **changes}, "forecast": {**forecast, **changes}}
        self.assertEqual(len(_episode_rows([record(0), record(2), record(2, outcome_3h="large_down")], "candidate")), 1)
        self.assertEqual(len(_episode_rows([record(0), record(3)], "candidate")), 2)
        self.assertEqual(len(_episode_rows([record(0), record(1, status="armed")], "candidate")), 2)

    def test_complete_candidate_and_baseline_keys_drive_transitions_only(self) -> None:
        event = _event("a", "2026-01-01T00:00:00+00:00")
        base = _forecast({}, event, {"level-1"}, {"present": True, "side": "short", "status": "armed", "grade": "C", "type": "x", "reason_codes": ["a"]})
        self.assertNotIn("outcome", candidate_evidence_key(base)); self.assertNotIn("baseline", candidate_evidence_key(base))
        self.assertIn("baseline_type", baseline_evidence_key(base)); self.assertIn("baseline_reason_codes", baseline_evidence_key(base))
        def record(hour: int, forecast: dict[str, object]) -> dict[str, object]:
            return {"event": {**event, "signal_id": str(hour), "event_id": str(hour), "event_timestamp_utc": (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=hour)).isoformat()}, "forecast": forecast}
        changed_target = {**base, "first_reliable_target": "level-2"}
        changed_obstruction = {**base, "intervening_obstruction": "none2"}
        changed_reason = {**base, "reason_codes": "other"}
        self.assertEqual(len(_episode_rows([record(0, base), record(1, changed_target)], "candidate")), 2)
        self.assertEqual(len(_episode_rows([record(0, base), record(1, changed_obstruction)], "candidate")), 2)
        self.assertEqual(len(_episode_rows([record(0, base), record(1, changed_reason)], "candidate")), 2)
        changed_baseline = {**base, "baseline_type": "y", "baseline_reason_codes": "b"}
        self.assertEqual(len(_episode_rows([record(0, base), record(1, changed_baseline)], "baseline")), 2)

    def test_baseline_adapter_does_not_mutate_rows(self) -> None:
        current = {"signal_id": "a", "bias": "long", "current_price": "100"}; previous = {"signal_id": "p", "bias": "short"}
        original = (json.dumps(current, sort_keys=True), json.dumps(previous, sort_keys=True))
        baseline_adapter(current, previous)
        self.assertEqual((json.dumps(current, sort_keys=True), json.dumps(previous, sort_keys=True)), original)

    def test_context_exclusion_gate_and_atomic_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); start = "2026-01-01T00:00:00+00:00"
            signals = root / "signals.csv"; events = root / "events.csv"; levels = root / "levels.csv"; replay = root / "replay.json"
            _write(signals, [{"signal_id": "context", "timestamp_utc": start, "current_price": "100", "macro_context_only": "true"}, {"signal_id": "a", "timestamp_utc": start, "current_price": "100", "macro_context_only": "false"}])
            _write(events, [_event("a", start)]); _write(levels, [{"schema_version": "level_reliability.v1", "method_version": "macro_structure_volatility_replay.v1", "level_id": "level-1", "reliability_band": "high"}]); replay.write_text(json.dumps({"schema_version": "macro_structure_volatility_replay.v1", "method_version": "macro_structure_volatility_replay.v1", "coverage": {"continuity_pass": True}}))
            outputs = [root / "out-events.csv", root / "episodes.csv", root / "out.json", root / "out.md"]
            result = replay_macro_next_regime(signals=signals, macro_events=events, macro_levels=levels, macro_replay_json=replay, output_events_csv=outputs[0], output_episodes_csv=outputs[1], output_json=outputs[2], output_md=outputs[3], replace_output=True)
            self.assertEqual(result["counts"]["events"], 1); self.assertEqual(json.loads(outputs[2].read_text())["recommendation"]["status"], "continue_shadow_collection")
            report = json.loads(outputs[2].read_text())
            self.assertEqual(set(report["metrics"]["candidate"]), {"3h", "6h", "12h", "24h"})
            self.assertEqual(set(report["splits"]["candidate"]), {"side", "structural_state", "price_location", "volatility_state", "level_reliability_band"})
            first = [path.read_bytes() for path in outputs]
            replay_macro_next_regime(signals=signals, macro_events=events, macro_levels=levels, macro_replay_json=replay, output_events_csv=outputs[0], output_episodes_csv=outputs[1], output_json=outputs[2], output_md=outputs[3], replace_output=True)
            self.assertEqual(first, [path.read_bytes() for path in outputs])
            import os
            calls = {"count": 0}; real_replace = os.replace
            def fail_after_first_promotion(source: object, destination: object) -> None:
                calls["count"] += 1
                if calls["count"] == 6: raise OSError("boom")
                real_replace(source, destination)
            with patch("src.feedback.macro_next_regime_replay.os.replace", side_effect=fail_after_first_promotion):
                with self.assertRaises(OSError): replay_macro_next_regime(signals=signals, macro_events=events, macro_levels=levels, macro_replay_json=replay, output_events_csv=outputs[0], output_episodes_csv=outputs[1], output_json=outputs[2], output_md=outputs[3], replace_output=True)
            self.assertEqual(first, [path.read_bytes() for path in outputs])


if __name__ == "__main__":
    unittest.main()
