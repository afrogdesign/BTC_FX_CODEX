from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import load_config  # noqa: E402
from main import run_cycle  # noqa: E402
from src.data.exchange_fetcher import MarketStructureSnapshot  # noqa: E402
from src.notification.trigger import should_notify  # noqa: E402
from tests.test_notification_detail_page import _sample_df  # noqa: E402


def _followup_cfg() -> SimpleNamespace:
    return SimpleNamespace(
        CONFIDENCE_LONG_MIN=45,
        CONFIDENCE_SHORT_MIN=55,
        CONFIDENCE_ALERT_CHANGE=10,
        ALERT_COOLDOWN_MINUTES=60,
        ATTENTION_ALERT_SCORE_MIN=55,
        ATTENTION_ALERT_GAP_MIN=15,
        ATTENTION_ALERT_COOLDOWN_MINUTES=60,
        FOLLOWUP_VALIDITY_MINUTES=60,
        FOLLOWUP_ALERT_COOLDOWN_MINUTES=60,
        FOLLOWUP_CONFIDENCE_DROP_MIN=10,
    )


class NotificationTriggerFollowupTest(unittest.TestCase):
    def test_trigger_returns_followup_when_main_and_attention_do_not_fire(self) -> None:
        cfg = _followup_cfg()
        current = {
            "signal_id": "20260705_230500",
            "timestamp_utc": "2026-07-05T14:10:00Z",
            "bias": "wait",
            "signals_1h": "wait",
            "confidence": 58,
            "primary_setup_status": "watch",
            "primary_setup_reason": "next_condition_pending",
            "long_setup": {"status": "invalid"},
            "short_setup": {"status": "watch"},
        }
        last_result = {"bias": "wait"}
        last_primary_notified = {
            "signal_id": "20260705_220500",
            "notification_kind": "main",
            "bias": "long",
            "timestamp_utc": "2026-07-05T12:05:00Z",
            "notified_at_utc": "2026-07-05T12:05:00Z",
            "confidence": 74,
        }

        decision = should_notify(current, last_result, last_primary_notified, None, cfg, None)

        self.assertTrue(decision["notify"])
        self.assertEqual(decision["notification_kind"], "followup")
        self.assertIn("validity_expired", decision["notify_reason_codes"])
        self.assertEqual(decision["followup_context"]["previous_signal_id"], "20260705_220500")
        self.assertEqual(decision["followup_context"]["safety_boundary"], "report-only / no automatic order / human decides manually")

    def test_run_cycle_persists_followup_state_to_dedicated_file(self) -> None:
        required_env = {
            "OPENAI_API_KEY": "x",
            "SMTP_HOST": "smtp",
            "SMTP_PORT": "587",
            "SMTP_USER": "u",
            "SMTP_PASSWORD": "p",
            "MAIL_FROM": "a@example.com",
            "MAIL_TO": "b@example.com",
            "NOTIFICATION_HTML_ENABLED": "true",
        }
        cfg = _followup_cfg()
        df = _sample_df()
        save_paths: list[Path] = []
        followup_context = {
            "followup_needed": True,
            "followup_kind": "followup",
            "previous_signal_id": "20260705_220500",
            "previous_notification_kind": "main",
            "valid_until_utc": "2026-07-05T13:05:00Z",
            "reason_codes": ["validity_expired"],
            "reason_labels": ["有効期限切れ"],
            "subject_hint": "⏱️ [期限切れ・再評価] 前回通知の有効期限切れ / 根拠再確認",
            "human_message": "前回通知は有効期限切れです。 保有中の場合は、15分足と1時間足で撤退・建値・損切り確認。 未保有の場合は、前回通知を新規根拠として使わない。 report-only / no automatic order / human decides manually",
            "safety_boundary": "report-only / no automatic order / human decides manually",
            "followup_for_signal_id": "20260705_220500",
        }

        def _capture_save_json(path: Path, payload: dict[str, object]) -> None:
            del payload
            save_paths.append(Path(path))

        with TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, required_env, clear=False):
                runtime_cfg = load_config(Path(tmp_dir))
            with patch("main.get_server_time_ms", return_value=1_700_000_000_000), patch(
                "main.fetch_klines", side_effect=[df, df, df]
            ), patch("main.validate_klines", return_value=True), patch(
                "main.fetch_market_structure", return_value=MarketStructureSnapshot(missing_fields=[])
            ), patch("main.fetch_funding_rate", return_value=0.0), patch(
                "main.resend_pending_email", return_value=None
            ), patch("main.cleanup_if_due", return_value=None), patch(
                "main.request_ai_advice",
                return_value=(
                    {
                        "verdict": "caution",
                        "agreement": "caution",
                        "reason": "stub",
                        "unique_risks": ["followup"],
                        "next_review_focus": "期限切れ確認",
                    },
                    "api",
                ),
            ), patch("main.build_summary_body", return_value=("summary body", "api")), patch(
                "main.build_summary_subject", return_value="subject"
            ), patch(
                "main.should_notify",
                return_value={
                    "notify": True,
                    "notify_reason_codes": ["validity_expired"],
                    "suppress_reason_codes": [],
                    "notification_kind": "followup",
                    "followup_context": followup_context,
                },
            ), patch(
                "main.publish_notification_detail",
                return_value={
                    "detail_page_enabled": True,
                    "detail_page_status": "published",
                    "detail_page_url": "https://server.afrog.jp/btc-monitor/notifications/manual-trading/followup/20260705_230500.html",
                    "detail_page_local_path": "/tmp/20260705_230500.html",
                    "detail_page_published_at_utc": "2026-07-05T14:10:00Z",
                },
            ), patch("main.send_email", return_value=None), patch(
                "main.append_trade_log", return_value=Path(tmp_dir) / "logs" / "csv" / "trades.csv"
            ), patch(
                "main.save_signal_snapshot", return_value=Path(tmp_dir) / "logs" / "signals" / "x.json"
            ), patch("main.save_json", side_effect=_capture_save_json):
                result = run_cycle(cfg=runtime_cfg, base_dir=Path(tmp_dir))

        self.assertEqual(result["notification_kind"], "followup")
        self.assertTrue(any(path.name == "last_followup_notified.json" for path in save_paths))
        self.assertFalse(any(path.name == "last_notified.json" for path in save_paths))


if __name__ == "__main__":
    unittest.main()
