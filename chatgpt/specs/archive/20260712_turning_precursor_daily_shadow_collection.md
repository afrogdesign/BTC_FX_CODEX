# Turning / Volatility Precursor Daily Shadow Collection — Active Specification

## Metadata

- work_id: `BTCFX-20260712-P8-TURNING-PRECURSOR-DAILY-SHADOW`
- status: approved for bounded source implementation
- phase: P8 operating evidence collection
- change_class: report-only daily shadow evidence integration
- created_at: `2026-07-12`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Decision

The corrected turning / volatility precursor replay is accepted as an offline evidence tool at commit `9f4f6a1`.

The evidence does not authorize live notification behavior.

Corrected replay result:

- 2,872 signal rows
- 28 independent realized-move opportunities
- current notification recall: 0.392857
- Combined precursor recall: 0.214286
- Combined clean directional precision: 0.307692
- Combined false rate: 0.384615
- Combined opposite rate: 0.192308
- Combined median lead: about 70 minutes
- validation Combined resolved: 6
- validation UP resolved: 0
- validation DOWN resolved: 6
- validation false rate: 0.666667
- actual-backed count: 0
- pinned 07:05 case: caught before move
- recommendation: `continue_shadow_collection`

The next safe step is to connect the accepted replay to the daily P8 operating cycle as an opt-in shadow evidence stage.

This is not a notification proposal and not a production tuning task.

## 2. Objective

Collect reproducible turning / volatility precursor evidence automatically with the daily P8 cycle while:

- reusing the same public 15-minute OHLCV fetch
- preventing a second exchange fetch
- limiting signal input to the OHLCV coverage window
- preserving date-scoped generated artifacts
- exposing compact success/failure status
- keeping the existing core P8 cycle independent and safe
- keeping the new stage disabled by default
- making no mail, notification, scoring, market-map, gate, threshold, runtime schedule, or order change

## 3. Non-goals

This task does not:

- enable the shadow stage in the installed launchd job
- edit the launchd plist
- change the daily schedule
- send a precursor email
- change the notification trigger
- display the precursor in production HTML
- change Long/Short scoring
- change market-map state
- change any execution or opportunity gate
- change the accepted precursor policies
- tune from the 07:05 case
- activate P9
- claim profitability
- use private/account/order endpoints

## 4. Activation boundary

The feature must be opt-in.

Add an explicit CLI flag:

```text
--include-turning-precursor-shadow
```

Rules:

- default is disabled
- the currently installed daily launchd invocation remains behaviorally unchanged
- no plist or runtime installation change is permitted in this source task
- a later explicit runtime task is required to enable the flag for the scheduled cycle
- dry-run output must make enabled/disabled state visible

## 5. Integration point

Use the accepted P8 operating-cycle runner:

```text
src/feedback/manual_operator_operating_cycle.py
```

The precursor shadow stage runs only after:

- public or explicit OHLCV is validated
- core candidate and signal lineage is valid
- P4, P5 and P8 core stages succeed

The stage must reuse the already available validated OHLCV path or frame.

It must not call `_fetch_ohlcv` a second time.

## 6. Signal slice contract

The previous full-history replay produced a high unresolved rate because 2,872 signals were compared with a 500-candle OHLCV window.

Daily shadow collection must build a bounded signal slice from the explicit signal context input.

Required behavior:

1. Read only the supplied signal context CSV.
2. Validate the accepted turning precursor signal contract.
3. Use the current validated OHLCV minimum and maximum timestamps.
4. Select signals whose event timestamp is within the OHLCV window.
5. Include at most three hours of immediately preceding signal context when available, only to preserve episode continuity.
6. Pre-window context rows must not become resolved performance rows.
7. Signals later than the OHLCV maximum remain excluded.
8. Signals too close to the right boundary for a four-hour outcome may be emitted as unresolved shadow evidence but never counted as resolved performance.
9. Sort deterministically by timestamp and signal ID.
10. Write a generated `turning_signal_slice.csv` only inside the date-scoped output transaction.

Boundary handling:

- events beginning before the valid outcome window are marked `left_boundary_context`
- events without four hours of contiguous future candles are `right_boundary_unresolved`
- neither boundary class contributes to precision, recall, false-rate, opposite-rate, whipsaw-rate, validation, or proposal gates

## 7. Output contract

When enabled and successful, add a subdirectory under the normal date output root:

```text
logs/p8_operating_cycles/YYYYMMDD/turning_precursor_shadow/
```

Required generated files:

```text
turning_signal_slice.csv
turning_volatility_precursor_events.csv
turning_volatility_precursor_replay.json
turning_volatility_precursor_replay.md
```

Generated outputs remain local and uncommitted.

The existing core P8 output names and schemas remain valid.

## 8. Core-cycle failure independence

The precursor stage is auxiliary evidence.

Required behavior:

- if core P8 fails, do not run precursor shadow
- if core P8 succeeds and precursor is disabled, record `disabled`
- if core P8 succeeds and precursor succeeds, record `success`
- if core P8 succeeds and precursor fails, preserve core P8 outputs and record `failed`
- precursor failure must not erase or roll back successful core P8 outputs
- precursor failure must not cause mail, restart, retry loops, or automatic fallback
- do not repeat public OHLCV fetch after failure

The runner may return overall core success with a compact warning code:

```text
turning_precursor_shadow_failed
```

## 9. Manifest and summary additions

Add a compact `turning_precursor_shadow` object to the cycle manifest and cycle summary.

Required fields:

- enabled
- status: `disabled` / `success` / `failed`
- method_version
- signal_slice_rows
- precursor_episodes
- resolved_episodes
- realized_move_opportunities
- current_notification_recall
- combined_recall
- combined_precision
- combined_false_rate
- combined_opposite_rate
- combined_whipsaw_rate
- combined_median_lead_minutes
- validation_status
- validation_up_resolved
- validation_down_resolved
- pinned_case_status
- actual_backed_count
- recommendation_status
- output_subdir
- error_codes

Do not include raw rows, reason payloads, private paths, or full reports in the manifest summary object.

## 10. Daily wrapper contract

Update:

```text
tools/run_p8_daily_cycle.py
```

Add:

```text
--include-turning-precursor-shadow
```

Rules:

- default false
- when true, append the corresponding flag to the child `run-p8-operating-cycle` argv
- dry-run JSON shows whether the shadow stage is enabled
- `p8_daily_cycle_last_result.json` includes the compact `turning_precursor_shadow` object
- existing actual episode/link pair behavior remains unchanged
- existing core counts and readiness fields remain unchanged
- no second subprocess for precursor replay
- no second public OHLCV fetch

## 11. Atomicity

Core P8 promotion and precursor shadow promotion must be deterministic.

Preferred behavior:

- core outputs retain their existing transaction
- precursor output subdirectory is built in the same temporary root
- on precursor success, promote the complete subdirectory atomically
- on precursor failure, do not promote a partial precursor subdirectory
- core outputs may still promote successfully
- same-day rerun with replace enabled replaces the whole precursor subdirectory
- no stale mixed-version files remain

## 12. Reuse requirements

Reuse the accepted implementation:

```text
src/feedback/turning_volatility_precursor_replay.py
```

Do not duplicate its policy classification or outcome logic inside the operating-cycle runner.

Allowed small extensions to the replay module:

- explicit signal-slice helper
- boundary data-quality fields
- compact summary extraction helper
- output-root transaction helper

Do not change the accepted policy semantics or proposal gates without a separate evidence-backed spec.

## 13. Validation run

After targeted tests pass, perform one opt-in bounded run using test-only local output paths.

Use the daily wrapper so the complete one-fetch path is exercised:

```bash
./.venv312/bin/python tools/run_p8_daily_cycle.py \
  --date 20260712 \
  --include-turning-precursor-shadow \
  --output-base local/p8_turning_precursor_shadow_acceptance \
  --status-path local/p8_turning_precursor_shadow_acceptance/last_result.json
```

Requirements:

- exactly one child operating-cycle invocation
- exactly one public OHLCV fetch inside that child
- no mail
- no runtime restart
- no launchd modification
- no generated outputs committed
- compact status only in the task report

## 14. Required tests

### Operating-cycle tests

- shadow disabled preserves existing output contract
- shadow enabled reuses the provided OHLCV input and does not call fetch twice
- bounded signal slice respects OHLCV minimum and maximum
- three-hour prior context is context-only
- left boundary does not enter resolved metrics
- right boundary remains unresolved
- successful shadow writes all four files
- shadow failure preserves successful core outputs
- partial shadow files are not promoted
- same-day replace replaces the entire shadow subdirectory
- manifest contains compact shadow summary
- manifest excludes raw rows and private paths
- deterministic rerun is byte-identical for stable inputs

### Daily-wrapper tests

- default argv does not include the shadow flag
- opt-in argv includes the shadow flag exactly once
- dry-run reports enabled state
- success status includes compact shadow summary
- shadow warning remains distinguishable from core failure
- actual pair behavior is unchanged

### Regression tests

- accepted precursor policy tests remain passing
- no notification, mail, scoring, market-map, gate, runtime, or order modules are changed

## 15. Allowed implementation files

- `src/feedback/manual_operator_operating_cycle.py`
- `src/feedback/turning_volatility_precursor_replay.py`
- `tools/log_feedback.py`
- `tools/run_p8_daily_cycle.py`
- `tests/test_manual_operator_operating_cycle.py`
- `tests/test_turning_volatility_precursor_replay.py`
- `tests/test_run_p8_daily_cycle.py`
- this active spec, moved to archive after successful bounded validation
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/CONTROL.md`

Do not edit:

- scoring
- market map
- notification trigger or formatting
- mail
- config thresholds
- execution/opportunity gates
- deploy plist
- launchd
- runtime startup scripts
- APIs
- account/order code

## 16. Minimum validation

```bash
./.venv312/bin/python -m unittest tests.test_turning_volatility_precursor_replay
./.venv312/bin/python -m unittest tests.test_manual_operator_operating_cycle
./.venv312/bin/python -m unittest tests.test_run_p8_daily_cycle
<one bounded opt-in wrapper run>
git diff --check -- <authorized files>
```

Do not run the full test suite.

## 17. Completion and archive condition

Archive this spec only when:

- targeted tests pass
- bounded opt-in wrapper run succeeds
- the status confirms one core cycle and one precursor shadow stage
- generated shadow output is date-scoped and complete
- core P8 outputs remain valid
- no live runtime schedule was enabled
- no production behavior changed

After archive, the next action is human review of a separate runtime-enable proposal.

A later runtime task may enable the flag only with explicit approval and must not change the schedule or mail behavior.

## 18. Success criteria

The task is successful when:

1. Daily P8 can optionally collect precursor evidence with one OHLCV fetch.
2. Full-history unresolved noise is avoided through bounded signal slicing.
3. Core P8 success is not destroyed by auxiliary shadow failure.
4. Compact daily status makes precursor evidence visible.
5. The installed schedule remains unchanged and the feature remains disabled by default.
6. No production signal, notification, mail, order, or runtime behavior changes.
7. The system is ready for a separately approved period of automatic shadow collection.

## 19. Bounded implementation completion

- implementation: opt-in shadow integration completed in the P8 operating-cycle runner
- default_enabled: false
- installed_runtime_enabled: false
- bounded_wrapper_cycle: success (2026-07-12)
- core_cycle: success; precursor_shadow: success
- signal_slice_rows: 127
- precursor_episodes: 175; resolved_episodes: 26
- realized_move_opportunities: 28
- current_notification_recall: 0.428571
- combined_recall: 0.25; combined_precision: 0.307692
- combined_false_rate: 0.384615; combined_opposite_rate: 0.192308; combined_whipsaw_rate: 0.115385
- combined_median_lead_minutes: 69.9885
- validation_status: established (UP=0, DOWN=6)
- pinned_case_status: caught_before_move
- actual_backed_count: 0
- recommendation_status: `continue_shadow_collection`
- targeted tests: turning precursor 19, operating cycle 22, daily wrapper 18 passed
- one public OHLCV fetch path was reused; no second fetch or subprocess was used for shadow replay
- no production scoring, notification, mail, runtime, launchd, API, account, order, or P9 behavior changed
- installed schedule remains unchanged and the feature remains disabled

The source of truth is archived after bounded validation. Any runtime enablement requires a separate explicit HUMAN_CHECK task.
