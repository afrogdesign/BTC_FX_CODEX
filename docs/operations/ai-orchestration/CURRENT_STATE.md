# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v4`
- accepted visual checkpoint: `a79e488`
- push: none
- safety: report-only / human-decided / no automatic order
- canonical visual plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`

## Product / P state

- P1–P8 accepted
- P9 remains blocked because no complete private MEXC Trade History / Order History / Position History batch exists under `local/manual_trade_imports/YYYYMMDD/`
- do not repeat P9 importer/linker/readiness work unless new private input, relevant code change, contradictory artifact, or explicit user request appears

## Autonomous macro backend

- M-OPS1 through M-OPS5 are accepted and active on the existing six-time cadence
- installed label: `com.afrog.btc-macro-structure`
- schedule JST: `01:10`, `05:10`, `09:10`, `13:10`, `17:10`, `21:10`
- current pipeline: public 15m / 1h / 4h OHLCV → snapshot → history → operator artifact → runtime status → health artifact
- accepted runtime, health semantics, source boundaries, and schedule are not reopened without a concrete contradiction

## Visual product state

### M-VIS1 accepted

Accepted checkpoint: `c1ceda3`.

- optional explicit public 4H OHLCV input
- 4H-first candlestick view
- visible 4H / 1H+4H horizontal zones
- support/resistance, reliability, lifecycle, cutoff, freshness, and safety visible
- future candles excluded
- invalid input preserves previous latest
- 15m view remains supplemental
- no-4H caller compatibility retained

### M-LINE1 accepted

Accepted implementation: `2d47f26`.
Accepted ranking FIX: `77b9ca3`.
Active specification:

- `chatgpt/specs/active/20260722_macro_structure_trendline_channel.md`

Accepted behavior:

- confirmed 4H pivots only, left=2/right=2
- ascending support and descending resistance only
- stable line/channel IDs and deterministic geometry
- fixed touch and break tolerances
- active, tested, broken, invalidated distinction
- corrected candidate ranking and channel base selection
- bounded display and explicit insufficient evidence
- M-VIS1 horizontal zones, supplemental 15m view, and safety boundary retained

### M-EVENT1 accepted

Accepted implementation: `9295005`.
Accepted sequence fixes: `0a6f3f8`, `a79e488`.
Active specification:

- `chatgpt/specs/active/20260722_macro_structure_structural_events.md`

Accepted behavior:

- one deterministic event model for displayed horizontal zones and trendlines
- event-time-correct approach, touch, clean rejection, break, acceptance, reclaim, retest, hold, and failure
- confirmed HH / HL / LH / LL at pivot confirmation time
- stable event IDs and resolvable parent chains
- original-side reclaim and retest-failure comparisons are correct
- incomplete three-bar break windows remain pending
- unresolved is used only after all three follow-up bars are observed
- a retest bar is not duplicated as ordinary touch/rejection evidence
- parent-aware retention remains at or below 48 events
- list and chart markers use the same displayed event IDs
- explicit insufficient behavior remains valid

Accepted review artifact:

- `local/reports/macro_structure/mevent1_fix2_review/operator/operator_06dc8eccbd664a8b79d8/macro_structure_operator.html`

Accepted validation:

- matching structural-event tests passed
- matching operator tests passed on the implementation checkpoint
- corrected bounded direct-renderer smokes passed
- final artifact contains 39 retained structural events, within the 48-event cap
- task-scoped diff checks passed

## Remaining product gap

- conditional scenarios with explicit confirmation and invalidation are implemented; pending ChatGPT acceptance
- fixed complete latest HTML entry is not accepted
- runtime still uses its accepted invocation; no runtime integration has been approved
- HTML mail integration remains separate and unauthorized

## Active plan

```text
M-VIS1 4H-first macro chart — accepted
→ M-LINE1 deterministic trendlines/channels — accepted
→ M-EVENT1 structural events — accepted
→ M-HYP1 bounded condition/invalidation scenarios — implementation pending ChatGPT acceptance; review is next
→ M-ENTRY1 fixed latest entry
→ separately approved M-DELIVERY1 HTML mail integration
```

M-STATS1 remains optional shadow evidence and does not block visual product v1 completion.

## M-HYP1 contract state

- active spec: `chatgpt/specs/active/20260722_macro_structure_scenarios.md`
- specification status: fixed by ChatGPT
- implementation status: not started
- inputs: accepted M-EVENT1 events, displayed horizontal zones, displayed M-LINE1 lines, current structure/location
- scenario families: break resolution watch, accepted-break continuation, failed-break reversal, boundary reaction watch, pivot-structure continuation
- every scenario must have condition, next confirmation, and invalidation
- maximum three scenarios
- opposite-direction candidates are suppressed from the same view
- probability, win rate, buy/sell, long/short, Entry / SL / TP, and execution permission are prohibited

## Current selected action

- next module: `M-HYP1`
- status: specification fixed; ready for one bounded Codex implementation
- normal validation budget: matching unittest, small deterministic fixture, one bounded smoke, task-scoped `git diff --check`
- not included: probability, historical outcome statistics, fixed latest entry, runtime, launchd, schedule, mail, notification, gate, score, threshold, classifier, private data, or automatic order
