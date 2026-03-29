from __future__ import annotations

from typing import Any


_MAJOR_WARNING_FLAGS = {
    "Funding_prohibited_long",
    "Funding_prohibited_short",
    "ATR_extreme",
    "Critical_zone_warning",
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _component(code: str, label: str, group: str, delta: float, value: Any) -> dict[str, Any]:
    return {
        "code": code,
        "label": label,
        "group": group,
        "delta": round(float(delta), 2),
        "value": value,
    }


def count_agreeing_timeframes(signals_4h: str, signals_1h: str, signals_15m: str, bias: str) -> int:
    return sum(1 for signal in (signals_4h, signals_1h, signals_15m) if signal == bias)


def compute_machine_agreement(
    *,
    bias: str,
    market_regime: str,
    ema_alignment_4h: str,
    price: float,
    support_zones: list[dict[str, Any]],
    resistance_zones: list[dict[str, Any]],
    volume_ratio: float,
    funding_rate: float,
) -> str:
    if bias not in {"long", "short"}:
        return "partial"

    matched = 0

    if bias == "long" and market_regime in {"uptrend", "transition"}:
        matched += 1
    elif bias == "short" and market_regime in {"downtrend", "transition"}:
        matched += 1

    if bias == "long" and ema_alignment_4h == "bullish":
        matched += 1
    elif bias == "short" and ema_alignment_4h == "bearish":
        matched += 1

    if bias == "long":
        above_support = any(float(z["high"]) <= price for z in support_zones) or any(
            float(z["low"]) <= price <= float(z["high"]) for z in support_zones
        )
        below_resistance = any(float(z["low"]) >= price for z in resistance_zones)
        if above_support and below_resistance:
            matched += 1
    else:
        below_resistance = any(float(z["low"]) >= price for z in resistance_zones) or any(
            float(z["low"]) <= price <= float(z["high"]) for z in resistance_zones
        )
        above_support = any(float(z["high"]) <= price for z in support_zones)
        if below_resistance and above_support:
            matched += 1

    if bias == "long":
        if volume_ratio >= 1.0 and funding_rate <= 0.05:
            matched += 1
    else:
        if volume_ratio >= 1.0 and funding_rate >= -0.03:
            matched += 1

    if matched >= 3:
        return "agree"
    if matched == 2:
        return "partial"
    return "disagree"


def compute_confidence_details(inputs: dict[str, Any], cfg: Any) -> dict[str, Any]:
    bias = inputs["bias"]
    long_display = int(inputs["long_display_score"])
    short_display = int(inputs["short_display_score"])
    signals_4h = inputs["signals_4h"]
    signals_1h = inputs["signals_1h"]
    signals_15m = inputs["signals_15m"]
    regime = inputs["market_regime"]
    phase = inputs["phase"]
    rr_estimate = float(inputs["rr_estimate"])
    opposite_gap_atr = float(inputs["opposite_gap_atr"])
    critical_zone = bool(inputs["critical_zone"])
    score_warning_flags = [str(flag) for flag in inputs.get("score_warning_flags", [])]
    position_risk_flags = [str(flag) for flag in inputs.get("position_risk_flags", [])]
    prelabel = str(inputs.get("prelabel", "")).upper()

    components: list[dict[str, Any]] = []
    direction_value = 0.0
    execution_value = 0.0
    wait_pressure = 0.0

    if bias == "long":
        base_confidence = float(long_display)
    elif bias == "short":
        base_confidence = float(short_display)
    else:
        base_confidence = min(50.0, max(long_display, short_display) * 0.6)
    confidence = base_confidence
    components.append(_component("base_selected_score", "選択方向の基礎点", "direction", base_confidence, base_confidence))
    direction_value += base_confidence

    agreeing = count_agreeing_timeframes(signals_4h, signals_1h, signals_15m, bias)
    timeframe_delta = 15.0 if agreeing >= 3 else 8.0 if agreeing == 2 else 0.0
    confidence += timeframe_delta
    direction_value += timeframe_delta
    components.append(_component("timeframe_agreement", "時間軸の一致", "direction", timeframe_delta, agreeing))

    regime_delta = 0.0
    if regime in {"uptrend", "downtrend"}:
        regime_delta = 10.0
    elif regime == "range":
        regime_delta = -5.0
    elif regime == "volatile":
        regime_delta = -10.0
    confidence += regime_delta
    direction_value += regime_delta
    if regime_delta < 0:
        wait_pressure += abs(regime_delta)
    components.append(_component("regime", "相場環境", "direction", regime_delta, regime))

    phase_delta = 0.0
    if phase == "trend_following":
        phase_delta = 5.0
    elif phase == "breakout":
        phase_delta = 6.0
    elif phase == "pullback":
        phase_delta = 3.0
    elif phase == "range":
        phase_delta = -5.0
    elif phase == "reversal_risk":
        phase_delta = -10.0
    confidence += phase_delta
    direction_value += phase_delta
    if phase_delta < 0:
        wait_pressure += abs(phase_delta)
    components.append(_component("phase", "局面", "direction", phase_delta, phase))

    rr_delta = 0.0
    if rr_estimate >= 2.0:
        rr_delta = 10.0
    elif rr_estimate >= 1.5:
        rr_delta = 5.0
    elif rr_estimate < 1.1:
        rr_delta = -18.0
    elif rr_estimate < 1.2:
        rr_delta = -10.0
    elif rr_estimate < 1.3:
        rr_delta = -5.0
    confidence += rr_delta
    execution_value += rr_delta
    if rr_delta < 0:
        wait_pressure += abs(rr_delta)
    components.append(_component("rr", "RR 条件", "execution", rr_delta, rr_estimate))

    gap_delta = 5.0 if opposite_gap_atr >= 1.5 else -5.0 if opposite_gap_atr < 0.8 else 0.0
    confidence += gap_delta
    execution_value += gap_delta
    if gap_delta < 0:
        wait_pressure += abs(gap_delta)
    components.append(_component("opposite_gap", "逆側ゾーンまでの余白", "execution", gap_delta, opposite_gap_atr))

    critical_delta = -10.0 if critical_zone else 0.0
    confidence += critical_delta
    execution_value += critical_delta
    if critical_delta < 0:
        wait_pressure += abs(critical_delta)
    components.append(_component("critical_zone_penalty", "重要価格帯ペナルティ", "wait", critical_delta, critical_zone))

    warning_penalty = 0.0
    for flag in score_warning_flags:
        if flag == "Critical_zone_warning" and critical_zone:
            continue
        warning_penalty += 6.0 if flag in _MAJOR_WARNING_FLAGS else 3.0
    warning_penalty = min(warning_penalty, 18.0)
    if warning_penalty:
        confidence -= warning_penalty
        execution_value -= warning_penalty
        wait_pressure += warning_penalty
    components.append(_component("warning_penalty", "警戒フラグの減点", "wait", -warning_penalty, score_warning_flags))

    position_penalty = 3.0 * len(position_risk_flags)
    if position_penalty:
        confidence -= position_penalty
        execution_value -= position_penalty
        wait_pressure += position_penalty
    components.append(_component("position_risk_penalty", "位置リスクの減点", "wait", -position_penalty, position_risk_flags))

    prelabel_penalty = 0.0
    if prelabel == "RISKY_ENTRY":
        prelabel_penalty = 4.0
    elif prelabel == "SWEEP_WAIT":
        prelabel_penalty = 8.0
    elif prelabel == "NO_TRADE_CANDIDATE":
        prelabel_penalty = 12.0
    if prelabel_penalty:
        confidence -= prelabel_penalty
        execution_value -= prelabel_penalty
        wait_pressure += prelabel_penalty
    components.append(_component("prelabel_penalty", "位置評価の減点", "wait", -prelabel_penalty, prelabel))

    raw_confidence = round(confidence, 2)
    final_confidence = int(round(_clamp(confidence, 0, 100)))
    direction_shadow = round(_clamp(direction_value, 0, 100), 2)
    execution_shadow = round(_clamp(50.0 + execution_value, 0, 100), 2)
    wait_shadow = round(_clamp(wait_pressure * 1.6, 0, 100), 2)

    return {
        "confidence": final_confidence,
        "raw_confidence": raw_confidence,
        "confidence_direction_shadow": direction_shadow,
        "confidence_execution_shadow": execution_shadow,
        "confidence_wait_shadow": wait_shadow,
        "confidence_components": components,
    }


def compute_confidence(inputs: dict[str, Any], cfg: Any) -> int:
    return int(compute_confidence_details(inputs, cfg)["confidence"])


def confidence_gate_ok(bias: str, confidence: int, cfg: Any) -> bool:
    if bias == "long":
        return confidence >= cfg.CONFIDENCE_LONG_MIN
    if bias == "short":
        return confidence >= cfg.CONFIDENCE_SHORT_MIN
    return False
