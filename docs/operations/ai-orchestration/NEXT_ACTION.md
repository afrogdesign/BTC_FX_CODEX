# NEXT_ACTION

- current_work_id: `BTCFX-20260630-OHLCV-RANGE-FRESHNESS-GUARD`
- mode: `NORMAL_CODEX`

## Current goal

old OHLCV coverage が silently `no_ohlcv` を支配しないように、report-only の OHLCV range freshness / staleness visibility を追加する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/trade/active_plan_intraperiod.py`, `tools/log_feedback.py`, `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `tests/test_active_plan_notification_formatting.py`, `tests/test_summary_format.py`, `tests/test_notification_detail_page.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/OHLCV_WINDOW_GAP_AUDIT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `src/trade/active_plan_intraperiod.py`, `tools/log_feedback.py`, `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `tests/test_active_plan_notification_formatting.py`, `tests/test_summary_format.py`, `tests/test_notification_detail_page.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/OHLCV_RANGE_FRESHNESS_GUARD.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | OHLCV range freshness / staleness visibility を report-only で追加する |
| Tests | `./.venv312/bin/python -m unittest tests.test_active_plan_candidate_intraperiod_outcomes tests.test_active_plan_notification_formatting tests.test_summary_format tests.test_notification_detail_page tests.test_log_feedback`, `git diff --check -- src/trade/active_plan_intraperiod.py tools/log_feedback.py src/ai/summary.py src/notification/detail_page.py tests/test_active_plan_candidate_intraperiod_outcomes.py tests/test_active_plan_notification_formatting.py tests/test_summary_format.py tests/test_notification_detail_page.py tests/test_log_feedback.py docs/operations/ai-orchestration/OHLCV_RANGE_FRESHNESS_GUARD.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | OHLCV fetch が必要、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated/logs を commit する必要がある、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-OHLCV-RANGE-FRESHNESS-E2E-SMOKE`
- Goal: run report-only export/check smoke and confirm OHLCV range freshness fields appear without committing generated files.
