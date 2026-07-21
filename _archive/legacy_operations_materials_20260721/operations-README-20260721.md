# 運用資料 — Legacy-compatible output area

`運用資料` is no longer the project plan, AI entrypoint, current-state source, or operating-rule source.

## What remains active

Only this subtree remains in use:

`運用資料/reports/`

Existing source, tests, and scripts still write generated Markdown reports there. This path is retained for compatibility until a separately tested source migration is approved.

## Do not use this directory for

- AI startup
- current plan selection
- branch or HEAD determination
- current task selection
- product or safety rules
- runtime instructions

Use instead:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `docs/operations/ai-orchestration/MASTER_PLAN.md`
4. `docs/operations/ai-orchestration/CURRENT_STATE.md`
5. `docs/operations/ai-orchestration/NEXT_ACTION.md`

## Archived material

Former settings, plans, progress boards, work logs, reference documents, and operating notes were moved to:

`_archive/legacy_operations_materials_20260721/`

Those files are historical evidence only and never override current source, tests, canonical docs, or active specs.
