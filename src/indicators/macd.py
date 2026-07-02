from __future__ import annotations

from typing import Any

import pandas as pd


def calculate_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict[str, pd.Series]:
    close = close.astype(float)
    fast_ema = close.ewm(span=max(int(fast), 1), adjust=False, min_periods=1).mean()
    slow_ema = close.ewm(span=max(int(slow), 1), adjust=False, min_periods=1).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=max(int(signal), 1), adjust=False, min_periods=1).mean()
    histogram = macd_line - signal_line
    return {
        "macd": macd_line.fillna(0.0),
        "signal": signal_line.fillna(0.0),
        "histogram": histogram.fillna(0.0),
    }


def _series_last(series: pd.Series | Any, default: float = 0.0) -> float:
    try:
        if series is None or len(series) == 0:
            return float(default)
        return float(series.iloc[-1])
    except Exception:  # noqa: BLE001
        return float(default)


def classify_macd_momentum(
    macd_line: pd.Series | Any,
    signal_line: pd.Series | Any,
    histogram: pd.Series | Any,
    histogram_prev: float | None = None,
) -> dict[str, Any]:
    macd_value = _series_last(macd_line)
    signal_value = _series_last(signal_line)
    histogram_value = _series_last(histogram)
    previous_histogram = float(histogram_prev) if histogram_prev is not None else histogram_value
    above_signal = macd_value > signal_value
    below_signal = macd_value < signal_value
    histogram_improving = above_signal and histogram_value >= 0
    histogram_weakening = below_signal and histogram_value <= 0
    if histogram_prev is not None:
        histogram_improving = histogram_improving or histogram_value > previous_histogram
        histogram_weakening = histogram_weakening or histogram_value < previous_histogram
    zero_line_recovery = macd_value >= 0 and histogram_value >= 0
    zero_line_rejection = macd_value <= 0 and histogram_value <= 0

    state = "neutral"
    if above_signal and (histogram_value >= 0 or histogram_improving or zero_line_recovery):
        state = "constructive_up"
    elif below_signal and (histogram_value <= 0 or histogram_weakening or zero_line_rejection):
        state = "constructive_down"
    elif above_signal:
        state = "upward"
    elif below_signal:
        state = "downward"

    return {
        "state": state,
        "above_signal": above_signal,
        "below_signal": below_signal,
        "histogram_improving": histogram_improving,
        "histogram_weakening": histogram_weakening,
        "zero_line_recovery": zero_line_recovery,
        "zero_line_rejection": zero_line_rejection,
        "macd": macd_value,
        "signal": signal_value,
        "histogram": histogram_value,
        "histogram_prev": previous_histogram,
    }
