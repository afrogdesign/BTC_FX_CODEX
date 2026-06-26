from __future__ import annotations

from typing import Any


SOURCE_WEIGHT = {"4h": 4.0, "1h": 3.0, "15m": 1.5}


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def _df_values(df: Any, key: str) -> list[float]:
    try:
        return [float(value) for value in df[key].tolist()]
    except AttributeError:
        return [float(value) for value in df[key]]


def _iter_rows(df: Any) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for row in df.itertuples(index=False):
        rows.append(
            {
                "open": float(getattr(row, "open")),
                "high": float(getattr(row, "high")),
                "low": float(getattr(row, "low")),
                "close": float(getattr(row, "close")),
                "volume": float(getattr(row, "volume", 0.0)),
            }
        )
    return rows


def _zone_mid(zone: dict[str, Any]) -> float:
    return (float(zone["low"]) + float(zone["high"])) / 2.0


def _zone_distance(price: float, zone: dict[str, Any]) -> float:
    low = float(zone["low"])
    high = float(zone["high"])
    if low <= price <= high:
        return 0.0
    if price < low:
        return low - price
    return price - high


def _touches_zone(row: dict[str, float], low: float, high: float) -> bool:
    return row["high"] >= low and row["low"] <= high


def _reaction_stats(df: Any, low: float, high: float, kind: str, cfg: Any) -> dict[str, Any]:
    rows = _iter_rows(df)
    if not rows:
        return {"reaction_count": 0, "wick_rejections": 0, "volume_touches": 0, "last_touch_age": None}

    avg_volume = sum(row["volume"] for row in rows) / len(rows) if rows else 0.0
    volume_mult = float(getattr(cfg, "MARKET_MAP_VOLUME_TOUCH_RATIO", 1.20))
    wick_min = float(getattr(cfg, "MARKET_MAP_WICK_REJECTION_RATIO_MIN", 0.35))
    reaction_count = 0
    wick_rejections = 0
    volume_touches = 0
    last_touch_idx: int | None = None
    last_reaction_idx = -999

    for idx, row in enumerate(rows):
        if not _touches_zone(row, low, high):
            continue
        if idx - last_reaction_idx > 3:
            reaction_count += 1
        last_reaction_idx = idx
        last_touch_idx = idx

        body_low = min(row["open"], row["close"])
        body_high = max(row["open"], row["close"])
        candle_range = max(row["high"] - row["low"], 1e-9)
        lower_wick_ratio = (body_low - row["low"]) / candle_range
        upper_wick_ratio = (row["high"] - body_high) / candle_range
        if kind == "support" and lower_wick_ratio >= wick_min and row["close"] >= low:
            wick_rejections += 1
        elif kind == "resistance" and upper_wick_ratio >= wick_min and row["close"] <= high:
            wick_rejections += 1
        if avg_volume > 0 and row["volume"] >= avg_volume * volume_mult:
            volume_touches += 1

    last_touch_age = len(rows) - 1 - last_touch_idx if last_touch_idx is not None else None
    return {
        "reaction_count": reaction_count,
        "wick_rejections": wick_rejections,
        "volume_touches": volume_touches,
        "last_touch_age": last_touch_age,
    }


def _build_raw_zone(
    *,
    price: float,
    atr: float,
    source: str,
    kind: str,
    df: Any,
    cfg: Any,
) -> dict[str, Any]:
    half = max(float(atr) * float(getattr(cfg, "MARKET_MAP_ZONE_HALF_ATR", 0.25)), price * 0.0004, 1.0)
    low = price - half
    high = price + half
    stats = _reaction_stats(df, low, high, kind, cfg)
    recency_score = 0.0
    if stats["last_touch_age"] is not None:
        lookback = max(int(getattr(cfg, "MARKET_MAP_RECENCY_LOOKBACK_BARS", 96)), 1)
        recency_score = max(0.0, 1.0 - (float(stats["last_touch_age"]) / lookback)) * 2.0
    strength = (
        SOURCE_WEIGHT.get(source, 1.0)
        + float(stats["reaction_count"]) * 1.5
        + float(stats["wick_rejections"]) * 1.25
        + float(stats["volume_touches"]) * 0.75
        + recency_score
    )
    return {
        "low": low,
        "high": high,
        "mid": (low + high) / 2.0,
        "kind": kind,
        "source": source,
        "sources": [source],
        "strength": strength,
        "reaction_count": stats["reaction_count"],
        "wick_rejections": stats["wick_rejections"],
        "volume_touches": stats["volume_touches"],
        "last_touch_age": stats["last_touch_age"],
        "recency_score": recency_score,
    }


def _collect_raw_zones(per_tf_inputs: dict[str, dict[str, Any]], atr: float, cfg: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    supports: list[dict[str, Any]] = []
    resistances: list[dict[str, Any]] = []
    swing_limit = max(int(getattr(cfg, "MARKET_MAP_SWING_LIMIT_PER_TF", 12)), 1)
    for source, payload in per_tf_inputs.items():
        df = payload.get("df")
        swings = payload.get("swings") or {}
        if df is None:
            continue
        for item in list(swings.get("lows", []))[-swing_limit:]:
            supports.append(
                _build_raw_zone(
                    price=float(item["price"]),
                    atr=atr,
                    source=source,
                    kind="support",
                    df=df,
                    cfg=cfg,
                )
            )
        for item in list(swings.get("highs", []))[-swing_limit:]:
            resistances.append(
                _build_raw_zone(
                    price=float(item["price"]),
                    atr=atr,
                    source=source,
                    kind="resistance",
                    df=df,
                    cfg=cfg,
                )
            )
    return supports, resistances


def _merge_zones(zones: list[dict[str, Any]], atr: float, price: float, cfg: Any) -> list[dict[str, Any]]:
    if not zones:
        return []
    threshold = max(atr * float(getattr(cfg, "MARKET_MAP_LEVEL_MERGE_ATR", 0.50)), price * 0.0004, 1.0)
    ordered = sorted(zones, key=_zone_mid)
    merged: list[dict[str, Any]] = []
    for zone in ordered:
        if not merged:
            merged.append(dict(zone))
            continue
        last = merged[-1]
        if abs(_zone_mid(zone) - _zone_mid(last)) <= threshold:
            last["low"] = min(float(last["low"]), float(zone["low"]))
            last["high"] = max(float(last["high"]), float(zone["high"]))
            last["mid"] = _zone_mid(last)
            last["sources"] = _dedupe(list(last.get("sources", [])) + list(zone.get("sources", [])))
            last["source"] = max(last["sources"], key=lambda item: SOURCE_WEIGHT.get(item, 1.0))
            last["strength"] = float(last.get("strength", 0.0)) + float(zone.get("strength", 0.0))
            last["reaction_count"] = int(last.get("reaction_count", 0)) + int(zone.get("reaction_count", 0))
            last["wick_rejections"] = int(last.get("wick_rejections", 0)) + int(zone.get("wick_rejections", 0))
            last["volume_touches"] = int(last.get("volume_touches", 0)) + int(zone.get("volume_touches", 0))
            ages = [age for age in (last.get("last_touch_age"), zone.get("last_touch_age")) if age is not None]
            last["last_touch_age"] = min(ages) if ages else None
            last["recency_score"] = float(last.get("recency_score", 0.0)) + float(zone.get("recency_score", 0.0))
        else:
            merged.append(dict(zone))
    return merged


def _format_level(level: dict[str, Any], price: float, atr: float) -> dict[str, Any]:
    distance = _zone_distance(price, level)
    formatted = {
        "low": round(float(level["low"]), 2),
        "high": round(float(level["high"]), 2),
        "mid": round(_zone_mid(level), 2),
        "kind": str(level.get("kind", "")),
        "source": str(level.get("source", "")),
        "sources": list(level.get("sources", [])),
        "confluence_count": len(set(level.get("sources", []))),
        "strength": round(float(level.get("strength", 0.0)), 2),
        "reaction_count": int(level.get("reaction_count", 0)),
        "wick_rejections": int(level.get("wick_rejections", 0)),
        "volume_touches": int(level.get("volume_touches", 0)),
        "last_touch_age": level.get("last_touch_age"),
        "distance_from_price": round(distance, 2),
        "distance_atr": round(distance / atr, 4) if atr > 0 else None,
    }
    return formatted


def _sort_nearest(levels: list[dict[str, Any]], price: float, atr: float) -> list[dict[str, Any]]:
    formatted = [_format_level(level, price, atr) for level in levels]
    formatted.sort(key=lambda level: (float(level["distance_from_price"]), -float(level["strength"])))
    return formatted


def _recent_rows(df: Any, bars: int) -> list[dict[str, float]]:
    rows = _iter_rows(df)
    return rows[-bars:] if bars > 0 else rows


def _detect_role_flip(
    *,
    price: float,
    atr: float,
    supports: list[dict[str, Any]],
    resistances: list[dict[str, Any]],
    df_15m: Any,
    cfg: Any,
) -> tuple[str, dict[str, Any], list[str]]:
    if atr <= 0:
        return "", {}, []
    flags: list[str] = []
    break_threshold = atr * float(getattr(cfg, "MARKET_MAP_ROLE_FLIP_BREAK_ATR", 0.15))
    retest_tolerance = atr * float(getattr(cfg, "MARKET_MAP_RETEST_TOLERANCE_ATR", 0.30))
    rows = _recent_rows(df_15m, max(int(getattr(cfg, "MARKET_MAP_ROLE_FLIP_LOOKBACK_BARS", 16)), 3))
    closes = [row["close"] for row in rows]
    if not rows or not closes:
        return "", {}, []

    broken_supports = [level for level in supports if price < float(level["low"]) - break_threshold]
    broken_supports.sort(key=lambda level: (_zone_distance(price, level), -float(level.get("strength", 0.0))))
    for level in broken_supports[:3]:
        low = float(level["low"])
        broke = any(close < low - break_threshold for close in closes)
        retested = any(row["high"] >= low - retest_tolerance and row["close"] < low for row in rows[-8:])
        if broke and retested:
            flags.extend(["support_to_resistance_flip", "support_to_resistance_retest_confirmed"])
            return "support_to_resistance_confirmed", _format_level(level, price, atr), _dedupe(flags)
        if broke and price >= low - (retest_tolerance * 1.5):
            flags.append("support_to_resistance_flip")
            return "support_to_resistance_early", _format_level(level, price, atr), _dedupe(flags)

    broken_resistances = [level for level in resistances if price > float(level["high"]) + break_threshold]
    broken_resistances.sort(key=lambda level: (_zone_distance(price, level), -float(level.get("strength", 0.0))))
    for level in broken_resistances[:3]:
        high = float(level["high"])
        broke = any(close > high + break_threshold for close in closes)
        retested = any(row["low"] <= high + retest_tolerance and row["close"] > high for row in rows[-8:])
        if broke and retested:
            flags.extend(["resistance_to_support_flip", "resistance_to_support_retest_confirmed"])
            return "resistance_to_support_confirmed", _format_level(level, price, atr), _dedupe(flags)
        if broke and price <= high + (retest_tolerance * 1.5):
            flags.append("resistance_to_support_flip")
            return "resistance_to_support_early", _format_level(level, price, atr), _dedupe(flags)

    return "", {}, []


def _detect_failed_breakout(
    *,
    price: float,
    atr: float,
    df_15m: Any,
    breakout_up: bool,
    breakout_down: bool,
    nearest_support: dict[str, Any],
    nearest_resistance: dict[str, Any],
    volume_info: dict[str, Any],
    cfg: Any,
) -> tuple[str, dict[str, Any], list[str]]:
    closes = _df_values(df_15m, "close")
    highs = _df_values(df_15m, "high")
    lows = _df_values(df_15m, "low")
    if len(closes) < 3 or atr <= 0:
        return "", {}, []

    bars = min(max(int(getattr(cfg, "MARKET_MAP_FAILED_BREAKOUT_LOOKBACK_BARS", 8)), 2), len(closes) - 1)
    threshold = atr * float(getattr(cfg, "MARKET_MAP_FAILED_BREAKOUT_EXCESS_ATR", 0.12))
    tolerance = atr * float(getattr(cfg, "MARKET_MAP_FAILED_BREAKOUT_RETURN_ATR", 0.10))
    wick_min = float(getattr(cfg, "MARKET_MAP_WICK_REJECTION_RATIO_MIN", 0.35))
    recent_high = max(highs[-(bars + 1) : -1])
    recent_low = min(lows[-(bars + 1) : -1])
    last_open = _df_values(df_15m, "open")[-1]
    last_high = highs[-1]
    last_low = lows[-1]
    last_close = closes[-1]
    candle_range = max(last_high - last_low, 1e-9)
    body_high = max(last_open, last_close)
    body_low = min(last_open, last_close)
    upper_wick_ratio = (last_high - body_high) / candle_range
    lower_wick_ratio = (body_low - last_low) / candle_range
    weak_volume = float(volume_info.get("expansion_score", 1.0) or 1.0) < float(getattr(cfg, "PATTERN_EXPANSION_RATIO_MIN", 1.15))
    flags: list[str] = []

    resistance_level = nearest_resistance or {}
    resistance_touched = bool(resistance_level) and last_high >= float(resistance_level.get("low", 0.0)) - threshold
    resistance_break_attempt = bool(resistance_level) and last_high >= float(resistance_level.get("high", 0.0)) + threshold
    resistance_rejected = bool(resistance_level) and last_close <= float(resistance_level.get("high", 0.0))
    up_attempt = bool(breakout_up) or last_high >= recent_high + threshold or resistance_break_attempt
    reverted_up = last_close <= recent_high + tolerance or (resistance_touched and resistance_rejected)
    if up_attempt and reverted_up and (upper_wick_ratio >= wick_min or weak_volume):
        flags.extend(["failed_breakout_down_reversal", "major_resistance_rejection"])
        return (
            "down_reversal",
            {
                "failed_level": round(max(recent_high, float(resistance_level.get("mid", recent_high))), 2),
                "upper_wick_ratio": round(upper_wick_ratio, 4),
                "weak_volume": weak_volume,
            },
            _dedupe(flags),
        )
    if resistance_touched and upper_wick_ratio >= wick_min:
        flags.append("major_resistance_rejection")

    support_level = nearest_support or {}
    support_touched = bool(support_level) and last_low <= float(support_level.get("high", 0.0)) + threshold
    support_break_attempt = bool(support_level) and last_low <= float(support_level.get("low", 0.0)) - threshold
    support_rejected = bool(support_level) and last_close >= float(support_level.get("low", 0.0))
    down_attempt = bool(breakout_down) or last_low <= recent_low - threshold or support_break_attempt
    reverted_down = last_close >= recent_low - tolerance or (support_touched and support_rejected)
    if down_attempt and reverted_down and (lower_wick_ratio >= wick_min or weak_volume):
        flags.extend(["failed_breakout_up_reversal", "major_support_rejection"])
        return (
            "up_reversal",
            {
                "failed_level": round(min(recent_low, float(support_level.get("mid", recent_low))), 2),
                "lower_wick_ratio": round(lower_wick_ratio, 4),
                "weak_volume": weak_volume,
            },
            _dedupe(flags),
        )
    if support_touched and lower_wick_ratio >= wick_min:
        flags.append("major_support_rejection")

    return "", {}, _dedupe(flags)


def _trend_flip_state(flags: list[str], per_tf_inputs: dict[str, dict[str, Any]]) -> str:
    structures = {tf: str(payload.get("structure", "")) for tf, payload in per_tf_inputs.items()}
    down_trigger = bool({"support_to_resistance_flip", "failed_breakout_down_reversal"} & set(flags))
    up_trigger = bool({"resistance_to_support_flip", "failed_breakout_up_reversal"} & set(flags))
    if down_trigger:
        if structures.get("1h") == "lh_ll" or (structures.get("15m") == "lh_ll" and structures.get("4h") in {"lh_ll", "mixed"}):
            return "confirmed_down"
        return "early_down"
    if up_trigger:
        if structures.get("1h") == "hh_hl" or (structures.get("15m") == "hh_hl" and structures.get("4h") in {"hh_hl", "mixed"}):
            return "confirmed_up"
        return "early_up"
    return ""


def _primary_state(flags: list[str], trend_flip_state: str, failed_breakout_state: str, active_role: str) -> str:
    if trend_flip_state:
        return trend_flip_state
    if failed_breakout_state:
        return failed_breakout_state
    if "long_into_major_resistance" in flags:
        return "near_major_resistance"
    if "short_into_major_support" in flags:
        return "near_major_support"
    if active_role:
        return f"active_{active_role}"
    return "balanced"


def build_market_map(
    *,
    price: float,
    atr: float,
    per_tf_inputs: dict[str, dict[str, Any]],
    volume_info: dict[str, Any] | None,
    breakout_up: bool,
    breakout_down: bool,
    cfg: Any,
) -> dict[str, Any]:
    safe_atr = max(float(atr), 1e-9)
    volume_info = volume_info or {}
    raw_supports, raw_resistances = _collect_raw_zones(per_tf_inputs, safe_atr, cfg)
    supports = _merge_zones(raw_supports, safe_atr, float(price), cfg)
    resistances = _merge_zones(raw_resistances, safe_atr, float(price), cfg)

    support_candidates = [level for level in supports if float(level["low"]) <= price]
    resistance_candidates = [level for level in resistances if float(level["high"]) >= price]
    nearest_supports = _sort_nearest(support_candidates or supports, float(price), safe_atr)[:5]
    nearest_resistances = _sort_nearest(resistance_candidates or resistances, float(price), safe_atr)[:5]
    nearest_support = nearest_supports[0] if nearest_supports else {}
    nearest_resistance = nearest_resistances[0] if nearest_resistances else {}

    active_level: dict[str, Any] = {}
    active_role = ""
    if nearest_support or nearest_resistance:
        support_dist = float(nearest_support.get("distance_from_price", 1e18)) if nearest_support else 1e18
        resistance_dist = float(nearest_resistance.get("distance_from_price", 1e18)) if nearest_resistance else 1e18
        if support_dist <= resistance_dist:
            active_level = dict(nearest_support)
            active_role = "support"
        else:
            active_level = dict(nearest_resistance)
            active_role = "resistance"

    flags: list[str] = []
    active_distance_atr = float(getattr(cfg, "MARKET_MAP_ACTIVE_DISTANCE_ATR", 0.75))
    if nearest_resistance and float(nearest_resistance.get("distance_atr") or 0.0) <= active_distance_atr:
        flags.append("long_into_major_resistance")
    if nearest_support and float(nearest_support.get("distance_atr") or 0.0) <= active_distance_atr:
        flags.append("short_into_major_support")

    df_15m = per_tf_inputs.get("15m", {}).get("df")
    level_flip_state = ""
    level_flip_reference: dict[str, Any] = {}
    if df_15m is not None:
        level_flip_state, level_flip_reference, flip_flags = _detect_role_flip(
            price=float(price),
            atr=safe_atr,
            supports=supports,
            resistances=resistances,
            df_15m=df_15m,
            cfg=cfg,
        )
        flags.extend(flip_flags)

    failed_breakout_state = ""
    failed_breakout_reference: dict[str, Any] = {}
    if df_15m is not None:
        failed_breakout_state, failed_breakout_reference, failed_flags = _detect_failed_breakout(
            price=float(price),
            atr=safe_atr,
            df_15m=df_15m,
            breakout_up=breakout_up,
            breakout_down=breakout_down,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            volume_info=volume_info,
            cfg=cfg,
        )
        flags.extend(failed_flags)

    flags = _dedupe(flags)
    trend_state = _trend_flip_state(flags, per_tf_inputs)
    if trend_state == "confirmed_down":
        flags.append("trend_flip_confirmed_down")
    elif trend_state == "confirmed_up":
        flags.append("trend_flip_confirmed_up")
    elif trend_state == "early_down":
        flags.append("trend_flip_early_down")
    elif trend_state == "early_up":
        flags.append("trend_flip_early_up")
    flags = _dedupe(flags)

    conflicts: list[str] = []
    if bool({"failed_breakout_down_reversal", "support_to_resistance_flip"} & set(flags)) and bool(
        {"failed_breakout_up_reversal", "resistance_to_support_flip"} & set(flags)
    ):
        conflicts.append("both_direction_flip_flags")

    active_level_role = active_role
    if level_flip_state.startswith("support_to_resistance"):
        active_level_role = "resistance"
    elif level_flip_state.startswith("resistance_to_support"):
        active_level_role = "support"

    return {
        "version": "v1",
        "market_map_primary_state": _primary_state(flags, trend_state, failed_breakout_state, active_level_role),
        "flags": flags,
        "major_support_levels": nearest_supports,
        "major_resistance_levels": nearest_resistances,
        "nearest_major_support": nearest_support,
        "nearest_major_resistance": nearest_resistance,
        "active_level": active_level,
        "active_level_role": active_level_role,
        "level_flip_state": level_flip_state,
        "level_flip_reference": level_flip_reference,
        "failed_breakout_state": failed_breakout_state,
        "failed_breakout_reference": failed_breakout_reference,
        "trend_flip_state": trend_state,
        "market_map_conflicts": conflicts,
    }
