from __future__ import annotations


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def assemble_result_flags(
    *,
    bias: str,
    score_no_trade_flags: list[str],
    score_warning_flags: list[str],
    long_setup_flags: list[str],
    short_setup_flags: list[str],
    position_risk_flags: list[str],
    critical_zone: bool,
) -> dict[str, list[str]]:
    primary_setup_flags: list[str] = []
    if bias == "long":
        primary_setup_flags = long_setup_flags
    elif bias == "short":
        primary_setup_flags = short_setup_flags

    warning_flags = list(score_warning_flags)
    if critical_zone:
        warning_flags.append("Critical_zone_warning")

    return {
        "no_trade_flags": _dedupe(list(score_no_trade_flags) + list(primary_setup_flags)),
        "warning_flags": _dedupe(warning_flags),
        "risk_flags": _dedupe(list(position_risk_flags)),
    }
