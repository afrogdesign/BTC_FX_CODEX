from __future__ import annotations

import json
import os
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import config
import tools.safe_config_schema_audit as safe_config_schema_audit


class SafeConfigSchemaAuditTest(unittest.TestCase):
    def test_stdout_json_reports_static_schema(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)
            (cwd / ".env").write_text(
                "\n".join(
                    [
                        "OPENAI_API_KEY=env-openai-secret",
                        "SMTP_PASSWORD=env-smtp-secret",
                        "SMTP_USER=env-smtp-user",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env.update(
                {
                    "OPENAI_API_KEY": "process-openai-secret",
                    "SMTP_PASSWORD": "process-smtp-secret",
                    "SMTP_USER": "process-smtp-user",
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "tools" / "safe_config_schema_audit.py"),
                    "--stdout-json",
                ],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], "safe_config_schema_audit.v1")
        self.assertIn("OPENAI_API_KEY", payload["required_keys"])
        self.assertIn("SMTP_HOST", payload["required_keys"])
        self.assertIn("SMTP_PORT", payload["required_keys"])
        self.assertIn("SMTP_USER", payload["required_keys"])
        self.assertIn("SMTP_PASSWORD", payload["required_keys"])
        self.assertIn("MAIL_FROM", payload["required_keys"])
        self.assertIn("MAIL_TO", payload["required_keys"])
        self.assertIn("OPENAI_API_KEY", payload["masked_keys"])
        self.assertIn("SMTP_PASSWORD", payload["masked_keys"])
        self.assertIn("SMTP_USER", payload["masked_keys"])
        self.assertEqual(
            payload["accepted_prefixes"],
            ["MEXC_", "OPENAI_", "BINANCE_", "NOTIFICATION_HTML_"],
        )
        self.assertFalse(payload["reads_env_values"])
        self.assertFalse(payload["reads_dotenv_values"])
        self.assertFalse(payload["calls_private_endpoints"])
        self.assertFalse(payload["calls_order_endpoints"])
        self.assertFalse(payload["live_trading_allowed"])
        self.assertFalse(payload["secret_values_exposed"])
        self.assertIn("no load_config", payload["safety_boundary"])
        self.assertNotIn("env-openai-secret", result.stdout)
        self.assertNotIn("env-smtp-secret", result.stdout)
        self.assertNotIn("env-smtp-user", result.stdout)
        self.assertNotIn("process-openai-secret", result.stdout)
        self.assertNotIn("process-smtp-secret", result.stdout)
        self.assertNotIn("process-smtp-user", result.stdout)

    def test_default_output_is_human_readable(self) -> None:
        with TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)
            (cwd / ".env").write_text(
                "\n".join(
                    [
                        "OPENAI_API_KEY=env-openai-secret",
                        "SMTP_PASSWORD=env-smtp-secret",
                        "SMTP_USER=env-smtp-user",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env.update(
                {
                    "OPENAI_API_KEY": "process-openai-secret",
                    "SMTP_PASSWORD": "process-smtp-secret",
                    "SMTP_USER": "process-smtp-user",
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "tools" / "safe_config_schema_audit.py"),
                ],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Safe Config Schema Audit", result.stdout)
        self.assertIn("schema_version: safe_config_schema_audit.v1", result.stdout)
        self.assertIn("required_keys:", result.stdout)
        self.assertIn("masked_keys:", result.stdout)
        self.assertIn("accepted_prefixes:", result.stdout)
        self.assertIn("safety_boundary:", result.stdout)
        self.assertNotIn("env-openai-secret", result.stdout)
        self.assertNotIn("env-smtp-secret", result.stdout)
        self.assertNotIn("env-smtp-user", result.stdout)
        self.assertNotIn("process-openai-secret", result.stdout)
        self.assertNotIn("process-smtp-secret", result.stdout)
        self.assertNotIn("process-smtp-user", result.stdout)

    def test_load_config_is_not_called(self) -> None:
        with patch.object(config, "load_config", side_effect=AssertionError("load_config must not be called")):
            buffer = StringIO()
            with redirect_stdout(buffer):
                exit_code = safe_config_schema_audit.main(["--stdout-json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["schema_version"], "safe_config_schema_audit.v1")


if __name__ == "__main__":
    unittest.main()
