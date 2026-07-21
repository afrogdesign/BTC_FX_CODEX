# Repository Map for AI

## Primary boundaries

| Purpose | Path |
|---|---|
| primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` |
| frozen old runtime repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` |

The frozen repo is outside normal inspection and execution.

## Canonical AI anchors

| Path | Purpose |
|---|---|
| `docs/operations/ai-orchestration/INITIAL_PROMPT.md` | ChatGPT Project initial prompt source |
| `AGENTS.md` | Codex worker boundary |
| `docs/operations/ai-orchestration/START_HERE.md` | role-aware repo entrypoint |
| `docs/operations/ai-orchestration/AI_WORKFLOW.md` | shared execution/review process |
| `docs/operations/ai-orchestration/CURRENT_STATE.md` | accepted current state |
| `docs/operations/ai-orchestration/NEXT_ACTION.md` | one current task |
| `docs/operations/ai-orchestration/CONTROL.md` | stable controls |
| `chatgpt/specs/active/` | current detailed implementation contract |
| `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md` | product route |

## Post-M5 orchestration design

| Path | Purpose |
|---|---|
| `docs/operations/ai-orchestration/AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md` | A1–A4 task-manifest design |
| `docs/operations/ai-orchestration/MACRO_REPLAY_AND_AI_ACCEPTANCE_SIMPLIFICATION_PLAN_20260721.md` | replay-cost and later R1–R5 backlog |

A1 task-contract work is separate from replay-stage/cache work.

## Source directories

| Path | Purpose |
|---|---|
| `src/` | application and evidence logic |
| `tools/` | CLI and support tools |
| `tests/` | tests |
| `scripts/` | operator scripts |
| `chatgpt/specs/active/` | current implementation spec |
| `chatgpt/specs/archive/` | accepted specs |
| `chatgpt/tasks/` | task contracts after A1 implementation |
| `docs/operations/strategy/` | product and research plans |

## Default read routes

Fresh ChatGPT:

```text
INITIAL_PROMPT.md
→ AGENTS.md
→ START_HERE.md
→ request-specific state/spec/workflow only
```

Fresh Codex:

```text
AGENTS.md
→ START_HERE.md
→ task prompt or rendered manifest launcher
→ named files and matching tests
```

Same-thread ChatGPT/Codex:

```text
new delta only
```

## Non-default reads

- `.venv312/`
- `logs/`
- generated files under `local/`
- full `TASK_LEDGER.md`
- handoffs
- history directories
- old task notes in the orchestration root

Read these only when the task explicitly depends on them.

## Compatibility entries

`PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHATGPT_COMMANDER_PROMPT.md`, and `RESUME.md` point back to the canonical route. They are not separate sources of truth.
