from __future__ import annotations

from typing import Any


def _select_horizon_levels(price: float, zones: list[dict[str, Any]], sources: set[str], limit: int = 5) -> list[dict[str, Any]]:
    selected = [zone for zone in zones if str(zone.get("source", "")) in sources]
    ordered = sorted(selected, key=lambda zone: (float(zone.get("distance_from_price", 0.0)), -float(zone.get("strength", 0.0))))
    levels: list[dict[str, Any]] = []
    for zone in ordered[:limit]:
        levels.append(
            {
                "low": zone.get("low"),
                "high": zone.get("high"),
                "strength": zone.get("strength"),
                "timeframe": zone.get("source"),
                "distance_from_price": zone.get("distance_from_price"),
            }
        )
    return levels


def _nearest_major(levels: list[dict[str, Any]], side: str) -> dict[str, Any]:
    if not levels:
        return {}
    directional = []
    for level in levels:
        low = float(level.get("low", 0.0) or 0.0)
        high = float(level.get("high", 0.0) or 0.0)
        if side == "support" and low <= high:
            directional.append(level)
        if side == "resistance" and low <= high:
            directional.append(level)
    return directional[0] if directional else levels[0]


def build_sr_context(
    price: float,
    support_zones_all: list[dict[str, Any]],
    resistance_zones_all: list[dict[str, Any]],
) -> dict[str, Any]:
    short_support = _select_horizon_levels(price, support_zones_all, {"15m"})
    short_resistance = _select_horizon_levels(price, resistance_zones_all, {"15m"})
    mid_support = _select_horizon_levels(price, support_zones_all, {"1h"})
    mid_resistance = _select_horizon_levels(price, resistance_zones_all, {"1h"})
    long_support = _select_horizon_levels(price, support_zones_all, {"4h"})
    long_resistance = _select_horizon_levels(price, resistance_zones_all, {"4h"})

    nearest_major_support = _nearest_major(long_support or mid_support or short_support, "support")
    nearest_major_resistance = _nearest_major(long_resistance or mid_resistance or short_resistance, "resistance")
    strength_total = sum(float(item.get("strength", 0.0) or 0.0) for item in (long_support + long_resistance)[:4])

    return {
        "short_horizon_levels": short_support + short_resistance,
        "mid_horizon_levels": mid_support + mid_resistance,
        "long_horizon_levels": long_support + long_resistance,
        "nearest_major_support": nearest_major_support,
        "nearest_major_resistance": nearest_major_resistance,
        "major_level_strength": round(strength_total, 2),
    }
