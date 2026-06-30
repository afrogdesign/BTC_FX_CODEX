# NEXT_ACTION

- current_work_id: `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-SURFACE-WIRING`
- mode: `NORMAL_CODEX`

## Current goal

`summarize_intraperiod_ohlcv_source_coverage` を manual surface / app contract / stdout-json 側へ report-only で露出する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/trade/active_plan_intraperiod.py`, `tools/log_feedback.py`, `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_active_plan_notification_formatting.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CAUSE_DIAGNOSTIC.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `tools/log_feedback.py`, `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_active_plan_notification_formatting.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_SURFACE_WIRING.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | `ohlcv_source_coverage_summary` を manual surface / app contract / stdout-json に追加する |
| Tests | `./.venv312/bin/python -m unittest tests.test_log_feedback tests.test_active_plan_notification_formatting`, `git diff --check -- tools/log_feedback.py src/ai/summary.py src/notification/detail_page.py tests/test_active_plan_notification_formatting.py tests/test_log_feedback.py docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_SURFACE_WIRING.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、OHLCV fetch が必要、generated/logs commit が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-E2E-SMOKE`
- Goal: run the manual surface export/check smoke path and confirm `ohlcv_source_coverage_summary` appears without committing generated files.
