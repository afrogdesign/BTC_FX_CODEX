# Manual Operator Trial Evidence

## Purpose

Offline comparison of event-time predictions, market-path outcomes, and eligible episode evidence.

## Evaluation
{"ambiguous_rows": 1, "no_ohlcv_rows": 0, "resolved_rows": 74, "review_queue_size": 38, "scenario_count": 83, "trial_fact_rows": 83, "unresolved_rows": 9}

## Comparison
{"aligned": 36, "too_defensive": 38}

## Class / Side / Regime / Setup
{"regime": {"range": 33, "transition": 50}, "setup_family": {"counter_scalp": 37, "limit_retest": 44, "market": 2}, "side": {"long": 42, "short": 41}}

## Actual Evidence
{"eligible_rows": 0, "high_confidence_rows": 0, "medium_confidence_rows": 0, "status": "missing", "unique_episode_count": 0}

## Review Queue
38 exception items require human review.

## P9 Readiness
{"initial": {"actual_entry_episodes": 0, "class_segmentation_available": false, "ready": false, "regime_segmentation_available": true, "reproducibility_metadata_available": true, "resolved_events": 74, "setup_segmentation_available": true, "side_segmentation_available": true}, "practical": {"actual_entry_episodes": 0, "ready": false, "resolved_events": 74, "validation_window_status": "not_established"}}

## Limitations
Unresolved, no_ohlcv, low-confidence, and ambiguous evidence are excluded from performance claims.
Actual trade absence does not prove skip, watch, or intent.
No automatic tuning or production recommendation is applied by this report.

## Safety Boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
