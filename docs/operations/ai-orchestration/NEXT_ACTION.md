# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-STRUCTURE-P8-AUXILIARY-SHADOW`
- mode: `CODEX_EXEC`
- task_type: `M2 OPTIONAL P8 AUXILIARY SHADOW IMPLEMENTATION`
- branch: `Ver04-v2` (repo document state; git HEAD must be checked by Codex)
- active_spec: `chatgpt/specs/active/20260721_macro_structure_p8_auxiliary_shadow.md`
- accepted_m1_commit: `663288b`
- archived_m1_spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- parent_plan: `docs/operations/strategy/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md`
- research_basis: `docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- runtime_change: none

## Accepted M1 result

M1 offline macro evidence is accepted after source and focused-test review.

Accepted foundation:

- event-time confirmed 1H/4H levels
- stable level identity and role-aware lifecycle
- prior-only reliability history
- separate volatility state, expansion risk, activation, and target
- same-opportunity baseline comparison
- event-time policy episode deduplication
- independent realized opportunities
- fail-closed missed-move diagnostics
- deterministic atomic five-output replay

Acceptance is for the offline/report-only evidence layer only. It is not a production recommendation or runtime authorization.

## Exact next action

Implement the active M2 specification as one bounded source task.

M2 must:

1. add an explicit `--include-macro-structure-shadow` opt-in flag
2. keep the flag disabled by default
3. reuse the existing validated P8 15-minute OHLCV without a second 15-minute fetch
4. obtain bounded public 1-hour and 4-hour OHLCV through the accepted fetcher only when enabled
5. build a deterministic common-coverage signal slice
6. run the accepted M1 replay rather than duplicate its policies
7. write a complete date-scoped `macro_structure_shadow` subdirectory
8. expose only compact manifest, stdout, and daily-status fields
9. preserve core P8 and turning-shadow outputs when the macro stage fails
10. leave the installed schedule, plist, runtime, notifications, mail, scoring, gates, thresholds, classifiers, and production analysis unchanged

## Validation posture

Use only the targeted tests named by the active M2 spec, one bounded opt-in daily-wrapper run, and `git diff --check`.

Generated OHLCV, signal slices, and replay outputs remain local and uncommitted.

## Completion posture

M2 source completion permits only ChatGPT acceptance review.

It does not automatically permit:

- runtime flag enablement
- M3 implementation
- Big Chance production changes
- UI changes
- notification or mail changes
- scoring, threshold, gate, or classifier changes

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no automatic production mutation
- no API keys, secrets, private/account/position/order endpoints
- human decides manually
