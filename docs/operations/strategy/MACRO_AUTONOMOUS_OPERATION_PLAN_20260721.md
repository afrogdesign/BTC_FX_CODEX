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
→ M-OPS3 chart-first operator artifact — accepted at 09330b9
→ M-OPS4 separate runtime/schedule enablement — accepted at `a9b3d46` / runtime `690c014`
→ M-OPS5 continuous health and stale-data monitoring — next, not started
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

M5/M6 must not replace or bypass the M-OPS runtime approval boundary.

## 3. Accepted foundation and operation state

Accepted research/tooling:

- M1: deterministic event-time levels, lifecycle, prior-only reliability, structural location, volatility, activation, target/obstruction, outcomes, missed-move diagnostics
- M2: opt-in public-data auxiliary macro shadow
- M3: tactical and next-regime separation
- M4: chart-first local render shadow at `ea89e61`
- M5: deterministic bounded champion/challenger proposal engine

### Accepted M-OPS1

Checkpoint: `89bd338`.

Provides:

- `run-macro-structure-daily`;
- public 15m/1h/4h inputs only;
- actual common closed-candle cutoff;
- normalized observable evaluation time;
- stable M1 level identity and prior-only evidence;
- original side and current role separation;
- structure/location, reliable zones, targets, obstruction, volatility, activation, freshness, continuity, and valid `insufficient`;
- complete immutable run artifacts and atomic latest summary;
- deterministic run identity and byte-conflict-safe publication.

### Accepted M-OPS2

Checkpoint: `dea0e33`.

Provides:

- `run-macro-structure-history`;
- complete direct-child source validation;
- every evaluation plus deduplicated structural checkpoints;
- canonical structural source and latest freshness reevaluation separation;
- stable level identity, reliability, role, lifecycle, geometry, evidence, absence, reappearance, and latest-absence history;
- strict timestamp, version, symbol, public/report-only, and level-ID validation;
- deterministic v2 immutable history artifacts and atomic latest summary;
- legacy v1 artifact preservation;
- identifiable level transition events.

### Accepted M-OPS3

Checkpoint: `09330b9`.

Provides:

- `render-macro-structure-operator`;
- exact latest M-OPS1 snapshot and latest M-OPS2 v2 history selection;
- selected snapshot must be the latest reevaluation of the final structural checkpoint;
- explicit public 15-minute OHLCV input;
- no-future closed-candle validation and current-price agreement;
- deterministic self-contained v2 HTML/SVG, JSON, Markdown, manifest, and atomic latest summary;
- 96-candle chart window;
- all accepted high/medium zones, including non-nearest zones, by stable level ID and role;
- no low/insufficient zone promotion;
- complete accepted zone evidence without semantic recalculation;
- categorized structure, reliability, role, lifecycle, geometry, absence, reappearance, and stale/discontinuous history;
- truthful display-level source traces;
- visible status, data quality, limitations, and report-only safety boundary;
- no tactical Entry/SL/TP, live fetch, production UI, delivery, runtime, policy, or execution mutation.

Reviewed evidence:

- `local/reports/macro_structure/mops3_review/`
- accepted latest artifact: `operator_3f09d915f61d0183d51c`

Known remaining gaps:

- accepted commands are not yet enabled in an installed recurring runtime;
- autonomous health/status is not yet implemented as M-OPS5.

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

History supports every evaluation, unique structural checkpoints, stable level continuity, evidence changes, absence/reappearance, structure/location/target/obstruction changes, stale/continuity history, and deterministic later evaluation.

Do not infer permanent retirement from absence. Do not create mutable online learning.

### 4.4 Operator artifact

The accepted primary operator surface is chart-first and shows:

1. status and safety banner;
2. current price and 15-minute chart;
3. high/medium reliable macro zones;
4. current structural location;
5. targets and obstruction;
6. volatility, activation, freshness, continuity, and data quality;
7. recent chronological changes;
8. evidence details and limitations.

M-OPS3 is macro-only. Tactical Entry / SL / TP overlays are not included and must not be implied.

## 5. Implementation phases

### M-OPS1 — accepted

Accepted at `89bd338`. Do not reopen without a concrete source or contract defect.

### M-OPS2 — accepted

Accepted at `dea0e33`. Do not reopen without a concrete source or artifact contradiction.

### M-OPS3 — accepted

Accepted at `09330b9`.

Archived spec:

`chatgpt/specs/archive/20260721_macro_structure_chart_first_operator_artifact.md`

### M-OPS4 — accepted

M-OPS4 was completed as a separate bounded `RUNTIME_TASK` for `com.afrog.btc-macro-structure` only. The implementation is `690c014` and the optional-reference source fix is `a9b3d46`.

The installed target uses the primary repo and the six JST entries `01:10`, `05:10`, `09:10`, `13:10`, `17:10`, and `21:10`. The run was report-only with no private input and no automatic order.

After approval, the task may only:

- inspect the actual installed target and existing schedule;
- verify target repo/path before change;
- connect accepted M-OPS1 → M-OPS2 → M-OPS3 commands in one report-only cadence;
- preserve rollback and unrelated runtime configuration;
- verify target-specific command execution and local artifacts;
- keep mail, notification, private/account/order access, policy, and automatic orders unchanged.

The active runtime spec is archived after acceptance. M-OPS5 remains a separate, not-started source task.


### M-OPS5 — continuous health

After M-OPS4 acceptance, define a separate source task for success/failed/stale/insufficient state, input coverage, cutoff, artifact location, zone counts, continuity errors, and method/schema version.

Failure must not trigger delivery or execution actions.

## 6. M5 and M6 boundary

M5 is periodic, not a gate for accepted M-OPS source/artifacts. M6 remains the route for adopting one bounded improvement candidate and requires explicit approval.

If an M-OPS task needs to change accepted level semantics, thresholds, proposal gates, or policy behavior, stop and create a separate evidence-backed proposal.

## 7. Human involvement boundary

No recurring human involvement is required for public OHLCV collection, snapshot generation, reliability calculation, chronological history, local chart-first artifacts, or health status after setup.

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

Criteria 1–4 are accepted. Criteria 5–6 remain.

## 9. Immediate next transition

M-OPS4 is accepted for the target-only report-only service. Await a separate M-OPS5 source task; no production delivery or execution is implied.

Do not rerun M5 or reopen M-OPS1–M-OPS3 while waiting unless a concrete contradiction appears.

## 10. Canonical references

- research basis: `MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- accepted M1 spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- accepted M2 spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- accepted M4 spec: `chatgpt/specs/archive/20260721_macro_operator_hierarchy_render_shadow.md`
- accepted M-OPS1 spec: `chatgpt/specs/archive/20260721_macro_autonomous_structure_daily_operation.md`
- accepted M-OPS2 spec: `chatgpt/specs/archive/20260721_macro_structure_chronological_history_continuity.md`
- accepted M-OPS3 spec: `chatgpt/specs/archive/20260721_macro_structure_chart_first_operator_artifact.md`
- secondary improvement route: `M5_M6_EXECUTION_PLAN_20260721.md`
- current macro route: `MACRO_IMPLEMENTATION_ROUTE.md`
- current state and task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`
