# P8 Operating Cycle

## Cycle status
completed

## Source coverage/freshness
{"candidates": "active_plan_candidates.csv", "interval": "15m", "max_timestamp": "2026-07-12T03:15:00+00:00", "min_timestamp": "2026-07-06T22:45:00+00:00", "ohlcv": "public_fetch", "ohlcv_freshness": "valid", "rows": 499, "signal_context": "trades.csv", "source": "exchange-auto-public", "symbol": "BTC_USDT"}

## Resolved/unresolved/no-OHLCV
{"ambiguous_rows": 1, "candidate_rows": 207, "candidate_signals": 107, "no_ohlcv_rows": 0, "outcome_counts": {"ambiguous": 3, "entry_reached": 3, "not_entered": 7, "pending": 1, "sl_first": 92, "timeout": 2, "tp1_first": 93, "tp2_first": 6}, "resolved_rows": 74, "review_queue_size": 38, "scenario_count": 83, "trial_fact_rows": 83, "unresolved_rows": 9}

## A/B/C/STOP
{"C_WATCH_ZONE": 2, "STOP_OR_EXIT": 81}

## Long/Short
{"long": 42, "short": 41}

## Comparison results
{"aligned": 36, "too_defensive": 38}

## Actual-evidence coverage
{"eligible_rows": 0, "high_confidence_rows": 0, "medium_confidence_rows": 0, "status": "missing", "unique_episode_count": 0}

## Exception queue
38

## ISSUE-001
{"counterfactual_B": 9, "counterfactual_C": 28, "global_stop_present": true, "issue_001_qualified_rows": 37, "not_eligible": 40, "opposite_side_exists": 77, "stop_rows": 81}

## P9 readiness
{"initial": {"actual_entry_episodes": 0, "class_segmentation_available": false, "ready": false, "regime_segmentation_available": true, "reproducibility_metadata_available": true, "resolved_events": 74, "setup_segmentation_available": true, "side_segmentation_available": true}, "practical": {"actual_entry_episodes": 0, "ready": false, "resolved_events": 74, "validation_window_status": "not_established"}}

## Turning precursor shadow
{"actual_backed_count": 0, "combined_false_rate": 0.384615, "combined_median_lead_minutes": 69.9885, "combined_opposite_rate": 0.192308, "combined_precision": 0.307692, "combined_recall": 0.25, "combined_whipsaw_rate": 0.115385, "current_notification_recall": 0.428571, "enabled": true, "error_codes": [], "method_version": "turning_volatility_precursor_replay.v1", "output_subdir": "turning_precursor_shadow", "pinned_case_status": "caught_before_move", "precursor_episodes": 175, "realized_move_opportunities": 28, "recommendation_status": "continue_shadow_collection", "resolved_episodes": 26, "signal_slice_rows": 127, "status": "success", "validation_down_resolved": 6, "validation_status": "established", "validation_up_resolved": 0}

## Limitations
Unresolved, no-OHLCV, low-confidence, and ambiguous evidence are excluded from performance claims.

## Safety boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
No automatic tuning occurred.
