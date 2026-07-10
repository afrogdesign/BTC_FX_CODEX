# P5 Manual Operator Classifier — Offline Specification

## Metadata

- phase: P5
- status: active specification
- work family: manual trading practicality
- implementation mode: report-only / offline / local generated outputs
- safety: not FORMAL_GO / no automatic order / human decides manually
- preceding accepted phase: P4 scenario normalization and decision-event infrastructure
- accepted P4 commits reviewed through: `106042937a39fff495d14de219eb1728038cc7f8`

## 1. Purpose

Build an offline classifier that translates contemporaneous scenario evidence into one operator-action hypothesis:

```text
A_FORMAL
B_CHECK_15M
C_WATCH_ZONE
STOP_OR_EXIT
```

The classifier is for analysis and comparison only.

It must not:

- change any production gate
- change notification behavior
- change runtime behavior
- write orders
- declare FORMAL_GO
- treat an offline class as entry permission

## 2. Core design decision

Classification is event-time based, not final-scenario based.

Each assigned P4 scenario event is classified using only evidence available at that event timestamp.

Do not use later scenario state or later market outcomes to classify an earlier event.

One classification row corresponds to one P4 scenario event.

Ambiguous grouping rows remain visible but are not assigned an operator class.

## 3. No-leakage boundary

The following fields may be present in P4 outputs but are prohibited as classifier inputs:

```text
intraperiod_outcome
entry_reached_time
first_exit_time
first_exit_reason
mfe_r
mae_r
proxy_outcome
proxy_outcome_status
zone_touched_at_utc
zone_touched_at_jst
terminal_at_utc
terminal_at_jst
manual decision events
actual trade episodes
actual trade links
realized PnL
fees
```

These may be used only by later replay or evaluation phases.

The classifier must not derive a class from hindsight outcome evidence.

## 4. Required input files

All paths are explicit CLI arguments. Do not silently select among historical filenames.

### 4.1 P4 scenario summary

Schema:

```text
manual_scenario.v1
```

Purpose:

- validate scenario identity
- validate assigned event references
- retain scenario-level identity only

Do not use final scenario lifecycle or final proxy outcome for classification.

### 4.2 P4 scenario events

Schema:

```text
manual_scenario_event.v1
```

Purpose:

- one classifier input event per assigned row
- candidate ID
- signal ID
- side
- setup family
- entry zone
- invalidation
- TP values
- contemporaneous candidate status

Allowed grouping states:

```text
new_scenario
matched_existing
ambiguous
```

Rules:

- assigned events require a known scenario ID
- ambiguous events require blank scenario ID
- event IDs are non-empty and unique
- scenario summary `scenario_id` is non-empty and unique
- `new_scenario` and `matched_existing` events have a non-empty `scenario_id` that exists in the scenario summary
- `ambiguous` events have a blank `scenario_id`
- duplicate scenario IDs, unknown scenario references, or grouping-state/scenario-ID mismatches are invalid input and exit `2`

The scenario summary final lifecycle and proxy outcome are never classifier inputs. Classification uses event-time evidence only.

### 4.3 Active Plan candidate evidence

CLI argument:

```text
--candidates
```

No implicit default path.

Current source writer uses:

```text
logs/csv/active_plan_candidates.csv
```

Historical workflows may use another explicit local candidate path. The CLI must use only the supplied path.

Required columns:

```text
candidate_id
source_signal_id
timestamp_jst
candidate_type
candidate_status
side
entry_mode
entry_price
entry_zone_low
entry_zone_high
stop_loss
tp1
tp2
rr_current_tp1
rr_current_tp2
rr_zone_mid_tp1
rr_zone_mid_tp2
market_entry_status
limit_entry_status
counter_scalp_status
breakout_status
next_condition
```

Duplicate behavior:

- exact duplicate normalized row: skip and count
- same candidate ID with differing normalized business fields: identity conflict, exit 3
- assigned P4 event without candidate evidence: classification status `insufficient_evidence`

### 4.4 Signal context evidence

CLI argument:

```text
--signal-context
```

Expected current source file:

```text
logs/csv/trades.csv
```

Use required-header subset validation rather than requiring the full logger header order.

Required columns:

```text
signal_id
timestamp_jst
current_price
bias
market_regime
transition_direction
primary_setup_side
primary_setup_status
confidence_direction_shadow
confidence_execution_shadow
confidence_wait_shadow
prelabel
trade_execution_gate
trade_execution_blockers
phase1b_lite_gate
phase1b_lite_type
phase1b_lite_reasons
opportunity_gate
opportunity_type
opportunity_reasons
signal_tier
data_quality_flag
no_trade_flags
warning_flags
risk_flags
long_rr
short_rr
trend_flip_state
active_level_role
level_flip_state
failed_breakout_state
nearest_major_support
nearest_major_resistance
```

Signal identity:

- `signal_id` non-empty and unique after exact-duplicate removal
- exact duplicate normalized row: skip and count
- same signal ID with differing normalized business fields: identity conflict, exit 3
- assigned event without signal context: classification status `insufficient_evidence`

Candidate and signal fingerprints, and exact-duplicate identity, use only the required columns listed in their respective sections, in listed order, after the existing canonical normalization for blank values, Decimal values, timestamps, and list-like fields. Additional columns must not affect fingerprints, identity conflicts, duplicate detection, or classification IDs.

## 5. Time-consistency validation

For a matched candidate and signal context:

- source signal ID must match the event source signal ID
- candidate timestamp must be parseable
- signal timestamp must be parseable
- event timestamp must be parseable
- candidate timestamp and signal timestamp must not be later than event timestamp
- future evidence relative to the event causes input error, exit 2

Naive timestamps are interpreted as JST.

## 6. Output files

### 6.1 Classification CSV

Canonical generated output:

```text
logs/csv/manual_operator_classifications.csv
```

Schema version:

```text
manual_operator_classification.v1
```

Headers:

```text
schema_version
classification_id
classifier_method_version
scenario_event_id
scenario_id
candidate_id
source_signal_id
event_timestamp_utc
event_timestamp_jst
symbol
side
setup_family
market_regime
transition_direction
classification_status
operator_class
priority_rank
reason_codes
warning_codes
required_human_check
trade_execution_gate
trade_execution_blockers
phase1b_lite_gate
phase1b_lite_type
opportunity_gate
opportunity_type
prelabel
signal_tier
primary_setup_status
primary_setup_side
candidate_status
entry_mode
entry_price
entry_zone_low
entry_zone_high
invalidation_price
tp1_price
tp2_price
rr_tp1_used
rr_tp2_used
confidence_direction_shadow
confidence_execution_shadow
confidence_wait_shadow
data_quality_flag
no_trade_flags
risk_flags
source_join_status
short_direction_min
short_execution_min
short_wait_max
short_tp1_rr_min
short_tp2_rr_min
long_direction_min
long_execution_min
long_wait_max
long_tp1_rr_min
long_tp2_rr_min
```

Classification status values:

```text
classified
insufficient_evidence
ambiguous_grouping
```

`operator_class` is blank unless `classification_status=classified`.

### 6.2 JSON summary

Canonical generated output:

```text
logs/json/manual_operator_classifier_YYYYMMDD.json
```

Schema:

```text
manual_operator_classifier_report.v1
```

### 6.3 Markdown report

Canonical generated output:

```text
運用資料/reports/post_eval/manual_operator_classifier_YYYYMMDD.md
```

The classification CSV, JSON summary, and Markdown report are one process-level transaction. Prepare, serialize, and validate all three temporary files before replacing any target. If any replacement fails, restore all three prior targets and remove every temporary and backup file. Dry-run creates no files or directories. No power-loss atomicity is claimed.

Generated outputs remain local and are not committed.

## 7. Deterministic identity

Classifier method version:

```text
manual_operator_classifier.v1
```

Classification ID:

```text
opc_
+ first 24 lowercase hexadecimal characters of SHA-256 over:
  scenario_event_id
  candidate normalized fingerprint
  signal-context normalized fingerprint
  classifier method version
  all threshold arguments in canonical order
```

Do not include:

- execution timestamp
- output path
- row index
- random value
- future outcome evidence

Repeated unchanged input and arguments must produce byte-identical CSV, JSON, and Markdown.

Deterministic ordering is fixed: classification CSV rows sort by `event_timestamp_utc`, then `scenario_event_id`, then `classification_id`. JSON count-map keys sort lexically. Markdown class sections use `STOP_OR_EXIT`, `A_FORMAL`, `B_CHECK_15M`, `C_WATCH_ZONE`, then `insufficient_evidence`; side, market regime, and setup family breakdowns sort lexically.

## 8. Normalization

### 8.1 Empty values

Blank remains blank. Do not coerce blank numerics to zero.

### 8.2 Decimal values

Use Decimal parsing and canonical fixed-point text.

Malformed non-empty numerics are invalid input, exit 2.

### 8.3 List-like fields

Normalize reason, warning, risk, blocker, and no-trade fields from supported delimiters into sorted unique tokens.

Output uses semicolon-separated normalized tokens.

Do not echo raw text blobs.

### 8.4 Boolean-like gate values

Gate fields retain their normalized source string.

Do not invent pass values beyond exact documented values.

Formal pass value:

```text
pass
```

Blocked value commonly used by current source:

```text
blocked
```

Unknown non-empty gate values are retained and cannot satisfy A_FORMAL.

## 9. RR selection

For each event side, choose RR deterministically.

TP1 RR priority:

```text
rr_zone_mid_tp1
then rr_current_tp1
then side-specific signal RR
```

TP2 RR priority:

```text
rr_zone_mid_tp2
then rr_current_tp2
```

For side-specific signal RR:

- long uses `long_rr`
- short uses `short_rr`

Blank is allowed but may cause insufficient evidence for B.

Zero is retained.

## 10. Classification priority

Apply exactly in this order:

```text
1. STOP_OR_EXIT
2. A_FORMAL
3. B_CHECK_15M
4. C_WATCH_ZONE
5. insufficient_evidence
```

A lower-priority class must never override a higher-priority result.

## 11. STOP_OR_EXIT hypothesis

Classify `STOP_OR_EXIT` when all required joins are available and any of the following contemporaneous conditions is true:

```text
data_quality_flag is non-empty and not equal to ok
no_trade_flags contains at least one token
candidate_status is one of invalidated, cancelled, expired
```

Reason codes:

```text
stop_data_quality
stop_no_trade_flag
stop_candidate_invalidated
stop_candidate_cancelled
stop_candidate_expired
```

STOP is an operator-action hypothesis. It is not an automatic close instruction.

Warnings and risk flags remain visible.

Do not derive STOP from later TP/SL outcome fields.

## 12. A_FORMAL hypothesis

Classify `A_FORMAL` only when all conditions are true:

```text
trade_execution_gate == pass
data_quality_flag == ok
no_trade_flags is empty
primary_setup_status == ready
primary_setup_side matches event side
```

A retains current strict formal evidence.

A must not be created from phase1b-lite or opportunity evidence alone.

A reason codes:

```text
formal_gate_pass
formal_data_quality_ok
formal_setup_ready
formal_side_match
```

Required human check:

```text
confirm_15m_before_manual_action
```

A is not FORMAL_GO and does not authorize an order.

## 13. B_CHECK_15M hypothesis

B is an offline comparison hypothesis below formal A.

Common requirements:

```text
data_quality_flag == ok
no_trade_flags is empty
primary_setup_status in ready, watch
candidate_status in allowed, conditional, armed, watch
side matches primary_setup_side
RR evidence satisfies the side-specific rule
shadow metrics satisfy the side-specific thresholds
trade_execution_gate == blocked
```

If trade execution already passes and A requirements fail for another reason, do not downgrade silently to B unless all B rules independently pass and reason code `formal_evidence_incomplete` is included.

For a `pass` execution gate, B is allowed only when A is not satisfied, every B condition independently passes, and `formal_evidence_incomplete` is present. Blank or unknown gate values never satisfy B. Missing any required `confidence_direction_shadow`, `confidence_execution_shadow`, or `confidence_wait_shadow` is `insufficient_evidence`, not C. If all RR values required by the side-specific rule are missing, classification is `insufficient_evidence`, not C. Missing required shadow or RR evidence is never downgraded to C.

### 13.1 Default short thresholds

```text
short_direction_min = 55
short_execution_min = 18
short_wait_max = 75
short_tp1_rr_min = 0.8
short_tp2_rr_min = 1.5
```

Short RR rule:

```text
TP1 RR >= short_tp1_rr_min
OR
TP2 RR >= short_tp2_rr_min
```

### 13.2 Default long thresholds

Long is intentionally more conservative.

```text
long_direction_min = 60
long_execution_min = 22
long_wait_max = 70
long_tp1_rr_min = 1.0
long_tp2_rr_min = 1.8
```

Long RR rule:

```text
TP1 RR >= long_tp1_rr_min
OR
TP2 RR >= long_tp2_rr_min
```

Long B also requires:

```text
primary_setup_status == ready
```

Do not make `trend_flip_state` alone sufficient for long B.

The classifier records trend, level-flip, and failed-breakout fields only as visible evidence and warnings in v1.

### 13.3 B output

Required human check:

```text
check_15m_trigger_then_human_decides
```

Typical reason codes:

```text
b_shadow_thresholds_pass
b_rr_threshold_pass
b_setup_eligible
b_side_match
b_formal_gate_not_pass
b_long_conservative_rule
```

These thresholds are CLI/report comparison values, not production thresholds.

## 14. C_WATCH_ZONE hypothesis

Classify `C_WATCH_ZONE` when:

- STOP and A do not apply
- source joins are complete
- side and scenario identity are valid
- entry zone or entry price exists
- candidate status indicates a currently observable plan state
- B requirements are not fully satisfied

C is limited to a watch hypothesis where joins, side, entry definition, and required shadow/RR evidence are present, but a B threshold, setup state, or eligible candidate state is not satisfied. It never substitutes for missing required evidence and never implies entry permission.

Eligible candidate states:

```text
allowed
conditional
armed
watch
```

Required human check:

```text
watch_zone_and_wait_for_upgrade
```

Reason codes must explain the missing B requirements, for example:

```text
c_wait_direction_below_threshold
c_wait_execution_below_threshold
c_wait_pressure_above_threshold
c_wait_rr_below_threshold
c_wait_setup_not_ready
c_wait_formal_or_b_evidence_incomplete
```

Do not imply entry permission.

## 15. Insufficient evidence and ambiguity

### 15.1 Ambiguous grouping

For P4 ambiguous grouping rows:

```text
classification_status=ambiguous_grouping
operator_class=""
reason_codes=ambiguous_scenario_assignment
```

### 15.2 Missing joins or required evidence

Use:

```text
classification_status=insufficient_evidence
operator_class=""
```

Reason codes may include:

```text
missing_candidate_context
missing_signal_context
missing_required_shadow_metric
missing_required_rr
missing_entry_definition
side_mismatch
```

Missing evidence is not STOP and not a loss.

`future_context_rejected` is not a successful classification reason. A candidate or signal timestamp later than the event timestamp is input validation failure with exit `2`; no successful classification row is generated.

## 16. Regime and side separation

Every classified row retains:

```text
side
market_regime
transition_direction
setup_family
```

Reports must split counts by:

- operator class
- side
- market regime
- setup family
- classification status

Do not merge long and short into one recommendation metric.

Do not claim that one regime performs better in P5. Performance belongs to P6 replay.

## 17. Existing gate preservation

Output must retain the existing source evidence:

```text
trade_execution_gate
trade_execution_blockers
phase1b_lite_gate
phase1b_lite_type
opportunity_gate
opportunity_type
prelabel
signal_tier
```

P5 does not replace or recompute these gates.

No existing gate source may be edited.

## 18. Warnings and safety display

The output retains normalized:

```text
warning_flags
risk_flags
no_trade_flags
```

Markdown must visibly state:

- offline hypothesis only
- not FORMAL_GO
- no automatic order
- human decides manually
- A/B/C/STOP does not replace existing gates
- B thresholds are comparison values, not production settings
- P5 contains no profitability evaluation

## 19. Summary metrics

JSON and Markdown include:

```text
scenario_event_input_rows
assigned_event_rows
ambiguous_event_rows
candidate_context_rows
signal_context_rows
exact_duplicate_candidate_rows
exact_duplicate_signal_rows
candidate_conflict_rows
signal_conflict_rows
complete_join_rows
insufficient_evidence_rows
classified_rows
class_counts
classification_status_counts
side_class_counts
regime_class_counts
setup_family_class_counts
formal_gate_pass_rows
a_formal_rows
formal_pass_not_a_rows
b_check_15m_rows
c_watch_zone_rows
stop_or_exit_rows
warning_token_counts
risk_token_counts
no_trade_token_counts
```

`formal_pass_not_a_rows` must remain visible to reveal evidence inconsistencies.

No win rate, PF, PnL, MFE, MAE, TP-first, or SL-first metric in P5.

## 20. Report sections

Markdown sections:

```text
Purpose
Input Status
Method and No-Leakage Boundary
Threshold Snapshot
Classification Coverage
Class Distribution
Side Breakdown
Regime Breakdown
Setup-Family Breakdown
Existing Gate Comparison
Warnings and Risks
Limitations
Safety Boundary
```

## 21. CLI

Command:

```text
build-manual-operator-classifier
```

Required arguments:

```text
--scenarios
--scenario-events
--candidates
--signal-context
--output-csv
--output-json
--output-md
--date
--stdout-json
```

Threshold arguments:

```text
--short-direction-min
--short-execution-min
--short-wait-max
--short-tp1-rr-min
--short-tp2-rr-min
--long-direction-min
--long-execution-min
--long-wait-max
--long-tp1-rr-min
--long-tp2-rr-min
```

Optional:

```text
--dry-run
--replace-output
```

All thresholds must be finite Decimals.

Score thresholds must be within 0 through 100.

RR thresholds must be non-negative.

Invalid arguments exit 2.

Stdout is exactly one compact JSON object plus newline.

Stdout must not contain:

- raw rows
- full local paths
- large text fields
- headlines
- notes
- private values

## 22. Exit codes

```text
0 success or deterministic no-op
1 unexpected internal failure
2 invalid input, schema, timestamp, threshold, or time consistency
3 candidate or signal identity conflict
4 output schema mismatch or I/O transaction failure
```

Expected validation failures do not print a traceback.

## 23. Transaction behavior

Before writing:

1. validate all input schemas
2. validate identities and timestamps
3. build all classification rows and summaries in memory
4. validate generated schemas
5. prepare temporary files in target parent filesystems
6. replace classification CSV, JSON summary, and Markdown report
7. on any replacement failure, restore every prior target
8. remove temporary and backup files

The classification CSV, JSON, and Markdown are one process-level transaction. All three are fully prepared and validated before replacement; any replacement failure restores all three prior targets and leaves no temporary or backup residue. Dry-run creates neither files nor directories. No power-loss atomicity is claimed.

Do not claim power-loss atomicity.

Existing output with wrong schema fails with exit 4 unless `--replace-output` is explicit.

Dry-run writes nothing.

## 24. Preferred implementation files

```text
src/feedback/manual_operator_classifier.py
tools/log_feedback.py
tests/test_manual_operator_classifier.py
```

`src/feedback/__init__.py` may be edited only if needed for existing package conventions.

No production module should be edited.

## 25. Read-only reference files

```text
src/storage/csv_logger.py
src/trade/execution_gate.py
src/trade/phase1b_lite.py
src/trade/opportunity_gate.py
src/analysis/signal_tier.py
src/feedback/manual_scenario_normalizer.py
src/feedback/manual_scenario_coverage.py
```

Read only the relevant constants and value contracts.

## 26. Prohibited edits

Do not edit:

```text
src/trade/active_plan.py
src/trade/execution_gate.py
src/trade/phase1b_lite.py
src/trade/opportunity_gate.py
src/trade/judgment_self_review.py
src/analysis/position_risk.py
src/analysis/signal_tier.py
src/notification/trigger.py
runtime configuration
launchd configuration
mail sending code
```

Do not integrate with:

```text
paper_positions.csv
order endpoints
account endpoints
exchange APIs
secrets
```

## 27. Required tests

Use synthetic fixtures only.

At minimum cover:

### Input and identity

1. one assigned event produces one row
2. ambiguous event remains unclassified
3. missing candidate context is insufficient evidence
4. missing signal context is insufficient evidence
5. exact duplicate candidate is counted and skipped
6. candidate identity conflict exits 3
7. exact duplicate signal context is counted and skipped
8. signal identity conflict exits 3
9. candidate timestamp after event exits 2
10. signal timestamp after event exits 2
11. malformed timestamp exits 2
12. malformed numeric exits 2
13. zero numeric is retained

### STOP

14. non-ok data quality produces STOP
15. no-trade token produces STOP
16. invalidated candidate produces STOP
17. STOP takes priority over formal gate pass

### A

18. exact formal conditions produce A
19. formal pass with side mismatch does not produce A
20. formal pass with setup not ready does not produce A
21. phase1b or opportunity pass alone does not produce A
22. A retains existing gate evidence

### B short

23. short default thresholds produce B
24. direction below threshold prevents B
25. execution below threshold prevents B
26. wait above threshold prevents B
27. TP1 RR threshold can satisfy B
28. TP2 RR threshold can satisfy B
29. formal pass does not silently downgrade without explicit evidence

### B long

30. conservative long defaults produce B
31. long watch setup does not produce B
32. trend flip alone does not produce B
33. long and short thresholds are independent

### C

34. eligible zone candidate below B threshold produces C
35. missing entry definition is insufficient, not C
36. C reason codes identify missing B conditions
37. C never reports entry permission

### Reports and determinism

38. class counts are correct
39. side breakdown is separate
40. regime breakdown is separate
41. setup-family breakdown is separate
42. formal-pass-not-A metric is correct
43. report contains no performance claims
44. no prohibited outcome field influences class
45. repeated build is byte-identical
46. dry-run creates no files
47. wrong existing output schema exits 4
48. three-output rollback restores all prior files
49. no temporary or backup residue after rollback
50. CLI success returns one compact JSON line
51. CLI invalid input exits 2 without traceback
52. stdout exposes no full paths or raw rows
53. existing P4 targeted tests continue passing

Final source-review contract regressions must also cover: duplicate scenario ID exit `2`; assigned event with unknown scenario reference exit `2`; ambiguous event with non-empty scenario ID exit `2`; additional non-required columns not changing fingerprints or identity; blank and unknown execution gates not producing B; missing required shadow or RR evidence producing `insufficient_evidence` rather than C; future context exit `2` with no successful row; three-output rollback restoring CSV, JSON, and Markdown with no temporary or backup residue; and direct CLI success/error JSON contracts.

## 28. Validation

Implementation validation:

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
```

Then task-file-only `git diff --check`.

Do not run the full suite unless a shared CLI change creates a specific broader regression risk.

## 29. Completion criteria

P5 implementation is complete only when:

- event-time no-leakage classification is implemented
- all four operator classes are available as offline hypotheses
- incomplete and ambiguous evidence remains explicit
- side and regime breakdowns are present
- existing gate evidence is retained
- three outputs are deterministic and transactional
- focused tests and P4 regressions pass
- no production, notification, runtime, or order behavior changed
- ChatGPT reviews the actual source and tests

## 30. Safety boundary

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```

A class label is not permission to trade.
