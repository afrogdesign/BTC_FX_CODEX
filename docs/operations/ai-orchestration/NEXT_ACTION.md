# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW`
- mode: `CODEX_EXEC`
- task_type: `M3 OFFLINE NEXT-REGIME CONTRACT`
- branch: `Ver04-v2`
- active_spec: `chatgpt/specs/active/20260721_macro_next_regime_offline_shadow.md`
- accepted_m2_commit: `8aee427`
- accepted_m2_docs_commit: `c2eed44`
- runtime_change: none

## Exact next action

Implement the active M3 specification as one bounded source task.

M3 must:

- keep the existing production Big Chance evaluator unchanged
- create a deterministic offline next-regime replay
- separate tactical side, structural thesis, weakening thesis, activation, next-regime side, invalidation, and reliable target
- use accepted M1/M2 macro artifacts as explicit local inputs
- compare with the existing Big Chance result as a frozen baseline
- fail closed when direction, target, obstruction, schema, or coverage is unresolved
- publish four deterministic atomic outputs
- add only missing focused tests and one bounded offline replay

## Completion posture

After M3 implementation, ChatGPT performs acceptance review and then creates the separate M4 render-only active spec. M3 does not authorize live UI, notification, mail, scoring, gate, threshold, classifier, runtime, API, account, position, or order changes.

Future bounded Codex work defaults to `GPT-5.4-mini Medium`.

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order or automatic production mutation
- human decides manually
