# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-6`
- mode: `REVIEW_ONLY`
- task_type: `PYTHON SOURCE / DIRECT REGRESSION TESTS / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-FIX-4`
- previous_status: `P6 FIX-5 COMMITTED / PUSH NONE`

## Goal

Review the completed P6 policy evidence fix. P6 remains active. P7 has not started.

Source of truth:

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Reported FIX-4 commit:

```text
00fb36a
```

## Confirmed remaining defects

### 1. Duplicate classification assignment semantics

Classification IDs are now handled correctly, but duplicate classification rows referencing the same `scenario_event_id` still return exit 3 unconditionally.

Required:

- group classification rows by `scenario_event_id`
- compare canonical normalized content excluding only `classification_id`
- duplicate assignment with identical normalized content => exit 2
- duplicate assignment with differing normalized content => exit 3
- missing or extra event assignment remains exit 2

### 2. Decision attribution is still split

The replay-row construction still contains the old direct-scenario, input-order loop. The later policy-metrics pass supports signal-only decisions but does not update replay rows.

Required:

- remove the decision loop from initial row construction
- after all policy rows are selected, run one deterministic attribution pass per policy
- scenario-scoped decisions map by scenario ID
- signal-only decisions map only when the signal resolves to exactly one selected scenario in that policy
- sort eligible decisions by:
  - `human_checked_at_utc`
  - `decision_event_id`
- populate replay row fields from this pass:
  - `decision_join_status`
  - `first_effective_human_action`
  - `first_human_checked_at_utc`
- derive policy decision metrics from the same attribution result
- pre-selection, ambiguous signal-only, and orphan decisions remain counts only and are not attached

### 3. Open episodes still populate monetary evidence

Current code populates gross PnL and fee before checking that an episode is closed.

Required:

- a matched open episode may have a descriptive `actual_join_status`
- open episodes must have blank:
  - `actual_gross_realized_pnl`
  - `actual_fee_total`
  - `actual_net_pnl_after_fee`
- open episodes must not contribute to any monetary, win/loss, breakeven, or PF metric
- closed episodes with numeric realized PnL may populate gross
- net/PF require fee coverage

### 4. Policy-local episode dedup must alter rows

Current summary deduplicates episode IDs but later duplicate replay rows retain episode IDs and monetary fields.

Required:

- within each policy, sort candidate actual-attributed rows by:
  - `selected_at_utc`
  - `scenario_id`
  - `replay_row_id`
- retain the first row per episode
- for later rows using the same episode:
  - set `actual_join_status = duplicate_episode_excluded`
  - clear episode ID, confidence, gross, fee, and net fields
- when signal-to-scenario ambiguity is applied, also clear `actual_net_pnl_after_fee`

### 5. Actual summary must be policy-only and use contract names

Current output still publishes cross-policy totals that sum nested policy views, and policy metrics use abbreviated key names.

Required `actual_summary` shape:

```text
policy_summaries:
  CURRENT_STRICT: {...}
  A_ONLY: {...}
  A_PLUS_B: {...}
  A_PLUS_B_PLUS_C_OBSERVE: {...}
  STOP_OVERLAY: {...}
```

Each policy summary must use these exact keys:

```text
actual_linked_episode_count
actual_high_confidence_episode_count
actual_medium_confidence_episode_count
actual_gross_realized_pnl
actual_fee_covered_episode_count
actual_fee_missing_episode_count
actual_net_pnl_after_fee
actual_wins
actual_losses
actual_breakeven
actual_profit_factor
```

Rules:

- no cross-policy gross/net/win/loss/PF total
- STOP and C-only rows contribute zero
- open episodes contribute zero monetary evidence
- fee-missing closed episodes count as linked and gross-covered but not net/PF-covered
- PF blank when there are no negative net episodes

### 6. Direct tests must verify row fields and summary shape

Current tests increased to 12 methods, but several only check aggregate counts and do not verify the claimed row-level behavior.

Add direct tests for:

1. identical duplicate classification assignment with different classification IDs => exit 2
2. differing duplicate classification assignment with different classification IDs => exit 3
3. earliest scenario decision is written to CSV regardless of input order
4. unique signal-only decision is written to CSV and matches policy metrics
5. pre-selection decision leaves CSV row unmatched
6. open episode leaves gross/fee/net CSV fields blank and contributes zero monetary metrics
7. duplicate episode inside one policy clears the later replay row fields
8. signal-to-multiple-scenario ambiguity clears gross, fee, and net
9. `actual_summary` contains only `policy_summaries` for monetary results
10. policy summaries use the exact contract key names
11. fee-missing closed episode contributes gross but not net/PF
12. Markdown reflects the corrected policy-only actual summary

Increase the P6 replay test-method count beyond 12. Source and tests must be in the same commit.

## Allowed read

```text
AGENTS.md
docs/operations/ai-orchestration/NEXT_ACTION.md
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
src/feedback/manual_operator_historical_replay.py
tests/test_manual_operator_historical_replay.py
src/feedback/manual_decision_events.py
src/feedback/manual_trade_episode_builder.py
src/feedback/manual_trade_signal_linker.py
```

## Allowed edit

```text
src/feedback/manual_operator_historical_replay.py
tests/test_manual_operator_historical_replay.py
docs/operations/ai-orchestration/NEXT_ACTION.md
```

`tools/log_feedback.py` only if a concrete CLI regression is found.

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

Report the exact number of test methods in `HistoricalReplayTests`.

## Completion transition

After successful validation:

```text
current_work_id: BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-6
mode: REVIEW_ONLY
previous_status: P6 FIX-5 COMMITTED / PUSH NONE
```

Do not archive P6 or start P7.

## Stop / Safety / Git

- stop for branch mismatch, spec contradiction, unavoidable scope expansion, unrelated test failure, or private/generated/raw-data exposure
- no gate/scoring/threshold/notification/runtime/launchd/API/account/order/secret/FORMAL_GO/automatic-order changes
- no frozen runtime repo, raw exchange exports, generated-output commit, or `paper_positions.csv`
- preserve unrelated dirty changes; no reset, checkout, delete, or stash apply/pop/drop
- stage only task files; push none

## Commit

```text
fix: finalize replay policy evidence
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
