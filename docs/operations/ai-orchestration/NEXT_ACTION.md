# NEXT_ACTION

- current_work_id: `BTCFX-20260630-EVIDENCE-QUALITY-PHASE-CHECKPOINT`
- mode: `LIGHT_CODEX`

## Current goal

completed evidence-quality / OHLCV coverage visibility phase をまとめ、次の product-quality direction を決める。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_WARNING_E2E_SMOKE.md`, `docs/operations/ai-orchestration/OHLCV_RANGE_FRESHNESS_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_ACTUAL_SNAPSHOT.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/EVIDENCE_QUALITY_PHASE_CHECKPOINT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | evidence-quality / OHLCV coverage visibility phase の checkpoint をまとめる |
| Tests | `git diff --check -- docs/operations/ai-orchestration/EVIDENCE_QUALITY_PHASE_CHECKPOINT.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs checkpoint の区切りとして docs 2 files を 1 commit |
| Stop | source/test 編集が必要、generated/logs 編集が必要、progress HTML 更新が必要、CURRENT_PROGRESS.md 更新が必要、trading logic 変更が必要、OHLCV fetch が必要、runtime / old runtime / private / order / notification が必要、generated files を commit する必要がある、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-DEVELOPMENT-TO-RUNTIME-HANDOFF-PREP`
- Goal: prepare a report-only handoff package for reflecting the development repo state to the runtime/execution repo later, without touching the runtime repo yet.
