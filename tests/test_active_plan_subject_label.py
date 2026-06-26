import unittest

from src.presentation.sanitize import build_notification_context


class ActivePlanSubjectLabelTests(unittest.TestCase):
    def _base_result(self, action: str, bias: str = "short") -> dict[str, object]:
        return {
            "bias": bias,
            "primary_setup_status": "watch",
            "primary_setup_reason": "entry_zone_not_reached",
            "prelabel": "ENTRY_OK",
            "risk_flags": [],
            "warning_flags": [],
            "no_trade_flags": [],
            "invalid_reason": "",
            "trade_execution_gate": "blocked",
            "paper_order_status": "",
            "phase1_observation_gate": "blocked",
            "opportunity_gate": "blocked",
            "notification_kind": "main",
            "signal_tier": "normal",
            "support_zones": [{"low": 60322.42, "high": 60524.08}],
            "resistance_zones": [{"low": 60680.82, "high": 60882.88}],
            "nearest_major_support": {"low": 60322.42, "high": 60524.08},
            "nearest_major_resistance": {"low": 60680.82, "high": 60882.88},
            "primary_stop_loss": 61179.73,
            "primary_entry_mid": 60781.85,
            "primary_tp1": 60264.61,
            "primary_tp2": 59826.94,
            "rr_estimate": 1.3,
            "active_primary_action": action,
            "active_headline": "active headline fixture",
            "active_trade_plan": {
                "primary_action": action,
                "headline": "active headline fixture",
                "market_entry_now": {"long": "blocked", "short": "blocked"},
                "limit_retest_entry": {"long": "blocked", "short": "allowed"},
                "breakout_follow_entry": {"long": "blocked", "short": "blocked"},
                "countertrend_scalp_entry": {"long": "conditional", "short": "blocked"},
                "position_management": {
                    "if_long_holding": "",
                    "if_short_holding": "",
                },
            },
        }

    def test_active_subject_label_for_short_bias(self) -> None:
        cases = [
            ("ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP", "戻り売り待ち・短期反発注意"),
            ("ACTIVE_MARKET_SMALL", "小ロット成行ショート候補"),
            ("ACTIVE_LIMIT_RETEST", "戻り売り待ち"),
            ("ACTIVE_BREAKOUT_FOLLOW", "ブレイク追随待ち"),
            ("ACTIVE_COUNTER_SCALP", "逆方向短期注意"),
            ("NO_ACTION", "見送り"),
            ("", "見送り"),
            ("UNKNOWN_ACTION", "見送り"),
        ]

        for action, expected in cases:
            with self.subTest(action=action):
                context = build_notification_context(self._base_result(action=action, bias="short"))
                self.assertEqual(context["active_subject_label"], expected)

    def test_active_subject_label_for_long_bias(self) -> None:
        cases = [
            ("ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP", "押し目買い待ち・短期反落注意"),
            ("ACTIVE_MARKET_SMALL", "小ロット成行ロング候補"),
            ("ACTIVE_LIMIT_RETEST", "押し目買い待ち"),
            ("ACTIVE_BREAKOUT_FOLLOW", "ブレイク追随待ち"),
            ("ACTIVE_COUNTER_SCALP", "逆方向短期注意"),
            ("NO_ACTION", "見送り"),
        ]

        for action, expected in cases:
            with self.subTest(action=action):
                context = build_notification_context(self._base_result(action=action, bias="long"))
                self.assertEqual(context["active_subject_label"], expected)

    def test_active_subject_label_for_neutral_bias(self) -> None:
        cases = [
            ("ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP", "指値待ち・逆方向短期注意"),
            ("ACTIVE_MARKET_SMALL", "小ロット成行候補"),
            ("ACTIVE_LIMIT_RETEST", "指値・戻り待ち"),
            ("ACTIVE_BREAKOUT_FOLLOW", "ブレイク追随待ち"),
            ("ACTIVE_COUNTER_SCALP", "逆方向短期注意"),
            ("NO_ACTION", "見送り"),
        ]

        for action, expected in cases:
            with self.subTest(action=action):
                context = build_notification_context(self._base_result(action=action, bias="wait"))
                self.assertEqual(context["active_subject_label"], expected)

    def test_active_subject_label_falls_back_to_active_trade_plan_primary_action(self) -> None:
        result = self._base_result(action="ACTIVE_LIMIT_RETEST", bias="short")
        result["active_primary_action"] = ""

        context = build_notification_context(result)

        self.assertEqual(context["active_subject_label"], "戻り売り待ち")


if __name__ == "__main__":
    unittest.main()
