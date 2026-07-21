# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- recorded branch: `Ver04-v2`
- branch and HEAD must be confirmed by local git before Codex work
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: `chatgpt/specs/active/20260721_generated_reports_directory_migration.md`
- active task manifest: none
- safety: report-only / not `FORMAL_GO` / human-decided / no automatic order

## Plan state

### Product / P route

- P1〜P7: accepted
- P8 deterministic evidence pipeline: accepted and collecting evidence
- P9: blocked pending adequate evidence and explicit human approval
- main product gap: insufficient actual-backed ground truth and validation sample

### Macro / M route

- M1〜M5: accepted
- M5 winner: `none`
- M5 recommendation: `continue_shadow_collection`
- M6: not started and not authorized

### AI operations / A route

- A1: accepted as optional strict tooling
- A2: accepted pilot
- A3: superseded and archived
- A4: not planned
- normal route: compact prompt、bounded implementation、compact report、ChatGPT MCP review

## Documentation cleanup accepted in working tree

The canonical plan structure is:

```text
MASTER_PLAN.md
├─ PRODUCT_IMPLEMENTATION_ROUTE.md
├─ docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md
└─ AI_OPERATIONS_STATUS.md
```

Old planning, AI-routing, runtime-transition, and operations-management documents were moved under `_archive/` or orchestration history.

## Active migration

Generated reports are now written under `local/reports/`; the former top-level operations directory is retired.

The active implementation contract migrates generated reports to:

```text
local/reports/
```

Required behavior:

- active code/tests/scripts use `local/reports`
- tracked old report snapshots move to `_archive/legacy_operations_materials_20260721/reports_snapshot/`
- ignored/untracked generated reports remain local and uncommitted
- the former top-level operations directory is removed after acceptance
- no trading, runtime, notification, mail, gate, or classifier behavior changes

## Current blocker

The directory migration requires local source edits, matching tests, filesystem classification using git tracking state, and one local commit. MCP alone cannot safely complete it.

## Navigation

- active spec: `chatgpt/specs/active/20260721_generated_reports_directory_migration.md`
- immediate task: `NEXT_ACTION.md`
- overall plan: `MASTER_PLAN.md`
- product route: `PRODUCT_IMPLEMENTATION_ROUTE.md`
- execution: `AI_WORKFLOW.md`
- stable controls: `CONTROL.md`
