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

    above_liq = liquidity_info.get("liquidity_above")
    below_liq = liquidity_info.get("liquidity_below")
    largest_liq_price = liquidation_info.get("largest_liquidation_price")
    bid_wall_price = orderbook_info.get("orderbook_bid_wall_price")
    ask_wall_price = orderbook_info.get("orderbook_ask_wall_price")
    oi_state = oi_cvd_info.get("oi_state")
    divergence = oi_cvd_info.get("cvd_price_divergence")

    if bias == "short":
        risk_score += _score_from_distance(above_liq, 0.8, 1.8)
        if above_liq is not None and above_liq <= 0.8:
            flags.append("upper_liquidity_close")
        bid_wall_atr = _price_distance_atr(price, bid_wall_price, atr)
        risk_score += _score_from_distance(bid_wall_atr, 0.6, 1.2)
        if bid_wall_atr is not None and bid_wall_atr <= 0.6:
            flags.append("bid_wall_close")
        largest_liq_atr = _price_distance_atr(price, largest_liq_price, atr)
        risk_score += _score_from_distance(largest_liq_atr, 0.9, 1.6)
        if largest_liq_atr is not None and largest_liq_atr <= 0.9 and largest_liq_price > price:
            flags.append("liquidation_cluster_above")
    elif bias == "long":
        risk_score += _score_from_distance(below_liq, 0.8, 1.8)
        if below_liq is not None and below_liq <= 0.8:
            flags.append("lower_liquidity_close")
        ask_wall_atr = _price_distance_atr(price, ask_wall_price, atr)
        risk_score += _score_from_distance(ask_wall_atr, 0.6, 1.2)
        if ask_wall_atr is not None and ask_wall_atr <= 0.6:
            flags.append("ask_wall_close")
        largest_liq_atr = _price_distance_atr(price, largest_liq_price, atr)
        risk_score += _score_from_distance(largest_liq_atr, 0.9, 1.6)
        if largest_liq_atr is not None and largest_liq_atr <= 0.9 and largest_liq_price < price:
            flags.append("liquidation_cluster_below")

    if liquidity_info.get("liquidity_swept_recently"):
        risk_score -= 8.0
    else:
        flags.append("sweep_incomplete")
        risk_score += 8.0

    if oi_state in {"short_cover_risk", "long_flush_exhaustion"}:
        flags.append(oi_state)
        risk_score += 12.0
    if divergence in {"bearish", "bullish"}:
        flags.append(f"cvd_{divergence}_divergence")
        risk_score += 12.0

    orderbook_bias = orderbook_info.get("orderbook_bias")
    if bias == "long" and orderbook_bias == "ask_heavy":
        flags.append("orderbook_ask_heavy")
        risk_score += 10.0
    elif bias == "short" and orderbook_bias == "bid_heavy":
        flags.append("orderbook_bid_heavy")
        risk_score += 10.0

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
