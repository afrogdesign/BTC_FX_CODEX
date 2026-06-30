# NEXT_ACTION

- current_work_id: `BTCFX-20260630-APP-DASHBOARD-PARITY-SURFACE-ROLES`
- mode: `NORMAL_CODEX`

## Current goal

Improve local app dashboard parity by adding a compact Surface Roles section explaining the public HTML / notification mail / local dashboard relationship.

## Current summary

| Field | Value |
|---|---|
| Read | `START_HERE.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `MINI_CODEX_RULES.md`, `APP_PRODUCT_RESUME.md`, `NEXT_ACTION.md`, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, `local/manual_delivery_app_surface/app-ready.json`, `local/manual_delivery_app_surface/app-dashboard.html`, `tools/log_feedback.py`, `tests/test_active_plan_notification_formatting.py` |
| Edit | `tools/log_feedback.py`, `tests/test_active_plan_notification_formatting.py`, `NEXT_ACTION.md` |
| Do not | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `CURRENT_STATE.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `APP_PRODUCT_RESUME.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, `src/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, old runtime execution repo, push, pull, runtime actions |
| Test | `.venv312/bin/python -m unittest tests.test_active_plan_notification_formatting.ActivePlanNotificationFormattingTest.test_write_current_manual_delivery_app_dashboard_cli_supports_help_and_writes_static_html`, `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | unexpected uncommitted changes、scope 外編集が必要、dashboard generator 不明、runtime/source/generated edit が必要、push/pull/runtime action が必要、test/check fail |

## Next recommended follow-up

- `BTCFX-20260630-APP-DASHBOARD-PARITY-READY-GATE-COPY`
- Goal: Make the local dashboard ready-gate guidance more copyable for human review without changing runtime behavior or trading logic.
