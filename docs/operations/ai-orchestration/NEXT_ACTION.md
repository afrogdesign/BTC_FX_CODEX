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
