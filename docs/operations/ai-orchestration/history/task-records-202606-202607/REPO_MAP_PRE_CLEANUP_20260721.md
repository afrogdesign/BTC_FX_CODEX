# Repository Map for AI

## 1. Repo boundaries

| Purpose | Path | Rule |
|---|---|---|
| primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | normal work |
| frozen old runtime repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | explicit `RUNTIME_TASK` only |

Do not infer branch or HEAD from chat history. Confirm them from local repo state when git evidence is required.

## 2. Canonical entrypoints

| Path | Purpose |
|---|---|
| `AGENTS.md` | Codex worker and repo boundary |
| `docs/operations/ai-orchestration/START_HERE.md` | shortest role-aware router |
| `docs/operations/ai-orchestration/MASTER_PLAN.md` | overall plan and 3-axis relationship |
| `docs/operations/ai-orchestration/CURRENT_STATE.md` | accepted current state |
| `docs/operations/ai-orchestration/NEXT_ACTION.md` | one current task |

## 3. Current plan routes

| Path | Purpose |
|---|---|
| `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md` | Product/P route |
| `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md` | Macro/M route |
| `docs/operations/ai-orchestration/AI_OPERATIONS_STATUS.md` | A-route conclusion and optional tooling |
| `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md` | current P8/P9 operating contract |
| `docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md` | macro research basis |

## 4. Execution and control

| Path | Purpose |
|---|---|
| `docs/operations/ai-orchestration/INITIAL_PROMPT.md` | ChatGPT Project prompt source |
| `docs/operations/ai-orchestration/AI_WORKFLOW.md` | ChatGPT/Codex execution and review |
| `docs/operations/ai-orchestration/CONTROL.md` | stable safety、git、runtime、validation rules |
| `chatgpt/specs/active/` | one current implementation contract |
| `chatgpt/specs/archive/` | accepted and superseded contracts |
| `chatgpt/tasks/` | optional strict task-contract tooling |

## 5. Source directories

| Path | Purpose |
|---|---|
| `src/` | application and evidence logic |
| `tools/` | CLI and support tools |
| `tests/` | tests |
| `scripts/` | operator scripts |
| `docs/operations/strategy/` | current research and strategy references |
| `docs/operations/deploy/` | deployment and runtime records |

## 6. Record files

| Path | Purpose |
|---|---|
| `MILESTONES.md` | major accepted checkpoints |
| `DECISIONS.md` | durable decisions and supersession records |
| `TASK_LEDGER.md` | historical Work ID lookup only |
| `handoffs/` | explicit handoff records only |

## 7. Archive locations

| Path | Contents |
|---|---|
| `docs/operations/ai-orchestration/history/plan-archive-20260721/` | superseded product/A/replay plans |
| `docs/operations/ai-orchestration/history/record-optimization-20260721/` | verbose pre-optimization current records |
| `docs/operations/ai-orchestration/history/ai-routing-optimization-20260721/` | old routing documents |
| `docs/operations/strategy/archive/` | superseded integrated product and macro plans |
| `chatgpt/specs/archive/` | implementation contract history |

Archive is not a default read path.

## 8. Default read routes

Fresh ChatGPT planning task:

```text
AGENTS.md
→ START_HERE.md
→ MASTER_PLAN.md
→ current state / one target route only
```

Fresh ChatGPT implementation or review task:

```text
AGENTS.md
→ START_HERE.md
→ active spec or named source/tests/artifact
→ AI_WORKFLOW.md only when execution rules are needed
```

Fresh Codex task:

```text
AGENTS.md
→ START_HERE.md
→ task prompt
→ named files and matching tests
```

Same-thread work:

```text
new delta only
```

## 9. Non-default reads

Do not broadly scan:

- `.venv312/`
- `logs/`
- generated files under `local/`
- full `TASK_LEDGER.md`
- all handoffs
- history and archive directories
- frozen runtime repo
- old task notes in the orchestration root

Read these only when the request names the relevant evidence or historical question.

## 10. Compatibility entries

`PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHATGPT_COMMANDER_PROMPT.md`, and `RESUME.md` are compatibility pointers. Do not treat them as independent rules.


## 11. Legacy operations archive

`history/legacy-ops-20260701/` contains completed repository-switch and runtime-migration records. Current operational work uses `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `CONTROL.md`, and an explicit current task.
