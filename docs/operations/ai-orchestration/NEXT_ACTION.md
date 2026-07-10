# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-5`
- mode: `REVIEW_ONLY`
- task_type: `PYTHON SOURCE / DIRECT REGRESSION TESTS / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-FIX-3`
- previous_status: `P6 FIX-4 COMMITTED / PUSH NONE`

## Goal

Review the completed P6 attribution and validation fixes and direct regression tests.

P6 remains active. P7 is blocked.

Source of truth:

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Reported FIX-3 commit:

```text
2bae8d2
```

## Non-negotiable acceptance gate

`tests/test_manual_operator_historical_replay.py` must be edited and committed in this task.

The task must not report `done` unless:

- the P6 replay test module contains direct tests for every behavior listed below
- the reported P6 replay test-method count increases from the current 6
- source and tests are staged in the same commit

Changing source without adding these tests is incomplete.

## Confirmed source defects

### 1. Classification and correction integrity

Required fixes:

- `operator_class` must be blank for `insufficient_evidence` and `ambiguous_grouping`
- exact duplicate classification ID with identical normalized content => exit 2
- same classification ID with differing normalized content => exit 3
- duplicate scenario-event assignment with identical normalized content => exit 2
- duplicate scenario-event assignment with differing normalized content => exit 3
- multiple correction rows targeting the same decision event => exit 2

Use explicit grouping/counting. Do not compare a set against another set to detect duplicate correction targets.

### 2. One policy-level decision attribution pass

Remove the current split behavior where replay rows use the old direct-scenario/file-order loop while policy metrics use a separate pass.

Required:

- build one attribution result per policy after selections are fixed
- map scenario-scoped decisions directly
- map signal-only decisions only when the signal maps to exactly one selected scenario in that policy
- sort eligible decisions by `(human_checked_at_utc, decision_event_id)`
- populate replay row fields from that same attribution result:
  - `decision_join_status`
  - `first_effective_human_action`
  - `first_human_checked_at_utc`
- use the same result for policy metrics
- count pre-selection, ambiguous signal-only, and orphan decisions separately
- do not attach those excluded decisions to a replay row
- never expose `manual_note`

### 3. Actual evidence eligibility

Required fixes:

- only `row_role == entry_candidate` may receive actual entry attribution
- C and STOP rows must never receive actual episode IDs or monetary fields
- only a row with `link_status == linked` must have a non-empty signal ID; blank signal IDs on non-linked rows remain valid
- validate every episode open timestamp
- closed episode must have a valid close timestamp at or after open
- matched open episodes may have a descriptive join status but must not populate gross, fee, or net monetary fields
- gross/fee/net monetary fields require:
  - matched association
  - linked high/medium evidence
  - side and symbol match
  - post-selection opening
  - closed episode
  - numeric realized PnL
- row net PnL is `realized_pnl - abs(fee_total)` when fee exists

### 4. Ambiguity and policy-local deduplication

Required:

- multiple eligible links for one replay row => ambiguous and excluded
- one signal mapping to multiple selected scenarios in one policy => ambiguous and excluded
- one episode may contribute monetary evidence at most once within one policy
- choose the deterministic earliest selected replay row for a duplicated episode, ordered by:
  - selected timestamp
  - scenario ID
  - replay row ID
- mark later duplicate episode rows as excluded and clear monetary fields
- the same episode may independently contribute once to each separate policy

### 5. Actual summary shape

Required:

- monetary summaries are per policy in fixed policy order
- do not publish a cross-policy gross/net/win/PF total that adds nested policy views together
- each policy summary includes:
  - `actual_linked_episode_count`
  - `actual_high_confidence_episode_count`
  - `actual_medium_confidence_episode_count`
  - `actual_gross_realized_pnl`
  - `actual_fee_covered_episode_count`
  - `actual_fee_missing_episode_count`
  - `actual_net_pnl_after_fee`
  - `actual_wins`
  - `actual_losses`
  - `actual_breakeven`
  - `actual_profit_factor`
- PF is blank when there are no negative net episodes
- linked open episodes are excluded from these monetary metrics

### 6. Markdown

Keep the computed policy decision and actual summaries now present, but ensure they reflect the corrected row attribution and per-policy actual metrics.

Do not include raw rows, notes, account/order identifiers, local paths, or private values.

## Mandatory direct regression tests

Add direct synthetic tests for all of the following:

1. non-classified row with operator class => exit 2
2. identical duplicate classification ID => exit 2
3. differing duplicate classification ID => exit 3
4. identical duplicate scenario-event assignment => exit 2
5. differing duplicate scenario-event assignment => exit 3
6. multiple corrections targeting one decision => exit 2
7. earliest scenario decision wins regardless of input file order
8. unique signal-only decision populates replay row and policy metrics
9. pre-selection decision is counted but not attached
10. ambiguous signal-only decision is counted but not attached
11. orphan decision is counted but not attached
12. STOP row has no actual attribution
13. C row has no actual attribution
14. non-linked row with blank signal ID is accepted
15. linked row with blank signal ID => exit 2
16. malformed episode open timestamp => exit 2
17. closed timestamp before open => exit 2
18. open episode has no monetary fields and no monetary summary contribution
19. competing eligible links => ambiguous
20. one signal mapped to multiple selected scenarios => ambiguous
21. duplicate episode within one policy contributes once
22. same episode may contribute once in separate policies
23. row net PnL subtracts absolute fee
24. per-policy high/medium/gross/fee/net/win/loss/breakeven/PF values
25. no cross-policy monetary total is emitted
26. Markdown contains the computed decision and per-policy actual summaries

The P6 replay module must have more than 6 test methods after this task. Prefer one focused method per contract area rather than one oversized method.

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

Also report the exact number of test methods in `HistoricalReplayTests` after editing.

## Completion transition

After successful validation:

```text
current_work_id: BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-5
mode: REVIEW_ONLY
previous_status: P6 FIX-4 COMMITTED / PUSH NONE
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
fix: finalize replay attribution tests
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
