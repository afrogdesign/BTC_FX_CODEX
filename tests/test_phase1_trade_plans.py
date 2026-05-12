from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.storage.csv_logger import append_observation_paper_order, append_paper_order
from src.trade.execution_gate import determine_trade_execution_gate
from src.trade.exit_manager import build_exit_plan, build_shadow_exit_plan
from src.trade.observation_gate import determine_phase1_observation_gate
from src.trade.position_sizing import build_position_size_plan


class Phase1TradePlanTests(unittest.TestCase):
    def test_position_sizing_applies_loss_streak_reduction_and_cap_for_strong_machine(self) -> None:
        plan = build_position_size_plan(
            account_balance=10000,
            entry_price=70000,
            stop_loss_price=69500,
            signal_tier="strong_machine",
            loss_streak=2,
            base_risk_pct=0.5,
            loss_streak_step_pct=0.1,
            min_risk_pct=0.2,
            max_position_size_usd=3000,
        )

        self.assertEqual(plan["risk_percent_applied"], 0.3)
        self.assertEqual(plan["planned_risk_usd"], 30.0)
        self.assertEqual(plan["position_size_usd"], 3000.0)
        self.assertTrue(plan["max_size_capped"])
        self.assertIn("strong_tier_kept_flat", plan["size_reduction_reasons"])
        self.assertIn("loss_streak_risk_reduced", plan["size_reduction_reasons"])

    def test_position_sizing_does_not_treat_removed_ai_tier_as_strong(self) -> None:
        plan = build_position_size_plan(
            account_balance=10000,
            entry_price=70000,
            stop_loss_price=69500,
            signal_tier="strong_ai_confirmed",
            loss_streak=0,
            base_risk_pct=0.5,
            loss_streak_step_pct=0.1,
            min_risk_pct=0.2,
            max_position_size_usd=3000,
        )

        self.assertNotIn("strong_tier_kept_flat", plan["size_reduction_reasons"])
        self.assertNotIn("loss_streak_risk_reduced", plan["size_reduction_reasons"])

    def test_exit_plan_builds_prices_from_r_multiple(self) -> None:
        plan = build_exit_plan(
            side="long",
            entry_price=70000,
            stop_loss_price=69500,
            atr=180,
            tp1_rr_multiple=1.0,
            tp2_rr_multiple=2.0,
            trail_atr_multiplier=1.5,
            timeout_hours=12,
            exit_rule_version="phase1_v0",
        )

        self.assertEqual(plan["tp1_price"], 70500.0)
        self.assertEqual(plan["tp2_price"], 71000.0)
        self.assertTrue(plan["breakeven_after_tp1"])
        self.assertEqual(plan["trail_atr_multiplier"], 1.5)
        self.assertEqual(plan["timeout_hours"], 12)

    def test_shadow_exit_plan_uses_wider_phase1_v1_targets(self) -> None:
        long_plan = build_shadow_exit_plan(
            side="long",
            entry_price=70000,
            stop_loss_price=69500,
            atr=180,
            trail_atr_multiplier=1.5,
            timeout_hours=12,
        )
        short_plan = build_shadow_exit_plan(
            side="short",
            entry_price=70000,
            stop_loss_price=70500,
            atr=180,
            trail_atr_multiplier=1.5,
            timeout_hours=12,
        )

        self.assertEqual(long_plan["shadow_tp1_price"], 70650.0)
        self.assertEqual(long_plan["shadow_tp2_price"], 71200.0)
        self.assertEqual(short_plan["shadow_tp1_price"], 69350.0)
        self.assertEqual(short_plan["shadow_tp2_price"], 68800.0)
        self.assertEqual(long_plan["shadow_exit_rule_version"], "phase1_v1_shadow")

    def test_execution_gate_blocks_rr_and_weak_execution(self) -> None:
        result = determine_trade_execution_gate(
            phase1_active=True,
            primary_setup_status="ready",
            primary_setup_reason="rr_below_min",
            data_quality_flag="ok",
            no_trade_flags=[],
            confidence_execution_shadow=20,
            confidence_wait_shadow=60,
        )

        self.assertEqual(result["trade_execution_gate"], "blocked")
        self.assertIn("rr_below_min", result["trade_execution_blockers"])
        self.assertIn("execution_shadow_too_low", result["trade_execution_blockers"])
        self.assertIn("wait_pressure_too_high", result["trade_execution_blockers"])

    def test_execution_gate_passes_clean_ready_setup(self) -> None:
        result = determine_trade_execution_gate(
            phase1_active=True,
            primary_setup_status="ready",
            primary_setup_reason="inside_entry_zone_with_trigger",
            data_quality_flag="ok",
            no_trade_flags=[],
            confidence_execution_shadow=45,
            confidence_wait_shadow=20,
        )

        self.assertEqual(result["trade_execution_gate"], "pass")
        self.assertEqual(result["trade_execution_blockers"], [])

    def test_observation_gate_passes_rr_learning_with_direction_value(self) -> None:
        result = determine_phase1_observation_gate(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="invalid",
            primary_setup_reason="rr_below_min",
            prelabel="ENTRY_OK",
            data_quality_flag="ok",
            no_trade_flags=["RR_insufficient"],
            risk_flags=[],
            confidence_direction_shadow=35,
            confidence_execution_shadow=5,
            confidence_wait_shadow=95,
        )

        self.assertEqual(result["phase1_observation_gate"], "pass")
        self.assertEqual(result["phase1_observation_type"], "direction_rr_learning")
        self.assertEqual(result["phase1_observation_reasons"], ["direction_rr_learning"])

    def test_observation_gate_blocks_confidence_below_min(self) -> None:
        result = determine_phase1_observation_gate(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="watch",
            primary_setup_reason="confidence_below_min",
            prelabel="SWEEP_WAIT",
            data_quality_flag="ok",
            no_trade_flags=[],
            risk_flags=["sweep_incomplete", "lower_liquidity_close", "orderbook_ask_heavy"],
            confidence_direction_shadow=70,
            confidence_execution_shadow=40,
            confidence_wait_shadow=40,
        )

        self.assertEqual(result["phase1_observation_gate"], "blocked")
        self.assertIn("confidence_below_min", result["phase1_observation_reasons"])

    def test_observation_gate_passes_watch_learning(self) -> None:
        result = determine_phase1_observation_gate(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="watch",
            primary_setup_reason="entry_zone_not_reached",
            prelabel="SWEEP_WAIT",
            data_quality_flag="ok",
            no_trade_flags=[],
            risk_flags=[],
            confidence_direction_shadow=55,
            confidence_execution_shadow=20,
            confidence_wait_shadow=75,
        )

        self.assertEqual(result["phase1_observation_gate"], "pass")
        self.assertEqual(result["phase1_observation_type"], "setup_watch_learning")

    def test_observation_gate_blocks_fatal_no_trade_candidates(self) -> None:
        result = determine_phase1_observation_gate(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="watch",
            primary_setup_reason="entry_zone_not_reached",
            prelabel="NO_TRADE_CANDIDATE",
            data_quality_flag="ok",
            no_trade_flags=["ATR_extreme"],
            risk_flags=[],
            confidence_direction_shadow=80,
            confidence_execution_shadow=40,
            confidence_wait_shadow=20,
        )

        self.assertEqual(result["phase1_observation_gate"], "blocked")
        self.assertIn("no_trade_candidate", result["phase1_observation_reasons"])
        self.assertIn("ATR_extreme", result["phase1_observation_reasons"])

    def test_observation_gate_passes_confidence_watch_learning_candidate(self) -> None:
        result = determine_phase1_observation_gate(
            bias="long",
            primary_setup_side="long",
            primary_setup_status="watch",
            primary_setup_reason="confidence_below_min",
            prelabel="SWEEP_WAIT",
            data_quality_flag="ok",
            no_trade_flags=[],
            risk_flags=["sweep_incomplete", "lower_liquidity_close"],
            confidence_direction_shadow=58,
            confidence_execution_shadow=22,
            confidence_wait_shadow=80,
        )

        self.assertEqual(result["phase1_observation_gate"], "pass")
        self.assertEqual(result["phase1_observation_type"], "confidence_watch_learning")

    def test_append_paper_order_is_idempotent_by_signal_id(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            payload = {
                "signal_id": "paper_1",
                "timestamp_jst": "2026-04-17T10:00:00+09:00",
                "primary_setup_side": "long",
                "primary_entry_mid": 70000,
                "primary_stop_loss": 69500,
                "shadow_tp1_price": 70650,
                "shadow_tp2_price": 71200,
                "risk_percent_applied": 0.5,
                "planned_risk_usd": 50,
                "position_size_usd": 3000,
                "shadow_exit_rule_version": "phase1_v1_shadow",
                "trade_execution_gate": "pass",
                "trade_execution_blockers": [],
                "paper_order_status": "planned",
            }

            path = append_paper_order(base_dir, payload)
            append_paper_order(base_dir, payload)

            rows = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(rows), 2)
            self.assertIn("paper_1", rows[1])

    def test_append_observation_paper_order_is_separate_from_execution_orders(self) -> None:
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            payload = {
                "signal_id": "obs_1",
                "timestamp_jst": "2026-04-22T10:00:00+09:00",
                "current_price": 70000,
                "primary_setup_side": "long",
                "primary_entry_mid": 69900,
                "primary_stop_loss": 69500,
                "shadow_tp1_price": 70420,
                "shadow_tp2_price": 70860,
                "rr_estimate": 1.3,
                "prelabel": "RISKY_ENTRY",
                "primary_setup_status": "watch",
                "primary_setup_reason": "entry_zone_not_reached",
                "phase1_observation_gate": "pass",
                "phase1_observation_type": "setup_watch_learning",
                "phase1_observation_reasons": ["setup_watch_learning"],
                "confidence_direction_shadow": 60,
                "confidence_execution_shadow": 22,
                "confidence_wait_shadow": 70,
                "trade_execution_gate": "blocked",
            }

            path = append_observation_paper_order(base_dir, payload)
            append_observation_paper_order(base_dir, payload)

            rows = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(rows), 2)
            self.assertIn("phase1A", rows[1])
            self.assertFalse((base_dir / "logs" / "csv" / "paper_orders.csv").exists())


if __name__ == "__main__":
    unittest.main()
