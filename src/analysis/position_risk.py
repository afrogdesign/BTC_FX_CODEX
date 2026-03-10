from __future__ import annotations

from typing import Any


def _score_from_distance(distance_atr: float | None, close_threshold: float, warning_threshold: float) -> float:
    if distance_atr is None:
        return 0.0
    if distance_atr <= close_threshold:
        return 30.0
    if distance_atr <= warning_threshold:
        return 15.0
    return 0.0


def _price_distance_atr(price: float, level: float | None, atr: float) -> float | None:
    if level is None or atr <= 0:
        return None
    return abs(level - price) / atr


def _push_risk(
    breakdown: dict[str, float],
    flags: list[str],
    code: str,
    delta: float,
    *,
    flag: str | None = None,
) -> float:
    breakdown[code] = round(breakdown.get(code, 0.0) + delta, 4)
    if flag:
        flags.append(flag)
    return delta


def _primary_reason_from_breakdown(breakdown: dict[str, float]) -> str:
    ranked = [(code, score) for code, score in breakdown.items() if score > 0]
    if not ranked:
        return "balanced_location"
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[0][0]


def evaluate_position_risk(
    *,
    bias: str,
    price: float,
    atr: float,
    liquidity_info: dict[str, Any],
    liquidation_info: dict[str, Any],
    oi_cvd_info: dict[str, Any],
    orderbook_info: dict[str, Any],
    high_threshold: float,
    medium_threshold: float,
) -> dict[str, Any]:
    risk_score = 0.0
    flags: list[str] = []
    breakdown: dict[str, float] = {}

    above_liq = liquidity_info.get("liquidity_above")
    below_liq = liquidity_info.get("liquidity_below")
    largest_liq_price = liquidation_info.get("largest_liquidation_price")
    bid_wall_price = orderbook_info.get("orderbook_bid_wall_price")
    ask_wall_price = orderbook_info.get("orderbook_ask_wall_price")
    oi_state = oi_cvd_info.get("oi_state")
    divergence = oi_cvd_info.get("cvd_price_divergence")

    if bias == "short":
        delta = _score_from_distance(above_liq, 0.8, 1.8)
        risk_score += delta
        if delta:
            breakdown["upper_liquidity_distance"] = round(delta, 4)
        if above_liq is not None and above_liq <= 0.8:
            flags.append("upper_liquidity_close")
        bid_wall_atr = _price_distance_atr(price, bid_wall_price, atr)
        delta = _score_from_distance(bid_wall_atr, 0.6, 1.2)
        risk_score += delta
        if delta:
            breakdown["bid_wall_distance"] = round(delta, 4)
        if bid_wall_atr is not None and bid_wall_atr <= 0.6:
            flags.append("bid_wall_close")
        largest_liq_atr = _price_distance_atr(price, largest_liq_price, atr)
        delta = _score_from_distance(largest_liq_atr, 0.9, 1.6)
        risk_score += delta
        if delta:
            breakdown["liquidation_cluster_distance"] = round(delta, 4)
        if largest_liq_atr is not None and largest_liq_atr <= 0.9 and largest_liq_price > price:
            flags.append("liquidation_cluster_above")
    elif bias == "long":
        delta = _score_from_distance(below_liq, 0.8, 1.8)
        risk_score += delta
        if delta:
            breakdown["lower_liquidity_distance"] = round(delta, 4)
        if below_liq is not None and below_liq <= 0.8:
            flags.append("lower_liquidity_close")
        ask_wall_atr = _price_distance_atr(price, ask_wall_price, atr)
        delta = _score_from_distance(ask_wall_atr, 0.6, 1.2)
        risk_score += delta
        if delta:
            breakdown["ask_wall_distance"] = round(delta, 4)
        if ask_wall_atr is not None and ask_wall_atr <= 0.6:
            flags.append("ask_wall_close")
        largest_liq_atr = _price_distance_atr(price, largest_liq_price, atr)
        delta = _score_from_distance(largest_liq_atr, 0.9, 1.6)
        risk_score += delta
        if delta:
            breakdown["liquidation_cluster_distance"] = round(delta, 4)
        if largest_liq_atr is not None and largest_liq_atr <= 0.9 and largest_liq_price < price:
            flags.append("liquidation_cluster_below")

    if liquidity_info.get("liquidity_swept_recently"):
        breakdown["sweep_recent_bonus"] = -8.0
        risk_score -= 8.0
    else:
        risk_score += _push_risk(breakdown, flags, "sweep_incomplete", 8.0, flag="sweep_incomplete")

    if oi_state in {"short_cover_risk", "long_flush_exhaustion"}:
        risk_score += _push_risk(breakdown, flags, oi_state, 12.0, flag=oi_state)
    if divergence in {"bearish", "bullish"}:
        code = f"cvd_{divergence}_divergence"
        risk_score += _push_risk(breakdown, flags, code, 12.0, flag=code)

    orderbook_bias = orderbook_info.get("orderbook_bias")
    if bias == "long" and orderbook_bias == "ask_heavy":
        risk_score += _push_risk(breakdown, flags, "orderbook_ask_heavy", 10.0, flag="orderbook_ask_heavy")
    elif bias == "short" and orderbook_bias == "bid_heavy":
        risk_score += _push_risk(breakdown, flags, "orderbook_bid_heavy", 10.0, flag="orderbook_bid_heavy")

    risk_score = max(0.0, min(risk_score, 100.0))
    if bias not in {"long", "short"}:
        prelabel = "RISKY_ENTRY"
    elif risk_score >= high_threshold:
        prelabel = "NO_TRADE_CANDIDATE"
    elif risk_score >= medium_threshold:
        prelabel = "SWEEP_WAIT"
    elif risk_score >= medium_threshold * 0.55:
        prelabel = "RISKY_ENTRY"
    else:
        prelabel = "ENTRY_OK"

    return {
        "prelabel": prelabel,
        "location_risk": round(risk_score, 2),
        "risk_flags": sorted(set(flags)),
        "primary_reason": _primary_reason_from_breakdown(breakdown),
        "risk_breakdown": dict(sorted(breakdown.items(), key=lambda item: item[0])),
    }


def apply_prelabel_to_setup(setup: dict[str, Any], prelabel: str, side: str, bias: str) -> dict[str, Any]:
    updated = dict(setup)
    if bias not in {"long", "short"} or side != bias:
        return updated
    reason = str(updated.get("invalid_reason", "")).strip()
    if prelabel == "ENTRY_OK":
        return updated
    if prelabel == "RISKY_ENTRY" and updated.get("status") == "ready":
        updated["status"] = "watch"
        updated["invalid_reason"] = "位置リスク注意" if not reason else f"{reason} / 位置リスク注意"
        return updated
    if prelabel == "SWEEP_WAIT":
        updated["status"] = "watch"
        updated["invalid_reason"] = "Sweep待ち" if not reason else f"{reason} / Sweep待ち"
        return updated
    if prelabel == "NO_TRADE_CANDIDATE":
        updated["status"] = "invalid"
        updated["invalid_reason"] = "位置が悪い" if not reason else f"{reason} / 位置が悪い"
    return updated
