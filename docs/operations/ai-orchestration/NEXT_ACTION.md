# NEXT_ACTION

- current_work_id: `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-CHECKPOINT-REVIEW`
- mode: `LIGHT_CODEX`

## Current goal

no_ohlcv source coverage visibility path を一区切りとして review し、次の report-only product-quality task を決める。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CAUSE_DIAGNOSTIC.md`, `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_SURFACE_WIRING.md`, `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_E2E_SMOKE.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_SUMMARY_E2E_SMOKE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | `no_ohlcv` visibility path の review と次 task 決定 |
| Tests | `git diff --check -- docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CHECKPOINT_REVIEW.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs 2 files だけを 1 commit |
| Stop | source/test 編集が必要、generated/logs 編集が必要、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated files commit が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-NO-OHLCV-COVERAGE-ACTUAL-SNAPSHOT`
- Goal: capture the current actual OHLCV coverage summary values from existing report-only surfaces and identify the next safe coverage-improvement direction.
