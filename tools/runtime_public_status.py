from __future__ import annotations

import json
import argparse
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


def _html_after_startup(latest_html_path: Path | None, startup_dt: datetime | None) -> bool:
    if latest_html_path is None or startup_dt is None:
        return False
    try:
        latest_mtime = latest_html_path.stat().st_mtime
    except OSError:
        return False
    return datetime.fromtimestamp(latest_mtime, tz=timezone.utc) > startup_dt


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
    html_after_startup = bool(startup_status_available and _html_after_startup(latest_html_path, startup_dt))
    if not startup_status_available:
        operator_status = "startup_status_unavailable"
        operator_message = "startup status unavailable"
    elif html_after_startup:
        operator_status = "ok"
        operator_message = "post-startup public HTML found"
    else:
        operator_status = "waiting_for_html_cycle"
        operator_message = "waiting for the next HTML cycle"

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
        "operator_status": operator_status,
        "operator_message": operator_message,
    }


def _format_pretty_status(payload: dict[str, Any]) -> str:
    lines = [
        "runtime_public_status",
        f"operator_status: {payload['operator_status']}",
        f"operator_message: {payload['operator_message']}",
        f"startup_status_available: {str(bool(payload['startup_status_available'])).lower()}",
        f"html_after_startup: {str(bool(payload['html_after_startup'])).lower()}",
    ]
    if payload.get("timestamp_utc"):
        lines.append(f"timestamp_utc: {payload['timestamp_utc']}")
    if payload.get("pid") is not None:
        lines.append(f"pid: {payload['pid']}")
    if payload.get("timezone"):
        lines.append(f"timezone: {payload['timezone']}")
    if payload.get("next_report_time"):
        lines.append(f"next_report_time: {payload['next_report_time']}")
    if payload.get("report_times_count") is not None:
        lines.append(f"report_times_count: {payload['report_times_count']}")
    if payload.get("latest_html_path"):
        lines.append(f"latest_html_path: {payload['latest_html_path']}")
    if payload.get("latest_html_mtime"):
        lines.append(f"latest_html_mtime: {payload['latest_html_mtime']}")
    return "\n".join(lines)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize runtime startup and public HTML status")
    parser.add_argument("--pretty", action="store_true", help="print a human-readable summary instead of JSON")
    parser.add_argument("--check", action="store_true", help="print the pretty summary and exit with a status code")
    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()
    payload = build_runtime_public_status()
    if args.pretty or args.check:
        print(_format_pretty_status(payload))
        if args.check:
            status = str(payload.get("operator_status"))
            if status == "ok":
                return 0
            if status == "waiting_for_html_cycle":
                return 2
            if status == "startup_status_unavailable":
                return 3
            return 3
        return 0
    else:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
