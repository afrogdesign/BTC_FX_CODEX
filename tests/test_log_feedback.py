from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
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
    _ai_post_review_chart_dir,
    _build_review_chart_svg_path,
    _build_improvement_candidates,
    _merge_review_sources,
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
    main,
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
        self.assertEqual(row["review_action_class"], "watch")
        self.assertEqual(row["review_priority"], "low")
        self.assertEqual(row["next_action"], "同種通知を継続観測する")
        self.assertEqual(row["review_source"], "ai")
        self.assertEqual(row["review_model"], "gpt-test")

    def test_normalize_ai_post_review_infers_action_fields(self) -> None:
        row = _normalize_ai_post_review(
            {
                "user_verdict": "useful_wait",
                "usefulness_1to5": 4,
                "would_trade": "conditional",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "too_close",
                "tf_4h_eval": "good",
                "tf_1h_eval": "mixed",
                "tf_15m_eval": "good",
                "memo": "監視として有効",
            },
            model="gpt-test",
            image_mode="price_map_svg",
        )

        self.assertEqual(row["review_action_class"], "tune_exit")
        self.assertEqual(row["review_priority"], "high")
        self.assertEqual(row["next_action"], "TP1/TP2 を遠めにする候補を検証する")

    def test_build_review_chart_svg_path_persists_snapshot_when_enabled(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            signal_path = base_dir / "logs" / "signals" / "sig_1.json"
            signal_path.parent.mkdir(parents=True, exist_ok=True)
            signal_path.write_text(
                '{"signal_id":"sig_1","current_price":100,"long_setup":{"entry_zone":{"low":95,"high":97},"stop_loss":92,"tp1":103,"tp2":106},"short_setup":{"entry_zone":{"low":103,"high":105},"stop_loss":108,"tp1":99,"tp2":96},"support_zones":[{"low":95,"high":97}],"resistance_zones":[{"low":103,"high":105}],"chart_snapshot":{"candles_4h":[{"timestamp":1775746800000,"open":101,"high":102,"low":99,"close":100}],"candles_1h":[{"timestamp":1775781000000,"open":100,"high":101,"low":99,"close":100}],"candles_15m":[{"timestamp":1775782800000,"open":100,"high":101,"low":99,"close":100}]}}',
                encoding="utf-8",
            )
            temp_dir = base_dir / "tmp"
            temp_dir.mkdir()
            persist_dir = _ai_post_review_chart_dir(base_dir)

            image_path = _build_review_chart_svg_path(base_dir, "sig_1", temp_dir, persist_dir=persist_dir)

            self.assertIsNotNone(image_path)
            assert image_path is not None
            self.assertTrue(image_path.exists())
            saved_path = persist_dir / "sig_1_price_map.svg"
            self.assertTrue(saved_path.exists())
            self.assertIn('class="price-map"', saved_path.read_text(encoding="utf-8"))

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

    def test_improvement_candidates_split_entry_ok_invalid_from_poor_entry(self) -> None:
        rows = [
            {
                "signal_id": f"invalid_{idx}",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "invalid",
                "primary_setup_reason": "rr_below_min" if idx < 3 else "",
                "invalid_reason": "RR不足" if idx == 3 else "",
                "entry_outcome": "poor_entry",
            }
            for idx in range(4)
        ]
        rows.extend(
            {
                "signal_id": f"ready_{idx}",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "ready",
                "entry_outcome": "good_entry",
            }
            for idx in range(3)
        )

        candidates = _build_improvement_candidates(rows, monthly=False, period_rows=rows)
        titles = {item["title"] for item in candidates}
        conflict = next(item for item in candidates if item["title"] == "ENTRY_OK と setup invalid の整合性崩れ")

        self.assertIn("ENTRY_OK と setup invalid の整合性崩れ", titles)
        self.assertNotIn("ENTRY_OK が甘め", titles)
        self.assertIn("rr_below_min=3件", conflict["reason"])
        self.assertIn("RR不足=1件", conflict["reason"])

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
                    "review_action_class": "tune_exit",
                    "review_priority": "medium",
                    "next_action": "TPを調整する",
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
            self.assertEqual(rows[0]["review_action_class"], "tune_exit")
            self.assertEqual(rows[0]["review_priority"], "medium")
            self.assertEqual(rows[0]["next_action"], "TPを調整する")
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

    def test_sync_ai_post_reviews_treats_missing_notification_kind_as_main_for_notified_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "signal_tier"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_missing_kind",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_missing_kind", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            signal_path = base_dir / "logs" / "signals" / "sig_missing_kind.json"
            signal_path.write_text('{"signal_id":"sig_missing_kind","summary_subject":"subject"}', encoding="utf-8")

            ai_result = {
                "user_verdict": "useful_entry",
                "usefulness_1to5": "4",
                "would_trade": "yes",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "good",
                "tf_4h_eval": "good",
                "tf_1h_eval": "good",
                "tf_15m_eval": "mixed",
                "memo": "ok",
            }
            with patch("tools.log_feedback.run_cli_json", return_value=ai_result) as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 2,
                        "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True,
                        "AI_ADVICE_CLI_COMMAND": "dummy-cli",
                    },
                )()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_called_once()
            self.assertEqual(stats["created"], 1)

    def test_main_sync_ai_post_reviews_accepts_missing_max_new_ai_reviews(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "sync-ai-post-reviews"]), patch(
            "tools.log_feedback.sync_ai_post_reviews"
        ) as mocked_sync:
            mocked_sync.return_value = (Path("/tmp/user_reviews.csv"), {"created": 0})

            main()

        mocked_sync.assert_called_once()
        self.assertIsNone(mocked_sync.call_args.kwargs["max_new_reviews"])

    def test_merge_review_sources_prefers_csv_review_rows_over_stale_state(self) -> None:
        merged = _merge_review_sources(
            state_rows=[
                {
                    "signal_id": "sig_1",
                    "review_status": "pending",
                    "review_source": "",
                    "memo": "",
                }
            ],
            note_rows=[],
            review_rows=[
                {
                    "signal_id": "sig_1",
                    "review_status": "done",
                    "review_source": "ai",
                    "memo": "from csv",
                }
            ],
        )

        self.assertEqual(merged["sig_1"]["review_status"], "done")
        self.assertEqual(merged["sig_1"]["review_source"], "ai")
        self.assertEqual(merged["sig_1"]["memo"], "from csv")

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
                timestamp_jst = (datetime.now(timezone(timedelta(hours=9))) - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                )
                writer.writerow(
                    {
                        "signal_id": "sig_report",
                        "timestamp_jst": timestamp_jst,
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
                timestamp_jst = (datetime.now(timezone(timedelta(hours=9))) - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                )
                writer.writerow(
                    {
                        "signal_id": "sig_phase1_only",
                        "timestamp_jst": timestamp_jst,
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

    def test_build_feedback_report_shows_entry_ok_rr_and_ready_blockers(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"

            fieldnames = [
                "signal_id",
                "timestamp_jst",
                "evaluation_status",
                "data_quality_flag",
                "signal_based_MFE_24h",
                "signal_based_MAE_24h",
                "outcome",
                "direction_outcome",
                "entry_outcome",
                "wait_outcome",
                "skip_outcome",
                "tp1_hit_first",
                "was_notified",
                "prelabel",
                "primary_setup_status",
                "primary_setup_reason",
                "primary_setup_side",
                "primary_entry_mid",
                "tp1_price",
                "shadow_tp1_price",
                "shadow_exit_rule_version",
                "invalid_reason",
                "risk_flags",
                "confidence_direction_shadow",
                "confidence_execution_shadow",
                "confidence_wait_shadow",
                "phase1_active",
                "trade_execution_gate",
                "trade_execution_blockers",
                "paper_order_status",
                "tp_eval",
            ]
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                timestamp_jst = (datetime.now(timezone(timedelta(hours=9))) - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                )
                for idx in range(3):
                    writer.writerow(
                        {
                            "signal_id": f"entry_rr_{idx}",
                            "timestamp_jst": timestamp_jst,
                            "evaluation_status": "complete",
                            "data_quality_flag": "ok",
                            "signal_based_MFE_24h": "1.0",
                            "signal_based_MAE_24h": "0.5",
                            "outcome": "win",
                            "direction_outcome": "correct",
                            "entry_outcome": "poor_entry",
                            "wait_outcome": "not_applicable",
                            "skip_outcome": "not_applicable",
                            "tp1_hit_first": "true",
                            "was_notified": "true",
                            "prelabel": "ENTRY_OK",
                            "primary_setup_status": "invalid",
                            "primary_setup_reason": "rr_below_min",
                            "primary_setup_side": "long",
                            "primary_entry_mid": "70000",
                            "tp1_price": "70500",
                            "shadow_tp1_price": "70650",
                            "shadow_exit_rule_version": "phase1_v1_shadow",
                            "invalid_reason": "RR不足",
                            "risk_flags": "lower_liquidity_close,sweep_incomplete",
                            "confidence_direction_shadow": "80",
                            "confidence_execution_shadow": "10",
                            "confidence_wait_shadow": "70",
                            "phase1_active": "false",
                            "trade_execution_gate": "blocked",
                            "trade_execution_blockers": "[\"rr_below_min\", \"execution_shadow_too_low\"]",
                            "paper_order_status": "",
                            "tp_eval": "too_close",
                        }
                    )

            report = build_feedback_report(base_dir=base_dir, period="weekly", shadow_path=shadow_path)

            self.assertIn("ready阻害理由: rr_below_min=3件", report)
            self.assertIn("ENTRY_OK + rr_below_min: 3件 / 平均 execution=10.0 / 平均 wait=70.0", report)
            self.assertIn("ENTRY_OK + rr_below_min の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件", report)
            self.assertIn(
                "position_risk候補: lower_liquidity_close + sweep_incomplete 同居時は ENTRY_OK から RISKY_ENTRY 寄せを検討",
                report,
            )
            self.assertIn("confidence候補: execution<=20 かつ wait>=60 の本通知上位扱いを抑制", report)
            self.assertIn("direction_execution_conflict の主な理由: rr_below_min=3件", report)
            self.assertIn("direction_execution_conflict の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件", report)
            self.assertIn("trade_execution_gate=blocked: 3件", report)
            self.assertIn("主なブロック理由: rr_below_min=3件, execution_shadow_too_low=3件", report)
            self.assertIn("tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件", report)
            self.assertIn("### 改善アクション", report)
            self.assertIn("出口設計を調整=3件", report)
            self.assertIn("重要度: 高=3件", report)
            self.assertIn("TP1/TP2 を遠めにする候補を検証する", report)


if __name__ == "__main__":
    unittest.main()
