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
SCRIPT_PATH = BASE_DIR / "tools" / "operator_status.py"


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


def _write_html(base_dir: Path, relative_path: str, *, mtime: float) -> None:
    path = base_dir / "logs" / "notifications_html" / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<html><body>safe</body></html>", encoding="utf-8")
    os.utime(path, (mtime, mtime))


def _run_cli(base_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=base_dir,
        capture_output=True,
        text=True,
        check=False,
    )


class OperatorStatusCliTest(unittest.TestCase):
    def test_default_output_contains_operator_status_and_message(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)
            _write_html(base_dir, "ver03-v4/main/20260623_101500.html", mtime=datetime(2026, 6, 23, 10, 16, tzinfo=timezone.utc).timestamp())

            completed = _run_cli(base_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("operator_status:", completed.stdout)
        self.assertIn("operator_message:", completed.stdout)
        self.assertNotIn("{", completed.stdout)
        self.assertNotIn("/Users/", completed.stdout)
        self.assertNotIn("OPENAI_API_KEY", completed.stdout)
        self.assertNotIn("SMTP_PASSWORD", completed.stdout)
        self.assertNotIn("private/order", completed.stdout)
        self.assertNotIn("automatic_order_allowed=true", completed.stdout)

    def test_check_exit_codes(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)
            _write_html(base_dir, "ver03-v4/main/20260623_101500.html", mtime=datetime(2026, 6, 23, 10, 16, tzinfo=timezone.utc).timestamp())

            ok_completed = _run_cli(base_dir, "--check")

        self.assertEqual(ok_completed.returncode, 0, ok_completed.stdout + ok_completed.stderr)
        self.assertIn("operator_status: ok", ok_completed.stdout)

        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)

            waiting_completed = _run_cli(base_dir, "--check")

        self.assertEqual(waiting_completed.returncode, 2, waiting_completed.stdout + waiting_completed.stderr)
        self.assertIn("operator_status: waiting_for_html_cycle", waiting_completed.stdout)

        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            unavailable_completed = _run_cli(base_dir, "--check")

        self.assertEqual(unavailable_completed.returncode, 3, unavailable_completed.stdout + unavailable_completed.stderr)
        self.assertIn("operator_status: startup_status_unavailable", unavailable_completed.stdout)

    def test_check_mode_output_is_safe(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            _write_startup_status(base_dir)

            completed = _run_cli(base_dir, "--check")

        self.assertIn("operator_message:", completed.stdout)
        self.assertNotIn("/Users/", completed.stdout)
        self.assertNotIn("OPENAI_API_KEY", completed.stdout)
        self.assertNotIn("SMTP_PASSWORD", completed.stdout)
        self.assertNotIn("private/order", completed.stdout)
        self.assertNotIn("automatic_order_allowed=true", completed.stdout)


if __name__ == "__main__":
    unittest.main()
