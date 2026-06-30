# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ORCHESTRATION-CLEANUP-AUDIT-PASS`
- mode: `LIGHT_CODEX`

## Current goal

Review cleanup candidates and classify what can be archived later, without deleting files.

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md`, `REPO_MAP.md`, `CLEANUP_CANDIDATES.md`, `chatgpt/README.md` |
| Edit | `CLEANUP_CANDIDATES.md`, `CLEANUP_AUDIT.md`, `NEXT_ACTION.md` |
| Do not | `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `CONTROL.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, old runtime execution repo |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、deletion/move が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-ORCHESTRATION-MINI-CODEX-HARDENING`
- Goal: Harden prompt templates and runbooks for Codex 5.4-mini medium by making tasks more mechanical, smaller, and less judgment-heavy.
