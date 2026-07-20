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
    def test_weakening_without_activation_is_watch_and_non_directional(self) -> None:
        forecast = _forecast({}, _event("a", "2026-01-01T00:00:00+00:00", directional_activation="NONE", event_family=""), {"level-1"}, {"present": True, "side": "short", "status": "armed", "grade": "C"})
        self.assertEqual((forecast["status"], forecast["next_regime_side"]), ("watch", "NONE"))

    def test_matching_activation_requires_target_and_clear_corridor(self) -> None:
        good = _forecast({}, _event("a", "2026-01-01T00:00:00+00:00"), {"level-1"}, {})
        self.assertEqual((good["status"], good["next_regime_side"]), ("activated", "UP"))
        self.assertEqual(_forecast({}, _event("a", "2026-01-01T00:00:00+00:00", first_reliable_target=""), {"level-1"}, {})["status"], "armed")
        self.assertEqual(_forecast({}, _event("a", "2026-01-01T00:00:00+00:00", intervening_obstruction="block"), {"level-1"}, {})["status"], "armed")
        self.assertEqual(_forecast({}, _event("a", "2026-01-01T00:00:00+00:00", event_family="RELIABLE_LEVEL_REJECTION_DOWN"), {"level-1"}, {})["status"], "none")

    def test_forecast_fields_are_separate_and_outcomes_do_not_change_episode(self) -> None:
        event = _event("a", "2026-01-01T00:00:00+00:00")
        forecast = _forecast({"bias": "short"}, event, {"level-1"}, {})
        self.assertEqual(forecast["current_tactical_side"], "DOWN")
        self.assertEqual(forecast["current_structural_thesis"], "TREND_DOWN")
        self.assertEqual(forecast["next_regime_side"], "UP")
        records = [{"event": event, "forecast": forecast}, {"event": {**event, "event_timestamp_utc": "2026-01-01T01:00:00+00:00", "outcome_3h": "large_down"}, "forecast": forecast}]
        self.assertEqual(len(_episode_rows(records, "candidate")), 1)

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
            first = [path.read_bytes() for path in outputs]
            replay_macro_next_regime(signals=signals, macro_events=events, macro_levels=levels, macro_replay_json=replay, output_events_csv=outputs[0], output_episodes_csv=outputs[1], output_json=outputs[2], output_md=outputs[3], replace_output=True)
            self.assertEqual(first, [path.read_bytes() for path in outputs])
            with patch("src.feedback.macro_next_regime_replay.os.replace", side_effect=OSError("boom")):
                with self.assertRaises(OSError): replay_macro_next_regime(signals=signals, macro_events=events, macro_levels=levels, macro_replay_json=replay, output_events_csv=outputs[0], output_episodes_csv=outputs[1], output_json=outputs[2], output_md=outputs[3], replace_output=True)
            self.assertEqual(first, [path.read_bytes() for path in outputs])


if __name__ == "__main__":
    unittest.main()
