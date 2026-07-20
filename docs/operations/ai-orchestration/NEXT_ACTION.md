# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-OPERATOR-HIERARCHY-RENDER-SHADOW`
- mode: `BOUNDED_CODEX`
- task_type: `M4 LOCAL RENDER-ONLY HIERARCHY SHADOW`
- branch: `Ver04-v2`
- active_spec: `chatgpt/specs/active/20260721_macro_operator_hierarchy_render_shadow.md`
- accepted_m3_head: `3ae30f4`
- accepted_m3_spec: `chatgpt/specs/archive/20260721_macro_next_regime_offline_shadow.md`
- m3_recommendation: `continue_shadow_collection`
- runtime_change: none

## Exact next action

Implement the active M4 specification as one bounded local render task.

M4 must:

- leave production detail HTML and notification/mail behavior unchanged
- join one explicit event-time signal across tactical, macro, level, and M3 artifacts
- render a self-contained chart-first local HTML comparison
- use closed 1-hour public candles for the primary chart
- render 15-minute tactical Entry/SL/TP as a price map without fabricating candles
- show the macro strip and next-regime card before operator-action wording
- exclude all future outcome and replay-resolution fields from the view model and HTML
- publish exactly three deterministic atomic outputs
- add only focused renderer and CLI tests

## Completion posture

After M4 implementation, ChatGPT performs source/artifact acceptance. Only then may a separate M5 active specification be created.

M4 does not authorize live UI deployment, notification change, mail change, runtime reflection, scoring or gate changes, policy promotion, or automatic production mutation.

Future bounded Codex work defaults to `GPT-5.4-mini Medium`.

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no automatic production mutation
- human decides manually
