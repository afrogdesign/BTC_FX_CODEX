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

    def test_reason_buckets_and_relations(self):
        specs = [("side_conflict", {"side_compatibility":"conflict"}, "ambiguous"), ("symbol_conflict", {"symbol_compatibility":"conflict"}, "ambiguous"), ("ambiguous_tie", {"link_reason":"competing_candidate_tie","link_status":"ambiguous"}, "ambiguous"), ("followup_only", {"link_reason":"followup_management_notification"}, "no_candidate"), ("no_candidate", {"signal_id":"","link_reason":"no_candidate","link_status":"no_candidate"}, "no_candidate"), ("linked_high", {"link_status":"linked","link_confidence":"high"}, "linked"), ("linked_medium", {"link_status":"linked","link_confidence":"medium"}, "linked"), ("linked_low", {"link_status":"linked","link_confidence":"low"}, "linked"), ("multiple_signal_candidates", {"link_reason":"other","link_status":"candidate","link_confidence":"low"}, "ambiguous")]
        links = []
        for i, (bucket, extra, status) in enumerate(specs):
            link = {"link_id":"l"+str(i), "episode_id":"e"+str(i), "signal_id":"s"+str(i), "link_status":status, "link_confidence":"high", "link_reason":"matched", "side_compatibility":"compatible", "symbol_compatibility":"compatible"}; link.update(extra); links.append(link)
        out = build_modern_outputs(links, [], [{"episode_id":"e"+str(i),"realized_pnl":"1"} for i in range(len(links))], [], [])
        self.assertEqual(set(out["report"]["reason_bucket_counts"]), {x[0] for x in specs})

    def test_notification_fallbacks_and_metadata_states(self):
        link = {"link_id":"l","episode_id":"e","signal_id":"s","link_status":"linked","link_confidence":"high","link_reason":"matched","notification_class":"baseline"}
        for signal, expected in [({"signal_id":"s","notification_kind":"kind","summary_variant":"summary","reason_for_notification":"reason"}, "kind"), ({"signal_id":"s","summary_variant":"summary","reason_for_notification":"reason"}, "summary"), ({"signal_id":"s","reason_for_notification":"reason"}, "reason"), ({"signal_id":"s"}, "baseline")]:
            candidate = build_modern_outputs([link], [signal], [{"episode_id":"e","realized_pnl":"1"}], [], [])["candidates"][0]
            self.assertEqual(candidate["notification_kind"], expected)
        self.assertEqual(build_modern_outputs([link], [], [], [], [])["candidates"][0]["modern_metadata_status"], "missing")
        self.assertEqual(build_modern_outputs([link], [{"signal_id":"s","summary_variant":"x"}], [], [], [])["candidates"][0]["modern_metadata_status"], "partial")

    def test_multirow_aggregation_and_accounting(self):
        links = [{"link_id":"l1","episode_id":"e1","signal_id":"s1","link_status":"linked","link_confidence":"high","link_reason":"matched","time_delta_minutes":"12"}, {"link_id":"l2","episode_id":"e2","signal_id":"s2","link_status":"linked","link_confidence":"low","link_reason":"matched","time_delta_minutes":"4"}]
        signals = [{"signal_id":"s3","was_notified":"true","notification_kind":"x"}]
        out = build_modern_outputs(links, signals, [{"episode_id":"e1","realized_pnl":"10"},{"episode_id":"e2","realized_pnl":"20"}], [{"source_signal_id":"s1","operator_class":"B_CHECK_15M"},{"source_signal_id":"s1","operator_class":"A_FORMAL"}], [{"signal_id":"s1","outcome_status":"win"},{"signal_id":"s1","outcome_status":"resolved_positive"},{"signal_id":"s3","outcome_status":"resolved_positive"}])
        actual = [r for r in out["ledger"] if r["ledger_basis"] == "actual_episode"]
        self.assertEqual(actual[0]["entry_latency_minutes"], "12"); self.assertEqual(actual[0]["p5_operator_classes"], "A_FORMAL;B_CHECK_15M")
        low = next(r for r in actual if r["actual_link_confidence"] == "low"); self.assertEqual(low["actual_realized_pnl"], "20")
        self.assertEqual(out["report"]["actual_attribution"]["accepted_high_medium"], 1); self.assertEqual(out["report"]["actual_attribution"]["accepted_high_medium_rows_with_pnl"], 1)
        signal = next(r for r in out["ledger"] if r["ledger_basis"] == "notification_without_accepted_actual"); self.assertEqual(signal["actual_realized_pnl"], ""); self.assertEqual(signal["usefulness_category"], "useful_no_entry_proxy")
        self.assertEqual(out["report"]["causality_statement"]["automatic_causal_claims"], 0)

if __name__ == "__main__": unittest.main()
