# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- current branch: `Ver04-v3` (reported by bounded local git execution)
- accepted repository-cleanup checkpoint: `bff7669`
- accepted Product checkpoint: `0eeb26b`
- accepted P state checkpoint: `b9ca3f6`
- accepted P/M planning checkpoint: `ee68e94`
- accepted M5 implementation checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: `chatgpt/specs/active/20260721_macro_autonomous_structure_daily_operation.md`
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

## Macro / M purpose — controlling interpretation

The primary M objective is autonomous higher-timeframe market-structure understanding from public data.

The system must ultimately maintain, without recurring human input:

```text
public 15m / 1h / 4h OHLCV
→ stable support/resistance identity
→ prior-only reliability and lifecycle
→ current structural location
→ high/medium/low/insufficient zones
→ next reliable target and obstruction
→ chart-first operator artifact
→ chronological evidence history
```

Private actual-trade evidence is not a prerequisite for this market-structure operation. It remains relevant to human outcome evaluation and production adoption decisions.

Canonical plan:

- `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Canonical decision:

- `DEC-20260721-014`

## Macro implementation state

Accepted research/tooling foundation:

- M1 accepted: event-time levels, lifecycle, prior-only reliability, location, volatility, activation, target/obstruction, outcomes
- M2 accepted: opt-in public-data auxiliary macro shadow, disabled by default
- M3 accepted: tactical and next-regime separation
- M4 accepted: chart-first local render shadow
- M5 accepted: bounded champion/challenger proposal engine
- M6 not started and not authorized

Accepted M5 result remains:

- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

M5 is not the current primary task. Its no-winner result does not block autonomous macro collection, current support/resistance reporting, history accumulation, or chart-first local artifacts.

## Corrected M route

The M route now has two lanes.

Primary completion lane:

```text
M-OPS1 dedicated current snapshot and daily report source
→ M-OPS2 chronological history and confidence continuity
→ M-OPS3 chart-first operator artifact
→ M-OPS4 separately approved runtime/schedule enablement
→ M-OPS5 autonomous health and stale-data status
```

Secondary improvement lane:

```text
accumulated evidence
→ periodic bounded M5 refresh
→ optional one-candidate M6 proposal
→ explicit human approval
→ source-only shadow and validation
→ separate runtime adoption
```

`DEC-20260721-013` still controls the M5-to-M6 sequence, but it no longer controls the overall M next action.

## Current selected action

Implement M-OPS1 under:

- work ID: `BTCFX-20260721-MACRO-AUTONOMOUS-STRUCTURE-DAILY-OPERATION`
- active spec: `chatgpt/specs/active/20260721_macro_autonomous_structure_daily_operation.md`

Expected product result:

- dedicated report-only current macro snapshot command
- public-data only
- no actual-trade dependency
- confidence-labelled support/resistance zones
- current structural location, target, and obstruction
- date/time-scoped generated artifacts under `local/reports/macro_structure/`
- atomic compact latest summary
- no runtime or schedule application in the source task

Do not wait for seven M5 dates or an M5 challenger before executing M-OPS1.

## Human involvement boundary

No recurring human input is required after setup for public OHLCV collection, structure calculation, reliability updates, local artifacts, history, or health status.

Explicit human approval remains required for:

- installed runtime/schedule enablement
- live mail or notification integration
- production gates, thresholds, scoring, classifiers, or policy
- M6 adoption
- automatic order behavior
- phase/version promotion

## Version policy

- remain on `Ver04-v3` for M-OPS source, local artifacts, and planning
- M-OPS completion by itself does not automatically declare `Ver05`
- `Ver05` remains evidence-backed, explicitly approved, implemented, validated, and accepted production adoption territory

## Repository and safety boundary

- generated evidence remains ignored and uncommitted under `local/`
- no raw exchange export commit
- no automatic order
- no private/account/order endpoints
- no unapproved notification, mail, runtime, launchd, gate, threshold, scoring, or classifier change
- no frozen runtime repo access without an explicit `RUNTIME_TASK`
