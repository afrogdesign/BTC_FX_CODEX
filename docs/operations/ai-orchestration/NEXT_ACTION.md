# NEXT_ACTION

- current_work_id: `BTCFX-20260630-EVIDENCE-ACCURACY-RESUME`
- mode: `LIGHT_CODEX`

## Current goal

Close the now-unneeded runtime pull handoff path, confirm this MCP repo is the current source of truth, and resume the evidence / intraperiod / win-rate diagnostics phase.

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/MILESTONES.md`, `docs/operations/ai-orchestration/CURRENT_STATE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`, `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF_PLAN.md`, `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`, `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260624.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260625.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260626.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260627.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260628.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260629.md`, `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260630.md` |
| Edit | `docs/operations/ai-orchestration/CURRENT_STATE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md`, `docs/operations/ai-orchestration/EVIDENCE_ACCURACY_RESUME.md` |
| Do not | `AGENTS.md`, `START_HERE.md`, `CONTROL.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `MILESTONES.md`, `RUNTIME_PULL_HANDOFF.md`, `RUNTIME_PULL_HANDOFF_REVIEW.md`, `RUNTIME_PULL_HANDOFF_PLAN.md`, `DASHBOARD_PARITY_SMOKE_TEST.md`, `CHECKPOINT_RUNBOOK.md`, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, `src/`, `tools/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`, old runtime execution repo, push, pull, runtime actions` |
| Test | `git diff --check -- docs/operations/ai-orchestration/CURRENT_STATE.md docs/operations/ai-orchestration/NEXT_ACTION.md docs/operations/ai-orchestration/PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md docs/operations/ai-orchestration/EVIDENCE_ACCURACY_RESUME.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | unexpected uncommitted changes、required evidence/control file missing、scope 外編集が必要、broad repo inspection が必要、old runtime execution repo access が必要、pull が必要、push が必要、runtime action が必要、product/trading/safety judgment が必要、source/runtime/generated/logs/.venv312/old runtime repo or analysis report edit が必要、delete/move/archive/generated file commit/notification sending/trading action が必要、test/check fail、staging に allowed 外 file が混入 |

## Next recommended follow-up

- `BTCFX-20260630-INTRAPERIOD-WINRATE-DIAGNOSTIC-PASS`
- Goal: perform a focused diagnostic pass over available intraperiod outcome reports to identify what metrics and tests are needed next, without changing trading logic.
