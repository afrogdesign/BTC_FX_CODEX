# AI Orchestration Control

last_updated: 2026-07-02
repo: `afrogdesign/BTC_FX_CODEX`
primary_mcp_working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
frozen_old_runtime_execution_repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
branch_source_rule: `read from git status --short --branch and CONTROL.md, not from chat history`

## Current State

- repo-local orchestration default is MCP primary
- normal Codex task is local edit + local validation + local commit + compact report
- routine GitHub push is wasteful and out of default scope
- old runtime execution repo must not be edited, run, inspected, or synced in normal MCP tasks
- product route has been consolidated into Ver04-v1 self-improvement loop docs

## Current Objective

Build a practical human-operated BTC manual trading support system.

Primary objective:

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Immediate product objective:

- establish deterministic post-evaluation / self-improvement loop
- use daily proxy evaluation without requiring daily actual-trade import
- use weekly review for trend/regime drift
- use biweekly actual trade Excel import as ground truth calibration
- keep public HTML / notification mail / local dashboard aligned under single-source doctrine

## Safety Boundary

- Report-only.
- Not `FORMAL_GO`.
- No automatic order.
- No API keys.
- No private, account, or order endpoints.
- No runtime restart during normal product work.
- No notification send behavior change without explicit approval.
- No raw exchange export commit.
- No `paper_positions.csv` integration unless explicitly approved.
- Public HTML / mail / dashboard must not diverge in trading logic.
- Human decides manually.

## Product Source-of-Truth

- active route: `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- final self-improvement design: `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- manual 15m win definition: `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- high-level integrated plan: `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
- durable accepted history: `docs/operations/ai-orchestration/MILESTONES.md`

## Validation Rules

- Docs-only changes: `git diff --check`.
- Python code changes: targeted `./.venv312/bin/python -m unittest <tests>`.
- CLI/report builder changes: relevant CLI/report validation only.
- Every task: `git status --short --branch`.
- Exchange export import work must be local-file only and must not call exchange APIs.

## Operation Mode

- default: `LIGHT_CODEX`, `NORMAL_CODEX`, or `REVIEW_ONLY` depending on task scope
- local commit is allowed when checks pass
- push is reserved for `CHECKPOINT_PUSH` tasks only
- product docs should stay concise and route through `PRODUCT_IMPLEMENTATION_ROUTE.md`

## Next Decision

Proceed to post-evaluation asset health audit before implementing new evaluator code.

Default next task:

```text
BTCFX-20260702-POST-EVAL-ASSET-HEALTH-AUDIT
```

This task must be read-only / docs-only and must not call APIs, read secrets, restart runtime, change notification sending, change trading logic, fetch OHLCV, or touch private/order endpoints.

## Deferred Follow-up

- Implement deterministic daily proxy evaluator after asset health audit.
- Add manual actual trade import schema after daily proxy route is clear.
- Add actual trade to signal linking after import schema is stable.
- Add biweekly ground truth report after linking is stable.
- Restore AI post review only as optional qualitative enrichment after deterministic loop is reliable.

## Evidence Pointers

- durable accepted history: `docs/operations/ai-orchestration/MILESTONES.md`
- active product route: `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- active handoff context only: `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
- latest reviewed workflow metadata as needed: `docs/operations/ai-orchestration/TASK_LEDGER.md`
