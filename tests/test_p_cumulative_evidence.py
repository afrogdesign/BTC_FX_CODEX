import csv
import io
import unittest
from datetime import datetime, timezone

from src.contracts.generation_identity import GenerationIdentity
from src.feedback.p_cumulative_evidence import EVIDENCE_HEADERS, EvidenceIdentityConflict, build_evidence_facts

def row(**values):
    base = {"event_timestamp_utc": "2026-07-24T00:00:00Z"}; base.update(values); return base
def generation():
    return GenerationIdentity(program="P", runtime_generation="Ver04-v5", source_head="abc", schema_version="p_cumulative_evidence.v1", method_version="p_cumulative_evidence.v1", cutoff_utc="2026-07-25T00:00:00Z", classifier_version="v4", linker_version="v2", p8_evidence_version="v1")

class CumulativeEvidenceTests(unittest.TestCase):
    def test_dedup_and_cohorts_and_separation(self):
        inputs = {
            "classifications": ([row(classification_id="c1", classifier_method_version="v4", operator_class="B_CHECK_15M")], {"logical_name":"classifications.csv","row_count":1,"fingerprint":"a"}),
            "trial_facts": ([row(trial_fact_id="t1", classifier_method_version="v4", outcome_status="positive", actual_net_pnl_after_fee="99")], {"logical_name":"trial.csv","row_count":1,"fingerprint":"b"}),
            "episodes": ([row(episode_id="e1", association_method_version="a1", realized_pnl="12")], {"logical_name":"episodes.csv","row_count":1,"fingerprint":"c"}),
            "links_v2": ([row(link_id="l1", link_method_version="l2", episode_id="e1", signal_id="s1", link_confidence="high", link_status="linked")], {"logical_name":"links.csv","row_count":1,"fingerprint":"d"}),
            "signal_log": ([row(signal_id="s1", evaluation_trace_version="ev1")], {"logical_name":"signals.csv","row_count":1,"fingerprint":"e"}),
        }
        facts, stats = build_evidence_facts(inputs, generation(), "2026-07-25T00:00:00Z")
        self.assertEqual(len(facts), 5); self.assertEqual(stats["exact_duplicate_counts"]["evidence_facts"], 0)
        self.assertEqual({r["component_version"] for r in facts if r["evidence_kind"] == "classification"}, {"v4"})
        self.assertEqual(next(r for r in facts if r["evidence_kind"] == "proxy_trial_fact")["actual_realized_pnl"], "")
        self.assertEqual(set(facts[0]), set(EVIDENCE_HEADERS))
    def test_blank_signal_and_cutoff(self):
        inputs = {"classifications":([], {"logical_name":"c","row_count":0,"fingerprint":""}), "trial_facts":([], {"logical_name":"t","row_count":0,"fingerprint":""}), "episodes":([], {"logical_name":"e","row_count":0,"fingerprint":""}), "links_v2":([], {"logical_name":"l","row_count":0,"fingerprint":""}), "signal_log":([row(signal_id="", evaluation_trace_version="v1")], {"logical_name":"s","row_count":1,"fingerprint":"s"})}
        facts, stats = build_evidence_facts(inputs, generation(), "2026-07-25T00:00:00Z"); self.assertEqual(facts, []); self.assertEqual(stats["blank_identity_counts"]["signal_log"], 1)
        inputs["signal_log"] = ([row(signal_id="s", event_timestamp_utc="2026-07-26T00:00:00Z")], inputs["signal_log"][1])
        with self.assertRaises(ValueError): build_evidence_facts(inputs, generation(), "2026-07-25T00:00:00Z")
    def test_identity_conflict(self):
        r1 = row(classification_id="c", classifier_method_version="v1")
        r2 = row(classification_id="c", classifier_method_version="v2")
        inputs = {"classifications":([r1,r2], {"logical_name":"c","row_count":2,"fingerprint":"x"}), "trial_facts":([], {"logical_name":"t","row_count":0,"fingerprint":""}), "episodes":([], {"logical_name":"e","row_count":0,"fingerprint":""}), "links_v2":([], {"logical_name":"l","row_count":0,"fingerprint":""}), "signal_log":([], {"logical_name":"s","row_count":0,"fingerprint":""})}
        with self.assertRaises(EvidenceIdentityConflict): build_evidence_facts(inputs, generation(), "2026-07-25T00:00:00Z")

if __name__ == "__main__": unittest.main()
