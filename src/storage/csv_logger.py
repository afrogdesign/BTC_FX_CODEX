from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


CSV_HEADER = [
    "timestamp_utc",
    "timestamp_jst",
    "bias",
    "phase",
    "market_regime",
    "transition_direction",
    "long_display_score",
    "short_display_score",
    "score_gap",
    "confidence",
    "agreement_with_machine",
    "primary_setup_side",
    "primary_setup_status",
    "funding_rate",
    "atr_ratio",
    "volume_ratio",
    "rr_estimate",
    "long_status",
    "short_status",
    "long_rr",
    "short_rr",
    "no_trade_flags",
    "reason_for_notification",
]


def append_trade_log(base_dir: Path, payload: dict[str, Any]) -> Path:
    path = base_dir / "logs" / "csv" / "trades.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()

    row = {
        "timestamp_utc": payload.get("timestamp_utc"),
        "timestamp_jst": payload.get("timestamp_jst"),
        "bias": payload.get("bias"),
        "phase": payload.get("phase"),
        "market_regime": payload.get("market_regime"),
        "transition_direction": payload.get("transition_direction"),
        "long_display_score": payload.get("long_display_score"),
        "short_display_score": payload.get("short_display_score"),
        "score_gap": payload.get("score_gap"),
        "confidence": payload.get("confidence"),
        "agreement_with_machine": payload.get("agreement_with_machine"),
        "primary_setup_side": payload.get("primary_setup_side"),
        "primary_setup_status": payload.get("primary_setup_status"),
        "funding_rate": payload.get("funding_rate"),
        "atr_ratio": payload.get("atr_ratio"),
        "volume_ratio": payload.get("volume_ratio"),
        "rr_estimate": payload.get("rr_estimate"),
        "long_status": (payload.get("long_setup") or {}).get("status"),
        "short_status": (payload.get("short_setup") or {}).get("status"),
        "long_rr": (payload.get("long_setup") or {}).get("rr_estimate"),
        "short_rr": (payload.get("short_setup") or {}).get("rr_estimate"),
        "no_trade_flags": ",".join(payload.get("no_trade_flags", [])),
        "reason_for_notification": ",".join(payload.get("reason_for_notification", [])),
    }

    with path.open("a", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=CSV_HEADER)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    return path
