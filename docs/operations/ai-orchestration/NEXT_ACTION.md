# NEXT_ACTION

- current_work_id: `BTCFX-20260630-APP-DASHBOARD-PARITY-SMOKE-TEST`
- mode: `LIGHT_CODEX`

## Current goal

Perform a targeted dashboard parity smoke test covering Safety Flags, Surface Roles, Ready Gate Copy, single-source boundary, and report-only safety.

## Current summary

| Field | Value |
|---|---|
| Read | `APP_PRODUCT_RESUME.md`, `NEXT_ACTION.md`, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, `local/manual_delivery_app_surface/app-ready.json`, `scripts/refresh_current_manual_delivery_app_surface.command`, `tests/test_active_plan_notification_formatting.py` |
| Edit | `DASHBOARD_PARITY_SMOKE_TEST.md`, `NEXT_ACTION.md` |
| Do not | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `APP_PRODUCT_RESUME.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, `src/`, `tools/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, old runtime execution repo, push, pull, runtime actions |
| Test | `./.venv312/bin/python -m unittest tests.test_active_plan_notification_formatting.ActivePlanNotificationFormattingTest.test_write_current_manual_delivery_app_dashboard_cli_supports_help_and_writes_static_html`, `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | unexpected uncommitted changes、targeted dashboard unittest fails、scope 外編集が必要、runtime/source/generated edit が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-CHECKPOINT-REVIEW-BEFORE-PUSH`
- Goal: review local commits and decide whether a CHECKPOINT_PUSH is appropriate.
