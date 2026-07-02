from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import mock

import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import build_summary_body  # noqa: E402
from src.notification.detail_page import build_notification_detail_html  # noqa: E402
import tools.log_feedback as log_feedback  # noqa: E402
from tests.test_active_plan_notification_formatting import (  # noqa: E402
    _bootstrap_manual_delivery_handoff_fixtures,
    _write_json_fixture,
)


def _compact_post_eval_payload() -> dict[str, object]:
    return {
        "schema_version": "post_eval_recommendations.v1",
        "report_date": "20260702",
        "report_path": "運用資料/reports/post_eval/post_eval_recommendations_20260702.md",
        "output_csv_path": "logs/csv/post_eval_recommendation_candidates.csv",
        "candidate_count": 3,
        "top_recommendation_codes": [
            "NO_TRADE_SPLIT_REVIEW",
            "SUBJECT_DEFENSIVE_WORDING_REVIEW",
            "LINKAGE_COVERAGE_REVIEW",
        ],
        "priority_counts": {"high": 1, "medium": 1, "low": 1},
        "confidence_counts": {"actual_backed": 1, "proxy_backed": 2},
        "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually",
        "note": "report-only status / human approval required",
        "human_approval_required": True,
    }


def _malformed_post_eval_payload() -> dict[str, object]:
    return {
        "app_surface_validation_data": {
            "post_eval_recommendation_summary": "not-a-dict",
        }
    }


def _base_result_payload(post_eval_key: str | None = None, post_eval_value: object | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "timestamp_jst": "2026-03-15T06:05:00+09:00",
        "signal_id": "20260315_060500",
        "system_label": "Ver02.3",
        "system_mode_label": "CLI",
        "notification_kind": "attention",
        "summary_subject": "post-eval surface smoke",
        "bias": "short",
        "current_price": 70765.2,
        "long_display_score": 38,
        "short_display_score": 59,
        "score_gap": -21,
        "signals_4h": "wait",
        "signals_1h": "short",
        "signals_15m": "wait",
        "prelabel": "SWEEP_WAIT",
        "primary_setup_status": "watch",
        "primary_setup_reason": "near_entry_zone_waiting_trigger",
        "confidence": 41,
        "confidence_direction_shadow": 62.0,
        "confidence_execution_shadow": 28.0,
        "confidence_wait_shadow": 64.0,
        "warning_flags": ["Critical_zone_warning"],
        "risk_flags": ["upper_liquidity_close"],
        "no_trade_flags": ["sweep_incomplete"],
    }
    if post_eval_key is not None and post_eval_value is not None:
        payload[post_eval_key] = post_eval_value
    return payload


class PostEvalSurfaceSmokeTest(unittest.TestCase):
    def _build_summary_body(self, payload: dict[str, object]) -> str:
        with mock.patch("src.ai.summary.build_post_eval_recommendations", create=True, side_effect=AssertionError("must not run")):
            body, _provider = build_summary_body(
                provider="api",
                api_key="",
                model="",
                cli_command="",
                timeout_sec=1,
                retry_count=1,
                base_dir=BASE_DIR,
                result_payload=_base_result_payload("post_eval_recommendations", payload),
            )
        return body

    def _export_surface(self, handoff_dir: Path, output_dir: Path, payload_path: Path | None) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object], str]:
        post_eval_payload = None
        if payload_path is not None:
            post_eval_payload = log_feedback._manual_delivery_load_post_eval_recommendation_payload(payload_path, None)
        log_feedback._write_current_manual_delivery_app_state_outputs(
            self_check_json=handoff_dir / "self-check.json",
            post_eval_recommendations=post_eval_payload,
            parser=None,
        )
        log_feedback._write_manual_delivery_current_handoff_app_state_status_outputs(
            app_state_json=handoff_dir / "app-state.json",
            output_json=handoff_dir / "app-state-status.json",
            parser=None,
        )
        log_feedback._write_manual_delivery_current_handoff_app_state_ready_check_outputs(
            app_state_status_json=handoff_dir / "app-state-status.json",
            output_json=handoff_dir / "ready-check.json",
            parser=None,
        )
        with mock.patch.object(
            log_feedback,
            "build_post_eval_recommendation_report",
            side_effect=AssertionError("recommendation engine must not run during smoke export"),
        ):
            log_feedback._write_current_manual_delivery_app_surface_outputs(
                handoff_dir=handoff_dir,
                output_dir=output_dir,
                post_eval_recommendations_json=payload_path,
                parser=None,
            )

        check_buffer = io.StringIO()
        with contextlib.redirect_stdout(check_buffer):
            log_feedback._run_check_current_manual_delivery_app_surface_command(
                SimpleNamespace(stdout_json=True, app_surface_dir=str(output_dir), intraperiod_outcomes_path=None),
                parser=None,
            )

        app_ready_data = json.loads((output_dir / "app-ready.json").read_text(encoding="utf-8"))
        app_contract_data = json.loads((output_dir / "app-contract.json").read_text(encoding="utf-8"))
        app_snapshot_data = json.loads((output_dir / "app-snapshot.json").read_text(encoding="utf-8"))
        check_data = json.loads(check_buffer.getvalue())
        return app_ready_data, app_contract_data, app_snapshot_data, check_data, (output_dir / "app-dashboard.html").read_text(encoding="utf-8")

    def test_post_eval_surface_smoke_uses_same_payload_across_public_html_dashboard_ready_check_and_mail(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            handoff_dir = _bootstrap_manual_delivery_handoff_fixtures(base_dir)
            payload = _compact_post_eval_payload()
            payload_path = _write_json_fixture(base_dir / "fixtures" / "post-eval-recommendations.json", payload)

            detail_html = build_notification_detail_html(_base_result_payload("post_eval_recommendations", payload))
            summary_body = self._build_summary_body(payload)
            app_ready_data, app_contract_data, app_snapshot_data, check_data, dashboard_html = self._export_surface(
                handoff_dir=handoff_dir,
                output_dir=base_dir / "local" / "manual_delivery_app_surface",
                payload_path=payload_path,
            )

            self.assertIn("【Post-Eval】", summary_body)
            self.assertIn("report-only", summary_body)
            self.assertTrue("human approval" in summary_body.lower() or "human decides manually" in summary_body.lower())

            for body in (detail_html, dashboard_html):
                self.assertIn("Post-Eval Recommendation Status", body)
                self.assertIn("report-only", body)
                self.assertTrue(
                    "human approval" in body.lower() or "human decides manually" in body.lower()
                )
                self.assertNotIn("source_uid_hash", body)
                self.assertNotIn("uid-ABC123", body)
                self.assertNotIn("account_test", body)
                self.assertNotIn("private/order", body)
                self.assertNotIn("OPENAI_API_KEY", body)
                self.assertNotIn("SMTP_PASSWORD", body)
                self.assertNotIn("smtp", body.lower())
                self.assertNotIn("Gmail", body)
                self.assertNotIn("send_email", body)
                self.assertNotIn("<script", body.lower())
                self.assertNotIn("fetch(", body)

            for output_data in (app_ready_data, app_contract_data, app_snapshot_data, check_data):
                self.assertTrue(output_data["post_eval_recommendations_present"])
                self.assertTrue(output_data["post_eval_recommendations_ready"])
                self.assertEqual(output_data["post_eval_recommendations_status"], "ready")
                self.assertEqual(output_data["post_eval_recommendations_schema_version"], "post_eval_recommendations.v1")
                self.assertEqual(output_data["post_eval_recommendations_candidate_count"], 3)
                self.assertEqual(output_data["post_eval_recommendations_reason_codes"], [])

            for output_data in (app_contract_data, app_snapshot_data):
                self.assertIn("post_eval_recommendations", output_data)
                self.assertLessEqual(
                    set(output_data["post_eval_recommendations"].keys()),
                    {
                        "schema_version",
                        "report_date",
                        "report_path",
                        "output_csv_path",
                        "candidate_count",
                        "top_recommendation_codes",
                        "priority_counts",
                        "confidence_counts",
                        "safety_boundary",
                        "note",
                        "human_approval_required",
                        "required_human_approval",
                    },
                )

            combined_text = "\n".join(
                [
                    detail_html,
                    summary_body,
                    dashboard_html,
                    json.dumps(app_ready_data, ensure_ascii=False),
                    json.dumps(app_contract_data, ensure_ascii=False),
                    json.dumps(app_snapshot_data, ensure_ascii=False),
                    json.dumps(check_data, ensure_ascii=False),
                ]
            )
            self.assertNotIn("source_uid_hash", combined_text)
            self.assertNotIn("uid-ABC123", combined_text)
            self.assertNotIn("account_test", combined_text)
            self.assertNotIn("private/order", combined_text)
            self.assertNotIn("OPENAI_API_KEY", combined_text)
            self.assertNotIn("SMTP_PASSWORD", combined_text)
            self.assertNotIn("smtp", combined_text.lower())
            self.assertNotIn("Gmail", combined_text)
            self.assertNotIn("send_email", combined_text)
            self.assertNotIn("<script", combined_text.lower())
            self.assertNotIn("fetch(", combined_text)

    def test_post_eval_surface_smoke_handles_absent_and_malformed_payloads_without_generation(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            handoff_dir = _bootstrap_manual_delivery_handoff_fixtures(base_dir)
            absent_surface_dir = base_dir / "local" / "absent-manual_delivery_app_surface"
            malformed_surface_dir = base_dir / "local" / "malformed-manual_delivery_app_surface"
            malformed_payload_path = _write_json_fixture(base_dir / "fixtures" / "malformed-post-eval.json", _malformed_post_eval_payload())

            with mock.patch.object(
                log_feedback,
                "build_post_eval_recommendation_report",
                side_effect=AssertionError("recommendation engine must not run during smoke export"),
            ):
                log_feedback._write_current_manual_delivery_app_state_outputs(
                    self_check_json=handoff_dir / "self-check.json",
                    parser=None,
                )
                log_feedback._write_manual_delivery_current_handoff_app_state_status_outputs(
                    app_state_json=handoff_dir / "app-state.json",
                    output_json=handoff_dir / "app-state-status.json",
                    parser=None,
                )
                log_feedback._write_manual_delivery_current_handoff_app_state_ready_check_outputs(
                    app_state_status_json=handoff_dir / "app-state-status.json",
                    output_json=handoff_dir / "ready-check.json",
                    parser=None,
                )
                log_feedback._write_current_manual_delivery_app_surface_outputs(
                    handoff_dir=handoff_dir,
                    output_dir=absent_surface_dir,
                    parser=None,
                )
                log_feedback._write_current_manual_delivery_app_state_outputs(
                    self_check_json=handoff_dir / "self-check.json",
                    post_eval_recommendations=log_feedback._manual_delivery_load_post_eval_recommendation_payload(
                        malformed_payload_path,
                        None,
                    ),
                    parser=None,
                )
                log_feedback._write_manual_delivery_current_handoff_app_state_status_outputs(
                    app_state_json=handoff_dir / "app-state.json",
                    output_json=handoff_dir / "app-state-status.json",
                    parser=None,
                )
                log_feedback._write_manual_delivery_current_handoff_app_state_ready_check_outputs(
                    app_state_status_json=handoff_dir / "app-state-status.json",
                    output_json=handoff_dir / "ready-check.json",
                    parser=None,
                )
                log_feedback._write_current_manual_delivery_app_surface_outputs(
                    handoff_dir=handoff_dir,
                    output_dir=malformed_surface_dir,
                    post_eval_recommendations_json=malformed_payload_path,
                    parser=None,
                )

            absent_check_buffer = io.StringIO()
            malformed_check_buffer = io.StringIO()
            with contextlib.redirect_stdout(absent_check_buffer):
                log_feedback._run_check_current_manual_delivery_app_surface_command(
                    SimpleNamespace(stdout_json=True, app_surface_dir=str(absent_surface_dir), intraperiod_outcomes_path=None),
                    parser=None,
                )
            with contextlib.redirect_stdout(malformed_check_buffer):
                log_feedback._run_check_current_manual_delivery_app_surface_command(
                    SimpleNamespace(stdout_json=True, app_surface_dir=str(malformed_surface_dir), intraperiod_outcomes_path=None),
                    parser=None,
                )

            absent_ready_data = json.loads((absent_surface_dir / "app-ready.json").read_text(encoding="utf-8"))
            absent_check_data = json.loads(absent_check_buffer.getvalue())
            malformed_ready_data = json.loads((malformed_surface_dir / "app-ready.json").read_text(encoding="utf-8"))
            malformed_check_data = json.loads(malformed_check_buffer.getvalue())
            absent_detail_html = build_notification_detail_html(_base_result_payload())
            absent_summary_body = self._build_summary_body({})
            malformed_detail_html = build_notification_detail_html(_base_result_payload("post_eval_recommendation_summary", "not-a-dict"))
            malformed_summary_body = self._build_summary_body({"_malformed": True})

            self.assertFalse(absent_ready_data["post_eval_recommendations_present"])
            self.assertTrue(absent_ready_data["post_eval_recommendations_ready"])
            self.assertEqual(absent_ready_data["post_eval_recommendations_status"], "optional_not_present")
            self.assertFalse(absent_check_data["post_eval_recommendations_present"])
            self.assertTrue(absent_check_data["post_eval_recommendations_ready"])
            self.assertEqual(absent_check_data["post_eval_recommendations_status"], "optional_not_present")
            self.assertNotIn("Post-Eval Recommendation Status", absent_detail_html)
            self.assertIn("【Post-Eval】not ready", absent_summary_body)

            self.assertFalse(malformed_ready_data["post_eval_recommendations_ready"])
            self.assertEqual(malformed_ready_data["post_eval_recommendations_status"], "invalid_not_ready")
            self.assertIn("malformed_payload", malformed_ready_data["post_eval_recommendations_reason_codes"])
            self.assertFalse(malformed_check_data["post_eval_recommendations_ready"])
            self.assertEqual(malformed_check_data["post_eval_recommendations_status"], "invalid_not_ready")

            self.assertIn("post-eval recommendation payload is unavailable or malformed.", malformed_detail_html)
            self.assertIn("【Post-Eval】not ready", malformed_summary_body)
            self.assertNotIn("uid-ABC123", malformed_detail_html)
            self.assertNotIn("uid-ABC123", malformed_summary_body)
            self.assertNotIn("source_uid_hash", malformed_detail_html)
            self.assertNotIn("source_uid_hash", malformed_summary_body)


if __name__ == "__main__":
    unittest.main()
