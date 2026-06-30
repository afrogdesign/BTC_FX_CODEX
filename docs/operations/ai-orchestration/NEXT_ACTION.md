# NEXT_ACTION

- current_work_id: `BTCFX-20260630-OHLCV-STALE-COVERAGE-WARNING-E2E-SMOKE`
- mode: `LIGHT_CODEX`

## Current goal

report-only export/check smoke を走らせ、stale OHLCV warning が exported artifacts に出ることを確認する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_OPERATOR_WARNING.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_WARNING_E2E_SMOKE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | stale OHLCV warning の smoke 確認を記録する |
| Tests | smoke commands, `git diff --check -- docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_WARNING_E2E_SMOKE.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs smoke record の区切りとして docs 2 files を 1 commit |
| Stop | smoke command 失敗、stale warning 未確認、freshness fields 未確認、generated/logs を commit する必要、source/test 編集が必要、trading logic 変更が必要、OHLCV fetch が必要、runtime / old runtime / private / order / notification が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-OHLCV-STALE-COVERAGE-CHECKPOINT-REVIEW`
- Goal: review completed stale OHLCV operator warning path and decide the next report-only product-quality task.
