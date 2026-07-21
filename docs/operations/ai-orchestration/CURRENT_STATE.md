# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v4`
- accepted visual checkpoint: `e06fb99`
- push: none
- safety: report-only / human-decided / no automatic order
- canonical visual plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`

## Accepted backend

- P1–P8 accepted
- P9 blocked pending complete private MEXC history input
- M-OPS1 through M-OPS5 accepted on the existing six-time cadence
- accepted runtime, health semantics, source boundaries, and schedule are unchanged

## Accepted visual modules

### M-VIS1

- checkpoint: `c1ceda3`
- 4H-first chart, 1H/4H horizontal zones, supplemental 15m view
- fail-closed 4H input and no-4H compatibility

### M-LINE1

- implementation: `2d47f26`
- ranking fix: `77b9ca3`
- deterministic confirmed-4H trendlines/channels, bounded display, explicit insufficient state

### M-EVENT1

- implementation: `9295005`
- sequence fixes: `0a6f3f8`, `a79e488`
- deterministic event-time approach/touch/rejection/break/acceptance/reclaim/retest/hold/failure and HH/HL/LH/LL
- correct original-side returns, pending windows, rearm, deduplication, and parent-aware 48-event retention
- accepted artifact: `local/reports/macro_structure/mevent1_fix2_review/operator/operator_06dc8eccbd664a8b79d8/macro_structure_operator.html`

### M-HYP1

- implementation: `882ab64`
- input-validation fix: `7a51e98`
- latest-state precedence fix: `e06fb99`
- active spec: `chatgpt/specs/active/20260722_macro_structure_scenarios.md`
- five fixed scenario families
- every scenario has condition, next confirmation, and invalidation
- valid retained event/object references only; malformed vocabulary, parents, timestamps, and contradictions fail closed
- pending break has highest same-timestamp precedence
- maximum three scenarios and one displayed dominant direction
- probability, win rate, buy/sell, long/short, Entry / SL / TP, and execution permission are prohibited
- accepted artifact: `local/reports/macro_structure/mhyp1_review/operator/operator_2ec8b9f90c4524981667/macro_structure_operator.html`

## Remaining product gap

- fixed complete latest HTML entry is implemented and pending ChatGPT acceptance
- runtime integration is unchanged
- HTML mail integration remains separate and unauthorized

## Active plan

```text
M-VIS1 — accepted
→ M-LINE1 — accepted
→ M-EVENT1 — accepted
→ M-HYP1 — accepted
→ M-ENTRY1 fixed latest entry — implementation pending ChatGPT acceptance
→ separately approved M-DELIVERY1
```

M-STATS1 remains optional and does not block visual Product v1 completion.

## M-ENTRY1 contract state

- active spec: `chatgpt/specs/active/20260722_macro_structure_fixed_latest_entry.md`
- specification status: fixed by ChatGPT
- implementation status: pending ChatGPT acceptance
- fixed path: `<output_root>/latest.html`
- default path: `local/reports/macro_structure/operator/latest.html`
- 4H success atomically publishes a complete self-contained available entry
- 4H failure publishes an explicit unavailable entry when possible
- previous success is historical only and is not presented as the current successful result
- no-4H callers do not create or update the fixed entry
- immutable artifact identity and digest remain unchanged

## Current selected action

- next module: `M-ENTRY1`
- mode: one bounded Codex implementation
- normal validation: matching unittest, one bounded direct-renderer smoke, task-scoped diff check
- excluded: runtime, schedule, mail, notification, web server, network fetch, private data, automatic order
