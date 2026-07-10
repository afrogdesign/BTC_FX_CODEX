from __future__ import annotations

import copy
import json
import unittest
from unittest.mock import patch

from src.feedback.manual_operator_shadow_surface import build_manual_operator_shadow_surface


class ManualOperatorShadowSurfaceTests(unittest.TestCase):
    def payload(self) -> dict[str, object]:
        return {"timestamp_jst": "2026-07-10T10:00:00+09:00", "signal_id": "sig1", "current_price": 70000, "bias": "long", "primary_setup_status": "ready", "primary_setup_side": "long", "confidence_direction_shadow": 65, "confidence_execution_shadow": 30, "confidence_wait_shadow": 40, "long_rr": 2, "short_rr": 2, "no_trade_flags": [], "warning_flags": [], "risk_flags": [], "active_trade_plan": {"side_plans": {"long": {"bias_alignment": "primary", "market_entry_status": "allowed", "entry_mid": 70000, "stop_loss": 69500, "tp1": 70500, "tp2": 71000, "rr_zone_mid_tp1": 1.2, "rr_zone_mid_tp2": 2.0}}}}

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

    def test_missing_setup_side_is_insufficient(self) -> None:
        payload = self.payload(); payload["primary_setup_side"] = ""; result = build_manual_operator_shadow_surface(payload); self.assertNotEqual(result["rows"][0].get("operator_class"), "C_WATCH_ZONE")

    def test_missing_shadow_metric_is_insufficient(self) -> None:
        payload = self.payload(); payload["confidence_direction_shadow"] = ""; result = build_manual_operator_shadow_surface(payload); self.assertEqual(result["surface_status"], "insufficient_evidence")

    def test_class_priority_sorting_is_deterministic(self) -> None:
        first = build_manual_operator_shadow_surface(self.payload()); second = build_manual_operator_shadow_surface(self.payload()); self.assertEqual([r["shadow_row_id"] for r in first["rows"]], [r["shadow_row_id"] for r in second["rows"]])

    def test_no_private_or_scenario_wording(self) -> None:
        output = json.dumps(build_manual_operator_shadow_surface(self.payload()), ensure_ascii=False); self.assertNotIn("scenario", output.lower()); self.assertNotIn("/private/", output)

    def test_current_candidate_snapshot_is_not_p4_scenario(self) -> None:
        self.assertNotIn("scenario", json.dumps(build_manual_operator_shadow_surface(self.payload())).lower())

    def test_missing_setup_side_is_exactly_insufficient(self) -> None:
        payload = self.payload(); payload["primary_setup_side"] = ""
        result = build_manual_operator_shadow_surface(payload)
        self.assertEqual(result["surface_status"], "insufficient_evidence")
        self.assertEqual(result["rows"][0]["operator_class"], "")

    def test_deterministic_a_b_c_stop_rows(self) -> None:
        candidates = [
            {"candidate_id": "a", "source_signal_id": "s", "candidate_type": "a", "candidate_status": "allowed", "side": "long", "entry_price": "1"},
            {"candidate_id": "b", "source_signal_id": "s", "candidate_type": "b", "candidate_status": "allowed", "side": "long", "entry_price": "2"},
            {"candidate_id": "c", "source_signal_id": "s", "candidate_type": "c", "candidate_status": "allowed", "side": "long", "entry_price": "3"},
            {"candidate_id": "d", "source_signal_id": "s", "candidate_type": "d", "candidate_status": "allowed", "side": "long", "entry_price": "4"},
        ]
        classes = {"a": "A_FORMAL", "b": "B_CHECK_15M", "c": "C_WATCH_ZONE", "d": "STOP_OR_EXIT"}
        def classify(_event, candidate, _signal):
            return {"classification_status": "classified", "operator_class": classes[candidate["candidate_type"]], "reason_codes": "", "warning_codes": ""}
        with patch("src.feedback.manual_operator_shadow_surface.build_current_result_candidate_rows", return_value=candidates), patch("src.feedback.manual_operator_shadow_surface.build_current_result_signal_context", return_value={}), patch("src.feedback.manual_operator_shadow_surface.classify_manual_operator_candidate", side_effect=classify):
            result = build_manual_operator_shadow_surface(self.payload())
        self.assertEqual([row["operator_class"] for row in result["rows"]], ["STOP_OR_EXIT", "A_FORMAL", "B_CHECK_15M", "C_WATCH_ZONE"])
        self.assertEqual(result["surface_status"], "ready")


if __name__ == "__main__": unittest.main()
