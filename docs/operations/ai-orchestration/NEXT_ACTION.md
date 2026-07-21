# NEXT_ACTION

- current_work_id: `M-VIS1`
- mode: `BOUNDED_CODEX`
- branch / HEAD: `Ver04-v4` (accepted base `Ver04-v3`)
- active_spec: none; ChatGPT must first fix the bounded observable contract from the canonical plan and current source
- canonical_plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`
- status: M-VIS1 implementation pending review; do not select M-LINE1 before acceptance
- push: none

## Current action

Implement the first practical user-facing macro visual module only.

```text
existing accepted M-OPS snapshot/history/operator inputs
→ 4H-first candlestick chart
→ accepted high/medium horizontal zones
→ explicit 4H or 1H+4H source labels
→ visible current price, cutoff, evaluation time, health, and report-only boundary
→ immutable complete artifact
→ fail-closed publication
```

## User-visible acceptance

- the operator clearly presents a 4H macro chart as the primary view;
- horizontal zones do not appear to be generated from 15m support/resistance;
- each displayed zone exposes source timeframe, role, reliability band, and lifecycle;
- the artifact uses current accepted public data without extra fetches;
- incomplete generation does not replace a complete existing artifact;
- matching tests pass;
- one small deterministic smoke proves the generated page is usable;
- no automatic order or execution implication is introduced.

## Normal validation budget

- matching unittest
- one small deterministic fixture or smoke
- task-scoped `git diff --check`
- one generated artifact inspection

Do not run full suite, full replay, broad parameter search, repeated health cycles, or long background validation.

## Explicitly excluded

- M-LINE1 trendlines/channels
- M-EVENT1 structural events
- M-HYP1 scenarios
- M-STATS1 statistical evidence
- runtime, launchd, schedule, mail, notification, or delivery changes
- gate, score, threshold, classifier, or reliability-semantic changes
- private/account/order data
- automatic order

## Transition

After M-VIS1 implementation, ChatGPT reviews changed source, matching tests, CLI route, and one fresh artifact through `AFROG_Business_MCP`. Accept M-VIS1 or request one material FIX. Only after acceptance may `M-LINE1` become the selected action.
