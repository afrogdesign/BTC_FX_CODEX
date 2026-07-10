from __future__ import annotations

import copy
import json
import unittest

from src.feedback.manual_operator_shadow_surface import build_manual_operator_shadow_surface


class ManualOperatorShadowSurfaceTests(unittest.TestCase):
    def payload(self) -> dict[str, object]:
        return {"timestamp_jst": "2026-07-10T10:00:00+09:00", "signal_id": "sig1", "current_price": 70000, "bias": "long", "primary_setup_status": "ready", "confidence_direction_shadow": 65, "confidence_execution_shadow": 30, "confidence_wait_shadow": 40, "long_rr": 2, "short_rr": 2, "no_trade_flags": [], "warning_flags": [], "risk_flags": [], "active_trade_plan": {"side_plans": {"long": {"bias_alignment": "primary", "market_entry_status": "allowed", "entry_mid": 70000, "stop_loss": 69500, "tp1": 70500, "tp2": 71000, "rr_zone_mid_tp1": 1.2, "rr_zone_mid_tp2": 2.0}}}}

    def test_deterministic_sanitized_row(self) -> None:
        payload = self.payload(); first = build_manual_operator_shadow_surface(payload); second = build_manual_operator_shadow_surface(payload); self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)); self.assertEqual(first["surface_status"], "ready"); self.assertTrue(first["rows"])
        self.assertNotIn("candidate_id", first["rows"][0]); self.assertNotIn("sig1", json.dumps(first))

    def test_no_candidate_insufficient_and_malformed_fail_closed(self) -> None:
        payload = self.payload(); payload["active_trade_plan"] = {}; self.assertEqual(build_manual_operator_shadow_surface(payload)["surface_status"], "no_current_candidate")
        payload = self.payload(); payload["confidence_direction_shadow"] = "bad"; self.assertIn(build_manual_operator_shadow_surface(payload)["surface_status"], {"insufficient_evidence", "ready"})
        self.assertEqual(build_manual_operator_shadow_surface(None)["surface_status"], "malformed")

    def test_input_not_mutated_and_allowed_fields(self) -> None:
        payload = self.payload(); original = copy.deepcopy(payload); output = build_manual_operator_shadow_surface(payload); self.assertEqual(payload, original)
        allowed = {"shadow_row_id", "classification_status", "operator_class", "side", "candidate_type", "candidate_status", "required_human_check", "reason_codes", "warning_codes", "trade_execution_gate", "phase1b_lite_gate", "opportunity_gate", "entry_price", "entry_zone_low", "entry_zone_high", "invalidation_price", "tp1_price", "tp2_price"}
        for row in output["rows"]: self.assertTrue(set(row) <= allowed)


if __name__ == "__main__": unittest.main()
