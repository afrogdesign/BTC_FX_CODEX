from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd


def _evaluate_one(signal: dict[str, Any], future_df: pd.DataFrame, horizon_bars: int = 32) -> dict[str, Any]:
    bias = signal["bias"]
    if bias not in {"long", "short"}:
        return {"result": "skip", "realized_rr": 0.0}

    setup = signal["long_setup"] if bias == "long" else signal["short_setup"]
    if setup["status"] == "invalid":
        return {"result": "skip", "realized_rr": 0.0}

    tp1 = float(setup["tp1"])
    stop = float(setup["stop_loss"])
    entry = float(setup["entry_mid"])
    risk = abs(entry - stop)
    if risk <= 0:
        return {"result": "skip", "realized_rr": 0.0}

    sample = future_df.head(horizon_bars)
    for row in sample.itertuples(index=False):
        high = float(getattr(row, "high"))
        low = float(getattr(row, "low"))
        if bias == "long":
            if low <= stop:
                return {"result": "loss", "realized_rr": -1.0}
            if high >= tp1:
                return {"result": "win", "realized_rr": (tp1 - entry) / risk}
        else:
            if high >= stop:
                return {"result": "loss", "realized_rr": -1.0}
            if low <= tp1:
                return {"result": "win", "realized_rr": (entry - tp1) / risk}
    return {"result": "unresolved", "realized_rr": 0.0}


def evaluate_signals(signals: list[dict[str, Any]], df_15m: pd.DataFrame) -> list[dict[str, Any]]:
    ts_to_index = {int(ts): idx for idx, ts in enumerate(df_15m["timestamp"].tolist())}
    evaluated = []
    for signal in signals:
        idx = ts_to_index.get(int(signal["timestamp"]))
        if idx is None:
            continue
        future = df_15m.iloc[idx + 1 :].copy()
        result = _evaluate_one(signal, future)
        merged = dict(signal)
        merged.update(result)
        evaluated.append(merged)
    return evaluated


def save_evaluation_csv(path: Path, evaluated: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "timestamp",
        "price",
        "bias",
        "phase",
        "confidence",
        "market_regime",
        "long_display_score",
        "short_display_score",
        "score_gap",
        "primary_setup_side",
        "primary_setup_status",
        "result",
        "realized_rr",
    ]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        for row in evaluated:
            writer.writerow({k: row.get(k) for k in fields})
    return path
