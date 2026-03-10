from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        content = path.read_text(encoding="utf-8")
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except Exception:  # noqa: BLE001
        return None


def save_json(path: Path, payload: dict[str, Any]) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_signal_snapshot(base_dir: Path, payload: dict[str, Any]) -> Path:
    signal_id = str(payload.get("signal_id", "")).strip()
    ts = signal_id or datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = base_dir / "logs" / "signals" / f"{ts}.json"
    save_json(path, payload)
    return path


def get_last_result_path(base_dir: Path) -> Path:
    return base_dir / "logs" / "last_result.json"


def get_last_notified_path(base_dir: Path) -> Path:
    return base_dir / "logs" / "last_notified.json"
