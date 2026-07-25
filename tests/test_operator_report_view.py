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
        self.assertEqual(build_operator_report_view(_payload())["alignment_summary"], "4H・1H・15MがLongで一致")

    def test_all_short(self):
        self.assertEqual(build_operator_report_view(_payload("short", "short", "short"))["alignment_summary"], "4H・1H・15MがShortで一致")

    def test_countertrend_long_15m(self):
        self.assertEqual(build_operator_report_view(_payload("short", "short", "long"))["alignment_summary"], "4H・1HはShort、15MはLongのため短期は逆行")

    def test_countertrend_short_15m(self):
        self.assertEqual(build_operator_report_view(_payload("long", "long", "short"))["alignment_summary"], "4H・1HはLong、15MはShortのため短期は逆行")

    def test_turning_candidate(self):
        payload = _payload("long", "short", "short")
        payload["structural_priority"] = {"alignment_state": "turning_candidate"}
        payload["operator_decision"]["alignment_state"] = "turning_candidate"
        self.assertEqual(build_operator_report_view(payload)["alignment_summary"], "4HはLong、1H・15MはShort — 反対方向への転換候補")

    def test_conflict_blocks_new_entry(self):
        payload = _payload("long", "short", "long")
        payload["operator_decision"] = {"state": "direction_conflict", "new_entry_blocked": True}
        view = build_operator_report_view(payload)
        self.assertTrue(view["new_entry_blocked"])
        self.assertEqual(view["alignment_summary"], "4HはLong、1HはShort、15MはLong — 4H・1H・15Mの方向が競合しているため新規見送り")

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
        self.assertEqual(view["alignment_summary"], "4H・1H・15Mの判定材料が不足")

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

    def test_setup_and_diagnostic_dynamic_values_are_escaped(self):
        payload = _payload()
        payload["long_setup"]["value_defense_entry_layer"]["shallow_retest_zone"]["low"] = '<img src=x onerror="alert(1)">'
        payload["signals_4h"] = '<script>alert("direction")</script>'
        html = build_notification_detail_html(payload)
        self.assertNotIn('<img src=x onerror="alert(1)">', html)
        self.assertNotIn('<script>alert("direction")</script>', html)
        self.assertIn("&lt;script&gt;", html)

    def test_raw_terms_only_in_diagnostic_details(self):
        html = build_notification_detail_html(_payload())
        visible = re.sub(r"<details.*?</details>", "", html, flags=re.S)
        for term in ("B_CHECK_15M", "C_WATCH_ZONE", "STOP_OR_EXIT", "countertrend", "stale", "PRIMARY"):
            self.assertNotIn(term, visible)

    def test_five_area_order(self):
        html = build_notification_detail_html(_payload())
        positions = [html.find(token) for token in ("AREA 1", "AREA 2", "AREA 3", "AREA 4", "AREA 5")]
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

    def test_structural_allocation_and_independent_scores_show_actual_values(self):
        payload = _payload()
        payload.update(long_display_score=73, short_display_score=19)
        payload["structural_priority"] = {"present": True, "long_points": 61, "short_points": 39}
        html = build_notification_detail_html(payload)
        self.assertIn("中期構造配分", html)
        self.assertIn("Long 61 / Short 39", html)
        self.assertIn("Long方向材料スコア（独立評価）", html)
        self.assertIn("Short方向材料スコア（独立評価）", html)
        self.assertIn(">73<", html)
        self.assertIn(">19<", html)

    def test_structural_priority_alignment_wins(self):
        payload = _payload("long", "long", "long")
        payload["structural_priority"] = {"alignment_state": "turning_candidate"}
        self.assertEqual(build_operator_report_view(payload)["alignment_summary"], "4H・1H・15MがLongで一致 — 反対方向への転換候補")

    def test_two_real_action_cards_for_missing_invalid_and_malformed_priority(self):
        for primary in (None, "", "mystery", {"bad": "value"}):
            payload = _payload()
            payload["operator_decision"]["primary_side"] = primary
            html = build_notification_detail_html(payload)
            self.assertEqual(html.count('class="operator-action-card'), 2)
            self.assertEqual(html.count('data-side="long"'), 1)
            self.assertEqual(html.count('data-side="short"'), 1)
            self.assertNotIn('data-side="unknown"', html)

    def test_unknown_primary_side_does_not_infer_timeframe_direction(self):
        payload = _payload("wait", "wait", "wait")
        payload["operator_decision"]["primary_side"] = "mystery"
        view = build_operator_report_view(payload)
        self.assertEqual(view["primary_side"], "")
        self.assertEqual(view["signals"]["15M"]["label"], "中立・様子見")
        self.assertEqual(view["alignment_summary"], "4H・1H・15Mの判定材料が不足")

    def test_malformed_operator_decision_still_has_two_cards(self):
        payload = _payload()
        payload["operator_decision"] = {"primary_side": {"unexpected": "object"}}
        html = build_notification_detail_html(payload)
        self.assertEqual(html.count('class="operator-action-card'), 2)
        self.assertEqual(html.count('data-side="long"'), 1)
        self.assertEqual(html.count('data-side="short"'), 1)

    def test_no_chase_is_human_facing_once_inside_priority_card(self):
        payload = _payload()
        payload["side_aware_mtf_action"]["long"].update({"state": "late", "chase_status": "late_no_chase"})
        html = build_notification_detail_html(payload)
        area = html[html.find('class="area-3'):html.find('class="area-4')]
        long_card = area[area.find('data-side="long"'):area.find('</article>', area.find('data-side="long"'))]
        self.assertIn("追いかけ禁止", long_card)
        self.assertEqual(long_card.count("追いかけ禁止"), 1)

    def test_lifecycle_is_not_a_timeframe_direction(self):
        payload = _payload()
        payload.pop("signals_15m")
        payload["side_aware_mtf_action"]["execution_context"].update({"primary_side": "short", "primary_state": "armed"})
        payload["side_aware_mtf_action"]["short"]["state"] = "armed"
        payload["operator_decision"]["primary_side"] = "short"
        view = build_operator_report_view(payload)
        self.assertEqual(view["signals"]["15M"]["label"], "判定材料不足")
        self.assertEqual(view["rows"][1]["state"], "条件待ち")

        payload["operator_decision"]["primary_side"] = ""
        payload["side_aware_mtf_action"]["execution_context"]["primary_side"] = ""
        view = build_operator_report_view(payload)
        self.assertEqual(view["signals"]["15M"]["label"], "判定材料不足")

    def test_partial_evidence_names_only_known_timeframes(self):
        payload = _payload("long", "wait", "neutral")
        view = build_operator_report_view(payload)
        self.assertEqual(view["alignment_summary"], "4HはLong、1H・15Mは判定材料不足")
        self.assertNotIn("1HはLong", view["alignment_summary"])

    def test_lifecycle_values_are_not_directions(self):
        for lifecycle in ("armed", "watch", "late"):
            payload = _payload("long", lifecycle, lifecycle)
            view = build_operator_report_view(payload)
            self.assertEqual(view["signals"]["1H"]["label"], "判定材料不足")
            self.assertEqual(view["signals"]["15M"]["label"], "判定材料不足")
            self.assertIn("判定材料不足", view["alignment_summary"])

    def test_priority_next_condition_is_area_five_event(self):
        payload = _payload()
        payload["side_aware_mtf_action"]["long"]["next_condition"] = "優先側だけの具体的な確認イベント"
        payload["notification_context"] = {"reason_labels_full": ["古い一般理由"]}
        html = build_notification_detail_html(payload)
        area = html[html.find('class="area-5'):html.find('<section class="panel details-panel"')]
        self.assertIn("優先側だけの具体的な確認イベント", area)
        self.assertNotIn("古い一般理由", area)

    def test_missing_invalidation_is_fail_closed(self):
        payload = _payload()
        payload["long_setup"]["value_defense_entry_layer"] = {}
        html = build_notification_detail_html(payload)
        area = html[html.find('class="area-5'):html.find('<section class="panel details-panel"')]
        self.assertIn("無効化ラインはデータ未取得", area)
        self.assertNotIn("— を明確に抜け", area)

    def test_preserves_stable_surface_safety_and_hidden_version_labels(self):
        html = build_notification_detail_html(_payload())
        self.assertIn("BTCFX Manual Trading Report", html)
        self.assertIn("現在値 / 更新時刻", html)
        self.assertIn("65,818", html)
        self.assertIn("REPORT ONLY / HUMAN DECISION", html)
        for term in ("Ver02.6-v2", "Ver03-v4", "send_email", "private/order", "private endpoint", "account endpoint", "order endpoint"):
            self.assertNotIn(term, html)

    def test_chart_geometry_big_chance_and_responsive_contract(self):
        payload = _payload()
        payload["big_chance_candidate"] = {"present": True, "side": "short", "status": "armed", "headline": "補助候補"}
        html = build_notification_detail_html(payload)
        self.assertIn('class="chart-stage basic"', html)
        self.assertIn('viewBox="0 726 860 429"', html)
        self.assertIn("補助監視", html)
        self.assertIn("通常のLong / Short判断を上書きしません", html)
        self.assertIn("overflow-x:auto", html)
        self.assertIn("@media (max-width:860px)", html)

    def test_primary_15m_markers_and_zones_stay_in_visible_chart_range(self):
        html = build_notification_detail_html(_payload())
        svg = re.search(r'<svg viewBox="0 726 860 429".*?</svg>', html, re.S)
        self.assertIsNotNone(svg)
        svg_html = svg.group(0) if svg else ""
        marker_y = [float(value) for value in re.findall(r'class="marker-label marker-(?:long|short)"[^>]* y="([0-9.]+)"', svg_html)]
        if not marker_y:
            marker_y = [float(value) for value in re.findall(r' y="([0-9.]+)"[^>]* class="marker-label marker-(?:long|short)"', svg_html)]
        self.assertGreaterEqual(len(marker_y), 6)
        self.assertTrue(all(726.0 <= value <= 1155.0 for value in marker_y))
        self.assertIn('class="value-defense-band-long"', svg_html)
        self.assertIn('class="value-defense-band-short"', svg_html)

    def test_missing_one_or_both_setups_preserves_surface_chart_and_cards(self):
        for missing in (("long_setup",), ("short_setup",), ("long_setup", "short_setup")):
            payload = _payload()
            for key in missing:
                payload[key] = {}
            html = build_notification_detail_html(payload)
            self.assertEqual(html.count('class="operator-action-card'), 2)
            self.assertIn("chart-panel", html)
            self.assertIn("AREA 1", html)
            self.assertIn("AREA 5", html)
            area = html[html.find('class="area-3'):html.find('class="area-4')]
            self.assertGreaterEqual(area.count("<b>—</b>"), 2)

    def test_notification_kinds_keep_same_report_only_surface_and_diagnostics_below(self):
        for kind in ("main", "attention", "followup"):
            html = build_notification_detail_html({**_payload(), "notification_kind": kind})
            self.assertIn("operator-dashboard", html)
            for area in ("AREA 1", "AREA 2", "AREA 3", "AREA 4", "AREA 5"):
                self.assertIn(area, html)
            self.assertIn("REPORT ONLY / HUMAN DECISION", html)
            self.assertIn("この報告書は表示専用です。", html)
            self.assertIn("<details", html)
            self.assertNotIn("private/account/order", html)
            self.assertLess(html.find('class="area-4'), html.find('<section class="panel details-panel"'))

    def test_big_chance_is_later_auxiliary_and_not_stale_in_visible_text(self):
        payload = _payload()
        payload["big_chance_candidate"] = {
            "present": True,
            "side": "short",
            "status": "stale",
            "headline": "反対側候補",
            "operator_summary": "補助候補",
            "macro_context": {},
        }
        html = build_notification_detail_html(payload)
        self.assertLess(html.find("判断が変わる条件"), html.find('id="big-chance"'))
        visible = re.sub(r"<details.*?</details>|<style.*?</style>|<script.*?</script>|<[^>]+>", "", html, flags=re.S)
        self.assertIn("補助監視", visible)
        self.assertIn("通常のLong / Short判断を上書きしません", visible)
        self.assertNotIn("stale", visible.lower())


if __name__ == "__main__":
    unittest.main()
