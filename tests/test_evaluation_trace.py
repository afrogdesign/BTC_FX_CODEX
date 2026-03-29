from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analysis.evaluation_trace import build_evaluation_trace


class EvaluationTraceTest(unittest.TestCase):
    def test_trace_contains_required_fields(self) -> None:
        trace = build_evaluation_trace(
            result={
                "bias": "short",
                "primary_setup_status": "watch",
                "primary_setup_reason": "near_entry_zone_waiting_trigger",
                "volume_ratio": 0.8,
                "trigger_volume_ratio_threshold": 1.15,
                "signals_15m": "wait",
                "breakout_down": False,
                "breakout_up": False,
                "no_trade_flags": ["RR_insufficient_short"],
                "warning_flags": ["Critical_zone_warning"],
                "risk_flags": ["upper_liquidity_close"],
                "long_setup": {"invalid_reason_codes": []},
                "short_setup": {"invalid_reason_codes": ["confidence_below_min"]},
            },
            score_info={
                "direction_score_shadow": 68.0,
                "activity_score_shadow": 41.0,
                "entry_quality_score_shadow": 36.0,
            },
            position_risk={"risk_breakdown": {"upper_liquidity_distance": 30.0}},
            confidence_details={
                "confidence_components": [{"code": "rr", "delta": 5.0}],
                "confidence_direction_shadow": 80.0,
                "confidence_execution_shadow": 42.0,
                "confidence_wait_shadow": 33.0,
            },
            display_context={
                "direction_label": "相場は下方向バイアスです",
                "action_label": "戻り売り待ち",
                "entry_quality_label": "位置条件は悪くない",
                "setup_status_label": "監視継続",
                "confidence_metric_labels": {
                    "direction": "方向の強さ",
                    "execution": "実行しやすさ",
                    "wait": "待機圧力",
                },
            },
        )
        self.assertEqual(trace["evaluation_trace_version"], "v0.2")
        self.assertIn("direction_score_shadow", trace)
        self.assertIn("trigger_reason_codes", trace)
        self.assertIn("display_label_mapping", trace)
        self.assertEqual(trace["summary_variant"], "direction_execution_split_v2")
        self.assertEqual(trace["blocking_reason_codes"], ["RR_insufficient_short"])
        self.assertEqual(trace["warning_reason_codes"], ["Critical_zone_warning"])
        self.assertEqual(trace["position_risk_flags"], ["upper_liquidity_close"])
