from __future__ import annotations


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


_LONG_REVERSAL_RISK_REQUIRED_FLAGS = {"sweep_incomplete"}
_LONG_REVERSAL_RISK_TRIGGER_FLAGS = {
    "orderbook_ask_heavy",
    "ask_wall_close",
    "lower_liquidity_close",
    "long_flush_exhaustion",
}
_MARKET_MAP_RISK_FLAGS = {
    "long_into_major_resistance",
    "short_into_major_support",
    "major_resistance_rejection",
    "major_support_rejection",
    "failed_breakout_down_reversal",
    "failed_breakout_up_reversal",
    "support_to_resistance_flip",
    "resistance_to_support_flip",
    "support_to_resistance_retest_confirmed",
    "resistance_to_support_retest_confirmed",
    "trend_flip_confirmed_down",
    "trend_flip_confirmed_up",
    "trend_flip_early_down",
    "trend_flip_early_up",
}
_MARKET_MAP_LONG_REVERSAL_FLAGS = {
    "failed_breakout_down_reversal",
    "support_to_resistance_flip",
    "support_to_resistance_retest_confirmed",
    "trend_flip_confirmed_down",
    "trend_flip_early_down",
}


def derive_additional_risk_flags(
    *,
    bias: str,
    market_regime: str,
    transition_direction: str,
    primary_setup_status: str,
    primary_setup_reason: str,
    risk_flags: list[str],
    long_factor_breakdown: dict[str, float] | None = None,
    market_map_flags: list[str] | None = None,
) -> list[str]:
    derived_flags = list(risk_flags)
    normalized_flags = {str(flag or "").strip() for flag in risk_flags if str(flag or "").strip()}
    normalized_market_map_flags = {
        str(flag or "").strip()
        for flag in (market_map_flags or [])
        if str(flag or "").strip()
    }
    for flag in normalized_market_map_flags:
        if flag in _MARKET_MAP_RISK_FLAGS:
            derived_flags.append(flag)
    normalized_flags.update(normalized_market_map_flags)
    normalized_breakdown = long_factor_breakdown or {}
    market_map_long_reversal = bool(_MARKET_MAP_LONG_REVERSAL_FLAGS & normalized_flags)

    long_reversal_risk = (
        str(bias or "").strip() == "long"
        and str(primary_setup_status or "").strip() == "watch"
        and str(primary_setup_reason or "").strip() in {"entry_zone_not_reached", "confidence_below_min"}
        and (
            (
                str(market_regime or "").strip() == "transition"
                and str(transition_direction or "").strip() == "down"
                and _LONG_REVERSAL_RISK_REQUIRED_FLAGS.issubset(normalized_flags)
                and (
                    bool(_LONG_REVERSAL_RISK_TRIGGER_FLAGS & normalized_flags)
                    or "near_resistance_penalty" in normalized_breakdown
                )
            )
            or market_map_long_reversal
        )
    )
    if long_reversal_risk:
        derived_flags.append("long_reversal_risk")

    return _dedupe(derived_flags)


def assemble_result_flags(
    *,
    bias: str,
    score_no_trade_flags: list[str],
    score_warning_flags: list[str],
    long_setup_flags: list[str],
    short_setup_flags: list[str],
    position_risk_flags: list[str],
    critical_zone: bool,
) -> dict[str, list[str]]:
    primary_setup_flags: list[str] = []
    if bias == "long":
        primary_setup_flags = long_setup_flags
    elif bias == "short":
        primary_setup_flags = short_setup_flags

    warning_flags = list(score_warning_flags)
    if critical_zone:
        warning_flags.append("Critical_zone_warning")

    return {
        "no_trade_flags": _dedupe(list(score_no_trade_flags) + list(primary_setup_flags)),
        "warning_flags": _dedupe(warning_flags),
        "risk_flags": _dedupe(list(position_risk_flags)),
    }
