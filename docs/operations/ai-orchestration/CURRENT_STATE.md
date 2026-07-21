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
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: `chatgpt/specs/active/20260721_macro_structure_chart_first_operator_artifact.md`
- safety: report-only / human-decided / no automatic order
- push: none

MCP does not independently expose git branch, HEAD, commit objects, or the complete dirty tree. Branch and commit locators come from bounded local-git reports; acceptance-critical source, tests, CLI routes, specs, state paths, and artifacts are reviewed directly through MCP.

## Product / P state

- P1–P7 accepted
- P8 evidence pipeline accepted and collecting evidence
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

Completion route:

```text
public 15m / 1h / 4h OHLCV
→ stable support/resistance identity
→ prior-only reliability and lifecycle
→ current structural location
→ confidence-labelled zones
→ next target and obstruction
→ chronological evidence history
→ chart-first operator artifact
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

M5 remains secondary. Its accepted result remains:

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
- canonical structure/location, nearest zones, targets, obstruction, volatility, activation, freshness, continuity, and valid `insufficient`;
- complete immutable run artifacts plus atomic compact latest summary;
- byte-conflict-safe deterministic publication;
- no private actual-trade dependency;
- no runtime, mail, notification, policy, or order mutation.

Reviewed evidence:

- `local/reports/macro_structure/mops1_final_review/`

Do not reopen M-OPS1 without a concrete source or input-contract defect.

## Accepted M-OPS2

Accepted at `dea0e33`.

Command:

- `run-macro-structure-history`

Accepted behavior:

- reads only complete direct-child M-OPS1 immutable runs;
- preserves every evaluation run;
- separates freshness-only reevaluations from unique structural checkpoints;
- uses earliest evaluation as canonical structural source and latest evaluation for current freshness/status;
- exposes stable `level_id` continuity, reliability changes, role/lifecycle changes, geometry changes, evidence deltas, absence, reappearance, and `absent_from_latest`;
- does not infer permanent retirement;
- validates source identity, timestamps, public/report-only boundary, and unique non-empty level IDs;
- publishes deterministic v2 immutable history artifacts and atomic latest summary;
- preserves legacy v1 artifacts alongside v2;
- keeps transition events identifiable by `level_id`;
- no live fetch, private input, runtime, delivery, policy, or order mutation.

Reviewed evidence:

- `local/reports/macro_structure/mops2_review/history/`
- accepted latest v2 artifact: `history_037b8f5e06b11d7cfa5d`
- legacy v1 artifacts remain untouched

Do not reopen M-OPS2 without a concrete source or artifact contradiction.

## Current M route

```text
M-OPS1 current snapshot and daily report source — accepted
→ M-OPS2 chronological history and confidence continuity — accepted
→ M-OPS3 chart-first operator artifact — current
→ M-OPS4 separately approved runtime/schedule enablement
→ M-OPS5 autonomous health and stale-data status
```

Secondary improvement lane remains:

```text
accumulated evidence
→ periodic bounded M5 refresh
→ optional one-candidate M6 proposal
→ explicit human approval
→ source-only shadow and validation
→ separate runtime adoption
```

## Current selected action

Implement M-OPS3 under:

- work ID: `BTCFX-20260721-MACRO-STRUCTURE-CHART-FIRST-OPERATOR-ARTIFACT`
- active spec: `chatgpt/specs/active/20260721_macro_structure_chart_first_operator_artifact.md`

Expected product result:

- one deterministic self-contained local HTML/SVG operator artifact;
- latest accepted M-OPS1 snapshot and M-OPS2 v2 history as the only macro sources;
- explicit local public 15-minute OHLCV for the chart;
- current price and reliable macro zones shown first;
- structure, location, targets, obstruction, volatility, activation, freshness, continuity, and recent history visible;
- stale, discontinuous, and insufficient states shown prominently;
- macro-only surface with no tactical Entry/SL/TP or execution implication;
- immutable complete artifact set plus atomic latest summary;
- no live fetch, delivery, production UI, runtime, policy, or order changes.

## Human involvement boundary

No recurring human input is required after setup for public OHLCV collection, structure calculation, reliability updates, local artifacts, history, or health status.

Explicit human approval remains required for:

- installed runtime/schedule enablement
- live mail or notification integration
- production gates, thresholds, scoring, classifiers, or policy
- M6 adoption
- automatic order behavior
- phase/version promotion

## Version and safety policy

- remain on `Ver04-v3` for M-OPS source, local artifacts, and planning
- M-OPS completion does not automatically declare `Ver05`
- generated evidence remains ignored and uncommitted under `local/`
- no raw exchange export commit
- no automatic order
- no private/account/order endpoints
- no unapproved notification, mail, runtime, launchd, gate, threshold, scoring, or classifier change
- no frozen runtime repo access without an explicit `RUNTIME_TASK`
