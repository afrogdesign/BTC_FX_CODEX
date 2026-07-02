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

from tools.log_feedback import (  # noqa: E402
    _MEXC_TRADE_SIGNAL_LINK_HEADER,
    build_manual_trade_signal_link_rows,
    link_manual_trades_to_signals,
    score_manual_trade_signal_link,
)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return path


def _manual_trade_row(
    actual_trade_id: str,
    timestamp_jst: str,
    symbol: str,
    side: str,
    *,
    source_uid_hash: str = "uid_test",
) -> dict[str, str]:
    return {
        "actual_trade_id": actual_trade_id,
        "source_uid_hash": source_uid_hash,
        "source_file": "manual_actual_trades.csv",
        "timestamp_jst": timestamp_jst,
        "symbol": symbol,
        "side": side,
        "order_type": "Market",
        "fill_qty_contract": "1",
        "fill_qty_token": "0.01",
        "fill_qty_value": "1000",
        "fill_price": "100000",
        "fee": "0.1",
        "fee_asset": "USDT",
        "role": "Maker",
        "realized_pnl": "0",
        "import_status": "imported:trade_history",
    }


def _signal_review_row(signal_id: str, timestamp_jst: str, subject: str) -> dict[str, str]:
    return {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "subject": subject,
        "review_status": "done",
    }


def _signal_outcome_row(signal_id: str, timestamp_jst: str, bias: str, symbol: str = "") -> dict[str, str]:
    row = {
        "signal_id": signal_id,
        "timestamp_jst": timestamp_jst,
        "bias": bias,
    }
    if symbol:
        row["symbol"] = symbol
    return row


class ManualTradeSignalLinkerTest(unittest.TestCase):
    def test_score_manual_trade_signal_link_returns_expected_band(self) -> None:
        trade_row = _manual_trade_row("trade-high", "2026-07-01T09:50:00+09:00", "BTC_USDT", "long")
        signal_row = {
            "signal_id": "sig-high",
            "mail_timestamp_jst": "2026-07-01T09:20:00+09:00",
            "priority_direction": "long",
            "symbol": "BTC_USDT",
        }
        scored = score_manual_trade_signal_link(trade_row, signal_row, max_after_minutes=240)
        self.assertTrue(scored["eligible"])
        self.assertEqual(scored["link_score"], 8)
        self.assertEqual(scored["link_confidence"], "high")
        self.assertEqual(scored["side_match"], True)

    def test_link_rows_cover_high_medium_low_and_ambiguous_cases(self) -> None:
        manual_trades = [
            _manual_trade_row("trade-high", "2026-07-02T09:50:00+09:00", "BTC_USDT", "long"),
            _manual_trade_row("trade-medium", "2026-07-03T12:00:00+09:00", "BTC_USDT", "long"),
            _manual_trade_row("trade-low", "2026-07-01T08:00:00+09:00", "BTC_USDT", "long"),
            _manual_trade_row("trade-no-candidate", "2026-07-04T23:00:00+09:00", "BTC_USDT", "long"),
            _manual_trade_row("trade-tie", "2026-07-05T18:00:00+09:00", "BTC_USDT", "long"),
        ]
        signal_rows = [
            _signal_review_row("sig-high", "2026-07-02T09:20:00+09:00", "BTC fast follow"),
            _signal_review_row("sig-medium", "2026-07-03T10:00:00+09:00", "BTC later follow"),
            _signal_review_row("sig-low", "2026-07-01T07:30:00+09:00", "account-1234567890"),
            _signal_review_row("sig-far", "2026-07-04T18:00:00+09:00", "BTC far outside window"),
            _signal_review_row("sig-tie-a", "2026-07-05T17:20:00+09:00", "BTC tie a"),
            _signal_review_row("sig-tie-b", "2026-07-05T17:20:00+09:00", "BTC tie b"),
        ]
        signal_outcomes = [
            _signal_outcome_row("sig-high", "2026-07-02T09:20:00+09:00", "long", "BTC_USDT"),
            _signal_outcome_row("sig-medium", "2026-07-03T10:00:00+09:00", "long", "BTC_USDT"),
            _signal_outcome_row("sig-low", "2026-07-01T07:30:00+09:00", "short", "ETH_USDT"),
            _signal_outcome_row("sig-far", "2026-07-04T18:00:00+09:00", "long", "BTC_USDT"),
            _signal_outcome_row("sig-tie-a", "2026-07-05T17:20:00+09:00", "long", "BTC_USDT"),
            _signal_outcome_row("sig-tie-b", "2026-07-05T17:20:00+09:00", "long", "BTC_USDT"),
        ]

        rows = build_manual_trade_signal_link_rows(
            manual_trade_rows=manual_trades,
            signal_rows=signal_rows,
            signal_outcome_rows=signal_outcomes,
            max_after_minutes=240,
        )

        by_trade = {row["actual_trade_id"]: row for row in rows}
        self.assertEqual(by_trade["trade-high"]["signal_id"], "sig-high")
        self.assertEqual(by_trade["trade-high"]["link_confidence"], "high")
        self.assertEqual(by_trade["trade-high"]["link_score"], "9")
        self.assertEqual(by_trade["trade-medium"]["signal_id"], "sig-medium")
        self.assertEqual(by_trade["trade-medium"]["link_confidence"], "medium")
        self.assertEqual(by_trade["trade-medium"]["link_score"], "7")
        self.assertEqual(by_trade["trade-low"]["signal_id"], "sig-low")
        self.assertEqual(by_trade["trade-low"]["link_confidence"], "low")
        self.assertEqual(by_trade["trade-low"]["link_score"], "4")
        self.assertEqual(by_trade["trade-no-candidate"]["signal_id"], "")
        self.assertEqual(by_trade["trade-no-candidate"]["link_note"], "no_candidate")
        self.assertEqual(by_trade["trade-no-candidate"]["link_confidence"], "ambiguous")
        self.assertEqual(by_trade["trade-tie"]["signal_id"], "")
        self.assertEqual(by_trade["trade-tie"]["link_note"], "competing_candidate_tie")
        self.assertEqual(by_trade["trade-tie"]["link_confidence"], "ambiguous")

    def test_cli_dry_run_stdout_json_is_compact_and_private_safe(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manual_trades_path = _write_csv(
                root / "manual_actual_trades.csv",
                [
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
                ],
                [_manual_trade_row("trade-high", "2026-07-01T09:50:00+09:00", "BTC_USDT", "long")],
            )
            signals_path = _write_csv(
                root / "user_reviews.csv",
                ["signal_id", "timestamp_jst", "subject", "review_status"],
                [_signal_review_row("sig-high", "2026-07-01T09:20:00+09:00", "account-1234567890")],
            )
            signal_outcomes_path = _write_csv(
                root / "signal_outcomes.csv",
                ["signal_id", "timestamp_jst", "bias", "symbol"],
                [_signal_outcome_row("sig-high", "2026-07-01T09:20:00+09:00", "long", "BTC_USDT")],
            )
            output_csv = root / "manual_trade_signal_links.csv"

            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "link-manual-trades-to-signals",
                    "--manual-trades",
                    str(manual_trades_path),
                    "--signals",
                    str(signals_path),
                    "--signal-outcomes",
                    str(signal_outcomes_path),
                    "--output-csv",
                    str(output_csv),
                    "--dry-run",
                    "--stdout-json",
                ],
                cwd=BASE_DIR,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(result.stdout.endswith("\n"))
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["manual_trade_count"], 1)
            self.assertEqual(payload["linked_trade_count"], 1)
            self.assertNotIn("account-1234567890", result.stdout)
            self.assertFalse(output_csv.exists())

    def test_output_headers_match_required_headers_and_no_raw_uid_leaks(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manual_trades_path = _write_csv(
                root / "manual_actual_trades.csv",
                [
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
                ],
                [
                    _manual_trade_row("trade-high", "2026-07-01T09:50:00+09:00", "BTC_USDT", "long"),
                    _manual_trade_row("trade-medium", "2026-07-01T12:00:00+09:00", "BTC_USDT", "long"),
                ],
            )
            signals_path = _write_csv(
                root / "user_reviews.csv",
                ["signal_id", "timestamp_jst", "subject", "review_status"],
                [
                    _signal_review_row("sig-high", "2026-07-01T09:20:00+09:00", "BTC fast follow"),
                    _signal_review_row("sig-medium", "2026-07-01T10:00:00+09:00", "BTC later follow"),
                ],
            )
            signal_outcomes_path = _write_csv(
                root / "signal_outcomes.csv",
                ["signal_id", "timestamp_jst", "bias", "symbol"],
                [
                    _signal_outcome_row("sig-high", "2026-07-01T09:20:00+09:00", "long", "BTC_USDT"),
                    _signal_outcome_row("sig-medium", "2026-07-01T10:00:00+09:00", "long", "BTC_USDT"),
                ],
            )
            output_csv = root / "manual_trade_signal_links.csv"
            summary = link_manual_trades_to_signals(
                manual_trades=manual_trades_path,
                signals=signals_path,
                signal_outcomes=signal_outcomes_path,
                output_csv=output_csv,
                dry_run=False,
                max_after_minutes=240,
            )
            self.assertTrue(output_csv.exists())
            self.assertEqual(summary["output_written"], True)
            self.assertEqual(summary["manual_trade_count"], 2)

            with output_csv.open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            csv_text = output_csv.read_text(encoding="utf-8")
            self.assertEqual(list(rows[0].keys()), _MEXC_TRADE_SIGNAL_LINK_HEADER)
            self.assertEqual(len(rows), 2)
            self.assertNotIn("account-1234567890", csv_text)
            self.assertNotIn("uid_test", csv_text)

    def test_dry_run_writes_no_csv(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manual_trades_path = _write_csv(
                root / "manual_actual_trades.csv",
                [
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
                ],
                [_manual_trade_row("trade-high", "2026-07-01T09:50:00+09:00", "BTC_USDT", "long")],
            )
            signals_path = _write_csv(
                root / "user_reviews.csv",
                ["signal_id", "timestamp_jst", "subject", "review_status"],
                [_signal_review_row("sig-high", "2026-07-01T09:20:00+09:00", "BTC fast follow")],
            )
            signal_outcomes_path = _write_csv(
                root / "signal_outcomes.csv",
                ["signal_id", "timestamp_jst", "bias", "symbol"],
                [_signal_outcome_row("sig-high", "2026-07-01T09:20:00+09:00", "long", "BTC_USDT")],
            )
            output_csv = root / "manual_trade_signal_links.csv"
            summary = link_manual_trades_to_signals(
                manual_trades=manual_trades_path,
                signals=signals_path,
                signal_outcomes=signal_outcomes_path,
                output_csv=output_csv,
                dry_run=True,
                max_after_minutes=240,
            )
            self.assertFalse(output_csv.exists())
            self.assertEqual(summary["output_written"], False)
            self.assertEqual(summary["linked_trade_count"], 1)


if __name__ == "__main__":
    unittest.main()
