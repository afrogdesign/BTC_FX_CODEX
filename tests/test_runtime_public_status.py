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


def _run_cli(base_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
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
        self.assertEqual(payload["operator_status"], "ok")
        self.assertEqual(payload["operator_message"], "post-startup public HTML found")
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
        self.assertEqual(payload["operator_status"], "waiting_for_html_cycle")
        self.assertEqual(payload["operator_message"], "waiting for the next HTML cycle")

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
        self.assertEqual(payload["operator_status"], "startup_status_unavailable")
        self.assertEqual(payload["operator_message"], "startup status unavailable")

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
        self.assertEqual(payload["operator_status"], "startup_status_unavailable")
        self.assertEqual(payload["operator_message"], "startup status unavailable")

    def test_cli_pretty_mode_is_human_readable_and_safe(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)
            _write_html(base_dir, "ver03-v4/main/20260623_101500.html", mtime=datetime(2026, 6, 23, 10, 16, tzinfo=timezone.utc).timestamp())

            completed = _run_cli(base_dir, "--pretty")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("{", completed.stdout)
        self.assertIn("operator_status: ok", completed.stdout)
        self.assertIn("operator_message: post-startup public HTML found", completed.stdout)
        self.assertIn("next_report_time: 2026-06-23T20:05:00+09:00", completed.stdout)
        self.assertIn("latest_html_path: logs/notifications_html/ver03-v4/main/20260623_101500.html", completed.stdout)
        self.assertIn("latest_html_mtime: 2026-06-23T10:16:00Z", completed.stdout)
        self.assertIn("html_after_startup: true", completed.stdout)
        self.assertNotIn("/Users/", completed.stdout)
        self.assertNotIn("OPENAI_API_KEY", completed.stdout)
        self.assertNotIn("SMTP_PASSWORD", completed.stdout)
        self.assertNotIn("private/order", completed.stdout)
        self.assertNotIn("automatic_order_allowed=true", completed.stdout)

    def test_cli_check_mode_exit_codes(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)
            _write_html(base_dir, "ver03-v4/main/20260623_101500.html", mtime=datetime(2026, 6, 23, 10, 16, tzinfo=timezone.utc).timestamp())

            ok_completed = _run_cli(base_dir, "--check")

        self.assertEqual(ok_completed.returncode, 0, ok_completed.stdout + ok_completed.stderr)
        self.assertIn("operator_status: ok", ok_completed.stdout)
        self.assertIn("operator_message: post-startup public HTML found", ok_completed.stdout)

        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)

            waiting_completed = _run_cli(base_dir, "--check")

        self.assertEqual(waiting_completed.returncode, 2, waiting_completed.stdout + waiting_completed.stderr)
        self.assertIn("operator_status: waiting_for_html_cycle", waiting_completed.stdout)
        self.assertIn("operator_message: waiting for the next HTML cycle", waiting_completed.stdout)

        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            unavailable_completed = _run_cli(base_dir, "--check")

        self.assertEqual(unavailable_completed.returncode, 3, unavailable_completed.stdout + unavailable_completed.stderr)
        self.assertIn("operator_status: startup_status_unavailable", unavailable_completed.stdout)
        self.assertIn("operator_message: startup status unavailable", unavailable_completed.stdout)

    def test_html_after_startup_handles_disappearing_html_path(self) -> None:
        from tools.runtime_public_status import _html_after_startup

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.html"

        self.assertFalse(_html_after_startup(path, datetime(2026, 6, 23, 10, 14, tzinfo=timezone.utc)))


if __name__ == "__main__":
    unittest.main()
