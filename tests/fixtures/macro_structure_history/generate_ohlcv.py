from __future__ import annotations

import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def write(path: Path, count: int, interval: timedelta, label: str) -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("timestamp_utc", "open", "high", "low", "close", "interval"))
        for index in range(count):
            timestamp = start + index * interval
            phase = index % 16
            close = 100 + (phase if phase <= 8 else 16 - phase) * 2
            writer.writerow((timestamp.isoformat().replace("+00:00", "Z"), close - 1, close + 2, close - 2, close, label))


if __name__ == "__main__":
    root = Path(sys.argv[1])
    write(root / "ohlcv_15m.csv", 600, timedelta(minutes=15), "15m")
    write(root / "ohlcv_1h.csv", 180, timedelta(hours=1), "1h")
    write(root / "ohlcv_4h.csv", 60, timedelta(hours=4), "4h")
