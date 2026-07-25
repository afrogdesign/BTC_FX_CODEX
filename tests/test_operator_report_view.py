from __future__ import annotations

import re
import unittest

from src.notification.detail_page import build_notification_detail_html
from src.notification.operator_report_view import build_operator_report_view
from tests.test_notification_detail_page import _sample_detail_payload


def _payload(four_h: str = "long", one_h: str = "long", fifteen: str = "long") -> dict:
    payload = _sample_detail_payload()
    payload.update(signals_4h=four_h, signals_1h=one_h, signals_15m=fifteen)
    payload["operator_decision"] = {"primary_side": "long" if fifteen == "long" else "short", "state": "ready"}
    payload["side_aware_mtf_action"] = {
        "present": True,
        "structural_context": {"signals_4h": four_h},
        "tactical_context": {"signals_1h": one_h},
        "execution_context": {"primary_side": payload["operator_decision"]["primary_side"], "primary_action_class": "B_CHECK_15M", "primary_state": "armed"},
        "long": {"action_class": "B_CHECK_15M", "state": "armed", "next_condition": "Longの確認条件"},
        "short": {"action_class": "C_WATCH_ZONE", "state": "watch", "next_condition": "Shortの監視条件"},
    }
    return payload


class OperatorReportViewTests(unittest.TestCase):
    def test_all_long(self):
        self.assertEqual(build_operator_report_view(_payload())["alignment"], "時間軸は同方向")

    def test_all_short(self):
        self.assertEqual(build_operator_report_view(_payload("short", "short", "short"))["alignment"], "時間軸は同方向")

    def test_countertrend_long_15m(self):
        self.assertIn("逆方向", build_operator_report_view(_payload("short", "short", "long"))["alignment"])

    def test_countertrend_short_15m(self):
        self.assertIn("逆方向", build_operator_report_view(_payload("long", "long", "short"))["alignment"])

    def test_turning_candidate(self):
        payload = _payload("long", "short", "short")
        payload["structural_priority"] = {"alignment_state": "turning_candidate"}
        payload["operator_decision"]["alignment_state"] = "turning_candidate"
        self.assertIn("転換", build_operator_report_view(payload)["alignment"])

    def test_conflict_blocks_new_entry(self):
        payload = _payload("long", "short", "wait")
        payload["operator_decision"] = {"state": "direction_conflict", "new_entry_blocked": True}
        view = build_operator_report_view(payload)
        self.assertTrue(view["new_entry_blocked"])
        self.assertIn("競合", view["alignment"])

    def test_no_chase_and_invalidated(self):
        payload = _payload()
        payload["side_aware_mtf_action"]["long"].update({"state": "late", "chase_status": "late_no_chase"})
        payload["side_aware_mtf_action"]["short"].update({"action_class": "STOP_OR_EXIT", "state": "invalidated"})
        view = build_operator_report_view(payload)
        self.assertTrue(view["rows"][0]["no_chase"])
        self.assertEqual(view["rows"][1]["stage"], "新規見送り・保護確認")

    def test_insufficient_structural_evidence(self):
        payload = _payload("", "", "wait")
        view = build_operator_report_view(payload)
        self.assertIn("証拠不足", view["alignment"])

    def test_opposite_big_chance_is_auxiliary(self):
        payload = _payload()
        payload["big_chance_candidate"] = {"present": True, "side": "short", "status": "armed"}
        self.assertIn("反対側", build_operator_report_view(payload)["auxiliary_note"])

    def test_malformed_fails_closed(self):
        payload = _sample_detail_payload()
        payload["side_aware_mtf_action"] = "broken"
        html = build_notification_detail_html(payload)
        self.assertIn("判定材料不足", html)
        self.assertIn("chart-panel", html)

    def test_dynamic_content_escaped(self):
        payload = _payload()
        payload["side_aware_mtf_action"]["long"]["next_condition"] = '<script>alert("x")</script>'
        html = build_notification_detail_html(payload)
        self.assertNotIn('<script>alert("x")</script>', html)
        self.assertIn("&lt;script&gt;", html)

    def test_raw_terms_only_in_diagnostic_details(self):
        html = build_notification_detail_html(_payload())
        visible = re.sub(r"<details.*?</details>", "", html, flags=re.S)
        for term in ("B_CHECK_15M", "C_WATCH_ZONE", "STOP_OR_EXIT", "countertrend", "stale", "PRIMARY"):
            self.assertNotIn(term, visible)

    def test_five_area_order(self):
        html = build_notification_detail_html(_payload())
        positions = [html.find(token) for token in ("今の結論", "時間軸別の方向", "15分足の実行判断", "価格マップ｜", "判断が変わる条件")]
        self.assertEqual(positions, sorted(positions))

    def test_one_canonical_conclusion(self):
        html = build_notification_detail_html(_payload())
        self.assertEqual(html.count("area-1"), 1)
        self.assertEqual(html.count("<h1>"), 1)

    def test_prices_and_chart_controls_preserved(self):
        html = build_notification_detail_html(_payload())
        for value in ("65,629", "65,737", "65,225", "66,419", "66,588", "66,992"):
            self.assertIn(value, html)
        for control in ('data-chart-view="15m"', 'data-chart-view="1h"', 'data-chart-view="4h"', 'data-layer-mode="basic"', 'data-layer-mode="full"'):
            self.assertIn(control, html)

    def test_machine_indexes_are_not_probability(self):
        html = build_notification_detail_html(_payload())
        for label in ("方向の強さ", "実行準備度", "待機圧力", "確率・勝率・実行許可ではありません"):
            self.assertIn(label, html)

    def test_structural_and_side_scores_have_distinct_labels(self):
        payload = _payload()
        payload["structural_priority"] = {"present": True, "long_points": 75, "short_points": 25}
        html = build_notification_detail_html(payload)
        self.assertIn("中期構造配分", html)
        self.assertIn("Long方向評価", html)
        self.assertIn("Short方向評価", html)

    def test_safety_boundary_top_and_footer(self):
        html = build_notification_detail_html(_payload())
        self.assertIn("<p class=\"boundary-note\">", html)
        self.assertIn("<footer>この報告書は表示専用です。", html)

    def test_area_three_has_nearest_band_and_invalidation(self):
        html = build_notification_detail_html(_payload())
        area = html[html.find('class="area-3'):html.find('class="area-4')]
        self.assertIn("最寄りのエントリー帯", area)
        self.assertIn("無効化ライン", area)

    def test_chart_heading_switch_map_exists(self):
        html = build_notification_detail_html(_payload())
        for heading in ("価格マップ｜15分足の実行位置", "価格マップ｜1時間足の確認", "価格マップ｜4時間足の大局"):
            self.assertIn(heading, html)

    def test_mobile_priority_card_marker(self):
        html = build_notification_detail_html(_payload())
        self.assertIn("現在の優先側", html)
        self.assertIn("order:1", html)

    def test_auxiliary_metrics_are_secondary(self):
        html = build_notification_detail_html(_payload())
        self.assertIn('class="context-bar"', html)
        self.assertIn("補助監視", html)


if __name__ == "__main__":
    unittest.main()
