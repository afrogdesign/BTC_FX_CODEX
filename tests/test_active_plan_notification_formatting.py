from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import format_active_plan_notification_contract


class ActivePlanNotificationFormattingTest(unittest.TestCase):
    def _preview_cli_args(self) -> list[str]:
        return [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-active-plan-notification-preview",
            "--generated-at-jst",
            "2026-06-10T12:34:56+09:00",
            "--data-freshness",
            "15m latest-window exchange-auto-public",
            "--symbol",
            "BTC_USDT",
            "--timeframe",
            "15m",
            "--data-source",
            "exchange-auto-public",
            "--detail-report-path",
            "運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md",
            "--market-status-summary",
            "intraperiod evidence shows mixed TP1 / SL / pending outcomes",
            "--active-plan-label",
            "ACTIVE_LIMIT_RETEST",
            "--side",
            "long",
            "--entry-mode",
            "limit_zone_mid",
            "--entry-condition",
            "entry zone must be touched before consideration",
            "--tp-plan",
            "TP1 63507.96, TP2 64004.74",
            "--sl-or-invalidation",
            "SL 62469.23",
            "--timeout-or-wait-limit",
            "timeout after 4h",
            "--intraperiod-evidence-summary",
            "88 outcomes with 35 tp1_first, 39 sl_first, 12 pending",
            "--pending-caveat",
            "12 pending rows remain and reduce confidence",
        ]

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

    def test_write_active_plan_notification_preview_cli_stdout_only(self) -> None:
        result = subprocess.run(
            self._preview_cli_args(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("BTCFX Ver03-v2 report-only notification", result.stdout)
        self.assertIn("report-only", result.stdout)
        self.assertIn("not FORMAL_GO", result.stdout)
        self.assertIn("no automatic order", result.stdout)
        self.assertIn("ACTIVE_* is action guidance only", result.stdout)
        self.assertIn("detail_report_path", result.stdout)
        self.assertNotIn("notification_kind", result.stdout)

    def test_write_active_plan_notification_preview_cli_output_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "preview.txt"
            result = subprocess.run(
                self._preview_cli_args() + ["--output-path", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), result.stdout)
            self.assertIn("BTCFX Ver03-v2 report-only notification", result.stdout)
            self.assertIn("report-only", result.stdout)
            self.assertIn("not FORMAL_GO", result.stdout)
            self.assertIn("no automatic order", result.stdout)
            self.assertIn("ACTIVE_* is action guidance only", result.stdout)
            self.assertIn("detail_report_path", result.stdout)
            self.assertNotIn("notification_kind", result.stdout)

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
