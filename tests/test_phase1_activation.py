from __future__ import annotations

import unittest

from src.trade.activation import determine_phase1_activation


class Phase1ActivationTests(unittest.TestCase):
    def test_ready_setup_is_active(self) -> None:
        result = determine_phase1_activation(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="ready",
            data_quality_flag="ok",
            entry_price=70000,
            stop_loss_price=69500,
        )

        self.assertTrue(result["phase1_active"])
        self.assertEqual(result["phase1_activation_reason"], "ready_setup")

    def test_watch_setup_is_reference_only(self) -> None:
        result = determine_phase1_activation(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="watch",
            data_quality_flag="ok",
            entry_price=70000,
            stop_loss_price=69500,
        )

        self.assertFalse(result["phase1_active"])
        self.assertEqual(result["phase1_activation_reason"], "watch_reference_only")

    def test_partial_missing_blocks_activation(self) -> None:
        result = determine_phase1_activation(
            bias="short",
            primary_setup_side="short",
            primary_setup_status="ready",
            data_quality_flag="partial_missing",
            entry_price=70000,
            stop_loss_price=70500,
        )

        self.assertFalse(result["phase1_active"])
        self.assertEqual(result["phase1_activation_reason"], "partial_missing_data")


if __name__ == "__main__":
    unittest.main()
