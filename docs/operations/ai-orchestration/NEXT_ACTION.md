# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-SCENARIO-COVERAGE-DECISION-IMPLEMENT`
- mode: `BOUNDED_CODEX`
- task_type: `P4 SOURCE / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-SCENARIO-COVERAGE-DECISION-SPEC-CHECKPOINT`
- previous_status: `P4 ACTIVE SPEC COMMITTED / PUSH NONE`

## Current goal

P4 active specに従い、scenario normalizer、append-only manual decision-event recorder、deterministic scenario coverage reportをreport-only pipelineとして実装する。

Active spec:

```text
chatgpt/specs/active/20260710_manual_scenario_coverage_decision_events.md
```

## Required outputs

```text
logs/csv/manual_scenarios.csv
logs/csv/manual_scenario_events.csv
logs/csv/manual_decision_events.csv
logs/json/manual_scenario_coverage_YYYYMMDD.json
運用資料/reports/post_eval/manual_scenario_coverage_YYYYMMDD.md
```

The pipeline keeps scenario evidence, proxy market-path outcomes, and human decision/action separate. Candidate rows are not independent opportunities and are not human actions.

## Boundaries

- P4 does not implement an A/B/C/STOP classifier.
- no Active Plan, gate, threshold, scoring, notification, mail, runtime, or launchd changes
- no API, secret, private/account/order endpoint, real exchange export, or `paper_positions.csv`
- `no_ohlcv` is coverage failure, never win/loss
- decision events are append-only and do not contain hindsight results

## Validation

```bash
./.venv312/bin/python -m unittest \
  tests.test_manual_scenario_normalizer \
  tests.test_manual_decision_events \
  tests.test_manual_scenario_coverage \
  tests.test_manual_trade_episode_builder \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report \
  tests.test_mexc_actual_trade_importer
```

P4 generated CSV/JSON/Markdown remains local and is not committed. Preserve unrelated dirty and untracked files; do not reset, checkout, stash, or delete them.

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
