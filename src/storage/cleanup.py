from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from .json_store import load_json, save_json


def _cleanup_dir(directory: Path, retention_days: int, now: datetime) -> int:
    if not directory.exists():
        return 0
    threshold = now - timedelta(days=retention_days)
    removed = 0
    for item in directory.iterdir():
        if not item.is_file():
            continue
        mtime = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc)
        if mtime < threshold:
            item.unlink(missing_ok=True)
            removed += 1
    return removed


def cleanup_if_due(base_dir: Path, cfg: object, now: datetime | None = None) -> dict[str, int]:
    now = now or datetime.now(tz=timezone.utc)
    state_path = base_dir / "logs" / ".cleanup_state.json"
    state = load_json(state_path) or {}

    last_run = None
    raw = state.get("last_cleanup_utc")
    if isinstance(raw, str):
        try:
            last_run = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            last_run = None

    if last_run and now - last_run < timedelta(hours=24):
        return {"signals": 0, "notifications": 0, "errors": 0}

    removed = {
        "signals": _cleanup_dir(base_dir / "logs" / "signals", cfg.LOG_RETENTION_SIGNALS_DAYS, now),
        "notifications": _cleanup_dir(
            base_dir / "logs" / "notifications", cfg.LOG_RETENTION_NOTIFICATIONS_DAYS, now
        ),
        "errors": _cleanup_dir(base_dir / "logs" / "errors", cfg.LOG_RETENTION_ERRORS_DAYS, now),
    }
    save_json(state_path, {"last_cleanup_utc": now.isoformat().replace("+00:00", "Z")})
    return removed
