# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ORCHESTRATION-RESUME-SMOKE-TEST`
- mode: `LIGHT_CODEX`

## Current goal

Perform a docs-only dry-run review of the new START_HERE / CONTROL / PROMPTS / MINI_CODEX / PREFLIGHT flow, without editing product files.

## Current summary

| Field | Value |
|---|---|
| Read | `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `REPO_MAP.md` |
| Edit | `RESUME_SMOKE_TEST.md`, `NEXT_ACTION.md` |
| Do not | `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `CONTROL.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, old runtime execution repo |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、deletion/move が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-APP-RESUME-AND-NEXT-PRODUCT-STEP`
- Goal: return to app/product work from the new MCP-primary orchestration baseline.
