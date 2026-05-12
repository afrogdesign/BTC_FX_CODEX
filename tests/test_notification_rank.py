from __future__ import annotations

import sys
from itertools import product
from pathlib import Path
import unittest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.presentation.sanitize import build_notification_context


class NotificationRankTest(unittest.TestCase):
    def test_final_rank_examples_are_human_readable(self) -> None:
        cases = [
            (
                {
                    "bias": "long",
                    "notification_kind": "main",
                    "primary_setup_status": "ready",
                    "prelabel": "ENTRY_OK",
                    "signal_tier": "strong_machine",
                    "confidence": 80,
                    "rr_estimate": 1.9,
                    "score_gap": 28,
                },
                ("strong_main", "強い本通知", "🔥"),
            ),
            (
                {
                    "bias": "short",
                    "notification_kind": "main",
                    "primary_setup_status": "watch",
                    "prelabel": "SWEEP_WAIT",
                    "signal_tier": "normal",
                    "confidence": 66,
                    "rr_estimate": 1.2,
                    "score_gap": -18,
                },
                ("high_main", "高め本通知", "🟠"),
            ),
            (
                {
                    "bias": "short",
                    "notification_kind": "main",
                    "primary_setup_status": "invalid",
                    "prelabel": "SWEEP_WAIT",
                    "signal_tier": "normal",
                    "confidence": 60,
                    "rr_estimate": 0.9,
                    "score_gap": -12,
                },
                ("normal_main", "通常の本通知", "📊"),
            ),
            (
                {
                    "bias": "short",
                    "notification_kind": "attention",
                    "primary_setup_status": "watch",
                    "prelabel": "SWEEP_WAIT",
                    "signal_tier": "normal",
                    "confidence": 41,
                    "rr_estimate": 0.9,
                    "score_gap": -21,
                },
                ("attention", "注意報", "👀"),
            ),
            (
                {
                    "bias": "wait",
                    "notification_kind": "none",
                    "primary_setup_status": "none",
                    "prelabel": "NO_TRADE_CANDIDATE",
                    "signal_tier": "normal",
                    "confidence": 20,
                    "rr_estimate": 0.8,
                    "score_gap": 0,
                },
                ("no_send", "送信なし", "⚪"),
            ),
        ]

        for payload, expected in cases:
            ctx = build_notification_context(payload)
            self.assertEqual(
                (ctx["final_rank_code"], ctx["final_rank_label"], ctx["final_rank_emoji"]),
                expected,
            )

    def test_main_rank_is_downgraded_when_execution_is_low_and_wait_is_high(self) -> None:
        ctx = build_notification_context(
            {
                "bias": "long",
                "notification_kind": "main",
                "primary_setup_status": "ready",
                "prelabel": "ENTRY_OK",
                "signal_tier": "strong_machine",
                "confidence": 82,
                "rr_estimate": 1.9,
                "score_gap": 30,
                "confidence_execution_shadow": 18,
                "confidence_wait_shadow": 72,
            }
        )
        self.assertEqual(
            (ctx["final_rank_code"], ctx["final_rank_label"], ctx["final_rank_emoji"]),
            ("normal_main", "通常の本通知", "📊"),
        )

    def test_main_rank_is_downgraded_when_long_reversal_risk_is_present(self) -> None:
        ctx = build_notification_context(
            {
                "bias": "long",
                "notification_kind": "main",
                "primary_setup_status": "watch",
                "primary_setup_reason": "entry_zone_not_reached",
                "prelabel": "ENTRY_OK",
                "trade_execution_gate": "blocked",
                "signal_tier": "normal",
                "confidence": 68,
                "rr_estimate": 1.35,
                "score_gap": 42,
                "risk_flags": ["sweep_incomplete", "lower_liquidity_close", "long_reversal_risk"],
            }
        )
        self.assertEqual(
            (ctx["final_rank_code"], ctx["final_rank_label"], ctx["final_rank_emoji"]),
            ("normal_main", "通常の本通知", "📊"),
        )

    def test_final_rank_is_always_one_of_five_known_values(self) -> None:
        expected_codes = {"strong_main", "high_main", "normal_main", "attention", "no_send"}
        seen_codes: set[str] = set()
        biases = ["wait", "long", "short"]
        notification_kinds = ["none", "main", "attention"]
        statuses = ["none", "invalid", "watch", "ready"]
        prelabels = ["NO_TRADE_CANDIDATE", "SWEEP_WAIT", "RISKY_ENTRY", "ENTRY_OK"]
        signal_tiers = ["normal", "strong_machine"]
        confidences = [30, 45, 55, 63, 75]
        rrs = [0.9, 1.2, 1.35, 1.85]
        gaps = [0, 12, 18, 30]

        for bias, kind, status, prelabel, tier, confidence, rr_estimate, gap in product(
            biases, notification_kinds, statuses, prelabels, signal_tiers, confidences, rrs, gaps
        ):
            payload = {
                "bias": bias,
                "notification_kind": kind,
                "primary_setup_status": status,
                "prelabel": prelabel,
                "signal_tier": tier,
                "confidence": confidence,
                "rr_estimate": rr_estimate,
                "score_gap": gap if bias != "short" else -gap,
            }
            ctx = build_notification_context(payload)
            seen_codes.add(ctx["final_rank_code"])
            self.assertIn(ctx["final_rank_code"], expected_codes)
            self.assertTrue(ctx["final_rank_label"])
            self.assertTrue(ctx["final_rank_emoji"])

        self.assertEqual(seen_codes, expected_codes)


if __name__ == "__main__":
    unittest.main()
