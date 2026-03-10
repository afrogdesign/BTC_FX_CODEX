from __future__ import annotations

from typing import Any

import pandas as pd


def _nearest_level(price: float, levels: list[float], direction: str) -> float | None:
    if direction == "above":
        candidates = [level for level in levels if level > price]
        return min(candidates) if candidates else None
    candidates = [level for level in levels if level < price]
    return max(candidates) if candidates else None


def _swept_recently(price: float, recent_high: float, recent_low: float, atr: float) -> bool:
    threshold = max(atr * 0.15, price * 0.0005)
    return abs(price - recent_high) <= threshold or abs(price - recent_low) <= threshold


def analyze_liquidity(
    *,
    df_15m: pd.DataFrame,
    swings: dict[str, list[dict[str, Any]]],
    price: float,
    atr: float,
    equal_threshold_pct: float,
) -> dict[str, Any]:
    highs = [float(item["price"]) for item in swings.get("highs", [])[-8:]]
    lows = [float(item["price"]) for item in swings.get("lows", [])[-8:]]
    if not df_15m.empty:
        highs.append(float(df_15m["high"].tail(20).max()))
        lows.append(float(df_15m["low"].tail(20).min()))
        highs.extend(float(value) for value in df_15m["high"].tail(8).tolist())
        lows.extend(float(value) for value in df_15m["low"].tail(8).tolist())

    threshold = max(price * equal_threshold_pct, atr * 0.12, 1.0)
    clustered_highs: list[float] = []
    clustered_lows: list[float] = []
    for level in sorted(highs):
        if not clustered_highs or abs(level - clustered_highs[-1]) > threshold:
            clustered_highs.append(level)
    for level in sorted(lows):
        if not clustered_lows or abs(level - clustered_lows[-1]) > threshold:
            clustered_lows.append(level)

    nearest_above = _nearest_level(price, clustered_highs, "above")
    nearest_below = _nearest_level(price, clustered_lows, "below")
    recent_high = float(df_15m["high"].tail(6).max()) if not df_15m.empty else price
    recent_low = float(df_15m["low"].tail(6).min()) if not df_15m.empty else price

    return {
        "liquidity_above": round((nearest_above - price) / max(atr, 1e-9), 2) if nearest_above else None,
        "liquidity_below": round((price - nearest_below) / max(atr, 1e-9), 2) if nearest_below else None,
        "nearest_liquidity_above_price": round(nearest_above, 2) if nearest_above else None,
        "nearest_liquidity_below_price": round(nearest_below, 2) if nearest_below else None,
        "liquidity_swept_recently": _swept_recently(price, recent_high, recent_low, atr),
        "liquidity_levels_above": [round(level, 2) for level in clustered_highs if level > price][:5],
        "liquidity_levels_below": [round(level, 2) for level in reversed(clustered_lows) if level < price][:5],
    }
