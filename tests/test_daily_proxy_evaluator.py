from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import build_daily_proxy_evaluator_report, main


class DailyProxyEvaluatorTests(unittest.TestCase):
    def _write_csv(self, path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        return path

    def _write_headers_only(self, path: Path, fieldnames: list[str]) -> Path:
        return self._write_csv(path, fieldnames, [])

    def _write_sample_inputs(self, base_dir: Path) -> dict[str, Path]:
        signal_outcomes_path = self._write_csv(
            base_dir / "logs" / "csv" / "signal_outcomes.csv",
            [
                "signal_id",
                "timestamp_jst",
                "bias",
                "prelabel",
                "signal_tier",
                "direction_outcome",
                "entry_outcome",
                "wait_outcome",
                "skip_outcome",
                "outcome",
            ],
            [
                {
                    "signal_id": "sig-1",
                    "timestamp_jst": "2026-07-01T09:00:00+09:00",
                    "bias": "long",
                    "prelabel": "ENTRY_OK",
                    "signal_tier": "normal",
                    "direction_outcome": "correct",
                    "entry_outcome": "good_entry",
                    "wait_outcome": "not_applicable",
                    "skip_outcome": "not_applicable",
                    "outcome": "win",
                },
                {
                    "signal_id": "sig-2",
                    "timestamp_jst": "2026-07-01T10:00:00+09:00",
                    "bias": "short",
                    "prelabel": "NO_TRADE_CANDIDATE",
                    "signal_tier": "normal",
                    "direction_outcome": "wrong",
                    "entry_outcome": "poor_entry",
                    "wait_outcome": "wait_too_strict",
                    "skip_outcome": "skip_too_strict",
                    "outcome": "win",
                },
                {
                    "signal_id": "sig-3",
                    "timestamp_jst": "2026-06-30T10:00:00+09:00",
                    "bias": "short",
                    "prelabel": "NO_TRADE_CANDIDATE",
                    "signal_tier": "normal",
                    "direction_outcome": "wrong",
                    "entry_outcome": "poor_entry",
                    "wait_outcome": "not_applicable",
                    "skip_outcome": "not_applicable",
                    "outcome": "loss",
                },
            ],
        )
        candidate_outcomes_path = self._write_csv(
            base_dir / "logs" / "csv" / "active_plan_candidate_outcomes.csv",
            [
                "candidate_id",
                "source_signal_id",
                "timestamp_jst",
                "active_primary_action",
                "candidate_type",
                "candidate_status",
                "side",
                "outcome_direction_outcome",
                "tp1_close_reached_24h",
                "sl_close_reached_24h",
            ],
            [
                {
                    "candidate_id": "cand-1",
                    "source_signal_id": "sig-1",
                    "timestamp_jst": "2026-07-01T09:05:00+09:00",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "candidate_type": "active_limit_retest",
                    "candidate_status": "allowed",
                    "side": "long",
                    "outcome_direction_outcome": "correct",
                    "tp1_close_reached_24h": "true",
                    "sl_close_reached_24h": "false",
                },
                {
                    "candidate_id": "cand-2",
                    "source_signal_id": "sig-2",
                    "timestamp_jst": "2026-07-01T10:05:00+09:00",
                    "active_primary_action": "ACTIVE_MARKET_SMALL",
                    "candidate_type": "active_market_small",
                    "candidate_status": "candidate",
                    "side": "short",
                    "outcome_direction_outcome": "wrong",
                    "tp1_close_reached_24h": "false",
                    "sl_close_reached_24h": "true",
                },
                {
                    "candidate_id": "cand-3",
                    "source_signal_id": "sig-3",
                    "timestamp_jst": "2026-06-30T10:05:00+09:00",
                    "active_primary_action": "ACTIVE_COUNTER_SCALP",
                    "candidate_type": "active_counter_scalp",
                    "candidate_status": "conditional",
                    "side": "short",
                    "outcome_direction_outcome": "wrong",
                    "tp1_close_reached_24h": "false",
                    "sl_close_reached_24h": "false",
                },
            ],
        )
        intraperiod_outcomes_path = self._write_csv(
            base_dir / "logs" / "csv" / "active_plan_candidate_intraperiod_outcomes.csv",
            [
                "candidate_id",
                "signal_id",
                "timestamp_jst",
                "candidate_type",
                "active_primary_action",
                "side",
                "outcome",
                "first_exit_reason",
                "mfe_r",
                "mae_r",
            ],
            [
                {
                    "candidate_id": "cand-1",
                    "signal_id": "sig-1",
                    "timestamp_jst": "2026-07-01T09:05:00+09:00",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "NO_ACTION",
                    "side": "long",
                    "outcome": "tp1_first",
                    "first_exit_reason": "tp1",
                    "mfe_r": "1.5",
                    "mae_r": "0.3",
                },
                {
                    "candidate_id": "cand-2",
                    "signal_id": "sig-2",
                    "timestamp_jst": "2026-07-01T10:05:00+09:00",
                    "candidate_type": "active_market_small",
                    "active_primary_action": "ACTIVE_MARKET_SMALL",
                    "side": "short",
                    "outcome": "sl_first",
                    "first_exit_reason": "sl",
                    "mfe_r": "0.4",
                    "mae_r": "1.2",
                },
                {
                    "candidate_id": "cand-3",
                    "signal_id": "sig-3",
                    "timestamp_jst": "2026-07-01T10:10:00+09:00",
                    "candidate_type": "active_counter_scalp",
                    "active_primary_action": "ACTIVE_COUNTER_SCALP",
                    "side": "short",
                    "outcome": "sl_first",
                    "first_exit_reason": "sl",
                    "mfe_r": "0.6",
                    "mae_r": "1.4",
                },
                {
                    "candidate_id": "cand-4",
                    "signal_id": "sig-4",
                    "timestamp_jst": "2026-06-30T10:10:00+09:00",
                    "candidate_type": "active_counter_scalp",
                    "active_primary_action": "ACTIVE_COUNTER_SCALP",
                    "side": "short",
                    "outcome": "timeout",
                    "first_exit_reason": "timeout",
                    "mfe_r": "0.2",
                    "mae_r": "0.1",
                },
            ],
        )
        user_reviews_path = self._write_csv(
            base_dir / "logs" / "csv" / "user_reviews.csv",
            [
                "signal_id",
                "timestamp_jst",
                "subject",
                "user_verdict",
                "usefulness_1to5",
                "would_trade",
                "review_source",
                "review_status",
            ],
            [
                {
                    "signal_id": "sig-1",
                    "timestamp_jst": "2026-07-01T11:00:00+09:00",
                    "subject": "売買非推奨 / ちょっと遠い",
                    "user_verdict": "useful_entry",
                    "usefulness_1to5": "4",
                    "would_trade": "yes",
                    "review_source": "ai",
                    "review_status": "done",
                },
                {
                    "signal_id": "sig-2",
                    "timestamp_jst": "2026-07-01T11:05:00+09:00",
                    "subject": "実弾不可 / 注意報",
                    "user_verdict": "useful_wait",
                    "usefulness_1to5": "3",
                    "would_trade": "no",
                    "review_source": "human",
                    "review_status": "done",
                },
            ],
        )
        return {
            "signal_outcomes": signal_outcomes_path,
            "active_plan_candidate_outcomes": candidate_outcomes_path,
            "active_plan_candidate_intraperiod_outcomes": intraperiod_outcomes_path,
            "user_reviews": user_reviews_path,
        }

    def test_missing_inputs_do_not_crash_and_write_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            report = build_daily_proxy_evaluator_report(
                base_dir=base_dir,
                report_date="20260602",
                lookback_days=7,
            )
            output_path = base_dir / "運用資料" / "reports" / "post_eval" / "daily_proxy_evaluator_20260602.md"
            self.assertTrue(output_path.exists())
        self.assertIn("# Daily Proxy Evaluator", report)
        self.assertIn("`signal_outcomes`: status=missing", report)
        self.assertIn("`active_plan_candidate_outcomes`: status=missing", report)
        self.assertIn("`active_plan_candidate_intraperiod_outcomes`: status=missing", report)
        self.assertIn("`user_reviews`: status=missing", report)
        self.assertIn("INPUT_COVERAGE_REVIEW", report)
        self.assertIn("report-only", report)
        self.assertIn("not FORMAL_GO", report)
        self.assertIn("no automatic order", report)
        self.assertIn("no private/account/order endpoints", report)
        self.assertIn("human decides manually", report)
        self.assertIn("no actual human PnL yet", report)
        self.assertIn("biweekly actual trade import will calibrate proxy vs actual later", report)

    def test_header_only_inputs_produce_zero_row_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_headers_only(
                base_dir / "logs" / "csv" / "signal_outcomes.csv",
                ["signal_id", "timestamp_jst", "bias", "prelabel", "signal_tier", "direction_outcome", "entry_outcome", "wait_outcome", "skip_outcome", "outcome"],
            )
            self._write_headers_only(
                base_dir / "logs" / "csv" / "active_plan_candidate_outcomes.csv",
                ["candidate_id", "source_signal_id", "timestamp_jst", "active_primary_action", "candidate_type", "candidate_status", "side", "outcome_direction_outcome", "tp1_close_reached_24h", "sl_close_reached_24h"],
            )
            self._write_headers_only(
                base_dir / "logs" / "csv" / "active_plan_candidate_intraperiod_outcomes.csv",
                ["candidate_id", "signal_id", "timestamp_jst", "candidate_type", "active_primary_action", "side", "outcome", "first_exit_reason", "mfe_r", "mae_r"],
            )
            self._write_headers_only(
                base_dir / "logs" / "csv" / "user_reviews.csv",
                ["signal_id", "timestamp_jst", "subject", "user_verdict", "usefulness_1to5", "would_trade", "review_source", "review_status"],
            )

            report = build_daily_proxy_evaluator_report(
                base_dir=base_dir,
                report_date="20260602",
                lookback_days=7,
            )
            self.assertTrue(
                (base_dir / "運用資料" / "reports" / "post_eval" / "daily_proxy_evaluator_20260602.md").exists()
            )

        self.assertIn("`signal_outcomes`: status=header_only", report)
        self.assertIn("`active_plan_candidate_outcomes`: status=header_only", report)
        self.assertIn("`active_plan_candidate_intraperiod_outcomes`: status=header_only", report)
        self.assertIn("`user_reviews`: status=header_only", report)
        self.assertIn("selected_rows=0", report)
        self.assertIn("## 3. Signal Outcome Proxy", report)
        self.assertIn("bias: なし", report)
        self.assertIn("prelabel: なし", report)
        self.assertIn("INPUT_COVERAGE_REVIEW", report)

    def test_sample_rows_aggregate_counts_and_recommendations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_sample_inputs(base_dir)
            report = build_daily_proxy_evaluator_report(
                base_dir=base_dir,
                report_date=None,
                lookback_days=7,
            )
            output_path = base_dir / "運用資料" / "reports" / "post_eval" / "daily_proxy_evaluator_20260701.md"
            self.assertTrue(output_path.exists())
        self.assertIn("report_date: `20260701`", report)
        self.assertIn("selected_window: `2026-06-25", report)
        self.assertIn("## 3. Signal Outcome Proxy", report)
        self.assertIn("bias: short=2件, long=1件", report)
        self.assertIn("prelabel: NO_TRADE_CANDIDATE=2件, ENTRY_OK=1件", report)
        self.assertIn("skip_too_strict count: 1", report)
        self.assertIn("good_entry count: 1", report)
        self.assertIn("## 4. Active Plan Candidate Proxy", report)
        self.assertIn("side: short=2件, long=1件", report)
        self.assertIn("candidate_type: active_limit_retest=1件", report)
        self.assertIn("tp1_close_reached_24h true count: 1", report)
        self.assertIn("sl_close_reached_24h true count: 1", report)
        self.assertIn("## 5. Intraperiod Proxy", report)
        self.assertIn("NO_ACTION", report)
        self.assertIn("tp1_first count: 1", report)
        self.assertIn("sl_first count: 2", report)
        self.assertIn("timeout count: 1", report)
        self.assertIn("average mfe_r:", report)
        self.assertIn("average mae_r:", report)
        self.assertIn("## 6. User Review Proxy", report)
        self.assertIn("review_status: done=2件", report)
        self.assertIn("defensive wording count: 2", report)
        self.assertIn("## 7. Daily Proxy Recommendations", report)
        self.assertIn("NO_TRADE_SPLIT_CANDIDATE", report)
        self.assertIn("AGGRESSION_RISK_REVIEW", report)
        self.assertIn("LONG_SHORT_BALANCE_REVIEW", report)
        self.assertIn("SUBJECT_TOO_DEFENSIVE_REVIEW", report)
        self.assertIn("proxy-only / not trading permission", report)
        self.assertIn("## 8. Limitations", report)

    def test_cli_stdout_json_reports_compact_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self._write_sample_inputs(base_dir)
            stdout = io.StringIO()
            with patch("tools.log_feedback.BASE_DIR", base_dir), patch.object(
                sys,
                "argv",
                [
                    "tools/log_feedback.py",
                    "build-daily-proxy-evaluator-report",
                    "--date",
                    "20260702",
                    "--stdout-json",
                ],
            ), redirect_stdout(stdout):
                main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["schema_version"], "daily_proxy_evaluator.v1")
        self.assertEqual(payload["report_date"], "20260702")
        self.assertTrue(payload["report_path"].endswith("daily_proxy_evaluator_20260702.md"))
        self.assertIn("signal_outcomes", payload["input_counts"])
        self.assertIn("recommendation_codes", payload)
        self.assertIn("NO_TRADE_SPLIT_CANDIDATE", payload["recommendation_codes"])
        self.assertIn("AGGRESSION_RISK_REVIEW", payload["recommendation_codes"])
        self.assertIn("LONG_SHORT_BALANCE_REVIEW", payload["recommendation_codes"])
        self.assertIn("SUBJECT_TOO_DEFENSIVE_REVIEW", payload["recommendation_codes"])
        self.assertEqual(
            payload["safety_boundary"],
            "report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually",
        )


if __name__ == "__main__":
    unittest.main()
