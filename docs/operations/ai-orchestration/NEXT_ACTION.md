# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ORCHESTRATION-CHECKPOINT-PUSH-DESIGN`
- mode: `LIGHT_CODEX`

## Current goal

Define checkpoint push and runtime pull handoff procedures without executing push, pull, runtime actions, or product changes.

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md`, `PROMPTS.md`, `REPO_MAP.md`, `CLEANUP_CANDIDATES.md` |
| Edit | `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `START_HERE.md`, `PROMPTS.md`, `REPO_MAP.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md` |
| Do not | `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `CONTROL.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, old runtime execution repo, push, pull, runtime actions |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-ORCHESTRATION-CLEANUP-AUDIT-PASS`
- Goal: review cleanup candidates and classify what can be archived later, without deleting files.
