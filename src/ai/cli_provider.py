from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any


def _normalize_command(command: str) -> list[str]:
    parts = shlex.split(str(command).strip())
    if not parts:
        raise ValueError("CLI command is empty")
    return parts


def run_cli_json(
    *,
    command: str,
    timeout_sec: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    completed = subprocess.run(
        _normalize_command(command),
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"CLI exited with code {completed.returncode}")
    raw = completed.stdout.strip()
    if not raw:
        raise RuntimeError("CLI returned empty output")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("CLI output was not a JSON object")
    return parsed


def run_cli_text(
    *,
    command: str,
    timeout_sec: int,
    payload: dict[str, Any],
) -> str:
    completed = subprocess.run(
        _normalize_command(command),
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"CLI exited with code {completed.returncode}")
    return completed.stdout.strip()


def write_ai_error_log(base_dir: Path, title: str, details: str) -> None:
    from datetime import datetime, timezone

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = base_dir / "logs" / "errors" / f"{ts}_{title}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(details, encoding="utf-8")
