from __future__ import annotations

from typing import Any

from src.analysis.fallback_context import build_fallback_context
from src.analysis.patterns import analyze_chart_patterns
from src.analysis.sr_context import build_sr_context
from src.analysis.volume_structure import analyze_volume_structure


def build_chart_pattern_shadow(
    *,
    price: float,
    atr: float,
    df_15m: Any,
    swings_15m: dict[str, list[dict[str, Any]]],
    breakout_up: bool,
    breakout_down: bool,
    support_zones_all: list[dict[str, Any]],
    resistance_zones_all: list[dict[str, Any]],
    raw_missing_fields: list[str],
    cfg: Any,
) -> dict[str, Any]:
    volume_structure = analyze_volume_structure(df_15m, cfg)
    sr_context = build_sr_context(price, support_zones_all, resistance_zones_all)
    pattern_context = analyze_chart_patterns(
        price=price,
        atr=atr,
        df_15m=df_15m,
        swings_15m=swings_15m,
        breakout_up=breakout_up,
        breakout_down=breakout_down,
        volume_structure=volume_structure,
        sr_context=sr_context,
        cfg=cfg,
    )
    fallback_context = build_fallback_context(raw_missing_fields)
    return {
        "chart_pattern_shadow": {
            "version": "v1",
            "pattern_context": pattern_context,
            "window_context": {
                "macro_window": {"timeframe": "4h", "bars": int(getattr(cfg, "WINDOW_MACRO_4H_BARS", 240))},
                "structure_window": {"timeframe": "1h", "bars": int(getattr(cfg, "WINDOW_STRUCTURE_1H_BARS", 120))},
                "trigger_window": {"timeframe": "15m", "bars": int(getattr(cfg, "WINDOW_TRIGGER_15M_BARS", 24))},
                "micro_window": {"timeframe": "15m", "bars": int(getattr(cfg, "WINDOW_MICRO_15M_BARS", 96))},
            },
            "volume_structure": volume_structure,
            "sr_context": sr_context,
            "fallback_context": fallback_context,
        }
    }
