from __future__ import annotations

import pandas as pd


def calculate_ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def get_ema_alignment(ema_fast: float, ema_mid: float, ema_slow: float) -> str:
    if ema_fast > ema_mid > ema_slow:
        return "bullish"
    if ema_fast < ema_mid < ema_slow:
        return "bearish"
    return "mixed"


def get_ema20_slope(ema20_series: pd.Series, lookback: int = 3) -> str:
    if len(ema20_series) < lookback + 1:
        return "flat"
    prev = float(ema20_series.iloc[-(lookback + 1)])
    curr = float(ema20_series.iloc[-1])
    if prev == 0:
        return "flat"
    slope_pct_per_bar = ((curr - prev) / abs(prev)) * 100 / lookback
    if slope_pct_per_bar > 0.05:
        return "up"
    if slope_pct_per_bar < -0.05:
        return "down"
    return "flat"
