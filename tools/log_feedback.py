from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import pandas as pd

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import load_config
from src.data.fetcher import FetchConfig, fetch_klines, get_server_time_ms


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW_NOTE = Path(
    "/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/通知評価シート.md"
)
DEFAULT_REVIEW_FORM = DEFAULT_REVIEW_NOTE.with_name("評価シート入力フォーム.html")
JST = ZoneInfo("Asia/Tokyo")
REVIEW_START_CUTOFF_JST = "2026-03-30T05:05:00+09:00"
REVIEW_SERVER_HOST = "127.0.0.1"
REVIEW_SERVER_PORT = 8765
REVIEW_STATE_VERSION = 1

FORM_VERDICT_OPTIONS = [
    {"value": "", "label": "未選択"},
    {"value": "useful_entry", "label": "役に立った（入る判断）"},
    {"value": "useful_wait", "label": "役に立った（待つ判断）"},
    {"value": "useful_skip", "label": "役に立った（見送り判断）"},
    {"value": "too_early", "label": "早すぎた"},
    {"value": "too_late", "label": "遅すぎた"},
    {"value": "low_value", "label": "価値が低かった"},
]

FORM_WOULD_TRADE_OPTIONS = [
    {"value": "", "label": "未選択"},
    {"value": "yes", "label": "自分なら入る"},
    {"value": "no", "label": "自分なら入らない"},
    {"value": "conditional", "label": "条件つきなら入る"},
]

FORM_MISLEADING_ENTRY_OPTIONS = [
    {"value": "", "label": "未選択"},
    {"value": "no", "label": "誤読しにくかった"},
    {"value": "yes", "label": "エントリー寄りに誤読した"},
]

FORM_MOVE_DRIVER_OPTIONS = [
    {"value": "", "label": "未選択"},
    {"value": "technical", "label": "テクニカル要因"},
    {"value": "news", "label": "ニュース要因"},
    {"value": "macro", "label": "マクロ要因"},
    {"value": "unknown", "label": "よく分からない"},
]

FORM_REVIEW_STATUS_OPTIONS = [
    {"value": "pending", "label": "未完了"},
    {"value": "done", "label": "入力完了"},
]

FORM_USEFULNESS_OPTIONS = [{"value": "", "label": "未選択"}] + [
    {"value": str(score), "label": f"{score}"} for score in range(1, 6)
]

FORM_MEMO_PRESET_OPTIONS = [
    {"value": "", "label": "未選択"},
    {"value": "入る判断に使えた。", "label": "入る判断に使えた"},
    {"value": "待つ判断に使えた。", "label": "待つ判断に使えた"},
    {"value": "見送り判断に使えた。", "label": "見送り判断に使えた"},
    {"value": "方向は悪くないが少し早い。", "label": "少し早い"},
    {"value": "方向は悪くないが少し遅い。", "label": "少し遅い"},
    {"value": "判断材料としては弱い。", "label": "判断材料としては弱い"},
    {"value": "件名がやや強く見えた。", "label": "件名がやや強い"},
    {"value": "本文は分かりやすく、実務判断に使いやすかった。", "label": "本文は分かりやすかった"},
    {"value": "本文が読みにくく、実務判断に使いにくかった。", "label": "本文が読みにくかった"},
    {"value": "特になし", "label": "特になし"},
]

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
    "misleading_entry_like_wording",
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
    "misleading_entry_like_wording",
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
    "raw_confidence",
    "confidence_direction_shadow",
    "confidence_execution_shadow",
    "confidence_wait_shadow",
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
    "summary_variant",
    "advice_variant",
    "evaluation_trace_version",
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
VALID_MISLEADING_ENTRY = {"", "yes", "no"}

USER_VERDICT_LABELS = {
    "useful_entry": "入る判断に使えた",
    "useful_wait": "待つ判断に使えた",
    "useful_skip": "見送り判断に使えた",
    "too_early": "通知が早すぎた",
    "too_late": "通知が遅すぎた",
    "low_value": "価値が低かった",
}

BIAS_LABELS = {
    "long": "long / ロング寄り",
    "short": "short / ショート寄り",
    "wait": "wait / 様子見",
}
PRELABEL_LABELS = {
    "ENTRY_OK": "ENTRY_OK / 位置条件は悪くない",
    "RISKY_ENTRY": "RISKY_ENTRY / 位置はやや注意",
    "SWEEP_WAIT": "SWEEP_WAIT / 流動性回収待ち",
    "NO_TRADE_CANDIDATE": "NO_TRADE_CANDIDATE / 現状は見送り",
}
EVALUATION_LABELS = {
    "complete": "complete / 24時間後評価まで完了",
    "pending": "pending / 24時間後評価待ち",
}
SETUP_LABELS = {
    "ready": "ready / エントリー条件がそろった状態",
    "watch": "watch / 方向はあるが待ちたい状態",
    "invalid": "invalid / 今は見送りが妥当な状態",
    "none": "none / セットアップ未形成",
}
TIER_LABELS = {
    "normal": "normal / 通常通知",
    "strong_machine": "strong_machine / 機械的にかなり好条件",
    "strong_ai_confirmed": "strong_ai_confirmed / AI確認込みの強条件",
}
QUALITY_LABELS = {
    "ok": "ok / データ欠損なし",
    "partial_missing": "partial_missing / 一部データ欠損あり",
    "degraded": "degraded / 品質低下あり",
    "unknown": "unknown / 品質未判定",
}
NOTIFY_REASON_LABELS = {
    "status_upgraded": "status_upgraded / setup が昇格した",
    "bias_changed": "bias_changed / 方向感が wait から long または short に変わった",
    "prelabel_improved": "prelabel_improved / 位置評価が改善した",
    "confidence_jump": "confidence_jump / 信頼度が大きく変化した",
    "agreement_changed": "agreement_changed / AI と機械の一致状況が変わった",
    "signal_tier_upgraded": "signal_tier_upgraded / signal_tier が昇格した",
    "attention_bias_changed": "attention_bias_changed / 注意報の方向が切り替わった",
    "attention_score_crossed": "attention_score_crossed / 注意報スコア条件を超えた",
    "attention_gap_crossed": "attention_gap_crossed / ロングショート差が閾値を超えた",
    "attention_first_detection": "attention_first_detection / 初回の注意報検知",
}

VERDICT_DEFAULTS = {
    "useful_entry": {"would_trade": "yes", "usefulness_1to5": "5"},
    "useful_wait": {"would_trade": "no", "usefulness_1to5": "4"},
    "useful_skip": {"would_trade": "no", "usefulness_1to5": "4"},
    "too_early": {"would_trade": "conditional", "usefulness_1to5": "2"},
    "too_late": {"would_trade": "no", "usefulness_1to5": "2"},
    "low_value": {"would_trade": "no", "usefulness_1to5": "1"},
}

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


def _review_state_path(base_dir: Path) -> Path:
    return base_dir / "logs" / "review" / "review_form_state.json"


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def _is_stale_file(target: Path, sources: list[Path]) -> bool:
    if not target.exists():
        return True
    try:
        target_mtime = target.stat().st_mtime
    except OSError:
        return True
    for source in sources:
        if not source.exists():
            continue
        try:
            if source.stat().st_mtime > target_mtime:
                return True
        except OSError:
            continue
    return False


def _write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    _ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return path


def _load_review_state_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return []
    normalized: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        normalized.append({str(key): str(value or "") for key, value in row.items()})
    return normalized


def _write_review_state(path: Path, rows: list[dict[str, Any]]) -> Path:
    _ensure_parent(path)
    payload = {
        "version": REVIEW_STATE_VERSION,
        "saved_at": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "rows": rows,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
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
        "misleading_entry_like_wording": "",
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
    total = len(rows)
    done_rows = [row for row in rows if str(row.get("review_status", "")).strip() == "done"]
    pending_rows = [row for row in rows if str(row.get("review_status", "")).strip() != "done"]
    latest_updated = max(
        (
            str(row.get("reviewed_at_utc", "")).strip()
            for row in rows
            if str(row.get("reviewed_at_utc", "")).strip()
        ),
        default="未保存",
    )
    form_link = f"[評価シート入力フォーム](file://{DEFAULT_REVIEW_FORM})"
    lines = [
        "# 通知評価シート",
        "",
        "このノートは、新体制の通知レビューの進捗を見るための要約ノートです。",
        "",
        "## 進捗",
        f"- 評価対象は `{REVIEW_START_CUTOFF_JST}` 以降の通知だけです。",
        f"- 総件数: {total}",
        f"- 完了: {len(done_rows)}",
        f"- 未完了: {len(pending_rows)}",
        f"- 最終更新: {latest_updated}",
        f"- 入力画面: {form_link}",
        "",
        "## 最近の完了レビュー",
    ]
    if done_rows:
        for row in done_rows[:5]:
            lines.append(
                "- "
                + " / ".join(
                    part
                    for part in (
                        _format_time_badge(str(row.get("timestamp_jst", ""))),
                        str(row.get("subject", "")).strip(),
                        USER_VERDICT_LABELS.get(str(row.get("user_verdict", "")).strip(), str(row.get("user_verdict", "")).strip()),
                        f"役立ち度 {row.get('usefulness_1to5', '')}".strip(),
                    )
                    if part
                )
            )
    else:
        lines.append("- まだ完了レビューはありません")
    lines.extend(["", "## 未完了通知"])
    if pending_rows:
        for row in pending_rows[:10]:
            lines.append(
                "- "
                + " / ".join(
                    part
                    for part in (
                        _format_time_badge(str(row.get("timestamp_jst", ""))),
                        str(row.get("subject", "")).strip(),
                    )
                    if part
                )
            )
    else:
        lines.append("- 未完了はありません")
    lines.append("")
    return "\n".join(lines)


def _review_form_path(review_note_path: Path) -> Path:
    return review_note_path.with_name("評価シート入力フォーム.html")


def _pending_auto_eval_summary(trade: dict[str, str]) -> str:
    parts = ["事後評価待ち"]
    bias = str(trade.get("bias", "")).strip()
    prelabel = str(trade.get("prelabel", "")).strip()
    setup = str(trade.get("primary_setup_status", "")).strip()
    tier = str(trade.get("signal_tier", "")).strip()
    if bias:
        parts.append(f"bias:{bias}")
    if prelabel:
        parts.append(f"prelabel:{prelabel}")
    if setup:
        parts.append(f"setup:{setup}")
    if tier:
        parts.append(f"tier:{tier}")
    return " / ".join(parts)


def _describe_code(value: str, labels: dict[str, str]) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "未記録"
    return labels.get(raw, f"{raw} / 未定義コード")


def _parse_maybe_json_array(value: str) -> list[str]:
    raw = str(value or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    return [item.strip() for item in raw.split(",") if item.strip()]


def _describe_notify_reason(value: str) -> str:
    items = _parse_maybe_json_array(value)
    if not items:
        return "未記録"
    return " / ".join(_describe_code(item, NOTIFY_REASON_LABELS) for item in items)


def _format_time_badge(timestamp_jst: str) -> str:
    raw = str(timestamp_jst or "").strip()
    if len(raw) >= 16 and "T" in raw:
        return raw[5:10].replace("-", "/") + " " + raw[11:16]
    return raw or "--:--"


def _is_review_target(timestamp_jst: str) -> bool:
    cutoff = _parse_dt(REVIEW_START_CUTOFF_JST)
    current = _parse_dt(str(timestamp_jst or "").strip())
    if cutoff is None or current is None:
        return False
    return current >= cutoff


def _describe_auto_eval_summary(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "未記録"
    return (
        raw.replace("bias:long", f"bias:{BIAS_LABELS['long']}")
        .replace("bias:short", f"bias:{BIAS_LABELS['short']}")
        .replace("bias:wait", f"bias:{BIAS_LABELS['wait']}")
        .replace("prelabel:ENTRY_OK", f"prelabel:{PRELABEL_LABELS['ENTRY_OK']}")
        .replace("prelabel:RISKY_ENTRY", f"prelabel:{PRELABEL_LABELS['RISKY_ENTRY']}")
        .replace("prelabel:SWEEP_WAIT", f"prelabel:{PRELABEL_LABELS['SWEEP_WAIT']}")
        .replace("prelabel:NO_TRADE_CANDIDATE", f"prelabel:{PRELABEL_LABELS['NO_TRADE_CANDIDATE']}")
        .replace("setup:ready", f"setup:{SETUP_LABELS['ready']}")
        .replace("setup:watch", f"setup:{SETUP_LABELS['watch']}")
        .replace("setup:invalid", f"setup:{SETUP_LABELS['invalid']}")
        .replace("setup:none", f"setup:{SETUP_LABELS['none']}")
        .replace("tier:normal", f"tier:{TIER_LABELS['normal']}")
        .replace("tier:strong_machine", f"tier:{TIER_LABELS['strong_machine']}")
        .replace("tier:strong_ai_confirmed", f"tier:{TIER_LABELS['strong_ai_confirmed']}")
    )


def _render_select_html(
    option_list: list[dict[str, str]],
    value: str,
    row_index: int,
    key: str,
) -> str:
    selected_value = str(value or "")
    options_html: list[str] = []
    for item in option_list:
        item_value = str(item.get("value", ""))
        selected = ' selected="selected"' if item_value == selected_value else ""
        options_html.append(
            f'<option value="{html.escape(item_value, quote=True)}"{selected}>{html.escape(str(item.get("label", "")))}</option>'
        )
    return (
        f'<select data-row-index="{row_index}" data-key="{html.escape(key, quote=True)}">'
        + "".join(options_html)
        + "</select>"
    )


def _metric_hint(metric_key: str, value: Any) -> str:
    score = _parse_float(value, -1.0)
    if score < 0:
        return "未記録"
    if metric_key == "direction_strength":
        if score >= 70:
            return "強い"
        if score >= 40:
            return "中くらい"
        return "弱い"
    if metric_key == "execution_readiness":
        if score >= 70:
            return "入りやすい"
        if score >= 40:
            return "条件つき"
        return "まだ入りにくい"
    if score >= 70:
        return "強く待ちたい"
    if score >= 40:
        return "少し待ちたい"
    return "待機圧力は低い"


def _card_is_ready(row: dict[str, str]) -> bool:
    return all(str(row.get(key, "")).strip() for key in ("user_verdict", "would_trade", "usefulness_1to5"))


def _detail_open(row: dict[str, str]) -> bool:
    return any(str(row.get(key, "")).strip() for key in ("user_verdict", "would_trade", "usefulness_1to5", "memo", "actual_move_driver"))


def _render_static_review_cards(rows: list[dict[str, str]], options_payload: dict[str, list[dict[str, str]]]) -> str:
    del options_payload
    cards: list[str] = []
    for index, row in enumerate(rows, start=1):
        time_badge = _format_time_badge(str(row.get("timestamp_jst", "")))
        status_done = str(row.get("review_status", "pending")).strip() == "done"
        verdict_buttons = "".join(
            f'<button type="button" class="choice-pill{" active" if item["value"] == str(row.get("user_verdict", "")) else ""}">{html.escape(str(item["label"]))}</button>'
            for item in FORM_VERDICT_OPTIONS
            if item["value"]
        )
        trade_buttons = "".join(
            f'<button type="button" class="choice-pill{" active" if item["value"] == str(row.get("would_trade", "")) else ""}">{html.escape(str(item["label"]))}</button>'
            for item in FORM_WOULD_TRADE_OPTIONS
            if item["value"]
        )
        usefulness_buttons = "".join(
            f'<button type="button" class="score-pill{" active" if item["value"] == str(row.get("usefulness_1to5", "")) else ""}">{html.escape(str(item["label"]))}</button>'
            for item in FORM_USEFULNESS_OPTIONS
            if item["value"]
        )
        move_driver_buttons = "".join(
            f'<button type="button" class="choice-pill{" active" if item["value"] == str(row.get("actual_move_driver", "")) else ""}">{html.escape(str(item["label"]))}</button>'
            for item in FORM_MOVE_DRIVER_OPTIONS
            if item["value"]
        )
        memo_buttons = "".join(
            f'<button type="button" class="memo-chip{" active" if item["value"] == str(row.get("memo", "")) else ""}">{html.escape(str(item["label"]))}</button>'
            for item in FORM_MEMO_PRESET_OPTIONS
            if item["value"]
        )
        metric_cards = "".join(
            '<div class="metric-card">'
            f'<div class="metric-top"><span class="context-label">{html.escape(label)}</span><span class="metric-hint">{html.escape(_metric_hint(key, value))}</span></div>'
            f'<div class="metric-value">{html.escape(str(value or "未記録"))}</div>'
            "</div>"
            for key, label, value in (
                ("direction_strength", "方向の強さ", str(row.get("confidence_direction_shadow", "")) or "未記録"),
                ("execution_readiness", "実行しやすさ", str(row.get("confidence_execution_shadow", "")) or "未記録"),
                ("wait_pressure", "待機圧力", str(row.get("confidence_wait_shadow", "")) or "未記録"),
            )
        )
        cards.append(
            '<div class="card">'
            f'<div class="card-top"><h3>通知 {index}</h3><div class="time-badge">{html.escape(time_badge)}</div></div>'
            f'<div class="meta">{html.escape(str(row.get("timestamp_jst", "")))} / {html.escape(str(row.get("signal_id", "")))}</div>'
            f'<div class="subject">{html.escape(str(row.get("subject", "")))}</div>'
            '<div class="summary-row">'
            f'<span class="chip">方向感: {html.escape(_describe_code(str(row.get("bias", "")), BIAS_LABELS))}</span>'
            f'<span class="chip">位置評価: {html.escape(_describe_code(str(row.get("prelabel", "")), PRELABEL_LABELS))}</span>'
            f'<span class="chip">24時間後評価: {html.escape(_describe_code(str(row.get("evaluation_status", "") or "pending"), EVALUATION_LABELS))}</span>'
            f'<span class="status-chip{" done" if status_done else ""}">{"完了" if status_done else "未完了"}</span>'
            "</div>"
            '<div class="primary-question">'
            '<div class="section-title">この通知、役に立った？</div>'
            f'<div class="choice-row">{verdict_buttons}</div>'
            "</div>"
            '<div class="detail-panel">'
            '<div class="section-title">判断を残す</div>'
            '<div class="compact-field"><div class="field-title">自分ならどうする？</div>'
            f'<div class="choice-row">{trade_buttons}</div></div>'
            '<div class="compact-field"><div class="field-title">役立ち度 1-5</div>'
            f'<div class="choice-row">{usefulness_buttons}</div></div>'
            f'<button type="button" class="complete-button{" ready" if _card_is_ready(row) else ""}">{"未完了に戻す" if status_done else "完了にする"}</button>'
            f'<details class="detail-box"{" open" if _detail_open(row) else ""}>'
            '<summary>詳細を見る</summary>'
            f'<div class="metric-grid">{metric_cards}</div>'
            f'<div class="detail-text"><strong>通知理由:</strong> {html.escape(_describe_notify_reason(str(row.get("notify_reason", ""))))}</div>'
            f'<div class="detail-text"><strong>自動評価:</strong> {html.escape(_describe_auto_eval_summary(str(row.get("auto_eval_summary", ""))))}</div>'
            '<div class="compact-field"><div class="field-title">値動きの主因</div>'
            f'<div class="choice-row">{move_driver_buttons}</div></div>'
            '<div class="compact-field"><div class="field-title">一言メモ</div>'
            f'<div class="memo-chip-row">{memo_buttons}</div>'
            f'<textarea class="memo-input" rows="3">{html.escape(str(row.get("memo", "")))}</textarea></div>'
            '</details>'
            '</div>'
            "</div>"
        )
    return "".join(cards)


def _render_review_form_html(rows: list[dict[str, str]], review_note_path: Path) -> str:
    page_title = "通知評価シート入力フォーム"
    options_payload = {
        "verdict": FORM_VERDICT_OPTIONS,
        "usefulness": FORM_USEFULNESS_OPTIONS,
        "wouldTrade": FORM_WOULD_TRADE_OPTIONS,
        "moveDriver": FORM_MOVE_DRIVER_OPTIONS,
        "memoPreset": FORM_MEMO_PRESET_OPTIONS,
    }
    rows_payload = []
    for row in rows:
        row_copy = {column: str(row.get(column, "")) for column in REVIEW_NOTE_COLUMNS}
        for extra_key in (
            "bias",
            "prelabel",
            "primary_setup_status",
            "signal_tier",
            "notify_reason",
            "data_quality_flag",
            "evaluation_status",
            "confidence_direction_shadow",
            "confidence_execution_shadow",
            "confidence_wait_shadow",
        ):
            row_copy[extra_key] = str(row.get(extra_key, ""))
        rows_payload.append(row_copy)

    note_name = review_note_path.name
    note_key = str(review_note_path)
    header_text = _render_review_note([])
    initial_cards_html = _render_static_review_cards(rows_payload, options_payload)
    intro = (
        "この画面は、新体制の通知を人が直感的にレビューするための入力フォームです。"
        " 保存すると JSON 正本と CSV、Obsidian 要約が自動で更新されます。"
    )

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page_title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f6f7f8;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --line: #d1d5db;
      --accent: #1d4ed8;
      --accent-soft: #dbeafe;
      --chip: #eef2ff;
      --chip-text: #334155;
      --hero-bg: linear-gradient(135deg, #eff6ff 0%, #f8fafc 55%, #ecfeff 100%);
      --soft-green: #dcfce7;
      --soft-yellow: #fef3c7;
    }}
    body {{
      margin: 0;
      padding: 24px;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", sans-serif;
      line-height: 1.5;
    }}
    .wrap {{
      max-width: 980px;
      margin: 0 auto;
    }}
    .hero, .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }}
    .hero {{
      background: var(--hero-bg);
    }}
    h1, h2, h3 {{
      margin: 0 0 10px;
    }}
    .muted {{
      color: var(--muted);
      font-size: 14px;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 16px;
      align-items: start;
    }}
    .hero-panel {{
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 12px;
      padding: 14px;
    }}
    .hero-panel h2 {{
      font-size: 15px;
      margin-bottom: 8px;
    }}
    .hero-panel ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .hero-panel li {{
      margin-bottom: 6px;
      color: var(--chip-text);
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
      align-items: center;
    }}
    .progress-chip {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.35);
      background: rgba(255, 255, 255, 0.84);
      color: var(--chip-text);
      font-size: 13px;
      padding: 8px 12px;
    }}
    .draft-status {{
      font-size: 13px;
      color: var(--muted);
    }}
    button {{
      border: 0;
      border-radius: 10px;
      padding: 10px 14px;
      background: var(--accent);
      color: #fff;
      cursor: pointer;
      font-size: 14px;
    }}
    button.secondary {{
      background: #475569;
    }}
    .meta {{
      font-size: 14px;
      color: var(--muted);
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }}
    .time-badge {{
      min-width: 84px;
      padding: 8px 12px;
      border-radius: 12px;
      background: #dbeafe;
      color: #1e3a8a;
      font-size: 24px;
      line-height: 1;
      font-weight: 800;
      text-align: center;
      letter-spacing: 0.04em;
    }}
    .subject {{
      font-weight: 700;
      margin: 8px 0 2px;
      font-size: 20px;
    }}
    .summary-row, .choice-row, .memo-chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .summary-row {{
      margin: 12px 0 4px;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--chip);
      color: var(--chip-text);
      font-size: 12px;
      font-weight: 700;
      border: 1px solid #cbd5e1;
    }}
    .status-chip {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid #cbd5e1;
      background: #fff;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    .status-chip.done {{
      background: var(--soft-green);
      border-color: #86efac;
      color: #166534;
    }}
    .primary-question, .detail-panel {{
      margin-top: 12px;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
      background: rgba(255, 255, 255, 0.96);
    }}
    .section-title {{
      font-size: 15px;
      font-weight: 700;
      margin-bottom: 10px;
    }}
    .field-title {{
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .choice-pill, .score-pill, .memo-chip {{
      background: #fff;
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 10px 14px;
      font-size: 14px;
    }}
    .choice-pill.active, .score-pill.active {{
      background: var(--accent-soft);
      color: var(--accent);
      border-color: var(--accent);
    }}
    .memo-chip.active {{
      background: var(--soft-yellow);
      border-color: #f59e0b;
      color: #92400e;
    }}
    .compact-field {{
      margin-top: 14px;
    }}
    .complete-button {{
      margin-top: 14px;
      background: #475569;
    }}
    .complete-button.ready {{
      background: #0f766e;
    }}
    .detail-box {{
      margin-top: 14px;
      border-top: 1px dashed var(--line);
      padding-top: 14px;
    }}
    .detail-box summary {{
      cursor: pointer;
      font-weight: 700;
      color: var(--chip-text);
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}
    .metric-card {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      background: #f8fafc;
    }}
    .metric-top {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 6px;
    }}
    .context-label {{
      display: block;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--muted);
      text-transform: uppercase;
    }}
    .metric-hint {{
      font-size: 12px;
      color: var(--accent);
      font-weight: 700;
    }}
    .metric-value {{
      font-size: 24px;
      font-weight: 700;
      color: var(--text);
    }}
    .detail-text {{
      margin-top: 12px;
      color: var(--chip-text);
      font-size: 14px;
    }}
    textarea {{
      width: 100%;
      min-height: 88px;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      font-family: inherit;
      font-size: 14px;
      box-sizing: border-box;
      background: #fff;
      color: #111827;
    }}
    .status-panel {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
      background: #f8fafc;
      color: var(--chip-text);
    }}
    @media (max-width: 760px) {{
      body {{
        padding: 16px;
      }}
      .hero-grid {{
        grid-template-columns: 1fr;
      }}
      .subject {{
        font-size: 18px;
      }}
      .choice-pill, .score-pill, .memo-chip, button {{
        width: 100%;
      }}
      .choice-row, .memo-chip-row {{
        flex-direction: column;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="hero-grid">
        <div>
          <h1>{html.escape(page_title)}</h1>
          <p>{html.escape(intro)}</p>
          <p class="muted">使い方: まず `この通知、役に立った？` を選ぶ → 補足が必要なら詳細を見る → 完了にする → `保存` を押す。</p>
          <p class="muted">このブラウザでは入力内容を自動で下書き保存します。ページを開き直しても、同じ端末・同じブラウザなら復元されます。</p>
        </div>
        <div class="hero-panel">
          <h2>今の確認軸</h2>
          <ul>
            <li><strong>対象範囲:</strong> 2026-03-30 05:05 JST 以降の通知だけを見る</li>
            <li><strong>最初の問い:</strong> `この通知、役に立った？` を先に決める</li>
            <li><strong>補足確認:</strong> `自分ならどうするか` と `役立ち度 1-5` を埋める</li>
            <li><strong>詳細材料:</strong> 3 指標と通知理由は迷ったときだけ開く</li>
          </ul>
        </div>
      </div>
      <div class="toolbar">
        <span id="progress-chip" class="progress-chip">レビュー進捗: 0 / 0 完了</span>
        <button type="button" class="secondary" onclick="togglePendingOnly()">未完了だけ表示</button>
        <button type="button" class="secondary" onclick="focusNextPending()">次の未完了へ</button>
        <button type="button" onclick="saveToServer()">保存</button>
        <button type="button" class="secondary" onclick="reloadFromServer()">再読込</button>
        <button type="button" class="secondary" onclick="resetSelections()">入力を初期化</button>
        <span id="draft-status" class="draft-status">下書き未保存</span>
      </div>
    </div>

    <div id="cards">{initial_cards_html}</div>

    <div class="card status-panel">
      <h2>保存先</h2>
      <p class="muted">この画面の保存先は JSON 正本です。保存時に CSV と {html.escape(note_name)} の要約も自動更新します。</p>
      <div id="server-status">ローカル補助への接続を確認中です。</div>
    </div>
  </div>

  <script>
    var reviewColumns = {json.dumps(REVIEW_NOTE_COLUMNS, ensure_ascii=False)};
    var options = {json.dumps(options_payload, ensure_ascii=False)};
    var rows = {json.dumps(rows_payload, ensure_ascii=False)};
    var noteName = {json.dumps(note_name, ensure_ascii=False)};
    var noteKey = {json.dumps(note_key, ensure_ascii=False)};
    var noteHeader = {json.dumps(header_text, ensure_ascii=False)};
    var draftStorageKey = 'btc-monitor-review-form:' + noteKey;
    var apiBase = window.location.protocol === 'http:' || window.location.protocol === 'https:' ? '' : 'http://{REVIEW_SERVER_HOST}:{REVIEW_SERVER_PORT}';
    var verdictDefaults = {json.dumps(VERDICT_DEFAULTS, ensure_ascii=False)};
    var showPendingOnly = rows.some(function(row) {{ return String(row.review_status || 'pending') !== 'done'; }});
    var biasLabels = {json.dumps(BIAS_LABELS, ensure_ascii=False)};
    var prelabelLabels = {json.dumps(PRELABEL_LABELS, ensure_ascii=False)};
    var evaluationLabels = {json.dumps(EVALUATION_LABELS, ensure_ascii=False)};
    var setupLabels = {json.dumps(SETUP_LABELS, ensure_ascii=False)};
    var tierLabels = {json.dumps(TIER_LABELS, ensure_ascii=False)};
    var qualityLabels = {json.dumps(QUALITY_LABELS, ensure_ascii=False)};
    var notifyReasonLabels = {json.dumps(NOTIFY_REASON_LABELS, ensure_ascii=False)};
    var autoEvalLabels = {{
      correct: 'correct / 方向は合っていた',
      wrong: 'wrong / 方向は外れた',
      unclear: 'unclear / 判定しきれない',
      pending: 'pending / 評価待ち',
      not_applicable: 'not_applicable / 対象外',
      good_entry: 'good_entry / 入る価値があった',
      poor_entry: 'poor_entry / 入るには弱かった',
      wait_was_good: 'wait_was_good / 待機判断が良かった',
      wait_too_strict: 'wait_too_strict / 待機が厳しすぎた',
      skip_was_good: 'skip_was_good / 見送りが良かった',
      skip_too_strict: 'skip_too_strict / 見送りが厳しすぎた',
      win: 'win / 勝ち相当',
      loss: 'loss / 負け相当',
      breakeven: 'breakeven / 建値相当',
      expired: 'expired / 時間切れ',
      untouched: 'untouched / 未接触',
      held: 'held / 守られた',
      broken: 'broken / 抜けた',
      touched: 'touched / 接触した',
      touched_only: 'touched_only / 接触のみ',
      'n/a': 'n/a / 対象外',
    }};

    function formatContext(value, fallback) {{
      var defaultValue = fallback || '未記録';
      return value && String(value).trim() ? String(value) : defaultValue;
    }}

    function parseMaybeJsonArray(value) {{
      var raw = String(value || '').trim();
      if (!raw) return [];
      if (raw.charAt(0) === '[') {{
        try {{
          var parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) return parsed.map(function(item) {{ return String(item); }});
        }} catch (_error) {{
        }}
      }}
      return raw.split(',').map(function(item) {{ return item.trim(); }}).filter(Boolean);
    }}

    function describeCode(value, labels) {{
      var raw = String(value || '').trim();
      if (!raw) return '未記録';
      return labels[raw] || (raw + ' / 未定義コード');
    }}

    function describeBias(value) {{
      return describeCode(value, biasLabels);
    }}

    function describePrelabel(value) {{
      return describeCode(value, prelabelLabels);
    }}

    function describeEvaluation(value) {{
      return describeCode(value, evaluationLabels);
    }}

    function describeSetup(value) {{
      return describeCode(value, setupLabels);
    }}

    function describeTier(value) {{
      return describeCode(value, tierLabels);
    }}

    function describeNotifyReason(value) {{
      var items = parseMaybeJsonArray(value);
      if (!items.length) return '未記録';
      return items.map(function(item) {{ return describeCode(item, notifyReasonLabels); }}).join(' / ');
    }}

    function describeAutoEvalSummary(value) {{
      var raw = String(value || '').trim();
      if (!raw) return '未記録';
      return raw
        .replace(/bias:([A-Za-z_]+)/g, function(_m, code) {{ return 'bias:' + describeBias(code); }})
        .replace(/prelabel:([A-Z_]+)/g, function(_m, code) {{ return 'prelabel:' + describePrelabel(code); }})
        .replace(/setup:([A-Za-z_]+)/g, function(_m, code) {{ return 'setup:' + describeSetup(code); }})
        .replace(/tier:([A-Za-z_]+)/g, function(_m, code) {{ return 'tier:' + describeTier(code); }})
        .replace(/方向:([A-Za-z_]+)/g, function(_m, code) {{ return '方向:' + describeCode(code, autoEvalLabels); }})
        .replace(/ENTRY:([A-Za-z_]+)/g, function(_m, code) {{ return 'ENTRY:' + describeCode(code, autoEvalLabels); }})
        .replace(/WAIT:([A-Za-z_]+)/g, function(_m, code) {{ return 'WAIT:' + describeCode(code, autoEvalLabels); }})
        .replace(/SKIP:([A-Za-z_]+)/g, function(_m, code) {{ return 'SKIP:' + describeCode(code, autoEvalLabels); }})
        .replace(/結果:([A-Za-z_]+)/g, function(_m, code) {{ return '結果:' + describeCode(code, autoEvalLabels); }})
        .replace(/S:([A-Za-z_]+)/g, function(_m, code) {{ return 'S:' + describeCode(code, autoEvalLabels); }})
        .replace(/R:([A-Za-z_]+)/g, function(_m, code) {{ return 'R:' + describeCode(code, autoEvalLabels); }});
    }}

    function metricHint(metricKey, value) {{
      var score = Number(value);
      if (!isFinite(score)) return '未記録';
      if (metricKey === 'direction_strength') {{
        if (score >= 70) return '強い';
        if (score >= 40) return '中くらい';
        return '弱い';
      }}
      if (metricKey === 'execution_readiness') {{
        if (score >= 70) return '入りやすい';
        if (score >= 40) return '条件つき';
        return 'まだ入りにくい';
      }}
      if (score >= 70) return '強く待ちたい';
      if (score >= 40) return '少し待ちたい';
      return '待機圧力は低い';
    }}

    function extractTime(value) {{
      var raw = String(value || '').trim();
      if (raw.length >= 16 && raw.indexOf('T') !== -1) return raw.slice(5, 10).replace('-', '/') + ' ' + raw.slice(11, 16);
      return raw || '--:--';
    }}

    function isReadyForCompletion(row) {{
      return Boolean(String(row.user_verdict || '').trim() && String(row.would_trade || '').trim() && String(row.usefulness_1to5 || '').trim());
    }}

    function updateReviewStatus(row) {{
      if (String(row.review_status || 'pending') === 'done' && !isReadyForCompletion(row)) {{
        row.review_status = 'pending';
      }}
    }}

    function createActionButton(label, active, className, onClick) {{
      var button = document.createElement('button');
      button.type = 'button';
      button.className = className + (active ? ' active' : '');
      button.textContent = label;
      button.addEventListener('click', onClick);
      return button;
    }}

    function applyVerdictDefaults(row) {{
      var defaults = verdictDefaults[String(row.user_verdict || '')];
      if (!defaults) return;
      if (!row.would_trade || row.would_trade === row._auto_would_trade) {{
        row.would_trade = String(defaults.would_trade || '');
      }}
      if (!row.usefulness_1to5 || row.usefulness_1to5 === row._auto_usefulness_1to5) {{
        row.usefulness_1to5 = String(defaults.usefulness_1to5 || '');
      }}
      row._auto_would_trade = String(defaults.would_trade || '');
      row._auto_usefulness_1to5 = String(defaults.usefulness_1to5 || '');
      updateReviewStatus(row);
    }}

    function buildButtonRow(optionList, currentValue, className, onPick) {{
      var wrap = document.createElement('div');
      wrap.className = className === 'memo-chip' ? 'memo-chip-row' : 'choice-row';
      optionList.forEach(function(item) {{
        if (!item.value) return;
        wrap.appendChild(createActionButton(item.label, item.value === currentValue, className, function() {{
          onPick(item.value);
          saveDraft();
          renderCards();
        }}));
      }});
      return wrap;
    }}

    function buildMetricCard(metricKey, label, value) {{
      var card = document.createElement('div');
      card.className = 'metric-card';
      var top = document.createElement('div');
      top.className = 'metric-top';
      var labelEl = document.createElement('span');
      labelEl.className = 'context-label';
      labelEl.textContent = label;
      var hintEl = document.createElement('span');
      hintEl.className = 'metric-hint';
      hintEl.textContent = metricHint(metricKey, value);
      top.appendChild(labelEl);
      top.appendChild(hintEl);
      var valueEl = document.createElement('div');
      valueEl.className = 'metric-value';
      valueEl.textContent = formatContext(value);
      card.appendChild(top);
      card.appendChild(valueEl);
      return card;
    }}

    function createChip(text, className) {{
      var chip = document.createElement('span');
      chip.className = className || 'chip';
      chip.textContent = text;
      return chip;
    }}

    function updateProgress() {{
      var doneCount = rows.filter(function(row) {{ return String(row.review_status || 'pending') === 'done'; }}).length;
      var chip = document.getElementById('progress-chip');
      if (chip) chip.textContent = 'レビュー進捗: ' + String(doneCount) + ' / ' + String(rows.length) + ' 完了';
    }}

    function updateServerStatus(message) {{
      var el = document.getElementById('server-status');
      if (el) el.textContent = message;
    }}

    function togglePendingOnly() {{
      showPendingOnly = !showPendingOnly;
      renderCards();
    }}

    function focusNextPending() {{
      var pendingIndex = rows.findIndex(function(row) {{ return String(row.review_status || 'pending') !== 'done'; }});
      var target = pendingIndex >= 0 ? document.getElementById('review-card-' + String(pendingIndex)) : null;
      if (target && target.scrollIntoView) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    function renderCards() {{
      var root = document.getElementById('cards');
      root.innerHTML = '';
      rows.forEach(function(row, index) {{
        updateReviewStatus(row);
        if (showPendingOnly && String(row.review_status || 'pending') === 'done') return;

        var card = document.createElement('div');
        card.className = 'card';
        card.id = 'review-card-' + String(index);

        var cardTop = document.createElement('div');
        cardTop.className = 'card-top';
        var title = document.createElement('h3');
        title.textContent = '通知 ' + String(index + 1);
        cardTop.appendChild(title);
        var timeBadge = document.createElement('div');
        timeBadge.className = 'time-badge';
        timeBadge.textContent = extractTime(row.timestamp_jst);
        cardTop.appendChild(timeBadge);
        card.appendChild(cardTop);

        var meta = document.createElement('div');
        meta.className = 'meta';
        meta.textContent = row.timestamp_jst + ' / ' + row.signal_id;
        card.appendChild(meta);

        var subject = document.createElement('div');
        subject.className = 'subject';
        subject.textContent = row.subject;
        card.appendChild(subject);

        var summaryRow = document.createElement('div');
        summaryRow.className = 'summary-row';
        summaryRow.appendChild(createChip('方向感: ' + describeBias(row.bias)));
        summaryRow.appendChild(createChip('位置評価: ' + describePrelabel(row.prelabel)));
        summaryRow.appendChild(createChip('24時間後評価: ' + describeEvaluation(row.evaluation_status || 'pending')));
        summaryRow.appendChild(createChip(String(row.review_status || 'pending') === 'done' ? '完了' : '未完了', 'status-chip' + (String(row.review_status || 'pending') === 'done' ? ' done' : '')));
        card.appendChild(summaryRow);

        var primaryQuestion = document.createElement('div');
        primaryQuestion.className = 'primary-question';
        var primaryTitle = document.createElement('div');
        primaryTitle.className = 'section-title';
        primaryTitle.textContent = 'この通知、役に立った？';
        primaryQuestion.appendChild(primaryTitle);
        primaryQuestion.appendChild(buildButtonRow(options.verdict, row.user_verdict || '', 'choice-pill', function(value) {{
          row.user_verdict = value;
          applyVerdictDefaults(row);
        }}));
        card.appendChild(primaryQuestion);

        var detailPanel = document.createElement('div');
        detailPanel.className = 'detail-panel';

        var actionTitle = document.createElement('div');
        actionTitle.className = 'section-title';
        actionTitle.textContent = '判断を残す';
        detailPanel.appendChild(actionTitle);

        var wouldTradeField = document.createElement('div');
        wouldTradeField.className = 'compact-field';
        wouldTradeField.innerHTML = '<div class="field-title">自分ならどうする？</div>';
        wouldTradeField.appendChild(buildButtonRow(options.wouldTrade, row.would_trade || '', 'choice-pill', function(value) {{
          row.would_trade = value;
          updateReviewStatus(row);
        }}));
        detailPanel.appendChild(wouldTradeField);

        var usefulnessField = document.createElement('div');
        usefulnessField.className = 'compact-field';
        usefulnessField.innerHTML = '<div class="field-title">役立ち度 1-5</div>';
        usefulnessField.appendChild(buildButtonRow(options.usefulness, row.usefulness_1to5 || '', 'score-pill', function(value) {{
          row.usefulness_1to5 = value;
          updateReviewStatus(row);
        }}));
        detailPanel.appendChild(usefulnessField);

        var completeButton = document.createElement('button');
        completeButton.type = 'button';
        completeButton.className = 'complete-button' + (isReadyForCompletion(row) ? ' ready' : '');
        completeButton.textContent = String(row.review_status || 'pending') === 'done' ? '未完了に戻す' : '完了にする';
        completeButton.addEventListener('click', function() {{
          if (String(row.review_status || 'pending') === 'done') {{
            row.review_status = 'pending';
          }} else if (isReadyForCompletion(row)) {{
            row.review_status = 'done';
          }}
          saveDraft();
          renderCards();
        }});
        detailPanel.appendChild(completeButton);

        var details = document.createElement('details');
        details.className = 'detail-box';
        if (String(row.user_verdict || '').trim() || String(row.would_trade || '').trim() || String(row.usefulness_1to5 || '').trim() || String(row.memo || '').trim()) {{
          details.open = true;
        }}
        var summary = document.createElement('summary');
        summary.textContent = '詳細を見る';
        details.appendChild(summary);

        var metricGrid = document.createElement('div');
        metricGrid.className = 'metric-grid';
        metricGrid.appendChild(buildMetricCard('direction_strength', '方向の強さ', row.confidence_direction_shadow));
        metricGrid.appendChild(buildMetricCard('execution_readiness', '実行しやすさ', row.confidence_execution_shadow));
        metricGrid.appendChild(buildMetricCard('wait_pressure', '待機圧力', row.confidence_wait_shadow));
        details.appendChild(metricGrid);

        var reasonText = document.createElement('div');
        reasonText.className = 'detail-text';
        reasonText.innerHTML = '<strong>通知理由:</strong> ' + describeNotifyReason(row.notify_reason);
        details.appendChild(reasonText);

        var autoEval = document.createElement('div');
        autoEval.className = 'detail-text';
        autoEval.innerHTML = '<strong>自動評価:</strong> ' + describeAutoEvalSummary(row.auto_eval_summary);
        details.appendChild(autoEval);

        var moveDriverField = document.createElement('div');
        moveDriverField.className = 'compact-field';
        moveDriverField.innerHTML = '<div class="field-title">値動きの主因</div>';
        moveDriverField.appendChild(buildButtonRow(options.moveDriver, row.actual_move_driver || '', 'choice-pill', function(value) {{
          row.actual_move_driver = value;
        }}));
        details.appendChild(moveDriverField);

        var memoField = document.createElement('div');
        memoField.className = 'compact-field';
        memoField.innerHTML = '<div class="field-title">一言メモ</div>';
        memoField.appendChild(buildButtonRow(options.memoPreset, row.memo || '', 'memo-chip', function(value) {{
          row.memo = value;
        }}));
        var memoInput = document.createElement('textarea');
        memoInput.value = row.memo || '';
        memoInput.placeholder = '必要なら短くメモを残します';
        memoInput.addEventListener('input', function(event) {{
          row.memo = event.target.value;
          saveDraft();
        }});
        memoField.appendChild(memoInput);
        details.appendChild(memoField);

        detailPanel.appendChild(details);
        card.appendChild(detailPanel);
        root.appendChild(card);
      }});
      updateProgress();
    }}

    function syncRowsFromDom() {{
      rows.forEach(function(row) {{
        updateReviewStatus(row);
      }});
    }}

    function bindSelectHandlers() {{
      return;
    }}

    function updatePreview() {{
      return;
    }}

    function updateDraftStatus(message) {{
      var el = document.getElementById('draft-status');
      if (el) el.textContent = message;
    }}

    function getDraftStorage() {{
      try {{
        if (!window.localStorage) return null;
        var probeKey = draftStorageKey + ':probe';
        window.localStorage.setItem(probeKey, 'ok');
        window.localStorage.removeItem(probeKey);
        return window.localStorage;
      }} catch (_error) {{
        return null;
      }}
    }}

    function editableDraftFields(row) {{
      return {{
        signal_id: String(row.signal_id || ''),
        user_verdict: String(row.user_verdict || ''),
        usefulness_1to5: String(row.usefulness_1to5 || ''),
        would_trade: String(row.would_trade || ''),
        actual_move_driver: String(row.actual_move_driver || ''),
        memo: String(row.memo || ''),
        review_status: String(row.review_status || 'pending'),
      }};
    }}

    function saveDraft() {{
      var storage = getDraftStorage();
      if (!storage) {{
        updateDraftStatus('下書き保存はこのブラウザでは使えません');
        return;
      }}
      var payload = {{
        version: 1,
        saved_at: new Date().toISOString(),
        rows: rows.map(function(row) {{ return editableDraftFields(row); }}),
      }};
      storage.setItem(draftStorageKey, JSON.stringify(payload));
      updateDraftStatus('下書き保存済み');
    }}

    function restoreDraft() {{
      var storage = getDraftStorage();
      if (!storage) {{
        updateDraftStatus('下書き保存はこのブラウザでは使えません');
        return;
      }}
      var raw = storage.getItem(draftStorageKey);
      if (!raw) {{
        updateDraftStatus('下書きなし');
        return;
      }}
      try {{
        var parsed = JSON.parse(raw);
        var savedRows = Array.isArray(parsed.rows) ? parsed.rows : [];
        var restored = 0;
        rows.forEach(function(row) {{
          var saved = null;
          savedRows.forEach(function(item) {{
            if (!saved && String(item.signal_id || '') === String(row.signal_id || '')) saved = item;
          }});
          if (!saved) return;
          row.user_verdict = String(saved.user_verdict || '');
          row.usefulness_1to5 = String(saved.usefulness_1to5 || '');
          row.would_trade = String(saved.would_trade || '');
          row.actual_move_driver = String(saved.actual_move_driver || '');
          row.memo = String(saved.memo || '');
          row.review_status = String(saved.review_status || 'pending');
          restored += 1;
        }});
        updateDraftStatus(restored ? ('下書きを復元しました: ' + restored + '件') : '下書きはありましたが一致行なし');
      }} catch (_error) {{
        updateDraftStatus('下書き復元に失敗');
      }}
    }}

    function clearDraft() {{
      var storage = getDraftStorage();
      if (!storage) {{
        updateDraftStatus('下書き保存はこのブラウザでは使えません');
        return;
      }}
      storage.removeItem(draftStorageKey);
      updateDraftStatus('下書きを削除');
    }}

    function savePayload() {{
      syncRowsFromDom();
      return {{ rows: rows }};
    }}

    async function saveToServer() {{
      saveDraft();
      updateDraftStatus('保存中...');
      try {{
        var response = await fetch(apiBase + '/api/review-form/save', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(savePayload()),
        }});
        if (!response.ok) throw new Error('save failed');
        var payload = await response.json();
        rows = Array.isArray(payload.rows) ? payload.rows : rows;
        updateDraftStatus('保存済み');
        updateServerStatus('保存成功: JSON / CSV / Obsidian 要約を更新しました');
        renderCards();
      }} catch (_error) {{
        updateDraftStatus('ローカル下書きのみ保存');
        updateServerStatus('ローカル補助へ保存できませんでした。localhost 起動を確認してください');
      }}
    }}

    async function reloadFromServer() {{
      updateServerStatus('ローカル補助へ接続中...');
      try {{
        var response = await fetch(apiBase + '/api/review-form/state');
        if (!response.ok) throw new Error('load failed');
        var payload = await response.json();
        rows = Array.isArray(payload.rows) ? payload.rows : rows;
        updateServerStatus('ローカル補助と接続済み。最新状態を読み込みました');
        renderCards();
      }} catch (_error) {{
        updateServerStatus('ローカル補助へ接続できません。下書き復元で継続できます');
      }}
    }}

    function resetSelections() {{
      rows.forEach(function(row) {{
        row.user_verdict = '';
        row.usefulness_1to5 = '';
        row.would_trade = '';
        row.actual_move_driver = '';
        row.memo = '';
        row.review_status = 'pending';
        row._auto_would_trade = '';
        row._auto_usefulness_1to5 = '';
      }});
      clearDraft();
      renderCards();
    }}

    renderCards();
    restoreDraft();
    renderCards();
    bindSelectHandlers();
    reloadFromServer();
  </script>
</body>
</html>
"""


def write_review_form_html(rows: list[dict[str, str]], review_note_path: Path) -> Path:
    form_path = _review_form_path(review_note_path)
    _ensure_parent(form_path)
    target_rows = [row for row in rows if _is_review_target(str(row.get("timestamp_jst", "")))]
    form_path.write_text(_render_review_form_html(target_rows, review_note_path), encoding="utf-8")
    return form_path


def _review_rows_to_csv_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    reviewed_at = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
    imported_rows: list[dict[str, str]] = []
    for row in rows:
        signal_id = str(row.get("signal_id", "")).strip()
        if not signal_id or str(row.get("review_status", "")).strip() != "done":
            continue
        if not _is_review_target(str(row.get("timestamp_jst", ""))):
            continue
        imported_rows.append(
            {
                "signal_id": signal_id,
                "timestamp_jst": str(row.get("timestamp_jst", "")),
                "subject": str(row.get("subject", "")),
                "auto_eval_summary": str(row.get("auto_eval_summary", "")),
                "user_verdict": str(row.get("user_verdict", "")),
                "usefulness_1to5": str(row.get("usefulness_1to5", "")),
                "would_trade": str(row.get("would_trade", "")),
                "actual_move_driver": str(row.get("actual_move_driver", "")),
                "misleading_entry_like_wording": str(row.get("misleading_entry_like_wording", "")),
                "logic_validated": str(row.get("logic_validated", "")),
                "memo": str(row.get("memo", "")),
                "review_status": "done",
                "reviewed_at_utc": str(row.get("reviewed_at_utc", "")).strip() or reviewed_at,
            }
        )
    return imported_rows


def _merge_review_sources(
    *,
    state_rows: list[dict[str, str]],
    note_rows: list[dict[str, str]],
    review_rows: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for source_rows in (review_rows, note_rows, state_rows):
        for row in source_rows:
            signal_id = str(row.get("signal_id", "")).strip()
            if not signal_id:
                continue
            current = merged.get(signal_id, {})
            combined = current.copy()
            combined.update({str(key): str(value or "") for key, value in row.items()})
            merged[signal_id] = combined
    return merged


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
    state_path = _review_state_path(base_dir)

    outcomes = {row.get("signal_id", ""): row for row in _load_csv_rows(outcomes_path) if row.get("signal_id", "")}
    trades = {row.get("signal_id", ""): row for row in _load_csv_rows(trades_path) if row.get("signal_id", "")}
    review_rows = [row for row in _load_csv_rows(reviews_path) if row.get("signal_id", "")]
    note_rows = _load_review_note_rows(review_note_path)
    state_rows = _load_review_state_rows(state_path)

    merged_rows = _merge_review_sources(state_rows=state_rows, note_rows=note_rows, review_rows=review_rows)

    for signal_id, trade in trades.items():
        if not _parse_bool(trade.get("was_notified")):
            continue
        current = merged_rows.get(signal_id, {})
        outcome = outcomes.get(signal_id, {})
        auto_eval_summary = current.get("auto_eval_summary", "")
        if not auto_eval_summary:
            if outcome.get("evaluation_status") == "complete":
                auto_eval_summary = _auto_eval_summary(outcome)
            else:
                auto_eval_summary = _pending_auto_eval_summary(trade)
        merged_rows[signal_id] = {
            "signal_id": signal_id,
            "timestamp_jst": current.get("timestamp_jst", trade.get("timestamp_jst", outcome.get("timestamp_jst", ""))),
            "subject": current.get("subject", trade.get("summary_subject", "")),
            "auto_eval_summary": auto_eval_summary,
            "user_verdict": current.get("user_verdict", ""),
            "usefulness_1to5": current.get("usefulness_1to5", ""),
            "would_trade": current.get("would_trade", ""),
            "actual_move_driver": current.get("actual_move_driver", ""),
            "misleading_entry_like_wording": current.get("misleading_entry_like_wording", ""),
            "logic_validated": current.get("logic_validated", ""),
            "memo": current.get("memo", ""),
            "review_status": current.get("review_status", "pending") or "pending",
            "bias": trade.get("bias", ""),
            "prelabel": trade.get("prelabel", ""),
            "primary_setup_status": trade.get("primary_setup_status", ""),
            "signal_tier": trade.get("signal_tier", ""),
            "notify_reason": trade.get("notify_reason_codes", trade.get("reason_for_notification", "")),
            "data_quality_flag": trade.get("data_quality_flag", ""),
            "evaluation_status": outcome.get("evaluation_status", ""),
            "confidence_direction_shadow": trade.get("confidence_direction_shadow", ""),
            "confidence_execution_shadow": trade.get("confidence_execution_shadow", ""),
            "confidence_wait_shadow": trade.get("confidence_wait_shadow", ""),
            "summary_variant": trade.get("summary_variant", ""),
            "advice_variant": trade.get("advice_variant", ""),
            "evaluation_trace_version": trade.get("evaluation_trace_version", ""),
            "reviewed_at_utc": current.get("reviewed_at_utc", ""),
        }

    ordered_rows = sorted(
        [row for row in merged_rows.values() if _is_review_target(str(row.get("timestamp_jst", "")))],
        key=lambda row: row.get("timestamp_jst", ""),
        reverse=True,
    )
    _write_review_state(state_path, ordered_rows)
    _upsert_csv_rows(reviews_path, USER_REVIEW_HEADER, _review_rows_to_csv_rows(ordered_rows), "signal_id")
    _ensure_parent(review_note_path)
    review_note_path.write_text(_render_review_note(ordered_rows), encoding="utf-8")
    write_review_form_html(ordered_rows, review_note_path)
    return review_note_path


def import_reviews(
    *,
    base_dir: Path,
    review_note_path: Path = DEFAULT_REVIEW_NOTE,
    reviews_path: Path | None = None,
) -> Path:
    reviews_path = reviews_path or base_dir / "logs" / "csv" / "user_reviews.csv"
    state_rows = _load_review_state_rows(_review_state_path(base_dir))
    source_rows = state_rows or _load_review_note_rows(review_note_path)
    imported_rows = []

    for row in _review_rows_to_csv_rows(source_rows):
        signal_id = str(row.get("signal_id", "")).strip()
        user_verdict = str(row.get("user_verdict", "")).strip()
        would_trade = str(row.get("would_trade", "")).strip()
        usefulness = str(row.get("usefulness_1to5", "")).strip()
        actual_move_driver = str(row.get("actual_move_driver", "")).strip()
        misleading_entry_like_wording = str(row.get("misleading_entry_like_wording", "")).strip()
        if user_verdict not in VALID_USER_VERDICTS:
            raise ValueError(f"invalid user_verdict: {signal_id} -> {user_verdict}")
        if would_trade not in VALID_WOULD_TRADE:
            raise ValueError(f"invalid would_trade: {signal_id} -> {would_trade}")
        if actual_move_driver not in VALID_MOVE_DRIVERS:
            raise ValueError(f"invalid actual_move_driver: {signal_id} -> {actual_move_driver}")
        if misleading_entry_like_wording not in VALID_MISLEADING_ENTRY:
            raise ValueError(f"invalid misleading_entry_like_wording: {signal_id} -> {misleading_entry_like_wording}")
        if usefulness:
            usefulness_int = int(usefulness)
            if usefulness_int < 1 or usefulness_int > 5:
                raise ValueError(f"invalid usefulness_1to5: {signal_id} -> {usefulness}")
        imported_rows.append(row)

    return _upsert_csv_rows(reviews_path, USER_REVIEW_HEADER, imported_rows, "signal_id")


def _save_review_rows(
    *,
    base_dir: Path,
    incoming_rows: list[dict[str, Any]],
    review_note_path: Path = DEFAULT_REVIEW_NOTE,
    reviews_path: Path | None = None,
    outcomes_path: Path | None = None,
    trades_path: Path | None = None,
) -> list[dict[str, str]]:
    reviews_path = reviews_path or base_dir / "logs" / "csv" / "user_reviews.csv"
    export_review_queue(
        base_dir=base_dir,
        review_note_path=review_note_path,
        outcomes_path=outcomes_path,
        reviews_path=reviews_path,
        trades_path=trades_path,
    )
    state_path = _review_state_path(base_dir)
    current_rows = _load_review_state_rows(state_path)
    current_map = {str(row.get("signal_id", "")): row for row in current_rows if str(row.get("signal_id", "")).strip()}
    for raw_row in incoming_rows:
        signal_id = str(raw_row.get("signal_id", "")).strip()
        if not signal_id:
            continue
        current = current_map.get(signal_id, {"signal_id": signal_id})
        for key in (
            "timestamp_jst",
            "subject",
            "auto_eval_summary",
            "user_verdict",
            "usefulness_1to5",
            "would_trade",
            "actual_move_driver",
            "memo",
            "review_status",
        ):
            if key in raw_row:
                current[key] = str(raw_row.get(key, "") or "")
        current["reviewed_at_utc"] = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
        current_map[signal_id] = current

    ordered_rows = sorted(
        [row for row in current_map.values() if _is_review_target(str(row.get("timestamp_jst", "")))],
        key=lambda row: row.get("timestamp_jst", ""),
        reverse=True,
    )
    _write_review_state(state_path, ordered_rows)
    _upsert_csv_rows(reviews_path, USER_REVIEW_HEADER, _review_rows_to_csv_rows(ordered_rows), "signal_id")
    review_note_path.write_text(_render_review_note(ordered_rows), encoding="utf-8")
    write_review_form_html(ordered_rows, review_note_path)
    return ordered_rows


def serve_review_form(
    *,
    base_dir: Path,
    review_note_path: Path = DEFAULT_REVIEW_NOTE,
    host: str = REVIEW_SERVER_HOST,
    port: int = REVIEW_SERVER_PORT,
) -> None:
    export_review_queue(base_dir=base_dir, review_note_path=review_note_path)
    form_path = _review_form_path(review_note_path)

    class ReviewFormHandler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                export_review_queue(base_dir=base_dir, review_note_path=review_note_path)
                self._send(200, form_path.read_bytes(), "text/html; charset=utf-8")
                return
            if parsed.path == "/api/review-form/state":
                export_review_queue(base_dir=base_dir, review_note_path=review_note_path)
                payload = {
                    "rows": _load_review_state_rows(_review_state_path(base_dir)),
                    "review_note_path": str(review_note_path),
                    "review_form_path": str(form_path),
                }
                self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
                return
            self._send(404, b"not found", "text/plain; charset=utf-8")

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/api/review-form/save":
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except json.JSONDecodeError:
                self._send(400, b"invalid json", "text/plain; charset=utf-8")
                return
            rows = payload.get("rows", [])
            if not isinstance(rows, list):
                self._send(400, b"rows must be list", "text/plain; charset=utf-8")
                return
            saved_rows = _save_review_rows(base_dir=base_dir, incoming_rows=rows, review_note_path=review_note_path)
            self._send(
                200,
                json.dumps({"rows": saved_rows}, ensure_ascii=False).encode("utf-8"),
                "application/json; charset=utf-8",
            )

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer((host, port), ReviewFormHandler)
    print(f"http://{host}:{port}/")
    server.serve_forever()


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
                "raw_confidence": trade.get("raw_confidence", ""),
                "confidence_direction_shadow": trade.get("confidence_direction_shadow", ""),
                "confidence_execution_shadow": trade.get("confidence_execution_shadow", ""),
                "confidence_wait_shadow": trade.get("confidence_wait_shadow", ""),
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
                "summary_variant": trade.get("summary_variant", ""),
                "advice_variant": trade.get("advice_variant", ""),
                "evaluation_trace_version": trade.get("evaluation_trace_version", ""),
                "actual_move_driver": actual_move_driver,
                "misleading_entry_like_wording": review.get("misleading_entry_like_wording", ""),
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


def _format_period_range(rows: list[dict[str, Any]]) -> str:
    dt_values = sorted(row.get("timestamp_jst", "") for row in rows if row.get("timestamp_jst", ""))
    if not dt_values:
        return "集計期間なし"
    return f"{dt_values[0][:16].replace('T', ' ')} 〜 {dt_values[-1][:16].replace('T', ' ')}"


def _verdict_summary_lines(review_summary: dict[str, Any]) -> list[str]:
    verdicts: Counter[str] = review_summary["verdicts"]
    if not verdicts:
        return ["- 完了レビューはまだありません"]
    return [
        f"- {USER_VERDICT_LABELS.get(verdict, verdict)}: {count}件"
        for verdict, count in verdicts.most_common()
    ]


def _headline_findings(
    completed: list[dict[str, Any]],
    review_summary: dict[str, Any],
    improvements: list[dict[str, Any]],
) -> list[str]:
    if not completed:
        return ["- まだ集計対象の完了データがありません"]

    findings = [
        f"- 今回の完了データは {len(completed)} 件です。近似PF は {_profit_factor_proxy(completed):.2f}、全体勝率は {_format_pct(_ratio(sum(1 for row in completed if _success_flag(row) is True), sum(1 for row in completed if _success_flag(row) is not None)))} でした。"
    ]
    verdicts: Counter[str] = review_summary["verdicts"]
    if verdicts:
        top_verdict, top_count = verdicts.most_common(1)[0]
        findings.append(f"- 人のレビューでは「{USER_VERDICT_LABELS.get(top_verdict, top_verdict)}」が最も多く、{top_count} 件でした。")
        if review_summary["avg_usefulness"] > 0:
            findings.append(f"- 平均の役立ち度は {review_summary['avg_usefulness']:.2f} / 5 でした。")
    else:
        findings.append("- 人のレビューはまだ十分に集まっていません。")
    if improvements:
        findings.append(f"- 今回の改善候補の最上位は「{improvements[0]['title']}」です。")
    else:
        findings.append("- 目立った改善候補はまだ確定していません。")
    return findings


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


_COUNTERTREND_LONG_CLUSTER_FLAGS = {
    "lower_liquidity_close",
    "orderbook_ask_heavy",
    "long_flush_exhaustion",
    "cvd_bullish_divergence",
    "sweep_incomplete",
}


def _direction_execution_conflict(row: dict[str, Any]) -> bool:
    return (
        _parse_float(row.get("confidence_direction_shadow"), 0.0) >= 60.0
        and _parse_float(row.get("confidence_execution_shadow"), 999.0) <= 20.0
        and _parse_float(row.get("confidence_wait_shadow"), 0.0) >= 60.0
    )


def _entry_ok_invalid_conflict(row: dict[str, Any]) -> bool:
    return row.get("prelabel") == "ENTRY_OK" and row.get("primary_setup_status") == "invalid"


def _countertrend_long_cluster(row: dict[str, Any]) -> bool:
    if row.get("bias") != "long":
        return False
    flags = set(_split_values(str(row.get("risk_flags", ""))))
    return len(flags & _COUNTERTREND_LONG_CLUSTER_FLAGS) >= 2


def _recent_rows(rows: list[dict[str, Any]], *, hours: int = 12) -> list[dict[str, Any]]:
    start = datetime.now(tz=JST) - timedelta(hours=hours)
    recent: list[dict[str, Any]] = []
    for row in rows:
        dt = _parse_dt(row.get("timestamp_jst", ""))
        if dt is None:
            continue
        if dt >= start:
            recent.append(row)
    return recent


def _bias_direction_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for bias in ("long", "short", "wait"):
        subset = [row for row in rows if row.get("bias") == bias]
        if not subset:
            continue
        counts = Counter(row.get("direction_outcome", "") for row in subset if row.get("direction_outcome", ""))
        total = len(subset)
        summary.append(
            {
                "bias": bias,
                "count": total,
                "correct": counts.get("correct", 0),
                "wrong": counts.get("wrong", 0),
                "unclear": counts.get("unclear", 0),
                "wrong_rate": _ratio(counts.get("wrong", 0), total),
            }
        )
    return summary


def _risk_flag_wrong_rate_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    wrongs: Counter[str] = Counter()
    for row in rows:
        flags = _split_values(row.get("risk_flags", ""))
        is_wrong = row.get("direction_outcome") == "wrong"
        for flag in flags:
            counts[flag] += 1
            if is_wrong:
                wrongs[flag] += 1
    summary: list[dict[str, Any]] = []
    for flag, count in counts.items():
        if count < 5:
            continue
        summary.append(
            {
                "flag": flag,
                "count": count,
                "wrong_count": wrongs[flag],
                "wrong_rate": _ratio(wrongs[flag], count),
            }
        )
    summary.sort(key=lambda item: (item["wrong_rate"], item["count"]), reverse=True)
    return summary


def _recent_live_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    direction_conflicts = [row for row in rows if _direction_execution_conflict(row)]
    entry_invalid_rows = [row for row in rows if _entry_ok_invalid_conflict(row)]
    countertrend_rows = [row for row in rows if _countertrend_long_cluster(row)]
    return {
        "count": len(rows),
        "direction_execution_conflict_count": len(direction_conflicts),
        "entry_ok_invalid_count": len(entry_invalid_rows),
        "countertrend_long_cluster_count": len(countertrend_rows),
    }


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


def _build_improvement_candidates(
    rows: list[dict[str, Any]],
    *,
    monthly: bool,
    period_rows: list[dict[str, Any]] | None = None,
    recent_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    period_rows = period_rows or []
    recent_rows = recent_rows or []

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

    long_rows = [row for row in rows if row.get("bias") == "long"]
    short_rows = [row for row in rows if row.get("bias") == "short"]
    if len(long_rows) >= 20 and short_rows:
        long_wrong_count = sum(1 for row in long_rows if row.get("direction_outcome") == "wrong")
        short_wrong_count = sum(1 for row in short_rows if row.get("direction_outcome") == "wrong")
        long_wrong_rate = _ratio(long_wrong_count, len(long_rows))
        short_wrong_rate = _ratio(short_wrong_count, len(short_rows))
        if long_wrong_rate >= 0.55 and (long_wrong_rate - short_wrong_rate) >= 0.15:
            candidates.append(
                {
                    "title": "ロング方向スコアが強すぎる",
                    "reason": (
                        f"bias=long の wrong が {long_wrong_count}/{len(long_rows)} 件 ({_format_pct(long_wrong_rate)}) "
                        f"で、short より {_format_pct(long_wrong_rate - short_wrong_rate)} 悪い"
                    ),
                    "evidence_count": long_wrong_count,
                    "category": "direction/confidence 補正",
                    "touchpoints": "main.py, src/analysis/confidence.py",
                }
            )

    cluster_rows = [row for row in rows if _countertrend_long_cluster(row)]
    if len(cluster_rows) >= 8:
        wrong_count = sum(1 for row in cluster_rows if row.get("direction_outcome") == "wrong")
        wrong_rate = _ratio(wrong_count, len(cluster_rows))
        if wrong_rate >= 0.6:
            candidates.append(
                {
                    "title": "反発示唆の過大評価",
                    "reason": f"countertrend_long_cluster の wrong が {wrong_count}/{len(cluster_rows)} 件 ({_format_pct(wrong_rate)})",
                    "evidence_count": wrong_count,
                    "category": "risk_flag と direction の整合",
                    "touchpoints": "src/analysis/confidence.py, src/analysis/position_risk.py",
                }
            )

    entry_invalid_rows = [row for row in period_rows if _entry_ok_invalid_conflict(row)]
    if len(entry_invalid_rows) >= 3:
        candidates.append(
            {
                "title": "ENTRY_OK と setup invalid の整合性崩れ",
                "reason": f"期間内で ENTRY_OK + invalid が {len(entry_invalid_rows)} 件あります",
                "evidence_count": len(entry_invalid_rows),
                "category": "評価整合性",
                "touchpoints": "main.py, src/analysis/confidence.py, src/analysis/position_risk.py",
            }
        )

    direction_conflicts = [row for row in recent_rows if _direction_execution_conflict(row)]
    if len(direction_conflicts) >= 2:
        candidates.append(
            {
                "title": "速報で方向/実行不整合が継続",
                "reason": f"直近12時間で direction_execution_conflict が {len(direction_conflicts)} 件あります",
                "evidence_count": len(direction_conflicts),
                "category": "速報監視",
                "touchpoints": "tools/log_feedback.py",
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
    return candidates


def build_feedback_report(
    *,
    base_dir: Path,
    period: str,
    output_md: Path | None = None,
    shadow_path: Path | None = None,
) -> str:
    shadow_path = shadow_path or base_dir / "logs" / "csv" / "shadow_log.csv"
    trades_path = base_dir / "logs" / "csv" / "trades.csv"
    outcomes_path = base_dir / "logs" / "csv" / "signal_outcomes.csv"
    reviews_path = base_dir / "logs" / "csv" / "user_reviews.csv"
    if _is_stale_file(shadow_path, [trades_path, outcomes_path, reviews_path]):
        build_shadow_log(
            base_dir=base_dir,
            shadow_path=shadow_path,
            trades_path=trades_path,
            outcomes_path=outcomes_path,
            reviews_path=reviews_path,
        )
    all_rows = _load_csv_rows(shadow_path)
    rows, previous_rows = _period_filter(all_rows, period)
    completed = [row for row in rows if row.get("evaluation_status") == "complete"]
    previous_completed = [row for row in previous_rows if row.get("evaluation_status") == "complete"]
    review_summary = _review_summary(completed)
    recent_rows = _recent_rows(all_rows, hours=12)
    live_summary = _recent_live_summary(recent_rows)
    improvements = _build_improvement_candidates(
        completed,
        monthly=(period == "monthly"),
        period_rows=rows,
        recent_rows=recent_rows,
    )

    lines = [f"# フィードバック分析レポート ({period})", ""]
    lines.append("## 1. まず結論")
    lines.extend(_headline_findings(completed, review_summary, improvements))
    lines.append("")

    lines.append("## 2. 今回の対象")
    lines.append(f"- 集計期間: {_format_period_range(completed)}")
    lines.append(f"- 総観測件数: {len(completed)}")
    quality_counts = Counter(row.get("data_quality_flag", "") or "unknown" for row in completed)
    quality_text = ", ".join(f"{key}={value}" for key, value in sorted(quality_counts.items())) or "なし"
    lines.append(f"- データ品質の内訳: {quality_text}")
    lines.append(f"- 近似PF: {_profit_factor_proxy(completed):.2f}")
    lines.append("")

    lines.append("## 3. 人のレビュー要約")
    lines.extend(_verdict_summary_lines(review_summary))
    if review_summary["verdicts"]:
        lines.append(f"- 平均の役立ち度: {review_summary['avg_usefulness']:.2f} / 5")
        lines.append(f"- 値動きの主因の入力率: {_format_pct(review_summary['actual_move_driver_rate'])}")
    lines.append("")

    lines.append("## 4. 改善候補")
    if improvements:
        for idx, item in enumerate(improvements, start=1):
            lines.append(f"{idx}. {item['title']}")
            lines.append(f"   理由: {item['reason']}")
            lines.append(f"   主に触る場所: {item['touchpoints']}")
    else:
        lines.append("- まだ改善候補を絞れるだけのデータがありません")
    lines.append("")

    lines.append("## 5. 技術集計")
    lines.append("")

    lines.append("### regime別件数・勝率・平均MFE・平均MAE")
    regime_summary = _summary_by_field(completed, "regime")
    if regime_summary:
        for item in regime_summary:
            lines.append(
                f"- {item['label']}: 勝率={_format_pct(item['win_rate'])}, 平均MFE={item['avg_mfe']:.2f}, 平均MAE={item['avg_mae']:.2f} (n={item['count']}){_sample_note(item['count'])}"
            )
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("### signal_tier別件数・勝率・平均MFE・平均MAE")
    tier_summary = _signal_tier_summary(completed)
    if tier_summary:
        for item in tier_summary:
            lines.append(
                f"- {item['label']}: 勝率={_format_pct(item['win_rate'])}, 平均MFE={item['avg_mfe']:.2f}, 平均MAE={item['avg_mae']:.2f} (n={item['count']}){_sample_note(item['count'])}"
            )
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("### prelabel別件数・勝率・平均MFE・平均MAE")
    prelabel_summary = _prelabel_summary(completed)
    if prelabel_summary:
        for item in prelabel_summary:
            lines.append(
                f"- {item['label']}: 勝率={_format_pct(item['win_rate'])}, 平均MFE={item['avg_mfe']:.2f}, 平均MAE={item['avg_mae']:.2f} (n={item['count']}){_sample_note(item['count'])}"
            )
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("### bias別件数・勝率")
    bias_summary = _summary_by_field(completed, "bias", ["long", "short", "wait"])
    if bias_summary:
        for item in bias_summary:
            lines.append(f"- {item['label']}: 勝率={_format_pct(item['win_rate'])} (n={item['count']}){_sample_note(item['count'])}")
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("### bias別 direction 正誤")
    bias_direction_summary = _bias_direction_summary(completed)
    if bias_direction_summary:
        for item in bias_direction_summary:
            lines.append(
                f"- {item['bias']}: correct={item['correct']}, wrong={item['wrong']}, unclear={item['unclear']} / wrong_rate={_format_pct(item['wrong_rate'])} (n={item['count']})"
            )
    else:
        lines.append("- まだ十分なデータがありません")
    lines.append("")

    lines.append("### 成績指標")
    lines.append(f"- 全体勝率: {_format_pct(_ratio(sum(1 for row in completed if _success_flag(row) is True), sum(1 for row in completed if _success_flag(row) is not None)))}")
    lines.append(f"- 平均MFE(signal_based): {_mean_value(completed, 'signal_based_MFE_24h'):.2f}")
    lines.append(f"- 平均MAE(signal_based): {_mean_value(completed, 'signal_based_MAE_24h'):.2f}")
    lines.append(f"- 平均MFE(entry_ready_based): {_mean_value(completed, 'entry_ready_based_MFE_24h'):.2f}")
    lines.append(f"- 平均MAE(entry_ready_based): {_mean_value(completed, 'entry_ready_based_MAE_24h'):.2f}")
    tp1_pool = [row for row in completed if row.get("tp1_hit_first") in {"true", "false"}]
    lines.append(f"- TP1先行率: {_format_pct(_ratio(sum(1 for row in tp1_pool if row.get('tp1_hit_first') == 'true'), len(tp1_pool)))}")
    lines.append("")

    lines.append("### 通知品質")
    audit = _notification_audit(completed)
    lines.append(f"- A: 通知して良かった = {audit['A']}件")
    lines.append(f"- B: 通知したが微妙 = {audit['B']}件")
    lines.append(f"- C: 通知しなかったが本当は良かった = {audit['C']}件")
    lines.append(f"- D: 通知しなかったので正解 = {audit['D']}件")
    lines.append("")

    lines.append("### risk flag 群別 wrong rate")
    wrong_rate_summary = _risk_flag_wrong_rate_summary(completed)
    if wrong_rate_summary:
        for item in wrong_rate_summary:
            lines.append(
                f"- {item['flag']}: wrong_rate={_format_pct(item['wrong_rate'])} (wrong={item['wrong_count']}/{item['count']})"
            )
    else:
        lines.append("- 比較対象となる risk_flag はまだありません")
    lines.append("")

    lines.append("### 直近12時間速報")
    lines.append(f"- 対象件数: {live_summary['count']}件")
    lines.append(f"- direction_execution_conflict: {live_summary['direction_execution_conflict_count']}件")
    lines.append(f"- ENTRY_OK + invalid: {live_summary['entry_ok_invalid_count']}件")
    lines.append(f"- countertrend_long_cluster: {live_summary['countertrend_long_cluster_count']}件")
    lines.append("")

    lines.append("### Phase 1 計画ログ")
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
        lines.append("### risk_flags 有効性比較")
        risk_flags = _risk_flag_summary(completed)
        if risk_flags:
            for item in risk_flags:
                lines.append(f"- {item['flag']}: negative_rate={_format_pct(item['negative_rate'])} (n={item['count']})")
        else:
            lines.append("- 比較対象となる risk_flag はまだありません")
        lines.append("")
    else:
        lines.append("### 前月比")
        if previous_completed:
            lines.append(f"- 前月件数: {len(previous_completed)}")
            lines.append(f"- 今月との差: {len(completed) - len(previous_completed)} 件")
        else:
            lines.append("- 前月データはまだありません")
        lines.append("")
        lines.append("### 設定変更提案")
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
        "review_form_path": _review_form_path(review_note),
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

    serve_parser = subparsers.add_parser("serve-review-form")
    serve_parser.add_argument("--review-note", default=str(DEFAULT_REVIEW_NOTE))
    serve_parser.add_argument("--host", default=REVIEW_SERVER_HOST)
    serve_parser.add_argument("--port", type=int, default=REVIEW_SERVER_PORT)

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

    if args.command == "serve-review-form":
        serve_review_form(
            base_dir=base_dir,
            review_note_path=Path(args.review_note),
            host=str(args.host),
            port=int(args.port),
        )
        return

    if args.command == "daily-sync":
        output_md = Path(args.output_md) if args.output_md else None
        paths = daily_sync(base_dir=base_dir, review_note_path=Path(args.review_note), output_md=output_md)
        for key, path in paths.items():
            print(f"{key}={path}")
        return


if __name__ == "__main__":
    main()
