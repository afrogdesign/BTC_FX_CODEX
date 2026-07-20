# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-STRUCTURE-P8-SHADOW-COLLECTION`
- mode: `OBSERVE`
- task_type: `M2 ACCEPTED / CONTINUE SHADOW COLLECTION`
- branch: `Ver04-v2`
- active_spec: none
- accepted_m2_commit: `8aee427`
- archived_m2_spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- accepted_m1_commit: `663288b`
- archived_m1_spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- runtime_change: none

## Accepted M2 result

The optional, disabled-by-default P8 macro-structure auxiliary shadow is accepted.

Accepted behavior:

- reuse of the core validated 15-minute OHLCV path
- one bounded public 1-hour and 4-hour fetch each when enabled
- context rows used only for event-time episode continuity
- performance-only published events, levels, counts, metrics, splits, dates, diagnostics, gates, and denominators
- complete atomic macro subdirectory publication
- compact consistent manifest, summary, operating-cycle, and daily-status output
- independent core, turning-shadow, and macro-shadow failure handling

Fresh bounded result:

- macro status: `success`
- events: `124`
- levels: `94`
- independent opportunities: `33`
- recommendation: `continue_shadow_collection`

## Exact next action

Continue automatic report-only evidence collection and exception review.

Do not start M3 from this single bounded run. Create a separate M3 active spec only after the accumulated M1/M2 evidence is sufficient for a bounded next-regime contract decision and the human approves that phase.

Future Codex prompts should use the active spec as source of truth, focus only on task-specific deltas, avoid duplicate coverage, and default to `GPT-5.4-mini Medium` for bounded work.

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order or automatic tuning
- no macro-shadow runtime enablement without separate approval
- no notification, mail, production scoring, gate, threshold, classifier, API, account, position, or order change
- human decides manually
