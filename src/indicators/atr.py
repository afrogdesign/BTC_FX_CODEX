from __future__ import annotations

import pandas as pd


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / length, adjust=False, min_periods=length).mean().bfill()


def calculate_atr_ratio(atr_series: pd.Series, lookback: int = 50) -> float:
    if atr_series.empty:
        return 1.0
    current = float(atr_series.iloc[-1])
    baseline = float(atr_series.tail(lookback).mean()) if len(atr_series) >= lookback else float(atr_series.mean())
    if baseline == 0:
        return 1.0
    return current / baseline
