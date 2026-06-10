from __future__ import annotations

import sys
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import format_active_plan_notification_contract


class ActivePlanNotificationFormattingTest(unittest.TestCase):
    def test_format_active_plan_notification_contract_includes_required_fields_and_guardrails(self) -> None:
        body = format_active_plan_notification_contract(
            generated_at_jst="2026-06-10T12:34:56+09:00",
            data_freshness="15m latest-window exchange-auto-public",
            symbol="BTC_USDT",
            timeframe="15m",
            data_source="exchange-auto-public",
            detail_report_path="運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md",
            market_status_summary="intraperiod evidence shows mixed TP1 / SL / pending outcomes",
            active_plan_label="ACTIVE_LIMIT_RETEST",
            side="long",
            entry_mode="limit_zone_mid",
            entry_condition="entry zone must be touched before consideration",
            tp_plan="TP1 63507.96, TP2 64004.74",
            sl_or_invalidation="SL 62469.23",
            timeout_or_wait_limit="timeout after 4h",
            intraperiod_evidence_summary="88 outcomes with 35 tp1_first, 39 sl_first, 12 pending",
            pending_caveat="12 pending rows remain and reduce confidence",
        )

        expected_labels = [
            "generated_at_jst",
            "data_freshness",
            "symbol",
            "timeframe",
            "data_source",
            "report_mode",
            "formal_go_status",
            "auto_order_status",
            "detail_report_path",
            "market_status_summary",
            "active_plan_label",
            "side",
            "entry_mode",
            "entry_condition",
            "tp_plan",
            "sl_or_invalidation",
            "timeout_or_wait_limit",
            "intraperiod_evidence_summary",
            "pending_caveat",
        ]
        for label in expected_labels:
            with self.subTest(label=label):
                self.assertIn(label, body)

        self.assertIn("report-only", body)
        self.assertIn("not FORMAL_GO", body)
        self.assertIn("no automatic order", body)
        self.assertIn("ACTIVE_* is action guidance only", body)
        self.assertIn("12 pending rows remain and reduce confidence", body)
        self.assertIn("BTCFX Ver03-v2 report-only notification", body)

    def test_format_active_plan_notification_contract_keeps_output_deterministic(self) -> None:
        kwargs = dict(
            generated_at_jst="2026-06-10T12:34:56+09:00",
            data_freshness="15m latest-window exchange-auto-public",
            symbol="BTC_USDT",
            timeframe="15m",
            data_source="exchange-auto-public",
            detail_report_path="運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md",
            market_status_summary="mixed",
            active_plan_label="ACTIVE_LIMIT_RETEST",
            side="long",
            entry_mode="limit_zone_mid",
            entry_condition="entry zone must be touched before consideration",
            tp_plan="TP1 63507.96, TP2 64004.74",
            sl_or_invalidation="SL 62469.23",
            timeout_or_wait_limit="timeout after 4h",
            intraperiod_evidence_summary="88 outcomes",
            pending_caveat="",
        )
        body1 = format_active_plan_notification_contract(**kwargs)
        body2 = format_active_plan_notification_contract(**kwargs)
        self.assertEqual(body1, body2)
        self.assertIn("pending_caveat: none", body1)


if __name__ == "__main__":
    unittest.main()
