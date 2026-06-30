# NEXT_ACTION

- current_work_id: `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-E2E-SMOKE`
- mode: `LIGHT_CODEX`

## Current goal

manual surface export/check の smoke path を走らせ、`ohlcv_source_coverage_summary` が exported artifacts に出ることを確認する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_SURFACE_WIRING.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_E2E_SMOKE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | `ohlcv_source_coverage_summary` の smoke 確認と記録 |
| Tests | smoke commands, `git diff --check -- docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_E2E_SMOKE.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs 2 files だけを 1 commit |
| Stop | smoke 失敗、`ohlcv_source_coverage_summary` 未確認、generated/logs commit が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-CHECKPOINT-REVIEW`
- Goal: review the completed no_ohlcv source coverage visibility path and decide the next report-only product-quality task.
