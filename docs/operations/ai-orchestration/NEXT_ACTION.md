# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW-FIX-05`
- mode: `BOUNDED_CODEX`
- task_type: `M3 ELIGIBLE-DATE BURDEN AND VALIDATION-QUALITY CORRECTION`
- branch: `Ver04-v2`
- active_spec: `chatgpt/specs/active/20260721_macro_next_regime_offline_shadow.md`
- m3_implementation_head_before_fix: `3ae30f4`
- m3_recommendation: `continue_shadow_collection`
- preserved_unaccepted_m4_commit: `5574a2e`
- preserved_inactive_m4_draft: `chatgpt/specs/archive/20260721_macro_operator_hierarchy_render_shadow_draft.md`
- runtime_change: none

## Exact next action

Correct M3 burden denominators and validation-period data-quality coverage, run one fresh bounded replay, and obtain ChatGPT M3 acceptance.

Required posture:

- overall candidate and baseline burden use the same all-eligible-event JST-date denominator
- validation candidate and baseline burden use the same validation-date denominator, including zero-episode dates
- split burden uses the same split-specific eligible-event date denominator for both policies
- validation data-quality checks include eligible events with no episode
- candidate policy, baseline behavior, episode identity, thresholds, CLI contract, production behavior, and runtime remain unchanged

## Completion posture

M4 commit `5574a2e` is preserved but unaccepted. M4 FIX-01 may begin only after M3 FIX-05 acceptance. M5 is blocked.

Future bounded Codex work defaults to `GPT-5.4-mini Medium`.

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no automatic production mutation
- human decides manually
