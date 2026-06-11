from __future__ import annotations

import contextlib
import csv
import io
import json
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import format_active_plan_notification_contract
from tools.log_feedback import format_active_plan_pending_coverage_caveat
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

    def _latest_manual_preview_argv(self, extra_args: list[str] | None = None) -> list[str]:
        argv = [
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-latest-active-plan-manual-preview",
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

    def _latest_manual_preview_cli_args(self, extra_args: list[str] | None = None) -> list[str]:
        args = [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-latest-active-plan-manual-preview",
        ]
        if extra_args:
            args.extend(extra_args)
        return args

    def _latest_manual_delivery_package_argv(self, extra_args: list[str] | None = None) -> list[str]:
        argv = [
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-latest-active-plan-manual-delivery-package",
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

    def _latest_manual_delivery_files_argv(self, output_dir: Path, extra_args: list[str] | None = None) -> list[str]:
        argv = [
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-latest-active-plan-manual-delivery-files",
            "--output-dir",
            str(output_dir),
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

    def _latest_manual_delivery_files_from_json_argv(
        self,
        input_json: Path,
        output_dir: Path,
        extra_args: list[str] | None = None,
    ) -> list[str]:
        argv = [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-latest-active-plan-manual-delivery-files-from-json",
            "--input-json",
            str(input_json),
            "--output-dir",
            str(output_dir),
        ]
        if extra_args:
            argv.extend(extra_args)
        return argv

    def _manual_delivery_source_files_argv(self, extra_args: list[str] | None = None) -> list[str]:
        argv = [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "resolve-latest-manual-delivery-source-files",
        ]
        if extra_args:
            argv.extend(extra_args)
        return argv

    def _manual_delivery_input_json_argv(self, output_json: Path, extra_args: list[str] | None = None) -> list[str]:
        argv = [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-latest-manual-delivery-input-json",
            "--output-json",
            str(output_json),
        ]
        if extra_args:
            argv.extend(extra_args)
        return argv

    def _manual_delivery_local_inbox_argv(
        self,
        input_json: Path,
        bundle_dir: Path,
        output_md: Path,
        extra_args: list[str] | None = None,
    ) -> list[str]:
        argv = [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "write-latest-manual-delivery-local-inbox",
            "--input-json",
            str(input_json),
            "--bundle-dir",
            str(bundle_dir),
            "--output-md",
            str(output_md),
        ]
        if extra_args:
            argv.extend(extra_args)
        return argv

    def _pending_coverage_caveat_argv(self, extra_args: list[str] | None = None) -> list[str]:
        argv = [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "format-active-plan-pending-coverage-caveat",
        ]
        if extra_args:
            argv.extend(extra_args)
        return argv

    def _pending_coverage_caveat_from_csv_argv(self, extra_args: list[str] | None = None) -> list[str]:
        argv = [
            sys.executable,
            str(BASE_DIR / "tools" / "log_feedback.py"),
            "format-active-plan-pending-coverage-caveat-from-csv",
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

    def _run_latest_manual_preview_main(self, extra_args: list[str], base_dir: Path | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(sys, "argv", self._latest_manual_preview_argv(extra_args)):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_latest_manual_preview_main_with_argv(self, argv: list[str], base_dir: Path | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(
                sys,
                "argv",
                [str(BASE_DIR / "tools" / "log_feedback.py"), "write-latest-active-plan-manual-preview", *argv],
            ):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_latest_manual_delivery_package_main(self, extra_args: list[str], base_dir: Path | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(sys, "argv", self._latest_manual_delivery_package_argv(extra_args)):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_latest_manual_delivery_package_main_with_argv(self, argv: list[str], base_dir: Path | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(
                sys,
                "argv",
                [str(BASE_DIR / "tools" / "log_feedback.py"), "write-latest-active-plan-manual-delivery-package", *argv],
            ):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_latest_manual_delivery_files_main(self, extra_args: list[str], base_dir: Path | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        output_dir = resolved_base_dir / "tmp-manual-delivery-files"
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(sys, "argv", self._latest_manual_delivery_files_argv(output_dir, extra_args)):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_latest_manual_delivery_files_main_with_argv(self, argv: list[str], base_dir: Path | None = None) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(
                sys,
                "argv",
                [str(BASE_DIR / "tools" / "log_feedback.py"), "write-latest-active-plan-manual-delivery-files", *argv],
            ):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_manual_delivery_source_files_main_with_argv(
        self,
        argv: list[str],
        base_dir: Path | None = None,
    ) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(
                sys,
                "argv",
                [str(BASE_DIR / "tools" / "log_feedback.py"), "resolve-latest-manual-delivery-source-files", *argv],
            ):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_manual_delivery_input_json_main_with_argv(
        self,
        argv: list[str],
        base_dir: Path | None = None,
    ) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(
                sys,
                "argv",
                [str(BASE_DIR / "tools" / "log_feedback.py"), "write-latest-manual-delivery-input-json", *argv],
            ):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    try:
                        log_feedback.main()
                    except SystemExit as exc:
                        code = int(exc.code) if isinstance(exc.code, int) else 1
                    else:
                        code = 0
        return code, stdout.getvalue(), stderr.getvalue()

    def _run_manual_delivery_local_inbox_main_with_argv(
        self,
        argv: list[str],
        base_dir: Path | None = None,
    ) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        resolved_base_dir = base_dir or BASE_DIR
        with mock.patch.object(log_feedback, "BASE_DIR", resolved_base_dir):
            with mock.patch.object(
                sys,
                "argv",
                [str(BASE_DIR / "tools" / "log_feedback.py"), "write-latest-manual-delivery-local-inbox", *argv],
            ):
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

    def _write_intraperiod_outcomes_csv(self, base_dir: Path, rows: list[dict[str, str]]) -> Path:
        path = base_dir / "logs" / "csv" / "active_plan_candidate_intraperiod_outcomes.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=["timestamp_jst", "outcome", "first_exit_reason"])
            writer.writeheader()
            writer.writerows(rows)
        return path

    def _write_manual_delivery_input_json(self, base_dir: Path, *, pending_caveat: str, include_manual_delivery_checklist: bool = False) -> Path:
        path = base_dir / "manual-delivery-input.json"
        path.write_text(
            json.dumps(
                {
                    "generated_at_jst": "2026-06-11T01:23:45+09:00",
                    "symbol": "ETH_USDT",
                    "timeframe": "30m",
                    "data_source": "exchange-auto-public",
                    "data_freshness": "30m latest-window exchange-auto-public",
                    "market_status_summary": "report-only manual preview; not FORMAL_GO; no automatic order",
                    "active_plan_label": "ACTIVE_LIMIT_RETEST",
                    "side": "short",
                    "entry_mode": "limit_zone_mid",
                    "entry_condition": "entry zone must be touched before consideration",
                    "tp_plan": "TP1/TP2 from JSON",
                    "sl_or_invalidation": "SL from JSON",
                    "timeout_or_wait_limit": "timeout after JSON window",
                    "intraperiod_evidence_summary": "JSON provided evidence summary",
                    "pending_caveat": pending_caveat,
                    "include_manual_delivery_checklist": include_manual_delivery_checklist,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return path

    def _pending_coverage_caveat_csv_rows(self) -> list[dict[str, str]]:
        jst = timezone(timedelta(hours=9))
        base_dt = datetime(2026, 6, 11, 0, 0, 0, tzinfo=jst)
        rows: list[dict[str, str]] = []
        for index in range(88):
            timestamp = (base_dt - timedelta(minutes=index)).isoformat(timespec="seconds")
            if index < 11:
                outcome = "pending"
                first_exit_reason = ""
            elif index == 11:
                outcome = "entry_not_touched_by_simple_range_check"
                first_exit_reason = "entry_not_touched_by_simple_range_check"
            elif index == 12:
                outcome = "pending"
                first_exit_reason = ""
            else:
                outcome = "tp1_first"
                first_exit_reason = "tp1_hit_first"
            rows.append(
                {
                    "timestamp_jst": timestamp,
                    "outcome": outcome,
                    "first_exit_reason": first_exit_reason,
                }
            )
        return rows

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

    def test_format_active_plan_pending_coverage_caveat_is_deterministic_across_core_cases(self) -> None:
        cases = [
            (
                "coverage_caveat",
                {
                    "total_outcome_rows": 88,
                    "resolved_rows": 76,
                    "pending_rows": 12,
                    "recent_unresolved_windows": 11,
                    "entry_not_touched_count": 1,
                },
                "pending_coverage_caveat: total_outcome_rows=88; resolved_rows=76; pending_rows=12; pending_rate=13.6%; recent_unresolved_windows=11; entry_not_touched_count=1; count_consistency=matches; diagnostic=coverage_caveat; action=reduce_confidence_and_review_detail_report_manually; safety=report-only_not_FORMAL_GO_no_automatic_order",
            ),
            (
                "no_intraperiod_evidence",
                {
                    "total_outcome_rows": 0,
                    "resolved_rows": 0,
                    "pending_rows": 0,
                    "recent_unresolved_windows": 0,
                    "entry_not_touched_count": 0,
                },
                "pending_coverage_caveat: total_outcome_rows=0; resolved_rows=0; pending_rows=0; pending_rate=n/a; recent_unresolved_windows=0; entry_not_touched_count=0; count_consistency=matches; diagnostic=no_intraperiod_evidence; action=do_not_use_as_trade_trigger; safety=report-only_not_FORMAL_GO_no_automatic_order",
            ),
            (
                "coverage_ok",
                {
                    "total_outcome_rows": 76,
                    "resolved_rows": 76,
                    "pending_rows": 0,
                    "recent_unresolved_windows": 0,
                    "entry_not_touched_count": 0,
                },
                "pending_coverage_caveat: total_outcome_rows=76; resolved_rows=76; pending_rows=0; pending_rate=0.0%; recent_unresolved_windows=0; entry_not_touched_count=0; count_consistency=matches; diagnostic=coverage_ok; action=still_review_detail_report_manually; safety=report-only_not_FORMAL_GO_no_automatic_order",
            ),
            (
                "count_mismatch",
                {
                    "total_outcome_rows": 10,
                    "resolved_rows": 6,
                    "pending_rows": 3,
                    "recent_unresolved_windows": 0,
                    "entry_not_touched_count": 0,
                },
                "pending_coverage_caveat: total_outcome_rows=10; resolved_rows=6; pending_rows=3; pending_rate=30.0%; recent_unresolved_windows=0; entry_not_touched_count=0; count_consistency=mismatch_review_required; diagnostic=coverage_caveat; action=reduce_confidence_and_review_detail_report_manually; safety=report-only_not_FORMAL_GO_no_automatic_order",
            ),
        ]

        for name, kwargs, expected in cases:
            with self.subTest(name=name):
                self.assertEqual(format_active_plan_pending_coverage_caveat(**kwargs), expected)

    def test_format_active_plan_pending_coverage_caveat_cli_stdout_and_help(self) -> None:
        help_result = subprocess.run(
            self._pending_coverage_caveat_argv(["--help"]),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0, msg=help_result.stderr)
        self.assertIn("format-active-plan-pending-coverage-caveat", help_result.stdout)
        self.assertIn("--total-outcome-rows", help_result.stdout)
        self.assertIn("--pending-rows", help_result.stdout)

        result = subprocess.run(
            self._pending_coverage_caveat_argv(
                [
                    "--total-outcome-rows",
                    "88",
                    "--resolved-rows",
                    "76",
                    "--pending-rows",
                    "12",
                    "--recent-unresolved-windows",
                    "11",
                    "--entry-not-touched-count",
                    "1",
                ]
            ),
            capture_output=True,
            text=True,
            check=False,
        )

        expected = (
            "pending_coverage_caveat: total_outcome_rows=88; resolved_rows=76; pending_rows=12; "
            "pending_rate=13.6%; recent_unresolved_windows=11; entry_not_touched_count=1; "
            "count_consistency=matches; diagnostic=coverage_caveat; "
            "action=reduce_confidence_and_review_detail_report_manually; "
            "safety=report-only_not_FORMAL_GO_no_automatic_order"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, f"{expected}\n")

    def test_format_active_plan_pending_coverage_caveat_cli_rejects_negative_input(self) -> None:
        result = subprocess.run(
            self._pending_coverage_caveat_argv(
                [
                    "--total-outcome-rows",
                    "88",
                    "--resolved-rows",
                    "76",
                    "--pending-rows",
                    "-1",
                ]
            ),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("must be a non-negative integer", result.stderr)

    def test_format_active_plan_pending_coverage_caveat_from_csv_cli_summarizes_counts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            csv_path = self._write_intraperiod_outcomes_csv(base_dir, self._pending_coverage_caveat_csv_rows())
            before_text = csv_path.read_text(encoding="utf-8")

            result = subprocess.run(
                self._pending_coverage_caveat_from_csv_argv(
                    ["--intraperiod-outcomes-path", str(csv_path), "--recent-row-window", "12"]
                ),
                capture_output=True,
                text=True,
                check=False,
            )

            expected = (
                "pending_coverage_caveat: total_outcome_rows=88; resolved_rows=76; pending_rows=12; "
                "pending_rate=13.6%; recent_unresolved_windows=11; entry_not_touched_count=1; "
                "count_consistency=matches; diagnostic=coverage_caveat; "
                "action=reduce_confidence_and_review_detail_report_manually; "
                "safety=report-only_not_FORMAL_GO_no_automatic_order"
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, f"{expected}\n")
            self.assertEqual(csv_path.read_text(encoding="utf-8"), before_text)

    def test_format_active_plan_pending_coverage_caveat_from_csv_cli_missing_path_uses_no_evidence(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            missing_path = base_dir / "missing.csv"

            result = subprocess.run(
                self._pending_coverage_caveat_from_csv_argv(["--intraperiod-outcomes-path", str(missing_path)]),
                capture_output=True,
                text=True,
                check=False,
            )

            expected = (
                "pending_coverage_caveat: total_outcome_rows=0; resolved_rows=0; pending_rows=0; "
                "pending_rate=n/a; recent_unresolved_windows=0; entry_not_touched_count=0; "
                "count_consistency=matches; diagnostic=no_intraperiod_evidence; "
                "action=do_not_use_as_trade_trigger; safety=report-only_not_FORMAL_GO_no_automatic_order"
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, f"{expected}\n")

    def test_format_active_plan_pending_coverage_caveat_from_csv_cli_empty_file_uses_no_evidence(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            csv_path = base_dir / "empty.csv"
            csv_path.write_text("timestamp_jst,outcome,first_exit_reason\n", encoding="utf-8")
            before_text = csv_path.read_text(encoding="utf-8")

            result = subprocess.run(
                self._pending_coverage_caveat_from_csv_argv(["--intraperiod-outcomes-path", str(csv_path)]),
                capture_output=True,
                text=True,
                check=False,
            )

            expected = (
                "pending_coverage_caveat: total_outcome_rows=0; resolved_rows=0; pending_rows=0; "
                "pending_rate=n/a; recent_unresolved_windows=0; entry_not_touched_count=0; "
                "count_consistency=matches; diagnostic=no_intraperiod_evidence; "
                "action=do_not_use_as_trade_trigger; safety=report-only_not_FORMAL_GO_no_automatic_order"
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, f"{expected}\n")
            self.assertEqual(csv_path.read_text(encoding="utf-8"), before_text)

    def test_format_active_plan_pending_coverage_caveat_from_csv_cli_recent_window_is_deterministic(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            csv_path = base_dir / "intraperiod.csv"
            rows = [
                {
                    "timestamp_jst": (datetime(2026, 6, 11, 0, 30, tzinfo=timezone(timedelta(hours=9))) - timedelta(minutes=index)).isoformat(timespec="seconds"),
                    "outcome": "pending" if index in {0, 2} else "tp1_first",
                    "first_exit_reason": "",
                }
                for index in range(3)
            ]
            self._write_intraperiod_outcomes_csv(base_dir, rows).rename(csv_path)

            result_window_1 = subprocess.run(
                self._pending_coverage_caveat_from_csv_argv(["--intraperiod-outcomes-path", str(csv_path), "--recent-row-window", "1"]),
                capture_output=True,
                text=True,
                check=False,
            )
            result_window_3 = subprocess.run(
                self._pending_coverage_caveat_from_csv_argv(["--intraperiod-outcomes-path", str(csv_path), "--recent-row-window", "3"]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result_window_1.returncode, 0, msg=result_window_1.stderr)
            self.assertEqual(result_window_3.returncode, 0, msg=result_window_3.stderr)
            self.assertIn("recent_unresolved_windows=1", result_window_1.stdout)
            self.assertIn("recent_unresolved_windows=2", result_window_3.stdout)
            self.assertNotEqual(result_window_1.stdout, result_window_3.stdout)

    def test_format_active_plan_pending_coverage_caveat_from_csv_cli_rejects_negative_recent_window(self) -> None:
        result = subprocess.run(
            self._pending_coverage_caveat_from_csv_argv(
                [
                    "--intraperiod-outcomes-path",
                    str(BASE_DIR / "logs" / "csv" / "active_plan_candidate_intraperiod_outcomes.csv"),
                    "--recent-row-window",
                    "-1",
                ]
            ),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("must be a non-negative integer", result.stderr)

    def test_format_active_plan_pending_coverage_caveat_from_csv_cli_stdout_is_single_line(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            csv_path = self._write_intraperiod_outcomes_csv(base_dir, self._pending_coverage_caveat_csv_rows())

            help_result = subprocess.run(
                self._pending_coverage_caveat_from_csv_argv(["--help"]),
                capture_output=True,
                text=True,
                check=False,
            )
            result = subprocess.run(
                self._pending_coverage_caveat_from_csv_argv(["--intraperiod-outcomes-path", str(csv_path)]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(help_result.returncode, 0, msg=help_result.stderr)
            self.assertIn("format-active-plan-pending-coverage-caveat-from-csv", help_result.stdout)
            self.assertIn("--recent-row-window", help_result.stdout)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertTrue(result.stdout.endswith("\n"))
            self.assertEqual(len(result.stdout.rstrip("\n").splitlines()), 1)

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
        self.assertNotIn("manual trading support preview", result.stdout)
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
            self.assertNotIn("manual trading support preview", result.stdout)
            self.assertEqual(result.stdout, self._expected_preview_body())

    def test_write_active_plan_notification_preview_cli_practical_manual_preview_with_explicit_detail_report_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            detail_report_path = Path(tmpdir) / "detail_report.md"
            detail_report_path.write_text("practical preview detail", encoding="utf-8")
            before_text = detail_report_path.read_text(encoding="utf-8")
            result = subprocess.run(
                self._preview_cli_args(["--practical-manual-preview", "--detail-report-path", str(detail_report_path)]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(detail_report_path.read_text(encoding="utf-8"), before_text)

            stdout = result.stdout
            sections = [
                "BTCFX Ver03-v2 manual trading support preview",
                "Safety status",
                "Market context",
                "Active Plan guidance",
                "Manual decision checklist",
                "Detail report",
                "Caveats",
            ]
            positions = [stdout.index(section) for section in sections]
            self.assertEqual(positions, sorted(positions))

            required_fields = [
                "generated_at_jst",
                "data_freshness",
                "symbol",
                "timeframe",
                "data_source",
                "active_plan_label",
                "side",
                "entry_mode",
                "entry_condition",
                "tp_plan",
                "sl_or_invalidation",
                "timeout_or_wait_limit",
                "intraperiod_evidence_summary",
                "pending_caveat",
                "detail_report_path",
            ]
            for field in required_fields:
                with self.subTest(field=field):
                    self.assertIn(field, stdout)

            safety_phrases = [
                "report-only",
                "not FORMAL_GO",
                "no automatic order",
                "ACTIVE_* is action guidance only",
                "human must decide manually",
            ]
            for phrase in safety_phrases:
                with self.subTest(phrase=phrase):
                    self.assertIn(phrase, stdout)

            self.assertNotIn("formal_go_status: FORMAL_GO", stdout)
            self.assertNotIn("place a trade automatically", stdout)
            self.assertNotIn("automatic order should be placed", stdout)

    def test_write_active_plan_notification_preview_cli_practical_manual_preview_uses_latest_intraperiod_report(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            older_report = self._write_intraperiod_report(base_dir, "20260610", "older report")
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            latest_before = latest_report.read_text(encoding="utf-8")
            older_before = older_report.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_preview_main(
                ["--use-latest-intraperiod-report", "--practical-manual-preview"],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertNotIn(older_report.relative_to(base_dir).as_posix(), stdout)
            self.assertEqual(latest_report.read_text(encoding="utf-8"), latest_before)
            self.assertEqual(older_report.read_text(encoding="utf-8"), older_before)
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", stdout)
            self.assertIn("report-only", stdout)
            self.assertIn("not FORMAL_GO", stdout)
            self.assertIn("no automatic order", stdout)
            self.assertIn("ACTIVE_* is action guidance only", stdout)

    def test_write_active_plan_notification_preview_cli_practical_manual_preview_with_manual_delivery_checklist(self) -> None:
        result = subprocess.run(
            self._preview_cli_args(["--practical-manual-preview", "--include-manual-delivery-checklist"]),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("BTCFX Ver03-v2 manual trading support preview", result.stdout)
        self.assertIn("Manual delivery checklist", result.stdout)
        self.assertIn("report-only", result.stdout)
        self.assertIn("not FORMAL_GO", result.stdout)
        self.assertIn("no automatic order", result.stdout)
        self.assertIn("ACTIVE_* is action guidance only", result.stdout)
        self.assertIn("human must decide manually", result.stdout)
        self.assertIn("detail_report_path", result.stdout)
        self.assertEqual(result.stdout.count("Manual delivery checklist"), 1)

    def test_write_latest_active_plan_manual_preview_cli_prints_input_json_template(self) -> None:
        result = subprocess.run(
            self._latest_manual_preview_cli_args(["--print-input-json-template"]),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        template = json.loads(result.stdout)
        self.assertIsInstance(template, dict)
        self.assertEqual(template["include_manual_delivery_checklist"], False)
        self.assertIn("report-only", template["market_status_summary"])
        self.assertIn("not FORMAL_GO", template["market_status_summary"])
        self.assertIn("no automatic order", template["market_status_summary"])
        self.assertIn("report-only", template["pending_caveat"])
        self.assertIn("human must decide manually", template["pending_caveat"])
        self.assertEqual(
            set(template),
            {
                "generated_at_jst",
                "symbol",
                "timeframe",
                "data_source",
                "data_freshness",
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
                "include_manual_delivery_checklist",
            },
        )
        self.assertNotIn("manual trading support preview", result.stdout)

    def test_write_latest_active_plan_manual_preview_cli_writes_input_json_template(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "manual-preview-input.json"

            result = subprocess.run(
                self._latest_manual_preview_cli_args(["--write-input-json-template", str(output_path)]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output_path.parent.exists())
            self.assertTrue(output_path.exists())
            self.assertIn(str(output_path), result.stdout)
            template = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertIsInstance(template, dict)
            self.assertEqual(template["include_manual_delivery_checklist"], False)
            self.assertEqual(
                set(template),
                {
                    "generated_at_jst",
                    "symbol",
                    "timeframe",
                    "data_source",
                    "data_freshness",
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
                    "include_manual_delivery_checklist",
                },
            )
            self.assertIn("report-only", template["market_status_summary"])
            self.assertIn("not FORMAL_GO", template["market_status_summary"])
            self.assertIn("no automatic order", template["market_status_summary"])
            self.assertIn("human must decide manually", template["pending_caveat"])

    def test_write_latest_active_plan_manual_preview_cli_prints_and_writes_input_json_template(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "manual-preview-input.json"

            result = subprocess.run(
                self._latest_manual_preview_cli_args(
                    ["--print-input-json-template", "--write-input-json-template", str(output_path)]
                ),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output_path.exists())
            stdout_template = json.loads(result.stdout)
            file_template = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(stdout_template, file_template)
            self.assertEqual(stdout_template["include_manual_delivery_checklist"], False)
            self.assertIn("report-only", stdout_template["market_status_summary"])
            self.assertIn("not FORMAL_GO", stdout_template["market_status_summary"])
            self.assertIn("no automatic order", stdout_template["market_status_summary"])
            self.assertIn("human must decide manually", stdout_template["pending_caveat"])

    def test_write_latest_active_plan_manual_delivery_package_cli_uses_latest_report_and_orders_sections(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            older_report = self._write_intraperiod_report(base_dir, "20260610", "older report")
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            latest_before = latest_report.read_text(encoding="utf-8")
            older_before = older_report.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_latest_manual_delivery_package_main([], base_dir=base_dir)

            self.assertEqual(code, 0, msg=stderr)
            sections = [
                "Manual delivery copy package",
                "Copy-ready subject",
                "Copy-ready body",
                "Human send checklist",
                "Safety boundary",
            ]
            positions = [stdout.index(section) for section in sections]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("subject: BTCFX Ver03-v2 report-only | BTC_USDT | 15m | ACTIVE_LIMIT_RETEST | long | report-only", stdout)
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", stdout)
            self.assertIn("report-only", stdout)
            self.assertIn("not FORMAL_GO", stdout)
            self.assertIn("no automatic order", stdout)
            self.assertIn("ACTIVE_* is action guidance only", stdout)
            self.assertIn("human must decide manually", stdout)
            self.assertIn("copy/paste is a human action outside repo automation", stdout)
            self.assertIn("confirm no automatic order is triggered", stdout)
            self.assertIn("confirm not FORMAL_GO", stdout)
            self.assertIn("confirm generated preview files are not committed unless explicitly approved", stdout)
            self.assertIn("manual external app", stdout)
            self.assertIn("no external notification integration", stdout)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertNotIn(older_report.relative_to(base_dir).as_posix(), stdout)
            self.assertEqual(latest_report.read_text(encoding="utf-8"), latest_before)
            self.assertEqual(older_report.read_text(encoding="utf-8"), older_before)

    def test_write_latest_active_plan_manual_delivery_package_cli_subject_prefix_and_target_override(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            self._write_intraperiod_report(base_dir, "20260611", "latest report")

            code, stdout, stderr = self._run_latest_manual_delivery_package_main(
                ["--subject-prefix", "BTCFX CUSTOM report-only", "--delivery-target-label", "custom external app"],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn("subject: BTCFX CUSTOM report-only | BTC_USDT | 15m | ACTIVE_LIMIT_RETEST | long | report-only", stdout)
            self.assertIn("custom external app", stdout)

    def test_write_latest_active_plan_manual_delivery_package_cli_supports_input_json_and_output_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            input_json = base_dir / "manual-delivery-input.json"
            input_json.write_text(
                json.dumps(
                    {
                        "generated_at_jst": "2026-06-11T01:23:45+09:00",
                        "symbol": "ETH_USDT",
                        "timeframe": "30m",
                        "data_source": "exchange-auto-public",
                        "data_freshness": "30m latest-window exchange-auto-public",
                        "market_status_summary": "report-only manual preview; not FORMAL_GO; no automatic order",
                        "active_plan_label": "ACTIVE_LIMIT_RETEST",
                        "side": "short",
                        "entry_mode": "limit_zone_mid",
                        "entry_condition": "entry zone must be touched before consideration",
                        "tp_plan": "TP1/TP2 from JSON",
                        "sl_or_invalidation": "SL from JSON",
                        "timeout_or_wait_limit": "timeout after JSON window",
                        "intraperiod_evidence_summary": "JSON provided evidence summary",
                        "pending_caveat": "report-only manual preview; human must decide manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            output_path = base_dir / "nested" / "manual-delivery-package.txt"

            code, stdout, stderr = self._run_latest_manual_delivery_package_main_with_argv(
                ["--input-json", str(input_json), "--output-path", str(output_path)],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertTrue(output_path.exists())
            self.assertEqual(stdout, output_path.read_text(encoding="utf-8"))
            self.assertIn("subject: BTCFX Ver03-v2 report-only | ETH_USDT | 30m | ACTIVE_LIMIT_RETEST | short | report-only", stdout)
            self.assertIn("ETH_USDT", stdout)
            self.assertIn("30m", stdout)
            self.assertIn("report-only", stdout)
            self.assertIn("not FORMAL_GO", stdout)
            self.assertIn("no automatic order", stdout)
            self.assertIn("ACTIVE_* is action guidance only", stdout)
            self.assertIn("human must decide manually", stdout)
            self.assertIn("manual external app", stdout)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertEqual(latest_report.read_text(encoding="utf-8"), "latest report")

    def test_write_latest_active_plan_manual_delivery_files_cli_creates_bundle_and_keeps_latest_report_unchanged(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            older_report = self._write_intraperiod_report(base_dir, "20260610", "older report")
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            latest_before = latest_report.read_text(encoding="utf-8")
            output_dir = base_dir / "nested" / "manual-delivery-bundle"

            code, stdout, stderr = self._run_latest_manual_delivery_files_main_with_argv(
                self._latest_manual_delivery_files_argv(output_dir, ["--include-manual-delivery-checklist"])[2:],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            lines = stdout.strip().splitlines()
            self.assertEqual(len(lines), 5)
            self.assertTrue(lines[0].startswith("subject_path="))
            self.assertTrue(lines[1].startswith("body_path="))
            self.assertTrue(lines[2].startswith("checklist_path="))
            self.assertTrue(lines[3].startswith("package_path="))
            self.assertTrue(lines[4].startswith("readme_path="))
            path_map: dict[str, Path] = {}
            for line in lines:
                key, value = line.split("=", 1)
                path_map[key] = Path(value)

            self.assertEqual(
                set(path_map),
                {"subject_path", "body_path", "checklist_path", "package_path", "readme_path"},
            )
            self.assertTrue(output_dir.exists())
            self.assertTrue(output_dir.parent.exists())
            for path in path_map.values():
                self.assertTrue(path.exists(), msg=str(path))

            subject_text = path_map["subject_path"].read_text(encoding="utf-8")
            body_text = path_map["body_path"].read_text(encoding="utf-8")
            checklist_text = path_map["checklist_path"].read_text(encoding="utf-8")
            package_text = path_map["package_path"].read_text(encoding="utf-8")
            readme_text = path_map["readme_path"].read_text(encoding="utf-8")
            package_stdout = self._run_latest_manual_delivery_package_main(
                ["--include-manual-delivery-checklist"],
                base_dir=base_dir,
            )[1]

            self.assertEqual(subject_text, "BTCFX Ver03-v2 report-only | BTC_USDT | 15m | ACTIVE_LIMIT_RETEST | long | report-only")
            self.assertNotIn("\n", subject_text)
            self.assertIn("report-only", subject_text)
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", body_text)
            self.assertNotIn("Manual delivery copy package", body_text)
            self.assertNotIn("Manual delivery checklist", body_text)
            self.assertIn("Human send checklist", checklist_text)
            self.assertIn("report-only", checklist_text)
            self.assertIn("not FORMAL_GO", checklist_text)
            self.assertIn("no automatic order", checklist_text)
            self.assertIn("ACTIVE_* is action guidance only", checklist_text)
            self.assertIn("human must decide manually", checklist_text)
            self.assertIn("manual external app", checklist_text)
            self.assertEqual(package_text, package_stdout)
            self.assertIn("Manual delivery local file bundle", readme_text)
            self.assertIn("report-only", readme_text)
            self.assertIn("not FORMAL_GO", readme_text)
            self.assertIn("no automatic order", readme_text)
            self.assertIn("ACTIVE_* is action guidance only", readme_text)
            self.assertIn("human must decide manually", readme_text)
            self.assertIn("no external notification integration", readme_text)
            self.assertIn("files are for manual copy/paste only", readme_text)
            self.assertIn("generated files must not be committed unless explicitly approved", readme_text)
            self.assertIn("no email, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, or address-book integration is performed", readme_text)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), package_text)
            self.assertEqual(latest_report.read_text(encoding="utf-8"), latest_before)
            self.assertEqual(older_report.read_text(encoding="utf-8"), "older report")

    def test_write_latest_active_plan_manual_delivery_files_cli_supports_input_json_and_overrides(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            input_json = base_dir / "manual-delivery-input.json"
            input_json.write_text(
                json.dumps(
                    {
                        "generated_at_jst": "2026-06-11T01:23:45+09:00",
                        "symbol": "ETH_USDT",
                        "timeframe": "30m",
                        "data_source": "exchange-auto-public",
                        "data_freshness": "30m latest-window exchange-auto-public",
                        "market_status_summary": "report-only manual preview; not FORMAL_GO; no automatic order",
                        "active_plan_label": "ACTIVE_LIMIT_RETEST",
                        "side": "short",
                        "entry_mode": "limit_zone_mid",
                        "entry_condition": "entry zone must be touched before consideration",
                        "tp_plan": "TP1/TP2 from JSON",
                        "sl_or_invalidation": "SL from JSON",
                        "timeout_or_wait_limit": "timeout after JSON window",
                        "intraperiod_evidence_summary": "JSON provided evidence summary",
                        "pending_caveat": "report-only manual preview; human must decide manually",
                        "include_manual_delivery_checklist": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            before_text = input_json.read_text(encoding="utf-8")
            output_dir = base_dir / "bundle" / "json"

            code, stdout, stderr = self._run_latest_manual_delivery_files_main_with_argv(
                [
                    "--output-dir",
                    str(output_dir),
                    "--input-json",
                    str(input_json),
                    "--subject-prefix",
                    "BTCFX CUSTOM report-only",
                    "--delivery-target-label",
                    "custom external app",
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(input_json.read_text(encoding="utf-8"), before_text)
            lines = stdout.strip().splitlines()
            self.assertEqual(len(lines), 5)
            self.assertTrue(lines[0].startswith("subject_path="))
            self.assertTrue(lines[1].startswith("body_path="))
            self.assertTrue(lines[2].startswith("checklist_path="))
            self.assertTrue(lines[3].startswith("package_path="))
            self.assertTrue(lines[4].startswith("readme_path="))
            path_map: dict[str, Path] = {}
            for line in lines:
                key, value = line.split("=", 1)
                path_map[key] = Path(value)
            self.assertTrue(output_dir.exists())
            self.assertIn("subject_path", path_map)
            self.assertIn("body_path", path_map)
            self.assertIn("checklist_path", path_map)
            self.assertIn("package_path", path_map)
            self.assertIn("readme_path", path_map)

            subject_text = path_map["subject_path"].read_text(encoding="utf-8")
            body_text = path_map["body_path"].read_text(encoding="utf-8")
            checklist_text = path_map["checklist_path"].read_text(encoding="utf-8")
            package_text = path_map["package_path"].read_text(encoding="utf-8")
            readme_text = path_map["readme_path"].read_text(encoding="utf-8")
            package_stdout = self._run_latest_manual_delivery_package_main_with_argv(
                [
                    "--input-json",
                    str(input_json),
                    "--subject-prefix",
                    "BTCFX CUSTOM report-only",
                    "--delivery-target-label",
                    "custom external app",
                ],
                base_dir=base_dir,
            )[1]

            self.assertEqual(subject_text, "BTCFX CUSTOM report-only | ETH_USDT | 30m | ACTIVE_LIMIT_RETEST | short | report-only")
            self.assertIn("ETH_USDT", body_text)
            self.assertIn("30m", body_text)
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", body_text)
            self.assertIn("custom external app", checklist_text)
            self.assertIn("custom external app", package_text)
            self.assertIn("report-only", readme_text)
            self.assertIn("no external notification integration", readme_text)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), package_text)
            self.assertEqual(package_text, package_stdout)
            self.assertEqual(latest_report.read_text(encoding="utf-8"), "latest report")

    def test_write_latest_active_plan_manual_delivery_files_from_json_cli_writes_bundle_and_auto_caveat(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_json = self._write_manual_delivery_input_json(
                base_dir,
                pending_caveat="manual json caveat",
                include_manual_delivery_checklist=True,
            )
            csv_path = self._write_intraperiod_outcomes_csv(base_dir, self._pending_coverage_caveat_csv_rows())
            output_dir = base_dir / "bundle" / "from-json"

            result = subprocess.run(
                self._latest_manual_delivery_files_from_json_argv(
                    input_json,
                    output_dir,
                    [
                        "--auto-pending-caveat-from-csv",
                        "--intraperiod-outcomes-path",
                        str(csv_path),
                        "--recent-row-window",
                        "12",
                    ],
                ),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, f"{output_dir}\n")

            subject_path = output_dir / "subject.txt"
            body_path = output_dir / "body.txt"
            checklist_path = output_dir / "checklist.txt"
            package_path = output_dir / "package.txt"
            readme_path = output_dir / "README.txt"
            for path in [subject_path, body_path, checklist_path, package_path, readme_path]:
                self.assertTrue(path.exists(), msg=str(path))

            self.assertEqual(
                subject_path.read_text(encoding="utf-8"),
                "BTCFX Ver03-v2 report-only | ETH_USDT | 30m | ACTIVE_LIMIT_RETEST | short | report-only",
            )
            body_text = body_path.read_text(encoding="utf-8")
            package_text = package_path.read_text(encoding="utf-8")
            checklist_text = checklist_path.read_text(encoding="utf-8")
            readme_text = readme_path.read_text(encoding="utf-8")

            self.assertIn("pending_coverage_caveat:", body_text)
            self.assertIn("diagnostic=coverage_caveat", body_text)
            self.assertIn("report-only", body_text)
            self.assertIn("not FORMAL_GO", body_text)
            self.assertIn("no automatic order", body_text)
            self.assertIn("ACTIVE_* is action guidance only", body_text)
            self.assertIn("human must decide manually", body_text)
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", package_text)
            self.assertIn("pending_coverage_caveat:", package_text)
            self.assertIn("diagnostic=coverage_caveat", package_text)
            self.assertIn("Human send checklist", package_text)
            self.assertIn("delivery target label: manual external app", checklist_text)
            self.assertIn("human must decide manually", checklist_text)
            self.assertIn("no external notification integration", readme_text)
            self.assertIn("files are for manual copy/paste only", readme_text)

    def test_write_latest_active_plan_manual_delivery_files_from_json_cli_preserves_json_pending_caveat_without_auto_flag(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_json = self._write_manual_delivery_input_json(
                base_dir,
                pending_caveat="manual json caveat",
                include_manual_delivery_checklist=False,
            )
            output_dir = base_dir / "bundle" / "json-only"

            result = subprocess.run(
                self._latest_manual_delivery_files_from_json_argv(input_json, output_dir),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stdout, f"{output_dir}\n")
            body_text = (output_dir / "body.txt").read_text(encoding="utf-8")
            package_text = (output_dir / "package.txt").read_text(encoding="utf-8")
            self.assertIn("manual json caveat", body_text)
            self.assertIn("manual json caveat", package_text)
            self.assertNotIn("diagnostic=no_intraperiod_evidence", package_text)

    def test_write_latest_active_plan_manual_delivery_files_from_json_cli_missing_csv_uses_no_evidence_caveat(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_json = self._write_manual_delivery_input_json(
                base_dir,
                pending_caveat="manual json caveat",
                include_manual_delivery_checklist=True,
            )
            output_dir = base_dir / "bundle" / "missing-csv"
            missing_csv = base_dir / "logs" / "csv" / "missing.csv"

            result = subprocess.run(
                self._latest_manual_delivery_files_from_json_argv(
                    input_json,
                    output_dir,
                    [
                        "--auto-pending-caveat-from-csv",
                        "--intraperiod-outcomes-path",
                        str(missing_csv),
                    ],
                ),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stdout, f"{output_dir}\n")
            package_text = (output_dir / "package.txt").read_text(encoding="utf-8")
            body_text = (output_dir / "body.txt").read_text(encoding="utf-8")
            self.assertIn("diagnostic=no_intraperiod_evidence", package_text)
            self.assertIn("diagnostic=no_intraperiod_evidence", body_text)

    def test_write_latest_active_plan_manual_delivery_files_from_json_cli_rejects_negative_recent_window(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_json = self._write_manual_delivery_input_json(base_dir, pending_caveat="manual json caveat")
            output_dir = base_dir / "bundle" / "negative-window"

            result = subprocess.run(
                self._latest_manual_delivery_files_from_json_argv(
                    input_json,
                    output_dir,
                    [
                        "--auto-pending-caveat-from-csv",
                        "--recent-row-window",
                        "-1",
                    ],
                ),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("must be a non-negative integer", result.stderr)

    def test_resolve_latest_manual_delivery_source_files_cli_help_includes_command_arguments(self) -> None:
        result = subprocess.run(
            self._manual_delivery_source_files_argv(["--help"]),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("resolve-latest-manual-delivery-source-files", result.stdout)
        self.assertIn("--intraperiod-outcomes-path", result.stdout)
        self.assertIn("--detail-report-path", result.stdout)
        self.assertIn("--format", result.stdout)

    def test_resolve_latest_manual_delivery_source_files_cli_prints_default_key_value_lines(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            code, stdout, stderr = self._run_manual_delivery_source_files_main_with_argv([], base_dir=base_dir)

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stderr, "")
            lines = stdout.splitlines()
            self.assertEqual(lines, [
                "intraperiod_outcomes_path=logs/csv/active_plan_candidate_intraperiod_outcomes.csv",
                "intraperiod_outcomes_exists=false",
                "detail_report_path=",
                "detail_report_exists=false",
                "safety=report-only_not_FORMAL_GO_no_automatic_order",
            ])
            self.assertTrue(stdout.endswith("\n"))

    def test_resolve_latest_manual_delivery_source_files_cli_reports_existing_paths_without_mutating_inputs(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            intraperiod_outcomes_path = base_dir / "logs" / "csv" / "active_plan_candidate_intraperiod_outcomes.csv"
            intraperiod_outcomes_path.parent.mkdir(parents=True, exist_ok=True)
            intraperiod_outcomes_path.write_text("timestamp_jst,outcome,first_exit_reason\n", encoding="utf-8")
            detail_report_path = base_dir / "運用資料" / "reports" / "analysis" / "manual-detail.md"
            detail_report_path.parent.mkdir(parents=True, exist_ok=True)
            detail_report_path.write_text("manual detail", encoding="utf-8")
            before_intraperiod = intraperiod_outcomes_path.read_text(encoding="utf-8")
            before_detail = detail_report_path.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_manual_delivery_source_files_main_with_argv(
                [
                    "--intraperiod-outcomes-path",
                    str(intraperiod_outcomes_path),
                    "--detail-report-path",
                    str(detail_report_path),
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stderr, "")
            self.assertEqual(
                stdout.splitlines(),
                [
                    f"intraperiod_outcomes_path={intraperiod_outcomes_path}",
                    "intraperiod_outcomes_exists=true",
                    f"detail_report_path={detail_report_path}",
                    "detail_report_exists=true",
                    "safety=report-only_not_FORMAL_GO_no_automatic_order",
                ],
            )
            self.assertEqual(intraperiod_outcomes_path.read_text(encoding="utf-8"), before_intraperiod)
            self.assertEqual(detail_report_path.read_text(encoding="utf-8"), before_detail)

    def test_resolve_latest_manual_delivery_source_files_cli_reports_missing_intraperiod_outcomes_path_without_failing(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            missing_intraperiod_outcomes_path = base_dir / "logs" / "csv" / "missing.csv"

            code, stdout, stderr = self._run_manual_delivery_source_files_main_with_argv(
                ["--intraperiod-outcomes-path", str(missing_intraperiod_outcomes_path)],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stderr, "")
            self.assertIn(f"intraperiod_outcomes_path={missing_intraperiod_outcomes_path}", stdout)
            self.assertIn("intraperiod_outcomes_exists=false", stdout)
            self.assertIn("detail_report_path=", stdout)
            self.assertIn("detail_report_exists=false", stdout)
            self.assertIn("safety=report-only_not_FORMAL_GO_no_automatic_order", stdout)

    def test_resolve_latest_manual_delivery_source_files_cli_reports_missing_latest_detail_report_without_failing(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            code, stdout, stderr = self._run_manual_delivery_source_files_main_with_argv([], base_dir=base_dir)

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stderr, "")
            self.assertIn("detail_report_path=", stdout)
            self.assertIn("detail_report_exists=false", stdout)
            self.assertIn("safety=report-only_not_FORMAL_GO_no_automatic_order", stdout)

    def test_write_latest_manual_delivery_local_inbox_cli_help_includes_command_arguments(self) -> None:
        result = subprocess.run(
            self._manual_delivery_local_inbox_argv(
                Path("/tmp/input.json"),
                Path("/tmp/bundle"),
                Path("/tmp/inbox.md"),
                ["--help"],
            ),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("write-latest-manual-delivery-local-inbox", result.stdout)
        self.assertIn("--input-json", result.stdout)
        self.assertIn("--bundle-dir", result.stdout)
        self.assertIn("--output-md", result.stdout)

    def test_write_latest_manual_delivery_local_inbox_cli_writes_markdown_and_stdout_path_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_json = base_dir / "input.json"
            bundle_dir = base_dir / "bundle"
            output_md = base_dir / "inbox.md"
            bundle_dir.mkdir(parents=True, exist_ok=True)
            input_json.write_text(
                json.dumps(
                    {
                        "generated_at_jst": "2026-06-11T00:00:00+09:00",
                        "symbol": "BTC_USDT",
                        "timeframe": "15m",
                        "data_source": "exchange-auto-public",
                        "data_freshness": "15m latest-window exchange-auto-public",
                        "detail_report_path": "運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260611.md",
                        "market_status_summary": "report-only manual preview; not FORMAL_GO; no automatic order; JSON seed",
                        "active_plan_label": "NO_ACTION_REVIEW_REQUIRED",
                        "side": "review_required",
                        "entry_mode": "review_required",
                        "entry_condition": "review latest report before any manual decision",
                        "tp_plan": "review_required",
                        "sl_or_invalidation": "review_required",
                        "timeout_or_wait_limit": "review_required",
                        "intraperiod_evidence_summary": "detail_report_exists=true; intraperiod_outcomes_exists=true; local source resolver seed",
                        "pending_caveat": "pending_coverage_caveat: total_outcome_rows=0; resolved_rows=0; pending_rows=0; pending_rate=n/a; recent_unresolved_windows=0; entry_not_touched_count=0; count_consistency=matches; diagnostic=no_intraperiod_evidence; action=do_not_use_as_trade_trigger; safety=report-only_not_FORMAL_GO_no_automatic_order",
                        "include_manual_delivery_checklist": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            before_json = input_json.read_text(encoding="utf-8")
            expected_bundle_texts = {
                "subject.txt": "subject text",
                "body.txt": "body report-only not FORMAL_GO no automatic order",
                "checklist.txt": "checklist human must decide manually",
                "package.txt": "package ACTIVE_* guidance only",
                "README.txt": "README no external notification integration",
            }
            for name, text in expected_bundle_texts.items():
                (bundle_dir / name).write_text(text, encoding="utf-8")
            before_bundle_texts = {name: (bundle_dir / name).read_text(encoding="utf-8") for name in expected_bundle_texts}

            code, stdout, stderr = self._run_manual_delivery_local_inbox_main_with_argv(
                [
                    "--input-json",
                    str(input_json),
                    "--bundle-dir",
                    str(bundle_dir),
                    "--output-md",
                    str(output_md),
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stderr, "")
            self.assertEqual(stdout, f"{output_md}\n")
            self.assertTrue(output_md.exists())
            self.assertEqual(input_json.read_text(encoding="utf-8"), before_json)
            for name, before_text in before_bundle_texts.items():
                self.assertEqual((bundle_dir / name).read_text(encoding="utf-8"), before_text)

            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("# Manual Delivery Local Inbox", markdown)
            self.assertIn("## Safety Status", markdown)
            self.assertIn("## Input JSON", markdown)
            self.assertIn("## Bundle Files", markdown)
            self.assertIn("## Human Review Checklist", markdown)
            self.assertIn("## Next Human Action", markdown)
            self.assertIn("report-only", markdown)
            self.assertIn("not FORMAL_GO", markdown)
            self.assertIn("no automatic order", markdown)
            self.assertIn("ACTIVE_* guidance only", markdown)
            self.assertIn("human must decide manually", markdown)
            self.assertIn("no external notification integration", markdown)
            self.assertIn("generated_at_jst=2026-06-11T00:00:00+09:00", markdown)
            self.assertIn("symbol=BTC_USDT", markdown)
            self.assertIn("timeframe=15m", markdown)
            self.assertIn("data_source=exchange-auto-public", markdown)
            self.assertIn("data_freshness=15m latest-window exchange-auto-public", markdown)
            self.assertIn(
                "detail_report_path=運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260611.md",
                markdown,
            )
            self.assertIn("active_plan_label=NO_ACTION_REVIEW_REQUIRED", markdown)
            self.assertIn("side=review_required", markdown)
            self.assertIn("entry_mode=review_required", markdown)
            self.assertIn("pending_caveat=pending_coverage_caveat:", markdown)
            self.assertIn("safety=report-only_not_FORMAL_GO_no_automatic_order", markdown)
            self.assertIn("subject.txt exists=true", markdown)
            self.assertIn("body.txt exists=true", markdown)
            self.assertIn("checklist.txt exists=true", markdown)
            self.assertIn("package.txt exists=true", markdown)
            self.assertIn("README.txt exists=true", markdown)
            self.assertIn("confirm JSON was reviewed by a human", markdown)
            self.assertIn("confirm body/package wording is report-only", markdown)
            self.assertIn("confirm not FORMAL_GO is visible", markdown)
            self.assertIn("confirm no automatic order is visible", markdown)
            self.assertIn("confirm pending caveat is visible", markdown)
            self.assertIn("confirm human decides manually", markdown)
            self.assertIn("confirm any send/post/share action is outside repo automation", markdown)
            self.assertIn("inspect the generated local files manually", markdown)
            self.assertIn("optionally copy/paste manually into an external app", markdown)
            self.assertIn("do not treat the inbox as trade approval", markdown)

    def test_write_latest_manual_delivery_local_inbox_cli_handles_missing_input_json_and_missing_bundle_files(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_json = base_dir / "missing.json"
            bundle_dir = base_dir / "bundle"
            output_md = base_dir / "missing-inbox.md"

            code, stdout, stderr = self._run_manual_delivery_local_inbox_main_with_argv(
                [
                    "--input-json",
                    str(input_json),
                    "--bundle-dir",
                    str(bundle_dir),
                    "--output-md",
                    str(output_md),
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stdout, f"{output_md}\n")
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("input_json_exists=false", markdown)
            self.assertIn("subject.txt exists=false", markdown)
            self.assertIn("body.txt exists=false", markdown)
            self.assertIn("checklist.txt exists=false", markdown)
            self.assertIn("package.txt exists=false", markdown)
            self.assertIn("README.txt exists=false", markdown)
            self.assertIn("report-only", markdown)
            self.assertIn("not FORMAL_GO", markdown)
            self.assertIn("no automatic order", markdown)
            self.assertIn("ACTIVE_* guidance only", markdown)
            self.assertIn("human must decide manually", markdown)
            self.assertIn("no external notification integration", markdown)

    def test_write_latest_manual_delivery_local_inbox_cli_rejects_invalid_input_json(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            input_json = base_dir / "invalid.json"
            input_json.write_text("{not json", encoding="utf-8")
            output_md = base_dir / "inbox.md"

            result = subprocess.run(
                self._manual_delivery_local_inbox_argv(input_json, base_dir / "bundle", output_md),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("invalid JSON in", result.stderr)
            self.assertFalse(output_md.exists())

    def test_write_latest_manual_delivery_input_json_cli_help_includes_command_arguments(self) -> None:
        result = subprocess.run(
            self._manual_delivery_input_json_argv(Path("/tmp/manual-delivery-input.json"), ["--help"]),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("write-latest-manual-delivery-input-json", result.stdout)
        self.assertIn("--output-json", result.stdout)
        self.assertIn("--intraperiod-outcomes-path", result.stdout)
        self.assertIn("--detail-report-path", result.stdout)
        self.assertIn("--recent-row-window", result.stdout)

    def test_write_latest_manual_delivery_input_json_cli_writes_default_seed_json(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_json = base_dir / "nested" / "manual-delivery-input.json"

            code, stdout, stderr = self._run_manual_delivery_input_json_main_with_argv(
                ["--output-json", str(output_json)],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stderr, "")
            self.assertEqual(stdout, f"{output_json}\n")
            self.assertTrue(output_json.exists())

            seed = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(
                set(seed),
                {
                    "generated_at_jst",
                    "symbol",
                    "timeframe",
                    "data_source",
                    "data_freshness",
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
                    "include_manual_delivery_checklist",
                },
            )
            self.assertTrue(seed["generated_at_jst"])
            self.assertEqual(seed["symbol"], "BTC_USDT")
            self.assertEqual(seed["timeframe"], "15m")
            self.assertEqual(seed["data_source"], "exchange-auto-public")
            self.assertEqual(seed["data_freshness"], "15m latest-window exchange-auto-public")
            self.assertEqual(seed["detail_report_path"], "")
            self.assertIn("report-only manual preview", seed["market_status_summary"])
            self.assertIn("not FORMAL_GO", seed["market_status_summary"])
            self.assertIn("no automatic order", seed["market_status_summary"])
            self.assertIn("JSON seed", seed["market_status_summary"])
            self.assertEqual(seed["active_plan_label"], "NO_ACTION_REVIEW_REQUIRED")
            self.assertEqual(seed["side"], "review_required")
            self.assertEqual(seed["entry_mode"], "review_required")
            self.assertEqual(seed["entry_condition"], "review latest report before any manual decision")
            self.assertEqual(seed["tp_plan"], "review_required")
            self.assertEqual(seed["sl_or_invalidation"], "review_required")
            self.assertEqual(seed["timeout_or_wait_limit"], "review_required")
            self.assertIn("detail_report_exists=false", seed["intraperiod_evidence_summary"])
            self.assertIn("intraperiod_outcomes_exists=false", seed["intraperiod_evidence_summary"])
            self.assertIn("local source resolver seed", seed["intraperiod_evidence_summary"])
            self.assertIn("safety=report-only_not_FORMAL_GO_no_automatic_order", seed["pending_caveat"])
            self.assertFalse(seed["include_manual_delivery_checklist"])

    def test_write_latest_manual_delivery_input_json_cli_derives_pending_caveat_from_csv(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_json = base_dir / "manual-delivery-input.json"
            csv_path = self._write_intraperiod_outcomes_csv(base_dir, self._pending_coverage_caveat_csv_rows())
            before_csv = csv_path.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_manual_delivery_input_json_main_with_argv(
                [
                    "--output-json",
                    str(output_json),
                    "--intraperiod-outcomes-path",
                    str(csv_path),
                    "--detail-report-path",
                    str(base_dir / "運用資料" / "reports" / "analysis" / "manual-detail.md"),
                    "--include-manual-delivery-checklist",
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stdout, f"{output_json}\n")
            seed = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertIn("pending_coverage_caveat:", seed["pending_caveat"])
            self.assertIn("diagnostic=coverage_caveat", seed["pending_caveat"])
            self.assertIn("report-only", seed["pending_caveat"])
            self.assertIn("safety=report-only_not_FORMAL_GO_no_automatic_order", seed["pending_caveat"])
            self.assertIn("detail_report_exists=false", seed["intraperiod_evidence_summary"])
            self.assertIn("intraperiod_outcomes_exists=true", seed["intraperiod_evidence_summary"])
            self.assertTrue(seed["include_manual_delivery_checklist"])
            self.assertEqual(csv_path.read_text(encoding="utf-8"), before_csv)

    def test_write_latest_manual_delivery_input_json_cli_missing_csv_uses_no_evidence_caveat(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_json = base_dir / "manual-delivery-input.json"
            missing_csv = base_dir / "logs" / "csv" / "missing.csv"

            code, stdout, stderr = self._run_manual_delivery_input_json_main_with_argv(
                [
                    "--output-json",
                    str(output_json),
                    "--intraperiod-outcomes-path",
                    str(missing_csv),
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stdout, f"{output_json}\n")
            seed = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertIn("diagnostic=no_intraperiod_evidence", seed["pending_caveat"])
            self.assertIn("detail_report_exists=false", seed["intraperiod_evidence_summary"])
            self.assertIn("intraperiod_outcomes_exists=false", seed["intraperiod_evidence_summary"])

    def test_write_latest_manual_delivery_input_json_cli_uses_explicit_detail_report_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_json = base_dir / "manual-delivery-input.json"
            detail_report_path = base_dir / "custom" / "manual-detail.md"
            detail_report_path.parent.mkdir(parents=True, exist_ok=True)
            detail_report_path.write_text("manual detail", encoding="utf-8")
            before_detail = detail_report_path.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_manual_delivery_input_json_main_with_argv(
                [
                    "--output-json",
                    str(output_json),
                    "--detail-report-path",
                    str(detail_report_path),
                    "--symbol",
                    "ETH_USDT",
                    "--timeframe",
                    "30m",
                    "--data-source",
                    "exchange-auto-public",
                    "--data-freshness",
                    "30m latest-window exchange-auto-public",
                    "--active-plan-label",
                    "ACTIVE_LIMIT_RETEST",
                    "--side",
                    "long",
                    "--entry-mode",
                    "limit_zone_mid",
                    "--entry-condition",
                    "entry zone must be touched before consideration",
                    "--tp-plan",
                    "TP1/TP2 from report context",
                    "--sl-or-invalidation",
                    "SL from report context",
                    "--timeout-or-wait-limit",
                    "timeout after configured window",
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stdout, f"{output_json}\n")
            seed = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(seed["detail_report_path"], str(detail_report_path))
            self.assertIn("detail_report_exists=true", seed["intraperiod_evidence_summary"])
            self.assertIn("intraperiod_outcomes_exists=false", seed["intraperiod_evidence_summary"])
            self.assertEqual(detail_report_path.read_text(encoding="utf-8"), before_detail)

    def test_write_latest_manual_delivery_input_json_cli_missing_latest_detail_report_uses_empty_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_json = base_dir / "manual-delivery-input.json"

            code, stdout, stderr = self._run_manual_delivery_input_json_main_with_argv(
                ["--output-json", str(output_json)],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(stdout, f"{output_json}\n")
            seed = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(seed["detail_report_path"], "")
            self.assertIn("detail_report_exists=false", seed["intraperiod_evidence_summary"])

    def test_write_latest_manual_delivery_input_json_cli_overrides_fields_and_rejects_negative_recent_window(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_json = base_dir / "manual-delivery-input.json"
            result = subprocess.run(
                self._manual_delivery_input_json_argv(
                    output_json,
                    [
                        "--recent-row-window",
                        "-1",
                    ],
                ),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("must be a non-negative integer", result.stderr)

            override_result = subprocess.run(
                self._manual_delivery_input_json_argv(
                    output_json,
                    [
                        "--symbol",
                        "ETH_USDT",
                        "--timeframe",
                        "30m",
                        "--data-source",
                        "custom-source",
                        "--data-freshness",
                        "custom freshness",
                        "--active-plan-label",
                        "ACTIVE_LIMIT_RETEST",
                        "--side",
                        "long",
                        "--entry-mode",
                        "limit_zone_mid",
                        "--entry-condition",
                        "entry zone must be touched before consideration",
                        "--tp-plan",
                        "TP1/TP2 custom",
                        "--sl-or-invalidation",
                        "SL custom",
                        "--timeout-or-wait-limit",
                        "timeout custom",
                    ],
                ),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(override_result.returncode, 0, msg=override_result.stderr)
            self.assertEqual(override_result.stdout, f"{output_json}\n")
            seed = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(seed["symbol"], "ETH_USDT")
            self.assertEqual(seed["timeframe"], "30m")
            self.assertEqual(seed["data_source"], "custom-source")
            self.assertEqual(seed["data_freshness"], "custom freshness")
            self.assertEqual(seed["active_plan_label"], "ACTIVE_LIMIT_RETEST")
            self.assertEqual(seed["side"], "long")
            self.assertEqual(seed["entry_mode"], "limit_zone_mid")
            self.assertEqual(seed["entry_condition"], "entry zone must be touched before consideration")
            self.assertEqual(seed["tp_plan"], "TP1/TP2 custom")
            self.assertEqual(seed["sl_or_invalidation"], "SL custom")
            self.assertEqual(seed["timeout_or_wait_limit"], "timeout custom")

    def test_write_latest_active_plan_manual_preview_cli_loads_fields_from_input_json(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            input_json = base_dir / "manual-preview-input.json"
            input_data = {
                "generated_at_jst": "2026-06-11T01:23:45+09:00",
                "symbol": "ETH_USDT",
                "timeframe": "30m",
                "data_source": "exchange-auto-public",
                "data_freshness": "30m latest-window exchange-auto-public",
                "market_status_summary": "report-only manual preview; not FORMAL_GO; no automatic order",
                "active_plan_label": "ACTIVE_LIMIT_RETEST",
                "side": "long",
                "entry_mode": "limit_zone_mid",
                "entry_condition": "entry zone must be touched before consideration",
                "tp_plan": "TP1/TP2 from JSON",
                "sl_or_invalidation": "SL from JSON",
                "timeout_or_wait_limit": "timeout after JSON window",
                "intraperiod_evidence_summary": "JSON provided evidence summary",
                "pending_caveat": "report-only manual preview; human must decide manually",
                "include_manual_delivery_checklist": True,
            }
            input_json.write_text(json.dumps(input_data, ensure_ascii=False, indent=2), encoding="utf-8")
            before_text = input_json.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_latest_manual_preview_main_with_argv(
                ["--input-json", str(input_json)],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(input_json.read_text(encoding="utf-8"), before_text)
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", stdout)
            self.assertIn("symbol: ETH_USDT", stdout)
            self.assertIn("timeframe: 30m", stdout)
            self.assertIn("data_source: exchange-auto-public", stdout)
            self.assertIn("data_freshness: 30m latest-window exchange-auto-public", stdout)
            self.assertIn("report-only", stdout)
            self.assertIn("not FORMAL_GO", stdout)
            self.assertIn("no automatic order", stdout)
            self.assertIn("ACTIVE_* is action guidance only", stdout)
            self.assertIn("human must decide manually", stdout)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertIn("Manual delivery checklist", stdout)

    def test_write_latest_active_plan_manual_preview_cli_overrides_input_json_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            self._write_intraperiod_report(base_dir, "20260611", "latest report")
            json_report = base_dir / "custom" / "json-detail.md"
            json_report.parent.mkdir(parents=True, exist_ok=True)
            json_report.write_text("json report", encoding="utf-8")
            cli_report = base_dir / "custom" / "cli-detail.md"
            cli_report.parent.mkdir(parents=True, exist_ok=True)
            cli_report.write_text("cli report", encoding="utf-8")
            input_json = base_dir / "manual-preview-input.json"
            input_json.write_text(
                json.dumps(
                    {
                        "generated_at_jst": "2026-06-11T01:23:45+09:00",
                        "symbol": "ETH_USDT",
                        "timeframe": "30m",
                        "data_source": "json-data-source",
                        "data_freshness": "json freshness",
                        "detail_report_path": json_report.relative_to(base_dir).as_posix(),
                        "market_status_summary": "json market status",
                        "active_plan_label": "JSON_ACTIVE_LIMIT_RETEST",
                        "side": "short",
                        "entry_mode": "json-entry-mode",
                        "entry_condition": "json entry condition",
                        "tp_plan": "json tp plan",
                        "sl_or_invalidation": "json sl",
                        "timeout_or_wait_limit": "json timeout",
                        "intraperiod_evidence_summary": "json evidence",
                        "pending_caveat": "json caveat",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            code, stdout, stderr = self._run_latest_manual_preview_main(
                [
                    "--input-json",
                    str(input_json),
                    "--generated-at-jst",
                    "2026-06-11T09:00:00+09:00",
                    "--symbol",
                    "BTC_USDT",
                    "--data-source",
                    "exchange-auto-public",
                    "--detail-report-path",
                    str(cli_report.relative_to(base_dir)),
                    "--market-status-summary",
                    "CLI market status",
                    "--active-plan-label",
                    "ACTIVE_LIMIT_RETEST",
                    "--side",
                    "long",
                    "--entry-mode",
                    "limit_zone_mid",
                    "--entry-condition",
                    "CLI entry condition",
                    "--tp-plan",
                    "CLI tp plan",
                    "--sl-or-invalidation",
                    "CLI sl",
                    "--timeout-or-wait-limit",
                    "CLI timeout",
                    "--intraperiod-evidence-summary",
                    "CLI evidence",
                    "--pending-caveat",
                    "CLI caveat",
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn("generated_at_jst: 2026-06-11T09:00:00+09:00", stdout)
            self.assertIn("symbol: BTC_USDT", stdout)
            self.assertIn("data_source: exchange-auto-public", stdout)
            self.assertIn(cli_report.relative_to(base_dir).as_posix(), stdout)
            self.assertNotIn(json_report.relative_to(base_dir).as_posix(), stdout)
            self.assertIn("CLI market status", stdout)
            self.assertIn("CLI entry condition", stdout)
            self.assertIn("CLI tp plan", stdout)
            self.assertIn("CLI sl", stdout)
            self.assertIn("CLI timeout", stdout)
            self.assertIn("CLI evidence", stdout)
            self.assertIn("CLI caveat", stdout)

    def test_write_latest_active_plan_manual_preview_cli_uses_json_detail_report_override(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            json_report = base_dir / "custom" / "json-detail.md"
            json_report.parent.mkdir(parents=True, exist_ok=True)
            json_report.write_text("json report", encoding="utf-8")
            input_json = base_dir / "manual-preview-input.json"
            input_json.write_text(
                json.dumps(
                    {
                        "generated_at_jst": "2026-06-11T01:23:45+09:00",
                        "symbol": "ETH_USDT",
                        "timeframe": "30m",
                        "data_source": "exchange-auto-public",
                        "data_freshness": "30m latest-window exchange-auto-public",
                        "detail_report_path": json_report.relative_to(base_dir).as_posix(),
                        "market_status_summary": "json market status",
                        "active_plan_label": "ACTIVE_LIMIT_RETEST",
                        "side": "long",
                        "entry_mode": "limit_zone_mid",
                        "entry_condition": "json entry condition",
                        "tp_plan": "json tp plan",
                        "sl_or_invalidation": "json sl",
                        "timeout_or_wait_limit": "json timeout",
                        "intraperiod_evidence_summary": "json evidence",
                        "pending_caveat": "json caveat",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            before_text = input_json.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_latest_manual_preview_main_with_argv(
                ["--input-json", str(input_json)],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertEqual(input_json.read_text(encoding="utf-8"), before_text)
            self.assertIn(json_report.relative_to(base_dir).as_posix(), stdout)
            self.assertNotIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertEqual(json_report.read_text(encoding="utf-8"), "json report")

    def test_write_latest_active_plan_manual_preview_cli_reports_missing_merged_fields(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            self._write_intraperiod_report(base_dir, "20260611", "latest report")
            input_json = base_dir / "manual-preview-input.json"
            input_json.write_text(
                json.dumps(
                    {
                        "market_status_summary": "json market status",
                        "active_plan_label": "ACTIVE_LIMIT_RETEST",
                        "side": "long",
                        "entry_mode": "limit_zone_mid",
                        "entry_condition": "json entry condition",
                        "tp_plan": "json tp plan",
                        "sl_or_invalidation": "json sl",
                        "timeout_or_wait_limit": "json timeout",
                        "intraperiod_evidence_summary": "json evidence",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            code, stdout, stderr = self._run_latest_manual_preview_main_with_argv(
                ["--input-json", str(input_json)],
                base_dir=base_dir,
            )

            self.assertNotEqual(code, 0)
            self.assertEqual(stdout, "")
            self.assertIn("pending_caveat is required after merging --input-json and CLI arguments", stderr)

    def test_write_latest_active_plan_manual_preview_cli_uses_latest_report_without_modifying_it(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            before_text = latest_report.read_text(encoding="utf-8")

            code, stdout, stderr = self._run_latest_manual_preview_main([], base_dir=base_dir)

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", stdout)
            self.assertIn("report-only", stdout)
            self.assertIn("not FORMAL_GO", stdout)
            self.assertIn("no automatic order", stdout)
            self.assertIn("ACTIVE_* is action guidance only", stdout)
            self.assertIn("human must decide manually", stdout)
            self.assertIn("BTC_USDT", stdout)
            self.assertIn("15m", stdout)
            self.assertIn("exchange-auto-public", stdout)
            self.assertIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertEqual(latest_report.read_text(encoding="utf-8"), before_text)

    def test_write_latest_active_plan_manual_preview_cli_supports_explicit_detail_report_override(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            latest_report = self._write_intraperiod_report(base_dir, "20260611", "latest report")
            override_report = base_dir / "custom" / "manual-detail.md"
            override_report.parent.mkdir(parents=True, exist_ok=True)
            override_report.write_text("override report", encoding="utf-8")

            code, stdout, stderr = self._run_latest_manual_preview_main(
                ["--detail-report-path", str(override_report)],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn(override_report.as_posix(), stdout)
            self.assertNotIn(latest_report.relative_to(base_dir).as_posix(), stdout)
            self.assertEqual(override_report.read_text(encoding="utf-8"), "override report")

    def test_write_latest_active_plan_manual_preview_cli_shows_default_values_when_omitted(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            self._write_intraperiod_report(base_dir, "20260611", "latest report")

            code, stdout, stderr = self._run_latest_manual_preview_main(
                [
                    "--market-status-summary",
                    "intraperiod evidence review only",
                    "--active-plan-label",
                    "ACTIVE_LIMIT_RETEST",
                    "--side",
                    "long",
                    "--entry-mode",
                    "limit_zone_mid",
                    "--entry-condition",
                    "entry zone must be touched before consideration",
                    "--tp-plan",
                    "TP1/TP2 from report context",
                    "--sl-or-invalidation",
                    "SL from report context",
                    "--timeout-or-wait-limit",
                    "timeout after configured window",
                    "--intraperiod-evidence-summary",
                    "latest intraperiod report linked",
                    "--pending-caveat",
                    "pending rows may reduce confidence",
                ],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn("symbol: BTC_USDT", stdout)
            self.assertIn("timeframe: 15m", stdout)
            self.assertIn("data_source: exchange-auto-public", stdout)
            self.assertIn("data_freshness: 15m latest-window exchange-auto-public", stdout)
            self.assertRegex(stdout, r"generated_at_jst: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
            self.assertIn("BTCFX Ver03-v2 manual trading support preview", stdout)

    def test_write_latest_active_plan_manual_preview_cli_supports_manual_delivery_checklist(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            self._write_intraperiod_report(base_dir, "20260611", "latest report")

            code, stdout, stderr = self._run_latest_manual_preview_main(
                ["--include-manual-delivery-checklist"],
                base_dir=base_dir,
            )

            self.assertEqual(code, 0, msg=stderr)
            self.assertIn("Manual delivery checklist", stdout)
            self.assertIn("report-only", stdout)
            self.assertIn("not FORMAL_GO", stdout)
            self.assertIn("no automatic order", stdout)
            self.assertIn("ACTIVE_* is action guidance only", stdout)
            self.assertIn("human must decide manually", stdout)
            self.assertEqual(stdout.count("Manual delivery checklist"), 1)

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
