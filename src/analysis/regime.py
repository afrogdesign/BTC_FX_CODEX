from __future__ import annotations

from typing import Any


def _ema50_slope_pct_per_bar(ema50_series: list[float], bars: int = 3) -> float:
    if len(ema50_series) < bars + 1:
        return 0.0
    prev = float(ema50_series[-(bars + 1)])
    curr = float(ema50_series[-1])
    if prev == 0:
        return 0.0
    return ((curr - prev) / abs(prev)) * 100 / bars


def determine_transition_direction(
    *,
    ema20: float,
    ema20_prev: float,
    ema50: float,
    ema50_series: list[float],
    rsi14: float,
    structure_4h: str,
    atr_value: float,
) -> str:
    near_cross = abs(ema20 - ema50) <= atr_value * 0.5
    ema20_up = ema20 > ema20_prev
    ema20_down = ema20 < ema20_prev
    ema50_slope = _ema50_slope_pct_per_bar(ema50_series, bars=3)

    up_conditions = 0
    down_conditions = 0

    if near_cross and ema20_up:
        up_conditions += 1
    if near_cross and ema20_down:
        down_conditions += 1

    if ema50_slope > -0.05:
        up_conditions += 1
    if ema50_slope < 0.05:
        down_conditions += 1

    if rsi14 >= 50:
        up_conditions += 1
    if rsi14 < 50:
        down_conditions += 1

    if structure_4h == "hh_hl":
        up_conditions += 1
    if structure_4h == "lh_ll":
        down_conditions += 1

    if up_conditions >= 3 and up_conditions > down_conditions:
        return "up"
    if down_conditions >= 3 and down_conditions > up_conditions:
        return "down"
    return ""


def classify_market_regime(
    *,
    ema_alignment_4h: str,
    ema20_slope_4h: str,
    structure_4h: str,
    atr_ratio: float,
    rsi_4h: float,
    ema20_4h: float,
    ema20_prev_4h: float,
    ema50_4h: float,
    ema50_series_4h: list[float],
    atr_4h: float,
) -> dict[str, Any]:
    transition_direction = determine_transition_direction(
        ema20=ema20_4h,
        ema20_prev=ema20_prev_4h,
        ema50=ema50_4h,
        ema50_series=ema50_series_4h,
        rsi14=rsi_4h,
        structure_4h=structure_4h,
        atr_value=atr_4h,
    )

    if atr_ratio >= 2.0:
        regime = "volatile"
    elif ema_alignment_4h == "bullish" and structure_4h == "hh_hl" and ema20_slope_4h == "up":
        regime = "uptrend"
    elif ema_alignment_4h == "bearish" and structure_4h == "lh_ll" and ema20_slope_4h == "down":
        regime = "downtrend"
    elif transition_direction in {"up", "down"}:
        regime = "transition"
    else:
        regime = "range"

    if regime != "transition":
        transition_direction = ""

    return {"market_regime": regime, "transition_direction": transition_direction}
