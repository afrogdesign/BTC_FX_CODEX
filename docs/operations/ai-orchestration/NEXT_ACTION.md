# NEXT_ACTION

- current_work_id: `BTCFX-20260630-MANUAL-SURFACE-QUALITY-BACKLOG`
- mode: `LIGHT_CODEX`

## Current goal

report-only evidence improvements を manual trading surface backlog にまとめる。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/EVIDENCE_QUALITY_BACKLOG.md`, `docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_DIAGNOSTIC.md`, `docs/operations/ai-orchestration/VALID_SAMPLE_WINRATE_REPORT.md`, `docs/operations/ai-orchestration/ENTRY_REACHED_OUTCOME_BREAKDOWN.md`, `docs/operations/ai-orchestration/CANDIDATE_TYPE_SIDE_BREAKDOWN.md`, `docs/operations/ai-orchestration/MAJOR_TURN_CANDIDATE_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/MANUAL_SURFACE_QUALITY_BACKLOG.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | manual trading surface backlog を report-only で整理する |
| Tests | `git diff --check -- docs/operations/ai-orchestration/MANUAL_SURFACE_QUALITY_BACKLOG.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs backlog の一区切りとして 1 commit |
| Stop | source/test 編集が必要、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-MANUAL-SURFACE-EVIDENCE-SUMMARY`
- Goal: expose the evidence-quality summaries on the manual trading surface without changing trading logic.
