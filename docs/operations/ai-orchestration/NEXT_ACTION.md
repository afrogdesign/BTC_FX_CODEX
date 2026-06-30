# NEXT_ACTION

- current_work_id: `BTCFX-20260630-EVIDENCE-QUALITY-CHECKPOINT-REVIEW`
- mode: `LIGHT_CODEX`

## Current goal

evidence-quality surface path を一区切りとして確認し、次の product-quality task を決める。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_DIAGNOSTIC.md`, `docs/operations/ai-orchestration/VALID_SAMPLE_WINRATE_REPORT.md`, `docs/operations/ai-orchestration/ENTRY_REACHED_OUTCOME_BREAKDOWN.md`, `docs/operations/ai-orchestration/CANDIDATE_TYPE_SIDE_BREAKDOWN.md`, `docs/operations/ai-orchestration/MAJOR_TURN_CANDIDATE_REVIEW.md`, `docs/operations/ai-orchestration/MANUAL_SURFACE_QUALITY_BACKLOG.md`, `docs/operations/ai-orchestration/MANUAL_SURFACE_EVIDENCE_SUMMARY.md`, `docs/operations/ai-orchestration/MANUAL_SURFACE_EVIDENCE_SUMMARY_APP_CONTRACT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/EVIDENCE_QUALITY_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | evidence-quality surface path を一区切りとして確認し、次の product-quality task を決める |
| Tests | `git diff --check -- docs/operations/ai-orchestration/EVIDENCE_QUALITY_CHECKPOINT_REVIEW.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs checkpoint として 1 commit |
| Stop | source/test 編集が必要、generated/logs 編集が必要、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-EVIDENCE-QUALITY-SMOKE-EXPORT`
- Goal: run the existing manual surface export/check path and confirm `evidence_quality_summary` appears in exported surface artifacts without committing generated files.
