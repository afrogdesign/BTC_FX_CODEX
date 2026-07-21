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

This is an accepted no-repeat boundary, not a source defect. Do not repeat importer/linker/readiness review unless a reopening trigger in `CURRENT_STATE.md` or `DEC-20260721-012` is true.

## 4. Macro / M route

### 4.1 Controlling purpose

M計画の主目的は、公開市場データから大局構造と信頼度付きsupport/resistanceを人間の継続入力なしで更新し、15分足manual判断へ提供することである。

```text
public OHLCV
→ stable higher-timeframe levels
→ lifecycle and prior-only reliability
→ current structural location
→ confidence-labelled zones
→ next target and obstruction
→ chronological history
→ chart-first operator artifact
```

Private actual-trade evidence is not required for this market-structure calculation.

### 4.2 Accepted foundation

| Phase | Result | Status |
|---|---|---|
| M1 | event-time macro structure and reliable levels | accepted |
| M2 | opt-in public-data auxiliary shadow | accepted |
| M3 | tactical / next-regime separation | accepted |
| M4 | chart-first local render shadow | accepted |
| M5 | bounded champion/challenger engine | accepted |
| M6 | approved improvement adoption | unauthorized |

Accepted M5 result remains `winner=none` and `continue_shadow_collection`. It does not block autonomous macro operation.

### 4.3 Primary completion lane: M-OPS

Canonical plan:

- `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Sequence and status:

```text
M-OPS1 current snapshot and daily local report — accepted at 89bd338
→ M-OPS2 chronological history and confidence continuity — current
→ M-OPS3 chart-first operator artifact
→ M-OPS4 separate runtime/schedule enablement
→ M-OPS5 autonomous status and stale-data health
```

Current active implementation:

- `chatgpt/specs/active/20260721_macro_structure_chronological_history_continuity.md`

M-OPS2 must proceed without waiting for M5 refresh or private trade data. M-OPS1 must not be reopened without a concrete defect.

### 4.4 Secondary improvement lane: M5/M6

Canonical plan:

- `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md`

```text
accumulated accepted evidence
→ periodic bounded M5 refresh
→ zero or one eligible challenger
→ one explicitly approved M6 proposal
→ source-only shadow
→ validation
→ separate runtime adoption
```

`DEC-20260721-013` controls this improvement sequence. `DEC-20260721-014` prevents it from blocking unfinished M-OPS work.

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
→ implement M-OPS2 history source
→ focused tests and bounded multi-date fixture
→ ChatGPT MCP review
→ accept or one bounded material FIX
→ continue to M-OPS3
```

Do not:

- route current M work to `WAIT_FOR_EVIDENCE`;
- rerun M5 as part of M-OPS2;
- require private trades for macro history;
- rewrite accepted M1 or M-OPS1 semantics without a demonstrated defect;
- mix source edits with runtime/schedule application;
- start M6 without an eligible challenger and explicit approval;
- change delivery, gates, thresholds, scoring, classifiers, or execution behavior under M-OPS source tasks;
- create new orchestration frameworks.

## 7. Human involvement boundary

No recurring human input is required after setup for public OHLCV collection, macro snapshots, reliability updates, local artifacts, chronological history, or health status.

Human approval is required for installed runtime/schedule enablement, live delivery integration, production policy changes, M6 adoption, automatic execution, and phase/version promotion.

## 8. Standard read route

New context:

1. `AGENTS.md`
2. `START_HERE.md`
3. `MASTER_PLAN.md` for planning
4. `CURRENT_STATE.md` and `NEXT_ACTION.md`
5. target route only
6. one active spec for implementation

Do not broadly scan history or archived plans.

## 9. Document roles

| Document | Role |
|---|---|
| `MASTER_PLAN.md` | overall architecture and current priority |
| `PRODUCT_IMPLEMENTATION_ROUTE.md` | P route and P9 gate |
| `MACRO_IMPLEMENTATION_ROUTE.md` | canonical M route |
| `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md` | M operational completion contract |
| `M5_M6_EXECUTION_PLAN_20260721.md` | secondary improvement/adoption route |
| `CURRENT_STATE.md` | accepted state and controlling interpretation |
| `NEXT_ACTION.md` | exactly one current task |
| active spec | detailed implementation contract |
| `CONTROL.md` | stable safety/git/runtime rules |
| `AI_WORKFLOW.md` | ChatGPT/Codex execution and review |

## 10. Completion definitions

P route completion requires adequate actual-backed evidence and an accepted human-reviewed proposal where applicable.

M route completion requires:

- accepted public-data current snapshot operation;
- accepted chronological history and latest status;
- chart-first operator artifact;
- fail-closed stale/insufficient behavior;
- separately approved and verified report-only runtime cadence;
- current docs and operator behavior agreement.

## 11. Safety and version boundary

- no automatic order;
- no private/account/order endpoints;
- no unapproved runtime, delivery, gate, threshold, scoring, or classifier change;
- generated/private data remains local and uncommitted;
- frozen runtime repo requires explicit `RUNTIME_TASK`.

M-OPS source and local evidence remain Ver04.x. `Ver05` requires explicitly approved production adoption and matching validation; local M-OPS completion alone does not promote the version.
