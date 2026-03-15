from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.notification.trigger import should_notify


class NotificationTriggerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = SimpleNamespace(
            CONFIDENCE_LONG_MIN=40,
            CONFIDENCE_SHORT_MIN=70,
            CONFIDENCE_ALERT_CHANGE=10,
            ALERT_COOLDOWN_MINUTES=60,
            ATTENTION_ALERT_SCORE_MIN=55,
            ATTENTION_ALERT_GAP_MIN=15,
            ATTENTION_ALERT_COOLDOWN_MINUTES=60,
        )

    def test_notify_on_signal_tier_upgrade_even_in_cooldown(self) -> None:
        now = datetime.now(tz=timezone.utc)
        current = {
            "timestamp_utc": now.isoformat().replace("+00:00", "Z"),
            "bias": "long",
            "confidence": 80,
            "primary_setup_status": "ready",
            "prelabel": "ENTRY_OK",
            "agreement_with_machine": "agree",
            "no_trade_flags": [],
            "signal_tier": "strong_machine",
        }
        last_result = {
            "bias": "long",
            "primary_setup_status": "ready",
            "prelabel": "ENTRY_OK",
        }
        last_notified = {
            "timestamp_utc": (now - timedelta(minutes=10)).isoformat().replace("+00:00", "Z"),
            "confidence": 80,
            "agreement_with_machine": "agree",
            "signal_tier": "normal",
        }

        decision = should_notify(current, last_result, last_notified, None, self.cfg)
        self.assertTrue(decision["notify"])
        self.assertIn("signal_tier_upgraded", decision["notify_reason_codes"])
        self.assertEqual(decision["notification_kind"], "main")

    def test_respect_cooldown_when_no_tier_upgrade(self) -> None:
        now = datetime.now(tz=timezone.utc)
        current = {
            "timestamp_utc": now.isoformat().replace("+00:00", "Z"),
            "bias": "long",
            "confidence": 80,
            "primary_setup_status": "ready",
            "prelabel": "ENTRY_OK",
            "agreement_with_machine": "agree",
            "no_trade_flags": [],
            "signal_tier": "normal",
        }
        last_result = {
            "bias": "long",
            "primary_setup_status": "ready",
            "prelabel": "ENTRY_OK",
        }
        last_notified = {
            "timestamp_utc": (now - timedelta(minutes=10)).isoformat().replace("+00:00", "Z"),
            "confidence": 80,
            "agreement_with_machine": "agree",
            "signal_tier": "normal",
        }

        decision = should_notify(current, last_result, last_notified, None, self.cfg)
        self.assertFalse(decision["notify"])
        self.assertEqual(decision["notify_reason_codes"], [])
        self.assertIn("no_material_change", decision["suppress_reason_codes"])
        self.assertEqual(decision["notification_kind"], "none")

    def test_attention_notify_for_long_early_signal(self) -> None:
        now = datetime.now(tz=timezone.utc)
        current = {
            "timestamp_utc": now.isoformat().replace("+00:00", "Z"),
            "bias": "long",
            "confidence": 4,
            "long_display_score": 59,
            "short_display_score": 38,
            "score_gap": 21,
            "primary_setup_status": "watch",
            "prelabel": "SWEEP_WAIT",
            "agreement_with_machine": "partial",
            "no_trade_flags": ["RR_insufficient"],
            "signal_tier": "normal",
        }
        last_result = {
            "bias": "wait",
            "long_display_score": 41,
            "short_display_score": 41,
            "score_gap": 0,
            "primary_setup_status": "none",
            "prelabel": "RISKY_ENTRY",
        }

        decision = should_notify(current, last_result, None, None, self.cfg)
        self.assertTrue(decision["notify"])
        self.assertEqual(decision["notification_kind"], "attention")
        self.assertIn("attention_bias_changed", decision["notify_reason_codes"])

    def test_attention_notify_for_short_early_signal(self) -> None:
        now = datetime.now(tz=timezone.utc)
        current = {
            "timestamp_utc": now.isoformat().replace("+00:00", "Z"),
            "bias": "short",
            "confidence": 25,
            "long_display_score": 32,
            "short_display_score": 57,
            "score_gap": -18,
            "primary_setup_status": "watch",
            "prelabel": "RISKY_ENTRY",
            "agreement_with_machine": "partial",
            "no_trade_flags": ["RR_insufficient"],
            "signal_tier": "normal",
        }
        last_result = {
            "bias": "wait",
            "long_display_score": 45,
            "short_display_score": 44,
            "score_gap": 1,
            "primary_setup_status": "none",
            "prelabel": "RISKY_ENTRY",
        }

        decision = should_notify(current, last_result, None, None, self.cfg)
        self.assertTrue(decision["notify"])
        self.assertEqual(decision["notification_kind"], "attention")
        self.assertIn("attention_bias_changed", decision["notify_reason_codes"])


if __name__ == "__main__":
    unittest.main()
