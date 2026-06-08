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
    "market_map_primary_state",
    "market_map_flags",
    "nearest_major_support",
    "nearest_major_resistance",
    "active_level_role",
    "level_flip_state",
    "failed_breakout_state",
    "trend_flip_state",
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
    "raw_confidence",
    "confidence_direction_shadow",
    "confidence_execution_shadow",
    "confidence_wait_shadow",
    "agreement_with_machine",
    "prelabel",
    "prelabel_primary_reason",
    "location_risk",
    "primary_setup_side",
    "primary_setup_status",
    "primary_setup_reason",
    "execution_precision_action",
    "execution_precision_flags",
    "execution_precision_reason",
    "invalid_reason",
    "primary_entry_mid",
    "primary_stop_loss",
    "primary_tp1",
    "primary_tp2",
    "risk_percent_applied",
    "planned_risk_usd",
    "position_size_usd",
    "loss_streak_at_entry",
    "phase1_active",
    "phase1_activation_reason",
    "max_size_capped",
    "size_reduction_reasons",
    "tp1_price",
    "tp2_price",
    "breakeven_after_tp1",
    "trail_atr_multiplier",
    "timeout_hours",
    "exit_rule_version",
    "shadow_tp1_price",
    "shadow_tp2_price",
    "shadow_breakeven_after_tp1",
    "shadow_trail_atr_multiplier",
    "shadow_timeout_hours",
    "shadow_exit_rule_version",
    "trade_execution_gate",
    "trade_execution_blockers",
    "phase1_observation_gate",
    "phase1_observation_type",
    "phase1_observation_reasons",
    "phase1b_lite_gate",
    "phase1b_lite_type",
    "phase1b_lite_reasons",
    "opportunity_gate",
    "opportunity_type",
    "opportunity_reasons",
    "paper_order_status",
    "active_plan_version",
    "active_primary_action",
    "active_subject_label",
    "active_headline",
    "active_market_entry_long",
    "active_market_entry_short",
    "active_limit_retest_long",
    "active_limit_retest_short",
    "active_breakout_follow_long",
    "active_breakout_follow_short",
    "active_countertrend_scalp_long",
    "active_countertrend_scalp_short",
    "active_position_management_long",
    "active_position_management_short",
    "active_trade_plan_json",
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
    "ai_audit_status",
    "ai_audit_verdict",
    "ai_audit_agreement",
    "ai_audit_reason",
    "ai_audit_unique_risks",
    "ai_audit_next_review_focus",
    "data_quality_flag",
    "data_missing_fields",
    "nearest_support_low",
    "nearest_support_high",
    "nearest_support_distance",
    "nearest_resistance_low",
    "nearest_resistance_high",
    "nearest_resistance_distance",
    "summary_subject",
    "summary_variant",
    "advice_variant",
    "prompt_variant",
    "evaluation_trace_version",
    "no_trade_flags",
    "notify_reason_codes",
    "suppress_reason_codes",
    "reason_for_notification",
]


ACTIVE_PLAN_CANDIDATE_HEADER = [
    "candidate_id",
    "source_signal_id",
    "timestamp_jst",
    "active_primary_action",
    "candidate_type",
    "candidate_status",
    "side",
    "entry_mode",
    "entry_price",
    "entry_zone_low",
    "entry_zone_high",
    "stop_loss",
    "tp1",
    "tp2",
    "rr_current_tp1",
    "rr_current_tp2",
    "rr_zone_mid_tp1",
    "rr_zone_mid_tp2",
    "market_entry_status",
    "limit_entry_status",
    "counter_scalp_status",
    "breakout_status",
    "active_subject_label",
    "active_headline",
    "next_condition",
]


def _first_zone(zones: list[dict[str, Any]] | None) -> dict[str, Any]:
    if not zones:
        return {}
    first = zones[0]
    return first if isinstance(first, dict) else {}


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False) if value not in (None, "", []) else ""


def _active_plan_row_fields(payload: dict[str, Any]) -> dict[str, Any]:
    raw_active_plan = payload.get("active_trade_plan")
    active_plan = _dict_or_empty(raw_active_plan)
    notification_context = _dict_or_empty(payload.get("notification_context"))

    market_entry_now = _dict_or_empty(active_plan.get("market_entry_now"))
    limit_retest_entry = _dict_or_empty(active_plan.get("limit_retest_entry"))
    breakout_follow_entry = _dict_or_empty(active_plan.get("breakout_follow_entry"))
    countertrend_scalp_entry = _dict_or_empty(active_plan.get("countertrend_scalp_entry"))
    position_management = _dict_or_empty(active_plan.get("position_management"))

    return {
        "active_plan_version": active_plan.get("plan_version", ""),
        "active_primary_action": (
            payload.get("active_primary_action")
            or active_plan.get("primary_action")
            or ""
        ),
        "active_subject_label": notification_context.get("active_subject_label", ""),
        "active_headline": (
            payload.get("active_headline")
            or active_plan.get("headline")
            or ""
        ),
        "active_market_entry_long": market_entry_now.get("long", ""),
        "active_market_entry_short": market_entry_now.get("short", ""),
        "active_limit_retest_long": limit_retest_entry.get("long", ""),
        "active_limit_retest_short": limit_retest_entry.get("short", ""),
        "active_breakout_follow_long": breakout_follow_entry.get("long", ""),
        "active_breakout_follow_short": breakout_follow_entry.get("short", ""),
        "active_countertrend_scalp_long": countertrend_scalp_entry.get("long", ""),
        "active_countertrend_scalp_short": countertrend_scalp_entry.get("short", ""),
        "active_position_management_long": position_management.get("if_long_holding", ""),
        "active_position_management_short": position_management.get("if_short_holding", ""),
        "active_trade_plan_json": _json_dumps(raw_active_plan if isinstance(raw_active_plan, dict) else ""),
    }


def _active_plan_candidate_base_row(payload: dict[str, Any], side: str, side_plan: dict[str, Any]) -> dict[str, Any]:
    active_plan = _dict_or_empty(payload.get("active_trade_plan"))
    notification_context = _dict_or_empty(payload.get("notification_context"))
    source_signal_id = str(payload.get("signal_id", "")).strip() or "unknown_signal"
    active_primary_action = (
        str(payload.get("active_primary_action", "")).strip()
        or str(active_plan.get("primary_action", "")).strip()
    )
    active_headline = (
        str(payload.get("active_headline", "")).strip()
        or str(active_plan.get("headline", "")).strip()
    )
    active_subject_label = (
        str(payload.get("active_subject_label", "")).strip()
        or str(notification_context.get("active_subject_label", "")).strip()
    )
    return {
        "candidate_id": "",
        "source_signal_id": source_signal_id,
        "timestamp_jst": payload.get("timestamp_jst", ""),
        "active_primary_action": active_primary_action,
        "candidate_type": "",
        "candidate_status": "",
        "side": side,
        "entry_mode": "",
        "entry_price": "",
        "entry_zone_low": side_plan.get("entry_zone_low", ""),
        "entry_zone_high": side_plan.get("entry_zone_high", ""),
        "stop_loss": side_plan.get("stop_loss", ""),
        "tp1": side_plan.get("tp1", ""),
        "tp2": side_plan.get("tp2", ""),
        "rr_current_tp1": side_plan.get("rr_current_tp1", ""),
        "rr_current_tp2": side_plan.get("rr_current_tp2", ""),
        "rr_zone_mid_tp1": side_plan.get("rr_zone_mid_tp1", ""),
        "rr_zone_mid_tp2": side_plan.get("rr_zone_mid_tp2", ""),
        "market_entry_status": side_plan.get("market_entry_status", ""),
        "limit_entry_status": side_plan.get("limit_entry_status", ""),
        "counter_scalp_status": side_plan.get("counter_scalp_status", ""),
        "breakout_status": side_plan.get("breakout_status", ""),
        "active_subject_label": active_subject_label,
        "active_headline": active_headline,
        "next_condition": side_plan.get("next_condition", ""),
    }


def _active_plan_candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    active_plan = _dict_or_empty(payload.get("active_trade_plan"))
    side_plans = _dict_or_empty(active_plan.get("side_plans"))
    rows: list[dict[str, Any]] = []

    for side in ("long", "short"):
        side_plan = _dict_or_empty(side_plans.get(side))
        if not side_plan:
            continue

        base_row = _active_plan_candidate_base_row(payload, side, side_plan)
        directional_candidate_added = False
        is_primary_side = str(side_plan.get("bias_alignment", "")).strip() == "primary"
        is_counter_side = str(side_plan.get("bias_alignment", "")).strip() == "counter"

        if is_primary_side and str(side_plan.get("market_entry_status", "")).strip() == "allowed":
            row = dict(base_row)
            row["candidate_type"] = "market"
            row["candidate_status"] = "allowed"
            row["entry_mode"] = "market"
            row["entry_price"] = payload.get("current_price", side_plan.get("current_price", ""))
            row["candidate_id"] = f"{row['source_signal_id']}:{side}:market"
            rows.append(row)
            directional_candidate_added = True
        elif is_primary_side and str(side_plan.get("limit_entry_status", "")).strip() == "allowed":
            row = dict(base_row)
            row["candidate_type"] = "limit_retest"
            row["candidate_status"] = "allowed"
            row["entry_mode"] = "limit"
            row["entry_price"] = side_plan.get("entry_mid", "")
            row["candidate_id"] = f"{row['source_signal_id']}:{side}:limit_retest"
            rows.append(row)
            directional_candidate_added = True

        breakout_status = str(side_plan.get("breakout_status", "")).strip()
        if is_primary_side and not directional_candidate_added and breakout_status in {"armed", "watch"}:
            row = dict(base_row)
            row["candidate_type"] = "breakout_follow"
            row["candidate_status"] = breakout_status
            row["entry_mode"] = "breakout"
            row["entry_price"] = payload.get("current_price", side_plan.get("current_price", ""))
            row["candidate_id"] = f"{row['source_signal_id']}:{side}:breakout_follow"
            rows.append(row)

        if is_counter_side and str(side_plan.get("counter_scalp_status", "")).strip() == "conditional":
            row = dict(base_row)
            row["candidate_type"] = "counter_scalp"
            row["candidate_status"] = "conditional"
            row["entry_mode"] = "conditional"
            row["entry_price"] = payload.get("current_price", side_plan.get("current_price", ""))
            row["candidate_id"] = f"{row['source_signal_id']}:{side}:counter_scalp"
            rows.append(row)

    return rows


def _row_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    support_zone = _first_zone(payload.get("support_zones"))
    resistance_zone = _first_zone(payload.get("resistance_zones"))
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
        "market_map_primary_state": payload.get("market_map_primary_state"),
        "market_map_flags": ",".join(payload.get("market_map_flags", [])),
        "nearest_major_support": _json_dumps(payload.get("nearest_major_support")),
        "nearest_major_resistance": _json_dumps(payload.get("nearest_major_resistance")),
        "active_level_role": payload.get("active_level_role"),
        "level_flip_state": payload.get("level_flip_state"),
        "failed_breakout_state": payload.get("failed_breakout_state"),
        "trend_flip_state": payload.get("trend_flip_state"),
        "long_score": payload.get("long_score"),
        "short_score": payload.get("short_score"),
        "long_display_score": payload.get("long_display_score"),
        "short_display_score": payload.get("short_display_score"),
        "long_raw_score": payload.get("long_raw_score"),
        "short_raw_score": payload.get("short_raw_score"),
        "score_gap": payload.get("score_gap"),
        "score_factor_breakdown_long": _json_dumps(payload.get("score_factor_breakdown_long")),
        "score_factor_breakdown_short": _json_dumps(payload.get("score_factor_breakdown_short")),
        "top_positive_factors": _json_dumps(payload.get("top_positive_factors")),
        "top_negative_factors": _json_dumps(payload.get("top_negative_factors")),
        "confidence": payload.get("confidence"),
        "raw_confidence": payload.get("raw_confidence"),
        "confidence_direction_shadow": payload.get("confidence_direction_shadow"),
        "confidence_execution_shadow": payload.get("confidence_execution_shadow"),
        "confidence_wait_shadow": payload.get("confidence_wait_shadow"),
        "agreement_with_machine": payload.get("agreement_with_machine"),
        "prelabel": payload.get("prelabel"),
        "prelabel_primary_reason": payload.get("prelabel_primary_reason"),
        "location_risk": payload.get("location_risk"),
        "primary_setup_side": payload.get("primary_setup_side"),
        "primary_setup_status": payload.get("primary_setup_status"),
        "primary_setup_reason": payload.get("primary_setup_reason"),
        "execution_precision_action": payload.get("execution_precision_action"),
        "execution_precision_flags": ",".join(payload.get("execution_precision_flags", [])),
        "execution_precision_reason": payload.get("execution_precision_reason"),
        "invalid_reason": payload.get("invalid_reason"),
        "primary_entry_mid": payload.get("primary_entry_mid"),
        "primary_stop_loss": payload.get("primary_stop_loss"),
        "primary_tp1": payload.get("primary_tp1"),
        "primary_tp2": payload.get("primary_tp2"),
        "risk_percent_applied": payload.get("risk_percent_applied"),
        "planned_risk_usd": payload.get("planned_risk_usd"),
        "position_size_usd": payload.get("position_size_usd"),
        "loss_streak_at_entry": payload.get("loss_streak_at_entry"),
        "phase1_active": payload.get("phase1_active"),
        "phase1_activation_reason": payload.get("phase1_activation_reason"),
        "max_size_capped": payload.get("max_size_capped"),
        "size_reduction_reasons": _json_dumps(payload.get("size_reduction_reasons")),
        "tp1_price": payload.get("tp1_price"),
        "tp2_price": payload.get("tp2_price"),
        "breakeven_after_tp1": payload.get("breakeven_after_tp1"),
        "trail_atr_multiplier": payload.get("trail_atr_multiplier"),
        "timeout_hours": payload.get("timeout_hours"),
        "exit_rule_version": payload.get("exit_rule_version"),
        "shadow_tp1_price": payload.get("shadow_tp1_price"),
        "shadow_tp2_price": payload.get("shadow_tp2_price"),
        "shadow_breakeven_after_tp1": payload.get("shadow_breakeven_after_tp1"),
        "shadow_trail_atr_multiplier": payload.get("shadow_trail_atr_multiplier"),
        "shadow_timeout_hours": payload.get("shadow_timeout_hours"),
        "shadow_exit_rule_version": payload.get("shadow_exit_rule_version"),
        "trade_execution_gate": payload.get("trade_execution_gate"),
        "trade_execution_blockers": _json_dumps(payload.get("trade_execution_blockers")),
        "phase1_observation_gate": payload.get("phase1_observation_gate"),
        "phase1_observation_type": payload.get("phase1_observation_type"),
        "phase1_observation_reasons": _json_dumps(payload.get("phase1_observation_reasons")),
        "phase1b_lite_gate": payload.get("phase1b_lite_gate"),
        "phase1b_lite_type": payload.get("phase1b_lite_type"),
        "phase1b_lite_reasons": _json_dumps(payload.get("phase1b_lite_reasons")),
        "opportunity_gate": payload.get("opportunity_gate"),
        "opportunity_type": payload.get("opportunity_type"),
        "opportunity_reasons": _json_dumps(payload.get("opportunity_reasons")),
        "paper_order_status": payload.get("paper_order_status"),
        **_active_plan_row_fields(payload),
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
        "signal_tier_reason_codes": _json_dumps(payload.get("signal_tier_reason_codes")),
        "ai_decision": payload.get("ai_decision"),
        "ai_confidence": payload.get("ai_confidence"),
        "ai_audit_status": payload.get("ai_audit_status"),
        "ai_audit_verdict": payload.get("ai_audit_verdict"),
        "ai_audit_agreement": payload.get("ai_audit_agreement"),
        "ai_audit_reason": payload.get("ai_audit_reason"),
        "ai_audit_unique_risks": _json_dumps(payload.get("ai_audit_unique_risks")),
        "ai_audit_next_review_focus": payload.get("ai_audit_next_review_focus"),
        "data_quality_flag": payload.get("data_quality_flag"),
        "data_missing_fields": _json_dumps(payload.get("data_missing_fields")),
        "nearest_support_low": support_zone.get("low"),
        "nearest_support_high": support_zone.get("high"),
        "nearest_support_distance": support_zone.get("distance_from_price"),
        "nearest_resistance_low": resistance_zone.get("low"),
        "nearest_resistance_high": resistance_zone.get("high"),
        "nearest_resistance_distance": resistance_zone.get("distance_from_price"),
        "summary_subject": payload.get("summary_subject"),
        "summary_variant": payload.get("summary_variant"),
        "advice_variant": payload.get("advice_variant"),
        "prompt_variant": payload.get("prompt_variant"),
        "evaluation_trace_version": payload.get("evaluation_trace_version"),
        "no_trade_flags": ",".join(payload.get("no_trade_flags", [])),
        "notify_reason_codes": _json_dumps(payload.get("notify_reason_codes")),
        "suppress_reason_codes": _json_dumps(payload.get("suppress_reason_codes")),
        "reason_for_notification": ",".join(payload.get("reason_for_notification", [])),
    }


def _paper_position_setup_fields(payload: dict[str, Any]) -> dict[str, Any]:
    opportunity_type = str(payload.get("opportunity_type", "")).strip()
    bias = str(payload.get("bias", "")).strip()

    if opportunity_type == "counter_long_short_watch":
        if bias == "long":
            setup = _dict_or_empty(payload.get("short_setup"))
            if setup:
                return {
                    "side": "short",
                    "entry_price": setup.get("entry_mid", ""),
                    "stop_loss_price": setup.get("stop_loss", ""),
                    "tp1_price": setup.get("tp1", ""),
                    "tp2_price": setup.get("tp2", ""),
                    "rr_estimate": setup.get("rr_estimate", ""),
                }
        elif bias == "short":
            setup = _dict_or_empty(payload.get("long_setup"))
            if setup:
                return {
                    "side": "long",
                    "entry_price": setup.get("entry_mid", ""),
                    "stop_loss_price": setup.get("stop_loss", ""),
                    "tp1_price": setup.get("tp1", ""),
                    "tp2_price": setup.get("tp2", ""),
                    "rr_estimate": setup.get("rr_estimate", ""),
                }

    return {
        "side": payload.get("primary_setup_side", ""),
        "entry_price": payload.get("primary_entry_mid", ""),
        "stop_loss_price": payload.get("primary_stop_loss", ""),
        "tp1_price": payload.get("shadow_tp1_price", payload.get("tp1_price", "")),
        "tp2_price": payload.get("shadow_tp2_price", payload.get("tp2_price", "")),
        "rr_estimate": payload.get("rr_estimate", ""),
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


def append_active_plan_candidates(base_dir: Path, payload: dict[str, Any]) -> Path:
    path = base_dir / "logs" / "csv" / "active_plan_candidates.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    current_header, existing_rows = _load_existing_rows(path)
    candidate_rows = _active_plan_candidate_rows(payload)
    existing_ids = {
        str(row.get("candidate_id", "")).strip()
        for row in existing_rows
        if str(row.get("candidate_id", "")).strip()
    }
    new_rows = [row for row in candidate_rows if str(row.get("candidate_id", "")).strip() not in existing_ids]

    needs_rewrite = current_header and current_header != ACTIVE_PLAN_CANDIDATE_HEADER
    mode = "a"
    if not path.exists() or needs_rewrite:
        mode = "w"

    with path.open(mode, newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=ACTIVE_PLAN_CANDIDATE_HEADER)
        if mode == "w":
            writer.writeheader()
            for existing in existing_rows:
                writer.writerow({field: existing.get(field, "") for field in ACTIVE_PLAN_CANDIDATE_HEADER})
        for row in new_rows:
            writer.writerow({field: row.get(field, "") for field in ACTIVE_PLAN_CANDIDATE_HEADER})
    return path


PAPER_ORDER_HEADER = [
    "signal_id",
    "timestamp_jst",
    "side",
    "entry_price",
    "stop_loss_price",
    "tp1_price",
    "tp2_price",
    "risk_percent_applied",
    "planned_risk_usd",
    "position_size_usd",
    "exit_rule_version",
    "trade_execution_gate",
    "trade_execution_blockers",
    "paper_order_status",
]


OBSERVATION_PAPER_ORDER_HEADER = [
    "signal_id",
    "timestamp_jst",
    "observation_phase",
    "observation_type",
    "observation_status",
    "side",
    "reference_price",
    "entry_price",
    "stop_loss_price",
    "tp1_price",
    "tp2_price",
    "rr_estimate",
    "prelabel",
    "primary_setup_status",
    "primary_setup_reason",
    "phase1_observation_reasons",
    "confidence_direction_shadow",
    "confidence_execution_shadow",
    "confidence_wait_shadow",
    "trade_execution_gate",
]


PHASE1B_LITE_PAPER_ORDER_HEADER = [
    "signal_id",
    "timestamp_jst",
    "lite_phase",
    "lite_type",
    "lite_status",
    "side",
    "reference_price",
    "entry_price",
    "stop_loss_price",
    "tp1_price",
    "tp2_price",
    "rr_estimate",
    "prelabel",
    "primary_setup_status",
    "primary_setup_reason",
    "phase1b_lite_reasons",
    "confidence_direction_shadow",
    "confidence_execution_shadow",
    "confidence_wait_shadow",
    "trade_execution_gate",
]


PAPER_POSITION_HEADER = [
    "signal_id",
    "timestamp_jst",
    "position_phase",
    "position_status",
    "opportunity_type",
    "opportunity_reasons",
    "side",
    "reference_price",
    "entry_price",
    "stop_loss_price",
    "tp1_price",
    "tp2_price",
    "breakeven_after_tp1",
    "timeout_hours",
    "exit_rule_version",
    "rr_estimate",
    "prelabel",
    "primary_setup_status",
    "primary_setup_reason",
    "market_map_flags",
    "confidence_direction_shadow",
    "confidence_execution_shadow",
    "confidence_wait_shadow",
    "trade_execution_gate",
    "opened_at_jst",
    "closed_at_jst",
    "exit_status",
    "exit_reason",
    "close_price",
    "tp1_hit_at_jst",
    "tp2_hit_at_jst",
    "sl_hit_at_jst",
    "timeout_at_jst",
    "mfe_atr",
    "mae_atr",
    "realized_r",
    "missed_opportunity",
    "missed_reason",
    "last_evaluated_at_utc",
]


def append_paper_order(base_dir: Path, payload: dict[str, Any]) -> Path:
    path = base_dir / "logs" / "csv" / "paper_orders.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    current_header, existing_rows = _load_existing_rows(path)
    signal_id = str(payload.get("signal_id", "")).strip()
    if signal_id and any(str(row.get("signal_id", "")).strip() == signal_id for row in existing_rows):
        return path

    json_dumps = lambda value: json.dumps(value, ensure_ascii=False) if value not in (None, "", []) else ""
    row = {
        "signal_id": signal_id,
        "timestamp_jst": payload.get("timestamp_jst", ""),
        "side": payload.get("primary_setup_side", ""),
        "entry_price": payload.get("primary_entry_mid", ""),
        "stop_loss_price": payload.get("primary_stop_loss", ""),
        "tp1_price": payload.get("shadow_tp1_price", payload.get("tp1_price", "")),
        "tp2_price": payload.get("shadow_tp2_price", payload.get("tp2_price", "")),
        "risk_percent_applied": payload.get("risk_percent_applied", ""),
        "planned_risk_usd": payload.get("planned_risk_usd", ""),
        "position_size_usd": payload.get("position_size_usd", ""),
        "exit_rule_version": payload.get("shadow_exit_rule_version", payload.get("exit_rule_version", "")),
        "trade_execution_gate": payload.get("trade_execution_gate", ""),
        "trade_execution_blockers": json_dumps(payload.get("trade_execution_blockers")),
        "paper_order_status": payload.get("paper_order_status", "planned"),
    }

    needs_rewrite = current_header and current_header != PAPER_ORDER_HEADER
    mode = "a"
    if not path.exists() or needs_rewrite:
        mode = "w"

    with path.open(mode, newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=PAPER_ORDER_HEADER)
        if mode == "w":
            writer.writeheader()
            for existing in existing_rows:
                writer.writerow({field: existing.get(field, "") for field in PAPER_ORDER_HEADER})
        writer.writerow(row)
    return path


def append_observation_paper_order(base_dir: Path, payload: dict[str, Any]) -> Path:
    path = base_dir / "logs" / "csv" / "observation_paper_orders.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    current_header, existing_rows = _load_existing_rows(path)
    signal_id = str(payload.get("signal_id", "")).strip()
    if signal_id and any(str(row.get("signal_id", "")).strip() == signal_id for row in existing_rows):
        return path

    observation_type = str(payload.get("phase1_observation_type", "")).strip()
    observation_side = payload.get("primary_setup_side", "")
    if observation_type == "counter_long_short_watch":
        bias = str(payload.get("bias", "")).strip()
        if bias == "long":
            observation_side = "short"
        elif bias == "short":
            observation_side = "long"

    json_dumps = lambda value: json.dumps(value, ensure_ascii=False) if value not in (None, "", []) else ""
    row = {
        "signal_id": signal_id,
        "timestamp_jst": payload.get("timestamp_jst", ""),
        "observation_phase": "phase1A",
        "observation_type": observation_type,
        "observation_status": "observing",
        "side": observation_side,
        "reference_price": payload.get("current_price", ""),
        "entry_price": payload.get("primary_entry_mid", ""),
        "stop_loss_price": payload.get("primary_stop_loss", ""),
        "tp1_price": payload.get("shadow_tp1_price", payload.get("tp1_price", "")),
        "tp2_price": payload.get("shadow_tp2_price", payload.get("tp2_price", "")),
        "rr_estimate": payload.get("rr_estimate", ""),
        "prelabel": payload.get("prelabel", ""),
        "primary_setup_status": payload.get("primary_setup_status", ""),
        "primary_setup_reason": payload.get("primary_setup_reason", ""),
        "phase1_observation_reasons": json_dumps(payload.get("phase1_observation_reasons")),
        "confidence_direction_shadow": payload.get("confidence_direction_shadow", ""),
        "confidence_execution_shadow": payload.get("confidence_execution_shadow", ""),
        "confidence_wait_shadow": payload.get("confidence_wait_shadow", ""),
        "trade_execution_gate": payload.get("trade_execution_gate", ""),
    }

    needs_rewrite = current_header and current_header != OBSERVATION_PAPER_ORDER_HEADER
    mode = "a"
    if not path.exists() or needs_rewrite:
        mode = "w"

    with path.open(mode, newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=OBSERVATION_PAPER_ORDER_HEADER)
        if mode == "w":
            writer.writeheader()
            for existing in existing_rows:
                writer.writerow({field: existing.get(field, "") for field in OBSERVATION_PAPER_ORDER_HEADER})
        writer.writerow(row)
    return path


def append_phase1b_lite_paper_order(base_dir: Path, payload: dict[str, Any]) -> Path:
    path = base_dir / "logs" / "csv" / "phase1b_lite_paper_orders.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    current_header, existing_rows = _load_existing_rows(path)
    signal_id = str(payload.get("signal_id", "")).strip()
    if signal_id and any(str(row.get("signal_id", "")).strip() == signal_id for row in existing_rows):
        return path

    json_dumps = lambda value: json.dumps(value, ensure_ascii=False) if value not in (None, "", []) else ""
    row = {
        "signal_id": signal_id,
        "timestamp_jst": payload.get("timestamp_jst", ""),
        "lite_phase": "phase1B-lite",
        "lite_type": payload.get("phase1b_lite_type", ""),
        "lite_status": "observing",
        "side": payload.get("primary_setup_side", ""),
        "reference_price": payload.get("current_price", ""),
        "entry_price": payload.get("primary_entry_mid", ""),
        "stop_loss_price": payload.get("primary_stop_loss", ""),
        "tp1_price": payload.get("shadow_tp1_price", payload.get("tp1_price", "")),
        "tp2_price": payload.get("shadow_tp2_price", payload.get("tp2_price", "")),
        "rr_estimate": payload.get("rr_estimate", ""),
        "prelabel": payload.get("prelabel", ""),
        "primary_setup_status": payload.get("primary_setup_status", ""),
        "primary_setup_reason": payload.get("primary_setup_reason", ""),
        "phase1b_lite_reasons": json_dumps(payload.get("phase1b_lite_reasons")),
        "confidence_direction_shadow": payload.get("confidence_direction_shadow", ""),
        "confidence_execution_shadow": payload.get("confidence_execution_shadow", ""),
        "confidence_wait_shadow": payload.get("confidence_wait_shadow", ""),
        "trade_execution_gate": payload.get("trade_execution_gate", ""),
    }

    needs_rewrite = current_header and current_header != PHASE1B_LITE_PAPER_ORDER_HEADER
    mode = "a"
    if not path.exists() or needs_rewrite:
        mode = "w"

    with path.open(mode, newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=PHASE1B_LITE_PAPER_ORDER_HEADER)
        if mode == "w":
            writer.writeheader()
            for existing in existing_rows:
                writer.writerow({field: existing.get(field, "") for field in PHASE1B_LITE_PAPER_ORDER_HEADER})
        writer.writerow(row)
    return path


def append_paper_position(base_dir: Path, payload: dict[str, Any]) -> Path:
    path = base_dir / "logs" / "csv" / "paper_positions.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    current_header, existing_rows = _load_existing_rows(path)
    signal_id = str(payload.get("signal_id", "")).strip()
    if signal_id and any(str(row.get("signal_id", "")).strip() == signal_id for row in existing_rows):
        return path

    json_dumps = lambda value: json.dumps(value, ensure_ascii=False) if value not in (None, "", []) else ""
    setup_status = str(payload.get("primary_setup_status", "")).strip()
    position_status = "opened" if setup_status == "ready" else "pending"
    setup_fields = _paper_position_setup_fields(payload)
    row = {
        "signal_id": signal_id,
        "timestamp_jst": payload.get("timestamp_jst", ""),
        "position_phase": "pre_auto_paper",
        "position_status": position_status,
        "opportunity_type": payload.get("opportunity_type", ""),
        "opportunity_reasons": json_dumps(payload.get("opportunity_reasons")),
        "side": setup_fields["side"],
        "reference_price": payload.get("current_price", ""),
        "entry_price": setup_fields["entry_price"],
        "stop_loss_price": setup_fields["stop_loss_price"],
        "tp1_price": setup_fields["tp1_price"],
        "tp2_price": setup_fields["tp2_price"],
        "breakeven_after_tp1": payload.get("shadow_breakeven_after_tp1", payload.get("breakeven_after_tp1", "")),
        "timeout_hours": payload.get("shadow_timeout_hours", payload.get("timeout_hours", "")),
        "exit_rule_version": payload.get("shadow_exit_rule_version", payload.get("exit_rule_version", "")),
        "rr_estimate": setup_fields["rr_estimate"],
        "prelabel": payload.get("prelabel", ""),
        "primary_setup_status": setup_status,
        "primary_setup_reason": payload.get("primary_setup_reason", ""),
        "market_map_flags": ",".join(payload.get("market_map_flags", [])),
        "confidence_direction_shadow": payload.get("confidence_direction_shadow", ""),
        "confidence_execution_shadow": payload.get("confidence_execution_shadow", ""),
        "confidence_wait_shadow": payload.get("confidence_wait_shadow", ""),
        "trade_execution_gate": payload.get("trade_execution_gate", ""),
        "opened_at_jst": payload.get("timestamp_jst", "") if position_status == "opened" else "",
        "closed_at_jst": "",
        "exit_status": "",
        "exit_reason": "",
        "close_price": "",
        "tp1_hit_at_jst": "",
        "tp2_hit_at_jst": "",
        "sl_hit_at_jst": "",
        "timeout_at_jst": "",
        "mfe_atr": "",
        "mae_atr": "",
        "realized_r": "",
        "missed_opportunity": "",
        "missed_reason": "",
        "last_evaluated_at_utc": "",
    }

    needs_rewrite = current_header and current_header != PAPER_POSITION_HEADER
    mode = "a"
    if not path.exists() or needs_rewrite:
        mode = "w"

    with path.open(mode, newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
        if mode == "w":
            writer.writeheader()
            for existing in existing_rows:
                writer.writerow({field: existing.get(field, "") for field in PAPER_POSITION_HEADER})
        writer.writerow(row)
    return path
