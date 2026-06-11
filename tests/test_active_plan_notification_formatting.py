from __future__ import annotations

import contextlib
import io
import json
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
