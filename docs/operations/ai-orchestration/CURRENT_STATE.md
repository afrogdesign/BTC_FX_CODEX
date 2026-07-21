# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- current branch: `Ver04-v3` (reported by bounded local git execution)
- accepted repository-cleanup checkpoint: `bff7669`
- accepted Product checkpoint: `0eeb26b`
- accepted P state checkpoint: `b9ca3f6`
- accepted P/M planning checkpoint: `ee68e94`
- accepted M5 implementation checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- accepted M-OPS1 checkpoint: `89bd338`
- accepted M-OPS2 checkpoint: `dea0e33`
- accepted M-OPS3 checkpoint: `09330b9`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: `chatgpt/specs/active/20260721_macro_structure_runtime_service_enable.md`
- current transition: M-OPS4 explicitly approved for bounded implementation and installed service activation
- target label: `com.afrog.btc-macro-structure`
- safety: report-only / human-decided / no automatic order
- push: none

MCP does not independently expose git branch, HEAD, commit objects, installed launchctl state, or the complete dirty tree. Branch/commit/runtime evidence must be confirmed from bounded local execution; acceptance-critical source, tests, specs, state paths, and generated artifacts are reviewed directly through MCP.

## Product / P state

- P1–P8 accepted
- P9 blocked pending adequate actual-backed evidence and human approval

### P no-repeat boundary

`BTCFX-20260721-P8-ACTUAL-EVIDENCE-READINESS-REVIEW` is complete and accepted.

Confirmed blocker:

- no complete private MEXC Trade History / Order History / Position History batch under `local/manual_trade_imports/YYYYMMDD/`
- no generated actual-trade episode/link pair
- eligible actual-backed evidence remains 0
- this is an input-availability blocker, not an importer, linker, or P8 evaluator defect

Do not repeat importer, episode-builder, signal-linker, CLI, or readiness review unless one documented reopening trigger is true:

1. a complete private export batch appears;
2. relevant source/tests change;
3. a contradictory artifact appears;
4. the user explicitly requests re-verification.

Canonical decision: `DEC-20260721-012`.

## Macro / M purpose

The primary M objective is autonomous higher-timeframe market-structure understanding from public data.

```text
public 15m / 1h / 4h OHLCV
→ stable support/resistance identity
→ prior-only reliability and lifecycle
→ current structural location
→ confidence-labelled zones
→ next target and obstruction
→ chronological evidence history
→ chart-first operator artifact
→ installed report-only cadence
→ autonomous health/status
```

Private actual-trade evidence is not a prerequisite for market-structure operation. It remains relevant to human outcome evaluation and production adoption decisions.

Canonical plan:

- `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Canonical decision:

- `DEC-20260721-014`

## Macro accepted foundation

- M1 accepted: event-time levels, lifecycle, prior-only reliability, location, volatility, activation, target/obstruction, outcomes
- M2 accepted: opt-in public-data auxiliary macro shadow, disabled by default
- M3 accepted: tactical and next-regime separation
- M4 accepted: chart-first local render shadow at `ea89e61`
- M5 accepted: bounded champion/challenger proposal engine
- M6 not started and not authorized

Accepted M5 result remains:

- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

## Accepted M-OPS1

Accepted at `89bd338`.

Command:

- `run-macro-structure-daily`

Accepted behavior:

- public 15m/1h/4h only;
- deterministic actual common closed-candle cutoff;
- explicit normalized evaluation time;
- stable M1 level identity and prior-only evidence;
- original level side separated from current lifecycle role;
- structure/location, reliable zones, targets, obstruction, volatility, activation, freshness, continuity, and valid `insufficient`;
- complete immutable run artifacts plus atomic compact latest summary;
- byte-conflict-safe deterministic publication;
- no private actual-trade, runtime, delivery, policy, or order mutation.

Reviewed evidence:

- `local/reports/macro_structure/mops1_final_review/`

## Accepted M-OPS2

Accepted at `dea0e33`.

Command:

- `run-macro-structure-history`

Accepted behavior:

- complete direct-child M-OPS1 source validation;
- every evaluation plus unique structural checkpoints;
- earliest canonical structural source and latest freshness/status reevaluation separation;
- stable level identity, reliability, role, lifecycle, geometry, evidence deltas, absence, reappearance, and latest absence;
- deterministic v2 immutable history artifacts and atomic latest summary;
- legacy v1 preservation;
- identifiable level transition events;
- no live fetch, private input, runtime, delivery, policy, or order mutation.

Reviewed evidence:

- `local/reports/macro_structure/mops2_review/history/`
- accepted v2 artifact: `history_037b8f5e06b11d7cfa5d`

## Accepted M-OPS3

Accepted at `09330b9`.

Command:

- `render-macro-structure-operator`

Accepted behavior:

- exact direct-child latest M-OPS1 snapshot and M-OPS2 v2 history selection;
- selected snapshot is the latest evaluation of the final structural checkpoint;
- explicit public 15-minute OHLCV and no-future closed-candle filtering;
- current-price agreement;
- deterministic self-contained v2 HTML/SVG, JSON, Markdown, manifest, and atomic latest summary;
- latest 96 eligible 15-minute candles;
- all accepted high/medium support and resistance zones including non-nearest zones;
- low/insufficient zones not promoted;
- complete zone evidence without reliability/lifecycle recalculation;
- categorized structure, reliability, role, lifecycle, geometry, absence, reappearance, and stale/discontinuous history;
- display-level source traces;
- visible stale, continuity, data-quality, insufficient, checkpoint, and safety state;
- macro-only surface with no tactical Entry/SL/TP or execution implication;
- no live fetch, production UI, mail, notification, runtime, policy, or order mutation.

Reviewed evidence:

- `local/reports/macro_structure/mops3_review/`
- accepted latest v2 artifact: `operator_3f09d915f61d0183d51c`

Archived accepted spec:

- `chatgpt/specs/archive/20260721_macro_structure_chart_first_operator_artifact.md`

Do not reopen M-OPS1–M-OPS3 without a concrete source or artifact contradiction.

## Authorized M-OPS4

The user explicitly approved actual service implementation on 2026-07-21.

Work ID:

- `BTCFX-20260721-MACRO-STRUCTURE-RUNTIME-SERVICE-ENABLE`

Active spec:

- `chatgpt/specs/active/20260721_macro_structure_runtime_service_enable.md`

Approved target:

- new label only: `com.afrog.btc-macro-structure`
- primary repo runtime
- public OHLCV only
- M-OPS1 → M-OPS2 → M-OPS3
- JST schedule: 01:10, 05:10, 09:10, 13:10, 17:10, 21:10
- one compact atomic runtime status
- one bounded launchd-triggered live-public-data acceptance run

The task may inspect the frozen repo read-only to confirm installed target boundaries. It must not edit or run frozen-repo source/tests and must not deploy the new service there.

## Current M route

```text
M-OPS1 current snapshot and daily report source — accepted
→ M-OPS2 chronological history and confidence continuity — accepted
→ M-OPS3 chart-first operator artifact — accepted
→ M-OPS4 runtime/schedule enablement — explicitly approved and current
→ M-OPS5 autonomous health and stale-data status — not started
```

## Current selected action

Implement and activate the dedicated report-only macro LaunchAgent under the active spec.

Acceptance requires:

- local implementation commit;
- target-only installed plist and rollback evidence;
- loaded primary-repo contract;
- all six schedule entries;
- exactly one bounded kickstart;
- successful launchd-triggered snapshot/history/operator artifacts;
- compact success status;
- no unrelated runtime, mail, notification, policy, private endpoint, or order change.

## Human involvement boundary

No recurring human input is required after setup for public OHLCV collection, structure calculation, reliability updates, local artifacts, history, or health status.

Explicit human approval remains required for:

- live mail or notification integration
- production gates, thresholds, scoring, classifiers, or policy
- M6 adoption
- automatic order behavior
- phase/version promotion

M-OPS4 runtime approval is granted only for the target and boundaries recorded above.

## Version and safety policy

- remain on `Ver04-v3`
- M-OPS runtime activation does not automatically declare `Ver05`
- generated evidence remains ignored and uncommitted under `local/`
- no raw exchange export commit
- no automatic order
- no private/account/order endpoints
- no mail or notification change
- no production gate, threshold, scoring, or classifier change
- no unrelated LaunchAgent change
