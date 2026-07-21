# Macro Implementation Route

last_updated: 2026-07-21
status: canonical macro route

## Purpose

M計画は、公開市場データから大局構造と信頼できるhigher-timeframe support/resistanceを自動的に更新し、manual 15-minute trading判断を補強するrouteである。

本体Product計画を置き換えない。しかし、private actual-trade evidenceがなくてもMの市場構造計算・信頼度更新・local operator artifactは進める。

## Controlling objective

完成時の主線:

```text
public 15m / 1h / 4h OHLCV
→ stable reliable-level map
→ prior-only lifecycle and reliability
→ current structural location
→ support/resistance confidence bands
→ next reliable target and obstruction
→ chart-first operator artifact
→ autonomous chronological collection
```

`high reliability`は過去のinteraction evidenceに基づく。nearest lineや単一pivotだけでは高信頼にしない。

Weak, stale, discontinuous, or one-sided evidence must fail closed to `insufficient`.

## Research priority

```text
reliable level map
→ level reliability history
→ current structural location
→ volatility state
→ pressure / activation evidence
→ next reliable target
→ outcome resolution
→ periodic improvement proposal
```

Midpoint and compression are auxiliary variables, not standalone directional triggers.

## Accepted foundation

| Phase | Result | Status |
|---|---|---|
| M1 | reliable macro levels, lifecycle, event-time replay | accepted |
| M2 | optional disabled-by-default P8 auxiliary shadow | accepted |
| M3 | tactical bias and next-regime risk separation | accepted |
| M4 | chart-first local render shadow | accepted |
| M5 | bounded champion/challenger proposal engine | accepted |
| M6 | approved proposal adoption | not started / not authorized |

M1–M5 acceptance created the analysis, evidence, UI-shadow, and proposal foundations. It did not complete normal autonomous operation.

## Two-lane route

### Primary lane: autonomous operation

Canonical plan:

- `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Sequence:

```text
M-OPS1 dedicated current snapshot and daily report source
→ M-OPS2 chronological history and reliability continuity
→ M-OPS3 chart-first operator artifact
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

The secondary lane must not block M-OPS1–M-OPS3.

## Current source task

Active spec:

- `chatgpt/specs/active/20260721_macro_autonomous_structure_daily_operation.md`

Work ID:

- `BTCFX-20260721-MACRO-AUTONOMOUS-STRUCTURE-DAILY-OPERATION`

Expected result:

- dedicated report-only current macro snapshot command
- public-data only
- deterministic common closed-candle cutoff
- accepted M1 semantics reused
- confidence-labelled support/resistance zones
- current location, target, and obstruction
- local date/time-scoped artifacts
- atomic compact latest status
- no runtime/schedule application in the source task

Do not wait for M5 evidence refresh before implementing this task.

## M5 boundary

Accepted M5 result:

- checkpoint locator: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- champion: 1
- challengers: 4
- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

This is a valid fail-closed improvement result. It does not imply that macro operation should remain disabled.

M5 is rerun only after its documented trigger. It is never run as part of M-OPS1 source implementation.

## M6 boundary

M6 requires:

1. one proposal-eligible challenger;
2. adequate comparison and validation evidence;
3. no hidden material directional/regime damage;
4. explicit conflict reporting for actual evidence;
5. one bounded proposal;
6. explicit human approval.

M6 source, validation, adoption, and runtime apply remain separate.

M6 is not required to operationalize already accepted M1–M4 behavior through M-OPS.

## Human involvement

No recurring human input is required for:

- public OHLCV collection
- structure and reliable-level calculation
- local snapshot/report generation
- chronological reliability history
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

- a dedicated autonomous current snapshot route exists;
- confidence-labelled zones are generated from public data;
- history and latest status are maintained atomically;
- chart-first operator output exists;
- a separately approved runtime cadence is verified;
- stale and insufficient states fail closed;
- current docs and operator runbook match actual behavior.

## Canonical references

- overall plan: `docs/operations/ai-orchestration/MASTER_PLAN.md`
- autonomous completion: `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- M5/M6 secondary route: `M5_M6_EXECUTION_PLAN_20260721.md`
- research basis: `MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- accepted specs: `chatgpt/specs/archive/20260720_macro_*` and `chatgpt/specs/archive/20260721_macro_*`
- current state/task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`

## Safety

- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no automatic production mutation
- no runtime, mail, notification, gate, threshold, scoring, or classifier change without separate approval
- human decides trades and production adoption

## Version boundary

M-OPS source and local autonomous evidence remain within Ver04.x.

`Ver05` may be proposed only after an explicitly approved production adoption is implemented, validated, and accepted. Offline M1–M5 or local M-OPS completion alone does not automatically promote the version.
