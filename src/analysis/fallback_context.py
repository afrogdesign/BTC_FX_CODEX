from __future__ import annotations

from typing import Any


def build_fallback_context(missing_fields: list[str]) -> dict[str, Any]:
    normalized = sorted({str(field).strip() for field in missing_fields if str(field).strip()})
    substituted_by: list[str] = []

    if any(field.startswith("orderbook") for field in normalized):
        substituted_by.extend(["wick_rejection", "nearby_zone_density"])
    if "liquidation_events" in normalized:
        substituted_by.extend(["swing_cluster", "recent_extrema_density"])
    if any(field.startswith("oi_") or field == "oi_value" for field in normalized):
        substituted_by.extend(["price_change", "volume"])
    if "cvd_series" in normalized:
        substituted_by.extend(["oi", "volume"])

    if not normalized:
        mode = "normal"
    elif len(normalized) <= 2:
        mode = "price_only_partial"
    else:
        mode = "structure_only"

    penalty = 0.0 if mode == "normal" else 4.0 if mode == "price_only_partial" else 8.0
    return {
        "mode": mode,
        "missing_fields": normalized,
        "substituted_by": sorted(set(substituted_by)),
        "confidence_penalty_shadow": penalty,
    }
