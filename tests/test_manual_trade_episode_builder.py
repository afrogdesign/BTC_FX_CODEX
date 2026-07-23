from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.feedback.manual_trade_episode_builder import (
    EPISODE_HEADERS,
    build_manual_trade_episode_rows,
    build_manual_trade_episodes,
)
from src.feedback.manual_actual_trade_importer import ORDER_HEADERS, POSITION_HEADERS, TRADE_HEADERS
from src.feedback.manual_trade_signal_linker import LINK_HEADERS


def _position(position_id: str = "pos-1", side: str = "long", opened: str = "2026-07-01T10:00:00+09:00", closed: str = "2026-07-01T11:00:00+09:00") -> dict[str, str]:
    return {"actual_position_id": position_id, "symbol": "BTCUSDT", "side": side, "opened_at_jst": opened, "closed_at_jst": closed, "status": "closed", "realized_pnl": "10"}


def _fill(fill_id: str, timestamp: str, *, side: str = "", action: str = "", fee: str = "1", pnl: str = "") -> dict[str, str]:
    return {"actual_trade_id": fill_id, "symbol": "BTCUSDT", "side": side, "position_action": action, "timestamp_jst": timestamp, "fee": fee, "realized_pnl": pnl}


def _order(order_id: str, timestamp: str) -> dict[str, str]:
    return {"actual_order_id": order_id, "symbol": "BTCUSDT", "timestamp_jst": timestamp, "status": "partially_filled"}


def _write(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=headers)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in headers} for row in rows)


class ManualTradeEpisodeBuilderTest(unittest.TestCase):
    def test_position_with_multiple_fills_and_order_is_one_episode(self) -> None:
        rows = build_manual_trade_episode_rows(
            trade_rows=[_fill("f1", "2026-07-01T10:05:00+09:00"), _fill("f2", "2026-07-01T10:10:00+09:00")],
            order_rows=[_order("o1", "2026-07-01T10:04:00+09:00")], position_rows=[_position()],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["fill_count"], "2")
        self.assertEqual(rows[0]["order_count"], "1")
        self.assertEqual(rows[0]["episode_source"], "position_backed")

    def test_overlapping_positions_mark_competing_association_ambiguous(self) -> None:
        rows = build_manual_trade_episode_rows(
            trade_rows=[_fill("f1", "2026-07-01T10:30:00+09:00")], order_rows=[],
            position_rows=[_position("p1"), _position("p2", opened="2026-07-01T10:20:00+09:00", closed="2026-07-01T11:20:00+09:00")],
        )
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["association_status"] == "ambiguous" for row in rows))
        self.assertTrue(all(row["fill_count"] == "0" for row in rows))

    def test_buy_only_and_sell_only_derived_evidence_stays_unknown(self) -> None:
        rows = build_manual_trade_episode_rows(
            trade_rows=[_fill("buy", "2026-07-01T10:00:00+09:00", side="unknown", action="") , _fill("sell", "2026-07-01T10:01:00+09:00", side="unknown", action="")],
            order_rows=[], position_rows=[],
        )
        self.assertEqual(rows, [])
        explicit = build_manual_trade_episode_rows(
            trade_rows=[_fill("long-open", "2026-07-01T10:00:00+09:00", side="long", action="open"), _fill("long-close", "2026-07-01T10:30:00+09:00", side="long", action="close")], order_rows=[], position_rows=[],
        )
        self.assertEqual(explicit, [])
        short = build_manual_trade_episode_rows(
            trade_rows=[_fill("short-open", "2026-07-01T10:00:00+09:00", side="short", action="open"), _fill("short-close", "2026-07-01T10:30:00+09:00", side="short", action="close")], order_rows=[], position_rows=[],
        )
        self.assertEqual(short, [])

    def test_side_conflict_and_ids_are_deterministic(self) -> None:
        inputs = {"trade_rows": [_fill("f1", "2026-07-01T10:05:00+09:00", side="short")], "order_rows": [], "position_rows": [_position()]}
        first = build_manual_trade_episode_rows(**inputs)
        second = build_manual_trade_episode_rows(**inputs)
        self.assertEqual(first, second)
        self.assertEqual(first[0]["association_status"], "ambiguous")
        self.assertIn("side_conflict", first[0]["association_reason_codes"])

    def test_status_resolution_uses_close_timestamp_only_for_unknown_status(self) -> None:
        unknown_closed = build_manual_trade_episode_rows(
            trade_rows=[], order_rows=[], position_rows=[_position() | {"status": "unknown"}]
        )[0]
        unknown_open = build_manual_trade_episode_rows(
            trade_rows=[], order_rows=[], position_rows=[_position(closed="") | {"status": "unknown"}]
        )[0]
        explicit_closed = build_manual_trade_episode_rows(
            trade_rows=[], order_rows=[], position_rows=[_position() | {"status": "closed"}]
        )[0]
        explicit_open = build_manual_trade_episode_rows(
            trade_rows=[], order_rows=[], position_rows=[_position(closed="") | {"status": "open"}]
        )[0]
        self.assertEqual(unknown_closed["status"], "closed")
        self.assertEqual(unknown_open["status"], "unknown")
        self.assertEqual(explicit_closed["status"], "closed")
        self.assertEqual(explicit_open["status"], "open")

    def test_dry_run_legacy_schema_and_malformed_timestamp(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            trades = root / "trades.csv"; orders = root / "orders.csv"; positions = root / "positions.csv"; output = root / "episodes.csv"
            _write(trades, ["symbol", "timestamp_jst"], [{"symbol": "BTCUSDT", "timestamp_jst": "2026-07-01T10:00:00+09:00"}])
            _write(orders, ["symbol"], [])
            _write(positions, ["symbol"], [])
            summary = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output, dry_run=True)
            self.assertFalse(summary["ok"])
            self.assertEqual(summary["exit_code"], 2)
            self.assertFalse(output.exists())
            _write(positions, ["symbol", "episode_id"], [{"symbol": "BTCUSDT", "episode_id": "legacy"}])
            _write(trades, ["symbol", "timestamp_jst"], [{"symbol": "BTCUSDT", "timestamp_jst": "bad"}])
            invalid = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output)
            self.assertEqual(invalid["exit_code"], 2)
            _write(output, ["legacy"], [{"legacy": "1"}])
            self.assertTrue(output.exists())

    def test_three_v2_cli_routes_emit_compact_json(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            trades = root / "trades.csv"; orders = root / "orders.csv"; positions = root / "positions.csv"
            trade = {field: "" for field in TRADE_HEADERS}; trade.update(schema_version="manual_actual_trade.v2", actual_trade_id="t1", symbol="BTCUSDT", timestamp_jst="2026-07-01T10:05:00+09:00", fee="0", realized_pnl="0")
            order = {field: "" for field in ORDER_HEADERS}; order.update(schema_version="manual_actual_trade.v2", actual_order_id="o1", symbol="BTCUSDT", timestamp_jst="2026-07-01T10:05:00+09:00")
            position = {field: "" for field in POSITION_HEADERS}; position.update(schema_version="manual_actual_trade.v2", actual_position_id="p1", symbol="BTCUSDT", side="long", opened_at_jst="2026-07-01T10:00:00+09:00", closed_at_jst="2026-07-01T11:00:00+09:00", status="closed", realized_pnl="0", fee_total="0")
            _write(trades, TRADE_HEADERS, [trade]); _write(orders, ORDER_HEADERS, [order]); _write(positions, POSITION_HEADERS, [position])
            episodes = root / "episodes.csv"; links = root / "links.csv"; report = root / "report.md"; signals = root / "signals.csv"; outcomes = root / "outcomes.csv"
            _write(signals, ["signal_id", "timestamp_jst", "bias", "symbol"], [{"signal_id": "s1", "timestamp_jst": "2026-07-01T09:50:00+09:00", "bias": "long", "symbol": "BTCUSDT", "notification_kind": "attention"}])
            _write(outcomes, ["signal_id"], [{"signal_id": "s1"}])
            script = str(Path(__file__).parents[1] / "tools" / "log_feedback.py")
            episode_cmd = [sys.executable, script, "build-manual-trade-episodes", "--trades", str(trades), "--orders", str(orders), "--positions", str(positions), "--output-csv", str(episodes), "--stdout-json"]
            episode_result = subprocess.run(episode_cmd, cwd=Path(__file__).parents[1], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(episode_result.stdout)["schema_version"], "manual_trade_episode.v1")
            link_cmd = [sys.executable, script, "link-manual-trades-to-signals", "--episodes", str(episodes), "--signals", str(signals), "--signal-outcomes", str(outcomes), "--output-csv", str(links), "--max-lookback-minutes", "240", "--stdout-json"]
            link_result = subprocess.run(link_cmd, cwd=Path(__file__).parents[1], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(link_result.stdout)["schema_version"], "manual_trade_signal_link.v2")
            report_cmd = [sys.executable, script, "build-manual-trade-ground-truth-report", "--trades", str(trades), "--orders", str(orders), "--positions", str(positions), "--episodes", str(episodes), "--links", str(links), "--signal-outcomes", str(outcomes), "--output-md", str(report), "--stdout-json"]
            report_result = subprocess.run(report_cmd, cwd=Path(__file__).parents[1], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(report_result.stdout)["schema_version"], "manual_trade_ground_truth.v2")
            self.assertTrue(report.exists())

    def test_header_only_exact_contract_and_wrong_headers_fail_closed(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            trades, orders, positions, output = (root / name for name in ("trades.csv", "orders.csv", "positions.csv", "episodes.csv"))
            _write(trades, TRADE_HEADERS, []); _write(orders, ORDER_HEADERS, []); _write(positions, POSITION_HEADERS, [])
            valid = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output, dry_run=True)
            self.assertTrue(valid["ok"])
            for bad_headers in (TRADE_HEADERS[:-1], TRADE_HEADERS + ["extra"], TRADE_HEADERS[1:] + TRADE_HEADERS[:1]):
                _write(trades, bad_headers, [])
                invalid = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output)
                self.assertEqual(invalid["exit_code"], 2)
                self.assertIn("input_schema_mismatch", invalid["errors"])
            _write(trades, TRADE_HEADERS, [{field: ("wrong.version" if field == "schema_version" else "") for field in TRADE_HEADERS}])
            invalid_version = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output)
            self.assertEqual(invalid_version["exit_code"], 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
