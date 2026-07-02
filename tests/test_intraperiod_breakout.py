from __future__ import annotations

import inspect
import sys
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.notification.intraperiod_breakout import build_intraperiod_breakout_alert_candidate


def _base_result() -> dict[str, object]:
    return {
        "momentum_confirmation_flags": [],
        "breakout_inversion_flags": [],
        "warning_flags": [],
    }


class IntraperiodBreakoutTest(unittest.TestCase):
    def test_upside_candidate_from_momentum_and_short_risk(self) -> None:
        result = _base_result()
        result["momentum_confirmation_flags"] = ["upside_momentum_confirmed", "upside_macd_confirmed"]
        result["breakout_inversion_flags"] = ["upside_breakout_follow_watch", "short_invalidation_watch"]

        candidate = build_intraperiod_breakout_alert_candidate(result)

        self.assertEqual(candidate["status"], "candidate")
        self.assertEqual(candidate["side"], "upside")
        self.assertIn("upside_momentum_confirmed", candidate["reason_codes"])
        self.assertIn("short_invalidation_watch", candidate["reason_codes"])
        self.assertFalse(candidate["real_mail_sent"])
        self.assertFalse(candidate["automatic_order"])
        self.assertIn("report-only", candidate["safety_boundary"])

    def test_downside_candidate_from_momentum_and_long_risk(self) -> None:
        result = _base_result()
        result["momentum_confirmation_flags"] = ["downside_momentum_confirmed", "downside_macd_confirmed"]
        result["breakout_inversion_flags"] = ["downside_breakdown_follow_watch", "long_invalidation_watch"]

        candidate = build_intraperiod_breakout_alert_candidate(result)

        self.assertEqual(candidate["status"], "candidate")
        self.assertEqual(candidate["side"], "downside")
        self.assertIn("downside_momentum_confirmed", candidate["reason_codes"])
        self.assertIn("long_invalidation_watch", candidate["reason_codes"])
        self.assertFalse(candidate["real_mail_sent"])
        self.assertFalse(candidate["automatic_order"])

    def test_no_candidate_for_weak_flags(self) -> None:
        candidate = build_intraperiod_breakout_alert_candidate(_base_result())

        self.assertEqual(candidate["status"], "none")
        self.assertEqual(candidate["side"], "none")
        self.assertEqual(candidate["reason_codes"], [])
        self.assertFalse(candidate["real_mail_sent"])
        self.assertFalse(candidate["automatic_order"])

    def test_both_side_conflict_remains_report_only(self) -> None:
        result = _base_result()
        result["momentum_confirmation_flags"] = [
            "upside_momentum_confirmed",
            "downside_momentum_confirmed",
            "upside_macd_confirmed",
            "downside_macd_confirmed",
        ]
        result["breakout_inversion_flags"] = [
            "upside_breakout_follow_watch",
            "short_invalidation_watch",
            "downside_breakdown_follow_watch",
            "long_invalidation_watch",
        ]

        candidate = build_intraperiod_breakout_alert_candidate(result)

        self.assertEqual(candidate["status"], "candidate")
        self.assertEqual(candidate["side"], "both")
        self.assertEqual(candidate["severity"], "warning")
        self.assertFalse(candidate["real_mail_sent"])
        self.assertFalse(candidate["automatic_order"])
        self.assertIn("short_invalidation_watch", candidate["reason_codes"])
        self.assertIn("long_invalidation_watch", candidate["reason_codes"])

    def test_builder_has_no_send_side_effects(self) -> None:
        import src.notification.intraperiod_breakout as module

        source = inspect.getsource(module)
        self.assertNotIn("send_email", source)
        self.assertNotIn("save_pending_email", source)
