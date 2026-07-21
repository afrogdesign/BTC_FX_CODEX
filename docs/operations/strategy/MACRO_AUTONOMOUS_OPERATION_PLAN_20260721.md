# Macro Autonomous Structure Operation Plan

created_at: 2026-07-21
status: canonical completion route
primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
safety: report-only / not `FORMAL_GO` / no automatic order / human decides trades and production adoption

## 1. Purpose

M計画の主目的は、公開市場データから人間の継続入力なしで大局構造を更新し、manual 15-minute trading判断に使える信頼度付きsupport/resistanceを提供することである。

完成状態では、systemが自動的に次を行う。

```text
public 15m / 1h / 4h OHLCV
→ stable higher-timeframe level identity
→ touch / rejection / break / acceptance / reclaim lifecycle
→ prior-only reliability history
→ current structural location
→ reliable support / resistance candidates
→ next reliable target and obstruction
→ chart-first operator artifact
→ chronological evidence accumulation
```

人間のprivate trade exportは、このmarket-structure理解の前提ではない。

Actual trade evidenceは、予測が人間の取引成果に寄与したか、または改善候補をproductionへ採用してよいかを判断する別のevidenceである。

## 2. Corrected plan hierarchy

M route has two lanes.

### Primary lane — autonomous macro operation

```text
M1 accepted structure/reliability engine
→ M-OPS1 current snapshot and daily artifact
→ M-OPS2 chronological history and confidence calibration
→ M-OPS3 chart-first operator surface
→ M-OPS4 separate runtime/schedule enablement
→ M-OPS5 continuous health and stale-data monitoring
```

This lane provides the actual product value: an automatically maintained, evidence-backed macro map.

### Secondary lane — bounded improvement and adoption

```text
accumulated M evidence
→ periodic M5 champion/challenger refresh
→ optional one-candidate M6 proposal
→ explicit human approval
→ source-only shadow
→ validation
→ separate runtime adoption
```

M5/M6 must not block M-OPS1–M-OPS3. A no-winner M5 result does not mean macro collection or reliable-level reporting should stop.

## 3. Accepted foundation

Already accepted:

- M1: deterministic event-time 1H/4H levels, lifecycle, prior-only reliability, structural location, volatility state, activation, target/obstruction, outcomes, missed-move diagnostics
- M2: opt-in P8 auxiliary macro shadow using public market data
- M3: tactical bias and next-regime risk separation
- M4: chart-first local render shadow
- M5: deterministic bounded champion/challenger proposal engine

Accepted implementation locators remain historical locators and are not reopened merely to operationalize the accepted capability.

Known gap:

- accepted analysis exists;
- a normal autonomous macro operation route is not yet accepted or enabled;
- current routing incorrectly made M5 refresh the selected next action;
- M2 is opt-in and disabled by default;
- M4 is local render-only and not connected to a maintained latest macro snapshot.

## 4. Product contract

### 4.1 Current macro snapshot

Every successful run must produce one deterministic current snapshot as of the latest eligible closed candle.

Minimum fields:

- `snapshot_id`
- `as_of_utc` and `as_of_jst`
- input coverage and fingerprints
- structure state
- current price and structural location
- nearest reliable support zone
- nearest reliable resistance zone
- additional high/medium-reliability support and resistance zones
- current role for each zone
- reliability score and band
- touch, rejection, break, acceptance, and reclaim counts available at the cutoff
- last confirmation time
- distance from current price in percent and ATR
- next upside and downside reliable target
- intervening obstruction
- volatility state
- expansion risk separated from directional activation
- data-quality and stale-data status
- reason codes
- safety boundary

The snapshot must not use future-confirmed level geometry or later lifecycle outcomes.

### 4.2 Confidence language

The system must not claim certainty.

Allowed operator labels:

- `high reliability`
- `medium reliability`
- `low reliability`
- `insufficient`

A line becomes high reliability only through the accepted prior-only reliability evidence. Nearest price alone is insufficient.

When evidence is weak, discontinuous, stale, or one-sided, publish `insufficient` instead of inventing a line.

### 4.3 Operator artifact

The primary artifact must be chart-first and understandable without reading raw replay files.

Required information order:

1. current price and chart
2. high/medium reliable support and resistance zones
3. current structural location
4. first reliable upside/downside targets and obstruction
5. volatility and activation status
6. evidence breakdown and limitations

The artifact must visually distinguish macro zones from tactical Entry / SL / TP levels when tactical context is present.

### 4.4 History

Each run writes a date/time-scoped immutable generated artifact set and updates a small deterministic latest pointer or latest summary atomically.

History must support:

- level identity continuity
- reliability change over time
- role changes
- stale or retired levels
- false-break and reclaim history
- snapshot-to-snapshot stability
- later chronological evaluation

Generated outputs remain under `local/` and uncommitted.

## 5. Implementation phases

### M-OPS1 — Dedicated autonomous daily operation source

Create one source-only, report-only route that can run without private trade inputs and without M5.

Required behavior:

- use only accepted public market-data paths;
- obtain explicit 15m, 1h, and 4h OHLCV;
- calculate one current macro snapshot from the accepted M1 logic or accepted pure helpers;
- avoid duplicating level/reliability semantics;
- publish a deterministic JSON summary and human-readable Markdown;
- publish a chart-first HTML only if it can reuse the accepted M4 model safely within the same bounded implementation;
- write under a dedicated `local/reports/macro_structure/` root;
- expose compact stdout and status without raw rows or private paths;
- fail closed without affecting P8, mail, notification, or runtime.

M-OPS1 does not edit launchd, the frozen runtime repo, mail, notification selection, production gates, or automatic orders.

### M-OPS2 — Chronological reliability operation

After M-OPS1 source acceptance:

- retain date-scoped artifacts;
- maintain an atomic latest summary;
- record continuity and staleness;
- verify stable level identity across sequential snapshots;
- expose reliability upgrades/downgrades and role changes;
- add a bounded multi-date fixture or replay proving no future leakage and deterministic history behavior.

Do not introduce a mutable online-learning model. Recompute from explicit event-time data or use an auditable deterministic rollup.

### M-OPS3 — Operator-facing chart-first surface

After snapshot/history acceptance:

- connect the latest accepted snapshot to a chart-first local operator artifact;
- reuse M4 hierarchy principles;
- show reliable zones, current location, target and obstruction;
- label confidence as evidence confidence, not execution permission;
- retain `insufficient` and stale states visibly;
- keep live mail/notification unchanged until a separate adoption decision.

### M-OPS4 — Runtime and schedule enablement

This is a separate explicit `RUNTIME_TASK`.

Only after source and bounded artifact acceptance:

- inspect the actual installed invocation and target;
- enable one report-only macro operation cadence;
- do not mix source edits with runtime application;
- preserve rollback capability;
- verify one scheduled or equivalent target-specific execution;
- do not alter mail, notification, thresholds, gates, scoring, or orders.

Human approval is required once for this runtime activation because it changes installed execution. Repeated human input is not required after successful activation.

### M-OPS5 — Continuous operation and health

After runtime acceptance, normal operation is autonomous.

Each run must expose:

- success / failed / stale / insufficient status
- input coverage
- snapshot cutoff
- artifact location
- number of reliable support/resistance zones by band
- latest high/medium zones
- continuity errors
- method/schema version

Failure must not trigger retries, mail changes, order actions, or fallback private endpoints.

## 6. M5 and M6 after realignment

M5 remains accepted and is used periodically, not as the gate for autonomous macro operation.

Run one bounded M5 refresh only when its evidence trigger is met. Its input should include accumulated accepted M-OPS evidence when compatible with the frozen M5 contract.

M6 remains the route for adopting one bounded improvement candidate. M6 is not required to start M-OPS1–M-OPS3 because those phases operationalize already accepted M1–M4 capabilities rather than adopting a new challenger.

If M-OPS implementation requires changing accepted level semantics, thresholds, proposal gates, or policy behavior, stop and create a separate evidence-backed proposal instead of hiding the change as operations work.

## 7. Human involvement boundary

No recurring human involvement is required for:

- public OHLCV collection through accepted paths
- current structure snapshot generation
- support/resistance reliability calculation
- local report generation
- chronological evidence accumulation
- health/status publication

Explicit human approval remains required for:

- installed runtime or schedule changes
- live mail/notification integration
- production policy, gate, threshold, classifier, or scoring changes
- M6 candidate adoption
- automatic execution or order behavior
- phase/version promotion

## 8. Completion criteria

The autonomous M plan is not complete merely because M1–M5 source exists.

It is complete when all are true:

1. a dedicated report-only daily macro route exists;
2. it uses public data and does not require private trade history;
3. it emits a deterministic current macro snapshot;
4. it clearly reports high/medium/low/insufficient reliability;
5. support/resistance identity and lifecycle remain event-time safe;
6. date-scoped history and latest status are maintained atomically;
7. a chart-first operator artifact exposes the current reliable zones;
8. stale, discontinuous, and insufficient states fail closed;
9. one bounded source validation and one target-specific runtime validation pass;
10. the installed report-only cadence is explicitly approved and verified;
11. no automatic order, mail mutation, gate change, or production tuning is introduced;
12. `CURRENT_STATE.md`, `NEXT_ACTION.md`, and operator documentation agree with the active behavior.

## 9. Immediate next task

The immediate task is M-OPS1 under:

`chatgpt/specs/active/20260721_macro_autonomous_structure_daily_operation.md`

Do not wait for M5 refresh evidence before implementing M-OPS1.

## 10. Canonical references

- research basis: `MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- accepted M1 spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- accepted M2 spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- accepted M4 spec: `chatgpt/specs/archive/20260721_macro_operator_hierarchy_render_shadow.md`
- secondary improvement route: `M5_M6_EXECUTION_PLAN_20260721.md`
- current macro route: `MACRO_IMPLEMENTATION_ROUTE.md`
- current state and task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`
