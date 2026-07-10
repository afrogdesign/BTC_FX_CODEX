# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-IMPLEMENT`
- mode: `BOUNDED CODEX IMPLEMENTATION`
- task_type: `PYTHON SOURCE / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-SPEC-CHECKPOINT`
- previous_status: `P5 ACTIVE SPEC CHECKPOINT COMMITTED / PUSH NONE`

## Current goal

active P5 specに従い、event-time offline A/B/C/STOP classifier、deterministic CSV/JSON/Markdown report、compact CLI routeを実装する。

Active spec:

```text
chatgpt/specs/active/20260710_manual_operator_classifier_offline.md
```

## Preferred implementation files

```text
src/feedback/manual_operator_classifier.py
tools/log_feedback.py
tests/test_manual_operator_classifier.py
```

`src/feedback/__init__.py`は既存package convention上必要な場合だけ編集する。

## Validation

```bash
./.venv312/bin/python -m unittest \
  tests.test_manual_operator_classifier \
  tests.test_manual_scenario_normalizer \
  tests.test_manual_decision_events \
  tests.test_manual_scenario_coverage \
  tests.test_manual_trade_episode_builder \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report \
  tests.test_mexc_actual_trade_importer

git diff --check -- \
  src/feedback/manual_operator_classifier.py \
  tools/log_feedback.py \
  tests/test_manual_operator_classifier.py \
  src/feedback/__init__.py
```

## Safety boundaries

- no production gate edit
- no scoring / threshold edit
- no notification edit
- no runtime / launchd edit
- no order / account / private endpoint
- no generated output commit
- no raw exchange export commit
- no `paper_positions.csv` integration
- no frozen runtime repo access

P5 remains offline, report-only, event-time, and separate from production behavior. Do not connect A/B/C/STOP to gates, notifications, runtime, or orders.

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
