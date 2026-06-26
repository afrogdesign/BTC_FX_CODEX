import unittest

from src.presentation.sanitize import build_notification_context


class NotificationContextActivePlanTests(unittest.TestCase):
    def _base_result(self) -> dict[str, object]:
        return {
            "bias": "short",
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
        }

    def test_build_notification_context_includes_active_plan_fields(self) -> None:
        result = self._base_result()
        result.update(
            {
                "active_primary_action": "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP",
                "active_headline": "下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。",
                "active_trade_plan": {
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
            }
        )

        context = build_notification_context(result)

        self.assertEqual(context["active_primary_action"], "ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP")
        self.assertEqual(
            context["active_headline"],
            "下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。",
        )
        self.assertEqual(context["active_market_entry_now"]["short"], "blocked")
        self.assertEqual(context["active_limit_retest_entry"]["short"], "allowed")
        self.assertEqual(context["active_countertrend_scalp_entry"]["long"], "conditional")
        self.assertIn("long 保有中なら", context["active_position_management"]["if_long_holding"])
        self.assertIn("short 保有中なら", context["active_position_management"]["if_short_holding"])

    def test_build_notification_context_active_plan_defaults_when_missing(self) -> None:
        context = build_notification_context(self._base_result())

        self.assertEqual(context["active_primary_action"], "NO_ACTION")
        self.assertEqual(context["active_headline"], "")
        self.assertEqual(context["active_market_entry_now"], {"long": "blocked", "short": "blocked"})
        self.assertEqual(context["active_limit_retest_entry"], {"long": "blocked", "short": "blocked"})
        self.assertEqual(context["active_breakout_follow_entry"], {"long": "blocked", "short": "blocked"})
        self.assertEqual(context["active_countertrend_scalp_entry"], {"long": "blocked", "short": "blocked"})
        self.assertEqual(context["active_position_management"], {"if_long_holding": "", "if_short_holding": ""})

    def test_build_notification_context_active_plan_defaults_when_malformed(self) -> None:
        result = self._base_result()
        result["active_trade_plan"] = "malformed"

        context = build_notification_context(result)

        self.assertEqual(context["active_primary_action"], "NO_ACTION")
        self.assertEqual(context["active_market_entry_now"], {"long": "blocked", "short": "blocked"})
        self.assertEqual(context["active_position_management"], {"if_long_holding": "", "if_short_holding": ""})


if __name__ == "__main__":
    unittest.main()
