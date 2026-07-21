# Macro Replay and AI Acceptance Simplification Plan

last_updated: 2026-07-21
status: approved design backlog; M5 accepted; A1 may proceed after docs checkpoint
scope: macro M1/M3/M5 offline replay cost and ChatGPT/Codex task execution

## Purpose

Reduce repeated replay, long prompts, duplicated AI review, and thread handoff overhead without weakening event-time correctness, fail-closed behavior, deterministic evidence, or human approval.

M5 is accepted as an offline/report-only proposal engine. Its outcome remains:

- winner: `none`
- recommendation: `continue_shadow_collection`
- no challenger adoption
- no production, runtime, notification, mail, gate, threshold, or order change

This plan does not reopen M5 and does not authorize M6.

## Diagnosis

The main complexity was not CWT itself. It came from three coupled problems:

1. M1 replay, M3 replay, comparison, diagnosis, and publication were treated as one validation unit.
2. Implementation debugging and heavy real-data acceptance ran in the same loop.
3. Natural-language prompts carried state, specification, validation, dirty-tree rules, and report schemas at once.

CWT or thread switching amplified handoff cost, but did not create the underlying evaluation workload.

The following requirements remain essential and must not be relaxed:

- cutoff/event-time isolation
- closed-candle isolation
- same-date champion comparison
- exact eligible and validation date bases
- higher-is-better and lower-is-better guarded metrics
- fail-closed missing/low-quality evidence
- deterministic outputs
- report-only and human-decided posture

## Operating model

### Implementation pass

Codex owns:

- bounded source/test implementation
- helper, fixture, cache, and execution-order design inside allowed files
- obvious in-scope bug fixes
- matching unit tests
- small deterministic fixture E2E
- task-scoped diff check
- local commit

A normal implementation pass does not run the full candidate/date bundle.

### ChatGPT review gate

ChatGPT owns:

- source, test, CLI, and artifact review through MCP
- product/trading/safety judgment
- validation sufficiency
- acceptance or minimal FIX decision
- explicit authorization for any later heavy run

The Codex report is a locator, not proof.

### Acceptance-only run

Only after implementation is review-ready:

- one exact bounded real-data command by default
- no source repair or redesign
- no unchanged retry after failure
- no second full replay unless replay-level determinism is an explicit acceptance requirement and publication-only verification is insufficient

M5 demonstrated this model successfully: implementation and focused fixture validation were reviewed first, followed by one 31-unit acceptance run.

## AI task-contract route

The concrete design for short prompts and machine-readable execution contracts is:

```text
AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md
```

Implement it separately in phases:

```text
A1 contract schemas, validator, renderer, tests
→ A2 one low-risk pilot
→ A3 canonical routing activation
→ A4 optional CWT integration
```

Do not combine A1 with replay-pipeline redesign.

## Replay architecture backlog

The long-term internal pipeline should permit these stages to be reused independently:

```text
1. prepare snapshot inputs
2. run M1 snapshot replay
3. run M3 snapshot replay
4. compare champion and challengers
5. diagnose candidate and report-global issues
6. publish CSV / JSON / Markdown outputs
```

The public CLI may remain one command. Internal boundaries should allow targeted reruns and publication-only determinism.

### Stage metadata

A reusable stage should record:

- schema and logic version
- input fingerprints
- parameter fingerprint
- cutoff timestamp
- eligible-date fingerprint
- validation-date fingerprint when relevant
- output row counts and fingerprints
- quality status and failure reason

Do not publish temporary absolute paths, raw IDs, or private rows.

## Cache contract

Caching is valid only when it preserves the accepted evaluation contract.

Suggested M1 key:

```text
signal snapshot fingerprint
+ 15m/1h/4h OHLCV fingerprints
+ cutoff
+ M1 parameters
+ M1 schema/logic version
```

Suggested M3 key:

```text
M1 output fingerprints
+ cutoff
+ M3 policy/config fingerprint
+ M3 schema/logic version
```

Rules:

- deterministic/content-addressed key
- metadata and fingerprint verification on hit
- mismatch fails closed to recomputation
- no cross-candidate or cross-cutoff reuse
- champion reuse across challengers only for exact same-date inputs
- local cache remains uncommitted unless a future spec defines safe fixtures

## Targeted rerun matrix

| Changed area | Minimum rerun |
|---|---|
| Markdown/render formatting | publication only |
| issue categorization | diagnosis and publication |
| Pareto/comparison logic | comparison onward |
| M3 replay/policy | M3 onward |
| M1 replay/parameters | M1 onward |
| snapshot/cutoff construction | all stages |

Earlier stages should not rerun when their fingerprints and contracts are unchanged.

## Determinism contracts

### Publication determinism

Given one immutable intermediate bundle, publishing the four outputs twice produces byte-identical files.

This should normally avoid repeating M1/M3 replay.

### Replay determinism

Given identical raw inputs and parameters, replay stages produce identical intermediate fingerprints and outputs.

This is heavier and requires explicit acceptance authorization.

Do not treat these contracts as equivalent by default.

## Lightweight fixture baseline

Before a real-data heavy run, a small deterministic fixture should cover the task-relevant subset of:

- at least two snapshot dates
- champion plus challenger
- future signal and OHLCV isolation
- same-date champion comparison
- champion cache call count
- higher/lower metric direction
- missing metric fail-closed
- candidate-specific issue lineage
- one report-global P8 row when P8 is insufficient
- champion/challenger count separation
- count/fingerprint publication instead of raw IDs
- exactly four outputs
- publication determinism
- no runtime, notification, mail, API, account, position, or order operation

The fixture is development evidence, not automatic replacement for all real-data acceptance.

## Validation budget

Normal implementation task:

- matching unit tests
- one small deterministic fixture/smoke
- task-scoped `git diff --check`

Heavy validation includes:

- more than 10 replay/evaluation units
- multiple candidates across multiple real dates
- a second complete replay
- a long-running background process

Heavy validation requires explicit ChatGPT authorization and stated work units.

Prohibited patterns:

- duplicate background runs
- unchanged heavy retry after failure
- alternating implementation debugging and full replay
- rerunning unrelated passing tests without related changes
- redundant compile and importing-test evidence

## Thread and state rules

Source of truth:

```text
repo implementation and artifacts
→ active spec
→ task manifest
→ CURRENT_STATE / NEXT_ACTION
→ stable workflow/control docs
→ validated report
→ chat history
```

- fresh threads read the canonical startup route
- same-task threads use delta-only inspection
- partial work is represented by working-tree diff plus compact report
- prompts do not repeat stable repo rules
- CWT/session IDs are transport details, not product state

## Dirty-tree and worktree direction

For sequential work, one working tree is acceptable if each task stages only owned files.

For concurrent ownership:

- ChatGPT orchestration docs and Codex source should use separate worktrees when overlap risk exists
- the task manifest becomes the ownership lease for allowed edit files
- unrelated dirty changes remain preserved

Worktree separation should reduce collisions, not become mandatory overhead for every small task.

## Migration route

### A1–A4: AI task contracts

Proceed using the task-manifest specification. This is the immediate post-M5 improvement route.

### R1: measure replay work

After A1–A3 are stable:

- count M1/M3 invocations
- record candidate/date work units
- locate exact repeated calculations
- measure stage elapsed time
- make no evaluation-contract change

### R2: intermediate contracts

Define snapshot/M1/M3 metadata and fingerprint schemas while preserving final outputs.

### R3: contract-preserving cache

Cache exact fingerprinted stage results and test invalidation/future isolation.

### R4: publication-only determinism

Publish twice from one immutable intermediate bundle without replay repetition.

### R5: optional stage CLI

Expose bounded internal stage commands only if operator/debug value is demonstrated.

Each replay phase requires its own active spec. Do not bundle R1–R5.

## Success criteria

The simplification succeeds when:

1. implementation tasks finish without real-data replay loops
2. ChatGPT rejects incomplete source before heavy execution
3. heavy acceptance normally runs once
4. prompts are rendered from manifests and remain short
5. reports are machine-validated
6. unchanged replay stages are safely reusable
7. publication changes do not require replay recomputation
8. future isolation and fail-closed evidence remain unchanged or stronger
9. no acceptance evidence is reduced

## Non-goals

This plan does not authorize:

- trading logic, gates, thresholds, scoring, or classifier changes
- candidate/date/evidence reduction
- challenger promotion
- runtime, notification, mail, API, account, position, or order changes
- automatic acceptance or production adoption
- M6
