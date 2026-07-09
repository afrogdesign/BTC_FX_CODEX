# PHASE4_OPERATOR_V3_RUNTIME_APPLY_20260709

- work_id: `BTCFX-20260709-OPERATOR-V3-STASH-AND-PRODUCTION-APPLY`
- date: `2026-07-09`
- status: `runtime applied`

## Summary

Operator v3 detail layout was implemented and runtime-applied on the Primary repo path.
Legacy/current detail HTML content was preserved below the new operator-facing top area so rollback remains easy with git history and a single revert.

## Deployment Record

- pre_operator_v3_head: `1dd89c9`
- source_commit: `d170959`
- stash_created_for_unrelated_dirty_worktree: `yes`
- stash_name: `pre-operator-v3 unrelated dirty worktree 20260709`
- active_process_path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/main.py`
- runtime_applied: `yes`
- no_send_render_only_smoke: `/private/tmp/btcfx_operator_v3_runtime_smoke.html`

## Safety And Scope

- report-only / not FORMAL_GO / no automatic order / human decides manually
- no scoring changes
- no gate changes
- no threshold changes
- no trading logic changes
- no notification trigger changes
- no launchd plist change
- no real mail/send/trade/API/private/order/secrets activity
- Phase4 tuning remains blocked

## Runtime Result

- The operator v3 top layout is active on the Primary repo runtime path.
- The existing chart rendering path was kept intact.
- Big Chance remains secondary and explicitly says it is not an entry instruction.
- Value Defense wording keeps `浅い反応帯` and `本命防衛帯` separate.
- The unrelated dirty worktree was preserved in stash and was not popped in this task.

## Next Posture

Observe the next natural generated detail HTML for human readability only.
Confirm the new top area is easier to read in practice, does not make long review look prohibited, and does not make Big Chance look like an entry instruction.
