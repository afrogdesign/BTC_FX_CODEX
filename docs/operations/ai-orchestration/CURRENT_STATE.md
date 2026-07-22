# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v4`
- accepted visual checkpoint: `475ae4d`
- push: none
- safety: report-only / human-decided / no automatic order
- canonical visual plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`

## Accepted backend

- P1–P8 accepted
- P9 blocked pending complete private MEXC history input
- M-OPS1 through M-OPS5 accepted on the existing six-time cadence
- accepted runtime and health semantics are unchanged

## Accepted visual Product v1

### M-VIS1

- accepted checkpoint: `c1ceda3`
- 4H-first chart, 1H/4H horizontal zones, supplemental 15m view

### M-LINE1

- accepted implementation: `2d47f26`
- accepted ranking fix: `77b9ca3`
- deterministic confirmed-4H trendlines and channels

### M-EVENT1

- accepted implementation: `9295005`
- accepted fixes: `0a6f3f8`, `a79e488`
- deterministic structure events with valid parent chains and bounded retention

### M-HYP1

- accepted implementation: `882ab64`
- accepted validation fix: `7a51e98`
- accepted precedence fix: `e06fb99`
- bounded condition / next-confirmation / invalidation scenarios

### M-ENTRY1

- accepted implementation: `69c54cd`
- accepted hardening fix: `475ae4d`
- active spec: `chatgpt/specs/active/20260722_macro_structure_fixed_latest_entry.md`
- fixed local entry: `local/reports/macro_structure/operator/latest.html`
- complete available/unavailable screen with atomic replacement
- exact section validation and deterministic publication failure semantics
- no-4H callers do not modify the fixed entry

Visual Product v1 is complete in the primary repo.

## M-DELIVERY1 authorization

The user explicitly authorized completing public-URL delivery through the notification email.

Active specification:

- `chatgpt/specs/active/20260722_macro_structure_public_mail_delivery.md`

Fixed product route:

```text
local M-ENTRY1 latest.html
→ validate available/unavailable status
→ existing SSH + rsync notification host
→ atomic remote macro-structure/latest.html
→ existing approved notification email receives one public URL block
```

Public URL:

```text
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
```

M-DELIVERY1 reuses existing `NOTIFICATION_HTML_*` hosting configuration. It does not add a hosting service, credential, notification trigger, threshold, schedule, or order path.

## Remaining product gap

- M-DELIVERY1 implementation is complete pending ChatGPT acceptance
- notification email integration is covered by focused no-send tests
- primary-repo implementation is complete pending review
- frozen runtime installation remains prohibited without a separately explicit `RUNTIME_TASK`

## Active plan

```text
M-VIS1 — accepted
→ M-LINE1 — accepted
→ M-EVENT1 — accepted
→ M-HYP1 — accepted
→ M-ENTRY1 — accepted
→ M-DELIVERY1 public URL mail integration — implementation pending ChatGPT acceptance
```

M-STATS1 remains optional and does not block delivery completion.

## Current selected action

- current module: `M-DELIVERY1`
- mode: one bounded Codex implementation
- accepted checkpoint: `475ae4d`
- implementation target: primary repo only
- validation: focused unittest, no-network/no-send smoke, task-scoped `git diff --check`
- excluded: real email send, real SSH/rsync during validation, notification threshold changes, LaunchAgent/schedule changes, frozen runtime access, private/account/order endpoints, automatic order
