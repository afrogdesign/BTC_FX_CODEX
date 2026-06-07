from __future__ import annotations

from typing import Any


PLAN_VERSION = "active_trade_plan_v1"

_FATAL_NO_TRADE_FLAGS = {
    "ATR_extreme",
    "Funding_prohibited",
    "Funding_prohibited_long",
    "Funding_prohibited_short",
}

_SUPPORT_REACTION_FLAGS = {
    "major_support_rejection",
    "short_into_major_support",
    "short_at_major_support_wait_only",
}

_RESISTANCE_REACTION_FLAGS = {
    "major_resistance_rejection",
    "long_into_major_resistance",
    "long_at_major_resistance_wait_only",
}


def _to_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return 0.0
    if parsed <= 0:
        return 0.0
    return parsed


def _format_price_range(low: float, high: float) -> str:
    return f"{round(low):,}-{round(high):,}"


def _bias_alignment(bias: str, side: str) -> str:
    normalized_bias = str(bias).strip().lower()
    normalized_side = str(side).strip().lower()
    if normalized_bias == normalized_side:
        return "primary"
    if normalized_bias in {"long", "short"}:
        return "counter"
    return "neutral"


def _extract_setup(setup: dict[str, Any]) -> dict[str, float]:
    entry_zone = setup.get("entry_zone") if isinstance(setup, dict) else {}
    if not isinstance(entry_zone, dict):
        entry_zone = {}
    low = _to_float(entry_zone.get("low"))
    high = _to_float(entry_zone.get("high"))
    if low and high and low > high:
        low, high = high, low
    entry_mid = _to_float(setup.get("entry_mid")) if isinstance(setup, dict) else 0.0
    stop_loss = _to_float(setup.get("stop_loss")) if isinstance(setup, dict) else 0.0
    tp1 = _to_float(setup.get("tp1")) if isinstance(setup, dict) else 0.0
    tp2 = _to_float(setup.get("tp2")) if isinstance(setup, dict) else 0.0
    if not entry_mid and low and high:
        entry_mid = round((low + high) / 2, 2)
    return {
        "entry_zone_low": low,
        "entry_zone_high": high,
        "entry_mid": entry_mid,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "tp2": tp2,
    }


def classify_zone_position(side: str, price: float, entry_low: float, entry_high: float) -> str:
    normalized_side = str(side).strip().lower()
    if normalized_side not in {"long", "short"}:
        return "unknown"
    price_value = _to_float(price)
    low = _to_float(entry_low)
    high = _to_float(entry_high)
    if not price_value or not low or not high:
        return "unknown"
    if low > high:
        low, high = high, low
    if price_value < low:
        return "below_zone"
    if price_value <= high:
        return "inside_zone"
    return "above_zone"


def rr_for_entry(side: str, entry_price: float, stop: float, target: float) -> float | None:
    normalized_side = str(side).strip().lower()
    if normalized_side not in {"long", "short"}:
        return None
    entry_value = _to_float(entry_price)
    stop_value = _to_float(stop)
    target_value = _to_float(target)
    if not entry_value or not stop_value or not target_value:
        return None
    if normalized_side == "long":
        risk = entry_value - stop_value
        reward = target_value - entry_value
    else:
        risk = stop_value - entry_value
        reward = entry_value - target_value
    if risk <= 0 or reward <= 0:
        return None
    return round(reward / risk, 2)


def _build_side_plan(
    *,
    side: str,
    current_price: float,
    bias: str,
    setup: dict[str, Any],
    confidence_execution_shadow: float,
    confidence_wait_shadow: float,
    combined_flags: set[str],
    fatal_flags: list[str],
    data_quality_flag: str,
    breakout_up: bool,
    breakout_down: bool,
    volume_ratio: float,
    trigger_volume_ratio_threshold: float,
) -> dict[str, Any]:
    values = _extract_setup(setup)
    zone_position = classify_zone_position(
        side,
        current_price,
        values["entry_zone_low"],
        values["entry_zone_high"],
    )
    prices_valid = all(
        (
            values["entry_zone_low"] > 0,
            values["entry_zone_high"] > 0,
            values["entry_mid"] > 0,
            values["stop_loss"] > 0,
            values["tp1"] > 0,
            values["tp2"] > 0,
        )
    )
    rr_current_tp1 = rr_for_entry(side, current_price, values["stop_loss"], values["tp1"])
    rr_current_tp2 = rr_for_entry(side, current_price, values["stop_loss"], values["tp2"])
    rr_zone_mid_tp1 = rr_for_entry(side, values["entry_mid"], values["stop_loss"], values["tp1"])
    rr_zone_mid_tp2 = rr_for_entry(side, values["entry_mid"], values["stop_loss"], values["tp2"])

    blockers: list[str] = []
    triggers: list[str] = []

    if data_quality_flag != "ok":
        blockers.append("data_quality_not_ok")
    if fatal_flags:
        blockers.append("fatal_no_trade_flags_present")
    if not prices_valid:
        blockers.append("missing_setup_prices")

    market_entry_status = "blocked"
    market_blockers = list(blockers)
    if zone_position != "inside_zone":
        market_blockers.append("current_price_not_inside_entry_zone")
    rr_current_ok = (rr_current_tp1 is not None and rr_current_tp1 >= 0.8) or (
        rr_current_tp2 is not None and rr_current_tp2 >= 1.5
    )
    if not rr_current_ok:
        market_blockers.append("current_rr_too_low")
    if confidence_execution_shadow < 24:
        market_blockers.append("execution_too_low_for_market")
    if confidence_wait_shadow >= 55:
        market_blockers.append("wait_pressure_too_high")

    if side == "short":
        if zone_position == "below_zone":
            market_blockers.append("current_price_below_short_zone_chase_risk")
        if {"short_into_major_support", "short_at_major_support_wait_only"} & combined_flags:
            market_blockers.append("short_into_major_support_market_block")
        if "trend_flip_confirmed_up" in combined_flags:
            market_blockers.append("short_market_warning_trend_flip_up")
    elif side == "long":
        if zone_position == "above_zone":
            market_blockers.append("current_price_above_long_zone_chase_risk")
        if {"long_into_major_resistance", "long_at_major_resistance_wait_only"} & combined_flags:
            market_blockers.append("long_into_major_resistance_market_block")
        if "trend_flip_confirmed_down" in combined_flags:
            market_blockers.append("long_market_warning_trend_flip_down")

    if not market_blockers:
        market_entry_status = "allowed"
        triggers.append("market_entry_conditions_met")

    limit_entry_status = "blocked"
    limit_blockers = list(blockers)
    rr_limit_ok = (rr_zone_mid_tp1 is not None and rr_zone_mid_tp1 >= 1.0) and (
        rr_zone_mid_tp2 is not None and rr_zone_mid_tp2 >= 1.8
    )
    if not rr_limit_ok:
        limit_blockers.append("limit_rr_too_low")
    if not limit_blockers:
        limit_entry_status = "allowed"
        triggers.append("limit_retest_conditions_met")

    breakout_status = "blocked"
    breakout_blockers = list(blockers)
    if not breakout_blockers:
        if side == "long":
            if breakout_up and volume_ratio >= trigger_volume_ratio_threshold:
                breakout_status = "armed"
            elif breakout_up:
                breakout_status = "watch"
        else:
            if breakout_down and volume_ratio >= trigger_volume_ratio_threshold:
                breakout_status = "armed"
            elif breakout_down:
                breakout_status = "watch"

    counter_scalp_status = "blocked"
    counter_blockers = list(blockers)
    rr_for_counter = rr_current_tp1
    counter_conditions_met = False
    if side == "long":
        counter_conditions_met = (
            str(bias).strip().lower() == "short"
            and prices_valid
            and rr_for_counter is not None
            and rr_for_counter > 0
            and (
                zone_position == "inside_zone"
                or bool(_SUPPORT_REACTION_FLAGS & combined_flags)
            )
        )
    elif side == "short":
        counter_conditions_met = (
            str(bias).strip().lower() == "long"
            and prices_valid
            and rr_for_counter is not None
            and rr_for_counter > 0
            and (
                zone_position == "inside_zone"
                or bool(_RESISTANCE_REACTION_FLAGS & combined_flags)
            )
        )
    if not counter_blockers and counter_conditions_met:
        counter_scalp_status = "conditional"
        triggers.append("counter_scalp_conditions_met")

    if side == "short":
        next_condition = f"{_format_price_range(values['entry_zone_low'], values['entry_zone_high'])} へ戻り、15分足で再失速するなら候補"
    else:
        next_condition = f"{_format_price_range(values['entry_zone_low'], values['entry_zone_high'])} へ押し、15分足で反発継続なら候補"

    return {
        "side": side,
        "bias_alignment": _bias_alignment(bias, side),
        "entry_zone_low": values["entry_zone_low"],
        "entry_zone_high": values["entry_zone_high"],
        "entry_mid": values["entry_mid"],
        "current_price": current_price,
        "zone_position": zone_position,
        "market_entry_status": market_entry_status,
        "limit_entry_status": limit_entry_status,
        "breakout_status": breakout_status,
        "counter_scalp_status": counter_scalp_status,
        "stop_loss": values["stop_loss"],
        "tp1": values["tp1"],
        "tp2": values["tp2"],
        "rr_current_tp1": rr_current_tp1,
        "rr_current_tp2": rr_current_tp2,
        "rr_zone_mid_tp1": rr_zone_mid_tp1,
        "rr_zone_mid_tp2": rr_zone_mid_tp2,
        "blockers": sorted(set(market_blockers + limit_blockers + breakout_blockers + counter_blockers)),
        "triggers": triggers,
        "next_condition": next_condition,
    }


def _headline(
    *,
    bias: str,
    primary_action: str,
    primary_plan: dict[str, Any] | None,
    counter_plan: dict[str, Any] | None,
) -> str:
    normalized_bias = str(bias).strip().lower()
    if normalized_bias not in {"long", "short"}:
        return "方向は中立。現時点では見送り。"
    if normalized_bias == "short":
        direction = "下方向優勢。"
        market_text = "成行ショート可。" if primary_plan and primary_plan["market_entry_status"] == "allowed" else "ただし成行ショート不可。"
        limit_text = "戻り売り待ち。" if primary_plan and primary_plan["limit_entry_status"] == "allowed" else ""
        counter_text = "現値は短期反発帯。" if counter_plan and counter_plan["counter_scalp_status"] == "conditional" else ""
    elif normalized_bias == "long":
        direction = "上方向優勢。"
        market_text = "成行ロング可。" if primary_plan and primary_plan["market_entry_status"] == "allowed" else "ただし成行ロング不可。"
        limit_text = "押し目買い待ち。" if primary_plan and primary_plan["limit_entry_status"] == "allowed" else ""
        counter_text = "現値は短期反落帯。" if counter_plan and counter_plan["counter_scalp_status"] == "conditional" else ""

    if primary_action == "NO_ACTION":
        return f"{direction} 現時点では見送り。"
    return f"{direction}{market_text}{limit_text}{counter_text}".strip()


def build_active_trade_plan(
    *,
    current_price: float,
    bias: str,
    market_regime: str,
    long_setup: dict[str, Any],
    short_setup: dict[str, Any],
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
    risk_flags: list[str],
    market_map_flags: list[str],
    no_trade_flags: list[str],
    data_quality_flag: str,
    breakout_up: bool,
    breakout_down: bool,
    volume_ratio: float,
    trigger_volume_ratio_threshold: float,
) -> dict[str, Any]:
    del market_regime
    del confidence_direction_shadow

    current_price_value = _to_float(current_price)
    execution_value = _to_float(confidence_execution_shadow)
    wait_value = _to_float(confidence_wait_shadow)
    combined_flags = {str(flag) for flag in [*risk_flags, *market_map_flags] if str(flag).strip()}
    fatal_flags = sorted(flag for flag in no_trade_flags if flag in _FATAL_NO_TRADE_FLAGS)

    long_plan = _build_side_plan(
        side="long",
        current_price=current_price_value,
        bias=bias,
        setup=long_setup,
        confidence_execution_shadow=execution_value,
        confidence_wait_shadow=wait_value,
        combined_flags=combined_flags,
        fatal_flags=fatal_flags,
        data_quality_flag=data_quality_flag,
        breakout_up=breakout_up,
        breakout_down=breakout_down,
        volume_ratio=volume_ratio,
        trigger_volume_ratio_threshold=trigger_volume_ratio_threshold,
    )
    short_plan = _build_side_plan(
        side="short",
        current_price=current_price_value,
        bias=bias,
        setup=short_setup,
        confidence_execution_shadow=execution_value,
        confidence_wait_shadow=wait_value,
        combined_flags=combined_flags,
        fatal_flags=fatal_flags,
        data_quality_flag=data_quality_flag,
        breakout_up=breakout_up,
        breakout_down=breakout_down,
        volume_ratio=volume_ratio,
        trigger_volume_ratio_threshold=trigger_volume_ratio_threshold,
    )

    normalized_bias = str(bias).strip().lower()
    if normalized_bias == "long":
        primary_plan = long_plan
        counter_plan = short_plan
    elif normalized_bias == "short":
        primary_plan = short_plan
        counter_plan = long_plan
    else:
        primary_plan = None
        counter_plan = None

    if primary_plan is None or counter_plan is None:
        primary_action = "NO_ACTION"
    elif primary_plan["market_entry_status"] == "allowed":
        primary_action = "ACTIVE_MARKET_SMALL"
    elif primary_plan["limit_entry_status"] == "allowed" and counter_plan["counter_scalp_status"] == "conditional":
        primary_action = "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP"
    elif primary_plan["limit_entry_status"] == "allowed":
        primary_action = "ACTIVE_LIMIT_RETEST"
    elif primary_plan["breakout_status"] == "armed":
        primary_action = "ACTIVE_BREAKOUT_FOLLOW"
    elif counter_plan["counter_scalp_status"] == "conditional":
        primary_action = "ACTIVE_COUNTER_SCALP"
    else:
        primary_action = "NO_ACTION"

    if data_quality_flag != "ok" or fatal_flags:
        primary_action = "NO_ACTION"

    warnings: list[str] = []
    if data_quality_flag != "ok":
        warnings.append("data_quality_not_ok")
    warnings.extend(fatal_flags)

    headline = _headline(
        bias=bias,
        primary_action=primary_action,
        primary_plan=primary_plan,
        counter_plan=counter_plan,
    )

    return {
        "plan_version": PLAN_VERSION,
        "primary_action": primary_action,
        "headline": headline,
        "market_entry_now": {
            "long": long_plan["market_entry_status"],
            "short": short_plan["market_entry_status"],
        },
        "limit_retest_entry": {
            "long": long_plan["limit_entry_status"],
            "short": short_plan["limit_entry_status"],
        },
        "breakout_follow_entry": {
            "long": long_plan["breakout_status"],
            "short": short_plan["breakout_status"],
        },
        "countertrend_scalp_entry": {
            "long": long_plan["counter_scalp_status"],
            "short": short_plan["counter_scalp_status"],
        },
        "position_management": {
            "if_long_holding": "long 保有中なら、主要レジスタンス反応では利確または建値撤退を優先。直近押し安値割れで上昇継続シナリオを弱める。",
            "if_short_holding": "short 保有中なら、主要サポート反応では利確または建値撤退を優先。直近戻り高値上抜けで下落継続シナリオを弱める。",
        },
        "side_plans": {
            "long": long_plan,
            "short": short_plan,
        },
        "warnings": warnings,
    }
