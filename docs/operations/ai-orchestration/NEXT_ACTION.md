# NEXT_ACTION

- current_work_id: `BTCFX-20260630-RUNTIME-PULL-HANDOFF-REVIEW`
- mode: `LIGHT_CODEX`

## Current goal

Review whether the old runtime execution repo should pull the pushed checkpoint, without executing pull, runtime restart, notification sending, or trading actions.

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md`, `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md`, `docs/operations/ai-orchestration/DASHBOARD_PARITY_SMOKE_TEST.md`, `docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`, `docs/operations/ai-orchestration/MILESTONES.md`, `docs/operations/ai-orchestration/CURRENT_STATE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`, `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md` |
| Edit | `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do not | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `DASHBOARD_PARITY_SMOKE_TEST.md`, `PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`, `MILESTONES.md`, `CURRENT_STATE.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, `src/`, `tools/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, old runtime execution repo, push, pull, runtime actions` |
| Test | `git diff --check -- docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF_REVIEW.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | unexpected uncommitted changes、required evidence file missing、scope 外編集が必要、broad repo inspection が必要、old runtime execution repo access が必要、pull が必要、push が必要、runtime action が必要、product/trading/safety judgment が必要、source/runtime/generated/logs/.venv312/old runtime repo edit が必要、delete/move/archive/generated file commit/notification sending/trading action が必要、test/check fail、staging に allowed 外 file が混入 |

## Next recommended follow-up

- `BTCFX-20260630-RUNTIME-PULL-HANDOFF-PLAN`
- Goal: 実 pull の前に、old runtime execution repo の pull 手順と確認点を別 task で整える。
