# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-SCENARIO-COVERAGE-DECISION-SPEC-CHECKPOINT`
- mode: `DOCS-ONLY / CODEX CHECKPOINT`
- task_type: `SPEC VALIDATION / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-LINKAGE-DEAD-CODE-CLEANUP`
- previous_status: `P3 COMPLETE / REVIEWED / LOCAL COMMITS REPORTED / PUSH NONE`

## Current goal

P3を完了・archiveし、P4のscenario identity、OHLCV coverage、manual decision-event schemaをactive specとして確定する。

Archived P3 spec:

```text
chatgpt/specs/archive/20260710_manual_trade_linkage_ground_truth_pipeline.md
```

Active P4 spec:

```text
chatgpt/specs/active/20260710_manual_scenario_coverage_decision_events.md
```

## P4 design decision

P4は次の3層を分離する。

```text
scenario evidence
proxy market-path outcome
human decision/action
```

P4 does not implement A/B/C/STOP classification, notification changes, gate changes, or runtime changes.

Core outputs:

```text
logs/csv/manual_scenarios.csv
logs/csv/manual_scenario_events.csv
logs/csv/manual_decision_events.csv
運用資料/reports/post_eval/manual_scenario_coverage_YYYYMMDD.md
logs/json/manual_scenario_coverage_YYYYMMDD.json
```

## Required checkpoint validation

- P3 active spec absent
- P3 archive exists
- P4 active spec exists
- active spec defines deterministic scenario identity
- ambiguous grouping has no hidden tie-break
- no_ohlcv is coverage failure, not win/loss
- human decision events do not contain hindsight result fields
- P4 explicitly blocks classifier, gate, notification, and runtime work
- docs-only `git diff --check` passes

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```

## Next after checkpoint

After the checkpoint commit, implement P4 as one bounded theme:

```text
scenario normalizer
+ decision-event recorder
+ coverage report
```

No production behavior change.
