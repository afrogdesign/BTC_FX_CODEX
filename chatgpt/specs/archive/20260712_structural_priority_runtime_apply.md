# Structural Priority Meter Runtime Apply

## Metadata

- work_id: `BTCFX-20260712-P8-STRUCTURAL-PRIORITY-RUNTIME-APPLY`
- status: human-approved runtime application
- accepted_source_commit: `9a32e42`
- target_label: `com.afrog.btc-monitor`
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## Goal

Apply the accepted structural-priority display implementation to the existing normal monitor runtime with one controlled target-only restart.

Future naturally generated detail HTML and CSV rows must use:

- 4H 75% / 1H 25% structural priority in the top meter,
- 45–55 neutral band,
- 10–90 structural point bounds,
- separate turning-watch and alignment context,
- existing tactical Long/Short scores labeled as short-term execution scores,
- existing side-aware 15-minute action, entry zone, SL, TP1, TP2 and no-chase lifecycle.

Historical HTML and CSV rows must not be regenerated.

## Accepted evidence

- numeric audit over 336 recent rows:
  - old/new 0/100 saturation: 41 -> 0
  - old/new p90 step: 47.6 -> 10
  - old/new maximum step: 88 -> 18
  - old/new direction flips: 73 -> 10
- 13:05, 14:05 and 15:05 structural points: Long 47 / Short 53
- qualitative strength and Japanese labels completed
- confirmed turning evidence takes precedence over opposite early evidence
- CSV strength field uses stable lowercase token
- canonical previews attach side-aware action before structural priority
- 14:05 preview visibly contains `追いかけ禁止`
- targeted validation: 59 tests passed

## Runtime boundary

Allowed:

- verify current branch and accepted commit containment,
- inspect the existing target label only,
- perform one `launchctl kickstart -k` for `com.afrog.btc-monitor`,
- verify replacement PID, primary repo paths and bounded error-log delta,
- archive this spec and update milestone/observation docs after success,
- create one local docs-only commit.

Forbidden:

- source edits,
- plist edits, bootout or bootstrap,
- other LaunchAgent operations,
- manual monitor cycle,
- historical report regeneration,
- manual mail or notification,
- scoring, config, market-map, gate, threshold or Active Plan changes,
- API/account/order operations,
- frozen old runtime repo access.

## Acceptance

- branch is `Ver04-v2`,
- HEAD contains accepted source commit `9a32e42`,
- target label is already registered and points only to the primary repo Python and `main.py`,
- one target-only restart succeeds,
- replacement process is running with a new PID,
- bounded `monitor.err` delta has no new Traceback, Exception, fatal or source-related ERROR,
- no manual cycle, mail or notification occurs,
- active spec is archived,
- `CURRENT_STATE.md` records the runtime milestone,
- `NEXT_ACTION.md` returns to observation of the first naturally generated HTML and CSV row,
- one local commit is created,
- no push.
