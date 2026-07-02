from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


SAFETY_BOUNDARY = "report-only / not FORMAL_GO / no automatic order / human decides manually"
OUTPUT_COLUMNS = [
    "review_id",
    "source_signal_id",
    "candidate_id",
    "timestamp_jst",
    "candidate_type",
    "candidate_status",
    "side",
    "predicted_side",
    "predicted_position_status",
    "entry_price",
    "stop_price",
    "tp1_price",
    "tp2_price",
    "intraperiod_outcome",
    "entry_reached",
    "first_exit_reason",
    "tp_accuracy_result",
    "position_accuracy_result",
    "timing_review",
    "self_review_label",
    "mfe_r",
    "mae_r",
    "reason_codes",
    "safety_boundary",
    "review_bucket",
    "review_severity",
    "human_review_required",
    "improvement_focus",
    "operator_review_hint",
]

_KNOWN_OUTCOMES = {
    "tp1_first",
    "tp2_first",
    "sl_first",
    "ambiguous",
    "timeout",
    "entry_reached",
    "not_entered",
    "no_ohlcv",
    "pending",
}
_ENTRY_REACHED_OUTCOMES = {
    "tp1_first",
    "tp2_first",
    "sl_first",
    "ambiguous",
    "timeout",
    "entry_reached",
}
_TP_HIT_OUTCOMES = {"tp1_first", "tp2_first"}
_WRONG_OUTCOMES = {"sl_first"}
_FALSE_ALARM_OUTCOMES = {"not_entered"}
_UNRESOLVED_OUTCOMES = {"ambiguous", "timeout", "entry_reached", "pending"}
_NO_DATA_OUTCOMES = {"no_ohlcv"}

_SENSITIVE_PATTERNS = [
    r"\bsource_uid_hash\b",
    r"uid_[A-Za-z0-9][A-Za-z0-9_-]*",
    r"\buid[-_][A-Za-z0-9][A-Za-z0-9_-]*\b",
    r"\baccount[-_][A-Za-z0-9][A-Za-z0-9_-]*\b",
    r"<\s*script\b",
    r"fetch\(",
    r"OPENAI_API_KEY",
    r"SMTP_PASSWORD",
    r"automatic_order_allowed=true",
    r"send_email",
    r"Gmail",
    r"private/(?:account/)?order",
    r"smtp",
]


def _ensure_df(value: pd.DataFrame | None) -> pd.DataFrame:
    if value is None:
        return pd.DataFrame()
    if isinstance(value, pd.DataFrame):
        return value.copy()
    return pd.DataFrame(value)


def _normalize_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if pd.isna(value):
            return default
        return str(value)
    text = str(value).strip()
    if not text:
        return default
    for pattern in _SENSITIVE_PATTERNS:
        text = re.sub(pattern, "[redacted]", text, flags=re.IGNORECASE)
    return text


def _normalize_value(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, list):
        items = [_normalize_value(item, "") for item in value]
        items = [item for item in items if item]
        return ", ".join(items) if items else default
    if isinstance(value, dict):
        if not value:
            return default
        return ", ".join(f"{_normalize_value(key, '')}={_normalize_value(val, '')}" for key, val in value.items())
    return _normalize_text(value, default=default)


def _normalize_side(value: Any) -> str:
    text = _normalize_text(value).lower()
    if text in {"long", "buy"}:
        return "long"
    if text in {"short", "sell"}:
        return "short"
    if text in {"both", "dual"}:
        return "both"
    if text in {"none", "unknown", ""}:
        return ""
    return text


def _normalize_outcome(value: Any) -> str:
    text = _normalize_text(value).lower()
    if not text:
        return ""
    text = text.replace(" ", "_")
    if text in _KNOWN_OUTCOMES:
        return text
    if "tp2" in text and "first" in text:
        return "tp2_first"
    if "tp1" in text and "first" in text:
        return "tp1_first"
    if "sl" in text and "first" in text:
        return "sl_first"
    if "not_entered" in text or "not_entered" in text.replace("-", "_"):
        return "not_entered"
    if "no_ohlcv" in text or "noohlcv" in text or "no_ohlcv" in text.replace("-", "_"):
        return "no_ohlcv"
    if "entry_reached" in text or "entryreached" in text:
        return "entry_reached"
    if "ambiguous" in text:
        return "ambiguous"
    if "timeout" in text:
        return "timeout"
    return text


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return not pd.isna(value) and float(value) != 0.0
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "on"}


def _pick_text(row: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = row.get(key)
        text = _normalize_text(value, "")
        if text:
            return text
    return default


def _pick_normalized_outcome(row: dict[str, Any]) -> str:
    for key in ("outcome", "direction_outcome", "candidate_status", "first_exit_reason"):
        outcome = _normalize_outcome(row.get(key))
        if outcome:
            return outcome
    return ""


def _review_id(*parts: Any) -> str:
    normalized = "|".join(_normalize_value(part, "") for part in parts if _normalize_value(part, ""))
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()
    return f"jr_{digest[:16]}"


def _entry_reached_text(outcome: str, value: Any = None) -> str:
    if value is not None and _truthy(value):
        return "yes"
    if outcome in _ENTRY_REACHED_OUTCOMES:
        return "yes"
    if outcome in _FALSE_ALARM_OUTCOMES or outcome in _NO_DATA_OUTCOMES or outcome == "pending":
        return "no"
    return ""


def _tp_accuracy_for_outcome(outcome: str) -> str:
    if outcome == "tp2_first":
        return "tp2_hit"
    if outcome == "tp1_first":
        return "tp1_hit"
    if outcome == "sl_first":
        return "sl_before_tp"
    if outcome == "not_entered":
        return "not_reached"
    if outcome in {"timeout", "entry_reached", "ambiguous", "pending"}:
        return "unresolved"
    if outcome == "no_ohlcv":
        return "no_data"
    return "unresolved"


def _position_accuracy_for_outcome(outcome: str) -> str:
    if outcome in {"tp1_first", "tp2_first"}:
        return "good"
    if outcome == "sl_first":
        return "wrong"
    if outcome == "not_entered":
        return "false_alarm"
    if outcome in {"timeout", "entry_reached"}:
        return "unresolved"
    if outcome == "ambiguous":
        return "unresolved"
    if outcome == "no_ohlcv":
        return "no_data"
    if outcome == "pending":
        return "unresolved"
    return "unresolved"


def _self_review_label_for_outcome(outcome: str) -> str:
    if outcome in {"tp1_first", "tp2_first"}:
        return "good"
    if outcome == "sl_first":
        return "wrong"
    if outcome == "not_entered":
        return "false_alarm"
    if outcome in {"timeout", "entry_reached", "pending"}:
        return "unresolved"
    if outcome == "ambiguous":
        return "ambiguous"
    if outcome == "no_ohlcv":
        return "no_data"
    return "invalid"


def _timing_review_for_label(label: str) -> str:
    return {
        "good": "on_time",
        "wrong": "late_or_wrong",
        "false_alarm": "not_entered",
        "unresolved": "unresolved",
        "ambiguous": "ambiguous",
        "no_data": "no_data",
        "missed": "missed",
        "invalid": "invalid",
    }.get(label, "unresolved")


def _reason_codes_for_row(row: dict[str, Any], outcome: str, *, missed: bool = False) -> list[str]:
    reason_codes: list[str] = []
    if missed:
        reason_codes.append("missed_without_candidate")
    if not _pick_text(row, "candidate_id", "source_signal_id", "signal_id"):
        reason_codes.append("missing_identity")
    if not _pick_text(row, "timestamp_jst", "timestamp_utc", "timestamp"):
        reason_codes.append("missing_timestamp")
    if not outcome:
        reason_codes.append("missing_outcome")
    elif outcome not in _KNOWN_OUTCOMES:
        reason_codes.append("unknown_outcome")
    if not _pick_text(row, "entry_price"):
        reason_codes.append("missing_entry_price")
    if not _pick_text(row, "stop_price", "stop_loss"):
        reason_codes.append("missing_stop_price")
    if not _pick_text(row, "tp1_price", "tp1"):
        reason_codes.append("missing_tp1_price")
    if not _pick_text(row, "tp2_price", "tp2"):
        reason_codes.append("missing_tp2_price")
    return reason_codes


def _reason_codes_text(reason_codes: list[str]) -> str:
    return "|".join(code for code in reason_codes if code)


def _review_support_fields(self_review_label: str) -> dict[str, str]:
    normalized_label = _normalize_text(self_review_label).lower()
    if normalized_label == "good":
        return {
            "review_bucket": "confirmed_useful",
            "review_severity": "low",
            "human_review_required": "no",
            "improvement_focus": "keep_current_logic",
            "operator_review_hint": "方向とTP到達は良好。大きな調整は不要。",
        }
    if normalized_label == "wrong":
        return {
            "review_bucket": "bad_entry_or_wrong_direction",
            "review_severity": "high",
            "human_review_required": "yes",
            "improvement_focus": "entry_filter_or_direction_check",
            "operator_review_hint": "SL先行。方向、エントリー位置、SL幅を見直す。",
        }
    if normalized_label == "false_alarm":
        return {
            "review_bucket": "no_entry_after_alert",
            "review_severity": "medium",
            "human_review_required": "yes",
            "improvement_focus": "alert_threshold_or_entry_reach",
            "operator_review_hint": "通知後にentry到達なし。早すぎる警告や価格距離を確認する。",
        }
    if normalized_label == "missed":
        return {
            "review_bucket": "missed_opportunity",
            "review_severity": "high",
            "human_review_required": "yes",
            "improvement_focus": "missed_signal_detection",
            "operator_review_hint": "候補なしで有利な値動き。拾えなかった条件を確認する。",
        }
    if normalized_label == "unresolved":
        return {
            "review_bucket": "unresolved_followup",
            "review_severity": "medium",
            "human_review_required": "yes",
            "improvement_focus": "wait_for_outcome_or_timeout_rule",
            "operator_review_hint": "結果未確定。追加足またはtimeout条件を確認する。",
        }
    if normalized_label == "ambiguous":
        return {
            "review_bucket": "ambiguous_outcome",
            "review_severity": "medium",
            "human_review_required": "yes",
            "improvement_focus": "outcome_disambiguation",
            "operator_review_hint": "TP/SL順序が曖昧。足内判定またはデータ粒度を確認する。",
        }
    if normalized_label == "no_data":
        return {
            "review_bucket": "data_gap",
            "review_severity": "medium",
            "human_review_required": "yes",
            "improvement_focus": "data_coverage",
            "operator_review_hint": "OHLCV不足。データ取得範囲と生成タイミングを確認する。",
        }
    if normalized_label == "invalid":
        return {
            "review_bucket": "invalid_input",
            "review_severity": "high",
            "human_review_required": "yes",
            "improvement_focus": "input_schema_or_missing_fields",
            "operator_review_hint": "入力欠損または未知値。reason_codesを確認する。",
        }
    return {
        "review_bucket": "unresolved_followup",
        "review_severity": "medium",
        "human_review_required": "yes",
        "improvement_focus": "manual_review",
        "operator_review_hint": "分類不能。入力値とreason_codesを確認する。",
    }


def _build_review_row_from_candidate(row: dict[str, Any]) -> dict[str, Any]:
    source_signal_id = _pick_text(row, "source_signal_id", "signal_id")
    candidate_id = _pick_text(row, "candidate_id")
    timestamp_jst = _pick_text(row, "timestamp_jst", "timestamp_utc", "timestamp")
    candidate_type = _pick_text(row, "candidate_type")
    candidate_status = _pick_text(row, "candidate_status")
    side = _normalize_side(row.get("side"))
    predicted_side = side or _normalize_side(row.get("bias")) or _normalize_side(row.get("prelabel"))
    predicted_position_status = candidate_status or _pick_text(row, "active_primary_action") or "reviewed"
    outcome = _pick_normalized_outcome(row)
    first_exit_reason = _pick_text(row, "first_exit_reason")
    entry_reached = _entry_reached_text(outcome, row.get("entry_reached"))
    if outcome == "no_ohlcv":
        entry_reached = "no"
    if outcome in {"tp1_first", "tp2_first", "sl_first"} and not first_exit_reason:
        first_exit_reason = outcome.replace("_first", "")
    reason_codes = _reason_codes_for_row(row, outcome)
    if outcome in _TP_HIT_OUTCOMES:
        self_review_label = "good"
    elif outcome == "sl_first":
        self_review_label = "wrong"
    elif outcome == "not_entered":
        self_review_label = "false_alarm"
    elif outcome == "no_ohlcv":
        self_review_label = "no_data"
    elif outcome in {"timeout", "entry_reached", "pending"}:
        self_review_label = "unresolved"
    elif outcome == "ambiguous":
        self_review_label = "ambiguous"
    elif reason_codes:
        self_review_label = "invalid"
    else:
        self_review_label = _self_review_label_for_outcome(outcome)
    position_accuracy_result = _position_accuracy_for_outcome(outcome)
    tp_accuracy_result = _tp_accuracy_for_outcome(outcome)
    if self_review_label == "invalid":
        position_accuracy_result = "unresolved"
        tp_accuracy_result = "unresolved"
    timing_review = _timing_review_for_label(self_review_label)
    support_fields = _review_support_fields(self_review_label)
    return {
        "review_id": _review_id(source_signal_id, candidate_id, timestamp_jst, outcome, candidate_type, side),
        "source_signal_id": source_signal_id,
        "candidate_id": candidate_id,
        "timestamp_jst": timestamp_jst,
        "candidate_type": candidate_type,
        "candidate_status": candidate_status,
        "side": side,
        "predicted_side": predicted_side,
        "predicted_position_status": predicted_position_status,
        "entry_price": _pick_text(row, "entry_price"),
        "stop_price": _pick_text(row, "stop_price", "stop_loss"),
        "tp1_price": _pick_text(row, "tp1_price", "tp1"),
        "tp2_price": _pick_text(row, "tp2_price", "tp2"),
        "intraperiod_outcome": outcome,
        "entry_reached": entry_reached,
        "first_exit_reason": first_exit_reason,
        "tp_accuracy_result": tp_accuracy_result,
        "position_accuracy_result": position_accuracy_result,
        "timing_review": timing_review,
        "self_review_label": self_review_label,
        "mfe_r": _pick_text(row, "mfe_r"),
        "mae_r": _pick_text(row, "mae_r"),
        "reason_codes": _reason_codes_text(reason_codes),
        "safety_boundary": SAFETY_BOUNDARY,
        **support_fields,
    }


def _signal_row_has_favorable_movement(row: dict[str, Any]) -> bool:
    if _truthy(row.get("tp1_hit_first")) or _truthy(row.get("tp2_hit_first")):
        return True
    for key in ("direction_outcome", "outcome", "prelabel"):
        text = _normalize_text(row.get(key), "").lower()
        if not text:
            continue
        normalized = text.replace(" ", "_")
        for token in ("tp1_first", "tp2_first", "win", "favorable", "good", "positive", "profit", "success", "hit_first"):
            if token in normalized:
                return True
    return False


def _build_missed_row(row: dict[str, Any]) -> dict[str, Any]:
    signal_id = _pick_text(row, "signal_id", "source_signal_id")
    timestamp_jst = _pick_text(row, "timestamp_jst", "timestamp_utc", "timestamp")
    outcome = _normalize_outcome(row.get("outcome"))
    if not outcome:
        outcome = "missed"
    predicted_side = _normalize_side(row.get("bias")) or _normalize_side(row.get("prelabel"))
    candidate_type = _pick_text(row, "candidate_type", default="missed_opportunity") or "missed_opportunity"
    candidate_status = "missed_candidate"
    reason_codes = ["missed_without_candidate", "favorable_signal_outcome"]
    if _truthy(row.get("tp1_hit_first")):
        reason_codes.append("tp1_hit_first")
    if _truthy(row.get("tp2_hit_first")):
        reason_codes.append("tp2_hit_first")
    if not signal_id:
        reason_codes.append("missing_signal_id")
    if not timestamp_jst:
        reason_codes.append("missing_timestamp")
    return {
        "review_id": _review_id(signal_id, timestamp_jst, "missed"),
        "source_signal_id": signal_id,
        "candidate_id": "",
        "timestamp_jst": timestamp_jst,
        "candidate_type": candidate_type,
        "candidate_status": candidate_status,
        "side": _normalize_side(row.get("side")) or predicted_side,
        "predicted_side": predicted_side,
        "predicted_position_status": "missed_candidate",
        "entry_price": _pick_text(row, "entry_price", "base_price"),
        "stop_price": _pick_text(row, "stop_price", "stop_loss"),
        "tp1_price": _pick_text(row, "tp1_price", "tp1"),
        "tp2_price": _pick_text(row, "tp2_price", "tp2"),
        "intraperiod_outcome": _pick_text(row, "direction_outcome", "outcome", default="favorable"),
        "entry_reached": "",
        "first_exit_reason": _pick_text(row, "first_exit_reason"),
        "tp_accuracy_result": "missed_without_candidate",
        "position_accuracy_result": "missed",
        "timing_review": "missed",
        "self_review_label": "missed",
        "mfe_r": _pick_text(row, "signal_based_MFE_4h", "signal_based_MFE_12h", "signal_based_MFE_24h", "candidate_delta_24h"),
        "mae_r": _pick_text(row, "signal_based_MAE_4h", "signal_based_MAE_12h", "signal_based_MAE_24h"),
        "reason_codes": _reason_codes_text(reason_codes),
        "safety_boundary": SAFETY_BOUNDARY,
        **_review_support_fields("missed"),
    }


def build_judgment_self_review_rows(
    intraperiod_outcomes_df: pd.DataFrame | None,
    signal_outcomes_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    review_rows: list[dict[str, Any]] = []
    reviewed_signal_ids: set[str] = set()

    intraperiod_df = _ensure_df(intraperiod_outcomes_df)
    for row in intraperiod_df.to_dict(orient="records"):
        review_row = _build_review_row_from_candidate(row)
        review_rows.append(review_row)
        for key in (review_row["source_signal_id"], review_row["candidate_id"]):
            if key:
                reviewed_signal_ids.add(key)

    signal_df = _ensure_df(signal_outcomes_df)
    for row in signal_df.to_dict(orient="records"):
        signal_id = _pick_text(row, "signal_id", "source_signal_id")
        if not signal_id or signal_id in reviewed_signal_ids:
            continue
        if not _signal_row_has_favorable_movement(row):
            continue
        review_rows.append(_build_missed_row(row))

    if not review_rows:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    review_df = pd.DataFrame(review_rows)
    for column in OUTPUT_COLUMNS:
        if column not in review_df.columns:
            review_df[column] = ""
    review_df = review_df.loc[:, OUTPUT_COLUMNS]
    return review_df


def _count_series(series: pd.Series, *, exclude_empty: bool = True) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for value in series.astype("object").tolist():
        text = _normalize_value(value, "").strip()
        if not text and exclude_empty:
            continue
        counts[text or "(blank)"] += 1
    return dict(counts)


def _review_severity_rank(value: Any) -> int:
    text = _normalize_text(value).lower()
    return {"high": 0, "medium": 1, "low": 2}.get(text, 1)


def _human_review_required_rank(value: Any) -> int:
    text = _normalize_text(value).lower()
    return {"yes": 0, "no": 1}.get(text, 1)


def _review_bucket_rank(value: Any) -> int:
    text = _normalize_text(value).lower()
    return {
        "bad_entry_or_wrong_direction": 0,
        "missed_opportunity": 1,
        "no_entry_after_alert": 2,
        "invalid_input": 3,
        "ambiguous_outcome": 4,
        "unresolved_followup": 5,
        "data_gap": 6,
        "confirmed_useful": 7,
    }.get(text, 5)


def build_judgment_self_review_queue(review_df: pd.DataFrame | None, *, limit: int = 10) -> list[dict[str, Any]]:
    df = _ensure_df(review_df)
    if df.empty:
        return []
    for column in (
        "review_id",
        "timestamp_jst",
        "source_signal_id",
        "candidate_id",
        "side",
        "candidate_type",
        "intraperiod_outcome",
        "self_review_label",
        "review_bucket",
        "review_severity",
        "human_review_required",
        "improvement_focus",
        "operator_review_hint",
        "mfe_r",
        "mae_r",
        "reason_codes",
    ):
        if column not in df.columns:
            df[column] = ""
    work_df = df.loc[:, [
        "review_id",
        "timestamp_jst",
        "source_signal_id",
        "candidate_id",
        "side",
        "candidate_type",
        "intraperiod_outcome",
        "self_review_label",
        "review_bucket",
        "review_severity",
        "human_review_required",
        "improvement_focus",
        "operator_review_hint",
        "mfe_r",
        "mae_r",
        "reason_codes",
    ]].copy()
    work_df["_severity_rank"] = work_df["review_severity"].map(_review_severity_rank)
    work_df["_human_review_required_rank"] = work_df["human_review_required"].map(_human_review_required_rank)
    work_df["_bucket_rank"] = work_df["review_bucket"].map(_review_bucket_rank)
    work_df["_timestamp_sort"] = work_df["timestamp_jst"].map(lambda value: _normalize_text(value, ""))
    work_df["_review_id_sort"] = work_df["review_id"].map(lambda value: _normalize_text(value, ""))
    work_df = work_df.sort_values(
        by=[
            "_severity_rank",
            "_human_review_required_rank",
            "_bucket_rank",
            "_timestamp_sort",
            "_review_id_sort",
        ],
        ascending=[True, True, True, True, True],
        kind="mergesort",
    )
    if limit is not None:
        work_df = work_df.head(max(int(limit), 0))
    queue: list[dict[str, Any]] = []
    for row in work_df.to_dict(orient="records"):
        queue.append(
            {
                "review_id": _normalize_value(row.get("review_id"), ""),
                "timestamp_jst": _normalize_value(row.get("timestamp_jst"), ""),
                "source_signal_id": _normalize_value(row.get("source_signal_id"), ""),
                "candidate_id": _normalize_value(row.get("candidate_id"), ""),
                "side": _normalize_value(row.get("side"), ""),
                "candidate_type": _normalize_value(row.get("candidate_type"), ""),
                "intraperiod_outcome": _normalize_value(row.get("intraperiod_outcome"), ""),
                "self_review_label": _normalize_value(row.get("self_review_label"), ""),
                "review_bucket": _normalize_value(row.get("review_bucket"), ""),
                "review_severity": _normalize_value(row.get("review_severity"), ""),
                "human_review_required": _normalize_value(row.get("human_review_required"), ""),
                "improvement_focus": _normalize_value(row.get("improvement_focus"), ""),
                "operator_review_hint": _normalize_value(row.get("operator_review_hint"), ""),
                "mfe_r": _normalize_value(row.get("mfe_r"), ""),
                "mae_r": _normalize_value(row.get("mae_r"), ""),
                "reason_codes": _normalize_value(row.get("reason_codes"), ""),
            }
        )
    return queue


def _top_count_items(counts: dict[str, Any], *, limit: int = 5, key_name: str = "bucket") -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key, value in counts.items():
        try:
            count = int(value)
        except (TypeError, ValueError):
            continue
        text = _normalize_value(key, "")
        if not text:
            continue
        items.append({key_name: text, "count": count})
    items.sort(key=lambda item: (-int(item["count"]), str(item[key_name])))
    return items[: max(int(limit), 0)]


def build_judgment_self_review_digest(
    review_df: pd.DataFrame | None,
    summary: dict[str, Any] | None = None,
    review_queue: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    df = _ensure_df(review_df)
    summary_data = summary or summarize_judgment_self_reviews(df)
    queue = review_queue if review_queue is not None else build_judgment_self_review_queue(df)

    total_review_rows = int(summary_data.get("total_review_rows", len(df)) or 0)
    high_priority_count = int(summary_data.get("high_severity_rows", 0) or 0)
    human_review_required_count = int(summary_data.get("human_review_required_rows", 0) or 0)
    evidence_state = "reviewable"
    if total_review_rows == 0:
        evidence_state = "no_rows"
    else:
        review_bucket_counts = summary_data.get("review_bucket_counts") or {}
        if int(summary_data.get("no_data_rows", 0) or 0) > 0 or int(review_bucket_counts.get("data_gap", 0) or 0) > 0:
            evidence_state = "data_gap"
        elif high_priority_count > 0:
            evidence_state = "high_priority_review"

    primary_condition = "insufficient_evidence"
    if int(summary_data.get("wrong_rows", 0) or 0) > 0:
        primary_condition = "bad_entry_or_wrong_direction"
    elif int(summary_data.get("missed_rows", 0) or 0) > 0:
        primary_condition = "missed_opportunity"
    elif int(summary_data.get("false_alarm_rows", 0) or 0) > 0:
        primary_condition = "no_entry_after_alert"
    elif int(summary_data.get("no_data_rows", 0) or 0) > 0:
        primary_condition = "data_gap"
    elif int(summary_data.get("ambiguous_rows", 0) or 0) > 0:
        primary_condition = "ambiguous_outcome"
    elif int(summary_data.get("unresolved_rows", 0) or 0) > 0:
        primary_condition = "unresolved_followup"
    elif int(summary_data.get("good_rows", 0) or 0) > 0 and human_review_required_count == 0:
        primary_condition = "confirmed_useful"

    if total_review_rows == 0:
        digest_status = "no_evidence"
    elif human_review_required_count > 0:
        digest_status = "needs_human_review"
    elif total_review_rows > 0:
        digest_status = "stable"
    else:
        digest_status = "review_required"

    primary_improvement_focus = "collect_more_evidence"
    if queue:
        primary_improvement_focus = _normalize_value(queue[0].get("improvement_focus"), "") or "collect_more_evidence"
    else:
        focus_counts = summary_data.get("improvement_focus_counts") or {}
        top_focuses = _top_count_items(focus_counts, limit=1, key_name="focus")
        if top_focuses:
            primary_improvement_focus = top_focuses[0]["focus"]

    if digest_status == "no_evidence":
        operator_next_action = "まず通常通知後のintraperiod結果を蓄積する。"
    elif primary_condition == "bad_entry_or_wrong_direction":
        operator_next_action = "SL先行の高優先行から、方向・entry位置・SL幅を確認する。"
    elif primary_condition == "missed_opportunity":
        operator_next_action = "候補なしで有利に動いた行を確認し、拾えなかった条件を整理する。"
    elif primary_condition == "no_entry_after_alert":
        operator_next_action = "entry未到達の警告を確認し、通知が早すぎるか価格距離が遠すぎるかを見る。"
    elif primary_condition == "data_gap":
        operator_next_action = "OHLCVや生成タイミングの欠損を確認し、判定より先にデータ品質を直す。"
    elif primary_condition == "ambiguous_outcome":
        operator_next_action = "TP/SL順序が曖昧な行を確認し、足内判定の粒度を見直す。"
    elif primary_condition == "unresolved_followup":
        operator_next_action = "結果未確定のため、追加足またはtimeout後に再確認する。"
    elif primary_condition == "confirmed_useful":
        operator_next_action = "現行ロジックは維持し、次の通知でも同傾向が続くか観察する。"
    else:
        operator_next_action = "human review queue を上から確認する。"

    review_bucket_counts = summary_data.get("review_bucket_counts") or {}
    improvement_focus_counts = summary_data.get("improvement_focus_counts") or {}
    digest = {
        "digest_status": digest_status,
        "primary_condition": primary_condition,
        "primary_improvement_focus": primary_improvement_focus,
        "high_priority_count": high_priority_count,
        "human_review_required_count": human_review_required_count,
        "evidence_state": evidence_state,
        "top_review_buckets": _top_count_items(review_bucket_counts, limit=5, key_name="bucket"),
        "top_improvement_focuses": _top_count_items(improvement_focus_counts, limit=5, key_name="focus"),
        "operator_next_action": operator_next_action,
        "safety_boundary": SAFETY_BOUNDARY,
    }
    return digest


def build_judgment_self_review_change_readiness(
    summary: dict[str, Any] | None,
    review_digest: dict[str, Any] | None = None,
    review_queue: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    summary_data = summary or {}
    digest_data = review_digest or {}
    queue = review_queue or []

    total_review_rows = int(summary_data.get("total_review_rows", 0) or 0)
    human_review_required_rows = int(summary_data.get("human_review_required_rows", 0) or 0)
    high_severity_rows = int(summary_data.get("high_severity_rows", 0) or 0)
    good_rows = int(summary_data.get("good_rows", 0) or 0)
    improvement_focus_counts = summary_data.get("improvement_focus_counts") or {}

    repeated_issue_focus = ""
    repeated_issue_count = 0
    if queue:
        focus_counts = Counter(
            _normalize_value(item.get("improvement_focus"), "")
            for item in queue
            if _normalize_value(item.get("improvement_focus"), "")
        )
        if focus_counts:
            repeated_issue_focus, repeated_issue_count = sorted(
                focus_counts.items(),
                key=lambda item: (-int(item[1]), str(item[0])),
            )[0]
    if not repeated_issue_focus:
        top_focuses = _top_count_items(improvement_focus_counts, limit=1, key_name="focus")
        if top_focuses:
            repeated_issue_focus = top_focuses[0]["focus"]
            repeated_issue_count = int(top_focuses[0]["count"])

    evidence_gate = "review_required"
    if total_review_rows == 0:
        evidence_gate = "no_rows"
    elif total_review_rows < 5:
        evidence_gate = "insufficient_sample"
    elif repeated_issue_count >= 3:
        evidence_gate = "repeated_issue_detected"
    elif total_review_rows >= 5 and repeated_issue_count > 0:
        evidence_gate = "single_or_mixed_issue"

    if total_review_rows == 0:
        change_readiness_status = "no_evidence"
    elif total_review_rows < 5:
        change_readiness_status = "observe_more"
    elif human_review_required_rows == 0 and good_rows >= 5:
        change_readiness_status = "stable_observation"
    elif human_review_required_rows > 0 and high_severity_rows < 3:
        change_readiness_status = "human_review_first"
    elif repeated_issue_count >= 3 and total_review_rows >= 5:
        change_readiness_status = "tuning_review_candidate"
    else:
        change_readiness_status = "observe_more"

    change_readiness_level = {
        "no_evidence": "none",
        "observe_more": "low",
        "human_review_first": "medium",
        "tuning_review_candidate": "high",
        "stable_observation": "low",
    }.get(change_readiness_status, "low")

    if total_review_rows == 0:
        minimum_next_observations = 5
    elif total_review_rows < 5:
        minimum_next_observations = 5 - total_review_rows
    elif evidence_gate == "single_or_mixed_issue":
        minimum_next_observations = 2
    else:
        minimum_next_observations = 0

    operator_change_guidance = {
        "no_evidence": "まだ変更判断はしない。通常通知後の自己判定を最低5件蓄積する。",
        "observe_more": "まだサンプル不足。変更せず、次の通常通知を観察する。",
        "human_review_first": "高優先行を人間が確認する。変更判断はレビュー後に限定する。",
        "tuning_review_candidate": "同じ改善焦点が複数回出ている。自動変更せず、別タスクで人間承認付きの調整レビューを切る。",
        "stable_observation": "大きな変更は不要。現行ロジックを維持して観察を続ける。",
    }.get(change_readiness_status, "変更せず、human review queue を確認する。")

    return {
        "change_readiness_status": change_readiness_status,
        "change_readiness_level": change_readiness_level,
        "tuning_review_candidate": "yes" if change_readiness_status == "tuning_review_candidate" else "no",
        "tuning_review_allowed": "no",
        "human_approval_required": "yes",
        "evidence_gate": evidence_gate,
        "evidence_reason": _normalize_value(digest_data.get("primary_condition"), "") or _normalize_value(digest_data.get("evidence_state"), ""),
        "repeated_issue_focus": repeated_issue_focus,
        "repeated_issue_count": repeated_issue_count,
        "minimum_next_observations": minimum_next_observations,
        "operator_change_guidance": operator_change_guidance,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def summarize_judgment_self_reviews(review_df: pd.DataFrame | None) -> dict[str, Any]:
    df = _ensure_df(review_df)
    if df.empty:
        return {
            "total_review_rows": 0,
            "candidate_review_rows": 0,
            "missed_rows": 0,
            "good_rows": 0,
            "wrong_rows": 0,
            "false_alarm_rows": 0,
            "unresolved_rows": 0,
            "ambiguous_rows": 0,
            "no_data_rows": 0,
            "tp1_hit_rows": 0,
            "tp2_hit_rows": 0,
            "sl_before_tp_rows": 0,
            "position_accuracy_counts": {},
            "tp_accuracy_counts": {},
            "self_review_label_counts": {},
            "review_bucket_counts": {},
            "review_severity_counts": {},
            "human_review_required_counts": {},
            "improvement_focus_counts": {},
            "side_counts": {},
            "candidate_type_counts": {},
            "missed_opportunity_rows": 0,
            "high_severity_rows": 0,
            "human_review_required_rows": 0,
            "safety_boundary": SAFETY_BOUNDARY,
        }

    if "self_review_label" not in df.columns:
        df["self_review_label"] = ""
    if "position_accuracy_result" not in df.columns:
        df["position_accuracy_result"] = ""
    if "tp_accuracy_result" not in df.columns:
        df["tp_accuracy_result"] = ""
    if "side" not in df.columns:
        df["side"] = ""
    if "candidate_type" not in df.columns:
        df["candidate_type"] = ""
    for column in ("review_bucket", "review_severity", "human_review_required", "improvement_focus"):
        if column not in df.columns:
            df[column] = ""

    self_review_counts = _count_series(df["self_review_label"])
    position_counts = _count_series(df["position_accuracy_result"])
    tp_counts = _count_series(df["tp_accuracy_result"])
    review_bucket_counts = _count_series(df["review_bucket"])
    review_severity_counts = _count_series(df["review_severity"])
    human_review_required_counts = _count_series(df["human_review_required"])
    improvement_focus_counts = _count_series(df["improvement_focus"])
    side_counts = _count_series(df["side"])
    candidate_type_counts = _count_series(df["candidate_type"])

    total_rows = int(len(df))
    missed_rows = int((df["self_review_label"].astype("object").astype(str).str.lower() == "missed").sum())
    candidate_review_rows = int(total_rows - missed_rows)
    good_rows = int((df["self_review_label"].astype("object").astype(str).str.lower() == "good").sum())
    wrong_rows = int((df["self_review_label"].astype("object").astype(str).str.lower() == "wrong").sum())
    false_alarm_rows = int((df["self_review_label"].astype("object").astype(str).str.lower() == "false_alarm").sum())
    unresolved_rows = int((df["self_review_label"].astype("object").astype(str).str.lower() == "unresolved").sum())
    ambiguous_rows = int((df["self_review_label"].astype("object").astype(str).str.lower() == "ambiguous").sum())
    no_data_rows = int((df["self_review_label"].astype("object").astype(str).str.lower() == "no_data").sum())
    tp1_hit_rows = int((df["tp_accuracy_result"].astype("object").astype(str).str.lower() == "tp1_hit").sum())
    tp2_hit_rows = int((df["tp_accuracy_result"].astype("object").astype(str).str.lower() == "tp2_hit").sum())
    sl_before_tp_rows = int((df["tp_accuracy_result"].astype("object").astype(str).str.lower() == "sl_before_tp").sum())
    high_severity_rows = int((df["review_severity"].astype("object").astype(str).str.lower() == "high").sum())
    human_review_required_rows = int((df["human_review_required"].astype("object").astype(str).str.lower() == "yes").sum())

    return {
        "total_review_rows": total_rows,
        "candidate_review_rows": candidate_review_rows,
        "missed_rows": missed_rows,
        "good_rows": good_rows,
        "wrong_rows": wrong_rows,
        "false_alarm_rows": false_alarm_rows,
        "unresolved_rows": unresolved_rows,
        "ambiguous_rows": ambiguous_rows,
        "no_data_rows": no_data_rows,
        "tp1_hit_rows": tp1_hit_rows,
        "tp2_hit_rows": tp2_hit_rows,
        "sl_before_tp_rows": sl_before_tp_rows,
        "position_accuracy_counts": position_counts,
        "tp_accuracy_counts": tp_counts,
        "self_review_label_counts": self_review_counts,
        "review_bucket_counts": review_bucket_counts,
        "review_severity_counts": review_severity_counts,
        "human_review_required_counts": human_review_required_counts,
        "improvement_focus_counts": improvement_focus_counts,
        "side_counts": side_counts,
        "candidate_type_counts": candidate_type_counts,
        "missed_opportunity_rows": missed_rows,
        "high_severity_rows": high_severity_rows,
        "human_review_required_rows": human_review_required_rows,
        "safety_boundary": SAFETY_BOUNDARY,
    }


def _sanitize_review_df(review_df: pd.DataFrame | None) -> pd.DataFrame:
    df = _ensure_df(review_df)
    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    sanitized = df.copy()
    for column in sanitized.columns:
        sanitized[column] = sanitized[column].map(lambda value: _normalize_value(value, "") if not isinstance(value, (int, float, bool)) or isinstance(value, bool) else value)
    return sanitized.loc[:, [column for column in OUTPUT_COLUMNS if column in sanitized.columns]]


def _markdown_lines(
    review_df: pd.DataFrame,
    review_queue: list[dict[str, Any]],
    review_digest: dict[str, Any],
    change_readiness: dict[str, Any],
    summary: dict[str, Any],
    report_date: str,
    input_counts: dict[str, Any],
) -> list[str]:
    lines = [
        "# Judgment Self-Review Report",
        "",
        "## Purpose",
        "- report-only",
        "- not FORMAL_GO",
        "- no automatic order",
        "- human decides manually",
        "- links intraperiod judgments to later outcome evidence and evaluates predicted position / TP accuracy",
        "",
        "## Report Date",
        f"- {report_date}",
        "",
        "## Input Status",
        f"- intraperiod_outcomes: status={input_counts['intraperiod_outcomes']['status']} / rows={input_counts['intraperiod_outcomes']['rows']}",
        f"- signal_outcomes: status={input_counts['signal_outcomes']['status']} / rows={input_counts['signal_outcomes']['rows']}",
        "",
        "## Summary",
        f"- total_review_rows: {summary['total_review_rows']}",
        f"- candidate_review_rows: {summary['candidate_review_rows']}",
        f"- missed_rows: {summary['missed_rows']}",
        f"- good_rows: {summary['good_rows']}",
        f"- wrong_rows: {summary['wrong_rows']}",
        f"- false_alarm_rows: {summary['false_alarm_rows']}",
        f"- unresolved_rows: {summary['unresolved_rows']}",
        f"- ambiguous_rows: {summary['ambiguous_rows']}",
        f"- no_data_rows: {summary['no_data_rows']}",
        f"- tp1_hit_rows: {summary['tp1_hit_rows']}",
        f"- tp2_hit_rows: {summary['tp2_hit_rows']}",
        f"- sl_before_tp_rows: {summary['sl_before_tp_rows']}",
        "",
        "## Position Accuracy",
        f"- {json.dumps(summary['position_accuracy_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## TP Accuracy",
        f"- {json.dumps(summary['tp_accuracy_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Self-Review Labels",
        f"- {json.dumps(summary['self_review_label_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Review Buckets",
        f"- {json.dumps(summary['review_bucket_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Review Severity",
        f"- {json.dumps(summary['review_severity_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Human Review Required",
        f"- {json.dumps(summary['human_review_required_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Improvement Focus",
        f"- {json.dumps(summary['improvement_focus_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Self-Review Digest",
        f"- digest_status: {_normalize_value(review_digest.get('digest_status'), '')}",
        f"- primary_condition: {_normalize_value(review_digest.get('primary_condition'), '')}",
        f"- primary_improvement_focus: {_normalize_value(review_digest.get('primary_improvement_focus'), '')}",
        f"- evidence_state: {_normalize_value(review_digest.get('evidence_state'), '')}",
        f"- high_priority_count: {_normalize_value(review_digest.get('high_priority_count'), '')}",
        f"- human_review_required_count: {_normalize_value(review_digest.get('human_review_required_count'), '')}",
        f"- operator_next_action: {_normalize_value(review_digest.get('operator_next_action'), '')}",
        "",
        "## Change Readiness Gate",
        f"- change_readiness_status: {_normalize_value(change_readiness.get('change_readiness_status'), '')}",
        f"- change_readiness_level: {_normalize_value(change_readiness.get('change_readiness_level'), '')}",
        f"- tuning_review_candidate: {_normalize_value(change_readiness.get('tuning_review_candidate'), '')}",
        f"- tuning_review_allowed: {_normalize_value(change_readiness.get('tuning_review_allowed'), '')}",
        f"- evidence_gate: {_normalize_value(change_readiness.get('evidence_gate'), '')}",
        f"- evidence_reason: {_normalize_value(change_readiness.get('evidence_reason'), '')}",
        f"- repeated_issue_focus: {_normalize_value(change_readiness.get('repeated_issue_focus'), '')}",
        f"- repeated_issue_count: {_normalize_value(change_readiness.get('repeated_issue_count'), '')}",
        f"- minimum_next_observations: {_normalize_value(change_readiness.get('minimum_next_observations'), '')}",
        f"- operator_change_guidance: {_normalize_value(change_readiness.get('operator_change_guidance'), '')}",
        "",
        "## Human Review Queue",
    ]
    if not review_queue:
        lines.append("- none")
    else:
        for item in review_queue:
            lines.append(
                "- "
                f"{_normalize_value(item.get('review_severity'), '')} / "
                f"{_normalize_value(item.get('self_review_label'), '')} / "
                f"{_normalize_value(item.get('side'), '')} / "
                f"{_normalize_value(item.get('timestamp_jst'), '')} / "
                f"focus={_normalize_value(item.get('improvement_focus'), '')} / "
                f"hint={_normalize_value(item.get('operator_review_hint'), '')}"
            )
    lines.extend([
        "## Side Counts",
        f"- {json.dumps(summary['side_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Candidate Type Counts",
        f"- {json.dumps(summary['candidate_type_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Safety Boundary",
        f"- {summary['safety_boundary']}",
    ])
    if summary["missed_opportunity_rows"]:
        lines.extend(["", "## Missed Opportunity", f"- missed_opportunity_rows: {summary['missed_opportunity_rows']}"])
    return lines


def build_judgment_self_review_report(
    intraperiod_outcomes_df: pd.DataFrame | None,
    signal_outcomes_df: pd.DataFrame | None = None,
    *,
    output_csv: Path | None = None,
    output_md: Path | None = None,
    report_date: str | None = None,
    dry_run: bool = False,
) -> tuple[str, dict[str, Any]]:
    intraperiod_input_df = _ensure_df(intraperiod_outcomes_df)
    signal_input_df = _ensure_df(signal_outcomes_df)
    review_df = build_judgment_self_review_rows(intraperiod_input_df, signal_input_df if not signal_input_df.empty else signal_input_df)
    review_queue = build_judgment_self_review_queue(review_df)
    summary = summarize_judgment_self_reviews(review_df)
    review_digest = build_judgment_self_review_digest(review_df, summary, review_queue)
    change_readiness = build_judgment_self_review_change_readiness(summary, review_digest, review_queue)
    resolved_report_date = (report_date or datetime.now(tz=timezone(timedelta(hours=9))).strftime("%Y%m%d")).strip()
    input_counts = {
        "intraperiod_outcomes": {
            "status": "missing" if intraperiod_outcomes_df is None else ("header_only" if intraperiod_input_df.empty else "ok"),
            "rows": int(len(intraperiod_input_df)),
        },
        "signal_outcomes": {
            "status": "missing" if signal_outcomes_df is None else ("header_only" if signal_input_df.empty else "ok"),
            "rows": int(len(signal_input_df)),
        },
    }
    report = "\n".join(_markdown_lines(review_df, review_queue, review_digest, change_readiness, summary, resolved_report_date, input_counts)) + "\n"

    sanitized_df = _sanitize_review_df(review_df)
    if not dry_run:
        if output_csv is not None:
            output_csv.parent.mkdir(parents=True, exist_ok=True)
            sanitized_df.to_csv(output_csv, index=False)
        if output_md is not None:
            output_md.parent.mkdir(parents=True, exist_ok=True)
            output_md.write_text(report, encoding="utf-8")

    payload = {
        "schema_version": "judgment_self_review.v1",
        "report_date": resolved_report_date,
        "report_path": str(output_md) if output_md is not None else "",
        "output_csv_path": str(output_csv) if output_csv is not None else "",
        "input_counts": input_counts,
        "summary": summary,
        "review_digest": review_digest,
        "change_readiness": change_readiness,
        "review_queue": review_queue,
        "review_queue_count": len(review_queue),
        "report_only": True,
        "formal_go": False,
        "automatic_order_allowed": False,
        "human_decides_manually": True,
        "safety_boundary": SAFETY_BOUNDARY,
    }
    return report, payload
