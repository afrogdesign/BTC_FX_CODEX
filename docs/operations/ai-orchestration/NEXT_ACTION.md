# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT`
- mode: `REVIEW_ONLY`
- task_type: `PYTHON SOURCE / CLI / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-SPEC-CHECKPOINT`
- previous_status: `P6 IMPLEMENTATION COMMITTED / PUSH NONE`

## Goal

Review the completed offline P6 historical replay implementation without changing production behavior.

P6 remains active. P7 has not started.

## Source of truth

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Implement sections 3 through 16 and the test contract in sections 20 through 22.

## Allowed read

```text
AGENTS.md
docs/operations/ai-orchestration/START_HERE.md
docs/operations/ai-orchestration/NEXT_ACTION.md
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
src/feedback/manual_operator_classifier.py
src/feedback/manual_scenario_normalizer.py
src/feedback/manual_decision_events.py
src/feedback/manual_scenario_coverage.py
src/feedback/manual_trade_episode_builder.py
src/feedback/manual_trade_signal_linker.py
src/feedback/manual_trade_ground_truth.py
tools/log_feedback.py
matching targeted tests
```

## Allowed edit

```text
src/feedback/manual_operator_historical_replay.py
tools/log_feedback.py
tests/test_manual_operator_historical_replay.py
docs/operations/ai-orchestration/NEXT_ACTION.md
src/feedback/__init__.py only if required by package convention
```

## Do

- implement event-time, scenario-deduplicated policy selection exactly as specified
- join outcome, human-decision, and actual-trade evidence only after policy selection is fixed
- keep C observation-only and STOP as a separate overlay
- use selected-event proxy outcome for primary metrics
- preserve unresolved/no-OHLCV separation
- implement deterministic CSV/JSON/Markdown and three-output rollback transaction
- add compact CLI command `build-manual-operator-historical-replay`
- use synthetic fixtures only
- after successful validation, transition `NEXT_ACTION.md` to `BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT`; do not archive P6 or start P7

## Validation

```bash
./.venv312/bin/python -m unittest \
  tests.test_manual_operator_historical_replay \
  tests.test_manual_operator_classifier \
  tests.test_manual_scenario_normalizer \
  tests.test_manual_decision_events \
  tests.test_manual_scenario_coverage \
  tests.test_manual_trade_episode_builder \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report \
  tests.test_mexc_actual_trade_importer

git diff --check -- \
  src/feedback/manual_operator_historical_replay.py \
  tools/log_feedback.py \
  tests/test_manual_operator_historical_replay.py \
  docs/operations/ai-orchestration/NEXT_ACTION.md \
  src/feedback/__init__.py
```

## Stop / Safety / Git

- stop for branch mismatch, spec contradiction, unavoidable out-of-scope edit, unrelated test failure, or private/generated/raw data exposure
- do not change gates, scoring, thresholds, notifications, runtime, launchd, APIs, account/order endpoints, secrets, FORMAL_GO, or automatic-order behavior
- do not access the frozen runtime repo, raw exchange exports, or `paper_positions.csv`
- preserve unrelated dirty changes; no reset, checkout, delete, or stash apply/pop/drop
- stage only task files; push none

## Commit

```text
feat: add offline historical replay
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
