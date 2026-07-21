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

M1–M5 created analysis, evidence, local UI-shadow, and proposal foundations. They did not by themselves authorize installed recurring operation.

## Two-lane route

### Primary lane: autonomous operation

Canonical plan:

- `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Sequence and status:

```text
M-OPS1 dedicated current snapshot and daily report source — accepted at 89bd338
→ M-OPS2 chronological history and reliability continuity — accepted at dea0e33
→ M-OPS3 chart-first operator artifact — accepted at 09330b9
→ M-OPS4 separate runtime/schedule enablement — accepted at `a9b3d46` / runtime `690c014`
→ M-OPS5 autonomous health and stale-data status — next, not started
```

The current priority is the separate M-OPS5 health/status source task, not another M-OPS4 runtime run.

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

The secondary lane must not replace M-OPS4 authorization or M-OPS5 completion.

## Accepted M-OPS checkpoints

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

### M-OPS3

- checkpoint: `09330b9`
- command: `render-macro-structure-operator`
- exact latest M-OPS1 and M-OPS2 v2 source selection
- final structural checkpoint and latest reevaluation enforcement
- explicit public 15-minute OHLCV and no-future closed-candle validation
- final close/current-price agreement
- deterministic self-contained v2 chart-first artifact
- all high/medium zones including non-nearest support/resistance
- low/insufficient zone non-promotion
- complete zone evidence and categorized recent history
- truthful display-level traces
- immutable complete artifacts and atomic latest summary
- macro-only, report-only, no tactical or execution implication

Reviewed evidence:

- `local/reports/macro_structure/mops3_review/`
- accepted latest artifact: `operator_3f09d915f61d0183d51c`

Do not reopen accepted M-OPS1–M-OPS3 without a concrete contradiction.

## Current transition: M-OPS4 accepted

The runtime spec is archived after acceptance. M-OPS5 remains a separate source task.

M-OPS4 was completed under an explicit human-approved `RUNTIME_TASK` for the target only:

- reading, editing, or running the frozen runtime repo;
- inspecting or changing installed launchd/plist/cron/schedule configuration;
- installing a recurring macro pipeline.

The bounded task:

1. inspect the actual installed target and existing schedule;
2. confirm the runtime repo/path rather than assuming it;
3. connect accepted commands in order:
   - `run-macro-structure-daily`
   - `run-macro-structure-history`
   - `render-macro-structure-operator`;
4. enable one report-only cadence;
5. preserve rollback and unrelated configuration;
6. verify target-specific execution and generated local artifacts;
7. leave mail, notification, production policy, private/account/order access, and automatic orders unchanged.

M-OPS4 acceptance does not automatically authorize M-OPS5 implementation or production adoption.

## M-OPS5 boundary

M-OPS5 begins only after M-OPS4 acceptance as a separate source task.

It must expose success/failed/stale/insufficient status, input coverage, cutoff, artifact location, zone counts, continuity errors, and schema/method versions without triggering delivery or execution.

## M5 boundary

Accepted M5 result:

- checkpoint locator: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

This fail-closed result does not invalidate accepted M-OPS work. M5 is rerun only after its documented trigger.

## M6 boundary

M6 requires one proposal-eligible challenger, adequate evidence, one bounded proposal, and explicit human approval. It is not required to operationalize already accepted M-OPS behavior.

## Human involvement

No recurring human input is required for:

- public OHLCV collection
- structure and reliable-level calculation
- snapshot and history generation
- local chart-first artifact generation
- health and stale-data status after setup

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

The first three conditions are accepted. Runtime cadence and autonomous health remain.

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
