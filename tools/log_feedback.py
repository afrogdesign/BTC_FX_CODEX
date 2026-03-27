from __future__ import annotations

import argparse
import csv
import html
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
    "/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム/通知評価シート.md"
)
DEFAULT_REVIEW_FORM = DEFAULT_REVIEW_NOTE.with_name("評価シート入力フォーム.html")
JST = ZoneInfo("Asia/Tokyo")
REVIEW_START_CUTOFF_JST = "2026-03-25T00:00:00+09:00"

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
    {"value": "ready だが位置はまだ良くなく、次の確認足待ち。", "label": "ready だが次の確認足待ち"},
    {"value": "watch 通知として有効で、飛び乗り防止に役立った。", "label": "watch として有効だった"},
    {"value": "notify_reason の格上げは妥当だが、件名ほどの優位性は感じない。", "label": "通知理由は妥当だが件名が強い"},
    {"value": "signal_tier は normal のままで、注意喚起として見るのが妥当。", "label": "normal tier の注意喚起として妥当"},
    {"value": "signal_tier は強くないが、監視価値のある変化だった。", "label": "強くないが監視価値あり"},
    {"value": "data_quality に問題はなく、判断材料として使えた。", "label": "データ品質は問題なかった"},
    {"value": "位置は悪いが、注意喚起としては良かった。", "label": "位置は悪いが、注意喚起としては良かった"},
    {"value": "方向は合っていたが、通知が少し早い。", "label": "方向は合っていたが、通知が少し早い"},
    {"value": "方向は合っていたが、通知が少し遅い。", "label": "方向は合っていたが、通知が少し遅い"},
    {"value": "待機判断として有効で、無理なエントリー回避に役立った。", "label": "待機判断として有効だった"},
    {"value": "見送り判断として有効で、無駄なエントリー回避に役立った。", "label": "見送り判断として有効だった"},
    {"value": "本文は分かりやすく、実務判断に使いやすかった。", "label": "本文は分かりやすかった"},
    {"value": "本文が読みにくく、実務判断に使いにくかった。", "label": "本文が読みにくかった"},
    {"value": "下側の流動性回収後なら、より使いやすい通知だった。", "label": "流動性回収後なら使いやすかった"},
    {"value": "件名がやや強く見え、印象と実態に少しズレがあった。", "label": "件名がやや強すぎた"},
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

BIAS_LABELS = {
    "long": "long / ロング寄り",
    "short": "short / ショート寄り",
    "wait": "wait / 様子見",
}
PRELABEL_LABELS = {
    "ENTRY_OK": "ENTRY_OK / 入る条件がほぼそろった",
    "RISKY_ENTRY": "RISKY_ENTRY / 方向はあるが位置が悪い",
    "SWEEP_WAIT": "SWEEP_WAIT / 先に振り落とし確認を待ちたい",
    "NO_TRADE_CANDIDATE": "NO_TRADE_CANDIDATE / 見送り候補",
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
        "# 通知評価シート",
        "",
        "このノートは、通知済みシグナルを翌日まとめてレビューするための専用ノートです。",
        "",
        "## 入力ルール",
        "- まず `primary_setup_status` / `signal_tier` / `notify_reason` を見て、通知の種類を確認します。",
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


def _render_static_review_cards(rows: list[dict[str, str]], options_payload: dict[str, list[dict[str, str]]]) -> str:
    cards: list[str] = []
    field_defs = [
        ("user_verdict", "実務評価", "verdict", "入る価値・待つ価値・見送る価値、または早い/遅い/低価値を選ぶ", True),
        ("usefulness_1to5", "総合価値", "usefulness", "5 が最も実務価値あり。迷ったら 3 を基準にする"),
        ("would_trade", "自分ならどうするか", "wouldTrade", "今のルールと別に、自分の実行判断を残す", True),
        ("actual_move_driver", "値動きの主因", "moveDriver", ""),
        ("memo_preset", "メモ候補", "memoPreset", "最近の通知軸に合わせた短文をそのまま使える"),
        ("review_status", "レビュー状態", "reviewStatus", "入力し終えたら done にする", True),
    ]
    for index, row in enumerate(rows, start=1):
        time_badge = _format_time_badge(str(row.get("timestamp_jst", "")))
        chips = [
            f'<span class="chip">方向感: {html.escape(_describe_code(str(row.get("bias", "")), BIAS_LABELS))}</span>',
            f'<span class="chip">位置評価: {html.escape(_describe_code(str(row.get("prelabel", "")), PRELABEL_LABELS))}</span>',
            f'<span class="chip">24時間後評価: {html.escape(_describe_code(str(row.get("evaluation_status", "") or "pending"), EVALUATION_LABELS))}</span>',
        ]
        context_boxes = [
            ("セットアップ状態", _describe_code(str(row.get("primary_setup_status", "")), SETUP_LABELS)),
            ("通知の強さ", _describe_code(str(row.get("signal_tier", "")), TIER_LABELS)),
            ("通知理由", _describe_notify_reason(str(row.get("notify_reason", "")))),
            ("データ品質", _describe_code(str(row.get("data_quality_flag", "")), QUALITY_LABELS)),
        ]
        fields_html: list[str] = []
        for key, label, option_key, help_text, *extra in field_defs:
            is_recommended = bool(extra[0]) if extra else False
            field_class = "field recommended" if is_recommended else "field"
            label_html = html.escape(label) + (' <span class="recommended-badge">おすすめ</span>' if is_recommended else "")
            fields_html.append(
                f'<div class="{field_class}">'
                f"<label>{label_html}</label>"
                f"{_render_select_html(options_payload[option_key], str(row.get(key, "")), index - 1, key)}"
                + (
                    f'<div class="field-help">{html.escape(help_text)}</div>'
                    if help_text
                    else ""
                )
                + "</div>"
            )
        context_html = "".join(
            '<div class="context-box">'
            f'<span class="context-label">{html.escape(label)}</span>'
            f'<div class="context-value{" empty" if not str(value or "").strip() else ""}">{html.escape(str(value or "未記録"))}</div>'
            "</div>"
            for label, value in context_boxes
        )
        cards.append(
            '<div class="card">'
            f'<div class="card-top"><h3>通知 {index}</h3><div class="time-badge">{html.escape(time_badge)}</div></div>'
            f'<div class="meta">{html.escape(str(row.get("timestamp_jst", "")))} / {html.escape(str(row.get("signal_id", "")))}</div>'
            f'<div class="subject">{html.escape(str(row.get("subject", "")))}</div>'
            f'<div class="chips">{"".join(chips)}</div>'
            f'<p class="muted">自動評価: {html.escape(_describe_auto_eval_summary(str(row.get("auto_eval_summary", ""))))}</p>'
            f'<div class="context-grid">{context_html}</div>'
            f'<div class="grid">{"".join(fields_html)}</div>'
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
        "reviewStatus": FORM_REVIEW_STATUS_OPTIONS,
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
        ):
            row_copy[extra_key] = str(row.get(extra_key, ""))
        row_copy["memo_preset"] = row_copy["memo"] if row_copy["memo"] in {
            item["value"] for item in FORM_MEMO_PRESET_OPTIONS if item["value"]
        } else ""
        rows_payload.append(row_copy)

    note_name = review_note_path.name
    note_key = str(review_note_path)
    header_text = _render_review_note([])
    initial_cards_html = _render_static_review_cards(rows_payload, options_payload)
    initial_preview = _render_review_note(rows)
    intro = (
        "この画面は、最近の通知を今の評価軸でレビューするための入力フォームです。"
        " 入力後は下のプレビュー全文を "
        f"{note_name} に貼り付けて更新します。"
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
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}
    label {{
      display: block;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 6px;
    }}
    select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      background: #fff;
      color: #111827;
      font-size: 14px;
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
    .context-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
      margin: 12px 0 8px;
    }}
    .context-box {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      background: #f8fafc;
    }}
    .context-label {{
      display: block;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--muted);
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .context-value {{
      font-size: 14px;
      font-weight: 700;
      color: var(--text);
      word-break: break-word;
    }}
    .subject {{
      font-weight: 700;
      margin: 6px 0 2px;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 10px 0 4px;
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
    .empty {{
      color: var(--muted);
      font-weight: 500;
    }}
    .field-help {{
      margin-top: 4px;
      font-size: 12px;
      color: var(--muted);
    }}
    .field.recommended {{
      padding: 12px;
      border: 1px solid #fde68a;
      border-radius: 12px;
      background: #fffbeb;
    }}
    .recommended-badge {{
      display: inline-block;
      margin-left: 6px;
      padding: 2px 6px;
      border-radius: 999px;
      background: #f59e0b;
      color: #fff;
      font-size: 11px;
      vertical-align: middle;
    }}
    .preview {{
      width: 100%;
      min-height: 280px;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      white-space: pre-wrap;
      background: #fff;
      color: #111827;
      box-sizing: border-box;
    }}
    @media (max-width: 760px) {{
      body {{
        padding: 16px;
      }}
      .hero-grid {{
        grid-template-columns: 1fr;
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
          <p class="muted">使い方: まず通知の種類と理由を見る → 実務価値を選ぶ → 下のプレビュー全文を {html.escape(note_name)} に貼り付ける。</p>
          <p class="muted">このブラウザでは入力内容を自動で下書き保存します。ページを開き直しても、同じ端末・同じブラウザなら復元されます。</p>
        </div>
        <div class="hero-panel">
          <h2>今の確認軸</h2>
          <ul>
            <li><strong>通知の種類:</strong> `primary_setup_status` と `signal_tier` を先に見る</li>
            <li><strong>通知理由:</strong> `notify_reason` で何が変化した通知かを見る</li>
            <li><strong>実務価値:</strong> `user_verdict` と `would_trade` で使えたかを残す</li>
            <li><strong>事後整合:</strong> 24時間後評価と `actual_move_driver` のズレを `memo` に残す</li>
          </ul>
        </div>
      </div>
      <div class="toolbar">
        <button type="button" onclick="copyMarkdown()">Markdownをコピー</button>
        <button type="button" class="secondary" onclick="selectPreviewText()">全文を選択</button>
        <button type="button" class="secondary" onclick="resetSelections()">入力を初期化</button>
        <span id="draft-status" class="draft-status">下書き未保存</span>
      </div>
    </div>

    <div id="cards">{initial_cards_html}</div>

    <div class="card">
      <h2>生成される Markdown</h2>
      <p class="muted">この全文をそのまま {html.escape(note_name)} に貼り付けます。保存ボタンは使わず、この欄を正本として扱います。</p>
      <textarea id="preview" class="preview">{html.escape(initial_preview)}</textarea>
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
    var contextHeadings = {{
      setup: 'SETUP / セットアップ状態',
      signal_tier: 'SIGNAL_TIER / 通知の強さ',
      notify_reason: 'NOTIFY_REASON / 通知理由',
      data_quality: 'DATA_QUALITY / データ品質',
    }};
    var biasLabels = {{
      long: 'long / ロング寄り',
      short: 'short / ショート寄り',
      wait: 'wait / 様子見',
    }};
    var prelabelLabels = {{
      ENTRY_OK: 'ENTRY_OK / 入る条件がほぼそろった',
      RISKY_ENTRY: 'RISKY_ENTRY / 方向はあるが位置が悪い',
      SWEEP_WAIT: 'SWEEP_WAIT / 先に振り落とし確認を待ちたい',
      NO_TRADE_CANDIDATE: 'NO_TRADE_CANDIDATE / 見送り候補',
    }};
    var evaluationLabels = {{
      complete: 'complete / 24時間後評価まで完了',
      pending: 'pending / 24時間後評価待ち',
    }};
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
    var setupLabels = {{
      ready: 'ready / エントリー条件がそろった状態',
      watch: 'watch / 方向はあるが待ちたい状態',
      invalid: 'invalid / 今は見送りが妥当な状態',
      none: 'none / セットアップ未形成',
    }};
    var tierLabels = {{
      normal: 'normal / 通常通知',
      strong_machine: 'strong_machine / 機械的にかなり好条件',
      strong_ai_confirmed: 'strong_ai_confirmed / AI確認込みの強条件',
    }};
    var qualityLabels = {{
      ok: 'ok / データ欠損なし',
      partial_missing: 'partial_missing / 一部データ欠損あり',
      degraded: 'degraded / 品質低下あり',
      unknown: 'unknown / 品質未判定',
    }};
    var notifyReasonLabels = {{
      status_upgraded: 'status_upgraded / setup が昇格した',
      bias_changed: 'bias_changed / 方向感が wait から long または short に変わった',
      prelabel_improved: 'prelabel_improved / 位置評価が改善した',
      confidence_jump: 'confidence_jump / 信頼度が大きく変化した',
      agreement_changed: 'agreement_changed / AI と機械の一致状況が変わった',
      signal_tier_upgraded: 'signal_tier_upgraded / signal_tier が昇格した',
      attention_bias_changed: 'attention_bias_changed / 注意報の方向が切り替わった',
      attention_score_crossed: 'attention_score_crossed / 注意報スコア条件を超えた',
      attention_gap_crossed: 'attention_gap_crossed / ロングショート差が閾値を超えた',
      attention_first_detection: 'attention_first_detection / 初回の注意報検知',
    }};

    function createSelect(optionList, value, onChange) {{
      var select = document.createElement('select');
      optionList.forEach(function(item) {{
        var opt = document.createElement('option');
        opt.value = item.value;
        opt.textContent = item.label;
        if (item.value === value) opt.selected = true;
        select.appendChild(opt);
      }});
      select.addEventListener('change', onChange);
      return select;
    }}

    function formatContext(value, fallback = '未記録') {{
      return value && String(value).trim() ? String(value) : fallback;
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

    function describeNotifyReason(value) {{
      var items = parseMaybeJsonArray(value);
      if (!items.length) return '未記録';
      return items.map(function(item) {{ return describeCode(item, notifyReasonLabels); }}).join(' / ');
    }}

    function describeSetup(value) {{
      return describeCode(value, setupLabels);
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

    function describeTier(value) {{
      return describeCode(value, tierLabels);
    }}

    function describeQuality(value) {{
      return describeCode(value, qualityLabels);
    }}

    function createContextBox(label, value) {{
      var box = document.createElement('div');
      box.className = 'context-box';
      var labelEl = document.createElement('span');
      labelEl.className = 'context-label';
      labelEl.textContent = contextHeadings[label] || label;
      var valueEl = document.createElement('div');
      var displayValue = formatContext(value);
      if (label === 'setup') displayValue = describeSetup(value);
      if (label === 'signal_tier') displayValue = describeTier(value);
      if (label === 'notify_reason') displayValue = describeNotifyReason(value);
      if (label === 'data_quality') displayValue = describeQuality(value);
      valueEl.className = 'context-value' + (!value || !String(value).trim() ? ' empty' : '');
      valueEl.textContent = displayValue;
      box.appendChild(labelEl);
      box.appendChild(valueEl);
      return box;
    }}

    function createChip(text) {{
      var chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = text;
      return chip;
    }}

    function extractTime(value) {{
      var raw = String(value || '').trim();
      if (raw.length >= 16 && raw.indexOf('T') !== -1) return raw.slice(5, 10).replace('-', '/') + ' ' + raw.slice(11, 16);
      return raw || '--:--';
    }}

    function renderCards() {{
      var root = document.getElementById('cards');
      root.innerHTML = '';
      rows.forEach(function(row, index) {{
        var card = document.createElement('div');
        card.className = 'card';

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

        var chips = document.createElement('div');
        chips.className = 'chips';
        chips.appendChild(createChip('方向感: ' + describeBias(row.bias)));
        chips.appendChild(createChip('位置評価: ' + describePrelabel(row.prelabel)));
        chips.appendChild(createChip('24時間後評価: ' + describeEvaluation(row.evaluation_status || 'pending')));
        card.appendChild(chips);

        var autoEval = document.createElement('p');
        autoEval.className = 'muted';
        autoEval.textContent = '自動評価: ' + describeAutoEvalSummary(row.auto_eval_summary);
        card.appendChild(autoEval);

        var contextGrid = document.createElement('div');
        contextGrid.className = 'context-grid';
        contextGrid.appendChild(createContextBox('setup', row.primary_setup_status));
        contextGrid.appendChild(createContextBox('signal_tier', row.signal_tier));
        contextGrid.appendChild(createContextBox('notify_reason', row.notify_reason));
        contextGrid.appendChild(createContextBox('data_quality', row.data_quality_flag));
        card.appendChild(contextGrid);

        var grid = document.createElement('div');
        grid.className = 'grid';

        var fields = [
          ['user_verdict', '実務評価', options.verdict, '入る価値・待つ価値・見送る価値、または早い/遅い/低価値を選ぶ', true],
          ['usefulness_1to5', '総合価値', options.usefulness, '5 が最も実務価値あり。迷ったら 3 を基準にする'],
          ['would_trade', '自分ならどうするか', options.wouldTrade, '今のルールと別に、自分の実行判断を残す', true],
          ['actual_move_driver', '値動きの主因', options.moveDriver],
          ['memo_preset', 'メモ候補', options.memoPreset, '最近の通知軸に合わせた短文をそのまま使える'],
          ['review_status', 'レビュー状態', options.reviewStatus, '入力し終えたら done にする', true],
        ];

        fields.forEach(function(fieldDef) {{
          var key = fieldDef[0];
          var label = fieldDef[1];
          var optionList = fieldDef[2];
          var helpText = fieldDef[3];
          var isRecommended = fieldDef[4];
          var box = document.createElement('div');
          box.className = isRecommended ? 'field recommended' : 'field';
          var labelEl = document.createElement('label');
          labelEl.textContent = label;
          if (isRecommended) {{
            var badge = document.createElement('span');
            badge.className = 'recommended-badge';
            badge.textContent = 'おすすめ';
            labelEl.appendChild(badge);
          }}
          box.appendChild(labelEl);
          box.appendChild(createSelect(optionList, row[key] || '', function(event) {{
            row[key] = event.target.value;
            if (key === 'memo_preset') {{
              row.memo = event.target.value;
            }}
            saveDraft();
            updatePreview();
          }}));
          if (helpText) {{
            var helpEl = document.createElement('div');
            helpEl.className = 'field-help';
            helpEl.textContent = helpText;
            box.appendChild(helpEl);
          }}
          grid.appendChild(box);
        }});

        card.appendChild(grid);
        root.appendChild(card);
      }});
      bindSelectHandlers();
    }}

    function syncRowsFromDom() {{
      var selects = document.querySelectorAll('select[data-row-index][data-key]');
      Array.prototype.forEach.call(selects, function(selectEl) {{
        var rowIndex = parseInt(selectEl.getAttribute('data-row-index') || '', 10);
        var key = selectEl.getAttribute('data-key') || '';
        if (isNaN(rowIndex) || !rows[rowIndex] || !key) return;
        rows[rowIndex][key] = selectEl.value;
        if (key === 'memo_preset') {{
          rows[rowIndex].memo = selectEl.value;
        }}
      }});
    }}

    function bindSelectHandlers() {{
      var selects = document.querySelectorAll('select[data-row-index][data-key]');
      Array.prototype.forEach.call(selects, function(selectEl) {{
        if (selectEl.getAttribute('data-bound') === 'true') return;
        selectEl.setAttribute('data-bound', 'true');
        selectEl.addEventListener('change', function(event) {{
          var rowIndex = parseInt(event.target.getAttribute('data-row-index') || '', 10);
          var key = event.target.getAttribute('data-key') || '';
          if (isNaN(rowIndex) || !rows[rowIndex] || !key) return;
          rows[rowIndex][key] = event.target.value;
          if (key === 'memo_preset') {{
            rows[rowIndex].memo = event.target.value;
          }}
          saveDraft();
          updatePreview();
        }});
      }});
    }}

    function escapeMd(value) {{
      return String(value == null ? '' : value).split('|').join('\\\\|').split('\\n').join(' ');
    }}

    function buildMarkdown() {{
      syncRowsFromDom();
      var lines = noteHeader.split('\\n');
      var body = rows.map(function(row) {{
        var cells = reviewColumns.map(function(column) {{ return escapeMd(row[column] || ''); }});
        return '| ' + cells.join(' | ') + ' |';
      }});
      return lines.concat(body).concat(['']).join('\\n');
    }}

    function updatePreview() {{
      document.getElementById('preview').value = buildMarkdown();
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
        memo_preset: String(row.memo_preset || ''),
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
          row.memo_preset = String(saved.memo_preset || '');
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

    function copyMarkdown() {{
      var content = buildMarkdown();
      saveDraft();
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(content);
        alert('Markdown をコピーしました。');
      }} else {{
        var preview = document.getElementById('preview');
        preview.focus();
        preview.select();
        try {{
          document.execCommand('copy');
          alert('Markdown をコピーしました。');
        }} catch (_error) {{
          alert('コピーに失敗しました。下の Markdown を手動でコピーしてください。');
        }}
      }}
      updatePreview();
    }}

    function selectPreviewText() {{
      var preview = document.getElementById('preview');
      buildMarkdown();
      preview.focus();
      preview.select();
      updatePreview();
    }}

    function resetSelections() {{
      rows.forEach(function(row) {{
        row.user_verdict = '';
        row.usefulness_1to5 = '';
        row.would_trade = '';
        row.actual_move_driver = '';
        row.memo_preset = '';
        row.memo = '';
        row.review_status = 'pending';
      }});
      clearDraft();
      renderCards();
      updatePreview();
    }}

    renderCards();
    restoreDraft();
    renderCards();
    bindSelectHandlers();
    updatePreview();
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
        trade = trades.get(signal_id, {})
        outcome = outcomes.get(signal_id, {})
        merged_rows[signal_id] = {
            "signal_id": signal_id,
            "timestamp_jst": row.get("timestamp_jst", ""),
            "subject": row.get("subject", ""),
            "auto_eval_summary": row.get("auto_eval_summary", "") or (
                _auto_eval_summary(outcome) if outcome.get("evaluation_status") == "complete" else _pending_auto_eval_summary(trade)
            ),
            "user_verdict": row.get("user_verdict", ""),
            "usefulness_1to5": row.get("usefulness_1to5", ""),
            "would_trade": row.get("would_trade", ""),
            "actual_move_driver": row.get("actual_move_driver", ""),
            "logic_validated": row.get("logic_validated", ""),
            "memo": row.get("memo", ""),
            "review_status": row.get("review_status", "pending") or "pending",
            "bias": trade.get("bias", ""),
            "prelabel": trade.get("prelabel", ""),
            "primary_setup_status": trade.get("primary_setup_status", ""),
            "signal_tier": trade.get("signal_tier", ""),
            "notify_reason": trade.get("notify_reason_codes", trade.get("reason_for_notification", "")),
            "data_quality_flag": trade.get("data_quality_flag", ""),
            "evaluation_status": outcome.get("evaluation_status", ""),
        }

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
        }

    ordered_rows = sorted(merged_rows.values(), key=lambda row: row.get("timestamp_jst", ""), reverse=True)
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
        if not _is_review_target(str(row.get("timestamp_jst", ""))):
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
