# CURRENT_STATE

last_updated: 2026-07-22

## Primary source and macro runtime

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v4`
- accepted core runtime implementation: `bc61478`
- prior factual state commit: `601dfc4`
- macro LaunchAgent: `com.afrog.btc-macro-structure`
- current macro runtime status: `success`
- latest directly reviewed runtime finished: `2026-07-22T08:21:57.814589+00:00`
- latest snapshot: `macro_snapshot_505f74b6ceea0bd149bd`
- latest history: `history_b577253c26a862df59f6`
- latest operator: `operator_9db15ecade825fb21568`
- latest fixed entry ID/status: `c9ec82e7273d289a0df4` / `available`
- 4H fingerprint, chart, trendline, structural-event, and scenario models are present
- public publication and controlled verification email were completed before this task; no new publication or email was performed by the M-STATS1 deployment
- safety: report-only / human-decided / no automatic order
- push: none

## Notification runtime reload

Operational completion remains directly verified for the installed notification monitor.

- active notification repo: primary `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- accepted runtime source: `bc61478`
- frozen source commit `3e75a2f` exists but is not the active execution target
- target: `com.afrog.btc-monitor`; prior target-only reload succeeded
- current startup: `2026-07-22T04:21:58.891682Z`, PID `14203`
- loaded ProgramArguments and WorkingDirectory remain primary
- effective publication enabled: `true`
- fixed entry path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/local/reports/macro_structure/operator/latest.html`
- no notification, email, or public-publication action was performed during the M-STATS1 runtime deployment
- safety: report-only / human-decided / no automatic order
- push: none

## M-STATS1 evaluator

The scenario outcome-count evaluator is accepted.

- initial report locator: `e0e8ed3`
- FIX1 report locator: `68ed430`
- schema/method: `macro_structure_scenario_outcome_stats.v1`
- horizons: 6H / 12H / 24H
- outcomes: continuation / rejection / indeterminate / immature
- repeated `event_id` or `scenario_id` with conflicting payload fails closed across artifacts
- each scenario-type and direction group has independent mature-row count and evidence strength
- fewer than 20 mature rows per group remains `insufficient`; 20 or more is `descriptive_only`
- output is counts only; no probability, win rate, confidence percentage, or execution guidance
- evaluator spec: `chatgpt/specs/archive/20260722_macro_structure_scenario_outcome_stats.md`

## M-STATS1 runtime shadow

M-STATS1 is deployed as a non-blocking local shadow auxiliary of the existing macro service.

- runtime-shadow report locator: `c4d9a4a`
- accepted runtime route: snapshot -> history -> operator -> scenario stats -> health
- core snapshot/history/operator success remains the service success gate
- stats failure does not change a successful core result or suppress health generation
- default output: `local/reports/macro_structure/scenario_stats`
- directly reviewed stats artifact: `ef3dc500f1368a83912e`
- latest pointer is byte-identical to the immutable summary
- source artifact count: `4`
- excluded incompatible/legacy artifacts: `8`
- mature rows: `0`
- evidence strength: `insufficient`
- directly reviewed health artifact: `health_5330bd8fad66b16a07d6`
- health state: `healthy`
- report-only: `true`
- private actual-trade input: `false`
- automatic order allowed: `false`
- no notification, mail, public publication, operator-page integration, plist edit, schedule edit, gate, threshold, score, or classifier change
- one bounded target activation was reported and verified through the resulting runtime status/artifacts; do not repeat live verification
- commit object access is restricted in the safe public workspace; `c4d9a4a` remains a report locator
- runtime-shadow spec: `chatgpt/specs/archive/20260722_macro_structure_scenario_stats_runtime_shadow.md`
- frozen repo was not accessed or activated
- push: none


## 2026-07-23 M-DELIVERY1 runtime publication decoupling acceptance

The fixed macro page publication is accepted as part of the scheduled macro runtime rather than the notification-send branch. This section supersedes older publication-route descriptions above where they conflict.

- implementation report locator: `ae6969e`
- focused FIX1 report locator: `c4d7caf`
- accepted runtime route: snapshot -> history -> operator -> fixed public publication -> scenario stats -> health
- publication runs once after successful operator generation and before scenario stats
- core success remains snapshot/history/operator only
- publication failure or disabled state does not change successful core status or suppress scenario stats or health
- atomic runtime status records bounded `public_delivery_generation` metadata
- notification integration reads the recorded publication result only; it no longer performs SSH, rsync, remote rename, or fixed-entry validation
- notification decision, kind, cooldown, duplicate suppression, subject, recipient, and send count were not changed
- one bounded runtime activation produced entry `113cbd20a4345818f644`
- runtime status: `success`
- publication status: `published`
- local/public entry ID match: confirmed
- fixed public URL: `https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html`
- single HTTPS verification contained the required fixed-entry, safety, and freshness markers
- report-only: `true`
- automatic order allowed: `false`
- no new LaunchAgent, plist change, schedule change, notification reload, SMTP test, or notification cycle
- FIX1 added focused coverage for publication ordering, non-blocking behavior, dry-run isolation, bounded metadata, and runtime-status reader fail-closed behavior
- runtime/public verification was not repeated during FIX1
- accepted spec: `chatgpt/specs/archive/20260723_macro_structure_runtime_publication_decouple.md`
- frozen repo was not accessed
- push: none
