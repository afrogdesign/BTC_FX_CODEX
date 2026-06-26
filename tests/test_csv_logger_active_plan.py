from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.storage.csv_logger import CSV_HEADER, append_trade_log


class CsvLoggerActivePlanTests(unittest.TestCase):
    def _base_payload(self) -> dict[str, object]:
        return {
            "signal_id": "20260607_090500",
            "timestamp_utc": "2026-06-07T00:05:00Z",
            "timestamp_jst": "2026-06-07T09:05:00+09:00",
            "was_notified": True,
            "notified_at_utc": "2026-06-07T00:05:10Z",
            "current_price": 60513.0,
            "bias": "short",
            "phase": "pullback",
            "market_regime": "range",
            "market_map_flags": ["support_to_resistance_flip"],
            "primary_setup_side": "short",
            "primary_setup_status": "watch",
            "primary_setup_reason": "entry_zone_not_reached",
            "trade_execution_gate": "blocked",
            "paper_order_status": "",
            "active_primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
            "active_headline": "下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。",
            "notification_context": {
                "active_subject_label": "戻り売り待ち・短期反発注意",
            },
            "active_trade_plan": {
                "plan_version": "active_trade_plan_v1",
                "primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                "headline": "下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。",
                "market_entry_now": {"long": "blocked", "short": "blocked"},
                "limit_retest_entry": {"long": "allowed", "short": "allowed"},
                "breakout_follow_entry": {"long": "blocked", "short": "blocked"},
                "countertrend_scalp_entry": {"long": "conditional", "short": "blocked"},
                "position_management": {
                    "if_long_holding": "long 保有中なら、主要レジスタンス反応では利確または建値撤退を優先。",
                    "if_short_holding": "short 保有中なら、主要サポート反応では利確または建値撤退を優先。",
                },
            },
            "warning_flags": [],
            "risk_flags": ["short_into_major_support"],
            "no_trade_flags": [],
            "notify_reason_codes": ["main_interval"],
            "suppress_reason_codes": [],
            "reason_for_notification": ["main_interval"],
        }

    def _read_first_row(self, base_dir: Path) -> dict[str, str]:
        path = base_dir / "logs" / "csv" / "trades.csv"
        with path.open("r", newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_csv_header_includes_active_plan_columns(self) -> None:
        expected_columns = [
            "active_plan_version",
            "active_primary_action",
            "active_subject_label",
            "active_headline",
            "active_market_entry_long",
            "active_market_entry_short",
            "active_limit_retest_long",
            "active_limit_retest_short",
            "active_breakout_follow_long",
            "active_breakout_follow_short",
            "active_countertrend_scalp_long",
            "active_countertrend_scalp_short",
            "active_position_management_long",
            "active_position_management_short",
            "active_trade_plan_json",
        ]
        for column in expected_columns:
            with self.subTest(column=column):
                self.assertIn(column, CSV_HEADER)

    def test_append_trade_log_writes_active_plan_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            append_trade_log(base_dir, self._base_payload())
            row = self._read_first_row(base_dir)

        self.assertEqual(row["active_plan_version"], "active_trade_plan_v1")
        self.assertEqual(row["active_primary_action"], "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP")
        self.assertEqual(row["active_subject_label"], "戻り売り待ち・短期反発注意")
        self.assertEqual(row["active_headline"], "下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。")
        self.assertEqual(row["active_market_entry_long"], "blocked")
        self.assertEqual(row["active_market_entry_short"], "blocked")
        self.assertEqual(row["active_limit_retest_long"], "allowed")
        self.assertEqual(row["active_limit_retest_short"], "allowed")
        self.assertEqual(row["active_breakout_follow_long"], "blocked")
        self.assertEqual(row["active_breakout_follow_short"], "blocked")
        self.assertEqual(row["active_countertrend_scalp_long"], "conditional")
        self.assertEqual(row["active_countertrend_scalp_short"], "blocked")
        self.assertIn("long 保有中なら", row["active_position_management_long"])
        self.assertIn("short 保有中なら", row["active_position_management_short"])
        self.assertIn("active_trade_plan_v1", row["active_trade_plan_json"])

    def test_append_trade_log_defaults_when_active_plan_missing(self) -> None:
        payload = self._base_payload()
        payload.pop("active_primary_action", None)
        payload.pop("active_headline", None)
        payload.pop("active_trade_plan", None)
        payload.pop("notification_context", None)

        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            append_trade_log(base_dir, payload)
            row = self._read_first_row(base_dir)

        self.assertEqual(row["active_plan_version"], "")
        self.assertEqual(row["active_primary_action"], "")
        self.assertEqual(row["active_subject_label"], "")
        self.assertEqual(row["active_headline"], "")
        self.assertEqual(row["active_market_entry_long"], "")
        self.assertEqual(row["active_market_entry_short"], "")
        self.assertEqual(row["active_trade_plan_json"], "")

    def test_append_trade_log_defaults_when_active_plan_malformed(self) -> None:
        payload = self._base_payload()
        payload["active_trade_plan"] = "malformed"
        payload["notification_context"] = "malformed"

        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            append_trade_log(base_dir, payload)
            row = self._read_first_row(base_dir)

        self.assertEqual(row["active_plan_version"], "")
        self.assertEqual(row["active_subject_label"], "")
        self.assertEqual(row["active_trade_plan_json"], "")


if __name__ == "__main__":
    unittest.main()
