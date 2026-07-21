# Macro Implementation Route

last_updated: 2026-07-21
status: canonical macro route

## Purpose

M計画は、公開市場データから大局構造と信頼できるhigher-timeframe support/resistanceを自動的に更新し、manual 15-minute trading判断を補強するrouteである。

Private actual-trade evidenceがなくても、Mの市場構造計算・信頼度更新・chronological history・local operator artifactは進める。

## Controlling objective

```text
public 15m / 1h / 4h OHLCV
→ stable reliable-level map
→ prior-only lifecycle and reliability
→ current structural location
→ support/resistance confidence bands
→ next reliable target and obstruction
→ chronological history
→ chart-first operator artifact
→ autonomous collection and health
```

`high reliability`は過去のinteraction evidenceに基づく。nearest lineや単一pivotだけでは高信頼にしない。

Weak, stale, discontinuous, or one-sided evidence must remain explicit and must not be promoted.

## Accepted foundation

| Phase | Result | Status |
|---|---|---|
| M1 | reliable macro levels, lifecycle, event-time replay | accepted |
| M2 | optional disabled-by-default P8 auxiliary shadow | accepted |
| M3 | tactical bias and next-regime risk separation | accepted |
| M4 | chart-first local render shadow | accepted at `ea89e61` |
| M5 | bounded champion/challenger proposal engine | accepted |
| M6 | approved proposal adoption | not started / not authorized |

M1–M5 acceptance created analysis, evidence, local UI-shadow, and proposal foundations. It did not by itself complete normal autonomous operation.

## Two-lane route

### Primary lane: autonomous operation

Canonical plan:

- `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Sequence and status:

```text
M-OPS1 dedicated current snapshot and daily report source — accepted at 89bd338
→ M-OPS2 chronological history and reliability continuity — accepted at dea0e33
→ M-OPS3 chart-first operator artifact — current
→ M-OPS4 separate runtime/schedule enablement
→ M-OPS5 autonomous health and stale-data status
```

This lane is the current priority.

### Secondary lane: improvement and adoption

Canonical plan:

- `M5_M6_EXECUTION_PLAN_20260721.md`

Sequence:

```text
accumulated accepted evidence
→ bounded M5 refresh
→ zero or one proposal-eligible challenger
→ explicit human-approved M6 proposal
→ source-only shadow
→ validation
→ separate adoption/runtime task
```

The secondary lane must not block unfinished M-OPS work.

## Accepted M-OPS source checkpoints

### M-OPS1

- checkpoint: `89bd338`
- command: `run-macro-structure-daily`
- public-data current snapshot
- deterministic common closed-candle cutoff and evaluation time
- accepted M1 semantics reused
- reliable zones, structure/location, targets, obstruction, volatility, activation, freshness, continuity
- immutable complete artifacts and atomic latest summary

### M-OPS2

- checkpoint: `dea0e33`
- command: `run-macro-structure-history`
- deterministic v2 chronological rollup
- every evaluation plus unique structural checkpoints
- stable level continuity, evidence changes, role/lifecycle/geometry changes, absence/reappearance/latest absence
- canonical versus latest evaluation separation
- identifiable level transition events
- immutable complete artifacts, legacy v1 preservation, and atomic latest summary

Do not reopen either accepted source without a concrete contradiction.

## Current source task

Active spec:

- `chatgpt/specs/active/20260721_macro_structure_chart_first_operator_artifact.md`

Work ID:

- `BTCFX-20260721-MACRO-STRUCTURE-CHART-FIRST-OPERATOR-ARTIFACT`

Expected result:

- new `render-macro-structure-operator` route;
- exact latest M-OPS1 snapshot and M-OPS2 v2 history selection;
- explicit local public 15-minute OHLCV input;
- closed-candle/no-future validation;
- self-contained chart-first HTML with inline SVG;
- high/medium reliable macro zones and current structural status;
- targets, obstruction, volatility, activation, freshness, continuity, and recent history;
- complete immutable operator artifacts and atomic latest summary;
- macro-only, report-only, no tactical or execution implication;
- no live fetch, delivery, production UI, runtime, or policy change.

## M5 boundary

Accepted M5 result:

- checkpoint locator: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

This valid fail-closed result does not imply that macro operation should remain disabled. M5 is rerun only after its documented trigger and never as part of M-OPS3.

## M6 boundary

M6 requires one proposal-eligible challenger, adequate evidence, one bounded proposal, and explicit human approval. It is not required to operationalize already accepted M1–M4 behavior through M-OPS.

## Human involvement

No recurring human input is required for:

- public OHLCV collection
- structure and reliable-level calculation
- snapshot and history generation
- local chart-first artifact generation
- health and stale-data status

Explicit human approval is required for:

- installed runtime/schedule changes
- live mail or notification integration
- production policy, gate, threshold, scoring, or classifier changes
- M6 adoption
- automatic order behavior
- version/phase promotion

## Completion boundary

M route is not complete until:

- current snapshot source is accepted;
- chronological history is accepted;
- chart-first operator output is accepted;
- a separately approved runtime cadence is verified;
- autonomous health/status is available;
- stale and insufficient states remain explicit;
- current docs and operator runbook match actual behavior.

## Canonical references

- overall plan: `docs/operations/ai-orchestration/MASTER_PLAN.md`
- autonomous completion: `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- M5/M6 secondary route: `M5_M6_EXECUTION_PLAN_20260721.md`
- research basis: `MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- accepted specs: `chatgpt/specs/archive/20260720_macro_*` and `chatgpt/specs/archive/20260721_macro_*`
- current state/task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`

## Safety and version boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no automatic production mutation
- no runtime, mail, notification, gate, threshold, scoring, or classifier change without separate approval
- human decides trades and production adoption
- M-OPS source and local autonomous evidence remain within Ver04.x
- `Ver05` requires explicitly approved production adoption and matching validation
