# Manual Delivery App Surface Runbook

status: current operator runbook

## Purpose

Generate or refresh the local manual-delivery app surface for human review.

This runbook does not define product strategy or version promotion. Current product direction is in `docs/operations/ai-orchestration/MASTER_PLAN.md`.

## Standard command

```bash
scripts/refresh_current_manual_delivery_app_surface.command
```

The command uses `tools/log_feedback.py` to refresh the surface and verify its ready gate.

## Expected local outputs

```text
local/manual_delivery_app_surface/index.html
local/manual_delivery_app_surface/app-dashboard.html
local/manual_delivery_app_surface/app-surface-manifest.json
```

Open `index.html` manually. Generated files remain local and uncommitted.

## Required output checks

The command must report:

- readiness status
- allowed next action
- human review requirement
- trade execution permission
- automatic order permission
- external notification permission
- paper-position integration state
- dashboard, snapshot, and manifest paths
- safety boundary

Missing ready-gate fields are an error.

## Safety boundary

- report-only
- not `FORMAL_GO`
- human review required
- no automatic order
- no external notification
- no unapproved `paper_positions.csv` integration

## Detailed CLI discovery

Use current CLI help rather than copying old command inventories into this runbook.

```bash
.venv312/bin/python tools/log_feedback.py --help
```

## History

The long Ver03-v4 operating record was archived at:

`docs/operations/history/manual-preview-ver03-v4/ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md`
