# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-LINKAGE-INPUT-CONTRACT-FIX`
- mode: `BOUNDED_CODEX`
- task_type: `SMALL PYTHON BUG FIX / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-LINKAGE-PIPELINE-FINALIZE`
- previous_status: `IMPLEMENTED / TWO INPUT-CONTRACT DEFECTS REMAIN`

## Current goal

P3 final reviewで確認された2つのinput-contract defectだけを修正する。

1. episode builder `_read_csv()`のexpected-header shadowingによりexact header validationが機能していない
2. v2 ground-truth reportがsignal outcomesの必須`signal_id` headerを検証していない

No redesign and no unrelated refactor.

## Allowed edit

```text
src/feedback/manual_trade_episode_builder.py
src/feedback/manual_trade_ground_truth.py
tests/test_manual_trade_episode_builder.py
tests/test_manual_trade_ground_truth_report.py
docs/operations/ai-orchestration/NEXT_ACTION.md
```

## Required validation

```bash
./.venv312/bin/python -m unittest \
  tests.test_manual_trade_episode_builder \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report \
  tests.test_mexc_actual_trade_importer
```

```bash
git diff --check -- \
  src/feedback/manual_trade_episode_builder.py \
  src/feedback/manual_trade_ground_truth.py \
  tests/test_manual_trade_episode_builder.py \
  tests/test_manual_trade_ground_truth_report.py \
  docs/operations/ai-orchestration/NEXT_ACTION.md
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
