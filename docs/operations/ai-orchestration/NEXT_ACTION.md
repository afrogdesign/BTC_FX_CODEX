# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-8`
- mode: `REVIEW_ONLY`
- task_type: `PYTHON SOURCE / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-FIX-7`
- previous_status: `P6 FIX-7 COMMITTED / PUSH NONE`

## Goal

Final ChatGPT P6 acceptance review after unified decision attribution and closed-only actual metrics. P6 remains active; P7 has not started.

Source of truth:

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Reported fix commit:

```text
64b7b56
```

## Fix

### 1. One-to-one classification integrity

Required:
- exactly one classification row per scenario event
- duplicate classification ID or duplicate event assignment with differing content => exit 3
- missing/extra event assignment => exit 2
- operator class must be blank unless `classification_status == classified`
- classifier method must be non-empty
- compare threshold snapshots as canonical finite Decimals
- reject multiple correction rows targeting the same decision event

### 2. Entry metrics must exclude C and STOP

Current behavior still counts observe-only C and STOP outcomes in `resolved_proxy_rows`, positive/negative rows, and `proxy_positive_rate`.

Required:
- entry metrics use `row_role == entry_candidate` only
- C and STOP retain descriptive outcome breakdowns but never enter entry denominators
- later C upgrade requires `classification_status == classified` and class A/B

### 3. Human decision attribution

Implement active spec section 8 fully:
- deterministic earliest eligible scenario-scoped decision
- uniquely attributable signal-only decision
- pre-selection, ambiguous signal-only, and orphan counts
- per-policy decision coverage and action counts
- row-level join status reflects matched/no-match/ambiguous/pre-selection as applicable
- no `manual_note` output

### 4. Actual evidence attribution and metrics

Implement active spec section 9 fully:
- validate non-empty link signal IDs and valid opened/closed timestamps
- only closed, matched episodes with linked high/medium, side match, symbol match, and post-selection open time are eligible for monetary metrics
- one signal mapping to multiple selected scenarios in one policy is ambiguous and excluded
- no episode double-count within one policy
- multiple competing eligible links are ambiguous, not first-row-wins
- C/STOP receive no entry attribution
- populate row net PnL when fee exists
- per-policy high/medium counts, gross, fee coverage, net, win/loss/breakeven, and PF
- PF blank when no losses

### 5. Markdown and regression coverage

Required:
- Markdown prints the computed decision and actual summaries, not only explanatory text
- expand focused synthetic tests for every item above
- add tests for one-to-one classification assignment, class/status consistency, duplicate conflict exit 3, C/STOP denominator exclusion, signal-only decision attribution, decision timing categories, multiple corrections, actual ambiguity/dedup/fee/net/PF, and classified-only C upgrade
- retain deterministic bytes, rollback, compact CLI, and privacy checks

## Allowed read

```text
AGENTS.md
docs/operations/ai-orchestration/NEXT_ACTION.md
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
src/feedback/manual_operator_historical_replay.py
tests/test_manual_operator_historical_replay.py
active spec section 18 reference files as needed
```

## Allowed edit

```text
src/feedback/manual_operator_historical_replay.py
tests/test_manual_operator_historical_replay.py
docs/operations/ai-orchestration/NEXT_ACTION.md
```

`tools/log_feedback.py` only if an actual CLI defect is found.

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
  tests/test_manual_operator_historical_replay.py \
  docs/operations/ai-orchestration/NEXT_ACTION.md \
  tools/log_feedback.py
```

## Completion transition

After validation:

```text
current_work_id: BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-3
mode: REVIEW_ONLY
previous_status: P6 FIX-2 COMMITTED / PUSH NONE
```

Do not archive P6 or start P7.

## Stop / Safety / Git

- stop for branch mismatch, spec contradiction, unavoidable scope expansion, unrelated test failure, or private/generated/raw-data exposure
- no gate/scoring/threshold/notification/runtime/launchd/API/account/order/secret/FORMAL_GO/automatic-order changes
- no frozen runtime repo, raw exchange export, generated output commit, or `paper_positions.csv`
- preserve unrelated dirty changes; no reset, checkout, delete, or stash apply/pop/drop
- stage only task files; push none

## Commit

```text
fix: finish replay attribution metrics
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
