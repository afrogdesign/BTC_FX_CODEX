# NEXT_ACTION

- current_work_id: `BTCFX-20260630-DEVELOPMENT-TO-RUNTIME-HANDOFF-PREP`
- mode: `LIGHT_CODEX`

## Current goal

development repo の evidence-quality / OHLCV coverage visibility phase を、後で runtime / execution repo に反映するための report-only handoff package として整理する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/EVIDENCE_QUALITY_PHASE_CHECKPOINT.md`, `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_WARNING_E2E_SMOKE.md`, `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_OPERATOR_WARNING.md`, `docs/operations/ai-orchestration/OHLCV_RANGE_FRESHNESS_GUARD.md`, `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CAUSE_DIAGNOSTIC.md`, `docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_ACTUAL_SNAPSHOT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/DEVELOPMENT_TO_RUNTIME_HANDOFF_PREP.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | development repo の report-only handoff package を整理する |
| Tests | `git diff --check -- docs/operations/ai-orchestration/DEVELOPMENT_TO_RUNTIME_HANDOFF_PREP.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs handoff prep の区切りとして docs 2 files を 1 commit |
| Stop | source/test 編集が必要、generated/logs 編集が必要、progress HTML 更新が必要、CURRENT_PROGRESS.md 更新が必要、trading logic 変更が必要、OHLCV fetch が必要、runtime / old runtime / private / order / notification が必要、generated files を commit する必要がある、runtime repo reflection が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-DEVELOPMENT-TO-RUNTIME-HANDOFF-CHECKPOINT`
- Goal: review the handoff package and stop at a clean development-repo checkpoint, ready for explicit user approval before any runtime repo reflection.
