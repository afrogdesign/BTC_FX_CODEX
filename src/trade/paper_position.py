from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


JST = ZoneInfo("Asia/Tokyo")
STATE_FIELDS = {
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
}


def _parse_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_dt(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=JST)
    return dt


def _format_jst(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(JST).isoformat()


def _format_utc(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _candle_dt(row: Any) -> datetime | None:
    ts = getattr(row, "timestamp", None)
    if ts is None:
        return None
    try:
        if isinstance(ts, pd.Timestamp):
            dt = ts.to_pydatetime()
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        value = float(ts)
    except (TypeError, ValueError):
        return _parse_dt(ts)
    if value > 10_000_000_000:
        value = value / 1000
    return datetime.fromtimestamp(value, tz=timezone.utc)


def _touches_entry(side: str, high: float, low: float, entry: float) -> bool:
    if side == "long":
        return low <= entry
    if side == "short":
        return high >= entry
    return False


def _touches_tp(side: str, high: float, low: float, price: float) -> bool:
    if side == "long":
        return high >= price
    if side == "short":
        return low <= price
    return False


def _touches_stop(side: str, high: float, low: float, stop: float) -> bool:
    if side == "long":
        return low <= stop
    if side == "short":
        return high >= stop
    return False


def _realized_r(side: str, entry: float, stop: float, close_price: float) -> float | str:
    risk = abs(entry - stop)
    if risk <= 0:
        return ""
    if side == "long":
        value = (close_price - entry) / risk
    elif side == "short":
        value = (entry - close_price) / risk
    else:
        return ""
    return round(value, 4)


def _mfe_mae(side: str, entry: float, atr: float | None, candles: list[dict[str, Any]]) -> tuple[float | str, float | str]:
    if not candles or not atr or atr <= 0:
        return "", ""
    highs = [float(item["high"]) for item in candles]
    lows = [float(item["low"]) for item in candles]
    if side == "long":
        mfe = max(0.0, (max(highs) - entry) / atr)
        mae = max(0.0, (entry - min(lows)) / atr)
    elif side == "short":
        mfe = max(0.0, (entry - min(lows)) / atr)
        mae = max(0.0, (max(highs) - entry) / atr)
    else:
        return "", ""
    return round(mfe, 4), round(mae, 4)


def _close_position(
    row: dict[str, Any],
    *,
    status: str,
    reason: str,
    closed_at: datetime,
    close_price: float,
    entry: float,
    initial_stop: float,
    eval_candles: list[dict[str, Any]],
    atr: float | None,
) -> dict[str, Any]:
    row["position_status"] = "closed"
    row["closed_at_jst"] = _format_jst(closed_at)
    row["exit_status"] = status
    row["exit_reason"] = reason
    row["close_price"] = round(close_price, 4)
    row["realized_r"] = _realized_r(str(row.get("side", "")).strip(), entry, initial_stop, close_price)
    mfe, mae = _mfe_mae(str(row.get("side", "")).strip(), entry, atr, eval_candles)
    row["mfe_atr"] = mfe
    row["mae_atr"] = mae
    return row


def evaluate_paper_position(row: dict[str, Any], future_df: pd.DataFrame) -> dict[str, Any]:
    """Update one paper position using subsequent 15m candles."""
    updated = dict(row)
    signal_dt = _parse_dt(updated.get("timestamp_jst")) or _parse_dt(updated.get("timestamp_utc"))
    side = str(updated.get("side", "")).strip()
    entry = _parse_float(updated.get("entry_price"))
    initial_stop = _parse_float(updated.get("stop_loss_price"))
    tp1 = _parse_float(updated.get("tp1_price"))
    tp2 = _parse_float(updated.get("tp2_price"))
    atr = _parse_float(updated.get("atr_15m_value"))
    timeout_hours = _parse_float(updated.get("timeout_hours")) or 12.0
    breakeven_after_tp1 = _parse_bool(updated.get("breakeven_after_tp1"))
    now = datetime.now(tz=timezone.utc)
    updated["last_evaluated_at_utc"] = _format_utc(now)

    if updated.get("position_status") == "closed":
        return updated
    if signal_dt is None or side not in {"long", "short"} or entry is None or initial_stop is None:
        return updated

    candles: list[dict[str, Any]] = []
    if not future_df.empty:
        for candle in future_df.sort_values("timestamp").itertuples(index=False):
            candle_dt = _candle_dt(candle)
            if candle_dt is None or candle_dt <= signal_dt.astimezone(timezone.utc):
                continue
            candles.append(
                {
                    "dt": candle_dt,
                    "high": float(getattr(candle, "high")),
                    "low": float(getattr(candle, "low")),
                    "close": float(getattr(candle, "close")),
                }
            )

    status = str(updated.get("position_status", "")).strip()
    if status not in {"pending", "opened"}:
        status = "pending"
        updated["position_status"] = status

    opened_dt = _parse_dt(updated.get("opened_at_jst"))
    if status == "opened" and opened_dt is None:
        opened_dt = signal_dt
        updated["opened_at_jst"] = _format_jst(opened_dt)

    pending_deadline = signal_dt + timedelta(hours=24)
    open_eval_candles: list[dict[str, Any]] = []
    effective_stop = initial_stop

    for candle in candles:
        candle_dt = candle["dt"]
        high = candle["high"]
        low = candle["low"]

        if status == "pending":
            entry_hit = _touches_entry(side, high, low, entry)
            missed_hit = bool(tp1 is not None and _touches_tp(side, high, low, tp1))
            if entry_hit:
                status = "opened"
                updated["position_status"] = "opened"
                opened_dt = candle_dt
                updated["opened_at_jst"] = _format_jst(opened_dt)
            elif missed_hit:
                updated["missed_opportunity"] = "true"
                updated["missed_reason"] = "tp_direction_before_entry"
                return _close_position(
                    updated,
                    status="missed_opportunity",
                    reason="tp_direction_before_entry",
                    closed_at=candle_dt,
                    close_price=tp1,
                    entry=entry,
                    initial_stop=initial_stop,
                    eval_candles=[],
                    atr=atr,
                )
            elif candle_dt >= pending_deadline:
                return _close_position(
                    updated,
                    status="entry_not_reached",
                    reason="pending_24h_timeout",
                    closed_at=pending_deadline,
                    close_price=candle["close"],
                    entry=entry,
                    initial_stop=initial_stop,
                    eval_candles=[],
                    atr=atr,
                )
            else:
                continue

        if status != "opened" or opened_dt is None:
            continue

        timeout_at = opened_dt + timedelta(hours=timeout_hours)
        open_eval_candles.append(candle)
        if candle_dt >= timeout_at:
            updated["timeout_at_jst"] = _format_jst(timeout_at)
            return _close_position(
                updated,
                status="timeout",
                reason="timeout",
                closed_at=timeout_at,
                close_price=candle["close"],
                entry=entry,
                initial_stop=initial_stop,
                eval_candles=open_eval_candles,
                atr=atr,
            )

        if tp1 is not None and not updated.get("tp1_hit_at_jst") and _touches_tp(side, high, low, tp1):
            updated["tp1_hit_at_jst"] = _format_jst(candle_dt)
            if breakeven_after_tp1:
                effective_stop = entry

        stop_hit = _touches_stop(side, high, low, effective_stop)
        tp2_hit = bool(tp2 is not None and _touches_tp(side, high, low, tp2))
        if stop_hit:
            updated["sl_hit_at_jst"] = _format_jst(candle_dt)
            return _close_position(
                updated,
                status="sl_hit",
                reason="sl_hit",
                closed_at=candle_dt,
                close_price=effective_stop,
                entry=entry,
                initial_stop=initial_stop,
                eval_candles=open_eval_candles,
                atr=atr,
            )
        if tp2_hit:
            updated["tp2_hit_at_jst"] = _format_jst(candle_dt)
            return _close_position(
                updated,
                status="tp2_hit",
                reason="tp2_hit",
                closed_at=candle_dt,
                close_price=tp2,
                entry=entry,
                initial_stop=initial_stop,
                eval_candles=open_eval_candles,
                atr=atr,
            )

    if status == "opened" and opened_dt is not None and open_eval_candles:
        mfe, mae = _mfe_mae(side, entry, atr, open_eval_candles)
        updated["mfe_atr"] = mfe
        updated["mae_atr"] = mae
    if status == "pending" and now >= pending_deadline.astimezone(timezone.utc):
        updated["exit_status"] = "pending_waiting"
    return updated
