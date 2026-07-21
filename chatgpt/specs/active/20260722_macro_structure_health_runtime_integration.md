# Macro Structure Health Runtime Integration

## Metadata

- work_id: `BTCFX-20260722-MACRO-STRUCTURE-HEALTH-RUNTIME-INTEGRATION`
- phase: `M-OPS6`
- mode: `RUNTIME_TASK`
- status: human approved
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- implementation_base: `dac7e8f`
- installed_label: `com.afrog.btc-macro-structure`
- schedule: existing six JST runs only
- safety: report-only / no private input / no automatic order

## Objective

Connect the completed M-OPS5 health command to the existing M-OPS4 runtime wrapper so every scheduled macro cycle automatically publishes a health artifact after the runtime status is finalized.

Do not add another LaunchAgent, schedule, fetch, mail, notification, or execution path.

## Required behavior

1. Keep the existing M-OPS1 → M-OPS2 → M-OPS3 pipeline unchanged.
2. Atomically write `logs/runtime/macro_structure_service_last_result.json` first.
3. Invoke `check-macro-structure-health` exactly once after the status write for both successful and failed completed cycles.
4. Use the same snapshot/history/operator roots, repository plist, runtime status path, and health output root `local/reports/macro_structure/health/`.
5. Use an explicit health evaluation time not earlier than the runtime finish time.
6. Do not add the health operation to the canonical runtime `steps` list.
7. Do not rewrite the runtime status after health generation.
8. Preserve core exit semantics:
   - core pipeline success remains exit 0 even when health is `healthy_insufficient` or `degraded`;
   - core pipeline failure remains nonzero;
   - health-generation failure must not rewrite a successful core run as failed.
9. Print a compact privacy-safe wrapper result containing a separate `health_generation` summary.
10. Health generation must not fetch data, rerun M-OPS1–3, read private data, or send notifications.

## Health summary

Expose only:

- attempted
- command return code
- health state
- health artifact ID
- report written
- operator HTML path when available
- error code when generation itself fails

Do not expose raw subprocess stdout/stderr or absolute paths.

## Dry run

Dry-run must include the planned health command and retain zero write/fetch side effects.

## Runtime apply

The installed plist content and six-time schedule remain unchanged. After the implementation commit:

1. verify the installed label remains loaded and points to the primary wrapper;
2. do not bootstrap a new service;
3. kickstart the existing target exactly once;
4. wait for one bounded result;
5. require a new runtime status and a new or idempotently valid health artifact derived from that status;
6. verify no unrelated service changed.

If runtime acceptance fails, do not repeat the unchanged kickstart. Preserve the existing loaded service unless the new wrapper is demonstrably unsafe; rollback only the source commit when necessary and report the exact blocker.

## Completion criteria

- focused wrapper tests pass;
- focused health CLI tests pass;
- dry-run shows one health command;
- one launchd-triggered cycle publishes runtime status and health artifact;
- health source fingerprints include the exact runtime status used;
- core success/failure semantics remain unchanged;
- no plist, schedule, mail, notification, private-data, policy, or order change;
- one local implementation commit and one factual state commit when runtime acceptance succeeds.
