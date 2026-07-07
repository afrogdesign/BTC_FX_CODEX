from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai.summary import CURRENT_EMAIL_SUBJECT_PREFIX, build_summary_body, build_summary_subject  # noqa: E402
from src.notification.detail_page import build_notification_detail_html  # noqa: E402
from src.notification.followup import (  # noqa: E402
    FOLLOWUP_HUMAN_MESSAGE,
    FOLLOWUP_PUBLIC_LABEL,
    FOLLOWUP_SAFETY_BOUNDARY,
    build_followup_notification_context,
    evaluate_followup_notification,
)
from tests.test_notification_detail_page import _sample_detail_payload  # noqa: E402


def _followup_cfg() -> SimpleNamespace:
    return SimpleNamespace(
        FOLLOWUP_VALIDITY_MINUTES=60,
        FOLLOWUP_ALERT_COOLDOWN_MINUTES=60,
        FOLLOWUP_CONFIDENCE_DROP_MIN=10,
        CONFIDENCE_LONG_MIN=45,
        CONFIDENCE_SHORT_MIN=55,
        CONFIDENCE_ALERT_CHANGE=10,
        ALERT_COOLDOWN_MINUTES=60,
        ATTENTION_ALERT_SCORE_MIN=55,
        ATTENTION_ALERT_GAP_MIN=15,
        ATTENTION_ALERT_COOLDOWN_MINUTES=60,
    )


def _baseline_payload(*, side: str, signal_id: str, timestamp_utc: str, notified_at_utc: str | None = None, confidence: int = 74) -> dict[str, object]:
    return {
        "signal_id": signal_id,
        "notification_kind": "main" if side in {"long", "short"} else "attention",
        "bias": side,
        "timestamp_utc": timestamp_utc,
        "notified_at_utc": notified_at_utc or timestamp_utc,
        "confidence": confidence,
    }


def _current_payload(timestamp_utc: str, *, bias: str, signals_1h: str, confidence: int = 58) -> dict[str, object]:
    return {
        "signal_id": "20260706_010500",
        "timestamp_utc": timestamp_utc,
        "timestamp_jst": "2026-07-06T10:10:00+09:00",
        "notification_kind": "none",
        "bias": bias,
        "signals_1h": signals_1h,
        "confidence": confidence,
        "primary_setup_status": "watch",
        "primary_setup_reason": "next_condition_pending",
        "long_setup": {"status": "invalid"},
        "short_setup": {"status": "watch"},
        "market_map_flags": [],
        "level_flip_state": "",
        "trend_flip_state": "",
        "current_price": 65817.7,
    }


class ValueDefenseFollowupObservationTest(unittest.TestCase):
    def test_expired_attention_baseline_creates_followup_even_when_current_bias_is_wait(self) -> None:
        cfg = _followup_cfg()
        baseline = _baseline_payload(
            side="long",
            signal_id="20260705_220500",
            timestamp_utc="2026-07-05T13:05:00Z",
            confidence=76,
        )
        baseline["notification_kind"] = "attention"
        current = _current_payload("2026-07-05T14:10:00Z", bias="wait", signals_1h="wait")

        evaluation = evaluate_followup_notification(current, None, baseline, None, cfg)

        self.assertTrue(evaluation["followup_needed"])
        self.assertEqual(evaluation["previous_signal_id"], "20260705_220500")
        self.assertIn("validity_expired", evaluation["reason_codes"])
        self.assertIn("prior_long_bias_lost", evaluation["reason_codes"])
        self.assertIn("prior_long_1h_weakened", evaluation["reason_codes"])
        self.assertEqual(evaluation["safety_boundary"], FOLLOWUP_SAFETY_BOUNDARY)
        self.assertIn("report-only / no automatic order / human decides manually", evaluation["human_message"])

    def test_expired_long_baseline_with_weakenings_produces_reason_codes(self) -> None:
        cfg = _followup_cfg()
        baseline = _baseline_payload(
            side="long",
            signal_id="20260705_180500",
            timestamp_utc="2026-07-05T09:05:00Z",
            confidence=74,
        )
        current = _current_payload("2026-07-05T10:45:00Z", bias="wait", signals_1h="wait", confidence=58)
        current["market_map_flags"] = ["support_to_resistance_flip", "resistance_to_support_retest_confirmed"]
        current["level_flip_state"] = "support_to_resistance_retest_confirmed"
        current["trend_flip_state"] = "trend_flip_early_down"
        current["long_setup"] = {"status": "invalid"}

        evaluation = evaluate_followup_notification(current, baseline, None, None, cfg)

        self.assertTrue(evaluation["followup_needed"])
        self.assertTrue({"prior_long_1h_weakened", "prior_long_support_to_resistance", "prior_long_trend_flip_early_down"}.issubset(evaluation["reason_codes"]))
        self.assertIn("prior_long_confidence_drop", evaluation["reason_codes"])
        self.assertIn("prior_long_setup_invalid", evaluation["reason_codes"])

    def test_not_expired_baseline_does_not_create_followup(self) -> None:
        cfg = _followup_cfg()
        baseline = _baseline_payload(
            side="short",
            signal_id="20260705_220500",
            timestamp_utc="2026-07-05T13:05:00Z",
            confidence=74,
        )
        current = _current_payload("2026-07-05T13:50:00Z", bias="wait", signals_1h="wait")

        evaluation = evaluate_followup_notification(current, None, baseline, None, cfg)

        self.assertFalse(evaluation["followup_needed"])
        self.assertEqual(evaluation["reason_codes"], [])

    def test_same_baseline_already_followed_is_suppressed(self) -> None:
        cfg = _followup_cfg()
        baseline = _baseline_payload(
            side="long",
            signal_id="20260705_220500",
            timestamp_utc="2026-07-05T12:00:00Z",
            confidence=74,
        )
        current = _current_payload("2026-07-05T13:15:00Z", bias="wait", signals_1h="wait")
        last_followup = {
            "signal_id": "20260705_230500",
            "followup_for_signal_id": "20260705_220500",
            "timestamp_utc": "2026-07-05T12:40:00Z",
        }

        evaluation = evaluate_followup_notification(current, None, baseline, last_followup, cfg)

        self.assertFalse(evaluation["followup_needed"])
        self.assertEqual(evaluation["followup_for_signal_id"], "20260705_220500")

    def test_followup_summary_and_detail_render_safety_text(self) -> None:
        cfg = _followup_cfg()
        baseline = _baseline_payload(
            side="long",
            signal_id="20260705_220500",
            timestamp_utc="2026-07-05T12:05:00Z",
            confidence=74,
        )
        current = _sample_detail_payload()
        current.update(
            {
                "signal_id": "20260705_230500",
                "timestamp_utc": "2026-07-05T14:10:00Z",
                "timestamp_jst": "2026-07-05T23:10:00+09:00",
                "notification_kind": "followup",
                "bias": "wait",
                "signals_1h": "wait",
                "confidence": 57,
                "long_setup": {"status": "invalid"},
            }
        )
        evaluation = evaluate_followup_notification(current, None, baseline, None, cfg)
        current["followup_context"] = evaluation
        current["summary_subject"] = build_summary_subject(current)

        body, provider = build_summary_body(
            provider="api",
            api_key="x",
            model="gpt-4o",
            cli_command="",
            timeout_sec=1,
            retry_count=0,
            base_dir=BASE_DIR,
            result_payload=current,
        )
        html = build_notification_detail_html(current)

        self.assertEqual(provider, "api")
        self.assertTrue(current["summary_subject"].startswith(CURRENT_EMAIL_SUBJECT_PREFIX))
        self.assertIn("⏱期限切れ", current["summary_subject"])
        self.assertIn("前回通知は失効。新規根拠として使わない。", body)
        self.assertIn("report-only / no automatic order / human decides manually", body)
        self.assertIn(FOLLOWUP_PUBLIC_LABEL, html)
        self.assertIn("前回通知の有効期限", html)
        self.assertIn("再評価中", html)
        self.assertIn("安全境界", html)


if __name__ == "__main__":
    unittest.main()
