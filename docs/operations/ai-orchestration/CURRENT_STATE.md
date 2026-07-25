# CURRENT_STATE

last_updated: 2026-07-25

## Canonical P state — 2026-07-25

- branch: `Ver04-v5`
- WP0/WP1 reviewed base HEAD: `34c751fb9f257d188dc1ed2680df90fbe29855d1`
- WP0/WP1 reconciliation implementation commit: `f4966efe2891e87e2a095293721b48bdad0ec091`
- actual input status: `provided`
- actual episodes / links: `149` / `149`
- actual eligible rows: `2`; high-confidence `0`; medium-confidence `2`
- unique actual episodes used: `2`
- resolved / unresolved proxy events: `40` / `4`
- classifier: `manual_operator_classifier.v4`
- Product P9 (`program=P`, `phase=P9`) initial readiness: `false`; practical readiness: `false`
- blocker: evidence volume, side/setup coverage, confidence, and validation window; not actual input absence
- proxy and actual evidence remain separate; no phase promotion, P9 start, FORMAL_GO, or production tuning is approved
- P8 daily health is one cycle's health/lineage; Product P9 cumulative evidence is multi-day/version-consistent proposal eligibility
- Macro `macro_p9_proposal_engine.v1` is `program=M` M5/M6 proposal engine, not Product P9
- safety: report-only / human-decided / no automatic tuning / no automatic order

## Current authorized work

- WP0 and WP1 are accepted.
- `WP2 — Semantic Identity and Versioning` is the sole authorized next package.
- WP2 is report-only/spec-first and defines identity, generation, schema/method version, legacy separation, and comparison boundaries.
- This status authorizes no source behavior, gate, classifier, threshold, scoring, notification, mail, runtime, Product P9, or order change.
- Reviewed-base and implementation-commit records above are historical anchors; no self-invalidating exact current HEAD field is used.

## Primary source and macro runtime

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v5`
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


## Authoritative override — P generation-alignment closure through WP8

last_verified_at: `2026-07-25`
verified_branch: `Ver04-v5`
verified_head: `d43a67db7e8b339316e6a2ffd14144bf362b5aa8`
status_source: `local/reports/p_proposals/wp8_closure_20260725/wp8_closure.json`

This section supersedes earlier P-package status and authorized-work statements in this file where they conflict.

- WP0 through WP8 are accepted.
- WP8 closure commit: `d43a67db7e8b339316e6a2ffd14144bf362b5aa8`.
- WP7 review ID: `wp7_889b730abeac4ead3ae9ea7afb0c0cd9`.
- WP8 closure ID: `wp8_f4eeadd6864d736e7c457490d362ac0b`.
- P9 readiness v2 state: `collecting`.
- WP7 selection status: `no_behavior_proposal_selected`.
- selected proposal: `null`.
- implementation decision: `no_implementation_authorized`.
- adoption decision: `no_adoption_authorized`.
- completion status: `completed_no_approved_proposal`.
- current classifier: `manual_operator_classifier.v4`.
- cumulative classification and proxy-trial cohorts remain `manual_operator_classifier.v1`; current v4 cohorts are missing.
- accepted high/medium actual associations: `58`; descriptive low/ambiguous/no-candidate: `91`; automatic causal claims: `0`.
- no source, gate, classifier, score, threshold, notification, runtime, launchd, mail, canonical-link, schedule, production, FORMAL_GO, or order behavior was changed by WP8.
- the P generation-alignment package is complete through WP8 as a report-only, non-adopted result.
- H2 through H8 and every production/live action remain unauthorized.

## P operational evidence FIX2 acceptance

- implementation commit: `1224a31f1126bdc17564192193e00a8224ee927e`
- acceptance evidence: `local/reports/p_evidence/p_current_generation/latest/`; P8/P9 v2: `local/reports/p8_daily_v2/wp5_wp6_acceptance_20260724_fix2/`
- acceptance source head: `1224a31f1126bdc17564192193e00a8224ee927e`; cycle-derived cutoff: `2026-07-24T02:15:00Z`
- snapshot policy: `latest_accepted_snapshot_as_of_cutoff`; accepted daily directories: `14`
- selected snapshots: classification `907`, proxy-trial `346`; revisions classification `23`, trial `48`; superseded rows `23` / `48`
- cohorts: classification v1/v4 `679/228`; proxy-trial v1/v4 `297/49`
- actual associations `58`; notified accepted actual `58`; not-notified `0`; unknown notification status `0`; human-confirmed usefulness `0`; metadata-complete notified actual `0`
- ambiguous notified actual `54` / rate `0.9310344827586207`; direction match/mismatch/unknown `0/0/58`; Long/Short `25/33`
- formal headline population is selected classification snapshots only: advisory `898`, hard `3`, unknown `0`, mixed `3`, blocker removed `898`, other blockers `896`, potentially pass `2`
- P9 v2 state: `baseline_available`; missing requirements: frozen proposal thresholds and frozen validation cohort; production_ready `false`; proposal approval `not_requested`
- evidence remains descriptive and no-causality: automatic causal claims `0`, `causality_status=not_claimed`, canonical link replacement `false`
- formal gate change remains unapproved; no source, gate, classifier, score, threshold, notification, runtime, launchd, mail, schedule, production, FORMAL_GO, or order behavior changed.
