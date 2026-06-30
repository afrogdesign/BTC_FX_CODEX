# NEXT_ACTION

- current_work_id: `BTCFX-20260630-MAJOR-TURN-CANDIDATE-REVIEW`
- mode: `LIGHT_CODEX`

## Current goal

potential_fakeout / potential_missed_turn / bad_entry_timing を report-only で整理する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/INTRAPERIOD_WINRATE_DIAGNOSTIC_PASS.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_BACKLOG.md`, `docs/operations/ai-orchestration/CANDIDATE_TYPE_SIDE_BREAKDOWN.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260624.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260630.md` |
| Edit | `docs/operations/ai-orchestration/MAJOR_TURN_CANDIDATE_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | major-turn 候補の report-only 要約を整理する |
| Tests | `git diff --check -- docs/operations/ai-orchestration/MAJOR_TURN_CANDIDATE_REVIEW.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs の一区切りとして 1 commit |
| Stop | report 値が読めない、candidate ID の捏造が必要、source/test 編集が必要、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-MANUAL-SURFACE-QUALITY-BACKLOG`
- Goal: consolidate report-only evidence improvements into the manual trading surface backlog.
