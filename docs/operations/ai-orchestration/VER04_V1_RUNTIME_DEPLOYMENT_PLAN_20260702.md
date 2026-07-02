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

## Runtime reflection result

- approved source commit: `c37e46ff948cda664b0ca3641ad922369d16b436`
- runtime branch before: `Ver03-v4`
- runtime branch after: `Ver04-v1`
- runtime HEAD after: `c37e46ff948cda664b0ca3641ad922369d16b436`
- reflection method used: explicit local source path/ref/commit handoff from `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- validation summary: source and runtime read-only status checks passed; `py_compile`, `tests.test_post_eval_surface_smoke`, and `tests.test_active_plan_notification_formatting tests.test_notification_detail_page tests.test_summary_format` passed
- restart/launchd/notification sending: not performed
- notification-operation smoke: can proceed in the next explicit task
- no secrets/private data were recorded

## Notification-operation smoke result

- runtime branch/HEAD checked: `Ver04-v1` / `c37e46ff948cda664b0ca3641ad922369d16b436`
- smoke commands run: `./.venv312/bin/python -m unittest tests.test_summary_format`, `./.venv312/bin/python -m unittest tests.test_notification_detail_page`, `./.venv312/bin/python -m unittest tests.test_active_plan_notification_formatting`, `./.venv312/bin/python -m unittest tests.test_post_eval_surface_smoke`, `./.venv312/bin/python tools/render_notification_no_send_smoke.py --stdout-json`
- documented no-send / dry-run / render-only notification smoke command exists: yes
- validation summary: notification rendering tests passed, report-only / human-decided safety text remained present, and the new no-send/render-only smoke command reported `status=pass` without real mail sending
- restart/launchd: not performed
- controlled restart decision readiness: yes, after runtime reflection and the no-send smoke validation
- no secrets/private data were recorded

## Controlled restart decision result

- runtime branch/HEAD checked: `Ver04-v1` / `c37e46ff948cda664b0ca3641ad922369d16b436`
- no-send smoke result: `pass`
- operation style found: launchd-managed runtime target with safe no-send CLI smoke support
- restart_required: no
- launchd_action_required: no
- real mail sending: not performed
- restart/launchd: not performed
- reason: the runtime is already reflected to the approved commit, the worktree is clean, and the no-send/render-only notification smoke passed; no runtime code, scheduler, or launchd change was introduced in this task
- next task: `BTCFX-20260702-VER04-V1-RUNTIME-ROLLBACK-NOTE`

## Rollback note result

- rollback note path: `docs/operations/ai-orchestration/VER04_V1_RUNTIME_ROLLBACK_NOTE_20260702.md`
- runtime branch/HEAD: `Ver04-v1` / `9c07c0fe75f69c5c849426a9bf64518eba2f54df`
- previous runtime branch/head: `Ver03-v4` / `7a5ccee01bce36cdd2a7be2d16520296e090ba62`
- rollback executed: no
- restart/launchd/mail sending: not performed
- deployment state: reflected Ver04-v1 active, no controlled restart required
- no secrets/private data were recorded

## Deployment complete result

- completion note path: `docs/operations/ai-orchestration/VER04_V1_RUNTIME_DEPLOYMENT_COMPLETE_20260702.md`
- runtime branch/HEAD: `Ver04-v1` / `9c07c0fe75f69c5c849426a9bf64518eba2f54df`
- no-send smoke status: `pass`
- restart/launchd/rollback/mail sending: not performed
- deployment state: complete
- no secrets/private data were recorded
