# Active Plan Intraperiod Outcome Specification

## 1. Purpose

Define the intraperiod outcome model for Active Plan candidates before any source-code implementation.

The specification converts the current forward-close-based candidate evaluation into a path-based evaluation that can observe the actual 15m price sequence after each candidate is emitted.

## 2. Scope

This specification covers:

- Active Plan candidate rows produced by the existing candidate logging flow
- intraperiod evaluation against 15m OHLCV data
- outcome classification for entry, exit, timeout, and unresolved cases
- the shape of the future outcome CSV
- the acceptance criteria for helper, fixture test, builder, and CLI work

This specification does not cover:

- source code changes
- daily-sync wiring
- connection to `paper_positions.csv`
- live trading or API access

## 3. Inputs

The evaluator must accept the following inputs:

- `logs/csv/active_plan_candidates.csv`
- the corresponding 15m OHLCV sequence for each candidate timestamp

The evaluator must preserve the candidate identity fields already present in the input CSV, including:

- signal identity
- timestamp
- candidate identity
- candidate type
- action label
- side
- entry mode
- entry and risk prices when available

If a required field is missing, the evaluator must leave the derived column blank or mark the row as unresolved rather than inventing a value.

## 4. Outcome states

Each candidate must be assigned exactly one top-level outcome state:

- `entry_reached`
- `not_entered`
- `tp1_first`
- `tp2_first`
- `sl_first`
- `timeout`
- `ambiguous`
- `pending`
- `no_ohlcv`

Meanings:

- `entry_reached`: the candidate entry band was touched during the observation window.
- `not_entered`: the observation window ended without touching the entry band.
- `tp1_first`: TP1 was touched before SL after entry was reached.
- `tp2_first`: TP2 was touched before SL after entry was reached.
- `sl_first`: SL was touched before TP1 / TP2 after entry was reached.
- `timeout`: entry was reached, but no exit condition was reached before the observation window ended.
- `ambiguous`: the OHLCV path does not allow a reliable first-touch decision.
- `pending`: the observation window is incomplete for a final verdict.
- `no_ohlcv`: the required OHLCV data could not be loaded.

## 5. Intraperiod evaluation rules

The evaluator must follow these rules:

1. Use only price bars at or after the candidate timestamp.
2. Determine entry reach from the candidate entry band.
3. Once entry is reached, evaluate the first-touch order of TP and SL.
4. Use the side of the candidate to interpret high / low movement symmetrically.
5. If the same bar touches both TP and SL and the first touch cannot be determined, mark the candidate `ambiguous`.
6. If the bar sequence ends before a definitive resolution, mark the candidate `pending`.
7. If no bar data exists for the requested interval, mark the candidate `no_ohlcv`.

The evaluator must not reinterpret the candidate as a different action or change the candidate type.

## 6. Derived metrics

The output row should include derived metrics that describe the price path after the candidate is emitted:

- `entry_reached_time`
- `first_exit_time`
- `first_exit_reason`
- `mfe_price`
- `mae_price`
- `mfe_r`
- `mae_r`

Rules:

- `mfe_price` and `mae_price` are measured from the candidate entry price.
- `mfe_r` and `mae_r` are normalized by the candidate stop distance when a stop price is available.
- If the stop price is unavailable, the evaluator may leave the R-normalized fields blank.

## 7. Output CSV

The future implementation must write:

- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`

Each row must carry the original candidate identity fields plus the outcome columns above.

Minimum output columns:

- `candidate_id`
- `signal_id`
- `timestamp_jst`
- `candidate_type`
- `active_primary_action`
- `side`
- `entry_mode`
- `entry_price`
- `stop_price`
- `tp1_price`
- `tp2_price`
- `outcome`
- `entry_reached_time`
- `first_exit_time`
- `first_exit_reason`
- `mfe_price`
- `mae_price`
- `mfe_r`
- `mae_r`
- `notes`

## 8. Fixture coverage

The future fixture set must include at least:

- long candidate that reaches entry and then TP
- long candidate that reaches entry and then SL
- short candidate that reaches entry and then TP
- short candidate that reaches entry and then SL
- candidate that never reaches entry
- candidate that times out after entry
- candidate with ambiguous same-bar TP / SL touch
- candidate with missing OHLCV

## 9. Acceptance criteria

This specification is ready when:

- the helper implementation can follow it without extra product decisions
- the fixture set can be written directly from it
- the builder can be added later without changing the rules above
- the CLI can be added later without changing the rules above
- daily-sync integration remains deferred until helper, fixture, and builder layers are stable

## 10. Follow-up sequence

After this specification is frozen, the implementation order should be:

1. helper functions
2. fixture tests
3. builder
4. CLI
5. report wiring

No source-code changes are part of this specification task.
