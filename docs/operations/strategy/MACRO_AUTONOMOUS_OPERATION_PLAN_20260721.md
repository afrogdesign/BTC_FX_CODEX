# Macro Autonomous Structure Operation Plan

created_at: 2026-07-21
last_updated: 2026-07-21
status: canonical completion route
primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
safety: report-only / not `FORMAL_GO` / no automatic order / human decides trades and production adoption

## 1. Purpose

M計画の主目的は、公開市場データから人間の継続入力なしで大局構造を更新し、manual 15-minute trading判断に使える信頼度付きsupport/resistanceを提供することである。

完成状態:

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

Private trade exportはmarket-structure理解の前提ではない。Actual trade evidenceは、人間の取引成果やproduction採用を判断する別のevidenceである。

## 2. Plan hierarchy

### Primary lane — autonomous macro operation

```text
M1 accepted structure/reliability engine
→ M-OPS1 current snapshot and daily artifact — accepted at 89bd338
→ M-OPS2 chronological history and confidence continuity — current
→ M-OPS3 chart-first operator surface
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

M5/M6 must not block unfinished M-OPS work. A no-winner M5 result does not stop macro collection, reliability history, or local operator artifacts.

## 3. Accepted foundation and operation state

Accepted research/tooling:

- M1: deterministic event-time levels, lifecycle, prior-only reliability, structural location, volatility, activation, target/obstruction, outcomes, missed-move diagnostics
- M2: opt-in public-data auxiliary macro shadow
- M3: tactical and next-regime separation
- M4: chart-first local render shadow
- M5: deterministic bounded champion/challenger proposal engine

Accepted M-OPS1 source checkpoint: `89bd338`.

M-OPS1 provides:

- dedicated `run-macro-structure-daily` route;
- public 15m/1h/4h inputs only;
- actual common closed-candle cutoff;
- normalized observable evaluation time;
- stable M1 level identity and prior-only evidence;
- original side and current role separation;
- canonical structure/location, nearest zones, targets, obstruction, volatility, activation, freshness, and continuity;
- valid `insufficient` output;
- complete immutable run artifacts and atomic latest summary;
- deterministic run identity and byte-conflict-safe publication.

Known remaining gap:

- immutable M-OPS1 runs exist;
- no accepted chronological rollup yet exposes evaluation-versus-structural checkpoints, level continuity, reliability changes, role/lifecycle transitions, absence/reappearance, or snapshot-to-snapshot changes.

## 4. Product contract

### 4.1 Current macro snapshot

Every successful daily run produces one deterministic snapshot as of the latest eligible common closed candle.

It exposes:

- snapshot/evaluation times and input fingerprints
- structure and location
- current price
- nearest and additional reliable zones
- original side and current role
- prior-only reliability and lifecycle evidence
- targets and obstruction
- volatility and activation
- stale, discontinuous, and insufficient state
- safety boundary

The snapshot must not use future-confirmed geometry or later lifecycle outcomes.

### 4.2 Confidence language

Allowed labels:

- `high reliability`
- `medium reliability`
- `low reliability`
- `insufficient`

Nearest price alone is not reliability. Weak, stale, discontinuous, or one-sided evidence must not be promoted.

### 4.3 Chronological history

History must support:

- every evaluation run;
- unique structural checkpoints without freshness-only duplicate transitions;
- stable `level_id` continuity;
- reliability score and band changes;
- role and lifecycle changes;
- evidence-count changes;
- levels absent from and reappearing in later checkpoints;
- structure/location/target/obstruction changes;
- stale and continuity history;
- deterministic later chronological evaluation.

Do not infer permanent retirement from one absence. Do not create mutable online learning. Recompute an auditable deterministic rollup from immutable source artifacts.

### 4.4 Operator artifact

The primary operator surface must be chart-first and show, in order:

1. current price and chart
2. high/medium reliable zones
3. current structural location
4. first targets and obstruction
5. volatility and activation
6. recent history changes, evidence, and limitations

Macro zones must remain visually distinct from tactical Entry / SL / TP levels.

## 5. Implementation phases

### M-OPS1 — accepted

Accepted at `89bd338`. Do not reopen without a concrete source or contract defect.

### M-OPS2 — current

Implement `run-macro-structure-history` over complete immutable M-OPS1 runs.

Required:

- direct-child complete source-run validation;
- explicit symbol isolation;
- evaluation history and unique structural checkpoints;
- level continuity and transitions;
- absence/reappearance without invented retirement;
- snapshot changes;
- deterministic immutable history artifacts;
- atomic compact latest summary;
- bounded multi-date no-future fixture proof.

Active spec:

`chatgpt/specs/active/20260721_macro_structure_chronological_history_continuity.md`

### M-OPS3 — chart-first operator surface

After snapshot/history acceptance, connect the accepted latest snapshot and history summary to a chart-first local artifact. Keep delivery unchanged until a separate adoption decision.

### M-OPS4 — runtime and schedule enablement

A separate explicit `RUNTIME_TASK` only after source and artifact acceptance. Inspect the installed target, enable one report-only cadence, preserve rollback, and verify target-specific execution. Human approval is required once for installed execution changes.

### M-OPS5 — continuous health

Each run must expose success/failed/stale/insufficient state, input coverage, cutoff, artifact location, zone counts, continuity errors, and method/schema version. Failure must not trigger delivery or execution actions.

## 6. M5 and M6 boundary

M5 is periodic, not a gate for autonomous operation. M6 remains the route for adopting one bounded improvement candidate and requires explicit approval.

If an M-OPS task needs to change accepted level semantics, thresholds, proposal gates, or policy behavior, stop and create a separate evidence-backed proposal.

## 7. Human involvement boundary

No recurring human involvement is required for public OHLCV collection, snapshot generation, reliability calculation, local reports, chronological history, or health status.

Explicit human approval remains required for installed runtime/schedule changes, live delivery changes, production policy changes, candidate adoption, automatic execution, and phase/version promotion.

## 8. Completion criteria

The autonomous M plan is complete when:

1. dedicated daily snapshot source is accepted;
2. deterministic chronological level/history source is accepted;
3. chart-first operator artifact is accepted;
4. stale/discontinuous/insufficient states fail closed;
5. one explicitly approved installed report-only cadence is verified;
6. autonomous health/status is available;
7. current state and operator documentation agree;
8. no delivery, policy, or order behavior is introduced without separate approval.

## 9. Immediate next task

M-OPS2:

`chatgpt/specs/active/20260721_macro_structure_chronological_history_continuity.md`

Do not rerun M5 or reopen M-OPS1 while this task is active unless a concrete contradiction appears.

## 10. Canonical references

- research basis: `MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- accepted M1 spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- accepted M2 spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- accepted M4 spec: `chatgpt/specs/archive/20260721_macro_operator_hierarchy_render_shadow.md`
- accepted M-OPS1 spec: `chatgpt/specs/archive/20260721_macro_autonomous_structure_daily_operation.md`
- secondary improvement route: `M5_M6_EXECUTION_PLAN_20260721.md`
- current macro route: `MACRO_IMPLEMENTATION_ROUTE.md`
- current state and task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`
