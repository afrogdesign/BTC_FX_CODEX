from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd


MIN_OUTCOME_COLUMNS = [
    "candidate_id",
    "signal_id",
    "timestamp_jst",
    "candidate_type",
    "active_primary_action",
    "side",
    "entry_mode",
    "entry_price",
    "stop_price",
    "tp1_price",
    "tp2_price",
    "outcome",
    "entry_reached_time",
    "first_exit_time",
    "first_exit_reason",
    "mfe_price",
    "mae_price",
    "mfe_r",
    "mae_r",
    "notes",
]


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


def _blank_if_missing(value: Any) -> Any:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return value


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


def summarize_intraperiod_outcome_coverage(outcomes_df: pd.DataFrame | None) -> dict[str, Any]:
    if outcomes_df is None or outcomes_df.empty or "outcome" not in outcomes_df.columns:
        total_rows = 0
        no_ohlcv_rows = 0
        valid_sample_rows = 0
        entry_reached_rows = 0
        no_ohlcv_rate = 0.0
        valid_sample_rate = 0.0
        entry_reached_rate = 0.0
    else:
        total_rows = int(len(outcomes_df))
        outcome_series = outcomes_df["outcome"].astype("object")
        no_ohlcv_rows = int((outcome_series == "no_ohlcv").sum())
        valid_sample_rows = int(total_rows - no_ohlcv_rows)
        entry_reached_rows = int(
            outcome_series.isin(
                {
                    "tp1_first",
                    "tp2_first",
                    "sl_first",
                    "timeout",
                    "ambiguous",
                    "entry_reached",
                }
            ).sum()
        )
        no_ohlcv_rate = float(no_ohlcv_rows / total_rows) if total_rows else 0.0
        valid_sample_rate = float(valid_sample_rows / total_rows) if total_rows else 0.0
        entry_reached_rate = float(entry_reached_rows / total_rows) if total_rows else 0.0

    return {
        "total_rows": total_rows,
        "no_ohlcv_rows": no_ohlcv_rows,
        "valid_sample_rows": valid_sample_rows,
        "entry_reached_rows": entry_reached_rows,
        "no_ohlcv_rate": no_ohlcv_rate,
        "valid_sample_rate": valid_sample_rate,
        "entry_reached_rate": entry_reached_rate,
        "valid_sample_definition": 'rows excluding outcome == no_ohlcv',
    }


def summarize_intraperiod_valid_sample_winrate(outcomes_df: pd.DataFrame | None) -> dict[str, Any]:
    valid_sample_definition = "rows excluding outcome == no_ohlcv"
    winrate_definition = "win-like outcomes divided by entry-reached rows; report-only, not profitability"
    safety_note = "report-only / not FORMAL_GO / no automatic order / human decides manually"
    entry_reached_outcomes = {
        "tp1_first",
        "tp2_first",
        "sl_first",
        "timeout",
        "ambiguous",
        "entry_reached",
    }

    if outcomes_df is None or outcomes_df.empty or "outcome" not in outcomes_df.columns:
        return {
            "total_rows": 0,
            "no_ohlcv_rows": 0,
            "valid_sample_rows": 0,
            "entry_reached_rows": 0,
            "win_like_rows": 0,
            "loss_like_rows": 0,
            "unresolved_entry_rows": 0,
            "not_entered_rows": 0,
            "pending_rows": 0,
            "valid_sample_rate": 0.0,
            "entry_reached_rate_of_valid_sample": 0.0,
            "win_like_rate_of_entry_reached": 0.0,
            "loss_like_rate_of_entry_reached": 0.0,
            "unresolved_rate_of_entry_reached": 0.0,
            "valid_sample_definition": valid_sample_definition,
            "winrate_definition": winrate_definition,
            "safety_note": safety_note,
        }

    outcome_series = outcomes_df["outcome"].astype("object")
    total_rows = int(len(outcomes_df))
    no_ohlcv_rows = int((outcome_series == "no_ohlcv").sum())
    valid_sample_rows = int(total_rows - no_ohlcv_rows)
    entry_reached_rows = int(outcome_series.isin(entry_reached_outcomes).sum())
    win_like_rows = int(outcome_series.isin({"tp1_first", "tp2_first"}).sum())
    loss_like_rows = int((outcome_series == "sl_first").sum())
    unresolved_entry_rows = int(outcome_series.isin({"timeout", "ambiguous", "entry_reached"}).sum())
    not_entered_rows = int((outcome_series == "not_entered").sum())
    pending_rows = int((outcome_series == "pending").sum())

    return {
        "total_rows": total_rows,
        "no_ohlcv_rows": no_ohlcv_rows,
        "valid_sample_rows": valid_sample_rows,
        "entry_reached_rows": entry_reached_rows,
        "win_like_rows": win_like_rows,
        "loss_like_rows": loss_like_rows,
        "unresolved_entry_rows": unresolved_entry_rows,
        "not_entered_rows": not_entered_rows,
        "pending_rows": pending_rows,
        "valid_sample_rate": float(valid_sample_rows / total_rows) if total_rows else 0.0,
        "entry_reached_rate_of_valid_sample": float(entry_reached_rows / valid_sample_rows) if valid_sample_rows else 0.0,
        "win_like_rate_of_entry_reached": float(win_like_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "loss_like_rate_of_entry_reached": float(loss_like_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "unresolved_rate_of_entry_reached": float(unresolved_entry_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "valid_sample_definition": valid_sample_definition,
        "winrate_definition": winrate_definition,
        "safety_note": safety_note,
    }


def build_intraperiod_evidence_quality_summary(outcomes_df: pd.DataFrame | None) -> dict[str, Any]:
    valid_sample_summary = summarize_intraperiod_valid_sample_winrate(outcomes_df)
    return {
        "valid_sample_definition": valid_sample_summary["valid_sample_definition"],
        "total_rows": valid_sample_summary["total_rows"],
        "no_ohlcv_rows": valid_sample_summary["no_ohlcv_rows"],
        "valid_sample_rows": valid_sample_summary["valid_sample_rows"],
        "entry_reached_rows": valid_sample_summary["entry_reached_rows"],
        "win_like_rows": valid_sample_summary["win_like_rows"],
        "loss_like_rows": valid_sample_summary["loss_like_rows"],
        "unresolved_entry_rows": valid_sample_summary["unresolved_entry_rows"],
        "potential_fakeout": valid_sample_summary["loss_like_rows"],
        "potential_missed_turn": valid_sample_summary["win_like_rows"],
        "bad_entry_timing": valid_sample_summary["unresolved_entry_rows"],
        "safety_note": valid_sample_summary["safety_note"],
    }


def summarize_intraperiod_entry_reached_outcomes(outcomes_df: pd.DataFrame | None) -> dict[str, Any]:
    entry_reached_definition = "tp1_first, tp2_first, sl_first, timeout, ambiguous, entry_reached"
    safety_note = "report-only / not FORMAL_GO / no automatic order / human decides manually"
    entry_reached_outcomes = {
        "tp1_first",
        "tp2_first",
        "sl_first",
        "timeout",
        "ambiguous",
        "entry_reached",
    }
    unresolved_outcomes = {"timeout", "ambiguous", "entry_reached"}

    if outcomes_df is None or outcomes_df.empty or "outcome" not in outcomes_df.columns:
        return {
            "entry_reached_rows": 0,
            "tp1_first_rows": 0,
            "tp2_first_rows": 0,
            "sl_first_rows": 0,
            "timeout_rows": 0,
            "ambiguous_rows": 0,
            "open_entry_reached_rows": 0,
            "resolved_exit_rows": 0,
            "unresolved_entry_rows": 0,
            "tp1_first_rate_of_entry_reached": 0.0,
            "tp2_first_rate_of_entry_reached": 0.0,
            "sl_first_rate_of_entry_reached": 0.0,
            "timeout_rate_of_entry_reached": 0.0,
            "ambiguous_rate_of_entry_reached": 0.0,
            "open_entry_reached_rate_of_entry_reached": 0.0,
            "resolved_exit_rate_of_entry_reached": 0.0,
            "unresolved_entry_rate_of_entry_reached": 0.0,
            "entry_reached_definition": entry_reached_definition,
            "safety_note": safety_note,
        }

    outcome_series = outcomes_df["outcome"].astype("object")
    entry_reached_rows = int(outcome_series.isin(entry_reached_outcomes).sum())
    tp1_first_rows = int((outcome_series == "tp1_first").sum())
    tp2_first_rows = int((outcome_series == "tp2_first").sum())
    sl_first_rows = int((outcome_series == "sl_first").sum())
    timeout_rows = int((outcome_series == "timeout").sum())
    ambiguous_rows = int((outcome_series == "ambiguous").sum())
    open_entry_reached_rows = int((outcome_series == "entry_reached").sum())
    resolved_exit_rows = int(tp1_first_rows + tp2_first_rows + sl_first_rows)
    unresolved_entry_rows = int(timeout_rows + ambiguous_rows + open_entry_reached_rows)

    return {
        "entry_reached_rows": entry_reached_rows,
        "tp1_first_rows": tp1_first_rows,
        "tp2_first_rows": tp2_first_rows,
        "sl_first_rows": sl_first_rows,
        "timeout_rows": timeout_rows,
        "ambiguous_rows": ambiguous_rows,
        "open_entry_reached_rows": open_entry_reached_rows,
        "resolved_exit_rows": resolved_exit_rows,
        "unresolved_entry_rows": unresolved_entry_rows,
        "tp1_first_rate_of_entry_reached": float(tp1_first_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "tp2_first_rate_of_entry_reached": float(tp2_first_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "sl_first_rate_of_entry_reached": float(sl_first_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "timeout_rate_of_entry_reached": float(timeout_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "ambiguous_rate_of_entry_reached": float(ambiguous_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "open_entry_reached_rate_of_entry_reached": float(open_entry_reached_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "resolved_exit_rate_of_entry_reached": float(resolved_exit_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "unresolved_entry_rate_of_entry_reached": float(unresolved_entry_rows / entry_reached_rows) if entry_reached_rows else 0.0,
        "entry_reached_definition": entry_reached_definition,
        "safety_note": safety_note,
    }


def _normalize_dimension_value(value: Any) -> str:
    if value is None:
        return "(blank)"
    if isinstance(value, str):
        return value if value.strip() else "(blank)"
    if pd.isna(value):
        return "(blank)"
    return str(value)


def summarize_intraperiod_candidate_dimension_breakdowns(outcomes_df: pd.DataFrame | None) -> dict[str, Any]:
    dimension_names = ("candidate_type", "side", "active_primary_action")
    breakdowns: dict[str, Any] = {dimension: {} for dimension in dimension_names}

    if outcomes_df is None or outcomes_df.empty or "outcome" not in outcomes_df.columns:
        return breakdowns

    for dimension in dimension_names:
        if dimension not in outcomes_df.columns:
            breakdowns[dimension] = {}
            continue

        working_df = outcomes_df.loc[:, [dimension, "outcome"]].copy()
        working_df[dimension] = working_df[dimension].map(_normalize_dimension_value)
        dimension_breakdown: dict[str, Any] = {}
        for dimension_value, group_df in working_df.groupby(dimension, sort=True):
            dimension_breakdown[str(dimension_value)] = summarize_intraperiod_valid_sample_winrate(group_df)
        breakdowns[dimension] = dimension_breakdown

    return breakdowns


def summarize_intraperiod_ohlcv_source_coverage(
    candidates_df: pd.DataFrame | None,
    ohlcv_df: pd.DataFrame | None,
    *,
    timeout_hours: float = 24.0,
) -> dict[str, Any]:
    coverage_note = (
        "report-only coverage summary from candidate timestamps and valid OHLCV bars; "
        "missing windows indicate source coverage gaps, not trading logic"
    )
    safety_note = "report-only / not FORMAL_GO / no automatic order / human decides manually"

    candidate_rows = int(len(candidates_df)) if candidates_df is not None else 0
    if candidates_df is None or candidates_df.empty:
        return {
            "candidate_rows": candidate_rows,
            "ohlcv_input_rows": 0,
            "ohlcv_valid_rows": 0,
            "candidate_timestamp_rows": 0,
            "missing_candidate_timestamp_rows": 0,
            "window_covered_rows": 0,
            "window_missing_rows": 0,
            "no_global_ohlcv_risk_rows": 0,
            "window_missing_rate": 0.0,
            "ohlcv_start": "",
            "ohlcv_end": "",
            "coverage_note": coverage_note,
            "safety_note": safety_note,
        }

    ohlcv_input_rows = int(len(ohlcv_df)) if ohlcv_df is not None else 0
    ohlcv_records = _ohlcv_records(ohlcv_df)
    ohlcv_valid_rows = int(len(ohlcv_records))
    candidate_timestamp_rows = 0
    missing_candidate_timestamp_rows = 0
    window_covered_rows = 0
    window_missing_rows = 0
    coverage_start = ohlcv_records[0]["dt"] if ohlcv_records else None
    coverage_end = ohlcv_records[-1]["dt"] if ohlcv_records else None
    if candidates_df is not None and not candidates_df.empty:
        for candidate in candidates_df.to_dict(orient="records"):
            candidate_ts = _candidate_timestamp(candidate)
            if candidate_ts is None:
                missing_candidate_timestamp_rows += 1
                continue

            candidate_timestamp_rows += 1
            candidate_ts = _normalize_dt(candidate_ts)
            window_end = candidate_ts + timedelta(hours=float(timeout_hours))
            if any(candidate_ts <= record["dt"] <= window_end for record in ohlcv_records):
                window_covered_rows += 1
            else:
                window_missing_rows += 1

    return {
        "candidate_rows": candidate_rows,
        "ohlcv_input_rows": ohlcv_input_rows,
        "ohlcv_valid_rows": ohlcv_valid_rows,
        "candidate_timestamp_rows": candidate_timestamp_rows,
        "missing_candidate_timestamp_rows": missing_candidate_timestamp_rows,
        "window_covered_rows": window_covered_rows,
        "window_missing_rows": window_missing_rows,
        "no_global_ohlcv_risk_rows": candidate_rows if ohlcv_valid_rows == 0 else 0,
        "window_missing_rate": float(window_missing_rows / candidate_timestamp_rows) if candidate_timestamp_rows else 0.0,
        "ohlcv_start": coverage_start.isoformat() if coverage_start is not None else "",
        "ohlcv_end": coverage_end.isoformat() if coverage_end is not None else "",
        "coverage_note": coverage_note,
        "safety_note": safety_note,
    }


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
        if tp2_hit:
            exit_index = index
            exit_reason = "tp2"
            outcome = "tp2_first"
            break
        if tp1_hit:
            exit_index = index
            exit_reason = "tp1"
            outcome = "tp1_first"
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


def build_active_plan_intraperiod_outcome_rows(
    candidates_df: pd.DataFrame | None,
    ohlcv_df: pd.DataFrame | None,
    *,
    now: datetime | None = None,
    timeout_hours: float = 24.0,
) -> pd.DataFrame:
    if candidates_df is None or candidates_df.empty:
        return pd.DataFrame(columns=MIN_OUTCOME_COLUMNS)

    rows: list[dict[str, Any]] = []
    for candidate in candidates_df.to_dict(orient="records"):
        evaluated = evaluate_active_plan_intraperiod_candidate(
            candidate,
            ohlcv_df,
            now=now,
            timeout_hours=timeout_hours,
        )
        row = {key: _blank_if_missing(value) for key, value in evaluated.items()}
        for column in MIN_OUTCOME_COLUMNS:
            row.setdefault(column, "")
        rows.append(row)

    output_df = pd.DataFrame(rows)
    ordered_columns = MIN_OUTCOME_COLUMNS + [column for column in output_df.columns if column not in MIN_OUTCOME_COLUMNS]
    return output_df.loc[:, ordered_columns]


def write_active_plan_intraperiod_outcomes(
    candidates_csv_path: str | Path,
    ohlcv_df: pd.DataFrame | None,
    output_csv_path: str | Path,
    *,
    now: datetime | None = None,
    timeout_hours: float = 24.0,
) -> pd.DataFrame:
    candidates_df = pd.read_csv(candidates_csv_path)
    output_df = build_active_plan_intraperiod_outcome_rows(
        candidates_df,
        ohlcv_df,
        now=now,
        timeout_hours=timeout_hours,
    )
    output_df.to_csv(output_csv_path, index=False)
    return output_df


__all__ = [
    "MIN_OUTCOME_COLUMNS",
    "build_active_plan_intraperiod_outcome_rows",
    "evaluate_active_plan_intraperiod_candidate",
    "summarize_intraperiod_candidate_dimension_breakdowns",
    "build_intraperiod_evidence_quality_summary",
    "summarize_intraperiod_entry_reached_outcomes",
    "summarize_intraperiod_ohlcv_source_coverage",
    "summarize_intraperiod_outcome_coverage",
    "summarize_intraperiod_valid_sample_winrate",
    "write_active_plan_intraperiod_outcomes",
]
