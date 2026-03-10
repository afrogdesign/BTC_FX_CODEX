from __future__ import annotations

from typing import Any


def _round2(value: float) -> float:
    return round(float(value), 2)


def _empty_setup(reason: str = "") -> dict[str, Any]:
    return {
        "status": "invalid",
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
        target_hint = _nearest_target(side, entry_mid, support_zones, resistance_zones)
        tp1 = target_hint if target_hint and target_hint > entry_mid else entry_mid + risk * 1.8
        tp2 = entry_mid + risk * 2.0
        tp1, tp2 = _normalize_take_profits(side, entry_mid, tp1, tp2)
        reward = tp1 - entry_mid
    else:
        stop_loss = entry_high + sl_atr_multiplier * atr
        risk = max(stop_loss - entry_mid, 1e-9)
        target_hint = _nearest_target(side, entry_mid, support_zones, resistance_zones)
        tp1 = target_hint if target_hint and target_hint < entry_mid else entry_mid - risk * 1.8
        tp2 = entry_mid - risk * 2.0
        tp1, tp2 = _normalize_take_profits(side, entry_mid, tp1, tp2)
        reward = entry_mid - tp1

    rr_estimate = reward / risk if risk > 0 else 0.0

    invalid_reasons: list[str] = []
    if rr_estimate < min_rr_ratio:
        invalid_reasons.append("RR不足")
        no_trade_flags.append("RR_insufficient")

    if atr_ratio > atr_ratio_max or atr_ratio < atr_ratio_min:
        invalid_reasons.append("ATR極端値")
        no_trade_flags.append("ATR_extreme")

    if side == "long":
        if funding_rate >= funding_prohibited:
            invalid_reasons.append("Funding禁止域")
            no_trade_flags.append("Funding_prohibited")
        elif funding_rate >= funding_warning:
            no_trade_flags.append("Funding_warning")
    else:
        if funding_rate <= funding_prohibited:
            invalid_reasons.append("Funding禁止域")
            no_trade_flags.append("Funding_prohibited")
        elif funding_rate <= funding_warning:
            no_trade_flags.append("Funding_warning")

    if confidence < confidence_min:
        invalid_reasons.append("confidence不足")

    if warning_count >= 2:
        invalid_reasons.append("warning多発")

    if invalid_reasons:
        status = "invalid"
    else:
        inside_zone = entry_low <= price <= entry_high
        zone_distance = min(abs(price - entry_low), abs(price - entry_high))
        if inside_zone and trigger_ready:
            status = "ready"
        elif zone_distance <= atr * 0.3:
            status = "watch"
        else:
            status = "watch"

    entry_to_stop_pct = abs(entry_mid - stop_loss) / atr if atr > 0 else 0.0
    entry_to_target_pct = abs(tp1 - entry_mid) / atr if atr > 0 else 0.0

    setup = {
        "status": status,
        "entry_zone": {"low": _round2(entry_low), "high": _round2(entry_high)},
        "entry_mid": _round2(entry_mid),
        "stop_loss": _round2(stop_loss),
        "tp1": _round2(tp1),
        "tp2": _round2(tp2),
        "rr_estimate": _round2(rr_estimate),
        "entry_to_stop_pct": _round2(entry_to_stop_pct),
        "entry_to_target_pct": _round2(entry_to_target_pct),
        "invalid_reason": " / ".join(invalid_reasons),
    }
    return setup, sorted(set(no_trade_flags))


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
