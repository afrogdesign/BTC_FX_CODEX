from __future__ import annotations

import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from config import load_config
from src.ai.advice import request_ai_advice
from src.ai.summary import build_summary_body, build_summary_subject
from src.analysis.chart_pattern_shadow import build_chart_pattern_shadow
from src.analysis.liquidation import analyze_liquidation_clusters
from src.analysis.liquidity import analyze_liquidity
from src.analysis.breakout import previous_breakout_levels
from src.analysis.funding import format_funding_pct, funding_rate_label, funding_rate_raw_to_pct
from src.analysis.market_map import build_market_map
from src.analysis.oi_cvd import analyze_oi_cvd
from src.analysis.orderbook import analyze_orderbook
from src.analysis.position_risk import apply_prelabel_to_setup, evaluate_position_risk, reconcile_prelabel_with_setup
from src.analysis.result_flags import assemble_result_flags, derive_additional_risk_flags
from src.analysis.signal_tier import compute_signal_tier, signal_tier_badge
from src.analysis.confidence import compute_confidence_details, compute_machine_agreement
from src.analysis.evaluation_trace import build_evaluation_trace
from src.analysis.phase import determine_phase
from src.analysis.qualitative import build_qualitative_context
from src.analysis.regime import classify_market_regime
from src.analysis.rr import build_setup, choose_primary_setup, refine_execution_precision
from src.analysis.scoring import compute_scores
from src.analysis.structure import calc_tf_signal, classify_structure, detect_swings
from src.analysis.support_resistance import (
    build_all_support_resistance,
    build_support_resistance,
    detect_critical_zone,
    nearest_zone_distance,
    select_nearest_directional_zones,
    sort_zones_by_distance,
    zone_gap_to_opposite,
)
from src.analysis.volume_structure import analyze_volume_structure
from src.data.fetcher import DataFetchError, FetchConfig, fetch_funding_rate, fetch_klines, get_server_time_ms
from src.data.exchange_fetcher import fetch_market_structure
from src.data.validator import validate_klines
from src.indicators.atr import calculate_atr, calculate_atr_ratio
from src.indicators.ema import calculate_ema, get_ema20_slope, get_ema_alignment
from src.indicators.rsi import calculate_rsi
from src.indicators.volume import calculate_volume_ratio
from src.notification.email_sender import resend_pending_email, save_pending_email, send_email
from src.notification.detail_page import (
    append_detail_page_url,
    detail_page_enabled,
    publish_notification_detail,
)
from src.notification.trigger import should_notify
from src.storage.cleanup import cleanup_if_due
from src.storage.csv_logger import (
    append_active_plan_candidates,
    append_observation_paper_order,
    append_paper_order,
    append_paper_position,
    append_phase1b_lite_paper_order,
    append_trade_log,
)
from src.storage.json_store import (
    get_last_attention_notified_path,
    get_last_notified_path,
    get_last_result_path,
    load_json,
    save_json,
    save_signal_snapshot,
)
from src.trade.active_plan import build_active_trade_plan
from src.trade.activation import determine_phase1_activation
from src.trade.execution_gate import determine_trade_execution_gate
from src.trade.exit_manager import build_exit_plan, build_shadow_exit_plan
from src.trade.observation_gate import determine_phase1_observation_gate
from src.trade.opportunity_gate import determine_opportunity_gate
from src.trade.phase1b_lite import determine_phase1b_lite_gate
from src.trade.performance_state import load_loss_streak
from src.trade.position_sizing import build_position_size_plan
from src.presentation.sanitize import (
    ADVICE_VARIANT,
    EVALUATION_TRACE_VERSION,
    PROMPT_VARIANT,
    SUMMARY_VARIANT,
    build_display_context,
    build_notification_context,
)


def _base_dir() -> Path:
    return Path(__file__).resolve().parent


def update_heartbeat(base_dir: Path, heartbeat_file: str) -> None:
    path = base_dir / heartbeat_file
    path.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
    path.write_text(now_iso, encoding="utf-8")


def _error_log(base_dir: Path, title: str, details: str) -> None:
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = base_dir / "logs" / "errors" / f"{ts}_{title}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(details, encoding="utf-8")


def _round2(value: float) -> float:
    return round(float(value), 2)


def _round_optional(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


_DIRECTIONAL_VOLUME_LONG_FLAGS = {
    "failed_breakout_up_reversal",
    "resistance_to_support_flip",
    "resistance_to_support_retest_confirmed",
}

_DIRECTIONAL_VOLUME_SHORT_FLAGS = {
    "failed_breakout_down_reversal",
    "support_to_resistance_flip",
    "support_to_resistance_retest_confirmed",
}


def _directional_volume_triggers(
    *,
    volume_ratio: float,
    volume_threshold: float,
    candle_open: float,
    candle_high: float,
    candle_low: float,
    candle_close: float,
    range_high: float,
    range_low: float,
    breakout_up: bool,
    breakout_down: bool,
    market_map: dict[str, Any] | None,
) -> dict[str, bool]:
    flags = set((market_map or {}).get("flags") or [])
    trigger_up = bool(breakout_up)
    trigger_down = bool(breakout_down)

    if flags & _DIRECTIONAL_VOLUME_LONG_FLAGS:
        trigger_up = True
    if flags & _DIRECTIONAL_VOLUME_SHORT_FLAGS:
        trigger_down = True

    if float(volume_ratio) < float(volume_threshold):
        return {"trigger_up": trigger_up, "trigger_down": trigger_down}

    candle_range = max(float(candle_high) - float(candle_low), 1e-9)
    body = abs(float(candle_close) - float(candle_open))
    body_ratio = body / candle_range
    close_position = (float(candle_close) - float(candle_low)) / candle_range

    if body_ratio < 0.20:
        return {"trigger_up": trigger_up, "trigger_down": trigger_down}

    bullish = float(candle_close) > float(candle_open)
    bearish = float(candle_close) < float(candle_open)

    range_span = max(float(range_high) - float(range_low), 1e-9)
    range_close_position = (float(candle_close) - float(range_low)) / range_span

    if bullish and (close_position >= 0.60 or range_close_position >= 0.60):
        trigger_up = True
    if bearish and (close_position <= 0.40 or range_close_position <= 0.40):
        trigger_down = True

    return {"trigger_up": trigger_up, "trigger_down": trigger_down}


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        key = str(value).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(key)
    return ordered


def _normalize_provider_label(value: Any) -> str:
    label = str(value or "api").strip().lower()
    if label == "cli":
        return "CLI"
    if label == "api":
        return "API"
    return label.upper() or "API"


def _build_chart_candles(df: Any, *, limit: int) -> list[dict[str, Any]]:
    if df is None or len(df) <= 0:
        return []
    subset = df.tail(limit)
    candles: list[dict[str, Any]] = []
    for row in subset.itertuples(index=False):
        timestamp = getattr(row, "timestamp", None)
        if timestamp is None:
            continue
        try:
            ts_ms = int(timestamp)
        except (TypeError, ValueError):
            continue
        candles.append(
            {
                "timestamp": ts_ms,
                "open": _round_optional(getattr(row, "open", None), 2),
                "high": _round_optional(getattr(row, "high", None), 2),
                "low": _round_optional(getattr(row, "low", None), 2),
                "close": _round_optional(getattr(row, "close", None), 2),
                "volume": _round_optional(getattr(row, "volume", None), 4),
            }
        )
    return candles


def _build_chart_snapshot(df_4h: Any, df_1h: Any, df_15m: Any) -> dict[str, Any]:
    return {
        "intervals": ["4h", "1h", "15m"],
        "candles_4h": _build_chart_candles(df_4h, limit=80),
        "candles_1h": _build_chart_candles(df_1h, limit=96),
        "candles_15m": _build_chart_candles(df_15m, limit=96),
    }


def _build_system_mode_label(cfg: Any) -> str:
    advice = _normalize_provider_label(getattr(cfg, "AI_ADVICE_PROVIDER", "api"))
    summary = _normalize_provider_label(getattr(cfg, "AI_SUMMARY_PROVIDER", "api"))
    if advice == summary:
        return advice
    return f"{advice}/{summary}"


def _build_system_mode_label_from_values(advice_provider: Any, summary_provider: Any) -> str:
    advice = _normalize_provider_label(advice_provider)
    summary = _normalize_provider_label(summary_provider)
    if advice == summary:
        return advice
    return f"{advice}/{summary}"


def _normalize_missing_data_fields(raw_fields: list[str], *, ai_missing: bool, funding_missing: bool) -> list[str]:
    mapped: list[str] = []
    if funding_missing:
        mapped.append("funding")
    if ai_missing:
        mapped.append("ai_response")
    for field in raw_fields:
        if field in {"oi_value", "oi_change_pct", "oi_trend_values"}:
            mapped.append("oi")
        elif field in {"buy_volume", "sell_volume", "cvd_series"}:
            mapped.append("taker")
        elif field in {"orderbook_bids", "orderbook_asks"}:
            mapped.append("orderbook")
        elif field == "liquidation_events":
            mapped.append("liquidation")
    return _dedupe_preserve(mapped)


def _data_quality_flag(missing_fields: list[str]) -> str:
    count = len(_dedupe_preserve(missing_fields))
    if count <= 0:
        return "ok"
    if count == 1:
        return "degraded"
    return "partial_missing"


def _prepare_tf(df, cfg, swing_n: int) -> dict[str, Any]:
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    ema_fast = calculate_ema(close, cfg.EMA_FAST)
    ema_mid = calculate_ema(close, cfg.EMA_MID)
    ema_slow = calculate_ema(close, cfg.EMA_SLOW)
    rsi = calculate_rsi(close, cfg.RSI_LENGTH)
    atr = calculate_atr(high, low, close, cfg.ATR_LENGTH)
    vol_ratio = calculate_volume_ratio(volume, 20)

    swings = detect_swings(df, swing_n)
    structure = classify_structure(swings)
    ema_alignment = get_ema_alignment(float(ema_fast.iloc[-1]), float(ema_mid.iloc[-1]), float(ema_slow.iloc[-1]))
    signal = calc_tf_signal(ema_alignment, structure)

    return {
        "df": df,
        "swings": swings,
        "structure": structure,
        "signal": signal,
        "ema_alignment": ema_alignment,
        "ema_fast": ema_fast,
        "ema_mid": ema_mid,
        "ema_slow": ema_slow,
        "ema20_slope": get_ema20_slope(ema_fast),
        "rsi": rsi,
        "atr": atr,
        "volume_ratio": vol_ratio,
    }


def _build_fetch_cfg(cfg: Any) -> FetchConfig:
    return FetchConfig(
        base_url=cfg.MEXC_BASE_URL,
        symbol=cfg.MEXC_SYMBOL,
        timeout_sec=cfg.API_TIMEOUT_SEC,
        retry_count=cfg.API_RETRY_COUNT,
        request_interval_sec=cfg.REQUEST_INTERVAL_SEC,
    )


def _phase1_defaults() -> dict[str, Any]:
    return {
        "risk_percent_applied": "",
        "planned_risk_usd": "",
        "position_size_usd": "",
        "loss_streak_at_entry": "",
        "phase1_active": "",
        "phase1_activation_reason": "",
        "max_size_capped": "",
        "size_reduction_reasons": [],
        "tp1_price": "",
        "tp2_price": "",
        "breakeven_after_tp1": "",
        "trail_atr_multiplier": "",
        "timeout_hours": "",
        "exit_rule_version": "",
        "shadow_tp1_price": "",
        "shadow_tp2_price": "",
        "shadow_breakeven_after_tp1": "",
        "shadow_trail_atr_multiplier": "",
        "shadow_timeout_hours": "",
        "shadow_exit_rule_version": "",
        "trade_execution_gate": "blocked",
        "trade_execution_blockers": ["phase1_inactive"],
        "phase1_observation_gate": "blocked",
        "phase1_observation_type": "blocked",
        "phase1_observation_reasons": ["no_directional_setup"],
        "phase1b_lite_gate": "blocked",
        "phase1b_lite_type": "blocked",
        "phase1b_lite_reasons": ["not_evaluated"],
        "opportunity_gate": "blocked",
        "opportunity_type": "blocked",
        "opportunity_reasons": ["not_evaluated"],
        "paper_order_status": "",
    }


def run_cycle(cfg: Any | None = None, base_dir: Path | None = None) -> dict[str, Any]:
    base_dir = base_dir or _base_dir()
    cfg = cfg or load_config(base_dir)
    now_utc = datetime.now(tz=timezone.utc)
    now_jst = now_utc.astimezone(ZoneInfo(cfg.TIMEZONE))
    now_ms = int(now_utc.timestamp() * 1000)
    signal_id = now_utc.strftime("%Y%m%d_%H%M%S")

    update_heartbeat(base_dir, cfg.HEARTBEAT_FILE)
    cleanup_if_due(base_dir, cfg, now_utc)
    resend_pending_email(base_dir, cfg)

    fetch_cfg = _build_fetch_cfg(cfg)
    server_ms = get_server_time_ms(fetch_cfg)
    gap_sec = (server_ms - now_ms) / 1000.0

    df_4h = fetch_klines(fetch_cfg, "4h", cfg.FETCH_LIMIT_4H, server_time_ms=server_ms)
    df_1h = fetch_klines(fetch_cfg, "1h", cfg.FETCH_LIMIT_1H, server_time_ms=server_ms)
    df_15m = fetch_klines(fetch_cfg, "15m", cfg.FETCH_LIMIT_15M, server_time_ms=server_ms)

    if not validate_klines(df_4h, cfg.EMA_SLOW + 20):
        raise DataFetchError("4h data invalid")
    if not validate_klines(df_1h, cfg.EMA_SLOW + 20):
        raise DataFetchError("1h data invalid")
    if not validate_klines(df_15m, cfg.EMA_SLOW + 20):
        raise DataFetchError("15m data invalid")

    tf_4h = _prepare_tf(df_4h, cfg, cfg.SWING_N_4H)
    tf_1h = _prepare_tf(df_1h, cfg, cfg.SWING_N_1H)
    tf_15m = _prepare_tf(df_15m, cfg, cfg.SWING_N_15M)

    price = float(df_15m["close"].iloc[-1])
    atr_15m = float(tf_15m["atr"].iloc[-1])
    atr_ratio = calculate_atr_ratio(tf_15m["atr"], 50)
    funding_missing = False
    try:
        funding_rate_raw = fetch_funding_rate(fetch_cfg)
        funding_rate_pct = funding_rate_raw_to_pct(funding_rate_raw)
        funding_label = funding_rate_label(
            funding_rate_pct=funding_rate_pct,
            long_warning_pct=cfg.FUNDING_LONG_WARNING,
            long_prohibited_pct=cfg.FUNDING_LONG_PROHIBITED,
            short_warning_pct=cfg.FUNDING_SHORT_WARNING,
            short_prohibited_pct=cfg.FUNDING_SHORT_PROHIBITED,
        )
        funding_display = f"{funding_label} ({format_funding_pct(funding_rate_pct)})"
    except Exception:  # noqa: BLE001
        funding_missing = True
        funding_rate_raw = 0.0
        funding_rate_pct = 0.0
        funding_label = "取得失敗"
        funding_display = "取得失敗 (中立扱い)"
    market_structure = fetch_market_structure(cfg, base_dir=base_dir)

    per_tf_inputs = {
        "4h": {"df": df_4h, "swings": tf_4h["swings"], "structure": tf_4h["structure"]},
        "1h": {"df": df_1h, "swings": tf_1h["swings"], "structure": tf_1h["structure"]},
        "15m": {"df": df_15m, "swings": tf_15m["swings"], "structure": tf_15m["structure"]},
    }
    all_support_zones, all_resistance_zones = build_all_support_resistance(per_tf_inputs, atr_15m)
    support_zones, resistance_zones = build_support_resistance(per_tf_inputs, atr_15m)
    support_zones_nearest = select_nearest_directional_zones(price, all_support_zones, "support")
    resistance_zones_nearest = select_nearest_directional_zones(price, all_resistance_zones, "resistance")
    critical_zone = detect_critical_zone(price, all_support_zones, all_resistance_zones)

    regime_info = classify_market_regime(
        ema_alignment_4h=tf_4h["ema_alignment"],
        ema20_slope_4h=tf_4h["ema20_slope"],
        structure_4h=tf_4h["structure"],
        atr_ratio=atr_ratio,
        rsi_4h=float(tf_4h["rsi"].iloc[-1]),
        ema20_4h=float(tf_4h["ema_fast"].iloc[-1]),
        ema20_prev_4h=float(tf_4h["ema_fast"].iloc[-2]),
        ema50_4h=float(tf_4h["ema_mid"].iloc[-1]),
        ema50_series_4h=[float(v) for v in tf_4h["ema_mid"].tail(10).tolist()],
        atr_4h=float(tf_4h["atr"].iloc[-1]),
    )
    market_regime = regime_info["market_regime"]
    transition_direction = regime_info["transition_direction"]

    near_support = nearest_zone_distance(price, all_support_zones) <= atr_15m * 0.5
    near_resistance = nearest_zone_distance(price, all_resistance_zones) <= atr_15m * 0.5
    recent_high, recent_low = previous_breakout_levels(df_15m, int(cfg.BREAKOUT_LOOKBACK_BARS))
    breakout_up = recent_high is not None and price > recent_high
    breakout_down = recent_low is not None and price < recent_low
    range_high = recent_high if recent_high is not None else price
    range_low = recent_low if recent_low is not None else price
    range_mid = (range_high + range_low) / 2
    in_range_center = abs(price - range_mid) <= atr_15m * 0.5
    volume_structure = analyze_volume_structure(df_15m, cfg)
    market_map = build_market_map(
        price=price,
        atr=atr_15m,
        per_tf_inputs=per_tf_inputs,
        volume_info=volume_structure,
        breakout_up=breakout_up,
        breakout_down=breakout_down,
        cfg=cfg,
    )

    pre_long_setup, _ = build_setup(
        side="long",
        price=price,
        atr=atr_15m,
        support_zones=all_support_zones,
        resistance_zones=all_resistance_zones,
        sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
        min_rr_ratio=0.0,
        confidence=100,
        confidence_min=0,
        atr_ratio=atr_ratio,
        atr_ratio_min=0.0,
        atr_ratio_max=999.0,
        funding_rate=funding_rate_pct,
        funding_warning=999.0,
        funding_prohibited=999.0,
        trigger_ready=False,
        warning_count=0,
    )
    pre_short_setup, _ = build_setup(
        side="short",
        price=price,
        atr=atr_15m,
        support_zones=all_support_zones,
        resistance_zones=all_resistance_zones,
        sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
        min_rr_ratio=0.0,
        confidence=100,
        confidence_min=0,
        atr_ratio=atr_ratio,
        atr_ratio_min=0.0,
        atr_ratio_max=999.0,
        funding_rate=funding_rate_pct,
        funding_warning=-999.0,
        funding_prohibited=-999.0,
        trigger_ready=False,
        warning_count=0,
    )

    score_info = compute_scores(
        {
            "market_regime": market_regime,
            "ema_alignment_4h": tf_4h["ema_alignment"],
            "ema20_slope_4h": tf_4h["ema20_slope"],
            "structure_4h": tf_4h["structure"],
            "structure_1h": tf_1h["structure"],
            "price": price,
            "ema50_4h": float(tf_4h["ema_mid"].iloc[-1]),
            "rsi_15m": float(tf_15m["rsi"].iloc[-1]),
            "volume_ratio": float(tf_15m["volume_ratio"].iloc[-1]),
            "atr_ratio": atr_ratio,
            "funding_rate": funding_rate_pct,
            "rr_long": pre_long_setup["rr_estimate"],
            "rr_short": pre_short_setup["rr_estimate"],
            "near_support": near_support,
            "near_resistance": near_resistance,
            "breakout_up": breakout_up,
            "breakout_down": breakout_down,
            "in_range_center": in_range_center,
            "transition_direction": transition_direction,
            "signals_15m": tf_15m["signal"],
            "market_map": market_map,
        },
        cfg,
    )
    bias = score_info["bias"]

    liquidity_info = analyze_liquidity(
        df_15m=df_15m,
        swings=tf_15m["swings"],
        price=price,
        atr=atr_15m,
        equal_threshold_pct=cfg.LIQUIDITY_EQUAL_THRESHOLD_PCT,
    )
    liquidation_info = analyze_liquidation_clusters(
        price=price,
        atr=atr_15m,
        liquidation_events=market_structure.liquidation_events,
    )
    oi_cvd_info = analyze_oi_cvd(
        oi_value=market_structure.oi_value,
        oi_change_pct=market_structure.oi_change_pct,
        oi_trend_values=market_structure.oi_trend_values,
        cvd_series=market_structure.cvd_series,
        price_series=[float(v) for v in df_15m["close"].tail(12).tolist()],
    )
    orderbook_info = analyze_orderbook(
        bids=market_structure.orderbook_bids,
        asks=market_structure.orderbook_asks,
        price=price,
    )
    position_risk = evaluate_position_risk(
        bias=bias,
        price=price,
        atr=atr_15m,
        liquidity_info=liquidity_info,
        liquidation_info=liquidation_info,
        oi_cvd_info=oi_cvd_info,
        orderbook_info=orderbook_info,
        high_threshold=cfg.POSITION_RISK_HIGH_THRESHOLD,
        medium_threshold=cfg.POSITION_RISK_MEDIUM_THRESHOLD,
    )

    pullback_depth_atr = abs(price - float(tf_4h["ema_mid"].iloc[-1])) / max(float(tf_4h["atr"].iloc[-1]), 1e-9)
    reversal_risk_flag = (
        float(tf_15m["rsi"].iloc[-1]) > 75
        or float(tf_15m["rsi"].iloc[-1]) < 25
        or abs(float(df_15m["close"].iloc[-1]) - float(df_15m["open"].iloc[-1])) < atr_15m * 0.08
    )
    phase = determine_phase(
        bias=bias,
        market_regime=market_regime,
        pullback_depth_atr=pullback_depth_atr,
        breakout_confirmed=(breakout_up or breakout_down)
        and float(tf_15m["volume_ratio"].iloc[-1]) >= cfg.TRIGGER_VOLUME_RATIO,
        reversal_risk_flag=reversal_risk_flag,
        price=price,
        ema50=float(tf_4h["ema_mid"].iloc[-1]),
        ema200=float(tf_4h["ema_slow"].iloc[-1]),
    )

    rr_for_conf = (
        pre_long_setup["rr_estimate"]
        if bias == "long"
        else pre_short_setup["rr_estimate"]
        if bias == "short"
        else max(pre_long_setup["rr_estimate"], pre_short_setup["rr_estimate"])
    )
    opposite_gap = zone_gap_to_opposite(
        price,
        bias if bias in {"long", "short"} else "long",
        all_support_zones,
        all_resistance_zones,
    )
    opposite_gap_atr = opposite_gap / atr_15m if atr_15m > 0 and opposite_gap != float("inf") else 10.0

    directional_triggers = _directional_volume_triggers(
        volume_ratio=float(tf_15m["volume_ratio"].iloc[-1]),
        volume_threshold=float(cfg.TRIGGER_VOLUME_RATIO),
        candle_open=float(df_15m["open"].iloc[-1]),
        candle_high=float(df_15m["high"].iloc[-1]),
        candle_low=float(df_15m["low"].iloc[-1]),
        candle_close=float(df_15m["close"].iloc[-1]),
        range_high=float(range_high),
        range_low=float(range_low),
        breakout_up=bool(breakout_up),
        breakout_down=bool(breakout_down),
        market_map=market_map,
    )
    trigger_up = bool(directional_triggers["trigger_up"])
    trigger_down = bool(directional_triggers["trigger_down"])
    confidence_inputs = {
        "bias": bias,
        "long_display_score": score_info["long_display_score"],
        "short_display_score": score_info["short_display_score"],
        "signals_4h": tf_4h["signal"],
        "signals_1h": tf_1h["signal"],
        "signals_15m": tf_15m["signal"],
        "market_regime": market_regime,
        "phase": phase,
        "rr_estimate": rr_for_conf,
        "opposite_gap_atr": opposite_gap_atr,
        "critical_zone": critical_zone,
        "score_warning_flags": score_info["warning_flags"] + (["Critical_zone_warning"] if critical_zone else []),
        "position_risk_flags": position_risk["risk_flags"],
        "prelabel": position_risk["prelabel"],
        "primary_setup_status": "none",
    }
    confidence_details = compute_confidence_details(confidence_inputs, cfg)
    preliminary_confidence = int(confidence_details["confidence"])

    def _build_directional_setups(selected_confidence: int) -> tuple[dict[str, Any], list[str], dict[str, Any], list[str]]:
        long_setup_local, long_flags_local = build_setup(
            side="long",
            price=price,
            atr=atr_15m,
            support_zones=all_support_zones,
            resistance_zones=all_resistance_zones,
            sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
            min_rr_ratio=cfg.MIN_RR_RATIO,
            confidence=selected_confidence,
            confidence_min=cfg.CONFIDENCE_LONG_MIN,
            atr_ratio=atr_ratio,
            atr_ratio_min=cfg.MIN_ACCEPTABLE_ATR_RATIO,
            atr_ratio_max=cfg.MAX_ACCEPTABLE_ATR_RATIO,
            funding_rate=funding_rate_pct,
            funding_warning=cfg.FUNDING_LONG_WARNING,
            funding_prohibited=cfg.FUNDING_LONG_PROHIBITED,
            trigger_ready=trigger_up,
            warning_count=len(score_info["warning_flags"]),
        )
        short_setup_local, short_flags_local = build_setup(
            side="short",
            price=price,
            atr=atr_15m,
            support_zones=all_support_zones,
            resistance_zones=all_resistance_zones,
            sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
            min_rr_ratio=cfg.MIN_RR_RATIO,
            confidence=selected_confidence,
            confidence_min=cfg.CONFIDENCE_SHORT_MIN,
            atr_ratio=atr_ratio,
            atr_ratio_min=cfg.MIN_ACCEPTABLE_ATR_RATIO,
            atr_ratio_max=cfg.MAX_ACCEPTABLE_ATR_RATIO,
            funding_rate=funding_rate_pct,
            funding_warning=cfg.FUNDING_SHORT_WARNING,
            funding_prohibited=cfg.FUNDING_SHORT_PROHIBITED,
            trigger_ready=trigger_down,
            warning_count=len(score_info["warning_flags"]),
        )
        long_setup_local = apply_prelabel_to_setup(long_setup_local, position_risk["prelabel"], "long", bias)
        short_setup_local = apply_prelabel_to_setup(short_setup_local, position_risk["prelabel"], "short", bias)
        long_setup_local, long_precision_flags = refine_execution_precision(
            long_setup_local,
            side="long",
            market_map=market_map,
            signal_15m=tf_15m["signal"],
            breakout_up=breakout_up,
            breakout_down=breakout_down,
        )
        short_setup_local, short_precision_flags = refine_execution_precision(
            short_setup_local,
            side="short",
            market_map=market_map,
            signal_15m=tf_15m["signal"],
            breakout_up=breakout_up,
            breakout_down=breakout_down,
        )
        return (
            long_setup_local,
            sorted(set(long_flags_local + long_precision_flags)),
            short_setup_local,
            sorted(set(short_flags_local + short_precision_flags)),
        )

    long_setup, long_flags, short_setup, short_flags = _build_directional_setups(preliminary_confidence)
    primary_setup_side, primary_setup_status = choose_primary_setup(bias, long_setup, short_setup)
    confidence_inputs["primary_setup_status"] = primary_setup_status
    confidence_details = compute_confidence_details(confidence_inputs, cfg)
    confidence = int(confidence_details["confidence"])

    long_setup, long_flags, short_setup, short_flags = _build_directional_setups(confidence)
    primary_setup_side, primary_setup_status = choose_primary_setup(bias, long_setup, short_setup)
    primary_setup = (
        long_setup if primary_setup_side == "long" else short_setup if primary_setup_side == "short" else {}
    )
    effective_prelabel = reconcile_prelabel_with_setup(position_risk["prelabel"], primary_setup_status)
    result_flags = assemble_result_flags(
        bias=bias,
        score_no_trade_flags=score_info["no_trade_flags"],
        score_warning_flags=score_info["warning_flags"],
        long_setup_flags=long_flags,
        short_setup_flags=short_flags,
        position_risk_flags=position_risk["risk_flags"],
        critical_zone=critical_zone,
    )
    result_flags["risk_flags"] = derive_additional_risk_flags(
        bias=bias,
        market_regime=market_regime,
        transition_direction=transition_direction,
        primary_setup_status=primary_setup_status,
        primary_setup_reason=str(primary_setup.get("status_reason_code", "")),
        risk_flags=result_flags["risk_flags"],
        long_factor_breakdown=score_info["long_factor_breakdown"],
        market_map_flags=market_map["flags"],
    )

    qualitative_context = build_qualitative_context(
        now_ms=now_ms,
        timezone_name=cfg.TIMEZONE,
        df_15m=df_15m,
        market_regime=market_regime,
        bias=bias,
        blocking_flags=result_flags["no_trade_flags"],
        price=price,
        ema50=float(tf_15m["ema_mid"].iloc[-1]),
        atr=atr_15m,
    )

    agreement_with_machine = compute_machine_agreement(
        bias=bias,
        market_regime=market_regime,
        ema_alignment_4h=tf_4h["ema_alignment"],
        price=price,
        support_zones=all_support_zones,
        resistance_zones=all_resistance_zones,
        volume_ratio=float(tf_15m["volume_ratio"].iloc[-1]),
        funding_rate=funding_rate_pct,
    )

    core_result: dict[str, Any] = {
        "signal_id": signal_id,
        "timestamp_utc": now_utc.isoformat().replace("+00:00", "Z"),
        "timestamp_jst": now_jst.isoformat(),
        "system_label": str(getattr(cfg, "SYSTEM_LABEL", "")).strip(),
        "system_mode_label": _build_system_mode_label(cfg),
        "current_price": _round2(price),
        "was_notified": False,
        "notified_at_utc": "",
        "server_time_gap_sec": round(gap_sec, 2),
        "bias": bias,
        "phase": phase,
        "market_regime": market_regime,
        "transition_direction": transition_direction,
        "signals_4h": tf_4h["signal"],
        "signals_1h": tf_1h["signal"],
        "signals_15m": tf_15m["signal"],
        "long_score": score_info["long_display_score"],
        "short_score": score_info["short_display_score"],
        "long_display_score": score_info["long_display_score"],
        "short_display_score": score_info["short_display_score"],
        "long_raw_score": _round_optional(score_info["long_raw_score"], 4),
        "short_raw_score": _round_optional(score_info["short_raw_score"], 4),
        "score_gap": score_info["score_gap"],
        "score_factor_breakdown_long": score_info["long_factor_breakdown"],
        "score_factor_breakdown_short": score_info["short_factor_breakdown"],
        "top_positive_factors": score_info["top_positive_factors"],
        "top_negative_factors": score_info["top_negative_factors"],
        "confidence": confidence,
        "agreement_with_machine": agreement_with_machine,
        "prelabel": effective_prelabel,
        "prelabel_primary_reason": position_risk["primary_reason"],
        "location_risk": position_risk["location_risk"],
        "critical_zone": critical_zone,
        "support_zones": support_zones_nearest,
        "resistance_zones": resistance_zones_nearest,
        "support_zones_by_strength": support_zones,
        "resistance_zones_by_strength": resistance_zones,
        "support_zones_all": all_support_zones,
        "resistance_zones_all": all_resistance_zones,
        "market_map": market_map,
        "market_map_primary_state": market_map["market_map_primary_state"],
        "market_map_flags": market_map["flags"],
        "nearest_major_support": market_map["nearest_major_support"],
        "nearest_major_resistance": market_map["nearest_major_resistance"],
        "active_level_role": market_map["active_level_role"],
        "level_flip_state": market_map["level_flip_state"],
        "failed_breakout_state": market_map["failed_breakout_state"],
        "trend_flip_state": market_map["trend_flip_state"],
        "chart_snapshot": _build_chart_snapshot(df_4h, df_1h, df_15m),
        "long_setup": long_setup,
        "short_setup": short_setup,
        "primary_setup_side": primary_setup_side,
        "primary_setup_status": primary_setup_status,
        "primary_setup_reason": primary_setup.get("status_reason_code", ""),
        "execution_precision_action": primary_setup.get("execution_precision_action", ""),
        "execution_precision_flags": primary_setup.get("execution_precision_flags", []),
        "execution_precision_reason": primary_setup.get("execution_precision_reason", ""),
        "invalid_reason": primary_setup.get("invalid_reason", ""),
        "primary_entry_mid": primary_setup.get("entry_mid", ""),
        "primary_stop_loss": primary_setup.get("stop_loss", ""),
        "primary_tp1": primary_setup.get("tp1", ""),
        "primary_tp2": primary_setup.get("tp2", ""),
        **_phase1_defaults(),
        "funding_rate": _round_optional(funding_rate_raw, 8),
        "funding_rate_raw": _round_optional(funding_rate_raw, 8),
        "funding_rate_pct": _round_optional(funding_rate_pct, 4),
        "funding_rate_label": funding_label,
        "funding_rate_display": funding_display,
        "atr_15m_value": _round_optional(atr_15m, 4),
        "atr_ratio": _round2(atr_ratio),
        "volume_ratio": _round2(float(tf_15m["volume_ratio"].iloc[-1])),
        "liquidity_above": _round_optional(liquidity_info.get("liquidity_above")),
        "liquidity_below": _round_optional(liquidity_info.get("liquidity_below")),
        "nearest_liquidity_above_price": _round_optional(liquidity_info.get("nearest_liquidity_above_price")),
        "nearest_liquidity_below_price": _round_optional(liquidity_info.get("nearest_liquidity_below_price")),
        "liquidity_swept_recently": liquidity_info.get("liquidity_swept_recently"),
        "liquidation_above": _round_optional(liquidation_info.get("liquidation_above"), 4),
        "liquidation_below": _round_optional(liquidation_info.get("liquidation_below"), 4),
        "largest_liquidation_price": _round_optional(liquidation_info.get("largest_liquidation_price")),
        "distance_to_largest_liquidation": _round_optional(liquidation_info.get("distance_to_largest_liquidation")),
        "liquidation_density_above": _round_optional(liquidation_info.get("liquidation_density_above"), 4),
        "liquidation_density_below": _round_optional(liquidation_info.get("liquidation_density_below"), 4),
        "oi_value": _round_optional(oi_cvd_info.get("oi_value"), 4),
        "oi_change_pct": _round_optional(oi_cvd_info.get("oi_change_pct")),
        "cvd_value": _round_optional(oi_cvd_info.get("cvd_value"), 4),
        "cvd_slope": _round_optional(oi_cvd_info.get("cvd_slope"), 4),
        "cvd_price_divergence": oi_cvd_info.get("cvd_price_divergence"),
        "orderbook_bid_wall_price": _round_optional(orderbook_info.get("orderbook_bid_wall_price")),
        "orderbook_ask_wall_price": _round_optional(orderbook_info.get("orderbook_ask_wall_price")),
        "orderbook_bid_wall_size": _round_optional(orderbook_info.get("orderbook_bid_wall_size"), 4),
        "orderbook_ask_wall_size": _round_optional(orderbook_info.get("orderbook_ask_wall_size"), 4),
        "orderbook_bias": orderbook_info.get("orderbook_bias"),
        "breakout_up": breakout_up,
        "breakout_down": breakout_down,
        "trigger_volume_ratio_threshold": _round_optional(cfg.TRIGGER_VOLUME_RATIO, 4),
        "rr_estimate": _round2(
            long_setup["rr_estimate"] if bias == "long" else short_setup["rr_estimate"] if bias == "short" else max(long_setup["rr_estimate"], short_setup["rr_estimate"])
        ),
        "ai_advice": None,
        "ai_audit": None,
        "ai_audit_status": "skipped_non_notify",
        "ai_decision": "",
        "ai_confidence": "",
        "ai_audit_verdict": "",
        "ai_audit_agreement": "",
        "ai_audit_reason": "",
        "ai_audit_unique_risks": [],
        "ai_audit_next_review_focus": "",
        "raw_confidence": confidence_details["raw_confidence"],
        "confidence_direction_shadow": confidence_details["confidence_direction_shadow"],
        "confidence_execution_shadow": confidence_details["confidence_execution_shadow"],
        "confidence_wait_shadow": confidence_details["confidence_wait_shadow"],
        "confidence_components": confidence_details["confidence_components"],
        "warning_flags": result_flags["warning_flags"],
        "no_trade_flags": result_flags["no_trade_flags"],
        "risk_flags": result_flags["risk_flags"],
        "summary_variant": SUMMARY_VARIANT,
        "advice_variant": ADVICE_VARIANT,
        "prompt_variant": PROMPT_VARIANT,
        "evaluation_trace_version": EVALUATION_TRACE_VERSION,
        "signal_tier": "normal",
        "signal_badge": "",
        "signal_tier_reason_codes": [],
        "market_structure_missing_fields": market_structure.missing_fields or [],
        "data_missing_fields": [],
        "data_quality_flag": "ok",
        "notify_reason_codes": [],
        "suppress_reason_codes": [],
        "reason_for_notification": [],
        "notification_kind": "none",
        "notification_context": {},
        "detail_page_enabled": False,
        "detail_page_status": "disabled",
        "detail_page_url": "",
        "detail_page_local_path": "",
        "detail_page_published_at_utc": "",
    }
    core_result["display_context"] = build_display_context(core_result)

    data_missing_fields = _normalize_missing_data_fields(
        market_structure.missing_fields or [],
        ai_missing=False,
        funding_missing=funding_missing,
    )
    core_result["data_missing_fields"] = data_missing_fields
    core_result["data_quality_flag"] = _data_quality_flag(data_missing_fields)

    signal_tier_info = compute_signal_tier(core_result, cfg)
    core_result["signal_tier"] = signal_tier_info["tier"]
    core_result["signal_tier_reason_codes"] = signal_tier_info["reason_codes"]
    core_result["signal_badge"] = signal_tier_badge(core_result["signal_tier"])

    if primary_setup_side in {"long", "short"}:
        phase1_activation = determine_phase1_activation(
            bias=bias,
            primary_setup_side=primary_setup_side,
            primary_setup_status=primary_setup_status,
            data_quality_flag=core_result["data_quality_flag"],
            entry_price=float(primary_setup.get("entry_mid", 0.0) or 0.0),
            stop_loss_price=float(primary_setup.get("stop_loss", 0.0) or 0.0),
        )
        loss_streak = load_loss_streak(
            base_dir=base_dir,
            fallback_streak=int(cfg.PHASE1_LOSS_STREAK),
        )
        position_size_plan = build_position_size_plan(
            account_balance=float(cfg.PHASE1_ACCOUNT_BALANCE_USD),
            entry_price=float(primary_setup.get("entry_mid", 0.0) or 0.0),
            stop_loss_price=float(primary_setup.get("stop_loss", 0.0) or 0.0),
            signal_tier=core_result["signal_tier"],
            loss_streak=loss_streak,
            base_risk_pct=float(cfg.PHASE1_BASE_RISK_PCT),
            loss_streak_step_pct=float(cfg.PHASE1_LOSS_STREAK_STEP_PCT),
            min_risk_pct=float(cfg.PHASE1_MIN_RISK_PCT),
            max_position_size_usd=float(cfg.PHASE1_MAX_POSITION_SIZE_USD),
        )
        exit_plan = build_exit_plan(
            side=primary_setup_side,
            entry_price=float(primary_setup.get("entry_mid", 0.0) or 0.0),
            stop_loss_price=float(primary_setup.get("stop_loss", 0.0) or 0.0),
            atr=atr_15m,
            tp1_rr_multiple=float(cfg.PHASE1_TP1_RR_MULTIPLE),
            tp2_rr_multiple=float(cfg.PHASE1_TP2_RR_MULTIPLE),
            trail_atr_multiplier=float(cfg.PHASE1_TRAIL_ATR_MULTIPLIER),
            timeout_hours=int(cfg.PHASE1_TIMEOUT_HOURS),
            exit_rule_version="phase1_v0",
        )
        shadow_exit_plan = build_shadow_exit_plan(
            side=primary_setup_side,
            entry_price=float(primary_setup.get("entry_mid", 0.0) or 0.0),
            stop_loss_price=float(primary_setup.get("stop_loss", 0.0) or 0.0),
            atr=atr_15m,
            trail_atr_multiplier=float(cfg.PHASE1_TRAIL_ATR_MULTIPLIER),
            timeout_hours=int(cfg.PHASE1_TIMEOUT_HOURS),
        )
        execution_gate = determine_trade_execution_gate(
            phase1_active=bool(phase1_activation["phase1_active"]),
            primary_setup_status=primary_setup_status,
            primary_setup_reason=str(primary_setup.get("status_reason_code", "")),
            data_quality_flag=core_result["data_quality_flag"],
            no_trade_flags=result_flags["no_trade_flags"],
            confidence_execution_shadow=confidence_details["confidence_execution_shadow"],
            confidence_wait_shadow=confidence_details["confidence_wait_shadow"],
        )
        observation_gate = determine_phase1_observation_gate(
            bias=bias,
            primary_setup_side=primary_setup_side,
            primary_setup_status=primary_setup_status,
            primary_setup_reason=str(primary_setup.get("status_reason_code", "")),
            prelabel=effective_prelabel,
            data_quality_flag=core_result["data_quality_flag"],
            no_trade_flags=result_flags["no_trade_flags"],
            risk_flags=result_flags["risk_flags"],
            confidence_direction_shadow=confidence_details["confidence_direction_shadow"],
            confidence_execution_shadow=confidence_details["confidence_execution_shadow"],
            confidence_wait_shadow=confidence_details["confidence_wait_shadow"],
            secondary_setup_status=str(short_setup.get("status", "")) if bias == "long" else str(long_setup.get("status", "")),
        )
        phase1b_lite_gate = determine_phase1b_lite_gate(
            phase1_observation_type=observation_gate["phase1_observation_type"],
            primary_setup_status=primary_setup_status,
            primary_setup_reason=str(primary_setup.get("status_reason_code", "")),
            prelabel=effective_prelabel,
            data_quality_flag=core_result["data_quality_flag"],
            no_trade_flags=result_flags["no_trade_flags"],
            risk_flags=result_flags["risk_flags"],
            confidence_direction_shadow=confidence_details["confidence_direction_shadow"],
            confidence_execution_shadow=confidence_details["confidence_execution_shadow"],
            confidence_wait_shadow=confidence_details["confidence_wait_shadow"],
        )
        opportunity_gate = determine_opportunity_gate(
            bias=bias,
            primary_setup_side=primary_setup_side,
            primary_setup_status=primary_setup_status,
            data_quality_flag=core_result["data_quality_flag"],
            no_trade_flags=result_flags["no_trade_flags"],
            risk_flags=result_flags["risk_flags"],
            market_map_flags=market_map["flags"],
            phase1_observation_gate=observation_gate["phase1_observation_gate"],
            phase1_observation_type=observation_gate["phase1_observation_type"],
            phase1b_lite_gate=phase1b_lite_gate["phase1b_lite_gate"],
            phase1b_lite_type=phase1b_lite_gate["phase1b_lite_type"],
            trade_execution_gate=execution_gate["trade_execution_gate"],
            confidence_direction_shadow=confidence_details["confidence_direction_shadow"],
            confidence_execution_shadow=confidence_details["confidence_execution_shadow"],
            confidence_wait_shadow=confidence_details["confidence_wait_shadow"],
        )
        core_result["loss_streak_at_entry"] = loss_streak
        core_result.update(phase1_activation)
        core_result.update(position_size_plan)
        core_result.update(exit_plan)
        core_result.update(shadow_exit_plan)
        core_result.update(execution_gate)
        core_result.update(observation_gate)
        core_result.update(phase1b_lite_gate)
        core_result.update(opportunity_gate)
        if core_result["trade_execution_gate"] == "pass":
            core_result["paper_order_status"] = "planned"

    active_trade_plan = build_active_trade_plan(
        current_price=float(core_result.get("current_price", 0.0) or 0.0),
        bias=bias,
        market_regime=market_regime,
        long_setup=long_setup,
        short_setup=short_setup,
        confidence_direction_shadow=confidence_details["confidence_direction_shadow"],
        confidence_execution_shadow=confidence_details["confidence_execution_shadow"],
        confidence_wait_shadow=confidence_details["confidence_wait_shadow"],
        risk_flags=result_flags["risk_flags"],
        market_map_flags=market_map["flags"],
        no_trade_flags=result_flags["no_trade_flags"],
        data_quality_flag=core_result["data_quality_flag"],
        breakout_up=breakout_up,
        breakout_down=breakout_down,
        volume_ratio=float(tf_15m["volume_ratio"].iloc[-1]),
        trigger_volume_ratio_threshold=float(cfg.TRIGGER_VOLUME_RATIO),
    )
    core_result["active_trade_plan"] = active_trade_plan
    core_result["active_primary_action"] = active_trade_plan.get("primary_action", "NO_ACTION")
    core_result["active_headline"] = active_trade_plan.get("headline", "")

    last_result = load_json(get_last_result_path(base_dir))
    last_notified = load_json(get_last_notified_path(base_dir))
    last_attention_notified = load_json(get_last_attention_notified_path(base_dir))
    notify_info = should_notify(core_result, last_result, last_notified, last_attention_notified, cfg)
    notify = bool(notify_info["notify"])
    core_result["notify_reason_codes"] = notify_info["notify_reason_codes"]
    core_result["suppress_reason_codes"] = notify_info["suppress_reason_codes"]
    core_result["reason_for_notification"] = notify_info["notify_reason_codes"]
    core_result["notification_kind"] = notify_info["notification_kind"]
    core_result["notification_context"] = build_notification_context(core_result)
    advice_provider_used = getattr(cfg, "AI_ADVICE_PROVIDER", "api")
    if notify:
        ai_advice, advice_provider_used = request_ai_advice(
            provider=cfg.AI_ADVICE_PROVIDER,
            api_key=cfg.OPENAI_API_KEY,
            model=cfg.OPENAI_ADVICE_MODEL,
            cli_command=cfg.AI_ADVICE_CLI_COMMAND,
            timeout_sec=cfg.AI_TIMEOUT_SEC,
            retry_count=cfg.AI_RETRY_COUNT,
            base_dir=base_dir,
            machine_payload=core_result,
            qualitative_payload=qualitative_context,
        )
        core_result["ai_advice"] = ai_advice
        core_result["ai_audit"] = ai_advice
        core_result["ai_advice_provider_used"] = _normalize_provider_label(advice_provider_used)
        if isinstance(ai_advice, dict):
            core_result["ai_audit_status"] = "completed"
            core_result["ai_decision"] = ai_advice.get("decision", "")
            core_result["ai_confidence"] = ai_advice.get("confidence", "")
            core_result["advice_variant"] = ai_advice.get("advice_variant", ADVICE_VARIANT)
            core_result["ai_audit_verdict"] = ai_advice.get("verdict", "")
            core_result["ai_audit_agreement"] = ai_advice.get("agreement", "")
            core_result["ai_audit_reason"] = ai_advice.get("reason", "")
            core_result["ai_audit_unique_risks"] = list(ai_advice.get("unique_risks", []) or [])
            core_result["ai_audit_next_review_focus"] = ai_advice.get("next_review_focus", "")
        else:
            core_result["ai_audit_status"] = "unavailable"
    else:
        core_result["ai_advice_provider_used"] = _normalize_provider_label(advice_provider_used)

    summary_body, summary_provider_used = build_summary_body(
        provider=cfg.AI_SUMMARY_PROVIDER,
        api_key=cfg.OPENAI_API_KEY,
        model=cfg.OPENAI_SUMMARY_MODEL,
        cli_command=cfg.AI_SUMMARY_CLI_COMMAND,
        timeout_sec=cfg.AI_SUMMARY_TIMEOUT_SEC,
        retry_count=cfg.AI_RETRY_COUNT,
        base_dir=base_dir,
        result_payload=core_result,
    )
    core_result["ai_summary_provider_used"] = _normalize_provider_label(summary_provider_used)
    core_result["system_mode_label"] = _build_system_mode_label(cfg)
    core_result["display_context"] = build_display_context(core_result)
    core_result["notification_context"] = build_notification_context(core_result)
    core_result["summary_subject"] = build_summary_subject(core_result)
    core_result["summary_body"] = summary_body
    core_result["evaluation_trace"] = build_evaluation_trace(
        result=core_result,
        score_info=score_info,
        position_risk=position_risk,
        confidence_details=confidence_details,
        display_context=core_result["display_context"],
    )

    if notify:
        if detail_page_enabled(cfg, core_result):
            try:
                detail_page_info = publish_notification_detail(base_dir, cfg, core_result)
                core_result["summary_body"] = append_detail_page_url(
                    core_result["summary_body"],
                    detail_page_info.get("detail_page_url", ""),
                )
                core_result.update(detail_page_info)
            except Exception as exc:  # noqa: BLE001
                core_result["detail_page_enabled"] = True
                core_result["detail_page_status"] = "failed"
                _error_log(base_dir, "notification_detail_page_error", f"{exc}\n{traceback.format_exc()}")
        notify_path = (
            get_last_attention_notified_path(base_dir)
            if core_result["notification_kind"] == "attention"
            else get_last_notified_path(base_dir)
        )
        if cfg.DRYRUN_MODE:
            core_result["was_notified"] = True
            core_result["notified_at_utc"] = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
            save_json(notify_path, core_result)
        else:
            try:
                send_email(
                    smtp_host=cfg.SMTP_HOST,
                    smtp_port=cfg.SMTP_PORT,
                    smtp_user=cfg.SMTP_USER,
                    smtp_password=cfg.SMTP_PASSWORD,
                    mail_from=cfg.MAIL_FROM,
                    mail_to=cfg.MAIL_TO,
                    subject=core_result["summary_subject"],
                    body=core_result["summary_body"],
                )
                core_result["was_notified"] = True
                core_result["notified_at_utc"] = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
                save_json(notify_path, core_result)
            except Exception as exc:  # noqa: BLE001
                save_pending_email(base_dir, core_result["summary_subject"], core_result["summary_body"])
                _error_log(base_dir, "smtp_error", f"{exc}\n{traceback.format_exc()}")

    persisted_result = dict(core_result)
    persisted_result.update(
        build_chart_pattern_shadow(
            price=price,
            atr=atr_15m,
            df_15m=df_15m,
            swings_15m=tf_15m["swings"],
            breakout_up=breakout_up,
            breakout_down=breakout_down,
            support_zones_all=sort_zones_by_distance(price, all_support_zones),
            resistance_zones_all=sort_zones_by_distance(price, all_resistance_zones),
            raw_missing_fields=market_structure.missing_fields or [],
            cfg=cfg,
        )
    )

    save_signal_snapshot(base_dir, persisted_result)
    append_trade_log(base_dir, persisted_result)
    append_active_plan_candidates(base_dir, persisted_result)
    if persisted_result.get("phase1_observation_gate") == "pass":
        append_observation_paper_order(base_dir, persisted_result)
    if persisted_result.get("phase1b_lite_gate") == "pass":
        append_phase1b_lite_paper_order(base_dir, persisted_result)
    if persisted_result.get("opportunity_gate") == "pass":
        append_paper_position(base_dir, persisted_result)
    if persisted_result.get("paper_order_status") == "planned":
        append_paper_order(base_dir, persisted_result)
    save_json(get_last_result_path(base_dir), persisted_result)

    return persisted_result


def _run_cycle_safe(cfg: Any, base_dir: Path) -> None:
    try:
        run_cycle(cfg, base_dir)
    except Exception as exc:  # noqa: BLE001
        _error_log(base_dir, "cycle_error", f"{exc}\n{traceback.format_exc()}")


def main() -> None:
    import schedule

    base_dir = _base_dir()
    cfg = load_config(base_dir)
    for report_time in cfg.REPORT_TIMES:
        schedule.every().day.at(report_time).do(_run_cycle_safe, cfg, base_dir)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
