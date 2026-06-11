from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import format_active_plan_notification_contract
import tools.log_feedback as log_feedback


class ActivePlanNotificationFormattingTest(unittest.TestCase):
    def _preview_cli_args(self, extra_args: list[str] | None = None, *, include_detail_report_path: bool = True) -> list[str]:
        args = [
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
        if include_detail_report_path:
            args.extend(
                [
                    "--detail-report-path",
                    "運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md",
                ]
            )
        if extra_args:
            args.extend(extra_args)
        return args

    def _preview_argv(self, extra_args: list[str] | None = None) -> list[str]:
        argv = [
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
        if extra_args:
            argv.extend(extra_args)
        return argv

    def _run_preview_main(self, extra_args: list[str], base_dir: Path | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(sys, "argv", self._preview_argv(extra_args)):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _write_intraperiod_report(self, base_dir: Path, date: str, contents: str) -> Path:
        path = base_dir / "運用資料" / "reports" / "analysis" / f"active_plan_candidate_intraperiod_outcomes_{date}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    def _preview_kwargs(self) -> dict[str, str]:
        return {
            "generated_at_jst": "2026-06-10T12:34:56+09:00",
            "data_freshness": "15m latest-window exchange-auto-public",
            "symbol": "BTC_USDT",
            "timeframe": "15m",
            "data_source": "exchange-auto-public",
            "detail_report_path": "運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md",
            "market_status_summary": "intraperiod evidence shows mixed TP1 / SL / pending outcomes",
            "active_plan_label": "ACTIVE_LIMIT_RETEST",
            "side": "long",
            "entry_mode": "limit_zone_mid",
            "entry_condition": "entry zone must be touched before consideration",
            "tp_plan": "TP1 63507.96, TP2 64004.74",
            "sl_or_invalidation": "SL 62469.23",
            "timeout_or_wait_limit": "timeout after 4h",
            "intraperiod_evidence_summary": "88 outcomes with 35 tp1_first, 39 sl_first, 12 pending",
            "pending_caveat": "12 pending rows remain and reduce confidence",
        }

    def _expected_preview_body(self) -> str:
        return format_active_plan_notification_contract(**self._preview_kwargs())

    def _expected_manual_delivery_checklist(self) -> str:
        return "\n".join(
            [
                "Manual delivery checklist",
                "",
                "- report-only wording is visible",
                "- not FORMAL_GO is visible",
                "- no automatic order wording is visible",
                "- ACTIVE_* guidance-only wording is visible",
                "- pending caveat is visible",
                "- detail_report_path is visible",
                "- symbol, timeframe, and data freshness are visible",
                "- entry, TP, SL, and timeout are visible",
                "- a human inspected the detailed report and market context or intentionally chose not to trade",
                "- no automatic trade/order action will be taken from the message",
                "- the external app choice and any send/post/share action are human actions outside repo automation",
            ]
        )

    def _expected_preview_body_with_checklist(self) -> str:
        return f"{self._expected_preview_body()}\n\n{self._expected_manual_delivery_checklist()}"

    def test_format_active_plan_notification_contract_includes_required_fields_and_guardrails(self) -> None:
        body = self._expected_preview_body()

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
        self.assertNotIn("Manual delivery checklist", result.stdout)
        self.assertNotIn("notification_kind", result.stdout)
        self.assertEqual(result.stdout, self._expected_preview_body())

    def test_write_active_plan_notification_preview_cli_output_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "preview.txt"
            result = subprocess.run(
                self._preview_cli_args(["--output-path", str(output_path)]),
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
            self.assertNotIn("Manual delivery checklist", result.stdout)
            self.assertNotIn("notification_kind", result.stdout)
            self.assertEqual(result.stdout, self._expected_preview_body())

    def test_resolve_latest_intraperiod_report_relative_path_uses_latest_matching_report(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            self._write_intraperiod_report(base_dir, "20260609", "older")
            latest_report = self._write_intraperiod_report(base_dir, "20260610", "latest")

            resolved = log_feedback._resolve_latest_active_plan_intraperiod_report_relative_path(base_dir)

            self.assertEqual(resolved, latest_report.relative_to(base_dir).as_posix())
            self.assertEqual(latest_report.read_text(encoding="utf-8"), "latest")

    def test_write_active_plan_notification_preview_cli_uses_latest_intraperiod_report_when_requested(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest")

            code, stdout, stderr = self._run_preview_main(["--use-latest-intraperiod-report"], base_dir=base_dir)

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertEqual(
                stdout,
                format_active_plan_notification_contract(
                    **{
                        **self._preview_kwargs(),
                        "detail_report_path": latest_report.relative_to(base_dir).as_posix(),
                    }
                ),
            )
            self.assertEqual(latest_report.read_text(encoding="utf-8"), "latest")

    def test_write_active_plan_notification_preview_cli_requires_detail_or_latest_flag(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            code, stdout, stderr = self._run_preview_main([], base_dir=base_dir)

            self.assertNotEqual(code, 0)
            self.assertEqual(stdout, "")
            self.assertIn("--detail-report-path is required unless --use-latest-intraperiod-report is supplied", stderr)

    def test_write_active_plan_notification_preview_cli_errors_when_latest_intraperiod_report_missing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            code, stdout, stderr = self._run_preview_main(["--use-latest-intraperiod-report"], base_dir=base_dir)

            self.assertNotEqual(code, 0)
            self.assertEqual(stdout, "")
            self.assertIn("no report found for family: active_plan_candidate_intraperiod_outcomes", stderr)

    def test_write_active_plan_notification_preview_cli_stdout_only_with_manual_delivery_checklist(self) -> None:
        result = subprocess.run(
            self._preview_cli_args(["--include-manual-delivery-checklist"]),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Manual delivery checklist", result.stdout)
        self.assertIn("report-only", result.stdout)
        self.assertIn("not FORMAL_GO", result.stdout)
        self.assertIn("no automatic order", result.stdout)
        self.assertIn("ACTIVE_*", result.stdout)
        self.assertIn("pending", result.stdout)
        self.assertIn("detail_report_path", result.stdout)
        self.assertIn("human actions outside repo automation", result.stdout)
        self.assertEqual(result.stdout, self._expected_preview_body_with_checklist())

    def test_write_active_plan_notification_preview_cli_output_path_with_manual_delivery_checklist(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "preview.txt"
            result = subprocess.run(
                self._preview_cli_args(["--include-manual-delivery-checklist", "--output-path", str(output_path)]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), result.stdout)
            self.assertIn("Manual delivery checklist", result.stdout)
            self.assertIn("report-only", result.stdout)
            self.assertIn("not FORMAL_GO", result.stdout)
            self.assertIn("no automatic order", result.stdout)
            self.assertIn("ACTIVE_*", result.stdout)
            self.assertIn("pending", result.stdout)
            self.assertIn("detail_report_path", result.stdout)
            self.assertIn("human actions outside repo automation", result.stdout)
            self.assertEqual(result.stdout, self._expected_preview_body_with_checklist())

    def test_format_active_plan_notification_contract_keeps_output_deterministic(self) -> None:
        kwargs = self._preview_kwargs()
        kwargs["pending_caveat"] = ""
        body1 = format_active_plan_notification_contract(**kwargs)
        body2 = format_active_plan_notification_contract(**kwargs)
        self.assertEqual(body1, body2)
        self.assertIn("pending_caveat: none", body1)


if __name__ == "__main__":
    unittest.main()
