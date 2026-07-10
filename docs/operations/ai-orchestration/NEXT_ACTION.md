# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-2`
- mode: `REVIEW_ONLY`
- task_type: `PYTHON SOURCE / CLI / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-IMPLEMENT`
- previous_status: `P6 FIX-1 COMMITTED / PUSH NONE`

## Goal

Review the completed P6 contract fix. P6 remains active. P7 has not started.

Source of truth:

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Reported implementation commit:

```text
6de0391
```

## Fix

### 1. Input and identity integrity

Current gaps:
- classification timestamps are not checked against scenario events
- classified/insufficient/ambiguous status and operator-class consistency is incomplete
- assigned/ambiguous consistency is incomplete
- duplicate classification conflict does not return exit 3
- classifier method/threshold snapshot values are not fully validated
- optional episode/link IDs, references, timestamps, side/symbol compatibility, and monetary Decimals are not fail-closed
- multiple corrections targeting one decision are not rejected

Required behavior:
- implement active spec section 4 exactly
- malformed timestamps/non-finite numerics exit 2
- differing duplicate identities exit 3
- optional actual inputs remain valid when absent

### 2. Policy and proxy metrics

Current gaps:
- C observe-only rows are included in resolved entry-rate denominators
- MFE/MAE count, average, and median are missing
- `qualifying_events_per_selected_scenario` is missing
- `proxy_over_suppression_candidate_rows` is hard-coded to zero
- later C upgrade does not require a valid classified A/B row

Required behavior:
- implement sections 5–7 exactly
- C may retain descriptive outcome distribution but must be excluded from entry metrics
- selected-event outcomes remain primary
- unresolved/no-OHLCV remain outside resolved denominators

### 3. Human decision evidence

Current gaps:
- only direct scenario joins are implemented
- file order, not earliest timestamp, chooses the displayed decision
- signal-only unique attribution, pre-selection, ambiguous, orphan, action counts, and coverage are missing

Required behavior:
- implement section 8 metrics and attribution
- choose earliest eligible effective decision deterministically
- never output `manual_note`

### 4. Actual trade evidence

Current gaps:
- side/symbol compatibility is not enforced
- first matching link is chosen without ambiguity handling
- C rows can receive entry attribution
- closed status, duplicate episode use, fee/net PnL, wins/losses/breakeven, and PF are missing
- `actual_net_pnl_after_fee` is not populated

Required behavior:
- implement section 9 exactly
- exclude low/ambiguous/pre-selection/conflicting/multi-scenario evidence
- no episode double-count within one policy
- fee-missing rows excluded from net/PF
- never fabricate actual R

### 5. Output validation and tests

Current gaps:
- JSON/Markdown existing-output schema checks are marker-only
- Markdown does not report the implemented decision/actual metrics
- new test module has only four broad tests and does not cover the section 20 contract

Required behavior:
- exact existing schema/version validation for all outputs
- keep three-output rollback and deterministic bytes
- add focused synthetic tests covering every required behavior above and the active spec section 20 list
- direct CLI success/error remains compact and privacy-safe

## Allowed read

```text
AGENTS.md
docs/operations/ai-orchestration/NEXT_ACTION.md
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
src/feedback/manual_operator_historical_replay.py
tests/test_manual_operator_historical_replay.py
tools/log_feedback.py
active spec section 18 reference files as needed
```

## Allowed edit

```text
src/feedback/manual_operator_historical_replay.py
tests/test_manual_operator_historical_replay.py
tools/log_feedback.py only if CLI behavior must change
docs/operations/ai-orchestration/NEXT_ACTION.md
```

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
  tools/log_feedback.py \
  docs/operations/ai-orchestration/NEXT_ACTION.md
```

## Completion transition

After validation, set:

```text
current_work_id: BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-2
mode: REVIEW_ONLY
previous_status: P6 FIX-1 COMMITTED / PUSH NONE
```

Do not archive P6 or start P7.

## Stop / Safety / Git

- stop for branch mismatch, spec contradiction, unavoidable scope expansion, unrelated test failure, or private/generated/raw data exposure
- no gate/scoring/threshold/notification/runtime/launchd/API/account/order/secret/FORMAL_GO/automatic-order changes
- no frozen runtime repo, raw exchange export, generated output commit, or `paper_positions.csv`
- preserve unrelated dirty changes; no reset, checkout, delete, or stash apply/pop/drop
- stage only task files; push none

## Commit

```text
fix: complete historical replay contract
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
