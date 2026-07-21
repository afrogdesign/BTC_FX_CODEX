# btc_monitor Master Plan

last_updated: 2026-07-21
status: canonical overall plan

## 1. Product objective

`btc_monitor`の最上位目的は、notification mailを受け取った人間が15分足を確認し、manual trading判断を行うための支援システムを完成させることである。

Maintain:

- report-only
- not `FORMAL_GO`
- human-decided trades and production adoption
- no automatic order

## 2. Plan structure

```text
Product / P route
├─ P1–P9: manual-trading evidence and improvement loop
Macro / M route
├─ M1–M5: accepted research/evaluation foundations
├─ M-OPS1–M-OPS5: autonomous macro operation completion lane
└─ M5/M6: periodic improvement and adoption lane
AI / A route
└─ completed operations experiments
```

Priority:

1. increase observable operator value;
2. preserve safety and contract integrity;
3. avoid repeated review and heavy validation;
4. keep orchestration compact.

## 3. Product / P route

| Phase | Result | Status |
|---|---|---|
| P1–P7 | importer, linking, scenarios, classifier, replay, shadow | accepted |
| P8 | deterministic evidence pipeline and operating cycle | accepted / collecting |
| P9 | evidence-backed tuning proposal | blocked |

Current blocker:

```text
complete private MEXC export batch missing
→ no actual episode/link pair
→ actual-backed evidence = 0
→ P9 remains blocked
```

This is an accepted no-repeat boundary, not a source defect.

Do not repeat importer/linker/readiness review unless a reopening trigger in `CURRENT_STATE.md` or `DEC-20260721-012` is true.

## 4. Macro / M route

### 4.1 Controlling purpose

M計画の主目的は、公開市場データから大局構造と信頼度付きsupport/resistanceを人間の継続入力なしで更新し、15分足manual判断へ提供することである。

```text
public OHLCV
→ stable higher-timeframe levels
→ lifecycle and prior-only reliability
→ current structural location
→ support/resistance confidence bands
→ next target and obstruction
→ chronological history
→ chart-first operator artifact
```

Private actual-trade evidence is not required for this calculation. It remains relevant to human outcome and production-adoption evaluation.

### 4.2 Accepted foundation

| Phase | Result | Status |
|---|---|---|
| M1 | event-time macro structure and reliable levels | accepted |
| M2 | opt-in public-data auxiliary shadow | accepted |
| M3 | tactical / next-regime separation | accepted |
| M4 | chart-first local render shadow | accepted |
| M5 | bounded champion/challenger engine | accepted |
| M6 | approved improvement adoption | unauthorized |

Accepted M5 result:

- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

This no-winner result does not block autonomous macro operation.

### 4.3 Primary M-OPS completion lane

Canonical plan:

- `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Sequence and state:

```text
M-OPS1 current snapshot and daily local report — accepted at 89bd338
→ M-OPS2 chronological history and reliability continuity — accepted at dea0e33
→ M-OPS3 chart-first operator artifact — accepted at 09330b9
→ M-OPS4 separate runtime/schedule enablement — awaiting explicit human RUNTIME_TASK approval
→ M-OPS5 autonomous status and stale-data health — not started
```

There is no active source implementation spec.

M-OPS3 accepted command:

- `render-macro-structure-operator`

Accepted local review evidence:

- `local/reports/macro_structure/mops3_review/`
- latest v2 artifact: `operator_3f09d915f61d0183d51c`

M-OPS4 must not begin until the user explicitly authorizes inspection and change of the installed report-only runtime/schedule.

### 4.4 Secondary M5/M6 lane

Canonical plan:

- `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md`

Sequence:

```text
accumulated accepted evidence
→ periodic bounded M5 refresh
→ zero or one eligible challenger
→ one explicitly approved M6 proposal
→ source-only shadow
→ validation
→ separate runtime adoption
```

`DEC-20260721-013` controls this sequence only. `DEC-20260721-014` prevents it from blocking unfinished M-OPS work.

## 5. AI / A route

| Phase | Result | Status |
|---|---|---|
| A1 | manifest schema / validator / renderer | accepted |
| A2 | low-risk pilot | accepted |
| A3 | canonical manifest routing | superseded |
| A4 | optional CWT integration | not planned |

Compact prompts and compact reports remain normal. Strict manifest tooling is optional for heavy or machine-aligned tasks.

## 6. Current execution policy

Current order:

```text
P remains parked on private input
→ M-OPS1–M-OPS3 remain accepted and unchanged
→ wait for explicit M-OPS4 RUNTIME_TASK approval
→ inspect actual installed target only after approval
→ perform one bounded report-only runtime/schedule task
→ verify target-specific execution and rollback
→ then define M-OPS5 health/status source as a separate phase
```

Do not:

- route current M work to M5 refresh while runtime approval is pending;
- reopen accepted M1/M-OPS1/M-OPS2/M-OPS3 semantics without a demonstrated contradiction;
- read, edit, or run the frozen runtime repo without explicit `RUNTIME_TASK` approval;
- mix runtime/schedule work with mail, notification, production policy, or order behavior;
- start M6 without one eligible challenger and explicit approval;
- create new orchestration frameworks.

## 7. Human involvement boundary

No recurring human input is required after setup for:

- public OHLCV collection;
- macro snapshot calculation;
- level lifecycle/reliability updates;
- chronological history;
- local chart-first artifact generation;
- health and stale-data status.

Human approval is required for:

- installed runtime/schedule enablement;
- live mail/notification integration;
- production policy/gate/threshold/scoring/classifier changes;
- M6 adoption;
- automatic orders;
- phase/version promotion.

## 8. Standard read route

New context:

1. `AGENTS.md`
2. `START_HERE.md`
3. `MASTER_PLAN.md` for planning
4. `CURRENT_STATE.md` and `NEXT_ACTION.md`
5. target route only
6. active spec only when one is authorized and present

Do not broadly scan history or archived plans.

## 9. Completion definitions

P route completion requires adequate actual-backed evidence and an accepted human-reviewed proposal where applicable.

M route completion requires:

- dedicated public-data current snapshot operation;
- confidence-labelled support/resistance;
- chronological history and latest status;
- chart-first operator artifact;
- fail-closed stale/insufficient behavior;
- separately approved and verified report-only runtime cadence;
- autonomous health/status;
- current docs and operator behavior agreement.

M-OPS1–M-OPS3 satisfy the accepted source and local-artifact portion. M-OPS4 and M-OPS5 remain.

## 10. Safety and version boundary

- no automatic order;
- no private/account/order endpoints;
- no unapproved runtime, launchd, mail, notification, gate, threshold, scoring, or classifier change;
- generated/private data remains local and uncommitted;
- frozen runtime repo requires explicit `RUNTIME_TASK`.

M-OPS source and local evidence remain Ver04.x. `Ver05` requires explicitly approved production adoption, matching validation, runtime verification where applicable, and ChatGPT acceptance.
