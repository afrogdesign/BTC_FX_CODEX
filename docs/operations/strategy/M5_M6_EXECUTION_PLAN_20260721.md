# M5 / M6 Improvement and Adoption Plan

created_at: 2026-07-21
last_updated: 2026-07-21
status: canonical secondary lane; M5 accepted; M6 conditional and unauthorized
primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
safety: report-only / not `FORMAL_GO` / no automatic order / human decides adoption

## 1. Scope correction

This document controls periodic improvement proposals and production adoption only.

It does not control the primary autonomous macro-operation route.

Primary M completion follows:

- `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Controlling relationship:

```text
M-OPS current snapshot / history / operator artifact proceeds first
→ accumulated accepted evidence may later trigger M5 refresh
→ M6 handles one bounded improvement adoption only
```

Do not route unfinished M-OPS work to `WAIT_FOR_EVIDENCE` or stop normal macro operation because M5 selected no winner.

## 2. Accepted M5 baseline

M5 is implemented and accepted at checkpoint locator:

`3c7f01d90c3f5cc126cedd9aed294cf67a602c42`

Accepted result:

- champion count: 1
- challenger count: 4
- chronological snapshot dates: 6
- structurally valid challengers: 4
- comparison-eligible challengers: 0
- proposal-eligible challengers: 0
- winner: `none`
- recommendation: `continue_shadow_collection`
- primary horizon: 3H
- diagnostic horizons: 6H / 12H / 24H
- production mutation: none

A no-winner result is valid fail-closed evidence. It is not an engine defect and does not block M-OPS.

## 3. M5 refresh trigger

Do not run the heavy proposal bundle daily.

One bounded refresh becomes eligible when at least one is true:

1. at least seven new eligible JST dates exist after the accepted cutoff;
2. accepted M-OPS history materially expands the validation basis;
3. P8 actual episode/link evidence becomes available;
4. an accepted M1/M3 source change changes the comparison basis;
5. the user explicitly requests an earlier bounded refresh.

The seven-date rule is a replay-cost trigger, not an eligibility threshold.

## 4. M5 refresh execution

Create one active refresh spec before execution.

Default scope:

- accepted champion unchanged;
- accepted four-challenger proposal space unchanged;
- fresh explicit M1/M3/M-OPS-compatible inputs;
- P8 evidence only when accepted and available;
- exactly one proposal-engine execution;
- exactly four fresh outputs;
- no generated artifact or raw input commit;
- no second complete replay without explicit ChatGPT approval and a changed failure cause.

Required outputs remain:

- `macro_p9_challenger_results.csv`
- `macro_p9_issue_diagnosis.csv`
- `macro_p9_proposal_engine.json`
- `macro_p9_proposal_engine.md`

If a material engine defect appears, stop and create one bounded FIX spec. Do not repair source during a heavy evidence run.

## 5. M5 decision

| Result | Action |
|---|---|
| no eligible challenger | record `continue_shadow_collection`; continue M-OPS normally |
| material M5 defect | one bounded FIX; M6 remains blocked |
| exactly one eligible challenger | create one M6 proposal package |
| multiple eligible challengers | do not combine; ChatGPT/human selects one |

M5 never applies a candidate automatically.

## 6. M6 entry gate

M6 may begin only when all are true:

1. one proposal-eligible candidate exists;
2. comparison and validation windows are adequate;
3. Long/Short, regime, false-warning, missed-move, opposite-move, whipsaw, and burden checks show no hidden material damage;
4. actual-backed evidence conflict is absent or explicitly disclosed;
5. scope is one bounded UI or policy change;
6. the user explicitly approves that proposal.

M6 is not required to operationalize already accepted M1–M4 behavior through M-OPS.

## 7. M6 task sequence

### M6-P1 — Proposal package

Record:

- exact candidate ID and parameters;
- champion identity;
- observable operator change;
- evidence strengths and weaknesses;
- directional/regime splits;
- actual evidence status;
- unchanged safety boundaries;
- rollback condition;
- allowed files and validation budget.

Request explicit user approval before source implementation.

### M6-S1 — Source-only shadow

Implement one disabled-by-default or explicit shadow route.

No production config, live notification, mail, schedule, runtime, order, or broad scoring/gate redesign.

Required evidence:

- matching tests;
- one small deterministic fixture;
- scoped `git diff --check`;
- one local commit;
- compact report.

### M6-V1 — Bounded validation

Use the same eligible opportunities and date denominators, event-time construction, 3H primary selection horizon, directional/regime splits, and guarded damage checks.

No duplicate full replay without explicit approval.

### M6-A1 — Human adoption decision

Allowed decisions:

- reject;
- continue shadow collection;
- approve one runtime apply.

No automatic adoption.

### M6-R1 — Separate runtime apply

A separate explicit `RUNTIME_TASK` is required.

Do not mix source changes and runtime apply. Target one approved component, preserve rollback, verify installed arguments/target, and run one bounded post-apply check.

## 8. Relationship to autonomous operation

M-OPS uses accepted M1/M4 semantics to provide current public-data macro value.

M5/M6 may improve those semantics later, but cannot delay:

- current snapshot generation;
- reliable-level history;
- chart-first local artifacts;
- stale/insufficient health reporting;
- separately approved report-only scheduling.

If M-OPS exposes a real accepted-logic defect, handle it as a bounded defect task. Do not disguise a policy redesign as operations work.

## 9. Human involvement boundary

No recurring human involvement is needed for M-OPS market-data calculation.

Human approval is required for:

- M6 proposal adoption;
- installed runtime/schedule changes;
- live delivery changes;
- production gate, threshold, scoring, classifier, or policy changes;
- automatic execution/order behavior;
- version promotion.

## 10. Version boundary

M5 acceptance, M5 refresh, and M6 source-only shadow do not by themselves qualify for `Ver05`.

`Ver05` may be proposed only after one explicitly approved adoption is implemented, validated, applied where relevant, verified, and accepted by ChatGPT.

## 11. Canonical references

- primary autonomous route: `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- current macro route: `MACRO_IMPLEMENTATION_ROUTE.md`
- accepted M5 spec: `chatgpt/specs/archive/20260721_macro_p9_champion_challenger_proposal_engine.md`
- current state/task: `docs/operations/ai-orchestration/CURRENT_STATE.md` and `NEXT_ACTION.md`
- durable decisions: `DEC-20260721-013` and `DEC-20260721-014`
