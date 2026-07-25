import unittest
from src.feedback.manual_trade_modern_attribution import build_modern_outputs

class ModernAttributionTests(unittest.TestCase):
    def test_preserves_relations_and_reason_buckets(self):
        links = [{"link_id":"l1","episode_id":"e1","signal_id":"s1","link_status":"linked","link_confidence":"high","link_reason":"matched_unique_top_candidate","side_compatibility":"compatible","symbol_compatibility":"compatible"}, {"link_id":"l2","episode_id":"e2","signal_id":"","link_status":"no_candidate","link_confidence":"ambiguous","link_reason":"no_candidate"}]
        signals = [{"signal_id":"s1","was_notified":"true","summary_variant":"attention","trade_execution_gate":"pass"}]
        out = build_modern_outputs(links, signals, [{"episode_id":"e1","realized_pnl":"1","side":"long"}], [], [])
        self.assertEqual({r["candidate_relation"] for r in out["candidates"]}, {"preserved_v2_no_candidate","preserved_v2_link"})
        self.assertIn("formal_candidate_used", {r["usefulness_category"] for r in out["ledger"]})
        self.assertEqual(out["report"]["causality_statement"]["automatic_causal_claims"], 0)
    def test_metadata_conflict(self):
        with self.assertRaisesRegex(ValueError, "signal_identity_conflict"):
            build_modern_outputs([], [{"signal_id":"s","summary_variant":"a"},{"signal_id":"s","summary_variant":"b"}], [], [], [])

if __name__ == "__main__": unittest.main()
