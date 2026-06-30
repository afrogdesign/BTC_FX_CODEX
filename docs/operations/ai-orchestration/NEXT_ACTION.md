# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ORCHESTRATION-PROMPT-LINT-CHECKLIST`
- mode: `LIGHT_CODEX`

## Current goal

Add a preflight checklist that ChatGPT uses before issuing Codex prompts, so malformed or oversized tasks are caught before sending.

## Current summary

| Field | Value |
|---|---|
| Read | `START_HERE.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `NEXT_ACTION.md` |
| Edit | `PROMPT_PREFLIGHT_CHECKLIST.md`, `PROMPTS.md`, `START_HERE.md`, `MINI_CODEX_RULES.md`, `NEXT_ACTION.md` |
| Do not | `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `CONTROL.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, old runtime execution repo |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、deletion/move が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-ORCHESTRATION-RESUME-SMOKE-TEST`
- Goal: Perform a docs-only dry-run review of the new START_HERE / CONTROL / PROMPTS / MINI_CODEX / PREFLIGHT flow, without editing product files.
