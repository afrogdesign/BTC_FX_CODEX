from __future__ import annotations

from typing import Any

from src.presentation.sanitize import ADVICE_VARIANT, EVALUATION_TRACE_VERSION, PROMPT_VARIANT, SUMMARY_VARIANT


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _round_optional(value: Any, digits: int = 2) -> float | None:
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _trigger_reason_codes(result: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    bias = str(result.get("bias", "")).lower()
    status = str(result.get("primary_setup_status", "")).lower()
    reason_code = str(result.get("primary_setup_reason", "")).strip()
    volume_ratio = float(result.get("volume_ratio", 0.0) or 0.0)
    trigger_ratio = float(result.get("trigger_volume_ratio_threshold", 0.0) or 0.0)
    signal_15m = str(result.get("signals_15m", "")).lower()

    if status == "ready":
        reasons.append("setup_ready")
    elif status == "watch":
        reasons.append("setup_watch")
    elif status == "invalid":
        reasons.append("setup_invalid")

    if reason_code:
        reasons.append(reason_code)

    if trigger_ratio > 0 and volume_ratio >= trigger_ratio:
        reasons.append("volume_ready")
    else:
        reasons.append("volume_missing")

    if bias == "long" and result.get("breakout_up"):
        reasons.append("breakout_ready")
    elif bias == "short" and result.get("breakout_down"):
        reasons.append("breakout_ready")
    else:
        reasons.append("breakout_missing")

    if bias in {"long", "short"} and signal_15m == bias:
        reasons.append("tf15m_bias_match")
    elif signal_15m == "wait":
        reasons.append("tf15m_wait")
    else:
        reasons.append("tf15m_bias_mismatch")

    unique: list[str] = []
    seen: set[str] = set()
    for reason in reasons:
        if reason in seen:
            continue
        seen.add(reason)
        unique.append(reason)
    return unique


def _trigger_quality_score(result: dict[str, Any]) -> float:
    status = str(result.get("primary_setup_status", "")).lower()
    score = 15.0
    if status == "ready":
        score = 82.0
    elif status == "watch":
        score = 48.0
    elif status == "invalid":
        score = 18.0

    volume_ratio = float(result.get("volume_ratio", 0.0) or 0.0)
    trigger_ratio = float(result.get("trigger_volume_ratio_threshold", 0.0) or 0.0)
    if trigger_ratio > 0 and volume_ratio >= trigger_ratio:
        score += 8.0
    else:
        score -= 6.0

    bias = str(result.get("bias", "")).lower()
    signal_15m = str(result.get("signals_15m", "")).lower()
    if bias in {"long", "short"} and signal_15m == bias:
        score += 6.0
    elif signal_15m == "wait":
        score -= 2.0
    else:
        score -= 8.0

    if bias == "long" and result.get("breakout_up"):
        score += 6.0
    elif bias == "short" and result.get("breakout_down"):
        score += 6.0

    return round(_clamp(score), 2)


def build_evaluation_trace(
    *,
    result: dict[str, Any],
    score_info: dict[str, Any],
    position_risk: dict[str, Any],
    confidence_details: dict[str, Any],
    display_context: dict[str, Any],
) -> dict[str, Any]:
    risk_component_scores = {
        key: _round_optional(value, 4)
        for key, value in (position_risk.get("risk_breakdown") or {}).items()
    }
    trace = {
        "evaluation_trace_version": EVALUATION_TRACE_VERSION,
        "direction_score_shadow": _round_optional(score_info.get("direction_score_shadow")),
        "activity_score_shadow": _round_optional(score_info.get("activity_score_shadow")),
        "entry_quality_score_shadow": _round_optional(score_info.get("entry_quality_score_shadow")),
        "trigger_quality_score_shadow": _trigger_quality_score(result),
        "risk_component_scores": risk_component_scores,
        "confidence_components": confidence_details.get("confidence_components", []),
        "confidence_direction_shadow": _round_optional(confidence_details.get("confidence_direction_shadow")),
        "confidence_execution_shadow": _round_optional(confidence_details.get("confidence_execution_shadow")),
        "confidence_wait_shadow": _round_optional(confidence_details.get("confidence_wait_shadow")),
        "trigger_reason_codes": _trigger_reason_codes(result),
        "setup_decision_reason_codes": [
            code
            for code in [
                str(result.get("primary_setup_reason", "")).strip(),
                *[str(code).strip() for code in ((result.get("long_setup") or {}).get("invalid_reason_codes", []))],
                *[str(code).strip() for code in ((result.get("short_setup") or {}).get("invalid_reason_codes", []))],
            ]
            if code
        ],
        "display_label_mapping": {
            "direction_label": display_context.get("direction_label", ""),
            "action_label": display_context.get("action_label", ""),
            "entry_quality_label": display_context.get("entry_quality_label", ""),
            "setup_status_label": display_context.get("setup_status_label", ""),
            "confidence_metric_labels": display_context.get("confidence_metric_labels", {}),
        },
        "blocking_reason_codes": [str(code).strip() for code in (result.get("no_trade_flags") or []) if str(code).strip()],
        "warning_reason_codes": [str(code).strip() for code in (result.get("warning_flags") or []) if str(code).strip()],
        "position_risk_flags": [str(code).strip() for code in (result.get("risk_flags") or []) if str(code).strip()],
        "summary_variant": SUMMARY_VARIANT,
        "advice_variant": ADVICE_VARIANT,
        "prompt_variant": PROMPT_VARIANT,
    }
    return trace
