from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import mock

import pandas as pd
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.trade.judgment_self_review import (  # noqa: E402
    SAFETY_BOUNDARY,
    build_judgment_self_review_change_readiness,
    build_judgment_self_review_digest,
    build_judgment_self_review_report,
    build_judgment_self_review_run_metadata,
    build_judgment_self_review_rows,
    build_judgment_self_review_queue,
    summarize_judgment_self_reviews,
)
import tools.log_feedback as log_feedback  # noqa: E402


INTRAPERIOD_HEADERS = [
    "candidate_id",
    "source_signal_id",
    "timestamp_jst",
    "active_primary_action",
    "candidate_type",
    "candidate_status",
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
]

SIGNAL_HEADERS = [
    "signal_id",
    "timestamp_jst",
    "bias",
    "prelabel",
    "direction_outcome",
    "tp1_hit_first",
    "outcome",
    "signal_based_MFE_4h",
    "signal_based_MAE_4h",
    "signal_based_MFE_12h",
    "signal_based_MAE_12h",
    "signal_based_MFE_24h",
    "signal_based_MAE_24h",
]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return path


def _candidate_row(
    candidate_id: str,
    signal_id: str,
    outcome: str,
    side: str = "long",
    *,
    candidate_status: str = "ready",
    candidate_type: str = "active_limit_retest",
) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "source_signal_id": signal_id,
        "timestamp_jst": "2026-07-02T09:00:00+09:00",
        "active_primary_action": "ACTIVE_LIMIT_RETEST",
        "candidate_type": candidate_type,
        "candidate_status": candidate_status,
        "side": side,
        "entry_mode": "limit_zone_mid",
        "entry_price": "100",
        "stop_price": "95",
        "tp1_price": "110",
        "tp2_price": "120",
        "outcome": outcome,
        "entry_reached_time": "2026-07-02T09:15:00+09:00",
        "first_exit_time": "2026-07-02T09:30:00+09:00",
        "first_exit_reason": outcome.replace("_first", "") if outcome in {"tp1_first", "tp2_first", "sl_first"} else outcome,
        "mfe_price": "5",
        "mae_price": "1",
        "mfe_r": "1.2500",
        "mae_r": "0.2500",
    }


def _signal_row(signal_id: str, *, favorable: bool = True, sensitive: bool = False) -> dict[str, str]:
    text = "positive" if favorable else "neutral"
    return {
        "signal_id": signal_id,
        "timestamp_jst": "2026-07-02T09:00:00+09:00",
        "bias": "long",
        "prelabel": "ENTRY_OK",
        "direction_outcome": text,
        "tp1_hit_first": "yes" if favorable else "no",
        "outcome": text,
        "signal_based_MFE_4h": "2.0",
        "signal_based_MAE_4h": "0.5",
        "signal_based_MFE_12h": "3.0",
        "signal_based_MAE_12h": "0.7",
        "signal_based_MFE_24h": "4.0",
        "signal_based_MAE_24h": "0.9",
        **({"prelabel": "uid_sensitive_12345 <script> fetch( send_email Gmail smtp OPENAI_API_KEY SMTP_PASSWORD private/order"} if sensitive else {}),
    }


class JudgmentSelfReviewTests(unittest.TestCase):
    def test_change_readiness_gate_blocks_premature_tuning(self) -> None:
        empty_gate = build_judgment_self_review_change_readiness(None, None, None)
        self.assertEqual(empty_gate["change_readiness_status"], "no_evidence")
        self.assertEqual(empty_gate["change_readiness_level"], "none")
        self.assertEqual(empty_gate["tuning_review_allowed"], "no")
        self.assertEqual(empty_gate["human_approval_required"], "yes")
        self.assertEqual(empty_gate["minimum_next_observations"], 5)

        small_df = build_judgment_self_review_rows(
            pd.DataFrame([_candidate_row("cand-small", "sig-small", "tp1_first")]),
            None,
        )
        small_summary = summarize_judgment_self_reviews(small_df)
        small_queue = build_judgment_self_review_queue(small_df)
        small_digest = build_judgment_self_review_digest(small_df, small_summary, small_queue)
        small_gate = build_judgment_self_review_change_readiness(small_summary, small_digest, small_queue)
        self.assertEqual(small_gate["change_readiness_status"], "observe_more")
        self.assertEqual(small_gate["change_readiness_level"], "low")
        self.assertEqual(small_gate["minimum_next_observations"], 4)

        repeated_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-r1", "sig-r1", "sl_first"),
                    _candidate_row("cand-r2", "sig-r2", "sl_first"),
                    _candidate_row("cand-r3", "sig-r3", "sl_first"),
                    _candidate_row("cand-g1", "sig-g1", "tp1_first"),
                    _candidate_row("cand-g2", "sig-g2", "tp2_first"),
                ]
            ),
            None,
        )
        repeated_summary = summarize_judgment_self_reviews(repeated_df)
        repeated_queue = build_judgment_self_review_queue(repeated_df)
        repeated_digest = build_judgment_self_review_digest(repeated_df, repeated_summary, repeated_queue)
        repeated_gate = build_judgment_self_review_change_readiness(repeated_summary, repeated_digest, repeated_queue)
        self.assertEqual(repeated_gate["change_readiness_status"], "tuning_review_candidate")
        self.assertEqual(repeated_gate["change_readiness_level"], "high")
        self.assertEqual(repeated_gate["tuning_review_candidate"], "yes")
        self.assertEqual(repeated_gate["tuning_review_allowed"], "no")
        self.assertEqual(repeated_gate["repeated_issue_focus"], "entry_filter_or_direction_check")
        self.assertEqual(repeated_gate["repeated_issue_count"], 3)

        good_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-good-1", "sig-good-1", "tp1_first"),
                    _candidate_row("cand-good-2", "sig-good-2", "tp2_first"),
                    _candidate_row("cand-good-3", "sig-good-3", "tp1_first"),
                    _candidate_row("cand-good-4", "sig-good-4", "tp2_first"),
                    _candidate_row("cand-good-5", "sig-good-5", "tp1_first"),
                ]
            ),
            None,
        )
        good_summary = summarize_judgment_self_reviews(good_df)
        good_queue = build_judgment_self_review_queue(good_df)
        good_digest = build_judgment_self_review_digest(good_df, good_summary, good_queue)
        good_gate = build_judgment_self_review_change_readiness(good_summary, good_digest, good_queue)
        self.assertEqual(good_gate["change_readiness_status"], "stable_observation")
        self.assertEqual(good_gate["change_readiness_level"], "low")
        self.assertEqual(good_gate["operator_change_guidance"], "大きな変更は不要。現行ロジックを維持して観察を続ける。")

    def test_explicit_late_outcome_is_classified_as_late(self) -> None:
        review_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    {
                        "candidate_id": "cand-late",
                        "source_signal_id": "sig-late",
                        "timestamp_jst": "2026-07-02T09:00:00+09:00",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "candidate_type": "active_limit_retest",
                        "candidate_status": "ready",
                        "side": "long",
                        "entry_mode": "limit_zone_mid",
                        "entry_price": "100",
                        "stop_price": "95",
                        "tp1_price": "110",
                        "tp2_price": "120",
                        "outcome": "too_late",
                        "entry_reached_time": "2026-07-02T09:15:00+09:00",
                        "first_exit_time": "2026-07-02T09:30:00+09:00",
                        "first_exit_reason": "too_late",
                        "mfe_price": "5",
                        "mae_price": "1",
                        "mfe_r": "1.2500",
                        "mae_r": "0.2500",
                    }
                ]
            ),
            None,
        )
        self.assertEqual(review_df.loc[0, "intraperiod_outcome"], "late")
        self.assertEqual(review_df.loc[0, "self_review_label"], "late")
        self.assertEqual(review_df.loc[0, "timing_review"], "late")
        self.assertEqual(review_df.loc[0, "review_bucket"], "late_signal")
        self.assertEqual(review_df.loc[0, "review_severity"], "high")
        self.assertEqual(review_df.loc[0, "human_review_required"], "yes")
        self.assertEqual(review_df.loc[0, "improvement_focus"], "timing_or_alert_delay")
        self.assertEqual(review_df.loc[0, "operator_review_hint"], "通知または判定が遅い可能性。15分足で初動後になっていないか確認する。")

        summary = summarize_judgment_self_reviews(review_df)
        self.assertEqual(summary["late_rows"], 1)
        digest = build_judgment_self_review_digest(review_df, summary, build_judgment_self_review_queue(review_df))
        self.assertEqual(digest["primary_condition"], "late_signal")
        self.assertEqual(digest["operator_next_action"], "遅れ判定の行を確認し、通知時点で15分足の初動後になっていないかを見る。")

    def test_self_review_digest_prioritizes_error_classes_deterministically(self) -> None:
        empty_digest = build_judgment_self_review_digest(None)
        self.assertEqual(empty_digest["digest_status"], "no_evidence")
        self.assertEqual(empty_digest["primary_condition"], "insufficient_evidence")
        self.assertEqual(empty_digest["primary_improvement_focus"], "collect_more_evidence")
        self.assertEqual(empty_digest["operator_next_action"], "まず通常通知後のintraperiod結果を蓄積する。")

        wrong_df = build_judgment_self_review_rows(
            pd.DataFrame([_candidate_row("cand-wrong", "sig-wrong", "sl_first")]),
            None,
        )
        wrong_summary = summarize_judgment_self_reviews(wrong_df)
        wrong_queue = build_judgment_self_review_queue(wrong_df)
        wrong_digest = build_judgment_self_review_digest(wrong_df, wrong_summary, wrong_queue)
        self.assertEqual(wrong_digest["digest_status"], "needs_human_review")
        self.assertEqual(wrong_digest["primary_condition"], "bad_entry_or_wrong_direction")
        self.assertEqual(wrong_digest["primary_improvement_focus"], "entry_filter_or_direction_check")
        self.assertEqual(wrong_digest["operator_next_action"], "SL先行の高優先行から、方向・entry位置・SL幅を確認する。")
        self.assertEqual(wrong_digest["evidence_state"], "high_priority_review")
        self.assertGreaterEqual(wrong_digest["high_priority_count"], 1)
        self.assertGreaterEqual(wrong_digest["human_review_required_count"], 1)

        missed_df = build_judgment_self_review_rows(
            pd.DataFrame([_candidate_row("cand-good", "sig-good", "tp1_first")]),
            pd.DataFrame([_signal_row("sig-missed", favorable=True)]),
        )
        missed_summary = summarize_judgment_self_reviews(missed_df)
        missed_queue = build_judgment_self_review_queue(missed_df)
        missed_digest = build_judgment_self_review_digest(missed_df, missed_summary, missed_queue)
        self.assertEqual(missed_digest["primary_condition"], "missed_opportunity")
        self.assertEqual(missed_digest["primary_improvement_focus"], "missed_signal_detection")
        self.assertEqual(missed_digest["operator_next_action"], "候補なしで有利に動いた行を確認し、拾えなかった条件を整理する。")

        good_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-good-1", "sig-good-1", "tp1_first"),
                    _candidate_row("cand-good-2", "sig-good-2", "tp2_first"),
                ]
            ),
            None,
        )
        good_summary = summarize_judgment_self_reviews(good_df)
        good_queue = build_judgment_self_review_queue(good_df)
        good_digest = build_judgment_self_review_digest(good_df, good_summary, good_queue)
        self.assertEqual(good_digest["digest_status"], "stable")
        self.assertEqual(good_digest["primary_condition"], "confirmed_useful")
        self.assertEqual(good_digest["primary_improvement_focus"], "keep_current_logic")
        self.assertEqual(good_digest["operator_next_action"], "現行ロジックは維持し、次の通知でも同傾向が続くか観察する。")

    def test_human_review_queue_orders_rows_deterministically(self) -> None:
        review_df = pd.DataFrame(
            [
                {
                    "review_id": "r-good",
                    "timestamp_jst": "2026-07-02T10:00:00+09:00",
                    "source_signal_id": "sig-good",
                    "candidate_id": "cand-good",
                    "side": "long",
                    "candidate_type": "type-a",
                    "intraperiod_outcome": "tp1_first",
                    "self_review_label": "good",
                    "review_bucket": "confirmed_useful",
                    "review_severity": "low",
                    "human_review_required": "no",
                    "improvement_focus": "keep_current_logic",
                    "operator_review_hint": "good hint",
                    "mfe_r": "1.0",
                    "mae_r": "0.1",
                    "reason_codes": "",
                },
                {
                    "review_id": "r-wrong",
                    "timestamp_jst": "2026-07-02T09:00:00+09:00",
                    "source_signal_id": "sig-wrong",
                    "candidate_id": "cand-wrong",
                    "side": "short",
                    "candidate_type": "type-b",
                    "intraperiod_outcome": "sl_first",
                    "self_review_label": "wrong",
                    "review_bucket": "bad_entry_or_wrong_direction",
                    "review_severity": "high",
                    "human_review_required": "yes",
                    "improvement_focus": "entry_filter_or_direction_check",
                    "operator_review_hint": "wrong hint",
                    "mfe_r": "2.0",
                    "mae_r": "0.5",
                    "reason_codes": "r1",
                },
                {
                    "review_id": "r-late",
                    "timestamp_jst": "2026-07-02T08:30:00+09:00",
                    "source_signal_id": "sig-late",
                    "candidate_id": "cand-late",
                    "side": "long",
                    "candidate_type": "type-b2",
                    "intraperiod_outcome": "late",
                    "self_review_label": "late",
                    "review_bucket": "late_signal",
                    "review_severity": "high",
                    "human_review_required": "yes",
                    "improvement_focus": "timing_or_alert_delay",
                    "operator_review_hint": "late hint",
                    "mfe_r": "1.5",
                    "mae_r": "0.2",
                    "reason_codes": "r1b",
                },
                {
                    "review_id": "r-false",
                    "timestamp_jst": "2026-07-02T08:00:00+09:00",
                    "source_signal_id": "sig-false",
                    "candidate_id": "cand-false",
                    "side": "long",
                    "candidate_type": "type-c",
                    "intraperiod_outcome": "not_entered",
                    "self_review_label": "false_alarm",
                    "review_bucket": "no_entry_after_alert",
                    "review_severity": "medium",
                    "human_review_required": "yes",
                    "improvement_focus": "alert_threshold_or_entry_reach",
                    "operator_review_hint": "false hint",
                    "mfe_r": "0.2",
                    "mae_r": "0.1",
                    "reason_codes": "r2",
                },
                {
                    "review_id": "r-missed",
                    "timestamp_jst": "2026-07-02T07:00:00+09:00",
                    "source_signal_id": "sig-missed",
                    "candidate_id": "",
                    "side": "short",
                    "candidate_type": "missed_opportunity",
                    "intraperiod_outcome": "tp2_first",
                    "self_review_label": "missed",
                    "review_bucket": "missed_opportunity",
                    "review_severity": "high",
                    "human_review_required": "yes",
                    "improvement_focus": "missed_signal_detection",
                    "operator_review_hint": "missed hint",
                    "mfe_r": "3.0",
                    "mae_r": "0.0",
                    "reason_codes": "missed_without_candidate",
                },
                {
                    "review_id": "r-no-data",
                    "timestamp_jst": "2026-07-02T06:00:00+09:00",
                    "source_signal_id": "sig-no-data",
                    "candidate_id": "cand-no-data",
                    "side": "long",
                    "candidate_type": "type-d",
                    "intraperiod_outcome": "no_ohlcv",
                    "self_review_label": "no_data",
                    "review_bucket": "data_gap",
                    "review_severity": "medium",
                    "human_review_required": "yes",
                    "improvement_focus": "data_coverage",
                    "operator_review_hint": "no data hint",
                    "mfe_r": "",
                    "mae_r": "",
                    "reason_codes": "missing",
                },
                {
                    "review_id": "r-invalid",
                    "timestamp_jst": "2026-07-02T11:00:00+09:00",
                    "source_signal_id": "sig-invalid",
                    "candidate_id": "cand-invalid",
                    "side": "long",
                    "candidate_type": "type-e",
                    "intraperiod_outcome": "",
                    "self_review_label": "invalid",
                    "review_bucket": "invalid_input",
                    "review_severity": "high",
                    "human_review_required": "yes",
                    "improvement_focus": "input_schema_or_missing_fields",
                    "operator_review_hint": "invalid hint",
                    "mfe_r": "4.0",
                    "mae_r": "1.0",
                    "reason_codes": "missing_outcome",
                },
            ]
        )
        queue = build_judgment_self_review_queue(review_df, limit=10)
        self.assertEqual([row["review_id"] for row in queue], [
            "r-wrong",
            "r-late",
            "r-missed",
            "r-invalid",
            "r-false",
            "r-no-data",
            "r-good",
        ])
        self.assertEqual(queue[0]["review_severity"], "high")
        self.assertEqual(queue[0]["human_review_required"], "yes")
        self.assertEqual(queue[-1]["review_severity"], "low")

    def test_classifies_core_outcomes_deterministically(self) -> None:
        review_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-tp1", "sig-tp1", "tp1_first"),
                    _candidate_row("cand-tp2", "sig-tp2", "tp2_first"),
                    _candidate_row("cand-sl", "sig-sl", "sl_first"),
                    _candidate_row("cand-not-entered", "sig-no", "not_entered"),
                    _candidate_row("cand-timeout", "sig-timeout", "timeout"),
                    _candidate_row("cand-ambiguous", "sig-ambiguous", "ambiguous"),
                    _candidate_row("cand-no-data", "sig-no-data", "no_ohlcv"),
                    _candidate_row("cand-entry", "sig-entry", "entry_reached"),
                    _candidate_row("cand-invalid", "sig-invalid", "", candidate_status=""),
                ]
            ),
            None,
        )
        self.assertEqual(list(review_df["self_review_label"]), [
            "good",
            "good",
            "wrong",
            "false_alarm",
            "unresolved",
            "ambiguous",
            "no_data",
            "unresolved",
            "invalid",
        ])
        self.assertEqual(list(review_df["tp_accuracy_result"]), [
            "tp1_hit",
            "tp2_hit",
            "sl_before_tp",
            "not_reached",
            "unresolved",
            "unresolved",
            "no_data",
            "unresolved",
            "unresolved",
        ])
        self.assertEqual(list(review_df["position_accuracy_result"]), [
            "good",
            "good",
            "wrong",
            "false_alarm",
            "unresolved",
            "unresolved",
            "no_data",
            "unresolved",
            "unresolved",
        ])
        self.assertEqual(list(review_df["review_bucket"]), [
            "confirmed_useful",
            "confirmed_useful",
            "bad_entry_or_wrong_direction",
            "no_entry_after_alert",
            "unresolved_followup",
            "ambiguous_outcome",
            "data_gap",
            "unresolved_followup",
            "invalid_input",
        ])
        self.assertEqual(list(review_df["review_severity"]), [
            "low",
            "low",
            "high",
            "medium",
            "medium",
            "medium",
            "medium",
            "medium",
            "high",
        ])
        self.assertEqual(list(review_df["human_review_required"]), [
            "no",
            "no",
            "yes",
            "yes",
            "yes",
            "yes",
            "yes",
            "yes",
            "yes",
        ])
        self.assertEqual(list(review_df["improvement_focus"]), [
            "keep_current_logic",
            "keep_current_logic",
            "entry_filter_or_direction_check",
            "alert_threshold_or_entry_reach",
            "wait_for_outcome_or_timeout_rule",
            "outcome_disambiguation",
            "data_coverage",
            "wait_for_outcome_or_timeout_rule",
            "input_schema_or_missing_fields",
        ])
        self.assertEqual(list(review_df["operator_review_hint"]), [
            "方向とTP到達は良好。大きな調整は不要。",
            "方向とTP到達は良好。大きな調整は不要。",
            "SL先行。方向、エントリー位置、SL幅を見直す。",
            "通知後にentry到達なし。早すぎる警告や価格距離を確認する。",
            "結果未確定。追加足またはtimeout条件を確認する。",
            "TP/SL順序が曖昧。足内判定またはデータ粒度を確認する。",
            "OHLCV不足。データ取得範囲と生成タイミングを確認する。",
            "結果未確定。追加足またはtimeout条件を確認する。",
            "入力欠損または未知値。reason_codesを確認する。",
        ])

    def test_summary_includes_new_review_support_counts(self) -> None:
        review_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-good", "sig-good", "tp1_first"),
                    _candidate_row("cand-wrong", "sig-wrong", "sl_first"),
                    _candidate_row("cand-no", "sig-no", "not_entered"),
                ]
            ),
            pd.DataFrame([_signal_row("sig-missed", favorable=True)]),
        )
        summary = summarize_judgment_self_reviews(review_df)
        self.assertEqual(summary["review_bucket_counts"]["confirmed_useful"], 1)
        self.assertEqual(summary["review_bucket_counts"]["bad_entry_or_wrong_direction"], 1)
        self.assertEqual(summary["review_bucket_counts"]["no_entry_after_alert"], 1)
        self.assertEqual(summary["review_bucket_counts"]["missed_opportunity"], 1)
        self.assertEqual(summary["late_rows"], 0)
        self.assertEqual(summary["review_severity_counts"]["high"], 2)
        self.assertEqual(summary["human_review_required_counts"]["yes"], 3)
        self.assertEqual(summary["human_review_required_counts"]["no"], 1)
        self.assertEqual(summary["high_severity_rows"], 2)
        self.assertEqual(summary["human_review_required_rows"], 3)
        self.assertIn("entry_filter_or_direction_check", summary["improvement_focus_counts"])
        self.assertIn("missed_signal_detection", summary["improvement_focus_counts"])
        self.assertIn("good", summary["direction_quality_counts"])
        self.assertIn("weak", summary["execution_gate_quality_counts"])
        self.assertIn("too_shallow", summary["entry_depth_quality_counts"])
        self.assertIn("scenario_invalidated", summary["scenario_lifecycle_result_counts"])
        self.assertIn("not_touched", summary["value_defense_result_counts"])
        digest = build_judgment_self_review_digest(review_df, summary, build_judgment_self_review_queue(review_df))
        self.assertEqual(digest["primary_condition"], "bad_entry_or_wrong_direction")
        self.assertEqual(digest["primary_improvement_focus"], "entry_filter_or_direction_check")
        gate = build_judgment_self_review_change_readiness(summary, digest, build_judgment_self_review_queue(review_df))
        self.assertEqual(gate["change_readiness_status"], "observe_more")
        self.assertEqual(gate["tuning_review_allowed"], "no")

        late_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-late-1", "sig-late-1", "too_late"),
                    _candidate_row("cand-good-1", "sig-good-1", "tp1_first"),
                    _candidate_row("cand-good-2", "sig-good-2", "tp2_first"),
                    _candidate_row("cand-good-3", "sig-good-3", "tp1_first"),
                    _candidate_row("cand-good-4", "sig-good-4", "tp2_first"),
                ]
            ),
            None,
        )
        late_summary = summarize_judgment_self_reviews(late_df)
        late_queue = build_judgment_self_review_queue(late_df)
        late_digest = build_judgment_self_review_digest(late_df, late_summary, late_queue)
        self.assertEqual(late_digest["primary_condition"], "late_signal")
        self.assertEqual(late_summary["late_rows"], 1)
        late_gate = build_judgment_self_review_change_readiness(late_summary, late_digest, late_queue)
        self.assertEqual(late_gate["change_readiness_status"], "human_review_first")

    def test_sl_first_with_shallow_context_marks_entry_depth_too_shallow(self) -> None:
        review_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    {
                        **_candidate_row("cand-shallow", "sig-shallow", "sl_first"),
                        "candidate_type": "active_limit_retest",
                        "entry_mode": "limit_zone_mid",
                        "shallow_retest_zone_low": "61467",
                        "shallow_retest_zone_high": "61555",
                        "value_defense_zone_low": "61280",
                        "value_defense_zone_high": "61350",
                        "lifecycle_state": "shallow_retest_risk",
                    }
                ]
            ),
            None,
        )
        self.assertEqual(review_df.loc[0, "self_review_label"], "wrong")
        self.assertEqual(review_df.loc[0, "entry_depth_quality"], "too_shallow")
        self.assertEqual(review_df.loc[0, "direction_quality"], "wrong")
        self.assertEqual(review_df.loc[0, "scenario_lifecycle_result"], "scenario_invalidated")
        self.assertEqual(review_df.loc[0, "value_defense_result"], "unresolved")

    def test_explicit_value_defense_fields_are_preserved_and_sanitized(self) -> None:
        review_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    {
                        **_candidate_row("cand-vd", "sig-vd", "tp1_first"),
                        "direction_quality": "weak",
                        "execution_gate_quality": "good",
                        "entry_depth_quality": "too_deep",
                        "scenario_lifecycle_result": "reclaim_pending",
                        "value_defense_touched": "yes",
                        "value_defense_zone_low": "61280",
                        "value_defense_zone_high": "61350",
                        "shallow_retest_zone_low": "61467",
                        "shallow_retest_zone_high": "61555",
                        "value_defense_result": "value_entry_validated",
                        "value_defense_review_hint": "OPENAI_API_KEY Gmail smtp send_email <script> fetch( private/order automatic_order_allowed=true",
                    }
                ]
            ),
            None,
        )
        self.assertEqual(review_df.loc[0, "direction_quality"], "weak")
        self.assertEqual(review_df.loc[0, "execution_gate_quality"], "good")
        self.assertEqual(review_df.loc[0, "entry_depth_quality"], "too_deep")
        self.assertEqual(review_df.loc[0, "scenario_lifecycle_result"], "reclaim_pending")
        self.assertEqual(review_df.loc[0, "value_defense_result"], "value_entry_validated")
        self.assertNotIn("OPENAI_API_KEY", review_df.loc[0, "value_defense_review_hint"])

        summary = summarize_judgment_self_reviews(review_df)
        queue = build_judgment_self_review_queue(review_df)
        digest = build_judgment_self_review_digest(review_df, summary, queue)
        gate = build_judgment_self_review_change_readiness(summary, digest, queue)
        metadata = build_judgment_self_review_run_metadata(review_df, summary, digest, gate, queue)
        report, payload = build_judgment_self_review_report(review_df, None, dry_run=True)
        self.assertEqual(queue[0]["direction_quality"], "weak")
        self.assertEqual(queue[0]["entry_depth_quality"], "too_deep")
        self.assertEqual(queue[0]["value_defense_result"], "value_entry_validated")
        self.assertEqual(payload["review_queue"][0]["direction_quality"], "weak")
        self.assertEqual(payload["review_queue"][0]["value_defense_result"], "value_entry_validated")
        self.assertIn("review_queue", payload)
        self.assertIn("review_digest", payload)
        self.assertIn("change_readiness", payload)
        self.assertIn("run_metadata", payload)
        self.assertEqual(payload["report_fingerprint"], payload["run_metadata"]["report_fingerprint"])
        self.assertTrue(str(payload["report_fingerprint"]).startswith("jsr_"))
        self.assertNotIn("OPENAI_API_KEY", report)
        self.assertNotIn("send_email", report)
        self.assertNotIn("Gmail", report)
        self.assertNotIn("smtp", report.lower())
        self.assertNotIn("<script", report.lower())
        self.assertNotIn("fetch(", report.lower())
        self.assertNotIn("private/order", report.lower())
        self.assertNotIn("automatic_order_allowed=true", report.lower())

    def test_run_metadata_produces_stable_fingerprints(self) -> None:
        empty_metadata = build_judgment_self_review_run_metadata(None, None, None, None, None)
        self.assertEqual(empty_metadata["observation_start_jst"], "")
        self.assertEqual(empty_metadata["observation_end_jst"], "")
        self.assertEqual(empty_metadata["observation_row_count"], 0)
        self.assertTrue(str(empty_metadata["report_fingerprint"]).startswith("jsr_"))
        self.assertTrue(str(empty_metadata["digest_fingerprint"]).startswith("jsd_"))
        self.assertTrue(str(empty_metadata["change_readiness_fingerprint"]).startswith("jsc_"))
        self.assertTrue(str(empty_metadata["queue_fingerprint"]).startswith("jsq_"))
        self.assertEqual(empty_metadata["fingerprint_version"], "judgment_self_review_fingerprint.v1")
        self.assertEqual(empty_metadata["safety_boundary"], SAFETY_BOUNDARY)

        review_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-a", "sig-a", "tp1_first"),
                    _candidate_row("cand-b", "sig-b", "tp2_first"),
                ]
            ),
            None,
        )
        review_df.loc[0, "timestamp_jst"] = "2026-07-02T08:30:00+09:00"
        review_df.loc[1, "timestamp_jst"] = "2026-07-02T09:45:00+09:00"
        summary = summarize_judgment_self_reviews(review_df)
        queue = build_judgment_self_review_queue(review_df)
        digest = build_judgment_self_review_digest(review_df, summary, queue)
        gate = build_judgment_self_review_change_readiness(summary, digest, queue)
        metadata = build_judgment_self_review_run_metadata(review_df, summary, digest, gate, queue)
        self.assertEqual(metadata["observation_start_jst"], "2026-07-02T08:30:00+09:00")
        self.assertEqual(metadata["observation_end_jst"], "2026-07-02T09:45:00+09:00")
        self.assertEqual(metadata["observation_row_count"], 2)
        self.assertEqual(metadata["candidate_review_rows"], 2)
        self.assertEqual(metadata["missed_rows"], 0)

        metadata_again = build_judgment_self_review_run_metadata(review_df, summary, digest, gate, queue)
        self.assertEqual(metadata["report_fingerprint"], metadata_again["report_fingerprint"])

        changed_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    _candidate_row("cand-a", "sig-a", "tp1_first"),
                    _candidate_row("cand-b", "sig-b", "sl_first"),
                ]
            ),
            None,
        )
        changed_df.loc[0, "timestamp_jst"] = "2026-07-02T08:30:00+09:00"
        changed_df.loc[1, "timestamp_jst"] = "2026-07-02T09:45:00+09:00"
        changed_summary = summarize_judgment_self_reviews(changed_df)
        changed_queue = build_judgment_self_review_queue(changed_df)
        changed_digest = build_judgment_self_review_digest(changed_df, changed_summary, changed_queue)
        changed_gate = build_judgment_self_review_change_readiness(changed_summary, changed_digest, changed_queue)
        changed_metadata = build_judgment_self_review_run_metadata(changed_df, changed_summary, changed_digest, changed_gate, changed_queue)
        self.assertNotEqual(metadata["report_fingerprint"], changed_metadata["report_fingerprint"])

    def test_missed_opportunity_detection_adds_row_for_favorable_signal_without_candidate(self) -> None:
        review_df = build_judgment_self_review_rows(
            pd.DataFrame([_candidate_row("cand-good", "sig-good", "tp1_first")]),
            pd.DataFrame(
                [
                    _signal_row("sig-good"),
                    _signal_row("sig-missed", favorable=True),
                    _signal_row("sig-neutral", favorable=False),
                ]
            ),
        )

        self.assertIn("missed", set(review_df["self_review_label"]))
        missed_row = review_df.loc[review_df["self_review_label"] == "missed"].iloc[0]
        self.assertEqual(missed_row["source_signal_id"], "sig-missed")
        self.assertEqual(missed_row["tp_accuracy_result"], "missed_without_candidate")
        self.assertEqual(missed_row["position_accuracy_result"], "missed")
        self.assertEqual(missed_row["timing_review"], "missed")

    def test_empty_inputs_produce_zero_count_summary(self) -> None:
        review_df = build_judgment_self_review_rows(None, None)
        summary = summarize_judgment_self_reviews(review_df)

        self.assertTrue(review_df.empty)
        self.assertEqual(summary["total_review_rows"], 0)
        self.assertEqual(summary["candidate_review_rows"], 0)
        self.assertEqual(summary["missed_rows"], 0)
        self.assertEqual(summary["good_rows"], 0)
        self.assertEqual(summary["wrong_rows"], 0)
        self.assertEqual(summary["false_alarm_rows"], 0)
        self.assertEqual(summary["unresolved_rows"], 0)
        self.assertEqual(summary["ambiguous_rows"], 0)
        self.assertEqual(summary["no_data_rows"], 0)
        self.assertEqual(summary["safety_boundary"], SAFETY_BOUNDARY)

    def test_malformed_row_does_not_crash_and_is_marked_invalid(self) -> None:
        review_df = build_judgment_self_review_rows(
            pd.DataFrame(
                [
                    {
                        "candidate_id": "cand-malformed",
                        "source_signal_id": "sig-malformed",
                        "timestamp_jst": "2026-07-02T09:00:00+09:00",
                        "candidate_type": "active_limit_retest",
                        "candidate_status": "",
                        "side": "long",
                        "outcome": "",
                    }
                ]
            ),
            None,
        )
        self.assertEqual(review_df.loc[0, "self_review_label"], "invalid")
        self.assertEqual(review_df.loc[0, "position_accuracy_result"], "unresolved")
        self.assertEqual(review_df.loc[0, "tp_accuracy_result"], "unresolved")
        self.assertIn("missing_outcome", review_df.loc[0, "reason_codes"])
        self.assertEqual(review_df.loc[0, "review_bucket"], "invalid_input")
        self.assertEqual(review_df.loc[0, "review_severity"], "high")
        self.assertEqual(review_df.loc[0, "human_review_required"], "yes")
        self.assertEqual(review_df.loc[0, "improvement_focus"], "input_schema_or_missing_fields")
        self.assertEqual(review_df.loc[0, "operator_review_hint"], "入力欠損または未知値。reason_codesを確認する。")

    def test_report_and_cli_outputs_do_not_leak_sensitive_strings(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            intraperiod_path = _write_csv(
                base_dir / "intraperiod.csv",
                INTRAPERIOD_HEADERS,
                [
                    {
                        **_candidate_row("cand-safe", "sig-safe", "tp1_first"),
                        "candidate_type": "uid_sensitive_12345",
                        "candidate_status": "ready <script> fetch( send_email Gmail smtp OPENAI_API_KEY SMTP_PASSWORD private/order",
                        "first_exit_reason": "private/account/order",
                    },
                    {
                        **_candidate_row("cand-sensitive", "sig-sensitive", "sl_first", side="short"),
                        "candidate_type": "active_breakout uid_sensitive_12345",
                        "candidate_status": "watch",
                        "candidate_id": "cand-sensitive-account-1234",
                        "source_signal_id": "sig-sensitive-account-1234",
                        "mfe_r": "uid-ABC123",
                        "mae_r": "account-1234567890",
                    },
                ],
            )
            signal_path = _write_csv(
                base_dir / "signal.csv",
                SIGNAL_HEADERS,
                [
                    {
                        **_signal_row("sig-missed", favorable=True, sensitive=True),
                        "signal_id": "sig-missed",
                    }
                ],
            )
            output_csv = base_dir / "out" / "report.csv"
            output_md = base_dir / "out" / "report.md"
            report, payload = build_judgment_self_review_report(
                pd.read_csv(intraperiod_path),
                pd.read_csv(signal_path),
                output_csv=output_csv,
                output_md=output_md,
                report_date="20260702",
                dry_run=False,
            )
            self.assertTrue(output_csv.exists())
            self.assertTrue(output_md.exists())
            csv_text = output_csv.read_text(encoding="utf-8")
            md_text = output_md.read_text(encoding="utf-8")
            self.assertIn("Human Review Queue", md_text)
            self.assertIn("Self-Review Digest", md_text)
            self.assertIn("Change Readiness Gate", md_text)
            self.assertIn("Run Metadata", md_text)
            self.assertIn("## Review Buckets", md_text)
            self.assertIn("## Review Severity", md_text)
            self.assertIn("## Human Review Required", md_text)
            self.assertIn("## Improvement Focus", md_text)
            self.assertIn("## Direction Quality", md_text)
            self.assertIn("## Execution Gate Quality", md_text)
            self.assertIn("## Entry Depth Quality", md_text)
            self.assertIn("## Scenario Lifecycle Result", md_text)
            self.assertIn("## Value Defense Result", md_text)
            self.assertIn("review_digest", json.dumps(payload, ensure_ascii=False))
            self.assertIn("change_readiness", json.dumps(payload, ensure_ascii=False))
            self.assertIn("run_metadata", json.dumps(payload, ensure_ascii=False))
            self.assertIn("report_fingerprint", json.dumps(payload, ensure_ascii=False))
            self.assertEqual(payload["review_queue_count"], len(payload["review_queue"]))
            self.assertTrue(payload["review_queue"])
            for text in (report, json.dumps(payload, ensure_ascii=False), csv_text, md_text):
                self.assertNotIn("uid_sensitive_12345", text)
                self.assertNotIn("account-1234567890", text)
                self.assertNotIn("source_uid_hash", text)
                self.assertNotIn("OPENAI_API_KEY", text)
                self.assertNotIn("SMTP_PASSWORD", text)
                self.assertNotIn("send_email", text)
                self.assertNotIn("Gmail", text)
                self.assertNotIn("smtp", text.lower())
                self.assertNotIn("<script", text.lower())
                self.assertNotIn("fetch(", text.lower())
                self.assertNotIn("private/order", text.lower())
                self.assertNotIn("automatic_order_allowed=true", text.lower())

    def test_cli_dry_run_stdout_json_does_not_write_files(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            intraperiod_path = _write_csv(
                base_dir / "intraperiod.csv",
                INTRAPERIOD_HEADERS,
                [_candidate_row("cand-cli", "sig-cli", "tp2_first")],
            )
            signal_path = _write_csv(
                base_dir / "signal.csv",
                SIGNAL_HEADERS,
                [_signal_row("sig-cli-missed", favorable=True)],
            )
            output_csv = base_dir / "out" / "report.csv"
            output_md = base_dir / "out" / "report.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/log_feedback.py",
                    "build-judgment-self-review-report",
                    "--intraperiod-outcomes",
                    str(intraperiod_path),
                    "--signal-outcomes",
                    str(signal_path),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(output_md),
                    "--dry-run",
                    "--stdout-json",
                ],
                cwd=BASE_DIR,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(payload["report_only"])
            self.assertTrue(payload["human_decides_manually"])
            self.assertFalse(output_csv.exists())
            self.assertFalse(output_md.exists())

    def test_cli_non_dry_run_writes_output_files(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            intraperiod_path = _write_csv(
                base_dir / "intraperiod.csv",
                INTRAPERIOD_HEADERS,
                [_candidate_row("cand-cli-write", "sig-cli-write", "tp1_first")],
            )
            output_csv = base_dir / "out" / "report.csv"
            output_md = base_dir / "out" / "report.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/log_feedback.py",
                    "build-judgment-self-review-report",
                    "--intraperiod-outcomes",
                    str(intraperiod_path),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(output_md),
                    "--report-date",
                    "20260702",
                    "--stdout-json",
                ],
                cwd=BASE_DIR,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["report_date"], "20260702")
            self.assertTrue(output_csv.exists())
            self.assertTrue(output_md.exists())
            self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", output_md.read_text(encoding="utf-8"))

    def test_no_external_engine_or_runtime_behavior_is_invoked(self) -> None:
        with mock.patch.object(
            log_feedback,
            "build_post_eval_recommendation_report",
            side_effect=AssertionError("should not call post-eval recommendation engine"),
        ):
            review_df = build_judgment_self_review_rows(
                pd.DataFrame([_candidate_row("cand-safe-2", "sig-safe-2", "tp1_first")]),
                None,
            )
            summary = summarize_judgment_self_reviews(review_df)
            self.assertEqual(summary["good_rows"], 1)
