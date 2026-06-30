# NEXT_ACTION

- current_work_id: `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-CAUSE-DIAGNOSTIC`
- mode: `NORMAL_CODEX`

## Current goal

`no_ohlcv` が支配的になる原因を、candidate timestamp と OHLCV coverage の観点で report-only に診断する pure helper を追加する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_SUMMARY_E2E_SMOKE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CAUSE_DIAGNOSTIC.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | report-only の OHLCV source coverage cause helper を追加する |
| Tests | `./.venv312/bin/python -m unittest tests.test_active_plan_candidate_intraperiod_outcomes`, `git diff --check -- src/trade/active_plan_intraperiod.py tests/test_active_plan_candidate_intraperiod_outcomes.py docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CAUSE_DIAGNOSTIC.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated/logs commit が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-SURFACE-WIRING`
- Goal: surface the OHLCV source coverage cause summary on the manual/app report path without changing trading logic.
