from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


CSV_HEADER = [
    "signal_id",
    "timestamp_utc",
    "timestamp_jst",
    "was_notified",
    "notified_at_utc",
    "current_price",
    "bias",
    "phase",
    "market_regime",
    "transition_direction",
    "long_score",
    "short_score",
    "long_display_score",
    "short_display_score",
    "long_raw_score",
    "short_raw_score",
    "score_gap",
    "score_factor_breakdown_long",
    "score_factor_breakdown_short",
    "top_positive_factors",
    "top_negative_factors",
    "confidence",
    "agreement_with_machine",
    "prelabel",
    "prelabel_primary_reason",
    "location_risk",
    "primary_setup_side",
    "primary_setup_status",
    "primary_setup_reason",
    "invalid_reason",
    "primary_entry_mid",
    "primary_stop_loss",
    "primary_tp1",
    "primary_tp2",
    "risk_percent_applied",
    "planned_risk_usd",
    "position_size_usd",
    "max_size_capped",
    "size_reduction_reasons",
    "tp1_price",
    "tp2_price",
    "breakeven_after_tp1",
    "trail_atr_multiplier",
    "timeout_hours",
    "exit_rule_version",
    "funding_rate",
    "funding_rate_raw",
    "funding_rate_pct",
    "funding_rate_label",
    "atr_15m_value",
    "atr_ratio",
    "volume_ratio",
    "rr_estimate",
    "oi_value",
    "oi_change_pct",
    "cvd_value",
    "cvd_slope",
    "cvd_price_divergence",
    "liquidity_above",
    "liquidity_below",
    "largest_liquidation_price",
    "orderbook_bias",
    "long_status",
    "short_status",
    "long_rr",
    "short_rr",
    "warning_flags",
    "risk_flags",
    "signal_tier",
    "signal_badge",
    "signal_tier_reason_codes",
    "ai_decision",
    "ai_confidence",
    "data_quality_flag",
    "data_missing_fields",
    "nearest_support_low",
    "nearest_support_high",
    "nearest_support_distance",
    "nearest_resistance_low",
    "nearest_resistance_high",
    "nearest_resistance_distance",
    "summary_subject",
    "no_trade_flags",
    "notify_reason_codes",
    "suppress_reason_codes",
    "reason_for_notification",
]


def _first_zone(zones: list[dict[str, Any]] | None) -> dict[str, Any]:
    if not zones:
        return {}
    first = zones[0]
    return first if isinstance(first, dict) else {}


def _row_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    support_zone = _first_zone(payload.get("support_zones"))
    resistance_zone = _first_zone(payload.get("resistance_zones"))
    json_dumps = lambda value: json.dumps(value, ensure_ascii=False) if value not in (None, "", []) else ""
    return {
        "signal_id": payload.get("signal_id"),
        "timestamp_utc": payload.get("timestamp_utc"),
        "timestamp_jst": payload.get("timestamp_jst"),
        "was_notified": payload.get("was_notified"),
        "notified_at_utc": payload.get("notified_at_utc"),
        "current_price": payload.get("current_price"),
        "bias": payload.get("bias"),
        "phase": payload.get("phase"),
        "market_regime": payload.get("market_regime"),
        "transition_direction": payload.get("transition_direction"),
        "long_score": payload.get("long_score"),
        "short_score": payload.get("short_score"),
        "long_display_score": payload.get("long_display_score"),
        "short_display_score": payload.get("short_display_score"),
        "long_raw_score": payload.get("long_raw_score"),
        "short_raw_score": payload.get("short_raw_score"),
        "score_gap": payload.get("score_gap"),
        "score_factor_breakdown_long": json_dumps(payload.get("score_factor_breakdown_long")),
        "score_factor_breakdown_short": json_dumps(payload.get("score_factor_breakdown_short")),
        "top_positive_factors": json_dumps(payload.get("top_positive_factors")),
        "top_negative_factors": json_dumps(payload.get("top_negative_factors")),
        "confidence": payload.get("confidence"),
        "agreement_with_machine": payload.get("agreement_with_machine"),
        "prelabel": payload.get("prelabel"),
        "prelabel_primary_reason": payload.get("prelabel_primary_reason"),
        "location_risk": payload.get("location_risk"),
        "primary_setup_side": payload.get("primary_setup_side"),
        "primary_setup_status": payload.get("primary_setup_status"),
        "primary_setup_reason": payload.get("primary_setup_reason"),
        "invalid_reason": payload.get("invalid_reason"),
        "primary_entry_mid": payload.get("primary_entry_mid"),
        "primary_stop_loss": payload.get("primary_stop_loss"),
        "primary_tp1": payload.get("primary_tp1"),
        "primary_tp2": payload.get("primary_tp2"),
        "risk_percent_applied": payload.get("risk_percent_applied"),
        "planned_risk_usd": payload.get("planned_risk_usd"),
        "position_size_usd": payload.get("position_size_usd"),
        "max_size_capped": payload.get("max_size_capped"),
        "size_reduction_reasons": json_dumps(payload.get("size_reduction_reasons")),
        "tp1_price": payload.get("tp1_price"),
        "tp2_price": payload.get("tp2_price"),
        "breakeven_after_tp1": payload.get("breakeven_after_tp1"),
        "trail_atr_multiplier": payload.get("trail_atr_multiplier"),
        "timeout_hours": payload.get("timeout_hours"),
        "exit_rule_version": payload.get("exit_rule_version"),
        "funding_rate": payload.get("funding_rate"),
        "funding_rate_raw": payload.get("funding_rate_raw"),
        "funding_rate_pct": payload.get("funding_rate_pct"),
        "funding_rate_label": payload.get("funding_rate_label"),
        "atr_15m_value": payload.get("atr_15m_value"),
        "atr_ratio": payload.get("atr_ratio"),
        "volume_ratio": payload.get("volume_ratio"),
        "rr_estimate": payload.get("rr_estimate"),
        "oi_value": payload.get("oi_value"),
        "oi_change_pct": payload.get("oi_change_pct"),
        "cvd_value": payload.get("cvd_value"),
        "cvd_slope": payload.get("cvd_slope"),
        "cvd_price_divergence": payload.get("cvd_price_divergence"),
        "liquidity_above": payload.get("liquidity_above"),
        "liquidity_below": payload.get("liquidity_below"),
        "largest_liquidation_price": payload.get("largest_liquidation_price"),
        "orderbook_bias": payload.get("orderbook_bias"),
        "long_status": (payload.get("long_setup") or {}).get("status"),
        "short_status": (payload.get("short_setup") or {}).get("status"),
        "long_rr": (payload.get("long_setup") or {}).get("rr_estimate"),
        "short_rr": (payload.get("short_setup") or {}).get("rr_estimate"),
        "warning_flags": ",".join(payload.get("warning_flags", [])),
        "risk_flags": ",".join(payload.get("risk_flags", [])),
        "signal_tier": payload.get("signal_tier"),
        "signal_badge": payload.get("signal_badge"),
        "signal_tier_reason_codes": json_dumps(payload.get("signal_tier_reason_codes")),
        "ai_decision": payload.get("ai_decision"),
        "ai_confidence": payload.get("ai_confidence"),
        "data_quality_flag": payload.get("data_quality_flag"),
        "data_missing_fields": json_dumps(payload.get("data_missing_fields")),
        "nearest_support_low": support_zone.get("low"),
        "nearest_support_high": support_zone.get("high"),
        "nearest_support_distance": support_zone.get("distance_from_price"),
        "nearest_resistance_low": resistance_zone.get("low"),
        "nearest_resistance_high": resistance_zone.get("high"),
        "nearest_resistance_distance": resistance_zone.get("distance_from_price"),
        "summary_subject": payload.get("summary_subject"),
        "no_trade_flags": ",".join(payload.get("no_trade_flags", [])),
        "notify_reason_codes": json_dumps(payload.get("notify_reason_codes")),
        "suppress_reason_codes": json_dumps(payload.get("suppress_reason_codes")),
        "reason_for_notification": ",".join(payload.get("reason_for_notification", [])),
    }


def _load_existing_rows(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    if not path.exists():
        return [], []
    with path.open("r", newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        return list(reader.fieldnames or []), list(reader)


def append_trade_log(base_dir: Path, payload: dict[str, Any]) -> Path:
    path = base_dir / "logs" / "csv" / "trades.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    current_header, existing_rows = _load_existing_rows(path)
    row = _row_from_payload(payload)

    needs_rewrite = current_header and current_header != CSV_HEADER
    mode = "a"
    if not path.exists() or needs_rewrite:
        mode = "w"

    with path.open(mode, newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=CSV_HEADER)
        if mode == "w":
            writer.writeheader()
            for existing in existing_rows:
                writer.writerow({field: existing.get(field, "") for field in CSV_HEADER})
        writer.writerow(row)
    return path
