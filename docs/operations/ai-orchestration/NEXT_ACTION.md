# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-4`
- mode: `REVIEW_ONLY`
- task_type: `PYTHON SOURCE / TARGETED TEST / COMMIT`
- previous_work_id: `BTCFX-20260710-MTP-HISTORICAL-REPLAY-FIX-2`
- previous_status: `P6 FIX-3 COMMITTED / PUSH NONE`

## Goal

Review the completed P6 evidence attribution fix. P6 remains active. P7 has not started.

Source of truth:

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

Reported FIX-2 commit:

```text
f301ad3
```

## Confirmed remaining gaps

### 1. Classification and correction integrity

- duplicate `classification_id` still exits 2 unconditionally; differing normalized duplicate content must exit 3
- non-classified rows may still carry an operator class; they must not
- multiple correction rows targeting one decision are still accepted because the current set comparison cannot detect duplicates

Required:
- exact duplicate classification ID with identical normalized content: reject as non-unique input, exit 2
- same classification ID with differing normalized content: identity conflict, exit 3
- duplicate scenario-event assignment: exit 3 when differing content; otherwise exit 2
- `operator_class` blank unless status is `classified`
- reject more than one correction targeting the same decision event

### 2. Row-level decision attribution

The current per-policy metrics pass does not update replay rows. Row display still uses the earlier direct-scenario, file-order loop and does not support signal-only attribution.

Required:
- build attribution once per policy before serializing rows and metrics
- choose the earliest eligible effective decision by `(human_checked_at_utc, decision_event_id)`
- support scenario-scoped and uniquely attributable signal-only decisions
- row-level `decision_join_status`, action, and checked-at must match the same attribution used by policy metrics
- represent no-match, pre-selection, ambiguous-signal-only, and orphan evidence in counts without attaching it as a matched row
- never expose `manual_note`

### 3. Actual attribution and per-policy metrics

Current gaps:
- STOP rows can still receive actual attribution
- empty link signal IDs and malformed episode open timestamps are not rejected
- matched open episodes can populate monetary row fields
- episode deduplication within one policy is missing
- summary is global across all policy rows, so the same episode is multiplied across nested policies
- row `actual_net_pnl_after_fee` remains blank
- per-policy actual summaries are missing

Required:
- actual entry attribution only for `row_role == entry_candidate`
- validate non-empty linked signal IDs and valid episode open timestamps; closed episodes require valid close timestamp not before open
- row-level link status may describe eligible linked evidence, but gross/fee/net monetary fields require a closed episode with numeric realized PnL
- prevent one episode from contributing more than once within one policy
- retain the same episode independently in separate policy summaries, but never sum nested-policy rows into one misleading global monetary total
- provide actual metrics per policy in fixed policy order
- populate row net PnL as `realized_pnl - abs(fee_total)` when fee exists
- per-policy counts: linked, high, medium, fee-covered, fee-missing, wins, losses, breakeven, gross, net, PF
- PF blank when no negative net episodes

### 4. Markdown output

Current Markdown still contains explanatory text only for human and actual evidence.

Required:
- print deterministic policy decision summaries
- print deterministic policy actual summaries
- retain all required safety and limitation statements
- do not print raw rows, notes, identifiers, or private values

### 5. Required regression tests

The P6 test module still contains only six test methods and does not exercise the FIX-2 claims.

Add focused synthetic tests for at least:
- differing duplicate classification ID => exit 3
- identical duplicate ID/non-unique assignment => exit 2
- non-classified row with operator class => exit 2
- multiple corrections targeting one event => exit 2
- earliest decision chosen regardless of file order
- unique signal-only decision joins row and metrics
- ambiguous signal-only, pre-selection, and orphan counts
- STOP receives no actual attribution
- empty link signal ID and malformed episode timestamps => exit 2
- open episode excluded from monetary fields
- competing links => ambiguous
- one signal mapped to multiple scenarios => ambiguous
- same episode deduplicated within one policy
- per-policy high/medium, gross, fee, net, win/loss/breakeven, PF
- row-level net PnL
- Markdown contains computed decision and actual summaries

Do not satisfy this task by changing only existing assertions. The new behaviors must have direct tests.

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

`tools/log_feedback.py` only if an actual CLI regression is found.

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
current_work_id: BTCFX-20260710-MTP-HISTORICAL-REPLAY-REVIEW-CHECKPOINT-4
mode: REVIEW_ONLY
previous_status: P6 FIX-3 COMMITTED / PUSH NONE
```

Do not archive P6 or start P7.

## Stop / Safety / Git

- stop for branch mismatch, spec contradiction, unavoidable scope expansion, unrelated test failure, or private/generated/raw-data exposure
- no gate/scoring/threshold/notification/runtime/launchd/API/account/order/secret/FORMAL_GO/automatic-order changes
- no frozen runtime repo, raw exchange exports, generated output commit, or `paper_positions.csv`
- preserve unrelated dirty changes; no reset, checkout, delete, or stash apply/pop/drop
- stage only task files; push none

## Commit

```text
fix: complete replay evidence attribution
```

## Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```
