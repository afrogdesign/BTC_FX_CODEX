# NEXT_ACTION

- current_work_id: `BTCFX-20260630-NO-OHLCV-COVERAGE-ACTUAL-SNAPSHOT`
- mode: `LIGHT_CODEX`

## Current goal

既存 report-only export/check/contract path から、現在の実際の `ohlcv_source_coverage_summary` values を記録する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_ACTUAL_SNAPSHOT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | actual `ohlcv_source_coverage_summary` values を記録し、blocker を分類する |
| Tests | report-only commands, `git diff --check -- docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_ACTUAL_SNAPSHOT.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs 2 files だけを 1 commit |
| Stop | report-only command 失敗、`ohlcv_source_coverage_summary` 未確認、generated files commit が必要、source/test 編集が必要、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-OHLCV-WINDOW-GAP-AUDIT`
- Goal: inspect why many candidate windows remain uncovered and identify the next safe coverage-improvement direction without changing trading logic.
