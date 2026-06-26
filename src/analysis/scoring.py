from __future__ import annotations

from typing import Any


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _normalize_display(raw: float) -> int:
    display = (raw + 30) / 80 * 100
    return int(round(_clamp(display, 0, 100)))


def _bucket_display(value: float) -> float:
    return round(_clamp((value + 20.0) / 60.0 * 100.0, 0.0, 100.0), 2)


def _add_factor(bucket: dict[str, float], code: str, delta: float) -> None:
    bucket[code] = round(bucket.get(code, 0.0) + delta, 4)


def _top_factors(factors: dict[str, float], *, positive: bool) -> list[dict[str, float | str]]:
    filtered = [
        {"code": code, "score": round(score, 4)}
        for code, score in factors.items()
        if (score > 0 if positive else score < 0)
    ]
    filtered.sort(key=lambda item: abs(float(item["score"])), reverse=True)
    return filtered[:3]


def decide_bias(long_display_score: int, short_display_score: int, long_threshold: int, short_threshold: int) -> tuple[str, int]:
    score_gap = int(round(long_display_score - short_display_score))
    if score_gap >= long_threshold:
        return "long", score_gap
    if score_gap <= -short_threshold:
        return "short", score_gap
    return "wait", score_gap


def compute_scores(inputs: dict[str, Any], cfg: Any) -> dict[str, Any]:
    long_raw = 0.0
    short_raw = 0.0
    long_factors: dict[str, float] = {}
    short_factors: dict[str, float] = {}
    no_trade_flags: list[str] = []
    warning_flags: list[str] = []

    regime = inputs["market_regime"]
    ema_alignment = inputs["ema_alignment_4h"]
    ema20_slope = inputs["ema20_slope_4h"]
    structure_4h = inputs["structure_4h"]
    structure_1h = inputs["structure_1h"]
    price = float(inputs["price"])
    ema50_4h = float(inputs["ema50_4h"])
    rsi_15m = float(inputs["rsi_15m"])
    volume_ratio = float(inputs["volume_ratio"])
    atr_ratio = float(inputs["atr_ratio"])
    funding_rate = float(inputs["funding_rate"])
    rr_long = float(inputs["rr_long"])
    rr_short = float(inputs["rr_short"])
    near_support = bool(inputs["near_support"])
    near_resistance = bool(inputs["near_resistance"])
    breakout_up = bool(inputs["breakout_up"])
    breakout_down = bool(inputs["breakout_down"])
    in_range_center = bool(inputs["in_range_center"])
    transition_direction = str(inputs.get("transition_direction", ""))
    signal_15m = str(inputs.get("signals_15m", ""))
    market_map = inputs.get("market_map") or {}
    market_map_flags = {
        str(flag or "").strip()
        for flag in market_map.get("flags", [])
        if str(flag or "").strip()
    }

    if regime == "uptrend":
        long_raw += 15
        _add_factor(long_factors, "regime_uptrend", 15.0)
    elif regime == "downtrend":
        short_raw += 15
        _add_factor(short_factors, "regime_downtrend", 15.0)
    elif regime == "volatile":
        long_raw -= 10
        short_raw -= 10
        _add_factor(long_factors, "regime_volatile", -10.0)
        _add_factor(short_factors, "regime_volatile", -10.0)
        no_trade_flags.append("volatile_regime")

    if ema_alignment == "bullish":
        long_raw += 12
        _add_factor(long_factors, "ema_alignment_bullish", 12.0)
    elif ema_alignment == "bearish":
        short_raw += 12
        _add_factor(short_factors, "ema_alignment_bearish", 12.0)

    if ema20_slope == "up":
        long_raw += 6
        _add_factor(long_factors, "ema20_slope_up", 6.0)
    elif ema20_slope == "down":
        short_raw += 6
        _add_factor(short_factors, "ema20_slope_down", 6.0)

    if price > ema50_4h:
        long_raw += 6
        _add_factor(long_factors, "price_above_ema50_4h", 6.0)
    elif price < ema50_4h:
        short_raw += 6
        _add_factor(short_factors, "price_below_ema50_4h", 6.0)

    if structure_4h == "hh_hl":
        long_raw += 14
        _add_factor(long_factors, "structure_4h_hh_hl", 14.0)
    elif structure_4h == "lh_ll":
        short_raw += 14
        _add_factor(short_factors, "structure_4h_lh_ll", 14.0)

    if structure_1h == "hh_hl":
        long_raw += 12
        _add_factor(long_factors, "structure_1h_hh_hl", 12.0)
    elif structure_1h == "lh_ll":
        short_raw += 12
        _add_factor(short_factors, "structure_1h_lh_ll", 12.0)

    if near_support:
        long_raw += 7
        _add_factor(long_factors, "near_support", 7.0)
    if near_resistance:
        short_raw += 7
        _add_factor(short_factors, "near_resistance", 7.0)

    if breakout_up:
        long_raw += 10
        _add_factor(long_factors, "breakout_up", 10.0)
    if breakout_down:
        short_raw += 10
        _add_factor(short_factors, "breakout_down", 10.0)

    if "support_to_resistance_flip" in market_map_flags:
        long_raw -= 12
        short_raw += 7
        _add_factor(long_factors, "market_map_support_to_resistance_flip", -12.0)
        _add_factor(short_factors, "market_map_support_to_resistance_flip", 7.0)
    if "resistance_to_support_flip" in market_map_flags:
        short_raw -= 12
        long_raw += 7
        _add_factor(short_factors, "market_map_resistance_to_support_flip", -12.0)
        _add_factor(long_factors, "market_map_resistance_to_support_flip", 7.0)

    if "support_to_resistance_retest_confirmed" in market_map_flags:
        long_raw -= 4
        short_raw += 6
        _add_factor(long_factors, "market_map_support_retest_failed", -4.0)
        _add_factor(short_factors, "market_map_support_retest_failed", 6.0)
    if "resistance_to_support_retest_confirmed" in market_map_flags:
        short_raw -= 4
        long_raw += 6
        _add_factor(short_factors, "market_map_resistance_retest_failed", -4.0)
        _add_factor(long_factors, "market_map_resistance_retest_held", 6.0)

    if "failed_breakout_down_reversal" in market_map_flags:
        long_raw -= 14
        short_raw += 8
        _add_factor(long_factors, "market_map_failed_breakout_down", -14.0)
        _add_factor(short_factors, "market_map_failed_breakout_down", 8.0)
    elif "major_resistance_rejection" in market_map_flags:
        long_raw -= 8
        short_raw += 3
        _add_factor(long_factors, "market_map_major_resistance_rejection", -8.0)
        _add_factor(short_factors, "market_map_major_resistance_rejection", 3.0)

    if "failed_breakout_up_reversal" in market_map_flags:
        short_raw -= 14
        long_raw += 8
        _add_factor(short_factors, "market_map_failed_breakout_up", -14.0)
        _add_factor(long_factors, "market_map_failed_breakout_up", 8.0)
    elif "major_support_rejection" in market_map_flags:
        short_raw -= 8
        long_raw += 3
        _add_factor(short_factors, "market_map_major_support_rejection", -8.0)
        _add_factor(long_factors, "market_map_major_support_rejection", 3.0)

    if "long_into_major_resistance" in market_map_flags:
        long_raw -= 6
        _add_factor(long_factors, "market_map_long_into_major_resistance", -6.0)
    if "short_into_major_support" in market_map_flags:
        short_raw -= 6
        _add_factor(short_factors, "market_map_short_into_major_support", -6.0)

    if "trend_flip_confirmed_down" in market_map_flags:
        long_raw -= 8
        short_raw += 8
        _add_factor(long_factors, "market_map_trend_flip_confirmed_down", -8.0)
        _add_factor(short_factors, "market_map_trend_flip_confirmed_down", 8.0)
    if "trend_flip_confirmed_up" in market_map_flags:
        short_raw -= 3
        long_raw += 2
        _add_factor(short_factors, "market_map_trend_flip_confirmed_up_weak", -3.0)
        _add_factor(long_factors, "market_map_trend_flip_confirmed_up_weak", 2.0)

    if regime == "transition" and transition_direction == "down" and breakout_up:
        long_raw -= 8
        short_raw += 4
        _add_factor(long_factors, "breakout_up_reversal_risk", -8.0)
        _add_factor(short_factors, "failed_breakout_down_hint", 4.0)
    elif regime == "transition" and transition_direction == "up" and breakout_down:
        short_raw -= 8
        long_raw += 4
        _add_factor(short_factors, "breakout_down_reversal_risk", -8.0)
        _add_factor(long_factors, "failed_breakout_up_hint", 4.0)

    if regime == "transition" and transition_direction == "up":
        long_raw += 6
        _add_factor(long_factors, "transition_up_hint", 6.0)
    elif regime == "transition" and transition_direction == "down":
        short_raw += 6
        _add_factor(short_factors, "transition_down_hint", 6.0)

    if signal_15m == "long":
        long_raw += 3
        _add_factor(long_factors, "signal_15m_long_hint", 3.0)
    elif signal_15m == "short":
        short_raw += 3
        _add_factor(short_factors, "signal_15m_short_hint", 3.0)

    if volume_ratio >= cfg.TRIGGER_VOLUME_RATIO:
        long_raw += 4
        short_raw += 4
        _add_factor(long_factors, "volume_expansion", 4.0)
        _add_factor(short_factors, "volume_expansion", 4.0)

    if 35 <= rsi_15m <= 70:
        long_raw += 3
        _add_factor(long_factors, "rsi_long_window", 3.0)
    if 30 <= rsi_15m <= 65:
        short_raw += 3
        _add_factor(short_factors, "rsi_short_window", 3.0)

    risk_long = 0.0
    risk_short = 0.0

    if near_resistance:
        risk_long -= 6
        _add_factor(long_factors, "near_resistance_penalty", -6.0)
    if near_support:
        risk_short -= 6
        _add_factor(short_factors, "near_support_penalty", -6.0)
    if rr_long < cfg.MIN_RR_RATIO:
        risk_long -= 8
        _add_factor(long_factors, "rr_long_penalty", -8.0)
        no_trade_flags.append("RR_insufficient_long")
    if rr_short < cfg.MIN_RR_RATIO:
        risk_short -= 8
        _add_factor(short_factors, "rr_short_penalty", -8.0)
        no_trade_flags.append("RR_insufficient_short")
    if in_range_center:
        risk_long -= 10
        risk_short -= 10
        _add_factor(long_factors, "range_center_penalty", -10.0)
        _add_factor(short_factors, "range_center_penalty", -10.0)
    if atr_ratio > cfg.MAX_ACCEPTABLE_ATR_RATIO or atr_ratio < cfg.MIN_ACCEPTABLE_ATR_RATIO:
        risk_long -= 6
        risk_short -= 6
        _add_factor(long_factors, "atr_extreme_penalty", -6.0)
        _add_factor(short_factors, "atr_extreme_penalty", -6.0)
        no_trade_flags.append("ATR_extreme")
    elif atr_ratio > cfg.MAX_ACCEPTABLE_ATR_RATIO * 0.8 or atr_ratio < cfg.MIN_ACCEPTABLE_ATR_RATIO * 1.2:
        warning_flags.append("ATR_warning")

    if funding_rate >= cfg.FUNDING_LONG_PROHIBITED:
        risk_long -= 12
        _add_factor(long_factors, "funding_long_prohibited", -12.0)
        no_trade_flags.append("Funding_prohibited_long")
    elif funding_rate >= cfg.FUNDING_LONG_WARNING:
        risk_long -= 4
        warning_flags.append("Funding_warning_long")
        _add_factor(long_factors, "funding_long_warning", -4.0)

    if funding_rate <= cfg.FUNDING_SHORT_PROHIBITED:
        risk_short -= 12
        _add_factor(short_factors, "funding_short_prohibited", -12.0)
        no_trade_flags.append("Funding_prohibited_short")
    elif funding_rate <= cfg.FUNDING_SHORT_WARNING:
        risk_short -= 4
        warning_flags.append("Funding_warning_short")
        _add_factor(short_factors, "funding_short_warning", -4.0)

    long_raw += max(-30.0, risk_long)
    short_raw += max(-30.0, risk_short)

    long_display = _normalize_display(long_raw)
    short_display = _normalize_display(short_raw)
    bias, score_gap = decide_bias(
        long_display,
        short_display,
        cfg.LONG_SHORT_DIFF_THRESHOLD,
        cfg.SHORT_LONG_DIFF_THRESHOLD,
    )
    selected_factors = long_factors if bias != "short" else short_factors
    direction_shadow_long = 0.0
    direction_shadow_short = 0.0
    for code, value in long_factors.items():
        if code.startswith(("regime_", "ema_", "price_above", "structure_", "transition_", "market_map_trend_")):
            direction_shadow_long += value
    for code, value in short_factors.items():
        if code.startswith(("regime_", "ema_", "price_below", "structure_", "transition_", "market_map_trend_")):
            direction_shadow_short += value

    activity_shadow_long = 0.0
    activity_shadow_short = 0.0
    for code, value in long_factors.items():
        if code.startswith(("breakout_", "volume_", "signal_15m_", "market_map_failed_breakout")):
            activity_shadow_long += value
    for code, value in short_factors.items():
        if code.startswith(("breakout_", "volume_", "signal_15m_", "market_map_failed_breakout")):
            activity_shadow_short += value

    entry_shadow_long = 0.0
    entry_shadow_short = 0.0
    for code, value in long_factors.items():
        if code.startswith(
            (
                "near_support",
                "near_resistance",
                "rr_",
                "range_center",
                "atr_",
                "funding_",
                "market_map_long_into",
                "market_map_short_into",
                "market_map_support_to_resistance",
                "market_map_resistance_to_support",
                "market_map_support_retest",
                "market_map_resistance_retest",
                "market_map_major_",
            )
        ):
            entry_shadow_long += value
    for code, value in short_factors.items():
        if code.startswith(
            (
                "near_support",
                "near_resistance",
                "rr_",
                "range_center",
                "atr_",
                "funding_",
                "market_map_long_into",
                "market_map_short_into",
                "market_map_support_to_resistance",
                "market_map_resistance_to_support",
                "market_map_support_retest",
                "market_map_resistance_retest",
                "market_map_major_",
            )
        ):
            entry_shadow_short += value

    selected_direction_shadow = direction_shadow_long if bias != "short" else direction_shadow_short
    selected_activity_shadow = activity_shadow_long if bias != "short" else activity_shadow_short
    selected_entry_shadow = entry_shadow_long if bias != "short" else entry_shadow_short

    return {
        "long_raw_score": long_raw,
        "short_raw_score": short_raw,
        "long_display_score": long_display,
        "short_display_score": short_display,
        "score_gap": score_gap,
        "bias": bias,
        "long_factor_breakdown": dict(sorted(long_factors.items(), key=lambda item: item[0])),
        "short_factor_breakdown": dict(sorted(short_factors.items(), key=lambda item: item[0])),
        "top_positive_factors": _top_factors(selected_factors, positive=True),
        "top_negative_factors": _top_factors(selected_factors, positive=False),
        "no_trade_flags": sorted(set(no_trade_flags)),
        "warning_flags": sorted(set(warning_flags)),
        "direction_score_shadow": _bucket_display(selected_direction_shadow),
        "activity_score_shadow": _bucket_display(selected_activity_shadow),
        "entry_quality_score_shadow": _bucket_display(selected_entry_shadow),
    }
