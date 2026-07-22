# Notification Runtime Reload Completion

## Metadata

- work_id: `BTCFX-20260722-VER04-V4-NOTIFICATION-RUNTIME-RELOAD`
- mode: `RUNTIME_TASK`
- status: authorized completion correction
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- frozen_repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- accepted_primary_source: `bc61478`
- accepted_runtime_state_record: `601dfc4`
- safety: report-only / no automatic order / human decides manually

## Audit finding

The previous runtime completion report is not sufficient for normal notification activation.

Evidence:

- repo-owned `deploy/com.afrog.btc-monitor.plist` points to the primary repo;
- runtime `monitor.out` latest startup lines point to the primary repo;
- `logs/runtime/startup_status.json` records `2026-07-13T15:57:07.931511Z` and PID `90160`;
- therefore the long-running primary `main.py` process started before today's M-DELIVERY1 source commits and has not reloaded them;
- the frozen source commit is not the current installed monitor execution source;
- the controlled SMTP verification proves SMTP and formatting, but not that the long-running normal monitor loaded the new integration.

## Objective

Activate the already accepted primary M-DELIVERY1 code in the actual installed `com.afrog.btc-monitor` process with one bounded target-only restart and verify the new process contract without generating a fabricated trading notification.

## Required procedure

1. Inspect the installed `com.afrog.btc-monitor` in `gui/$(id -u)`.
2. Confirm actual ProgramArguments and WorkingDirectory.
3. Stop if it does not point to the primary repo; report the exact safe blocker.
4. Inspect only these non-secret primary config keys without printing `.env`:
   - `NOTIFICATION_HTML_ENABLED`
   - `MACRO_STRUCTURE_FIXED_ENTRY_PATH`
5. Require:
   - `NOTIFICATION_HTML_ENABLED=true`
   - fixed entry path resolves to `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/local/reports/macro_structure/operator/latest.html`
6. If a non-secret key is wrong, update only that key atomically while preserving mode/ownership and all unrelated lines. Do not expose or commit `.env`.
7. Verify current primary fixed entry is available and entry ID matches the latest runtime status.
8. Run the focused no-network/no-send notification integration tests once if no source changed since their accepted pass; do not rerun otherwise without cause.
9. Restart only `com.afrog.btc-monitor` exactly once using target-only launchctl operations.
10. Do not restart the macro service or any other label.
11. Wait a bounded period for a newer `logs/runtime/startup_status.json`.
12. Verify:
    - timestamp is newer than `2026-07-13T15:57:07.931511Z`;
    - PID changed from `90160`;
    - monitor output latest startup path points to the primary repo;
    - loaded ProgramArguments and WorkingDirectory remain primary;
    - target remains loaded/running;
    - `monitor.err` has no new startup failure attributable to this restart.
13. Run one no-send import/runtime-contract check in a separate process using the primary repo that proves:
    - `main.publish_macro_structure_public` is importable;
    - `main.format_macro_structure_email_block` is importable;
    - current config enables publication;
    - current fixed entry validates as available;
    - formatted block contains the fixed public URL exactly once;
    - no SSH, rsync, HTTP, SMTP, Gmail, exchange, or notification decision is invoked.
14. Do not force `run_cycle`, do not alter `should_notify`, and do not send another verification email.
15. Update factual state documents and runtime record only after successful reload verification.

## Rollback

If the one restart fails:

- do not repeat the unchanged restart;
- restore only a changed non-secret config key from a mode-0600 temporary rollback record when applicable;
- keep the target state truthful;
- do not touch other LaunchAgents;
- leave this spec active and report the exact blocker.

## Allowed changes

Primary repo:

- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/runtime/20260722_macro_structure_delivery_completion.md`
- this spec, moved to archive only on success
- `.env` only for atomic non-secret key correction; never stage or commit it

No source change is expected. If a source defect is discovered, stop and report before editing.

Frozen repo:

- read-only confirmation only;
- no additional edit, commit, test, restart, or config change.

## Acceptance

Complete only when the actual installed primary notification process has a new startup timestamp/PID after one target-only restart and the no-send process-level contract check proves the loaded source/config can append the current macro public URL on a future already-approved notification.
