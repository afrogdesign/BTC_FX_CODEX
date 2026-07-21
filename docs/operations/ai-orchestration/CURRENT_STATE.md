# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v4`
- accepted M-VIS1 checkpoint: `c1ceda3` (`b0bb3ca` implementation + `c1ceda3` focused CLI assertion)
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

## Visual product state

### M-VIS1 accepted

M-VIS1 is accepted on `Ver04-v4`.

Accepted behavior:

- optional explicit public 4H OHLCV input;
- no extra fetch;
- 4H-first candlestick chart when the 4H input is supplied;
- high / medium horizontal zones with visible `4H`, `1H+4H`, or `1H` source labels;
- role, reliability band, and lifecycle visible on the chart/evidence;
- future or unclosed 4H candles excluded by snapshot cutoff;
- existing 15m view retained as supplemental manual-confirmation view;
- invalid 4H input fails closed without replacing the previous `latest.json`;
- existing no-4H caller behavior remains compatible;
- report-only / no automatic order / human decides manually remain visible.

Accepted review artifact:

- `local/reports/macro_structure/mvis1_review/operator/operator_eea81e0efb24d41261be/macro_structure_operator.html`

Accepted validation:

- focused renderer unittest passed;
- focused CLI parser/dispatch test passed with the repository virtual environment;
- one bounded direct-renderer smoke passed;
- task-scoped `git diff --check` passed.

## Remaining product gap

- deterministic 4H trendlines/channels are not implemented;
- touch, break, retest, reclaim, and structural leg events are not presented as a coherent operator model;
- condition/invalidation scenarios are not implemented;
- a fixed complete latest HTML entry is not yet accepted;
- HTML mail integration remains separate and unauthorized;
- accepted runtime service still uses its existing invocation until a separate runtime task is approved.

## Active plan

```text
M-VIS1 4H-first macro chart — accepted
→ M-LINE1 deterministic trendlines/channels — specification fixed, implementation next
→ M-EVENT1 structural events
→ M-HYP1 bounded condition/invalidation scenarios
→ M-ENTRY1 fixed latest entry
→ separately approved M-DELIVERY1 HTML mail integration
```

M-STATS1 remains optional shadow evidence and does not block product v1 completion when sample size is insufficient.

## M-LINE1 contract state

- active spec: `chatgpt/specs/active/20260722_macro_structure_trendline_channel.md`
- specification status: fixed by ChatGPT
- implementation status: pending ChatGPT acceptance
- confirmed pivot source: existing event-time 4H `confirmed_pivots(..., left=2, right=2)`
- line families: ascending support and descending resistance only
- touch tolerance: `0.25 ATR`
- wrong-side close breach: `0.35 ATR`
- stable IDs, state definitions, ranking, channel construction, display limits, and insufficient behavior are fixed in the active spec

## Current selected action

- next module: `M-LINE1`
- status: ready for one bounded Codex implementation
- objective: add deterministic 4H trendline/channel model and limited overlay to the accepted M-VIS1 artifact
- normal validation budget: matching unittest, small deterministic fixture, one bounded smoke, task-scoped `git diff --check`
- not included: wave labeling, probability, M-EVENT1 event history, M-HYP1 scenarios, runtime, launchd, schedule, mail, notification, policy, gate, threshold, classifier, private data, or automatic order
