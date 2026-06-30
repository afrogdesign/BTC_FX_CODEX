# NEXT_ACTION

- current_work_id: `BTCFX-20260630-OHLCV-STALE-COVERAGE-OPERATOR-WARNING`
- mode: `NORMAL_CODEX`

## Current goal

`ohlcv_range_freshness_status == stale_before_latest_candidate` のとき、operator / manual surface 上で stale OHLCV coverage を見落とせない report-only warning として表示する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_summary_format.py`, `tests/test_notification_detail_page.py`, `tests/test_active_plan_notification_formatting.py`, `docs/operations/ai-orchestration/OHLCV_RANGE_FRESHNESS_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_summary_format.py`, `tests/test_notification_detail_page.py`, `tests/test_active_plan_notification_formatting.py`, `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_OPERATOR_WARNING.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | stale OHLCV coverage を report-only warning として可視化する |
| Tests | `./.venv312/bin/python -m unittest tests.test_summary_format tests.test_notification_detail_page tests.test_active_plan_notification_formatting`, `git diff --check -- src/ai/summary.py src/notification/detail_page.py tests/test_summary_format.py tests/test_notification_detail_page.py tests/test_active_plan_notification_formatting.py docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_OPERATOR_WARNING.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | OHLCV fetch が必要、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated/logs を commit する必要がある、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-OHLCV-STALE-COVERAGE-WARNING-E2E-SMOKE`
- Goal: run report-only export/check smoke and confirm stale OHLCV warning appears without committing generated files.
