# APP_PRODUCT_RESUME

## Purpose

新しい MCP-primary orchestration baseline から app/product work に安全に戻るための compact note。

## Orchestration baseline

- `RESUME_SMOKE_TEST.md` の結果は `ready_for_product_work`
- Normal work は MCP local edit / validation / local commit / compact report
- Push は checkpoint-only
- Old runtime execution repo は触らない

## Product direction

- public HTML notification report is the current main manual-trading UI
- notification mail is triage / entry point
- local dashboard / app surface is confirmation and future automation surface
- 3 つは同じ source of truth を共有する
- safety boundary は report-only, not FORMAL_GO, no automatic order, human decides manually

## Explicit evidence checks

| Check | Evidence file | Result | Notes |
|---|---|---|---|
| `RESUME_SMOKE_TEST.md` has `ready_for_product_work` | `docs/operations/ai-orchestration/RESUME_SMOKE_TEST.md` | pass | smoke test summary の next recommendation が一致 |
| strategy plan says public HTML report is the main manual-trading UI | `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` | pass | Public HTML section に明記 |
| strategy plan says local dashboard / app surface is confirmation and future automation surface | `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` | pass | Local dashboard / app surface section に明記 |
| manual-preview runbook says `scripts/refresh_current_manual_delivery_app_surface.command` prints compact terminal operator summary | `docs/operations/manual-preview/ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md` | pass | runbook に明記 |
| launcher script contains summary output lines for ready gate fields | `scripts/refresh_current_manual_delivery_app_surface.command` | pass | ready gate field lines と local_app_surface_* 行がある |
| `tests/test_notification_detail_page.py` checks `scripts/refresh_current_manual_delivery_app_surface.command` | `tests/test_notification_detail_page.py` | pass | `assertIn` で確認 |
| `tests/test_notification_detail_page.py` checks `local/manual_delivery_app_surface/index.html` | `tests/test_notification_detail_page.py` | pass | `assertIn` で確認 |
| `tests/test_notification_detail_page.py` checks `local/manual_delivery_app_surface/app-dashboard.html` | `tests/test_notification_detail_page.py` | pass | `assertIn` で確認 |
| `tests/test_summary_format.py` checks `scripts/refresh_current_manual_delivery_app_surface.command` | `tests/test_summary_format.py` | pass | `assertIn` で確認 |
| `tests/test_summary_active_plan_subject.py` checks `[BTCFX Ver03-v4]` | `tests/test_summary_active_plan_subject.py` | pass | subject prefix が一致 |

## Current app/product status

- ready_for_next_product_task

## Next recommended product task

- Work ID: `BTCFX-20260630-APP-DASHBOARD-PARITY-CHECK`
- Goal: compare local app dashboard readiness/safety context against the public HTML and mail surface expectations, then make one small dashboard-parity improvement if a concrete missing field is found.

## Out of scope

- no source edits
- no tests edits
- no runtime execution
- no generated file commit
- no push
- no pull
- no old runtime repo access
- no trading logic change
- no notification sending
