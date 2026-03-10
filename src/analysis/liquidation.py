from __future__ import annotations

from typing import Any


def analyze_liquidation_clusters(
    *,
    price: float,
    atr: float,
    liquidation_events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    if not liquidation_events:
        return {
            "liquidation_above": None,
            "liquidation_below": None,
            "largest_liquidation_price": None,
            "distance_to_largest_liquidation": None,
            "liquidation_density_above": None,
            "liquidation_density_below": None,
        }

    bucket_size = max(atr * 0.35, price * 0.0008, 5.0)
    buckets: dict[float, float] = {}
    above_total = 0.0
    below_total = 0.0
    for event in liquidation_events:
        event_price = float(event.get("price", 0.0) or 0.0)
        event_qty = float(event.get("qty", 0.0) or 0.0)
        if event_price <= 0 or event_qty <= 0:
            continue
        bucket = round(round(event_price / bucket_size) * bucket_size, 2)
        buckets[bucket] = buckets.get(bucket, 0.0) + event_qty
        if event_price > price:
            above_total += event_qty
        elif event_price < price:
            below_total += event_qty

    if not buckets:
        return {
            "liquidation_above": None,
            "liquidation_below": None,
            "largest_liquidation_price": None,
            "distance_to_largest_liquidation": None,
            "liquidation_density_above": None,
            "liquidation_density_below": None,
        }

    largest_price, largest_qty = max(buckets.items(), key=lambda item: item[1])
    density_above = above_total / max(len([p for p in buckets if p > price]), 1)
    density_below = below_total / max(len([p for p in buckets if p < price]), 1)
    return {
        "liquidation_above": round(above_total, 4),
        "liquidation_below": round(below_total, 4),
        "largest_liquidation_price": round(largest_price, 2),
        "distance_to_largest_liquidation": round(abs(largest_price - price), 2),
        "liquidation_density_above": round(density_above, 4),
        "liquidation_density_below": round(density_below, 4),
        "largest_liquidation_qty": round(largest_qty, 4),
    }
