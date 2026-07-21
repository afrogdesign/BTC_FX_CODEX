# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch / HEAD: `Ver04-v4` (development line; accepted base `Ver04-v3`)
- push: none
- safety: report-only / human-decided / no automatic order
- current product transition: accepted M-OPS analysis backend → practical user-facing macro visual product
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
- current accepted live evidence is report-only, public-data-only, and no-automatic-order
- accepted M-OPS source, health semantics, runtime target, and schedule are not reopened without a concrete contradiction

## Product gap

The backend is operational, but the practical user-facing macro view remains incomplete.

Current limitations:

- the current operator is 15m-first and can make higher-timeframe zones look like 15m support/resistance;
- there is no dedicated 4H-first macro chart;
- deterministic trendlines/channels are not implemented;
- touch, break, retest, reclaim, and structural leg events are not presented as a coherent operator model;
- condition/invalidation scenarios are not implemented;
- a fixed complete latest HTML entry is not yet accepted;
- HTML mail integration remains separate and unauthorized.

## Active plan

The practical visual product will be completed one module at a time:

```text
M-VIS1 4H-first macro chart
→ M-LINE1 deterministic trendlines/channels
→ M-EVENT1 structural events
→ M-HYP1 bounded condition/invalidation scenarios
→ M-ENTRY1 fixed latest entry
→ separately approved M-DELIVERY1 HTML mail integration
```

M-STATS1 remains optional shadow evidence and does not block product v1 completion when sample size is insufficient.

## Current selected action

- next module: `M-VIS1`
- status: M-VIS1 implementation pending ChatGPT acceptance
- objective: generate a practical 4H-first macro chart from existing accepted M-OPS data and clearly label 1H / 4H horizontal zones
- default validation: matching unittest, small deterministic fixture, one bounded smoke, task-scoped `git diff --check`
- not included: M-LINE1, wave labeling, statistical probability, runtime, launchd, schedule, mail, notification, policy, gate, threshold, classifier, private data, or automatic order
