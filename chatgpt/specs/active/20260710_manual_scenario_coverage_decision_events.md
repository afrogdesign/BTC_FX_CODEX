# Manual Scenario Coverage and Decision Events Active Spec

## Metadata

- work_id: `BTCFX-20260710-MTP-SCENARIO-COVERAGE-DECISION-SPEC`
- created_at: `2026-07-10`
- status: active / design baseline
- phase: `P4`
- previous_phase: `P3 manual trade linkage and ground-truth pipeline complete`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

---

## 1. Objective

P4は、Active Planのcandidate rowを独立した相場scenarioへ正規化し、OHLCV evidence coverageをscenario単位で可視化し、将来のhuman manual trialで使うdecision-event schemaとlocal recorderを準備する。

P4はA/B/C/STOP classifierを実装しない。

P4はnotification triggerやlive mail behaviorを変更しない。

Canonical flow:

```text
active plan candidate rows
+ intraperiod proxy outcomes
+ optional OHLCV coverage evidence
→ deterministic scenarios and scenario events
→ coverage report

human chart check/action
→ append-only manual decision event
```

Three evidence dimensions must remain separate:

```text
scenario evidence
proxy market-path outcome
human decision/action
```

Exchange actual outcomes remain the P3 episode/link layer.

---

## 2. Existing repo evidence

Existing candidate source:

```text
logs/csv/active_plan_paper_candidates.csv
```

Observed fields include:

```text
candidate_id
source_signal_id
timestamp_jst
active_primary_action
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
active_subject_label
active_headline
next_condition
```

Existing intraperiod outcome source:

```text
logs/csv/active_plan_candidate_intraperiod_outcomes.csv
```

The existing evaluator already distinguishes:

```text
tp1_first
tp2_first
sl_first
timeout
ambiguous
entry_reached
not_entered
pending
no_ohlcv
```

Existing judgment self-review contains candidate-level dimensions including `scenario_lifecycle_result`, but it does not provide a stable cross-signal `scenario_id` and must not be treated as the canonical scenario model.

P4 adds a new derived scenario model without rewriting existing Active Plan or self-review assets.

---

## 3. Responsibility boundaries

### P4 owns

- scenario identity
- candidate-to-scenario grouping
- deterministic scenario events
- duplicate candidate compression measurement
- signal-to-scenario mapping
- row-level and scenario-level OHLCV coverage diagnostics
- manual decision-event schema
- local append-only decision-event recording
- compact coverage reports

### P4 does not own

- A/B/C/STOP classification
- production thresholds
- execution-gate changes
- notification trigger changes
- live mail changes
- historical profitability claims
- actual order/fill/position import
- trade-to-signal linkage
- counterfactual outcome judgment
- avoided-loss or missed-opportunity classification
- runtime deployment

---

## 4. Input contracts

## 4.1 Active Plan candidates

Canonical input:

```text
logs/csv/active_plan_paper_candidates.csv
```

Required headers:

```text
candidate_id
source_signal_id
timestamp_jst
candidate_type
side
```

At least one entry definition is required per row:

```text
entry_price
or
entry_zone_low + entry_zone_high
```

Optional but retained when present:

```text
active_primary_action
candidate_status
entry_mode
stop_loss
tp1
tp2
next_condition
active_subject_label
active_headline
symbol
```

Row requirements:

- `candidate_id` non-empty and unique by identity
- `source_signal_id` non-empty
- `timestamp_jst` parseable and timezone-consistent
- `side` is `long` or `short`
- entry zone is numerically valid
- when both bounds exist, normalize low <= high
- `stop_loss`, `tp1`, and `tp2` are optional numeric values
- explicit non-BTC symbol is rejected in P4 v1
- missing symbol is normalized to fixed `BTCUSDT`

The source CSV is existing unversioned evidence. P4 validates a required-header subset and does not rewrite it.

## 4.2 Intraperiod outcomes

Canonical input:

```text
logs/csv/active_plan_candidate_intraperiod_outcomes.csv
```

Required headers:

```text
candidate_id
outcome
```

Optional evidence:

```text
signal_id
timestamp_jst
entry_reached_time
first_exit_time
first_exit_reason
mfe_r
mae_r
```

Rules:

- one candidate may have zero or one canonical outcome row
- exact duplicates are ignored
- conflicting rows for the same candidate are input conflicts
- `no_ohlcv` is coverage failure, never win/loss
- `pending`, `timeout`, `ambiguous`, and `entry_reached` are not silently promoted to resolved outcomes

## 4.3 Optional OHLCV coverage input

P4 may accept an explicit local OHLCV CSV for row-level root-cause diagnosis.

Required fields when supplied:

```text
timestamp or timestamp_jst or timestamp_utc
high
low
```

P4 does not fetch market data and does not access any exchange API.

## 4.4 P3 evidence

Optional coverage inputs:

```text
logs/csv/manual_trade_episodes.csv
logs/csv/manual_trade_signal_links.csv
```

These are used only for coverage counts and later evidence availability. P4 does not rewrite or reinterpret their schemas.

---

## 5. Candidate identity and conflicts

Candidate fingerprint:

```text
sha256(normalized candidate business fields)
```

Duplicate behavior:

- same `candidate_id` + same fingerprint: duplicate skipped
- same `candidate_id` + different fingerprint: conflict
- conflict exits `3`
- no generated scenario output mutation on conflict

Candidate rows are sorted deterministically by:

```text
timestamp_jst
candidate_id
```

---

## 6. Setup-family normalization

P4 uses `setup_family` for grouping while retaining raw `candidate_type` in events.

Initial mapping:

| source candidate type | setup family |
|---|---|
| `active_limit_retest` | `limit_retest` |
| `active_market_small` | `market_entry` |
| `active_breakout_follow` | `breakout_follow` |
| `active_counter_scalp` | `counter_scalp` |

Unknown non-empty candidate types normalize to a safe lowercase snake-case value and only group with the same normalized value.

P4 does not rank setup families.

---

## 7. Scenario grouping contract

Method version:

```text
manual_scenario_normalization.v1
```

Default analysis parameters:

```text
max_update_gap_minutes = 360
max_scenario_age_hours = 24
zone_tolerance_bps = 25
invalidation_tolerance_bps = 50
```

These values are deduplication-analysis parameters, not entry thresholds or production trading settings.

A candidate may join an existing open scenario only when all are true:

1. same symbol
2. same side
3. same setup family
4. candidate timestamp is after or equal to the scenario's latest event
5. gap from latest event <= `max_update_gap_minutes`
6. age from initial detection <= `max_scenario_age_hours`
7. entry zones overlap after both are expanded by `zone_tolerance_bps`
8. if both invalidation prices exist, they are compatible within `invalidation_tolerance_bps`
9. candidate timestamp is not after a deterministic terminal boundary already established for the scenario

Terminal boundary may come from:

- first resolved TP/SL timestamp
- timeout timestamp
- expired-without-touch timestamp

A candidate matching:

- zero scenarios -> creates a new scenario
- exactly one scenario -> joins that scenario
- multiple scenarios -> remains unassigned with `grouping_status=ambiguous`; no hidden tie-breaker

Side reversal, setup-family change, incompatible zone, incompatible invalidation, terminal scenario, or excessive time gap creates a new scenario.

Small price updates alone do not create a new scenario when the grouping contract remains satisfied.

---

## 8. Deterministic scenario identity

Scenario ID:

```text
scenario_id = "scn_" + sha256(
  symbol
  + side
  + setup_family
  + first_candidate_timestamp_jst
  + normalized_initial_zone_low
  + normalized_initial_zone_high
  + normalized_initial_invalidation
  + scenario_method_version
)[:24]
```

Scenario event ID:

```text
scenario_event_id = "sce_" + sha256(
  candidate_id
  + candidate_fingerprint
  + grouping_status
  + scenario_method_version
)[:24]
```

Repeated builds with unchanged inputs and parameters must produce byte-identical scenario/event CSVs.

No execution-time timestamp is used in deterministic IDs.

---

## 9. Scenario lifecycle model

P4 lifecycle describes candidate and market-evidence state only.

Allowed lifecycle states:

```text
detected
updated
zone_touched
proxy_resolved
expired_without_touch
pending
coverage_missing
ambiguous_grouping
```

Mapping principles:

- first candidate -> `detected`
- later grouped candidate -> `updated`
- valid `entry_reached_time` -> `zone_touched`
- `tp1_first`, `tp2_first`, or `sl_first` -> `proxy_resolved`
- `not_entered` after completed timeout -> `expired_without_touch`
- `pending`, `timeout`, `ambiguous`, or open `entry_reached` remain explicitly unresolved/pending as defined in the scenario event
- `no_ohlcv` -> `coverage_missing`
- multi-scenario match -> `ambiguous_grouping`

P4 must not emit the following from proxy evidence:

```text
human_entered
human_skipped
human_watched
human_exited
human_took_profit
```

Those belong only to manual decision events.

`confirmed` is not inferred merely because an entry zone was touched.

---

## 10. Canonical scenario outputs

## 10.1 Scenario summary

Output:

```text
logs/csv/manual_scenarios.csv
```

Schema version:

```text
manual_scenario.v1
```

Columns:

```text
schema_version
scenario_id
symbol
side
setup_family
scenario_status
lifecycle_state
initial_candidate_id
latest_candidate_id
initial_signal_id
latest_signal_id
detected_at_utc
detected_at_jst
last_updated_at_utc
last_updated_at_jst
entry_zone_low
entry_zone_high
invalidation_price
tp1_price
tp2_price
candidate_event_count
source_signal_count
zone_touched_at_utc
zone_touched_at_jst
terminal_at_utc
terminal_at_jst
proxy_outcome
proxy_outcome_status
ohlcv_coverage_status
scenario_method_version
max_update_gap_minutes
max_scenario_age_hours
zone_tolerance_bps
invalidation_tolerance_bps
```

`scenario_status` values:

```text
active
resolved
expired
coverage_missing
ambiguous
```

## 10.2 Scenario events and candidate mapping

Output:

```text
logs/csv/manual_scenario_events.csv
```

Schema version:

```text
manual_scenario_event.v1
```

Columns:

```text
schema_version
scenario_event_id
scenario_id
candidate_id
candidate_fingerprint
source_signal_id
event_timestamp_utc
event_timestamp_jst
event_type
grouping_status
symbol
side
candidate_type
setup_family
active_primary_action
candidate_status
entry_mode
entry_price
entry_zone_low
entry_zone_high
invalidation_price
tp1_price
tp2_price
next_condition
intraperiod_outcome
entry_reached_time
first_exit_time
first_exit_reason
mfe_r
mae_r
ohlcv_coverage_status
ohlcv_gap_reason
reason_codes
scenario_method_version
```

`grouping_status` values:

```text
new_scenario
matched_existing
ambiguous
```

Ambiguous rows retain blank `scenario_id` and remain visible in coverage.

---

## 11. OHLCV coverage root causes

Canonical row-level categories:

```text
covered
no_ohlcv_input
candidate_timestamp_missing
candidate_before_ohlcv_start
candidate_after_ohlcv_end
candidate_window_gap
malformed_ohlcv
stale_ohlcv_range
unknown_gap
```

Rules:

- root-cause category is diagnostic, not trade outcome
- `no_ohlcv` rows never enter win/loss denominators
- stale source range is reported separately from candidate-specific window gaps
- missing or malformed candidate timestamps are input errors when the scenario builder reads the canonical candidate source
- if only an existing `no_ohlcv` outcome is available and no OHLCV input is supplied, use `no_ohlcv_input`

---

## 12. Manual decision-event model

P4 defines and implements local recording infrastructure but does not start the P8 live human trial.

Canonical output:

```text
logs/csv/manual_decision_events.csv
```

Schema version:

```text
manual_decision_event.v1
```

Columns:

```text
schema_version
decision_event_id
event_fingerprint
identity_scope
scenario_id
signal_id
mail_timestamp_jst
human_checked_at_utc
human_checked_at_jst
decision_stage
human_action
human_side
observed_price
planned_entry_price
planned_sl_price
planned_tp1_price
planned_tp2_price
reason_codes
manual_note
source
recorded_at_utc
supersedes_decision_event_id
record_status
```

### 12.1 Identity

At least one is required:

```text
scenario_id
signal_id
```

`scenario_id` is preferred after P4 scenario output exists.

`identity_scope`:

```text
scenario
signal_only
```

Decision event ID:

```text
decision_event_id = "mde_" + sha256(
  identity_scope
  + scenario_id
  + signal_id
  + human_checked_at_jst
  + decision_stage
  + human_action
  + human_side
  + supersedes_decision_event_id
)[:24]
```

Event fingerprint includes all normalized fields except `recorded_at_utc`.

### 12.2 Human action

Allowed actions:

```text
entered
watched_no_entry
skipped
exited
took_profit
adjusted_stop
cancelled_plan
```

Allowed stages:

```text
entry
management
exit
```

Allowed side:

```text
long
short
none
```

Examples of allowed reason codes:

```text
trigger_confirmed
trigger_missing
bad_setup
late
risk_too_high
side_unclear
defensive_subject
zone_not_reached
scenario_invalidated
profit_protection
manual_override
other
```

Reason codes are descriptive human input, not system truth.

### 12.3 Action consistency

- `entered` requires side long/short
- `watched_no_entry`, `skipped`, and `cancelled_plan` normally use side none or the reviewed side
- `exited`, `took_profit`, and `adjusted_stop` use stage management/exit
- planned price fields are optional Decimal strings
- malformed numeric values are rejected, never converted to zero
- zero is retained when explicitly supplied

### 12.4 Hindsight separation

The decision event records what the human decided at check time.

It does not contain a final `result` field.

The following must not be written as immediate decision truth:

```text
avoided_loss
missed_opportunity
tp1_success
sl_first
profitable
```

Those require later actual episode evidence or versioned counterfactual replay.

This overrides earlier drafts that placed action and final result in one row.

### 12.5 Corrections

Manual decision events are append-only.

- no in-place row editing by default
- correction uses a new event with `supersedes_decision_event_id`
- superseded event remains in source history
- `record_status` is `active` or `correction`
- correction target must exist

### 12.6 Privacy

- manual note maximum 280 Unicode characters
- normalize line breaks to spaces
- reject raw UID/account/private path/API-key-like content
- no raw exchange rows
- no private full path in stdout
- generated event CSV remains local and is not committed

---

## 13. Decision-event append semantics

Exact duplicate:

- same decision event ID and same fingerprint -> no-op
- exit `0`
- `duplicate_event=true`

Identity conflict:

- same event ID but different fingerprint without valid correction -> exit `3`
- no mutation

Write behavior:

- validate existing exact schema
- read and merge in memory
- write to same-filesystem temporary file
- replace target only after complete serialization
- preserve existing target on failure
- dry-run creates no directory/file

---

## 14. Coverage report

Canonical outputs:

```text
運用資料/reports/post_eval/manual_scenario_coverage_YYYYMMDD.md
logs/json/manual_scenario_coverage_YYYYMMDD.json
```

Generated/local policy follows existing report conventions.

Required metrics:

### Candidate and scenario identity

```text
candidate_input_rows
unique_candidate_rows
duplicate_candidate_rows
candidate_conflict_rows
assigned_candidate_rows
ambiguous_candidate_rows
scenario_count
candidate_to_scenario_compression_ratio
source_signal_count
signals_with_scenario_count
signal_to_scenario_coverage_rate
```

Compression definition:

```text
assigned candidate rows / scenario count
```

Also report:

```text
scenario_count / assigned candidate rows
```

as the independent-scenario rate.

### OHLCV and proxy coverage

```text
covered_candidate_rows
no_ohlcv_candidate_rows
pending_candidate_rows
resolved_proxy_candidate_rows
scenario_with_covered_evidence_count
scenario_with_resolved_proxy_count
ohlcv_gap_reason_counts
```

### Human decision coverage

```text
decision_event_count
scenario_with_decision_count
signal_only_decision_count
decision_action_counts
decision_stage_counts
scenario_decision_coverage_rate
```

When no decision file exists, report zero/absent coverage without claiming human inactivity.

### P3 evidence availability

When optional P3 files are supplied:

```text
scenario_signal_ids_with_high_medium_episode_link
scenario_count_with_actual_episode_evidence
```

This is evidence availability only. It does not prove the mail caused a trade.

---

## 15. CLI contracts

## 15.1 Build scenarios

```bash
./.venv312/bin/python tools/log_feedback.py build-manual-scenarios \
  --candidates logs/csv/active_plan_paper_candidates.csv \
  --intraperiod-outcomes logs/csv/active_plan_candidate_intraperiod_outcomes.csv \
  --scenarios-out logs/csv/manual_scenarios.csv \
  --events-out logs/csv/manual_scenario_events.csv \
  --max-update-gap-minutes 360 \
  --max-scenario-age-hours 24 \
  --zone-tolerance-bps 25 \
  --invalidation-tolerance-bps 50 \
  --stdout-json
```

Optional:

```text
--ohlcv <local csv>
--replace-output
--dry-run
```

## 15.2 Record human decision

```bash
./.venv312/bin/python tools/log_feedback.py record-manual-decision \
  --scenario-id <scenario_id> \
  --signal-id <signal_id> \
  --human-checked-at-jst <ISO timestamp> \
  --decision-stage entry \
  --human-action watched_no_entry \
  --human-side none \
  --reason-code trigger_missing \
  --output-csv logs/csv/manual_decision_events.csv \
  --stdout-json
```

Optional:

```text
--mail-timestamp-jst
--observed-price
--planned-entry-price
--planned-sl-price
--planned-tp1-price
--planned-tp2-price
--manual-note
--supersedes-decision-event-id
--scenarios <manual_scenarios.csv>
--dry-run
```

`--reason-code` may repeat.

## 15.3 Build coverage report

```bash
./.venv312/bin/python tools/log_feedback.py build-manual-scenario-coverage \
  --candidates logs/csv/active_plan_paper_candidates.csv \
  --scenarios logs/csv/manual_scenarios.csv \
  --scenario-events logs/csv/manual_scenario_events.csv \
  --intraperiod-outcomes logs/csv/active_plan_candidate_intraperiod_outcomes.csv \
  --decision-events logs/csv/manual_decision_events.csv \
  --output-json logs/json/manual_scenario_coverage_20260710.json \
  --output-md 運用資料/reports/post_eval/manual_scenario_coverage_20260710.md \
  --stdout-json
```

Optional P3 inputs:

```text
--episodes
--episode-links
```

All CLI stdout uses one compact JSON object plus newline.

No full local paths, raw rows, or manual notes are printed.

---

## 16. Exit codes

| code | meaning |
|---:|---|
| 0 | success, including duplicate/no-op |
| 1 | unexpected internal error |
| 2 | missing/invalid input or schema |
| 3 | candidate/event identity conflict |
| 4 | existing generated output schema mismatch or I/O failure |

---

## 17. Output replacement and legacy handling

Derived scenario/event outputs are deterministic rebuilds.

- existing exact current schema -> rebuild allowed
- existing wrong/legacy schema -> exit `4`
- `--replace-output` explicitly permits generated-output replacement
- scenario and event outputs are replaced as one process-level transaction with rollback
- decision-event source truth is never replaced by scenario rebuild
- coverage JSON/Markdown use same-filesystem temporary replacement

No absolute power-loss atomicity claim is made.

---

## 18. Required tests

### Scenario identity

1. one candidate creates one scenario
2. overlapping zone update within time gap joins the same scenario
3. different side creates a new scenario
4. different setup family creates a new scenario
5. non-overlapping zone creates a new scenario
6. excessive update gap creates a new scenario
7. excessive total scenario age creates a new scenario
8. incompatible invalidation creates a new scenario
9. candidate after terminal boundary creates a new scenario
10. candidate matching multiple scenarios remains ambiguous and unassigned
11. no hidden timestamp or lexical tie-break
12. deterministic scenario/event IDs and byte ordering
13. same candidate ID/same fingerprint is duplicate
14. same candidate ID/different fingerprint exits `3`
15. missing candidate identity/timestamp/side/entry definition exits `2`
16. explicit non-BTC symbol rejected
17. zero numeric values retained

### Lifecycle and proxy separation

18. first member is detected
19. later member is updated
20. entry-reached evidence yields zone_touched, not human_entered
21. tp/sl outcomes remain proxy outcomes
22. no_ohlcv becomes coverage_missing, not loss
23. pending/unresolved remain unresolved
24. no human action is inferred from candidate outcome

### Coverage diagnosis

25. OHLCV fully covers candidate window
26. candidate before source start
27. candidate after source end
28. window gap inside source range
29. no OHLCV input
30. malformed OHLCV
31. stale range
32. compression and independent-scenario rates use documented denominators
33. signal-to-scenario coverage uses unique signal IDs
34. ambiguous/unassigned candidates remain visible

### Decision events

35. minimal scenario decision append
36. signal-only decision append
37. exact duplicate is no-op
38. identity conflict exits `3`
39. correction requires existing superseded ID
40. entered requires long/short
41. invalid stage/action combination rejected
42. malformed timestamp rejected
43. malformed numeric rejected
44. numeric zero retained
45. note length and sensitive-content validation
46. no final result/avoided-loss/missed-opportunity field exists
47. dry-run writes nothing
48. write failure preserves prior file
49. wrong existing schema exits `4`
50. full private path/manual note not leaked to stdout

### Coverage report and CLI

51. no decision file reports absent/zero coverage without claiming no human action
52. action and stage counts
53. scenario decision coverage denominator
54. optional P3 evidence availability count
55. build scenarios CLI subprocess
56. record decision CLI subprocess
57. coverage CLI subprocess
58. compact stdout and safety boundary
59. existing P2/P3 targeted tests remain passing

---

## 19. Preferred implementation structure

```text
src/feedback/manual_scenario_normalizer.py
src/feedback/manual_decision_events.py
src/feedback/manual_scenario_coverage.py
```

CLI wiring only:

```text
tools/log_feedback.py
```

Existing trade-analysis modules are read-only inputs for P4:

```text
src/trade/active_plan_intraperiod.py
src/trade/judgment_self_review.py
```

Do not move new scenario business logic into the already-large CLI file.

---

## 20. Allowed implementation files

```text
tools/log_feedback.py
src/feedback/__init__.py
src/feedback/manual_scenario_normalizer.py
src/feedback/manual_decision_events.py
src/feedback/manual_scenario_coverage.py
tests/test_manual_scenario_normalizer.py
tests/test_manual_decision_events.py
tests/test_manual_scenario_coverage.py
chatgpt/specs/active/20260710_manual_scenario_coverage_decision_events.md
```

P4 must not modify:

```text
src/trade/active_plan.py
src/trade/active_plan_intraperiod.py
src/trade/judgment_self_review.py
src/trade/execution_gate.py
src/trade/phase1b_lite.py
src/trade/opportunity_gate.py
src/notification/trigger.py
notification sending code
runtime/launchd files
```

---

## 21. Safety and privacy

Hard requirements:

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no exchange API
- no account/private/order endpoint
- no API keys/secrets
- no runtime restart
- no launchd modification
- no live mail behavior change
- no gate/threshold/scoring change
- no raw exchange export read or commit
- no `paper_positions.csv` integration
- generated scenario and decision files remain local
- no candidate row count interpreted as trade opportunity count
- no `no_ohlcv` interpreted as win/loss
- no human intent inferred from exchange or proxy evidence

---

## 22. Completion criteria

P4 spec is complete when:

- scenario grouping identity is deterministic
- ambiguous grouping has no hidden tie-break
- candidate, proxy, human, and actual evidence are separate
- canonical scenario/event schemas are fixed
- OHLCV root-cause categories and denominators are fixed
- decision-event schema is append-only and hindsight-safe
- CLI, exit codes, replacement, privacy, and tests are fixed
- P5 classifier has a stable scenario input contract

P4 implementation is complete when:

- scenario and event builders pass targeted tests
- duplicate compression and signal mapping are measurable
- no_ohlcv root causes are reported
- decision-event recorder is safe and idempotent
- coverage report is deterministic
- P2/P3 regressions remain passing
- ChatGPT reviews source and tests

---

## 23. Archive condition

Archive after:

1. scenario normalizer implemented
2. decision-event recorder implemented
3. coverage report implemented
4. targeted tests pass
5. no source/gate/notification/runtime behavior changed
6. no private/raw data is in diff
7. ChatGPT reviews the implementation
8. P5 offline classifier spec is selected explicitly

Archive destination:

```text
chatgpt/specs/archive/20260710_manual_scenario_coverage_decision_events.md
```
