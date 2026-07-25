# START_HERE

This is the shortest role-aware entrypoint for `btc_monitor` work.

## 1. Choose the route

### New ChatGPT thread or unknown context

Always read:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

Then read only what the request needs.

| Need | Read |
|---|---|
| overall plan or next-area judgment | `MASTER_PLAN.md` |
| accepted current state | `CURRENT_STATE.md` |
| exactly one current task or approval boundary | `NEXT_ACTION.md` |
| Product planning | `PRODUCT_IMPLEMENTATION_ROUTE.md` |
| Macro route | `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md` |
| autonomous macro completion | `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md` |
| M5/M6 improvement and adoption | `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md` |
| implementation / FIX / acceptance | one file under `chatgpt/specs/active/` when present |
| ChatGPT/Codex execution | `AI_WORKFLOW.md` |
| stable safety, git, runtime, validation | `CONTROL.md` |
| accepted checkpoints | `MILESTONES.md` |

Do not read all of these by default.

### Same thread and same task

Read only the delta:

- new Codex report
- changed source
- matching tests
- CLI parser/dispatch when relevant
- fresh artifact
- active-spec note when present
- task-related diff

Do not reread stable planning or workflow docs.

### New Codex report review

Triage the Codex report first as a locator, not proof. For a committed task, use
the two-call Git fast path before source reads or searches:

1. `get_workspace_repo_status`
2. `get_workspace_repo_diff(scope="commit", commit="<reported commit>")`

Use conditional log or targeted file reads only for one explicit unresolved
acceptance question. Ignore unrelated dirty/untracked entries; they are not review
targets. The detailed contract is `AI_WORKFLOW.md` Step G.

### Fresh Codex context

Read:

1. `AGENTS.md`
2. `START_HERE.md`
3. the task prompt
4. files explicitly named by the task

Read state, master plan, or active spec only when named, required, or inconsistent with the task.

## 2. Plan hierarchy

```text
MASTER_PLAN.md
├─ PRODUCT_IMPLEMENTATION_ROUTE.md
├─ docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md
│  ├─ MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md
│  └─ M5_M6_EXECUTION_PLAN_20260721.md
└─ AI_OPERATIONS_STATUS.md
```

Meaning:

- Product / P route is the main manual-trading support axis
- Macro / M route autonomously builds higher-timeframe structure and reliable support/resistance from public data
- M5/M6 is a secondary improvement/adoption lane, not the prerequisite for normal macro operation
- AI / A route is a completed operations experiment, not an active product backlog

Current high-level state:

- P1–P8 accepted; P9 blocked by absent actual-backed evidence
- M1–M5 research/tooling accepted
- M-OPS1 accepted at `89bd338`
- M-OPS2 accepted at `dea0e33`
- M-OPS3 accepted at `09330b9`
- M-OPS4 runtime/schedule enablement accepted at source fix `a9b3d46` with runtime implementation `690c014`
- M-OPS5 is next and not started
- M6 not started and not authorized
- A1/A2 accepted, A3 superseded, A4 not planned

## 3. Mandatory current-state handoff

Before proposing or starting a new task, read `CURRENT_STATE.md` and `NEXT_ACTION.md` when they contain an accepted blocker, no-repeat boundary, or approval boundary.

The first status report must state:

1. the latest accepted checkpoint locator;
2. the current blocker, active implementation, or approval boundary;
3. the exact event that permits the next transition;
4. which accepted review must not be repeated.

### P route

Report:

- P1–P8 and actual-evidence readiness are accepted;
- P9 is blocked by the absent complete MEXC Trade History / Order History / Position History batch;
- importer, episode-builder, linker, CLI, and P8 readiness review are not repeated unless a reopening trigger is true.

Canonical decision: `DEC-20260721-012`.

### M route — controlling interpretation

Report:

- the primary M objective is autonomous public-data macro structure operation;
- private actual-trade data is not required to calculate support/resistance reliability;
- M1–M5 are accepted foundations;
- M-OPS1–M-OPS3 are accepted and must not be reopened without a concrete contradiction;
- M-OPS4 is accepted only for the target `com.afrog.btc-macro-structure`, primary repo, six JST times, and report-only boundaries recorded in the archived runtime spec;
- installed runtime, scheduling, launchd/plist/cron, mail, and notification operations remain prohibited until an explicit named `RUNTIME_TASK`; installed targets are not repositories;
- M5 `winner=none` does not invalidate accepted M-OPS source/artifact work;
- M5/M6 remains secondary and follows its separate plan only when improvement/adoption is being considered.

Canonical decision: `DEC-20260721-014`.

## 4. Current execution route

Normal source route:

```text
ChatGPT fixes one useful scope
→ one bounded Codex implementation
→ matching tests / small fixture
→ compact text report
→ ChatGPT MCP review
→ accept, one material FIX, or human judgment
```

Runtime route:

```text
accepted source and local artifacts
→ explicit human RUNTIME_TASK approval
→ inspect actual installed target
→ one bounded runtime/schedule task
→ target-specific verification and rollback evidence
```

Use direct MCP work for deterministic Markdown, spec, state, and review tasks that do not require local tests or git operations.

## 5. Macro completion order

```text
accepted M1–M4 capabilities
→ M-OPS1 current snapshot and local daily report — accepted
→ M-OPS2 chronological reliability continuity — accepted
→ M-OPS3 chart-first operator artifact — accepted
→ M-OPS4 runtime/schedule enablement — accepted
→ M-OPS5 autonomous health and stale-data reporting — next, not implemented
→ periodic M5 refresh only when triggered
→ optional M6 proposal and adoption
```

Human approval is not required for public-data calculations or local artifacts. It is required for installed runtime/schedule changes, live delivery changes, production policy changes, and candidate adoption.

## 6. Repo boundary

| Purpose | Path | Rule |
|---|---|---|
| canonical repository | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | only development/source/runtime-source repo |
| installed runtime/delivery target | operational target | explicit named `RUNTIME_TASK` only; never a second repository |

ChatGPT uses `AFROG_MCP` as the primary repo inspection path. Branch and HEAD are confirmed from local repo state when git evidence is required.

## 7. Current source-of-truth order

```text
repo source, tests, generated artifacts
→ active spec when present
→ MASTER_PLAN and target route
→ CURRENT_STATE and NEXT_ACTION
→ CONTROL and AI_WORKFLOW
→ MILESTONES and DECISIONS
→ archived plans and specs
→ TASK_LEDGER and chat history
```

Historical documents never override current source or canonical routes.

## 8. Non-default reads

Do not broadly scan:

- `TASK_LEDGER.md`
- `history/`
- `docs/operations/strategy/archive/`
- old task notes in the orchestration root
- unrelated generated outputs and logs
- old repositories; installed targets are not repositories

Read a historical file only when a current task identifies the exact evidence or decision being investigated.

## 9. Record roles

| File | Responsibility |
|---|---|
| `MASTER_PLAN.md` | overall plan and current priority |
| `CURRENT_STATE.md` | accepted state, blocker, controlling interpretation |
| `NEXT_ACTION.md` | exactly one current task or approval boundary |
| `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md` | completion route for automatic macro structure operation |
| `M5_M6_EXECUTION_PLAN_20260721.md` | secondary challenger improvement and adoption route |
| `CONTROL.md` | stable safety / git / runtime rules |
| `AI_WORKFLOW.md` | shared execution and review process |
| `MILESTONES.md` | major accepted checkpoints |
| `DECISIONS.md` | durable decisions and supersession records |
| active spec | current detailed implementation contract when authorized |
| `TASK_LEDGER.md` | historical Work ID lookup only |

## 10. Safety baseline

- report-only
- not `FORMAL_GO`
- human-decided trades and production adoption
- no automatic order
- no secrets or private/account/order endpoints
- no unapproved runtime, launchd, mail, notification change
- no raw exchange export commit
- no unsupported gate, threshold, scoring, classifier change
- no automatic phase promotion or production adoption


---

## 11. Product-facing macro visual route — 2026-07-22

For work related to the practical 4H macro chart, trendlines/channels, structural events, scenario hypotheses, fixed latest entry, or final HTML mail integration, read:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `docs/operations/ai-orchestration/CURRENT_STATE.md`
4. `docs/operations/ai-orchestration/NEXT_ACTION.md`
5. `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`

Then read only the current module source, matching tests, CLI route, and current artifact.

Controlling interpretation:

- M-OPS1 through M-OPS5 remain accepted and are not reopened without a concrete contradiction;
- the current product-facing next module is `M-VIS1`;
- `M-VIS1` adds a practical 4H-first macro chart using existing accepted levels and does not change reliability semantics;
- M-LINE1, M-EVENT1, M-HYP1, and M-ENTRY1 are subsequent separate modules;
- mail/notification/runtime/schedule changes remain prohibited until a separately approved `M-DELIVERY1` task;
- long replay, repeated health observation, broad evaluation, and full-suite validation are not default completion requirements.
