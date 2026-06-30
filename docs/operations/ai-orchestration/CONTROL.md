# AI Orchestration Control

last_updated: 2026-06-30
repo: `afrogdesign/BTC_FX_CODEX`
primary_mcp_working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
old_runtime_execution_repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
branch_source_rule: `read from git status --short --branch and CONTROL.md, not from chat history`

## Current State

- repo-local orchestration default is MCP primary
- normal Codex task is local edit + local validation + local commit + compact report
- routine GitHub push is wasteful and out of default scope
- old runtime execution repo must not be edited, run, inspected, or synced in normal MCP tasks

## Current Objective

- AI orchestration を MCP-primary / no-routine-push で軽く保つ
- そのあと evidence-based accuracy diagnostics へ戻る
- public HTML / notification mail / local dashboard の single-source doctrine は維持する

## Safety Boundary

- Report-only.
- Not `FORMAL_GO`.
- No automatic order.
- No API keys.
- No private, account, or order endpoints.
- No runtime restart.
- No `paper_positions.csv` integration unless explicitly approved.
- Public HTML / mail / dashboard must not diverge in trading logic.

## Validation Rules

- Docs-only changes: `git diff --check`.
- Python code changes: targeted `./.venv312/bin/python -m unittest <tests>`.
- CLI/report builder changes: relevant CLI/report validation only.
- Every task: `git status --short --branch`.

## Operation Mode

- default: `LIGHT_CODEX` or `NORMAL_CODEX`
- local commit is allowed when checks pass
- push is reserved for `CHECKPOINT_PUSH` tasks only

## Next Decision

Continue with local/report-only operator tooling, diagnostics, and evidence-based accuracy after the orchestration cleanup settles, without daily-sync wiring, exchange fetch, trading logic changes, notification sending, runtime changes, report regeneration, or automation safety changes.

## Deferred Follow-up

- Define a minimal checkpoint branch/push procedure and runtime-repo pull handoff without executing either action.
- Future verification must stay configuration/docs/dry-run oriented and must not read or print secrets.
- Keep `CONTROL.md` lightweight and move durable accepted history into `MILESTONES.md`.

## Evidence Pointers

- durable accepted history: `docs/operations/ai-orchestration/MILESTONES.md`
- active handoff context only: `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
- product direction: `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`
- latest reviewed workflow metadata as needed: `docs/operations/ai-orchestration/TASK_LEDGER.md`
