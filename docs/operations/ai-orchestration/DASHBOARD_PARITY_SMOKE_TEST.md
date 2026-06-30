# DASHBOARD_PARITY_SMOKE_TEST

## Purpose

`Safety Flags` / `Surface Roles` / `Ready Gate Copy` / single-source boundary / report-only safety が、ローカル dashboard parity として揃っているかを機械的に確認する。

## Scope

- 対象は docs-only の smoke report。
- 実装変更はしない。
- 判定は指定されたテストと文書の明示文字列だけに限定する。

## Targeted test command

`./.venv312/bin/python -m unittest tests.test_active_plan_notification_formatting.ActivePlanNotificationFormattingTest.test_write_current_manual_delivery_app_dashboard_cli_supports_help_and_writes_static_html`

## Smoke checklist

| Check | Evidence | Result | Notes |
|---|---|---|---|
| targeted dashboard unittest passes | test command output | pass | `OK` |
| dashboard test asserts `Safety Flags` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `human_review_required` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `trade_execution_allowed` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `automatic_order_allowed` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `external_notification_allowed` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `paper_positions_integration` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `Surface Roles` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `Public HTML notification report` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `Notification mail` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `Local dashboard / app surface` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `Single source of truth` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `same decision source, no separate decision path` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `Ready Gate Copy` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `manual_trade_ready=` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `dashboard=local/manual_delivery_app_surface/app-dashboard.html` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `snapshot=local/manual_delivery_app_surface/app-snapshot.json` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `manifest=local/manual_delivery_app_surface/app-surface-manifest.json` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| dashboard test asserts `safety_boundary=report-only / not FORMAL_GO / no automatic order / human decides manually` | `tests/test_active_plan_notification_formatting.py` | pass | 追加済み |
| strategy plan keeps public HTML as current main manual-trading UI | `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` | pass | 明記あり |
| strategy plan keeps notification mail as triage / entry point | `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` | pass | 明記あり |
| strategy plan keeps local dashboard / app surface as confirmation and future automation surface | `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` | pass | 明記あり |
| strategy plan keeps single-source doctrine | `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` | pass | 明記あり |
| strategy plan keeps report-only / not FORMAL_GO / no automatic order / human decides manually | `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` | pass | 明記あり |

## Result

dashboard_parity_complete

## Issues found

none

## Next recommendation

ready_for_checkpoint_review

## Out of scope

- no source edits
- no test edits
- no generated file commit
- no runtime execution
- no notification sending
- no trading logic change
- no push
- no pull
- no old runtime repo access
