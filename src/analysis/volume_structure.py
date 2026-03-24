from __future__ import annotations

from typing import Any


def analyze_volume_structure(df_15m: Any, cfg: Any) -> dict[str, Any]:
    volumes = [float(value) for value in df_15m["volume"].tolist()]
    if not volumes:
        return {
            "contraction_score": 0.0,
            "expansion_score": 1.0,
            "breakout_volume_confirmed": False,
            "volume_regime": "neutral",
            "reference_leg_bars": 0,
            "consolidation_bars": 0,
        }

    trigger_bars = max(int(getattr(cfg, "WINDOW_TRIGGER_15M_BARS", 24)), 1)
    consolidation_bars = min(max(int(getattr(cfg, "PATTERN_CONSOLIDATION_BARS_MAX", 20)), 1), len(volumes))
    consolidation = volumes[-consolidation_bars:]
    reference = volumes[-(consolidation_bars + trigger_bars) : -consolidation_bars] if len(volumes) > consolidation_bars else []
    if not reference:
        reference = volumes[:-1] or volumes

    consolidation_avg = sum(consolidation) / len(consolidation)
    reference_avg = sum(reference) / len(reference) if reference else consolidation_avg
    contraction_ratio = consolidation_avg / reference_avg if reference_avg > 0 else 1.0
    expansion_ratio = volumes[-1] / consolidation_avg if consolidation_avg > 0 else 1.0

    contraction_score = max(0.0, min(1.0, 1.0 - contraction_ratio))
    expansion_score = round(expansion_ratio, 4)
    breakout_volume_confirmed = expansion_ratio >= float(getattr(cfg, "PATTERN_EXPANSION_RATIO_MIN", 1.15))

    if contraction_ratio <= float(getattr(cfg, "PATTERN_CONTRACTION_RATIO_MAX", 0.85)):
        regime = "contracting"
    elif expansion_ratio >= float(getattr(cfg, "PATTERN_EXPANSION_RATIO_MIN", 1.15)):
        regime = "expanding"
    else:
        regime = "neutral"

    return {
        "contraction_score": round(contraction_score, 4),
        "expansion_score": expansion_score,
        "breakout_volume_confirmed": breakout_volume_confirmed,
        "volume_regime": regime,
        "reference_leg_bars": len(reference),
        "consolidation_bars": consolidation_bars,
    }
