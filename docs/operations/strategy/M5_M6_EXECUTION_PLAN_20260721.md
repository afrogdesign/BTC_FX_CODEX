# M5 / M6 Execution Plan

created_at: 2026-07-21
status: canonical implementation plan; M5 refresh planned; M6 conditional and unauthorized
primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Decision

M5 is not an unimplemented phase. The deterministic offline champion/challenger proposal engine is accepted at checkpoint locator `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`.

The next M-route work is therefore:

```text
accumulate gate-relevant evidence
→ run one bounded M5 evidence refresh
→ select zero or one proposal-eligible challenger
→ create one human-reviewed M6 proposal
→ implement source-only shadow
→ validate
→ obtain explicit human adoption approval
→ apply runtime separately
```

Do not rewrite M5 merely because its accepted result had no winner. `winner=none` and `continue_shadow_collection` are valid fail-closed outcomes.

M6 remains unauthorized until the documented entry gate is satisfied and the user explicitly approves one candidate.

## 2. Accepted baseline

Accepted M5 result:

- champion count: `1`
- challenger count: `4`
- chronological snapshot dates: `6`
- structurally valid challengers: `4`
- comparison-eligible challengers: `0`
- Pareto-dominant challengers: `0`
- proposal-eligible challengers: `0`
- winner: `none`
- recommendation: `continue_shadow_collection`
- primary gate horizon: `3h`
- diagnostic-only horizons: `6h`, `12h`, `24h`
- P8 eligible actual-backed count: `0`
- production mutation: none

The accepted engine, CLI route, output schema, champion identity, proposal-space manifest contract, rolling comparison semantics, and fail-closed gates are frozen unless a material defect is demonstrated.

## 3. M5 continuation plan

### M5-E0 — Preserve the accepted engine

No source task is opened by default.

Reopen M5 source only when one of these is demonstrated:

- deterministic output or identity defect
- accepted CLI route failure
- future-data leakage
- comparison denominator mismatch
- gate result inconsistent with the accepted contract
- output privacy or atomicity defect

A weak or empty challenger result is not itself an engine defect.

### M5-E1 — Accumulate evidence without daily heavy replay

Use existing accepted public-market-data and generated local evidence paths. Do not run the 31-unit M5 bundle every day.

A bounded M5 refresh becomes eligible when at least one operational trigger is true:

1. at least seven new eligible JST dates exist after the accepted 2026-07-21 cutoff;
2. the P-route actual episode/link pair becomes available and changes `p8_actual_status`;
3. an accepted M1 or M3 source change materially changes the comparison basis;
4. the user explicitly requests an earlier bounded refresh.

The seven-date rule is a replay-cost scheduling rule, not a proposal-eligibility threshold. Candidate eligibility continues to use the engine's accepted gates.

Do not modify launchd, runtime schedules, notification, mail, or production behavior merely to satisfy this collection step.

### M5-E2 — One bounded evidence refresh

Create one active spec before execution.

Default refresh scope:

- primary repo only
- accepted champion manifest unchanged
- accepted proposal-space unchanged: champion plus four declared challengers
- fresh explicit M1 and M3 inputs
- optional P8 trial report and trial facts only when the accepted actual episode/link route has produced them
- exactly one `run-macro-p9-proposal-engine` execution
- exactly four fresh outputs in a new local artifact directory
- no output or raw input commit
- no second full replay unless ChatGPT explicitly approves it after identifying a changed failure cause

Required outputs:

- `macro_p9_challenger_results.csv`
- `macro_p9_issue_diagnosis.csv`
- `macro_p9_proposal_engine.json`
- `macro_p9_proposal_engine.md`

If no source changes are needed, this is an operations/artifact task and should not create a source commit. If a material engine defect is found, stop and create a separate bounded FIX spec.

### M5-E3 — ChatGPT acceptance review

Review only the evidence needed for the decision:

- input fingerprints and chronological cutoff dates
- champion exactly once
- challenger count and deterministic IDs
- same-opportunity and same-date comparison basis
- 3H primary gate and diagnostic-only longer horizons
- Long/Short representation
- validation concentration and data-quality gates
- guarded metric non-degradation
- P8 actual status and any explicit contradiction
- winner, recommendation, and reason codes
- no private path, raw opportunity identity, runtime, or production mutation

Decision outcomes:

| Result | Action |
|---|---|
| no eligible challenger | record `continue_shadow_collection`; park M5 until the next trigger |
| material M5 defect | one bounded FIX task; do not start M6 |
| exactly one eligible challenger | create an M6 proposal package; M6 still requires human approval |
| multiple eligible challengers | do not combine them; ChatGPT selects one or asks for human choice |

## 4. M6 implementation plan

### M6-P1 — One-candidate proposal package

Create one active proposal spec containing:

- exact M5 candidate ID and deterministic parameters
- accepted champion identity
- affected observable behavior
- why the change helps the manual 15-minute operator
- validation and calibration metrics
- Long/Short, regime, structure/location, false-warning, missed-move, whipsaw, and burden splits
- P8 actual evidence status and any conflict
- unchanged safety boundaries
- rollback condition
- allowed files
- validation budget

The proposal must be limited to one bounded UI or policy change. It must not combine UI, threshold, gate, scoring, notification, mail, and runtime changes.

The user must explicitly approve the proposal before M6 source implementation begins.

### M6-S1 — Source-only shadow implementation

Implement the approved candidate in one bounded Codex task.

Default boundaries:

- disabled by default or reachable only through an explicit shadow route
- no production config adoption
- no live notification or mail change
- no launchd or runtime change
- no automatic order
- no private/account/order endpoint
- no broad gate, threshold, classifier, or scoring redesign
- no frozen runtime repo access

Implementation form depends on the approved proposal:

- UI proposal: render-only comparison with explicit champion/challenger labels
- policy proposal: offline/shadow candidate output alongside the accepted champion

Required implementation evidence:

- matching unit tests
- one small deterministic fixture or smoke
- task-scoped `git diff --check`
- one local commit
- compact report

### M6-V1 — Bounded validation

After source review, run one bounded validation task.

Validation must use:

- the same eligible opportunities and date denominators
- event-time construction only
- 3H primary selection horizon
- Long/Short and relevant regime/location splits
- false-warning, missed-move, opposite-move, whipsaw, and burden checks
- actual-backed contradiction check when actual evidence exists
- one fresh operator-facing shadow artifact when the proposal changes UI

Do not run a duplicate full replay or a second validation bundle without explicit ChatGPT approval.

### M6-A1 — Human adoption decision

ChatGPT presents:

- the candidate and champion difference
- expected operator-visible change
- evidence strengths and weaknesses
- unresolved risks
- rollback condition
- source-only validation result

Human choices:

- reject
- continue shadow collection
- approve runtime apply

No automatic adoption is permitted.

### M6-R1 — Separate runtime apply

Runtime apply is a separate explicit `RUNTIME_TASK` after source acceptance and human approval.

Rules:

- do not mix source edits and runtime apply
- target one approved runtime component only
- inspect the frozen runtime repo only when the task explicitly names it
- preserve backup and rollback capability
- verify the installed target and arguments
- perform one bounded post-apply verification
- do not infer production success from source tests alone

Notification, mail, schedule, gate, threshold, or scoring changes require their own explicit approval even when the source proposal is accepted.

### M6-C1 — Acceptance and version boundary

M6 is complete only when:

1. one proposal passed the M6 entry gate;
2. human approval was explicit;
3. source-only implementation and matching tests were accepted;
4. bounded validation passed without hidden material damage;
5. any runtime apply was separately approved and verified;
6. operator-facing docs and current state match the adopted behavior;
7. ChatGPT records acceptance.

Only then may `Ver05` be proposed. M5 acceptance alone and an M6 shadow implementation alone do not qualify.

## 5. Task packaging

| Task | Default owner | Commit | Heavy run |
|---|---|---:|---:|
| evidence trigger check | ChatGPT/MCP | no | no |
| bounded M5 refresh | Codex operations | normally no | one approved bundle |
| M5 review and candidate decision | ChatGPT/MCP | state docs only | no duplicate run |
| M6 proposal spec | ChatGPT/MCP | docs checkpoint when bundled | no |
| M6 source-only shadow | Codex | one local commit | small fixture only |
| M6 bounded validation | Codex | artifact normally uncommitted | one approved bundle |
| M6 runtime apply | Codex under explicit `RUNTIME_TASK` | source commit already accepted | target-only verification |
| final acceptance/state update | ChatGPT/MCP | bundled docs checkpoint | no |

## 6. Stop conditions

Stop and return to ChatGPT when:

- M5 still returns no eligible challenger
- actual evidence conflicts materially with the challenger
- comparison denominator or event-time integrity is uncertain
- a candidate damages either direction or a relevant regime materially
- proposal scope expands beyond one observable change
- runtime, notification, mail, gate, threshold, scoring, account, position, or order scope appears without approval
- the frozen runtime repo would be touched without an explicit `RUNTIME_TASK`

## 7. Relationship to the P route

The P route remains parked on the human-supplied private actual-trade export batch. M-route evidence work may continue using public market evidence, but M6 proposal eligibility still fails closed when the accepted engine requires P8 practical readiness and actual-backed evidence.

Do not substitute macro proxy evidence for missing actual trading evidence.

## 8. Canonical references

- current macro route: `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md`
- M5 accepted spec: `chatgpt/specs/archive/20260721_macro_p9_champion_challenger_proposal_engine.md`
- research basis: `docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- current accepted state: `docs/operations/ai-orchestration/CURRENT_STATE.md`
- exactly one current task: `docs/operations/ai-orchestration/NEXT_ACTION.md`
