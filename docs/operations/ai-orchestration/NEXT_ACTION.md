# NEXT_ACTION

- current_work_id: `BTCFX-20260630-CANDIDATE-TYPE-SIDE-BREAKDOWN`
- mode: `NORMAL_CODEX`

## Current goal

candidate_type / side / active_primary_action の report-only breakdown を追加する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/ENTRY_REACHED_OUTCOME_BREAKDOWN.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/CANDIDATE_TYPE_SIDE_BREAKDOWN.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | candidate_type / side / active_primary_action の report-only breakdown を追加する |
| Tests | `.venv312/bin/python -m unittest tests.test_active_plan_candidate_intraperiod_outcomes`, `git diff --check -- src/trade/active_plan_intraperiod.py tests/test_active_plan_candidate_intraperiod_outcomes.py docs/operations/ai-orchestration/CANDIDATE_TYPE_SIDE_BREAKDOWN.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、source/test/docs 以外の編集が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-MAJOR-TURN-CANDIDATE-REVIEW`
- Goal: review potential_fakeout and potential_missed_turn candidates using report-only evidence, without changing trading logic.
