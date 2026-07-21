# Macro Autonomous Structure Operation Plan

created_at: 2026-07-21
last_updated: 2026-07-21
status: canonical completion route
primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
safety: report-only / not `FORMAL_GO` / no automatic order / human decides trades and production adoption

## 1. Purpose

M計画の主目的は、公開市場データから人間の継続入力なしで大局構造を更新し、manual 15-minute trading判断に使える信頼度付きsupport/resistanceを提供することである。

Completion state:

```text
public 15m / 1h / 4h OHLCV
→ stable higher-timeframe level identity
→ touch / rejection / break / acceptance / reclaim lifecycle
→ prior-only reliability history
→ current structural location
→ reliable support / resistance candidates
→ next reliable target and obstruction
→ chronological evidence accumulation
→ chart-first operator artifact
```

Private trade export is not a prerequisite for market-structure understanding. Actual trade evidence is separate evidence for human outcomes and production adoption.

## 2. Plan hierarchy

### Primary lane — autonomous macro operation

```text
M1 accepted structure/reliability engine
→ M-OPS1 current snapshot and daily artifact — accepted at 89bd338
→ M-OPS2 chronological history and confidence continuity — accepted at dea0e33
→ M-OPS3 chart-first operator artifact — current
→ M-OPS4 separate runtime/schedule enablement
→ M-OPS5 continuous health and stale-data monitoring
```

### Secondary lane — bounded improvement and adoption

```text
accumulated M evidence
→ periodic M5 champion/challenger refresh
→ optional one-candidate M6 proposal
→ explicit human approval
→ source-only shadow and validation
→ separate runtime adoption
```

M5/M6 must not block unfinished M-OPS work.

## 3. Accepted foundation and operation state

Accepted research/tooling:

- M1: deterministic event-time levels, lifecycle, prior-only reliability, structural location, volatility, activation, target/obstruction, outcomes, missed-move diagnostics
- M2: opt-in public-data auxiliary macro shadow
- M3: tactical and next-regime separation
- M4: chart-first local render shadow at `ea89e61`
- M5: deterministic bounded champion/challenger proposal engine

Accepted M-OPS1 checkpoint: `89bd338`.

M-OPS1 provides:

- dedicated `run-macro-structure-daily` route;
- public 15m/1h/4h inputs only;
- actual common closed-candle cutoff;
- normalized observable evaluation time;
- stable M1 level identity and prior-only evidence;
- original side and current role separation;
- structure/location, reliable zones, targets, obstruction, volatility, activation, freshness, continuity, and valid `insufficient`;
- complete immutable run artifacts and atomic latest summary;
- deterministic run identity and byte-conflict-safe publication.

Accepted M-OPS2 checkpoint: `dea0e33`.

M-OPS2 provides:

- `run-macro-structure-history`;
- complete direct-child source validation;
- every evaluation run plus deduplicated structural checkpoints;
- canonical structural source and latest freshness reevaluation separation;
- stable level identity, reliability, role, lifecycle, geometry, evidence, absence, reappearance, and latest-absence history;
- strict timestamp, version, symbol, public/report-only, and level-ID validation;
- deterministic v2 immutable history artifacts and atomic latest summary;
- legacy v1 artifact preservation;
- identifiable level transition events.

Known remaining gap:

- accepted current snapshot and chronological history exist;
- no accepted normal operator artifact yet presents the latest macro zones directly on a 15-minute chart.

## 4. Product contract

### 4.1 Current macro snapshot

Every successful daily run produces one deterministic snapshot as of the latest eligible common closed candle.

It exposes snapshot/evaluation times, input fingerprints, structure/location, current price, reliable zones, prior-only evidence, targets/obstruction, volatility/activation, stale/continuity status, and safety boundary.

The snapshot must not use future-confirmed geometry or later lifecycle outcomes.

### 4.2 Confidence language

Allowed labels:

- `high reliability`
- `medium reliability`
- `low reliability`
- `insufficient`

Nearest price alone is not reliability. Weak, stale, discontinuous, or one-sided evidence must not be promoted.

### 4.3 Chronological history

History must support every evaluation, unique structural checkpoints, stable level continuity, evidence changes, absence/reappearance, structure/location/target/obstruction changes, stale/continuity history, and deterministic later evaluation.

Do not infer permanent retirement from absence. Do not create mutable online learning.

### 4.4 Operator artifact

The primary operator surface must be chart-first and show, in order:

1. status and safety banner;
2. current price and 15-minute chart;
3. high/medium reliable macro zones;
4. current structural location;
5. targets and obstruction;
6. volatility, activation, freshness, and continuity;
7. recent chronological changes;
8. evidence details and limitations.

M-OPS3 is macro-only. Tactical Entry / SL / TP overlays are not included and must not be implied. Any later tactical overlay integration requires a separate contract and visual distinction.

## 5. Implementation phases

### M-OPS1 — accepted

Accepted at `89bd338`. Do not reopen without a concrete source or contract defect.

### M-OPS2 — accepted

Accepted at `dea0e33`. Do not reopen without a concrete source or artifact contradiction.

### M-OPS3 — current

Implement `render-macro-structure-operator`.

Required:

- exact latest M-OPS1 and M-OPS2 v2 source selection;
- proof that history contains the current snapshot;
- explicit public 15-minute OHLCV input;
- closed-candle/no-future validation;
- current-price/last-close agreement;
- self-contained inline SVG chart;
- deterministic reliable macro-zone overlays;
- visible stale/discontinuous/insufficient states;
- bounded chronological change panel;
- complete immutable operator artifacts and atomic latest summary;
- no live fetch, tactical selection, delivery, production UI, runtime, policy, or execution change.

Active spec:

`chatgpt/specs/active/20260721_macro_structure_chart_first_operator_artifact.md`

### M-OPS4 — runtime and schedule enablement

A separate explicit `RUNTIME_TASK` only after M-OPS3 acceptance and explicit human approval. Inspect the actual installed target, enable one report-only cadence, preserve rollback, and verify target-specific execution.

### M-OPS5 — continuous health

Each run must expose success/failed/stale/insufficient state, input coverage, cutoff, artifact location, zone counts, continuity errors, and method/schema version. Failure must not trigger delivery or execution actions.

## 6. M5 and M6 boundary

M5 is periodic, not a gate for autonomous operation. M6 remains the route for adopting one bounded improvement candidate and requires explicit approval.

If an M-OPS task needs to change accepted level semantics, thresholds, proposal gates, or policy behavior, stop and create a separate evidence-backed proposal.

## 7. Human involvement boundary

No recurring human involvement is required for public OHLCV collection, snapshot generation, reliability calculation, chronological history, local chart-first artifacts, or health status.

Explicit human approval remains required for installed runtime/schedule changes, live delivery changes, production policy changes, candidate adoption, automatic execution, and phase/version promotion.

## 8. Completion criteria

The autonomous M plan is complete when:

1. dedicated daily snapshot source is accepted;
2. deterministic chronological level/history source is accepted;
3. chart-first operator artifact is accepted;
4. stale/discontinuous/insufficient states fail closed or remain prominently visible;
5. one explicitly approved installed report-only cadence is verified;
6. autonomous health/status is available;
7. current state and operator documentation agree;
8. no delivery, policy, or order behavior is introduced without separate approval.

## 9. Immediate next task

M-OPS3:

`chatgpt/specs/active/20260721_macro_structure_chart_first_operator_artifact.md`

Do not rerun M5 or reopen M-OPS1/M-OPS2 while this task is active unless a concrete contradiction appears.

## 10. Canonical references

- research basis: `MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- accepted M1 spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- accepted M2 spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- accepted M4 spec: `chatgpt/specs/archive/20260721_macro_operator_hierarchy_render_shadow.md`
- accepted M-OPS1 spec: `chatgpt/specs/archive/20260721_macro_autonomous_structure_daily_operation.md`
- accepted M-OPS2 spec: `chatgpt/specs/archive/20260721_macro_structure_chronological_history_continuity.md`
- secondary improvement route: `M5_M6_EXECUTION_PLAN_20260721.md`
- current macro route: `MACRO_IMPLEMENTATION_ROUTE.md`
- current state and task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`
