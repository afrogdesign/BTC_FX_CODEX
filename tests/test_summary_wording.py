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
        self.assertIn("執行判断: 監視継続", body)
        self.assertIn("現値帯の扱い: 価格到達待ち", body)
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
        self.assertIn("執行判断: 条件付きで検討", body)
        self.assertIn("現値帯の扱い: 現値帯のみ条件付き", body)
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
        self.assertIn("執行判断: 見送り", body)

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

    def test_watch_blocked_entry_ok_is_marked_as_not_reached_and_not_actionable(self) -> None:
        body = self._build(
            {
                "bias": "long",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "watch",
                "primary_setup_reason": "entry_zone_not_reached",
                "trade_execution_gate": "blocked",
                "confidence": 68,
                "risk_flags": ["sweep_incomplete", "lower_liquidity_close", "long_reversal_risk"],
                "no_trade_flags": [],
                "long_setup": {"status": "watch", "entry_zone": {"low": 101, "high": 102}, "stop_loss": 99, "tp1": 104, "tp2": 105},
                "short_setup": {},
            }
        )
        self.assertIn("これは実行候補ではありません。監視と再評価のための通知です。", body)
        self.assertIn("執行判断: 監視継続（実行不可）", body)
        self.assertIn("位置評価: 位置は悪くないが未到達", body)

    def test_market_map_down_reversal_is_explained_without_internal_codes(self) -> None:
        body = self._build(
            {
                "bias": "long",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "watch",
                "primary_setup_reason": "entry_zone_not_reached",
                "trade_execution_gate": "blocked",
                "notification_kind": "main",
                "confidence": 68,
                "rr_estimate": 1.4,
                "score_gap": 24,
                "risk_flags": [
                    "failed_breakout_down_reversal",
                    "support_to_resistance_flip",
                    "long_into_major_resistance",
                ],
                "no_trade_flags": [],
                "nearest_major_resistance": {"low": 105.0, "high": 106.0},
                "long_setup": {"status": "watch", "entry_zone": {"low": 101, "high": 102}, "stop_loss": 99, "tp1": 104, "tp2": 105},
                "short_setup": {"status": "watch", "entry_zone": {"low": 103, "high": 104}, "stop_loss": 106, "tp1": 100, "tp2": 98},
            }
        )

        self.assertIn("これは実行候補ではありません。監視と再評価のための通知です。", body)
        self.assertIn("最終ランク: 📊 通常の本通知（上抜け失敗・戻り売り警戒を優先して標準扱いに抑制）", body)
        self.assertIn("上抜け失敗後の下落転換型", body)
        self.assertIn("割れたサポートがレジスタンス化", body)
        self.assertIn("ロングは主要レジスタンス接近で追いかけ注意", body)
        self.assertIn("上抜け失敗後、戻りが主要レジスタンスで止まるか再評価", body)
        self.assertIn("主要レジスタンス 106.00 を明確に上抜けたら下落警戒は弱まる", body)
        self.assertNotIn("failed_breakout_down_reversal", body)
        self.assertNotIn("support_to_resistance_flip", body)
        self.assertNotIn("long_into_major_resistance", body)

    def test_market_map_up_reversal_is_explained_without_internal_codes(self) -> None:
        body = self._build(
            {
                "bias": "short",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "watch",
                "primary_setup_reason": "entry_zone_not_reached",
                "trade_execution_gate": "blocked",
                "notification_kind": "main",
                "confidence": 68,
                "rr_estimate": 1.4,
                "score_gap": -24,
                "risk_flags": [
                    "failed_breakout_up_reversal",
                    "resistance_to_support_flip",
                    "short_into_major_support",
                ],
                "no_trade_flags": [],
                "nearest_major_support": {"low": 95.0, "high": 96.0},
                "long_setup": {"status": "watch", "entry_zone": {"low": 96, "high": 97}, "stop_loss": 94, "tp1": 100, "tp2": 102},
                "short_setup": {"status": "watch", "entry_zone": {"low": 99, "high": 100}, "stop_loss": 102, "tp1": 96, "tp2": 94},
            }
        )

        self.assertIn("最終ランク: 📊 通常の本通知（下抜け失敗・押し目確認を優先して標準扱いに抑制）", body)
        self.assertIn("下抜け失敗後の上昇転換型", body)
        self.assertIn("上抜けたレジスタンスがサポート化", body)
        self.assertIn("ショートは主要サポート接近で追いかけ注意", body)
        self.assertIn("下抜け失敗後、押し目が主要サポートで止まるか再評価", body)
        self.assertIn("主要サポート 95.00 を明確に割れたら上昇警戒は弱まる", body)
        self.assertNotIn("failed_breakout_up_reversal", body)
        self.assertNotIn("resistance_to_support_flip", body)
