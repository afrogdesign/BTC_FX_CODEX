import unittest
from src.feedback.p9_readiness_v2 import evaluate_readiness

def base():
    manifest={"generation":{"classifier_version":"manual_operator_classifier.v4"},"operational_health":{"state":"healthy"},"cumulative_evidence_pointer":{"compatibility_status":"compatible","missing_current_component_cohorts":["v4"],"current_component_cohorts":[],"cohort_counts":{},"fingerprints_present":True,"available_segments":[]},"modern_attribution_pointer":{"accepted_high_medium_actual":58}}
    trial={"p9_readiness":{"initial":{"ready":False},"practical":{"ready":False}}}; cum={}; modern={"causality_statement":{"automatic_causal_claims":0},"canonical_link_replacement":False}; return manifest,trial,cum,modern
class P9ReadinessTests(unittest.TestCase):
    def test_collecting_and_legacy_separation(self):
        m,t,c,modern=base(); out=evaluate_readiness(m,t,c,modern); self.assertEqual(out["state"],"collecting"); self.assertEqual(out["legacy_readiness_v1"],t["p9_readiness"]); self.assertFalse(out["production_ready"]); self.assertEqual(out["proposal_approval_status"],"not_requested")
    def test_current_cohort_baseline_and_usefulness_blockers(self):
        m,t,c,modern=base(); m["cumulative_evidence_pointer"].update({"missing_current_component_cohorts":[],"current_component_cohorts":["a","b"]}); out=evaluate_readiness(m,t,c,modern); self.assertEqual(out["dimensions"]["evidence_coverage"]["state"],"baseline_available"); self.assertEqual(out["dimensions"]["notification_usefulness"]["state"],"baseline_available")
        modern["causality_statement"]["automatic_causal_claims"]=1; self.assertEqual(evaluate_readiness(m,t,c,modern)["state"],"blocked_data")
    def test_claim_scope_and_validation_states(self):
        m,t,c,modern=base(); m["cumulative_evidence_pointer"].update({"missing_current_component_cohorts":[],"current_component_cohorts":["a"],"compatibility_status":"compatible"}); scope={"claim_id":"x","component_field":"classifier_version","component_version":"v4","required_segments":[],"minimum_requirements":{"n":1},"threshold_status":"frozen_before_validation"}; out=evaluate_readiness(m,t,c,modern,scope); self.assertEqual(out["dimensions"]["proposal_eligibility"]["state"],"eligible_for_proposal")
        validation={"validation_status":"in_progress","generation_compatible":True,"cohort_compatible":True,"time_split":True}; self.assertEqual(evaluate_readiness(m,t,c,modern,scope,validation)["state"],"shadow_validating")
        validation["validation_status"]="passed"; self.assertEqual(evaluate_readiness(m,t,c,modern,scope,validation)["state"],"human_approval_required")
        validation["validation_status"]="failed"; self.assertEqual(evaluate_readiness(m,t,c,modern,scope,validation)["state"],"rejected")

if __name__ == "__main__": unittest.main()
