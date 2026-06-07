from __future__ import annotations

import unittest

from src.notification.detail_page import build_notification_detail_html


class DetailPageActivePlanHeroTests(unittest.TestCase):
    def _base_payload(self) -> dict[str, object]:
        return {
            "timestamp_jst": "2026-06-07T09:05:00+09:00",
            "signal_id": "20260607_090500",
            "summary_subject": "📊 [通常監視・実行不可] 戻り売り待ち・短期反発注意 / 実弾不可・行動計画 | 下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。 【BTC:60,513】 2026-06-07 09:05 [Ver03-v1][CLI]",
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
            "long_display_score": 44,
            "short_display_score": 62,
            "market_regime": "range",
            "phase": "pullback",
            "signals_4h": "wait",
            "signals_1h": "short",
            "signals_15m": "wait",
            "funding_rate_display": "ほぼ中立 (+0.0030%)",
            "atr_ratio": 0.92,
            "volume_ratio": 1.0,
            "warning_flags": [],
            "risk_flags": ["short_into_major_support"],
            "no_trade_flags": [],
            "support_zones": [{"low": 60322.42, "high": 60524.08, "distance_from_price": 190.58}],
            "resistance_zones": [{"low": 60680.82, "high": 60882.88, "distance_from_price": 167.82}],
            "nearest_major_support": {"low": 60322.42, "high": 60524.08},
            "nearest_major_resistance": {"low": 60680.82, "high": 60882.88},
            "primary_stop_loss": 61179.73,
            "primary_entry_mid": 60781.85,
            "primary_tp1": 60264.61,
            "primary_tp2": 59826.94,
            "long_setup": {
                "status": "watch",
                "entry_zone": {"low": 60322.42, "high": 60524.08},
                "stop_loss": 60025.57,
                "tp1": 60940.23,
                "tp2": 61377.68,
            },
            "short_setup": {
                "status": "invalid",
                "entry_zone": {"low": 60680.82, "high": 60882.88},
                "stop_loss": 61179.73,
                "tp1": 60264.61,
                "tp2": 59826.94,
            },
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
            "ai_advice": {"decision": "WAIT"},
        }

    def test_detail_page_hero_prioritizes_active_plan(self) -> None:
        html = build_notification_detail_html(self._base_payload())

        self.assertIn("戻り売り待ち・短期反発注意 / 実弾不可・行動計画", html)
        self.assertIn("下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。", html)
        self.assertIn("<strong>Active Plan:</strong>", html)
        self.assertIn("<strong>成行:</strong>", html)
        self.assertIn("long: blocked / short: blocked", html)
        self.assertIn("<strong>指値・戻り待ち:</strong>", html)
        self.assertIn("long: allowed / short: allowed", html)
        self.assertIn("<strong>逆方向短期:</strong>", html)
        self.assertIn("long: conditional / short: blocked", html)
        self.assertIn("まず方向ではなく、実際に取れる行動を確認します。", html)

    def test_detail_page_hero_keeps_formal_go_message_for_gate_pass(self) -> None:
        payload = self._base_payload()
        payload["trade_execution_gate"] = "pass"
        payload["paper_order_status"] = "planned"
        payload["primary_setup_status"] = "ready"
        payload["summary_subject"] = "🔥 [執行候補・強] 下方向バイアス | 条件成立 【BTC:60,513】"

        html = build_notification_detail_html(payload)

        self.assertIn("正式GO・紙トレード記録候補", html)
        self.assertIn("これは正式な執行候補です。ただし現段階では自動売買ではなく、紙トレード記録対象です。", html)

    def test_detail_page_hero_keeps_attention_message(self) -> None:
        payload = self._base_payload()
        payload["notification_kind"] = "attention"
        payload["summary_subject"] = "👀 [注意報・売買非推奨] 下方向監視 | 注意"

        html = build_notification_detail_html(payload)

        self.assertIn("注意報・売買非推奨", html)
        self.assertIn("これは売買推奨ではなく、方向変化や初動を早めに共有する注意通知です。", html)

    def test_detail_page_hero_falls_back_when_active_plan_missing(self) -> None:
        payload = self._base_payload()
        payload.pop("active_primary_action", None)
        payload.pop("active_headline", None)
        payload.pop("active_trade_plan", None)

        html = build_notification_detail_html(payload)

        self.assertIn("見送り / 実弾不可・行動計画", html)
        self.assertIn("<strong>Active Plan:</strong>", html)


if __name__ == "__main__":
    unittest.main()
