# P6 Manual Operator Historical Replay — Offline Specification

## Metadata

- phase: P6
- status: active specification
- work family: manual trading practicality
- implementation mode: report-only / offline / local generated outputs
- preceding accepted phase: P5 offline A/B/C/STOP classifier
- accepted P5 implementation reviewed through reported commit: `57d6151`
- safety: not FORMAL_GO / no automatic order / human decides manually

## 1. Purpose

Build a deterministic historical replay that compares the current strict formal path with the P5 operator hypotheses without changing production behavior.

Required policy views:

```text
CURRENT_STRICT
A_ONLY
A_PLUS_B
A_PLUS_B_PLUS_C_OBSERVE
```

The replay must answer:

- how many independent scenarios each policy would surface
- how many repeated event rows are compressed by first-scenario selection
- how proxy outcomes differ by policy
- how long, short, regime, and setup family differ
- where B adds resolved proxy opportunities beyond the strict baseline
- where C provides earlier observation before a later A/B upgrade
- how STOP events overlap with later proxy outcomes
- what optional human-decision and actual-trade evidence is available

The replay is descriptive evidence only.

It must not:

- change any production gate or threshold
- change notification behavior
- imply that every selected row would have been mailed
- treat C as an entry permission
- convert STOP into an automatic close instruction
- declare profitability from unresolved or low-confidence evidence
- declare FORMAL_GO
- write or plan an order

## 2. Core design decisions

### 2.1 Event-time selection, future-only evaluation

Policy selection uses only P5 classification evidence available at each scenario event timestamp.

Outcomes, later classifications, human decisions, and actual trades may be joined only after the policy selection event has been fixed.

Never select an event because its later outcome was favorable.

### 2.2 Scenario-level replay unit

The primary replay unit is one selected event per independent scenario per policy.

Candidate rows and classification rows are not independent opportunities.

For each policy, select the earliest qualifying assigned event in a scenario using:

```text
event_timestamp_utc
scenario_event_id
classification_id
```

A scenario may appear once in each policy because the policies are separate counterfactual views.

### 2.3 Event-specific proxy outcome

Primary proxy metrics use the P4 outcome fields belonging to the selected `scenario_event_id`.

Do not substitute the outcome of a later candidate update for the selected event.

Scenario-final lifecycle and proxy outcome may be reported as secondary context only and must not overwrite the selected-event outcome.

### 2.4 Nested policies are compared independently

`A_ONLY` is a subset hypothesis of `A_PLUS_B`.

`A_PLUS_B_PLUS_C_OBSERVE` adds observation coverage. A C selection is never counted as a hypothetical entry.

The same actual episode may appear in multiple policy summaries when independently attributable to each policy. Counts must not be summed across policies as though they were disjoint.

## 3. Required input files

All paths are explicit CLI arguments. Do not silently select historical filenames.

### 3.1 P4 scenario summary

Argument:

```text
--scenarios
```

Schema:

```text
manual_scenario.v1
```

Required exact header:

```text
src.feedback.manual_scenario_normalizer.SCENARIO_HEADERS
```

Use for:

- scenario identity validation
- side, setup family, and final lifecycle context
- secondary scenario-final outcome context only

### 3.2 P4 scenario events

Argument:

```text
--scenario-events
```

Schema:

```text
manual_scenario_event.v1
```

Required exact header:

```text
src.feedback.manual_scenario_normalizer.EVENT_HEADERS
```

Use for:

- selected event timestamp
- selected-event entry plan
- selected-event proxy outcome
- selected-event MFE / MAE
- OHLCV coverage and gap reason

### 3.3 P5 classifications

Argument:

```text
--classifications
```

Schema:

```text
manual_operator_classification.v1
```

Required exact header:

```text
src.feedback.manual_operator_classifier.OUTPUT_HEADERS
```

Use for policy selection only.

All rows in one run must use one:

- classifier method version
- threshold snapshot

Mixed method versions or mixed threshold snapshots are invalid input, exit `2`.

### 3.4 Optional human decision events

Argument:

```text
--decision-events
```

Schema:

```text
manual_decision_event.v1
```

Required exact header:

```text
src.feedback.manual_decision_events.DECISION_HEADERS
```

If omitted, the replay remains valid and reports decision input as absent.

Effective decision semantics:

- a row referenced by `supersedes_decision_event_id` is superseded
- the unsuperseded correction row is effective
- unsuperseded active rows are effective
- malformed correction graphs are invalid input, exit `2`

Do not include `manual_note` text in replay outputs.

### 3.5 Optional actual trade episodes and links

Arguments must be supplied together:

```text
--trade-episodes
--episode-links
```

Schemas:

```text
manual_trade_episode.v1
manual_trade_signal_link.v2
```

Required exact headers:

```text
src.feedback.manual_trade_episode_builder.EPISODE_HEADERS
src.feedback.manual_trade_signal_linker.LINK_HEADERS
```

If one is supplied without the other, exit `2`.

Raw exchange exports are not P6 inputs.

## 4. Referential integrity

### 4.1 Scenario and event integrity

Require:

- non-empty unique `scenario_id`
- non-empty unique `scenario_event_id`
- non-empty unique candidate reference per event
- assigned events reference a known scenario
- ambiguous events have blank scenario ID
- scenario/event schema versions match

Violations exit `2`.

### 4.2 Classification integrity

Require exactly one classification row per scenario event.

Classification and event values must agree for:

```text
scenario_event_id
scenario_id
candidate_id
source_signal_id
event_timestamp_utc
event_timestamp_jst
symbol
side
setup_family
```

Require:

- unique non-empty `classification_id`
- known classification status
- operator class blank unless status is `classified`
- assigned event is not marked `ambiguous_grouping`
- ambiguous event is marked `ambiguous_grouping`
- assigned classified rows use only P5 classes

Missing classification rows, extra unknown references, or mismatched identity fields exit `2`.

Duplicate classification ID with differing normalized content is identity conflict, exit `3`.

### 4.3 Optional actual evidence integrity

Require:

- unique non-empty episode IDs
- unique non-empty link IDs
- link episode reference exists
- linked row signal ID is non-empty
- closed episodes have a close timestamp
- non-empty monetary fields are finite Decimals

Identity conflict exits `3`; schema or reference failures exit `2`.

## 5. Replay policies

Fixed policy order:

```text
CURRENT_STRICT
A_ONLY
A_PLUS_B
A_PLUS_B_PLUS_C_OBSERVE
STOP_OVERLAY
```

`STOP_OVERLAY` is a separate analysis layer, not an entry policy.

### 5.1 CURRENT_STRICT

Qualifying event:

```text
classification_status == classified
trade_execution_gate == pass
operator_class != STOP_OR_EXIT
```

This is a replay of the strict formal gate evidence retained by P5.

Count but do not select inconsistent strict-pass rows where:

- operator class is STOP
- classification is insufficient
- classification is ambiguous

Metric:

```text
strict_pass_inconsistent_rows
```

### 5.2 A_ONLY

Qualifying event:

```text
classification_status == classified
operator_class == A_FORMAL
```

Row role:

```text
entry_candidate
```

### 5.3 A_PLUS_B

Qualifying event:

```text
classification_status == classified
operator_class in A_FORMAL, B_CHECK_15M
```

Row role:

```text
entry_candidate
```

### 5.4 A_PLUS_B_PLUS_C_OBSERVE

Qualifying event:

```text
classification_status == classified
operator_class in A_FORMAL, B_CHECK_15M, C_WATCH_ZONE
```

Row role:

```text
A_FORMAL or B_CHECK_15M -> entry_candidate
C_WATCH_ZONE -> observe_only
```

C rows are excluded from entry win-rate, PF, and actual-entry attribution denominators.

For a selected C event, evaluate later classification events in the same scenario only after selection to report:

```text
later_upgrade_class
later_upgrade_at_utc
upgrade_latency_minutes
```

The first later A or B event is used. No later upgrade is blank.

### 5.5 STOP_OVERLAY

Select the earliest assigned event per scenario where:

```text
classification_status == classified
operator_class == STOP_OR_EXIT
```

Row role:

```text
stop_overlay
```

STOP rows are never included in entry-policy denominators.

## 6. Outcome normalization

Primary outcome comes from the selected P4 event.

Normalized outcome statuses:

```text
resolved_positive
resolved_negative
entry_reached_unresolved
not_entered
expired
coverage_missing
pending
ambiguous
unknown
```

Mapping:

```text
tp1_first, tp2_first -> resolved_positive
sl_first -> resolved_negative
entry_reached -> entry_reached_unresolved
not_entered, entry_not_reached -> not_entered
expired -> expired
no_ohlcv or missing OHLCV category -> coverage_missing
blank, pending, timeout -> pending
ambiguous -> ambiguous
other -> unknown
```

Rules:

- unresolved, pending, ambiguous, no-OHLCV, expired, and not-entered rows are not wins or losses
- `tp1_first` and `tp2_first` are proxy positives, not actual profits
- `sl_first` is a proxy negative, not an actual realized loss
- malformed non-empty `mfe_r` or `mae_r` exits `2`
- MFE / MAE coverage is reported separately from outcome coverage

## 7. Proxy comparison metrics

For each policy, report:

```text
qualifying_event_rows
selected_scenario_rows
duplicate_event_rows_suppressed
scenario_selection_rate
entry_candidate_rows
observe_only_rows
resolved_proxy_rows
resolved_positive_rows
resolved_negative_rows
proxy_positive_rate
entry_reached_unresolved_rows
not_entered_rows
expired_rows
coverage_missing_rows
pending_rows
ambiguous_outcome_rows
unknown_outcome_rows
mfe_r_count
mae_r_count
average_mfe_r
average_mae_r
median_mfe_r
median_mae_r
```

`proxy_positive_rate` denominator is only:

```text
resolved_positive_rows + resolved_negative_rows
```

Do not label it as actual win rate.

### 7.1 Required breakdowns

For every policy, split counts by:

- side
- market regime
- setup family
- selected operator class
- selected row role
- normalized outcome status

Do not combine long and short into one recommendation.

### 7.2 Duplicate compression

For each policy:

```text
duplicate_event_rows_suppressed
= qualifying_event_rows - selected_scenario_rows
```

Also report:

```text
qualifying_events_per_selected_scenario
```

Do not call selected scenario rows actual notifications.

### 7.3 Proxy opportunity review candidates

These are review labels, not facts about human behavior.

`proxy_over_suppression_candidate`:

```text
scenario absent from CURRENT_STRICT
scenario selected by A_PLUS_B as B_CHECK_15M
selected B event outcome is resolved_positive
```

`proxy_false_positive_candidate`:

```text
entry-candidate selected event outcome is resolved_negative
```

`proxy_c_observation_positive_candidate`:

```text
A_PLUS_B_PLUS_C_OBSERVE selects C
selected C event outcome is resolved_positive
```

`proxy_c_upgrade_candidate`:

```text
selected C event later upgrades to A or B
```

Do not name these `missed_opportunity` or `avoided_loss` unless an effective human decision provides that evidence in a later phase.

## 8. Human decision evidence

Human decision evidence is optional and descriptive.

### 8.1 Attribution

For each policy selection:

- scenario-scoped decision joins directly by scenario ID
- signal-only decision may join only if its signal maps to exactly one selected scenario for that policy
- decision timestamp must be at or after policy selection timestamp
- if multiple effective decisions qualify, retain all in counts but choose the earliest for row-level display

Pre-selection decisions are counted separately and not attributed to the policy.

### 8.2 Decision metrics

Per policy:

```text
effective_decision_rows
scenarios_with_decision
decision_coverage_rate
entered_rows
watched_no_entry_rows
skipped_rows
exited_rows
took_profit_rows
adjusted_stop_rows
cancelled_plan_rows
pre_selection_decision_rows
ambiguous_signal_only_decision_rows
orphan_decision_rows
```

Do not infer success from an action alone.

Do not expose manual notes.

## 9. Actual trade evidence

Actual trade evidence is optional and descriptive.

### 9.1 Eligible actual links

An episode is eligible only when all are true:

```text
episode association_status == matched
link_status == linked
link_confidence in high, medium
side_compatibility == match
symbol_compatibility == match
episode opened_at >= selected policy event timestamp
```

If one signal maps to more than one selected scenario in the same policy, mark attribution ambiguous and exclude it from monetary aggregates.

Low-confidence, ambiguous, unmatched, pre-selection, side-conflict, and symbol-conflict evidence remains counted but excluded.

### 9.2 Monetary metrics

For eligible closed episodes with numeric realized PnL:

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

Definitions:

```text
net episode PnL = realized_pnl - abs(fee_total)
```

If fee is blank, that episode is excluded from net-PnL and profit-factor calculations but remains in gross coverage counts.

Actual profit factor:

```text
sum positive net episode PnL / abs(sum negative net episode PnL)
```

If there are no negative net episodes, profit factor is blank, not infinity.

Do not calculate actual R because the current episode schema does not establish an actual risk denominator.

Do not claim policy profitability when actual-linked sample is absent or insufficient.

## 10. Replay CSV

Canonical generated output:

```text
logs/csv/manual_operator_historical_replay.csv
```

Schema:

```text
manual_operator_historical_replay.v1
```

Headers:

```text
schema_version
replay_row_id
replay_method_version
policy_name
row_role
scenario_id
selected_scenario_event_id
classification_id
selected_at_utc
selected_at_jst
symbol
side
setup_family
market_regime
selected_operator_class
trade_execution_gate
selection_reason
intraperiod_outcome
normalized_outcome_status
first_exit_reason
mfe_r
mae_r
ohlcv_coverage_status
ohlcv_gap_reason
scenario_final_status
scenario_final_lifecycle
scenario_final_proxy_outcome
later_upgrade_class
later_upgrade_at_utc
upgrade_latency_minutes
decision_join_status
first_effective_human_action
first_human_checked_at_utc
actual_join_status
actual_episode_id
actual_link_confidence
actual_gross_realized_pnl
actual_fee_total
actual_net_pnl_after_fee
source_join_status
```

One row is emitted for every selected policy/scenario pair and every STOP overlay scenario.

Do not include:

- manual note
- raw exchange source fields
- account identifiers
- local full paths
- order identifiers

## 11. JSON summary

Canonical generated output:

```text
logs/json/manual_operator_historical_replay_YYYYMMDD.json
```

Schema:

```text
manual_operator_historical_replay_report.v1
```

Required top-level metrics:

```text
scenario_rows
scenario_event_rows
classification_rows
assigned_event_rows
ambiguous_event_rows
insufficient_classification_rows
classifier_method_version
threshold_snapshot
policy_summaries
side_policy_summaries
regime_policy_summaries
setup_family_policy_summaries
class_policy_summaries
outcome_policy_summaries
strict_pass_inconsistent_rows
proxy_over_suppression_candidate_rows
proxy_false_positive_candidate_rows
proxy_c_observation_positive_candidate_rows
proxy_c_upgrade_candidate_rows
decision_input_status
decision_summary
actual_input_status
actual_summary
```

All count-map keys sort lexically.

Policy maps use the fixed policy order.

## 12. Markdown report

Canonical generated output:

```text
運用資料/reports/post_eval/manual_operator_historical_replay_YYYYMMDD.md
```

Sections in order:

```text
Purpose
Input Status
Method and No-Leakage Boundary
Policy Definitions
Coverage
Policy Comparison
Duplicate Compression
Proxy Outcome Comparison
Side Breakdown
Regime Breakdown
Setup-Family Breakdown
C Observation and Upgrade Review
STOP Overlay Review
Human Decision Evidence
Actual Trade Evidence
Limitations
Safety Boundary
```

The report must visibly state:

- offline historical replay only
- not FORMAL_GO
- no automatic order
- human decides manually
- existing gates are not replaced or recomputed
- C is observation-only
- STOP is not an automatic exit
- proxy positive rate is not actual win rate
- unresolved and no-OHLCV rows are excluded from resolved denominators
- actual evidence uses only eligible high/medium links
- no production tuning recommendation is made in P6

Do not include raw rows, manual notes, or private values.

## 13. Deterministic identity and ordering

Replay method version:

```text
manual_operator_historical_replay.v1
```

Replay row ID:

```text
rpl_
+ first 24 lowercase hexadecimal characters of SHA-256 over:
  policy_name
  row_role
  scenario_id
  selected_scenario_event_id
  classification_id
  replay method version
```

Do not include:

- execution timestamp
- output path
- row index
- random value
- later outcome in the ID
- human note
- actual monetary result in the ID

CSV ordering:

```text
fixed policy order
selected_at_utc
scenario_id
replay_row_id
```

Repeated unchanged inputs and arguments must produce byte-identical CSV, JSON, and Markdown.

## 14. Transaction behavior

CSV, JSON, and Markdown are one process-level transaction.

Before replacement:

1. validate all schemas and references
2. construct all policy selections in memory
3. join evaluation evidence only after selections are fixed
4. serialize and validate all three outputs
5. prepare all temporary files in target parent filesystems
6. replace all three targets
7. on any replacement failure, restore every prior target
8. remove all temporary and backup files

Dry-run creates no files or directories.

Existing output with wrong schema fails with exit `4` unless `--replace-output` is explicit.

No power-loss atomicity is claimed.

Generated outputs remain local and are not committed.

## 15. CLI

Command:

```text
build-manual-operator-historical-replay
```

Required arguments:

```text
--scenarios
--scenario-events
--classifications
--output-csv
--output-json
--output-md
--date
--stdout-json
```

Optional arguments:

```text
--decision-events
--trade-episodes
--episode-links
--dry-run
--replace-output
```

Stdout is exactly one compact JSON object plus newline when `--stdout-json` is supplied.

Stdout must not contain:

- full local paths
- raw rows
- manual notes
- account or order identifiers
- large text fields
- traceback for expected validation errors

## 16. Exit codes

```text
0 success or deterministic no-op
1 unexpected internal failure
2 invalid input, schema, reference, timestamp, or numeric value
3 identity conflict
4 output schema mismatch or transaction failure
```

Expected validation failures do not print a traceback.

## 17. Preferred implementation files

```text
src/feedback/manual_operator_historical_replay.py
tools/log_feedback.py
tests/test_manual_operator_historical_replay.py
```

`src/feedback/__init__.py` may be edited only if required by existing package conventions.

No production module should be edited.

## 18. Read-only reference files

```text
src/feedback/manual_operator_classifier.py
src/feedback/manual_scenario_normalizer.py
src/feedback/manual_decision_events.py
src/feedback/manual_scenario_coverage.py
src/feedback/manual_trade_episode_builder.py
src/feedback/manual_trade_signal_linker.py
src/feedback/manual_trade_ground_truth.py
docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md
```

Read only the required schemas and established correction/link semantics.

## 19. Prohibited edits and integrations

Do not edit:

```text
src/trade/
src/analysis/
src/notification/
runtime configuration
launchd configuration
mail sending code
```

Do not integrate with:

```text
exchange APIs
account endpoints
order endpoints
secrets
raw exchange exports
paper_positions.csv
```

Do not add live notification or runtime behavior.

## 20. Required tests

Use synthetic fixtures only.

### Input and integrity

1. exact scenario, event, and classification schemas are accepted
2. unknown scenario reference exits 2
3. missing classification reference exits 2
4. extra classification reference exits 2
5. mismatched classification identity field exits 2
6. duplicate classification identity conflict exits 3
7. mixed classifier method versions exit 2
8. mixed threshold snapshots exit 2
9. optional trade inputs must be supplied together
10. malformed Decimal or timestamp exits 2

### Policy selection

11. earliest qualifying event per scenario is selected
12. later favorable outcome does not alter selected event
13. CURRENT_STRICT uses formal pass evidence
14. inconsistent strict-pass rows are counted and excluded
15. A_ONLY selects A only
16. A_PLUS_B selects the earlier eligible A or B
17. A_PLUS_B_PLUS_C selects C as observe-only
18. C is excluded from entry denominators
19. STOP overlay is separate from entry policies
20. ambiguous and insufficient rows are not selected

### Outcome and metrics

21. tp1/tp2 map to resolved positive
22. sl maps to resolved negative
23. unresolved, no-OHLCV, expired, and not-entered are excluded from resolved denominator
24. proxy positive rate denominator is correct
25. MFE / MAE averages and medians use only numeric covered rows
26. duplicate suppression is scenario based
27. side breakdown is separate
28. regime breakdown is separate
29. setup-family breakdown is separate
30. B positive beyond strict baseline is labeled proxy over-suppression candidate only
31. C positive is not treated as an entry win
32. first later A/B upgrade after C is deterministic
33. STOP outcome distribution does not imply automatic exit

### Human decisions

34. absent decision input is valid
35. correction semantics choose unsuperseded effective rows
36. malformed correction graph exits 2
37. pre-selection decision is not attributed
38. scenario decision joins directly
39. ambiguous signal-only decision is excluded
40. manual note is absent from outputs

### Actual trade evidence

41. absent actual inputs are valid
42. only matched high/medium links with side and symbol match are eligible
43. low and ambiguous links are excluded
44. episode opened before policy selection is excluded
45. one signal mapping to multiple scenarios is excluded as ambiguous
46. fee-missing episode is excluded from net metrics
47. net PnL subtracts absolute fee
48. profit factor is blank with no losses
49. actual R is not fabricated
50. actual episode is not double-counted within one policy

### Determinism, transaction, and CLI

51. repeated build is byte-identical
52. dry-run creates no files or directories
53. wrong existing output schema exits 4
54. three-output rollback restores all prior outputs
55. no temporary or backup residue remains
56. direct CLI success emits one compact JSON line
57. direct CLI expected input error exits 2 without traceback
58. stdout exposes no full paths, raw rows, manual notes, or identifiers
59. P5 and P4 targeted tests continue passing
60. P3 episode/link tests continue passing

## 21. Validation

Implementation validation:

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
```

Then task-file-only `git diff --check`.

Do not run the full suite unless the shared CLI change creates a concrete broader regression risk.

## 22. Completion criteria

P6 implementation is complete only when:

- policy selection is event-time and scenario-deduplicated
- all four required policy comparisons exist
- C remains observation-only
- STOP remains a separate overlay
- selected-event outcomes are used for primary proxy metrics
- unresolved and no-OHLCV rows remain outside resolved denominators
- side, regime, setup, class, and outcome breakdowns exist
- optional human and actual evidence is fail-closed and descriptive
- no actual R is fabricated
- outputs are deterministic and transactional
- focused regressions pass
- no production, notification, runtime, API, or order behavior changes
- ChatGPT reviews actual source and tests

## 23. Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```

P6 produces evidence for review. It does not authorize P7 shadow display, production tuning, live notification changes, or orders.
