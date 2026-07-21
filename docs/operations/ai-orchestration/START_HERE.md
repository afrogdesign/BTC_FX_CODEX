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
| exactly one current task | `NEXT_ACTION.md` |
| Product planning | `PRODUCT_IMPLEMENTATION_ROUTE.md` |
| Macro route | `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md` |
| autonomous macro completion | `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md` |
| M5/M6 improvement and adoption | `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md` |
| implementation / FIX / acceptance | one file under `chatgpt/specs/active/` |
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
- active-spec note
- task-related diff

Do not reread stable planning or workflow docs.

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
- M-OPS1 current snapshot source accepted at `89bd338`
- M-OPS2 chronological history accepted at `dea0e33`
- M-OPS3 chart-first operator artifact is the current implementation task
- M6 not started and not authorized
- A1/A2 accepted, A3 superseded, A4 not planned

## 3. Mandatory current-state handoff

Before proposing or starting a new task, read `CURRENT_STATE.md` and `NEXT_ACTION.md` when they contain an accepted blocker, no-repeat boundary, or active spec.

The first status report must state:

1. the latest accepted checkpoint locator;
2. the current blocker or active implementation;
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
- M1–M5 are accepted foundations, not completion of autonomous operation;
- M-OPS1 and M-OPS2 are accepted and must not be reopened without a concrete defect;
- M-OPS3 is the current active source task;
- M5 `winner=none` does not block operator artifact work;
- current implementation follows `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md` and the active M-OPS spec;
- M5/M6 remains secondary and follows its separate plan only when improvement/adoption is being considered.

Do not route general M work to `WAIT_FOR_EVIDENCE` or M5 refresh while an unfinished M-OPS phase exists.

Canonical decision: `DEC-20260721-014`.

## 4. Current execution route

Normal route:

```text
ChatGPT fixes one useful scope
→ one bounded Codex implementation
→ matching tests / small fixture
→ compact text report
→ ChatGPT MCP review
→ accept, one material FIX, or human judgment
```

Use direct MCP work for deterministic Markdown, spec, state, and review tasks that do not require local tests or git operations.

Task manifests and JSON reports are optional strict tooling only. See `AI_OPERATIONS_STATUS.md`.

## 5. Macro completion order

The controlling order is:

```text
accepted M1–M4 capabilities
→ M-OPS1 current snapshot and local daily report — accepted
→ M-OPS2 chronological reliability continuity — accepted
→ M-OPS3 chart-first operator artifact — current
→ explicit human-approved M-OPS4 runtime/schedule enablement
→ autonomous M-OPS5 health and stale-data reporting
→ periodic M5 refresh only when triggered
→ optional M6 proposal and adoption
```

Do not substitute M5 replay for unfinished M-OPS work.

Human approval is not required for every public-data calculation. It is required for installed runtime/schedule changes, live delivery changes, production policy changes, and candidate adoption.

## 6. Repo boundary

| Purpose | Path | Rule |
|---|---|---|
| primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | normal read/edit/test/git |
| frozen old runtime repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | explicit `RUNTIME_TASK` only |

ChatGPT uses `AFROG_Business_MCP` as the primary repo inspection path. Branch and HEAD are confirmed from local repo state when git evidence is required.

## 7. Current source-of-truth order

```text
repo source, tests, generated artifacts
→ active spec
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
- frozen runtime repo

Read a historical file only when a current task identifies the exact evidence or decision being investigated.

## 9. Record roles

| File | Responsibility |
|---|---|
| `MASTER_PLAN.md` | overall plan and current priority |
| `CURRENT_STATE.md` | accepted state, blocker, controlling interpretation |
| `NEXT_ACTION.md` | exactly one current task |
| `MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md` | completion route for automatic macro structure operation |
| `M5_M6_EXECUTION_PLAN_20260721.md` | secondary challenger improvement and adoption route |
| `CONTROL.md` | stable safety / git / runtime rules |
| `AI_WORKFLOW.md` | shared execution and review process |
| `MILESTONES.md` | major accepted checkpoints |
| `DECISIONS.md` | durable decisions and supersession records |
| active spec | current detailed implementation contract |
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
- no automatic Phase promotion or production adoption
