# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-SCENARIO-COVERAGE-DECISION-FINAL-FIX`
- mode: `BOUNDED_CODEX`
- task_type: `P4 FINAL SOURCE FIX / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-SCENARIO-COVERAGE-DECISION-CORRECT`
- previous_status: `MOST CORRECTIONS COMPLETE / FINAL SOURCE-REVIEW DEFECTS REMAIN / PUSH NONE`

## MCP書き込み時の再構成ルール

ChatGPT がこのファイルを MCP 経由で更新するときは、現在のファイル内容を再読込し、今回必要な差分だけを加えて送信データを作り直す。

- 拒否された過去の下書きは再利用しない
- 他の source / test ファイルにある具体的な値を orchestration 文書へ転記しない
- 機微情報に見える値は具体値を使わず、一般化した説明に置き換える
- 更新対象外の文書内容を混ぜない
- 確認画面が出た場合は、その送信を中止し、対象ファイルを再読込して小さい差分として一度だけ作り直す

## Current goal

Apply the final P4 corrections defined in:

```text
chatgpt/specs/active/20260710_manual_scenario_coverage_decision_events.md
```

Controlling section:

```text
## 25. Final source-review corrections — 2026-07-10
```

## Required final fixes

- covered OHLCV evidence must not be counted as missing coverage
- resolved proxy outcomes require valid first-exit time
- existing correction chains fail closed
- duplicate or malformed scenario evidence fails closed in the decision recorder
- pair-write rollback tests are present
- CLI subprocess success and error tests are present
- local duplicate/unused imports are removed where behavior-neutral

## Allowed edit

```text
src/feedback/manual_scenario_normalizer.py
src/feedback/manual_decision_events.py
src/feedback/manual_scenario_coverage.py
tools/log_feedback.py
tests/test_manual_scenario_normalizer.py
tests/test_manual_decision_events.py
tests/test_manual_scenario_coverage.py
chatgpt/specs/active/20260710_manual_scenario_coverage_decision_events.md
docs/operations/ai-orchestration/NEXT_ACTION.md
```

## Important unrelated file

`docs/operations/ai-orchestration/START_HERE.md` は Tier 0 として読む。今回の task では編集・stage・commit しない。

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

```bash
git diff --check -- \
  src/feedback/manual_scenario_normalizer.py \
  src/feedback/manual_decision_events.py \
  src/feedback/manual_scenario_coverage.py \
  tools/log_feedback.py \
  tests/test_manual_scenario_normalizer.py \
  tests/test_manual_decision_events.py \
  tests/test_manual_scenario_coverage.py \
  chatgpt/specs/active/20260710_manual_scenario_coverage_decision_events.md \
  docs/operations/ai-orchestration/NEXT_ACTION.md
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
