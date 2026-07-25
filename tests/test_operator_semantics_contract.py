from __future__ import annotations

import unittest

from src.contracts.operator_semantics import (
    ADVISORY_NO_TRADE_TOKENS,
    HARD_NO_TRADE_TOKENS,
    SEMANTICS_SCHEMA_VERSION,
    classify_no_trade_tokens,
    formal_execution_blocks_no_trade,
    normalize_no_trade_tokens,
    offline_classifier_stops_for_no_trade,
)


class OperatorSemanticsContractTests(unittest.TestCase):
    def test_exact_accepted_token_sets(self) -> None:
        self.assertEqual(HARD_NO_TRADE_TOKENS, frozenset({"volatile_regime"}))
        self.assertEqual(ADVISORY_NO_TRADE_TOKENS, frozenset({
            "short_at_major_support_wait_only", "long_at_major_resistance_wait_only",
            "breakout_follow_candidate", "upside_breakout_follow_watch",
            "downside_breakdown_follow_watch", "short_invalidated_by_up_break",
            "long_invalidated_by_down_break", "short_invalidation_watch",
            "long_invalidation_watch",
        }))

    def test_empty_and_supported_input_forms(self) -> None:
        for value in (None, "", [], (), set()):
            self.assertEqual(normalize_no_trade_tokens(value), ())
        expected = ("a", "b")
        for value in ([" B ", "a", "a"], ("b", "A"), {"a", "b"}, " B, a;A|b ", '["b", "a", "a"]'):
            self.assertEqual(normalize_no_trade_tokens(value), expected)

    def test_malformed_json_like_text_is_safe(self) -> None:
        self.assertEqual(normalize_no_trade_tokens("[B, a]"), ("[b", "a]"))

    def test_partitions_and_lane_helpers(self) -> None:
        advisory = "long_at_major_resistance_wait_only;breakout_follow_candidate"
        for value in (advisory, "volatile_regime", "unknown_token", f"{advisory};volatile_regime", f"{advisory};unknown_token"):
            result = classify_no_trade_tokens(value)
            self.assertEqual(result.schema_version, SEMANTICS_SCHEMA_VERSION)
            self.assertEqual(set(result.hard_tokens) & set(result.advisory_tokens), set())
            self.assertEqual(set(result.hard_tokens) & set(result.unknown_tokens), set())
            self.assertEqual(set(result.advisory_tokens) & set(result.unknown_tokens), set())
            self.assertEqual(result.has_tokens, bool(result.normalized_tokens))
            self.assertTrue(formal_execution_blocks_no_trade(value))

        self.assertTrue(classify_no_trade_tokens(advisory).all_advisory)
        self.assertFalse(classify_no_trade_tokens(advisory).fail_closed)
        self.assertFalse(offline_classifier_stops_for_no_trade(advisory))
        self.assertTrue(offline_classifier_stops_for_no_trade("volatile_regime"))
        self.assertTrue(offline_classifier_stops_for_no_trade("unknown_token"))
        self.assertTrue(classify_no_trade_tokens("volatile_regime").fail_closed)
        self.assertTrue(classify_no_trade_tokens("unknown_token").fail_closed)

    def test_deterministic_and_input_is_not_mutated(self) -> None:
        value = [" B ", "a", "b"]
        before = list(value)
        first = classify_no_trade_tokens(value)
        second = classify_no_trade_tokens(value)
        self.assertEqual(first, second)
        self.assertEqual(value, before)


if __name__ == "__main__":
    unittest.main()
