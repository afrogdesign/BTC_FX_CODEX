import unittest

from src.feedback.formal_gate_semantic_impact import build_impact


class FormalGateSemanticImpactTests(unittest.TestCase):
    def test_counterfactual_separates_advisory_hard_unknown_and_other_blockers(self):
        report = build_impact([
            {"no_trade_flags": "short_at_major_support_wait_only", "formal_blockers": "short_at_major_support_wait_only"},
            {"no_trade_flags": "volatile_regime", "formal_blockers": "volatile_regime"},
            {"no_trade_flags": "unknown_token", "formal_blockers": "unknown_token"},
            {"no_trade_flags": "short_at_major_support_wait_only", "formal_blockers": "short_at_major_support_wait_only;phase1_inactive"},
        ])
        counts = report["counts"]
        self.assertEqual(counts["advisory_only_rows"], 2)
        self.assertEqual(counts["hard_token_rows"], 1)
        self.assertEqual(counts["unknown_token_rows"], 1)
        self.assertEqual(counts["rows_where_no_trade_blocker_would_be_removed"], 2)
        self.assertEqual(counts["rows_still_blocked_by_other_formal_reasons"], 1)
        self.assertEqual(counts["rows_potentially_changed_to_pass"], 1)
        self.assertIn("counterfactual only", report["statements"])


if __name__ == "__main__":
    unittest.main()
