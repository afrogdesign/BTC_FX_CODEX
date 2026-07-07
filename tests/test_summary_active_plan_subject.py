from __future__ import annotations

import unittest

from src.ai.summary import CURRENT_EMAIL_SUBJECT_PREFIX, build_summary_subject


class SummaryActivePlanSubjectTests(unittest.TestCase):
    def _base_payload(self) -> dict[str, object]:
        return {
            "timestamp_jst": "2026-06-07T09:05:00+09:00",
            "notification_kind": "main",
            "bias": "short",
            "signal_tier": "normal",
            "primary_setup_status": "watch",
            "primary_setup_reason": "entry_zone_not_reached",
            "trade_execution_gate": "blocked",
            "paper_order_status": "",
            "current_price": 60513.0,
            "confidence": 66,
            "score_gap": -18,
            "confidence_direction_shadow": 72.0,
            "confidence_execution_shadow": 18.0,
            "confidence_wait_shadow": 59.2,
        }

    def test_main_subject_is_compact(self) -> None:
        subject = build_summary_subject(self._base_payload())
        self.assertTrue(subject.startswith(f"{CURRENT_EMAIL_SUBJECT_PREFIX} 📊 結論 | "))
        self.assertIn("BTC 60,513", subject)
        self.assertNotIn("Ver", subject)
        self.assertNotIn("[CLI]", subject)
        self.assertNotIn("[API]", subject)

    def test_no_action_subject_is_compact(self) -> None:
        payload = self._base_payload()
        payload["active_primary_action"] = "NO_ACTION"
        subject = build_summary_subject(payload)
        self.assertTrue(subject.startswith(f"{CURRENT_EMAIL_SUBJECT_PREFIX} 📊 結論 | "))
        self.assertIn("BTC 60,513", subject)

    def test_formal_gate_pass_subject_is_paper_candidate(self) -> None:
        payload = self._base_payload()
        payload["trade_execution_gate"] = "pass"
        payload["paper_order_status"] = "planned"
        subject = build_summary_subject(payload)
        self.assertTrue(subject.startswith(f"{CURRENT_EMAIL_SUBJECT_PREFIX} 🧪 紙実行候補 | "))
        self.assertIn("実弾不可", subject)

    def test_attention_subject_is_compact(self) -> None:
        payload = self._base_payload()
        payload["notification_kind"] = "attention"
        subject = build_summary_subject(payload)
        self.assertTrue(subject.startswith(f"{CURRENT_EMAIL_SUBJECT_PREFIX} 👀 注意報 | "))
        self.assertIn("BTC 60,513", subject)


if __name__ == "__main__":
    unittest.main()
