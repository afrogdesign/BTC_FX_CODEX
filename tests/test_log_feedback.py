from __future__ import annotations

import csv
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import (
    REVIEW_NOTE_COLUMNS,
    _build_improvement_candidates,
    _load_csv_rows,
    _load_review_note_rows,
    build_shadow_log,
    evaluate_trade_row,
    export_review_queue,
    import_reviews,
)


class LogFeedbackTest(unittest.TestCase):
    def test_evaluate_trade_row_computes_outcomes_and_zone_results(self) -> None:
        trade_row = {
            "signal_id": "20260311_090500",
            "timestamp_utc": "2026-03-11T00:05:00Z",
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "current_price": "100",
            "atr_15m_value": "10",
            "bias": "long",
            "prelabel": "SWEEP_WAIT",
            "signal_tier": "normal",
            "nearest_support_low": "96",
            "nearest_support_high": "99",
            "nearest_resistance_low": "120",
            "nearest_resistance_high": "123",
        }
        signal_ms = int(pd.Timestamp(trade_row["timestamp_utc"]).timestamp() * 1000)
        future_df = pd.DataFrame(
            [
                {"timestamp": signal_ms + 15 * 60 * 1000, "open": 100, "high": 101, "low": 97, "close": 98, "volume": 1},
                {"timestamp": signal_ms + 30 * 60 * 1000, "open": 98, "high": 103, "low": 95, "close": 101, "volume": 1},
                {"timestamp": signal_ms + 60 * 60 * 1000, "open": 101, "high": 106, "low": 100, "close": 104, "volume": 1},
                {"timestamp": signal_ms + 4 * 60 * 60 * 1000, "open": 104, "high": 112, "low": 103, "close": 108, "volume": 1},
                {"timestamp": signal_ms + 24 * 60 * 60 * 1000, "open": 108, "high": 115, "low": 107, "close": 113, "volume": 1},
            ]
        )

        outcome = evaluate_trade_row(trade_row, future_df)

        self.assertEqual(outcome["evaluation_status"], "complete")
        self.assertEqual(outcome["direction_outcome"], "correct")
        self.assertEqual(outcome["wait_outcome"], "wait_was_good")
        self.assertEqual(outcome["signal_based_MFE_12h"], 1.2)
        self.assertEqual(outcome["support_touch_result"], "touched")
        self.assertEqual(outcome["support_hold_result"], "held")
        self.assertEqual(outcome["resistance_touch_result"], "untouched")
        self.assertEqual(outcome["resistance_hold_result"], "untouched")

    def test_import_reviews_reads_done_rows_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            review_note = base_dir / "review.md"
            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| sig_done | 2026-03-11T09:05:00+09:00 | subject | auto | useful_entry | 5 | yes | technical |  | good | done |",
                        "| sig_pending | 2026-03-11T13:05:00+09:00 | subject2 | auto2 |  |  |  |  |  |  | pending |",
                    ]
                ),
                encoding="utf-8",
            )

            reviews_path = import_reviews(base_dir=base_dir, review_note_path=review_note, reviews_path=base_dir / "user_reviews.csv")
            rows = _load_csv_rows(reviews_path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "sig_done")
            self.assertEqual(rows[0]["review_status"], "done")

    def test_export_review_queue_keeps_staged_done_and_adds_pending(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
                    "evaluation_status",
                    "outcome",
                    "direction_outcome",
                    "entry_outcome",
                    "wait_outcome",
                    "skip_outcome",
                    "support_hold_result",
                    "resistance_hold_result",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_new",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "held",
                        "resistance_hold_result": "untouched",
                        "outcome": "win",
                    }
                )

            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_new",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "new subject",
                    }
                )

            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| sig_done | 2026-03-10T09:05:00+09:00 | subject | auto | useful_skip | 4 | no | technical |  | ok | done |",
                    ]
                ),
                encoding="utf-8",
            )

            export_review_queue(
                base_dir=base_dir,
                review_note_path=review_note,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
            )

            rows = _load_review_note_rows(review_note)
            signal_ids = [row["signal_id"] for row in rows]
            self.assertIn("sig_done", signal_ids)
            self.assertIn("sig_new", signal_ids)

    def test_improvement_candidates_have_expected_limits(self) -> None:
        rows = []
        for idx in range(5):
            rows.append(
                {
                    "signal_id": f"entry_{idx}",
                    "prelabel": "ENTRY_OK",
                    "entry_outcome": "poor_entry",
                    "signal_tier": "normal",
                    "direction_outcome": "wrong",
                    "user_verdict": "too_early" if idx < 3 else "",
                    "support_hold_result": "broken",
                }
            )
        for idx in range(5):
            rows.append(
                {
                    "signal_id": f"wait_{idx}",
                    "prelabel": "SWEEP_WAIT",
                    "wait_outcome": "wait_too_strict",
                    "signal_tier": "normal",
                    "direction_outcome": "correct",
                    "user_verdict": "low_value" if idx < 3 else "",
                    "support_hold_result": "broken",
                }
            )
        for idx in range(5):
            rows.append(
                {
                    "signal_id": f"skip_{idx}",
                    "prelabel": "NO_TRADE_CANDIDATE",
                    "skip_outcome": "skip_too_strict",
                    "signal_tier": "strong_ai_confirmed",
                    "direction_outcome": "wrong",
                    "support_hold_result": "broken",
                }
            )

        weekly = _build_improvement_candidates(rows, monthly=False)
        monthly = _build_improvement_candidates(rows, monthly=True)

        self.assertLessEqual(len(weekly), 3)
        self.assertLessEqual(len(monthly), 2)

    def test_build_shadow_log_sets_logic_validated(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
                    "current_price",
                    "bias",
                    "market_regime",
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
                    "notify_reason_codes",
                    "suppress_reason_codes",
                    "data_quality_flag",
                    "data_missing_fields",
                    "risk_flags",
                    "warning_flags",
                    "no_trade_flags",
                    "summary_subject",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_logic",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "current_price": "100",
                        "bias": "long",
                        "market_regime": "uptrend",
                        "phase": "pullback",
                        "long_score": "78",
                        "short_score": "52",
                        "score_gap": "26",
                        "confidence": "80",
                        "top_positive_factors": '["regime_uptrend"]',
                        "top_negative_factors": '["ask_wall_distance"]',
                        "prelabel": "ENTRY_OK",
                        "prelabel_primary_reason": "ask_wall_distance",
                        "location_risk": "12.0",
                        "primary_setup_status": "ready",
                        "invalid_reason": "",
                        "signal_tier": "strong_machine",
                        "ai_decision": "LONG",
                        "ai_confidence": "0.8",
                        "was_notified": "true",
                        "notify_reason_codes": '["status_upgraded"]',
                        "suppress_reason_codes": "[]",
                        "data_quality_flag": "ok",
                        "data_missing_fields": "[]",
                        "risk_flags": "ask_wall_close",
                        "warning_flags": "",
                        "no_trade_flags": "",
                        "summary_subject": "subject",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
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
                    "evaluation_status",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_logic",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "signal_based_MFE_4h": "1.2",
                        "signal_based_MAE_4h": "0.2",
                        "signal_based_MFE_12h": "1.5",
                        "signal_based_MAE_12h": "0.4",
                        "signal_based_MFE_24h": "1.6",
                        "signal_based_MAE_24h": "0.5",
                        "entry_ready_based_MFE_4h": "1.2",
                        "entry_ready_based_MAE_4h": "0.2",
                        "entry_ready_based_MFE_12h": "1.5",
                        "entry_ready_based_MAE_12h": "0.4",
                        "entry_ready_based_MFE_24h": "1.6",
                        "entry_ready_based_MAE_24h": "0.5",
                        "tp1_hit_first": "true",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "held",
                        "resistance_hold_result": "untouched",
                        "evaluation_status": "complete",
                    }
                )

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
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
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_logic",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "subject": "subject",
                        "auto_eval_summary": "summary",
                        "user_verdict": "useful_entry",
                        "usefulness_1to5": "5",
                        "would_trade": "yes",
                        "actual_move_driver": "technical",
                        "logic_validated": "",
                        "memo": "ok",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-03-12T00:00:00Z",
                    }
                )

            shadow_path = build_shadow_log(
                base_dir=base_dir,
                trades_path=trades_path,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
            )
            rows = _load_csv_rows(shadow_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["logic_validated"], "true")
            self.assertEqual(rows[0]["risk_percent_applied"], "")
            self.assertEqual(rows[0]["phase1_active"], "")


if __name__ == "__main__":
    unittest.main()
