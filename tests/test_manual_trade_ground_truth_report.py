from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import build_manual_trade_ground_truth_report  # noqa: E402


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
    "bias",
    "prelabel",
    "symbol",
]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return path


def _write_headers_only(path: Path, fieldnames: list[str]) -> Path:
    return _write_csv(path, fieldnames, [])


def _trade_row(
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
        "import_status": "imported:trade_history",
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
    time_delta_minutes: str = "30",
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
        "time_delta_minutes": time_delta_minutes,
        "price_context_match": "unknown",
        "link_score": "9",
        "link_confidence": link_confidence,
        "link_note": link_note,
    }


def _signal_outcome_row(signal_id: str, timestamp_jst: str, bias: str, prelabel: str, symbol: str = "BTC_USDT") -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "bias": bias,
        "prelabel": prelabel,
        "symbol": symbol,
    }


class ManualTradeGroundTruthReportTest(unittest.TestCase):
    def test_missing_inputs_do_not_crash_and_include_safety_boundary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            report, payload = build_manual_trade_ground_truth_report(
                base_dir=base_dir,
                manual_trades=base_dir / "missing_manual.csv",
                links=base_dir / "missing_links.csv",
                signal_outcomes=base_dir / "missing_outcomes.csv",
                output_md=base_dir / "report.md",
                report_date="20260702",
                dry_run=False,
            )
            self.assertTrue((base_dir / "report.md").exists())
            self.assertIn("report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually", report)
            self.assertEqual(payload["input_counts"]["manual_trades"]["status"], "missing")
            self.assertEqual(payload["input_counts"]["links"]["status"], "missing")
            self.assertEqual(payload["input_counts"]["signal_outcomes"]["status"], "missing")
            self.assertIn("manual_actual_trades input is missing or header-only", report)
            self.assertNotIn("uid_sensitive_12345", report)

    def test_header_only_inputs_produce_zero_count_report(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manual_trades = _write_headers_only(base_dir / "logs" / "csv" / "manual_actual_trades.csv", MANUAL_TRADE_HEADERS)
            links = _write_headers_only(base_dir / "logs" / "csv" / "manual_trade_signal_links.csv", LINK_HEADERS)
            outcomes = _write_headers_only(base_dir / "logs" / "csv" / "signal_outcomes.csv", SIGNAL_OUTCOME_HEADERS)
            report, payload = build_manual_trade_ground_truth_report(
                base_dir=base_dir,
                manual_trades=manual_trades,
                links=links,
                signal_outcomes=outcomes,
                output_md=base_dir / "report.md",
                report_date="20260702",
                dry_run=False,
            )
            self.assertEqual(payload["total_actual_trades"], 0)
            self.assertEqual(payload["gross_realized_pnl"], 0.0)
            self.assertEqual(payload["net_pnl_after_fee"], 0.0)
            self.assertEqual(payload["win_rate"], 0.0)
            self.assertIn("status=header_only", report)
            self.assertIn("INSUFFICIENT_GROUND_TRUTH_DATA", report)

    def test_sample_aggregation_link_quality_and_calibration(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manual_trades = _write_csv(
                base_dir / "logs" / "csv" / "manual_actual_trades.csv",
                MANUAL_TRADE_HEADERS,
                [
                    _trade_row("trade-high", "2026-07-02T09:50:00+09:00", "BUY", "10", "1"),
                    _trade_row("trade-medium", "2026-07-03T12:00:00+09:00", "long", "-5", "0.5"),
                    _trade_row("trade-pessimistic", "2026-07-01T08:00:00+09:00", "short", "6", "0.2"),
                    _trade_row("trade-mismatch", "2026-07-04T09:00:00+09:00", "sell", "-2", ""),
                    _trade_row("trade-low", "2026-07-05T11:00:00+09:00", "BUY", "0", "0.1"),
                    _trade_row("trade-no-candidate", "2026-07-06T11:00:00+09:00", "unknown", "1", "0.2"),
                    _trade_row("trade-tie", "2026-07-07T11:00:00+09:00", "long", "-1", "0.1"),
                ],
            )
            links = _write_csv(
                base_dir / "logs" / "csv" / "manual_trade_signal_links.csv",
                LINK_HEADERS,
                [
                    _link_row("trade-high", "sig-high", "2026-07-02T09:20:00+09:00", "long", "long", "high", "matched_unique_top_candidate", time_delta_minutes="30"),
                    _link_row("trade-medium", "sig-medium", "2026-07-03T10:00:00+09:00", "long", "long", "medium", "matched_unique_top_candidate", time_delta_minutes="120"),
                    _link_row("trade-pessimistic", "sig-pessimistic", "2026-07-01T07:40:00+09:00", "short", "short", "high", "matched_unique_top_candidate", time_delta_minutes="20"),
                    _link_row("trade-mismatch", "sig-mismatch", "2026-07-04T08:45:00+09:00", "short", "long", "high", "matched_unique_top_candidate", side_match="no", time_delta_minutes="15"),
                    _link_row("trade-low", "sig-low", "2026-07-05T09:00:00+09:00", "long", "long", "low", "matched_unique_top_candidate", time_delta_minutes="120"),
                    _link_row("trade-no-candidate", "", "", "unknown", "", "ambiguous", "no_candidate", side_match="unknown", time_delta_minutes=""),
                    _link_row("trade-tie", "", "", "long", "", "ambiguous", "competing_candidate_tie", side_match="unknown", time_delta_minutes=""),
                ],
            )
            outcomes = _write_csv(
                base_dir / "logs" / "csv" / "signal_outcomes.csv",
                SIGNAL_OUTCOME_HEADERS,
                [
                    _signal_outcome_row("sig-high", "2026-07-02T09:20:00+09:00", "long", "ENTRY_OK"),
                    _signal_outcome_row("sig-medium", "2026-07-03T10:00:00+09:00", "long", "ENTRY_OK"),
                    _signal_outcome_row("sig-pessimistic", "2026-07-01T07:40:00+09:00", "short", "NO_TRADE_CANDIDATE"),
                    _signal_outcome_row("sig-mismatch", "2026-07-04T08:45:00+09:00", "long", "ENTRY_OK"),
                    _signal_outcome_row("sig-low", "2026-07-05T09:00:00+09:00", "long", "ENTRY_OK", symbol="ETH_USDT"),
                ],
            )
            report, payload = build_manual_trade_ground_truth_report(
                base_dir=base_dir,
                manual_trades=manual_trades,
                links=links,
                signal_outcomes=outcomes,
                output_md=base_dir / "report.md",
                report_date="20260702",
                dry_run=False,
            )
            self.assertEqual(payload["total_actual_trades"], 7)
            self.assertEqual(payload["gross_realized_pnl"], 9.0)
            self.assertEqual(payload["net_pnl_after_fee"], 6.9)
            self.assertEqual(payload["win_rate"], 0.4286)
            self.assertEqual(payload["link_confidence_counts"]["high"], 3)
            self.assertEqual(payload["link_confidence_counts"]["medium"], 1)
            self.assertEqual(payload["link_confidence_counts"]["low"], 1)
            self.assertEqual(payload["link_confidence_counts"]["ambiguous"], 2)
            self.assertEqual(payload["calibration_counts"]["manual_edge_confirmed"], 1)
            self.assertEqual(payload["calibration_counts"]["proxy_too_aggressive"], 1)
            self.assertEqual(payload["calibration_counts"]["proxy_too_pessimistic"], 1)
            self.assertEqual(payload["calibration_counts"]["direction_mismatch_loss"], 1)
            self.assertEqual(payload["calibration_counts"]["ambiguous_needs_review"], 3)
            self.assertIn("LINKAGE_COVERAGE_REVIEW", payload["recommendation_codes"])
            self.assertIn("FEE_COVERAGE_REVIEW", payload["recommendation_codes"])
            self.assertIn("AMBIGUOUS_LINK_MANUAL_REVIEW", payload["recommendation_codes"])
            self.assertIn("## 7. Proxy-vs-Actual Calibration", report)
            self.assertNotIn("uid_sensitive_12345", report)
            self.assertNotIn("account-1234567890", report)

    def test_cli_stdout_json_and_dry_run_write_no_markdown(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manual_trades = _write_csv(
                base_dir / "manual_actual_trades.csv",
                MANUAL_TRADE_HEADERS,
                [_trade_row("trade-high", "2026-07-02T09:50:00+09:00", "BUY", "10", "1")],
            )
            links = _write_csv(
                base_dir / "manual_trade_signal_links.csv",
                LINK_HEADERS,
                [
                    _link_row("trade-high", "sig-high", "2026-07-02T09:20:00+09:00", "long", "long", "high", "matched_unique_top_candidate", time_delta_minutes="30"),
                ],
            )
            outcomes = _write_csv(
                base_dir / "signal_outcomes.csv",
                SIGNAL_OUTCOME_HEADERS,
                [_signal_outcome_row("sig-high", "2026-07-02T09:20:00+09:00", "long", "ENTRY_OK")],
            )
            output_md = base_dir / "manual_trade_ground_truth_20260702.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "build-manual-trade-ground-truth-report",
                    "--manual-trades",
                    str(manual_trades),
                    "--links",
                    str(links),
                    "--signal-outcomes",
                    str(outcomes),
                    "--output-md",
                    str(output_md),
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
            self.assertEqual(payload["schema_version"], "manual_trade_ground_truth.v1")
            self.assertEqual(payload["report_date"], "20260702")
            self.assertFalse(output_md.exists())
            self.assertNotIn("uid_sensitive_12345", result.stdout)
            self.assertEqual(payload["safety_boundary"], "report-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually")


if __name__ == "__main__":
    unittest.main()
