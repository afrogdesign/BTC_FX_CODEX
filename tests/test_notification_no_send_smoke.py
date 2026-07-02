from __future__ import annotations

import contextlib
import io
import json
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import tools.render_notification_no_send_smoke as render_no_send_smoke  # noqa: E402


def _unsafe_post_eval_payload() -> dict[str, object]:
    return {
        "schema_version": "post_eval_recommendations.v1",
        "report_date": "20260702",
        "report_path": "../../secrets/<script>/smtp/Gmail/send_email/uid-ABC123/account_test",
        "output_csv_path": "logs/csv/uid-ABC123-account_test.csv",
        "candidate_count": 3,
        "top_recommendation_codes": [
            "uid-ABC123",
            "account_test",
            "private/order",
            "OPENAI_API_KEY",
            "SMTP_PASSWORD",
            "smtp",
            "Gmail",
            "send_email",
            "<script",
            "fetch(",
        ],
        "priority_counts": {"high": 1},
        "confidence_counts": {"actual_backed": 1},
        "safety_boundary": "private/order / smtp / Gmail / send_email",
        "note": "report-only status <script> fetch( send_email Gmail smtp OPENAI_API_KEY SMTP_PASSWORD source_uid_hash uid-ABC123 account_test",
        "human_approval_required": True,
    }


class NotificationNoSendSmokeTest(unittest.TestCase):
    def test_command_stdout_json_is_pass_and_implicitly_no_send(self) -> None:
        with TemporaryDirectory() as tmpdir:
            workdir = Path(tmpdir)
            stdout_buffer = io.StringIO()
            with contextlib.redirect_stdout(stdout_buffer):
                with contextlib.chdir(workdir):
                    exit_code = render_no_send_smoke.main(["--stdout-json"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(list(workdir.iterdir()), [])
            report = json.loads(stdout_buffer.getvalue())

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["mode"], "no_send_render_only")
        self.assertFalse(report["real_mail_sent"])
        self.assertTrue(report["report_only"])
        self.assertTrue(report["not_formal_go"])
        self.assertTrue(report["no_automatic_order"])
        self.assertTrue(report["human_decides_manually"])
        self.assertTrue(report["summary_body_rendered"])
        self.assertTrue(report["detail_html_rendered"])
        self.assertTrue(report["post_eval_recommendations_present"])
        self.assertFalse(report["sensitive_leak_detected"])

    def test_helper_does_not_touch_send_email_or_save_pending_email(self) -> None:
        fake_main = types.SimpleNamespace(
            send_email=mock.Mock(name="send_email"),
            save_pending_email=mock.Mock(name="save_pending_email"),
        )

        with mock.patch.dict(sys.modules, {"main": fake_main}):
            report = render_no_send_smoke._render_no_send_render_only_smoke()

        fake_main.send_email.assert_not_called()
        fake_main.save_pending_email.assert_not_called()
        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["post_eval_recommendations_present"])
        self.assertFalse(report["sensitive_leak_detected"])
        self.assertIn("report_only", report)
        self.assertIn("not_formal_go", report)
        self.assertIn("no_automatic_order", report)
        self.assertIn("human_decides_manually", report)

    def test_unsafe_payload_causes_non_zero_failure(self) -> None:
        stdout_buffer = io.StringIO()
        with mock.patch.object(render_no_send_smoke, "_synthetic_result_payload", return_value=render_no_send_smoke._synthetic_result_payload(_unsafe_post_eval_payload())):
            with contextlib.redirect_stdout(stdout_buffer):
                exit_code = render_no_send_smoke.main(["--stdout-json"])

        report = json.loads(stdout_buffer.getvalue())
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(report["sensitive_leak_detected"])
        self.assertTrue(report["forbidden_tokens"])


if __name__ == "__main__":
    unittest.main()
