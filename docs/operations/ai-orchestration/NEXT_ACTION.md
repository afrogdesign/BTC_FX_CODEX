# NEXT_ACTION

- current_work_id: `BTCFX-20260630-APP-RESUME-AND-NEXT-PRODUCT-STEP`
- mode: `LIGHT_CODEX`

## Current goal

Return to app/product work from the new MCP-primary orchestration baseline.

## Current summary

| Field | Value |
|---|---|
| Read | `RESUME_SMOKE_TEST.md`, `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `REPO_MAP.md`, `ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md`, `scripts/refresh_current_manual_delivery_app_surface.command`, `tests/test_notification_detail_page.py`, `tests/test_summary_format.py`, `tests/test_summary_active_plan_subject.py` |
| Edit | `APP_PRODUCT_RESUME.md`, `NEXT_ACTION.md` |
| Do not | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHECKPOINT_RUNBOOK.md`, `RUNTIME_PULL_HANDOFF.md`, `REPO_MAP.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, old runtime execution repo, push, pull, runtime actions |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-APP-DASHBOARD-PARITY-CHECK`
- Goal: compare local app dashboard readiness/safety context against the public HTML and mail surface expectations, then make one small dashboard-parity improvement if a concrete missing field is found.
