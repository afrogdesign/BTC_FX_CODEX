# NEXT_ACTION

- current_work_id: `BTCFX-20260630-EVIDENCE-QUALITY-BACKLOG-WITH-METRIC-FIX`
- mode: `NORMAL_CODEX`

## Current goal

Correct the intraperiod diagnostic metrics exactly and create the evidence-quality backlog for the next practical trading-system improvement tasks.

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/INTRAPERIOD_WINRATE_DIAGNOSTIC_PASS.md`, `docs/operations/ai-orchestration/EVIDENCE_ACCURACY_RESUME.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `docs/operations/ai-orchestration/CURRENT_STATE.md`, `docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`, `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`, `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260624.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260625.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260626.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260627.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260628.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260629.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260630.md` |
| Edit | `docs/operations/ai-orchestration/INTRAPERIOD_WINRATE_DIAGNOSTIC_PASS.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_BACKLOG.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md` |
| Do not | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `MILESTONES.md`, `CURRENT_STATE.md`, `EVIDENCE_ACCURACY_RESUME.md`, `RUNTIME_PULL_HANDOFF.md`, `RUNTIME_PULL_HANDOFF_REVIEW.md`, `RUNTIME_PULL_HANDOFF_PLAN.md`, `DASHBOARD_PARITY_SMOKE_TEST.md`, `CHECKPOINT_RUNBOOK.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, `src/`, `tools/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, old runtime execution repo, push, pull, runtime actions` |
| Test | `git diff --check -- docs/operations/ai-orchestration/INTRAPERIOD_WINRATE_DIAGNOSTIC_PASS.md docs/operations/ai-orchestration/EVIDENCE_QUALITY_BACKLOG.md docs/operations/ai-orchestration/NEXT_ACTION.md docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | unexpected uncommitted changes、required evidence/control file missing or unreadable、corrected table cannot be made internally consistent with the listed source reports、scope 外編集が必要、broad repo inspection が必要、old runtime execution repo access が必要、pull が必要、push が必要、runtime action が必要、product/trading/safety judgment が必要、source/runtime/generated/logs/.venv312/old runtime repo or analysis report edit が必要、delete/move/archive/generated file commit/notification sending/trading action が必要、test/check fail、staging に allowed 外 file が混入 |

## Next recommended follow-up

- `BTCFX-20260630-NO-OHLCV-COVERAGE-DIAGNOSTIC`
- Goal: diagnose why no_ohlcv dominates the intraperiod reports and make the valid sample denominator explicit without changing trading logic.
