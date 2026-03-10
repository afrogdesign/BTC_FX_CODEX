from __future__ import annotations


def funding_rate_raw_to_pct(funding_rate_raw: float) -> float:
    return float(funding_rate_raw) * 100.0


def format_funding_pct(funding_rate_pct: float, digits: int = 4) -> str:
    return f"{float(funding_rate_pct):+.{digits}f}%"


def funding_rate_label(
    *,
    funding_rate_pct: float,
    long_warning_pct: float,
    long_prohibited_pct: float,
    short_warning_pct: float,
    short_prohibited_pct: float,
) -> str:
    if funding_rate_pct >= long_prohibited_pct:
        return "ロング過熱"
    if funding_rate_pct >= long_warning_pct:
        return "ロングやや過熱"
    if funding_rate_pct <= short_prohibited_pct:
        return "ショート過熱"
    if funding_rate_pct <= short_warning_pct:
        return "ショートやや過熱"
    return "ほぼ中立"

