# Manual Operator Classifier Report

## Purpose

Offline hypothesis only. This is not FORMAL_GO; no automatic order is created and a human decides manually.

## Input Status

- scenario_event_input_rows: 206
- candidate_context_rows: 206
- signal_context_rows: 108

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

- classified_rows: 206
- insufficient_evidence_rows: 0
- ambiguous_event_rows: 0

## Class Distribution

- STOP_OR_EXIT: 205
- A_FORMAL: 0
- B_CHECK_15M: 0
- C_WATCH_ZONE: 1
- insufficient_evidence: 0

## Side Breakdown
{"long": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 104}, "short": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 1, "STOP_OR_EXIT": 101}}

## Regime Breakdown
{"range": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 82}, "transition": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 1, "STOP_OR_EXIT": 123}}

## Setup-Family Breakdown
{"counter_scalp": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 98}, "limit_retest": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 106}, "market": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 1, "STOP_OR_EXIT": 1}}

## Existing Gate Comparison
- formal_gate_pass_rows: 0
- formal_pass_not_a_rows: 0
- B thresholds are comparison values, not production settings.

## Warnings and Risks
- warning_token_counts: {"critical_zone_warning": 149, "long_countertrend_risk": 3, "short_countertrend_risk": 1}
- risk_token_counts: {"ask_wall_close": 41, "bid_wall_close": 52, "cvd_bearish_divergence": 38, "cvd_bullish_divergence": 13, "failed_breakout_down_reversal": 69, "failed_breakout_up_reversal": 39, "long_flush_exhaustion": 54, "long_into_major_resistance": 192, "long_reversal_risk": 26, "lower_liquidity_close": 99, "major_resistance_rejection": 89, "major_support_rejection": 63, "orderbook_ask_heavy": 41, "orderbook_bid_heavy": 53, "resistance_to_support_flip": 84, "resistance_to_support_retest_confirmed": 84, "short_cover_risk": 51, "short_into_major_support": 187, "support_to_resistance_flip": 119, "support_to_resistance_retest_confirmed": 117, "sweep_incomplete": 180, "trend_flip_confirmed_down": 62, "trend_flip_confirmed_up": 26, "trend_flip_early_down": 86, "trend_flip_early_up": 30, "upper_liquidity_close": 87}
- no_trade_token_counts: {"breakout_follow_candidate": 183, "downside_breakdown_follow_watch": 121, "long_at_major_resistance_wait_only": 100, "long_invalidated_by_down_break": 22, "long_invalidation_watch": 22, "short_at_major_support_wait_only": 96, "short_invalidated_by_up_break": 1, "short_invalidation_watch": 1, "upside_breakout_follow_watch": 85}

## Limitations
- No P5 profitability evaluation exists.
- Outcome, actual trade, and human decision evidence are not classifier inputs.
- This report does not modify gates, thresholds, notifications, runtime, or orders.

## Safety Boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
