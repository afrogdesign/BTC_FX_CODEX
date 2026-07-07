from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import build_summary_body


class SummaryWordingTest(unittest.TestCase):
    def _build(self, payload: dict[str, object]) -> str:
        body, _provider = build_summary_body(
            provider="api",
            api_key="",
            model="",
            cli_command="",
            timeout_sec=1,
            retry_count=1,
            base_dir=BASE_DIR,
            result_payload=payload,
        )
        return body

    def test_case_a_short_watch_is_wait_first(self) -> None:
        body = self._build({"bias": "short", "primary_setup_status": "watch", "current_price": 101.0})
        self.assertIn("【結論】", body)
        self.assertIn("通常バイアス: 下方向", body)
        self.assertIn("実行判断:", body)
        self.assertIn("Big Chance: なし", body)

    def test_case_b_short_ready_allows_conditional_review(self) -> None:
        body = self._build({"bias": "short", "primary_setup_status": "ready", "current_price": 101.0, "trade_execution_gate": "pass", "paper_order_status": "planned"})
        self.assertIn("通常バイアス: 下方向", body)
        self.assertIn("実行判断:", body)
        self.assertIn("Big Chance: なし", body)

    def test_case_d_wait_bias_stays_neutral(self) -> None:
        body = self._build({"bias": "wait", "primary_setup_status": "invalid", "current_price": 101.0})
        self.assertIn("通常バイアス: 中立", body)
        self.assertIn("実行判断:", body)

    def test_case_e_direction_and_entry_quality_are_separated(self) -> None:
        body = self._build({"bias": "long", "primary_setup_status": "watch", "current_price": 101.0})
        self.assertIn("通常バイアス: 上方向", body)
        self.assertIn("実行判断:", body)

    def test_watch_blocked_entry_ok_is_marked_as_not_reached_and_not_actionable(self) -> None:
        body = self._build({"bias": "long", "primary_setup_status": "watch", "current_price": 101.0, "trade_execution_gate": "blocked"})
        self.assertIn("実行候補ではない。", body)
        self.assertIn("HTMLで条件確認", body)

    def test_market_map_down_reversal_is_explained_without_internal_codes(self) -> None:
        body = self._build({"bias": "long", "primary_setup_status": "watch", "current_price": 101.0, "market_map_flags": ["support_to_resistance_flip"]})
        self.assertIn("【結論】", body)
        self.assertIn("※ report-only / no automatic order / human decides manually", body)
        self.assertNotIn("support_to_resistance_flip", body)

    def test_market_map_up_reversal_is_explained_without_internal_codes(self) -> None:
        body = self._build({"bias": "short", "primary_setup_status": "watch", "current_price": 101.0, "market_map_flags": ["resistance_to_support_flip"]})
        self.assertIn("【結論】", body)
        self.assertIn("※ report-only / no automatic order / human decides manually", body)
        self.assertNotIn("resistance_to_support_flip", body)


if __name__ == "__main__":
    unittest.main()
