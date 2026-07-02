from __future__ import annotations

from typing import Any


_SAFETY_BOUNDARY = "report-only / not FORMAL_GO / no automatic order / human decides manually"


def _flag_set(result: dict[str, Any], key: str) -> set[str]:
    return {str(flag).strip() for flag in result.get(key, []) if str(flag).strip()}


def _has_any(flags: set[str], candidates: tuple[str, ...]) -> bool:
    return any(candidate in flags for candidate in candidates)


def _candidate_payload(result: dict[str, Any]) -> dict[str, Any]:
    momentum_flags = _flag_set(result, "momentum_confirmation_flags")
    inversion_flags = _flag_set(result, "breakout_inversion_flags")
    warning_flags = _flag_set(result, "warning_flags")
    combined = momentum_flags | inversion_flags | warning_flags

    upside_trigger = _has_any(
        combined,
        (
            "upside_momentum_confirmed",
            "upside_breakout_follow_watch",
            "upside_macd_confirmed",
        ),
    )
    upside_risk = _has_any(
        combined,
        (
            "short_countertrend_risk",
            "short_invalidation_watch",
            "missed_upside_breakout_watch",
            "macd_upside_countertrend_risk",
        ),
    )
    downside_trigger = _has_any(
        combined,
        (
            "downside_momentum_confirmed",
            "downside_breakdown_follow_watch",
            "downside_macd_confirmed",
        ),
    )
    downside_risk = _has_any(
        combined,
        (
            "long_countertrend_risk",
            "long_invalidation_watch",
            "missed_downside_breakdown_watch",
            "macd_downside_countertrend_risk",
        ),
    )

    reason_codes: list[str] = []
    side = "none"
    severity = "watch"

    if upside_trigger and upside_risk:
        side = "upside" if not downside_trigger or not downside_risk else "both"
        reason_codes.extend(
            code
            for code in (
                "upside_momentum_confirmed",
                "upside_breakout_follow_watch",
                "upside_macd_confirmed",
                "short_countertrend_risk",
                "short_invalidation_watch",
                "missed_upside_breakout_watch",
                "macd_upside_countertrend_risk",
            )
            if code in combined
        )
    if downside_trigger and downside_risk:
        if side == "upside":
            side = "both"
        elif side == "none":
            side = "downside"
        reason_codes.extend(
            code
            for code in (
                "downside_momentum_confirmed",
                "downside_breakdown_follow_watch",
                "downside_macd_confirmed",
                "long_countertrend_risk",
                "long_invalidation_watch",
                "missed_downside_breakdown_watch",
                "macd_downside_countertrend_risk",
            )
            if code in combined
        )

    reason_codes = sorted(set(reason_codes))

    if side == "both":
        severity = "warning"
    elif side in {"upside", "downside"} and reason_codes:
        severity = "watch"

    if side == "none":
        return {
            "status": "none",
            "side": "none",
            "severity": "watch",
            "reason_codes": [],
            "human_summary": "15分足の早期注意候補はまだ出ていません。",
            "safety_boundary": _SAFETY_BOUNDARY,
            "real_mail_sent": False,
            "automatic_order": False,
        }

    if side == "both":
        human_summary = (
            "上抜けと下抜けの両方で早期注意候補が出ています。"
            " どちらも報告のみで、15分足の維持を人間が確認します。"
        )
    elif side == "upside":
        human_summary = (
            "上抜け初動の可能性があります。ショート方向の逆風を優先して、"
            "15分足で上に維持できるか確認します。"
        )
    else:
        human_summary = (
            "下抜け初動の可能性があります。ロング方向の逆風を優先して、"
            "15分足で下に維持できるか確認します。"
        )

    if "upside_macd_confirmed" in reason_codes:
        human_summary += " MACDは上方向の勢いを補強します。"
    if "downside_macd_confirmed" in reason_codes:
        human_summary += " MACDは下方向の勢いを補強します。"

    return {
        "status": "candidate",
        "side": side,
        "severity": severity,
        "reason_codes": reason_codes,
        "human_summary": human_summary,
        "safety_boundary": _SAFETY_BOUNDARY,
        "real_mail_sent": False,
        "automatic_order": False,
    }


def build_intraperiod_breakout_alert_candidate(
    result: dict[str, Any],
    last_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = _candidate_payload(result)
    if last_result:
        previous = _candidate_payload(last_result)
        if current["status"] == "candidate" and previous["status"] != "candidate":
            current["severity"] = "warning"
    return current
