# NEXT_ACTION

- current_work_id: `BTCFX-20260712-P8-TURNING-PRECURSOR-SHADOW-RUNTIME-DIAGNOSE`
- mode: `RUNTIME_DIAGNOSIS`
- task_type: `TARGET-LABEL LAUNCHD REGISTRATION DIAGNOSIS`
- previous_work_id: `BTCFX-20260712-P8-TURNING-PRECURSOR-SHADOW-RUNTIME-ENABLE-RETRY`
- previous_status: `PARTIAL / SOURCE PUSHED / RUNTIME ROLLED BACK`

## Current state

Repository source is pushed through commit `72d1733` and the repository plist contains `--include-turning-precursor-shadow` exactly once.

Installed runtime remains disabled:

- target label: `com.afrog.btc-p8-operating-cycle`
- installed plist restored to original SHA-256: `bfbf6020567ca957a7bb5d204e22cdc61217875f9c7206f8a3a248e62890e0a7`
- installed shadow flag count: 0
- label state: unloaded
- schedule contract: 11:30 JST
- backup preserved at `/Users/marupro/Library/LaunchAgents/_btc_monitor_backup_20260712_turning_shadow/com.afrog.btc-p8-operating-cycle.plist`

The new plist passed unit tests and `plutil`, but `launchctl bootstrap gui/<uid>` returned `Input/output error`. Rollback restored the original plist; no production P8 cycle was run.

## Current exact next action

Perform a bounded read-mostly diagnosis of the target label only.

Collect:

- GUI/user launchd domain availability
- target-label registration state in relevant domains
- exact installed plist ownership, mode, ACL and extended attributes
- executable, working-directory and log-path existence/access
- exact bootstrap stderr and matching launchd unified-log entry
- whether the restored original plist also fails for the same environmental reason

Do not edit source, notification, mail, scoring, gates, schedule, or other LaunchAgents. Do not retry repeatedly. One controlled target-only repair/bootstrap is allowed only when the diagnostic evidence identifies a deterministic safe cause.

## Runtime boundary

- repository flag: enabled in source
- installed runtime flag: disabled
- target label: unloaded
- normal monitor: unchanged
- mail/notification behavior: unchanged
- manual P8 cycle: not run

## Next acceptance event

After a successful target-label load, the first normal 11:30 JST scheduled shadow-enabled cycle is the evidence acceptance event.

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually
# Current next action — 2026-07-12

- mode: `HUMAN_CHECK`
- next task: verify the first normal 11:30 JST shadow-enabled scheduled cycle
- target label: `com.afrog.btc-p8-operating-cycle`
- runtime shadow flag is enabled in the installed target plist; no manual cycle was run
- inspect only compact daily status and date-scoped shadow manifest after the scheduled event
- P9 remains blocked and no live notification proposal is authorized


---

# Current next action — 2026-07-12 side-aware MTF implementation

- current_work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-OPERATOR-ACTION`
- mode: `BOUNDED_CODEX`
- task_type: `SIDE-AWARE OPERATOR ACTION / SOURCE + TEST + DISPLAY`
- active_spec: `chatgpt/specs/active/20260712_side_aware_multi_timeframe_operator_action.md`
- human_approval: received

## Goal

Implement an independent Long/Short operator-action layer that can surface `LONG STOP_OR_EXIT + SHORT B_CHECK_15M` without changing existing scores, formal gates, notification triggers, mail behavior, runtime, or order behavior.

## Pinned acceptance

Signal `20260712_040500` must produce:

- Long: `STOP_OR_EXIT`
- Short: `B_CHECK_15M`
- Short state: `armed`
- primary operator side: `short`
- existing `bias=long`, score `76/12`, and blocked formal gate remain unchanged

The subsequent moved signal must be classified as late/no-chase when at least 70% of entry-to-TP1 distance is already consumed.

## Runtime boundary

- source implementation only
- local targeted validation and local commit
- no push
- no monitor restart
- no launchd change
- no mail/notification behavior change
- scheduled Turning Precursor shadow acceptance remains independent and unchanged

## Implementation completed

- side-aware MTF source implementation is complete and awaiting review/runtime-apply approval
- no runtime apply, monitor restart, notification trigger, mail, score, gate, or order behavior change is authorized by this task
- the first scheduled shadow-enabled P8 cycle remains an independent runtime acceptance event


---

# Current next action — 2026-07-12 side-aware MTF review fix

- current_work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-OPERATOR-ACTION-REVIEW-FIX`
- mode: `BOUNDED_CODEX_FIX`
- active_spec: `chatgpt/specs/active/20260712_side_aware_mtf_operator_action_review_fix.md`
- parent_commit: `2e6cde5`

## Review finding

The pinned 13:05 case is correct, but the bounded 14:05 preview incorrectly promotes `LONG B_CHECK_15M` while the completed Short move is only recorded as `STOP_OR_EXIT / late_no_chase`.

The fix must preserve Short as the primary directional no-chase action in the moved case, distinguish readiness invalidity from directional thesis invalidity, implement zone activation, normalize up/down states, parse JSON-list flags, and enforce side-specific wait-only behavior.

## Boundary

- source/test correction only
- no score, market-map, gate, notification trigger, mail, runtime, launchd, API, or order behavior change
- no runtime apply until review passes
## Side-aware MTF review fix completed

- 13:05 pinned case remains Long STOP / Short B armed / primary Short
- 14:05 moved case remains Short primary with late/no-chase state
- future review should use the archived side-aware review-fix spec; no runtime apply is authorized by this source fix


---

# Current next action — 2026-07-12 side-aware MTF final review fix

- current_work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-TOKEN-NO-CHASE-FIX`
- mode: `BOUNDED_CODEX`
- task_type: `DIRECTION TOKEN SAFETY + NO-CHASE DISPLAY`
- active_spec: `chatgpt/specs/active/20260712_side_aware_mtf_token_and_no_chase_fix.md`
- parent_commits: `2e6cde5`, `eaa4733`

## Review finding

The accepted 13:05 and 14:05 directional previews are preserved, but final source review found an unsafe raw-substring direction matcher: `up` can match inside `support`. The current late candidate headline also does not visibly prohibit chasing.

## Goal

- replace substring direction matching with exact tokens and explicit semantic mappings
- make `late_no_chase` / `tp1_reached_no_chase` visibly say `追いかけ禁止`
- ensure genuine opposite `triggered` / `follow_through` evidence outranks a merely late candidate
- preserve 13:05 Short armed and 14:05 Short late primary acceptance

## Runtime boundary

- source/test/display fix only
- local commit only
- no push
- no runtime restart
- no scoring, gate, trigger, mail, launchd, API, or order change
## Side-aware token/no-chase fix completed

- exact directional token and semantic mapping correction is complete
- late primary action now displays `追いかけ禁止`
- next review remains report-only; no runtime or notification change is authorized


---

# Current next action — 2026-07-12 side-aware MTF final lifecycle fix

- current_work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-TRIGGER-PRIORITY-FINAL-FIX`
- mode: `BOUNDED_CODEX`
- task_type: `FINAL LIFECYCLE / PRIMARY-SELECTION CORRECTION`
- active_spec: `chatgpt/specs/active/20260712_side_aware_mtf_trigger_priority_final_fix.md`

## Review finding

The 13:05 and 14:05 direct previews pass, but source review found that a genuinely fresh opposite trigger can still lose to a merely late candidate when both share the same trigger-strength value. Previous opposite-stop crossing also does not produce `triggered` before late conversion, and true thesis invalidation is computed but not independently included in activation.

## Goal

Complete deterministic fresh-trigger lifecycle, primary ordering, true-thesis invalidation activation, and own-side wait-only degradation while preserving all accepted previews and safety boundaries.

## Runtime boundary

- source and targeted tests only
- no push
- no monitor restart
- no launchd change
- no mail or notification behavior change
- no score, gate, market-map, or order behavior change
## Side-aware trigger priority final fix completed

- fresh trigger lifecycle and primary ordering are corrected
- 13:05 and 14:05 acceptance remains stable
- no runtime apply or production notification change is authorized


---

# Current next action — 2026-07-12 side-aware wait-only / priority final contract fix

- current_work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-WAIT-ONLY-PRIORITY-FIX`
- mode: `BOUNDED_CODEX`
- task_type: `FINAL CONTRACT FIX / SOURCE + TEST`
- active_spec: `chatgpt/specs/active/20260712_side_aware_mtf_wait_only_and_priority_contract_fix.md`
- parent_commit: `75b6413`

## Review finding

The real 13:05 and 14:05 previews pass, but the implementation still violates two approved edge contracts:

- exact side-specific wait-only can be bypassed by zone-only activation or can incorrectly suppress a genuine matching 15M trigger,
- B-candidate state priority still ranks `late` above fresh `triggered` / `follow_through` when trigger strength ties.

## Goal

Correct wait-only degradation/exception behavior and enforce:

```text
follow_through > triggered > late > armed > watch
```

Preserve the accepted real previews and all safety boundaries.

## Runtime boundary

- source/test only
- no push
- no runtime apply
- no monitor restart
- no launchd change
- no mail/notification trigger change
- no score, market-map, gate, API, or order behavior change
## Side-aware wait-only and priority contract completed

- wait-only degradation and fresh-trigger exceptions are finalized
- B primary ordering is finalized and pinned previews remain stable
- no runtime apply or production notification change is authorized
