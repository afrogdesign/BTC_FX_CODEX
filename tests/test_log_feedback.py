from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
import sys
import subprocess
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.log_feedback import (
    DEFAULT_REVIEW_FORM,
    DEFAULT_REVIEW_NOTE,
    REVIEW_NOTE_COLUMNS,
    SHADOW_HEADER,
    USER_REVIEW_HEADER,
    _ai_review_health_summary,
    _ai_post_review_chart_dir,
    _build_review_chart_svg_path,
    _build_improvement_candidates,
    _load_latest_ai_sync_stats,
    _merge_review_sources,
    _normalize_ai_post_review,
    _load_csv_rows,
    _load_review_note_rows,
    _load_review_state_rows,
    _normalize_ai_review_row,
    _review_state_path,
    _review_form_path,
    _render_review_form_html,
    backfill_ai_post_review_v2,
    build_current_setup_comparison_report,
    build_failed_breakout_down_reversal_report,
    build_feedback_report,
    build_market_map_effectiveness_report,
    build_market_map_readiness_report,
    build_observation_paper_orders,
    build_paper_entry_sl_wait_redesign_report,
    build_paper_opportunity_diagnostics_report,
    build_quality_guard_effectiveness_report,
    build_soft_risk_collateral_damage_report,
    build_paper_positions,
    build_phase1b_lite_paper_orders,
    build_operational_focus_report,
    build_phase1b_promotion_report,
    build_report_hub,
    build_relaxation_candidates_report,
    build_active_plan_candidate_intraperiod_outcomes,
    build_active_plan_candidate_intraperiod_outcomes_report,
    build_shadow_log,
    daily_sync,
    evaluate_trade_row,
    export_review_queue,
    import_reviews,
    main,
    refresh_standard_setup_comparison_reports,
    sync_ai_post_reviews,
    JST,
    _manual_delivery_current_app_dashboard_html,
    _manual_delivery_current_app_integrated_evidence_overview_data,
    _manual_delivery_current_app_integration_contract_data,
    _manual_delivery_current_app_operator_triage_summary_data,
    _write_manual_delivery_current_app_integration_contract_outputs,
    _manual_delivery_current_app_surface_validation_data,
)
from src.storage.csv_logger import OBSERVATION_PAPER_ORDER_HEADER, PAPER_POSITION_HEADER, PHASE1B_LITE_PAPER_ORDER_HEADER
from src.trade.active_plan_intraperiod import MIN_OUTCOME_COLUMNS


class LogFeedbackTest(unittest.TestCase):
    def test_build_report_hub_lists_latest_previous_and_warnings(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            reports_dir = base_dir / "運用資料" / "reports"
            analysis_dir = reports_dir / "analysis"
            archive_daily = reports_dir / "archive" / "daily" / "2026-05"
            archive_weekly = reports_dir / "archive" / "weekly"
            archive_analysis = reports_dir / "archive" / "analysis"
            legacy_v23 = reports_dir / "Ver02.3のレポート"
            legacy_old = reports_dir / "Ver02までのレポート"
            for path in [analysis_dir, archive_daily, archive_weekly, archive_analysis, legacy_v23, legacy_old]:
                path.mkdir(parents=True, exist_ok=True)

            (reports_dir / "feedback_daily_sync_20260526.md").write_text("# daily 26\n", encoding="utf-8")
            (archive_daily / "feedback_daily_sync_20260525.md").write_text("# daily 25\n", encoding="utf-8")
            (archive_weekly / "feedback_weekly_20260330.md").write_text("# weekly 30\n", encoding="utf-8")
            (analysis_dir / "market_map_effectiveness_20260526.md").write_text("# map 26\n", encoding="utf-8")
            (archive_analysis / "market_map_effectiveness_20260520.md").write_text("# map 20\n", encoding="utf-8")
            (analysis_dir / "market_map_readiness_20260514.md").write_text("# readiness 14\n", encoding="utf-8")
            (analysis_dir / "operational_focus_20260526.md").write_text("# focus 26\n", encoding="utf-8")
            (analysis_dir / "paper_opportunity_diagnostics_20260526.md").write_text("# paper 26\n", encoding="utf-8")
            (analysis_dir / "active_plan_candidate_intraperiod_outcomes_20260601.md").write_text("# intraperiod\n", encoding="utf-8")
            (analysis_dir / "quality_guard_effectiveness_20260601.md").write_text("# qg 0601\n", encoding="utf-8")
            (analysis_dir / "rr_to_confidence.md").write_text("# rr confidence\n", encoding="utf-8")
            (legacy_v23 / "README.md").write_text("# legacy v23\n", encoding="utf-8")
            (legacy_old / "README.md").write_text("# legacy old\n", encoding="utf-8")

            report = build_report_hub(base_dir=base_dir)

            self.assertIn("feedback_daily_sync_20260526.md", report)
            self.assertIn("feedback_daily_sync_20260525.md", report)
            self.assertIn("storage: `active`", report)
            self.assertIn("archive/daily/2026-05/feedback_daily_sync_20260525.md", report)
            self.assertIn("archive/weekly/feedback_weekly_20260330.md", report)
            self.assertIn("## Dormant / 補助診断", report)
            self.assertIn("market_map_readiness_20260514.md", report)
            self.assertIn("## Archived / 現行運用外", report)
            self.assertIn("rr_to_confidence.md", report)
            self.assertIn("active_plan_candidate_intraperiod_outcomes_20260601.md", report)
            self.assertIn("Active Plan 候補別 intraperiod 評価", report)
            self.assertIn("quality_guard_effectiveness_20260601.md", report)
            self.assertIn("missing: `paper_entry_sl_wait_redesign`", report)
            self.assertIn("legacy", report)
            self.assertNotIn("stale: `feedback_weekly`", report)
            self.assertNotIn("stale: `market_map_readiness`", report)
            self.assertTrue((reports_dir / "report_hub_latest.md").exists())

    def test_manual_delivery_current_app_dashboard_html_includes_manual_action_checklist(self) -> None:
        snapshot_data = {
            "entry_condition": "snapshot entry condition",
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
        }
        status_data = {
            "snapshot_status": "ready_for_human_review",
            "current_manual_delivery_ready": True,
            "allowed_next_action": "human_review_only",
            "display_mode": "dashboard",
            "primary_action": "human_review_only",
            "source_readiness": "ready",
            "actionability_label": "watch",
            "human_action": "manual review",
            "shadow_decision_enabled": True,
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
            "human_review_required": True,
            "trade_execution_allowed": False,
            "automatic_order_allowed": False,
            "external_notification_allowed": False,
            "paper_positions_integration": False,
            "active_plan_label": "active plan sample",
            "side": "long",
            "entry_mode": "market",
            "tp_plan": "TP plan sample",
            "sl_or_invalidation": "SL or invalidation sample",
            "timeout_or_wait_limit": "timeout sample",
            "intraperiod_evidence_summary": "evidence sample",
            "app_state_json": "app-state.json",
            "ready_check_json": "ready-check.json",
            "self_check_json": "self-check.json",
        }
        contract_data = _manual_delivery_current_app_integration_contract_data()

        html = _manual_delivery_current_app_dashboard_html(
            app_snapshot_json=Path("app-snapshot.json"),
            app_snapshot_status_json=Path("app-snapshot-status.json"),
            snapshot_data=snapshot_data,
            status_data=status_data,
            app_contract_data=contract_data,
        )

        self.assertIn("Readiness / Status", html)
        self.assertIn("Active Plan Summary", html)
        self.assertIn("Manual Action Checklist", html)
        self.assertIn("Source Files / Generated At", html)
        self.assertIn("Safety Boundary", html)
        self.assertIn("Entry mode", html)
        self.assertIn("Entry condition", html)
        self.assertIn("TP / SL", html)
        self.assertIn("Invalidation / wait", html)
        self.assertIn("Timeout / validity", html)
        self.assertIn("Safety", html)
        self.assertIn("market", html)
        self.assertIn("snapshot entry condition", html)
        self.assertIn("TP plan sample", html)
        self.assertIn("SL or invalidation sample", html)
        self.assertIn("timeout sample", html)
        self.assertIn("watch", html)
        self.assertIn("manual review", html)
        self.assertIn("human_review_only", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertIn("Operator Triage Summary", html)
        self.assertIn("Integrated Evidence Overview", html)
        self.assertIn("Summary status", html)
        self.assertIn("evidence_keys", html)
        self.assertIn("missing_evidence_keys", html)
        self.assertIn("not_ready_evidence_keys", html)
        self.assertIn("execution_required_keys", html)
        self.assertIn("operator_status_diagnostic", html)
        self.assertIn("safe_config_schema_audit", html)
        self.assertIn("intraperiod_review_stdout_json", html)
        self.assertIn("operator_triage_summary", html)
        self.assertIn("manual_action_checklist_surface", html)
        self.assertIn("present=true / ready=true", html)
        self.assertIn("present=true / ready_or_valid=true / execution_required=false", html)
        self.assertIn(
            "intraperiod_review_stdout_json, manual_action_checklist_surface, operator_status_diagnostic, operator_triage_summary, safe_config_schema_audit",
            html,
        )
        self.assertIn("<th>missing_evidence_keys</th><td>none</td>", html)
        self.assertIn("<th>not_ready_evidence_keys</th><td>none</td>", html)
        self.assertIn("<th>execution_required_keys</th><td>none</td>", html)
        self.assertIn("derived from existing app contract data only", html)
        self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", html)
        self.assertIn("Operator Status Diagnostics", html)
        self.assertIn("./.venv312/bin/python tools/operator_status.py", html)
        self.assertIn("./.venv312/bin/python tools/operator_status.py --check", html)
        self.assertIn("0 ok, 2 waiting_for_html_cycle, 3 startup_status_unavailable", html)
        self.assertIn("json_required", html)
        self.assertIn("report/local diagnostics only", html)
        self.assertIn("no FORMAL_GO", html)
        self.assertIn("no automatic order", html)
        self.assertIn("no exchange fetch", html)
        self.assertIn("no private/account/order endpoints", html)
        self.assertIn("no secrets", html)
        self.assertIn("app surface does not execute this command", html)
        self.assertIn("Safe Config Schema Audit", html)
        self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py", html)
        self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json", html)
        self.assertIn("safe_config_schema_audit.v1", html)
        self.assertIn("contract_only", html)
        self.assertIn("command_executed_by_app", html)
        self.assertIn("reads_env_values", html)
        self.assertIn("reads_dotenv_values", html)
        self.assertIn("calls_private_endpoints", html)
        self.assertIn("calls_order_endpoints", html)
        self.assertIn("live_trading_allowed", html)
        self.assertIn("secret_values_exposed", html)
        self.assertIn("static config schema audit only / no load_config / no .env / no os.environ / no secrets / no private/account/order endpoints / no live trading", html)
        self.assertIn("This app surface does not execute", html)
        self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py", html)
        self.assertNotIn("smtp", html.lower())
        self.assertNotIn("Gmail", html)
        self.assertNotIn("send_email", html)
        self.assertNotIn("private/order", html)
        self.assertNotIn("automatic_order_allowed=true", html)
        self.assertNotIn("execution_required=true", html)

    def test_manual_delivery_current_app_dashboard_html_shows_integrated_evidence_missing_lists(self) -> None:
        snapshot_data = {
            "entry_condition": "snapshot entry condition",
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
        }
        status_data = {
            "snapshot_status": "ready_for_human_review",
            "current_manual_delivery_ready": True,
            "allowed_next_action": "human_review_only",
            "display_mode": "dashboard",
            "primary_action": "human_review_only",
            "source_readiness": "ready",
            "actionability_label": "watch",
            "human_action": "manual review",
            "shadow_decision_enabled": True,
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
            "human_review_required": True,
            "trade_execution_allowed": False,
            "automatic_order_allowed": False,
            "external_notification_allowed": False,
            "paper_positions_integration": False,
            "active_plan_label": "active plan sample",
            "side": "long",
            "entry_mode": "market",
            "tp_plan": "TP plan sample",
            "sl_or_invalidation": "SL or invalidation sample",
            "timeout_or_wait_limit": "timeout sample",
            "intraperiod_evidence_summary": "evidence sample",
            "app_state_json": "app-state.json",
            "ready_check_json": "ready-check.json",
            "self_check_json": "self-check.json",
        }
        contract_data = _manual_delivery_current_app_integration_contract_data()
        contract_data.pop("safe_config_schema_audit")

        html = _manual_delivery_current_app_dashboard_html(
            app_snapshot_json=Path("app-snapshot.json"),
            app_snapshot_status_json=Path("app-snapshot-status.json"),
            snapshot_data=snapshot_data,
            status_data=status_data,
            app_contract_data=contract_data,
        )

        self.assertIn("Integrated Evidence Overview", html)
        self.assertIn("evidence_keys", html)
        self.assertIn("missing_evidence_keys", html)
        self.assertIn("not_ready_evidence_keys", html)
        self.assertIn("execution_required_keys", html)
        self.assertIn("intraperiod_review_stdout_json, manual_action_checklist_surface, operator_status_diagnostic, operator_triage_summary, safe_config_schema_audit", html)
        self.assertIn("<th>missing_evidence_keys</th><td>safe_config_schema_audit</td>", html)
        self.assertIn(
            "<th>not_ready_evidence_keys</th><td>operator_triage_summary, safe_config_schema_audit</td>",
            html,
        )
        self.assertIn("<th>execution_required_keys</th><td>none</td>", html)
        self.assertNotIn("execution_required=true", html)

    def test_manual_delivery_current_app_operator_triage_summary_data_handles_missing_evidence(self) -> None:
        status_data = {
            "snapshot_status": "ready_for_human_review",
            "app_snapshot_status": "valid_ready_for_human_review",
            "readiness_status": "ready_for_human_review",
            "allowed_next_action": "human_review_only",
            "human_review_required": True,
            "trade_execution_allowed": False,
            "automatic_order_allowed": False,
            "external_notification_allowed": False,
            "paper_positions_integration": False,
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
            "current_manual_delivery_ready": True,
        }
        contract_data = _manual_delivery_current_app_integration_contract_data()
        contract_data.pop("safe_config_schema_audit")

        triage_summary = _manual_delivery_current_app_operator_triage_summary_data(
            app_contract_data=contract_data,
            status_data=status_data,
        )

        self.assertEqual(triage_summary["schema_version"], "manual_delivery_app_operator_triage_summary.v1")
        self.assertEqual(triage_summary["summary_status"], "partial_or_missing")
        self.assertFalse(triage_summary["all_evidence_present"])
        self.assertFalse(triage_summary["all_evidence_ready"])
        self.assertTrue(triage_summary["evidence"]["operator_status_diagnostic"]["present"])
        self.assertTrue(triage_summary["evidence"]["operator_status_diagnostic"]["ready"])
        self.assertFalse(triage_summary["evidence"]["safe_config_schema_audit"]["present"])
        self.assertFalse(triage_summary["evidence"]["safe_config_schema_audit"]["ready"])
        self.assertTrue(triage_summary["evidence"]["intraperiod_review_stdout_json"]["present"])
        self.assertTrue(triage_summary["evidence"]["intraperiod_review_stdout_json"]["ready"])
        self.assertTrue(triage_summary["evidence"]["manual_action_checklist_surface"]["present"])
        self.assertTrue(triage_summary["evidence"]["manual_action_checklist_surface"]["ready"])
        self.assertEqual(
            triage_summary["safety_boundary"],
            "report-only / not FORMAL_GO / no automatic order / human decides manually",
        )

    def test_manual_delivery_current_app_integrated_evidence_overview_data_handles_missing_evidence(self) -> None:
        status_data = {
            "snapshot_status": "ready_for_human_review",
            "app_snapshot_status": "valid_ready_for_human_review",
            "readiness_status": "ready_for_human_review",
            "allowed_next_action": "human_review_only",
            "human_review_required": True,
            "trade_execution_allowed": False,
            "automatic_order_allowed": False,
            "external_notification_allowed": False,
            "paper_positions_integration": False,
            "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
            "current_manual_delivery_ready": True,
        }
        contract_data = _manual_delivery_current_app_integration_contract_data()
        contract_data.pop("safe_config_schema_audit")

        integrated_evidence_overview = _manual_delivery_current_app_integrated_evidence_overview_data(
            app_contract_data=contract_data,
            status_data=status_data,
        )

        self.assertEqual(
            integrated_evidence_overview["schema_version"],
            "manual_delivery_app_integrated_evidence_overview.v1",
        )
        self.assertEqual(integrated_evidence_overview["summary_status"], "partial_or_missing")
        self.assertFalse(integrated_evidence_overview["all_evidence_present"])
        self.assertFalse(integrated_evidence_overview["all_evidence_ready"])
        self.assertTrue(integrated_evidence_overview["report_only"])
        self.assertFalse(integrated_evidence_overview["formal_go"])
        self.assertFalse(integrated_evidence_overview["automatic_order_allowed"])
        self.assertTrue(integrated_evidence_overview["human_decides_manually"])
        self.assertEqual(
            integrated_evidence_overview["safety_boundary"],
            "report-only / not FORMAL_GO / no automatic order / human decides manually",
        )
        self.assertTrue(integrated_evidence_overview["evidence"]["intraperiod_review_stdout_json"]["present"])
        self.assertTrue(integrated_evidence_overview["evidence"]["intraperiod_review_stdout_json"]["ready_or_valid"])
        self.assertFalse(integrated_evidence_overview["evidence"]["intraperiod_review_stdout_json"]["execution_required"])
        self.assertTrue(integrated_evidence_overview["evidence"]["operator_status_diagnostic"]["present"])
        self.assertTrue(integrated_evidence_overview["evidence"]["operator_status_diagnostic"]["ready_or_valid"])
        self.assertFalse(integrated_evidence_overview["evidence"]["operator_status_diagnostic"]["execution_required"])
        self.assertFalse(integrated_evidence_overview["evidence"]["safe_config_schema_audit"]["present"])
        self.assertFalse(integrated_evidence_overview["evidence"]["safe_config_schema_audit"]["ready_or_valid"])
        self.assertFalse(integrated_evidence_overview["evidence"]["safe_config_schema_audit"]["execution_required"])
        self.assertTrue(integrated_evidence_overview["evidence"]["operator_triage_summary"]["present"])
        self.assertFalse(integrated_evidence_overview["evidence"]["operator_triage_summary"]["ready_or_valid"])
        self.assertFalse(integrated_evidence_overview["evidence"]["operator_triage_summary"]["execution_required"])
        self.assertTrue(integrated_evidence_overview["evidence"]["manual_action_checklist_surface"]["present"])
        self.assertTrue(integrated_evidence_overview["evidence"]["manual_action_checklist_surface"]["ready_or_valid"])
        self.assertFalse(integrated_evidence_overview["evidence"]["manual_action_checklist_surface"]["execution_required"])
        self.assertEqual(
            integrated_evidence_overview["evidence_keys"],
            sorted(
                [
                    "intraperiod_review_stdout_json",
                    "manual_action_checklist_surface",
                    "operator_status_diagnostic",
                    "operator_triage_summary",
                    "safe_config_schema_audit",
                ]
            ),
        )
        self.assertEqual(integrated_evidence_overview["missing_evidence_keys"], ["safe_config_schema_audit"])
        self.assertEqual(
            integrated_evidence_overview["not_ready_evidence_keys"],
            ["operator_triage_summary", "safe_config_schema_audit"],
        )
        self.assertEqual(integrated_evidence_overview["execution_required_keys"], [])
        self.assertEqual(integrated_evidence_overview["note"], "derived from existing app contract/status data only")

    def test_manual_delivery_current_app_integration_contract_includes_intraperiod_review_stdout_json(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            output_md = base_dir / "app-contract.md"
            output_json = base_dir / "app-contract.json"

            markdown, contract_data = _write_manual_delivery_current_app_integration_contract_outputs(
                output_md=output_md,
                output_json=output_json,
            )

            self.assertTrue(output_md.exists())
            self.assertTrue(output_json.exists())
            self.assertIn("build-active-plan-intraperiod-review --stdout-json", markdown)
            self.assertIn("active_plan_intraperiod_review.v1", markdown)
            self.assertIn("no exchange fetch", markdown)
            self.assertIn("no daily-sync wiring", markdown)
            self.assertIn("no secret/API key reading", markdown)
            self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", markdown)
            self.assertIn("./.venv312/bin/python tools/operator_status.py", markdown)
            self.assertIn("./.venv312/bin/python tools/operator_status.py --check", markdown)
            self.assertIn("json_required: false", markdown)
            self.assertIn("0=ok, 2=waiting_for_html_cycle, 3=startup_status_unavailable", markdown)
            self.assertIn("report/local diagnostics only", markdown)
            self.assertIn("no exchange fetch", markdown)
            self.assertIn("no private/account/order endpoints", markdown)
            self.assertIn("no secrets", markdown)
            self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py", markdown)
            self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json", markdown)
            self.assertIn("safe_config_schema_audit.v1", markdown)
            self.assertIn("static config schema audit only", markdown)
            self.assertIn("no load_config", markdown)
            self.assertIn("no .env", markdown)
            self.assertIn("no os.environ", markdown)

            contract_text = output_json.read_text(encoding="utf-8")
            parsed = json.loads(contract_text)
            self.assertEqual(contract_data, parsed)
            self.assertIn("build-active-plan-intraperiod-review --stdout-json", contract_text)
            self.assertIn("active_plan_intraperiod_review.v1", contract_text)
            self.assertIn("report_only", contract_text)
            self.assertIn("formal_go", contract_text)
            self.assertIn("automatic_order_allowed", contract_text)
            self.assertIn("exchange_fetch_allowed", contract_text)
            self.assertIn("daily_sync_wiring", contract_text)
            self.assertIn("secret_reading_allowed", contract_text)
            self.assertIn("human_decides_manually", contract_text)
            self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", contract_text)
            self.assertIn("operator_status_diagnostic", contract_text)
            self.assertIn("safe_config_schema_audit", contract_text)
            self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py", contract_text)
            self.assertIn("./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json", contract_text)
            self.assertIn("safe_config_schema_audit.v1", contract_text)
            self.assertIn("contract_only", contract_text)
            self.assertIn("command_executed_by_app", contract_text)
            self.assertIn("reads_env_values", contract_text)
            self.assertIn("reads_dotenv_values", contract_text)
            self.assertIn("calls_private_endpoints", contract_text)
            self.assertIn("calls_order_endpoints", contract_text)
            self.assertIn("live_trading_allowed", contract_text)
            self.assertIn("secret_values_exposed", contract_text)
            self.assertIn("./.venv312/bin/python tools/operator_status.py", contract_text)
            self.assertIn("./.venv312/bin/python tools/operator_status.py --check", contract_text)
            self.assertIn("json_required", contract_text)
            self.assertIn("check_exit_codes", contract_text)
            self.assertIn("report/local diagnostics only", contract_text)
            self.assertIn("no exchange fetch", contract_text)
            self.assertIn("no private/account/order endpoints", contract_text)
            self.assertIn("no secrets", contract_text)
            self.assertIn("static config schema audit only", contract_text)
            self.assertIn("no load_config", contract_text)
            self.assertIn("no .env", contract_text)
            self.assertIn("no os.environ", contract_text)

            intraperiod = parsed["intraperiod_review_stdout_json"]
            self.assertEqual(intraperiod["entrypoint_command"], "build-active-plan-intraperiod-review --stdout-json")
            self.assertEqual(intraperiod["schema_version"], "active_plan_intraperiod_review.v1")
            self.assertEqual(
                intraperiod["safety_boundary"],
                "report-only / not FORMAL_GO / no automatic order / human decides manually",
            )
            self.assertIn("local/report-only", intraperiod["allowed_behavior"])
            self.assertIn("no exchange fetch", intraperiod["allowed_behavior"])
            safe_config = parsed["safe_config_schema_audit"]
            self.assertEqual(safe_config["command"], "./.venv312/bin/python tools/safe_config_schema_audit.py")
            self.assertEqual(
                safe_config["stdout_json_command"],
                "./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json",
            )
            self.assertEqual(safe_config["schema_version"], "safe_config_schema_audit.v1")
            self.assertTrue(safe_config["contract_only"])
            self.assertFalse(safe_config["command_executed_by_app"])
            self.assertFalse(safe_config["reads_env_values"])
            self.assertFalse(safe_config["reads_dotenv_values"])
            self.assertFalse(safe_config["calls_private_endpoints"])
            self.assertFalse(safe_config["calls_order_endpoints"])
            self.assertFalse(safe_config["live_trading_allowed"])
            self.assertFalse(safe_config["secret_values_exposed"])
            self.assertIn("static config schema audit only", safe_config["safety_boundary"])
            self.assertIn("no load_config", safe_config["safety_boundary"])
            self.assertIn("no .env", safe_config["safety_boundary"])
            self.assertIn("no os.environ", safe_config["safety_boundary"])
            self.assertIn("no daily-sync wiring", intraperiod["allowed_behavior"])
            self.assertIn("no secret/API key reading", intraperiod["allowed_behavior"])
            self.assertIn("schema_version", intraperiod["output_fields"])
            self.assertIn("command", intraperiod["output_fields"])
            self.assertIn("candidates_csv", intraperiod["output_fields"])
            self.assertIn("ohlcv_csv", intraperiod["output_fields"])
            self.assertIn("outcomes_csv", intraperiod["output_fields"])
            self.assertIn("report_md", intraperiod["output_fields"])
            self.assertIn("row_count", intraperiod["output_fields"])
            self.assertIn("report_only", intraperiod["output_fields"])
            self.assertIn("formal_go", intraperiod["output_fields"])
            self.assertIn("automatic_order_allowed", intraperiod["output_fields"])
            self.assertIn("exchange_fetch_allowed", intraperiod["output_fields"])
            self.assertIn("daily_sync_wiring", intraperiod["output_fields"])
            self.assertIn("secret_reading_allowed", intraperiod["output_fields"])
            self.assertIn("human_decides_manually", intraperiod["output_fields"])
            self.assertIn("safety_boundary", intraperiod["output_fields"])
            self.assertTrue(intraperiod["required_safety_flags"]["report_only"])
            self.assertFalse(intraperiod["required_safety_flags"]["formal_go"])
            self.assertFalse(intraperiod["required_safety_flags"]["automatic_order_allowed"])
            self.assertFalse(intraperiod["required_safety_flags"]["exchange_fetch_allowed"])
            self.assertFalse(intraperiod["required_safety_flags"]["daily_sync_wiring"])
            self.assertFalse(intraperiod["required_safety_flags"]["secret_reading_allowed"])
            self.assertTrue(intraperiod["required_safety_flags"]["human_decides_manually"])
            operator_status_diag = parsed["operator_status_diagnostic"]
            self.assertEqual(operator_status_diag["wrapper_command"], "./.venv312/bin/python tools/operator_status.py")
            self.assertEqual(operator_status_diag["wrapper_check_command"], "./.venv312/bin/python tools/operator_status.py --check")
            self.assertFalse(operator_status_diag["json_required"])
            self.assertEqual(
                operator_status_diag["check_exit_codes"],
                {
                    "ok": 0,
                    "waiting_for_html_cycle": 2,
                    "startup_status_unavailable": 3,
                },
            )
            self.assertEqual(
                operator_status_diag["safety_boundary"],
                "report/local diagnostics only / no FORMAL_GO / no automatic order / no exchange fetch / no private/account/order endpoints / no secrets",
            )
            self.assertIn("read-only", operator_status_diag["allowed_behavior"])
            self.assertIn("local diagnostics", operator_status_diag["allowed_behavior"])
            self.assertIn("no notifications", operator_status_diag["allowed_behavior"])
            self.assertIn("no runtime restart", operator_status_diag["allowed_behavior"])
            self.assertIn("no exchange fetch", operator_status_diag["allowed_behavior"])
            self.assertIn("no secrets", operator_status_diag["allowed_behavior"])
            self.assertIn("no private/account/order endpoints", operator_status_diag["allowed_behavior"])
            self.assertIn("no FORMAL_GO", operator_status_diag["allowed_behavior"])
            self.assertEqual(operator_status_diag["json_required"], False)
            self.assertEqual(
                operator_status_diag["check_exit_codes"],
                {
                    "ok": 0,
                    "waiting_for_html_cycle": 2,
                    "startup_status_unavailable": 3,
                },
            )
            self.assertIn("report/local diagnostics only", operator_status_diag["safety_boundary"])

    def test_manual_delivery_current_app_surface_validation_data_requires_intraperiod_review_stdout_json_contract(self) -> None:
        def write_surface_files(surface_dir: Path, contract_data: dict[str, Any]) -> None:
            surface_dir.mkdir(parents=True, exist_ok=True)
            (surface_dir / "index.html").write_text(
                "\n".join(
                    [
                        "app-dashboard.html",
                        "app-ready.json",
                        "app-contract.json",
                        "app-snapshot.json",
                        "app-snapshot-status.json",
                        "app-surface-manifest.json",
                        "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    ]
                ),
                encoding="utf-8",
            )
            (surface_dir / "app-dashboard.html").write_text(
                "\n".join(
                    [
                        "<section>Readiness / Status</section>",
                        "<section>Active Plan Summary</section>",
                        "<section>Manual Action Checklist</section>",
                        "<section>Operator Triage Summary</section>",
                        "<section>Integrated Evidence Overview</section>",
                        "<section>Entry mode</section>",
                        "<section>Entry condition</section>",
                        "<section>TP / SL</section>",
                        "<section>Invalidation / wait</section>",
                        "<section>Timeout / validity</section>",
                        "<section>Safety</section>",
                        "<section>Summary status</section>",
                        "<section>operator_status_diagnostic</section>",
                        "<section>safe_config_schema_audit</section>",
                        "<section>intraperiod_review_stdout_json</section>",
                        "<section>operator_triage_summary</section>",
                        "<section>manual_action_checklist_surface</section>",
                        "<section>present=true / ready_or_valid=true / execution_required=false</section>",
                        "<section>derived from existing app contract data only</section>",
                        "<section>Source Files / Generated At</section>",
                        "<section>Safety Boundary</section>",
                        "<section>report-only / not FORMAL_GO / no automatic order / human decides manually</section>",
                    ]
                ),
                encoding="utf-8",
            )
            (surface_dir / "app-ready.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_ready_check.v1",
                        "current_manual_delivery_app_ready": True,
                        "readiness_status": "ready_for_human_review",
                        "allowed_next_action": "human_review_only",
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-contract.json").write_text(
                json.dumps(
                    contract_data,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-snapshot.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_snapshot.v1",
                        "snapshot_status": "ready_for_human_review",
                        "current_manual_delivery_ready": True,
                        "allowed_next_action": "human_review_only",
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-snapshot-status.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_snapshot_status.v1",
                        "app_snapshot_status": "valid_ready_for_human_review",
                        "snapshot_status": "ready_for_human_review",
                        "current_manual_delivery_ready": True,
                        "allowed_next_action": "human_review_only",
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-surface-manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_surface_manifest.v1",
                        "surface_status": "ready_for_human_review",
                        "entrypoint": "index.html",
                        "files": {
                            "index_html": "index.html",
                            "app_dashboard_html": "app-dashboard.html",
                            "app_ready_json": "app-ready.json",
                            "app_contract_json": "app-contract.json",
                            "app_snapshot_json": "app-snapshot.json",
                            "app_snapshot_status_json": "app-snapshot-status.json",
                            "app_surface_manifest_json": "app-surface-manifest.json",
                        },
                        "commands": {
                            "surface_ready_gate": "refresh-and-check-current-manual-delivery-app-surface --stdout-json",
                            "surface_validate": "check-current-manual-delivery-app-surface --stdout-json",
                            "surface_export": "export-current-manual-delivery-app-surface",
                        },
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

        with TemporaryDirectory() as tmpdir:
            surface_dir = Path(tmpdir)

            write_surface_files(surface_dir, _manual_delivery_current_app_integration_contract_data())
            validation_data = _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertEqual(validation_data["surface_status"], "valid_ready_for_human_review")
            self.assertTrue(validation_data["current_manual_delivery_app_ready"])
            self.assertFalse(validation_data["automatic_order_allowed"])
            self.assertTrue(validation_data["operator_status_diagnostic_contract"])
            self.assertEqual(validation_data["operator_status_wrapper_command"], "./.venv312/bin/python tools/operator_status.py")
            self.assertEqual(validation_data["operator_status_check_command"], "./.venv312/bin/python tools/operator_status.py --check")
            self.assertFalse(validation_data["operator_status_json_required"])
            self.assertEqual(
                validation_data["operator_status_check_exit_codes"],
                {
                    "ok": 0,
                    "waiting_for_html_cycle": 2,
                    "startup_status_unavailable": 3,
                },
            )
            self.assertTrue(validation_data["operator_status_contract_only"])
            self.assertFalse(validation_data["operator_status_command_executed"])
            self.assertIn("report/local diagnostics only", validation_data["operator_status_safety_boundary"])
            self.assertIn("no FORMAL_GO", validation_data["operator_status_safety_boundary"])
            self.assertIn("no automatic order", validation_data["operator_status_safety_boundary"])
            self.assertIn("no exchange fetch", validation_data["operator_status_safety_boundary"])
            self.assertIn("no private/account/order endpoints", validation_data["operator_status_safety_boundary"])
            self.assertIn("no secrets", validation_data["operator_status_safety_boundary"])
            self.assertTrue(validation_data["safe_config_schema_audit_contract"])
            self.assertEqual(
                validation_data["safe_config_schema_audit_command"],
                "./.venv312/bin/python tools/safe_config_schema_audit.py",
            )
            self.assertEqual(
                validation_data["safe_config_schema_audit_stdout_json_command"],
                "./.venv312/bin/python tools/safe_config_schema_audit.py --stdout-json",
            )
            self.assertEqual(validation_data["safe_config_schema_audit_schema_version"], "safe_config_schema_audit.v1")
            self.assertTrue(validation_data["safe_config_schema_audit_contract_only"])
            self.assertFalse(validation_data["safe_config_schema_audit_command_executed_by_app"])
            self.assertFalse(validation_data["safe_config_schema_audit_reads_env_values"])
            self.assertFalse(validation_data["safe_config_schema_audit_reads_dotenv_values"])
            self.assertFalse(validation_data["safe_config_schema_audit_calls_private_endpoints"])
            self.assertFalse(validation_data["safe_config_schema_audit_calls_order_endpoints"])
            self.assertFalse(validation_data["safe_config_schema_audit_live_trading_allowed"])
            self.assertFalse(validation_data["safe_config_schema_audit_secret_values_exposed"])
            self.assertIn("static config schema audit only", validation_data["safe_config_schema_audit_safety_boundary"])
            self.assertIn("no load_config", validation_data["safe_config_schema_audit_safety_boundary"])
            self.assertIn("no .env", validation_data["safe_config_schema_audit_safety_boundary"])
            self.assertIn("no os.environ", validation_data["safe_config_schema_audit_safety_boundary"])
            self.assertIn("no secrets", validation_data["safe_config_schema_audit_safety_boundary"])
            self.assertIn(
                "no private/account/order endpoints",
                validation_data["safe_config_schema_audit_safety_boundary"],
            )
            self.assertIn("no live trading", validation_data["safe_config_schema_audit_safety_boundary"])

            operator_triage_summary = validation_data["operator_triage_summary"]
            self.assertEqual(operator_triage_summary["schema_version"], "manual_delivery_app_operator_triage_summary.v1")
            self.assertEqual(operator_triage_summary["summary_status"], "ready_for_human_review")
            self.assertTrue(operator_triage_summary["all_evidence_present"])
            self.assertTrue(operator_triage_summary["all_evidence_ready"])
            self.assertTrue(operator_triage_summary["report_only"])
            self.assertFalse(operator_triage_summary["formal_go"])
            self.assertFalse(operator_triage_summary["automatic_order_allowed"])
            self.assertTrue(operator_triage_summary["human_decides_manually"])
            self.assertEqual(
                operator_triage_summary["safety_boundary"],
                "report-only / not FORMAL_GO / no automatic order / human decides manually",
            )
            self.assertTrue(operator_triage_summary["evidence"]["operator_status_diagnostic"]["present"])
            self.assertTrue(operator_triage_summary["evidence"]["operator_status_diagnostic"]["ready"])
            self.assertTrue(operator_triage_summary["evidence"]["safe_config_schema_audit"]["present"])
            self.assertTrue(operator_triage_summary["evidence"]["safe_config_schema_audit"]["ready"])
            self.assertTrue(operator_triage_summary["evidence"]["intraperiod_review_stdout_json"]["present"])
            self.assertTrue(operator_triage_summary["evidence"]["intraperiod_review_stdout_json"]["ready"])
            self.assertTrue(operator_triage_summary["evidence"]["manual_action_checklist_surface"]["present"])
            self.assertTrue(operator_triage_summary["evidence"]["manual_action_checklist_surface"]["ready"])
            self.assertEqual(operator_triage_summary["note"], "derived from existing app contract data only")

            integrated_evidence_overview = validation_data["integrated_evidence_overview"]
            self.assertEqual(
                integrated_evidence_overview["schema_version"],
                "manual_delivery_app_integrated_evidence_overview.v1",
            )
            self.assertEqual(integrated_evidence_overview["summary_status"], "ready_for_human_review")
            self.assertTrue(integrated_evidence_overview["all_evidence_present"])
            self.assertTrue(integrated_evidence_overview["all_evidence_ready"])
            self.assertTrue(integrated_evidence_overview["report_only"])
            self.assertFalse(integrated_evidence_overview["formal_go"])
            self.assertFalse(integrated_evidence_overview["automatic_order_allowed"])
            self.assertTrue(integrated_evidence_overview["human_decides_manually"])
            self.assertEqual(
                integrated_evidence_overview["safety_boundary"],
                "report-only / not FORMAL_GO / no automatic order / human decides manually",
            )
            self.assertTrue(integrated_evidence_overview["evidence"]["intraperiod_review_stdout_json"]["present"])
            self.assertTrue(
                integrated_evidence_overview["evidence"]["intraperiod_review_stdout_json"]["ready_or_valid"]
            )
            self.assertFalse(
                integrated_evidence_overview["evidence"]["intraperiod_review_stdout_json"]["execution_required"]
            )
            self.assertTrue(integrated_evidence_overview["evidence"]["operator_status_diagnostic"]["present"])
            self.assertTrue(integrated_evidence_overview["evidence"]["operator_status_diagnostic"]["ready_or_valid"])
            self.assertFalse(
                integrated_evidence_overview["evidence"]["operator_status_diagnostic"]["execution_required"]
            )
            self.assertTrue(integrated_evidence_overview["evidence"]["safe_config_schema_audit"]["present"])
            self.assertTrue(integrated_evidence_overview["evidence"]["safe_config_schema_audit"]["ready_or_valid"])
            self.assertFalse(integrated_evidence_overview["evidence"]["safe_config_schema_audit"]["execution_required"])
            self.assertTrue(integrated_evidence_overview["evidence"]["operator_triage_summary"]["present"])
            self.assertTrue(integrated_evidence_overview["evidence"]["operator_triage_summary"]["ready_or_valid"])
            self.assertFalse(integrated_evidence_overview["evidence"]["operator_triage_summary"]["execution_required"])
            self.assertTrue(
                integrated_evidence_overview["evidence"]["manual_action_checklist_surface"]["present"]
            )
            self.assertTrue(
                integrated_evidence_overview["evidence"]["manual_action_checklist_surface"]["ready_or_valid"]
            )
            self.assertFalse(
                integrated_evidence_overview["evidence"]["manual_action_checklist_surface"]["execution_required"]
            )
            self.assertEqual(integrated_evidence_overview["note"], "derived from existing app contract/status data only")
            self.assertEqual(
                validation_data["integrated_evidence_overview_evidence_keys"],
                [
                    "intraperiod_review_stdout_json",
                    "manual_action_checklist_surface",
                    "operator_status_diagnostic",
                    "operator_triage_summary",
                    "safe_config_schema_audit",
                ],
            )
            self.assertEqual(validation_data["integrated_evidence_overview_missing_evidence_keys"], [])
            self.assertEqual(validation_data["integrated_evidence_overview_not_ready_evidence_keys"], [])
            self.assertEqual(validation_data["integrated_evidence_overview_execution_required_keys"], [])
            self.assertEqual(
                validation_data["integrated_evidence_overview_schema_version"],
                integrated_evidence_overview["schema_version"],
            )
            self.assertEqual(
                validation_data["integrated_evidence_overview_summary_status"],
                integrated_evidence_overview["summary_status"],
            )
            self.assertEqual(
                validation_data["integrated_evidence_overview_all_evidence_present"],
                integrated_evidence_overview["all_evidence_present"],
            )
            self.assertEqual(
                validation_data["integrated_evidence_overview_all_evidence_ready"],
                integrated_evidence_overview["all_evidence_ready"],
            )
            self.assertEqual(
                validation_data["integrated_evidence_overview_report_only"],
                integrated_evidence_overview["report_only"],
            )
            self.assertEqual(
                validation_data["integrated_evidence_overview_formal_go"],
                integrated_evidence_overview["formal_go"],
            )
            self.assertEqual(
                validation_data["integrated_evidence_overview_automatic_order_allowed"],
                integrated_evidence_overview["automatic_order_allowed"],
            )
            self.assertEqual(
                validation_data["integrated_evidence_overview_human_decides_manually"],
                integrated_evidence_overview["human_decides_manually"],
            )
            self.assertTrue(validation_data["integrated_evidence_overview_report_only"])
            self.assertFalse(validation_data["integrated_evidence_overview_formal_go"])
            self.assertFalse(validation_data["integrated_evidence_overview_automatic_order_allowed"])
            self.assertTrue(validation_data["integrated_evidence_overview_human_decides_manually"])
            self.assertNotIn("execution_required", validation_data["integrated_evidence_overview"])

            missing_contract_data = _manual_delivery_current_app_integration_contract_data()
            missing_contract_data.pop("intraperiod_review_stdout_json")
            write_surface_files(surface_dir, missing_contract_data)
            with self.assertRaises(ValueError) as cm:
                _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertIn("missing_intraperiod_review_stdout_json_contract", str(cm.exception))

            invalid_flags_contract_data = _manual_delivery_current_app_integration_contract_data()
            invalid_flags_contract_data["intraperiod_review_stdout_json"]["required_safety_flags"]["automatic_order_allowed"] = True
            write_surface_files(surface_dir, invalid_flags_contract_data)
            with self.assertRaises(ValueError) as cm:
                _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertIn("invalid_intraperiod_review_stdout_json_safety_flags", str(cm.exception))

            missing_operator_status_data = _manual_delivery_current_app_integration_contract_data()
            missing_operator_status_data.pop("operator_status_diagnostic")
            write_surface_files(surface_dir, missing_operator_status_data)
            with self.assertRaises(ValueError) as cm:
                _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertIn("missing_operator_status_diagnostic_contract", str(cm.exception))

            unsafe_operator_status_data = _manual_delivery_current_app_integration_contract_data()
            unsafe_operator_status_data["operator_status_diagnostic"]["json_required"] = True
            write_surface_files(surface_dir, unsafe_operator_status_data)
            with self.assertRaises(ValueError) as cm:
                _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertIn("invalid_operator_status_diagnostic_contract", str(cm.exception))

            missing_safe_config_data = _manual_delivery_current_app_integration_contract_data()
            missing_safe_config_data.pop("safe_config_schema_audit")
            write_surface_files(surface_dir, missing_safe_config_data)
            with self.assertRaises(ValueError) as cm:
                _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertIn("missing_safe_config_schema_audit_contract", str(cm.exception))

            unsafe_safe_config_data = _manual_delivery_current_app_integration_contract_data()
            unsafe_safe_config_data["safe_config_schema_audit"]["command_executed_by_app"] = True
            write_surface_files(surface_dir, unsafe_safe_config_data)
            with self.assertRaises(ValueError) as cm:
                _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertIn("invalid_safe_config_schema_audit_contract", str(cm.exception))

    def test_manual_delivery_current_app_surface_validation_data_requires_manual_action_checklist(self) -> None:
        def write_surface_files(surface_dir: Path, dashboard_html: str) -> None:
            surface_dir.mkdir(parents=True, exist_ok=True)
            (surface_dir / "index.html").write_text(
                "\n".join(
                    [
                        "app-dashboard.html",
                        "app-ready.json",
                        "app-contract.json",
                        "app-snapshot.json",
                        "app-snapshot-status.json",
                        "app-surface-manifest.json",
                        "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    ]
                ),
                encoding="utf-8",
            )
            (surface_dir / "app-dashboard.html").write_text(dashboard_html, encoding="utf-8")
            (surface_dir / "app-ready.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_ready_check.v1",
                        "current_manual_delivery_app_ready": True,
                        "readiness_status": "ready_for_human_review",
                        "allowed_next_action": "human_review_only",
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-contract.json").write_text(
                json.dumps(
                    _manual_delivery_current_app_integration_contract_data(),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-snapshot.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_snapshot.v1",
                        "snapshot_status": "ready_for_human_review",
                        "current_manual_delivery_ready": True,
                        "allowed_next_action": "human_review_only",
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-snapshot-status.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_snapshot_status.v1",
                        "app_snapshot_status": "valid_ready_for_human_review",
                        "snapshot_status": "ready_for_human_review",
                        "current_manual_delivery_ready": True,
                        "allowed_next_action": "human_review_only",
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (surface_dir / "app-surface-manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "manual_delivery_app_surface_manifest.v1",
                        "surface_status": "ready_for_human_review",
                        "entrypoint": "index.html",
                        "files": {
                            "index_html": "index.html",
                            "app_dashboard_html": "app-dashboard.html",
                            "app_ready_json": "app-ready.json",
                            "app_contract_json": "app-contract.json",
                            "app_snapshot_json": "app-snapshot.json",
                            "app_snapshot_status_json": "app-snapshot-status.json",
                            "app_surface_manifest_json": "app-surface-manifest.json",
                        },
                        "commands": {
                            "surface_ready_gate": "refresh-and-check-current-manual-delivery-app-surface --stdout-json",
                            "surface_validate": "check-current-manual-delivery-app-surface --stdout-json",
                            "surface_export": "export-current-manual-delivery-app-surface",
                        },
                        "human_review_required": True,
                        "trade_execution_allowed": False,
                        "automatic_order_allowed": False,
                        "external_notification_allowed": False,
                        "paper_positions_integration": False,
                        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

        with TemporaryDirectory() as tmpdir:
            surface_dir = Path(tmpdir)
            write_surface_files(
                surface_dir,
                "\n".join(
                    [
                        "<section>Readiness / Status</section>",
                        "<section>Active Plan Summary</section>",
                        "<section>Manual Action Checklist</section>",
                        "<section>Operator Triage Summary</section>",
                        "<section>Integrated Evidence Overview</section>",
                        "<section>Entry mode</section>",
                        "<section>Entry condition</section>",
                        "<section>TP / SL</section>",
                        "<section>Invalidation / wait</section>",
                        "<section>Timeout / validity</section>",
                        "<section>Safety</section>",
                        "<section>Summary status</section>",
                        "<section>operator_status_diagnostic</section>",
                        "<section>safe_config_schema_audit</section>",
                        "<section>intraperiod_review_stdout_json</section>",
                        "<section>operator_triage_summary</section>",
                        "<section>manual_action_checklist_surface</section>",
                        "<section>present=true / ready_or_valid=true / execution_required=false</section>",
                        "<section>derived from existing app contract data only</section>",
                        "<section>Source Files / Generated At</section>",
                        "<section>Safety Boundary</section>",
                        "<section>report-only / not FORMAL_GO / no automatic order / human decides manually</section>",
                    ]
                ),
            )

            validation_data = _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)
            self.assertEqual(validation_data["surface_status"], "valid_ready_for_human_review")
            self.assertTrue(validation_data["current_manual_delivery_app_ready"])
            self.assertFalse(validation_data["automatic_order_allowed"])

            write_surface_files(
                surface_dir,
                "\n".join(
                    [
                        "<section>Readiness / Status</section>",
                        "<section>Active Plan Summary</section>",
                        "<section>Entry mode</section>",
                        "<section>Entry condition</section>",
                        "<section>TP / SL</section>",
                        "<section>Invalidation / wait</section>",
                        "<section>Timeout / validity</section>",
                        "<section>Safety</section>",
                        "<section>Operator Triage Summary</section>",
                        "<section>Summary status</section>",
                        "<section>operator_status_diagnostic</section>",
                        "<section>safe_config_schema_audit</section>",
                        "<section>intraperiod_review_stdout_json</section>",
                        "<section>manual_action_checklist_surface</section>",
                        "<section>derived from existing app contract data only</section>",
                        "<section>Source Files / Generated At</section>",
                        "<section>Safety Boundary</section>",
                        "<section>report-only / not FORMAL_GO / no automatic order / human decides manually</section>",
                    ]
                ),
            )
            with self.assertRaises(ValueError):
                _manual_delivery_current_app_surface_validation_data(app_surface_dir=surface_dir)

    def test_daily_sync_wires_active_plan_candidate_intraperiod_diagnostics(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            reports_analysis = base_dir / "運用資料" / "reports" / "analysis"
            logs_csv.mkdir(parents=True, exist_ok=True)
            reports_analysis.mkdir(parents=True, exist_ok=True)

            candidate_path = logs_csv / "active_plan_paper_candidates.csv"
            with candidate_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "entry_zone_low",
                        "entry_zone_high",
                        "stop_loss",
                        "tp1",
                        "tp2",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-no-ohlcv",
                        "source_signal_id": "sig-no-ohlcv",
                        "timestamp_jst": "2026-06-09T10:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "entry_zone_low": "99",
                        "entry_zone_high": "101",
                        "stop_loss": "95",
                        "tp1": "105",
                        "tp2": "110",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            outcomes_path.write_text("signal_id,evaluation_status\n", encoding="utf-8")
            reviews_path = logs_csv / "user_reviews.csv"
            reviews_path.write_text(",".join(USER_REVIEW_HEADER) + "\n", encoding="utf-8")
            shadow_path = logs_csv / "shadow_log.csv"
            shadow_path.write_text("signal_id,timestamp_jst\n", encoding="utf-8")
            observation_paper_orders_path = logs_csv / "observation_paper_orders.csv"
            phase1b_lite_paper_orders_path = logs_csv / "phase1b_lite_paper_orders.csv"
            paper_positions_path = logs_csv / "paper_positions.csv"
            active_plan_candidate_outcomes_path = logs_csv / "active_plan_candidate_outcomes.csv"
            active_plan_candidate_outcomes_report_path = reports_analysis / "active_plan_candidate_outcomes_20260609.md"
            review_note_path = base_dir / "notes" / "review_note.md"
            daily_report_path = base_dir / "運用資料" / "reports" / "feedback_daily_sync_20260609.md"

            with (
                patch("tools.log_feedback.update_outcomes", return_value=outcomes_path),
                patch("tools.log_feedback.import_reviews", return_value=reviews_path),
                patch(
                    "tools.log_feedback.sync_ai_post_reviews",
                    return_value=(
                        reviews_path,
                        {
                            "eligible": 0,
                            "reused": 0,
                            "created": 0,
                            "skipped_existing_ai": 0,
                            "skipped_human_override": 0,
                            "request_failed": 0,
                            "backlog_pending": 0,
                            "resolved_cli_fallback": 0,
                        },
                    ),
                ),
                patch("tools.log_feedback.build_shadow_log", return_value=shadow_path),
                patch("tools.log_feedback.build_observation_paper_orders", return_value=observation_paper_orders_path),
                patch("tools.log_feedback.build_phase1b_lite_paper_orders", return_value=phase1b_lite_paper_orders_path),
                patch("tools.log_feedback.build_paper_positions", return_value=paper_positions_path),
                patch("tools.log_feedback.build_active_plan_paper_candidates", return_value=candidate_path),
                patch("tools.log_feedback.build_active_plan_candidate_outcomes", return_value=active_plan_candidate_outcomes_path),
                patch("tools.log_feedback.build_active_plan_candidate_outcomes_report", return_value=active_plan_candidate_outcomes_report_path),
                patch("tools.log_feedback.export_review_queue", return_value=review_note_path),
                patch("tools.log_feedback.build_feedback_report", return_value=daily_report_path),
            ):
                result = daily_sync(
                    base_dir=base_dir,
                    review_note_path=review_note_path,
                    output_md=daily_report_path,
                    max_new_reviews=0,
                )

            intraperiod_outcomes_path = logs_csv / "active_plan_candidate_intraperiod_outcomes.csv"
            intraperiod_report_path = (
                reports_analysis
                / f"active_plan_candidate_intraperiod_outcomes_{datetime.now(tz=JST).strftime('%Y%m%d')}.md"
            )

            self.assertEqual(result["active_plan_candidate_intraperiod_outcomes_path"], intraperiod_outcomes_path)
            self.assertEqual(result["active_plan_candidate_intraperiod_outcomes_report_path"], intraperiod_report_path)
            self.assertEqual(result["paper_positions_path"], paper_positions_path)
            self.assertIn("report_path", result)
            self.assertTrue(intraperiod_outcomes_path.exists())
            self.assertTrue(intraperiod_report_path.exists())

            with intraperiod_outcomes_path.open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["outcome"], "no_ohlcv")

            report_text = intraperiod_report_path.read_text(encoding="utf-8")
            self.assertIn("BTCFX Ver03-v4 Active Plan 候補別 intraperiod 評価", report_text)
            self.assertIn("no_ohlcv", report_text)
            self.assertIn("local CSV only", report_text)
            self.assertIn("no exchange fetch", report_text)
            self.assertIn("no daily-sync wiring", report_text)
            self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", report_text)

    def test_build_paper_positions_upserts_without_destroying_existing_state(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            trades_path = logs_csv / "shadow_log.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "opportunity_gate",
                        "opportunity_type",
                        "primary_setup_status",
                        "primary_setup_side",
                        "current_price",
                        "primary_entry_mid",
                        "primary_stop_loss",
                        "shadow_tp1_price",
                        "shadow_tp2_price",
                        "shadow_timeout_hours",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_existing",
                        "timestamp_jst": "2026-05-18T10:00:00+09:00",
                        "opportunity_gate": "pass",
                        "opportunity_type": "test_type",
                        "primary_setup_status": "watch",
                        "primary_setup_side": "long",
                        "current_price": "100",
                        "primary_entry_mid": "99",
                        "primary_stop_loss": "97",
                        "shadow_tp1_price": "103",
                        "shadow_tp2_price": "105",
                        "shadow_timeout_hours": "12",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "sig_new",
                        "timestamp_jst": "2026-05-18T11:00:00+09:00",
                        "opportunity_gate": "pass",
                        "opportunity_type": "new_type",
                        "primary_setup_status": "ready",
                        "primary_setup_side": "short",
                        "current_price": "100",
                        "primary_entry_mid": "100",
                        "primary_stop_loss": "102",
                        "shadow_tp1_price": "98",
                        "shadow_tp2_price": "96",
                        "shadow_timeout_hours": "12",
                    }
                )

            output_path = logs_csv / "paper_positions.csv"
            with output_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_existing",
                        "timestamp_jst": "2026-05-18T10:00:00+09:00",
                        "position_status": "closed",
                        "exit_status": "sl_hit",
                        "realized_r": "-1",
                    }
                )
                writer.writerow(row)

            with patch("tools.log_feedback.load_config", return_value=object()), patch(
                "tools.log_feedback._fetch_future_15m_df",
                return_value=pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"]),
            ):
                build_paper_positions(base_dir=base_dir, trades_path=trades_path, output_path=output_path)

            rows = {row["signal_id"]: row for row in _load_csv_rows(output_path)}
            self.assertEqual(rows["sig_existing"]["position_status"], "closed")
            self.assertEqual(rows["sig_existing"]["exit_status"], "sl_hit")
            self.assertEqual(rows["sig_new"]["position_status"], "opened")

    def test_build_paper_positions_extends_legacy_header(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            trades_path = logs_csv / "shadow_log.csv"
            trades_path.write_text("signal_id,timestamp_jst,opportunity_gate\n", encoding="utf-8")
            output_path = logs_csv / "paper_positions.csv"
            output_path.write_text("signal_id,timestamp_jst,position_status\nlegacy,2026-05-18T10:00:00+09:00,pending\n", encoding="utf-8")

            with patch("tools.log_feedback.load_config", return_value=object()), patch(
                "tools.log_feedback._fetch_future_15m_df",
                return_value=pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"]),
            ):
                build_paper_positions(base_dir=base_dir, trades_path=trades_path, output_path=output_path)

            header = output_path.read_text(encoding="utf-8").splitlines()[0].split(",")
            self.assertIn("opened_at_jst", header)
            self.assertIn("realized_r", header)
            rows = _load_csv_rows(output_path)
            self.assertEqual(rows[0]["signal_id"], "legacy")

    def test_feedback_report_includes_paper_position_execution_summary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                row = {field: "" for field in SHADOW_HEADER}
                row.update(
                    {
                        "signal_id": "sig_closed",
                        "timestamp_jst": datetime.now(timezone.utc).astimezone().isoformat(),
                        "evaluation_status": "complete",
                        "opportunity_gate": "pass",
                        "opportunity_type": "confidence_watch_learning",
                    }
                )
                writer.writerow(row)
            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_closed",
                        "timestamp_jst": datetime.now(timezone.utc).astimezone().isoformat(),
                        "position_status": "closed",
                        "opportunity_type": "confidence_watch_learning",
                        "exit_status": "tp2_hit",
                        "realized_r": "2.0",
                    }
                )
                writer.writerow(row)
            paper_orders_path = logs_csv / "paper_orders.csv"
            paper_orders_path.write_text("signal_id\n", encoding="utf-8")
            observation_path = logs_csv / "observation_paper_orders.csv"
            observation_path.write_text(",".join(OBSERVATION_PAPER_ORDER_HEADER) + "\n", encoding="utf-8")
            lite_path = logs_csv / "phase1b_lite_paper_orders.csv"
            lite_path.write_text(",".join(PHASE1B_LITE_PAPER_ORDER_HEADER) + "\n", encoding="utf-8")

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                paper_orders_path=paper_orders_path,
                observation_paper_orders_path=observation_path,
                phase1b_lite_paper_orders_path=lite_path,
                paper_positions_path=paper_positions_path,
                ai_health_summary={},
            )

            self.assertIn("紙ポジション終了状態: tp2_hit=1件", report)
            self.assertIn("opportunity_type 別 closed", report)
            self.assertIn("平均R=2.00", report)
            self.assertIn("quality guard blocked: 0件", report)

    def test_paper_opportunity_diagnostics_report_groups_market_map_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                row = {field: "" for field in SHADOW_HEADER}
                row.update(
                    {
                        "signal_id": "sig_sl",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "market_map_flags": "support_to_resistance_flip,trend_flip_confirmed_down",
                    }
                )
                writer.writerow(row)
            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_sl",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                        "side": "short",
                        "exit_status": "sl_hit",
                        "realized_r": "-1.0",
                        "primary_setup_reason": "confidence_below_min",
                        "market_map_flags": "support_to_resistance_flip,trend_flip_confirmed_down",
                        "confidence_direction_shadow": "64",
                        "confidence_execution_shadow": "23",
                        "confidence_wait_shadow": "59.2",
                    }
                )
                writer.writerow(row)

            report = build_paper_opportunity_diagnostics_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-05-21",
                date_to="2026-05-21",
            )

            self.assertIn("紙実行候補 entry/wait 診断", report)
            self.assertIn("closed: 1件 / opportunity_type: market_map_opportunity=1件", report)
            self.assertIn("market_map_opportunity: 1件", report)
            self.assertIn("support_to_resistance_flip: 1件", report)
            self.assertIn("sig_sl: sl_hit", report)

    def test_paper_opportunity_diagnostics_report_includes_quality_guard_counts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                blocked = {field: "" for field in SHADOW_HEADER}
                blocked.update(
                    {
                        "signal_id": "sig_blocked",
                        "timestamp_jst": "2026-05-21T09:00:00+09:00",
                        "market_map_flags": "support_to_resistance_flip",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "22",
                        "opportunity_gate": "blocked",
                        "opportunity_reasons": '["require_execution_for_high_wait"]',
                    }
                )
                writer.writerow(blocked)
                passed = {field: "" for field in SHADOW_HEADER}
                passed.update(
                    {
                        "signal_id": "sig_pass",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "market_map_flags": "support_to_resistance_flip",
                        "confidence_direction_shadow": "64",
                        "confidence_execution_shadow": "24",
                        "opportunity_gate": "pass",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                    }
                )
                writer.writerow(passed)

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_pass",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                        "side": "short",
                        "exit_status": "sl_hit",
                        "realized_r": "-1.0",
                        "market_map_flags": "support_to_resistance_flip",
                        "confidence_direction_shadow": "64",
                        "confidence_execution_shadow": "24",
                        "confidence_wait_shadow": "59.2",
                    }
                )
                writer.writerow(row)

            report = build_paper_opportunity_diagnostics_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-05-21",
                date_to="2026-05-21",
            )

            self.assertIn("quality guard blocked: 1件", report)
            self.assertIn("require_execution_for_high_wait=1件", report)
            self.assertIn("hard_quality_blocked: 1件", report)
            self.assertIn("soft_quality_risk: 0件", report)
            self.assertIn("market_map candidate before/after guard: 2件 -> 1件", report)
            self.assertIn("market_map candidate before/after hard guard: 2件 -> 1件", report)

    def test_paper_opportunity_diagnostics_report_includes_soft_quality_risk_counts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                passed = {field: "" for field in SHADOW_HEADER}
                passed.update(
                    {
                        "signal_id": "sig_soft",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "market_map_flags": "support_to_resistance_flip",
                        "confidence_direction_shadow": "64",
                        "confidence_execution_shadow": "28",
                        "confidence_wait_shadow": "60",
                        "opportunity_gate": "pass",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip","soft_risk:suppress_long_high_wait"]',
                    }
                )
                writer.writerow(passed)

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_soft",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip","soft_risk:suppress_long_high_wait"]',
                        "side": "long",
                        "exit_status": "missed_opportunity",
                        "realized_r": "1.3",
                        "market_map_flags": "support_to_resistance_flip",
                        "confidence_direction_shadow": "64",
                        "confidence_execution_shadow": "28",
                        "confidence_wait_shadow": "60.0",
                    }
                )
                writer.writerow(row)

            report = build_paper_opportunity_diagnostics_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-05-21",
                date_to="2026-05-21",
            )

            self.assertIn("quality guard blocked: 0件", report)
            self.assertIn("hard_quality_blocked: 0件", report)
            self.assertIn("soft_quality_risk: 1件", report)
            self.assertIn("soft_risk:suppress_long_high_wait=1件", report)

    def test_paper_opportunity_diagnostics_report_classifies_sl_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                for signal_id, flags in [
                    ("sig_long_wait", "trend_flip_confirmed_up,resistance_to_support_flip"),
                    ("sig_sweep", "support_to_resistance_flip"),
                ]:
                    row = {field: "" for field in SHADOW_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": "2026-05-21T10:00:00+09:00",
                            "market_map_flags": flags,
                            "review_source": "ai",
                            "actual_move_driver": "technical",
                        }
                    )
                    if signal_id == "sig_long_wait":
                        row["user_verdict"] = "too_early"
                        row["sl_eval"] = "too_tight"
                        row["tf_15m_eval"] = "poor"
                        row["logic_validated"] = "false"
                    else:
                        row["user_verdict"] = "useful_wait"
                        row["sl_eval"] = "good"
                        row["tf_15m_eval"] = "good"
                        row["logic_validated"] = "true"
                    writer.writerow(row)

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_long_wait",
                        "timestamp_jst": "2026-05-21T10:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:trend_flip_confirmed_up"]',
                        "side": "long",
                        "exit_status": "sl_hit",
                        "realized_r": "-1.0",
                        "rr_estimate": "1.2",
                        "mfe_atr": "0.10",
                        "mae_atr": "1.40",
                        "primary_setup_reason": "confidence_below_min",
                        "market_map_flags": "trend_flip_confirmed_up,resistance_to_support_flip",
                        "confidence_direction_shadow": "55",
                        "confidence_execution_shadow": "18",
                        "confidence_wait_shadow": "72",
                        "prelabel": "ENTRY_OK",
                    }
                )
                writer.writerow(row)
                row = {field: "" for field in PAPER_POSITION_HEADER}
                row.update(
                    {
                        "signal_id": "sig_sweep",
                        "timestamp_jst": "2026-05-21T11:00:00+09:00",
                        "position_status": "closed",
                        "opportunity_type": "market_map_opportunity",
                        "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                        "side": "short",
                        "exit_status": "missed_opportunity",
                        "realized_r": "1.3",
                        "rr_estimate": "1.5",
                        "mfe_atr": "1.60",
                        "mae_atr": "0.40",
                        "primary_setup_reason": "near_entry_zone_waiting_trigger",
                        "market_map_flags": "support_to_resistance_flip",
                        "confidence_direction_shadow": "70",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "76.8",
                        "prelabel": "SWEEP_WAIT",
                    }
                )
                writer.writerow(row)

            report = build_paper_opportunity_diagnostics_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-05-21",
                date_to="2026-05-21",
            )

            self.assertIn("紙実行候補 entry/wait 診断", report)
            self.assertIn("## SL失敗分類", report)
            self.assertIn("trend_flip_long_sl: 1件", report)
            self.assertIn("## AI事後評価サマリー", report)
            self.assertIn("review coverage: 2/2件", report)
            self.assertIn("suppress_long_high_wait", report)
            self.assertIn("suppress_trend_flip_up_strong", report)
            self.assertIn("require_execution_for_high_wait", report)
            self.assertIn("delay_entry_on_sweep_wait", report)

    def test_paper_entry_sl_wait_redesign_report_includes_required_sections_and_labels(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                for idx, signal_id in enumerate(("sig_a", "sig_b", "sig_c", "sig_d", "sig_e", "sig_f", "sig_g", "sig_h")):
                    row = {field: "" for field in SHADOW_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": f"2026-06-01T12:0{idx + 1}:00+09:00",
                            "market_map_flags": "trend_flip_confirmed_up,support_to_resistance_flip",
                            "user_verdict": "too_early" if signal_id == "sig_a" else "useful_wait",
                            "sl_eval": "too_tight" if signal_id == "sig_a" else "good",
                            "tf_15m_eval": "poor" if signal_id == "sig_a" else "good",
                            "opportunity_type": "market_map_opportunity",
                            "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                        }
                    )
                    writer.writerow(row)

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                rows = [
                    (
                        "sig_a",
                        "sl_hit",
                        "-1.0",
                        '["entry_recheck_required_high_wait","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_b",
                        "missed_opportunity",
                        "1.3",
                        '["entry_recheck_required_low_execution","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_c",
                        "entry_not_reached",
                        "1.3",
                        '["entry_recheck_required_long_weakness","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_d",
                        "tp2_hit",
                        "2.4",
                        '["entry_recheck_required_trend_flip_up","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_e",
                        "timeout",
                        "0.3",
                        '["price_distance_missing","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_f",
                        "sl_hit",
                        "-0.8",
                        '["entry_recheck_required_high_wait","entry_recheck_required_low_execution","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_i",
                        "sl_hit",
                        "-0.6",
                        '["entry_recheck_required_short_low_execution","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_g",
                        "tp2_hit",
                        "2.0",
                        '["entry_recheck_required_trend_flip_up","price_distance_missing","market_map:support_to_resistance_flip"]',
                    ),
                    (
                        "sig_h",
                        "timeout",
                        "0.1",
                        '["market_map:support_to_resistance_flip"]',
                    ),
                ]
                for idx, (signal_id, exit_status, realized_r, opportunity_reasons) in enumerate(rows):
                    row = {field: "" for field in PAPER_POSITION_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": f"2026-06-01T12:0{idx + 1}:00+09:00",
                            "position_status": "closed",
                            "opportunity_type": "market_map_opportunity",
                            "side": "long" if signal_id in {"sig_a", "sig_c", "sig_d", "sig_e"} else "short",
                            "exit_status": exit_status,
                            "realized_r": realized_r,
                            "confidence_direction_shadow": "65",
                            "confidence_execution_shadow": "30",
                            "confidence_wait_shadow": "52",
                            "market_map_flags": "trend_flip_confirmed_up,support_to_resistance_flip",
                            "primary_setup_reason": "near_entry_zone_waiting_trigger",
                            "opportunity_reasons": opportunity_reasons,
                        }
                    )
                    writer.writerow(row)

            report = build_paper_entry_sl_wait_redesign_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-06-01",
                date_to="2026-06-01",
            )

            self.assertIn("# 紙実行候補 entry/wait 診断", report)
            self.assertIn("## 判断", report)
            self.assertIn("## SL失敗分類", report)
            self.assertIn("## AI事後評価サマリー", report)
            self.assertIn("## proposal", report)
            self.assertIn("## 設計判断ラベル", report)
            self.assertIn("## entry recheck reason impact", report)
            self.assertIn("## entry recheck collateral damage breakdown", report)
            self.assertIn("| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | timeout | missed_opportunity | entry_not_reached | avg_R | judgement |", report)
            self.assertIn("| entry_recheck_required_high_wait |", report)
            self.assertIn("| entry_recheck_required_low_execution |", report)
            self.assertIn("| entry_recheck_required_short_low_execution |", report)
            self.assertIn("| entry_recheck_required_long_weakness |", report)
            self.assertIn("| entry_recheck_required_trend_flip_up |", report)
            self.assertIn("| price_distance_missing |", report)
            self.assertIn("| entry_recheck_any |", report)
            self.assertIn("| entry_recheck_none |", report)
            self.assertIn("| market_map_opportunity 全体 |", report)
            self.assertIn("judgement", report)
            self.assertIn("high_wait_sl_risk", report)
            self.assertIn("low_execution_sl_risk", report)
            self.assertIn("trend_flip_up_sl_risk", report)
            self.assertIn("`mfe_atr`", report)
            self.assertIn("`mae_atr`", report)
            self.assertIn("`rr_estimate`", report)

    def test_paper_entry_sl_wait_redesign_report_includes_counterfactual_impact_even_when_logged_reasons_empty(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                for idx, signal_id in enumerate(("sig_a", "sig_b", "sig_c", "sig_d", "sig_e", "sig_f")):
                    row = {field: "" for field in SHADOW_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": f"2026-06-01T13:0{idx + 1}:00+09:00",
                            "opportunity_type": "market_map_opportunity",
                            "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                            "market_map_flags": "support_to_resistance_flip",
                        }
                    )
                    writer.writerow(row)

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()
                rows = [
                    ("sig_a", "long", "entry_zone_not_reached", "sl_hit", "-1.0", "72", "18", "70", "trend_flip_confirmed_up,long_into_major_resistance"),
                    ("sig_b", "short", "confidence_below_min", "sl_hit", "-1.0", "60", "18", "50", "support_to_resistance_flip"),
                    ("sig_c", "long", "confidence_below_min", "timeout", "0.3", "62", "26", "70", "support_to_resistance_flip"),
                    ("sig_d", "long", "confidence_below_min", "tp2_hit", "2.1", "66", "29", "50", "trend_flip_confirmed_up,resistance_to_support_flip"),
                    ("sig_e", "short", "entry_zone_not_reached", "sl_hit", "-0.8", "63", "30", "50", "support_to_resistance_flip"),
                    ("sig_f", "short", "confidence_below_min", "timeout", "0.2", "68", "30", "50", "support_to_resistance_flip"),
                ]
                for idx, (
                    signal_id,
                    side,
                    setup_reason,
                    exit_status,
                    realized_r,
                    direction,
                    execution,
                    wait,
                    market_flags,
                ) in enumerate(rows):
                    row = {field: "" for field in PAPER_POSITION_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": f"2026-06-01T13:0{idx + 1}:00+09:00",
                            "position_status": "closed",
                            "opportunity_type": "market_map_opportunity",
                            "side": side,
                            "primary_setup_reason": setup_reason,
                            "exit_status": exit_status,
                            "realized_r": realized_r,
                            "confidence_direction_shadow": direction,
                            "confidence_execution_shadow": execution,
                            "confidence_wait_shadow": wait,
                            "market_map_flags": market_flags,
                            "opportunity_reasons": '["market_map:support_to_resistance_flip"]',
                        }
                    )
                    writer.writerow(row)

            report = build_paper_entry_sl_wait_redesign_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-06-01",
                date_to="2026-06-01",
            )

            self.assertIn("## entry recheck reason impact", report)
            self.assertIn("## entry recheck counterfactual impact", report)
            self.assertIn("## entry recheck collateral damage breakdown", report)
            reason_section = report.split("## entry recheck reason impact", 1)[1].split("## entry recheck counterfactual impact", 1)[0]
            counterfactual_section = report.split("## entry recheck counterfactual impact", 1)[1].split("## entry recheck collateral damage breakdown", 1)[0]
            breakdown_section = report.split("## entry recheck collateral damage breakdown", 1)[1]
            self.assertIn("| entry_recheck_any | 0 | 0 |", reason_section)
            self.assertIn("| entry_recheck_required_high_wait |", counterfactual_section)
            self.assertIn("| entry_recheck_required_low_execution |", counterfactual_section)
            self.assertIn("| entry_recheck_required_short_low_execution |", counterfactual_section)
            self.assertIn("| entry_recheck_required_long_weakness |", counterfactual_section)
            self.assertIn("| entry_recheck_required_trend_flip_up |", counterfactual_section)
            self.assertIn("| price_distance_missing |", counterfactual_section)
            self.assertIn("| entry_recheck_any | 5 | 5 |", counterfactual_section)
            self.assertIn("| entry_recheck_none | 1 | 1 |", counterfactual_section)
            self.assertIn("counterfactual であり、過去実行時に実際に出た reason ではない", counterfactual_section)
            self.assertIn("### side", breakdown_section)
            self.assertIn("### wait band", breakdown_section)
            self.assertIn("### execution band", breakdown_section)
            self.assertIn("### primary_setup_reason", breakdown_section)
            self.assertIn("### market_map_flags", breakdown_section)
            self.assertIn("### side + wait band", breakdown_section)
            self.assertIn("### side + execution band", breakdown_section)
            self.assertIn("### setup reason + execution band", breakdown_section)
            self.assertIn("| short | 1 | 1 | 0 | 0.0% | 0 | 0.0% | 0 | 0.0% | 1 | 0.20 | insufficient_n |", breakdown_section)
            self.assertIn("| support_to_resistance_flip | 1 | 1 | 0 | 0.0% | 0 | 0.0% | 0 | 0.0% | 1 | 0.20 | insufficient_n |", breakdown_section)

    def test_quality_guard_effectiveness_report_includes_split_and_judgement(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                rows: list[tuple[str, str]] = []
                for i in range(10):
                    rows.append((f"sig_a_{i}", '["require_execution_for_high_wait"]'))
                for i in range(20):
                    rows.append((f"sig_ab_{i}", '["require_execution_for_high_wait+suppress_long_high_wait"]'))
                rows.extend(
                    [
                        ("sig_b", '["soft_risk:suppress_long_high_wait"]'),
                        ("sig_c_0", '["soft_risk:suppress_trend_flip_up_strong"]'),
                        ("sig_c_1", '["soft_risk:suppress_trend_flip_up_strong"]'),
                        ("sig_ac", '["require_execution_for_high_wait+suppress_trend_flip_up_strong"]'),
                        ("sig_bc", '["soft_risk:suppress_long_high_wait+suppress_trend_flip_up_strong"]'),
                        ("sig_abc", '["require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong"]'),
                        ("sig_none", '["market_map:support_to_resistance_flip"]'),
                        ("sig_pass", '["market_map:failed_breakout_down_reversal"]'),
                    ]
                )
                for signal_id, reasons in rows:
                    row = {field: "" for field in SHADOW_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": "2026-06-01T12:05:00+09:00",
                            "opportunity_reasons": reasons,
                        }
                    )
                    writer.writerow(row)

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()

                def _write_row(signal_id: str, exit_status: str, realized_r: str) -> None:
                    row = {field: "" for field in PAPER_POSITION_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": "2026-06-01T12:05:00+09:00",
                            "position_status": "closed",
                            "exit_status": exit_status,
                            "realized_r": realized_r,
                        }
                    )
                    writer.writerow(row)

                for i in range(10):
                    _write_row(f"sig_a_{i}", "sl_hit", "-1.0")
                for i in range(10):
                    _write_row(f"sig_ab_{i}", "sl_hit", "-0.5")
                for i in range(10, 20):
                    _write_row(f"sig_ab_{i}", "entry_not_reached", "1.3")
                _write_row("sig_b", "missed_opportunity", "1.3")
                _write_row("sig_c_0", "timeout", "0.2")
                _write_row("sig_c_1", "tp2_hit", "1.1")
                _write_row("sig_ac", "sl_hit", "-1.0")
                _write_row("sig_bc", "tp2_hit", "2.4")
                _write_row("sig_abc", "sl_hit", "-0.8")
                _write_row("sig_none", "tp2_hit", "2.2")
                _write_row("sig_pass", "missed_opportunity", "1.3")
                _write_row("sig_missing", "sl_hit", "-1.0")

            report = build_quality_guard_effectiveness_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-06-01",
                date_to="2026-06-01",
            )

            self.assertIn("## counterfactual_quality_guard", report)
            self.assertIn("missing_shadow_join: `1件`", report)
            self.assertIn("| A only |", report)
            self.assertIn("| B only |", report)
            self.assertIn("| C only |", report)
            self.assertIn("| A+B |", report)
            self.assertIn("| A+C |", report)
            self.assertIn("| B+C |", report)
            self.assertIn("| A+B+C |", report)
            self.assertIn("| guard該当全体 |", report)
            self.assertIn("| guard非該当全体 |", report)
            self.assertIn("| closed全体 |", report)
            self.assertIn("## entered / non-entered split", report)
            self.assertIn("| group | count | entered_count |", report)
            self.assertIn("| A only | 10 | 10 | 10 | 100.0% | 0 | 0.0% | 0 | -1.00 | 0 | 0 | 0 | 0.00 | blocker_candidate |", report)
            self.assertIn(
                "| A+B | 20 | 10 | 10 | 100.0% | 0 | 0.0% | 0 | -0.50 | 10 | 0 | 10 | 1.30 | defer_due_to_non_entered_mix |",
                report,
            )
            self.assertIn("| C only | 2 | 2 | 0 | 0.0% | 1 | 50.0% | 1 | 0.65 | 0 | 0 | 0 | 0.00 | insufficient_n |", report)
            self.assertIn("純粋な約定後損益だけではない", report)
            self.assertIn("quality guard の blocker 判断では `entered_avg_R` を主判断に使う。", report)
            self.assertIn("`non_entered_avg_R` は参考値であり、約定後損益として扱わない。", report)
            self.assertIn("counterfactual は後付け再計算であり、実運用結果ではない。", report)

    def test_soft_risk_collateral_damage_report_includes_required_groups_and_judgement(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()

                def _write_shadow(signal_id: str, reasons: str) -> None:
                    row = {field: "" for field in SHADOW_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": "2026-06-01T12:05:00+09:00",
                            "opportunity_reasons": reasons,
                        }
                    )
                    writer.writerow(row)

                for i in range(12):
                    _write_shadow(f"sig_b_{i}", '["soft_risk:suppress_long_high_wait"]')
                for i in range(10):
                    _write_shadow(f"sig_c_{i}", '["soft_risk:suppress_trend_flip_up_strong"]')
                for i in range(6):
                    _write_shadow(f"sig_bc_{i}", '["soft_risk:suppress_long_high_wait+suppress_trend_flip_up_strong"]')
                for i in range(10):
                    _write_shadow(f"sig_ab_{i}", '["require_execution_for_high_wait+suppress_long_high_wait"]')
                _write_shadow("sig_none", '["market_map:support_to_resistance_flip"]')

            paper_positions_path = logs_csv / "paper_positions.csv"
            with paper_positions_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=PAPER_POSITION_HEADER)
                writer.writeheader()

                def _write_position(signal_id: str, exit_status: str, realized_r: str) -> None:
                    row = {field: "" for field in PAPER_POSITION_HEADER}
                    row.update(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": "2026-06-01T12:05:00+09:00",
                            "position_status": "closed",
                            "side": "short",
                            "primary_setup_reason": "confidence_below_min",
                            "market_map_flags": "support_to_resistance_flip",
                            "confidence_direction_shadow": "66",
                            "confidence_execution_shadow": "24",
                            "confidence_wait_shadow": "58",
                            "exit_status": exit_status,
                            "realized_r": realized_r,
                        }
                    )
                    writer.writerow(row)

                # B only -> keep_soft
                for i in range(2):
                    _write_position(f"sig_b_{i}", "sl_hit", "-1.0")
                _write_position("sig_b_2", "tp2_hit", "2.4")
                for i in range(3, 10):
                    _write_position(f"sig_b_{i}", "timeout", "0.2")
                _write_position("sig_b_10", "entry_not_reached", "1.3")
                _write_position("sig_b_11", "entry_not_reached", "1.3")

                # C only -> avoid_hardening
                for i in range(3):
                    _write_position(f"sig_c_{i}", "tp2_hit", "2.0")
                for i in range(3, 6):
                    _write_position(f"sig_c_{i}", "sl_hit", "-1.0")
                for i in range(6, 10):
                    _write_position(f"sig_c_{i}", "timeout", "0.1")

                # B+C -> monitor_only (count < 10)
                _write_position("sig_bc_0", "sl_hit", "-1.0")
                _write_position("sig_bc_1", "sl_hit", "-1.0")
                _write_position("sig_bc_2", "tp2_hit", "2.4")
                _write_position("sig_bc_3", "timeout", "0.3")
                _write_position("sig_bc_4", "missed_opportunity", "1.3")
                _write_position("sig_bc_5", "entry_not_reached", "1.3")

                for i in range(10):
                    _write_position(f"sig_ab_{i}", "sl_hit", "-0.7")
                _write_position("sig_none", "tp2_hit", "2.1")
                _write_position("sig_missing", "sl_hit", "-1.0")

            report = build_soft_risk_collateral_damage_report(
                base_dir=base_dir,
                paper_positions_path=paper_positions_path,
                shadow_path=shadow_path,
                date_from="2026-06-01",
                date_to="2026-06-01",
                limit=5,
            )

            self.assertIn("# soft risk collateral damage", report)
            self.assertIn("## group table", report)
            self.assertIn("## representative examples", report)
            self.assertIn("missing_shadow_join: `1件`", report)
            self.assertIn("| B only |", report)
            self.assertIn("| C only |", report)
            self.assertIn("| B+C |", report)
            self.assertIn("| B/C soft risk 全体 |", report)
            self.assertIn("collateral_damage_score", report)
            self.assertIn("judgement", report)
            self.assertIn("| B only | 12 | 10 | 2 | 20.0% | 1 | 10.0% | 7 | 0.18 | 2 | 0 | 2 | 1.30 | 1.50 | keep_soft |", report)
            self.assertIn("| C only | 10 | 10 | 3 | 30.0% | 3 | 30.0% | 4 | 0.34 | 0 | 0 | 0 | 0.00 | 4.50 | avoid_hardening |", report)
            self.assertIn("| B+C | 6 | 4 | 2 | 50.0% | 1 | 25.0% | 1 | 0.17 | 2 | 1 | 1 | 1.30 | 2.25 | monitor_only |", report)
            self.assertIn("### B only", report)
            self.assertIn("sig_b_0", report)

    def test_normalize_ai_post_review_applies_defaults(self) -> None:
        row = _normalize_ai_post_review(
            {
                "user_verdict": "invalid",
                "usefulness_1to5": 9,
                "would_trade": "maybe",
                "actual_move_driver": "other",
                "misleading_entry_like_wording": "",
                "sl_eval": "bad",
                "tp_eval": "",
                "tf_4h_eval": "bad",
                "tf_1h_eval": "",
                "tf_15m_eval": "oops",
                "memo": "メモ",
            },
            model="gpt-test",
            image_mode="price_map_svg",
        )

        self.assertEqual(row["user_verdict"], "low_value")
        self.assertEqual(row["usefulness_1to5"], "1")
        self.assertEqual(row["would_trade"], "no")
        self.assertEqual(row["actual_move_driver"], "unknown")
        self.assertEqual(row["misleading_entry_like_wording"], "no")
        self.assertEqual(row["sl_eval"], "good")
        self.assertEqual(row["tp_eval"], "good")
        self.assertEqual(row["tf_4h_eval"], "good")
        self.assertEqual(row["tf_1h_eval"], "good")
        self.assertEqual(row["tf_15m_eval"], "good")
        self.assertEqual(row["review_action_class"], "watch")
        self.assertEqual(row["review_priority"], "low")
        self.assertEqual(row["next_action"], "同種通知を継続観測する")
        self.assertEqual(row["review_source"], "ai")
        self.assertEqual(row["review_model"], "gpt-test")

    def test_normalize_ai_post_review_infers_action_fields(self) -> None:
        row = _normalize_ai_post_review(
            {
                "user_verdict": "useful_wait",
                "usefulness_1to5": 4,
                "would_trade": "conditional",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "too_close",
                "tf_4h_eval": "good",
                "tf_1h_eval": "mixed",
                "tf_15m_eval": "good",
                "memo": "監視として有効",
            },
            model="gpt-test",
            image_mode="price_map_svg",
        )

        self.assertEqual(row["review_action_class"], "tune_exit")
        self.assertEqual(row["review_priority"], "high")
        self.assertEqual(row["next_action"], "TP1/TP2 を遠めにする候補を検証する")

    def test_build_review_chart_svg_path_persists_snapshot_when_enabled(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            signal_path = base_dir / "logs" / "signals" / "sig_1.json"
            signal_path.parent.mkdir(parents=True, exist_ok=True)
            signal_path.write_text(
                '{"signal_id":"sig_1","current_price":100,"long_setup":{"entry_zone":{"low":95,"high":97},"stop_loss":92,"tp1":103,"tp2":106},"short_setup":{"entry_zone":{"low":103,"high":105},"stop_loss":108,"tp1":99,"tp2":96},"support_zones":[{"low":95,"high":97}],"resistance_zones":[{"low":103,"high":105}],"chart_snapshot":{"candles_4h":[{"timestamp":1775746800000,"open":101,"high":102,"low":99,"close":100}],"candles_1h":[{"timestamp":1775781000000,"open":100,"high":101,"low":99,"close":100}],"candles_15m":[{"timestamp":1775782800000,"open":100,"high":101,"low":99,"close":100}]}}',
                encoding="utf-8",
            )
            temp_dir = base_dir / "tmp"
            temp_dir.mkdir()
            persist_dir = _ai_post_review_chart_dir(base_dir)

            image_path = _build_review_chart_svg_path(base_dir, "sig_1", temp_dir, persist_dir=persist_dir)

            self.assertIsNotNone(image_path)
            assert image_path is not None
            self.assertTrue(image_path.exists())
            saved_path = persist_dir / "sig_1_price_map.svg"
            self.assertTrue(saved_path.exists())
            self.assertIn('class="price-map"', saved_path.read_text(encoding="utf-8"))

    def test_evaluate_trade_row_computes_outcomes_and_zone_results(self) -> None:
        trade_row = {
            "signal_id": "20260311_090500",
            "timestamp_utc": "2026-03-11T00:05:00Z",
            "timestamp_jst": "2026-03-11T09:05:00+09:00",
            "current_price": "100",
            "atr_15m_value": "10",
            "bias": "long",
            "prelabel": "SWEEP_WAIT",
            "signal_tier": "normal",
            "nearest_support_low": "96",
            "nearest_support_high": "99",
            "nearest_resistance_low": "120",
            "nearest_resistance_high": "123",
        }
        signal_ms = int(pd.Timestamp(trade_row["timestamp_utc"]).timestamp() * 1000)
        future_df = pd.DataFrame(
            [
                {"timestamp": signal_ms + 15 * 60 * 1000, "open": 100, "high": 101, "low": 97, "close": 98, "volume": 1},
                {"timestamp": signal_ms + 30 * 60 * 1000, "open": 98, "high": 103, "low": 95, "close": 101, "volume": 1},
                {"timestamp": signal_ms + 60 * 60 * 1000, "open": 101, "high": 106, "low": 100, "close": 104, "volume": 1},
                {"timestamp": signal_ms + 4 * 60 * 60 * 1000, "open": 104, "high": 112, "low": 103, "close": 108, "volume": 1},
                {"timestamp": signal_ms + 24 * 60 * 60 * 1000, "open": 108, "high": 115, "low": 107, "close": 113, "volume": 1},
            ]
        )

        outcome = evaluate_trade_row(trade_row, future_df)

        self.assertEqual(outcome["evaluation_status"], "complete")
        self.assertEqual(outcome["direction_outcome"], "correct")
        self.assertEqual(outcome["wait_outcome"], "wait_was_good")
        self.assertEqual(outcome["signal_based_MFE_12h"], 1.2)
        self.assertEqual(outcome["support_touch_result"], "touched")
        self.assertEqual(outcome["support_hold_result"], "held")
        self.assertEqual(outcome["resistance_touch_result"], "untouched")
        self.assertEqual(outcome["resistance_hold_result"], "untouched")

    def test_import_reviews_reads_done_rows_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            review_note = base_dir / "review.md"
            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| sig_done | 2026-03-30T09:05:00+09:00 | subject | auto | useful_entry | 5 | yes | technical | good | done |",
                        "| sig_pending | 2026-03-30T13:05:00+09:00 | subject2 | auto2 |  |  |  |  |  | pending |",
                    ]
                ),
                encoding="utf-8",
            )

            reviews_path = import_reviews(base_dir=base_dir, review_note_path=review_note, reviews_path=base_dir / "user_reviews.csv")
            rows = _load_csv_rows(reviews_path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "sig_done")
            self.assertEqual(rows[0]["review_status"], "done")

    def test_export_review_queue_keeps_staged_done_and_adds_pending(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
                    "evaluation_status",
                    "outcome",
                    "direction_outcome",
                    "entry_outcome",
                    "wait_outcome",
                    "skip_outcome",
                    "support_hold_result",
                    "resistance_hold_result",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_new",
                        "timestamp_jst": "2026-03-30T09:05:00+09:00",
                        "evaluation_status": "complete",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "held",
                        "resistance_hold_result": "untouched",
                        "outcome": "win",
                    }
                )

            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_new",
                        "timestamp_jst": "2026-03-30T09:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "new subject",
                    }
                )

            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| sig_done | 2026-03-30T07:05:00+09:00 | subject | auto | useful_skip | 4 | no | technical | ok | done |",
                    ]
                ),
                encoding="utf-8",
            )

            export_review_queue(
                base_dir=base_dir,
                review_note_path=review_note,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
            )

            rows = _load_review_state_rows(_review_state_path(base_dir))
            signal_ids = [row["signal_id"] for row in rows]
            self.assertIn("sig_done", signal_ids)
            self.assertIn("sig_new", signal_ids)

    def test_review_form_markdown_does_not_duplicate_table_header(self) -> None:
        row = {column: "" for column in REVIEW_NOTE_COLUMNS}
        row.update(
            {
                "signal_id": "sig_form",
                "timestamp_jst": "2026-03-30T09:05:00+09:00",
                "subject": "subject",
                "auto_eval_summary": "auto",
                "bias": "long",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "ready",
                "signal_tier": "strong_machine",
                "notify_reason": '["status_upgraded"]',
                "evaluation_status": "complete",
                "confidence_direction_shadow": "88",
                "confidence_execution_shadow": "63",
                "confidence_wait_shadow": "24",
                "review_status": "pending",
            }
        )

        html = _render_review_form_html([row], Path("/tmp/review.md"))

        self.assertNotIn("| signal_id |", html)
        self.assertIn("今の確認軸", html)
        self.assertIn("direction_strength", html)
        self.assertIn("notify_reason", html)
        self.assertIn("localStorage", html)
        self.assertIn("restoreDraft()", html)
        self.assertIn("draft-status", html)
        self.assertIn("getDraftStorage()", html)
        self.assertIn("renderCards();\n    restoreDraft();\n    renderCards();", html)
        self.assertIn("通知 1", html)
        self.assertIn(">subject<", html)
        self.assertIn("この通知、役に立った？", html)
        self.assertIn("レビュー進捗", html)
        self.assertIn("完了にする", html)
        self.assertIn("saveToServer()", html)
        self.assertIn("reloadFromServer()", html)
        self.assertIn("03/30 09:05", html)
        self.assertIn("ロング寄り", html)
        self.assertIn("2026-03-30 05:05 JST 以降の通知だけを見る", html)
        self.assertNotIn("??", html)
        self.assertNotIn("replaceAll", html)
        self.assertIn("syncRowsFromDom()", html)
        self.assertIn("bindSelectHandlers()", html)
        self.assertIn("保存先", html)
        self.assertIn("AI 評価を主系として使い", html)
        self.assertNotIn("Markdownをコピー", html)

    def test_import_reviews_ignores_rows_before_review_cutoff(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            review_note = base_dir / "review.md"
            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| old_sig | 2026-03-30T05:04:00+09:00 | old subject | auto | useful_entry | 5 | yes | technical | old | done |",
                        "| new_sig | 2026-03-30T05:05:00+09:00 | new subject | auto | useful_wait | 4 | no | macro | new | done |",
                    ]
                ),
                encoding="utf-8",
            )

            reviews_path = import_reviews(base_dir=base_dir, review_note_path=review_note, reviews_path=base_dir / "user_reviews.csv")
            rows = _load_csv_rows(reviews_path)

            self.assertEqual([row["signal_id"] for row in rows], ["new_sig"])

    def test_default_review_form_path_uses_review_note_sibling(self) -> None:
        self.assertEqual(_review_form_path(DEFAULT_REVIEW_NOTE), DEFAULT_REVIEW_FORM)

    def test_export_review_queue_includes_recent_notified_trade_without_complete_outcome(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "evaluation_status"])
                writer.writeheader()

            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "was_notified",
                        "summary_subject",
                        "bias",
                        "prelabel",
                        "primary_setup_status",
                        "signal_tier",
                        "notify_reason_codes",
                        "data_quality_flag",
                        "confidence_direction_shadow",
                        "confidence_execution_shadow",
                        "confidence_wait_shadow",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_recent",
                        "timestamp_jst": "2026-03-30T05:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "recent subject",
                        "bias": "short",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "ready",
                        "signal_tier": "normal",
                        "notify_reason_codes": '["status_upgraded"]',
                        "confidence_direction_shadow": "71",
                        "confidence_execution_shadow": "44",
                        "confidence_wait_shadow": "22",
                    }
                )

            export_review_queue(
                base_dir=base_dir,
                review_note_path=review_note,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
            )

            rows = _load_review_state_rows(_review_state_path(base_dir))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "sig_recent")
            self.assertIn("事後評価待ち", rows[0]["auto_eval_summary"])

    def test_export_review_queue_hides_old_rows_from_note_and_form(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "evaluation_status"])
                writer.writeheader()

            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject"])
                writer.writeheader()

            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| old_sig | 2026-03-30T05:04:00+09:00 | old subject | auto | useful_entry | 5 | yes | technical | old | done |",
                        "| new_sig | 2026-03-30T05:05:00+09:00 | new subject | auto | useful_wait | 4 | no | macro | new | done |",
                    ]
                ),
                encoding="utf-8",
            )

            export_review_queue(
                base_dir=base_dir,
                review_note_path=review_note,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
            )

            note_text = review_note.read_text(encoding="utf-8")
            form_text = _review_form_path(review_note).read_text(encoding="utf-8")

            self.assertNotIn("old_sig", note_text)
            self.assertIn("AI事後評価の進捗を確認", note_text)
            self.assertNotIn("old_sig", form_text)
            self.assertIn("new_sig", form_text)

    def test_export_review_queue_note_is_ai_first_and_lists_human_overrides_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            outcomes_path = base_dir / "outcomes.csv"
            trades_path = base_dir / "trades.csv"
            reviews_path = base_dir / "user_reviews.csv"
            review_note = base_dir / "review.md"
            logs_review = base_dir / "logs" / "review"
            logs_review.mkdir(parents=True, exist_ok=True)

            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "evaluation_status"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_human", "timestamp_jst": "2026-03-30T09:05:00+09:00", "evaluation_status": "complete"})
                writer.writerow({"signal_id": "sig_ai", "timestamp_jst": "2026-03-30T10:05:00+09:00", "evaluation_status": "complete"})

            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "was_notified",
                        "summary_subject",
                        "bias",
                        "prelabel",
                        "primary_setup_status",
                        "signal_tier",
                        "notify_reason_codes",
                        "confidence_direction_shadow",
                        "confidence_execution_shadow",
                        "confidence_wait_shadow",
                    ],
                )
                writer.writeheader()
                writer.writerow({"signal_id": "sig_human", "timestamp_jst": "2026-03-30T09:05:00+09:00", "was_notified": "true", "summary_subject": "human subject", "bias": "long", "prelabel": "ENTRY_OK", "primary_setup_status": "ready", "signal_tier": "normal", "notify_reason_codes": '["status_upgraded"]', "confidence_direction_shadow": "70", "confidence_execution_shadow": "45", "confidence_wait_shadow": "20"})
                writer.writerow({"signal_id": "sig_ai", "timestamp_jst": "2026-03-30T10:05:00+09:00", "was_notified": "true", "summary_subject": "ai subject", "bias": "short", "prelabel": "SWEEP_WAIT", "primary_setup_status": "watch", "signal_tier": "normal", "notify_reason_codes": '["attention_bias_changed"]', "confidence_direction_shadow": "60", "confidence_execution_shadow": "25", "confidence_wait_shadow": "70"})

            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_human",
                        "timestamp_jst": "2026-03-30T09:05:00+09:00",
                        "subject": "human subject",
                        "auto_eval_summary": "auto",
                        "user_verdict": "useful_wait",
                        "usefulness_1to5": "4",
                        "would_trade": "no",
                        "actual_move_driver": "technical",
                        "misleading_entry_like_wording": "no",
                        "logic_validated": "true",
                        "sl_eval": "good",
                        "tp_eval": "good",
                        "tf_4h_eval": "good",
                        "tf_1h_eval": "good",
                        "tf_15m_eval": "good",
                        "review_source": "human_override",
                        "review_model": "",
                        "review_image_mode": "",
                        "review_variant": "",
                        "review_action_class": "watch",
                        "review_priority": "medium",
                        "next_action": "watch",
                        "memo": "manual",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-03-30T00:30:00Z",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "sig_ai",
                        "timestamp_jst": "2026-03-30T10:05:00+09:00",
                        "subject": "ai subject",
                        "auto_eval_summary": "auto",
                        "user_verdict": "too_early",
                        "usefulness_1to5": "2",
                        "would_trade": "conditional",
                        "actual_move_driver": "technical",
                        "misleading_entry_like_wording": "yes",
                        "logic_validated": "false",
                        "sl_eval": "too_tight",
                        "tp_eval": "good",
                        "tf_4h_eval": "good",
                        "tf_1h_eval": "mixed",
                        "tf_15m_eval": "poor",
                        "review_source": "ai",
                        "review_model": "gpt-test",
                        "review_image_mode": "price_map_svg",
                        "review_variant": "ai_post_review_v2",
                        "review_action_class": "tune_entry",
                        "review_priority": "high",
                        "next_action": "delay",
                        "memo": "",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-03-30T00:35:00Z",
                    }
                )

            export_review_queue(
                base_dir=base_dir,
                review_note_path=review_note,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
            )

            note_text = review_note.read_text(encoding="utf-8")
            self.assertIn("AI事後評価の進捗を確認", note_text)
            self.assertIn("AI評価済み: 1", note_text)
            self.assertIn("人が上書き済み: 1", note_text)
            self.assertIn("human subject", note_text)
            self.assertNotIn("ai subject /", note_text)

    def test_load_review_note_rows_ignores_single_header_and_keeps_real_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            review_note = Path(tmpdir) / "review.md"
            review_note.write_text(
                "\n".join(
                    [
                        "# 通知評価シート",
                        "",
                        "## レビュー一覧",
                        f"| {' | '.join(REVIEW_NOTE_COLUMNS)} |",
                        f"| {' | '.join(['---'] * len(REVIEW_NOTE_COLUMNS))} |",
                        "| sig_form | 2026-03-30T09:05:00+09:00 | subject | auto |  |  |  |  |  | pending |",
                    ]
                ),
                encoding="utf-8",
            )

            rows = _load_review_note_rows(review_note)

            self.assertEqual([row["signal_id"] for row in rows], ["sig_form"])
            self.assertNotIn("signal_id", [row["signal_id"] for row in rows])

    def test_improvement_candidates_have_expected_limits(self) -> None:
        rows = []
        for idx in range(5):
            rows.append(
                {
                    "signal_id": f"entry_{idx}",
                    "prelabel": "ENTRY_OK",
                    "entry_outcome": "poor_entry",
                    "signal_tier": "normal",
                    "direction_outcome": "wrong",
                    "user_verdict": "too_early" if idx < 3 else "",
                    "support_hold_result": "broken",
                }
            )
        for idx in range(5):
            rows.append(
                {
                    "signal_id": f"wait_{idx}",
                    "prelabel": "SWEEP_WAIT",
                    "wait_outcome": "wait_too_strict",
                    "signal_tier": "normal",
                    "direction_outcome": "correct",
                    "user_verdict": "low_value" if idx < 3 else "",
                    "support_hold_result": "broken",
                }
            )
        for idx in range(5):
            rows.append(
                {
                    "signal_id": f"skip_{idx}",
                    "prelabel": "NO_TRADE_CANDIDATE",
                    "skip_outcome": "skip_too_strict",
                    "signal_tier": "strong_ai_confirmed",
                    "direction_outcome": "wrong",
                    "support_hold_result": "broken",
                }
            )

        weekly = _build_improvement_candidates(rows, monthly=False)
        monthly = _build_improvement_candidates(rows, monthly=True)

        self.assertLessEqual(len(weekly), 3)
        self.assertLessEqual(len(monthly), 2)

    def test_improvement_candidates_include_sl_tp_feedback(self) -> None:
        rows = [
            {"signal_id": f"tp_close_{idx}", "tp_eval": "too_close", "sl_eval": "good"}
            for idx in range(4)
        ] + [
            {"signal_id": f"sl_tight_{idx}", "tp_eval": "good", "sl_eval": "too_tight"}
            for idx in range(4)
        ] + [
            {"signal_id": f"filler_{idx}", "tp_eval": "good", "sl_eval": "good"}
            for idx in range(2)
        ]

        candidates = _build_improvement_candidates(rows, monthly=False)
        titles = {item["title"] for item in candidates}

        self.assertIn("TP が近すぎるケースが多い", titles)
        self.assertIn("SL が狭すぎるケースが多い", titles)

    def test_improvement_candidates_include_tf15_feedback(self) -> None:
        rows = [
            {"signal_id": f"tf_bad_{idx}", "tf_15m_eval": "poor"}
            for idx in range(4)
        ] + [
            {"signal_id": f"tf_good_{idx}", "tf_15m_eval": "good"}
            for idx in range(2)
        ]

        candidates = _build_improvement_candidates(rows, monthly=False)
        titles = {item["title"] for item in candidates}

        self.assertIn("15分足の執行価格精度が弱い", titles)

    def test_improvement_candidates_split_entry_ok_invalid_from_poor_entry(self) -> None:
        rows = [
            {
                "signal_id": f"invalid_{idx}",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "invalid",
                "primary_setup_reason": "rr_below_min" if idx < 3 else "",
                "invalid_reason": "RR不足" if idx == 3 else "",
                "entry_outcome": "poor_entry",
            }
            for idx in range(4)
        ]
        rows.extend(
            {
                "signal_id": f"ready_{idx}",
                "prelabel": "ENTRY_OK",
                "primary_setup_status": "ready",
                "entry_outcome": "good_entry",
            }
            for idx in range(3)
        )

        candidates = _build_improvement_candidates(rows, monthly=False, period_rows=rows)
        titles = {item["title"] for item in candidates}
        conflict = next(item for item in candidates if item["title"] == "ENTRY_OK と setup invalid の整合性崩れ")

        self.assertIn("ENTRY_OK と setup invalid の整合性崩れ", titles)
        self.assertNotIn("ENTRY_OK が甘め", titles)
        self.assertIn("rr_below_min=3件", conflict["reason"])
        self.assertIn("RR不足=1件", conflict["reason"])

    def test_sync_ai_post_reviews_writes_ai_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_ai",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_ai", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            (base_dir / "logs" / "signals" / "sig_ai.json").write_text(
                '{"signal_id":"sig_ai","summary_subject":"subject","current_price":100,"long_setup":{"status":"watch","entry_zone":{"low":99,"high":101},"stop_loss":97,"tp1":104,"tp2":106},"short_setup":{"status":"invalid","entry_zone":{"low":102,"high":103},"stop_loss":104,"tp1":98,"tp2":96},"support_zones":[],"resistance_zones":[],"chart_snapshot":{"intervals":["4h","1h","15m"],"candles_4h":[{"timestamp":1,"open":98,"high":102,"low":96,"close":100.5}],"candles_1h":[{"timestamp":1,"open":99,"high":101,"low":98,"close":100.2}],"candles_15m":[{"timestamp":1,"open":100,"high":101,"low":99,"close":100.5}]}}',
                encoding="utf-8",
            )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg, patch("tools.log_feedback._build_review_chart_svg_path", return_value=None):
                mocked_cli.return_value = {
                    "user_verdict": "useful_wait",
                    "usefulness_1to5": 4,
                    "would_trade": "conditional",
                    "actual_move_driver": "technical",
                    "misleading_entry_like_wording": "no",
                    "sl_eval": "good",
                    "tp_eval": "too_far",
                    "tf_4h_eval": "good",
                    "tf_1h_eval": "mixed",
                    "tf_15m_eval": "poor",
                    "review_action_class": "tune_exit",
                    "review_priority": "medium",
                    "next_action": "TPを調整する",
                    "memo": "監視として有効",
                }
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {"AI_ADVICE_CLI_COMMAND": "echo", "OPENAI_ADVICE_MODEL": "gpt-test", "AI_TIMEOUT_SEC": 30},
                )()

                sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                )

            rows = _load_csv_rows(reviews_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["review_source"], "ai")
            self.assertEqual(rows[0]["sl_eval"], "good")
            self.assertEqual(rows[0]["tp_eval"], "too_far")
            self.assertEqual(rows[0]["tf_4h_eval"], "good")
            self.assertEqual(rows[0]["tf_1h_eval"], "mixed")
            self.assertEqual(rows[0]["tf_15m_eval"], "poor")
            self.assertEqual(rows[0]["review_action_class"], "tune_exit")
            self.assertEqual(rows[0]["review_priority"], "medium")
            self.assertEqual(rows[0]["next_action"], "TPを調整する")
            self.assertEqual(rows[0]["logic_validated"], "true")

    def test_sync_ai_post_reviews_reuses_snapshot_without_cli(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "review" / "ai_post_reviews").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_cached",
                        "timestamp_jst": "2026-04-10T02:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "cached subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_cached", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            snapshot_path = base_dir / "logs" / "review" / "ai_post_reviews" / "sig_cached.json"
            snapshot_path.write_text(
                """{
  "signal_id": "sig_cached",
  "review": {
    "signal_id": "sig_cached",
    "timestamp_jst": "2026-04-10T02:05:00+09:00",
    "subject": "cached subject",
    "auto_eval_summary": "summary",
    "user_verdict": "useful_wait",
    "usefulness_1to5": "4",
    "would_trade": "no",
    "actual_move_driver": "technical",
    "misleading_entry_like_wording": "no",
    "logic_validated": "true",
    "sl_eval": "good",
    "tp_eval": "good",
    "tf_4h_eval": "good",
    "tf_1h_eval": "mixed",
    "tf_15m_eval": "poor",
    "review_source": "ai",
    "review_model": "gpt-test",
    "review_image_mode": "price_map_svg",
    "review_variant": "ai_post_review_v1",
    "memo": "cached",
    "review_status": "done",
    "reviewed_at_utc": "2026-04-10T00:00:00Z"
  }
}""",
                encoding="utf-8",
            )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type("Cfg", (), {})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=1,
                )

            mocked_cli.assert_not_called()
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["review_source"], "ai")
            self.assertEqual(rows[0]["tf_15m_eval"], "poor")
            self.assertEqual(stats["reused"], 1)
            self.assertEqual(rows[0]["review_action_class"], "tune_entry")
            self.assertEqual(rows[0]["review_priority"], "medium")
            self.assertEqual(rows[0]["review_variant"], "ai_post_review_v2")

    def test_sync_ai_post_reviews_skips_existing_ai_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_ai_done",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_ai_done", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_ai_done",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "subject": "subject",
                        "auto_eval_summary": "summary",
                        "user_verdict": "useful_wait",
                        "usefulness_1to5": "4",
                        "would_trade": "no",
                        "actual_move_driver": "technical",
                        "misleading_entry_like_wording": "no",
                        "logic_validated": "true",
                        "sl_eval": "good",
                        "tp_eval": "good",
                        "tf_4h_eval": "good",
                        "tf_1h_eval": "good",
                        "tf_15m_eval": "good",
                        "review_source": "ai",
                        "review_model": "gpt-test",
                        "review_image_mode": "price_map_svg",
                        "review_variant": "ai_post_review_v1",
                        "memo": "done",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-04-10T00:00:00Z",
                    }
                )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type("Cfg", (), {})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=1,
                )

            mocked_cli.assert_not_called()
            self.assertEqual(stats["skipped_existing_ai"], 1)

    def test_sync_ai_post_reviews_respects_daily_cap(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_today_cap",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_today_cap", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            today_utc = "2026-04-10T00:00:00Z"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "already_today",
                        "review_source": "ai",
                        "review_variant": "ai_post_review_v1",
                        "reviewed_at_utc": today_utc,
                    }
                )

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg, patch("tools.log_feedback._reviewed_on_jst", return_value=True):
                mocked_cfg.return_value = type("Cfg", (), {"AI_POST_REVIEW_DAILY_MAX": 1, "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_not_called()
            self.assertEqual(stats["already_reviewed_today"], 1)
            self.assertEqual(stats["skipped_daily_cap"], 1)

    def test_sync_ai_post_reviews_filters_attention_when_main_only_enabled(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_attention",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "attention",
                        "signal_tier": "strong_ai_confirmed",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_attention", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            with patch("tools.log_feedback.run_cli_json") as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type("Cfg", (), {"AI_POST_REVIEW_DAILY_MAX": 2, "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True})()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_not_called()
            self.assertEqual(stats["skipped_priority_filter"], 1)

    def test_sync_ai_post_reviews_stops_after_consecutive_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                for idx in range(5):
                    writer.writerow(
                        {
                            "signal_id": f"sig_fail_{idx}",
                            "timestamp_jst": "2026-04-10T03:05:00+09:00",
                            "was_notified": "true",
                            "summary_subject": "subject",
                            "prelabel_primary_reason": "balanced_location",
                            "notification_kind": "main",
                            "signal_tier": "normal",
                        }
                    )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                for idx in range(5):
                    writer.writerow({"signal_id": f"sig_fail_{idx}", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            with patch("tools.log_feedback.run_cli_json", side_effect=RuntimeError("usage limit")) as mocked_cli, patch(
                "tools.log_feedback.load_config"
            ) as mocked_cfg, patch("tools.log_feedback._build_review_chart_svg_path", return_value=None):
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 5,
                        "AI_POST_REVIEW_MAX_CONSECUTIVE_FAILURES": 2,
                        "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True,
                        "AI_ADVICE_CLI_COMMAND": "dummy-cli",
                    },
                )()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            self.assertEqual(mocked_cli.call_count, 2)
            self.assertEqual(stats["request_failed"], 2)
            self.assertEqual(stats["stopped_after_failures"], 1)

    def test_sync_ai_post_reviews_does_not_use_api_fallback_without_explicit_api_permission(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_api_fallback",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_api_fallback", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            with patch("tools.log_feedback.run_cli_json", side_effect=RuntimeError("usage limit")) as mocked_cli, patch(
                "tools.log_feedback.load_config"
            ) as mocked_cfg, patch("tools.log_feedback._build_review_chart_svg_path", return_value=None), patch(
                "openai.OpenAI"
            ) as mocked_openai, patch("tools.log_feedback.write_ai_error_log") as _error_log_mock:
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 1,
                        "AI_POST_REVIEW_MAX_CONSECUTIVE_FAILURES": 3,
                        "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True,
                        "AI_ADVICE_CLI_COMMAND": "dummy-cli",
                        "AI_POST_REVIEW_API_FALLBACK_ENABLED": True,
                    },
                )()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_called_once()
            mocked_openai.assert_not_called()
            self.assertEqual(stats["created"], 0)
            self.assertEqual(stats["request_failed"], 1)
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(rows, [])

    def test_sync_ai_post_reviews_uses_api_fallback_only_with_explicit_api_permission(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_api_fallback",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_api_fallback", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            api_review = {
                "user_verdict": "useful_wait",
                "usefulness_1to5": "4",
                "would_trade": "conditional",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "good",
                "tf_4h_eval": "good",
                "tf_1h_eval": "mixed",
                "tf_15m_eval": "mixed",
                "review_source": "ai",
                "review_model": "gpt-4o",
                "review_image_mode": "api_numeric_fallback",
                "review_variant": "ai_post_review_v2",
                "review_action_class": "watch",
                "review_priority": "medium",
                "next_action": "継続観測する",
                "memo": "API fallback",
            }
            api_response = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(api_review, ensure_ascii=False)))]
            )
            with patch("tools.log_feedback.run_cli_json", side_effect=RuntimeError("usage limit")) as mocked_cli, patch(
                "tools.log_feedback.load_config"
            ) as mocked_cfg, patch("tools.log_feedback._build_review_chart_svg_path", return_value=None), patch(
                "openai.OpenAI"
            ) as mocked_openai, patch("tools.log_feedback.write_ai_error_log") as _error_log_mock:
                mocked_openai.return_value.chat.completions.create.return_value = api_response
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 1,
                        "AI_POST_REVIEW_MAX_CONSECUTIVE_FAILURES": 3,
                        "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True,
                        "AI_ADVICE_CLI_COMMAND": "dummy-cli",
                        "AI_POST_REVIEW_API_FALLBACK_ENABLED": True,
                        "OPENAI_API_KEY": "sk-test",
                        "AI_API_USAGE_ALLOWED": True,
                    },
                )()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_called_once()
            mocked_openai.assert_called_once()
            self.assertEqual(stats["created"], 1)
            self.assertEqual(stats["request_failed"], 0)
            self.assertEqual(stats["resolved_cli_fallback"], 0)
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(rows[0]["review_image_mode"], "api_numeric_fallback")

    def test_sync_ai_post_reviews_treats_missing_notification_kind_as_main_for_notified_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "signal_tier"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_missing_kind",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_missing_kind", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            signal_path = base_dir / "logs" / "signals" / "sig_missing_kind.json"
            signal_path.write_text('{"signal_id":"sig_missing_kind","summary_subject":"subject"}', encoding="utf-8")

            ai_result = {
                "user_verdict": "useful_entry",
                "usefulness_1to5": "4",
                "would_trade": "yes",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "good",
                "tf_4h_eval": "good",
                "tf_1h_eval": "good",
                "tf_15m_eval": "mixed",
                "memo": "ok",
            }
            with patch("tools.log_feedback.run_cli_json", return_value=ai_result) as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 2,
                        "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True,
                        "AI_ADVICE_CLI_COMMAND": "dummy-cli",
                    },
                )()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_called_once()
            self.assertEqual(stats["created"], 1)
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(rows[0]["review_model"], "gpt-5.3-codex")

    def test_sync_ai_post_reviews_resolves_legacy_cli_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            (base_dir / "logs" / "signals").mkdir(parents=True, exist_ok=True)
            (base_dir / "tools").mkdir(parents=True, exist_ok=True)
            (base_dir / "tools" / "codex_cli_wrapper.py").write_text("# stub\n", encoding="utf-8")

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "timestamp_jst", "was_notified", "summary_subject", "prelabel_primary_reason", "notification_kind", "signal_tier"])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_legacy_path",
                        "timestamp_jst": "2026-04-10T03:05:00+09:00",
                        "was_notified": "true",
                        "summary_subject": "subject",
                        "prelabel_primary_reason": "balanced_location",
                        "notification_kind": "main",
                        "signal_tier": "normal",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status", "outcome"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_legacy_path", "evaluation_status": "complete", "outcome": "win"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            signal_path = base_dir / "logs" / "signals" / "sig_legacy_path.json"
            signal_path.write_text('{"signal_id":"sig_legacy_path","summary_subject":"subject"}', encoding="utf-8")

            ai_result = {
                "user_verdict": "useful_wait",
                "usefulness_1to5": "4",
                "would_trade": "conditional",
                "actual_move_driver": "technical",
                "misleading_entry_like_wording": "no",
                "sl_eval": "good",
                "tp_eval": "good",
                "tf_4h_eval": "good",
                "tf_1h_eval": "good",
                "tf_15m_eval": "mixed",
                "memo": "ok",
            }
            legacy_path = "/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/tools/codex_cli_wrapper.py"
            with patch("tools.log_feedback.run_cli_json", return_value=ai_result) as mocked_cli, patch("tools.log_feedback.load_config") as mocked_cfg:
                mocked_cfg.return_value = type(
                    "Cfg",
                    (),
                    {
                        "AI_POST_REVIEW_DAILY_MAX": 2,
                        "AI_POST_REVIEW_PRIORITY_MAIN_ONLY": True,
                        "AI_ADVICE_CLI_COMMAND": legacy_path,
                        "OPENAI_ADVICE_MODEL": "gpt-4o",
                    },
                )()
                _, stats = sync_ai_post_reviews(
                    base_dir=base_dir,
                    outcomes_path=outcomes_path,
                    reviews_path=reviews_path,
                    trades_path=trades_path,
                    max_new_reviews=None,
                )

            mocked_cli.assert_called_once()
            self.assertEqual(mocked_cli.call_args.kwargs["command"], str(base_dir / "tools" / "codex_cli_wrapper.py"))
            self.assertEqual(stats["resolved_cli_fallback"], 1)
            self.assertEqual(stats["created"], 1)

    def test_main_sync_ai_post_reviews_accepts_missing_max_new_ai_reviews(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "sync-ai-post-reviews"]), patch(
            "tools.log_feedback.sync_ai_post_reviews"
        ) as mocked_sync:
            mocked_sync.return_value = (Path("/tmp/user_reviews.csv"), {"created": 0})

            main()

        mocked_sync.assert_called_once()
        self.assertIsNone(mocked_sync.call_args.kwargs["max_new_reviews"])

    def test_backfill_ai_post_review_v2_updates_existing_rows_and_snapshots(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            snapshot_dir = base_dir / "logs" / "review" / "ai_post_reviews"
            snapshot_dir.mkdir(parents=True, exist_ok=True)

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_backfill",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "subject": "subject",
                        "auto_eval_summary": "summary",
                        "user_verdict": "too_early",
                        "usefulness_1to5": "2",
                        "would_trade": "no",
                        "actual_move_driver": "technical",
                        "misleading_entry_like_wording": "no",
                        "logic_validated": "true",
                        "sl_eval": "good",
                        "tp_eval": "good",
                        "tf_4h_eval": "good",
                        "tf_1h_eval": "good",
                        "tf_15m_eval": "poor",
                        "review_source": "ai",
                        "review_model": "gpt-test",
                        "review_image_mode": "price_map_svg",
                        "review_variant": "ai_post_review_v1",
                        "review_action_class": "",
                        "review_priority": "",
                        "next_action": "",
                        "memo": "memo",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-04-10T00:00:00Z",
                    }
                )

            (snapshot_dir / "sig_backfill.json").write_text(
                json_text := """{
  "signal_id": "sig_backfill",
  "review": {
    "signal_id": "sig_backfill",
    "timestamp_jst": "2026-04-10T01:05:00+09:00",
    "subject": "subject",
    "auto_eval_summary": "summary",
    "user_verdict": "too_early",
    "usefulness_1to5": "2",
    "would_trade": "no",
    "actual_move_driver": "technical",
    "misleading_entry_like_wording": "no",
    "logic_validated": "true",
    "sl_eval": "good",
    "tp_eval": "good",
    "tf_4h_eval": "good",
    "tf_1h_eval": "good",
    "tf_15m_eval": "poor",
    "review_source": "ai",
    "review_model": "gpt-test",
    "review_image_mode": "price_map_svg",
    "review_variant": "ai_post_review_v1",
    "review_action_class": "",
    "review_priority": "",
    "next_action": "",
    "memo": "memo",
    "review_status": "done",
    "reviewed_at_utc": "2026-04-10T00:00:00Z"
  }
}""",
                encoding="utf-8",
            )

            result = backfill_ai_post_review_v2(base_dir=base_dir, review_note_path=base_dir / "review.md", reviews_path=reviews_path)

            self.assertEqual(result["updated_reviews"], 1)
            self.assertEqual(result["updated_snapshots"], 1)
            rows = _load_csv_rows(reviews_path)
            self.assertEqual(rows[0]["review_action_class"], "tune_entry")
            self.assertEqual(rows[0]["review_priority"], "medium")
            self.assertEqual(rows[0]["next_action"], "早すぎる通知を抑えるため発火条件を一段遅らせる")
            self.assertEqual(rows[0]["review_variant"], "ai_post_review_v2")
            snapshot_text = (snapshot_dir / "sig_backfill.json").read_text(encoding="utf-8")
            self.assertIn('"review_action_class": "tune_entry"', snapshot_text)
            self.assertIn('"review_variant": "ai_post_review_v2"', snapshot_text)

    def test_build_feedback_report_includes_ai_health_warning(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            shadow_path = base_dir / "logs" / "csv" / "shadow_log.csv"
            shadow_path.parent.mkdir(parents=True, exist_ok=True)
            fieldnames = [
                "signal_id",
                "timestamp_jst",
                "evaluation_status",
                "data_quality_flag",
                "signal_based_MFE_24h",
                "signal_based_MAE_24h",
                "outcome",
                "direction_outcome",
                "entry_outcome",
                "wait_outcome",
                "skip_outcome",
                "tp1_hit_first",
                "was_notified",
                "notify_reason",
                "prelabel",
                "primary_setup_status",
                "primary_setup_reason",
                "signal_tier",
            ]
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_health",
                        "timestamp_jst": "2026-04-10T01:05:00+09:00",
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.0",
                        "signal_based_MAE_24h": "0.5",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "ready",
                        "primary_setup_reason": "balanced_location",
                        "signal_tier": "normal",
                    }
                )

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                ai_health_summary={
                    "status": "stalled",
                    "eligible": 5,
                    "backlog_pending": 3,
                    "ai_reviewed": 2,
                    "human_override": 0,
                    "created": 0,
                    "reused": 0,
                    "request_failed": 3,
                    "daily_cap": 4,
                    "last_ai_review_at": "2026-04-15T18:36:50Z",
                    "last_ai_error_at": "2026-04-18T18:35:03Z",
                    "resolved_cli_fallback": 1,
                },
            )

            self.assertIn("AI事後評価は停止中です。候補残 3 件", report)
            self.assertIn("### AI事後評価 health", report)
            self.assertIn("状態: 停止中", report)
            self.assertIn("created=0 / reused=0 / request_failed=3 / daily_cap=4", report)
            self.assertIn("旧CLIパスを現行repoへ自動補正 1 件", report)

    def test_load_latest_ai_sync_stats_reads_last_runtime_block(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            runtime_path = base_dir / "logs" / "runtime" / "ai_post_reviews.out"
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.write_text(
                "\n".join(
                    [
                        "reviews_path=/tmp/old.csv",
                        "eligible=150",
                        "created=1",
                        "request_failed=41",
                        "backlog_pending=41",
                        "reviews_path=/tmp/latest.csv",
                        "eligible=161",
                        "reused=0",
                        "created=4",
                        "request_failed=0",
                        "resolved_cli_fallback=0",
                        "daily_cap=4",
                        "backlog_pending=38",
                    ]
                ),
                encoding="utf-8",
            )

            stats = _load_latest_ai_sync_stats(base_dir)

            self.assertEqual(stats["eligible"], 161)
            self.assertEqual(stats["created"], 4)
            self.assertEqual(stats["request_failed"], 0)
            self.assertEqual(stats["backlog_pending"], 38)

    def test_ai_review_health_summary_uses_runtime_stats_when_daily_sync_is_noop(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            runtime_path = base_dir / "logs" / "runtime" / "ai_post_reviews.out"
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.write_text(
                "\n".join(
                    [
                        "reviews_path=/tmp/latest.csv",
                        "eligible=161",
                        "reused=0",
                        "created=4",
                        "request_failed=0",
                        "resolved_cli_fallback=0",
                        "daily_cap=4",
                        "backlog_pending=38",
                    ]
                ),
                encoding="utf-8",
            )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_1", "evaluation_status": "complete"})

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "was_notified", "notification_kind"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_1", "was_notified": "true", "notification_kind": "main"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            summary = _ai_review_health_summary(
                base_dir=base_dir,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
                trades_path=trades_path,
                sync_stats={"created": 0, "reused": 0, "request_failed": 0, "resolved_cli_fallback": 0, "daily_cap": 0},
            )

            self.assertEqual(summary["eligible"], 1)
            self.assertEqual(summary["backlog_pending"], 1)
            self.assertEqual(summary["created"], 4)
            self.assertEqual(summary["request_failed"], 0)
            self.assertEqual(summary["daily_cap"], 4)

    def test_merge_review_sources_prefers_csv_review_rows_over_stale_state(self) -> None:
        merged = _merge_review_sources(
            state_rows=[
                {
                    "signal_id": "sig_1",
                    "review_status": "pending",
                    "review_source": "",
                    "memo": "",
                }
            ],
            note_rows=[],
            review_rows=[
                {
                    "signal_id": "sig_1",
                    "review_status": "done",
                    "review_source": "ai",
                    "memo": "from csv",
                }
            ],
        )

        self.assertEqual(merged["sig_1"]["review_status"], "done")
        self.assertEqual(merged["sig_1"]["review_source"], "ai")
        self.assertEqual(merged["sig_1"]["memo"], "from csv")

    def test_build_shadow_log_sets_logic_validated(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
                    "current_price",
                    "bias",
                    "market_regime",
                    "phase",
                    "long_score",
                    "short_score",
                    "score_gap",
                    "confidence",
                    "top_positive_factors",
                    "top_negative_factors",
                    "prelabel",
                    "prelabel_primary_reason",
                    "location_risk",
                    "primary_setup_status",
                    "invalid_reason",
                    "signal_tier",
                    "ai_decision",
                    "ai_confidence",
                    "was_notified",
                    "notify_reason_codes",
                    "suppress_reason_codes",
                    "data_quality_flag",
                    "data_missing_fields",
                    "risk_flags",
                    "warning_flags",
                    "no_trade_flags",
                    "summary_subject",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_logic",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "current_price": "100",
                        "bias": "long",
                        "market_regime": "uptrend",
                        "phase": "pullback",
                        "long_score": "78",
                        "short_score": "52",
                        "score_gap": "26",
                        "confidence": "80",
                        "top_positive_factors": '["regime_uptrend"]',
                        "top_negative_factors": '["ask_wall_distance"]',
                        "prelabel": "ENTRY_OK",
                        "prelabel_primary_reason": "ask_wall_distance",
                        "location_risk": "12.0",
                        "primary_setup_status": "ready",
                        "invalid_reason": "",
                        "signal_tier": "strong_machine",
                        "ai_decision": "LONG",
                        "ai_confidence": "0.8",
                        "was_notified": "true",
                        "notify_reason_codes": '["status_upgraded"]',
                        "suppress_reason_codes": "[]",
                        "data_quality_flag": "ok",
                        "data_missing_fields": "[]",
                        "risk_flags": "ask_wall_close",
                        "warning_flags": "",
                        "no_trade_flags": "",
                        "summary_subject": "subject",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
                    "signal_based_MFE_4h",
                    "signal_based_MAE_4h",
                    "signal_based_MFE_12h",
                    "signal_based_MAE_12h",
                    "signal_based_MFE_24h",
                    "signal_based_MAE_24h",
                    "entry_ready_based_MFE_4h",
                    "entry_ready_based_MAE_4h",
                    "entry_ready_based_MFE_12h",
                    "entry_ready_based_MAE_12h",
                    "entry_ready_based_MFE_24h",
                    "entry_ready_based_MAE_24h",
                    "tp1_hit_first",
                    "outcome",
                    "direction_outcome",
                    "entry_outcome",
                    "wait_outcome",
                    "skip_outcome",
                    "support_hold_result",
                    "resistance_hold_result",
                    "evaluation_status",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_logic",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "signal_based_MFE_4h": "1.2",
                        "signal_based_MAE_4h": "0.2",
                        "signal_based_MFE_12h": "1.5",
                        "signal_based_MAE_12h": "0.4",
                        "signal_based_MFE_24h": "1.6",
                        "signal_based_MAE_24h": "0.5",
                        "entry_ready_based_MFE_4h": "1.2",
                        "entry_ready_based_MAE_4h": "0.2",
                        "entry_ready_based_MFE_12h": "1.5",
                        "entry_ready_based_MAE_12h": "0.4",
                        "entry_ready_based_MFE_24h": "1.6",
                        "entry_ready_based_MAE_24h": "0.5",
                        "tp1_hit_first": "true",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "held",
                        "resistance_hold_result": "untouched",
                        "evaluation_status": "complete",
                    }
                )

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
                    "subject",
                    "auto_eval_summary",
                    "user_verdict",
                    "usefulness_1to5",
                    "would_trade",
                    "actual_move_driver",
                    "logic_validated",
                    "memo",
                    "review_status",
                    "reviewed_at_utc",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_logic",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "subject": "subject",
                        "auto_eval_summary": "summary",
                        "user_verdict": "useful_entry",
                        "usefulness_1to5": "5",
                        "would_trade": "yes",
                        "actual_move_driver": "technical",
                        "logic_validated": "",
                        "memo": "ok",
                        "review_status": "done",
                        "reviewed_at_utc": "2026-03-12T00:00:00Z",
                    }
                )

            shadow_path = build_shadow_log(
                base_dir=base_dir,
                trades_path=trades_path,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
            )
            rows = _load_csv_rows(shadow_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["logic_validated"], "true")
            self.assertEqual(rows[0]["risk_percent_applied"], "")
            self.assertEqual(rows[0]["phase1_active"], "")

    def test_build_shadow_log_reconciles_entry_ok_invalid_prelabel(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=[
                    "signal_id",
                    "timestamp_jst",
                    "current_price",
                    "bias",
                    "market_regime",
                    "phase",
                    "long_score",
                    "short_score",
                    "score_gap",
                    "confidence",
                    "top_positive_factors",
                    "top_negative_factors",
                    "prelabel",
                    "prelabel_primary_reason",
                    "location_risk",
                    "primary_setup_side",
                    "primary_setup_status",
                    "primary_setup_reason",
                    "invalid_reason",
                    "signal_tier",
                    "ai_decision",
                    "ai_confidence",
                    "was_notified",
                    "notify_reason_codes",
                    "suppress_reason_codes",
                    "data_quality_flag",
                    "data_missing_fields",
                    "risk_flags",
                    "warning_flags",
                    "no_trade_flags",
                    "summary_subject",
                    "confidence_direction_shadow",
                    "confidence_execution_shadow",
                    "confidence_wait_shadow",
                ])
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "sig_reconcile",
                        "timestamp_jst": "2026-03-11T09:05:00+09:00",
                        "current_price": "100",
                        "bias": "long",
                        "market_regime": "uptrend",
                        "phase": "pullback",
                        "long_score": "78",
                        "short_score": "52",
                        "score_gap": "26",
                        "confidence": "80",
                        "top_positive_factors": '["regime_uptrend"]',
                        "top_negative_factors": '["rr_long_penalty"]',
                        "prelabel": "ENTRY_OK",
                        "prelabel_primary_reason": "balanced_location",
                        "location_risk": "12.0",
                        "primary_setup_side": "long",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "invalid_reason": "RR不足",
                        "signal_tier": "normal",
                        "ai_decision": "",
                        "ai_confidence": "",
                        "was_notified": "true",
                        "notify_reason_codes": '["status_upgraded"]',
                        "suppress_reason_codes": "[]",
                        "data_quality_flag": "ok",
                        "data_missing_fields": "[]",
                        "risk_flags": "sweep_incomplete",
                        "warning_flags": "",
                        "no_trade_flags": "RR_insufficient",
                        "summary_subject": "subject",
                        "confidence_direction_shadow": "80",
                        "confidence_execution_shadow": "18",
                        "confidence_wait_shadow": "72",
                    }
                )

            outcomes_path = logs_csv / "signal_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["signal_id", "evaluation_status"])
                writer.writeheader()
                writer.writerow({"signal_id": "sig_reconcile", "evaluation_status": "pending"})

            reviews_path = logs_csv / "user_reviews.csv"
            with reviews_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=USER_REVIEW_HEADER)
                writer.writeheader()

            shadow_path = build_shadow_log(
                base_dir=base_dir,
                trades_path=trades_path,
                outcomes_path=outcomes_path,
                reviews_path=reviews_path,
            )
            rows = _load_csv_rows(shadow_path)
            self.assertEqual(rows[0]["prelabel"], "RISKY_ENTRY")
            self.assertEqual(rows[0]["phase1_observation_gate"], "pass")

    def test_build_observation_paper_orders_backfills_phase1a_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            trades_path = logs_csv / "trades.csv"
            with trades_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "current_price",
                        "primary_setup_side",
                        "primary_entry_mid",
                        "primary_stop_loss",
                        "shadow_tp1_price",
                        "shadow_tp2_price",
                        "rr_estimate",
                        "prelabel",
                        "primary_setup_status",
                        "primary_setup_reason",
                        "phase1_observation_gate",
                        "phase1_observation_type",
                        "phase1_observation_reasons",
                        "confidence_direction_shadow",
                        "confidence_execution_shadow",
                        "confidence_wait_shadow",
                        "trade_execution_gate",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "obs_backfill",
                        "timestamp_jst": "2026-04-22T10:00:00+09:00",
                        "current_price": "70000",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "69900",
                        "primary_stop_loss": "69500",
                        "shadow_tp1_price": "70420",
                        "shadow_tp2_price": "70860",
                        "rr_estimate": "1.3",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "phase1_observation_reasons": "[\"setup_watch_learning\"]",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "70",
                        "trade_execution_gate": "blocked",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "blocked",
                        "timestamp_jst": "2026-04-22T11:00:00+09:00",
                        "phase1_observation_gate": "blocked",
                    }
                )

            path = build_observation_paper_orders(base_dir=base_dir, trades_path=trades_path)
            rows = _load_csv_rows(path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "obs_backfill")
            self.assertEqual(rows[0]["observation_phase"], "phase1A")
            self.assertEqual(rows[0]["observation_type"], "setup_watch_learning")
            self.assertEqual(rows[0]["observation_status"], "observing")

    def test_build_feedback_report_starts_with_human_summary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)

            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "evaluation_status",
                        "data_quality_flag",
                        "signal_based_MFE_24h",
                        "signal_based_MAE_24h",
                        "entry_ready_based_MFE_24h",
                        "entry_ready_based_MAE_24h",
                        "outcome",
                        "direction_outcome",
                        "entry_outcome",
                        "wait_outcome",
                        "skip_outcome",
                        "support_hold_result",
                        "resistance_hold_result",
                        "tp1_hit_first",
                        "was_notified",
                        "user_verdict",
                        "usefulness_1to5",
                        "actual_move_driver",
                        "prelabel",
                        "primary_setup_status",
                        "signal_tier",
                        "bias",
                        "regime",
                        "risk_flags",
                        "phase1_active",
                        "max_size_capped",
                    ],
                )
                writer.writeheader()
                timestamp_jst = (datetime.now(timezone(timedelta(hours=9))) - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                )
                writer.writerow(
                    {
                        "signal_id": "sig_report",
                        "timestamp_jst": timestamp_jst,
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.2",
                        "signal_based_MAE_24h": "0.4",
                        "entry_ready_based_MFE_24h": "1.0",
                        "entry_ready_based_MAE_24h": "0.3",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "not_applicable",
                        "wait_outcome": "wait_was_good",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "untouched",
                        "resistance_hold_result": "held",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "user_verdict": "useful_wait",
                        "usefulness_1to5": "4",
                        "actual_move_driver": "technical",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "ready",
                        "signal_tier": "normal",
                        "bias": "short",
                        "regime": "downtrend",
                        "risk_flags": "",
                        "phase1_active": "true",
                        "max_size_capped": "false",
                        "outcome": "win",
                    }
                )

            observation_orders_path = logs_csv / "observation_paper_orders.csv"
            with observation_orders_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=OBSERVATION_PAPER_ORDER_HEADER,
                )
                writer.writeheader()
                for signal_id in ["entry_rr_0", "entry_rr_1", "entry_rr_2", "risky_rr_0"]:
                    writer.writerow(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": timestamp_jst,
                            "observation_phase": "phase1A",
                            "observation_type": "direction_rr_learning",
                            "observation_status": "observing",
                        }
                    )

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                observation_paper_orders_path=observation_orders_path,
            )

            self.assertIn("## 1. まず結論", report)
            self.assertIn("Phase 1 判定では ready=1 件、phase1_active=true=1 件です。", report)
            self.assertIn("判定: Phase 1 の本有効確認を進めてよい", report)
            self.assertIn("## 3. Phase 1 判定サマリー", report)
            self.assertIn("## 4. AI事後評価サマリー", report)
            self.assertIn("待つ判断に使えた", report)
            self.assertIn("平均の役立ち度", report)
            self.assertIn("`primary_setup_status=ready` 件数: 1", report)
            self.assertIn("`phase1_active=true` 件数: 1", report)

    def test_build_feedback_report_keeps_phase1_summary_without_reviews(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"

            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "signal_id",
                        "timestamp_jst",
                        "evaluation_status",
                        "data_quality_flag",
                        "signal_based_MFE_24h",
                        "signal_based_MAE_24h",
                        "entry_ready_based_MFE_24h",
                        "entry_ready_based_MAE_24h",
                        "outcome",
                        "direction_outcome",
                        "entry_outcome",
                        "wait_outcome",
                        "skip_outcome",
                        "support_hold_result",
                        "resistance_hold_result",
                        "tp1_hit_first",
                        "was_notified",
                        "user_verdict",
                        "usefulness_1to5",
                        "actual_move_driver",
                        "prelabel",
                        "primary_setup_status",
                        "signal_tier",
                        "bias",
                        "regime",
                        "risk_flags",
                        "phase1_active",
                        "max_size_capped",
                    ],
                )
                writer.writeheader()
                timestamp_jst = (datetime.now(timezone(timedelta(hours=9))) - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                )
                writer.writerow(
                    {
                        "signal_id": "sig_phase1_only",
                        "timestamp_jst": timestamp_jst,
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.2",
                        "signal_based_MAE_24h": "0.4",
                        "entry_ready_based_MFE_24h": "1.0",
                        "entry_ready_based_MAE_24h": "0.3",
                        "outcome": "expired",
                        "direction_outcome": "correct",
                        "entry_outcome": "good_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "support_hold_result": "untouched",
                        "resistance_hold_result": "held",
                        "tp1_hit_first": "false",
                        "was_notified": "true",
                        "user_verdict": "",
                        "usefulness_1to5": "",
                        "actual_move_driver": "",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "ready",
                        "signal_tier": "normal",
                        "bias": "long",
                        "regime": "range",
                        "risk_flags": "",
                        "phase1_active": "true",
                        "max_size_capped": "true",
                    }
                )

            report = build_feedback_report(base_dir=base_dir, period="weekly", shadow_path=shadow_path)

            self.assertIn("## 3. Phase 1 判定サマリー", report)
            self.assertIn("判定: Phase 1 の本有効確認を進めてよい", report)
            self.assertIn("直近の観測対象:", report)
            self.assertIn("sig_phase1_only / setup=ready / phase1_active=true / outcome=expired", report)
            self.assertIn("TP1 到達率: 0.0%", report)
            self.assertIn("`tp1_hit_first=false` 率: 100.0%", report)
            self.assertIn("`expired` 率: 100.0%", report)
            self.assertIn("`max_size_capped` 発生率: 100.0%", report)
            self.assertIn("## 4. AI事後評価サマリー", report)
            self.assertIn("完了レビューはまだありません", report)

    def test_build_feedback_report_shows_entry_ok_rr_and_ready_blockers(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)

            fieldnames = [
                "signal_id",
                "timestamp_jst",
                "evaluation_status",
                "data_quality_flag",
                "signal_based_MFE_24h",
                "signal_based_MAE_24h",
                "outcome",
                "direction_outcome",
                "entry_outcome",
                "wait_outcome",
                "skip_outcome",
                "tp1_hit_first",
                "was_notified",
                "notify_reason",
                "prelabel",
                "primary_setup_status",
                "primary_setup_reason",
                "primary_setup_side",
                "primary_entry_mid",
                "tp1_price",
                "shadow_tp1_price",
                "shadow_exit_rule_version",
                "invalid_reason",
                "risk_flags",
                "confidence_direction_shadow",
                "confidence_execution_shadow",
                "confidence_wait_shadow",
                "phase1_active",
                "trade_execution_gate",
                "trade_execution_blockers",
                "phase1_observation_gate",
                "phase1_observation_type",
                "phase1_observation_reasons",
                "suppress_reason",
                "paper_order_status",
                "tp_eval",
            ]
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                timestamp_jst = (datetime.now(timezone(timedelta(hours=9))) - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                )
                for idx in range(3):
                    writer.writerow(
                        {
                            "signal_id": f"entry_rr_{idx}",
                            "timestamp_jst": timestamp_jst,
                            "evaluation_status": "complete",
                            "data_quality_flag": "ok",
                            "signal_based_MFE_24h": "1.0",
                            "signal_based_MAE_24h": "0.5",
                            "outcome": "win",
                            "direction_outcome": "correct",
                            "entry_outcome": "poor_entry",
                            "wait_outcome": "not_applicable",
                            "skip_outcome": "not_applicable",
                            "tp1_hit_first": "true",
                            "was_notified": "true",
                            "prelabel": "ENTRY_OK",
                            "primary_setup_status": "invalid",
                            "primary_setup_reason": "rr_below_min",
                            "primary_setup_side": "long",
                            "primary_entry_mid": "70000",
                            "tp1_price": "70500",
                            "shadow_tp1_price": "70650",
                            "shadow_exit_rule_version": "phase1_v1_shadow",
                            "invalid_reason": "RR不足",
                            "risk_flags": "lower_liquidity_close,sweep_incomplete",
                            "confidence_direction_shadow": "80",
                            "confidence_execution_shadow": "10",
                            "confidence_wait_shadow": "70",
                            "phase1_active": "false",
                        "trade_execution_gate": "blocked",
                        "trade_execution_blockers": "[\"rr_below_min\", \"execution_shadow_too_low\"]",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "direction_rr_learning",
                        "phase1_observation_reasons": "[\"direction_rr_learning\"]",
                        "suppress_reason": "rr_sweep_recheck_wait,attention_rr_sweep_recheck_wait",
                        "paper_order_status": "",
                        "tp_eval": "too_close",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "risky_rr_0",
                        "timestamp_jst": timestamp_jst,
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "2.4",
                        "signal_based_MAE_24h": "0.8",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "poor_entry",
                        "wait_outcome": "not_applicable",
                        "skip_outcome": "not_applicable",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "notify_reason": "[\"attention_gap_crossed\", \"attention_score_crossed\"]",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "70100",
                        "tp1_price": "70600",
                        "shadow_tp1_price": "70750",
                        "shadow_exit_rule_version": "phase1_v1_shadow",
                        "invalid_reason": "RR不足",
                        "risk_flags": "orderbook_ask_heavy,sweep_incomplete",
                        "confidence_direction_shadow": "75",
                        "confidence_execution_shadow": "26",
                        "confidence_wait_shadow": "70.4",
                        "phase1_active": "false",
                        "trade_execution_gate": "blocked",
                        "trade_execution_blockers": "[\"rr_below_min\"]",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "direction_rr_learning",
                        "phase1_observation_reasons": "[\"direction_rr_learning\"]",
                        "suppress_reason": "rr_sweep_recheck_wait,attention_rr_sweep_recheck_wait",
                        "paper_order_status": "",
                        "tp_eval": "too_close",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "watch_sweep_0",
                        "timestamp_jst": timestamp_jst,
                        "evaluation_status": "complete",
                        "data_quality_flag": "ok",
                        "signal_based_MFE_24h": "1.8",
                        "signal_based_MAE_24h": "0.7",
                        "outcome": "win",
                        "direction_outcome": "correct",
                        "entry_outcome": "not_applicable",
                        "wait_outcome": "good_wait",
                        "skip_outcome": "not_applicable",
                        "tp1_hit_first": "true",
                        "was_notified": "true",
                        "notify_reason": "[\"attention_bias_changed\"]",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "70200",
                        "tp1_price": "70700",
                        "shadow_tp1_price": "70800",
                        "shadow_exit_rule_version": "phase1_v1_shadow",
                        "invalid_reason": "",
                        "risk_flags": "sweep_incomplete",
                        "confidence_direction_shadow": "72",
                        "confidence_execution_shadow": "21",
                        "confidence_wait_shadow": "72",
                        "phase1_active": "false",
                        "trade_execution_gate": "blocked",
                        "trade_execution_blockers": "[\"phase1_inactive\", \"setup_not_ready\"]",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "phase1_observation_reasons": "[\"setup_watch_learning\"]",
                        "suppress_reason": "rr_sweep_recheck_wait",
                        "paper_order_status": "",
                        "tp_eval": "too_close",
                    }
                )
            (signals_dir / "risky_rr_0.json").write_text(
                json.dumps(
                    {
                        "signal_id": "risky_rr_0",
                        "primary_setup_side": "long",
                        "bias": "long",
                        "current_price": 75748.9,
                        "atr_15m_value": 213.1,
                        "confidence": 58,
                        "atr_ratio": 0.94,
                        "funding_rate_pct": 0.0043,
                        "volume_ratio": 4.07,
                        "trigger_volume_ratio_threshold": 1.15,
                        "breakout_up": False,
                        "warning_flags": [],
                        "support_zones_all": [
                            {"low": 74926.6, "high": 75002.6},
                            {"low": 74720.7, "high": 74885.4},
                        ],
                        "resistance_zones_all": [
                            {"low": 75962.0, "high": 76038.0},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (signals_dir / "watch_sweep_0.json").write_text(
                json.dumps(
                    {
                        "signal_id": "watch_sweep_0",
                        "primary_setup_side": "long",
                        "bias": "long",
                        "current_price": 75810.0,
                        "atr_15m_value": 210.0,
                        "confidence": 57,
                        "atr_ratio": 0.92,
                        "funding_rate_pct": 0.0041,
                        "volume_ratio": 3.2,
                        "trigger_volume_ratio_threshold": 1.15,
                        "breakout_up": False,
                        "warning_flags": [],
                        "support_zones_all": [
                            {"low": 75010.0, "high": 75120.0},
                        ],
                        "resistance_zones_all": [
                            {"low": 75980.0, "high": 76060.0},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            observation_orders_path = logs_csv / "observation_paper_orders.csv"
            with observation_orders_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=OBSERVATION_PAPER_ORDER_HEADER)
                writer.writeheader()
                for signal_id in ["entry_rr_0", "entry_rr_1", "entry_rr_2", "risky_rr_0", "watch_sweep_0"]:
                    writer.writerow(
                        {
                            "signal_id": signal_id,
                            "timestamp_jst": timestamp_jst,
                            "observation_phase": "phase1A",
                            "observation_type": "setup_watch_learning" if signal_id == "watch_sweep_0" else "direction_rr_learning",
                            "observation_status": "observing",
                        }
                    )

            report = build_feedback_report(
                base_dir=base_dir,
                period="weekly",
                shadow_path=shadow_path,
                observation_paper_orders_path=observation_orders_path,
            )

            self.assertIn("ready阻害理由: rr_below_min=4件", report)
            self.assertIn("rr_below_min 代表例: risky_rr_0(invalid/RISKY_ENTRY, dir=75, exec=26, wait=70, MFE24h=2.40, MAE24h=0.80, outcome=win)", report)
            self.assertIn("entry_rr_0(invalid/ENTRY_OK, dir=80, exec=10, wait=70, MFE24h=1.00, MAE24h=0.50, outcome=win)", report)
            self.assertIn("ENTRY_OK + rr_below_min: 3件 / 平均 execution=10.0 / 平均 wait=70.0", report)
            self.assertIn("ENTRY_OK + rr_below_min の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件", report)
            self.assertIn(
                "position_risk候補: lower_liquidity_close + sweep_incomplete 同居時は ENTRY_OK から RISKY_ENTRY 寄せを検討",
                report,
            )
            self.assertIn("confidence候補: execution<=20 かつ wait>=60 の本通知上位扱いを抑制", report)
            self.assertIn("direction_execution_conflict の主な理由: rr_below_min=3件", report)
            self.assertIn("direction_execution_conflict の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件", report)
            self.assertIn("rr_sweep_recheck_wait: 4件", report)
            self.assertIn("attention_rr_sweep_recheck_wait: 4件", report)
            self.assertIn("suppress_reason の内訳: rr_sweep_recheck_wait=5件, attention_rr_sweep_recheck_wait=4件", report)
            self.assertIn("trade_execution_gate=blocked: 5件", report)
            self.assertIn("主なブロック理由: rr_below_min=4件, execution_shadow_too_low=3件, phase1_inactive=1件", report)
            self.assertIn("phase1_observation_gate=pass: 5件", report)
            self.assertIn("観測タイプ: direction_rr_learning=4件, setup_watch_learning=1件", report)
            self.assertIn("direction_rr_learning: 4件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=2.35", report)
            self.assertIn("setup_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=2.57", report)
            self.assertIn("observation_paper_orders observing: 5件", report)
            self.assertIn("setup_watch_learning の entry_zone_not_reached 率: 100.0%", report)
            self.assertIn("gate pass だが観測紙トレード未記録: 0件", report)
            self.assertIn("扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ", report)
            self.assertIn("RISKY_ENTRY + rr_below_min かつ execution>=20: 1件 / 平均 execution=26.0 / 平均 wait=70.4", report)
            self.assertIn("RISKY_ENTRY + rr_below_min の主な risk_flags: orderbook_ask_heavy=1件, sweep_incomplete=1件", report)
            self.assertIn("RR再調整候補: risky_rr_0(exec=26, dir=75, wait=70, MFE24h=2.40, MAE24h=0.80, outcome=win)", report)
            self.assertIn("現行RR再計算: risky_rr_0=>watch/entry_zone_not_reached/rr=2.40", report)
            self.assertIn("sweep_incomplete を含む RISKY_ENTRY + rr_below_min の通知済み履歴: 1件", report)
            self.assertIn("主な通知理由: attention_gap_crossed=1件, attention_score_crossed=1件", report)
            self.assertIn("代表例: risky_rr_0(attention_gap_crossed,attention_score_crossed, exec=26, wait=70)", report)
            self.assertIn("sweep_incomplete を含む watch 系通知済み履歴: 1件", report)
            self.assertIn("代表例: watch_sweep_0(attention_bias_changed, exec=21, wait=72)", report)
            self.assertIn("現行watch再計算: watch_sweep_0=>watch/entry_zone_not_reached/rr=2.40", report)
            self.assertIn("tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件", report)
            self.assertIn("### 改善アクション", report)
            self.assertIn("出口設計を調整=5件", report)
            self.assertIn("重要度: 高=5件", report)
            self.assertIn("TP1/TP2 を遠めにする候補を検証する", report)

    def test_build_current_setup_comparison_report_detects_status_changes(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "cmp_0",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                    }
                )
            (signals_dir / "cmp_0.json").write_text(
                json.dumps(
                    {
                        "signal_id": "cmp_0",
                        "primary_setup_side": "long",
                        "bias": "long",
                        "current_price": 75748.9,
                        "atr_15m_value": 213.1,
                        "confidence": 58,
                        "atr_ratio": 0.94,
                        "funding_rate_pct": 0.0043,
                        "volume_ratio": 4.07,
                        "trigger_volume_ratio_threshold": 1.15,
                        "breakout_up": False,
                        "warning_flags": [],
                        "support_zones_all": [
                            {"low": 74926.6, "high": 75002.6},
                            {"low": 74720.7, "high": 74885.4},
                        ],
                        "resistance_zones_all": [
                            {"low": 75962.0, "high": 76038.0},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report = build_current_setup_comparison_report(base_dir=base_dir, shadow_path=shadow_path, limit=5)

            self.assertIn("差分ありのうち通知済み: 1", report)
            self.assertIn("平均 execution_shadow: 0.0", report)
            self.assertIn("平均 wait_shadow: 0.0", report)
            self.assertIn("主な status 変化: invalid->watch=1件", report)
            self.assertIn("主な reason 変化: rr_below_min->entry_zone_not_reached=1件", report)
            self.assertIn("## status別集計", report)
            self.assertIn("- invalid->watch: 1件 / 平均 execution=0.0 / 平均 wait=0.0", report)
            self.assertIn(
                "cmp_0: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=2.40 / prelabel=RISKY_ENTRY / notified=yes",
                report,
            )

    def test_build_current_setup_comparison_report_supports_filters(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "cmp_keep",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                        "risk_flags": "sweep_incomplete",
                        "notify_reason": "[\"prelabel_improved\"]",
                        "confidence_execution_shadow": "21",
                        "confidence_wait_shadow": "72",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "cmp_drop",
                        "timestamp_jst": "2026-04-24T02:05:00+09:00",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "confidence_below_min",
                        "was_notified": "false",
                        "risk_flags": "ask_wall_close",
                        "notify_reason": "[\"status_upgraded\"]",
                        "confidence_execution_shadow": "11",
                        "confidence_wait_shadow": "90",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "cmp_old",
                        "timestamp_jst": "2026-04-23T23:55:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                        "risk_flags": "sweep_incomplete",
                        "notify_reason": "[\"status_upgraded\"]",
                        "confidence_execution_shadow": "19",
                        "confidence_wait_shadow": "61",
                    }
                )
            payload = {
                "primary_setup_side": "long",
                "bias": "long",
                "current_price": 75748.9,
                "atr_15m_value": 213.1,
                "confidence": 58,
                "atr_ratio": 0.94,
                "funding_rate_pct": 0.0043,
                "volume_ratio": 4.07,
                "trigger_volume_ratio_threshold": 1.15,
                "breakout_up": False,
                "warning_flags": [],
                "support_zones_all": [
                    {"low": 74926.6, "high": 75002.6},
                    {"low": 74720.7, "high": 74885.4},
                ],
                "resistance_zones_all": [
                    {"low": 75962.0, "high": 76038.0},
                ],
            }
            for signal_id in ("cmp_keep", "cmp_drop", "cmp_old"):
                (signals_dir / f"{signal_id}.json").write_text(
                    json.dumps({"signal_id": signal_id, **payload}, ensure_ascii=False),
                    encoding="utf-8",
                )

            report = build_current_setup_comparison_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                limit=5,
                only_notified=True,
                previous_reason="rr_below_min",
                current_reason="entry_zone_not_reached",
                prelabel="risky_entry",
                risk_flag="sweep_incomplete",
                date_from="2026-04-24",
                date_to="2026-04-24",
                status_transition="invalid->watch",
            )

            self.assertIn("- フィルタ: 通知済みのみ", report)
            self.assertIn("- フィルタ: 旧 reason=rr_below_min", report)
            self.assertIn("- フィルタ: 現行 reason=entry_zone_not_reached", report)
            self.assertIn("- フィルタ: prelabel=RISKY_ENTRY", report)
            self.assertIn("- フィルタ: risk_flag=sweep_incomplete", report)
            self.assertIn("- フィルタ: date_from=2026-04-24", report)
            self.assertIn("- フィルタ: date_to=2026-04-24", report)
            self.assertIn("- フィルタ: status_transition=invalid->watch", report)
            self.assertIn("現行 setup との差分あり: 1", report)
            self.assertIn("- 主な risk_flags: sweep_incomplete=1件", report)
            self.assertIn("- 主な通知理由: prelabel_improved=1件", report)
            self.assertIn("- invalid->watch: 1件 / 平均 execution=21.0 / 平均 wait=72.0", report)
            self.assertIn("cmp_keep: invalid/rr_below_min -> watch/entry_zone_not_reached", report)
            self.assertNotIn("cmp_drop", report)
            self.assertNotIn("cmp_old", report)

    def test_refresh_standard_setup_comparison_reports_generates_three_standard_reports(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            signals_dir = base_dir / "logs" / "signals"
            signals_dir.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "cmp_entry",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "prelabel": "RISKY_ENTRY",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "true",
                        "risk_flags": "sweep_incomplete,orderbook_ask_heavy",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "cmp_conf",
                        "timestamp_jst": "2026-04-24T04:05:00+09:00",
                        "prelabel": "SWEEP_WAIT",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "rr_below_min",
                        "was_notified": "false",
                        "risk_flags": "sweep_incomplete",
                        "confidence_execution_shadow": "11",
                        "confidence_wait_shadow": "100",
                    }
                )
            entry_payload = {
                "signal_id": "cmp_entry",
                "primary_setup_side": "long",
                "bias": "long",
                "current_price": 75748.9,
                "atr_15m_value": 213.1,
                "confidence": 58,
                "atr_ratio": 0.94,
                "funding_rate_pct": 0.0043,
                "volume_ratio": 4.07,
                "trigger_volume_ratio_threshold": 1.15,
                "breakout_up": False,
                "warning_flags": [],
                "support_zones_all": [
                    {"low": 74926.6, "high": 75002.6},
                    {"low": 74720.7, "high": 74885.4},
                ],
                "resistance_zones_all": [
                    {"low": 75962.0, "high": 76038.0},
                ],
            }
            confidence_payload = {
                "signal_id": "cmp_conf",
                "primary_setup_side": "long",
                "bias": "long",
                "current_price": 77740.8,
                "atr_15m_value": 100.0,
                "confidence": 17,
                "atr_ratio": 0.94,
                "funding_rate_pct": 0.0043,
                "volume_ratio": 1.2,
                "trigger_volume_ratio_threshold": 1.15,
                "breakout_up": False,
                "warning_flags": [],
                "support_zones_all": [
                    {"low": 77695.07, "high": 77793.93},
                ],
                "resistance_zones_all": [
                    {"low": 77765.27, "high": 77864.13},
                ],
            }
            (signals_dir / "cmp_entry.json").write_text(json.dumps(entry_payload, ensure_ascii=False), encoding="utf-8")
            (signals_dir / "cmp_conf.json").write_text(json.dumps(confidence_payload, ensure_ascii=False), encoding="utf-8")

            generated = refresh_standard_setup_comparison_reports(
                base_dir=base_dir,
                shadow_path=shadow_path,
                analysis_dir=base_dir / "analysis",
                date_from="2026-04-24",
                date_to="2026-04-24",
            )

            self.assertEqual(
                set(generated.keys()),
                {
                    "notified_rr_to_entry",
                    "notified_rr_to_entry_orderbook_ask_heavy",
                    "rr_to_confidence",
                },
            )
            self.assertIn("現行 setup との差分あり: 1", generated["notified_rr_to_entry"].read_text(encoding="utf-8"))
            self.assertIn("risk_flag=orderbook_ask_heavy", generated["notified_rr_to_entry_orderbook_ask_heavy"].read_text(encoding="utf-8"))
            self.assertIn("rr_below_min->confidence_below_min=1件", generated["rr_to_confidence"].read_text(encoding="utf-8"))

    def test_main_refresh_standard_setup_reports_accepts_optional_analysis_dir(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "refresh-standard-setup-reports", "--analysis-dir", "/tmp/analysis"]), patch(
            "tools.log_feedback.refresh_standard_setup_comparison_reports"
        ) as mocked_refresh:
            mocked_refresh.return_value = {"sample": Path("/tmp/analysis/sample.md")}

            main()

        mocked_refresh.assert_called_once()
        self.assertEqual(mocked_refresh.call_args.kwargs["analysis_dir"], Path("/tmp/analysis"))

    def test_build_operational_focus_report_summarizes_backlog_and_phase1_bias(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "backlog_1",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "prelabel": "SWEEP_WAIT",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "confidence_execution_shadow": "8",
                        "confidence_wait_shadow": "72",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "backlog_2",
                        "timestamp_jst": "2026-04-22T03:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "RISKY_ENTRY",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "",
                        "phase1_observation_reasons": "confidence_below_min,no_trade_candidate",
                        "confidence_execution_shadow": "14",
                        "confidence_wait_shadow": "90",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,orderbook_ask_heavy",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "backlog_3",
                        "timestamp_jst": "2026-04-22T02:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "invalid",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "",
                        "phase1_observation_reasons": "confidence_below_min",
                        "confidence_execution_shadow": "10",
                        "confidence_wait_shadow": "88",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "done_ai",
                        "timestamp_jst": "2026-04-24T04:05:00+09:00",
                        "was_notified": "true",
                        "evaluation_status": "complete",
                        "review_source": "ai",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "near_entry_zone_waiting_trigger",
                        "prelabel": "SWEEP_WAIT",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "setup_watch_learning",
                        "confidence_execution_shadow": "9",
                        "confidence_wait_shadow": "65",
                        "risk_flags": "sweep_incomplete",
                        "signal_tier": "normal",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "direction_1",
                        "timestamp_jst": "2026-04-24T05:05:00+09:00",
                        "was_notified": "false",
                        "evaluation_status": "complete",
                        "review_source": "",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "prelabel": "RISKY_ENTRY",
                        "phase1_observation_gate": "pass",
                        "phase1_observation_type": "direction_rr_learning",
                        "confidence_execution_shadow": "31",
                        "confidence_wait_shadow": "22",
                        "risk_flags": "ask_wall_close",
                        "signal_tier": "normal",
                    }
                )

            report = build_operational_focus_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-22",
                date_to="2026-04-24",
                limit=3,
            )

            self.assertIn("- 未処理 backlog 候補: 3件", report)
            self.assertIn("- 年齢分布:", report)
            self.assertIn("- phase1 観測タイプ: setup_watch_learning=1件", report)
            self.assertIn("- pass: 3件 / blocked: 2件", report)
            self.assertIn("- pass 内訳: setup_watch_learning=2件, direction_rr_learning=1件", report)
            self.assertIn("- 主な blocked 理由: confidence_below_min=2件, no_trade_candidate=1件", report)
            self.assertIn("- setup_watch_learning: 2件 / 平均 execution=8.5 / 平均 wait=68.5", report)
            self.assertIn("- direction_rr_learning: 1件 / 平均 execution=31.0 / 平均 wait=22.0", report)
            self.assertIn("## blocked 上位理由の内訳", report)
            self.assertIn("- confidence_below_min: 2件", report)
            self.assertIn("  - prelabel: RISKY_ENTRY=1件, SWEEP_WAIT=1件", report)
            self.assertIn("  - risk_flags: sweep_incomplete=2件, lower_liquidity_close=2件, orderbook_ask_heavy=1件", report)
            self.assertIn("## sweep+lower_liquidity の補助flag内訳", report)
            self.assertIn("- confidence_below_min: 2件 / 平均 execution=12.0 / 平均 wait=89.0", report)
            self.assertIn("  - 補助flag: orderbook_ask_heavy=1件, 補助flagなし=1件", report)
            self.assertIn("## 緩和候補の少数群", report)
            self.assertIn("- backlog_3: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=10.0 / wait=88.0", report)

    def test_main_build_operational_focus_report_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-operational-focus-report", "--output-md", "/tmp/focus.md"]), patch(
            "tools.log_feedback.build_operational_focus_report"
        ) as mocked_focus:
            mocked_focus.return_value = "# report\n"

            main()

        mocked_focus.assert_called_once()
        self.assertEqual(mocked_focus.call_args.kwargs["output_md"], Path("/tmp/focus.md"))

    def test_build_relaxation_candidates_report_lists_softer_confidence_candidates(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "soft_1",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_execution_shadow": "10",
                        "confidence_wait_shadow": "88",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "hard_1",
                        "timestamp_jst": "2026-04-24T02:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "RISKY_ENTRY",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,orderbook_ask_heavy",
                        "confidence_execution_shadow": "14",
                        "confidence_wait_shadow": "90",
                    }
                )

            report = build_relaxation_candidates_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-24",
                date_to="2026-04-24",
            )

            self.assertIn("- 候補件数: 1件", report)
            self.assertIn("- prelabel: SWEEP_WAIT=1件", report)
            self.assertIn("- phase1 reasons: confidence_below_min=1件", report)
            self.assertIn("- risk_flags: sweep_incomplete=1件, lower_liquidity_close=1件", report)
            self.assertIn("- soft_1: 2026-04-24 03:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=10.0 / wait=88.0", report)
            self.assertNotIn("hard_1", report)

    def test_build_phase1b_promotion_report_lists_limited_watch_candidates(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "promo_1",
                        "timestamp_jst": "2026-04-24T03:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "confidence_watch_learning",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_direction_shadow": "58",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "80",
                        "outcome": "win",
                        "tp1_hit_first": "true",
                        "signal_based_MFE_24h": "12",
                        "signal_based_MAE_24h": "4",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "blocked_1",
                        "timestamp_jst": "2026-04-24T02:05:00+09:00",
                        "phase1_observation_gate": "blocked",
                        "phase1_observation_type": "confidence_watch_learning",
                        "phase1_observation_reasons": "confidence_below_min",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,ask_wall_close",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "25",
                        "confidence_wait_shadow": "75",
                        "outcome": "win",
                        "tp1_hit_first": "true",
                        "signal_based_MFE_24h": "15",
                        "signal_based_MAE_24h": "5",
                    }
                )

            report = build_phase1b_promotion_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-24",
                date_to="2026-04-24",
            )

            self.assertIn("- 候補件数: 1件", report)
            self.assertIn("- prelabel: SWEEP_WAIT=1件", report)
            self.assertIn("- 勝率=100.0% / TP1先行=100.0% / 近似PF=3.00", report)
            self.assertIn("## Phase 1B-lite", report)
            self.assertIn("- lite 候補件数: 1件", report)
            self.assertIn("- 扱い: 実弾ではなく、正式 Phase 1B でもない。専用CSVでのみ追跡する", report)
            self.assertIn("- promo_1: 2026-04-24 03:05 / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=80.0", report)
            self.assertNotIn("blocked_1", report)

    def test_build_phase1b_lite_paper_orders_backfills_lite_only(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            output_path = logs_csv / "phase1b_lite_paper_orders.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "lite_1",
                        "timestamp_jst": "2026-05-17T10:00:00+09:00",
                        "primary_setup_side": "long",
                        "primary_entry_mid": "69900",
                        "primary_stop_loss": "69500",
                        "shadow_tp1_price": "70420",
                        "shadow_tp2_price": "70860",
                        "phase1_observation_type": "confidence_watch_learning",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "confidence_below_min",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "no_trade_flags": "",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "76.8",
                        "trade_execution_gate": "blocked",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "normal_obs_1",
                        "timestamp_jst": "2026-05-17T09:00:00+09:00",
                        "phase1_observation_type": "setup_watch_learning",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "prelabel": "SWEEP_WAIT",
                        "data_quality_flag": "ok",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close",
                        "confidence_direction_shadow": "60",
                        "confidence_execution_shadow": "22",
                        "confidence_wait_shadow": "76.8",
                    }
                )

            result_path = build_phase1b_lite_paper_orders(
                base_dir=base_dir,
                trades_path=shadow_path,
                output_path=output_path,
            )

            with result_path.open(newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(result_path, output_path)
            self.assertEqual(rows[0].keys(), set(PHASE1B_LITE_PAPER_ORDER_HEADER))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["signal_id"], "lite_1")
            self.assertEqual(rows[0]["lite_phase"], "phase1B-lite")
            self.assertEqual(rows[0]["lite_status"], "observing")
            self.assertEqual(rows[0]["lite_type"], "confidence_watch_sweep_lite")
            self.assertFalse((base_dir / "logs" / "csv" / "paper_orders.csv").exists())

    def test_build_failed_breakout_down_reversal_report_lists_reversal_failures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "20260429_100500",
                        "timestamp_jst": "2026-04-29T19:05:00+09:00",
                        "bias": "long",
                        "phase": "breakout",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "top_positive_factors": '[{"code":"ema_alignment_bullish","score":12},{"code":"breakout_up","score":10}]',
                        "direction_outcome": "wrong",
                        "entry_outcome": "poor_entry",
                        "signal_based_MFE_24h": "1.68",
                        "signal_based_MAE_24h": "12.27",
                        "risk_flags": "sweep_incomplete,lower_liquidity_close,long_reversal_risk",
                        "notify_reason": '["confidence_jump","prelabel_improved"]',
                        "long_score": "92",
                        "short_score": "50",
                        "score_gap": "42",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "other_case",
                        "timestamp_jst": "2026-04-29T18:05:00+09:00",
                        "bias": "long",
                        "phase": "breakout",
                        "prelabel": "ENTRY_OK",
                        "primary_setup_status": "watch",
                        "primary_setup_reason": "entry_zone_not_reached",
                        "top_positive_factors": '[{"code":"ema_alignment_bullish","score":12}]',
                        "direction_outcome": "wrong",
                        "entry_outcome": "poor_entry",
                        "signal_based_MFE_24h": "1.00",
                        "signal_based_MAE_24h": "9.00",
                    }
                )

            report = build_failed_breakout_down_reversal_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-29",
                date_to="2026-04-29",
            )

            self.assertIn("- 件数: 1件", report)
            self.assertIn("- risk_flags: sweep_incomplete=1件, lower_liquidity_close=1件, long_reversal_risk=1件", report)
            self.assertIn("20260429_100500", report)
            self.assertNotIn("other_case", report)

    def test_build_market_map_effectiveness_report_groups_flags(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "map_down_1",
                        "timestamp_jst": "2026-04-29T19:05:00+09:00",
                        "market_map_primary_state": "confirmed_down",
                        "market_map_flags": "failed_breakout_down_reversal,long_into_major_resistance",
                        "level_flip_state": "support_to_resistance_confirmed",
                        "failed_breakout_state": "down_reversal",
                        "trend_flip_state": "confirmed_down",
                        "direction_outcome": "wrong",
                        "outcome": "loss",
                        "signal_based_MFE_24h": "1.5",
                        "signal_based_MAE_24h": "12.0",
                    }
                )
                writer.writerow(
                    {
                        "signal_id": "plain_1",
                        "timestamp_jst": "2026-04-29T18:05:00+09:00",
                        "direction_outcome": "correct",
                        "outcome": "win",
                    }
                )

            report = build_market_map_effectiveness_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-04-29",
                date_to="2026-04-29",
            )

            self.assertIn("- market_map 記録あり: 1件", report)
            self.assertIn("failed_breakout_down_reversal=1件", report)
            self.assertIn("failed_breakout_down_reversal: 勝率=0.0%", report)
            self.assertIn("map_down_1", report)

    def test_build_market_map_readiness_report_waits_without_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "latest_without_map",
                        "timestamp_jst": "2026-05-13T04:05:00+09:00",
                        "summary_subject": "👀 [注意報] 上方向監視 【BTC:80,493】 [Ver02.5-v5] [CLI]",
                    }
                )

            report = build_market_map_readiness_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-05-13",
            )

            self.assertIn("- readiness: wait", report)
            self.assertIn("- market_map 記録あり: 0件", report)
            self.assertIn("subject_version=Ver02.5-v5", report)
            self.assertIn("market_map_primary_state", report)

    def test_build_market_map_readiness_report_passes_with_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            shadow_path = logs_csv / "shadow_log.csv"
            with shadow_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=SHADOW_HEADER)
                writer.writeheader()
                writer.writerow(
                    {
                        "signal_id": "map_ready",
                        "timestamp_jst": "2026-05-13T05:05:00+09:00",
                        "market_map_primary_state": "confirmed_down",
                        "market_map_flags": "support_to_resistance_flip,failed_breakout_down_reversal",
                    }
                )

            report = build_market_map_readiness_report(
                base_dir=base_dir,
                shadow_path=shadow_path,
                date_from="2026-05-13",
            )

            self.assertIn("- readiness: pass", report)
            self.assertIn("- market_map 記録あり: 1件", report)
            self.assertIn("confirmed_down=1件", report)
            self.assertIn("failed_breakout_down_reversal=1件", report)

    def test_main_build_relaxation_candidates_report_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-relaxation-candidates-report", "--output-md", "/tmp/relax.md"]), patch(
            "tools.log_feedback.build_relaxation_candidates_report"
        ) as mocked_report:
            mocked_report.return_value = "# relax\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/relax.md"))

    def test_main_build_phase1b_promotion_report_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-phase1b-promotion-report", "--output-md", "/tmp/promotion.md"]), patch(
            "tools.log_feedback.build_phase1b_promotion_report"
        ) as mocked_report:
            mocked_report.return_value = "# promotion\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/promotion.md"))

    def test_main_build_failed_breakout_down_reversal_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-failed-breakout-down-reversal-report", "--output-md", "/tmp/failed_breakout.md"],
        ), patch("tools.log_feedback.build_failed_breakout_down_reversal_report") as mocked_report:
            mocked_report.return_value = "# failed_breakout\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/failed_breakout.md"))

    def test_main_build_market_map_effectiveness_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-market-map-effectiveness-report", "--output-md", "/tmp/market_map.md"],
        ), patch("tools.log_feedback.build_market_map_effectiveness_report") as mocked_report:
            mocked_report.return_value = "# market_map\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/market_map.md"))

    def test_main_build_market_map_readiness_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-market-map-readiness-report", "--output-md", "/tmp/market_map_ready.md", "--min-market-rows", "3"],
        ), patch("tools.log_feedback.build_market_map_readiness_report") as mocked_report:
            mocked_report.return_value = "# market_map readiness\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/market_map_ready.md"))
        self.assertEqual(mocked_report.call_args.kwargs["min_market_rows"], 3)

    def test_main_build_report_hub_accepts_output_path(self) -> None:
        with patch.object(sys, "argv", ["log_feedback.py", "build-report-hub", "--output-md", "/tmp/report_hub.md"]), patch(
            "tools.log_feedback.build_report_hub"
        ) as mocked_report:
            mocked_report.return_value = "# hub\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/report_hub.md"))

    def test_main_build_quality_guard_effectiveness_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-quality-guard-effectiveness-report", "--output-md", "/tmp/qg.md"],
        ), patch("tools.log_feedback.build_quality_guard_effectiveness_report") as mocked_report:
            mocked_report.return_value = "# qg\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/qg.md"))

    def test_main_build_soft_risk_collateral_damage_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-soft-risk-collateral-damage-report", "--output-md", "/tmp/soft_risk.md"],
        ), patch("tools.log_feedback.build_soft_risk_collateral_damage_report") as mocked_report:
            mocked_report.return_value = "# soft risk\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/soft_risk.md"))

    def test_main_build_paper_entry_sl_wait_redesign_report_accepts_output_path(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "build-paper-entry-sl-wait-redesign-report", "--output-md", "/tmp/paper_entry.md"],
        ), patch("tools.log_feedback.build_paper_entry_sl_wait_redesign_report") as mocked_report:
            mocked_report.return_value = "# paper entry redesign\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/paper_entry.md"))

    def test_main_quality_guard_effectiveness_alias_maps_to_subcommand(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "--quality-guard-effectiveness", "--output-md", "/tmp/qg_alias.md"],
        ), patch("tools.log_feedback.build_quality_guard_effectiveness_report") as mocked_report:
            mocked_report.return_value = "# qg\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/qg_alias.md"))

    def test_main_paper_entry_sl_wait_redesign_alias_maps_to_subcommand(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "--paper-entry-sl-wait-redesign", "--output-md", "/tmp/paper_entry_alias.md"],
        ), patch("tools.log_feedback.build_paper_entry_sl_wait_redesign_report") as mocked_report:
            mocked_report.return_value = "# paper entry redesign\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/paper_entry_alias.md"))

    def test_main_soft_risk_collateral_damage_alias_maps_to_subcommand(self) -> None:
        with patch.object(
            sys,
            "argv",
            ["log_feedback.py", "--soft-risk-collateral-damage", "--output-md", "/tmp/soft_risk_alias.md"],
        ), patch("tools.log_feedback.build_soft_risk_collateral_damage_report") as mocked_report:
            mocked_report.return_value = "# soft risk\n"

            main()

        mocked_report.assert_called_once()
        self.assertEqual(mocked_report.call_args.kwargs["output_md"], Path("/tmp/soft_risk_alias.md"))

    def test_build_active_plan_candidate_intraperiod_outcomes_writes_default_csv_and_preserves_mapping(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            candidates_path = logs_csv / "active_plan_paper_candidates.csv"
            with candidates_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "entry_zone_low",
                        "entry_zone_high",
                        "stop_loss",
                        "tp1",
                        "tp2",
                        "notes",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-001",
                        "source_signal_id": "sig-001",
                        "signal_id": "legacy-sig-001",
                        "timestamp_jst": "2026-06-01T10:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "entry_zone_low": "99",
                        "entry_zone_high": "101",
                        "stop_loss": "95",
                        "tp1": "105",
                        "tp2": "110",
                        "notes": "seed",
                    }
                )

            ohlcv_path = logs_csv / "active_plan_intraperiod_ohlcv.csv"
            with ohlcv_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_jst", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T10:00:00+09:00",
                        "open": "100",
                        "high": "101",
                        "low": "99",
                        "close": "100.5",
                    }
                )
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T11:00:00+09:00",
                        "open": "100.5",
                        "high": "105.2",
                        "low": "100",
                        "close": "104.8",
                    }
                )

            output_path = build_active_plan_candidate_intraperiod_outcomes(
                base_dir=base_dir,
                candidates_path=candidates_path,
                ohlcv_path=ohlcv_path,
                evaluation_window_hours=24.0,
            )

            self.assertEqual(output_path, logs_csv / "active_plan_candidate_intraperiod_outcomes.csv")
            self.assertTrue(output_path.exists())
            with output_path.open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))

            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertTrue(set(MIN_OUTCOME_COLUMNS).issubset(row.keys()))
            self.assertEqual(row["candidate_id"], "cand-001")
            self.assertEqual(row["source_signal_id"], "sig-001")
            self.assertEqual(row["signal_id"], "sig-001")
            self.assertEqual(row["outcome"], "tp1_first")
            self.assertEqual(row["first_exit_reason"], "tp1")
            self.assertEqual(row["entry_reached_time"], "2026-06-01T10:00:00+09:00")
            self.assertEqual(row["first_exit_time"], "2026-06-01T11:00:00+09:00")

    def test_build_active_plan_candidate_intraperiod_outcomes_returns_no_ohlcv_when_ohlcv_path_missing_or_omitted(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            candidates_path = logs_csv / "active_plan_paper_candidates.csv"
            with candidates_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "entry_zone_low",
                        "entry_zone_high",
                        "stop_loss",
                        "tp1",
                        "tp2",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-no-ohlcv",
                        "source_signal_id": "sig-no-ohlcv",
                        "timestamp_jst": "2026-06-01T10:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "entry_zone_low": "99",
                        "entry_zone_high": "101",
                        "stop_loss": "95",
                        "tp1": "105",
                        "tp2": "110",
                    }
                )

            omitted_output = build_active_plan_candidate_intraperiod_outcomes(
                base_dir=base_dir,
                candidates_path=candidates_path,
                evaluation_window_hours=24.0,
            )
            missing_output = build_active_plan_candidate_intraperiod_outcomes(
                base_dir=base_dir,
                candidates_path=candidates_path,
                ohlcv_path=logs_csv / "missing.csv",
                output_csv=logs_csv / "active_plan_candidate_intraperiod_outcomes_missing.csv",
                evaluation_window_hours=24.0,
            )

            for output_path in [omitted_output, missing_output]:
                with output_path.open("r", newline="", encoding="utf-8") as fp:
                    rows = list(csv.DictReader(fp))
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["outcome"], "no_ohlcv")
                self.assertEqual(rows[0]["first_exit_reason"], "")
                self.assertEqual(rows[0]["candidate_id"], "cand-no-ohlcv")

    def test_build_active_plan_candidate_intraperiod_outcomes_filters_date_range_without_changing_outcome(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            candidates_path = logs_csv / "active_plan_paper_candidates.csv"
            with candidates_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "entry_zone_low",
                        "entry_zone_high",
                        "stop_loss",
                        "tp1",
                        "tp2",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-in-range",
                        "source_signal_id": "sig-in-range",
                        "timestamp_jst": "2026-06-01T10:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "entry_zone_low": "99",
                        "entry_zone_high": "101",
                        "stop_loss": "95",
                        "tp1": "105",
                        "tp2": "110",
                    }
                )
                writer.writerow(
                    {
                        "candidate_id": "cand-out-range",
                        "source_signal_id": "sig-out-range",
                        "timestamp_jst": "2026-06-02T10:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "entry_zone_low": "99",
                        "entry_zone_high": "101",
                        "stop_loss": "95",
                        "tp1": "105",
                        "tp2": "110",
                    }
                )

            ohlcv_path = logs_csv / "active_plan_intraperiod_ohlcv.csv"
            with ohlcv_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_jst", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T10:00:00+09:00",
                        "open": "100",
                        "high": "101",
                        "low": "99",
                        "close": "100.5",
                    }
                )
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T11:00:00+09:00",
                        "open": "100.5",
                        "high": "105.2",
                        "low": "100",
                        "close": "104.8",
                    }
                )

            output_path = build_active_plan_candidate_intraperiod_outcomes(
                base_dir=base_dir,
                candidates_path=candidates_path,
                ohlcv_path=ohlcv_path,
                output_csv=logs_csv / "active_plan_candidate_intraperiod_outcomes_filtered.csv",
                date_from="2026-06-01",
                date_to="2026-06-01",
                evaluation_window_hours=24.0,
            )

            with output_path.open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))

            self.assertEqual([row["candidate_id"] for row in rows], ["cand-in-range"])
            self.assertEqual(rows[0]["outcome"], "tp1_first")

    def test_main_build_active_plan_candidate_intraperiod_outcomes_accepts_cli_arguments(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            candidates_path = logs_csv / "active_plan_paper_candidates.csv"
            with candidates_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "entry_zone_low",
                        "entry_zone_high",
                        "stop_loss",
                        "tp1",
                        "tp2",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-cli",
                        "source_signal_id": "sig-cli",
                        "timestamp_jst": "2026-06-01T10:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "entry_zone_low": "99",
                        "entry_zone_high": "101",
                        "stop_loss": "95",
                        "tp1": "105",
                        "tp2": "110",
                    }
                )

            ohlcv_path = logs_csv / "active_plan_intraperiod_ohlcv.csv"
            with ohlcv_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_jst", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T10:00:00+09:00",
                        "open": "100",
                        "high": "101",
                        "low": "99",
                        "close": "100.5",
                    }
                )
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T11:00:00+09:00",
                        "open": "100.5",
                        "high": "105.2",
                        "low": "100",
                        "close": "104.8",
                    }
                )

            output_path = logs_csv / "active_plan_candidate_intraperiod_outcomes_cli.csv"
            from io import StringIO
            from contextlib import redirect_stdout

            with patch.object(
                sys,
                "argv",
                [
                    "log_feedback.py",
                    "build-active-plan-candidate-intraperiod-outcomes",
                    "--candidates-path",
                    str(candidates_path),
                    "--ohlcv-path",
                    str(ohlcv_path),
                    "--output-csv",
                    str(output_path),
                    "--evaluation-window-hours",
                    "24",
                ],
            ):
                buffer = StringIO()
                with redirect_stdout(buffer):
                    main()

            self.assertIn(str(output_path), buffer.getvalue())
            self.assertTrue(output_path.exists())

    def test_build_active_plan_intraperiod_outcomes_cli_builds_csv_from_local_files(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            candidates_csv = base_dir / "active_plan_candidates.csv"
            ohlcv_csv = base_dir / "active_plan_intraperiod_ohlcv.csv"
            output_csv = base_dir / "active_plan_candidate_intraperiod_outcomes.csv"

            with candidates_csv.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "stop_loss",
                        "tp1",
                        "tp2",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-cli",
                        "source_signal_id": "sig-cli",
                        "timestamp_jst": "2026-06-09T09:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                    }
                )

            with ohlcv_csv.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_jst", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-09T09:00:00+09:00",
                        "open": "99.5",
                        "high": "100.5",
                        "low": "99.0",
                        "close": "100.0",
                    }
                )
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-09T09:15:00+09:00",
                        "open": "100.0",
                        "high": "121.0",
                        "low": "100.0",
                        "close": "119.0",
                    }
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "build-active-plan-intraperiod-outcomes",
                    "--candidates-csv",
                    str(candidates_csv),
                    "--ohlcv-csv",
                    str(ohlcv_csv),
                    "--output-csv",
                    str(output_csv),
                    "--now",
                    "2026-06-09T10:00:00+09:00",
                ],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("active_plan_intraperiod_outcomes_csv=", result.stdout)
            self.assertIn("row_count=1", result.stdout)
            self.assertTrue(output_csv.exists())

            with output_csv.open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["candidate_id"], "cand-cli")
            self.assertEqual(row["signal_id"], "sig-cli")
            self.assertEqual(row["outcome"], "tp2_first")
            self.assertEqual(row["first_exit_reason"], "tp2")
            self.assertIn("mfe_r", row)
            self.assertIn("mae_r", row)

    def test_build_active_plan_intraperiod_outcomes_cli_fails_when_ohlcv_missing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            candidates_csv = base_dir / "active_plan_candidates.csv"
            candidates_csv.write_text(
                "\n".join(
                    [
                        "candidate_id,source_signal_id,timestamp_jst,candidate_type,active_primary_action,side,entry_mode,entry_price,stop_loss,tp1,tp2",
                        "cand-cli,sig-cli,2026-06-09T09:00:00+09:00,active_plan,enter_long,long,limit,100,95,110,120",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "build-active-plan-intraperiod-outcomes",
                    "--candidates-csv",
                    str(candidates_csv),
                    "--ohlcv-csv",
                    str(base_dir / "missing_ohlcv.csv"),
                    "--output-csv",
                    str(base_dir / "active_plan_candidate_intraperiod_outcomes.csv"),
                ],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((base_dir / "active_plan_candidate_intraperiod_outcomes.csv").exists())

    def test_build_active_plan_intraperiod_review_cli_builds_csv_and_report_from_local_files(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            candidates_csv = base_dir / "active_plan_candidates.csv"
            ohlcv_csv = base_dir / "active_plan_intraperiod_ohlcv.csv"
            outcomes_csv = base_dir / "active_plan_candidate_intraperiod_outcomes.csv"
            report_md = base_dir / "active_plan_candidate_intraperiod_outcomes_report.md"

            with candidates_csv.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "stop_loss",
                        "tp1",
                        "tp2",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-review",
                        "source_signal_id": "sig-review",
                        "timestamp_jst": "2026-06-09T09:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                    }
                )

            with ohlcv_csv.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_jst", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-09T09:00:00+09:00",
                        "open": "99.5",
                        "high": "100.5",
                        "low": "99.0",
                        "close": "100.0",
                    }
                )
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-09T09:15:00+09:00",
                        "open": "100.0",
                        "high": "121.0",
                        "low": "100.0",
                        "close": "119.0",
                    }
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "build-active-plan-intraperiod-review",
                    "--candidates-csv",
                    str(candidates_csv),
                    "--ohlcv-csv",
                    str(ohlcv_csv),
                    "--outcomes-csv",
                    str(outcomes_csv),
                    "--output-md",
                    str(report_md),
                    "--now",
                    "2026-06-09T10:00:00+09:00",
                ],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("active_plan_intraperiod_outcomes_csv=", result.stdout)
            self.assertIn("active_plan_intraperiod_report_md=", result.stdout)
            self.assertIn("row_count=1", result.stdout)
            self.assertTrue(outcomes_csv.exists())
            self.assertTrue(report_md.exists())

            with outcomes_csv.open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["candidate_id"], "cand-review")
            self.assertEqual(row["signal_id"], "sig-review")
            self.assertEqual(row["outcome"], "tp2_first")
            self.assertEqual(row["first_exit_reason"], "tp2")
            self.assertIn("mfe_r", row)
            self.assertIn("mae_r", row)

            report = report_md.read_text(encoding="utf-8")
            self.assertIn("BTCFX Ver03-v4 Active Plan 候補別 intraperiod 評価", report)
            self.assertIn("`tp2_first`: 1件", report)
            self.assertIn("local CSV only", report)
            self.assertIn("no exchange fetch", report)
            self.assertIn("no daily-sync wiring", report)
            self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", report)

    def test_build_active_plan_intraperiod_review_cli_stdout_json_is_machine_readable(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            candidates_csv = base_dir / "active_plan_candidates.csv"
            ohlcv_csv = base_dir / "active_plan_intraperiod_ohlcv.csv"
            outcomes_csv = base_dir / "active_plan_candidate_intraperiod_outcomes.csv"
            report_md = base_dir / "active_plan_candidate_intraperiod_outcomes_report.md"

            with candidates_csv.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "candidate_id",
                        "source_signal_id",
                        "timestamp_jst",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "stop_loss",
                        "tp1",
                        "tp2",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "candidate_id": "cand-review-json",
                        "source_signal_id": "sig-review-json",
                        "timestamp_jst": "2026-06-09T09:00:00+09:00",
                        "candidate_type": "active_plan",
                        "active_primary_action": "enter_long",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "stop_loss": "95",
                        "tp1": "110",
                        "tp2": "120",
                    }
                )

            with ohlcv_csv.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=["timestamp_jst", "open", "high", "low", "close"])
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-09T09:00:00+09:00",
                        "open": "99.5",
                        "high": "100.5",
                        "low": "99.0",
                        "close": "100.0",
                    }
                )
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-09T09:15:00+09:00",
                        "open": "100.0",
                        "high": "121.0",
                        "low": "100.0",
                        "close": "119.0",
                    }
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "build-active-plan-intraperiod-review",
                    "--candidates-csv",
                    str(candidates_csv),
                    "--ohlcv-csv",
                    str(ohlcv_csv),
                    "--outcomes-csv",
                    str(outcomes_csv),
                    "--output-md",
                    str(report_md),
                    "--now",
                    "2026-06-09T10:00:00+09:00",
                    "--stdout-json",
                ],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(
                result.stdout,
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            )
            self.assertEqual(payload["schema_version"], "active_plan_intraperiod_review.v1")
            self.assertEqual(payload["command"], "build-active-plan-intraperiod-review")
            self.assertEqual(payload["row_count"], 1)
            self.assertEqual(payload["candidates_csv"], str(candidates_csv))
            self.assertEqual(payload["ohlcv_csv"], str(ohlcv_csv))
            self.assertEqual(payload["outcomes_csv"], str(outcomes_csv))
            self.assertEqual(payload["report_md"], str(report_md))
            self.assertTrue(payload["report_only"])
            self.assertFalse(payload["formal_go"])
            self.assertFalse(payload["automatic_order_allowed"])
            self.assertFalse(payload["exchange_fetch_allowed"])
            self.assertFalse(payload["daily_sync_wiring"])
            self.assertFalse(payload["secret_reading_allowed"])
            self.assertTrue(payload["human_decides_manually"])
            self.assertEqual(
                payload["safety_boundary"],
                "report-only / not FORMAL_GO / no automatic order / human decides manually",
            )
            self.assertTrue(outcomes_csv.exists())
            self.assertTrue(report_md.exists())

            with outcomes_csv.open("r", newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["outcome"], "tp2_first")
            self.assertEqual(row["first_exit_reason"], "tp2")

    def test_build_active_plan_intraperiod_review_cli_fails_when_ohlcv_missing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            candidates_csv = base_dir / "active_plan_candidates.csv"
            candidates_csv.write_text(
                "\n".join(
                    [
                        "candidate_id,source_signal_id,timestamp_jst,candidate_type,active_primary_action,side,entry_mode,entry_price,stop_loss,tp1,tp2",
                        "cand-review,sig-review,2026-06-09T09:00:00+09:00,active_plan,enter_long,long,limit,100,95,110,120",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "tools" / "log_feedback.py"),
                    "build-active-plan-intraperiod-review",
                    "--candidates-csv",
                    str(candidates_csv),
                    "--ohlcv-csv",
                    str(base_dir / "missing_ohlcv.csv"),
                    "--outcomes-csv",
                    str(base_dir / "active_plan_candidate_intraperiod_outcomes.csv"),
                    "--output-md",
                    str(base_dir / "active_plan_candidate_intraperiod_outcomes_report.md"),
                ],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((base_dir / "active_plan_candidate_intraperiod_outcomes.csv").exists())
            self.assertFalse((base_dir / "active_plan_candidate_intraperiod_outcomes_report.md").exists())

    def test_build_active_plan_candidate_intraperiod_outcomes_report_writes_default_markdown_and_summarizes_counts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)

            outcomes_path = logs_csv / "active_plan_candidate_intraperiod_outcomes.csv"
            fieldnames = [
                "timestamp_jst",
                "candidate_id",
                "signal_id",
                "candidate_type",
                "active_primary_action",
                "side",
                "entry_mode",
                "entry_price",
                "stop_price",
                "tp1_price",
                "tp2_price",
                "outcome",
                "entry_reached_time",
                "first_exit_time",
                "first_exit_reason",
                "mfe_price",
                "mae_price",
            ]
            rows = [
                {
                    "timestamp_jst": "2026-06-07T12:00:00+09:00",
                    "candidate_id": "cand-1",
                    "signal_id": "sig-1",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit",
                    "entry_price": "100",
                    "stop_price": "95",
                    "tp1_price": "105",
                    "tp2_price": "110",
                    "outcome": "entry_reached",
                    "entry_reached_time": "2026-06-07T12:15:00+09:00",
                    "first_exit_time": "",
                    "first_exit_reason": "",
                    "mfe_price": "5.0",
                    "mae_price": "1.0",
                },
                {
                    "timestamp_jst": "2026-06-06T12:00:00+09:00",
                    "candidate_id": "cand-2",
                    "signal_id": "sig-2",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "side": "long",
                    "entry_mode": "limit",
                    "entry_price": "101",
                    "stop_price": "96",
                    "tp1_price": "106",
                    "tp2_price": "111",
                    "outcome": "tp1_first",
                    "entry_reached_time": "2026-06-06T12:20:00+09:00",
                    "first_exit_time": "2026-06-06T13:00:00+09:00",
                    "first_exit_reason": "tp1",
                    "mfe_price": "6.0",
                    "mae_price": "2.0",
                },
                {
                    "timestamp_jst": "2026-06-05T12:00:00+09:00",
                    "candidate_id": "cand-3",
                    "signal_id": "sig-3",
                    "candidate_type": "active_market_small",
                    "active_primary_action": "ACTIVE_MARKET_SMALL",
                    "side": "short",
                    "entry_mode": "market",
                    "entry_price": "102",
                    "stop_price": "107",
                    "tp1_price": "97",
                    "tp2_price": "95",
                    "outcome": "sl_first",
                    "entry_reached_time": "2026-06-05T12:10:00+09:00",
                    "first_exit_time": "2026-06-05T12:30:00+09:00",
                    "first_exit_reason": "sl",
                    "mfe_price": "3.0",
                    "mae_price": "2.5",
                },
                {
                    "timestamp_jst": "2026-06-04T12:00:00+09:00",
                    "candidate_id": "cand-4",
                    "signal_id": "sig-4",
                    "candidate_type": "active_counter_scalp",
                    "active_primary_action": "ACTIVE_COUNTER_SCALP",
                    "side": "short",
                    "entry_mode": "limit",
                    "entry_price": "103",
                    "stop_price": "108",
                    "tp1_price": "98",
                    "tp2_price": "96",
                    "outcome": "timeout",
                    "entry_reached_time": "2026-06-04T12:05:00+09:00",
                    "first_exit_time": "2026-06-04T15:00:00+09:00",
                    "first_exit_reason": "timeout",
                    "mfe_price": "2.2",
                    "mae_price": "0.9",
                },
                {
                    "timestamp_jst": "2026-06-03T12:00:00+09:00",
                    "candidate_id": "cand-5",
                    "signal_id": "sig-5",
                    "candidate_type": "active_counter_scalp",
                    "active_primary_action": "ACTIVE_COUNTER_SCALP",
                    "side": "long",
                    "entry_mode": "limit",
                    "entry_price": "104",
                    "stop_price": "99",
                    "tp1_price": "109",
                    "tp2_price": "111",
                    "outcome": "ambiguous",
                    "entry_reached_time": "2026-06-03T12:08:00+09:00",
                    "first_exit_time": "2026-06-03T12:15:00+09:00",
                    "first_exit_reason": "ambiguous",
                    "mfe_price": "4.2",
                    "mae_price": "1.1",
                },
                {
                    "timestamp_jst": "2026-06-02T12:00:00+09:00",
                    "candidate_id": "cand-6",
                    "signal_id": "sig-6",
                    "candidate_type": "active_market_small",
                    "active_primary_action": "ACTIVE_MARKET_SMALL",
                    "side": "long",
                    "entry_mode": "market",
                    "entry_price": "105",
                    "stop_price": "100",
                    "tp1_price": "110",
                    "tp2_price": "112",
                    "outcome": "no_ohlcv",
                    "first_exit_reason": "",
                    "mfe_price": "",
                    "mae_price": "",
                },
                {
                    "timestamp_jst": "2026-06-01T12:00:00+09:00",
                    "candidate_id": "cand-7",
                    "signal_id": "sig-7",
                    "candidate_type": "active_limit_retest",
                    "active_primary_action": "ACTIVE_LIMIT_RETEST",
                    "side": "short",
                    "entry_mode": "limit",
                    "entry_price": "106",
                    "stop_price": "111",
                    "tp1_price": "101",
                    "tp2_price": "99",
                    "outcome": "pending",
                    "first_exit_reason": "",
                    "mfe_price": "",
                    "mae_price": "",
                },
                {
                    "timestamp_jst": "2026-06-01T11:30:00+09:00",
                    "candidate_id": "cand-8",
                    "signal_id": "sig-8",
                    "candidate_type": "active_intraperiod_tp2_sample",
                    "active_primary_action": "ACTIVE_INTRAPERIOD_TP2_SAMPLE",
                    "side": "short",
                    "entry_mode": "limit",
                    "entry_price": "107",
                    "stop_price": "112",
                    "tp1_price": "102",
                    "tp2_price": "100",
                    "outcome": "tp2_first",
                    "entry_reached_time": "2026-06-01T11:45:00+09:00",
                    "first_exit_time": "2026-06-01T12:00:00+09:00",
                    "first_exit_reason": "tp2",
                    "mfe_price": "7.0",
                    "mae_price": "0.5",
                },
            ]
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            report = build_active_plan_candidate_intraperiod_outcomes_report(
                base_dir=base_dir,
                intraperiod_outcomes_path=outcomes_path,
                date_from="2026-06-01",
                date_to="2026-06-07",
                limit=3,
            )

            expected_path = (
                base_dir
                / "運用資料"
                / "reports"
                / "analysis"
                / f"active_plan_candidate_intraperiod_outcomes_{datetime.now(tz=JST).strftime('%Y%m%d')}.md"
            )
            self.assertTrue(expected_path.exists())
            self.assertIn("BTCFX Ver03-v4 Active Plan 候補別 intraperiod 評価", report)
            self.assertNotIn("BTCFX Ver03-v2 Active Plan 候補別 intraperiod 評価", report)
            self.assertIn("実弾売買判断ではない", report)
            self.assertIn("Active Plan は正式GOではない", report)
            self.assertIn("自動発注候補ではない", report)
            self.assertIn("local CSV only", report)
            self.assertIn("no exchange fetch", report)
            self.assertIn("no daily-sync wiring", report)
            self.assertIn("report-only / not FORMAL_GO / no automatic order / human decides manually", report)
            self.assertIn("build-active-plan-intraperiod-outcomes", report)
            self.assertIn("--candidates-csv logs/csv/active_plan_candidates.csv", report)
            self.assertIn("--ohlcv-csv <local_15m_ohlcv_csv>", report)
            self.assertIn("--output-csv logs/csv/active_plan_candidate_intraperiod_outcomes.csv", report)
            self.assertIn("outcome別集計", report)
            self.assertIn("`tp1_first`: 1件", report)
            self.assertIn("`tp2_first`: 1件", report)
            self.assertIn("`sl_first`: 1件", report)
            self.assertIn("`timeout`: 1件", report)
            self.assertIn("`no_ohlcv`: 1件", report)
            self.assertIn("`pending`: 1件", report)
            self.assertIn("## 4. candidate_type別集計", report)
            self.assertIn("`active_limit_retest`: 3件", report)
            self.assertIn("## 5. active_primary_action別集計", report)
            self.assertIn("`ACTIVE_LIMIT_RETEST`: 3件", report)
            self.assertIn("## 6. side別集計", report)
            self.assertIn("`long`: 4件", report)
            self.assertIn("`short`: 4件", report)
            self.assertIn("## 9. 代表例", report)
            self.assertIn("cand-1", report)
            self.assertIn("cand-2", report)
            self.assertIn("cand-3", report)
            self.assertIn("## 10. 未解決事項", report)
            self.assertIn("pending=1件", report)
            self.assertIn("ambiguous=1件", report)
            self.assertIn("no_ohlcv=1件", report)

    def test_build_active_plan_candidate_intraperiod_outcomes_report_handles_missing_input_csv(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            (base_dir / "logs" / "csv").mkdir(parents=True, exist_ok=True)
            report = build_active_plan_candidate_intraperiod_outcomes_report(
                base_dir=base_dir,
                intraperiod_outcomes_path=base_dir / "logs" / "csv" / "missing.csv",
            )
            expected_path = (
                base_dir
                / "運用資料"
                / "reports"
                / "analysis"
                / f"active_plan_candidate_intraperiod_outcomes_{datetime.now(tz=JST).strftime('%Y%m%d')}.md"
            )
            self.assertTrue(expected_path.exists())
            self.assertIn("入力CSVが見つかりません", report)
            self.assertIn("build-active-plan-intraperiod-outcomes", report)
            self.assertIn("no daily-sync wiring", report)

    def test_build_active_plan_candidate_intraperiod_outcomes_report_filters_date_range(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            outcomes_path = logs_csv / "active_plan_candidate_intraperiod_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "timestamp_jst",
                        "candidate_id",
                        "signal_id",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "stop_price",
                        "tp1_price",
                        "tp2_price",
                        "outcome",
                        "entry_reached_time",
                        "first_exit_time",
                        "first_exit_reason",
                        "mfe_price",
                        "mae_price",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T12:00:00+09:00",
                        "candidate_id": "cand-in",
                        "signal_id": "sig-in",
                        "candidate_type": "active_limit_retest",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "stop_price": "95",
                        "tp1_price": "105",
                        "tp2_price": "110",
                        "outcome": "tp1_first",
                        "entry_reached_time": "2026-06-01T12:10:00+09:00",
                        "first_exit_time": "2026-06-01T12:20:00+09:00",
                        "first_exit_reason": "tp1",
                        "mfe_price": "5.0",
                        "mae_price": "1.0",
                    }
                )
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-02T12:00:00+09:00",
                        "candidate_id": "cand-out",
                        "signal_id": "sig-out",
                        "candidate_type": "active_market_small",
                        "active_primary_action": "ACTIVE_MARKET_SMALL",
                        "side": "short",
                        "entry_mode": "market",
                        "entry_price": "101",
                        "stop_price": "106",
                        "tp1_price": "96",
                        "tp2_price": "94",
                        "outcome": "sl_first",
                        "entry_reached_time": "2026-06-02T12:10:00+09:00",
                        "first_exit_time": "2026-06-02T12:20:00+09:00",
                        "first_exit_reason": "sl",
                        "mfe_price": "3.0",
                        "mae_price": "2.0",
                    }
                )

            report = build_active_plan_candidate_intraperiod_outcomes_report(
                base_dir=base_dir,
                intraperiod_outcomes_path=outcomes_path,
                date_from="2026-06-01",
                date_to="2026-06-01",
            )

            self.assertIn("rows: 1", report)
            self.assertIn("cand-in", report)
            self.assertNotIn("cand-out", report)

    def test_main_build_active_plan_candidate_intraperiod_outcomes_report_accepts_output_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            logs_csv = base_dir / "logs" / "csv"
            logs_csv.mkdir(parents=True, exist_ok=True)
            outcomes_path = logs_csv / "active_plan_candidate_intraperiod_outcomes.csv"
            with outcomes_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=[
                        "timestamp_jst",
                        "candidate_id",
                        "signal_id",
                        "candidate_type",
                        "active_primary_action",
                        "side",
                        "entry_mode",
                        "entry_price",
                        "stop_price",
                        "tp1_price",
                        "tp2_price",
                        "outcome",
                        "entry_reached_time",
                        "first_exit_time",
                        "first_exit_reason",
                        "mfe_price",
                        "mae_price",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp_jst": "2026-06-01T12:00:00+09:00",
                        "candidate_id": "cand-cli-report",
                        "signal_id": "sig-cli-report",
                        "candidate_type": "active_limit_retest",
                        "active_primary_action": "ACTIVE_LIMIT_RETEST",
                        "side": "long",
                        "entry_mode": "limit",
                        "entry_price": "100",
                        "stop_price": "95",
                        "tp1_price": "105",
                        "tp2_price": "110",
                        "outcome": "tp1_first",
                        "entry_reached_time": "2026-06-01T12:10:00+09:00",
                        "first_exit_time": "2026-06-01T12:20:00+09:00",
                        "first_exit_reason": "tp1",
                        "mfe_price": "5.0",
                        "mae_price": "1.0",
                    }
                )

            output_md = base_dir / "custom_report.md"
            from io import StringIO
            from contextlib import redirect_stdout

            with patch.object(
                sys,
                "argv",
                [
                    "log_feedback.py",
                    "build-active-plan-candidate-intraperiod-outcomes-report",
                    "--intraperiod-outcomes-path",
                    str(outcomes_path),
                    "--output-md",
                    str(output_md),
                    "--date-from",
                    "2026-06-01",
                    "--date-to",
                    "2026-06-01",
                    "--limit",
                    "5",
                ],
            ):
                buffer = StringIO()
                with redirect_stdout(buffer):
                    main()

            self.assertIn(str(output_md), buffer.getvalue())
            self.assertTrue(output_md.exists())
            self.assertIn("BTCFX Ver03-v4 Active Plan 候補別 intraperiod 評価", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
