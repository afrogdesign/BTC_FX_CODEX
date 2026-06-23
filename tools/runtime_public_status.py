from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _base_dir() -> Path:
    return Path.cwd()


def _startup_status_path(base_dir: Path) -> Path:
    return base_dir / "logs" / "runtime" / "startup_status.json"


def _read_startup_status(base_dir: Path) -> dict[str, Any] | None:
    path = _startup_status_path(base_dir)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _latest_public_html_path(base_dir: Path) -> Path | None:
    html_root = base_dir / "logs" / "notifications_html"
    if not html_root.exists():
        return None
    latest_path: Path | None = None
    latest_mtime = -1.0
    for path in html_root.rglob("*.html"):
        if not path.is_file():
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime > latest_mtime or (mtime == latest_mtime and latest_path is not None and path.as_posix() > latest_path.as_posix()):
            latest_mtime = mtime
            latest_path = path
    return latest_path


def _format_mtime_utc(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def build_runtime_public_status(base_dir: Path | None = None) -> dict[str, Any]:
    base_dir = base_dir or _base_dir()
    startup_status = _read_startup_status(base_dir)
    startup_status_available = bool(startup_status and startup_status.get("timestamp_utc") and startup_status.get("pid") is not None)

    timestamp_utc = None
    pid = None
    timezone_name = None
    next_report_time = None
    report_times_count = 0
    startup_dt: datetime | None = None

    if startup_status_available:
        timestamp_utc = str(startup_status.get("timestamp_utc", "")).strip() or None
        pid = startup_status.get("pid")
        timezone_name = str(startup_status.get("timezone", "")).strip() or None
        next_report_time = str(startup_status.get("next_report_time", "")).strip() or None
        report_times = startup_status.get("report_times")
        if isinstance(report_times, list):
            report_times_count = sum(1 for item in report_times if str(item).strip())
        try:
            if timestamp_utc:
                startup_dt = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
        except ValueError:
            startup_status_available = False
            timestamp_utc = None
            pid = None
            timezone_name = None
            next_report_time = None
            report_times_count = 0
            startup_dt = None

    latest_html_path = _latest_public_html_path(base_dir)
    latest_html_mtime = _format_mtime_utc(latest_html_path)
    html_after_startup = bool(
        startup_status_available
        and startup_dt is not None
        and latest_html_path is not None
        and latest_html_mtime is not None
        and datetime.fromtimestamp(latest_html_path.stat().st_mtime, tz=timezone.utc) > startup_dt
    )

    return {
        "startup_status_available": startup_status_available,
        "timestamp_utc": timestamp_utc,
        "pid": pid,
        "timezone": timezone_name,
        "next_report_time": next_report_time,
        "report_times_count": report_times_count,
        "latest_html_path": str(latest_html_path.relative_to(base_dir)) if latest_html_path is not None else None,
        "latest_html_mtime": latest_html_mtime,
        "html_after_startup": html_after_startup,
    }


def main() -> int:
    payload = build_runtime_public_status()
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
