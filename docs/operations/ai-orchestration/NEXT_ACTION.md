# NEXT_ACTION

- current_work_id: `BTCFX-20260630-DEVELOPMENT-TO-RUNTIME-HANDOFF-CHECKPOINT`
- mode: `STOPPING_POINT`

## Current goal

handoff package を review し、development repo 側の切りの良い checkpoint として止める。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/DEVELOPMENT_TO_RUNTIME_HANDOFF_PREP.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_PHASE_CHECKPOINT.md`, `docs/operations/ai-orchestration/OHLCV_STALE_COVERAGE_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/DEVELOPMENT_TO_RUNTIME_HANDOFF_CHECKPOINT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | handoff package を review して development-repo checkpoint として止める |
| Tests | `git diff --check -- docs/operations/ai-orchestration/DEVELOPMENT_TO_RUNTIME_HANDOFF_CHECKPOINT.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs final checkpoint の区切りとして docs 2 files を 1 commit |
| Stop | source/test 編集が必要、generated/logs 編集が必要、progress HTML 更新が必要、CURRENT_PROGRESS.md 更新が必要、trading logic 変更が必要、OHLCV fetch が必要、runtime / old runtime / private / order / notification が必要、generated files を commit する必要がある、runtime repo reflection が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `USER_DECISION_REQUIRED`
- Goal: wait for explicit user approval before runtime repo reflection or further development work.
