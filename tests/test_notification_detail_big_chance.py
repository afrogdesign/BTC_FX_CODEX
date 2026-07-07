from __future__ import annotations

import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import build_summary_body, build_summary_subject  # noqa: E402
from src.analysis.big_chance import evaluate_big_chance  # noqa: E402
from src.notification.detail_page import build_notification_detail_html  # noqa: E402
from tests.test_big_chance import _payload  # noqa: E402


class NotificationDetailBigChanceTests(unittest.TestCase):
    def test_summary_and_detail_render_big_chance_section(self) -> None:
        current = _payload(
            signal_id="20260706_150500",
            timestamp_jst="2026-07-06T15:05:00+09:00",
            bias="long",
            current_price=50_100,
            signals_4h="short",
            signals_1h="wait",
            signals_15m="short",
            market_map_primary_state="early_down_transition",
            market_map_flags=["support_to_resistance_flip", "support_to_resistance_retest_confirmed"],
            level_flip_state="support_to_resistance_confirmed",
            trend_flip_state="trend_flip_early_down",
            failed_breakout_state="failed_long_breakout",
            transition_direction="down",
            long_zone=(47_000, 47_500, 46_800, 47_200, 46_200, 46_600, 46_900, 47_100, "invalidated"),
            short_zone=(52_000, 52_500, 52_600, 53_100, 53_600, 54_000, 52_850, 53_050, "watch"),
        )
        current["big_chance_candidate"] = evaluate_big_chance(current, None)
        current["summary_subject"] = build_summary_subject(current)

        summary_body, provider = build_summary_body(
            provider="api",
            api_key="x",
            model="gpt-4o",
            cli_command="",
            timeout_sec=1,
            retry_count=0,
            base_dir=BASE_DIR,
            result_payload=current,
        )
        html = build_notification_detail_html(current)

        self.assertEqual(provider, "api")
        self.assertIn("Big Chance: ロング失敗 → ショート候補 / follow_through / S", summary_body)
        self.assertIn("Big Chance / Failed Thesis", html)
        self.assertIn('id="big-chance"', html)
        self.assertIn("Big Chance is not an entry instruction", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", summary_body)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertNotIn("report-only_not_FORMAL_GO_no_automatic_order_human_decides_manually", html)
        self.assertIn("Big Chance: ロング失敗 → ショート候補 / follow_through / S", summary_body)

    def test_invalidated_big_chance_renders_as_replayed_not_active(self) -> None:
        current = _payload(
            signal_id="20260706_160500",
            timestamp_jst="2026-07-06T16:05:00+09:00",
            bias="short",
            current_price=62_019.7,
            signals_4h="wait",
            signals_1h="wait",
            signals_15m="short",
            market_map_primary_state="early_down",
            market_map_flags=["support_to_resistance_flip", "support_to_resistance_retest_confirmed", "trend_flip_early_down"],
            level_flip_state="support_to_resistance_confirmed",
            trend_flip_state="early_down",
            failed_breakout_state="",
            transition_direction="up",
            long_zone=(63_032.83, 63_381.07, 62_737.93, 62_982.77, 62_486.41, 62_541.75, 63_007.8, 63_206.95, "continuation_candidate"),
            short_zone=(63_826.73, 64_055.07, 64_546.15, 64_601.49, 63_991.25, 64_042.55, 64_105.0, 64_200.0, "shallow_retest_risk"),
        )
        current["big_chance_candidate"] = {
            "schema_version": "big_chance_failed_thesis.v1",
            "present": True,
            "side": "long",
            "type": "short_failed_to_long",
            "status": "invalidated",
            "score": 70,
            "grade": "B",
            "headline": "ショート失敗→ロング候補",
            "operator_summary": "ショート仮説の失敗を見ています。",
            "macro_context": {},
            "failed_thesis": {"thesis_summary": "Failed thesis is opportunity"},
            "activation": {},
            "invalidation": {},
            "reason_codes": ["failed_short_thesis"],
            "reason_labels": ["ショート仮説が崩れた"],
            "evidence": {},
            "normal_score_context": {},
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
        }
        current["summary_subject"] = build_summary_subject(current)

        summary_body, _provider = build_summary_body(
            provider="api",
            api_key="x",
            model="gpt-4o",
            cli_command="",
            timeout_sec=1,
            retry_count=0,
            base_dir=BASE_DIR,
            result_payload=current,
        )
        html = build_notification_detail_html(current)

        self.assertIn("候補失効 / 再評価済み", summary_body)
        self.assertIn("候補失効 / 再評価済み", html)
        self.assertIn('id="big-chance"', html)
        self.assertIn("Big Chance is not an entry instruction", html)
        self.assertNotIn("通常スコアとは別の report-only な失敗仮説チャンスです。", summary_body)
        self.assertNotIn("通常スコアとは別の report-only な失敗仮説チャンスです。", html)


if __name__ == "__main__":
    unittest.main()
