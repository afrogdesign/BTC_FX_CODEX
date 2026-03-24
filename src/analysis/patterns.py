from __future__ import annotations

from typing import Any


def _tail_values(df: Any, key: str, bars: int) -> list[float]:
    values = [float(value) for value in df[key].tolist()]
    return values[-bars:] if bars > 0 else values


def _reference_prices(levels: list[dict[str, Any]]) -> dict[str, Any]:
    if not levels:
        return {}
    first = levels[0]
    return {"low": first.get("low"), "high": first.get("high"), "strength": first.get("strength")}


def _recent_swings(swings: dict[str, list[dict[str, Any]]], kind: str, count: int = 3) -> list[dict[str, Any]]:
    return [dict(item) for item in swings.get(kind, [])[-count:]]


def _flag_pattern(
    *,
    side: str,
    closes: list[float],
    volumes: list[float],
    atr: float,
    volume_structure: dict[str, Any],
    cfg: Any,
) -> dict[str, Any] | None:
    cons_max = min(max(int(getattr(cfg, "PATTERN_CONSOLIDATION_BARS_MAX", 20)), 1), len(closes) - 1)
    cons_min = min(max(int(getattr(cfg, "PATTERN_CONSOLIDATION_BARS_MIN", 6)), 1), cons_max)
    if cons_max <= cons_min or atr <= 0:
        return None

    impulse = closes[-(cons_max + 1)] - closes[-1 - (cons_max * 2)] if len(closes) > cons_max * 2 else closes[-1] - closes[0]
    if side == "long":
        impulse = max(impulse, closes[-1] - min(closes[:-cons_min] or closes))
    else:
        impulse = max(-impulse, max(closes[:-cons_min] or closes) - closes[-1])
    if impulse < float(getattr(cfg, "PATTERN_FLAG_IMPULSE_ATR_MIN", 2.2)) * atr:
        return None

    consolidation = closes[-cons_max:]
    highest = max(consolidation)
    lowest = min(consolidation)
    pullback = (highest - lowest) / impulse if impulse > 0 else 1.0
    if not (float(getattr(cfg, "PATTERN_FLAG_PULLBACK_MIN_RATIO", 0.25)) <= pullback <= float(getattr(cfg, "PATTERN_FLAG_PULLBACK_MAX_RATIO", 0.55))):
        return None

    trend_ok = consolidation[-1] >= consolidation[0] if side == "long" else consolidation[-1] <= consolidation[0]
    if trend_ok:
        return None

    contraction_ok = volume_structure.get("volume_regime") == "contracting"
    breakout_ready = bool(volume_structure.get("breakout_volume_confirmed"))
    if not contraction_ok:
        return None

    return {
        "name": "bull_flag" if side == "long" else "bear_flag",
        "side": side,
        "score": 0.7 if breakout_ready else 0.55,
        "state": "active" if breakout_ready else "forming",
        "breakout_ready": breakout_ready,
        "reason_codes": [
            "impulse_leg_detected",
            "pullback_in_range",
            "volume_contracting",
        ] + (["breakout_volume_confirmed"] if breakout_ready else []),
        "reference_prices": {"high": round(highest, 2), "low": round(lowest, 2)},
        "window_label": "micro_window",
    }


def _triangle_pattern(
    *,
    side: str,
    swings: dict[str, list[dict[str, Any]]],
    atr: float,
    breakout_ready: bool,
    cfg: Any,
) -> dict[str, Any] | None:
    highs = _recent_swings(swings, "highs")
    lows = _recent_swings(swings, "lows")
    if len(highs) < 3 or len(lows) < 3 or atr <= 0:
        return None

    if side == "long":
        flat_points = highs
        slope_points = lows
        flat_name = "ascending_triangle"
    else:
        flat_points = lows
        slope_points = highs
        flat_name = "descending_triangle"

    flat_prices = [float(item["price"]) for item in flat_points]
    slope_prices = [float(item["price"]) for item in slope_points]
    flat_variance = (max(flat_prices) - min(flat_prices)) / atr
    if flat_variance > float(getattr(cfg, "PATTERN_TRIANGLE_FLAT_VARIANCE_ATR_MAX", 0.35)):
        return None

    diffs = [b - a for a, b in zip(slope_prices, slope_prices[1:])]
    step_min = float(getattr(cfg, "PATTERN_TRIANGLE_STEP_ATR_MIN", 0.15)) * atr
    if side == "long":
        valid_steps = all(diff >= step_min for diff in diffs)
    else:
        valid_steps = all(diff <= -step_min for diff in diffs)
    if not valid_steps:
        return None

    return {
        "name": flat_name,
        "side": side,
        "score": 0.75 if breakout_ready else 0.6,
        "state": "active" if breakout_ready else "forming",
        "breakout_ready": breakout_ready,
        "reason_codes": ["flat_boundary", "stepwise_compression"] + (["breakout_ready"] if breakout_ready else []),
        "reference_prices": {"flat_level": round(sum(flat_prices) / len(flat_prices), 2)},
        "window_label": "micro_window",
    }


def _failed_breakout_pattern(
    *,
    closes: list[float],
    highs: list[float],
    lows: list[float],
    price: float,
    atr: float,
    breakout_up: bool,
    breakout_down: bool,
    volume_structure: dict[str, Any],
    cfg: Any,
) -> dict[str, Any] | None:
    bars = min(max(int(getattr(cfg, "PATTERN_FAILED_BREAKOUT_RETURN_BARS", 4)), 1), len(closes) - 1)
    if bars <= 0 or atr <= 0:
        return None
    threshold = float(getattr(cfg, "PATTERN_FAILED_BREAKOUT_EXCESS_ATR_MIN", 0.15)) * atr
    wick_min = float(getattr(cfg, "PATTERN_FAILED_BREAKOUT_WICK_RATIO_MIN", 0.35))
    recent_high = max(highs[-(bars + 1) : -1]) if len(highs) > bars else max(highs[:-1] or highs)
    recent_low = min(lows[-(bars + 1) : -1]) if len(lows) > bars else min(lows[:-1] or lows)
    last_high = highs[-1]
    last_low = lows[-1]
    last_close = closes[-1]
    body = abs(last_close - closes[-2]) if len(closes) >= 2 else 0.0
    range_size = max(last_high - last_low, 1e-9)
    upper_wick_ratio = (last_high - max(last_close, closes[-2] if len(closes) >= 2 else last_close)) / range_size
    lower_wick_ratio = (min(last_close, closes[-2] if len(closes) >= 2 else last_close) - last_low) / range_size
    weak_volume = float(volume_structure.get("expansion_score", 1.0)) < float(getattr(cfg, "PATTERN_EXPANSION_RATIO_MIN", 1.15))

    if breakout_up and last_high >= recent_high + threshold and last_close <= recent_high and (upper_wick_ratio >= wick_min or weak_volume):
        return {
            "name": "failed_breakout",
            "side": "short",
            "score": 0.7,
            "state": "active",
            "breakout_ready": True,
            "reason_codes": ["breakout_reverted", "upper_wick_rejection" if upper_wick_ratio >= wick_min else "weak_volume_followthrough"],
            "reference_prices": {"failed_level": round(recent_high, 2), "body": round(body, 2)},
            "window_label": "trigger_window",
        }
    if breakout_down and last_low <= recent_low - threshold and last_close >= recent_low and (lower_wick_ratio >= wick_min or weak_volume):
        return {
            "name": "failed_breakout",
            "side": "long",
            "score": 0.7,
            "state": "active",
            "breakout_ready": True,
            "reason_codes": ["breakout_reverted", "lower_wick_rejection" if lower_wick_ratio >= wick_min else "weak_volume_followthrough"],
            "reference_prices": {"failed_level": round(recent_low, 2), "body": round(body, 2)},
            "window_label": "trigger_window",
        }
    return None


def analyze_chart_patterns(
    *,
    price: float,
    atr: float,
    df_15m: Any,
    swings_15m: dict[str, list[dict[str, Any]]],
    breakout_up: bool,
    breakout_down: bool,
    volume_structure: dict[str, Any],
    sr_context: dict[str, Any],
    cfg: Any,
) -> dict[str, Any]:
    closes = [float(value) for value in df_15m["close"].tolist()]
    highs = [float(value) for value in df_15m["high"].tolist()]
    lows = [float(value) for value in df_15m["low"].tolist()]
    volumes = [float(value) for value in df_15m["volume"].tolist()]
    detected: list[dict[str, Any]] = []

    for pattern in (
        _flag_pattern(side="long", closes=closes, volumes=volumes, atr=atr, volume_structure=volume_structure, cfg=cfg),
        _flag_pattern(side="short", closes=closes, volumes=volumes, atr=atr, volume_structure=volume_structure, cfg=cfg),
        _triangle_pattern(side="long", swings=swings_15m, atr=atr, breakout_ready=breakout_up, cfg=cfg),
        _triangle_pattern(side="short", swings=swings_15m, atr=atr, breakout_ready=breakout_down, cfg=cfg),
        _failed_breakout_pattern(
            closes=closes,
            highs=highs,
            lows=lows,
            price=price,
            atr=atr,
            breakout_up=breakout_up,
            breakout_down=breakout_down,
            volume_structure=volume_structure,
            cfg=cfg,
        ),
    ):
        if pattern is not None:
            detected.append(pattern)

    long_score = round(sum(float(item["score"]) for item in detected if item["side"] == "long"), 4)
    short_score = round(sum(float(item["score"]) for item in detected if item["side"] == "short"), 4)
    primary = max(detected, key=lambda item: float(item["score"]), default={})
    conflicts = []
    if long_score > 0 and short_score > 0:
        conflicts.append("long_short_pattern_conflict")
    if detected and not primary:
        conflicts.append("no_primary_pattern")

    context = {
        "detected_patterns": detected[:5],
        "primary_pattern": primary.get("name", ""),
        "pattern_scores": {"long": long_score, "short": short_score},
        "pattern_conflicts": conflicts,
    }
    if not detected:
        context["pattern_conflicts"] = []
    if not context["detected_patterns"]:
        context["primary_pattern"] = ""
    return context
