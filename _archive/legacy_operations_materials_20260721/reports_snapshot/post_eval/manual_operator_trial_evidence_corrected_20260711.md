# Manual Operator Trial Evidence

## Purpose

Offline comparison of event-time predictions, market-path outcomes, and eligible episode evidence.

## Evaluation
{"ambiguous_rows": 0, "no_ohlcv_rows": 0, "resolved_rows": 84, "review_queue_size": 41, "scenario_count": 97, "trial_fact_rows": 97, "unresolved_rows": 13}

## Comparison
{"aligned": 43, "too_defensive": 41}

## Class / Side / Regime / Setup
{"regime": {"range": 37, "transition": 60}, "setup_family": {"counter_scalp": 45, "limit_retest": 50, "market": 2}, "side": {"long": 48, "short": 49}}

## Actual Evidence
{"eligible_rows": 0, "high_confidence_rows": 0, "medium_confidence_rows": 0, "status": "missing", "unique_episode_count": 0}

## Review Queue
41 exception items require human review.

## P9 Readiness
{"initial": {"actual_entry_episodes": 0, "class_segmentation_available": false, "ready": false, "regime_segmentation_available": true, "reproducibility_metadata_available": true, "resolved_events": 84, "setup_segmentation_available": true, "side_segmentation_available": true}, "practical": {"actual_entry_episodes": 0, "ready": false, "resolved_events": 84, "validation_window_status": "not_established"}}

## Limitations
Unresolved, no_ohlcv, low-confidence, and ambiguous evidence are excluded from performance claims.
Actual trade absence does not prove skip, watch, or intent.
No automatic tuning or production recommendation is applied by this report.

## Safety Boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
