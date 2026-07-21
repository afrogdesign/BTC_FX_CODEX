# Manual Operator Classifier Report

## Purpose

Offline hypothesis only. This is not FORMAL_GO; no automatic order is created and a human decides manually.

## Input Status

- scenario_event_input_rows: 2104
- candidate_context_rows: 2104
- signal_context_rows: 2819

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

- classified_rows: 1661
- insufficient_evidence_rows: 295
- ambiguous_event_rows: 148

## Class Distribution

- STOP_OR_EXIT: 1661
- A_FORMAL: 0
- B_CHECK_15M: 0
- C_WATCH_ZONE: 0
- insufficient_evidence: 295

## Side Breakdown
{"long": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 926}, "short": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 735}}

## Regime Breakdown
{"downtrend": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 232}, "range": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 674}, "transition": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 748}, "volatile": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 7}}

## Setup-Family Breakdown
{"counter_scalp": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 513}, "limit_retest": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 1133}, "market_entry": {"A_FORMAL": 0, "B_CHECK_15M": 0, "C_WATCH_ZONE": 0, "STOP_OR_EXIT": 15}}

## Existing Gate Comparison
- formal_gate_pass_rows: 0
- formal_pass_not_a_rows: 0
- B thresholds are comparison values, not production settings.

## Warnings and Risks
- warning_token_counts: {"atr_warning": 9, "critical_zone_warning": 1534, "long_countertrend_risk": 5, "short_countertrend_risk": 7}
- risk_token_counts: {"ask_wall_close": 240, "bid_wall_close": 604, "cvd_bearish_divergence": 277, "cvd_bullish_divergence": 281, "failed_breakout_down_reversal": 540, "failed_breakout_up_reversal": 375, "long_flush_exhaustion": 560, "long_into_major_resistance": 1850, "long_reversal_risk": 84, "lower_liquidity_close": 528, "major_resistance_rejection": 824, "major_support_rejection": 608, "orderbook_ask_heavy": 235, "orderbook_bid_heavy": 627, "resistance_to_support_flip": 794, "resistance_to_support_retest_confirmed": 792, "short_cover_risk": 472, "short_into_major_support": 1690, "support_to_resistance_flip": 1115, "support_to_resistance_retest_confirmed": 1112, "sweep_incomplete": 1823, "trend_flip_confirmed_down": 659, "trend_flip_confirmed_up": 245, "trend_flip_early_down": 753, "trend_flip_early_up": 350, "upper_liquidity_close": 1225}
- no_trade_token_counts: {"breakout_follow_candidate": 530, "downside_breakdown_follow_watch": 279, "long_at_major_resistance_wait_only": 518, "long_invalidated_by_down_break": 65, "long_invalidation_watch": 35, "short_at_major_support_wait_only": 1122, "short_invalidated_by_up_break": 223, "short_invalidation_watch": 4, "upside_breakout_follow_watch": 205, "volatile_regime": 7}

## Limitations
- No P5 profitability evaluation exists.
- Outcome, actual trade, and human decision evidence are not classifier inputs.
- This report does not modify gates, thresholds, notifications, runtime, or orders.

## Safety Boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
