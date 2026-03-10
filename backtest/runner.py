from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from config import load_config
from src.analysis.confidence import compute_confidence
from src.analysis.liquidation import analyze_liquidation_clusters
from src.analysis.liquidity import analyze_liquidity
from src.analysis.oi_cvd import analyze_oi_cvd
from src.analysis.orderbook import analyze_orderbook
from src.analysis.phase import determine_phase
from src.analysis.position_risk import apply_prelabel_to_setup, evaluate_position_risk
from src.analysis.regime import classify_market_regime
from src.analysis.rr import build_setup, choose_primary_setup
from src.analysis.scoring import compute_scores
from src.analysis.structure import calc_tf_signal, classify_structure, detect_swings
from src.analysis.support_resistance import build_support_resistance, detect_critical_zone, nearest_zone_distance, zone_gap_to_opposite
from src.indicators.atr import calculate_atr, calculate_atr_ratio
from src.indicators.ema import calculate_ema, get_ema20_slope, get_ema_alignment
from src.indicators.rsi import calculate_rsi
from src.indicators.volume import calculate_volume_ratio


@dataclass
class BacktestInput:
    df_4h: pd.DataFrame
    df_1h: pd.DataFrame
    df_15m: pd.DataFrame


def load_ohlcv_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")
    return df.sort_values("timestamp").reset_index(drop=True)


def _prepare_tf(df: pd.DataFrame, cfg: Any, swing_n: int) -> dict[str, Any]:
    ema_fast = calculate_ema(df["close"], cfg.EMA_FAST)
    ema_mid = calculate_ema(df["close"], cfg.EMA_MID)
    ema_slow = calculate_ema(df["close"], cfg.EMA_SLOW)
    rsi = calculate_rsi(df["close"], cfg.RSI_LENGTH)
    atr = calculate_atr(df["high"], df["low"], df["close"], cfg.ATR_LENGTH)
    volume_ratio = calculate_volume_ratio(df["volume"], 20)
    swings = detect_swings(df, swing_n)
    structure = classify_structure(swings)
    ema_alignment = get_ema_alignment(float(ema_fast.iloc[-1]), float(ema_mid.iloc[-1]), float(ema_slow.iloc[-1]))
    return {
        "df": df,
        "swings": swings,
        "structure": structure,
        "signal": calc_tf_signal(ema_alignment, structure),
        "ema_alignment": ema_alignment,
        "ema_fast": ema_fast,
        "ema_mid": ema_mid,
        "ema_slow": ema_slow,
        "ema20_slope": get_ema20_slope(ema_fast),
        "rsi": rsi,
        "atr": atr,
        "volume_ratio": volume_ratio,
    }


def _slice_until(df: pd.DataFrame, ts: int) -> pd.DataFrame:
    return df[df["timestamp"] <= ts].copy()


def run_backtest(input_data: BacktestInput, cfg: Any | None = None) -> list[dict[str, Any]]:
    cfg = cfg or load_config(Path(__file__).resolve().parents[1])
    results: list[dict[str, Any]] = []
    df_15m = input_data.df_15m
    start_idx = max(cfg.EMA_SLOW + 20, 220)

    for i in range(start_idx, len(df_15m)):
        current_ts = int(df_15m.iloc[i]["timestamp"])
        part_15m = input_data.df_15m.iloc[: i + 1].copy()
        part_1h = _slice_until(input_data.df_1h, current_ts)
        part_4h = _slice_until(input_data.df_4h, current_ts)
        if len(part_15m) < cfg.EMA_SLOW + 20 or len(part_1h) < cfg.EMA_SLOW + 20 or len(part_4h) < cfg.EMA_SLOW + 20:
            continue

        tf_4h = _prepare_tf(part_4h, cfg, cfg.SWING_N_4H)
        tf_1h = _prepare_tf(part_1h, cfg, cfg.SWING_N_1H)
        tf_15m = _prepare_tf(part_15m, cfg, cfg.SWING_N_15M)
        price = float(part_15m["close"].iloc[-1])
        atr = float(tf_15m["atr"].iloc[-1])
        atr_ratio = calculate_atr_ratio(tf_15m["atr"], 50)

        support_zones, resistance_zones = build_support_resistance(
            {"4h": {"df": part_4h, "swings": tf_4h["swings"]}, "1h": {"df": part_1h, "swings": tf_1h["swings"]}, "15m": {"df": part_15m, "swings": tf_15m["swings"]}},
            atr,
        )
        critical_zone = detect_critical_zone(price, support_zones, resistance_zones)

        regime = classify_market_regime(
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
        near_support = nearest_zone_distance(price, support_zones) <= atr * 0.5
        near_resistance = nearest_zone_distance(price, resistance_zones) <= atr * 0.5
        recent_high = float(part_15m["high"].tail(20).max())
        recent_low = float(part_15m["low"].tail(20).min())
        breakout_up = price > recent_high
        breakout_down = price < recent_low
        in_range_center = abs(price - (recent_high + recent_low) / 2) <= atr * 0.5

        pre_long, _ = build_setup(
            side="long",
            price=price,
            atr=atr,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
            min_rr_ratio=0.0,
            confidence=100,
            confidence_min=0,
            atr_ratio=atr_ratio,
            atr_ratio_min=0.0,
            atr_ratio_max=999.0,
            funding_rate=0.0,
            funding_warning=999.0,
            funding_prohibited=999.0,
            trigger_ready=False,
            warning_count=0,
        )
        pre_short, _ = build_setup(
            side="short",
            price=price,
            atr=atr,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
            min_rr_ratio=0.0,
            confidence=100,
            confidence_min=0,
            atr_ratio=atr_ratio,
            atr_ratio_min=0.0,
            atr_ratio_max=999.0,
            funding_rate=0.0,
            funding_warning=-999.0,
            funding_prohibited=-999.0,
            trigger_ready=False,
            warning_count=0,
        )

        scores = compute_scores(
            {
                "market_regime": regime["market_regime"],
                "ema_alignment_4h": tf_4h["ema_alignment"],
                "ema20_slope_4h": tf_4h["ema20_slope"],
                "structure_4h": tf_4h["structure"],
                "structure_1h": tf_1h["structure"],
                "price": price,
                "ema50_4h": float(tf_4h["ema_mid"].iloc[-1]),
                "rsi_15m": float(tf_15m["rsi"].iloc[-1]),
                "volume_ratio": float(tf_15m["volume_ratio"].iloc[-1]),
                "atr_ratio": atr_ratio,
                "funding_rate": 0.0,
                "rr_long": pre_long["rr_estimate"],
                "rr_short": pre_short["rr_estimate"],
                "near_support": near_support,
                "near_resistance": near_resistance,
                "breakout_up": breakout_up,
                "breakout_down": breakout_down,
                "in_range_center": in_range_center,
            },
            cfg,
        )
        bias = scores["bias"]
        liquidity_info = analyze_liquidity(
            df_15m=part_15m,
            swings=tf_15m["swings"],
            price=price,
            atr=atr,
            equal_threshold_pct=cfg.LIQUIDITY_EQUAL_THRESHOLD_PCT,
        )
        liquidation_info = analyze_liquidation_clusters(price=price, atr=atr, liquidation_events=None)
        oi_cvd_info = analyze_oi_cvd(
            oi_value=None,
            oi_change_pct=None,
            oi_trend_values=None,
            cvd_series=None,
            price_series=[float(v) for v in part_15m["close"].tail(12).tolist()],
        )
        orderbook_info = analyze_orderbook(bids=None, asks=None, price=price)
        position_risk = evaluate_position_risk(
            bias=bias,
            price=price,
            atr=atr,
            liquidity_info=liquidity_info,
            liquidation_info=liquidation_info,
            oi_cvd_info=oi_cvd_info,
            orderbook_info=orderbook_info,
            high_threshold=cfg.POSITION_RISK_HIGH_THRESHOLD,
            medium_threshold=cfg.POSITION_RISK_MEDIUM_THRESHOLD,
        )
        phase = determine_phase(
            bias=bias,
            market_regime=regime["market_regime"],
            pullback_depth_atr=abs(price - float(tf_4h["ema_mid"].iloc[-1])) / max(float(tf_4h["atr"].iloc[-1]), 1e-9),
            breakout_confirmed=(breakout_up or breakout_down) and float(tf_15m["volume_ratio"].iloc[-1]) >= 1.2,
            reversal_risk_flag=False,
            price=price,
            ema50=float(tf_4h["ema_mid"].iloc[-1]),
            ema200=float(tf_4h["ema_slow"].iloc[-1]),
        )
        rr_conf = pre_long["rr_estimate"] if bias == "long" else pre_short["rr_estimate"]
        opposite_gap = zone_gap_to_opposite(price, bias if bias in {"long", "short"} else "long", support_zones, resistance_zones)
        confidence = compute_confidence(
            {
                "bias": bias,
                "long_display_score": scores["long_display_score"],
                "short_display_score": scores["short_display_score"],
                "signals_4h": tf_4h["signal"],
                "signals_1h": tf_1h["signal"],
                "signals_15m": tf_15m["signal"],
                "market_regime": regime["market_regime"],
                "phase": phase,
                "rr_estimate": rr_conf,
                "opposite_gap_atr": opposite_gap / atr if atr > 0 and opposite_gap != float("inf") else 10.0,
                "critical_zone": critical_zone,
                "warning_flags": scores["warning_flags"] + position_risk["risk_flags"],
            },
            cfg,
        )

        long_setup, _ = build_setup(
            side="long",
            price=price,
            atr=atr,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
            min_rr_ratio=cfg.MIN_RR_RATIO,
            confidence=confidence,
            confidence_min=cfg.CONFIDENCE_LONG_MIN,
            atr_ratio=atr_ratio,
            atr_ratio_min=cfg.MIN_ACCEPTABLE_ATR_RATIO,
            atr_ratio_max=cfg.MAX_ACCEPTABLE_ATR_RATIO,
            funding_rate=0.0,
            funding_warning=999.0,
            funding_prohibited=999.0,
            trigger_ready=True,
            warning_count=len(scores["warning_flags"]),
        )
        long_setup = apply_prelabel_to_setup(long_setup, position_risk["prelabel"], "long", bias)
        short_setup, _ = build_setup(
            side="short",
            price=price,
            atr=atr,
            support_zones=support_zones,
            resistance_zones=resistance_zones,
            sl_atr_multiplier=cfg.SL_ATR_MULTIPLIER,
            min_rr_ratio=cfg.MIN_RR_RATIO,
            confidence=confidence,
            confidence_min=cfg.CONFIDENCE_SHORT_MIN,
            atr_ratio=atr_ratio,
            atr_ratio_min=cfg.MIN_ACCEPTABLE_ATR_RATIO,
            atr_ratio_max=cfg.MAX_ACCEPTABLE_ATR_RATIO,
            funding_rate=0.0,
            funding_warning=-999.0,
            funding_prohibited=-999.0,
            trigger_ready=True,
            warning_count=len(scores["warning_flags"]),
        )
        short_setup = apply_prelabel_to_setup(short_setup, position_risk["prelabel"], "short", bias)
        primary_side, primary_status = choose_primary_setup(bias, long_setup, short_setup)
        results.append(
            {
                "timestamp": current_ts,
                "price": price,
                "bias": bias,
                "prelabel": position_risk["prelabel"],
                "location_risk": position_risk["location_risk"],
                "risk_flags": position_risk["risk_flags"],
                "phase": phase,
                "confidence": confidence,
                "market_regime": regime["market_regime"],
                "long_display_score": scores["long_display_score"],
                "short_display_score": scores["short_display_score"],
                "score_gap": scores["score_gap"],
                "long_setup": long_setup,
                "short_setup": short_setup,
                "primary_setup_side": primary_side,
                "primary_setup_status": primary_status,
            }
        )

    return results
