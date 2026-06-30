# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ORCHESTRATION-MINI-CODEX-HARDENING`
- mode: `LIGHT_CODEX`

## Current goal

Harden prompt templates and runbooks for Codex 5.4-mini medium by making tasks more mechanical, smaller, and less judgment-heavy.

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md`, `PROMPTS.md`, `REPO_MAP.md`, `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `CLEANUP_AUDIT.md` |
| Edit | `MINI_CODEX_RULES.md`, `PROMPTS.md`, `START_HERE.md`, `REPO_MAP.md`, `NEXT_ACTION.md` |
| Do not | `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `CONTROL.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, old runtime execution repo |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、deletion/move が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-ORCHESTRATION-PROMPT-LINT-CHECKLIST`
- Goal: Add a preflight checklist that ChatGPT uses before issuing Codex prompts, so malformed or oversized tasks are caught before sending.
