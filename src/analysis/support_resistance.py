from __future__ import annotations

from collections import defaultdict
from typing import Any

import pandas as pd


SOURCE_WEIGHT = {"4h": 3, "1h": 2, "15m": 1}


def count_zone_reactions(df: pd.DataFrame, low: float, high: float) -> int:
    reactions = 0
    last_hit_index = -999
    for idx, row in enumerate(df.itertuples(index=False)):
        candle_low = float(getattr(row, "low"))
        candle_high = float(getattr(row, "high"))
        if candle_high >= low and candle_low <= high:
            if idx - last_hit_index > 3:
                reactions += 1
            last_hit_index = idx
    return reactions


def _build_zone(price: float, atr: float, source: str, is_support: bool) -> dict[str, Any]:
    half = max(atr * 0.2, price * 0.0005)
    low, high = (price - half, price + half)
    return {
        "low": float(low),
        "high": float(high),
        "strength": SOURCE_WEIGHT.get(source, 1),
        "source": source,
        "kind": "support" if is_support else "resistance",
    }


def extract_zones_from_swings(
    df: pd.DataFrame,
    swings: dict[str, list[dict[str, Any]]],
    atr_value: float,
    source: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    support = []
    resistance = []
    for low in swings.get("lows", [])[-10:]:
        zone = _build_zone(float(low["price"]), atr_value, source, True)
        zone["strength"] += count_zone_reactions(df, zone["low"], zone["high"])
        support.append(zone)
    for high in swings.get("highs", [])[-10:]:
        zone = _build_zone(float(high["price"]), atr_value, source, False)
        zone["strength"] += count_zone_reactions(df, zone["low"], zone["high"])
        resistance.append(zone)
    return support, resistance


def merge_nearby_zones(zones: list[dict[str, Any]], atr_value: float) -> list[dict[str, Any]]:
    if not zones:
        return []
    threshold = max(atr_value * 0.5, 1.0)
    ordered = sorted(zones, key=lambda z: (z["low"] + z["high"]) / 2)
    merged: list[dict[str, Any]] = []
    for zone in ordered:
        mid = (zone["low"] + zone["high"]) / 2
        if not merged:
            merged.append(dict(zone))
            continue
        last = merged[-1]
        last_mid = (last["low"] + last["high"]) / 2
        if abs(mid - last_mid) <= threshold:
            total_strength = last["strength"] + zone["strength"]
            last["low"] = min(last["low"], zone["low"])
            last["high"] = max(last["high"], zone["high"])
            last["strength"] = total_strength
            if SOURCE_WEIGHT.get(zone["source"], 1) > SOURCE_WEIGHT.get(last["source"], 1):
                last["source"] = zone["source"]
        else:
            merged.append(dict(zone))
    return merged


def build_support_resistance(
    per_tf_inputs: dict[str, dict[str, Any]],
    atr_value: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_support, all_resistance = build_all_support_resistance(per_tf_inputs, atr_value)
    top_support = sorted(all_support, key=lambda z: z["strength"], reverse=True)[:3]
    top_resistance = sorted(all_resistance, key=lambda z: z["strength"], reverse=True)[:3]
    return top_support, top_resistance


def build_all_support_resistance(
    per_tf_inputs: dict[str, dict[str, Any]],
    atr_value: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    support_all: list[dict[str, Any]] = []
    resistance_all: list[dict[str, Any]] = []
    for tf, payload in per_tf_inputs.items():
        support, resistance = extract_zones_from_swings(
            payload["df"], payload["swings"], atr_value, tf
        )
        support_all.extend(support)
        resistance_all.extend(resistance)

    merged_support = merge_nearby_zones(support_all, atr_value)
    merged_resistance = merge_nearby_zones(resistance_all, atr_value)

    for zones in (merged_support, merged_resistance):
        for z in zones:
            z["low"] = round(float(z["low"]), 2)
            z["high"] = round(float(z["high"]), 2)
            z["strength"] = int(round(float(z["strength"])))
            z.pop("kind", None)

    return merged_support, merged_resistance


def nearest_zone_distance(price: float, zones: list[dict[str, Any]]) -> float:
    if not zones:
        return float("inf")
    distances = []
    for zone in zones:
        distances.append(zone_distance(price, zone))
    return min(distances)


def zone_distance(price: float, zone: dict[str, Any]) -> float:
    low, high = float(zone["low"]), float(zone["high"])
    if low <= price <= high:
        return 0.0
    if price < low:
        return low - price
    return price - high


def sort_zones_by_distance(price: float, zones: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(zones, key=lambda zone: (zone_distance(price, zone), -float(zone.get("strength", 0))))
    enriched: list[dict[str, Any]] = []
    for zone in ordered:
        copied = dict(zone)
        copied["distance_from_price"] = round(zone_distance(price, zone), 2)
        enriched.append(copied)
    return enriched


def select_nearest_directional_zones(
    price: float,
    zones: list[dict[str, Any]],
    zone_type: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    if zone_type == "support":
        directional = [zone for zone in zones if float(zone["low"]) <= price]
    elif zone_type == "resistance":
        directional = [zone for zone in zones if float(zone["high"]) >= price]
    else:
        directional = list(zones)

    ordered = sort_zones_by_distance(price, directional or zones)
    return ordered[:limit]


def zone_gap_to_opposite(price: float, side: str, support_zones: list[dict[str, Any]], resistance_zones: list[dict[str, Any]]) -> float:
    if side == "long":
        above = [z["low"] - price for z in resistance_zones if z["low"] > price]
        return min(above) if above else float("inf")
    below = [price - z["high"] for z in support_zones if z["high"] < price]
    return min(below) if below else float("inf")


def detect_critical_zone(price: float, support_zones: list[dict[str, Any]], resistance_zones: list[dict[str, Any]]) -> bool:
    for zone in support_zones + resistance_zones:
        if float(zone["low"]) <= price <= float(zone["high"]):
            return True
    return False
