from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.feedback.macro_structure_daily_operation import build_macro_structure_daily


def _bars(start: datetime, count: int, step: timedelta, interval: str) -> list[dict[str, object]]:
    pattern = (0.0, 1.8, 0.2, -1.8, -0.2, 1.4, 0.1, -1.4)
    rows = []
    for index in range(count):
        close = 100.0 + pattern[index % len(pattern)]
        rows.append({
            "timestamp_utc": (start + step * index).isoformat().replace("+00:00", "Z"),
            "open": close, "high": close + 0.35, "low": close - 0.35, "close": close,
            "volume": "1", "interval": interval,
        })
    return rows


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class MacroStructureDailyOperationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.paths = {"15m": self.root / "15m.csv", "1h": self.root / "1h.csv", "4h": self.root / "4h.csv"}
        _write(self.paths["15m"], _bars(start, 160, timedelta(minutes=15), "15m"))
        _write(self.paths["1h"], _bars(start, 60, timedelta(hours=1), "1h"))
        _write(self.paths["4h"], _bars(start, 24, timedelta(hours=4), "4h"))
        self.output = self.root / "local" / "reports" / "macro_structure"
        self.now = start + timedelta(hours=60, minutes=1)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self, **kwargs: object) -> dict[str, object]:
        now = kwargs.pop("now_override", self.now)
        return build_macro_structure_daily(
            ohlcv_15m=self.paths["15m"], ohlcv_1h=self.paths["1h"], ohlcv_4h=self.paths["4h"],
            output_root=self.output, now_utc=now, **kwargs,
        )

    def test_cutoff_is_latest_common_closed_candle_and_outputs_are_complete(self) -> None:
        result = self.build()
        self.assertTrue(result["ok"])
        run_dir = self.output / str(result["artifact_dir"])
        self.assertEqual(
            sorted(path.name for path in run_dir.iterdir()),
            sorted(("macro_structure_snapshot.json", "macro_structure_snapshot.md", "macro_level_reliability.csv", "run_manifest.json")),
        )
        snapshot = json.loads((run_dir / "macro_structure_snapshot.json").read_text(encoding="utf-8"))
        self.assertEqual(snapshot["snapshot_cutoff_utc"], "2026-01-02T16:00:00+00:00")
        self.assertEqual(snapshot["as_of_utc"], snapshot["snapshot_cutoff_utc"])
        self.assertEqual(json.loads((self.output / "latest.json").read_text(encoding="utf-8"))["run_id"], result["run_id"])
        markdown = (run_dir / "macro_structure_snapshot.md").read_text(encoding="utf-8")
        self.assertTrue(markdown.startswith("# Macro Structure Daily Snapshot\n\n- snapshot time:"))
        for label in ("evidence confidence, not execution permission", "report-only", "human decides manually"):
            self.assertIn(label, markdown)

    def test_future_candles_do_not_change_cutoff_safe_level_output(self) -> None:
        first = self.build(cutoff_utc="2026-01-02T12:00:00Z")
        first_levels = (self.output / str(first["artifact_dir"]) / "macro_level_reliability.csv").read_bytes()
        future_paths = {interval: self.root / f"future_{interval}.csv" for interval in self.paths}
        for interval, path in self.paths.items():
            rows = []
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            interval_step = {"15m": timedelta(minutes=15), "1h": timedelta(hours=1), "4h": timedelta(hours=4)}[interval]
            last_timestamp = datetime.fromisoformat(rows[-1]["timestamp_utc"].replace("Z", "+00:00"))
            rows.extend(_bars(last_timestamp + interval_step, 8, interval_step, interval))
            _write(future_paths[interval], rows)
        second = build_macro_structure_daily(
            ohlcv_15m=future_paths["15m"], ohlcv_1h=future_paths["1h"], ohlcv_4h=future_paths["4h"],
            output_root=self.root / "future-output", cutoff_utc="2026-01-02T12:00:00Z", now_utc=self.now,
        )
        second_levels = (self.root / "future-output" / str(second["artifact_dir"]) / "macro_level_reliability.csv").read_bytes()
        self.assertEqual(first_levels, second_levels)

    def test_nearest_unreliable_levels_are_not_promoted_and_insufficient_is_success(self) -> None:
        result = self.build()
        self.assertEqual(set(result["reliability_band_counts"]), {"high", "medium", "low", "insufficient"})
        self.assertIn(result["result_status"], {"ok", "insufficient"})
        short_paths = {}
        for interval, path in self.paths.items():
            rows = _bars(datetime(2026, 1, 1, tzinfo=timezone.utc), 20 if interval == "15m" else 4, {"15m": timedelta(minutes=15), "1h": timedelta(hours=1), "4h": timedelta(hours=4)}[interval], interval)
            short_paths[interval] = self.root / f"short_{interval}.csv"
            _write(short_paths[interval], rows)
        insufficient = build_macro_structure_daily(
            ohlcv_15m=short_paths["15m"], ohlcv_1h=short_paths["1h"], ohlcv_4h=short_paths["4h"],
            output_root=self.root / "insufficient-output", now_utc=datetime(2026, 1, 1, 1, tzinfo=timezone.utc),
        )
        self.assertTrue(insufficient["ok"])
        self.assertEqual(insufficient["result_status"], "insufficient")

    def test_stale_and_discontinuous_coverage_are_explicit(self) -> None:
        rows = []
        with self.paths["15m"].open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        del rows[10]
        _write(self.paths["15m"], rows)
        result = self.build(now_override=datetime(2026, 1, 10, tzinfo=timezone.utc))
        self.assertTrue(result["ok"])
        self.assertEqual(result["continuity_status"], "discontinuous")
        self.assertEqual(result["stale_status"], "stale")

    def test_public_only_boundary_and_atomic_failure_preserve_latest(self) -> None:
        self.assertFalse(build_macro_structure_daily(output_root=self.output)["ok"])
        self.build()
        before = (self.output / "latest.json").read_bytes()
        with patch("src.feedback.macro_structure_daily_operation._publish", side_effect=OSError("forced")):
            failed = self.build()
        self.assertFalse(failed["ok"])
        self.assertEqual((self.output / "latest.json").read_bytes(), before)

    def test_deterministic_repeat_and_cli_parser_dispatch_contract(self) -> None:
        first = self.build()
        first_bytes = tuple((self.output / str(first["artifact_dir"]) / name).read_bytes() for name in ("macro_structure_snapshot.json", "macro_structure_snapshot.md", "macro_level_reliability.csv", "run_manifest.json"))
        second = self.build()
        second_bytes = tuple((self.output / str(second["artifact_dir"]) / name).read_bytes() for name in ("macro_structure_snapshot.json", "macro_structure_snapshot.md", "macro_level_reliability.csv", "run_manifest.json"))
        self.assertEqual(first_bytes, second_bytes)
        from tools.log_feedback import _build_parser
        args = _build_parser().parse_args(["run-macro-structure-daily", "--ohlcv-15m", "a", "--ohlcv-1h", "b", "--ohlcv-4h", "c", "--stdout-json"])
        self.assertEqual(args.command, "run-macro-structure-daily")
        self.assertTrue(args.stdout_json)


if __name__ == "__main__":
    unittest.main()
