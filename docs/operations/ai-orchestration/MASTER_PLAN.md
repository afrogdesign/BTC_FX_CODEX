# btc_monitor Master Plan

last_updated: 2026-07-25
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

### 3.0 Current canonical state — 2026-07-25

Branch `Ver04-v5`, HEAD `34c751fb9f257d188dc1ed2680df90fbe29855d1`。canonical actual inputは`provided`で、actual episodes/linksは`149/149`。現行selected actual evidenceはeligible `2`、high `0`、medium `2`、unique actual episodes used `2`、resolved proxy events `40`、unresolved proxy events `4`である。

Product routeは`program=P`, `phase=P9`。P9 initial/practical readinessはともに`false`で、blockerはactual不存在ではなく量、side/setup coverage、confidence、validation windowの不足である。P8 daily healthは一回のcycleの健康・lineage、P9 cumulative evidenceは複数日/episodeのproposal eligibilityであり、daily successからP9 readinessへ自動昇格しない。

Macroの`macro_p9_proposal_engine.v1`は`program=M`のM5/M6 improvement proposal engineであり、Product P9とは別namespaceである。全体はreport-only / human-decided / no automatic tuning / no automatic phase promotion / no automatic order。

| Phase | Result | Status |
|---|---|---|
| P1–P7 | importer, linking, scenarios, classifier, replay, shadow | accepted |
| P8 | deterministic evidence pipeline and operating cycle | accepted / collecting |
| P9 | evidence-backed tuning proposal | blocked |

Current blocker:

```text
actual evidence exists but is insufficient in volume, coverage, confidence, and validation window
→ Product P9 remains evidence-gated and human-approval pending
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
→ M-OPS4 separate runtime/schedule enablement — accepted at `a9b3d46` / runtime `690c014`
→ M-OPS5 autonomous status and stale-data health — accepted in the existing report-only lane
```

There is no active source implementation spec.

M-OPS3 accepted command:

- `render-macro-structure-operator`

Accepted local review evidence:

- `local/reports/macro_structure/mops3_review/`
- latest v2 artifact: `operator_3f09d915f61d0183d51c`

M-OPS4 is accepted for `com.afrog.btc-macro-structure` only, with the six JST schedule entries and report-only boundaries recorded in the archived runtime spec. M-OPS5 remains a separate source task.

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
P8 continues evidence collection with actual and proxy lanes separated
→ Product P9 remains evidence-gated and human-approval pending
→ Macro M-OPS1–M-OPS5 remain accepted on the existing report-only lane
→ Product/Macro namespace and version boundaries are retained
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

M-OPS1–M-OPS4 satisfy the accepted source, local-artifact, and target-only runtime portion. M-OPS5 remains next.

## 10. Safety and version boundary

- no automatic order;
- no private/account/order endpoints;
- no unapproved runtime, launchd, mail, notification, gate, threshold, scoring, or classifier change;
- generated/private data remains local and uncommitted;
- frozen runtime repo requires explicit `RUNTIME_TASK`.

M-OPS source and local evidence remain Ver04.x. `Ver05` requires explicitly approved production adoption, matching validation, runtime verification where applicable, and ChatGPT acceptance.


---

## 11. Product-facing macro visual priority override — 2026-07-22

This section supersedes earlier `M-OPS5 next` and `no active source implementation` wording where they conflict.

M-OPS1 through M-OPS5 are accepted and active on the existing report-only cadence. The next product priority is not another M-OPS health or audit phase. It is the user-facing macro visual completion lane defined in:

- `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`

Current sequence:

```text
M-VIS1 4H-first macro chart
→ M-LINE1 deterministic trendlines/channels
→ M-EVENT1 structural events
→ M-HYP1 condition/invalidation scenarios
→ M-ENTRY1 fixed latest entry
→ separately approved M-DELIVERY1 HTML mail integration
```

M-STATS1 remains optional shadow evidence and does not block product v1 completion when sample size is insufficient.

Execution policy:

- finish one useful module before starting the next;
- reuse accepted M-OPS source and artifacts;
- prioritize visible operator value over metadata or audit completeness;
- use matching tests, a small deterministic fixture, one bounded smoke, and task-scoped diff check;
- do not run long replay, broad parameter search, repeated runtime health cycles, or full-suite validation without explicit acceptance-critical approval;
- do not change runtime, schedule, mail, notification, policy, gates, thresholds, classifiers, or automatic-order behavior in M-VIS1.
