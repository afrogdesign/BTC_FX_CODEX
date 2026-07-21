# Manual Operator Trial Evidence

## Purpose

Offline comparison of event-time predictions, market-path outcomes, and eligible episode evidence.

## Evaluation
{"ambiguous_rows": 0, "no_ohlcv_rows": 336, "resolved_rows": 22, "review_queue_size": 10, "scenario_count": 364, "trial_fact_rows": 364, "unresolved_rows": 6}

## Comparison
{"aligned": 12, "too_defensive": 10}

## Class / Side / Regime / Setup
{"regime": {"downtrend": 37, "range": 169, "transition": 151, "volatile": 7}, "setup_family": {"counter_scalp": 147, "limit_retest": 204, "market_entry": 13}, "side": {"long": 200, "short": 164}}

## Actual Evidence
{"eligible_rows": 0, "high_confidence_rows": 0, "medium_confidence_rows": 0, "status": "missing", "unique_episode_count": 0}

## Review Queue
10 exception items require human review.

## P9 Readiness
{"initial": {"actual_entry_episodes": 0, "class_segmentation_available": false, "ready": false, "regime_segmentation_available": true, "reproducibility_metadata_available": true, "resolved_events": 22, "setup_segmentation_available": true, "side_segmentation_available": true}, "practical": {"actual_entry_episodes": 0, "ready": false, "resolved_events": 22, "validation_window_status": "not_established"}}

## Limitations
Unresolved, no_ohlcv, low-confidence, and ambiguous evidence are excluded from performance claims.
Actual trade absence does not prove skip, watch, or intent.
No automatic tuning or production recommendation is applied by this report.

## Safety Boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
