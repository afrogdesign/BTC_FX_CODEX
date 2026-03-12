from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import load_config
from src.data.fetcher import FetchConfig, fetch_klines, get_server_time_ms


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW_NOTE = Path(
    "/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_デジタルスキル/00_PROJECT/FX/トレード支援システム/📝通知レビュー.md"
)
JST = ZoneInfo("Asia/Tokyo")

OUTCOME_HEADER = [
    "signal_id",
    "timestamp_jst",
    "bias",
    "prelabel",
    "signal_tier",
    "base_price",
    "atr_15m_value",
    "forward_price_1h",
    "forward_price_4h",
    "forward_price_12h",
    "forward_price_24h",
    "signal_based_MFE_4h",
    "signal_based_MAE_4h",
    "signal_based_MFE_12h",
    "signal_based_MAE_12h",
    "signal_based_MFE_24h",
    "signal_based_MAE_24h",
    "entry_ready_based_MFE_4h",
    "entry_ready_based_MAE_4h",
    "entry_ready_based_MFE_12h",
    "entry_ready_based_MAE_12h",
    "entry_ready_based_MFE_24h",
    "entry_ready_based_MAE_24h",
    "direction_outcome",
    "entry_outcome",
    "wait_outcome",
    "skip_outcome",
    "tp1_hit_first",
    "outcome",
    "support_touch_result",
    "support_hold_result",
    "resistance_touch_result",
    "resistance_hold_result",
    "evaluation_status",
    "evaluated_at_utc",
]

USER_REVIEW_HEADER = [
    "signal_id",
    "timestamp_jst",
    "subject",
    "auto_eval_summary",
    "user_verdict",
    "usefulness_1to5",
    "would_trade",
    "actual_move_driver",
    "logic_validated",
    "memo",
    "review_status",
    "reviewed_at_utc",
]

REVIEW_NOTE_COLUMNS = [
    "signal_id",
    "timestamp_jst",
    "subject",
    "auto_eval_summary",
    "user_verdict",
    "usefulness_1to5",
    "would_trade",
    "actual_move_driver",
    "logic_validated",
    "memo",
    "review_status",
]

SHADOW_HEADER = [
    "signal_id",
    "timestamp_jst",
    "price",
    "bias",
    "regime",
    "phase",
    "long_score",
    "short_score",
    "score_gap",
    "confidence",
    "top_positive_factors",
    "top_negative_factors",
    "prelabel",
    "prelabel_primary_reason",
    "location_risk",
    "primary_setup_status",
    "invalid_reason",
    "signal_tier",
    "ai_decision",
    "ai_confidence",
    "was_notified",
    "notify_reason",
    "suppress_reason",
    "data_quality_flag",
    "data_missing_fields",
    "signal_based_MFE_4h",
    "signal_based_MAE_4h",
    "signal_based_MFE_12h",
    "signal_based_MAE_12h",
    "signal_based_MFE_24h",
    "signal_based_MAE_24h",
    "entry_ready_based_MFE_4h",
    "entry_ready_based_MAE_4h",
    "entry_ready_based_MFE_12h",
    "entry_ready_based_MAE_12h",
    "entry_ready_based_MFE_24h",
    "entry_ready_based_MAE_24h",
    "tp1_hit_first",
    "outcome",
    "direction_outcome",
    "entry_outcome",
    "wait_outcome",
    "skip_outcome",
    "support_hold_result",
    "resistance_hold_result",
    "risk_flags",
    "warning_flags",
    "no_trade_flags",
    "summary_subject",
    "actual_move_driver",
    "logic_validated",
    "review_status",
    "user_verdict",
    "usefulness_1to5",
    "would_trade",
    "memo",
    "evaluation_status",
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
]

VALID_USER_VERDICTS = {
    "",
    "useful_entry",
    "useful_wait",
    "useful_skip",
    "too_early",
    "too_late",
    "low_value",
}
VALID_WOULD_TRADE = {"", "yes", "no", "conditional"}
VALID_REVIEW_STATUS = {"pending", "done"}
VALID_MOVE_DRIVERS = {"", "technical", "news", "macro", "unknown"}

TECHNICAL_REASON_CODES = {
    "balanced_location",
    "lower_liquidity_distance",
    "upper_liquidity_distance",
    "ask_wall_distance",
    "bid_wall_distance",
    "liquidation_cluster_distance",
    "sweep_incomplete",
    "orderbook_ask_heavy",
    "orderbook_bid_heavy",
    "cvd_bearish_divergence",
    "cvd_bullish_divergence",
    "short_cover_risk",
    "long_flush_exhaustion",
}


def _parse_dt(value: str) -> datetime | None:
    stripped = (value or "").strip()
    if not stripped:
        return None
    try:
        if stripped.endswith("Z"):
            return datetime.fromisoformat(stripped.replace("Z", "+00:00"))
        return datetime.fromisoformat(stripped)
    except ValueError:
        return None


def _parse_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _split_values(value: str) -> list[str]:
    if not value:
        return []
    stripped = str(value).strip()
    if stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [part.strip() for part in stripped.split(",") if part.strip()]


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def _write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    _ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return path


def _upsert_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]], key_field: str) -> Path:
    existing = {row.get(key_field, ""): row for row in _load_csv_rows(path) if row.get(key_field, "")}
    for row in rows:
        key = str(row.get(key_field, "")).strip()
        if not key:
            continue
        current = existing.get(key, {})
        merged = {field: current.get(field, "") for field in fieldnames}
        for field in fieldnames:
            if field in row:
                merged[field] = row.get(field, "")
        existing[key] = merged
    ordered = sorted(existing.values(), key=lambda row: row.get("timestamp_jst", ""), reverse=True)
    return _write_csv_rows(path, fieldnames, ordered)


def _build_fetch_cfg(cfg: Any) -> FetchConfig:
    return FetchConfig(
        base_url=cfg.MEXC_BASE_URL,
        symbol=cfg.MEXC_SYMBOL,
        timeout_sec=cfg.API_TIMEOUT_SEC,
        retry_count=cfg.API_RETRY_COUNT,
        request_interval_sec=cfg.REQUEST_INTERVAL_SEC,
    )


def _trade_timestamp_ms(row: dict[str, str]) -> int | None:
    for key in ("timestamp_utc", "timestamp_jst"):
        dt = _parse_dt(row.get(key, ""))
        if dt is not None:
            return int(dt.timestamp() * 1000)
    return None


def _important_candidate(row: dict[str, str]) -> bool:
    signal_tier = str(row.get("signal_tier", "")).strip()
    confidence = int(_parse_float(row.get("confidence"), 0.0))
    return signal_tier in {"strong_machine", "strong_ai_confirmed"} or confidence >= 80


def _load_trade_rows(trades_path: Path, *, include_important_unnotified: bool) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in _load_csv_rows(trades_path):
        signal_id = str(row.get("signal_id", "")).strip()
        if not signal_id:
            continue
        notified = _parse_bool(row.get("was_notified"))
        if notified or (include_important_unnotified and _important_candidate(row)):
            selected.append(row)
    return selected


def _fetch_future_15m_df(cfg: Any, trade_rows: list[dict[str, str]]) -> pd.DataFrame:
    timestamps = [ts for ts in (_trade_timestamp_ms(row) for row in trade_rows) if ts is not None]
    if not timestamps:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    fetch_cfg = _build_fetch_cfg(cfg)
    oldest_ts = min(timestamps)
    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    bars_needed = max(240, int((now_ms - oldest_ts) / (15 * 60 * 1000)) + 140)
    limit = min(max(int(cfg.FETCH_LIMIT_15M), bars_needed), 1500)
    server_ms = get_server_time_ms(fetch_cfg)
    return fetch_klines(fetch_cfg, "15m", limit, server_time_ms=server_ms)


def _window_df(df: pd.DataFrame, signal_ms: int, horizon_ms: int) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    mask = (df["timestamp"] > signal_ms) & (df["timestamp"] <= signal_ms + horizon_ms)
    return df.loc[mask].copy()


def _close_at_or_after(df: pd.DataFrame, target_ms: int) -> float | None:
    if df.empty:
        return None
    rows = df.loc[df["timestamp"] >= target_ms]
    if rows.empty:
        return None
    return float(rows.iloc[0]["close"])


def _mfe_mae_atr(base_price: float, atr_value: float, bias: str, df: pd.DataFrame) -> tuple[float | None, float | None]:
    if df.empty or atr_value <= 0:
        return None, None
    if bias == "long":
        mfe = max(0.0, (float(df["high"].max()) - base_price) / atr_value)
        mae = max(0.0, (base_price - float(df["low"].min())) / atr_value)
        return round(mfe, 4), round(mae, 4)
    if bias == "short":
        mfe = max(0.0, (base_price - float(df["low"].min())) / atr_value)
        mae = max(0.0, (float(df["high"].max()) - base_price) / atr_value)
        return round(mfe, 4), round(mae, 4)
    return None, None


def _evaluate_direction(bias: str, base_price: float, atr_value: float, forward_price_4h: float | None) -> str:
    if forward_price_4h is None or atr_value <= 0:
        return "pending"
    threshold = 0.5 * atr_value
    if bias == "long":
        if forward_price_4h >= base_price + threshold:
            return "correct"
        if forward_price_4h <= base_price - threshold:
            return "wrong"
        return "unclear"
    if bias == "short":
        if forward_price_4h <= base_price - threshold:
            return "correct"
        if forward_price_4h >= base_price + threshold:
            return "wrong"
        return "unclear"
    return "not_applicable"


def _evaluate_entry(prelabel: str, mfe_4h_atr: float | None, mae_4h_atr: float | None) -> str:
    if prelabel != "ENTRY_OK":
        return "not_applicable"
    if mfe_4h_atr is None or mae_4h_atr is None:
        return "pending"
    if mfe_4h_atr >= 1.0 and mae_4h_atr < 0.7:
        return "good_entry"
    return "poor_entry"


def _evaluate_wait(prelabel: str, bias: str, base_price: float, atr_value: float, future_4h: pd.DataFrame) -> str:
    if prelabel != "SWEEP_WAIT":
        return "not_applicable"
    if future_4h.empty or atr_value <= 0:
        return "pending"
    if bias == "long":
        reverse_hit = bool(((base_price - future_4h["low"]) >= atr_value * 0.4).any())
        moved_forward = bool(((future_4h["high"] - base_price) >= atr_value * 1.0).any())
    elif bias == "short":
        reverse_hit = bool(((future_4h["high"] - base_price) >= atr_value * 0.4).any())
        moved_forward = bool(((base_price - future_4h["low"]) >= atr_value * 1.0).any())
    else:
        return "not_applicable"
    if reverse_hit and moved_forward:
        return "wait_was_good"
    if not reverse_hit and moved_forward:
        return "wait_too_strict"
    return "unclear"


def _evaluate_skip(prelabel: str, mfe_4h_atr: float | None, mae_4h_atr: float | None) -> str:
    if prelabel != "NO_TRADE_CANDIDATE":
        return "not_applicable"
    if mfe_4h_atr is None or mae_4h_atr is None:
        return "pending"
    if mae_4h_atr > 0.6 and mfe_4h_atr < 0.8:
        return "skip_was_good"
    if mfe_4h_atr >= 1.0 and mae_4h_atr < 0.6:
        return "skip_too_strict"
    return "unclear"


def _evaluate_zone_hold(
    future_24h: pd.DataFrame,
    *,
    zone_low: float | None,
    zone_high: float | None,
    zone_type: str,
    atr_value: float,
) -> tuple[str, str]:
    if zone_low is None or zone_high is None or atr_value <= 0 or future_24h.empty:
        return "not_applicable", "not_applicable"
    touch_rows = future_24h.loc[(future_24h["high"] >= zone_low) & (future_24h["low"] <= zone_high)]
    if touch_rows.empty:
        return "untouched", "untouched"
    touch_index = touch_rows.index[0]
    after_touch = future_24h.loc[touch_index:]
    if zone_type == "support":
        bounce_level = zone_high + (0.6 * atr_value)
        break_level = zone_low - (0.2 * atr_value)
        for row in after_touch.itertuples(index=False):
            if float(getattr(row, "low")) < break_level:
                return "touched", "broken"
            if float(getattr(row, "high")) >= bounce_level:
                return "touched", "held"
        return "touched", "touched_only"
    bounce_level = zone_low - (0.6 * atr_value)
    break_level = zone_high + (0.2 * atr_value)
    for row in after_touch.itertuples(index=False):
        if float(getattr(row, "high")) > break_level:
            return "touched", "broken"
        if float(getattr(row, "low")) <= bounce_level:
            return "touched", "held"
    return "touched", "touched_only"


def _tp1_vs_stop(future_df: pd.DataFrame, *, side: str, tp1: float | None, stop_loss: float | None) -> str:
    if future_df.empty or tp1 is None or stop_loss is None:
        return ""
    for row in future_df.itertuples(index=False):
        high = float(getattr(row, "high"))
        low = float(getattr(row, "low"))
        if side == "long":
            stop_hit = low <= stop_loss
            tp_hit = high >= tp1
        else:
            stop_hit = high >= stop_loss
            tp_hit = low <= tp1
        if stop_hit and tp_hit:
            return "false"
        if tp_hit:
            return "true"
        if stop_hit:
            return "false"
    return ""


def _derive_trade_outcome(tp1_hit_first: str, direction_outcome: str, mae_24h_atr: float | None) -> str:
    if tp1_hit_first == "true":
        return "win"
    if tp1_hit_first == "false":
        return "loss"
    if direction_outcome == "correct" and (mae_24h_atr or 0.0) < 0.5:
        return "breakeven"
    if direction_outcome in {"correct", "unclear", "wrong"}:
        return "expired"
    return ""


def evaluate_trade_row(trade_row: dict[str, str], future_df: pd.DataFrame) -> dict[str, Any]:
    signal_id = str(trade_row.get("signal_id", "")).strip()
    signal_ms = _trade_timestamp_ms(trade_row)
    if not signal_id or signal_ms is None:
        return {}

    bias = str(trade_row.get("bias", "")).strip()
    prelabel = str(trade_row.get("prelabel", "")).strip()
    signal_tier = str(trade_row.get("signal_tier", "normal")).strip() or "normal"
    base_price = _parse_float(trade_row.get("current_price"), 0.0)
    atr_value = _parse_float(trade_row.get("atr_15m_value"), 0.0)
    primary_setup_status = str(trade_row.get("primary_setup_status", "")).strip()
    primary_setup_side = str(trade_row.get("primary_setup_side", bias)).strip() or bias

    future_1h = _window_df(future_df, signal_ms, 60 * 60 * 1000)
    future_4h = _window_df(future_df, signal_ms, 4 * 60 * 60 * 1000)
    future_12h = _window_df(future_df, signal_ms, 12 * 60 * 60 * 1000)
    future_24h = _window_df(future_df, signal_ms, 24 * 60 * 60 * 1000)

    forward_1h = _close_at_or_after(future_df, signal_ms + (60 * 60 * 1000))
    forward_4h = _close_at_or_after(future_df, signal_ms + (4 * 60 * 60 * 1000))
    forward_12h = _close_at_or_after(future_df, signal_ms + (12 * 60 * 60 * 1000))
    forward_24h = _close_at_or_after(future_df, signal_ms + (24 * 60 * 60 * 1000))

    signal_mfe_4h, signal_mae_4h = _mfe_mae_atr(base_price, atr_value, bias, future_4h)
    signal_mfe_12h, signal_mae_12h = _mfe_mae_atr(base_price, atr_value, bias, future_12h)
    signal_mfe_24h, signal_mae_24h = _mfe_mae_atr(base_price, atr_value, bias, future_24h)

    if primary_setup_status == "ready":
        entry_mfe_4h, entry_mae_4h = signal_mfe_4h, signal_mae_4h
        entry_mfe_12h, entry_mae_12h = signal_mfe_12h, signal_mae_12h
        entry_mfe_24h, entry_mae_24h = signal_mfe_24h, signal_mae_24h
    else:
        entry_mfe_4h = entry_mae_4h = ""
        entry_mfe_12h = entry_mae_12h = ""
        entry_mfe_24h = entry_mae_24h = ""

    direction_outcome = _evaluate_direction(bias, base_price, atr_value, forward_4h)
    tp1_hit_first = _tp1_vs_stop(
        future_24h,
        side=primary_setup_side,
        tp1=_parse_float(trade_row.get("primary_tp1"), 0.0) or None,
        stop_loss=_parse_float(trade_row.get("primary_stop_loss"), 0.0) or None,
    )
    outcome = _derive_trade_outcome(tp1_hit_first, direction_outcome, signal_mae_24h)

    support_touch_result, support_hold_result = _evaluate_zone_hold(
        future_24h,
        zone_low=_parse_float(trade_row.get("nearest_support_low"), 0.0) or None,
        zone_high=_parse_float(trade_row.get("nearest_support_high"), 0.0) or None,
        zone_type="support",
        atr_value=atr_value,
    )
    resistance_touch_result, resistance_hold_result = _evaluate_zone_hold(
        future_24h,
        zone_low=_parse_float(trade_row.get("nearest_resistance_low"), 0.0) or None,
        zone_high=_parse_float(trade_row.get("nearest_resistance_high"), 0.0) or None,
        zone_type="resistance",
        atr_value=atr_value,
    )

    evaluation_status = "complete" if forward_24h is not None else "pending"
    return {
        "signal_id": signal_id,
        "timestamp_jst": trade_row.get("timestamp_jst", ""),
        "bias": bias,
        "prelabel": prelabel,
        "signal_tier": signal_tier,
        "base_price": round(base_price, 4) if base_price else "",
        "atr_15m_value": round(atr_value, 4) if atr_value else "",
        "forward_price_1h": round(forward_1h, 4) if forward_1h is not None else "",
        "forward_price_4h": round(forward_4h, 4) if forward_4h is not None else "",
        "forward_price_12h": round(forward_12h, 4) if forward_12h is not None else "",
        "forward_price_24h": round(forward_24h, 4) if forward_24h is not None else "",
        "signal_based_MFE_4h": signal_mfe_4h if signal_mfe_4h is not None else "",
        "signal_based_MAE_4h": signal_mae_4h if signal_mae_4h is not None else "",
        "signal_based_MFE_12h": signal_mfe_12h if signal_mfe_12h is not None else "",
        "signal_based_MAE_12h": signal_mae_12h if signal_mae_12h is not None else "",
        "signal_based_MFE_24h": signal_mfe_24h if signal_mfe_24h is not None else "",
        "signal_based_MAE_24h": signal_mae_24h if signal_mae_24h is not None else "",
        "entry_ready_based_MFE_4h": entry_mfe_4h,
        "entry_ready_based_MAE_4h": entry_mae_4h,
        "entry_ready_based_MFE_12h": entry_mfe_12h,
        "entry_ready_based_MAE_12h": entry_mae_12h,
        "entry_ready_based_MFE_24h": entry_mfe_24h,
        "entry_ready_based_MAE_24h": entry_mae_24h,
        "direction_outcome": direction_outcome,
        "entry_outcome": _evaluate_entry(prelabel, signal_mfe_4h, signal_mae_4h),
        "wait_outcome": _evaluate_wait(prelabel, bias, base_price, atr_value, future_4h),
        "skip_outcome": _evaluate_skip(prelabel, signal_mfe_4h, signal_mae_4h),
        "tp1_hit_first": tp1_hit_first,
        "outcome": outcome,
        "support_touch_result": support_touch_result,
        "support_hold_result": support_hold_result,
        "resistance_touch_result": resistance_touch_result,
        "resistance_hold_result": resistance_hold_result,
        "evaluation_status": evaluation_status,
        "evaluated_at_utc": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def update_outcomes(
    *,
    base_dir: Path,
    include_important_unnotified: bool = False,
    outcomes_path: Path | None = None,
    trades_path: Path | None = None,
) -> Path:
    cfg = load_config(base_dir)
    trades_path = trades_path or base_dir / "logs" / "csv" / "trades.csv"
    outcomes_path = outcomes_path or base_dir / "logs" / "csv" / "signal_outcomes.csv"

    trade_rows = _load_trade_rows(trades_path, include_important_unnotified=include_important_unnotified)
    future_df = _fetch_future_15m_df(cfg, trade_rows)
    outcome_rows = [row for row in (evaluate_trade_row(trade_row, future_df) for trade_row in trade_rows) if row]
    return _upsert_csv_rows(outcomes_path, OUTCOME_HEADER, outcome_rows, "signal_id")


def _auto_eval_summary(outcome: dict[str, str]) -> str:
    parts = [
        f"方向:{outcome.get('direction_outcome', '') or 'pending'}",
        f"ENTRY:{outcome.get('entry_outcome', '') or 'n/a'}",
        f"WAIT:{outcome.get('wait_outcome', '') or 'n/a'}",
        f"SKIP:{outcome.get('skip_outcome', '') or 'n/a'}",
    ]
    trade_outcome = str(outcome.get("outcome", "")).strip()
    if trade_outcome:
        parts.append(f"結果:{trade_outcome}")
    support = str(outcome.get("support_hold_result", "")).strip()
    resistance = str(outcome.get("resistance_hold_result", "")).strip()
    if support and support != "not_applicable":
        parts.append(f"S:{support}")
    if resistance and resistance != "not_applicable":
        parts.append(f"R:{resistance}")
    return " / ".join(parts)


def _escape_md_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _parse_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip().replace("\\|", "|") for cell in stripped[1:-1].split("|")]


def _load_review_note_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = _parse_markdown_row(line)
        if not cells:
            continue
        if header is None:
            header = cells
            continue
        if all(cell.startswith("---") for cell in cells):
            continue
        if len(cells) != len(header):
            continue
        rows.append({key: value for key, value in zip(header, cells)})
    return rows


def _render_review_note(rows: list[dict[str, str]]) -> str:
    lines = [
        "# 通知レビュー",
        "",
        "このノートは、通知済みシグナルを翌日まとめてレビューするための専用ノートです。",
        "",
        "## 入力ルール",
        "- `user_verdict`: useful_entry / useful_wait / useful_skip / too_early / too_late / low_value",
        "- `would_trade`: yes / no / conditional",
        "- `actual_move_driver`: technical / news / macro / unknown",
        "- `logic_validated` は自動計算欄です。手入力しなくて大丈夫です。",
        "- `review_status`: pending / done",
        "- `memo` では `|` を使わないでください。",
        "",
        "## レビュー一覧",
        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_escape_md_cell(row.get(column, "")) for column in REVIEW_NOTE_COLUMNS) + " |")
    lines.append("")
    return "\n".join(lines)


def export_review_queue(
    *,
    base_dir: Path,
    review_note_path: Path = DEFAULT_REVIEW_NOTE,
    outcomes_path: Path | None = None,
    reviews_path: Path | None = None,
    trades_path: Path | None = None,
) -> Path:
    outcomes_path = outcomes_path or base_dir / "logs" / "csv" / "signal_outcomes.csv"
    reviews_path = reviews_path or base_dir / "logs" / "csv" / "user_reviews.csv"
    trades_path = trades_path or base_dir / "logs" / "csv" / "trades.csv"

    outcomes = {row.get("signal_id", ""): row for row in _load_csv_rows(outcomes_path) if row.get("signal_id", "")}
    trades = {row.get("signal_id", ""): row for row in _load_csv_rows(trades_path) if row.get("signal_id", "")}
    review_rows = {row.get("signal_id", ""): row for row in _load_csv_rows(reviews_path) if row.get("signal_id", "")}

    existing_rows = _load_review_note_rows(review_note_path)
    merged_rows: dict[str, dict[str, str]] = {
        row.get("signal_id", ""): row for row in existing_rows if row.get("signal_id", "")
    }

    for signal_id, row in review_rows.items():
        merged_rows[signal_id] = {
            "signal_id": signal_id,
            "timestamp_jst": row.get("timestamp_jst", ""),
            "subject": row.get("subject", ""),
            "auto_eval_summary": row.get("auto_eval_summary", ""),
            "user_verdict": row.get("user_verdict", ""),
            "usefulness_1to5": row.get("usefulness_1to5", ""),
            "would_trade": row.get("would_trade", ""),
            "actual_move_driver": row.get("actual_move_driver", ""),
            "logic_validated": row.get("logic_validated", ""),
            "memo": row.get("memo", ""),
            "review_status": row.get("review_status", "pending") or "pending",
        }

    for signal_id, outcome in outcomes.items():
        trade = trades.get(signal_id, {})
        if not _parse_bool(trade.get("was_notified")):
            continue
        if outcome.get("evaluation_status") != "complete":
            continue
        current = merged_rows.get(signal_id, {})
        merged_rows[signal_id] = {
            "signal_id": signal_id,
            "timestamp_jst": current.get("timestamp_jst", trade.get("timestamp_jst", outcome.get("timestamp_jst", ""))),
            "subject": current.get("subject", trade.get("summary_subject", "")),
            "auto_eval_summary": current.get("auto_eval_summary", _auto_eval_summary(outcome)),
            "user_verdict": current.get("user_verdict", ""),
            "usefulness_1to5": current.get("usefulness_1to5", ""),
            "would_trade": current.get("would_trade", ""),
            "actual_move_driver": current.get("actual_move_driver", ""),
            "logic_validated": current.get("logic_validated", ""),
            "memo": current.get("memo", ""),
            "review_status": current.get("review_status", "pending") or "pending",
        }

    ordered_rows = sorted(merged_rows.values(), key=lambda row: row.get("timestamp_jst", ""), reverse=True)
    _ensure_parent(review_note_path)
    review_note_path.write_text(_render_review_note(ordered_rows), encoding="utf-8")
    return review_note_path


def import_reviews(
    *,
    base_dir: Path,
    review_note_path: Path = DEFAULT_REVIEW_NOTE,
    reviews_path: Path | None = None,
) -> Path:
    reviews_path = reviews_path or base_dir / "logs" / "csv" / "user_reviews.csv"
    note_rows = _load_review_note_rows(review_note_path)
    imported_rows: list[dict[str, Any]] = []
    reviewed_at = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")

    for row in note_rows:
        signal_id = str(row.get("signal_id", "")).strip()
        review_status = str(row.get("review_status", "")).strip()
        user_verdict = str(row.get("user_verdict", "")).strip()
        would_trade = str(row.get("would_trade", "")).strip()
        usefulness = str(row.get("usefulness_1to5", "")).strip()
        actual_move_driver = str(row.get("actual_move_driver", "")).strip()
        if not signal_id or review_status != "done":
            continue
        if user_verdict not in VALID_USER_VERDICTS:
            raise ValueError(f"invalid user_verdict: {signal_id} -> {user_verdict}")
        if would_trade not in VALID_WOULD_TRADE:
            raise ValueError(f"invalid would_trade: {signal_id} -> {would_trade}")
        if actual_move_driver not in VALID_MOVE_DRIVERS:
            raise ValueError(f"invalid actual_move_driver: {signal_id} -> {actual_move_driver}")
        if usefulness:
            usefulness_int = int(usefulness)
            if usefulness_int < 1 or usefulness_int > 5:
                raise ValueError(f"invalid usefulness_1to5: {signal_id} -> {usefulness}")
        imported_rows.append(
            {
                "signal_id": signal_id,
                "timestamp_jst": row.get("timestamp_jst", ""),
                "subject": row.get("subject", ""),
                "auto_eval_summary": row.get("auto_eval_summary", ""),
                "user_verdict": user_verdict,
                "usefulness_1to5": usefulness,
                "would_trade": would_trade,
                "actual_move_driver": actual_move_driver,
                "logic_validated": row.get("logic_validated", ""),
                "memo": row.get("memo", ""),
                "review_status": review_status,
                "reviewed_at_utc": reviewed_at,
            }
        )

    return _upsert_csv_rows(reviews_path, USER_REVIEW_HEADER, imported_rows, "signal_id")


def _logic_validated(prelabel_primary_reason: str, actual_move_driver: str) -> str:
    reason = str(prelabel_primary_reason or "").strip()
    driver = str(actual_move_driver or "").strip()
    if not reason or not driver:
        return ""
    if driver == "technical":
        return "true" if reason in TECHNICAL_REASON_CODES else "false"
    if driver == "macro":
        return "true" if reason.startswith("macro_") else "false"
    if driver == "news":
        return "true" if reason.startswith("news_") else "false"
    if driver == "unknown":
        return ""
    return "false"


def build_shadow_log(
    *,
    base_dir: Path,
    shadow_path: Path | None = None,
    trades_path: Path | None = None,
    outcomes_path: Path | None = None,
    reviews_path: Path | None = None,
) -> Path:
    shadow_path = shadow_path or base_dir / "logs" / "csv" / "shadow_log.csv"
    trades_path = trades_path or base_dir / "logs" / "csv" / "trades.csv"
    outcomes_path = outcomes_path or base_dir / "logs" / "csv" / "signal_outcomes.csv"
    reviews_path = reviews_path or base_dir / "logs" / "csv" / "user_reviews.csv"

    outcomes = {row.get("signal_id", ""): row for row in _load_csv_rows(outcomes_path) if row.get("signal_id", "")}
    reviews = {row.get("signal_id", ""): row for row in _load_csv_rows(reviews_path) if row.get("signal_id", "")}

    shadow_rows: list[dict[str, Any]] = []
    for trade in _load_csv_rows(trades_path):
        signal_id = str(trade.get("signal_id", "")).strip()
        if not signal_id:
            continue
        outcome = outcomes.get(signal_id, {})
        review = reviews.get(signal_id, {})
        actual_move_driver = review.get("actual_move_driver", "")
        logic_validated = _logic_validated(trade.get("prelabel_primary_reason", ""), actual_move_driver)
        shadow_rows.append(
            {
                "signal_id": signal_id,
                "timestamp_jst": trade.get("timestamp_jst", ""),
                "price": trade.get("current_price", ""),
                "bias": trade.get("bias", ""),
                "regime": trade.get("market_regime", ""),
                "phase": trade.get("phase", ""),
                "long_score": trade.get("long_score", trade.get("long_display_score", "")),
                "short_score": trade.get("short_score", trade.get("short_display_score", "")),
                "score_gap": trade.get("score_gap", ""),
                "confidence": trade.get("confidence", ""),
                "top_positive_factors": trade.get("top_positive_factors", ""),
                "top_negative_factors": trade.get("top_negative_factors", ""),
                "prelabel": trade.get("prelabel", ""),
                "prelabel_primary_reason": trade.get("prelabel_primary_reason", ""),
                "location_risk": trade.get("location_risk", ""),
                "primary_setup_status": trade.get("primary_setup_status", ""),
                "invalid_reason": trade.get("invalid_reason", ""),
                "signal_tier": trade.get("signal_tier", "normal"),
                "ai_decision": trade.get("ai_decision", ""),
                "ai_confidence": trade.get("ai_confidence", ""),
                "was_notified": trade.get("was_notified", ""),
                "notify_reason": trade.get("notify_reason_codes", trade.get("reason_for_notification", "")),
                "suppress_reason": trade.get("suppress_reason_codes", ""),
                "data_quality_flag": trade.get("data_quality_flag", ""),
                "data_missing_fields": trade.get("data_missing_fields", ""),
                "signal_based_MFE_4h": outcome.get("signal_based_MFE_4h", ""),
                "signal_based_MAE_4h": outcome.get("signal_based_MAE_4h", ""),
                "signal_based_MFE_12h": outcome.get("signal_based_MFE_12h", ""),
                "signal_based_MAE_12h": outcome.get("signal_based_MAE_12h", ""),
                "signal_based_MFE_24h": outcome.get("signal_based_MFE_24h", ""),
                "signal_based_MAE_24h": outcome.get("signal_based_MAE_24h", ""),
                "entry_ready_based_MFE_4h": outcome.get("entry_ready_based_MFE_4h", ""),
                "entry_ready_based_MAE_4h": outcome.get("entry_ready_based_MAE_4h", ""),
                "entry_ready_based_MFE_12h": outcome.get("entry_ready_based_MFE_12h", ""),
                "entry_ready_based_MAE_12h": outcome.get("entry_ready_based_MAE_12h", ""),
                "entry_ready_based_MFE_24h": outcome.get("entry_ready_based_MFE_24h", ""),
                "entry_ready_based_MAE_24h": outcome.get("entry_ready_based_MAE_24h", ""),
                "tp1_hit_first": outcome.get("tp1_hit_first", ""),
                "outcome": outcome.get("outcome", ""),
                "direction_outcome": outcome.get("direction_outcome", ""),
                "entry_outcome": outcome.get("entry_outcome", ""),
                "wait_outcome": outcome.get("wait_outcome", ""),
                "skip_outcome": outcome.get("skip_outcome", ""),
                "support_hold_result": outcome.get("support_hold_result", ""),
                "resistance_hold_result": outcome.get("resistance_hold_result", ""),
                "risk_flags": trade.get("risk_flags", ""),
                "warning_flags": trade.get("warning_flags", ""),
                "no_trade_flags": trade.get("no_trade_flags", ""),
                "summary_subject": trade.get("summary_subject", ""),
                "actual_move_driver": actual_move_driver,
                "logic_validated": logic_validated or review.get("logic_validated", ""),
                "review_status": review.get("review_status", ""),
                "user_verdict": review.get("user_verdict", ""),
                "usefulness_1to5": review.get("usefulness_1to5", ""),
                "would_trade": review.get("would_trade", ""),
                "memo": review.get("memo", ""),
                "evaluation_status": outcome.get("evaluation_status", ""),
                "risk_percent_applied": trade.get("risk_percent_applied", ""),
                "planned_risk_usd": trade.get("planned_risk_usd", ""),
                "position_size_usd": trade.get("position_size_usd", ""),
                "loss_streak_at_entry": trade.get("loss_streak_at_entry", ""),
                "phase1_active": trade.get("phase1_active", ""),
                "phase1_activation_reason": trade.get("phase1_activation_reason", ""),
                "max_size_capped": trade.get("max_size_capped", ""),
                "size_reduction_reasons": trade.get("size_reduction_reasons", ""),
                "tp1_price": trade.get("tp1_price", ""),
                "tp2_price": trade.get("tp2_price", ""),
                "breakeven_after_tp1": trade.get("breakeven_after_tp1", ""),
                "trail_atr_multiplier": trade.get("trail_atr_multiplier", ""),
                "timeout_hours": trade.get("timeout_hours", ""),
                "exit_rule_version": trade.get("exit_rule_version", ""),
            }
        )

    shadow_rows.sort(key=lambda row: row.get("timestamp_jst", ""), reverse=True)
    return _write_csv_rows(shadow_path, SHADOW_HEADER, shadow_rows)


def _period_filter(rows: list[dict[str, Any]], period: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    now = datetime.now(tz=JST)
    filtered: list[dict[str, Any]] = []
    previous: list[dict[str, Any]] = []
    if period == "weekly":
        start = now - timedelta(days=7)
        for row in rows:
            dt = _parse_dt(row.get("timestamp_jst", ""))
            if dt is None:
                continue
            if dt >= start:
                filtered.append(row)
        return filtered, []

    current_month = now.strftime("%Y-%m")
    previous_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    for row in rows:
        dt = _parse_dt(row.get("timestamp_jst", ""))
        if dt is None:
            continue
        key = dt.strftime("%Y-%m")
        if key == current_month:
            filtered.append(row)
        elif key == previous_month:
            previous.append(row)
    return filtered, previous


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _sample_note(count: int) -> str:
    return "" if count >= 30 else f" / データ不足 {count}/30"


def _success_flag(row: dict[str, Any]) -> bool | None:
    outcome = str(row.get("outcome", "")).strip()
    if outcome == "win":
        return True
    if outcome in {"loss", "expired"}:
        return False
    direction = str(row.get("direction_outcome", "")).strip()
    if direction == "correct":
        return True
    if direction == "wrong":
        return False
    return None


def _mean_value(rows: list[dict[str, Any]], key: str) -> float:
    values = [_parse_float(row.get(key, ""), default=float("nan")) for row in rows if str(row.get(key, "")).strip()]
    cleaned = [value for value in values if value == value]
    return mean(cleaned) if cleaned else 0.0


def _summary_by_field(rows: list[dict[str, Any]], field: str, labels: list[str] | None = None) -> list[dict[str, Any]]:
    buckets = labels or sorted({str(row.get(field, "")).strip() for row in rows if str(row.get(field, "")).strip()})
    summary: list[dict[str, Any]] = []
    for label in buckets:
        subset = [row for row in rows if str(row.get(field, "")).strip() == label]
        if not subset:
            continue
        settled = [flag for flag in (_success_flag(row) for row in subset) if flag is not None]
        summary.append(
            {
                "label": label,
                "count": len(subset),
                "win_rate": _ratio(sum(1 for flag in settled if flag), len(settled)),
                "avg_mfe": _mean_value(subset, "signal_based_MFE_24h"),
                "avg_mae": _mean_value(subset, "signal_based_MAE_24h"),
            }
        )
    return summary


def _prelabel_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _summary_by_field(rows, "prelabel", ["ENTRY_OK", "RISKY_ENTRY", "SWEEP_WAIT", "NO_TRADE_CANDIDATE"])


def _signal_tier_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _summary_by_field(rows, "signal_tier", ["normal", "strong_machine", "strong_ai_confirmed"])


def _review_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts = Counter(row.get("user_verdict", "") for row in rows if row.get("user_verdict"))
    usefulness = [int(row.get("usefulness_1to5", "0")) for row in rows if str(row.get("usefulness_1to5", "")).isdigit()]
    actual_move_driver_count = sum(1 for row in rows if row.get("actual_move_driver"))
    return {
        "verdicts": verdicts,
        "avg_usefulness": mean(usefulness) if usefulness else 0.0,
        "actual_move_driver_rate": _ratio(actual_move_driver_count, len(rows)),
    }


def _phase1_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase1_rows = [
        row
        for row in rows
        if str(row.get("risk_percent_applied", "")).strip()
        or str(row.get("position_size_usd", "")).strip()
        or str(row.get("exit_rule_version", "")).strip()
    ]
    active_rows = [row for row in phase1_rows if _parse_bool(row.get("phase1_active"))]
    capped_count = sum(1 for row in active_rows if _parse_bool(row.get("max_size_capped")))
    timeout_rows = [row for row in active_rows if str(row.get("timeout_hours", "")).strip()]
    reduced_rows = [row for row in active_rows if _parse_float(row.get("loss_streak_at_entry"), 0.0) > 0]
    return {
        "count": len(phase1_rows),
        "active_count": len(active_rows),
        "reference_count": len(phase1_rows) - len(active_rows),
        "avg_risk_percent": _mean_value(active_rows, "risk_percent_applied"),
        "avg_planned_risk_usd": _mean_value(active_rows, "planned_risk_usd"),
        "avg_position_size_usd": _mean_value(active_rows, "position_size_usd"),
        "avg_loss_streak": _mean_value(active_rows, "loss_streak_at_entry"),
        "avg_reduced_risk_percent": _mean_value(reduced_rows, "risk_percent_applied"),
        "cap_rate": _ratio(capped_count, len(active_rows)),
        "avg_timeout_hours": _mean_value(timeout_rows, "timeout_hours"),
    }


def _negative_outcome(row: dict[str, Any]) -> bool:
    return any(
        row.get(key) in {"poor_entry", "wait_too_strict", "skip_too_strict", "wrong", "loss"}
        for key in ("entry_outcome", "wait_outcome", "skip_outcome", "direction_outcome", "outcome")
    )


def _risk_flag_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    negatives: Counter[str] = Counter()
    for row in rows:
        flags = _split_values(row.get("risk_flags", ""))
        is_negative = _negative_outcome(row)
        for flag in flags:
            counts[flag] += 1
            if is_negative:
                negatives[flag] += 1
    summary: list[dict[str, Any]] = []
    for flag, count in counts.items():
        if count < 10:
            continue
        summary.append({"flag": flag, "count": count, "negative_rate": _ratio(negatives[flag], count)})
    summary.sort(key=lambda item: (item["negative_rate"], item["count"]), reverse=True)
    return summary


def _notification_audit(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for row in rows:
        success = _success_flag(row)
        if success is None:
            continue
        notified = _parse_bool(row.get("was_notified"))
        if notified and success:
            counts["A"] += 1
        elif notified and not success:
            counts["B"] += 1
        elif not notified and success:
            counts["C"] += 1
        else:
            counts["D"] += 1
    return counts


def _profit_factor_proxy(rows: list[dict[str, Any]]) -> float:
    gross_profit = sum(max(_parse_float(row.get("signal_based_MFE_24h"), 0.0), 0.0) for row in rows)
    gross_loss = sum(max(_parse_float(row.get("signal_based_MAE_24h"), 0.0), 0.0) for row in rows)
    if gross_loss <= 0:
        return 0.0
    return gross_profit / gross_loss


def _build_improvement_candidates(rows: list[dict[str, Any]], *, monthly: bool) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    entry_rows = [row for row in rows if row.get("prelabel") == "ENTRY_OK"]
    if entry_rows:
        poor_count = sum(1 for row in entry_rows if row.get("entry_outcome") == "poor_entry")
        poor_rate = _ratio(poor_count, len(entry_rows))
        if poor_count >= 3 and poor_rate >= 0.4:
            candidates.append(
                {
                    "title": "ENTRY_OK が甘め",
                    "reason": f"ENTRY_OK の poor_entry が {poor_count}/{len(entry_rows)} 件 ({_format_pct(poor_rate)})",
                    "evidence_count": poor_count,
                    "category": "location_risk 閾値",
                    "touchpoints": "config.py, src/analysis/position_risk.py",
                }
            )

    wait_rows = [row for row in rows if row.get("prelabel") == "SWEEP_WAIT"]
    if wait_rows:
        strict_count = sum(1 for row in wait_rows if row.get("wait_outcome") == "wait_too_strict")
        strict_rate = _ratio(strict_count, len(wait_rows))
        if strict_count >= 3 and strict_rate >= 0.4:
            candidates.append(
                {
                    "title": "SWEEP_WAIT が厳しめ",
                    "reason": f"wait_too_strict が {strict_count}/{len(wait_rows)} 件 ({_format_pct(strict_rate)})",
                    "evidence_count": strict_count,
                    "category": "risk_flag 重み",
                    "touchpoints": "src/analysis/position_risk.py",
                }
            )

    skip_rows = [row for row in rows if row.get("prelabel") == "NO_TRADE_CANDIDATE"]
    if skip_rows:
        strict_count = sum(1 for row in skip_rows if row.get("skip_outcome") == "skip_too_strict")
        strict_rate = _ratio(strict_count, len(skip_rows))
        if strict_count >= 3 and strict_rate >= 0.35:
            candidates.append(
                {
                    "title": "NO_TRADE_CANDIDATE が強すぎる",
                    "reason": f"skip_too_strict が {strict_count}/{len(skip_rows)} 件 ({_format_pct(strict_rate)})",
                    "evidence_count": strict_count,
                    "category": "location_risk 閾値",
                    "touchpoints": "config.py, src/analysis/position_risk.py",
                }
            )

    normal_rows = [row for row in rows if row.get("signal_tier", "normal") == "normal"]
    strong_ai_rows = [row for row in rows if row.get("signal_tier") == "strong_ai_confirmed"]
    if normal_rows and strong_ai_rows:
        normal_rate = _ratio(sum(1 for row in normal_rows if row.get("direction_outcome") == "correct"), len(normal_rows))
        strong_ai_rate = _ratio(sum(1 for row in strong_ai_rows if row.get("direction_outcome") == "correct"), len(strong_ai_rows))
        if len(strong_ai_rows) >= 3 and strong_ai_rate <= normal_rate:
            candidates.append(
                {
                    "title": "strong_ai_confirmed の優位が薄い",
                    "reason": f"direction correct 率が normal={_format_pct(normal_rate)}, strong_ai_confirmed={_format_pct(strong_ai_rate)}",
                    "evidence_count": len(strong_ai_rows),
                    "category": "signal_tier 条件",
                    "touchpoints": "src/analysis/signal_tier.py",
                }
            )

    verdicts = Counter(row.get("user_verdict", "") for row in rows if row.get("user_verdict"))
    too_early = verdicts.get("too_early", 0)
    low_value = verdicts.get("low_value", 0)
    total_reviews = sum(verdicts.values())
    if total_reviews:
        if too_early >= 3 and _ratio(too_early, total_reviews) >= 0.3:
            candidates.append(
                {
                    "title": "通知が早すぎるケースが多い",
                    "reason": f"too_early が {too_early}/{total_reviews} 件 ({_format_pct(_ratio(too_early, total_reviews))})",
                    "evidence_count": too_early,
                    "category": "通知条件",
                    "touchpoints": "src/notification/trigger.py",
                }
            )
        if low_value >= 3 and _ratio(low_value, total_reviews) >= 0.3:
            candidates.append(
                {
                    "title": "通知価値が低いケースが多い",
                    "reason": f"low_value が {low_value}/{total_reviews} 件 ({_format_pct(_ratio(low_value, total_reviews))})",
                    "evidence_count": low_value,
                    "category": "通知条件",
                    "touchpoints": "src/notification/trigger.py, src/ai/summary.py",
                }
            )

    touched_zone_rows = [
        row
        for row in rows
        if row.get("support_hold_result") in {"held", "broken", "touched_only"}
        or row.get("resistance_hold_result") in {"held", "broken", "touched_only"}
    ]
    if touched_zone_rows:
        held_count = sum(
            1
            for row in touched_zone_rows
            if row.get("support_hold_result") == "held" or row.get("resistance_hold_result") == "held"
        )
        held_rate = _ratio(held_count, len(touched_zone_rows))
        if len(touched_zone_rows) >= 5 and held_rate < 0.4:
            candidates.append(
                {
                    "title": "サポレジの保持率が低い",
                    "reason": f"held が {held_count}/{len(touched_zone_rows)} 件 ({_format_pct(held_rate)})",
                    "evidence_count": len(touched_zone_rows),
                    "category": "サポレジ帯幅",
                    "touchpoints": "src/analysis/support_resistance.py",
                }
            )

    candidates.sort(key=lambda item: item["evidence_count"], reverse=True)
    limit = 2 if monthly else 3
    return candidates[:limit]


def build_feedback_report(
    *,
    base_dir: Path,
    period: str,
    output_md: Path | None = None,
    shadow_path: Path | None = None,
) -> str:
    shadow_path = shadow_path or base_dir / "logs" / "csv" / "shadow_log.csv"
    if not shadow_path.exists():
        build_shadow_log(base_dir=base_dir, shadow_path=shadow_path)
    all_rows = _load_csv_rows(shadow_path)
    rows, previous_rows = _period_filter(all_rows, period)
    completed = [row for row in rows if row.get("evaluation_status") == "complete"]
    previous_completed = [row for row in previous_rows if row.get("evaluation_status") == "complete"]

    lines = [f"# フィードバック分析レポート ({period})", ""]
    lines.append("## 1. 集計概要")
    if completed:
        dt_values = sorted(row.get("timestamp_jst", "") for row in completed if row.get("timestamp_jst", ""))
        if dt_values:
            lines.append(f"- 集計期間: {dt_values[-1][:16].replace('T', ' ')} 〜 {dt_values[0][:16].replace('T', ' ')}")
    lines.append(f"- 総観測件数: {len(completed)}")
    quality_counts = Counter(row.get("data_quality_flag", "") or "unknown" for row in completed)
    quality_text = ", ".join(f"{key}={value}" for key, value in sorted(quality_counts.items())) or "なし"
    lines.append(f"- data_quality_flag 別件数: {quality_text}")
    lines.append(f"- 近似PF: {_profit_factor_proxy(completed):.2f}")
    lines.append("")

    lines.append("## 2. regime別件数・勝率・平均MFE・平均MAE")
    regime_summary = _summary_by_field(completed, "regime")
    if regime_summary:
        for item in regime_summary:
            lines.append(
                f"- {item['label']}: 勝率={_format_pct(item['win_rate'])}, 平均MFE={item['avg_mfe']:.2f}, 平均MAE={item['avg_mae']:.2f} (n={item['count']}){_sample_note(item['count'])}"
            )
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("## 3. signal_tier別件数・勝率・平均MFE・平均MAE")
    tier_summary = _signal_tier_summary(completed)
    if tier_summary:
        for item in tier_summary:
            lines.append(
                f"- {item['label']}: 勝率={_format_pct(item['win_rate'])}, 平均MFE={item['avg_mfe']:.2f}, 平均MAE={item['avg_mae']:.2f} (n={item['count']}){_sample_note(item['count'])}"
            )
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("## 4. prelabel別件数・勝率・平均MFE・平均MAE")
    prelabel_summary = _prelabel_summary(completed)
    if prelabel_summary:
        for item in prelabel_summary:
            lines.append(
                f"- {item['label']}: 勝率={_format_pct(item['win_rate'])}, 平均MFE={item['avg_mfe']:.2f}, 平均MAE={item['avg_mae']:.2f} (n={item['count']}){_sample_note(item['count'])}"
            )
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("## 5. bias別件数・勝率")
    bias_summary = _summary_by_field(completed, "bias", ["long", "short", "wait"])
    if bias_summary:
        for item in bias_summary:
            lines.append(f"- {item['label']}: 勝率={_format_pct(item['win_rate'])} (n={item['count']}){_sample_note(item['count'])}")
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("## 6. 成績指標")
    lines.append(f"- 全体勝率: {_format_pct(_ratio(sum(1 for row in completed if _success_flag(row) is True), sum(1 for row in completed if _success_flag(row) is not None)))}")
    lines.append(f"- 平均MFE(signal_based): {_mean_value(completed, 'signal_based_MFE_24h'):.2f}")
    lines.append(f"- 平均MAE(signal_based): {_mean_value(completed, 'signal_based_MAE_24h'):.2f}")
    lines.append(f"- 平均MFE(entry_ready_based): {_mean_value(completed, 'entry_ready_based_MFE_24h'):.2f}")
    lines.append(f"- 平均MAE(entry_ready_based): {_mean_value(completed, 'entry_ready_based_MAE_24h'):.2f}")
    tp1_pool = [row for row in completed if row.get("tp1_hit_first") in {"true", "false"}]
    lines.append(f"- TP1先行率: {_format_pct(_ratio(sum(1 for row in tp1_pool if row.get('tp1_hit_first') == 'true'), len(tp1_pool)))}")
    lines.append("")

    lines.append("## 7. 通知品質")
    audit = _notification_audit(completed)
    lines.append(f"- A: 通知して良かった = {audit['A']}")
    lines.append(f"- B: 通知したが微妙 = {audit['B']}")
    lines.append(f"- C: 通知しなかったが本当は良かった = {audit['C']}")
    lines.append(f"- D: 通知しなかったので正解 = {audit['D']}")
    lines.append("")

    lines.append("## 8. データ品質とレビュー")
    review_summary = _review_summary(completed)
    lines.append(f"- actual_move_driver 入力率: {_format_pct(review_summary['actual_move_driver_rate'])}")
    if review_summary["verdicts"]:
        for verdict, count in review_summary["verdicts"].most_common():
            lines.append(f"- {verdict}: {count}")
        lines.append(f"- 平均 usefulness: {review_summary['avg_usefulness']:.2f}")
    else:
        lines.append("- 完了レビューはまだありません")
    lines.append("")

    lines.append("## 9. 改善候補")
    improvements = _build_improvement_candidates(completed, monthly=(period == "monthly"))
    if improvements:
        for idx, item in enumerate(improvements, start=1):
            lines.append(f"{idx}. {item['title']}: {item['reason']}")
    else:
        lines.append("- まだ改善候補を絞れるだけのデータがありません")
    lines.append("")

    lines.append("## 10. Phase 1 計画ログ")
    phase1_summary = _phase1_summary(completed)
    if phase1_summary["count"] > 0:
        lines.append(f"- Phase 1 計画付き件数: {phase1_summary['count']}")
        lines.append(f"- 本有効件数: {phase1_summary['active_count']}")
        lines.append(f"- 参考ログ件数: {phase1_summary['reference_count']}")
        lines.append(f"- 平均 risk_percent_applied: {phase1_summary['avg_risk_percent']:.2f}")
        lines.append(f"- 連敗時平均 risk_percent_applied: {phase1_summary['avg_reduced_risk_percent']:.2f}")
        lines.append(f"- 平均 planned_risk_usd: {phase1_summary['avg_planned_risk_usd']:.2f}")
        lines.append(f"- 平均 position_size_usd: {phase1_summary['avg_position_size_usd']:.2f}")
        lines.append(f"- 平均 loss_streak_at_entry: {phase1_summary['avg_loss_streak']:.2f}")
        lines.append(f"- max_size_capped 発生率: {_format_pct(phase1_summary['cap_rate'])}")
        lines.append(f"- 平均 timeout_hours: {phase1_summary['avg_timeout_hours']:.2f}")
    else:
        lines.append("- まだ Phase 1 計画ログは集計対象にありません")
    lines.append("")

    if period == "weekly":
        lines.append("## 11. risk_flags 有効性比較")
        risk_flags = _risk_flag_summary(completed)
        if risk_flags:
            for item in risk_flags:
                lines.append(f"- {item['flag']}: negative_rate={_format_pct(item['negative_rate'])} (n={item['count']})")
        else:
            lines.append("- 比較対象となる risk_flag はまだありません")
        lines.append("")
    else:
        lines.append("## 11. 前月比")
        if previous_completed:
            lines.append(f"- 前月件数: {len(previous_completed)}")
            lines.append(f"- 今月との差: {len(completed) - len(previous_completed)} 件")
        else:
            lines.append("- 前月データはまだありません")
        lines.append("")
        lines.append("## 12. 設定変更提案")
        if improvements:
            for item in improvements:
                lines.append(
                    f"- {item['category']} / 変更候補: {item['reason']} / 根拠件数 {item['evidence_count']} / 触る場所 {item['touchpoints']}"
                )
        else:
            lines.append("- 今月は変更候補なし。現設定を維持")
        lines.append("")

    report = "\n".join(lines)
    if output_md is not None:
        _ensure_parent(output_md)
        output_md.write_text(report, encoding="utf-8")
    return report


def daily_sync(
    *,
    base_dir: Path,
    review_note_path: Path = DEFAULT_REVIEW_NOTE,
    output_md: Path | None = None,
) -> dict[str, Path]:
    outcomes_path = update_outcomes(base_dir=base_dir)
    reviews_path = import_reviews(base_dir=base_dir, review_note_path=review_note_path)
    shadow_path = build_shadow_log(base_dir=base_dir, outcomes_path=outcomes_path, reviews_path=reviews_path)
    review_note = export_review_queue(
        base_dir=base_dir,
        review_note_path=review_note_path,
        outcomes_path=outcomes_path,
        reviews_path=reviews_path,
    )
    if output_md is None:
        today = datetime.now(tz=JST).strftime("%Y%m%d")
        output_md = base_dir / "運用資料" / "reports" / f"feedback_daily_sync_{today}.md"
    build_feedback_report(base_dir=base_dir, period="weekly", output_md=output_md, shadow_path=shadow_path)
    return {
        "outcomes_path": outcomes_path,
        "reviews_path": reviews_path,
        "shadow_path": shadow_path,
        "review_note_path": review_note,
        "report_path": output_md,
    }


def _default_report_path(base_dir: Path, period: str) -> Path:
    now = datetime.now(tz=JST)
    if period == "weekly":
        return base_dir / "運用資料" / "reports" / f"feedback_weekly_{now.strftime('%Y%m%d')}.md"
    return base_dir / "運用資料" / "reports" / f"feedback_monthly_{now.strftime('%Y-%m')}.md"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BTC monitor のログ活用基盤ツール")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update_parser = subparsers.add_parser("update-outcomes")
    update_parser.add_argument("--include-important-unnotified", action="store_true")

    shadow_parser = subparsers.add_parser("build-shadow-log")
    shadow_parser.add_argument("--shadow-path")

    export_parser = subparsers.add_parser("export-review-queue")
    export_parser.add_argument("--review-note", default=str(DEFAULT_REVIEW_NOTE))

    import_parser = subparsers.add_parser("import-reviews")
    import_parser.add_argument("--review-note", default=str(DEFAULT_REVIEW_NOTE))

    report_parser = subparsers.add_parser("build-feedback-report")
    report_parser.add_argument("--period", choices=["weekly", "monthly"], required=True)
    report_parser.add_argument("--output-md")

    sync_parser = subparsers.add_parser("daily-sync")
    sync_parser.add_argument("--review-note", default=str(DEFAULT_REVIEW_NOTE))
    sync_parser.add_argument("--output-md")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    base_dir = BASE_DIR

    if args.command == "update-outcomes":
        path = update_outcomes(base_dir=base_dir, include_important_unnotified=bool(args.include_important_unnotified))
        print(path)
        return

    if args.command == "build-shadow-log":
        path = build_shadow_log(base_dir=base_dir, shadow_path=Path(args.shadow_path) if args.shadow_path else None)
        print(path)
        return

    if args.command == "export-review-queue":
        path = export_review_queue(base_dir=base_dir, review_note_path=Path(args.review_note))
        print(path)
        return

    if args.command == "import-reviews":
        path = import_reviews(base_dir=base_dir, review_note_path=Path(args.review_note))
        print(path)
        return

    if args.command == "build-feedback-report":
        output_md = Path(args.output_md) if args.output_md else _default_report_path(base_dir, args.period)
        build_shadow_log(base_dir=base_dir)
        report = build_feedback_report(base_dir=base_dir, period=args.period, output_md=output_md)
        print(output_md)
        if not args.output_md:
            print(report)
        return

    if args.command == "daily-sync":
        output_md = Path(args.output_md) if args.output_md else None
        paths = daily_sync(base_dir=base_dir, review_note_path=Path(args.review_note), output_md=output_md)
        for key, path in paths.items():
            print(f"{key}={path}")
        return


if __name__ == "__main__":
    main()
