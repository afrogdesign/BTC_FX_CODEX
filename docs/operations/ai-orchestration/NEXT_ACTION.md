# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ENTRY-REACHED-OUTCOME-BREAKDOWN`
- mode: `NORMAL_CODEX`

## Current goal

entry-reached outcomes の内訳を report-only で明示する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/VALID_SAMPLE_WINRATE_REPORT.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_BACKLOG.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/ENTRY_REACHED_OUTCOME_BREAKDOWN.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do not | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `MILESTONES.md`, `CURRENT_STATE.md`, `PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`, `EVIDENCE_ACCURACY_RESUME.md`, `RUNTIME_PULL_HANDOFF.md`, `RUNTIME_PULL_HANDOFF_REVIEW.md`, `RUNTIME_PULL_HANDOFF_PLAN.md`, `DASHBOARD_PARITY_SMOKE_TEST.md`, `CHECKPOINT_RUNBOOK.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_BACKLOG.md`, `src/`, `tools/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, old runtime execution repo, push, pull, runtime actions` |
| Test | `./.venv312/bin/python -m unittest tests.test_active_plan_candidate_intraperiod_outcomes`, `git diff --check -- src/trade/active_plan_intraperiod.py tests/test_active_plan_candidate_intraperiod_outcomes.py docs/operations/ai-orchestration/ENTRY_REACHED_OUTCOME_BREAKDOWN.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | unexpected uncommitted changes、trading logic 変更が必要、runtime action が必要、old runtime repo access が必要、private/account/order endpoint が必要、通知送信が必要、source/test/docs 以外の編集が必要、テスト失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-CANDIDATE-TYPE-SIDE-BREAKDOWN`
- Goal: add report-only breakdowns by candidate_type, side, and active_primary_action without changing trading logic.
