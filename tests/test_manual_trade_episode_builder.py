from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.feedback.manual_trade_episode_builder import (
    EPISODE_HEADERS,
    build_manual_trade_episode_rows,
    build_manual_trade_episodes,
)


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
        self.assertEqual({row["side"] for row in rows}, {"unknown"})
        explicit = build_manual_trade_episode_rows(
            trade_rows=[_fill("long-open", "2026-07-01T10:00:00+09:00", side="long", action="open"), _fill("long-close", "2026-07-01T10:30:00+09:00", side="long", action="close")], order_rows=[], position_rows=[],
        )
        self.assertEqual(explicit[0]["side"], "long")
        short = build_manual_trade_episode_rows(
            trade_rows=[_fill("short-open", "2026-07-01T10:00:00+09:00", side="short", action="open"), _fill("short-close", "2026-07-01T10:30:00+09:00", side="short", action="close")], order_rows=[], position_rows=[],
        )
        self.assertEqual(short[0]["side"], "short")

    def test_side_conflict_and_ids_are_deterministic(self) -> None:
        inputs = {"trade_rows": [_fill("f1", "2026-07-01T10:05:00+09:00", side="short")], "order_rows": [], "position_rows": [_position()]}
        first = build_manual_trade_episode_rows(**inputs)
        second = build_manual_trade_episode_rows(**inputs)
        self.assertEqual(first, second)
        self.assertEqual(first[0]["association_status"], "ambiguous")
        self.assertIn("side_conflict", first[0]["association_reason_codes"])

    def test_dry_run_legacy_schema_and_malformed_timestamp(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            trades = root / "trades.csv"; orders = root / "orders.csv"; positions = root / "positions.csv"; output = root / "episodes.csv"
            _write(trades, ["symbol", "timestamp_jst"], [{"symbol": "BTCUSDT", "timestamp_jst": "2026-07-01T10:00:00+09:00"}])
            _write(orders, ["symbol"], [])
            _write(positions, ["symbol"], [])
            summary = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output, dry_run=True)
            self.assertTrue(summary["ok"])
            self.assertFalse(output.exists())
            _write(positions, ["symbol", "episode_id"], [{"symbol": "BTCUSDT", "episode_id": "legacy"}])
            _write(trades, ["symbol", "timestamp_jst"], [{"symbol": "BTCUSDT", "timestamp_jst": "bad"}])
            invalid = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output)
            self.assertEqual(invalid["exit_code"], 2)
            _write(output, ["legacy"], [{"legacy": "1"}])
            valid = build_manual_trade_episodes(trades=trades, orders=orders, positions=positions, output_csv=output)
            self.assertEqual(valid["exit_code"], 2)


if __name__ == "__main__":
    unittest.main()
