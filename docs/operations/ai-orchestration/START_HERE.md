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
| Macro planning | `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md` |
| implementation / FIX / acceptance | one file under `chatgpt/specs/active/` |
| ChatGPT/Codex execution | `AI_WORKFLOW.md` |
| stable safety、git、runtime、validation | `CONTROL.md` |
| accepted checkpoints | `MILESTONES.md` |

Do not read all of these by default.

### Same thread and same task

Read only the delta:

- new Codex report
- changed source
- matching tests
- CLI parser / dispatch when relevant
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
└─ AI_OPERATIONS_STATUS.md
```

Meaning:

- Product / P route is the main system-development axis
- Macro / M route is a supporting evidence and operator-decision axis
- AI / A route is a completed operations experiment, not an active product backlog

Current high-level state:

- P1〜P7 accepted
- P8 evidence pipeline accepted and collecting evidence
- P9 blocked pending adequate evidence and human approval
- M1〜M5 accepted
- M6 not started and not authorized
- A1/A2 accepted, A3 superseded, A4 not planned

## 3. Current execution route

Normal route:

```text
ChatGPT fixes one useful scope
→ one bounded Codex implementation
→ matching tests / small fixture
→ compact text report
→ ChatGPT MCP review
→ accept, one material FIX, or human judgment
```

Use direct MCP work for deterministic Markdown、spec、state、and review tasks that do not require local tests or git operations.

Task manifests and JSON reports are optional strict tooling only. See `AI_OPERATIONS_STATUS.md`.

## 4. Repo boundary

| Purpose | Path | Rule |
|---|---|---|
| primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | normal read/edit/test/git |
| frozen old runtime repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | explicit `RUNTIME_TASK` only |

ChatGPT uses `AFROG_Business_MCP` as the primary repo inspection path. Branch and HEAD are confirmed from local repo state when git evidence is required.

## 5. Current source-of-truth order

```text
repo source、tests、generated artifacts
→ active spec
→ MASTER_PLAN and target route
→ CURRENT_STATE and NEXT_ACTION
→ CONTROL and AI_WORKFLOW
→ MILESTONES and DECISIONS
→ archived plans and specs
→ TASK_LEDGER and chat history
```

Historical documents never override current source or canonical routes.

## 6. Non-default reads

Do not broadly scan:

- `TASK_LEDGER.md`
- `history/`
- `docs/operations/strategy/archive/`
- old task notes in the orchestration root
- generated outputs and logs
- frozen runtime repo

Read a historical file only when a current task identifies the exact evidence or decision being investigated.

## 7. Record roles

| File | Responsibility |
|---|---|
| `MASTER_PLAN.md` | overall plan and plan hierarchy |
| `CURRENT_STATE.md` | accepted state and blocker |
| `NEXT_ACTION.md` | exactly one current task |
| `CONTROL.md` | stable safety / git / runtime / validation rules |
| `AI_WORKFLOW.md` | shared execution and review process |
| `MILESTONES.md` | major accepted checkpoints |
| `DECISIONS.md` | durable decisions and supersession records |
| active spec | current detailed implementation contract |
| `TASK_LEDGER.md` | historical Work ID lookup only |

## 8. Safety baseline

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no secrets or private/account/order endpoints
- no unapproved runtime、launchd、mail、notification change
- no raw exchange export commit
- no unsupported gate、threshold、scoring、classifier change
- no automatic Phase promotion or production adoption
