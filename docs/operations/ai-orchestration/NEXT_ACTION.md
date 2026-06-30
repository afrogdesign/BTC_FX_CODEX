# NEXT_ACTION

- current_work_id: `BTCFX-20260630-OHLCV-WINDOW-GAP-AUDIT`
- mode: `LIGHT_CODEX`

## Current goal

`per_window_ohlcv_gap` の原因を report-only で監査し、candidate timestamp range と OHLCV coverage range のズレを確認する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_ACTUAL_SNAPSHOT.md`, `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CHECKPOINT_REVIEW.md`, `docs/operations/deploy/Ver03-v2_CANDIDATE_COVERAGE_WINDOW_REVIEW_20260610.md`, `docs/operations/deploy/Ver03-v2_OHLCV_INPUT_CONTRACT_20260609.md`, `docs/operations/deploy/Ver03-v2_CONTROLLED_BUILDER_RUN_20260610.md`, `docs/specs/active-plan-intraperiod-outcomes.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/OHLCV_WINDOW_GAP_AUDIT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | `per_window_ohlcv_gap` の原因監査と次 task 決定 |
| Tests | `git diff --check -- docs/operations/ai-orchestration/OHLCV_WINDOW_GAP_AUDIT.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs 2 files だけを 1 commit |
| Stop | source/test 編集が必要、generated/logs 編集が必要、generated files commit が必要、trading logic 変更が必要、OHLCV fetch が必要、runtime / old runtime / private / order / notification が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-OHLCV-RANGE-FRESHNESS-GUARD`
- Goal: add report-only OHLCV range freshness/staleness visibility so old OHLCV coverage cannot silently dominate `no_ohlcv`.
