from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import mock

import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import (  # noqa: E402
    build_post_eval_recommendations_handoff_contract,
    build_post_eval_recommendation_candidates,
    build_post_eval_recommendation_report,
    rank_post_eval_recommendation_candidates,
    normalize_post_eval_recommendations_handoff,
    validate_post_eval_recommendations_contract,
    validate_post_eval_recommendations_handoff_contract,
)
import tools.log_feedback as log_feedback  # noqa: E402


MANUAL_TRADE_HEADERS = [
    "actual_trade_id",
    "source_uid_hash",
    "source_file",
    "timestamp_jst",
    "symbol",
    "side",
    "order_type",
    "fill_qty_contract",
    "fill_qty_token",
    "fill_qty_value",
    "fill_price",
    "fee",
    "fee_asset",
    "role",
    "realized_pnl",
    "import_status",
]

LINK_HEADERS = [
    "actual_trade_id",
    "signal_id",
    "mail_timestamp_jst",
    "trade_opened_at_jst",
    "trade_closed_at_jst",
    "actual_side",
    "priority_direction",
    "side_match",
    "time_delta_minutes",
    "price_context_match",
    "link_score",
    "link_confidence",
    "link_note",
]

SIGNAL_OUTCOME_HEADERS = [
    "signal_id",
    "timestamp_jst",
    "prelabel",
    "candidate_delta_24h",
    "direction_outcome",
    "outcome",
    "signal_based_MFE_24h",
    "signal_based_MAE_24h",
    "bias",
]

USER_REVIEW_HEADERS = ["signal_id", "timestamp_jst", "subject"]

ACTIVE_PLAN_OUTCOME_HEADERS = ["signal_id", "timestamp_jst", "side", "candidate_type", "active_primary_action"]

INTRAPERIOD_OUTCOME_HEADERS = [
    "signal_id",
    "timestamp_jst",
    "side",
    "candidate_type",
    "active_primary_action",
    "sl_first",
    "mae_r",
    "notes",
    "first_exit_reason",
]

CSV_HEADERS = [
    "recommendation_id",
    "recommendation_code",
    "rank",
    "priority",
    "confidence",
    "evidence_score",
    "affected_area",
    "proposed_action",
    "evidence_summary",
    "required_human_approval",
    "safety_note",
]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return path


def _headers_only(path: Path, fieldnames: list[str]) -> Path:
    return _write_csv(path, fieldnames, [])


def _manual_trade_row(
    actual_trade_id: str,
    timestamp_jst: str,
    side: str,
    realized_pnl: str,
    fee: str,
    *,
    source_uid_hash: str = "uid_sensitive_12345",
) -> dict[str, str]:
    return {
        "actual_trade_id": actual_trade_id,
        "source_uid_hash": source_uid_hash,
        "source_file": "manual_actual_trades.csv",
        "timestamp_jst": timestamp_jst,
        "symbol": "BTC_USDT",
        "side": side,
        "order_type": "Market",
        "fill_qty_contract": "1",
        "fill_qty_token": "0.01",
        "fill_qty_value": "1000",
        "fill_price": "100000",
        "fee": fee,
        "fee_asset": "USDT",
        "role": "Maker",
        "realized_pnl": realized_pnl,
        "import_status": "imported",
    }


def _link_row(
    actual_trade_id: str,
    signal_id: str,
    mail_timestamp_jst: str,
    actual_side: str,
    priority_direction: str,
    link_confidence: str,
    link_note: str,
    *,
    side_match: str = "yes",
) -> dict[str, str]:
    return {
        "actual_trade_id": actual_trade_id,
        "signal_id": signal_id,
        "mail_timestamp_jst": mail_timestamp_jst,
        "trade_opened_at_jst": "",
        "trade_closed_at_jst": "",
        "actual_side": actual_side,
        "priority_direction": priority_direction,
        "side_match": side_match,
        "time_delta_minutes": "30",
        "price_context_match": "unknown",
        "link_score": "9",
        "link_confidence": link_confidence,
        "link_note": link_note,
    }


def _signal_outcome_row(signal_id: str, timestamp_jst: str, prelabel: str, candidate_delta_24h: str, *, outcome: str = "positive") -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "prelabel": prelabel,
        "candidate_delta_24h": candidate_delta_24h,
        "direction_outcome": outcome,
        "outcome": outcome,
        "signal_based_MFE_24h": candidate_delta_24h,
        "signal_based_MAE_24h": "0.5",
        "bias": "long",
    }


def _active_plan_row(signal_id: str, timestamp_jst: str, side: str, candidate_type: str, active_primary_action: str) -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "side": side,
        "candidate_type": candidate_type,
        "active_primary_action": active_primary_action,
    }


def _intraperiod_row(
    signal_id: str,
    timestamp_jst: str,
    side: str,
    candidate_type: str,
    active_primary_action: str,
    *,
    sl_first: str = "false",
    mae_r: str = "0.0",
    notes: str = "",
    first_exit_reason: str = "",
) -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "side": side,
        "candidate_type": candidate_type,
        "active_primary_action": active_primary_action,
        "sl_first": sl_first,
        "mae_r": mae_r,
        "notes": notes,
        "first_exit_reason": first_exit_reason,
    }


def _build_complete_inputs(base_dir: Path) -> dict[str, Path]:
    manual_trades = _write_csv(
        base_dir / "manual_actual_trades.csv",
        MANUAL_TRADE_HEADERS,
        [
            _manual_trade_row("trade-aggressive-loss", "2026-07-02T09:00:00+09:00", "long", "-3", "0.2"),
            _manual_trade_row("trade-pessimistic-win", "2026-07-02T10:00:00+09:00", "short", "4", "0.2"),
            _manual_trade_row("trade-fee-missing", "2026-07-03T10:00:00+09:00", "long", "1", ""),
            _manual_trade_row("trade-ambiguous", "2026-07-04T10:00:00+09:00", "short", "0", "0.1"),
        ],
    )
    links = _write_csv(
        base_dir / "manual_trade_signal_links.csv",
        LINK_HEADERS,
        [
            _link_row("trade-aggressive-loss", "sig-aggressive", "2026-07-02T08:30:00+09:00", "long", "long", "high", "matched_unique_top_candidate"),
            _link_row("trade-pessimistic-win", "sig-pessimistic", "2026-07-02T09:30:00+09:00", "short", "short", "high", "matched_unique_top_candidate"),
            _link_row("trade-fee-missing", "sig-fee", "2026-07-03T09:30:00+09:00", "long", "long", "medium", "matched_unique_top_candidate"),
            _link_row("trade-ambiguous", "", "", "short", "", "ambiguous", "no_candidate", side_match="unknown"),
            _link_row("trade-tie", "", "", "short", "", "ambiguous", "competing_candidate_tie", side_match="unknown"),
        ],
    )
    signal_outcomes = _write_csv(
        base_dir / "signal_outcomes.csv",
        SIGNAL_OUTCOME_HEADERS,
        [
            _signal_outcome_row("sig-no-trade", "2026-07-02T08:00:00+09:00", "NO_TRADE_CANDIDATE", "1.8", outcome="positive"),
            _signal_outcome_row("sig-defensive", "2026-07-02T08:05:00+09:00", "WATCH", "1.2", outcome="positive"),
            _signal_outcome_row("sig-aggressive", "2026-07-02T08:30:00+09:00", "ENTRY_OK", "-0.8", outcome="negative"),
            _signal_outcome_row("sig-pessimistic", "2026-07-02T09:30:00+09:00", "SKIP", "2.1", outcome="positive"),
            _signal_outcome_row("sig-fee", "2026-07-03T09:30:00+09:00", "ENTRY_OK", "0.5", outcome="positive"),
        ],
    )
    user_reviews = _write_csv(
        base_dir / "user_reviews.csv",
        USER_REVIEW_HEADERS,
        [
            {"signal_id": "sig-defensive", "timestamp_jst": "2026-07-02T08:05:00+09:00", "subject": "売買非推奨 / skip review"},
        ],
    )
    active_plan_outcomes = _write_csv(
        base_dir / "active_plan_candidate_outcomes.csv",
        ACTIVE_PLAN_OUTCOME_HEADERS,
        [
            *[_active_plan_row(f"sig-long-{idx}", f"2026-07-02T0{idx}:00:00+09:00", "long", "active_market_small", "review") for idx in range(1, 7)],
            _active_plan_row("sig-long-7", "2026-07-02T07:00:00+09:00", "long", "active_market_small", "review"),
            _active_plan_row("sig-short-1", "2026-07-02T08:00:00+09:00", "short", "active_market_small", "review"),
            _active_plan_row("sig-short-2", "2026-07-02T09:00:00+09:00", "short", "active_market_small", "review"),
        ],
    )
    intraperiod_outcomes = _write_csv(
        base_dir / "active_plan_candidate_intraperiod_outcomes.csv",
        INTRAPERIOD_OUTCOME_HEADERS,
        [
            _intraperiod_row("sig-turn-1", "2026-07-02T08:10:00+09:00", "long", "turning_counter", "counter", sl_first="true", mae_r="1.5", notes="turning caution"),
            _intraperiod_row("sig-turn-2", "2026-07-02T08:20:00+09:00", "short", "counter_reversal", "counter", sl_first="true", mae_r="1.6", notes="countertrend"),
        ],
    )
    return {
        "manual_trades": manual_trades,
        "links": links,
        "signal_outcomes": signal_outcomes,
        "user_reviews": user_reviews,
        "active_plan_candidate_outcomes": active_plan_outcomes,
        "active_plan_candidate_intraperiod_outcomes": intraperiod_outcomes,
    }


class PostEvalRecommendationEngineTest(unittest.TestCase):
    def test_missing_inputs_write_insufficient_candidate_and_safety_boundary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            report, payload = build_post_eval_recommendation_report(
                base_dir=base_dir,
                signal_outcomes=base_dir / "missing_signal_outcomes.csv",
                active_plan_candidate_outcomes=base_dir / "missing_candidate_outcomes.csv",
                active_plan_candidate_intraperiod_outcomes=base_dir / "missing_intraperiod.csv",
                user_reviews=base_dir / "missing_user_reviews.csv",
                manual_trades=base_dir / "missing_manual_trades.csv",
                links=base_dir / "missing_links.csv",
                output_md=base_dir / "post_eval_recommendations_20260702.md",
                output_csv=base_dir / "post_eval_recommendation_candidates.csv",
                report_date="20260702",
                dry_run=False,
            )
            self.assertTrue((base_dir / "post_eval_recommendations_20260702.md").exists())
            self.assertTrue((base_dir / "post_eval_recommendation_candidates.csv").exists())
            self.assertIn("INSUFFICIENT_EVIDENCE", report)
            self.assertIn("status=missing", report)
            self.assertIn("report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually", report)
            self.assertEqual(payload["candidate_count"], 1)
            self.assertEqual(payload["top_recommendation_codes"], ["INSUFFICIENT_EVIDENCE"])
            self.assertNotIn("uid_sensitive_12345", report)

    def test_header_only_inputs_produce_zero_or_insufficient_candidate_report(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            inputs = {
                "manual_trades": _headers_only(base_dir / "manual_actual_trades.csv", MANUAL_TRADE_HEADERS),
                "links": _headers_only(base_dir / "manual_trade_signal_links.csv", LINK_HEADERS),
                "signal_outcomes": _headers_only(base_dir / "signal_outcomes.csv", SIGNAL_OUTCOME_HEADERS),
                "user_reviews": _headers_only(base_dir / "user_reviews.csv", USER_REVIEW_HEADERS),
                "active_plan_candidate_outcomes": _headers_only(base_dir / "active_plan_candidate_outcomes.csv", ACTIVE_PLAN_OUTCOME_HEADERS),
                "active_plan_candidate_intraperiod_outcomes": _headers_only(base_dir / "active_plan_candidate_intraperiod_outcomes.csv", INTRAPERIOD_OUTCOME_HEADERS),
            }
            report, payload = build_post_eval_recommendation_report(
                base_dir=base_dir,
                signal_outcomes=inputs["signal_outcomes"],
                active_plan_candidate_outcomes=inputs["active_plan_candidate_outcomes"],
                active_plan_candidate_intraperiod_outcomes=inputs["active_plan_candidate_intraperiod_outcomes"],
                user_reviews=inputs["user_reviews"],
                manual_trades=inputs["manual_trades"],
                links=inputs["links"],
                output_md=base_dir / "post_eval_recommendations_20260702.md",
                output_csv=base_dir / "post_eval_recommendation_candidates.csv",
                report_date="20260702",
                dry_run=False,
            )
            self.assertIn("status=header_only", report)
            self.assertIn("INSUFFICIENT_EVIDENCE", report)
            self.assertEqual(payload["candidate_count"], 1)
            with (base_dir / "post_eval_recommendation_candidates.csv").open("r", encoding="utf-8", newline="") as fp:
                reader = csv.DictReader(fp)
                self.assertEqual(reader.fieldnames, CSV_HEADERS)
                rows = list(reader)
            self.assertEqual(rows[0]["recommendation_code"], "INSUFFICIENT_EVIDENCE")
            self.assertNotIn("uid_sensitive_12345", report)

    def test_sample_inputs_cover_review_candidates_and_sorted_ranking(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            inputs = _build_complete_inputs(base_dir)
            candidates, summary = build_post_eval_recommendation_candidates(
                base_dir=base_dir,
                signal_outcomes=inputs["signal_outcomes"],
                active_plan_candidate_outcomes=inputs["active_plan_candidate_outcomes"],
                active_plan_candidate_intraperiod_outcomes=inputs["active_plan_candidate_intraperiod_outcomes"],
                user_reviews=inputs["user_reviews"],
                manual_trades=inputs["manual_trades"],
                links=inputs["links"],
                report_date="20260702",
            )
            ranked = rank_post_eval_recommendation_candidates(
                candidates,
                report_date=summary["report_date"],
                coverage_complete=all(item["status"] == "ok" for item in summary["coverage"].values()),
            )
            self.assertEqual([row["rank"] for row in ranked], list(range(1, len(ranked) + 1)))
            self.assertEqual([row["evidence_score"] for row in ranked], sorted((row["evidence_score"] for row in ranked), reverse=True))
            codes = {row["recommendation_code"] for row in ranked}
            for expected_code in {
                "NO_TRADE_SPLIT_REVIEW",
                "SUBJECT_DEFENSIVE_WORDING_REVIEW",
                "LONG_SHORT_BALANCE_REVIEW",
                "TURNING_BRAKE_REVIEW",
                "PROXY_TOO_AGGRESSIVE_REVIEW",
                "PROXY_TOO_PESSIMISTIC_REVIEW",
                "LINKAGE_COVERAGE_REVIEW",
                "FEE_COVERAGE_REVIEW",
                "AMBIGUOUS_LINK_MANUAL_REVIEW",
            }:
                self.assertIn(expected_code, codes)

            report, payload = build_post_eval_recommendation_report(
                base_dir=base_dir,
                signal_outcomes=inputs["signal_outcomes"],
                active_plan_candidate_outcomes=inputs["active_plan_candidate_outcomes"],
                active_plan_candidate_intraperiod_outcomes=inputs["active_plan_candidate_intraperiod_outcomes"],
                user_reviews=inputs["user_reviews"],
                manual_trades=inputs["manual_trades"],
                links=inputs["links"],
                output_md=base_dir / "post_eval_recommendations_20260702.md",
                output_csv=base_dir / "post_eval_recommendation_candidates.csv",
                report_date="20260702",
                dry_run=False,
            )
            self.assertIn("# Post-Eval Recommendation Engine", report)
            self.assertIn("Human approval is required before any production wording/config/threshold/gate/runtime changes.", report)
            self.assertIn("report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually", report)
            self.assertNotIn("uid_sensitive_12345", report)
            self.assertNotIn("account-1234567890", report)
            self.assertGreaterEqual(payload["candidate_count"], 9)
            with (base_dir / "post_eval_recommendation_candidates.csv").open("r", encoding="utf-8", newline="") as fp:
                reader = csv.DictReader(fp)
                self.assertEqual(reader.fieldnames, CSV_HEADERS)
                rows = list(reader)
            self.assertEqual([row["rank"] for row in rows], [str(i) for i in range(1, len(rows) + 1)])
            self.assertIn("NO_TRADE_SPLIT_REVIEW", {row["recommendation_code"] for row in rows})
            self.assertNotIn("uid_sensitive_12345", json.dumps(payload, ensure_ascii=False))

    def test_cli_stdout_json_and_dry_run_write_no_files(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            inputs = _build_complete_inputs(base_dir)
            output_md = base_dir / "post_eval_recommendations_20260702.md"
            output_csv = base_dir / "post_eval_recommendation_candidates.csv"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "build-post-eval-recommendations",
                    "--signal-outcomes",
                    str(inputs["signal_outcomes"]),
                    "--active-plan-candidate-outcomes",
                    str(inputs["active_plan_candidate_outcomes"]),
                    "--active-plan-candidate-intraperiod-outcomes",
                    str(inputs["active_plan_candidate_intraperiod_outcomes"]),
                    "--user-reviews",
                    str(inputs["user_reviews"]),
                    "--manual-trades",
                    str(inputs["manual_trades"]),
                    "--links",
                    str(inputs["links"]),
                    "--output-md",
                    str(output_md),
                    "--output-csv",
                    str(output_csv),
                    "--date",
                    "20260702",
                    "--dry-run",
                    "--stdout-json",
                ],
                cwd=BASE_DIR,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["schema_version"], "post_eval_recommendations.v1")
            self.assertEqual(payload["report_date"], "20260702")
            self.assertFalse(output_md.exists())
            self.assertFalse(output_csv.exists())
            self.assertIn("top_recommendation_codes", payload)
            self.assertIn("safety_boundary", payload)
            self.assertEqual(payload["safety_boundary"], "report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually")
            self.assertNotIn("uid_sensitive_12345", result.stdout)

    def test_post_eval_recommendations_handoff_contract_sanitizes_and_uses_no_engine_generation(self) -> None:
        payload = {
            "schema_version": "post_eval_recommendations.v1",
            "report_date": "20260702",
            "report_path": "uid-ABC123/account_test/<script>post_eval.md",
            "output_csv_path": "logs/csv/uid-ABC123-account_test.csv",
            "candidate_count": 3,
            "top_recommendation_codes": [
                "PROXY_TOO_AGGRESSIVE_REVIEW",
                "uid-ABC123",
                "fetch(",
            ],
            "priority_counts": {"high": 2, "medium": 1, "uid-ABC123": 9},
            "confidence_counts": {"actual_backed": 1, "proxy_backed": 2},
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually / private/order",
            "note": "report-only status <script> fetch( send_email Gmail smtp OPENAI_API_KEY SMTP_PASSWORD source_uid_hash uid-ABC123 account_test",
            "human_approval_required": True,
        }

        with mock.patch.object(
            log_feedback,
            "build_post_eval_recommendation_report",
            side_effect=AssertionError("recommendation engine must not run while building handoff contracts"),
        ):
            handoff_payload = build_post_eval_recommendations_handoff_contract(payload)
            alias_payload = normalize_post_eval_recommendations_handoff(payload)
            ready_gate = validate_post_eval_recommendations_handoff_contract(payload)
            contract_gate = validate_post_eval_recommendations_contract(payload)

        self.assertEqual(handoff_payload, alias_payload)
        self.assertEqual(ready_gate, contract_gate)
        self.assertIsInstance(handoff_payload, dict)
        self.assertEqual(handoff_payload["schema_version"], "post_eval_recommendations.v1")
        self.assertEqual(handoff_payload["report_date"], "20260702")
        self.assertEqual(handoff_payload["candidate_count"], 3)
        self.assertEqual(handoff_payload["human_approval_required"], True)
        self.assertNotIn("source_uid_hash", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("uid-ABC123", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("account_test", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("<script", json.dumps(handoff_payload, ensure_ascii=False).lower())
        self.assertNotIn("fetch(", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("send_email", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("Gmail", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("smtp", json.dumps(handoff_payload, ensure_ascii=False).lower())
        self.assertNotIn("private/order", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("OPENAI_API_KEY", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertNotIn("SMTP_PASSWORD", json.dumps(handoff_payload, ensure_ascii=False))
        self.assertTrue(ready_gate["post_eval_recommendations_present"])
        self.assertTrue(ready_gate["post_eval_recommendations_ready"])
        self.assertEqual(ready_gate["post_eval_recommendations_status"], "ready")

    def test_post_eval_recommendations_handoff_contract_handles_absent_and_invalid_states(self) -> None:
        absent_gate = validate_post_eval_recommendations_handoff_contract(None)
        absent_payload = build_post_eval_recommendations_handoff_contract(None)
        malformed_gate = validate_post_eval_recommendations_handoff_contract({"_malformed": True})
        wrong_schema_gate = validate_post_eval_recommendations_handoff_contract(
            {
                "schema_version": "post_eval_recommendations.v0",
                "candidate_count": 1,
                "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                "human_approval_required": True,
            }
        )
        false_approval_gate = validate_post_eval_recommendations_handoff_contract(
            {
                "schema_version": "post_eval_recommendations.v1",
                "candidate_count": 1,
                "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                "human_approval_required": False,
            }
        )
        missing_boundary_gate = validate_post_eval_recommendations_handoff_contract(
            {
                "schema_version": "post_eval_recommendations.v1",
                "candidate_count": 1,
                "human_approval_required": True,
            }
        )
        invalid_count_gate = validate_post_eval_recommendations_handoff_contract(
            {
                "schema_version": "post_eval_recommendations.v1",
                "candidate_count": "three",
                "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                "human_approval_required": True,
            }
        )

        self.assertIsNone(absent_payload)
        self.assertTrue(absent_gate["post_eval_recommendations_ready"])
        self.assertEqual(absent_gate["post_eval_recommendations_status"], "optional_not_present")
        self.assertFalse(absent_gate["post_eval_recommendations_present"])
        self.assertEqual(malformed_gate["post_eval_recommendations_status"], "invalid_not_ready")
        self.assertIn("malformed_payload", malformed_gate["post_eval_recommendations_reason_codes"])
        self.assertEqual(wrong_schema_gate["post_eval_recommendations_status"], "invalid_not_ready")
        self.assertIn("schema_version_mismatch", wrong_schema_gate["post_eval_recommendations_reason_codes"])
        self.assertEqual(false_approval_gate["post_eval_recommendations_status"], "invalid_not_ready")
        self.assertIn("human_approval_required_false", false_approval_gate["post_eval_recommendations_reason_codes"])
        self.assertEqual(missing_boundary_gate["post_eval_recommendations_status"], "invalid_not_ready")
        self.assertIn("safety_boundary_invalid", missing_boundary_gate["post_eval_recommendations_reason_codes"])
        self.assertEqual(invalid_count_gate["post_eval_recommendations_status"], "invalid_not_ready")
        self.assertIn("candidate_count_invalid", invalid_count_gate["post_eval_recommendations_reason_codes"])


if __name__ == "__main__":
    unittest.main()
