from __future__ import annotations

from types import SimpleNamespace
import unittest

from src.analysis.operator_decision import build_operator_decision
from src.analysis.scoring import compute_scores
from src.ai.summary import build_summary_body, build_summary_subject
from src.notification.detail_page import build_notification_detail_html
from src.presentation.sanitize import build_display_context


def _cfg() -> SimpleNamespace:
    return SimpleNamespace(
        TRIGGER_VOLUME_RATIO=2.0, MIN_RR_RATIO=1.5, MAX_ACCEPTABLE_ATR_RATIO=0.08,
        MIN_ACCEPTABLE_ATR_RATIO=0.002, FUNDING_LONG_PROHIBITED=0.03,
        FUNDING_LONG_WARNING=0.01, FUNDING_SHORT_PROHIBITED=-0.03,
        FUNDING_SHORT_WARNING=-0.01, LONG_SHORT_DIFF_THRESHOLD=12, SHORT_LONG_DIFF_THRESHOLD=12,
    )


def _score_inputs(flags: list[str]) -> dict[str, object]:
    return {"market_regime": "range", "ema_alignment_4h": "neutral", "ema20_slope_4h": "flat", "structure_4h": "mixed", "structure_1h": "mixed", "price": 100.0, "ema50_4h": 100.0, "rsi_15m": 50.0, "volume_ratio": 1.0, "atr_ratio": 0.02, "funding_rate": 0.0, "rr_long": 2.0, "rr_short": 2.0, "near_support": False, "near_resistance": False, "breakout_up": False, "breakout_down": False, "in_range_center": False, "signals_15m": "wait", "market_map": {"flags": flags}}


def _incident(bias: str, signal_15m: str, side: str) -> dict[str, object]:
    return {"bias": bias, "signals_4h": "wait", "signals_1h": "wait", "signals_15m": signal_15m, "long_display_score": 100 if bias == "long" else 18, "short_display_score": 2 if bias == "long" else 82, "trade_execution_gate": "blocked", "side_aware_mtf_action": {"execution_context": {"primary_side": side, "primary_action_class": "STOP_OR_EXIT"}}, "market_map": {"flags": [], "market_map_conflicts": []}, "long_setup": {"status": "watch"}, "short_setup": {"status": "watch"}, "primary_setup_status": "watch"}


class SignalReversalSafetyTests(unittest.TestCase):
    def test_reversal_family_compresses_and_reports_suppression(self) -> None:
        score = compute_scores(_score_inputs(["failed_breakout_up_reversal", "major_support_rejection", "resistance_to_support_flip", "resistance_to_support_retest_confirmed", "trend_flip_confirmed_up"]), _cfg())
        self.assertEqual(len(score["score_evidence_families"]), 2)
        self.assertTrue(score["score_correlation_suppressed"])
        self.assertNotIn("market_map_major_support_rejection", score["long_factor_breakdown"])

    def test_both_reversal_families_are_suppressed(self) -> None:
        score = compute_scores(_score_inputs(["failed_breakout_up_reversal", "failed_breakout_down_reversal"]), _cfg())
        self.assertEqual(score["score_evidence_families"], [])
        self.assertIn("market_map_direction_conflict", score["warning_flags"])

    def test_saturation_metadata_matches_normalization_bounds(self) -> None:
        high = compute_scores(_score_inputs([]) | {"market_regime": "uptrend", "ema_alignment_4h": "bullish", "ema20_slope_4h": "up", "price": 110.0, "ema50_4h": 100.0, "structure_4h": "hh_hl", "structure_1h": "hh_hl"}, _cfg())
        low = compute_scores(_score_inputs([]) | {"market_regime": "volatile", "near_resistance": True, "rr_long": 1.0}, _cfg())
        self.assertEqual(high["long_display_saturated"], high["long_display_score"] in {0, 100})
        self.assertEqual(low["long_display_saturated"], low["long_display_score"] in {0, 100})

    def test_location_penalties_are_not_double_counted(self) -> None:
        inputs = _score_inputs(["long_into_major_resistance", "short_into_major_support"])
        inputs.update({"near_resistance": True, "near_support": True})
        score = compute_scores(inputs, _cfg())
        self.assertIn("market_map_long_into_major_resistance", score["long_factor_breakdown"])
        self.assertNotIn("near_resistance_penalty", score["long_factor_breakdown"])
        self.assertIn("market_map_short_into_major_support", score["short_factor_breakdown"])
        self.assertNotIn("near_support_penalty", score["short_factor_breakdown"])

    def test_2105_operator_decision_and_display_are_fail_closed(self) -> None:
        result = _incident("long", "short", "short")
        result["operator_decision"] = build_operator_decision(result)
        decision = result["operator_decision"]
        self.assertEqual(decision["state"], "blocked")
        self.assertEqual(decision["primary_side"], "short")
        self.assertTrue(decision["direction_conflict"])
        self.assertEqual(build_display_context(result)["direction_compact_label"], "方向競合 / 実行不可")
        html = build_notification_detail_html(result)
        self.assertIn("WAIT", html)
        self.assertIn("実行不可 / 新規見送り", html)
        self.assertIn("方向スコア / 100", html)
        self.assertNotIn("短期実行スコア", html)
        self.assertIn("REPORT ONLY", html)
        self.assertNotIn("上方向監視", build_summary_subject(result))
        body, _ = build_summary_body(provider="", api_key="", model="", cli_command="", timeout_sec=0, retry_count=0, base_dir=None, result_payload=result)
        self.assertIn("実行判断: 方向競合・新規見送り", body)
        self.assertIn("監視方向: ショート", body)
        self.assertIn("方向スコア上の傾き: ロング", body)
        self.assertNotIn("通常バイアス: 上方向 / 実行判断:", body)

    def test_2005_keeps_short_monitoring(self) -> None:
        result = _incident("short", "short", "short")
        result["operator_decision"] = build_operator_decision(result)
        self.assertEqual(result["operator_decision"]["primary_side"], "short")
        self.assertFalse(result["operator_decision"]["direction_conflict"])

    def test_conflict_has_no_score_bias_fallback_without_execution_side(self) -> None:
        result = _incident("long", "wait", "")
        result["trade_execution_gate"] = "pass"
        result["side_aware_mtf_action"] = {"execution_context": {"primary_side": "", "primary_action_class": "NONE"}}
        result["market_map"] = {"flags": ["failed_breakout_up_reversal", "failed_breakout_down_reversal"], "market_map_conflicts": []}
        decision = build_operator_decision(result)
        self.assertEqual(decision["state"], "direction_conflict")
        self.assertEqual(decision["primary_side"], "none")
        self.assertTrue(decision["new_entry_blocked"])

    def test_aligned_input_can_fall_back_to_score_bias(self) -> None:
        result = _incident("long", "wait", "")
        result["trade_execution_gate"] = "pass"
        result["side_aware_mtf_action"] = {"execution_context": {"primary_side": "", "primary_action_class": "NONE"}}
        decision = build_operator_decision(result)
        self.assertEqual(decision["primary_side"], "long")
        self.assertFalse(decision["direction_conflict"])


if __name__ == "__main__":
    unittest.main()
