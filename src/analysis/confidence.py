from __future__ import annotations

from typing import Any


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def count_agreeing_timeframes(signals_4h: str, signals_1h: str, signals_15m: str, bias: str) -> int:
    return sum(1 for signal in (signals_4h, signals_1h, signals_15m) if signal == bias)


def compute_machine_agreement(
    *,
    bias: str,
    market_regime: str,
    ema_alignment_4h: str,
    price: float,
    support_zones: list[dict[str, Any]],
    resistance_zones: list[dict[str, Any]],
    volume_ratio: float,
    funding_rate: float,
) -> str:
    if bias not in {"long", "short"}:
        return "partial"

    matched = 0

    if bias == "long" and market_regime in {"uptrend", "transition"}:
        matched += 1
    elif bias == "short" and market_regime in {"downtrend", "transition"}:
        matched += 1

    if bias == "long" and ema_alignment_4h == "bullish":
        matched += 1
    elif bias == "short" and ema_alignment_4h == "bearish":
        matched += 1

    if bias == "long":
        above_support = any(float(z["high"]) <= price for z in support_zones) or any(
            float(z["low"]) <= price <= float(z["high"]) for z in support_zones
        )
        below_resistance = any(float(z["low"]) >= price for z in resistance_zones)
        if above_support and below_resistance:
            matched += 1
    else:
        below_resistance = any(float(z["low"]) >= price for z in resistance_zones) or any(
            float(z["low"]) <= price <= float(z["high"]) for z in resistance_zones
        )
        above_support = any(float(z["high"]) <= price for z in support_zones)
        if below_resistance and above_support:
            matched += 1

    if bias == "long":
        if volume_ratio >= 1.0 and funding_rate <= 0.05:
            matched += 1
    else:
        if volume_ratio >= 1.0 and funding_rate >= -0.03:
            matched += 1

    if matched >= 3:
        return "agree"
    if matched == 2:
        return "partial"
    return "disagree"


def compute_confidence(inputs: dict[str, Any], cfg: Any) -> int:
    bias = inputs["bias"]
    long_display = int(inputs["long_display_score"])
    short_display = int(inputs["short_display_score"])
    signals_4h = inputs["signals_4h"]
    signals_1h = inputs["signals_1h"]
    signals_15m = inputs["signals_15m"]
    regime = inputs["market_regime"]
    phase = inputs["phase"]
    rr_estimate = float(inputs["rr_estimate"])
    opposite_gap_atr = float(inputs["opposite_gap_atr"])
    critical_zone = bool(inputs["critical_zone"])
    warning_flags = inputs.get("warning_flags", [])

    if bias == "long":
        confidence = float(long_display)
    elif bias == "short":
        confidence = float(short_display)
    else:
        confidence = min(50.0, max(long_display, short_display) * 0.6)

    agreeing = count_agreeing_timeframes(signals_4h, signals_1h, signals_15m, bias)
    if agreeing >= 3:
        confidence += 15
    elif agreeing == 2:
        confidence += 8

    if regime in {"uptrend", "downtrend"}:
        confidence += 10
    elif regime == "range":
        confidence -= 5
    elif regime == "volatile":
        confidence -= 10

    if phase == "trend_following":
        confidence += 5
    elif phase == "pullback":
        confidence += 3
    elif phase == "range":
        confidence -= 5
    elif phase == "reversal_risk":
        confidence -= 10

    if rr_estimate >= 2.0:
        confidence += 10
    elif rr_estimate >= 1.5:
        confidence += 5
    elif rr_estimate < 1.3:
        confidence -= 15

    if opposite_gap_atr >= 1.5:
        confidence += 5
    elif opposite_gap_atr < 0.8:
        confidence -= 5

    if critical_zone:
        confidence -= 10
    confidence -= 5 * len(warning_flags)

    return int(round(_clamp(confidence, 0, 100)))


def confidence_gate_ok(bias: str, confidence: int, cfg: Any) -> bool:
    if bias == "long":
        return confidence >= cfg.CONFIDENCE_LONG_MIN
    if bias == "short":
        return confidence >= cfg.CONFIDENCE_SHORT_MIN
    return False
