from __future__ import annotations

import unittest

from main import _attach_operator_decision
from src.ai.summary import build_summary_body, build_summary_subject
from src.notification.detail_page import build_notification_detail_html


def _result(*, bias: str, signal_15m: str, side: str, action_class: str, gate: str, conflicts: list[str] | None = None) -> dict[str, object]:
    return {
        "bias": bias,
        "signals_4h": "wait",
        "signals_1h": "wait",
        "signals_15m": signal_15m,
        "trade_execution_gate": gate,
        "side_aware_mtf_action": {"present": True, "execution_context": {"primary_side": side, "primary_action_class": action_class}},
        "market_map": {"flags": [], "market_map_conflicts": conflicts or []},
        "long_display_score": 100 if bias == "long" else 18,
        "short_display_score": 82 if bias == "short" else 2,
        "long_setup": {"status": "watch"},
        "short_setup": {"status": "watch"},
        "primary_setup_status": "watch",
    }


def _body(result: dict[str, object]) -> str:
    body, _ = build_summary_body(provider="", api_key="", model="", cli_command="", timeout_sec=0, retry_count=0, base_dir=None, result_payload=result)
    return body


class OperatorDecisionPipelineTests(unittest.TestCase):
    def test_2105_pipeline_is_blocked_short_and_conflicted_across_surfaces(self) -> None:
        result = _result(bias="long", signal_15m="short", side="short", action_class="STOP_OR_EXIT", gate="blocked")
        _attach_operator_decision(result)
        decision = result["operator_decision"]
        self.assertEqual(decision["state"], "blocked")
        self.assertEqual(decision["primary_side"], "short")
        self.assertEqual(decision["score_bias"], "long")
        self.assertTrue(decision["direction_conflict"])
        self.assertTrue(decision["new_entry_blocked"])
        self.assertNotIn("上方向監視", build_summary_subject(result))
        self.assertIn("実行判断: 方向競合・新規見送り", _body(result))
        html = build_notification_detail_html(result)
        self.assertIn("WAIT", html)
        self.assertIn("実行不可 / 新規見送り", html)
        self.assertIn("方向スコア / 100", html)
        self.assertIn("上限値。確率・勝率・実行許可ではありません", html)

    def test_2005_pipeline_keeps_short_monitoring_without_score_conflict(self) -> None:
        result = _result(bias="short", signal_15m="short", side="short", action_class="B_CHECK_15M", gate="pass")
        _attach_operator_decision(result)
        decision = result["operator_decision"]
        self.assertEqual(decision["primary_side"], "short")
        self.assertEqual(decision["score_bias"], "short")
        self.assertFalse(decision["direction_conflict"])

    def test_aligned_long_remains_conditional_and_report_only(self) -> None:
        result = _result(bias="long", signal_15m="long", side="long", action_class="A_FORMAL", gate="pass")
        _attach_operator_decision(result)
        self.assertEqual(result["operator_decision"]["state"], "conditional_candidate")
        self.assertEqual(result["operator_decision"]["primary_side"], "long")
        html = build_notification_detail_html(result)
        self.assertIn("REPORT ONLY", html)
        self.assertIn("no automatic order", html)

    def test_market_map_conflict_is_fail_closed_without_hard_block(self) -> None:
        result = _result(bias="long", signal_15m="wait", side="", action_class="NONE", gate="pass", conflicts=["market_map_direction_conflict"])
        _attach_operator_decision(result)
        self.assertEqual(result["operator_decision"]["state"], "direction_conflict")
        self.assertTrue(result["operator_decision"]["new_entry_blocked"])
        self.assertIn("新規見送り", _body(result))


if __name__ == "__main__":
    unittest.main()
