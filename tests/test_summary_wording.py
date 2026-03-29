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
        body = self._build(
            {
                "bias": "short",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "watch",
                "primary_setup_reason": "entry_zone_not_reached",
                "confidence": 89,
                "risk_flags": ["upper_liquidity_close"],
                "no_trade_flags": [],
                "long_setup": {},
                "short_setup": {"status": "watch", "entry_zone": {"low": 101, "high": 102}, "stop_loss": 103, "tp1": 99, "tp2": 97},
            }
        )
        self.assertIn("方向判断: 相場は下方向バイアスです", body)
        self.assertRegex(body, "いまの扱い: (上側流動性回収待ち|戻り売り待ち|再失速確認待ち|下目線で待機)")
        self.assertNotIn("入る条件がかなりそろっています", body)

    def test_case_b_short_ready_allows_conditional_review(self) -> None:
        body = self._build(
            {
                "bias": "short",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "ready",
                "primary_setup_reason": "inside_entry_zone_with_trigger",
                "confidence": 76,
                "risk_flags": [],
                "no_trade_flags": [],
                "short_setup": {"status": "ready", "entry_zone": {"low": 101, "high": 102}, "stop_loss": 103, "tp1": 99, "tp2": 97},
                "long_setup": {},
            }
        )
        self.assertIn("いまの扱い: ショートは条件付きで検討", body)
        self.assertNotIn("今すぐ入ってよい", body)

    def test_case_d_wait_bias_stays_neutral(self) -> None:
        body = self._build(
            {
                "bias": "wait",
                "prelabel": "RISKY_ENTRY",
                "primary_setup_status": "invalid",
                "confidence": 22,
                "risk_flags": [],
                "no_trade_flags": ["RR_insufficient"],
                "long_setup": {},
                "short_setup": {},
            }
        )
        self.assertIn("方向判断: 相場は中立です", body)
        self.assertIn("いまの扱い: 見送り", body)

    def test_case_e_direction_and_entry_quality_are_separated(self) -> None:
        body = self._build(
            {
                "bias": "long",
                "prelabel": "RISKY_ENTRY",
                "primary_setup_status": "watch",
                "primary_setup_reason": "near_entry_zone_waiting_trigger",
                "confidence": 61,
                "risk_flags": ["ask_wall_close"],
                "no_trade_flags": [],
                "long_setup": {"status": "watch", "entry_zone": {"low": 101, "high": 102}, "stop_loss": 99, "tp1": 104, "tp2": 105},
                "short_setup": {},
            }
        )
        self.assertIn("方向判断: 相場は上方向バイアスです", body)
        self.assertIn("位置評価: 位置はやや注意", body)
