# Side-Aware MTF Runtime Apply

## Metadata

- work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-RUNTIME-APPLY`
- status: human-approved runtime apply
- source_commit: `b805439`
- branch: `Ver04-v2`
- target_label: `com.afrog.btc-monitor`
- runtime_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## Goal

Load the accepted side-aware multi-timeframe operator-action implementation into the existing normal monitor process with one controlled target-only restart.

Future generated detail pages and future CSV rows must use the new source. Existing static HTML and historical CSV rows remain unchanged.

## Accepted source behavior

Pinned 13:05 case:

- Long: `STOP_OR_EXIT`
- Short: `B_CHECK_15M`
- Short lifecycle: `armed`
- primary side: Short
- chase status: `not_late`

Moved 14:05 case:

- Short remains `B_CHECK_15M`
- lifecycle: `late`
- primary side: Short
- visible `追いかけ禁止`

Additional accepted contracts:

- Long and Short evaluated independently
- exact semantic direction matching
- fresh trigger ordering: `follow_through > triggered > late > armed > watch`
- side-specific wait-only degradation
- conditional counter-scalp cannot bypass wait-only
- existing scores, bias, gates, Active Plan, trigger conditions, and mail behavior remain unchanged

## Runtime boundary

Allowed:

- inspect the current target label only
- inspect current branch and HEAD
- run the already accepted targeted unit tests only if a precondition is unclear
- restart `com.afrog.btc-monitor` exactly once with target-only `launchctl kickstart -k`
- verify replacement PID, running state, command path, and bounded runtime error log delta
- archive this spec and append runtime milestone state after successful verification

Not allowed:

- source logic changes
- scoring, market-map, gate, threshold, trigger, or mail changes
- editing or copying plist files
- `tools/start_monitor.sh`
- bootout/bootstrap
- changing launchd schedule or environment
- touching another LaunchAgent
- manual monitor cycle
- manual mail or notification
- regenerating historical HTML
- modifying historical CSV or signal artifacts
- frozen old runtime repo access
- API, account, position, or order endpoints

## Pre-apply checks

Run once:

```bash
git status --short --branch
git rev-parse HEAD
launchctl print "gui/$(id -u)/com.afrog.btc-monitor"
```

Require:

- branch is `Ver04-v2`
- HEAD is `b805439` or a later commit containing it with only expected orchestration-doc changes
- target label is registered
- target process command/path resolves to the primary repo

Record:

- pre-restart PID
- pre-restart `logs/runtime/monitor.err` byte size

If unrelated dirty source overlaps, stop.

## Apply

Execute exactly once:

```bash
launchctl kickstart -k "gui/$(id -u)/com.afrog.btc-monitor"
```

Do not run the start script and do not re-register the plist.

## Verification

After a short bounded wait, verify:

```bash
launchctl print "gui/$(id -u)/com.afrog.btc-monitor"
```

Acceptance:

- state is running
- replacement PID exists and differs from the recorded PID when a prior PID existed
- executable/arguments use the primary repo `.venv312/bin/python` and `main.py`
- no new traceback, exception, fatal, or error attributable to this restart appears in the appended portion of `logs/runtime/monitor.err`
- no manual cycle or manual notification was invoked

Existing static pages are not acceptance evidence. The first naturally generated future detail page is the display acceptance event.

## Documentation after success

- move this spec to `chatgpt/specs/archive/20260712_side_aware_mtf_runtime_apply.md`
- append a concise runtime-apply milestone to `docs/operations/ai-orchestration/CURRENT_STATE.md`
- update `docs/operations/ai-orchestration/NEXT_ACTION.md` to observation posture
- do not update task ledger or handoff

## Commit and push

- create one local docs-only commit after successful runtime verification
- push: none

## Stop conditions

Stop without restart or commit when:

- branch/HEAD does not contain the accepted source
- target label is absent or points outside the primary repo
- unrelated dirty source overlaps
- restart would require plist edit, bootout/bootstrap, another label, or mail behavior change
- runtime error delta contains a new source-related failure
- any private data or secret would enter the diff

## Runtime apply completion

- accepted source commit: `b805439`
- apply timestamp: `2026-07-12` (target-only controlled restart)
- pre-restart PID: `64053`; replacement PID verified at apply time: `82099`
- runtime path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- state: running; future generated HTML and CSV rows use side-aware action output
- historical HTML and CSV artifacts were not regenerated
- no scoring, gate, notification trigger, mail, schedule, API, account, position, or order behavior changed
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually
