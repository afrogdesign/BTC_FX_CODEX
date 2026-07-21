# NEXT_ACTION

- current_work_id: `M-HYP1`
- mode: `BOUNDED_CODEX`
- branch: `Ver04-v4`
- accepted_checkpoint: `a79e488`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_scenarios.md`
- canonical_plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`
- status: implementation complete; M-HYP1 review is next; pending ChatGPT acceptance
- push: none

## Current action

Implement one deterministic current-scenario model on the accepted M-VIS1, M-LINE1, and M-EVENT1 operator.

```text
accepted structural events
+ current horizontal / trendline object IDs
+ current structure and location
→ deterministic candidate families
→ condition
→ next confirmation
→ invalidation
→ conflict suppression
→ maximum three report-only scenarios
```

## Fixed contract

The complete observable contract is in:

- `chatgpt/specs/active/20260722_macro_structure_scenarios.md`

Key fixed decisions:

- retained M-EVENT1 events only
- no new fetch or raw replay
- object-interaction triggers must be within the latest 12 closed 4H bars
- pivot pairs must be within the latest 24 closed 4H bars
- scenario families are limited to:
  - break resolution watch
  - accepted-break continuation
  - failed-break reversal
  - boundary reaction watch
  - pivot-structure continuation
- every scenario must expose:
  - condition
  - next confirmation
  - invalidation
- root break direction is resolved through the retained parent chain
- latest object state suppresses older contradictory scenarios for the same object
- global selection displays only the dominant direction
- maximum three scenarios
- same scenario type is displayed at most once
- insufficient evidence produces no guessed scenario
- probability, win rate, buy/sell, long/short, Entry / SL / TP, and execution wording are prohibited

## User-visible acceptance

- the Scenario hypotheses panel appears after Structural events and before the supplemental 15m section
- every displayed scenario is traceable to valid current object and event IDs
- condition, next confirmation, and invalidation are readable
- pending break is not described as an accepted breakout
- retest direction comes from the root break event
- failed-break evidence overrides older acceptance for the same object
- opposite UP and DOWN continuation claims are not displayed together
- scenarios are bounded to three
- explicit insufficient text appears when current evidence is inadequate
- M-VIS1 zones, M-LINE1 overlays, M-EVENT1 panel/markers, 15m view, and safety boundary remain

## Normal validation budget

- matching unittest
- one small deterministic scenario fixture
- one bounded direct-renderer smoke using existing local inputs
- task-scoped `git diff --check`
- one generated artifact inspection

Do not run full suite, full replay, network fetches, parameter searches, repeated health cycles, runtime/launchd execution, or background processes.

## Explicitly excluded

- probability or historical outcome claims
- M-STATS1
- Elliott Wave or numbered wave interpretation
- Entry / SL / TP or target optimization
- M-ENTRY1 fixed latest entry
- runtime, launchd, schedule, mail, notification, or delivery changes
- existing gate, score, threshold, classifier, zone reliability, pivot semantics, M-LINE1 geometry, or M-EVENT1 threshold changes
- private/account/order data
- automatic order

## Transition

After implementation, ChatGPT reviews only changed source, matching tests, one fresh artifact, scope, and safety. Accept M-HYP1 or request one material FIX. Only after acceptance may M-ENTRY1 become current.
