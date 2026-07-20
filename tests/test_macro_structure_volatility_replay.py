from __future__ import annotations

import csv
import json
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.feedback.macro_structure_volatility_replay import (
    _gate,
    _atomic,
    _dedup_policy_episodes,
    _diagnose_miss,
    _level_events,
    _micro_value,
    _outcomes,
    _pressure,
    _policy_metrics,
    _policy_side,
    _realized_inventory,
    _split,
    _structure,
    build_levels,
    confirmed_pivots,
    replay_macro_structure_volatility,
)


def _bars(start: datetime, count: int, step: timedelta, interval: str, base: float = 100.0) -> list[dict[str, object]]:
    rows = []
    for index in range(count):
        price = base + ((index % 7) - 3) * 0.2
        rows.append({"timestamp_utc": (start + step * index).isoformat().replace("+00:00", "Z"), "open": price, "high": price + 0.5, "low": price - 0.5, "close": price + 0.1, "interval": interval})
    return rows


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


class MacroStructureVolatilityReplayTests(unittest.TestCase):
    def test_location_alone_does_not_emit_rejection_or_corridor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); start = datetime(2026, 1, 1, tzinfo=timezone.utc)
            signals = root / "signals.csv"; _write(signals, [{"signal_id": "s1", "timestamp_utc": start.isoformat().replace("+00:00", "Z"), "current_price": "99", "bias": "long"}])
            paths = {"15m": root / "15m.csv", "1h": root / "1h.csv", "4h": root / "4h.csv"}
            _write(paths["15m"], _bars(start, 100, timedelta(minutes=15), "15m")); _write(paths["1h"], _bars(start, 20, timedelta(hours=1), "1h")); _write(paths["4h"], _bars(start, 10, timedelta(hours=4), "4h"))
            out = [root / name for name in ("e.csv", "l.csv", "m.csv", "j.json", "r.md")]
            replay_macro_structure_volatility(signals=signals, ohlcv_15m=paths["15m"], ohlcv_1h=paths["1h"], ohlcv_4h=paths["4h"], output_events_csv=out[0], output_levels_csv=out[1], output_misses_csv=out[2], output_json=out[3], output_md=out[4], replace_output=True)
            self.assertNotIn("OPEN_TRAVEL_CORRIDOR", out[0].read_text())

    def test_closed_candle_rejection_break_acceptance_and_reclaim_are_mirrored(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        def candle(i: int, close: float, high: float | None = None, low: float | None = None) -> dict[str, object]:
            return {"timestamp": start + timedelta(hours=i), "open": close, "high": high if high is not None else close + .1, "low": low if low is not None else close - .1, "close": close, "interval": "1h"}
        support = {"side": "low", "center": 100.0, "low": 99.8, "high": 100.2}
        rejection = _level_events(support, [candle(0, 100.0, 100.2, 99.8), candle(1, 101.0, 101.1, 100.9)], start + timedelta(hours=3))
        self.assertEqual(rejection["family"], "RELIABLE_LEVEL_REJECTION_UP")
        accepted = _level_events({"side": "high", "center": 100.0, "low": 99.8, "high": 100.2}, [candle(0, 101.0, 101.1, 100.9), candle(1, 101.0, 101.1, 100.9)], start + timedelta(hours=3))
        self.assertEqual(accepted["family"], "LEVEL_BREAK_ACCEPTANCE_UP")
        reclaimed = _level_events({"side": "high", "center": 100.0, "low": 99.8, "high": 100.2}, [candle(0, 101.0, 101.1, 100.9), candle(1, 99.9, 100.0, 99.8)], start + timedelta(hours=3))
        self.assertEqual(reclaimed["family"], "FALSE_BREAK_RECLAIM_DOWN")
        self.assertEqual(reclaimed["activation"], "DOWN")

    def test_acceptance_uses_break_candle_plus_one_consecutive_close(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        level = {"side": "high", "center": 100.0, "low": 99.8, "high": 100.2}
        bars = [{"timestamp": start + timedelta(hours=i), "open": 101, "high": 101.1, "low": 100.9, "close": 101, "interval": "1h"} for i in range(2)]
        self.assertEqual(_level_events(level, bars, start + timedelta(hours=3))["family"], "LEVEL_BREAK_ACCEPTANCE_UP")

    def test_microstructure_is_directional_only_when_valid(self) -> None:
        self.assertEqual(_micro_value("0", "order_flow_imbalance"), ("absent", None))
        self.assertEqual(_micro_value("bad", "order_flow_imbalance"), ("unavailable", None))
        self.assertEqual(_micro_value("1.2", "aggressive_buy_ratio"), ("unavailable", None))
        self.assertEqual(_micro_value("0.8", "aggressive_buy_ratio"), ("present", "UP"))
        self.assertEqual(_micro_value("-2", "order_flow_imbalance"), ("present", "DOWN"))

    def test_policy_sides_normalize_notification_and_turning_vocabularies(self) -> None:
        notified = {"was_notified": "true", "current_tactical_side": "LONG", "event_family": ""}
        self.assertEqual(_policy_side(notified, "current_notification"), "UP")
        notified["current_tactical_side"] = "short"
        self.assertEqual(_policy_side(notified, "current_notification"), "DOWN")

    def test_policy_metrics_use_policy_episodes_for_false_warning_and_splits(self) -> None:
        event = {"was_notified": "true", "current_tactical_side": "LONG", "event_family": ""}
        episodes = [{"event": event, "signal": None, "outcome": "balanced_no_expansion", "timestamp": "2026-01-01T00:00:00+00:00", "mfe": 1.0, "mae": .4, "opportunity_id": "", "opportunity_direction": "", "lead_minutes": None}]
        metrics = _policy_metrics([], "current_notification", episodes)
        self.assertEqual(metrics["episodes"], 1)
        self.assertEqual(metrics["resolved_episodes"], 1)
        self.assertEqual(metrics["false_warning_rate"], 1.0)

    def test_policy_episode_dedup_keeps_transition_and_drops_repeated_snapshot(self) -> None:
        base = {"was_notified": "true", "current_tactical_side": "LONG", "event_family": "", "structural_state": "range", "volatility_state": "ordinary", "price_location": "lower_half"}
        def row(hour: int, event: dict[str, object] = base) -> dict[str, object]:
            return {"event": dict(event), "signal": None, "outcome": "unresolved", "timestamp": f"2026-01-01T{hour:02d}:00:00+00:00", "mfe": None, "mae": None}
        repeated = _dedup_policy_episodes([row(0), row(1)], "current_notification")
        changed = _dedup_policy_episodes([row(0), row(1, {**base, "current_tactical_side": "SHORT"})], "current_notification")
        self.assertEqual(len(repeated), 1)
        self.assertEqual(len(changed), 2)
        self.assertEqual(_policy_metrics([], "current_notification", [row(0), row(1)])["episodes"], 1)

    def test_resolved_future_outcome_does_not_split_event_time_episode(self) -> None:
        event = {"was_notified": "true", "current_tactical_side": "LONG", "event_family": "", "structural_state": "range", "volatility_state": "ordinary", "price_location": "lower_half"}
        rows = [{"event": event, "signal": None, "outcome": "large_up", "timestamp": f"2026-01-01T0{hour}:00:00+00:00"} for hour in (0, 1)]
        self.assertEqual(len(_dedup_policy_episodes(rows, "current_notification")), 1)

    def test_miss_diagnosis_uses_positive_predicates_and_fails_closed(self) -> None:
        row = {"data_quality_status": "ok", "structural_state": "range", "nearest_support_id": "s", "nearest_resistance_id": "r", "pressure_evidence_json": '{"rejection":"present","microstructure_status":"available"}', "event_family": "", "volatility_state": "ordinary"}
        self.assertEqual(_diagnose_miss(row, {"data_quality_status": "ok"}, False, False), "rejection_event_missing")
        ambiguous = {**row, "pressure_evidence_json": '{"rejection":"present","directional_microstructure":{"order_flow_imbalance":"UP"},"microstructure_status":"available"}'}
        self.assertEqual(_diagnose_miss(ambiguous, {"data_quality_status": "ok"}, False, False), "data_unresolved")

    def test_compression_only_requires_expansion_and_has_no_directional_precision(self) -> None:
        event = {"volatility_state": "compressed", "event_family": ""}
        episode = {"event": event, "signal": None, "outcome": "balanced_no_expansion", "timestamp": "2026-01-01T00:00:00+00:00", "mfe": 0.0, "mae": 0.0, "opportunity_id": "", "opportunity_direction": "", "lead_minutes": None}
        metrics = _policy_metrics([], "compression_only", [episode])
        self.assertIsNone(metrics["directional_precision"])
        self.assertEqual(metrics["expansion_precision"], 0.0)

    def test_lifecycle_records_multiple_completed_episodes_and_reaction_atr(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        level = {"side": "high", "center": 100.0, "low": 99.8, "high": 100.2}
        closes = [101.0, 101.0, 99.9, 99.9, 101.0, 101.0]
        bars = [{"timestamp": start + timedelta(hours=i), "open": close, "high": close + .1, "low": close - .1, "close": close, "interval": "1h"} for i, close in enumerate(closes)]
        lifecycle = _level_events(level, bars, start + timedelta(hours=7))
        completed = [item for item in lifecycle["interactions"] if item["kind"] != "break"]
        self.assertGreaterEqual(len(completed), 2)
        self.assertTrue(all(item["reaction_atr"] > 0 for item in completed))

    def test_lifecycle_does_not_repeat_historical_family_or_rearm_continuous_acceptance(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        level = {"side": "high", "center": 100.0, "low": 99.8, "high": 100.2}
        bars = [{"timestamp": start + timedelta(hours=i), "open": 101, "high": 101.1, "low": 100.9, "close": 101, "interval": "1h"} for i in range(4)]
        lifecycle = _level_events(level, bars, start + timedelta(hours=5))
        self.assertEqual(lifecycle["family"], "")
        self.assertEqual(sum(item["kind"] == "break" for item in lifecycle["interactions"]), 1)

    def test_new_approach_is_current_evidence_after_historical_acceptance(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        level = {"side": "high", "center": 100.0, "low": 99.8, "high": 100.2}
        bars = [{"timestamp": start + timedelta(hours=i), "open": value, "high": value + .1, "low": value - .1, "close": value, "interval": "1h"} for i, value in enumerate((101, 101, 100, 100))]
        lifecycle = _level_events(level, bars, start + timedelta(hours=5))
        self.assertEqual(lifecycle["family"], "RELIABLE_LEVEL_APPROACH")
        self.assertEqual(lifecycle["current_kind"], "")

    def test_atomic_failure_preserves_all_existing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); targets = [root / name for name in ("a", "b", "c", "d", "e")]
            for target in targets: target.write_bytes(b"old")
            original = Path.replace
            def fail_third(source: Path, target: Path) -> Path:
                if source.parent.name.startswith(".macro-replay-") and source.name.startswith("2-"):
                    raise OSError("forced")
                return original(source, target)
            with patch("src.feedback.macro_structure_volatility_replay.Path.replace", new=fail_third):
                with self.assertRaises(OSError):
                    _atomic({target: b"new" for target in targets}, True)
            self.assertEqual([target.read_bytes() for target in targets], [b"old"] * 5)

    def test_realized_move_side_is_not_overwritten_by_activation(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        candles = [{"timestamp": start + timedelta(minutes=15 * i), "open": 100, "high": 100.1, "low": 98.5, "close": 99, "interval": "15m"} for i in range(96)]
        result = _outcomes(100, start, .1, candles, [], "UP")
        self.assertEqual(result["large_move_side"], "DOWN")

    def test_structure_uses_event_time_roles_not_geometry(self) -> None:
        support = {"level_id": "s", "low": 99.0, "high": 100.0, "center": 99.5, "role": "support", "reliability_band": "high"}
        resistance = {"level_id": "r", "low": 101.0, "high": 102.0, "center": 101.5, "role": "resistance", "reliability_band": "high"}
        wrong_role = {"level_id": "x", "low": 98.0, "high": 99.0, "center": 98.5, "role": "resistance", "reliability_band": "high"}
        structure = _structure(100.5, [support, resistance, wrong_role], [], datetime(2026, 1, 2, tzinfo=timezone.utc), [])
        self.assertEqual(structure["support"]["level_id"], "s")
        self.assertEqual(structure["resistance"]["level_id"], "r")

    def test_outcome_keeps_the_selected_directional_target(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        candles = [{"timestamp": start + timedelta(minutes=15 * i), "open": 100, "high": 101, "low": 99.9, "close": 100, "interval": "15m"} for i in range(96)]
        selected = {"level_id": "selected", "side": "high", "low": 99.8, "high": 100.2, "center": 100.0}
        target = {"level_id": "target", "side": "high", "low": 101.9, "high": 102.1, "center": 102.0}
        result = _outcomes(100, start, .1, candles, [selected], "UP", target, selected)
        self.assertEqual(result["target_touch"], "unresolved")

    def test_gate_uses_validation_opportunities_and_reports_comparative_reasons(self) -> None:
        split = {"status": "established", "calibration": ["2026-01-01"], "validation": ["2026-01-02", "2026-01-03", "2026-01-04"], "holdout": []}
        events = [{"event_timestamp_utc": "2026-01-02T00:00:00+00:00"}]
        opportunities = [{"opportunity_id": "o1", "direction": "UP", "start_timestamp_utc": "2026-01-02T00:00:00+00:00"}]
        episodes = [{"event": {"level_reliability_band": "high", "data_quality_status": "ok", "event_family": ""}, "timestamp": "2026-01-01T00:00:00+00:00", "outcome": "large_up", "opportunity_id": ""}, {"event": {"level_reliability_band": "low", "data_quality_status": "ok", "event_family": ""}, "timestamp": "2026-01-02T00:00:00+00:00", "outcome": "large_up", "opportunity_id": "o1"}]
        gate = _gate(events, split, {"continuity_pass": True}, {"current_notification": {"large_move_recall": .5}, "reliable_level_acceptance_corridor": {"large_move_recall": .5}}, opportunities, episodes)
        self.assertIn("primary_objective_improvement_not_established", gate["reasons"])
        self.assertIn("single_opportunity_dependence", gate["reasons"])

    def test_outcome_uses_bar_open_equal_to_event_and_resolves_excursions(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        candles = [{"timestamp": start + timedelta(minutes=15 * i), "open": 100, "high": 101 if i == 0 else 100.1, "low": 99 if i == 1 else 99.9, "close": 100, "interval": "15m"} for i in range(96)]
        result = _outcomes(100, start, .1, candles, [])
        self.assertEqual(result["outcome_1h"], "whipsaw_both")
        self.assertGreater(result["mfe_atr"], 0)
        self.assertGreater(result["mae_atr"], 0)

    def test_independent_inventory_keeps_move_without_signal_and_deduplicates(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc); candles = []
        for i in range(110):
            price = 100.0; high = 101.0 if i in {14, 15} else 100.1; low = 99.9
            candles.append({"timestamp": start + timedelta(minutes=15 * i), "open": price, "high": high, "low": low, "close": price, "interval": "15m"})
        inventory = _realized_inventory(candles, [], [])
        self.assertTrue(inventory)
        self.assertEqual(inventory[0]["signal_id"], "")
        self.assertEqual(len([item for item in inventory if item["direction"] == "UP"]), 1)

    def test_walk_forward_uses_jst_and_gate_fails_closed(self) -> None:
        signals = [{"timestamp_utc": f"2026-01-{day:02d}T15:00:00Z", "signal_id": str(day), "current_price": "100"} for day in range(1, 7)]
        split = _split(signals)
        self.assertEqual(split["calibration"][0], "2026-01-02")
        gate = _gate([], split, {"continuity_pass": False})
        self.assertIn(gate["status"], {"continue_shadow_collection", "insufficient_evidence"})
        self.assertIn("continuity_or_coverage_failed", gate["reasons"])

    def test_confirmed_pivot_is_not_backdated(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        rows = _bars(start, 9, timedelta(hours=1), "1h")
        rows[4]["high"] = 110.0; rows[4]["low"] = 105.0
        candles = [{"timestamp": _dt(row["timestamp_utc"]), "open": row["open"], "high": row["high"], "low": row["low"], "close": row["close"], "interval": "1h"} for row in rows]
        pivots = confirmed_pivots(candles, "1h")
        pivot = next(item for item in pivots if item["side"] == "high")
        self.assertEqual(pivot["pivot_timestamp"], start + timedelta(hours=4))
        self.assertEqual(pivot["confirmation_timestamp"], start + timedelta(hours=7))

    def test_level_identity_is_stable_and_cross_timeframe_confluence_is_preserved(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        p1 = {"pivot_id": "1h:L:a", "side": "low", "price": 100.0, "pivot_timestamp": start, "confirmation_timestamp": start + timedelta(hours=1), "source_timeframe": "1h", "atr_at_confirmation": 2.0}
        p2 = {"pivot_id": "4h:L:b", "side": "low", "price": 100.2, "pivot_timestamp": start, "confirmation_timestamp": start + timedelta(hours=2), "source_timeframe": "4h", "atr_at_confirmation": 2.0}
        levels = build_levels([p1, p2])
        self.assertEqual(len(levels), 1)
        self.assertEqual(levels[0]["level_id"], build_levels([p1, p2])[0]["level_id"])
        self.assertEqual({m["source_timeframe"] for m in levels[0]["members"]}, {"1h", "4h"})

    def test_replay_is_deterministic_and_writes_five_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); start = datetime(2026, 1, 1, tzinfo=timezone.utc)
            signals = root / "signals.csv"; _write(signals, [{"signal_id": "s1", "timestamp_utc": start.isoformat().replace("+00:00", "Z"), "current_price": "100", "bias": "long", "market_map_flags": ""}])
            paths = {"15m": root / "15m.csv", "1h": root / "1h.csv", "4h": root / "4h.csv"}
            _write(paths["15m"], _bars(start, 100, timedelta(minutes=15), "15m"))
            _write(paths["1h"], _bars(start, 20, timedelta(hours=1), "1h"))
            _write(paths["4h"], _bars(start, 10, timedelta(hours=4), "4h"))
            def run(suffix: str) -> tuple[bytes, bytes, bytes, bytes, bytes]:
                out = [root / f"{name}{suffix}" for name in ("events.csv", "levels.csv", "misses.csv", "replay.json", "replay.md")]
                replay_macro_structure_volatility(signals=signals, ohlcv_15m=paths["15m"], ohlcv_1h=paths["1h"], ohlcv_4h=paths["4h"], output_events_csv=out[0], output_levels_csv=out[1], output_misses_csv=out[2], output_json=out[3], output_md=out[4], replace_output=True)
                return tuple(path.read_bytes() for path in out)
            first, second = run("-a"), run("-b")
            self.assertEqual(first, second)
            summary = json.loads(first[3]); self.assertIn(summary["recommendation_status"], {"insufficient_evidence", "continue_shadow_collection", "eligible_for_next_design_proposal"})

    def test_missing_continuity_is_reported_without_future_imputation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); start = datetime(2026, 1, 1, tzinfo=timezone.utc)
            signals = root / "signals.csv"; _write(signals, [{"signal_id": "s1", "timestamp_utc": start.isoformat().replace("+00:00", "Z"), "current_price": "100"}])
            m15 = _bars(start, 70, timedelta(minutes=15), "15m"); del m15[20]
            paths = {"15m": root / "15m.csv", "1h": root / "1h.csv", "4h": root / "4h.csv"}
            _write(paths["15m"], m15); _write(paths["1h"], _bars(start, 10, timedelta(hours=1), "1h")); _write(paths["4h"], _bars(start, 8, timedelta(hours=4), "4h"))
            outputs = [root / name for name in ("e.csv", "l.csv", "m.csv", "j.json", "r.md")]
            replay_macro_structure_volatility(signals=signals, ohlcv_15m=paths["15m"], ohlcv_1h=paths["1h"], ohlcv_4h=paths["4h"], output_events_csv=outputs[0], output_levels_csv=outputs[1], output_misses_csv=outputs[2], output_json=outputs[3], output_md=outputs[4], replace_output=True)
            self.assertFalse(json.loads(outputs[3].read_text())["coverage"]["continuity_pass"])


def _dt(value: object) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


if __name__ == "__main__":
    unittest.main()
