from __future__ import annotations

import csv
import json
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
    SHADOW_HEADER,
    USER_REVIEW_HEADER,
    _ai_review_health_summary,
    _ai_post_review_chart_dir,
    _build_review_chart_svg_path,
    _build_improvement_candidates,
    _load_latest_ai_sync_stats,
    _merge_review_sources,
    _normalize_ai_post_review,
    _load_csv_rows,
    _load_review_note_rows,
    _load_review_state_rows,
    _normalize_ai_review_row,
    _review_state_path,
    _review_form_path,
    _render_review_form_html,
    backfill_ai_post_review_v2,
    build_current_setup_comparison_report,
    build_failed_breakout_down_reversal_report,
    build_feedback_report,
    build_market_map_effectiveness_report,
    build_market_map_readiness_report,
    build_observation_paper_orders,
    build_paper_opportunity_diagnostics_report,
    build_paper_positions,
    build_phase1b_lite_paper_orders,
    build_operational_focus_report,
    build_phase1b_promotion_report,
    build_report_hub,
    build_relaxation_candidates_report,
    build_shadow_log,
    evaluate_trade_row,
    export_review_queue,
    import_reviews,
    main,
    refresh_standard_setup_comparison_reports,
    sync_ai_post_reviews,
)
from src.storage.csv_logger import OBSERVATION_PAPER_ORDER_HEADER, PAPER_POSITION_HEADER, PHASE1B_LITE_PAPER_ORDER_HEADER


class LogFeedbackTest(unittest.TestCase):
    def test_build_report_hub_lists_latest_previous_and_warnings(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            reports_dir = base_dir / "運用資料" / "reports"
            analysis_dir = reports_dir / "analysis"
            archive_daily = reports_dir / "archive" / "daily" / "2026-05"
            archive_analysis = reports_dir / "archive" / "analysis"
            legacy_v23 = reports_dir / "Ver02.3のレポート"
            legacy_old = reports_dir / "Ver02までのレポート"
            for path in [analysis_dir, archive_daily, archive_analysis, legacy_v23, legacy_old]:
                path.mkdir(parents=True, exist_ok=True)

            (reports_dir / "feedback_daily_sync_20260526.md").write_text("# daily 26\n", encoding="utf-8")
            (archive_daily / "feedback_daily_sync_20260525.md").write_text("# daily 25\n", encoding="utf-8")
            (analysis_dir / "market_map_effectiveness_20260526.md").write_text("# map 26\n", encoding="utf-8")
            (archive_analysis / "market_map_effectiveness_20260520.md").write_text("# map 20\n", encoding="utf-8")
            (analysis_dir / "operational_focus_20260526.md").write_text("# focus 26\n", encoding="utf-8")
            (analysis_dir / "paper_opportunity_diagnostics_20260526.md").write_text("# paper 26\n", encoding="utf-8")
            (analysis_dir / "rr_to_confidence.md").write_text("# rr confidence\n", encoding="utf-8")
            (legacy_v23 / "README.md").write_text("# legacy v23\n", encoding="utf-8")
            (legacy_old / "README.md").write_text("# legacy old\n", encoding="utf-8")

            report = build_report_hub(base_dir=base_dir)

            self.assertIn("feedback_daily_sync_20260526.md", report)
            self.assertIn("feedback_daily_sync_20260525.md", report)
            self.assertIn("storage: `active`", report)
            self.assertIn("archive/daily/2026-05/feedback_daily_sync_20260525.md", report)
            self.assertIn("rr_to_confidence.md", report)
            self.assertIn("missing: `paper_entry_sl_wait_redesign`", report)
            self.assertIn("legacy", report)
            self.assertTrue((reports_dir / "report_hub_latest.md").exists())

    def test_build_paper_positions_upserts_without_destroying_existing_state(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            trades_path = logs_csv / "shadow_log.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "opportunity_gate",
                        "opportunity_type",
                        "primary_setup_status",
                        "primary_setup_side",
                        "current_price",
                        "primary_entry_mid",
                        "primary_stop_loss",
                        "shadow_tp1_price",
                        "shadow_tp2_price",
                        "shadow_timeout_hours",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_existing",
                        "timestamp_jst": "2026-05-18T10:00:00+09:00",
                        "opportunity_gate": "pass",
                        "opportunity_type": "test_type",
                        "primary_setup_status": "watch",
                        "primary_setup_side": "long",
                        "current_price": "100",
                        "primary_entry_mid": "99",
                        "primary_stop_loss": "97",
                        "shadow_tp1_price": "103",
                        "shadow_tp2_price": "105",
                        "shadow_timeout_hours": "12",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "sig_new",
                        "timestamp_jst": "2026-05-18T11:00:00+09:00",
                        "opportunity_gate": "pass",
                        "opportunity_type": "new_type",
                        "primary_setup_status": "ready",
                        "primary_setup_side": "short",
                        "current_price": "100",
                        "primary_entry_mid": "100",
                        "primary_stop_loss": "102",
                        "shadow_tp1_price": "98",
                        "shadow_tp2_price": "96",
                        "shadow_timeout_hours": "12",
                    }
                )

            output_path = logs_csv / "paper_positions.csv"
            with output_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_existing",
                        "timestamp_jst": "2026-05-18T10:00:00+09:00",
                        "position_status": "closed",
                        "exit_status": "sl_hit",
                        "realized_r": "-1",
                    }
                )
                writer.writerow(row)

            with patch("tools.log_feedback.load_config", return_value=object()), patch(
                "tools.log_feedback._fetch_future_15m_df",
                return_value=pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"]),
            ):
                build_paper_positions(base_dir=base_dir, trades_path=trades_path, output_path=output_path)

            rows = {row["signal_id"]: row for row in _load_csv_rows(output_path)}
            self.assertEqual(rows["sig_existing"]["position_status"], "closed")
            self.assertEqual(rows["sig_existing"]["exit_status"], "sl_hit")
            self.assertEqual(rows["sig_new"]["position_status"], "opened")

    def test_build_paper_positions_extends_legacy_header(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            trades_path = logs_csv / "shadow_log.csv"
            trades_path.write_text("signal_id,timestamp_jst,opportunity_gate\n", encoding="utf-8")
            output_path = logs_csv / "paper_positions.csv"
            output_path.write_text("signal_id,timestamp_jst,position_status\nlegacy,2026-05-18T10:00:00+09:00,pending\n", encoding="utf-8")

            with patch("tools.log_feedback.load_config", return_value=object()), patch(
                "tools.log_feedback._fetch_future_15m_df",
                return_value=pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"]),
            ):
                build_paper_positions(base_dir=base_dir, trades_path=trades_path, output_path=output_path)

            header = output_path.read_text(encoding="utf-8").splitlines()[0].split(",")
            self.assertIn("opened_at_jst", header)
            self.assertIn("realized_r", header)
            rows = _load_csv_rows(output_path)
            self.assertEqual(rows[0]["signal_id"], "legacy")

    def test_feedback_report_includes_paper_position_execution_summary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                row = {field: "" for field in SHADOW_HEADER}
                row.update(
                    {
                        "signal_id": "sig_closed",
                        "timestamp_jst": datetime.now(timezone.utc).astimezone().isoformat(),
                        "evaluation_status": "complete",
                        "opportunity_gate": "pass",
                        "opportunity_type": "confidence_watch_learning",
                    }
                )
                writer.writerow(row)
            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_closed",
                        "timestamp_jst": datetime.now(timezone.utc).astimezone().isoformat(),
                        "position_status": "closed",
                        "opportunity_type": "confidence_watch_learning",
                        "exit_status": "tp2_hit",
                        "realized_r": "2.0",
                    }
                )
                writer.writerow(row)
            paper_orders_path = logs_csv / "paper_orders.csv"
            paper_orders_path.write_text("signal_id\n", encoding="utf-8")
            observation_path = logs_csv / "observation_paper_orders.csv"
            observation_path.write_text(",".join(OBSERVATION_PAPER_ORDER_HEADER) + "\n", encoding="utf-8")
            lite_path = logs_csv / "phase1b_lite_paper_orders.csv"
            lite_path.write_text(",".join(PHASE1B_LITE_PAPER_ORDER_HEADER) + "\n", encoding="utf-8")

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                paper_orders_path=paper_orders_path,
                observation_paper_orders_path=observation_path,
                phase1b_lite_paper_orders_path=lite_path,
                paper_positions_path=paper_positions_path,
                ai_health_summary={},
            )

            self.assertIn("紙ポジション終了状態: tp2_hit=1件", report)
            self.assertIn("opportunity_type 別 closed", report)
            self.assertIn("平均R=2.00", report)

    def test_paper_opportunity_diagnostics_report_groups_market_map_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                row = {field: "" for field in SHADOW_HEADER}
                row.update(
                    {
                        "signal_id": "sig_sl",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "market_map_flags": "support_to_resistance_flip,trend_flip_confirmed_down",
                    }
                )
                writer.writerow(row)
            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_sl",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                        "side": "short",
                        "exit_status": "sl_hit",
                        "realized_r": "-1.0",
                        "primary_setup_reason": "confidence_below_min",
                        "market_map_flags": "support_to_resistance_flip,trend_flip_confirmed_down",
                        "confidence_direction_shadow": "64",
                        "confidence_execution_shadow": "23",
                        "confidence_wait_shadow": "59.2",
                    }
                )
                writer.writerow(row)

            report = build_paper_opportunity_diagnostics_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-05-21",
                date_to="2026-05-21",
            )

            self.assertIn("紙実行候補 entry/wait 診断", report)
            self.assertIn("closed: 1件 / opportunity_type: market_map_opportunity=1件", report)
            self.assertIn("market_map_opportunity: 1件", report)
            self.assertIn("support_to_resistance_flip: 1件", report)
            self.assertIn("sig_sl: sl_hit", report)

    def test_paper_opportunity_diagnostics_report_classifies_sl_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                for signal_id, flags in [
                    ("sig_long_wait", "trend_flip_confirmed_up,resistance_to_support_flip"),
                    ("sig_sweep", "support_to_resistance_flip"),
                ]:
                    row = {field: "" for field in SHADOW_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": "2026-05-21T10:00:00+09:00",
                            "market_map_flags": flags,
                            "review_source": "ai",
                            "actual_move_driver": "technical",
                        }
                    )
                    if signal_id == "sig_long_wait":
                        row["user_verdict"] = "too_early"
                        row["sl_eval"] = "too_tight"
                        row["tf_15m_eval"] = "poor"
                        row["logic_validated"] = "false"
                    else:
                        row["user_verdict"] = "useful_wait"
                        row["sl_eval"] = "good"
                        row["tf_15m_eval"] = "good"
                        row["logic_validated"] = "true"
                    writer.writerow(row)

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_long_wait",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:trend_flip_confirmed_up"]',
                        "side": "long",
                        "exit_status": "sl_hit",
                        "realized_r": "-1.0",
                        "rr_estimate": "1.2",
                        "mfe_atr": "0.10",
                        "mae_atr": "1.40",
                        "primary_setup_reason": "confidence_below_min",
                        "market_map_flags": "trend_flip_confirmed_up,resistance_to_support_flip",
                        "confidence_direction_shadow": "55",
                        "confidence_execution_shadow": "18",
                        "confidence_wait_shadow": "72",
                        "prelabel": "ENTRY_OK",
                    }
                )
                writer.writerow(row)
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_sweep",
                        "timestamp_jst": "2026-05-21T11:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                        "side": "short",
                        "exit_status": "missed_opportunity",
                        "realized_r": "1.3",
                        "rr_estimate": "1.5",
                        "mfe_atr": "1.60",
                        "mae_atr": "0.40",
                        "primary_setup_reason": "near_entry_zone_waiting_trigger",
                        "market_map_flags": "support_to_resistance_flip",
                        "confidence_direction_shadow": "70",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "76.8",
                        "prelabel": "SWEEP_WAIT",
                    }
                )
                writer.writerow(row)

            report = build_paper_opportunity_diagnostics_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-05-21",
                date_to="2026-05-21",
            )

            self.assertIn("紙実行候補 entry/wait 診断", report)
            self.assertIn("## SL失敗分類", report)
            self.assertIn("trend_flip_long_sl: 1件", report)
            self.assertIn("## AI事後評価サマリー", report)
            self.assertIn("review coverage: 2/2件", report)
            self.assertIn("suppress_long_high_wait", report)
            self.assertIn("suppress_trend_flip_up_strong", report)
            self.assertIn("require_execution_for_high_wait", report)
            self.assertIn("delay_entry_on_sweep_wait", report)

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
        self.assertIn("AI 評価を主系として使い", html)
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
            self.assertIn("AI事後評価の進捗を確認", note_text)
            self.assertNotIn("old_sig", form_text)
            self.assertIn("new_sig", form_text)

    def test_export_review_queue_note_is_ai_first_and_lists_human_overrides_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"
            logs_review = base_dir / "logs" / "review"
            logs_review.mkdir(parents=True, exist_ok=True)

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "evaluation_status"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_human", "timestamp_jst": "2026-03-30T09:05:00+09:00", "evaluation_status": "complete"})
                writer.writerow({"signal_id": "sig_ai", "timestamp_jst": "2026-03-30T10:05:00+09:00", "evaluation_status": "complete"})

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
                        "confidence_direction_shadow",
                        "confidence_execution_shadow",
                        "confidence_wait_shadow",
                    ],
                )
                writer.writeheader()
                writer.writerow({"signal_id": "sig_human", "timestamp_jst": "2026-03-30T09:05:00+09:00", "was_notified": "true", "summary_subject": "human subject", "bias": "long", "prelabel": "ENTRY_OK", "primary_setup_status": "ready", "signal_tier": "normal", "notify_reason_codes": '["status_upgraded"]', "confidence_direction_shadow": "70", "confidence_execution_shadow": "45", "confidence_wait_shadow": "20"})
                writer.writerow({"signal_id": "sig_ai", "timestamp_jst": "2026-03-30T10:05:00+09:00", "was_notified": "true", "summary_subject": "ai subject", "bias": "short", "prelabel": "SWEEP_WAIT", "primary_setup_status": "watch", "signal_tier": "normal", "notify_reason_codes": '["attention_bias_changed"]', "confidence_direction_shadow": "60", "confidence_execution_shadow": "25", "confidence_wait_shadow": "70"})

            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_human",
                        "timestamp_jst": "2026-03-30T09:05:00+09:00",
                        "subject": "human subject",
                        "auto_eval_summary": "auto",
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
                        "review_source": "human_override",
                        "review_model": "",
                        "review_image_mode": "",
                        "review_variant": "",
                        "review_action_class": "watch",
                        "review_priority": "medium",
                        "next_action": "watch",
                        "memo": "manual",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-03-30T00:30:00Z",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "sig_ai",
                        "timestamp_jst": "2026-03-30T10:05:00+09:00",
                        "subject": "ai subject",
                        "auto_eval_summary": "auto",
                        "user_verdict": "too_early",
                        "usefulness_1to5": "2",
                        "would_trade": "conditional",
                        "actual_move_driver": "technical",
                        "misleading_entry_like_wording": "yes",
                        "logic_validated": "false",
                        "sl_eval": "too_tight",
                        "tp_eval": "good",
                        "tf_4h_eval": "good",
                        "tf_1h_eval": "mixed",
                        "tf_15m_eval": "poor",
                        "review_source": "ai",
                        "review_model": "gpt-test",
                        "review_image_mode": "price_map_svg",
                        "review_variant": "ai_post_review_v2",
                        "review_action_class": "tune_entry",
                        "review_priority": "high",
                        "next_action": "delay",
                        "memo": "",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-03-30T00:35:00Z",
                    }
                )

            export_review_queue(
                base_dir=base_dir,
                review_note_path=review_note,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
            )

            note_text = review_note.read_text(encoding="utf-8")
            self.assertIn("AI事後評価の進捗を確認", note_text)
            self.assertIn("AI評価済み: 1", note_text)
            self.assertIn("人が上書き済み: 1", note_text)
            self.assertIn("human subject", note_text)
            self.assertNotIn("ai subject /", note_text)

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
            self.assertEqual(rows[0]["review_action_class"], "tune_entry")
            self.assertEqual(rows[0]["review_priority"], "medium")
            self.assertEqual(rows[0]["review_variant"], "ai_post_review_v2")

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

    def test_sync_ai_post_reviews_stops_after_consecutive_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                for idx in range(5):
                    writer.writerow(
                        {
                            "signal_id": f"sig_fail_{idx}",
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
                for idx in range(5):
                    writer.writerow({"signal_id": f"sig_fail_{idx}", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            with patch("tools.log_feedback.run_cli_json", side_effect=RuntimeError("usage limit")) as mocked_cli, patch(
                "tools.log_feedback.load_config"
            ) as mocked_cfg, patch("tools.log_feedback._build_review_chart_svg_path", return_value=None):
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 5,
                        "AI_POST_REVIEW_MAX_CONSECUTIVE_FAILURES": 2,
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

            self.assertEqual(mocked_cli.call_count, 2)
            self.assertEqual(stats["request_failed"], 2)
            self.assertEqual(stats["stopped_after_failures"], 1)

    def test_sync_ai_post_reviews_uses_api_fallback_when_cli_fails(self) -> None:
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
                        "signal_id": "sig_api_fallback",
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
                writer.writerow({"signal_id": "sig_api_fallback", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            api_review = {
                "user_verdict": "useful_wait",
                "usefulness_1to5": "4",
                "would_trade": "conditional",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "good",
                "tf_4h_eval": "good",
                "tf_1h_eval": "mixed",
                "tf_15m_eval": "mixed",
                "review_source": "ai",
                "review_model": "gpt-4o",
                "review_image_mode": "api_numeric_fallback",
                "review_variant": "ai_post_review_v2",
                "review_action_class": "watch",
                "review_priority": "medium",
                "next_action": "継続観測する",
                "memo": "API fallback",
            }
            with patch("tools.log_feedback.run_cli_json", side_effect=RuntimeError("usage limit")) as mocked_cli, patch(
                "tools.log_feedback._request_ai_post_review_via_api", return_value=api_review
            ) as mocked_api, patch("tools.log_feedback.load_config") as mocked_cfg, patch("tools.log_feedback._build_review_chart_svg_path", return_value=None):
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 1,
                        "AI_POST_REVIEW_MAX_CONSECUTIVE_FAILURES": 3,
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
            mocked_api.assert_called_once()
            self.assertEqual(stats["created"], 1)
            self.assertEqual(stats["request_failed"], 0)
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(rows[0]["review_image_mode"], "api_numeric_fallback")

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
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(rows[0]["review_model"], "gpt-5.3-codex")

    def test_sync_ai_post_reviews_resolves_legacy_cli_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)
            (base_dir / "tools").mkdir(parents=True, exist_ok=True)
            (base_dir / "tools" / "codex_cli_wrapper.py").write_text("# stub\n", encoding="utf-8")

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_legacy_path",
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
                writer.writerow({"signal_id": "sig_legacy_path", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            signal_path = base_dir / "logs" / "signals" / "sig_legacy_path.json"
            signal_path.write_text('{"signal_id":"sig_legacy_path","summary_subject":"subject"}', encoding="utf-8")

            ai_result = {
                "user_verdict": "useful_wait",
                "usefulness_1to5": "4",
                "would_trade": "conditional",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "good",
                "tf_4h_eval": "good",
                "tf_1h_eval": "good",
                "tf_15m_eval": "mixed",
                "memo": "ok",
            }
            legacy_path = "/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/tools/codex_cli_wrapper.py"
            with patch("tools.log_feedback.run_cli_json", return_value=ai_result) as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 2,
                        "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True,
                        "AI_ADVICE_CLI_COMMAND": legacy_path,
                        "OPENAI_ADVICE_MODEL": "gpt-4o",
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
            self.assertEqual(mocked_cli.call_args.kwargs["command"], str(base_dir / "tools" / "codex_cli_wrapper.py"))
            self.assertEqual(stats["resolved_cli_fallback"], 1)
            self.assertEqual(stats["created"], 1)

    def test_main_sync_ai_post_reviews_accepts_missing_max_new_ai_reviews(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "sync-ai-post-reviews"]), patch(
            "tools.log_feedback.sync_ai_post_reviews"
        ) as mocked_sync:
            mocked_sync.return_value = (Path("/tmp/user_reviews.csv"), {"created": 0})

            main()

        mocked_sync.assert_called_once()
        self.assertIsNone(mocked_sync.call_args.kwargs["max_new_reviews"])

    def test_backfill_ai_post_review_v2_updates_existing_rows_and_snapshots(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            snapshot_dir = base_dir / "logs" / "review" / "ai_post_reviews"
            snapshot_dir.mkdir(parents=True, exist_ok=True)

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_backfill",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "subject": "subject",
                        "auto_eval_summary": "summary",
                        "user_verdict": "too_early",
                        "usefulness_1to5": "2",
                        "would_trade": "no",
                        "actual_move_driver": "technical",
                        "misleading_entry_like_wording": "no",
                        "logic_validated": "true",
                        "sl_eval": "good",
                        "tp_eval": "good",
                        "tf_4h_eval": "good",
                        "tf_1h_eval": "good",
                        "tf_15m_eval": "poor",
                        "review_source": "ai",
                        "review_model": "gpt-test",
                        "review_image_mode": "price_map_svg",
                        "review_variant": "ai_post_review_v1",
                        "review_action_class": "",
                        "review_priority": "",
                        "next_action": "",
                        "memo": "memo",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-04-10T00:00:00Z",
                    }
                )

            (snapshot_dir / "sig_backfill.json").write_text(
                json_text := """{
  "signal_id": "sig_backfill",
  "review": {
    "signal_id": "sig_backfill",
    "timestamp_jst": "2026-04-10T01:05:00+09:00",
    "subject": "subject",
    "auto_eval_summary": "summary",
    "user_verdict": "too_early",
    "usefulness_1to5": "2",
    "would_trade": "no",
    "actual_move_driver": "technical",
    "misleading_entry_like_wording": "no",
    "logic_validated": "true",
    "sl_eval": "good",
    "tp_eval": "good",
    "tf_4h_eval": "good",
    "tf_1h_eval": "good",
    "tf_15m_eval": "poor",
    "review_source": "ai",
    "review_model": "gpt-test",
    "review_image_mode": "price_map_svg",
    "review_variant": "ai_post_review_v1",
    "review_action_class": "",
    "review_priority": "",
    "next_action": "",
    "memo": "memo",
    "review_status": "done",
    "reviewed_at_utc": "2026-04-10T00:00:00Z"
  }
}""",
                encoding="utf-8",
            )

            result = backfill_ai_post_review_v2(base_dir=base_dir, review_note_path=base_dir / "review.md", reviews_path=reviews_path)

            self.assertEqual(result["updated_reviews"], 1)
            self.assertEqual(result["updated_snapshots"], 1)
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(rows[0]["review_action_class"], "tune_entry")
            self.assertEqual(rows[0]["review_priority"], "medium")
            self.assertEqual(rows[0]["next_action"], "早すぎる通知を抑えるため発火条件を一段遅らせる")
            self.assertEqual(rows[0]["review_variant"], "ai_post_review_v2")
            snapshot_text = (snapshot_dir / "sig_backfill.json").read_text(encoding="utf-8")
            self.assertIn('"review_action_class": "tune_entry"', snapshot_text)
            self.assertIn('"review_variant": "ai_post_review_v2"', snapshot_text)

    def test_build_feedback_report_includes_ai_health_warning(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            shadow_path = base_dir / "logs" / "csv" / "shadow_log.csv"
            shadow_path.parent.mkdir(parents=True, exist_ok=True)
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
                "notify_reason",
                "prelabel",
                "primary_setup_status",
                "primary_setup_reason",
                "signal_tier",
            ]
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_health",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.0",
                        "signal_based_MAE_24h": "0.5",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "ready",
                        "primary_setup_reason": "balanced_location",
                        "signal_tier": "normal",
                    }
                )

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                ai_health_summary={
                    "status": "stalled",
                    "eligible": 5,
                    "backlog_pending": 3,
                    "ai_reviewed": 2,
                    "human_override": 0,
                    "created": 0,
                    "reused": 0,
                    "request_failed": 3,
                    "daily_cap": 4,
                    "last_ai_review_at": "2026-04-15T18:36:50Z",
                    "last_ai_error_at": "2026-04-18T18:35:03Z",
                    "resolved_cli_fallback": 1,
                },
            )

            self.assertIn("AI事後評価は停止中です。候補残 3 件", report)
            self.assertIn("### AI事後評価 health", report)
            self.assertIn("状態: 停止中", report)
            self.assertIn("created=0 / reused=0 / request_failed=3 / daily_cap=4", report)
            self.assertIn("旧CLIパスを現行repoへ自動補正 1 件", report)

    def test_load_latest_ai_sync_stats_reads_last_runtime_block(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            runtime_path = base_dir / "logs" / "runtime" / "ai_post_reviews.out"
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.write_text(
                "\n".join(
                    [
                        "reviews_path=/tmp/old.csv",
                        "eligible=150",
                        "created=1",
                        "request_failed=41",
                        "backlog_pending=41",
                        "reviews_path=/tmp/latest.csv",
                        "eligible=161",
                        "reused=0",
                        "created=4",
                        "request_failed=0",
                        "resolved_cli_fallback=0",
                        "daily_cap=4",
                        "backlog_pending=38",
                    ]
                ),
                encoding="utf-8",
            )

            stats = _load_latest_ai_sync_stats(base_dir)

            self.assertEqual(stats["eligible"], 161)
            self.assertEqual(stats["created"], 4)
            self.assertEqual(stats["request_failed"], 0)
            self.assertEqual(stats["backlog_pending"], 38)

    def test_ai_review_health_summary_uses_runtime_stats_when_daily_sync_is_noop(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            runtime_path = base_dir / "logs" / "runtime" / "ai_post_reviews.out"
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.write_text(
                "\n".join(
                    [
                        "reviews_path=/tmp/latest.csv",
                        "eligible=161",
                        "reused=0",
                        "created=4",
                        "request_failed=0",
                        "resolved_cli_fallback=0",
                        "daily_cap=4",
                        "backlog_pending=38",
                    ]
                ),
                encoding="utf-8",
            )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_1", "evaluation_status": "complete"})

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "was_notified", "notification_kind"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_1", "was_notified": "true", "notification_kind": "main"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            summary = _ai_review_health_summary(
                base_dir=base_dir,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
                sync_stats={"created": 0, "reused": 0, "request_failed": 0, "resolved_cli_fallback": 0, "daily_cap": 0},
            )

            self.assertEqual(summary["eligible"], 1)
            self.assertEqual(summary["backlog_pending"], 1)
            self.assertEqual(summary["created"], 4)
            self.assertEqual(summary["request_failed"], 0)
            self.assertEqual(summary["daily_cap"], 4)

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

    def test_build_shadow_log_reconciles_entry_ok_invalid_prelabel(self) -> None:
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
                    "primary_setup_side",
                    "primary_setup_status",
                    "primary_setup_reason",
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
                    "confidence_direction_shadow",
                    "confidence_execution_shadow",
                    "confidence_wait_shadow",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_reconcile",
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
                        "top_negative_factors": '["rr_long_penalty"]',
                        "prelabel": "ENTRY_OK",
                        "prelabel_primary_reason": "balanced_location",
                        "location_risk": "12.0",
                        "primary_setup_side": "long",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "invalid_reason": "RR不足",
                        "signal_tier": "normal",
                        "ai_decision": "",
                        "ai_confidence": "",
                        "was_notified": "true",
                        "notify_reason_codes": '["status_upgraded"]',
                        "suppress_reason_codes": "[]",
                        "data_quality_flag": "ok",
                        "data_missing_fields": "[]",
                        "risk_flags": "sweep_incomplete",
                        "warning_flags": "",
                        "no_trade_flags": "RR_insufficient",
                        "summary_subject": "subject",
                        "confidence_direction_shadow": "80",
                        "confidence_execution_shadow": "18",
                        "confidence_wait_shadow": "72",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_reconcile", "evaluation_status": "pending"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            shadow_path = build_shadow_log(
                base_dir=base_dir,
                trades_path=trades_path,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
            )
            rows = _load_csv_rows(shadow_path)
            self.assertEqual(rows[0]["prelabel"], "RISKY_ENTRY")
            self.assertEqual(rows[0]["phase1_observation_gate"], "pass")

    def test_build_observation_paper_orders_backfills_phase1a_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "current_price",
                        "primary_setup_side",
                        "primary_entry_mid",
                        "primary_stop_loss",
                        "shadow_tp1_price",
                        "shadow_tp2_price",
                        "rr_estimate",
                        "prelabel",
                        "primary_setup_status",
                        "primary_setup_reason",
                        "phase1_observation_gate",
                        "phase1_observation_type",
                        "phase1_observation_reasons",
                        "confidence_direction_shadow",
                        "confidence_execution_shadow",
                        "confidence_wait_shadow",
                        "trade_execution_gate",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "obs_backfill",
                        "timestamp_jst": "2026-04-22T10:00:00+09:00",
                        "current_price": "70000",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "69900",
                        "primary_stop_loss": "69500",
                        "shadow_tp1_price": "70420",
                        "shadow_tp2_price": "70860",
                        "rr_estimate": "1.3",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "phase1_observation_reasons": "[\"setup_watch_learning\"]",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "70",
                        "trade_execution_gate": "blocked",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "blocked",
                        "timestamp_jst": "2026-04-22T11:00:00+09:00",
                        "phase1_observation_gate": "blocked",
                    }
                )

            path = build_observation_paper_orders(base_dir=base_dir, trades_path=trades_path)
            rows = _load_csv_rows(path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "obs_backfill")
            self.assertEqual(rows[0]["observation_phase"], "phase1A")
            self.assertEqual(rows[0]["observation_type"], "setup_watch_learning")
            self.assertEqual(rows[0]["observation_status"], "observing")

    def test_build_feedback_report_starts_with_human_summary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)

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

            observation_orders_path = logs_csv / "observation_paper_orders.csv"
            with observation_orders_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=OBSERVATION_PAPER_ORDER_HEADER,
                )
                writer.writeheader()
                for signal_id in ["entry_rr_0", "entry_rr_1", "entry_rr_2", "risky_rr_0"]:
                    writer.writerow(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": timestamp_jst,
                            "observation_phase": "phase1A",
                            "observation_type": "direction_rr_learning",
                            "observation_status": "observing",
                        }
                    )

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                observation_paper_orders_path=observation_orders_path,
            )

            self.assertIn("## 1. まず結論", report)
            self.assertIn("Phase 1 判定では ready=1 件、phase1_active=true=1 件です。", report)
            self.assertIn("判定: Phase 1 の本有効確認を進めてよい", report)
            self.assertIn("## 3. Phase 1 判定サマリー", report)
            self.assertIn("## 4. AI事後評価サマリー", report)
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
            self.assertIn("## 4. AI事後評価サマリー", report)
            self.assertIn("完了レビューはまだありません", report)

    def test_build_feedback_report_shows_entry_ok_rr_and_ready_blockers(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)

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
                "notify_reason",
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
                "phase1_observation_gate",
                "phase1_observation_type",
                "phase1_observation_reasons",
                "suppress_reason",
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
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "direction_rr_learning",
                        "phase1_observation_reasons": "[\"direction_rr_learning\"]",
                        "suppress_reason": "rr_sweep_recheck_wait,attention_rr_sweep_recheck_wait",
                        "paper_order_status": "",
                        "tp_eval": "too_close",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "risky_rr_0",
                        "timestamp_jst": timestamp_jst,
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "2.4",
                        "signal_based_MAE_24h": "0.8",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "poor_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "notify_reason": "[\"attention_gap_crossed\", \"attention_score_crossed\"]",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "70100",
                        "tp1_price": "70600",
                        "shadow_tp1_price": "70750",
                        "shadow_exit_rule_version": "phase1_v1_shadow",
                        "invalid_reason": "RR不足",
                        "risk_flags": "orderbook_ask_heavy,sweep_incomplete",
                        "confidence_direction_shadow": "75",
                        "confidence_execution_shadow": "26",
                        "confidence_wait_shadow": "70.4",
                        "phase1_active": "false",
                        "trade_execution_gate": "blocked",
                        "trade_execution_blockers": "[\"rr_below_min\"]",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "direction_rr_learning",
                        "phase1_observation_reasons": "[\"direction_rr_learning\"]",
                        "suppress_reason": "rr_sweep_recheck_wait,attention_rr_sweep_recheck_wait",
                        "paper_order_status": "",
                        "tp_eval": "too_close",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "watch_sweep_0",
                        "timestamp_jst": timestamp_jst,
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.8",
                        "signal_based_MAE_24h": "0.7",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "not_applicable",
                        "wait_outcome": "good_wait",
                        "skip_outcome": "not_applicable",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "notify_reason": "[\"attention_bias_changed\"]",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "70200",
                        "tp1_price": "70700",
                        "shadow_tp1_price": "70800",
                        "shadow_exit_rule_version": "phase1_v1_shadow",
                        "invalid_reason": "",
                        "risk_flags": "sweep_incomplete",
                        "confidence_direction_shadow": "72",
                        "confidence_execution_shadow": "21",
                        "confidence_wait_shadow": "72",
                        "phase1_active": "false",
                        "trade_execution_gate": "blocked",
                        "trade_execution_blockers": "[\"phase1_inactive\", \"setup_not_ready\"]",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "phase1_observation_reasons": "[\"setup_watch_learning\"]",
                        "suppress_reason": "rr_sweep_recheck_wait",
                        "paper_order_status": "",
                        "tp_eval": "too_close",
                    }
                )
            (signals_dir / "risky_rr_0.json").write_text(
                json.dumps(
                    {
                        "signal_id": "risky_rr_0",
                        "primary_setup_side": "long",
                        "bias": "long",
                        "current_price": 75748.9,
                        "atr_15m_value": 213.1,
                        "confidence": 58,
                        "atr_ratio": 0.94,
                        "funding_rate_pct": 0.0043,
                        "volume_ratio": 4.07,
                        "trigger_volume_ratio_threshold": 1.15,
                        "breakout_up": False,
                        "warning_flags": [],
                        "support_zones_all": [
                            {"low": 74926.6, "high": 75002.6},
                            {"low": 74720.7, "high": 74885.4},
                        ],
                        "resistance_zones_all": [
                            {"low": 75962.0, "high": 76038.0},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (signals_dir / "watch_sweep_0.json").write_text(
                json.dumps(
                    {
                        "signal_id": "watch_sweep_0",
                        "primary_setup_side": "long",
                        "bias": "long",
                        "current_price": 75810.0,
                        "atr_15m_value": 210.0,
                        "confidence": 57,
                        "atr_ratio": 0.92,
                        "funding_rate_pct": 0.0041,
                        "volume_ratio": 3.2,
                        "trigger_volume_ratio_threshold": 1.15,
                        "breakout_up": False,
                        "warning_flags": [],
                        "support_zones_all": [
                            {"low": 75010.0, "high": 75120.0},
                        ],
                        "resistance_zones_all": [
                            {"low": 75980.0, "high": 76060.0},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            observation_orders_path = logs_csv / "observation_paper_orders.csv"
            with observation_orders_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=OBSERVATION_PAPER_ORDER_HEADER)
                writer.writeheader()
                for signal_id in ["entry_rr_0", "entry_rr_1", "entry_rr_2", "risky_rr_0", "watch_sweep_0"]:
                    writer.writerow(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": timestamp_jst,
                            "observation_phase": "phase1A",
                            "observation_type": "setup_watch_learning" if signal_id == "watch_sweep_0" else "direction_rr_learning",
                            "observation_status": "observing",
                        }
                    )

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                observation_paper_orders_path=observation_orders_path,
            )

            self.assertIn("ready阻害理由: rr_below_min=4件", report)
            self.assertIn("rr_below_min 代表例: risky_rr_0(invalid/RISKY_ENTRY, dir=75, exec=26, wait=70, MFE24h=2.40, MAE24h=0.80, outcome=win)", report)
            self.assertIn("entry_rr_0(invalid/ENTRY_OK, dir=80, exec=10, wait=70, MFE24h=1.00, MAE24h=0.50, outcome=win)", report)
            self.assertIn("ENTRY_OK + rr_below_min: 3件 / 平均 execution=10.0 / 平均 wait=70.0", report)
            self.assertIn("ENTRY_OK + rr_below_min の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件", report)
            self.assertIn(
                "position_risk候補: lower_liquidity_close + sweep_incomplete 同居時は ENTRY_OK から RISKY_ENTRY 寄せを検討",
                report,
            )
            self.assertIn("confidence候補: execution<=20 かつ wait>=60 の本通知上位扱いを抑制", report)
            self.assertIn("direction_execution_conflict の主な理由: rr_below_min=3件", report)
            self.assertIn("direction_execution_conflict の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件", report)
            self.assertIn("rr_sweep_recheck_wait: 4件", report)
            self.assertIn("attention_rr_sweep_recheck_wait: 4件", report)
            self.assertIn("suppress_reason の内訳: rr_sweep_recheck_wait=5件, attention_rr_sweep_recheck_wait=4件", report)
            self.assertIn("trade_execution_gate=blocked: 5件", report)
            self.assertIn("主なブロック理由: rr_below_min=4件, execution_shadow_too_low=3件, phase1_inactive=1件", report)
            self.assertIn("phase1_observation_gate=pass: 5件", report)
            self.assertIn("観測タイプ: direction_rr_learning=4件, setup_watch_learning=1件", report)
            self.assertIn("direction_rr_learning: 4件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=2.35", report)
            self.assertIn("setup_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=2.57", report)
            self.assertIn("observation_paper_orders observing: 5件", report)
            self.assertIn("setup_watch_learning の entry_zone_not_reached 率: 100.0%", report)
            self.assertIn("gate pass だが観測紙トレード未記録: 0件", report)
            self.assertIn("扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ", report)
            self.assertIn("RISKY_ENTRY + rr_below_min かつ execution>=20: 1件 / 平均 execution=26.0 / 平均 wait=70.4", report)
            self.assertIn("RISKY_ENTRY + rr_below_min の主な risk_flags: orderbook_ask_heavy=1件, sweep_incomplete=1件", report)
            self.assertIn("RR再調整候補: risky_rr_0(exec=26, dir=75, wait=70, MFE24h=2.40, MAE24h=0.80, outcome=win)", report)
            self.assertIn("現行RR再計算: risky_rr_0=>watch/entry_zone_not_reached/rr=2.40", report)
            self.assertIn("sweep_incomplete を含む RISKY_ENTRY + rr_below_min の通知済み履歴: 1件", report)
            self.assertIn("主な通知理由: attention_gap_crossed=1件, attention_score_crossed=1件", report)
            self.assertIn("代表例: risky_rr_0(attention_gap_crossed,attention_score_crossed, exec=26, wait=70)", report)
            self.assertIn("sweep_incomplete を含む watch 系通知済み履歴: 1件", report)
            self.assertIn("代表例: watch_sweep_0(attention_bias_changed, exec=21, wait=72)", report)
            self.assertIn("現行watch再計算: watch_sweep_0=>watch/entry_zone_not_reached/rr=2.40", report)
            self.assertIn("tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件", report)
            self.assertIn("### 改善アクション", report)
            self.assertIn("出口設計を調整=5件", report)
            self.assertIn("重要度: 高=5件", report)
            self.assertIn("TP1/TP2 を遠めにする候補を検証する", report)

    def test_build_current_setup_comparison_report_detects_status_changes(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "cmp_0",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                    }
                )
            (signals_dir / "cmp_0.json").write_text(
                json.dumps(
                    {
                        "signal_id": "cmp_0",
                        "primary_setup_side": "long",
                        "bias": "long",
                        "current_price": 75748.9,
                        "atr_15m_value": 213.1,
                        "confidence": 58,
                        "atr_ratio": 0.94,
                        "funding_rate_pct": 0.0043,
                        "volume_ratio": 4.07,
                        "trigger_volume_ratio_threshold": 1.15,
                        "breakout_up": False,
                        "warning_flags": [],
                        "support_zones_all": [
                            {"low": 74926.6, "high": 75002.6},
                            {"low": 74720.7, "high": 74885.4},
                        ],
                        "resistance_zones_all": [
                            {"low": 75962.0, "high": 76038.0},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report = build_current_setup_comparison_report(base_dir=base_dir, shadow_path=shadow_path, limit=5)

            self.assertIn("差分ありのうち通知済み: 1", report)
            self.assertIn("平均 execution_shadow: 0.0", report)
            self.assertIn("平均 wait_shadow: 0.0", report)
            self.assertIn("主な status 変化: invalid->watch=1件", report)
            self.assertIn("主な reason 変化: rr_below_min->entry_zone_not_reached=1件", report)
            self.assertIn("## status別集計", report)
            self.assertIn("- invalid->watch: 1件 / 平均 execution=0.0 / 平均 wait=0.0", report)
            self.assertIn(
                "cmp_0: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=2.40 / prelabel=RISKY_ENTRY / notified=yes",
                report,
            )

    def test_build_current_setup_comparison_report_supports_filters(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "cmp_keep",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                        "risk_flags": "sweep_incomplete",
                        "notify_reason": "[\"prelabel_improved\"]",
                        "confidence_execution_shadow": "21",
                        "confidence_wait_shadow": "72",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "cmp_drop",
                        "timestamp_jst": "2026-04-24T02:05:00+09:00",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "confidence_below_min",
                        "was_notified": "false",
                        "risk_flags": "ask_wall_close",
                        "notify_reason": "[\"status_upgraded\"]",
                        "confidence_execution_shadow": "11",
                        "confidence_wait_shadow": "90",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "cmp_old",
                        "timestamp_jst": "2026-04-23T23:55:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                        "risk_flags": "sweep_incomplete",
                        "notify_reason": "[\"status_upgraded\"]",
                        "confidence_execution_shadow": "19",
                        "confidence_wait_shadow": "61",
                    }
                )
            payload = {
                "primary_setup_side": "long",
                "bias": "long",
                "current_price": 75748.9,
                "atr_15m_value": 213.1,
                "confidence": 58,
                "atr_ratio": 0.94,
                "funding_rate_pct": 0.0043,
                "volume_ratio": 4.07,
                "trigger_volume_ratio_threshold": 1.15,
                "breakout_up": False,
                "warning_flags": [],
                "support_zones_all": [
                    {"low": 74926.6, "high": 75002.6},
                    {"low": 74720.7, "high": 74885.4},
                ],
                "resistance_zones_all": [
                    {"low": 75962.0, "high": 76038.0},
                ],
            }
            for signal_id in ("cmp_keep", "cmp_drop", "cmp_old"):
                (signals_dir / f"{signal_id}.json").write_text(
                    json.dumps({"signal_id": signal_id, **payload}, ensure_ascii=False),
                    encoding="utf-8",
                )

            report = build_current_setup_comparison_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                limit=5,
                only_notified=True,
                previous_reason="rr_below_min",
                current_reason="entry_zone_not_reached",
                prelabel="risky_entry",
                risk_flag="sweep_incomplete",
                date_from="2026-04-24",
                date_to="2026-04-24",
                status_transition="invalid->watch",
            )

            self.assertIn("- フィルタ: 通知済みのみ", report)
            self.assertIn("- フィルタ: 旧 reason=rr_below_min", report)
            self.assertIn("- フィルタ: 現行 reason=entry_zone_not_reached", report)
            self.assertIn("- フィルタ: prelabel=RISKY_ENTRY", report)
            self.assertIn("- フィルタ: risk_flag=sweep_incomplete", report)
            self.assertIn("- フィルタ: date_from=2026-04-24", report)
            self.assertIn("- フィルタ: date_to=2026-04-24", report)
            self.assertIn("- フィルタ: status_transition=invalid->watch", report)
            self.assertIn("現行 setup との差分あり: 1", report)
            self.assertIn("- 主な risk_flags: sweep_incomplete=1件", report)
            self.assertIn("- 主な通知理由: prelabel_improved=1件", report)
            self.assertIn("- invalid->watch: 1件 / 平均 execution=21.0 / 平均 wait=72.0", report)
            self.assertIn("cmp_keep: invalid/rr_below_min -> watch/entry_zone_not_reached", report)
            self.assertNotIn("cmp_drop", report)
            self.assertNotIn("cmp_old", report)

    def test_refresh_standard_setup_comparison_reports_generates_three_standard_reports(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "cmp_entry",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                        "risk_flags": "sweep_incomplete,orderbook_ask_heavy",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "cmp_conf",
                        "timestamp_jst": "2026-04-24T04:05:00+09:00",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "false",
                        "risk_flags": "sweep_incomplete",
                        "confidence_execution_shadow": "11",
                        "confidence_wait_shadow": "100",
                    }
                )
            entry_payload = {
                "signal_id": "cmp_entry",
                "primary_setup_side": "long",
                "bias": "long",
                "current_price": 75748.9,
                "atr_15m_value": 213.1,
                "confidence": 58,
                "atr_ratio": 0.94,
                "funding_rate_pct": 0.0043,
                "volume_ratio": 4.07,
                "trigger_volume_ratio_threshold": 1.15,
                "breakout_up": False,
                "warning_flags": [],
                "support_zones_all": [
                    {"low": 74926.6, "high": 75002.6},
                    {"low": 74720.7, "high": 74885.4},
                ],
                "resistance_zones_all": [
                    {"low": 75962.0, "high": 76038.0},
                ],
            }
            confidence_payload = {
                "signal_id": "cmp_conf",
                "primary_setup_side": "long",
                "bias": "long",
                "current_price": 77740.8,
                "atr_15m_value": 100.0,
                "confidence": 17,
                "atr_ratio": 0.94,
                "funding_rate_pct": 0.0043,
                "volume_ratio": 1.2,
                "trigger_volume_ratio_threshold": 1.15,
                "breakout_up": False,
                "warning_flags": [],
                "support_zones_all": [
                    {"low": 77695.07, "high": 77793.93},
                ],
                "resistance_zones_all": [
                    {"low": 77765.27, "high": 77864.13},
                ],
            }
            (signals_dir / "cmp_entry.json").write_text(json.dumps(entry_payload, ensure_ascii=False), encoding="utf-8")
            (signals_dir / "cmp_conf.json").write_text(json.dumps(confidence_payload, ensure_ascii=False), encoding="utf-8")

            generated = refresh_standard_setup_comparison_reports(
                base_dir=base_dir,
                shadow_path=shadow_path,
                analysis_dir=base_dir / "analysis",
                date_from="2026-04-24",
                date_to="2026-04-24",
            )

            self.assertEqual(
                set(generated.keys()),
                {
                    "notified_rr_to_entry",
                    "notified_rr_to_entry_orderbook_ask_heavy",
                    "rr_to_confidence",
                },
            )
            self.assertIn("現行 setup との差分あり: 1", generated["notified_rr_to_entry"].read_text(encoding="utf-8"))
            self.assertIn("risk_flag=orderbook_ask_heavy", generated["notified_rr_to_entry_orderbook_ask_heavy"].read_text(encoding="utf-8"))
            self.assertIn("rr_below_min->confidence_below_min=1件", generated["rr_to_confidence"].read_text(encoding="utf-8"))

    def test_main_refresh_standard_setup_reports_accepts_optional_analysis_dir(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "refresh-standard-setup-reports", "--analysis-dir", "/tmp/analysis"]), patch(
            "tools.log_feedback.refresh_standard_setup_comparison_reports"
        ) as mocked_refresh:
            mocked_refresh.return_value = {"sample": Path("/tmp/analysis/sample.md")}

            main()

        mocked_refresh.assert_called_once()
        self.assertEqual(mocked_refresh.call_args.kwargs["analysis_dir"], Path("/tmp/analysis"))

    def test_build_operational_focus_report_summarizes_backlog_and_phase1_bias(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "backlog_1",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "prelabel": "SWEEP_WAIT",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "confidence_execution_shadow": "8",
                        "confidence_wait_shadow": "72",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "backlog_2",
                        "timestamp_jst": "2026-04-22T03:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "RISKY_ENTRY",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "",
                        "phase1_observation_reasons": "confidence_below_min,no_trade_candidate",
                        "confidence_execution_shadow": "14",
                        "confidence_wait_shadow": "90",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,orderbook_ask_heavy",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "backlog_3",
                        "timestamp_jst": "2026-04-22T02:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "",
                        "phase1_observation_reasons": "confidence_below_min",
                        "confidence_execution_shadow": "10",
                        "confidence_wait_shadow": "88",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "done_ai",
                        "timestamp_jst": "2026-04-24T04:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "ai",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "near_entry_zone_waiting_trigger",
                        "prelabel": "SWEEP_WAIT",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "confidence_execution_shadow": "9",
                        "confidence_wait_shadow": "65",
                        "risk_flags": "sweep_incomplete",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "direction_1",
                        "timestamp_jst": "2026-04-24T05:05:00+09:00",
                        "was_notified": "false",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "prelabel": "RISKY_ENTRY",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "direction_rr_learning",
                        "confidence_execution_shadow": "31",
                        "confidence_wait_shadow": "22",
                        "risk_flags": "ask_wall_close",
                        "signal_tier": "normal",
                    }
                )

            report = build_operational_focus_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-22",
                date_to="2026-04-24",
                limit=3,
            )

            self.assertIn("- 未処理 backlog 候補: 3件", report)
            self.assertIn("- 年齢分布:", report)
            self.assertIn("- phase1 観測タイプ: setup_watch_learning=1件", report)
            self.assertIn("- pass: 3件 / blocked: 2件", report)
            self.assertIn("- pass 内訳: setup_watch_learning=2件, direction_rr_learning=1件", report)
            self.assertIn("- 主な blocked 理由: confidence_below_min=2件, no_trade_candidate=1件", report)
            self.assertIn("- setup_watch_learning: 2件 / 平均 execution=8.5 / 平均 wait=68.5", report)
            self.assertIn("- direction_rr_learning: 1件 / 平均 execution=31.0 / 平均 wait=22.0", report)
            self.assertIn("## blocked 上位理由の内訳", report)
            self.assertIn("- confidence_below_min: 2件", report)
            self.assertIn("  - prelabel: RISKY_ENTRY=1件, SWEEP_WAIT=1件", report)
            self.assertIn("  - risk_flags: sweep_incomplete=2件, lower_liquidity_close=2件, orderbook_ask_heavy=1件", report)
            self.assertIn("## sweep+lower_liquidity の補助flag内訳", report)
            self.assertIn("- confidence_below_min: 2件 / 平均 execution=12.0 / 平均 wait=89.0", report)
            self.assertIn("  - 補助flag: orderbook_ask_heavy=1件, 補助flagなし=1件", report)
            self.assertIn("## 緩和候補の少数群", report)
            self.assertIn("- backlog_3: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=10.0 / wait=88.0", report)

    def test_main_build_operational_focus_report_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-operational-focus-report", "--output-md", "/tmp/focus.md"]), patch(
            "tools.log_feedback.build_operational_focus_report"
        ) as mocked_focus:
            mocked_focus.return_value = "# report\n"

            main()

        mocked_focus.assert_called_once()
        self.assertEqual(mocked_focus.call_args.kwargs["output_md"], Path("/tmp/focus.md"))

    def test_build_relaxation_candidates_report_lists_softer_confidence_candidates(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "soft_1",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_execution_shadow": "10",
                        "confidence_wait_shadow": "88",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "hard_1",
                        "timestamp_jst": "2026-04-24T02:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "RISKY_ENTRY",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,orderbook_ask_heavy",
                        "confidence_execution_shadow": "14",
                        "confidence_wait_shadow": "90",
                    }
                )

            report = build_relaxation_candidates_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-24",
                date_to="2026-04-24",
            )

            self.assertIn("- 候補件数: 1件", report)
            self.assertIn("- prelabel: SWEEP_WAIT=1件", report)
            self.assertIn("- phase1 reasons: confidence_below_min=1件", report)
            self.assertIn("- risk_flags: sweep_incomplete=1件, lower_liquidity_close=1件", report)
            self.assertIn("- soft_1: 2026-04-24 03:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=10.0 / wait=88.0", report)
            self.assertNotIn("hard_1", report)

    def test_build_phase1b_promotion_report_lists_limited_watch_candidates(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "promo_1",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "confidence_watch_learning",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_direction_shadow": "58",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "80",
                        "outcome": "win",
                        "tp1_hit_first": "true",
                        "signal_based_MFE_24h": "12",
                        "signal_based_MAE_24h": "4",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "blocked_1",
                        "timestamp_jst": "2026-04-24T02:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "confidence_watch_learning",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,ask_wall_close",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "25",
                        "confidence_wait_shadow": "75",
                        "outcome": "win",
                        "tp1_hit_first": "true",
                        "signal_based_MFE_24h": "15",
                        "signal_based_MAE_24h": "5",
                    }
                )

            report = build_phase1b_promotion_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-24",
                date_to="2026-04-24",
            )

            self.assertIn("- 候補件数: 1件", report)
            self.assertIn("- prelabel: SWEEP_WAIT=1件", report)
            self.assertIn("- 勝率=100.0% / TP1先行=100.0% / 近似PF=3.00", report)
            self.assertIn("## Phase 1B-lite", report)
            self.assertIn("- lite 候補件数: 1件", report)
            self.assertIn("- 扱い: 実弾ではなく、正式 Phase 1B でもない。専用CSVでのみ追跡する", report)
            self.assertIn("- promo_1: 2026-04-24 03:05 / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=80.0", report)
            self.assertNotIn("blocked_1", report)

    def test_build_phase1b_lite_paper_orders_backfills_lite_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            output_path = logs_csv / "phase1b_lite_paper_orders.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "lite_1",
                        "timestamp_jst": "2026-05-17T10:00:00+09:00",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "69900",
                        "primary_stop_loss": "69500",
                        "shadow_tp1_price": "70420",
                        "shadow_tp2_price": "70860",
                        "phase1_observation_type": "confidence_watch_learning",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "no_trade_flags": "",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "76.8",
                        "trade_execution_gate": "blocked",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "normal_obs_1",
                        "timestamp_jst": "2026-05-17T09:00:00+09:00",
                        "phase1_observation_type": "setup_watch_learning",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "76.8",
                    }
                )

            result_path = build_phase1b_lite_paper_orders(
                base_dir=base_dir,
                trades_path=shadow_path,
                output_path=output_path,
            )

            with result_path.open(newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(result_path, output_path)
            self.assertEqual(rows[0].keys(), set(PHASE1B_LITE_PAPER_ORDER_HEADER))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "lite_1")
            self.assertEqual(rows[0]["lite_phase"], "phase1B-lite")
            self.assertEqual(rows[0]["lite_status"], "observing")
            self.assertEqual(rows[0]["lite_type"], "confidence_watch_sweep_lite")
            self.assertFalse((base_dir / "logs" / "csv" / "paper_orders.csv").exists())

    def test_build_failed_breakout_down_reversal_report_lists_reversal_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "20260429_100500",
                        "timestamp_jst": "2026-04-29T19:05:00+09:00",
                        "bias": "long",
                        "phase": "breakout",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "top_positive_factors": '[{"code":"ema_alignment_bullish","score":12},{"code":"breakout_up","score":10}]',
                        "direction_outcome": "wrong",
                        "entry_outcome": "poor_entry",
                        "signal_based_MFE_24h": "1.68",
                        "signal_based_MAE_24h": "12.27",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,long_reversal_risk",
                        "notify_reason": '["confidence_jump","prelabel_improved"]',
                        "long_score": "92",
                        "short_score": "50",
                        "score_gap": "42",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "other_case",
                        "timestamp_jst": "2026-04-29T18:05:00+09:00",
                        "bias": "long",
                        "phase": "breakout",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "top_positive_factors": '[{"code":"ema_alignment_bullish","score":12}]',
                        "direction_outcome": "wrong",
                        "entry_outcome": "poor_entry",
                        "signal_based_MFE_24h": "1.00",
                        "signal_based_MAE_24h": "9.00",
                    }
                )

            report = build_failed_breakout_down_reversal_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-29",
                date_to="2026-04-29",
            )

            self.assertIn("- 件数: 1件", report)
            self.assertIn("- risk_flags: sweep_incomplete=1件, lower_liquidity_close=1件, long_reversal_risk=1件", report)
            self.assertIn("20260429_100500", report)
            self.assertNotIn("other_case", report)

    def test_build_market_map_effectiveness_report_groups_flags(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "map_down_1",
                        "timestamp_jst": "2026-04-29T19:05:00+09:00",
                        "market_map_primary_state": "confirmed_down",
                        "market_map_flags": "failed_breakout_down_reversal,long_into_major_resistance",
                        "level_flip_state": "support_to_resistance_confirmed",
                        "failed_breakout_state": "down_reversal",
                        "trend_flip_state": "confirmed_down",
                        "direction_outcome": "wrong",
                        "outcome": "loss",
                        "signal_based_MFE_24h": "1.5",
                        "signal_based_MAE_24h": "12.0",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "plain_1",
                        "timestamp_jst": "2026-04-29T18:05:00+09:00",
                        "direction_outcome": "correct",
                        "outcome": "win",
                    }
                )

            report = build_market_map_effectiveness_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-29",
                date_to="2026-04-29",
            )

            self.assertIn("- market_map 記録あり: 1件", report)
            self.assertIn("failed_breakout_down_reversal=1件", report)
            self.assertIn("failed_breakout_down_reversal: 勝率=0.0%", report)
            self.assertIn("map_down_1", report)

    def test_build_market_map_readiness_report_waits_without_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "latest_without_map",
                        "timestamp_jst": "2026-05-13T04:05:00+09:00",
                        "summary_subject": "👀 [注意報] 上方向監視 【BTC:80,493】 [Ver02.5-v5] [CLI]",
                    }
                )

            report = build_market_map_readiness_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-05-13",
            )

            self.assertIn("- readiness: wait", report)
            self.assertIn("- market_map 記録あり: 0件", report)
            self.assertIn("subject_version=Ver02.5-v5", report)
            self.assertIn("market_map_primary_state", report)

    def test_build_market_map_readiness_report_passes_with_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "map_ready",
                        "timestamp_jst": "2026-05-13T05:05:00+09:00",
                        "market_map_primary_state": "confirmed_down",
                        "market_map_flags": "support_to_resistance_flip,failed_breakout_down_reversal",
                    }
                )

            report = build_market_map_readiness_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-05-13",
            )

            self.assertIn("- readiness: pass", report)
            self.assertIn("- market_map 記録あり: 1件", report)
            self.assertIn("confirmed_down=1件", report)
            self.assertIn("failed_breakout_down_reversal=1件", report)

    def test_main_build_relaxation_candidates_report_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-relaxation-candidates-report", "--output-md", "/tmp/relax.md"]), patch(
            "tools.log_feedback.build_relaxation_candidates_report"
        ) as mocked_report:
            mocked_report.return_value = "# relax\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/relax.md"))

    def test_main_build_phase1b_promotion_report_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-phase1b-promotion-report", "--output-md", "/tmp/promotion.md"]), patch(
            "tools.log_feedback.build_phase1b_promotion_report"
        ) as mocked_report:
            mocked_report.return_value = "# promotion\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/promotion.md"))

    def test_main_build_failed_breakout_down_reversal_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-failed-breakout-down-reversal-report", "--output-md", "/tmp/failed_breakout.md"],
        ), patch("tools.log_feedback.build_failed_breakout_down_reversal_report") as mocked_report:
            mocked_report.return_value = "# failed_breakout\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/failed_breakout.md"))

    def test_main_build_market_map_effectiveness_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-market-map-effectiveness-report", "--output-md", "/tmp/market_map.md"],
        ), patch("tools.log_feedback.build_market_map_effectiveness_report") as mocked_report:
            mocked_report.return_value = "# market_map\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/market_map.md"))

    def test_main_build_market_map_readiness_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-market-map-readiness-report", "--output-md", "/tmp/market_map_ready.md", "--min-market-rows", "3"],
        ), patch("tools.log_feedback.build_market_map_readiness_report") as mocked_report:
            mocked_report.return_value = "# market_map readiness\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/market_map_ready.md"))
        self.assertEqual(mocked_report.call_args.kwargs["min_market_rows"], 3)

    def test_main_build_report_hub_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-report-hub", "--output-md", "/tmp/report_hub.md"]), patch(
            "tools.log_feedback.build_report_hub"
        ) as mocked_report:
            mocked_report.return_value = "# hub\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/report_hub.md"))


if __name__ == "__main__":
    unittest.main()
