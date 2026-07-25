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
        m,t,c,modern=base(); m["cumulative_evidence_pointer"].update({"missing_current_component_cohorts":[],"current_component_cohorts":["a"],"compatibility_status":"compatible","cohort_counts":{"x|classification|manual_operator_classifier.v4":2,"x|proxy_trial_fact|manual_operator_classifier.v4":2}}); scope={"claim_id":"x","component_field":"classifier_version","component_version":"manual_operator_classifier.v4","required_segments":[],"minimum_requirements":{"classification_cohort_rows_min":1,"proxy_trial_fact_cohort_rows_min":1,"accepted_high_medium_actual_min":1},"threshold_status":"frozen_before_validation"}; out=evaluate_readiness(m,t,c,modern,scope); self.assertEqual(out["dimensions"]["proposal_eligibility"]["state"],"eligible_for_proposal")
        validation={"validation_status":"in_progress","generation_compatible":True,"cohort_compatible":True,"time_split":True,"claim_scope_match":True}; self.assertEqual(evaluate_readiness(m,t,c,modern,scope,validation)["state"],"shadow_validating")
        validation.update({"validation_status":"passed","versions_frozen_before_validation":True,"thresholds_frozen_before_validation":True}); self.assertEqual(evaluate_readiness(m,t,c,modern,scope,validation)["state"],"human_approval_required")
        validation["validation_status"]="failed"; self.assertEqual(evaluate_readiness(m,t,c,modern,scope,validation)["state"],"rejected")

    def test_notification_usefulness_is_separate(self):
        m,t,c,modern=base(); m["cumulative_evidence_pointer"].update({"missing_current_component_cohorts":[],"current_component_cohorts":["a"]}); modern["actual_attribution"]={"accepted_high_medium_actual_associations":58,"notified_accepted_actual_associations":0}; out=evaluate_readiness(m,t,c,modern); self.assertIn("actual_association_coverage",out["dimensions"]); self.assertEqual(out["dimensions"]["notification_usefulness"]["state"],"collecting")

    def test_unsupported_minimum_does_not_qualify(self):
        m,t,c,modern=base(); m["cumulative_evidence_pointer"].update({"missing_current_component_cohorts":[],"current_component_cohorts":["a"],"cohort_counts":{"x|classification|manual_operator_classifier.v4":2,"x|proxy_trial_fact|manual_operator_classifier.v4":2}}); scope={"minimum_requirements":{"n":1},"threshold_status":"frozen_before_validation"}; out=evaluate_readiness(m,t,c,modern,scope); self.assertEqual(out["dimensions"]["proposal_eligibility"]["state"],"collecting")

if __name__ == "__main__": unittest.main()
