from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd


def _row_value(row: Any, key: str) -> Any:
    if isinstance(row, dict):
        return row[key]
    return getattr(row, key)


def _entry_zone_touched(row: Any, setup: dict[str, Any]) -> bool:
    zone = setup.get("entry_zone", {})
    entry_low = float(zone.get("low", 0.0))
    entry_high = float(zone.get("high", 0.0))
    high = float(getattr(row, "high"))
    low = float(getattr(row, "low"))
    return low <= entry_high and high >= entry_low


def _safe_rr(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def _missed_opportunity(sample: pd.DataFrame, bias: str, entry: float, risk: float, lookahead_bars: int) -> bool:
    if risk <= 0:
        return False
    target = entry + risk if bias == "long" else entry - risk
    for row in sample.head(lookahead_bars).itertuples(index=False):
        high = float(getattr(row, "high"))
        low = float(getattr(row, "low"))
        if bias == "long" and high >= target:
            return True
        if bias == "short" and low <= target:
            return True
    return False


def _evaluate_one(
    signal: dict[str, Any],
    current_row: Any,
    future_df: pd.DataFrame,
    horizon_bars: int = 32,
    missed_lookahead_bars: int = 16,
) -> dict[str, Any]:
    if signal.get("profile") == "baseline":
        return _evaluate_one_baseline(signal, future_df, horizon_bars)

    bias = signal["bias"]
    if bias not in {"long", "short"}:
        return {"result": "skip", "realized_rr": 0.0, "filled": False}

    setup = signal["long_setup"] if bias == "long" else signal["short_setup"]
    if signal.get("primary_setup_status") != "ready" or setup["status"] != "ready":
        return {"result": "skip", "realized_rr": 0.0, "filled": False, "fill_status": "not_ready"}

    entry = float(setup["entry_mid"])
    stop = float(setup["stop_loss"])
    tp1 = float(setup["tp1"])
    tp2 = float(setup["tp2"])
    risk = abs(entry - stop)
    if risk <= 0:
        return {"result": "skip", "realized_rr": 0.0, "filled": False, "fill_status": "invalid_risk"}

    sample = future_df.head(horizon_bars)
    filled = True
    fill_timestamp: int | None = int(_row_value(current_row, "timestamp"))
    bars_to_fill: int | None = 0
    tp1_hit = False
    breakeven_stop = entry
    tp1_rr = _safe_rr(abs(tp1 - entry), risk)
    tp2_rr = _safe_rr(abs(tp2 - entry), risk)

    for row in sample.itertuples(index=False):
        high = float(getattr(row, "high"))
        low = float(getattr(row, "low"))

        if bias == "long":
            if not tp1_hit:
                if low <= stop:
                    return {
                        "result": "loss",
                        "realized_rr": -1.0,
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": False,
                    }
                if high >= tp2:
                    tp1_hit = True
                    return {
                        "result": "tp2",
                        "realized_rr": round(0.5 * tp1_rr + 0.5 * tp2_rr, 4),
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": True,
                    }
                if high >= tp1:
                    tp1_hit = True
                    continue
            else:
                if low <= breakeven_stop:
                    return {
                        "result": "breakeven_after_tp1",
                        "realized_rr": round(0.5 * tp1_rr, 4),
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": True,
                    }
                if high >= tp2:
                    return {
                        "result": "tp2",
                        "realized_rr": round(0.5 * tp1_rr + 0.5 * tp2_rr, 4),
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": True,
                    }
        else:
            if not tp1_hit:
                if high >= stop:
                    return {
                        "result": "loss",
                        "realized_rr": -1.0,
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": False,
                    }
                if low <= tp2:
                    tp1_hit = True
                    return {
                        "result": "tp2",
                        "realized_rr": round(0.5 * tp1_rr + 0.5 * tp2_rr, 4),
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": True,
                    }
                if low <= tp1:
                    tp1_hit = True
                    continue
            else:
                if high >= breakeven_stop:
                    return {
                        "result": "breakeven_after_tp1",
                        "realized_rr": round(0.5 * tp1_rr, 4),
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": True,
                    }
                if low <= tp2:
                    return {
                        "result": "tp2",
                        "realized_rr": round(0.5 * tp1_rr + 0.5 * tp2_rr, 4),
                        "filled": True,
                        "fill_status": "filled",
                        "fill_timestamp": fill_timestamp,
                        "bars_to_fill": bars_to_fill,
                        "tp1_hit": True,
                    }

    return {
        "result": "unresolved",
        "realized_rr": 0.0,
        "filled": True,
        "fill_status": "filled",
        "fill_timestamp": fill_timestamp,
        "bars_to_fill": bars_to_fill,
        "tp1_hit": tp1_hit,
    }


def _evaluate_one_baseline(signal: dict[str, Any], future_df: pd.DataFrame, horizon_bars: int = 32) -> dict[str, Any]:
    bias = signal["bias"]
    if bias not in {"long", "short"}:
        return {"result": "skip", "realized_rr": 0.0, "filled": False}

    setup = signal["long_setup"] if bias == "long" else signal["short_setup"]
    if setup["status"] == "invalid":
        return {"result": "skip", "realized_rr": 0.0, "filled": False, "fill_status": "invalid"}

    tp1 = float(setup["tp1"])
    stop = float(setup["stop_loss"])
    entry = float(setup["entry_mid"])
    risk = abs(entry - stop)
    if risk <= 0:
        return {"result": "skip", "realized_rr": 0.0, "filled": False, "fill_status": "invalid_risk"}

    sample = future_df.head(horizon_bars)
    for row in sample.itertuples(index=False):
        high = float(getattr(row, "high"))
        low = float(getattr(row, "low"))
        if bias == "long":
            if low <= stop:
                return {"result": "loss", "realized_rr": -1.0, "filled": True, "fill_status": "filled"}
            if high >= tp1:
                return {
                    "result": "win",
                    "realized_rr": _safe_rr(tp1 - entry, risk),
                    "filled": True,
                    "fill_status": "filled",
                }
        else:
            if high >= stop:
                return {"result": "loss", "realized_rr": -1.0, "filled": True, "fill_status": "filled"}
            if low <= tp1:
                return {
                    "result": "win",
                    "realized_rr": _safe_rr(entry - tp1, risk),
                    "filled": True,
                    "fill_status": "filled",
                }
    return {"result": "unresolved", "realized_rr": 0.0, "filled": True, "fill_status": "filled"}


def evaluate_signals(signals: list[dict[str, Any]], df_15m: pd.DataFrame) -> list[dict[str, Any]]:
    ts_to_index = {int(ts): idx for idx, ts in enumerate(df_15m["timestamp"].tolist())}
    evaluated = []
    for signal in signals:
        idx = ts_to_index.get(int(signal["timestamp"]))
        if idx is None:
            continue
        current_row = df_15m.iloc[idx]
        future = df_15m.iloc[idx + 1 :].copy()
        result = _evaluate_one(signal, current_row, future)
        merged = dict(signal)
        merged.update(
            {
                "filled": False,
                "fill_status": "",
                "fill_timestamp": "",
                "bars_to_fill": "",
                "tp1_hit": False,
                "missed_ready_trade": False,
                "missed_opportunity": False,
            }
        )
        merged.update(result)
        evaluated.append(merged)
    return evaluated


def summarize_evaluated_signals(evaluated: list[dict[str, Any]], label: str) -> dict[str, Any]:
    ready_signals = sum(1 for row in evaluated if row.get("primary_setup_status") == "ready")
    watch_signals = sum(1 for row in evaluated if row.get("primary_setup_status") == "watch")
    filled_trades = sum(1 for row in evaluated if row.get("filled"))
    missed_ready_trades = sum(1 for row in evaluated if row.get("missed_ready_trade"))
    missed_opportunity_count = sum(1 for row in evaluated if row.get("missed_opportunity"))
    wins = sum(1 for row in evaluated if row.get("result") == "tp2")
    losses = sum(1 for row in evaluated if row.get("result") == "loss")
    breakeven_count = sum(1 for row in evaluated if row.get("result") == "breakeven_after_tp1")
    unresolved_count = sum(1 for row in evaluated if row.get("result") == "unresolved")
    rr_series = [float(row.get("realized_rr", 0.0)) for row in evaluated if row.get("filled")]
    gains = sum(value for value in rr_series if value > 0)
    losses_abs = abs(sum(value for value in rr_series if value < 0))
    running_rr = 0.0
    peak_rr = 0.0
    max_drawdown_rr = 0.0
    for value in rr_series:
        running_rr += value
        peak_rr = max(peak_rr, running_rr)
        max_drawdown_rr = max(max_drawdown_rr, peak_rr - running_rr)

    return {
        "label": label,
        "total_signals": len(evaluated),
        "ready_signals": ready_signals,
        "watch_signals": watch_signals,
        "filled_trades": filled_trades,
        "filled_rate": round(filled_trades / ready_signals, 4) if ready_signals else 0.0,
        "missed_ready_trades": missed_ready_trades,
        "missed_opportunity_count": missed_opportunity_count,
        "missed_opportunity_rate": round(missed_opportunity_count / ready_signals, 4) if ready_signals else 0.0,
        "wins": wins,
        "losses": losses,
        "breakeven_count": breakeven_count,
        "unresolved_count": unresolved_count,
        "avg_realized_rr": round(sum(rr_series) / len(rr_series), 4) if rr_series else 0.0,
        "profit_factor": round(gains / losses_abs, 4) if losses_abs else (round(gains, 4) if gains else 0.0),
        "max_drawdown_rr": round(max_drawdown_rr, 4),
    }


def save_evaluation_csv(path: Path, evaluated: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "timestamp",
        "price",
        "bias",
        "phase",
        "confidence",
        "market_regime",
        "long_display_score",
        "short_display_score",
        "score_gap",
        "primary_setup_side",
        "primary_setup_status",
        "filled",
        "fill_status",
        "fill_timestamp",
        "bars_to_fill",
        "tp1_hit",
        "missed_ready_trade",
        "missed_opportunity",
        "result",
        "realized_rr",
        "profile",
    ]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        for row in evaluated:
            writer.writerow({k: row.get(k) for k in fields})
    return path


def save_comparison_csv(path: Path, summaries: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "label",
        "total_signals",
        "ready_signals",
        "watch_signals",
        "filled_trades",
        "filled_rate",
        "missed_ready_trades",
        "missed_opportunity_count",
        "missed_opportunity_rate",
        "wins",
        "losses",
        "breakeven_count",
        "unresolved_count",
        "avg_realized_rr",
        "profit_factor",
        "max_drawdown_rr",
    ]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        for row in summaries:
            writer.writerow({k: row.get(k) for k in fields})
    return path
