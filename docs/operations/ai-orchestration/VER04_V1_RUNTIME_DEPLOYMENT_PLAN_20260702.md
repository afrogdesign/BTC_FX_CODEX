# Ver04-v1 Runtime Deployment Plan 2026-07-02

## Purpose

Bridge the completed Ver04-v1 development repo work into the runtime execution repo in a controlled, report-only, human-decided way.

This document is planning only. It does not access the runtime repo, does not restart anything, and does not send notifications.

## Scope

- source repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- source branch: `Ver04-v1`
- runtime target: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- user has explicitly approved proceeding toward runtime production reflection and notification operation
- no runtime access or execution happens in this plan task

## Mandatory safety boundary

- report-only
- not FORMAL_GO
- no automatic order
- human decides manually
- no API keys or secrets
- no private/account/order endpoints
- no order execution
- no raw/generated/private data commit
- no runtime restart in this plan task
- no launchd modification in this plan task
- no notification sending in this plan task
- no change to trading logic or production thresholds

## Deployment sequence

1. Development checkpoint
   - confirm the source repo state and the completed Ver04-v1 smoke coverage
   - summarize what must carry into runtime without changing behavior

2. Runtime preflight
   - in the future explicit preflight task only, verify target path, branch, remote, and worktree status
   - do not do this now

3. Runtime pull / sync
   - in the future explicit runtime task only, pull the approved Ver04-v1 state into the runtime repo
   - do not do this now

4. Read-only validation
   - in the future explicit runtime task only, run status checks and read-only validation only
   - do not do this now

5. Controlled restart / launchd decision
   - only after preflight and validation, decide whether a restart is needed
   - any restart or launchd action requires a separate explicit runtime task

6. Notification-operation smoke
   - after runtime reflection, verify notification operation behavior remains report-only and human-decided
   - no sending-behavior change is implied by this plan

7. Rollback note
   - keep a rollback note for the exact source commit or sync point used in the future runtime task
   - rollback is a future operational decision, not part of this plan

## Future task sequence

- `BTCFX-20260702-VER04-V1-RUNTIME-PREFLIGHT`
- `BTCFX-20260702-VER04-V1-RUNTIME-REFLECTION`
- `BTCFX-20260702-VER04-V1-NOTIFICATION-OPERATION-SMOKE`
- `BTCFX-20260702-VER04-V1-RUNTIME-ROLLBACK-NOTE`

## Notes

- The runtime path is intentionally separated from the development repo.
- This plan does not mention any execution commands that would touch the runtime repo yet.
- The notification path remains report-only until a later explicit task.

## Runtime preflight result

- checked target path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- `.gitignore` classification: safe_to_commit
- action taken: committed runtime `.gitignore` only with `chore: preserve runtime gitignore state`
- runtime branch before: `Ver03-v4`
- runtime branch after: `Ver03-v4`
- runtime upstream before: not configured
- runtime upstream after: not configured
- runtime worktree before: dirty (`.gitignore`)
- runtime worktree after: clean
- reflection readiness: no
- blocker: runtime target still has no Ver04-v1 branch and no configured upstream, so Ver04-v1 reflection cannot proceed yet

## Preflight-fix review result

- source repo path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- source branch: `Ver04-v1`
- source commit: `c37e46ff948cda664b0ca3641ad922369d16b436`
- runtime branch: `Ver03-v4`
- runtime branch/upstream gap: Ver04-v1 branch is not present locally and no upstream is configured on the runtime target
- runtime worktree: clean after preserving `.gitignore`
- selected reflection method: explicit local source path/ref/commit handoff from `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` at `Ver04-v1` commit `c37e46ff948cda664b0ca3641ad922369d16b436`
- next task boundaries: no fetch/pull/sync/branch switch/restart/launchd/notification sending/API/private endpoint/order execution in this review task
- reflection_ready: yes
- blocker: none for the next explicit reflection task when it uses the recorded source path/ref/commit method
