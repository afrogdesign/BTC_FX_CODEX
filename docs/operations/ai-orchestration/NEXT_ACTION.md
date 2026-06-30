# NEXT_ACTION

- current_work_id: `BTCFX-20260630-AUTO-EVIDENCE-QUALITY-SUMMARY-BUILDER`
- mode: `NORMAL_CODEX`

## Current goal

`evidence_quality_summary` を intraperiod outcomes から安定生成する pure helper を追加する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | evidence_quality_summary を intraperiod outcomes から安定生成する pure helper を追加する |
| Tests | `./.venv312/bin/python -m unittest tests.test_active_plan_candidate_intraperiod_outcomes`, `git diff --check -- src/trade/active_plan_intraperiod.py tests/test_active_plan_candidate_intraperiod_outcomes.py docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/NEXT_ACTION の一区切りとして 1 commit |
| Stop | trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated/logs 編集が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-EVIDENCE-QUALITY-SUMMARY-SURFACE-WIRING`
- Goal: wire the generated evidence quality summary into the existing manual surface/app snapshot path without changing trading logic.
