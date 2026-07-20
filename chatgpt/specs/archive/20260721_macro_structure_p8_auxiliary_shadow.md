# M2 Macro Structure P8 Auxiliary Shadow — Active Specification

## Metadata

- work_id: `BTCFX-20260721-MACRO-STRUCTURE-P8-AUXILIARY-SHADOW`
- status: approved for bounded source implementation
- phase: M2 optional P8 auxiliary shadow
- change_class: report-only daily evidence integration
- created_at: `2026-07-21`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- accepted_m1_commit: `663288b`
- accepted_m1_spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- parent_plan: `docs/operations/strategy/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md`
- research_basis: `docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Decision

M1 is accepted as a deterministic offline evidence layer.

Accepted M1 capabilities include:

- event-time confirmed 1H and 4H pivots
- stable structural-level identity
- support, resistance, role-flip, rejection, break, acceptance, and reclaim lifecycle
- prior-only level reliability
- separate volatility state, expansion risk, directional activation, and reliable target
- independent UP, DOWN, and BOTH realized-move opportunities
- per-policy event-time episode deduplication
- comparative chronological validation gates
- explicit fail-closed missed-move diagnosis
- deterministic five-output atomic publication

M1 acceptance does not authorize a production policy, UI, notification, mail, threshold, gate, classifier, or runtime change.

The next safe step is an optional P8 auxiliary shadow stage that collects the accepted macro evidence automatically while remaining disabled by default.

## 2. Objective

Integrate the accepted M1 macro replay into the existing P8 operating-cycle path so that an explicit opt-in run can:

- reuse the validated P8 15-minute public OHLCV input
- obtain bounded public 1-hour and 4-hour OHLCV through the existing accepted fetcher
- build an event-time bounded signal slice
- run the accepted macro replay without changing its policy semantics
- write date-scoped generated shadow artifacts
- expose a compact manifest and daily-status summary
- preserve successful core P8 and turning-precursor outputs when the macro auxiliary stage fails
- remain disabled by default

## 3. Non-goals

M2 does not:

- enable the new flag in the installed LaunchAgent
- edit a plist or schedule
- restart the normal monitor or P8 runtime
- send mail or notifications
- alter notification selection
- alter structural priority or Big Chance production logic
- alter A/B/C/STOP classification
- alter scoring, thresholds, gates, or market-map logic
- start M3, M4, or M5
- use private, account, position, or order endpoints
- use actual trade evidence as a prerequisite
- claim profitability
- tune M1 parameters from one day or one example

## 4. Activation boundary

Add one explicit opt-in flag:

```text
--include-macro-structure-shadow
```

Rules:

- default is false
- the existing installed daily invocation remains behaviorally unchanged
- no deploy or runtime file may be edited in this task
- dry-run output must expose enabled or disabled state
- runtime enablement, if ever proposed, requires a separate human-approved task

## 5. Integration point

Primary integration target:

```text
src/feedback/manual_operator_operating_cycle.py
```

Daily wrapper:

```text
tools/run_p8_daily_cycle.py
```

Reuse the accepted replay implementation:

```text
src/feedback/macro_structure_volatility_replay.py
```

The macro stage runs only after the core P8 inputs and public 15-minute OHLCV are validated.

It is an auxiliary sibling of the existing turning-precursor shadow. Neither auxiliary stage may become a prerequisite for the other.

## 6. Market-data contract

### 6.1 Fifteen-minute OHLCV

- reuse the already validated core P8 15-minute OHLCV path or staged file
- do not perform a second 15-minute public fetch
- use the same bytes for core P8 and macro shadow within one operating cycle

### 6.2 One-hour and four-hour OHLCV

When macro shadow is enabled:

- fetch each required timeframe at most once
- use the existing accepted public fetcher and public-market configuration
- use no private endpoint
- validate interval, monotonic timestamps, duplicates, numeric OHLCV, and continuity
- record row counts, minimum and maximum timestamps, interval, source, and fingerprints
- use bounded fetch limits declared in the manifest
- fail the macro stage closed when required coverage is absent or malformed

The implementation may factor a small reusable public-OHLCV staging helper. It must not change the established core P8 fetch behavior.

## 7. Signal-slice contract

Build a deterministic macro signal slice from the explicit signal-context input.

Required behavior:

1. Read only the supplied signal-context CSV.
2. Preserve the accepted M1 required and optional field handling.
3. Determine the common event-time coverage supported by the 15-minute, 1-hour, and 4-hour inputs.
4. Include signals inside that common coverage.
5. Include only the bounded prior context needed for policy-episode continuity.
6. Mark prior-context rows as context-only when they cannot be performance rows.
7. Exclude signals later than the common maximum closed-candle time.
8. Keep right-boundary outcomes unresolved when future 15-minute coverage is insufficient.
9. Sort deterministically by timestamp and signal ID.
10. Write the generated signal slice only inside the macro shadow transaction.

No future candle may affect event-time structure or forecast fields.

## 8. Replay contract

Call the accepted M1 replay rather than reimplementing its logic in the operating-cycle runner.

Preserve:

- method and schema versions unless a real schema change is required
- level identity and prior-only reliability
- lifecycle semantics
- pressure and microstructure fail-closed behavior
- expansion-versus-direction separation
- policy episode semantics
- independent opportunity inventory
- validation gate semantics
- missed-move root-cause schema
- atomic five-output behavior

M2 may add only integration-oriented helpers such as:

- bounded signal slicing
- public OHLCV staging
- compact summary extraction
- auxiliary-directory promotion

M2 must not alter replay thresholds or policy definitions to improve daily results.

## 9. Output contract

When enabled and successful, write a date-scoped subdirectory under the existing P8 output root:

```text
macro_structure_shadow/
```

Required generated files:

```text
macro_signal_slice.csv
macro_structure_volatility_events.csv
macro_level_reliability.csv
macro_missed_move_diagnostics.csv
macro_structure_volatility_replay.json
macro_structure_volatility_replay.md
```

The implementation may retain bounded generated 1H and 4H OHLCV inputs in this subdirectory when needed for reproducibility. If retained, their names, fingerprints, and generated/local status must be explicit.

Generated artifacts remain local and uncommitted.

## 10. Failure independence and atomicity

Required behavior:

- if core P8 fails, do not run macro shadow
- if macro shadow is disabled, record `disabled`
- if enabled and successful, record `success`
- if enabled and failed, record `failed`
- macro failure must not roll back successful core P8 outputs
- macro failure must not roll back a successful turning-precursor shadow
- turning-precursor failure must not roll back a successful macro shadow
- do not promote a partial macro subdirectory
- replace-enabled reruns replace the complete macro subdirectory
- no stale mixed-version files remain
- no retry loop, mail, restart, or fallback fetch is triggered

A failed auxiliary stage may produce a compact warning while overall core P8 remains successful.

## 11. Manifest and compact status

Add a compact `macro_structure_shadow` object to:

- cycle manifest
- cycle summary
- operating-cycle stdout JSON
- daily status JSON
- daily wrapper stdout JSON

Required fields:

- `enabled`
- `status`: `disabled`, `success`, or `failed`
- `method_version`
- `schema_version`
- `signal_slice_rows`
- `ohlcv_15m_rows`
- `ohlcv_1h_rows`
- `ohlcv_4h_rows`
- `events`
- `levels`
- `missed_moves`
- `independent_opportunities`
- `recommendation_status`
- `recommendation_reasons`
- current-notification recall
- turning-precursor recall
- reliable-level acceptance-corridor recall
- validation status
- validation UP opportunity count
- validation DOWN opportunity count
- continuity status
- output subdirectory
- error codes

The compact object must not include raw event rows, full reports, secrets, private paths, or account data.

## 12. Daily-wrapper contract

Update the daily wrapper to accept:

```text
--include-macro-structure-shadow
```

Rules:

- default false
- append the child operating-cycle flag exactly once when enabled
- preserve the existing turning-precursor flag independently
- dry-run reports both auxiliary-stage enable states
- use one child operating-cycle invocation
- preserve actual episode/link pair validation
- daily status distinguishes macro warning from core failure and turning warning
- no second subprocess for the macro replay

## 13. Required tests

### Operating-cycle tests

- macro shadow disabled preserves the current core contract
- enabled macro shadow reuses the validated 15-minute OHLCV and does not fetch 15-minute data twice
- 1-hour and 4-hour public data are each fetched at most once
- malformed or incomplete macro timeframe input fails only the macro auxiliary stage
- deterministic signal slice respects common timeframe coverage
- prior context does not enter resolved performance metrics
- right-boundary rows remain unresolved
- successful macro shadow writes all required files
- partial macro files are not promoted
- macro failure preserves core outputs
- macro and turning shadows fail independently
- replace rerun replaces the whole macro subdirectory
- manifest contains only the compact macro summary
- deterministic rerun is byte-identical for stable explicit inputs

### Daily-wrapper tests

- default child argv omits the macro flag
- opt-in child argv includes it exactly once
- macro and turning flags can coexist exactly once
- dry-run exposes both enable states
- success status carries the compact macro summary
- macro warning is distinguishable from core and turning failures
- existing actual-input behavior remains unchanged

### Replay regressions

- accepted M1 replay tests remain passing
- macro CLI tests remain passing
- no production analysis, notification, mail, gate, scoring, classifier, runtime, or order module changes

## 14. Allowed implementation files

- `src/feedback/manual_operator_operating_cycle.py`
- `src/feedback/macro_structure_volatility_replay.py`
- `tools/log_feedback.py`
- `tools/run_p8_daily_cycle.py`
- `tests/test_manual_operator_operating_cycle.py`
- `tests/test_macro_structure_volatility_replay.py`
- `tests/test_run_p8_daily_cycle.py`
- `tests/test_log_feedback.py` only when the existing CLI route needs integration coverage
- this active spec, archived only after M2 acceptance
- orchestration state documents only at the later M2 acceptance milestone

Do not edit:

- production structural-priority or Big Chance modules
- public HTML or notification rendering
- notification selection or mail
- A/B/C/STOP classifier logic
- scoring, thresholds, or gates
- deploy plist or launchd
- runtime startup files
- APIs, accounts, positions, or orders

## 15. Validation

Run targeted tests once after implementation:

```bash
./.venv312/bin/python -m unittest tests.test_macro_structure_volatility_replay
./.venv312/bin/python -m unittest tests.test_manual_operator_operating_cycle
./.venv312/bin/python -m unittest tests.test_run_p8_daily_cycle
./.venv312/bin/python -m unittest tests.test_log_feedback.MacroStructureVolatilityCliTests
```

Then run one bounded opt-in daily-wrapper cycle using test-only local output and status paths.

Requirements:

- one child operating-cycle invocation
- one 15-minute fetch path
- at most one 1-hour and one 4-hour fetch
- complete macro output subdirectory
- compact status object
- no mail
- no runtime or launchd modification
- no generated output committed

Finally run:

```bash
git diff --check
```

Do not run the full test suite.

## 16. Completion and archive condition

M2 is complete only when:

- targeted tests pass
- one bounded opt-in wrapper cycle succeeds
- macro artifacts are date-scoped and complete
- core P8 outputs remain valid
- turning and macro auxiliary stages are independent
- the new flag remains disabled by default
- installed runtime and schedule remain unchanged
- no production behavior changes

After M2 acceptance, ChatGPT reviews collected evidence before deciding whether to continue shadow collection or create the separate M3 Big Chance next-regime shadow contract.

## 17. Safety boundary

- report-only
- not FORMAL_GO
- no automatic order
- no automatic tuning or production mutation
- no notification or mail behavior change
- no runtime restart or launchd change
- no API keys, secrets, private, account, position, or order endpoints
- human decides all trades and all production adoption


---

## 18. Acceptance record — 2026-07-21

M2 is accepted at source commit `8aee427`.

Accepted evidence:

- targeted replay, operating-cycle, daily-wrapper, and macro-CLI tests passed
- context rows preserve event-time episode continuity only
- published events, performance counts, persisted levels, split keys, metrics, dates, diagnostics, gates, and opportunity denominators use performance rows only
- replay summary records deterministic performance bounds and total/context/performance signal counts
- one fresh bounded wrapper cycle completed successfully
- wrapper status, cycle manifest, and cycle summary agree on macro shadow `success`
- complete date-scoped macro output set was published
- generated local artifacts remained uncommitted

Observed bounded result:

- events: `124`
- levels: `94`
- independent opportunities: `33`
- recommendation: `continue_shadow_collection`

Acceptance authorizes the optional disabled-by-default report-only M2 auxiliary shadow only. It does not authorize installed runtime enablement, M3 implementation, notification or mail changes, production scoring/gate/threshold/classifier changes, or automatic production mutation.
