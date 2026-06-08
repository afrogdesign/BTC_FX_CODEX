from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd


def _as_dict(candidate_row: Any) -> dict[str, Any]:
    if candidate_row is None:
        return {}
    if hasattr(candidate_row, "to_dict"):
        value = candidate_row.to_dict()
        return value if isinstance(value, dict) else dict(value)
    return dict(candidate_row)


def _parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, pd.Timestamp):
        dt = value.to_pydatetime()
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        numeric = float(value)
        if abs(numeric) > 10_000_000_000:
            numeric /= 1000.0
        return datetime.fromtimestamp(numeric, tz=timezone.utc)

    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        try:
            numeric = float(text)
        except ValueError:
            return None
        if abs(numeric) > 10_000_000_000:
            numeric /= 1000.0
        return datetime.fromtimestamp(numeric, tz=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _format_dt(value: datetime | None) -> str:
    return value.isoformat() if value is not None else ""


def _format_price(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def _format_ratio(value: float | None) -> str:
    return "" if value is None else f"{value:.4f}"


def _normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _candidate_timestamp(candidate: dict[str, Any]) -> datetime | None:
    for key in ("timestamp_jst", "timestamp_utc", "timestamp"):
        value = _parse_dt(candidate.get(key))
        if value is not None:
            return value
    return None


def _ohlcv_timestamp(row: dict[str, Any]) -> datetime | None:
    for key in ("timestamp_jst", "timestamp_utc", "timestamp", "datetime", "dt"):
        value = _parse_dt(row.get(key))
        if value is not None:
            return value
    return None


def _ohlcv_records(ohlcv_df: pd.DataFrame | None) -> list[dict[str, Any]]:
    if ohlcv_df is None or ohlcv_df.empty:
        return []

    records: list[dict[str, Any]] = []
    for row in ohlcv_df.to_dict(orient="records"):
        dt = _ohlcv_timestamp(row)
        if dt is None:
            continue
        high = _parse_float(row.get("high"))
        low = _parse_float(row.get("low"))
        close = _parse_float(row.get("close"))
        open_ = _parse_float(row.get("open"))
        if high is None or low is None:
            continue
        records.append(
            {
                "dt": _normalize_dt(dt),
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
            }
        )

    records.sort(key=lambda item: item["dt"])
    return records


def _entry_band(candidate: dict[str, Any]) -> tuple[float | None, float | None, float | None]:
    entry_low = _parse_float(candidate.get("entry_zone_low"))
    entry_high = _parse_float(candidate.get("entry_zone_high"))
    entry_price = _parse_float(candidate.get("entry_price"))
    if entry_low is not None and entry_high is not None:
        return (min(entry_low, entry_high), max(entry_low, entry_high), entry_price)
    if entry_price is not None:
        return (entry_price, entry_price, entry_price)
    return (None, None, None)


def _touches_entry(high: float, low: float, band_low: float, band_high: float) -> bool:
    return high >= band_low and low <= band_high


def _touches_tp(side: str, high: float, low: float, tp: float) -> bool:
    if side == "long":
        return high >= tp
    if side == "short":
        return low <= tp
    return False


def _touches_stop(side: str, high: float, low: float, stop: float) -> bool:
    if side == "long":
        return low <= stop
    if side == "short":
        return high >= stop
    return False


def _path_metrics(
    side: str,
    entry_price: float,
    stop_price: float | None,
    bars: list[dict[str, Any]],
) -> tuple[str, str, str, str]:
    if not bars:
        return "", "", "", ""

    highs = [bar["high"] for bar in bars]
    lows = [bar["low"] for bar in bars]
    if side == "long":
        mfe_price = max(0.0, max(highs) - entry_price)
        mae_price = max(0.0, entry_price - min(lows))
    elif side == "short":
        mfe_price = max(0.0, entry_price - min(lows))
        mae_price = max(0.0, max(highs) - entry_price)
    else:
        return "", "", "", ""

    risk = None
    if stop_price is not None:
        risk = abs(entry_price - stop_price)
        if risk <= 0:
            risk = None

    mfe_r = mfe_price / risk if risk else None
    mae_r = mae_price / risk if risk else None
    return (
        _format_price(mfe_price),
        _format_price(mae_price),
        _format_ratio(mfe_r),
        _format_ratio(mae_r),
    )


def evaluate_active_plan_intraperiod_candidate(
    candidate_row: Any,
    ohlcv_df: pd.DataFrame | None,
    *,
    now: datetime | None = None,
    timeout_hours: float = 24.0,
) -> dict[str, Any]:
    candidate = _as_dict(candidate_row)
    result = dict(candidate)

    source_signal_id = str(candidate.get("source_signal_id") or candidate.get("signal_id") or "").strip()
    result["signal_id"] = source_signal_id
    stop_price = _parse_float(candidate.get("stop_loss"))
    tp1_price = _parse_float(candidate.get("tp1"))
    tp2_price = _parse_float(candidate.get("tp2"))
    result["stop_price"] = _format_price(stop_price)
    result["tp1_price"] = _format_price(tp1_price)
    result["tp2_price"] = _format_price(tp2_price)

    side = str(candidate.get("side") or "").strip().lower()
    candidate_dt = _candidate_timestamp(candidate)
    band_low, band_high, entry_price = _entry_band(candidate)
    now_dt = _normalize_dt(now or datetime.now(tz=timezone.utc))
    result["entry_reached_time"] = ""
    result["first_exit_time"] = ""
    result["first_exit_reason"] = ""
    result["mfe_price"] = ""
    result["mae_price"] = ""
    result["mfe_r"] = ""
    result["mae_r"] = ""

    records = _ohlcv_records(ohlcv_df)
    if not records:
        result["outcome"] = "no_ohlcv"
        return result

    if candidate_dt is None or band_low is None or band_high is None or entry_price is None or side not in {"long", "short"}:
        result["outcome"] = "pending"
        return result

    candidate_dt = _normalize_dt(candidate_dt)
    deadline = candidate_dt + timedelta(hours=float(timeout_hours))
    effective_end = min(now_dt, deadline)
    window_records = [row for row in records if candidate_dt <= row["dt"] <= effective_end]

    if not window_records:
        result["outcome"] = "no_ohlcv"
        return result

    entry_index: int | None = None
    for index, row in enumerate(window_records):
        if _touches_entry(row["high"], row["low"], band_low, band_high):
            entry_index = index
            result["entry_reached_time"] = _format_dt(row["dt"])
            break

    if entry_index is None:
        result["outcome"] = "not_entered" if effective_end >= deadline else "pending"
        return result

    observed_after_entry = window_records[entry_index:]
    exit_index: int | None = None
    exit_reason = ""
    outcome = ""

    for index, row in enumerate(window_records[entry_index:], start=entry_index):
        tp1_hit = tp1_price is not None and _touches_tp(side, row["high"], row["low"], tp1_price)
        tp2_hit = tp2_price is not None and _touches_tp(side, row["high"], row["low"], tp2_price)
        stop_hit = stop_price is not None and _touches_stop(side, row["high"], row["low"], stop_price)

        if stop_hit and (tp1_hit or tp2_hit):
            exit_index = index
            exit_reason = "ambiguous"
            outcome = "ambiguous"
            break
        if tp1_hit:
            exit_index = index
            exit_reason = "tp1"
            outcome = "tp1_first"
            break
        if tp2_hit:
            exit_index = index
            exit_reason = "tp2"
            outcome = "tp2_first"
            break
        if stop_hit:
            exit_index = index
            exit_reason = "sl"
            outcome = "sl_first"
            break

    if exit_index is not None:
        result["first_exit_time"] = _format_dt(window_records[exit_index]["dt"])
        result["first_exit_reason"] = exit_reason
        metrics = window_records[entry_index : exit_index + 1]
        mfe_price, mae_price, mfe_r, mae_r = _path_metrics(side, entry_price, stop_price, metrics)
        result["mfe_price"] = mfe_price
        result["mae_price"] = mae_price
        result["mfe_r"] = mfe_r
        result["mae_r"] = mae_r
        result["outcome"] = outcome
        return result

    metrics = observed_after_entry
    mfe_price, mae_price, mfe_r, mae_r = _path_metrics(side, entry_price, stop_price, metrics)
    result["mfe_price"] = mfe_price
    result["mae_price"] = mae_price
    result["mfe_r"] = mfe_r
    result["mae_r"] = mae_r
    if effective_end < deadline:
        result["outcome"] = "entry_reached"
    else:
        result["outcome"] = "timeout"
        result["first_exit_time"] = _format_dt(deadline)
        result["first_exit_reason"] = "timeout"
    return result


__all__ = ["evaluate_active_plan_intraperiod_candidate"]
