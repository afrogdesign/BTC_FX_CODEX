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
from src.analysis.liquidation import analyze_liquidation_clusters
from src.analysis.liquidity import analyze_liquidity
from src.analysis.oi_cvd import analyze_oi_cvd
from src.analysis.orderbook import analyze_orderbook
from src.analysis.position_risk import apply_prelabel_to_setup, evaluate_position_risk
from src.analysis.confidence import compute_confidence, compute_machine_agreement
from src.analysis.phase import determine_phase
from src.analysis.qualitative import build_qualitative_context
from src.analysis.regime import classify_market_regime
from src.analysis.rr import build_setup, choose_primary_setup
from src.analysis.scoring import compute_scores
from src.analysis.structure import calc_tf_signal, classify_structure, detect_swings
from src.analysis.support_resistance import (
    build_support_resistance,
    detect_critical_zone,
    nearest_zone_distance,
    zone_gap_to_opposite,
)
from src.data.fetcher import DataFetchError, FetchConfig, fetch_funding_rate, fetch_klines, get_server_time_ms
from src.data.exchange_fetcher import fetch_market_structure
from src.data.validator import validate_klines
from src.indicators.atr import calculate_atr, calculate_atr_ratio
from src.indicators.ema import calculate_ema, get_ema20_slope, get_ema_alignment
from src.indicators.rsi import calculate_rsi
from src.indicators.volume import calculate_volume_ratio
from src.notification.email_sender import resend_pending_email, save_pending_email, send_email
from src.notification.trigger import should_notify
from src.storage.cleanup import cleanup_if_due
from src.storage.csv_logger import append_trade_log
from src.storage.json_store import (
    get_last_notified_path,
    get_last_result_path,
    load_json,
    save_json,
    save_signal_snapshot,
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


def run_cycle(cfg: Any | None = None, base_dir: Path | None = None) -> dict[str, Any]:
    base_dir = base_dir or _base_dir()
    cfg = cfg or load_config(base_dir)
    now_utc = datetime.now(tz=timezone.utc)
    now_jst = now_utc.astimezone(ZoneInfo(cfg.TIMEZONE))
    now_ms = int(now_utc.timestamp() * 1000)

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
    funding_rate = fetch_funding_rate(fetch_cfg)
    market_structure = fetch_market_structure(cfg, base_dir=base_dir)

    support_zones, resistance_zones = build_support_resistance(
        {"4h": {"df": df_4h, "swings": tf_4h["swings"]}, "1h": {"df": df_1h, "swings": tf_1h["swings"]}, "15m": {"df": df_15m, "swings": tf_15m["swings"]}},
        atr_15m,
    )
    critical_zone = detect_critical_zone(price, support_zones, resistance_zones)

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

    near_support = nearest_zone_distance(price, support_zones) <= atr_15m * 0.5
    near_resistance = nearest_zone_distance(price, resistance_zones) <= atr_15m * 0.5
    recent_high = float(df_15m["high"].tail(20).max())
    recent_low = float(df_15m["low"].tail(20).min())
    breakout_up = price > recent_high
    breakout_down = price < recent_low
    range_mid = (recent_high + recent_low) / 2
    in_range_center = abs(price - range_mid) <= atr_15m * 0.5

    pre_long_setup, _ = build_setup(
        side="long",
        price=price,
        atr=atr_15m,
        support_zones=support_zones,
        resistance_zones=resistance_zones,
        sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
        min_rr_ratio=0.0,
        confidence=100,
        confidence_min=0,
        atr_ratio=atr_ratio,
        atr_ratio_min=0.0,
        atr_ratio_max=999.0,
        funding_rate=funding_rate,
        funding_warning=999.0,
        funding_prohibited=999.0,
        trigger_ready=False,
        warning_count=0,
    )
    pre_short_setup, _ = build_setup(
        side="short",
        price=price,
        atr=atr_15m,
        support_zones=support_zones,
        resistance_zones=resistance_zones,
        sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
        min_rr_ratio=0.0,
        confidence=100,
        confidence_min=0,
        atr_ratio=atr_ratio,
        atr_ratio_min=0.0,
        atr_ratio_max=999.0,
        funding_rate=funding_rate,
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
            "funding_rate": funding_rate,
            "rr_long": pre_long_setup["rr_estimate"],
            "rr_short": pre_short_setup["rr_estimate"],
            "near_support": near_support,
            "near_resistance": near_resistance,
            "breakout_up": breakout_up,
            "breakout_down": breakout_down,
            "in_range_center": in_range_center,
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
        breakout_confirmed=(breakout_up or breakout_down) and float(tf_15m["volume_ratio"].iloc[-1]) >= 1.2,
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
    opposite_gap = zone_gap_to_opposite(price, bias if bias in {"long", "short"} else "long", support_zones, resistance_zones)
    opposite_gap_atr = opposite_gap / atr_15m if atr_15m > 0 and opposite_gap != float("inf") else 10.0

    confidence = compute_confidence(
        {
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
            "warning_flags": score_info["warning_flags"] + position_risk["risk_flags"],
        },
        cfg,
    )

    trigger_up = breakout_up or float(tf_15m["volume_ratio"].iloc[-1]) >= 1.2
    trigger_down = breakout_down or float(tf_15m["volume_ratio"].iloc[-1]) >= 1.2
    long_setup, long_flags = build_setup(
        side="long",
        price=price,
        atr=atr_15m,
        support_zones=support_zones,
        resistance_zones=resistance_zones,
        sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
        min_rr_ratio=cfg.MIN_RR_RATIO,
        confidence=confidence,
        confidence_min=cfg.CONFIDENCE_LONG_MIN,
        atr_ratio=atr_ratio,
        atr_ratio_min=cfg.MIN_ACCEPTABLE_ATR_RATIO,
        atr_ratio_max=cfg.MAX_ACCEPTABLE_ATR_RATIO,
        funding_rate=funding_rate,
        funding_warning=cfg.FUNDING_LONG_WARNING,
        funding_prohibited=cfg.FUNDING_LONG_PROHIBITED,
        trigger_ready=trigger_up,
        warning_count=len(score_info["warning_flags"]),
    )
    short_setup, short_flags = build_setup(
        side="short",
        price=price,
        atr=atr_15m,
        support_zones=support_zones,
        resistance_zones=resistance_zones,
        sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
        min_rr_ratio=cfg.MIN_RR_RATIO,
        confidence=confidence,
        confidence_min=cfg.CONFIDENCE_SHORT_MIN,
        atr_ratio=atr_ratio,
        atr_ratio_min=cfg.MIN_ACCEPTABLE_ATR_RATIO,
        atr_ratio_max=cfg.MAX_ACCEPTABLE_ATR_RATIO,
        funding_rate=funding_rate,
        funding_warning=cfg.FUNDING_SHORT_WARNING,
        funding_prohibited=cfg.FUNDING_SHORT_PROHIBITED,
        trigger_ready=trigger_down,
        warning_count=len(score_info["warning_flags"]),
    )
    long_setup = apply_prelabel_to_setup(long_setup, position_risk["prelabel"], "long", bias)
    short_setup = apply_prelabel_to_setup(short_setup, position_risk["prelabel"], "short", bias)
    primary_setup_side, primary_setup_status = choose_primary_setup(bias, long_setup, short_setup)
    all_flags = sorted(set(score_info["no_trade_flags"] + long_flags + short_flags + position_risk["risk_flags"]))
    if critical_zone:
        all_flags.append("Critical_zone_warning")
        all_flags = sorted(set(all_flags))

    qualitative_context = build_qualitative_context(
        now_ms=now_ms,
        timezone_name=cfg.TIMEZONE,
        df_15m=df_15m,
        market_regime=market_regime,
        bias=bias,
        no_trade_flags=all_flags,
        price=price,
        ema50=float(tf_15m["ema_mid"].iloc[-1]),
        atr=atr_15m,
    )

    agreement_with_machine = compute_machine_agreement(
        bias=bias,
        market_regime=market_regime,
        ema_alignment_4h=tf_4h["ema_alignment"],
        price=price,
        support_zones=support_zones,
        resistance_zones=resistance_zones,
        volume_ratio=float(tf_15m["volume_ratio"].iloc[-1]),
        funding_rate=funding_rate,
    )

    result: dict[str, Any] = {
        "timestamp_utc": now_utc.isoformat().replace("+00:00", "Z"),
        "timestamp_jst": now_jst.isoformat(),
        "system_label": str(getattr(cfg, "SYSTEM_LABEL", "")).strip(),
        "current_price": _round2(price),
        "server_time_gap_sec": round(gap_sec, 2),
        "bias": bias,
        "phase": phase,
        "market_regime": market_regime,
        "transition_direction": transition_direction,
        "signals_4h": tf_4h["signal"],
        "signals_1h": tf_1h["signal"],
        "signals_15m": tf_15m["signal"],
        "long_display_score": score_info["long_display_score"],
        "short_display_score": score_info["short_display_score"],
        "score_gap": score_info["score_gap"],
        "confidence": confidence,
        "agreement_with_machine": agreement_with_machine,
        "prelabel": position_risk["prelabel"],
        "location_risk": position_risk["location_risk"],
        "critical_zone": critical_zone,
        "support_zones": support_zones,
        "resistance_zones": resistance_zones,
        "long_setup": long_setup,
        "short_setup": short_setup,
        "primary_setup_side": primary_setup_side,
        "primary_setup_status": primary_setup_status,
        "funding_rate": _round2(funding_rate),
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
        "rr_estimate": _round2(
            long_setup["rr_estimate"] if bias == "long" else short_setup["rr_estimate"] if bias == "short" else max(long_setup["rr_estimate"], short_setup["rr_estimate"])
        ),
        "ai_advice": None,
        "no_trade_flags": all_flags,
        "risk_flags": position_risk["risk_flags"],
        "market_structure_missing_fields": market_structure.missing_fields or [],
        "reason_for_notification": [],
    }

    ai_advice = request_ai_advice(
        api_key=cfg.OPENAI_API_KEY,
        model=cfg.OPENAI_ADVICE_MODEL,
        timeout_sec=cfg.AI_TIMEOUT_SEC,
        retry_count=cfg.AI_RETRY_COUNT,
        base_dir=base_dir,
        machine_payload=result,
        qualitative_payload=qualitative_context,
    )
    result["ai_advice"] = ai_advice

    last_result = load_json(get_last_result_path(base_dir))
    last_notified = load_json(get_last_notified_path(base_dir))
    notify, reasons = should_notify(result, last_result, last_notified, cfg)
    result["reason_for_notification"] = reasons
    if ai_advice is None:
        if "ai_error" not in result["reason_for_notification"]:
            result["reason_for_notification"].append("ai_error")

    result["summary_subject"] = build_summary_subject(result)
    result["summary_body"] = build_summary_body(
        api_key=cfg.OPENAI_API_KEY,
        model=cfg.OPENAI_SUMMARY_MODEL,
        timeout_sec=cfg.AI_SUMMARY_TIMEOUT_SEC,
        retry_count=cfg.AI_RETRY_COUNT,
        base_dir=base_dir,
        result_payload=result,
    )

    save_signal_snapshot(base_dir, result)
    append_trade_log(base_dir, result)
    save_json(get_last_result_path(base_dir), result)

    if notify:
        if cfg.DRYRUN_MODE:
            save_json(get_last_notified_path(base_dir), result)
        else:
            try:
                send_email(
                    smtp_host=cfg.SMTP_HOST,
                    smtp_port=cfg.SMTP_PORT,
                    smtp_user=cfg.SMTP_USER,
                    smtp_password=cfg.SMTP_PASSWORD,
                    mail_from=cfg.MAIL_FROM,
                    mail_to=cfg.MAIL_TO,
                    subject=result["summary_subject"],
                    body=result["summary_body"],
                )
                save_json(get_last_notified_path(base_dir), result)
            except Exception as exc:  # noqa: BLE001
                save_pending_email(base_dir, result["summary_subject"], result["summary_body"])
                _error_log(base_dir, "smtp_error", f"{exc}\n{traceback.format_exc()}")

    return result


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
