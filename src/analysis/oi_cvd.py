from __future__ import annotations

from typing import Any


def _price_trend(df_close: list[float]) -> str:
    if len(df_close) < 2:
        return "flat"
    if df_close[-1] > df_close[0]:
        return "up"
    if df_close[-1] < df_close[0]:
        return "down"
    return "flat"


def analyze_oi_cvd(
    *,
    oi_value: float | None,
    oi_change_pct: float | None,
    oi_trend_values: list[float] | None,
    cvd_series: list[float] | None,
    price_series: list[float],
) -> dict[str, Any]:
    price_trend = _price_trend(price_series[-5:])
    cvd_value = None if not cvd_series else round(float(cvd_series[-1]), 4)
    cvd_slope = None
    cvd_trend = "flat"
    if cvd_series and len(cvd_series) >= 2:
        cvd_slope = round(float(cvd_series[-1] - cvd_series[0]), 4)
        if cvd_slope > 0:
            cvd_trend = "up"
        elif cvd_slope < 0:
            cvd_trend = "down"

    divergence = "none"
    if price_trend == "up" and cvd_trend == "down":
        divergence = "bearish"
    elif price_trend == "down" and cvd_trend == "up":
        divergence = "bullish"

    oi_state = "unknown"
    if oi_change_pct is not None:
        if price_trend == "up" and oi_change_pct > 0:
            oi_state = "trend_supported_up"
        elif price_trend == "up" and oi_change_pct < 0:
            oi_state = "short_cover_risk"
        elif price_trend == "down" and oi_change_pct > 0:
            oi_state = "trend_supported_down"
        elif price_trend == "down" and oi_change_pct < 0:
            oi_state = "long_flush_exhaustion"

    return {
        "oi_value": round(float(oi_value), 4) if oi_value is not None else None,
        "oi_change_pct": round(float(oi_change_pct), 2) if oi_change_pct is not None else None,
        "oi_state": oi_state,
        "oi_trend_values": oi_trend_values[-5:] if oi_trend_values else None,
        "cvd_value": cvd_value,
        "cvd_slope": cvd_slope,
        "cvd_price_divergence": divergence,
        "cvd_trend": cvd_trend,
    }
