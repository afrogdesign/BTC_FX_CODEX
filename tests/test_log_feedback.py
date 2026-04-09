from __future__ import annotations

import csv
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import (
    DEFAULT_REVIEW_FORM,
    DEFAULT_REVIEW_NOTE,
    REVIEW_NOTE_COLUMNS,
    USER_REVIEW_HEADER,
    _build_improvement_candidates,
    _normalize_ai_post_review,
    _load_csv_rows,
    _load_review_note_rows,
    _load_review_state_rows,
    _review_state_path,
    _review_form_path,
    _render_review_form_html,
    build_feedback_report,
    build_shadow_log,
    evaluate_trade_row,
    export_review_queue,
    import_reviews,
    sync_ai_post_reviews,
)


class LogFeedbackTest(unittest.TestCase):
    def test_normalize_ai_post_review_applies_defaults(self) -> None:
        row = _normalize_ai_post_review(
            {
                "user_verdict": "invalid",
                "usefulness_1to5": 9,
                "would_trade": "maybe",
                "actual_move_driver": "other",
                "misleading_entry_like_wording": "",
                "sl_eval": "bad",
                "tp_eval": "",
                "tf_4h_eval": "bad",
                "tf_1h_eval": "",
                "tf_15m_eval": "oops",
                "memo": "メモ",
            },
            model="gpt-test",
            image_mode="price_map_svg",
        )

        self.assertEqual(row["user_verdict"], "low_value")
        self.assertEqual(row["usefulness_1to5"], "1")
        self.assertEqual(row["would_trade"], "no")
        self.assertEqual(row["actual_move_driver"], "unknown")
        self.assertEqual(row["misleading_entry_like_wording"], "no")
        self.assertEqual(row["sl_eval"], "good")
        self.assertEqual(row["tp_eval"], "good")
        self.assertEqual(row["tf_4h_eval"], "good")
        self.assertEqual(row["tf_1h_eval"], "good")
        self.assertEqual(row["tf_15m_eval"], "good")
        self.assertEqual(row["review_source"], "ai")
        self.assertEqual(row["review_model"], "gpt-test")

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
                        "| sig_done | 2026-03-30T09:05:00+09:00 | subject | auto | useful_entry | 5 | yes | technical | good | done |",
                        "| sig_pending | 2026-03-30T13:05:00+09:00 | subject2 | auto2 |  |  |  |  |  | pending |",
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
                        "timestamp_jst": "2026-03-30T09:05:00+09:00",
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
                        "timestamp_jst": "2026-03-30T09:05:00+09:00",
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
                        "| sig_done | 2026-03-30T07:05:00+09:00 | subject | auto | useful_skip | 4 | no | technical | ok | done |",
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

            rows = _load_review_state_rows(_review_state_path(base_dir))
            signal_ids = [row["signal_id"] for row in rows]
            self.assertIn("sig_done", signal_ids)
            self.assertIn("sig_new", signal_ids)

    def test_review_form_markdown_does_not_duplicate_table_header(self) -> None:
        row = {column: "" for column in REVIEW_NOTE_COLUMNS}
        row.update(
            {
                "signal_id": "sig_form",
                "timestamp_jst": "2026-03-30T09:05:00+09:00",
                "subject": "subject",
                "auto_eval_summary": "auto",
                "bias": "long",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "ready",
                "signal_tier": "strong_machine",
                "notify_reason": '["status_upgraded"]',
                "evaluation_status": "complete",
                "confidence_direction_shadow": "88",
                "confidence_execution_shadow": "63",
                "confidence_wait_shadow": "24",
                "review_status": "pending",
            }
        )

        html = _render_review_form_html([row], Path("/tmp/review.md"))

        self.assertNotIn("| signal_id |", html)
        self.assertIn("今の確認軸", html)
        self.assertIn("direction_strength", html)
        self.assertIn("notify_reason", html)
        self.assertIn("localStorage", html)
        self.assertIn("restoreDraft()", html)
        self.assertIn("draft-status", html)
        self.assertIn("getDraftStorage()", html)
        self.assertIn("renderCards();\n    restoreDraft();\n    renderCards();", html)
        self.assertIn("通知 1", html)
        self.assertIn(">subject<", html)
        self.assertIn("この通知、役に立った？", html)
        self.assertIn("レビュー進捗", html)
        self.assertIn("完了にする", html)
        self.assertIn("saveToServer()", html)
        self.assertIn("reloadFromServer()", html)
        self.assertIn("03/30 09:05", html)
        self.assertIn("ロング寄り", html)
        self.assertIn("2026-03-30 05:05 JST 以降の通知だけを見る", html)
        self.assertNotIn("??", html)
        self.assertNotIn("replaceAll", html)
        self.assertIn("syncRowsFromDom()", html)
        self.assertIn("bindSelectHandlers()", html)
        self.assertIn("保存先", html)
        self.assertNotIn("Markdownをコピー", html)

    def test_import_reviews_ignores_rows_before_review_cutoff(self) -> None:
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
                        "| old_sig | 2026-03-30T05:04:00+09:00 | old subject | auto | useful_entry | 5 | yes | technical | old | done |",
                        "| new_sig | 2026-03-30T05:05:00+09:00 | new subject | auto | useful_wait | 4 | no | macro | new | done |",
                    ]
                ),
                encoding="utf-8",
            )

            reviews_path = import_reviews(base_dir=base_dir, review_note_path=review_note, reviews_path=base_dir / "user_reviews.csv")
            rows = _load_csv_rows(reviews_path)

            self.assertEqual([row["signal_id"] for row in rows], ["new_sig"])

    def test_default_review_form_path_uses_review_note_sibling(self) -> None:
        self.assertEqual(_review_form_path(DEFAULT_REVIEW_NOTE), DEFAULT_REVIEW_FORM)

    def test_export_review_queue_includes_recent_notified_trade_without_complete_outcome(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "evaluation_status"])
                writer.writeheader()

            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "was_notified",
                        "summary_subject",
                        "bias",
                        "prelabel",
                        "primary_setup_status",
                        "signal_tier",
                        "notify_reason_codes",
                        "data_quality_flag",
                        "confidence_direction_shadow",
                        "confidence_execution_shadow",
                        "confidence_wait_shadow",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_recent",
                        "timestamp_jst": "2026-03-30T05:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "recent subject",
                        "bias": "short",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "ready",
                        "signal_tier": "normal",
                        "notify_reason_codes": '["status_upgraded"]',
                        "confidence_direction_shadow": "71",
                        "confidence_execution_shadow": "44",
                        "confidence_wait_shadow": "22",
                    }
                )

            export_review_queue(
                base_dir=base_dir,
                review_note_path=review_note,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
            )

            rows = _load_review_state_rows(_review_state_path(base_dir))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "sig_recent")
            self.assertIn("事後評価待ち", rows[0]["auto_eval_summary"])

    def test_export_review_queue_hides_old_rows_from_note_and_form(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "evaluation_status"])
                writer.writeheader()

            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject"])
                writer.writeheader()

            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| old_sig | 2026-03-30T05:04:00+09:00 | old subject | auto | useful_entry | 5 | yes | technical | old | done |",
                        "| new_sig | 2026-03-30T05:05:00+09:00 | new subject | auto | useful_wait | 4 | no | macro | new | done |",
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

            note_text = review_note.read_text(encoding="utf-8")
            form_text = _review_form_path(review_note).read_text(encoding="utf-8")

            self.assertNotIn("old_sig", note_text)
            self.assertIn("new subject", note_text)
            self.assertNotIn("old_sig", form_text)
            self.assertIn("new_sig", form_text)

    def test_load_review_note_rows_ignores_single_header_and_keeps_real_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            review_note = Path(tmpdir) / "review.md"
            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| sig_form | 2026-03-30T09:05:00+09:00 | subject | auto |  |  |  |  |  | pending |",
                    ]
                ),
                encoding="utf-8",
            )

            rows = _load_review_note_rows(review_note)

            self.assertEqual([row["signal_id"] for row in rows], ["sig_form"])
            self.assertNotIn("signal_id", [row["signal_id"] for row in rows])

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

    def test_improvement_candidates_include_sl_tp_feedback(self) -> None:
        rows = [
            {"signal_id": f"tp_close_{idx}", "tp_eval": "too_close", "sl_eval": "good"}
            for idx in range(4)
        ] + [
            {"signal_id": f"sl_tight_{idx}", "tp_eval": "good", "sl_eval": "too_tight"}
            for idx in range(4)
        ] + [
            {"signal_id": f"filler_{idx}", "tp_eval": "good", "sl_eval": "good"}
            for idx in range(2)
        ]

        candidates = _build_improvement_candidates(rows, monthly=False)
        titles = {item["title"] for item in candidates}

        self.assertIn("TP が近すぎるケースが多い", titles)
        self.assertIn("SL が狭すぎるケースが多い", titles)

    def test_improvement_candidates_include_tf15_feedback(self) -> None:
        rows = [
            {"signal_id": f"tf_bad_{idx}", "tf_15m_eval": "poor"}
            for idx in range(4)
        ] + [
            {"signal_id": f"tf_good_{idx}", "tf_15m_eval": "good"}
            for idx in range(2)
        ]

        candidates = _build_improvement_candidates(rows, monthly=False)
        titles = {item["title"] for item in candidates}

        self.assertIn("15分足の執行価格精度が弱い", titles)

    def test_sync_ai_post_reviews_writes_ai_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_ai",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_ai", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            (base_dir / "logs" / "signals" / "sig_ai.json").write_text(
                '{"signal_id":"sig_ai","summary_subject":"subject","current_price":100,"long_setup":{"status":"watch","entry_zone":{"low":99,"high":101},"stop_loss":97,"tp1":104,"tp2":106},"short_setup":{"status":"invalid","entry_zone":{"low":102,"high":103},"stop_loss":104,"tp1":98,"tp2":96},"support_zones":[],"resistance_zones":[],"chart_snapshot":{"intervals":["4h","1h","15m"],"candles_4h":[{"timestamp":1,"open":98,"high":102,"low":96,"close":100.5}],"candles_1h":[{"timestamp":1,"open":99,"high":101,"low":98,"close":100.2}],"candles_15m":[{"timestamp":1,"open":100,"high":101,"low":99,"close":100.5}]}}',
                encoding="utf-8",
            )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg, patch("tools.log_feedback._build_review_chart_svg_path", return_value=None):
                mocked_cli.return_value = {
                    "user_verdict": "useful_wait",
                    "usefulness_1to5": 4,
                    "would_trade": "conditional",
                    "actual_move_driver": "technical",
                    "misleading_entry_like_wording": "no",
                    "sl_eval": "good",
                    "tp_eval": "too_far",
                    "tf_4h_eval": "good",
                    "tf_1h_eval": "mixed",
                    "tf_15m_eval": "poor",
                    "memo": "監視として有効",
                }
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {"AI_ADVICE_CLI_COMMAND": "echo", "OPENAI_ADVICE_MODEL": "gpt-test", "AI_TIMEOUT_SEC": 30},
                )()

                sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                )

            rows = _load_csv_rows(reviews_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["review_source"], "ai")
            self.assertEqual(rows[0]["sl_eval"], "good")
            self.assertEqual(rows[0]["tp_eval"], "too_far")
            self.assertEqual(rows[0]["tf_4h_eval"], "good")
            self.assertEqual(rows[0]["tf_1h_eval"], "mixed")
            self.assertEqual(rows[0]["tf_15m_eval"], "poor")
            self.assertEqual(rows[0]["logic_validated"], "true")

    def test_sync_ai_post_reviews_reuses_snapshot_without_cli(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "review" / "ai_post_reviews").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_cached",
                        "timestamp_jst": "2026-04-10T02:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "cached subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_cached", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            snapshot_path = base_dir / "logs" / "review" / "ai_post_reviews" / "sig_cached.json"
            snapshot_path.write_text(
                """{
  "signal_id": "sig_cached",
  "review": {
    "signal_id": "sig_cached",
    "timestamp_jst": "2026-04-10T02:05:00+09:00",
    "subject": "cached subject",
    "auto_eval_summary": "summary",
    "user_verdict": "useful_wait",
    "usefulness_1to5": "4",
    "would_trade": "no",
    "actual_move_driver": "technical",
    "misleading_entry_like_wording": "no",
    "logic_validated": "true",
    "sl_eval": "good",
    "tp_eval": "good",
    "tf_4h_eval": "good",
    "tf_1h_eval": "mixed",
    "tf_15m_eval": "poor",
    "review_source": "ai",
    "review_model": "gpt-test",
    "review_image_mode": "price_map_svg",
    "review_variant": "ai_post_review_v1",
    "memo": "cached",
    "review_status": "done",
    "reviewed_at_utc": "2026-04-10T00:00:00Z"
  }
}""",
                encoding="utf-8",
            )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type("Cfg", (), {})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=1,
                )

            mocked_cli.assert_not_called()
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["review_source"], "ai")
            self.assertEqual(rows[0]["tf_15m_eval"], "poor")
            self.assertEqual(stats["reused"], 1)

    def test_sync_ai_post_reviews_skips_existing_ai_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_ai_done",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_ai_done", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_ai_done",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "subject": "subject",
                        "auto_eval_summary": "summary",
                        "user_verdict": "useful_wait",
                        "usefulness_1to5": "4",
                        "would_trade": "no",
                        "actual_move_driver": "technical",
                        "misleading_entry_like_wording": "no",
                        "logic_validated": "true",
                        "sl_eval": "good",
                        "tp_eval": "good",
                        "tf_4h_eval": "good",
                        "tf_1h_eval": "good",
                        "tf_15m_eval": "good",
                        "review_source": "ai",
                        "review_model": "gpt-test",
                        "review_image_mode": "price_map_svg",
                        "review_variant": "ai_post_review_v1",
                        "memo": "done",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-04-10T00:00:00Z",
                    }
                )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type("Cfg", (), {})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=1,
                )

            mocked_cli.assert_not_called()
            self.assertEqual(stats["skipped_existing_ai"], 1)

    def test_sync_ai_post_reviews_respects_daily_cap(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_today_cap",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_today_cap", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            today_utc = "2026-04-10T00:00:00Z"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "already_today",
                        "review_source": "ai",
                        "review_variant": "ai_post_review_v1",
                        "reviewed_at_utc": today_utc,
                    }
                )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg, patch("tools.log_feedback._reviewed_on_jst", return_value=True):
                mocked_cfg.return_value = type("Cfg", (), {"AI_POST_REVIEW_DAILY_MAX": 1, "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_not_called()
            self.assertEqual(stats["already_reviewed_today"], 1)
            self.assertEqual(stats["skipped_daily_cap"], 1)

    def test_sync_ai_post_reviews_filters_attention_when_main_only_enabled(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_attention",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "attention",
                        "signal_tier": "strong_ai_confirmed",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_attention", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type("Cfg", (), {"AI_POST_REVIEW_DAILY_MAX": 2, "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_not_called()
            self.assertEqual(stats["skipped_priority_filter"], 1)

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

    def test_build_feedback_report_starts_with_human_summary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"

            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "evaluation_status",
                        "data_quality_flag",
                        "signal_based_MFE_24h",
                        "signal_based_MAE_24h",
                        "entry_ready_based_MFE_24h",
                        "entry_ready_based_MAE_24h",
                        "outcome",
                        "direction_outcome",
                        "entry_outcome",
                        "wait_outcome",
                        "skip_outcome",
                        "support_hold_result",
                        "resistance_hold_result",
                        "tp1_hit_first",
                        "was_notified",
                        "user_verdict",
                        "usefulness_1to5",
                        "actual_move_driver",
                        "prelabel",
                        "primary_setup_status",
                        "signal_tier",
                        "bias",
                        "regime",
                        "risk_flags",
                        "phase1_active",
                        "max_size_capped",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_report",
                        "timestamp_jst": "2026-04-09T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.2",
                        "signal_based_MAE_24h": "0.4",
                        "entry_ready_based_MFE_24h": "1.0",
                        "entry_ready_based_MAE_24h": "0.3",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "not_applicable",
                        "wait_outcome": "wait_was_good",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "untouched",
                        "resistance_hold_result": "held",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "user_verdict": "useful_wait",
                        "usefulness_1to5": "4",
                        "actual_move_driver": "technical",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "ready",
                        "signal_tier": "normal",
                        "bias": "short",
                        "regime": "downtrend",
                        "risk_flags": "",
                        "phase1_active": "true",
                        "max_size_capped": "false",
                        "outcome": "win",
                    }
                )

            report = build_feedback_report(base_dir=base_dir, period="weekly", shadow_path=shadow_path)

            self.assertIn("## 1. まず結論", report)
            self.assertIn("Phase 1 判定では ready=1 件、phase1_active=true=1 件です。", report)
            self.assertIn("判定: Phase 1 の本有効確認を進めてよい", report)
            self.assertIn("## 3. Phase 1 判定サマリー", report)
            self.assertIn("## 4. 人のレビュー要約", report)
            self.assertIn("待つ判断に使えた", report)
            self.assertIn("平均の役立ち度", report)
            self.assertIn("`primary_setup_status=ready` 件数: 1", report)
            self.assertIn("`phase1_active=true` 件数: 1", report)

    def test_build_feedback_report_keeps_phase1_summary_without_reviews(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"

            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "evaluation_status",
                        "data_quality_flag",
                        "signal_based_MFE_24h",
                        "signal_based_MAE_24h",
                        "entry_ready_based_MFE_24h",
                        "entry_ready_based_MAE_24h",
                        "outcome",
                        "direction_outcome",
                        "entry_outcome",
                        "wait_outcome",
                        "skip_outcome",
                        "support_hold_result",
                        "resistance_hold_result",
                        "tp1_hit_first",
                        "was_notified",
                        "user_verdict",
                        "usefulness_1to5",
                        "actual_move_driver",
                        "prelabel",
                        "primary_setup_status",
                        "signal_tier",
                        "bias",
                        "regime",
                        "risk_flags",
                        "phase1_active",
                        "max_size_capped",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_phase1_only",
                        "timestamp_jst": "2026-04-09T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.2",
                        "signal_based_MAE_24h": "0.4",
                        "entry_ready_based_MFE_24h": "1.0",
                        "entry_ready_based_MAE_24h": "0.3",
                        "outcome": "expired",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "untouched",
                        "resistance_hold_result": "held",
                        "tp1_hit_first": "false",
                        "was_notified": "true",
                        "user_verdict": "",
                        "usefulness_1to5": "",
                        "actual_move_driver": "",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "ready",
                        "signal_tier": "normal",
                        "bias": "long",
                        "regime": "range",
                        "risk_flags": "",
                        "phase1_active": "true",
                        "max_size_capped": "true",
                    }
                )

            report = build_feedback_report(base_dir=base_dir, period="weekly", shadow_path=shadow_path)

            self.assertIn("## 3. Phase 1 判定サマリー", report)
            self.assertIn("判定: Phase 1 の本有効確認を進めてよい", report)
            self.assertIn("直近の観測対象:", report)
            self.assertIn("sig_phase1_only / setup=ready / phase1_active=true / outcome=expired", report)
            self.assertIn("TP1 到達率: 0.0%", report)
            self.assertIn("`tp1_hit_first=false` 率: 100.0%", report)
            self.assertIn("`expired` 率: 100.0%", report)
            self.assertIn("`max_size_capped` 発生率: 100.0%", report)
            self.assertIn("## 4. 人のレビュー要約", report)
            self.assertIn("完了レビューはまだありません", report)


if __name__ == "__main__":
    unittest.main()
