# P8 Turning / Volatility Precursor Replay — Archived Specification

## Metadata

- work_id: `BTCFX-20260712-P8-TURNING-VOLATILITY-PRECURSOR-REPLAY`
- status: approved for bounded offline implementation
- phase: P8 evidence collection / pre-P9 proposal preparation
- change_class: deterministic offline evidence and replay only
- created_at: `2026-07-12`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## Acceptance correction and completion record

- status: completed / accepted by bounded validation
- implementation checkpoint: `c80b4a9` followed by the correction commit recorded in the repository
- corrected public replay: completed once after OHLCV continuity and policy-contract corrections
- all pre-correction replay metrics are invalid and discarded
- corrected metrics: 2,872 signal rows; 28 independent realized opportunities; 2,194 precursor episodes; Combined 238 episodes / 26 resolved; Combined all precision `0.307692`, recall `0.214286`, false rate `0.384615`, opposite rate `0.192308`, whipsaw `0.115385`, median lead `69.9885` minutes
- Combined validation: 6 resolved episodes (UP 0 / DOWN 6), precision `0.333333`, recall `0.5`, false rate `0.666667`, opposite rate `0`, median lead `77.4875` minutes; validation established but proposal gate failed
- pinned signal `20260711_220501`: caught before move; exclusion gate pass
- actual-backed precursor count: `0`
- recommendation: `continue_shadow_collection`
- generated outputs remain local and uncommitted
- no production scoring, market-map, gate, notification, mail, runtime, API, account, or order behavior changed
- report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Objective

Build a deterministic offline replay that measures whether the system can warn a human before a large directional move begins, for both Long and Short, without weakening the current formal gates or increasing live notification noise blindly.

This task addresses the observed 2026-07-12 07:05 JST miss, but must not tune production from that single example.

The replay must answer:

1. Which event-time conditions repeatedly precede large upward or downward moves?
2. How early could a chart-check warning have been issued?
3. How many false warnings would each candidate policy add?
4. Are results stable for Long and Short separately?
5. Are results stable by regime, phase, and setup context?
6. Does a proposed early-warning layer improve large-move recall without unacceptable notification burden?
7. Which cases are scoring errors, market-map state errors, notification-trigger gaps, or merely correct no-entry decisions?

## 2. Non-goals

This task does not:

- change `compute_scores`
- change market-map classification
- change current Long/Short bias
- change `trade_execution_gate`
- change `phase1b_lite_gate`
- change `opportunity_gate`
- change confidence thresholds
- change notification triggers
- send mail
- restart runtime
- mutate launchd
- authorize entry
- claim actual profitability from proxy OHLCV
- activate P9

## 3. Current evidence

Pinned observed case:

- signal: `20260711_220501`
- timestamp: `2026-07-12T07:05:01+09:00`
- current price: approximately 64,325
- current notification: suppressed
- current bias: Long
- Long / Short display score: 81 / 19
- phase: `reversal_risk`
- market regime: `transition`
- high wait pressure and high location risk
- relevant event-time evidence included:
  - `long_into_major_resistance`
  - `major_resistance_rejection`
  - `resistance_to_support_flip`
  - `resistance_to_support_retest_confirmed`
  - `trend_flip_early_up`
  - orderbook / liquidity risk flags
- subsequent market path moved materially downward before the later Short attention at 11:05 JST

The miss has two distinct possible causes and they must be evaluated separately:

1. direction/state interpretation may have remained too bullish near a failed resistance transition
2. current notification logic has no dedicated state transition for thesis stress / turning risk while the formal setup remains invalid

## 4. Design doctrine

### 4.1 Separate direction, execution, and early warning

An early warning is not a new primary bias and is not an entry permission.

The proposed offline output layer is:

```text
primary direction: current Long / Short / Wait remains unchanged
early-warning side: UP / DOWN / BOTH / NONE
operator action: check the 15-minute chart
execution permission: unchanged and still human-decided
```

### 4.2 Symmetric Long and Short treatment

The implementation must use mirrored rules.

- bearish precursor: an existing Long thesis is under stress before a downward expansion
- bullish precursor: an existing Short thesis is under stress before an upward expansion

No rule may be added only for the pinned Short case without an equivalent mirrored Long rule and test.

### 4.3 State transition, not repeated hourly noise

Candidate rows are not independent alerts.

Consecutive qualifying rows with the same precursor side and policy are compressed into one precursor episode. A new episode begins only when:

- the precursor was absent on the immediately preceding signal, or
- the precursor side changed, or
- at least 3 hours passed from the prior episode start, or
- a materially different policy family became newly active after the prior episode had ended

The first qualifying timestamp is the episode alert time.

### 4.4 Event-time only

Candidate generation uses only fields available in the current and prior signal snapshots. Future OHLCV is used only for outcome evaluation.

No future candle, final outcome, later notification, or post-hoc label may influence candidate generation.

## 5. Inputs

Required explicit inputs:

- normalized signal context CSV compatible with `logs/csv/trades.csv`
- 15-minute OHLCV CSV compatible with the accepted P8 operating-cycle format

Optional inputs:

- actual manual trade episodes and links only when both validated and supplied together

The implementation must not scan broad log directories. It reads only paths supplied by the caller.

Minimum signal fields:

- `signal_id`
- `timestamp_utc`
- `timestamp_jst`
- `was_notified`
- `current_price`
- `bias`
- `phase`
- `market_regime`
- `transition_direction`
- `market_map_primary_state`
- `market_map_flags`
- `active_level_role`
- `level_flip_state`
- `failed_breakout_state`
- `trend_flip_state`
- `long_display_score`
- `short_display_score`
- `score_gap`
- `confidence`
- `confidence_direction_shadow`
- `confidence_execution_shadow`
- `confidence_wait_shadow`
- `location_risk`
- `primary_setup_side`
- `primary_setup_status`
- `primary_setup_reason`
- `prelabel`
- `warning_flags`
- `risk_flags`
- `no_trade_flags`
- `atr_15m_value`
- `atr_ratio`
- `volume_ratio`
- `oi_change_pct`
- `cvd_slope`
- `cvd_price_divergence`
- `orderbook_bias`
- `nearest_support_distance`
- `nearest_resistance_distance`
- `notify_reason_codes`
- `suppress_reason_codes`

Missing optional market microstructure fields must be reported, not imputed as favorable evidence.

## 6. Large-move outcome contract

Evaluate each precursor episode over future closed 15-minute bars.

Horizons:

- 1 hour: 4 bars
- 2 hours: 8 bars
- 4 hours: 16 bars

Reference threshold for a material directional move:

```text
material_move_distance = max(2.0 * event_atr_15m, event_price * 0.005)
```

The constants are replay/evaluation parameters only, not production thresholds.

For each horizon calculate:

- maximum upward excursion
- maximum downward excursion
- upward excursion in ATR
- downward excursion in ATR
- first timestamp reaching material move threshold upward
- first timestamp reaching material move threshold downward
- adverse excursion before the matching threshold

Outcome labels:

- `large_up`: upward threshold reached first and downward threshold not reached earlier
- `large_down`: downward threshold reached first and upward threshold not reached earlier
- `whipsaw_both`: both thresholds reached within the horizon
- `no_large_move`: neither threshold reached
- `unresolved`: insufficient future OHLCV

A DOWN precursor matches `large_down`; an UP precursor matches `large_up`. BOTH is reported separately and never counted as a clean directional success.

## 7. Explicit candidate policy families

All policies are offline hypotheses. They must be evaluated independently and as a combined candidate. Codex must not invent additional production rules.

### POLICY_CURRENT_NOTIFICATION

Baseline only.

- candidate when `was_notified` is true
- use recorded notification direction when deterministically available
- if direction is not available, classify as nondirectional and exclude from directional precision while retaining burden count

### POLICY_LEVEL_REJECTION

DOWN candidate when all are true:

- current bias is `long`
- `long_into_major_resistance` is present
- `major_resistance_rejection` or `failed_breakout_down_reversal` is present

UP candidate is the exact mirror:

- current bias is `short`
- `short_into_major_support` is present
- `major_support_rejection` or `failed_breakout_up_reversal` is present

### POLICY_FAILED_FLIP_GUARD

DOWN candidate when all are true:

- current bias is `long`
- a bullish role-flip state is present: `resistance_to_support_flip`, `resistance_to_support_retest_confirmed`, or `level_flip_state` beginning with `resistance_to_support`
- bearish rejection evidence is present: `major_resistance_rejection` or `failed_breakout_down_reversal`
- at least one stress condition is present:
  - `phase == reversal_risk`
  - `location_risk >= 70`
  - `confidence_wait_shadow >= 70`
  - `cvd_price_divergence == bearish`
  - `orderbook_bias == ask_heavy`

UP candidate is the exact mirror using bearish role flip, bullish rejection, and bullish microstructure evidence.

### POLICY_THESIS_STRESS

DOWN candidate when current bias is Long and at least two independent evidence groups are active:

1. location group:
   - `long_into_major_resistance`
   - near-resistance distance at or below one event ATR when the distance is available
2. rejection group:
   - `major_resistance_rejection`
   - `failed_breakout_down_reversal`
3. transition group:
   - `phase == reversal_risk`
   - `trend_flip_state` in `early_down`, `confirmed_down`
   - `market_map_primary_state` in `early_down`, `confirmed_down`, `down_reversal`
4. microstructure group:
   - bearish CVD divergence
   - ask-heavy orderbook
   - negative OI change together with negative CVD slope
5. current-thesis fragility group:
   - `primary_setup_status == invalid`
   - `confidence_wait_shadow >= 70`
   - `location_risk >= 70`

UP candidate is the mirrored rule.

### POLICY_COMBINED_PRECURSOR

Candidate when any two of the following policy families agree on the same side in the same signal:

- POLICY_LEVEL_REJECTION
- POLICY_FAILED_FLIP_GUARD
- POLICY_THESIS_STRESS

Exception:

- POLICY_FAILED_FLIP_GUARD alone may qualify when both rejection evidence and `phase == reversal_risk` are present.

If UP and DOWN qualify simultaneously, output BOTH and do not count it as a clean directional candidate.

## 8. Reason codes

Output stable reason codes. At minimum:

- `dominant_long_under_stress`
- `dominant_short_under_stress`
- `at_major_resistance`
- `at_major_support`
- `major_resistance_rejection`
- `major_support_rejection`
- `failed_breakout_down_reversal`
- `failed_breakout_up_reversal`
- `bullish_flip_conflicted`
- `bearish_flip_conflicted`
- `reversal_risk_phase`
- `high_location_risk`
- `high_wait_pressure`
- `bearish_microstructure_pressure`
- `bullish_microstructure_pressure`
- `primary_setup_invalid`

Reason codes must be deterministic, sorted, and independent of future outcomes.

## 9. Pinned regression and symmetry requirements

### 9.1 Real pinned case

The replay must locate signal `20260711_220501` when included in the supplied signal input.

Expected event-time classification:

- current notification baseline: no notification
- POLICY_LEVEL_REJECTION: DOWN candidate
- POLICY_FAILED_FLIP_GUARD: DOWN candidate
- POLICY_COMBINED_PRECURSOR: DOWN candidate

Expected outcome with the supplied fresh OHLCV window:

- matching material downward expansion within the evaluation horizon
- no claim about executable entry quality

If the pinned row or its OHLCV is absent, report `pinned_case_unavailable`; do not fabricate success.

### 9.2 Synthetic mirrored Long case

Unit tests must include a mirrored Short-under-stress fixture producing an UP candidate with equivalent reason symmetry.

### 9.3 Conflict case

A fixture where both sides qualify must produce BOTH and remain excluded from clean directional precision.

## 10. Outputs

Use atomic replacement and deterministic sorting.

### 10.1 Event CSV

Suggested name:

`turning_volatility_precursor_events.csv`

One row per deduplicated precursor episode and policy.

Minimum fields:

- schema_version
- method_version
- episode_id
- policy
- precursor_side
- first_signal_id
- first_timestamp_utc
- first_timestamp_jst
- current_bias
- current_was_notified
- event_price
- event_atr_15m
- phase
- regime
- reason_codes
- source_signal_count
- outcome_1h
- outcome_2h
- outcome_4h
- matching_move_distance
- opposing_move_distance
- matching_move_atr
- opposing_move_atr
- first_match_timestamp
- lead_minutes_to_material_move
- comparison_status
- data_quality_status

Comparison status:

- `caught_before_move`
- `missed_by_current_notification`
- `false_precursor`
- `opposite_move`
- `whipsaw`
- `unresolved`

### 10.2 JSON summary

Suggested name:

`turning_volatility_precursor_replay.json`

Include:

- input fingerprints
- evaluation cutoff
- method parameters
- row and episode counts
- missing-field counts
- unresolved counts
- metrics by policy
- metrics by Long/Short precursor side
- metrics by regime and phase
- calibration/validation window metrics
- pinned case status
- P9 proposal eligibility for this issue only
- safety boundary

### 10.3 Markdown report

Suggested name:

`turning_volatility_precursor_replay.md`

Required sections:

1. Executive result
2. Current baseline versus each policy
3. Long / Short split
4. Regime / phase split
5. Lead-time distribution
6. False-warning and whipsaw burden
7. Pinned 07:05 case
8. Top missed large moves
9. Top false precursors
10. Data limitations
11. Recommendation status
12. Safety boundary

## 11. Metrics

For each policy calculate:

- precursor episodes
- matching large moves
- clean directional precision
- large-move recall
- false precursor rate
- opposite move rate
- whipsaw rate
- unresolved rate
- notifications/precursor episodes per day
- median and quartile lead time
- median matching excursion ATR
- median adverse excursion ATR before move
- duplicate compression ratio

Do not rank policies by precision alone.

A policy is not proposal-eligible if:

- one side has fewer than 10 resolved precursor episodes
- validation window is not established
- false precursor rate exceeds 60%
- opposite move rate exceeds 25%
- median lead time is zero or negative
- the result depends primarily on the pinned case

These are proposal-quality gates for this replay only, not production thresholds.

## 12. Calibration and validation split

Sort resolved event-time signal rows chronologically.

- calibration window: earliest 80%
- validation window: latest 20%
- validation must contain at least 2 distinct JST dates and at least 20 resolved precursor episodes across all policies

If insufficient, set validation status to `not_established` and do not recommend production change.

The pinned case may appear in either window according to chronology; it must not be manually moved.

## 13. Actual evidence

If valid actual episode/link inputs are supplied:

- include only high, medium, or manual-confirmed links
- count unique episodes, never fills
- report actual-linked precursor count and actual R/PnL descriptively
- keep actual evidence separate from proxy metrics

When actual evidence is absent, state `actual_backed_count = 0` and prohibit profitability claims.

## 14. CLI contract

Add one explicit report-only command to the existing feedback CLI:

`replay-turning-volatility-precursors`

Required arguments:

- `--signals`
- `--ohlcv`
- `--output-csv`
- `--output-json`
- `--output-md`

Optional arguments:

- `--actual-episodes`
- `--actual-links`
- `--cutoff-utc`
- `--replace-output`
- `--stdout-json`

Behavior:

- no directory scanning
- no exchange API
- no mail
- no runtime change
- no production config read/write beyond normal module imports
- actual files must be supplied as a validated pair
- dry failure leaves existing outputs intact
- stdout JSON is compact and excludes raw rows

## 15. Allowed implementation files

- new: `src/feedback/turning_volatility_precursor_replay.py`
- `tools/log_feedback.py`
- new: `tests/test_turning_volatility_precursor_replay.py`
- `tests/test_log_feedback.py` only for the new CLI route
- this active spec, moved to archive after successful completion
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` only to record measured evidence after the replay succeeds
- `docs/operations/ai-orchestration/NEXT_ACTION.md` only when the next posture changes

Do not edit scoring, market map, notification, mail, runtime, deploy, config, gate, or UI files.

## 16. Required tests

Module tests:

- deterministic policy classification
- mirrored Long/Short behavior
- pinned-case event classification from a compact sanitized row
- BOTH conflict behavior
- no future outcome leakage into candidate fields
- 1h/2h/4h outcome labels
- threshold-first ordering
- unresolved OHLCV handling
- episode deduplication
- stable IDs and sort order
- calibration/validation split
- metrics and proposal eligibility
- actual pair fail-closed
- atomic output rollback
- deterministic rerun
- compact privacy-safe summary

CLI tests:

- successful explicit-path run
- missing required column
- malformed JSON-list field
- actual pair incomplete
- replace-output behavior
- stdout JSON excludes raw rows

## 17. Validation

Minimum validation:

```bash
./.venv312/bin/python -m unittest tests.test_turning_volatility_precursor_replay
./.venv312/bin/python -m unittest tests.test_log_feedback.LogFeedbackCliTests
./.venv312/bin/python tools/log_feedback.py replay-turning-volatility-precursors <explicit fixture arguments> --stdout-json

git diff --check
```

Use the exact matching CLI test class/method if the existing class name differs. Do not run the full repository suite.

A single bounded replay may be run against the current explicit local signal/OHLCV inputs after unit tests pass. It must write generated outputs under `local/` or `logs/` and must not commit them.

## 18. Success criteria

Implementation is complete when:

- all policy families are deterministic and symmetric
- current notifications and precursor policies are compared on the same resolved events
- the pinned case is measured without special-case production logic
- large-move recall, precision, false-warning burden, lead time, Long/Short, regime, and validation metrics are reported
- outputs are atomic and reproducible
- no production behavior changes
- the report states one of:
  - `insufficient_evidence`
  - `continue_shadow_collection`
  - `eligible_for_notification_proposal`

It must never state that production was changed or that profitability was proven from proxy evidence.

## 19. Responsibility boundary

Deterministic code calculates events and metrics.

ChatGPT reviews:

- whether the policy catches recurring missed moves
- whether Long/Short are balanced
- whether false-warning burden is acceptable
- whether market-map interpretation or notification behavior should be proposed separately

Human approval is required before any production notification or scoring change.

## 20. Archive condition

Archive this spec only after:

- source and CLI implementation pass targeted validation
- one bounded replay result is generated or explicitly unavailable due to missing input
- ChatGPT reviews the compact report
- no production behavior changed

The next spec, if evidence supports it, must separate:

1. market-map/scoring correction proposal
2. notification precursor proposal

Do not combine those change classes in one production implementation.

## 21. Fresh OHLCV implementation clarification

The canonical `logs/csv/active_plan_intraperiod_ohlcv.csv` is not fresh enough for the pinned case. The implementation must therefore support the accepted public-fetch path used by `manual_operator_operating_cycle`.

Add optional CLI arguments:

- `--fetch-public-ohlcv`
- `--ohlcv-limit` with default 500

Rules:

- when `--fetch-public-ohlcv` is present, fetch public BTC_USDT 15-minute OHLCV into the atomic temporary stage and use it as the replay input
- reuse the accepted fetch/validation behavior from `src/feedback/manual_operator_operating_cycle.py`; do not invent another exchange route
- do not persist raw fetched OHLCV as a committed source artifact
- include the fetched OHLCV fingerprint, minimum timestamp, maximum timestamp, row count, source, symbol, and interval in the replay JSON
- when explicit `--ohlcv` and `--fetch-public-ohlcv` are both provided, public fetch takes precedence and the summary must state `ohlcv_source=public_fetch`
- the bounded real replay must use `--fetch-public-ohlcv --ohlcv-limit 500` with `logs/csv/trades.csv`
- the pinned case is `pinned_case_unavailable` if the 500-row window cannot cover its event and required future horizon

CLI precedence correction: `--ohlcv` is required only when `--fetch-public-ohlcv` is absent. A public-fetch replay may omit `--ohlcv`. Tests must cover both explicit-file and public-fetch argument validation.
