from __future__ import annotations

import unittest

from src.ai.summary import build_summary_subject


class SummaryActivePlanSubjectTests(unittest.TestCase):
    def _base_payload(self) -> dict[str, object]:
        return {
            "timestamp_jst": "2026-06-07T09:05:00+09:00",
            "system_label": "Ver03-v1",
            "system_mode_label": "CLI",
            "notification_kind": "main",
            "prelabel": "ENTRY_OK",
            "bias": "short",
            "signal_tier": "normal",
            "primary_setup_status": "watch",
            "primary_setup_reason": "entry_zone_not_reached",
            "trade_execution_gate": "blocked",
            "paper_order_status": "",
            "phase1_observation_gate": "blocked",
            "opportunity_gate": "blocked",
            "current_price": 60513.0,
            "confidence": 66,
            "rr_estimate": 1.3,
            "confidence_direction_shadow": 72.0,
            "confidence_execution_shadow": 18.0,
            "confidence_wait_shadow": 59.2,
            "score_gap": -18,
            "warning_flags": [],
            "risk_flags": ["short_into_major_support"],
            "no_trade_flags": [],
            "support_zones": [{"low": 60322.42, "high": 60524.08}],
            "resistance_zones": [{"low": 60680.82, "high": 60882.88}],
            "nearest_major_support": {"low": 60322.42, "high": 60524.08},
            "nearest_major_resistance": {"low": 60680.82, "high": 60882.88},
            "primary_stop_loss": 61179.73,
            "primary_entry_mid": 60781.85,
            "primary_tp1": 60264.61,
            "primary_tp2": 59826.94,
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
                    "if_long_holding": "",
                    "if_short_holding": "",
                },
            },
            "ai_advice": {"decision": "WAIT"},
        }

    def test_main_subject_prioritizes_active_plan_action(self) -> None:
        subject = build_summary_subject(self._base_payload())

        self.assertIn("[BTCFX Ver03-v4]", subject)
        self.assertNotIn("[BTCFX Ver03-v2]", subject)
        self.assertIn("📊 [通常監視・実行不可]", subject)
        self.assertIn("戻り売り待ち・短期反発注意 / 実弾不可・行動計画", subject)
        self.assertIn("下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。", subject)
        self.assertIn("【BTC:60,513】", subject)
        self.assertIn("[Ver03-v1]", subject)
        self.assertIn("[CLI]", subject)
        self.assertNotIn("下方向バイアス |", subject)

    def test_no_action_subject_uses_miokuri_label(self) -> None:
        payload = self._base_payload()
        payload["active_primary_action"] = "NO_ACTION"
        payload["active_headline"] = "方向は中立。現時点では見送り。"
        payload["active_trade_plan"] = {
            "primary_action": "NO_ACTION",
            "headline": "方向は中立。現時点では見送り。",
        }

        subject = build_summary_subject(payload)

        self.assertIn("[BTCFX Ver03-v4]", subject)
        self.assertNotIn("[BTCFX Ver03-v2]", subject)
        self.assertIn("見送り / 実弾不可・行動計画", subject)
        self.assertIn("方向は中立。現時点では見送り。", subject)

    def test_formal_gate_pass_keeps_legacy_subject(self) -> None:
        payload = self._base_payload()
        payload["trade_execution_gate"] = "pass"
        payload["paper_order_status"] = "planned"
        payload["primary_setup_status"] = "ready"
        payload["signal_tier"] = "strong_machine"
        payload["active_primary_action"] = "ACTIVE_LIMIT_RETEST"
        payload["active_headline"] = "Active plan should not override formal go subject."

        subject = build_summary_subject(payload)

        self.assertIn("[BTCFX Ver03-v4]", subject)
        self.assertNotIn("[BTCFX Ver03-v2]", subject)
        self.assertIn("🔥 [執行候補・強]", subject)
        self.assertIn("下方向バイアス |", subject)
        self.assertNotIn("実弾不可・行動計画", subject)
        self.assertNotIn("Active plan should not override formal go subject.", subject)

    def test_attention_subject_keeps_legacy_subject(self) -> None:
        payload = self._base_payload()
        payload["notification_kind"] = "attention"
        payload["active_primary_action"] = "ACTIVE_LIMIT_RETEST"
        payload["active_headline"] = "Active plan should not override attention subject."
        payload["ai_advice"] = None

        subject = build_summary_subject(payload)

        self.assertTrue(subject.startswith("[BTCFX Ver03-v4] [機械判定のみ] 👀 [注意報・売買非推奨] "))
        self.assertNotIn("[BTCFX Ver03-v2]", subject)
        self.assertIn("下方向監視 |", subject)
        self.assertNotIn("実弾不可・行動計画", subject)
        self.assertNotIn("Active plan should not override attention subject.", subject)

    def test_missing_active_plan_label_falls_back_to_legacy_subject(self) -> None:
        payload = self._base_payload()
        payload.pop("active_primary_action", None)
        payload.pop("active_headline", None)
        payload.pop("active_trade_plan", None)

        subject = build_summary_subject(payload)

        self.assertIn("[BTCFX Ver03-v4]", subject)
        self.assertNotIn("[BTCFX Ver03-v2]", subject)
        self.assertIn("下方向監視 |", subject)
        self.assertNotIn("実弾不可・行動計画", subject)


if __name__ == "__main__":
    unittest.main()
