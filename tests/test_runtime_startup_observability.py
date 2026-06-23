from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from main import _runtime_startup_status_path, _write_runtime_startup_status


class RuntimeStartupObservabilityTest(unittest.TestCase):
    def test_write_runtime_startup_status_json_same_day_next_report_time(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            cfg = SimpleNamespace(TIMEZONE="Asia/Tokyo", REPORT_TIMES=["00:05", "09:05", "23:05"])
            now_utc = datetime(2026, 6, 23, 0, 0, tzinfo=timezone.utc)

            path = _write_runtime_startup_status(base_dir, cfg, pid=4321, now_utc=now_utc)

            self.assertEqual(path, _runtime_startup_status_path(base_dir))
            self.assertTrue(path.exists())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["timestamp_utc"], "2026-06-23T00:00:00Z")
            self.assertEqual(payload["pid"], 4321)
            self.assertEqual(payload["timezone"], "Asia/Tokyo")
            self.assertEqual(payload["report_times"], ["00:05", "09:05", "23:05"])
            self.assertEqual(payload["next_report_time"], "2026-06-23T09:05:00+09:00")

    def test_write_runtime_startup_status_json_rolls_to_next_day(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            cfg = SimpleNamespace(TIMEZONE="Asia/Tokyo", REPORT_TIMES=["00:05", "12:05", "23:05"])
            now_utc = datetime(2026, 6, 23, 14, 10, tzinfo=timezone.utc)

            path = _write_runtime_startup_status(base_dir, cfg, pid=9876, now_utc=now_utc)

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["next_report_time"], "2026-06-24T00:05:00+09:00")
            self.assertEqual(payload["report_times"], ["00:05", "12:05", "23:05"])
            self.assertEqual(payload["pid"], 9876)


if __name__ == "__main__":
    unittest.main()
