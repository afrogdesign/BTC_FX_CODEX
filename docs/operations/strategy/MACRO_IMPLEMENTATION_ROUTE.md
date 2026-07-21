# Macro Implementation Route

last_updated: 2026-07-21
status: canonical macro route

## Purpose

M計画は、公開市場データから大局構造と信頼できるhigher-timeframe support/resistanceを自動的に更新し、manual 15-minute trading判断を補強するrouteである。

本体Product計画を置き換えない。Private actual-trade evidenceがなくても、市場構造計算、信頼度更新、history、local operator artifactは進める。

## Controlling objective

```text
public 15m / 1h / 4h OHLCV
→ stable reliable-level map
→ prior-only lifecycle and reliability
→ current structural location
→ confidence-labelled support/resistance
→ next reliable target and obstruction
→ chronological reliability continuity
→ chart-first operator artifact
```

Nearest lineや単一pivotだけでは高信頼にしない。Weak, stale, discontinuous, or one-sided evidence must fail closed to `insufficient`.

## Accepted foundation

| Phase | Result | Status |
|---|---|---|
| M1 | reliable macro levels, lifecycle, event-time replay | accepted |
| M2 | optional disabled-by-default P8 auxiliary shadow | accepted |
| M3 | tactical bias and next-regime risk separation | accepted |
| M4 | chart-first local render shadow | accepted |
| M5 | bounded champion/challenger proposal engine | accepted |
| M6 | approved proposal adoption | not started / not authorized |

M1–M5 created the analysis, evidence, UI-shadow, and proposal foundations. They did not complete normal autonomous operation.

## Two-lane route

### Primary lane: autonomous operation

Canonical plan:

- `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

```text
M-OPS1 current snapshot and daily report — accepted at 89bd338
→ M-OPS2 chronological history and reliability continuity — current
→ M-OPS3 chart-first operator artifact
→ M-OPS4 separate runtime/schedule enablement
→ M-OPS5 autonomous health and stale-data status
```

### Secondary lane: improvement and adoption

Canonical plan:

- `M5_M6_EXECUTION_PLAN_20260721.md`

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

## Accepted M-OPS1

Accepted source checkpoint: `89bd338`.

Command:

- `run-macro-structure-daily`

Accepted behavior:

- public 15m/1h/4h only;
- actual common closed-candle cutoff;
- observable normalized evaluation time;
- stable M1 level identity and prior-only reliability;
- original side separated from current role;
- canonical structure/location, nearest zones, targets, obstruction, volatility, activation, freshness, and continuity;
- valid `insufficient` output;
- immutable complete run artifacts and atomic compact latest summary;
- deterministic identity and conflict-safe publication;
- no runtime or delivery mutation.

Do not reopen M-OPS1 without a concrete source or contract defect.

## Current source task — M-OPS2

Active spec:

- `chatgpt/specs/active/20260721_macro_structure_chronological_history_continuity.md`

Work ID:

- `BTCFX-20260721-MACRO-STRUCTURE-CHRONOLOGICAL-HISTORY-CONTINUITY`

Expected result:

- `run-macro-structure-history` report-only command;
- complete direct-child M-OPS1 source-run validation;
- explicit symbol isolation;
- chronological evaluation rows;
- freshness-only reevaluations distinguished from unique structural checkpoints;
- stable `level_id` continuity;
- reliability, role, lifecycle, and evidence transitions;
- absence and reappearance without invented permanent retirement;
- structure/location/target/obstruction/stale/continuity changes;
- deterministic immutable history artifacts;
- atomic compact history latest summary;
- bounded multi-date no-future fixture evidence.

Do not wait for M5 evidence refresh before implementing M-OPS2.

## M5 and M6 boundary

Accepted M5 result:

- checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

M5 is rerun only after its documented trigger. M6 requires one eligible challenger, adequate evidence, explicit human approval, and separate source/validation/adoption/runtime steps.

## Human involvement

No recurring human input is required for public OHLCV collection, structure calculation, local snapshot/report generation, chronological reliability history, or health status.

Explicit human approval is required for installed runtime/schedule changes, live delivery integration, production policy changes, M6 adoption, automatic execution, and version/phase promotion.

## Completion boundary

M route is not complete until:

- M-OPS1 current snapshot is accepted;
- M-OPS2 history and latest status are accepted;
- M-OPS3 chart-first operator output is accepted;
- a separately approved runtime cadence is verified;
- stale and insufficient states fail closed;
- health/status and current docs match actual behavior.

## Canonical references

- overall plan: `docs/operations/ai-orchestration/MASTER_PLAN.md`
- autonomous completion: `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- M5/M6 route: `M5_M6_EXECUTION_PLAN_20260721.md`
- accepted M-OPS1 spec: `chatgpt/specs/archive/20260721_macro_autonomous_structure_daily_operation.md`
- active M-OPS2 spec: `chatgpt/specs/active/20260721_macro_structure_chronological_history_continuity.md`
- current state/task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`

## Safety and version boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no automatic production mutation
- no runtime, delivery, gate, threshold, scoring, or classifier change without separate approval
- human decides trades and production adoption

M-OPS source and local evidence remain within Ver04.x. Local M-OPS completion alone does not automatically promote the version.
