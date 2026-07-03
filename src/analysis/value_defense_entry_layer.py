from __future__ import annotations

from typing import Any


_SAFETY_BOUNDARY = "report-only / not FORMAL_GO / no automatic order / human decides manually"


def _to_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed == 0.0:
        return None
    return parsed


def _round2(value: Any) -> float | None:
    parsed = _to_float(value)
    if parsed is None:
        return None
    return round(parsed, 2)


def _normalize_side(side: Any) -> str:
    text = str(side or "").strip().lower()
    if text in {"long", "buy"}:
        return "long"
    if text in {"short", "sell"}:
        return "short"
    return ""


def _normalize_zone(zone: Any) -> dict[str, float] | None:
    if not isinstance(zone, dict):
        return None
    low = _round2(zone.get("low"))
    high = _round2(zone.get("high"))
    if low is None or high is None:
        return None
    if low > high:
        low, high = high, low
    return {"low": low, "high": high}


def _next_deeper_zone(
    side: str,
    shallow_zone: dict[str, float] | None,
    support_zones: list[dict[str, Any]],
    resistance_zones: list[dict[str, Any]],
) -> dict[str, float] | None:
    if shallow_zone is None:
        return None
    if side == "long":
        candidates = [
            zone
            for zone in support_zones
            if isinstance(zone, dict)
            and _to_float(zone.get("low")) is not None
            and _to_float(zone.get("high")) is not None
            and float(zone["high"]) < float(shallow_zone["low"])
        ]
        if not candidates:
            return None
        selected = max(candidates, key=lambda zone: (float(zone["high"]), float(zone.get("strength", 0))))
        return _normalize_zone(selected)

    candidates = [
        zone
        for zone in resistance_zones
        if isinstance(zone, dict)
        and _to_float(zone.get("low")) is not None
        and _to_float(zone.get("high")) is not None
        and float(zone["low"]) > float(shallow_zone["high"])
    ]
    if not candidates:
        return None
    selected = min(candidates, key=lambda zone: (float(zone["low"]), -float(zone.get("strength", 0))))
    return _normalize_zone(selected)


def _clear_break_band(price: float, atr: float) -> float:
    del price
    return max(abs(float(atr)) * 0.08, 1.0)


def _market_entry_status(setup: dict[str, Any]) -> str:
    return str(setup.get("status", "")).strip() or "watch"


def _continuation_trigger_long(shallow_zone: dict[str, float] | None, entry_mid: Any) -> float | None:
    if shallow_zone is None:
        return _round2(entry_mid)
    if entry_mid is not None:
        mid = _round2(entry_mid)
        if mid is not None:
            return mid
    return _round2((float(shallow_zone["low"]) + float(shallow_zone["high"])) / 2)


def _continuation_trigger_short(shallow_zone: dict[str, float] | None, entry_mid: Any) -> float | None:
    return _continuation_trigger_long(shallow_zone, entry_mid)


def _lifecycle_state_long(
    price: float,
    shallow_zone: dict[str, float] | None,
    value_zone: dict[str, float] | None,
    invalidation_zone: dict[str, float] | None,
    reclaim_trigger: float | None,
    continuation_trigger: float | None,
) -> str:
    if invalidation_zone is not None and price <= float(invalidation_zone["high"]):
        return "invalidated"
    if value_zone is not None:
        if float(value_zone["low"]) <= price <= float(value_zone["high"]):
            return "defense_zone_touched"
        if float(value_zone["high"]) < price < (reclaim_trigger or float(shallow_zone["low"])):
            return "support_test"
        if reclaim_trigger is not None and price < float(shallow_zone["low"]) and price >= reclaim_trigger:
            return "support_defended"
        if shallow_zone is not None and float(shallow_zone["low"]) <= price <= float(shallow_zone["high"]):
            return "shallow_retest_risk"
        if reclaim_trigger is not None and price < reclaim_trigger:
            return "reclaim_wait"
    if shallow_zone is not None and float(shallow_zone["low"]) <= price <= float(shallow_zone["high"]):
        return "shallow_retest_risk"
    if continuation_trigger is not None and price < continuation_trigger:
        return "reclaim_wait"
    return "continuation_candidate"


def _lifecycle_state_short(
    price: float,
    shallow_zone: dict[str, float] | None,
    value_zone: dict[str, float] | None,
    invalidation_zone: dict[str, float] | None,
    reclaim_trigger: float | None,
    continuation_trigger: float | None,
) -> str:
    if invalidation_zone is not None and price >= float(invalidation_zone["low"]):
        return "invalidated"
    if value_zone is not None:
        if float(value_zone["low"]) <= price <= float(value_zone["high"]):
            return "defense_zone_touched"
        if float(value_zone["high"]) < price < (reclaim_trigger or float(shallow_zone["high"])):
            return "rebound_wait"
        if reclaim_trigger is not None and price > float(shallow_zone["high"]) and price <= reclaim_trigger:
            return "resistance_defended"
        if shallow_zone is not None and float(shallow_zone["low"]) <= price <= float(shallow_zone["high"]):
            return "shallow_retest_risk"
        if continuation_trigger is not None and price > continuation_trigger:
            return "breakdown_wait"
    if shallow_zone is not None and float(shallow_zone["low"]) <= price <= float(shallow_zone["high"]):
        return "shallow_retest_risk"
    if continuation_trigger is not None and price > continuation_trigger:
        return "breakdown_wait"
    return "continuation_candidate"


def build_value_defense_entry_layer(
    *,
    side: Any,
    price: Any,
    atr: Any,
    setup: dict[str, Any] | None,
    support_zones: list[dict[str, Any]] | None = None,
    resistance_zones: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_side = _normalize_side(side)
    current_price = _to_float(price)
    atr_value = _to_float(atr)
    setup_data = setup if isinstance(setup, dict) else {}
    support_zones = support_zones or []
    resistance_zones = resistance_zones or []

    shallow_zone = _normalize_zone(setup_data.get("entry_zone"))
    market_entry_status = _market_entry_status(setup_data)
    if normalized_side not in {"long", "short"}:
        return {
            "schema_version": "value_defense_entry_layer.v1",
            "side": "",
            "lifecycle_state": "unresolved",
            "market_entry_status": market_entry_status,
            "shallow_retest_zone": shallow_zone,
            "shallow_retest_risk": "unresolved",
            "value_defense_zone": None,
            "defense_zone_basis": "side_unknown",
            "invalidation_zone": None,
            "reclaim_trigger": None,
            "continuation_trigger": _round2(setup_data.get("entry_mid") or (None if shallow_zone is None else (float(shallow_zone["low"]) + float(shallow_zone["high"])) / 2)),
            "operator_guidance": "side が不明なため value defense entry は未確定です。",
            "safety_boundary": _SAFETY_BOUNDARY,
        }
    value_zone = _next_deeper_zone(normalized_side, shallow_zone, support_zones, resistance_zones)
    continuation_trigger = _round2(setup_data.get("entry_mid") or (None if shallow_zone is None else (float(shallow_zone["low"]) + float(shallow_zone["high"])) / 2))
    invalidation_zone = None
    if current_price is not None and atr_value is not None:
        band = _clear_break_band(current_price, atr_value)
        stop_loss = _to_float(setup_data.get("stop_loss"))
        if stop_loss is not None:
            invalidation_zone = {
                "low": round(stop_loss - band, 2),
                "high": round(stop_loss + band, 2),
            }
    else:
        band = None
    if normalized_side == "long":
        defense_basis = "next_support_below_shallow_zone" if value_zone is not None else "shallow_only_no_deeper_support"
        if value_zone is not None and shallow_zone is not None:
            reclaim_trigger = round((float(value_zone["high"]) + float(shallow_zone["low"])) / 2, 2)
        else:
            reclaim_trigger = _round2(shallow_zone["low"]) if shallow_zone is not None else None
        shallow_risk = "high" if value_zone is not None else "shallow_only"
        if current_price is None or atr_value is None:
            lifecycle_state = "unresolved"
        else:
            lifecycle_state = (
                "invalidated"
                if invalidation_zone is not None and current_price <= float(invalidation_zone["high"])
                else _lifecycle_state_long(
                    current_price,
                    shallow_zone,
                    value_zone,
                    invalidation_zone,
                    reclaim_trigger,
                    continuation_trigger,
                )
            )
        operator_guidance = (
            "浅い押し目だけで決め打ちせず、本命押し目と invalidation を先に確認する。"
            if value_zone is not None
            else "深い value defense zone が見当たらないため、浅い retest entry のみを参考にする。"
        )
    else:
        defense_basis = "next_resistance_above_shallow_zone" if value_zone is not None else "shallow_only_no_deeper_resistance"
        if value_zone is not None and shallow_zone is not None:
            reclaim_trigger = round((float(value_zone["low"]) + float(shallow_zone["high"])) / 2, 2)
        else:
            reclaim_trigger = _round2(shallow_zone["high"]) if shallow_zone is not None else None
        shallow_risk = "high" if value_zone is not None else "shallow_only"
        if current_price is None or atr_value is None:
            lifecycle_state = "unresolved"
        else:
            lifecycle_state = (
                "invalidated"
                if invalidation_zone is not None and current_price >= float(invalidation_zone["low"])
                else _lifecycle_state_short(
                    current_price,
                    shallow_zone,
                    value_zone,
                    invalidation_zone,
                    reclaim_trigger,
                    continuation_trigger,
                )
            )
        operator_guidance = (
            "浅い戻り売りだけで決め打ちせず、本命戻り売りと invalidation を先に確認する。"
            if value_zone is not None
            else "深い value defense zone が見当たらないため、浅い retest entry のみを参考にする。"
        )

    payload = {
        "schema_version": "value_defense_entry_layer.v1",
        "side": normalized_side,
        "lifecycle_state": lifecycle_state,
        "market_entry_status": market_entry_status,
        "shallow_retest_zone": shallow_zone,
        "shallow_retest_risk": shallow_risk,
        "value_defense_zone": value_zone,
        "defense_zone_basis": defense_basis,
        "invalidation_zone": invalidation_zone,
        "reclaim_trigger": reclaim_trigger,
        "continuation_trigger": continuation_trigger,
        "operator_guidance": operator_guidance,
        "safety_boundary": _SAFETY_BOUNDARY,
    }
    return payload
