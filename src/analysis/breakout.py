from __future__ import annotations

from typing import Any


def previous_breakout_levels(df_15m: Any, lookback_bars: int) -> tuple[float | None, float | None]:
    if lookback_bars <= 0 or len(df_15m) < 2:
        return None, None
    window = df_15m.iloc[-(lookback_bars + 1) : -1]
    if getattr(window, "empty", False):
        return None, None
    return float(window["high"].max()), float(window["low"].min())
