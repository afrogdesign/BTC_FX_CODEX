# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v4`
- accepted visual checkpoint: `77b9ca3`
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
- ranking order: tested → active → broken → insufficient → invalidated
- tested/active candidates cannot be displaced by invalidated/insufficient candidates
- channel base uses the same corrected ranking
- bounded display and explicit insufficient evidence
- M-VIS1 horizontal zones, supplemental 15m view, and safety boundary retained

Accepted validation:

- matching trendline/channel tests passed
- matching operator tests passed
- one bounded direct-renderer smoke passed
- ranking regression tests passed
- task-scoped diff checks passed

## Remaining product gap

- current horizontal and diagonal interactions are not yet represented as one coherent structural-event model
- conditional/invalidation scenarios are not implemented
- fixed complete latest HTML entry is not accepted
- runtime still uses its accepted invocation; no runtime integration has been approved
- HTML mail integration remains separate and unauthorized

## Active plan

```text
M-VIS1 4H-first macro chart — accepted
→ M-LINE1 deterministic trendlines/channels — accepted
→ M-EVENT1 structural events — specification fixed, implementation next
→ M-HYP1 bounded condition/invalidation scenarios
→ M-ENTRY1 fixed latest entry
→ separately approved M-DELIVERY1 HTML mail integration
```

M-STATS1 remains optional shadow evidence and does not block visual product v1 completion.

## M-EVENT1 contract state

- active spec: `chatgpt/specs/active/20260722_macro_structure_structural_events.md`
- specification status: fixed by ChatGPT
- implementation status: implemented; pending ChatGPT acceptance
- inputs: existing validated 4H candles, displayed high/medium horizontal zones, M-LINE1 displayed lines, confirmed 4H pivots
- events: approach, touch, clean rejection, break, closed-candle acceptance, false-break reclaim, retest, retest hold/failure, HH/HL/LH/LL
- event-time, stable IDs, parent relations, deduplication, state-machine windows, retention, display priority, and fail-closed rules are fixed in the active spec

## Current selected action

- next module: `M-EVENT1`
- status: implementation pending ChatGPT acceptance; review is next
- normal validation budget: matching unittest, small deterministic fixture, one bounded smoke, task-scoped `git diff --check`
- not included: probability, scenario generation, runtime, launchd, schedule, mail, notification, gate, score, threshold, classifier, private data, or automatic order
