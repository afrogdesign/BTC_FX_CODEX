from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.feedback.macro_structure_volatility_replay import (
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
