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
        self.assertIn("【Big Chance / Failed Thesis】", summary_body)
        self.assertIn("Big Chance / Failed Thesis", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", summary_body)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertIn("Failed thesis is opportunity", summary_body)


if __name__ == "__main__":
    unittest.main()
