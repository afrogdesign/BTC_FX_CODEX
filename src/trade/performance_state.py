from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any


LOSS_OUTCOMES = {"loss", "expired"}
RECOVERY_OUTCOMES = {"win", "breakeven"}


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _parse_dt(value: str) -> datetime | None:
    stripped = str(value or "").strip()
    if not stripped:
        return None
    try:
        if stripped.endswith("Z"):
            return datetime.fromisoformat(stripped.replace("Z", "+00:00"))
        return datetime.fromisoformat(stripped)
    except ValueError:
        return None


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def load_loss_streak(
    *,
    base_dir: Path,
    fallback_streak: int = 0,
    trades_path: Path | None = None,
    outcomes_path: Path | None = None,
) -> int:
    trades_path = trades_path or base_dir / "logs" / "csv" / "trades.csv"
    outcomes_path = outcomes_path or base_dir / "logs" / "csv" / "signal_outcomes.csv"

    trades = {row.get("signal_id", ""): row for row in _load_csv_rows(trades_path) if row.get("signal_id", "")}
    outcomes = [row for row in _load_csv_rows(outcomes_path) if row.get("signal_id", "")]

    settled_rows: list[dict[str, str]] = []
    for outcome in outcomes:
        signal_id = str(outcome.get("signal_id", "")).strip()
        trade = trades.get(signal_id, {})
        if not trade:
            continue
        if not _parse_bool(trade.get("was_notified")):
            continue
        if str(outcome.get("evaluation_status", "")).strip() != "complete":
            continue
        settled_rows.append({**outcome, "timestamp_jst": trade.get("timestamp_jst", outcome.get("timestamp_jst", ""))})

    if not settled_rows:
        return max(int(fallback_streak), 0)

    settled_rows.sort(
        key=lambda row: _parse_dt(row.get("timestamp_jst", "")) or datetime.min,
        reverse=True,
    )

    streak = 0
    for row in settled_rows:
        outcome = str(row.get("outcome", "")).strip()
        if outcome in LOSS_OUTCOMES:
            streak += 1
            continue
        if outcome in RECOVERY_OUTCOMES:
            break
    return streak
