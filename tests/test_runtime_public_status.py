from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = BASE_DIR / "tools" / "runtime_public_status.py"


def _write_startup_status(base_dir: Path) -> None:
    runtime_dir = base_dir / "logs" / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "startup_status.json").write_text(
        json.dumps(
            {
                "timestamp_utc": "2026-06-23T10:14:04.611446Z",
                "pid": 84464,
                "timezone": "Asia/Tokyo",
                "report_times": ["00:05", "09:05", "20:05"],
                "next_report_time": "2026-06-23T20:05:00+09:00",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_html(base_dir: Path, relative_path: str, *, mtime: float) -> Path:
    path = base_dir / "logs" / "notifications_html" / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<html><body>safe</body></html>", encoding="utf-8")
    os.utime(path, (mtime, mtime))
    return path


def _run_cli(base_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=base_dir,
        capture_output=True,
        text=True,
        check=False,
    )


class RuntimePublicStatusCliTest(unittest.TestCase):
    def test_cli_reports_startup_and_latest_html_after_startup(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)
            older = _write_html(base_dir, "ver03-v4/main/20260623_101000.html", mtime=datetime(2026, 6, 23, 10, 11, tzinfo=timezone.utc).timestamp())
            latest = _write_html(base_dir, "ver03-v4/main/20260623_101500.html", mtime=datetime(2026, 6, 23, 10, 16, tzinfo=timezone.utc).timestamp())

            completed = _run_cli(base_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["startup_status_available"])
        self.assertEqual(payload["timestamp_utc"], "2026-06-23T10:14:04.611446Z")
        self.assertEqual(payload["pid"], 84464)
        self.assertEqual(payload["timezone"], "Asia/Tokyo")
        self.assertEqual(payload["next_report_time"], "2026-06-23T20:05:00+09:00")
        self.assertEqual(payload["report_times_count"], 3)
        self.assertEqual(payload["latest_html_path"], "logs/notifications_html/ver03-v4/main/20260623_101500.html")
        self.assertEqual(payload["latest_html_mtime"], "2026-06-23T10:16:00Z")
        self.assertTrue(payload["html_after_startup"])
        self.assertEqual(older.name, "20260623_101000.html")
        self.assertEqual(latest.name, "20260623_101500.html")

    def test_cli_handles_missing_latest_html_safely(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)

            completed = _run_cli(base_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["startup_status_available"])
        self.assertIsNone(payload["latest_html_path"])
        self.assertIsNone(payload["latest_html_mtime"])
        self.assertFalse(payload["html_after_startup"])

    def test_cli_handles_missing_startup_status_safely(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_html(base_dir, "ver03-v4/attention/20260623_101500.html", mtime=datetime(2026, 6, 23, 10, 16, tzinfo=timezone.utc).timestamp())

            completed = _run_cli(base_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["startup_status_available"])
        self.assertIsNone(payload["timestamp_utc"])
        self.assertIsNone(payload["pid"])
        self.assertIsNone(payload["timezone"])
        self.assertIsNone(payload["next_report_time"])
        self.assertEqual(payload["report_times_count"], 0)
        self.assertEqual(payload["latest_html_path"], "logs/notifications_html/ver03-v4/attention/20260623_101500.html")
        self.assertEqual(payload["latest_html_mtime"], "2026-06-23T10:16:00Z")
        self.assertFalse(payload["html_after_startup"])

    def test_cli_handles_malformed_startup_status_safely(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            runtime_dir = base_dir / "logs" / "runtime"
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "startup_status.json").write_text("{not json", encoding="utf-8")
            _write_html(base_dir, "ver03-v4/main/20260623_102000.html", mtime=datetime(2026, 6, 23, 10, 21, tzinfo=timezone.utc).timestamp())

            completed = _run_cli(base_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["startup_status_available"])
        self.assertIsNone(payload["timestamp_utc"])
        self.assertIsNone(payload["pid"])
        self.assertIsNone(payload["timezone"])
        self.assertIsNone(payload["next_report_time"])
        self.assertEqual(payload["report_times_count"], 0)
        self.assertEqual(payload["latest_html_path"], "logs/notifications_html/ver03-v4/main/20260623_102000.html")
        self.assertEqual(payload["latest_html_mtime"], "2026-06-23T10:21:00Z")
        self.assertFalse(payload["html_after_startup"])


if __name__ == "__main__":
    unittest.main()
