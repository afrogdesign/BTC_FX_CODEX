# Manual Operator Classifier Report

## Purpose

Offline hypothesis only. This is not FORMAL_GO; no automatic order is created and a human decides manually.

## Input Status

- scenario_event_input_rows: 207
- candidate_context_rows: 207
- signal_context_rows: 107

## Method and No-Leakage Boundary

Event-time evidence only. Outcome, actual trade, and human decision evidence are not classifier inputs. A/B/C/STOP does not replace existing gates.

## Threshold Snapshot

- long_direction_min: 60
- long_execution_min: 22
- long_tp1_rr_min: 1.0
- long_tp2_rr_min: 1.8
- long_wait_max: 70
- short_direction_min: 55
- short_execution_min: 18
- short_tp1_rr_min: 0.8
- short_tp2_rr_min: 1.5
- short_wait_max: 75

## Classification Coverage

- classified_rows: 207
- insufficient_evidence_rows: 0
- ambiguous_event_rows: 0

## Class Distribution

- STOP_OR_EXIT: 205
- A_FORMAL: 0
- B_CHECK_15M: 0
- C_WATCH_ZONE: 2
- insufficient_evidence: 0

## Side Breakdown
{"long": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 103}, "short": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 2, "STOP_OR_EXIT": 102}}

## Regime Breakdown
{"range": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 82}, "transition": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 2, "STOP_OR_EXIT": 123}}

## Setup-Family Breakdown
{"counter_scalp": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 100}, "limit_retest": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 1, "STOP_OR_EXIT": 104}, "market": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 1, "STOP_OR_EXIT": 1}}

## Existing Gate Comparison
- formal_gate_pass_rows: 0
- formal_pass_not_a_rows: 0
- B thresholds are comparison values, not production settings.

## Warnings and Risks
- warning_token_counts: {"critical_zone_warning": 167}
- risk_token_counts: {"ask_wall_close": 54, "bid_wall_close": 54, "cvd_bearish_divergence": 36, "cvd_bullish_divergence": 4, "failed_breakout_down_reversal": 65, "failed_breakout_up_reversal": 35, "long_flush_exhaustion": 51, "long_into_major_resistance": 196, "long_reversal_risk": 26, "lower_liquidity_close": 101, "major_resistance_rejection": 83, "major_support_rejection": 65, "orderbook_ask_heavy": 40, "orderbook_bid_heavy": 50, "resistance_to_support_flip": 94, "resistance_to_support_retest_confirmed": 94, "short_cover_risk": 51, "short_into_major_support": 181, "support_to_resistance_flip": 107, "support_to_resistance_retest_confirmed": 105, "sweep_incomplete": 173, "trend_flip_confirmed_down": 65, "trend_flip_confirmed_up": 32, "trend_flip_early_down": 74, "trend_flip_early_up": 32, "upper_liquidity_close": 87}
- no_trade_token_counts: {"breakout_follow_candidate": 192, "downside_breakdown_follow_watch": 109, "long_at_major_resistance_wait_only": 104, "long_invalidated_by_down_break": 11, "long_invalidation_watch": 11, "short_at_major_support_wait_only": 96, "upside_breakout_follow_watch": 94}

## Limitations
- No P5 profitability evaluation exists.
- Outcome, actual trade, and human decision evidence are not classifier inputs.
- This report does not modify gates, thresholds, notifications, runtime, or orders.

## Safety Boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
