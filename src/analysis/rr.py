from __future__ import annotations

from typing import Any


def _round2(value: float) -> float:
    return round(float(value), 2)


_TP1_MIN_RR = 1.3
_TP2_MIN_RR = 2.4


def _empty_setup(reason: str = "") -> dict[str, Any]:
    return {
        "status": "invalid",
        "status_reason_code": "invalid_empty_setup",
        "entry_zone": {"low": 0.0, "high": 0.0},
        "entry_mid": 0.0,
        "stop_loss": 0.0,
        "tp1": 0.0,
        "tp2": 0.0,
        "rr_estimate": 0.0,
        "entry_to_stop_pct": 0.0,
        "entry_to_target_pct": 0.0,
        "invalid_reason": reason,
    }


def _normalize_take_profits(side: str, entry_mid: float, tp1: float, tp2: float) -> tuple[float, float]:
    if side == "long":
        candidates = [tp for tp in (tp1, tp2) if tp > entry_mid]
        if len(candidates) < 2:
            candidates = sorted([max(tp1, entry_mid), max(tp2, entry_mid)])
        else:
            candidates = sorted(candidates)
        return candidates[0], candidates[1]

    candidates = [tp for tp in (tp1, tp2) if tp < entry_mid]
    if len(candidates) < 2:
        candidates = sorted([min(tp1, entry_mid), min(tp2, entry_mid)], reverse=True)
    else:
        candidates = sorted(candidates, reverse=True)
    return candidates[0], candidates[1]


def _select_zone(side: str, price: float, support_zones: list[dict[str, Any]], resistance_zones: list[dict[str, Any]]) -> dict[str, Any] | None:
    if side == "long":
        candidates = [z for z in support_zones if float(z["high"]) <= price or float(z["low"]) <= price <= float(z["high"])]
        if not candidates:
            return None
        return max(candidates, key=lambda z: float(z["high"]))
    candidates = [z for z in resistance_zones if float(z["low"]) >= price or float(z["low"]) <= price <= float(z["high"])]
    if not candidates:
        return None
    return min(candidates, key=lambda z: float(z["low"]))


def _nearest_target(side: str, entry_mid: float, support_zones: list[dict[str, Any]], resistance_zones: list[dict[str, Any]]) -> float | None:
    if side == "long":
        above = [float(z["low"]) for z in resistance_zones if float(z["low"]) > entry_mid]
        return min(above) if above else None
    below = [float(z["high"]) for z in support_zones if float(z["high"]) < entry_mid]
    return max(below) if below else None


def _target_candidates(
    side: str,
    entry_mid: float,
    support_zones: list[dict[str, Any]],
    resistance_zones: list[dict[str, Any]],
) -> list[float]:
    if side == "long":
        return sorted(float(z["low"]) for z in resistance_zones if float(z["low"]) > entry_mid)
    return sorted((float(z["high"]) for z in support_zones if float(z["high"]) < entry_mid), reverse=True)


def build_setup(
    *,
    side: str,
    price: float,
    atr: float,
    support_zones: list[dict[str, Any]],
    resistance_zones: list[dict[str, Any]],
    sl_atr_multiplier: float,
    min_rr_ratio: float,
    confidence: int,
    confidence_min: int,
    atr_ratio: float,
    atr_ratio_min: float,
    atr_ratio_max: float,
    funding_rate: float,
    funding_warning: float,
    funding_prohibited: float,
    trigger_ready: bool,
    warning_count: int,
) -> tuple[dict[str, Any], list[str]]:
    if atr <= 0:
        return _empty_setup("ATR異常"), ["ATR_extreme"]

    no_trade_flags: list[str] = []
    zone = _select_zone(side, price, support_zones, resistance_zones)

    if zone is None:
        half = atr * 0.15
        entry_low = price - half
        entry_high = price + half
    else:
        entry_low = float(zone["low"])
        entry_high = float(zone["high"])

    entry_mid = (entry_low + entry_high) / 2
    if side == "long":
        stop_loss = entry_low - sl_atr_multiplier * atr
        risk = max(entry_mid - stop_loss, 1e-9)
        targets = _target_candidates(side, entry_mid, support_zones, resistance_zones)
        tp1_floor = entry_mid + risk * _TP1_MIN_RR
        tp2_floor = entry_mid + risk * _TP2_MIN_RR
        tp1_hint = targets[0] if targets else None
        tp2_hint = next((target for target in targets[1:] if target > tp1_floor), None)
        tp1 = max(tp1_hint, tp1_floor) if tp1_hint is not None else tp1_floor
        tp2 = max(tp2_hint, tp2_floor) if tp2_hint is not None else tp2_floor
        tp1, tp2 = _normalize_take_profits(side, entry_mid, tp1, tp2)
        reward = tp1 - entry_mid
    else:
        stop_loss = entry_high + sl_atr_multiplier * atr
        risk = max(stop_loss - entry_mid, 1e-9)
        targets = _target_candidates(side, entry_mid, support_zones, resistance_zones)
        tp1_floor = entry_mid - risk * _TP1_MIN_RR
        tp2_floor = entry_mid - risk * _TP2_MIN_RR
        tp1_hint = targets[0] if targets else None
        tp2_hint = next((target for target in targets[1:] if target < tp1_floor), None)
        tp1 = min(tp1_hint, tp1_floor) if tp1_hint is not None else tp1_floor
        tp2 = min(tp2_hint, tp2_floor) if tp2_hint is not None else tp2_floor
        tp1, tp2 = _normalize_take_profits(side, entry_mid, tp1, tp2)
        reward = entry_mid - tp1

    rr_estimate = reward / risk if risk > 0 else 0.0

    invalid_reasons: list[str] = []
    invalid_reason_codes: list[str] = []
    if rr_estimate < min_rr_ratio:
        invalid_reasons.append("RR不足")
        invalid_reason_codes.append("rr_below_min")
        no_trade_flags.append("RR_insufficient")

    if atr_ratio > atr_ratio_max or atr_ratio < atr_ratio_min:
        invalid_reasons.append("ATR極端値")
        invalid_reason_codes.append("atr_out_of_range")
        no_trade_flags.append("ATR_extreme")

    if side == "long":
        if funding_rate >= funding_prohibited:
            invalid_reasons.append("Funding禁止域")
            invalid_reason_codes.append("funding_long_prohibited")
            no_trade_flags.append("Funding_prohibited")
        elif funding_rate >= funding_warning:
            no_trade_flags.append("Funding_warning")
    else:
        if funding_rate <= funding_prohibited:
            invalid_reasons.append("Funding禁止域")
            invalid_reason_codes.append("funding_short_prohibited")
            no_trade_flags.append("Funding_prohibited")
        elif funding_rate <= funding_warning:
            no_trade_flags.append("Funding_warning")

    if confidence < confidence_min:
        invalid_reasons.append("confidence不足")
        invalid_reason_codes.append("confidence_below_min")

    if warning_count >= 3:
        invalid_reasons.append("warning多発")
        invalid_reason_codes.append("warning_cluster")

    if invalid_reasons:
        status = "invalid"
        status_reason_code = invalid_reason_codes[0] if invalid_reason_codes else "invalid_filters"
    else:
        inside_zone = entry_low <= price <= entry_high
        zone_distance = min(abs(price - entry_low), abs(price - entry_high))
        if inside_zone and trigger_ready:
            status = "ready"
            status_reason_code = "inside_entry_zone_with_trigger"
        elif zone_distance <= atr * 0.08 and trigger_ready:
            status = "ready"
            status_reason_code = "near_entry_zone_with_trigger"
        elif zone_distance <= atr * 0.3:
            status = "watch"
            status_reason_code = "near_entry_zone_waiting_trigger"
        else:
            status = "watch"
            status_reason_code = "entry_zone_not_reached"

    entry_to_stop_pct = abs(entry_mid - stop_loss) / atr if atr > 0 else 0.0
    entry_to_target_pct = abs(tp1 - entry_mid) / atr if atr > 0 else 0.0

    setup = {
        "status": status,
        "status_reason_code": status_reason_code,
        "entry_zone": {"low": _round2(entry_low), "high": _round2(entry_high)},
        "entry_mid": _round2(entry_mid),
        "stop_loss": _round2(stop_loss),
        "tp1": _round2(tp1),
        "tp2": _round2(tp2),
        "rr_estimate": _round2(rr_estimate),
        "entry_to_stop_pct": _round2(entry_to_stop_pct),
        "entry_to_target_pct": _round2(entry_to_target_pct),
        "invalid_reason": " / ".join(invalid_reasons),
        "invalid_reason_codes": invalid_reason_codes,
        "blocking_flags": sorted(set(no_trade_flags)),
    }
    return setup, sorted(set(no_trade_flags))


def _market_map_distance_atr(market_map: dict[str, Any], key: str) -> float | None:
    level = market_map.get(key)
    if not isinstance(level, dict):
        return None
    value = level.get("distance_atr")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def refine_execution_precision(
    setup: dict[str, Any],
    *,
    side: str,
    market_map: dict[str, Any] | None,
    signal_15m: str,
    breakout_up: bool,
    breakout_down: bool,
) -> tuple[dict[str, Any], list[str]]:
    refined = dict(setup)
    flags = {str(flag) for flag in refined.get("execution_precision_flags", []) if str(flag)}
    market_map = market_map or {}
    market_flags = {str(flag) for flag in market_map.get("flags", []) if str(flag)}
    action = str(refined.get("execution_precision_action") or "keep")
    reason = str(refined.get("execution_precision_reason") or "")

    support_distance_atr = _market_map_distance_atr(market_map, "nearest_major_support")
    resistance_distance_atr = _market_map_distance_atr(market_map, "nearest_major_resistance")

    if side == "short":
        if "short_into_major_support" in market_flags or (
            support_distance_atr is not None and support_distance_atr <= 0.30
        ):
            flags.add("short_at_major_support_wait_only")
            action = "wait_only"
            reason = "主要サポートが近く、15分足ショートは追いかけず待機"
        if {"resistance_to_support_flip", "trend_flip_confirmed_up"} & market_flags and signal_15m != "short":
            flags.add("short_invalidated_by_up_break")
            action = "wait_only"
            reason = "上抜け後の支持化が残り、15分足ショート発火は無効寄り"
        if breakout_down and {"support_to_resistance_flip", "trend_flip_confirmed_down"} & market_flags:
            flags.add("breakout_follow_candidate")
    elif side == "long":
        if "long_into_major_resistance" in market_flags or (
            resistance_distance_atr is not None and resistance_distance_atr <= 0.30
        ):
            flags.add("long_at_major_resistance_wait_only")
            action = "wait_only"
            reason = "主要レジスタンスが近く、15分足ロングは追いかけず待機"
        if {"support_to_resistance_flip", "trend_flip_confirmed_down"} & market_flags and signal_15m != "long":
            flags.add("long_invalidated_by_down_break")
            action = "wait_only"
            reason = "下抜け後の抵抗化が残り、15分足ロング発火は無効寄り"
        if breakout_up and {"resistance_to_support_flip", "trend_flip_confirmed_up"} & market_flags:
            flags.add("breakout_follow_candidate")

    if action == "wait_only" and refined.get("status") == "ready":
        refined["status"] = "watch"
        refined["status_reason_code"] = "execution_precision_wait_only"
        existing = [str(flag) for flag in refined.get("blocking_flags", []) if str(flag)]
        refined["blocking_flags"] = sorted(set(existing + ["execution_precision_wait_only"]))

    refined["execution_precision_action"] = action
    refined["execution_precision_flags"] = sorted(flags)
    refined["execution_precision_reason"] = reason
    return refined, sorted(flags)


def choose_primary_setup(bias: str, long_setup: dict[str, Any], short_setup: dict[str, Any]) -> tuple[str, str]:
    if bias == "long":
        return "long", long_setup["status"]
    if bias == "short":
        return "short", short_setup["status"]

    long_status = long_setup["status"]
    short_status = short_setup["status"]

    if long_status == "ready":
        return "long", "ready"
    if short_status == "ready":
        return "short", "ready"
    if long_status == "watch" and short_status != "watch":
        return "long", "watch"
    if short_status == "watch" and long_status != "watch":
        return "short", "watch"
    return "none", "none"
