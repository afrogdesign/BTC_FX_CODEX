from __future__ import annotations


def determine_phase(
    *,
    bias: str,
    market_regime: str,
    pullback_depth_atr: float,
    breakout_confirmed: bool,
    reversal_risk_flag: bool,
    price: float,
    ema50: float,
    ema200: float,
) -> str:
    if reversal_risk_flag:
        return "reversal_risk"
    if breakout_confirmed:
        return "breakout"
    if market_regime == "range" or bias == "wait":
        return "range"

    between_ema50_200 = min(ema50, ema200) <= price <= max(ema50, ema200)
    if market_regime in {"uptrend", "downtrend"}:
        if pullback_depth_atr >= 0.8 or between_ema50_200:
            return "pullback"
        return "trend_following"
    return "range"
