# Turning Precursor Daily Shadow Runtime Enable — Active Specification

## Metadata

- work_id: `BTCFX-20260712-P8-TURNING-PRECURSOR-SHADOW-RUNTIME-ENABLE`
- status: approved for runtime apply
- approved_by: human explicit approval on 2026-07-12
- phase: P8 evidence collection
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v2`
- target launchd label: `com.afrog.btc-p8-operating-cycle`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## Objective

Enable the already implemented turning / volatility precursor daily shadow stage in the installed 11:30 JST P8 operating-cycle LaunchAgent.

The runtime change is limited to adding this existing opt-in argument:

```text
--include-turning-precursor-shadow
```

The change collects evidence only. It does not alter notifications, mail, scoring, market-map interpretation, trade gates, thresholds, UI, or order behavior.

## Approved runtime change

Update the repository plist and installed LaunchAgent so ProgramArguments become equivalent to:

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor/.venv312/bin/python
/Users/marupro/CODEX/100_MCP_Server/btc_monitor/tools/run_p8_daily_cycle.py
--include-turning-precursor-shadow
```

Keep unchanged:

- label: `com.afrog.btc-p8-operating-cycle`
- WorkingDirectory
- daily schedule: 11:30 JST
- stdout/stderr paths
- no RunAtLoad
- no KeepAlive

## Allowed repository changes

- `deploy/com.afrog.btc-p8-operating-cycle.plist`
- `tests/test_run_p8_daily_cycle.py`
- this active spec, moved to archive after runtime apply
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md`

No source logic change is expected.

## Runtime apply procedure

1. Confirm branch and commit ancestry. Commit `f39375f` must be present.
2. Confirm the installed plist exists at:
   `~/Library/LaunchAgents/com.afrog.btc-p8-operating-cycle.plist`
3. Confirm the loaded label points to the primary repo.
4. Back up the installed plist once under a timestamped `_btc_monitor_backup_20260712` directory.
5. Add the shadow flag to the repository plist exactly once.
6. Update the focused plist contract test.
7. Validate with targeted test, `plutil -lint`, and `git diff --check`.
8. Commit and push before runtime replacement.
9. Boot out only `com.afrog.btc-p8-operating-cycle`.
10. Replace only its installed plist from the committed repository plist.
11. Bootstrap only that label in the current GUI domain.
12. Verify the loaded ProgramArguments, 11:30 schedule, primary repo paths, and log paths.
13. Do not manually start a P8 cycle during this task. The first normal scheduled cycle is the runtime acceptance event.

## Rollback

If bootstrap or verification fails:

- do not retry repeatedly
- restore the one backup plist
- bootstrap the restored plist once
- report rollback state
- do not modify other LaunchAgents

## Validation

```bash
./.venv312/bin/python -m unittest tests.test_run_p8_daily_cycle
plutil -lint deploy/com.afrog.btc-p8-operating-cycle.plist
git diff --check
```

Runtime verification:

- installed plist passes `plutil -lint`
- `launchctl print gui/$(id -u)/com.afrog.btc-p8-operating-cycle` succeeds
- ProgramArguments include `--include-turning-precursor-shadow` exactly once
- ProgramArguments and WorkingDirectory point only to the primary repo
- StartCalendarInterval remains Hour 11 / Minute 30
- no RunAtLoad / KeepAlive is introduced

## Completion and archive condition

Archive this spec after the repository change is committed and pushed, the installed LaunchAgent is reloaded successfully, and the loaded contract is verified.

The next action is a HUMAN_CHECK after the first normal 11:30 JST scheduled cycle. That review must confirm:

- core P8 status success
- turning precursor shadow status success
- no second OHLCV fetch
- no mail or notification behavior change
- date-scoped shadow outputs present

## Prohibited

- no manual notification or mail cycle
- no manual P8 cycle during runtime apply
- no scoring, market-map, gate, threshold, UI, or notification change
- no normal monitor restart
- no other LaunchAgent edit
- no frozen old runtime repo access
- no private/account/order endpoint
- no raw export commit
- no automatic order
