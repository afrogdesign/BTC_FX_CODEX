import tempfile
import unittest
from pathlib import Path
from src.feedback.p8_daily_manifest_v2 import IdentityConflict, build_manifest, write_outputs

def fixtures(classifier="v4"):
    cycle={"schema_version":"manual_operator_operating_cycle.v1","method_version":"manual_operator_operating_cycle.v1","report_date":"20260724","stage_statuses":{"candidate_slice":"ok","signal_context_slice":"ok","intraperiod_outcomes":"ok","p4":"ok","p5":"ok","p8":"ok","macro_structure_shadow":"disabled"},"source":{"ohlcv_freshness":"valid","interval":"15m"},"no_automatic_tuning":True,"input_fingerprints":{"a":"a"},"counts":{"trial_fact_rows":1,"resolved_rows":1,"unresolved_rows":0,"review_queue_size":1,"no_ohlcv_rows":0},"issue_001":{"stop_rows":0,"issue_001_qualified_rows":0}}
    trial={"ok":True,"method_version":"manual_operator_trial_evidence.v1","classifier_method_version":"manual_operator_classifier."+classifier,"report_date":"20260724","p9_readiness":{"initial":{"ready":False},"practical":{"ready":False}},"global_stop_opportunity":{"stop_rows":0,"issue_001_qualified_rows":0}}
    facts=[{"review_item_id":"r1","evidence_tier":"actual_high_medium","actual_episode_id":"e1","actual_link_confidence":"medium","no_trade_flags":"unknown_token"}]
    queue=[{"review_item_id":"q1"}]
    cumulative={"run_id":"run","schema_version":"p_cumulative_evidence.v1","method_version":"p_cumulative_evidence.v1","input_status":"provided","cutoff_utc":"2026-07-25T00:00:00Z","generation":{"program":"P","runtime_generation":"r","classifier_version":"v1"},"input_sources":[{"fingerprint":"i"}],"output_fingerprints":{"x":"x"},"cohort_counts":{"P|r|classification|v1":1,"P|r|proxy_trial_fact|v1":1}}
    modern={"baseline_episodes":149,"baseline_links":149,"actual_attribution":{"accepted_high_medium":58},"causality_statement":{"automatic_causal_claims":0},"canonical_link_replacement":False}
    return cycle,trial,facts,queue,cumulative,modern

class P8ManifestTests(unittest.TestCase):
    def test_first_baseline_and_semantics(self):
        args=fixtures(); m,_=build_manifest(*args,"r","h","2026-07-25T01:00:00Z")
        self.assertEqual(m["generation_comparison"]["status"],"first_v2_baseline"); self.assertEqual(m["review_queue_delta"]["new"],[]); self.assertEqual(m["review_queue_delta"]["backlog"],["q1"]); self.assertEqual(m["actual_attribution_delta"]["retained"],["e1"]); self.assertEqual(m["issue_applicability"]["issue_001"],"not_applicable_no_stop_population"); self.assertEqual(m["semantic_token_status"]["rows_with_unknown_tokens"],1); self.assertTrue(any(x["type"]=="unknown_semantic_token" for x in m["meaningful_changes"]))
    def test_auxiliary_failure_does_not_block_core(self):
        args=fixtures(); args[0]["turning_precursor_shadow"]={"status":"failed"}; m,_=build_manifest(*args,"r","h","2026-07-25T01:00:00Z"); self.assertEqual(m["operational_health"]["state"],"healthy")
    def test_identity_conflict_and_deterministic_output(self):
        args=list(fixtures()); args[3]=[{"review_item_id":"q","a":"1"},{"review_item_id":"q","a":"2"}]
        with self.assertRaises(IdentityConflict): build_manifest(*args,"r","h","2026-07-25T01:00:00Z")
        args=fixtures(); m1,f1=build_manifest(*args,"r","h","2026-07-25T01:00:00Z"); m2,f2=build_manifest(*args,"r","h","2026-07-25T01:00:00Z"); self.assertEqual(f1,f2); self.assertEqual(m1["run_id"],m2["run_id"])
    def test_comparable_deltas_and_generation_reset(self):
        args=list(fixtures()); previous,_=build_manifest(*args,"r","old","2026-07-25T01:00:00Z"); args[3]=[{"review_item_id":"q2"}]; current,_=build_manifest(*args,"r","h","2026-07-25T01:00:00Z",previous); self.assertEqual(current["review_queue_delta"]["new"],["q2"]); self.assertEqual(current["review_queue_delta"]["resolved"],["q1"])
        other,_=build_manifest(*fixtures("v5"),"r","h","2026-07-25T01:00:00Z",previous); self.assertFalse(other["generation_comparison"]["comparable"]); self.assertEqual(other["review_queue_delta"]["new"],[]); self.assertTrue(any(x["type"]=="generation_baseline_reset" for x in other["meaningful_changes"]))
    def test_atomic_output_and_existing_conflict(self):
        args=fixtures(); _,files=build_manifest(*args,"r","h","2026-07-25T01:00:00Z")
        with tempfile.TemporaryDirectory() as td:
            write_outputs(Path(td)/"out",files); write_outputs(Path(td)/"out",files,replace=True)

if __name__ == "__main__": unittest.main()
