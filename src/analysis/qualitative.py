from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd


def _calc_session(timestamp_utc_ms: int, timezone_name: str) -> str:
    dt = datetime.fromtimestamp(timestamp_utc_ms / 1000, tz=ZoneInfo("UTC")).astimezone(
        ZoneInfo(timezone_name)
    )
    hour = dt.hour
    if 6 <= hour < 15:
        return "asia"
    if 15 <= hour < 22:
        return "europe"
    return "us"


def _wick_rejection_score(df_15m: pd.DataFrame) -> float:
    if df_15m.empty:
        return 0.0
    sample = df_15m.tail(3)
    score = 0.0
    for row in sample.itertuples(index=False):
        high = float(getattr(row, "high"))
        low = float(getattr(row, "low"))
        open_ = float(getattr(row, "open"))
        close = float(getattr(row, "close"))
        body = abs(close - open_)
        candle_range = max(high - low, 1e-9)
        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low
        wick_ratio = max(upper_wick, lower_wick) / candle_range
        if wick_ratio > 0.5 and body / candle_range < 0.4:
            score += 1
    return score / 3


def _body_strength(df_15m: pd.DataFrame) -> float:
    if df_15m.empty:
        return 0.0
    sample = df_15m.tail(5)
    strengths: list[float] = []
    for row in sample.itertuples(index=False):
        high = float(getattr(row, "high"))
        low = float(getattr(row, "low"))
        open_ = float(getattr(row, "open"))
        close = float(getattr(row, "close"))
        candle_range = max(high - low, 1e-9)
        strengths.append(abs(close - open_) / candle_range)
    return float(sum(strengths) / len(strengths))


def build_qualitative_context(
    *,
    now_ms: int,
    timezone_name: str,
    df_15m: pd.DataFrame,
    market_regime: str,
    bias: str,
    no_trade_flags: list[str],
    price: float,
    ema50: float,
    atr: float,
) -> dict:
    pullback_depth_atr = abs(price - ema50) / atr if atr > 0 else 0.0
    wick_score = _wick_rejection_score(df_15m)
    body_strength = _body_strength(df_15m)

    late_entry_risk = pullback_depth_atr > 1.6 and bias in {"long", "short"}
    trend_exhaustion_risk = wick_score > 0.66 and body_strength < 0.35

    if market_regime == "range":
        range_state = "inside_range"
    elif market_regime == "transition":
        range_state = "transitioning"
    else:
        range_state = "trend"

    rule_conflicts = []
    if "ATR_extreme" in no_trade_flags:
        rule_conflicts.append("atr_extreme")
    if any(flag.startswith("Funding") for flag in no_trade_flags):
        rule_conflicts.append("funding_risk")
    if late_entry_risk:
        rule_conflicts.append("late_entry")
    if trend_exhaustion_risk:
        rule_conflicts.append("trend_exhaustion")

    return {
        "session": _calc_session(now_ms, timezone_name),
        "pullback_depth_atr": round(pullback_depth_atr, 2),
        "wick_rejection": round(wick_score, 2),
        "body_strength": round(body_strength, 2),
        "range_state": range_state,
        "late_entry_risk": late_entry_risk,
        "trend_exhaustion_risk": trend_exhaustion_risk,
        "rule_conflicts": sorted(set(rule_conflicts)),
    }
