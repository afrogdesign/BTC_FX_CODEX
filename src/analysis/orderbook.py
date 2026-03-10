from __future__ import annotations

from typing import Any


def _largest_wall(levels: list[list[str]] | None, side: str, price: float) -> tuple[float | None, float | None]:
    if not levels:
        return None, None
    filtered: list[tuple[float, float]] = []
    for row in levels:
        if not isinstance(row, list) or len(row) < 2:
            continue
        level_price = float(row[0])
        level_size = float(row[1])
        if side == "bid" and level_price < price:
            filtered.append((level_price, level_size))
        elif side == "ask" and level_price > price:
            filtered.append((level_price, level_size))
    if not filtered:
        return None, None
    best_price, best_size = max(filtered, key=lambda item: item[1])
    return round(best_price, 2), round(best_size, 4)


def analyze_orderbook(
    *,
    bids: list[list[str]] | None,
    asks: list[list[str]] | None,
    price: float,
) -> dict[str, Any]:
    bid_wall_price, bid_wall_size = _largest_wall(bids, "bid", price)
    ask_wall_price, ask_wall_size = _largest_wall(asks, "ask", price)

    total_bid = sum(float(item[1]) for item in (bids or [])[:20] if len(item) >= 2)
    total_ask = sum(float(item[1]) for item in (asks or [])[:20] if len(item) >= 2)
    bias = "neutral"
    if total_bid > total_ask * 1.15:
        bias = "bid_heavy"
    elif total_ask > total_bid * 1.15:
        bias = "ask_heavy"

    return {
        "orderbook_bid_wall_price": bid_wall_price,
        "orderbook_ask_wall_price": ask_wall_price,
        "orderbook_bid_wall_size": bid_wall_size,
        "orderbook_ask_wall_size": ask_wall_size,
        "orderbook_bias": bias,
        "orderbook_bid_ask_ratio": round(total_bid / total_ask, 4) if total_ask > 0 else None,
    }
