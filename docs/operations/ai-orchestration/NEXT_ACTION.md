# NEXT_ACTION

- current_work_id: `M-EVENT1`
- mode: `BOUNDED_CODEX`
- branch: `Ver04-v4`
- accepted_checkpoint: `77b9ca3`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_structural_events.md`
- canonical_plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`
- status: implementation complete; M-EVENT1 review is next; pending ChatGPT acceptance
- push: none

## Current action

Implement one deterministic 4H structural-event model on the accepted M-VIS1 and M-LINE1 operator.

```text
validated 4H candles
+ displayed high/medium horizontal zones
+ displayed M-LINE1 lines
+ confirmed 4H pivots
→ stable structural event IDs
→ approach / touch / rejection
→ break / acceptance / reclaim
→ retest / hold / failure
→ HH / HL / LH / LL
→ bounded chart markers and event list
```

## Fixed contract

The complete observable contract is in:

- `chatgpt/specs/active/20260722_macro_structure_structural_events.md`

Key fixed decisions:

- closed 4H candles only; no future or unclosed bars
- horizontal object availability starts at `last_confirmed_at`
- line availability starts at line confirmation time
- approach is an ongoing current state
- close-confirmed interactions are confirmed events
- approach `0.75 ATR`
- line touch `0.25 ATR`
- wrong-side break `0.35 ATR`
- clean rejection `0.50 ATR`
- reclaim/failure return `0.10 ATR`
- touch cluster separation 2 bars
- rejection window 2 bars
- reclaim window 3 bars before acceptance
- acceptance requires two consecutive wrong-side closes
- retest window 12 bars
- retest resolution window 2 bars
- stable event IDs and parent relations
- one active break sequence per object
- model retains latest 48 events and chart/list display is bounded
- no events is explicit `insufficient`, not guessed evidence

## User-visible acceptance

- current approach and confirmed events are distinguishable
- touch, break, acceptance, reclaim, retest, hold, and failure are not duplicated
- horizontal zones and trendlines use the same event model while retaining their original IDs
- HH / HL / LH / LL appear only at confirmed pivot time
- chart markers and event list reference the same event IDs
- the operator remains readable and bounded
- M-VIS1 zones, M-LINE1 overlays, 15m supplemental view, and safety boundary remain

## Normal validation budget

- matching unittest
- one small deterministic event-state fixture
- one bounded direct-renderer smoke using existing local inputs
- task-scoped `git diff --check`
- one generated artifact inspection

Do not run full suite, full replay, network fetches, parameter searches, repeated health cycles, runtime/launchd execution, or background processes.

## Explicitly excluded

- Elliott Wave or numbered wave interpretation
- probability or historical outcome claims
- M-HYP1 scenarios
- channel-boundary event generation
- entry / SL / TP
- runtime, launchd, schedule, mail, notification, or delivery changes
- existing gate, score, threshold, classifier, zone reliability, pivot semantics, or M-LINE1 geometry changes
- private/account/order data
- automatic order

## Transition

After implementation, ChatGPT reviews only changed source, matching tests, one fresh artifact, scope, and safety. Accept M-EVENT1 or request one material FIX. Only after acceptance may M-HYP1 become current.
