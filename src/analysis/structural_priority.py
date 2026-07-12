"""Deterministic medium-term structural priority (report-only)."""

from __future__ import annotations

import json
import math
from typing import Any


_LONG_4H = {
    "regime_uptrend": 15,
    "ema_alignment_bullish": 12,
    "ema20_slope_up": 6,
    "price_above_ema50_4h": 6,
    "structure_4h_hh_hl": 14,
}
_SHORT_4H = {
    "regime_downtrend": 15,
    "ema_alignment_bearish": 12,
    "ema20_slope_down": 6,
    "price_below_ema50_4h": 6,
    "structure_4h_lh_ll": 14,
}
_LONG_1H = {"structure_1h_hh_hl": 12}
_SHORT_1H = {"structure_1h_lh_ll": 12}

_TURNING = {
    "long": {
        "confirmed": {"trend_flip_confirmed_up", "resistance_to_support_confirmed", "resistance_to_support_retest_confirmed"},
        "early": {"trend_flip_early_up", "failed_breakout_up_reversal", "major_support_rejection"},
    },
    "short": {
        "confirmed": {"trend_flip_confirmed_down", "support_to_resistance_confirmed", "support_to_resistance_retest_confirmed"},
        "early": {"trend_flip_early_down", "failed_breakout_down_reversal", "major_resistance_rejection"},
    },
}


def _tokens(value: Any) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        values = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                values = parsed if isinstance(parsed, list) else [text]
            except (TypeError, ValueError, json.JSONDecodeError):
                values = text.replace("|", ",").split(",")
        else:
            values = text.replace("|", ",").split(",")
    else:
        return []
    return [str(item).strip().strip("[]'").strip().lower() for item in values if str(item).strip()]


def _factor_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
    return {}


def _positive(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number > 0


def _score(factors: dict[str, Any], weights: dict[str, int]) -> tuple[int, list[str]]:
    codes = [code for code in weights if _positive(factors.get(code))]
    return sum(weights[code] for code in codes), codes


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _turning_watch(current: dict[str, Any], structural_side: str) -> dict[str, Any]:
    fields = (
        "market_map_flags", "transition_direction", "market_map_primary_state",
        "trend_flip_state", "level_flip_state", "failed_breakout_state",
    )
    tokens = {token for field in fields for token in _tokens(current.get(field))}
    matched: dict[str, dict[str, list[str]]] = {
        "long": {"confirmed": [], "early": []},
        "short": {"confirmed": [], "early": []},
    }
    for side in ("long", "short"):
        for strength in ("confirmed", "early"):
            matched[side][strength] = sorted(tokens & _TURNING[side][strength])
    confirmed_sides = [side for side in ("long", "short") if matched[side]["confirmed"]]
    early_sides = [side for side in ("long", "short") if matched[side]["early"]]
    if len(confirmed_sides) == 2:
        direction, strength = "mixed", "confirmed"
    elif len(confirmed_sides) == 1:
        direction, strength = confirmed_sides[0], "confirmed"
    elif len(early_sides) == 2:
        direction, strength = "mixed", "early"
    elif len(early_sides) == 1:
        direction, strength = early_sides[0], "early"
    else:
        direction, strength = "none", "none"
    reason_codes = sorted({code for side in matched.values() for values in side.values() for code in values})
    return {
        "direction": direction,
        "strength": strength,
        "reason_codes": reason_codes,
        "against_structural_priority": bool(direction in {"long", "short"} and structural_side and direction != structural_side),
    }


def build_structural_priority(current: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(current, dict):
        current = {}
    long_4h_factors = _factor_dict(current.get("score_factor_breakdown_long"))
    short_4h_factors = _factor_dict(current.get("score_factor_breakdown_short"))
    long_4h, long_4h_codes = _score(long_4h_factors, _LONG_4H)
    short_4h, short_4h_codes = _score(short_4h_factors, _SHORT_4H)
    long_1h, long_1h_codes = _score(long_4h_factors, _LONG_1H)
    short_1h, short_1h_codes = _score(short_4h_factors, _SHORT_1H)
    present = bool(long_4h_codes or short_4h_codes or long_1h_codes or short_1h_codes)
    net_4h = _clamp((long_4h - short_4h) / 53, -1.0, 1.0)
    net_1h = _clamp((long_1h - short_1h) / 12, -1.0, 1.0)
    weighted_net = 0.75 * net_4h + 0.25 * net_1h
    long_points = int(round(_clamp(50 + 40 * weighted_net, 10, 90))) if present else 50
    short_points = 100 - long_points
    if not present:
        primary_side = ""
        strength = "insufficient"
        priority_label = "判定材料不足"
    elif 45 <= long_points <= 55:
        primary_side = ""
        strength = "neutral"
        priority_label = "中立圏（Long寄り）" if long_points > 50 else "中立圏（Short寄り）" if long_points < 50 else "中立"
    elif long_points > 55:
        primary_side = "long"
        if long_points <= 64:
            strength, priority_label = "slight", "Long やや優勢"
        elif long_points <= 74:
            strength, priority_label = "clear", "Long 明確優勢"
        elif long_points <= 84:
            strength, priority_label = "strong", "Long 強い優勢"
        else:
            strength, priority_label = "very_strong", "Long 非常に強い優勢"
    else:
        primary_side = "short"
        if short_points <= 64:
            strength, priority_label = "slight", "Short やや優勢"
        elif short_points <= 74:
            strength, priority_label = "clear", "Short 明確優勢"
        elif short_points <= 84:
            strength, priority_label = "strong", "Short 強い優勢"
        else:
            strength, priority_label = "very_strong", "Short 非常に強い優勢"
    turning = _turning_watch(current, primary_side)
    action = current.get("side_aware_mtf_action") if isinstance(current.get("side_aware_mtf_action"), dict) else {}
    execution = action.get("execution_context") if isinstance(action.get("execution_context"), dict) else {}
    action_side = str(execution.get("primary_side") or "").lower()
    if not primary_side or not action_side:
        alignment = "neutral"
    elif primary_side == action_side:
        alignment = "aligned"
    elif turning.get("direction") == action_side and turning.get("strength") == "confirmed":
        alignment = "turning_candidate"
    else:
        alignment = "countertrend"
    return {
        "schema_version": "structural_priority.v1",
        "present": present,
        "long_points": long_points,
        "short_points": short_points,
        "primary_side": primary_side,
        "strength": strength,
        "priority_label": priority_label,
        "weighting": {"4h": 0.75, "1h": 0.25, "4h_max": 53, "1h_max": 12},
        "components": {
            "4h": {"long": long_4h, "short": short_4h, "long_codes": long_4h_codes, "short_codes": short_4h_codes},
            "1h": {"long": long_1h, "short": short_1h, "long_codes": long_1h_codes, "short_codes": short_1h_codes},
        },
        "turning_watch": turning,
        "alignment_state": alignment,
        "tactical_context": {"primary_side": action_side, "primary_action_class": execution.get("primary_action_class", "")},
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
    }
