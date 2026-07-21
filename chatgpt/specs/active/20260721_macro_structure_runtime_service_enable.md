# Macro Structure Runtime Service Enable

## Metadata

- work_id: `BTCFX-20260721-MACRO-STRUCTURE-RUNTIME-SERVICE-ENABLE`
- phase: `M-OPS4`
- mode: `RUNTIME_TASK`
- status: explicitly approved for implementation and installed service activation
- approved_by: human explicit approval on 2026-07-21
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- frozen_runtime_repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- accepted_source_base: `09330b9`
- target_launchd_label: `com.afrog.btc-macro-structure`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Objective

Implement and activate one installed report-only macOS LaunchAgent that automatically executes the accepted macro pipeline:

```text
public 15m / 1h / 4h OHLCV fetch
→ M-OPS1 current snapshot
→ M-OPS2 chronological history
→ M-OPS3 chart-first operator artifact
```

The service must run without recurring human input after setup and must expose one compact atomic runtime result.

This approval authorizes bounded installed runtime and schedule changes for this new target label only. It does not authorize mail, notification, production-policy, private/account/order, or automatic-order behavior.

## 2. Accepted source contracts

Do not change accepted analysis semantics.

- M-OPS1 accepted at `89bd338`: `run-macro-structure-daily`
- M-OPS2 accepted at `dea0e33`: `run-macro-structure-history`
- M-OPS3 accepted at `09330b9`: `render-macro-structure-operator`

The runtime wrapper may call their accepted CLI routes in order and may add only runtime orchestration, public input staging, locking, status, launchd definition, and matching tests.

## 3. Installed target

Preferred installed target is the primary repo:

`/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

Before editing or loading anything, inspect:

- current GUI-domain LaunchAgents matching `com.afrog.btc-*`;
- `~/Library/LaunchAgents` target state;
- whether any existing macro service label exists;
- whether any installed macro path points to the frozen repo;
- primary repo Python, wrapper, permissions, output roots, and existing schedules.

The frozen repo is authorized for read-only inspection in this task only. Do not edit it. Do not copy source into it. The new service must point to the primary repo unless a concrete target constraint makes that impossible; if impossible, stop and report.

Do not alter existing monitor, P8, feedback, review-form, or AI-post-review labels.

## 4. Target schedule

Use one StartCalendarInterval array at these JST times:

- 01:10
- 05:10
- 09:10
- 13:10
- 17:10
- 21:10

This is ten minutes after each UTC-aligned 4-hour candle close.

LaunchAgent contract:

- label: `com.afrog.btc-macro-structure`
- no `RunAtLoad`
- no `KeepAlive`
- WorkingDirectory: primary repo
- Python: primary repo `.venv312/bin/python`
- wrapper: primary repo `tools/run_macro_structure_service.py`
- stdout: `logs/runtime/macro_structure_service.launchd.out`
- stderr: `logs/runtime/macro_structure_service.launchd.err`
- no environment secrets embedded in plist

## 5. Runtime wrapper

Add:

`tools/run_macro_structure_service.py`

Required behavior:

1. Resolve the repo root from the wrapper location.
2. Capture one aware UTC evaluation time, normalized to minute precision.
3. Acquire one non-blocking target-only lock so overlapping service runs cannot execute concurrently.
4. Fetch public MEXC OHLCV exactly once per timeframe for:
   - 15m
   - 1h
   - 4h
5. Use accepted fetch configuration and bounded retries.
6. Stage the three public CSV inputs under a local ignored runtime input area using temporary files and atomic promotion.
7. Invoke accepted CLI routes in this exact order:
   - `run-macro-structure-daily`
   - `run-macro-structure-history`
   - `render-macro-structure-operator`
8. Pass the same staged 15m CSV to M-OPS1 and M-OPS3.
9. Pass the captured evaluation time to M-OPS1.
10. Require compact JSON success from every command.
11. Stop immediately on the first failed step; do not run later steps.
12. Preserve each operation’s previous complete artifacts and latest pointer through its accepted fail-closed behavior.
13. Atomically write:
   `logs/runtime/macro_structure_service_last_result.json`
14. Print one compact privacy-safe JSON result.
15. Return zero only when all three operation steps succeed.

Default roots:

- snapshot: `local/reports/macro_structure/`
- history: `local/reports/macro_structure/history/`
- operator: `local/reports/macro_structure/operator/`
- staged public inputs: `local/runtime/macro_structure_inputs/latest/`

The status must include at minimum:

- schema/method version for the service wrapper;
- status: `success`, `failed`, or `already_running`;
- started/finished UTC and JST;
- evaluation time UTC and JST;
- symbol;
- per-step status and return code;
- selected snapshot run and snapshot ID;
- selected history ID;
- selected operator artifact ID;
- snapshot/history/operator result status;
- stale, continuity, and data-quality status;
- relative artifact locations;
- public input fingerprints;
- error code for the first failed step;
- report-only/private/order safety flags.

Do not include absolute paths, secrets, account data, order data, or raw response bodies in compact status.

## 6. CLI and dry-run

Wrapper arguments:

- `--symbol`, default `BTC_USDT`
- `--ohlcv-limit`, default `500`
- `--dry-run`
- hidden test-only overrides for repo root, Python binary, status path, input root, and output roots where useful

`--dry-run` must:

- perform no public fetch;
- make no artifact or status changes;
- print the planned step commands and target roots;
- return zero.

## 7. Atomicity and failure

Required:

- public inputs are promoted only as one complete three-file set;
- status is written atomically;
- a failed fetch or command does not replace successful prior operation artifacts;
- a failed service run may replace only the compact runtime status with a truthful failed result;
- lock cleanup is guaranteed;
- no retry loop beyond accepted bounded network retries;
- no second service process is launched when the lock is held.

## 8. Repository plist

Add:

`deploy/com.afrog.btc-macro-structure.plist`

Validate with `plutil -lint` and focused tests.

The installed plist must be copied from the committed repository plist. Do not hand-edit a divergent installed copy.

## 9. Installed apply procedure

1. Confirm branch `Ver04-v3` and HEAD `09330b9` before task edits.
2. Preserve expected uncommitted ChatGPT state/spec transitions.
3. Inspect installed target and launchctl GUI domain.
4. Implement wrapper, plist, tests, and documentation.
5. Run focused deterministic validation and wrapper dry-run.
6. Create a local implementation commit before installed replacement.
7. Back up an existing target plist once, if present, under a timestamped directory in `~/Library/LaunchAgents/`.
8. `bootout` only the target label if loaded.
9. Copy only the committed target plist to `~/Library/LaunchAgents/com.afrog.btc-macro-structure.plist`.
10. Run `plutil -lint` on the installed plist.
11. Bootstrap only this target in `gui/$(id -u)`.
12. Verify loaded ProgramArguments, WorkingDirectory, six calendar times, log paths, and absence of RunAtLoad/KeepAlive.
13. Kickstart this target exactly once.
14. Wait only a bounded period for one new runtime status result; do not poll indefinitely.
15. Verify the launchd-triggered run produced successful M-OPS1, M-OPS2, and M-OPS3 latest artifacts in the primary repo.
16. Verify no existing unrelated LaunchAgent changed.
17. On success, archive this spec and update current state to M-OPS4 accepted / M-OPS5 next.

No push is required or authorized.

## 10. Rollback

If bootstrap, kickstart, or target verification fails:

- do not retry repeatedly;
- boot out only the target label;
- restore the target backup if one existed, otherwise remove only the new installed target plist;
- bootstrap the restored target once when applicable;
- preserve repository implementation and diagnostic status;
- do not modify other LaunchAgents;
- report exact rollback state.

## 11. Allowed files

Repository implementation:

- new `tools/run_macro_structure_service.py`
- new `deploy/com.afrog.btc-macro-structure.plist`
- new `tests/test_run_macro_structure_service.py`
- `tests/test_log_feedback.py` only if a genuine accepted CLI invocation regression is found
- this active spec
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/MASTER_PLAN.md`
- `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md`
- one concise runtime deployment/rollback record under `docs/operations/runtime/` when useful

Installed target:

- `~/Library/LaunchAgents/com.afrog.btc-macro-structure.plist`
- one target-only backup directory
- target runtime logs/status and generated `local/` artifacts

Do not edit M1, M-OPS1, M-OPS2, or M-OPS3 source unless a concrete command-breaking defect is demonstrated. If found, stop and report before changing accepted source.

## 12. Focused tests

Cover at minimum:

- exact three-step command order;
- one shared evaluation time;
- one staged 15m input reused by M-OPS1 and M-OPS3;
- one fetch per timeframe;
- complete public input atomic promotion;
- first-step failure stops history/operator;
- second-step failure stops operator;
- third-step failure is reported;
- compact JSON parsing and required IDs;
- success status atomic write;
- failed status atomic write;
- prior operation artifacts are not deleted by wrapper failure;
- dry-run has no fetch/write side effects;
- lock prevents overlap;
- no private/account/order/mail/notification arguments;
- plist label, primary paths, six schedule entries, logs, and no RunAtLoad/KeepAlive.

## 13. Validation budget

Run once:

```text
./.venv312/bin/python -m unittest tests.test_run_macro_structure_service
./.venv312/bin/python -m unittest tests.test_log_feedback.MacroStructureDailyCliTests tests.test_log_feedback.MacroStructureHistoryCliTests tests.test_log_feedback.MacroStructureOperatorCliTests
./.venv312/bin/python tools/run_macro_structure_service.py --dry-run
plutil -lint deploy/com.afrog.btc-macro-structure.plist
git diff --check -- <task files>
```

Runtime acceptance permits exactly one launchd kickstart and one bounded verification of the resulting status/artifacts.

Do not run:

- full test suite;
- M5 or M6;
- broad replay;
- mail or notification send;
- account, position, or order operations;
- automatic order;
- another LaunchAgent restart;
- frozen repo source/test commands.

## 14. Acceptance criteria

M-OPS4 is complete only when:

1. wrapper and plist are committed locally;
2. installed target points to the primary repo;
3. target is loaded in the current GUI domain;
4. all six schedule entries are verified;
5. one launchd-triggered live-public-data run succeeds;
6. fresh complete snapshot, history, and operator artifacts exist;
7. compact runtime status reports success and accepted safety flags;
8. no unrelated service, mail, notification, policy, private endpoint, or order behavior changes;
9. rollback evidence is recorded;
10. current docs identify M-OPS4 as accepted and M-OPS5 as next.

## 15. Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/position/order endpoint
- no mail or notification integration
- no production gate, threshold, scoring, classifier, or policy mutation
- no M6
- no version promotion
