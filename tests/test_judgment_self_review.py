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
    build_judgment_self_review_report,
    build_judgment_self_review_rows,
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
