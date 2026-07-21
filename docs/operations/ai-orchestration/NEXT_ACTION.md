# NEXT_ACTION

- current_work_id: `M-LINE1`
- mode: `BOUNDED_CODEX`
- branch: `Ver04-v4`
- accepted_checkpoint: `c1ceda3`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_trendline_channel.md`
- canonical_plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`
- status: M-LINE1 review is next; implementation pending ChatGPT acceptance
- push: none

## Current action

Implement deterministic 4H trendlines and parallel channels on the accepted M-VIS1 operator.

```text
accepted M-VIS1 4H chart
→ existing confirmed 4H pivots, left=2/right=2
→ ascending support and descending resistance candidates
→ deterministic IDs, state, ranking, and bounded display
→ parallel channel candidates
→ chart overlay and evidence panel
→ matching tests and one bounded smoke
```

## Fixed contract

The complete observable contract is in:

- `chatgpt/specs/active/20260722_macro_structure_trendline_channel.md`

Key fixed decisions:

- only confirmed 4H pivots at or before snapshot cutoff;
- `ascending_support` from higher swing lows;
- `descending_resistance` from lower swing highs;
- anchor gap: 3–120 four-hour bars;
- last 12 pivots per side are searched;
- touch tolerance: `0.25 ATR`;
- wrong-side close breach: `0.35 ATR`;
- `active`, `tested`, `broken`, `invalidated` definitions are fixed;
- stable ID is based only on method, kind, and anchor pivot IDs;
- model retains at most three candidates per kind;
- chart displays at most one live and one recent broken line per kind;
- channels are derived only from the top live base line;
- insufficient evidence produces an explicit status and no guessed line.

## User-visible acceptance

- a small number of important diagonal structures appears on the primary 4H chart;
- each line exposes kind, state, anchors, confirmation time, and touch count;
- no line is shown before both anchors are confirmed;
- same inputs produce the same IDs and geometry;
- broken lines are visually distinct and not described as active support/resistance;
- channels are parallel, deterministic, and within the fixed width range;
- insufficient evidence is stated explicitly;
- M-VIS1 horizontal zones, supplemental 15m chart, and safety boundary remain unchanged.

## Normal validation budget

- matching unittest;
- one small deterministic line/channel fixture;
- one bounded direct-renderer smoke using existing local inputs;
- task-scoped `git diff --check`;
- one generated artifact inspection.

Do not run full suite, full replay, parameter search, network fetches, repeated health cycles, or background processes.

## Explicitly excluded

- M-EVENT1 event history;
- Elliott Wave or numbered wave interpretation;
- probability or historical outcome claims;
- M-HYP1 scenarios;
- runtime, launchd, schedule, mail, notification, or delivery changes;
- horizontal-zone reliability, score, threshold, gate, classifier, or pivot-semantic changes;
- private/account/order data;
- automatic order.

## Transition

After implementation, ChatGPT reviews changed source, matching tests, one fresh artifact, scope, and safety through `AFROG_Business_MCP`. Accept M-LINE1 or request one material FIX. Only after acceptance may M-EVENT1 become current.
