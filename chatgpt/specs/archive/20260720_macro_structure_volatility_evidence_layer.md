# M1 Macro Structure / Volatility Evidence Layer — Active Specification

## Metadata

- work_id: `BTCFX-20260720-MACRO-STRUCTURE-VOLATILITY-EVIDENCE-SPEC`
- status: design ready for human review; source implementation not yet authorized
- phase: M1 offline macro evidence before P9 proposal generation
- change_class: deterministic offline replay and evidence only
- created_at: `2026-07-20`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- parent_plan: `docs/operations/strategy/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Objective

Build a deterministic offline evidence layer that measures higher-timeframe structure, reliable support/resistance, range midpoint behavior, and volatility expansion before any production UI or trading-policy change.

The task must answer:

1. What broad structural range or trend was knowable at each event time?
2. Where was price inside that structure?
3. Which levels had repeatable evidence of holding, rejecting, breaking, or reclaiming?
4. Does midpoint / equilibrium behavior predict volatility expansion or directional travel to the next reliable level?
5. Which large moves were missed by the existing notification and turning-precursor layers?
6. Can the system separate current tactical direction from next-regime risk?
7. Is there enough balanced validation evidence to justify a later Big Chance or UI proposal?

## 2. Non-goals

M1 does not:

- edit `src/analysis/structural_priority.py`
- edit `src/analysis/big_chance.py`
- edit current support/resistance production generation
- edit `src/notification/detail_page.py`
- change scoring
- change thresholds
- change `trade_execution_gate`
- change `phase1b_lite_gate`
- change `opportunity_gate`
- change notification triggers or mail behavior
- change launchd or runtime
- send a manual notification
- generate an entry instruction
- import private exchange/account data
- automatically mutate production code or configuration
- claim profitability from public OHLCV proxy evidence

## 3. Evidence basis

Current source review establishes:

- `structural_priority.v1` is a fixed 4H/1H trend and structure score, not a complete structural location model
- current support/resistance context selects nearest levels but does not maintain stable level identity or reliability history
- Big Chance uses failed-thesis and short-term activation evidence without an explicit broad-range midpoint or next structural target contract
- the current turning precursor replay evaluates 1H/2H/4H material moves but does not evaluate broad midpoint acceptance, travel corridors, or level reliability

The user-supplied live example is a product-design case only. It must not be hard-coded or used as the sole tuning case.

## 4. Design doctrine

### 4.1 Event-time only

All structure, level, and forecast fields must use only candles closed at or before the event timestamp.

Future candles are reserved exclusively for outcome resolution.

### 4.2 Stable structure before prediction

The replay must first construct stable level and structure identities. It must not recalculate unrelated levels in a way that makes every signal a new structure.

### 4.3 Separate three forecasts

Output separate records for:

- macro structure and location
- tactical context copied from the event-time signal
- next-regime / expansion risk

A tactical Long and a next-regime Short risk may coexist.

### 4.4 Symmetry

Long/up and Short/down logic must be mirrored unless a difference is explicitly justified by measured evidence in a later proposal.

### 4.5 No automatic production mutation

M1 may conclude only:

- `insufficient_evidence`
- `continue_shadow_collection`
- `eligible_for_next_design_proposal`

It may never apply the proposal.

## 5. Inputs

Required explicit inputs:

- event-time signal context CSV compatible with the accepted signal/trade context
- 15-minute public OHLCV for outcome resolution
- 1-hour OHLCV for structure confirmation
- 4-hour OHLCV for higher-timeframe structure

Optional:

- daily OHLCV only when the existing public fetcher supports it through the accepted data path and tests cover absence
- current notification records through the supplied signal context
- current turning precursor events for comparative diagnostics

Rules:

- no broad log-directory scan
- all local input paths are explicit
- public fetch, when implemented, must reuse `src.data.fetcher.fetch_klines` and accepted public-market configuration
- no private, account, position, or order endpoint
- fetched raw market data remains generated/local and uncommitted
- the replay must record source metadata and input fingerprints

Minimum signal fields:

- `signal_id`
- `timestamp_utc`
- `timestamp_jst`
- `current_price`
- `was_notified`
- `notification_kind`
- `bias`
- `phase`
- `market_regime`
- `signals_4h`
- `signals_1h`
- `signals_15m`
- `structural_priority_long`
- `structural_priority_short`
- `structural_priority_side`
- `structural_priority_strength`
- `market_map_flags`
- `market_map_primary_state`
- `active_level_role`
- `level_flip_state`
- `failed_breakout_state`
- `trend_flip_state`
- `nearest_major_support`
- `nearest_major_resistance`
- `atr_15m_value`
- `atr_ratio`
- `volume_ratio`
- `primary_setup_side`
- `primary_setup_status`
- `primary_setup_reason`
- `confidence_direction_shadow`
- `confidence_execution_shadow`
- `confidence_wait_shadow`

Optional missing fields must be reported and must not be imputed as favorable evidence.

## 6. Structure construction contract

### 6.1 Confirmed pivots

Detect event-time confirmed pivots separately on 1H and 4H OHLCV.

A pivot may be confirmed only after the required right-side closed candles exist at the event time. The algorithm must not use later candles to backdate an unconfirmed pivot.

The first implementation may use bounded pivot-window candidates supplied as CLI parameters. Defaults are replay parameters, not production thresholds.

### 6.2 Level clustering

Cluster overlapping pivot prices into structural zones.

The cluster distance must be expressed using event-time ATR or a bounded percentage, with explicit parameter output.

Each cluster receives a stable deterministic `level_id` from:

- method version
- side
- normalized center bucket
- first confirmed timestamp
- source timeframes

Minor boundary movement must not create a new level identity unless the cluster membership changes materially.

### 6.3 Level lifecycle

For each level, derive event-time lifecycle facts:

- first confirmed
- active
- touched
- rejected
- broken
- accepted beyond
- false break reclaimed
- retired

A break and acceptance must be separate from an intrabar pierce.

### 6.4 Level reliability

Produce `level_reliability.v1` with at least:

- `level_id`
- `side`
- `low`
- `high`
- `center`
- `source_timeframes`
- `first_seen_at`
- `last_confirmed_at`
- `touch_count`
- `clean_rejection_count`
- `break_count`
- `false_break_reclaim_count`
- `median_reaction_atr`
- `median_hold_hours`
- `recency_score`
- `cross_timeframe_confluence`
- `reliability_score`
- `reliability_band`
- `reason_codes`

Reliability must use only historical interactions available before the event.

### 6.5 Broad structure envelope

At each signal event, derive one primary broad structure when evidence permits.

Fields:

- `structure_id`
- `structure_state`
- `range_low`
- `range_high`
- `range_midpoint`
- `lower_quartile`
- `upper_quartile`
- `location_percentile`
- `price_location`
- `nearest_reliable_support_id`
- `nearest_reliable_resistance_id`
- `next_upside_target_id`
- `next_downside_target_id`
- `upside_travel_atr`
- `downside_travel_atr`
- `data_quality_status`

Fail closed to `insufficient` when a defensible envelope cannot be established.

## 7. Midpoint and travel-corridor events

Generate event-time candidate events:

- `MIDPOINT_APPROACH`
- `MIDPOINT_COMPRESSION`
- `MIDPOINT_REJECTION_UP`
- `MIDPOINT_REJECTION_DOWN`
- `MIDPOINT_ACCEPTANCE_UP`
- `MIDPOINT_ACCEPTANCE_DOWN`
- `RANGE_EDGE_REJECTION_UP`
- `RANGE_EDGE_REJECTION_DOWN`
- `RANGE_EDGE_BREAK_ACCEPTANCE_UP`
- `RANGE_EDGE_BREAK_ACCEPTANCE_DOWN`
- `OPEN_TRAVEL_CORRIDOR_UP`
- `OPEN_TRAVEL_CORRIDOR_DOWN`

### 7.1 Midpoint corridor

The midpoint corridor width is a replay parameter based on event-time ATR and/or structure width.

Proximity alone is not an expansion signal.

### 7.2 Compression evidence

Compression may use only event-time values such as:

- recent realized high-low range versus ATR
- repeated closes inside the midpoint corridor
- lower short-horizon realized volatility versus the preceding window
- declining candle-body expansion

### 7.3 Acceptance evidence

Acceptance requires closed-candle evidence beyond the midpoint or structure edge. The number of closes is a bounded replay parameter.

### 7.4 Open travel corridor

An open corridor exists only when:

- a directional acceptance or rejection event exists
- distance to the next reliable level exceeds a bounded ATR minimum
- no higher-reliability opposing level lies inside the corridor

## 8. Forecast records

One event may produce multiple forecast families. Keep them separate.

### 8.1 Macro direction

- side: UP / DOWN / BALANCED / NONE
- target level
- invalidation level or condition
- horizon: 3H / 6H / 12H

### 8.2 Expansion

- expansion expected: true / false
- expansion side: UP / DOWN / BOTH / NONE
- expected time band
- first structural target

### 8.3 Level behavior

For the next tested reliable level:

- HOLD_REJECT
- BREAK_ACCEPT
- FALSE_BREAK_RECLAIM
- NOT_TESTED
- UNRESOLVED

### 8.4 Next-regime

Fields:

- `current_tactical_side`
- `current_structural_side`
- `weakening_thesis_side`
- `candidate_next_regime_side`
- `activation_condition_codes`
- `invalidation_condition_codes`
- `first_structural_target_id`
- `evidence_confidence`

This output is not a replacement for current Big Chance. It is offline evidence for a later design.

## 9. Outcome contract

Use future closed 15-minute bars only after the event timestamp.

Horizons:

- 1H for early reaction
- 3H
- 6H
- 12H
- 24H only when continuous data is available

Calculate:

- maximum upward excursion
- maximum downward excursion
- excursion in event-time ATR
- realized range expansion
- first material-move timestamp
- first target-level touch
- adverse excursion before target
- midpoint recross count
- next reliable level reached
- level hold / break / reclaim outcome

Material expansion threshold must be explicit and replay-only. Candidate defaults may compare:

```text
max(k * ATR_15M, event_price * p)
```

with bounded `k` and `p` values declared in the report.

Outcome labels:

- `large_up`
- `large_down`
- `balanced_no_expansion`
- `whipsaw_both`
- `target_up_reached`
- `target_down_reached`
- `level_hold_reject`
- `level_break_accept`
- `false_break_reclaim`
- `unresolved`

## 10. Episode deduplication

Do not count every hourly signal as a new opportunity.

A new macro event episode begins when:

- the event family was absent on the preceding eligible snapshot
- event side changes
- structure identity changes
- the prior event was resolved or invalidated
- a configurable minimum separation has passed after the prior episode start

Small level-boundary updates inside the same structure do not create a new episode.

## 11. Baselines and comparisons

Compare at minimum:

- current notification baseline
- current turning precursor combined policy
- major-level-only baseline
- midpoint-only hypothesis
- midpoint + compression
- midpoint + acceptance
- reliable-level + open-corridor
- combined macro expansion candidate

The replay must not rank by precision alone.

## 12. Metrics

For each policy and forecast family:

- episodes
- resolved episodes
- directional precision
- large-move recall
- expansion precision
- expansion recall
- target-hit rate
- false-warning rate
- opposite-move rate
- whipsaw rate
- unresolved rate
- median lead time
- median favorable excursion ATR
- median adverse excursion ATR
- median travel-to-target time
- duplicate compression ratio
- missed independent large moves
- burden per JST day

Required splits:

- UP / DOWN
- trend / range / transition
- near lower edge / lower half / midpoint / upper half / upper edge / outside
- level reliability low / medium / high
- 3H / 6H / 12H horizon

## 13. Chronological validation

Use walk-forward chronological evaluation.

At minimum report:

- calibration window
- validation window
- final holdout window when sample size permits

No event may use future outcomes to choose its own parameter set.

A parameter candidate must be fitted or selected using prior windows and evaluated on later windows.

## 14. Proposal-quality gates

Set `eligible_for_next_design_proposal` only when all are true:

- validation is established across multiple JST dates
- both UP and DOWN have sufficient resolved events
- at least two price-location groups have sufficient evidence
- the result does not depend materially on one pinned case
- validation improves at least one primary objective without unacceptable degradation in the others
- false-warning and opposite-move rates remain within declared bounds
- level reliability calibration is stable across windows
- input coverage and continuity pass

The implementation must expose exact gate reasons.

These gates authorize only a later design proposal, not production change.

## 15. Missed-move diagnostics

Create an independent inventory of realized large moves.

For each missed move report:

- opportunity ID
- direction
- start timestamp
- material-move timestamp
- move size in ATR
- structure state and price location before the move
- nearest reliable levels
- whether midpoint, edge, compression, acceptance, or open-corridor evidence existed
- whether current notification fired
- whether current turning precursor fired
- candidate root-cause classification

Root-cause labels:

- `structure_not_established`
- `reliable_level_missing`
- `midpoint_event_missing`
- `acceptance_event_missing`
- `travel_corridor_not_recognized`
- `precursor_policy_too_strict`
- `correct_no_signal`
- `data_unresolved`

## 16. Outputs

Use atomic replacement and deterministic sorting.

### Event CSV

Suggested:

`macro_structure_volatility_events.csv`

### Level CSV

Suggested:

`macro_level_reliability.csv`

### Missed-move CSV

Suggested:

`macro_missed_move_diagnostics.csv`

### JSON summary

Suggested:

`macro_structure_volatility_replay.json`

Include:

- method and schema versions
- source fingerprints and coverage
- method parameters
- structure and level counts
- policy metrics
- split metrics
- chronological windows
- proposal gates
- top misses
- top false warnings
- recommendation status
- safety boundary

### Markdown report

Suggested:

`macro_structure_volatility_replay.md`

Required sections:

1. Executive result
2. Structure coverage
3. Reliable-level calibration
4. Midpoint / equilibrium hypothesis
5. Expansion and target metrics
6. Current notification and precursor comparison
7. UP / DOWN and regime splits
8. Price-location splits
9. Top missed large moves
10. Top false warnings
11. Walk-forward validation
12. Proposal gate result
13. Limitations
14. Safety boundary

## 17. CLI contract

Add one report-only command to the existing feedback CLI:

```text
replay-macro-structure-volatility
```

Required explicit-file arguments:

- `--signals`
- `--ohlcv-15m`
- `--ohlcv-1h`
- `--ohlcv-4h`
- `--output-events-csv`
- `--output-levels-csv`
- `--output-misses-csv`
- `--output-json`
- `--output-md`

Optional:

- public-fetch flags for each timeframe only when implemented through the accepted fetcher
- `--cutoff-utc`
- bounded method parameters
- `--replace-output`
- `--stdout-json`

Rules:

- no directory scanning
- no mail
- no runtime operation
- compact stdout without raw event rows
- existing outputs remain intact on failure

## 18. Allowed implementation files

Proposed bounded scope after human approval:

- new: `src/feedback/macro_structure_volatility_replay.py`
- `tools/log_feedback.py`
- new: `tests/test_macro_structure_volatility_replay.py`
- `tests/test_log_feedback.py` only for the new CLI route
- this spec, archived after acceptance
- `docs/operations/ai-orchestration/NEXT_ACTION.md` only when posture changes

Do not edit production analysis, scoring, gate, notification, mail, runtime, deploy, or UI files in M1.

## 19. Required tests

- event-time pivot confirmation without future leakage
- stable level clustering and identity
- mirrored support/resistance behavior
- level touch / reject / break / accept / reclaim lifecycle
- reliability uses past interactions only
- structure envelope and midpoint
- fail-closed insufficient structure
- price-location classification
- midpoint approach, compression, rejection, and acceptance
- open travel corridor
- separate tactical and next-regime output
- 1H / 3H / 6H / 12H outcomes
- level behavior outcomes
- independent realized-move inventory
- episode deduplication
- chronological walk-forward split
- proposal gates
- missing and discontinuous OHLCV
- deterministic IDs, sort, and rerun
- atomic rollback
- privacy-safe compact summary
- CLI explicit paths
- CLI missing timeframe input
- CLI malformed structured signal fields
- CLI replace behavior

## 20. Validation

After source implementation is separately authorized:

```bash
./.venv312/bin/python -m unittest tests.test_macro_structure_volatility_replay
./.venv312/bin/python -m unittest <targeted log_feedback CLI tests>
./.venv312/bin/python tools/log_feedback.py replay-macro-structure-volatility <explicit fixture arguments> --stdout-json
git diff --check
```

One bounded local replay may follow targeted tests. Generated market data and outputs remain local and uncommitted.

## 21. Success criteria

M1 is complete when:

- stable event-time macro structures and levels are produced
- reliability is measured without hindsight leakage
- midpoint and open-corridor hypotheses are evaluated rather than assumed
- forecasts are resolved over 3H / 6H / 12H
- current notification and precursor baselines are compared on the same opportunities
- missed large moves are classified by root cause
- recommendation status is deterministic
- no production behavior changed

## 22. Next phases after acceptance

M1 acceptance permits only one of:

- continue offline collection
- create an optional P8 auxiliary shadow spec
- create a bounded Big Chance next-regime redesign proposal

It does not permit UI, notification, scoring, threshold, gate, or runtime changes automatically.

## 23. Human authorization and thread milestone

- authorized_at: `2026-07-20`
- authorization: M1 source implementation is approved
- immediate_work_id: `BTCFX-20260720-MACRO-STRUCTURE-VOLATILITY-EVIDENCE-IMPLEMENTATION`
- implementation boundary: M1 only under this active spec
- broader thread milestone: complete the safe shadow/self-improvement route through M5 when each preceding phase is accepted and the next phase receives its own bounded spec

The broader milestone is:

```text
M1 offline macro evidence
→ M2 optional P8 macro shadow
→ M3 Big Chance next-regime shadow contract
→ M4 chart-first shadow HTML
→ M5 offline champion/challenger proposal engine
```

This authorization does not permit Codex to skip phase review, invent later-phase requirements, or edit production behavior under the M1 task.

Mandatory stop boundary:

- no M6 runtime apply
- no live notification or mail behavior change
- no production score, gate, threshold, or classifier mutation
- no automatic adoption of an AI proposal
- no API, account, position, or order operation

After M1 implementation and bounded replay, ChatGPT must review the evidence before choosing and specifying M2.


---

## 23. Research-backed scope correction and precedence

This section supersedes any conflicting midpoint-first wording in Sections 1-22.

Research basis:

`docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`

### 23.1 Mandatory M1 core

M1 must prioritize:

1. event-time confirmed 1H/4H pivots
2. stable structural-zone clustering and deterministic level identity
3. support/resistance/role-flip lifecycle
4. event-time reliability history
5. current position relative to reliable levels
6. rejection, break, closed-candle acceptance, and false-break/reclaim events
7. next reliable target and intervening obstruction
8. realized-volatility state and persistence
9. independent large-move and jump-like opportunity inventory
10. missed-move root-cause diagnostics
11. chronological walk-forward validation

A defensible reliable-level layer is required for M1 acceptance. Midpoint behavior is not.

### 23.2 Corrected expansion doctrine

The implementation must not encode either of the following as a fact:

```text
midpoint causes volatility expansion
low volatility must soon expand
```

Instead, M1 separates:

- volatility state
- expansion risk
- directional activation
- first reliable target

Compression may contribute to expansion-risk evaluation only when tested alongside independent event-time evidence such as:

- interaction with a reliable structural boundary
- repeated one-sided tests
- diminishing rejection distance
- directional close concentration
- order-flow imbalance
- aggressive-side participation
- depth asymmetry
- spread or liquidity deterioration
- clean rejection
- break and closed-candle acceptance
- false break and reclaim

Unavailable microstructure fields must be marked unavailable and must not be imputed as favorable.

### 23.3 Primary event families

The primary required event families are revised to:

- `RELIABLE_LEVEL_APPROACH`
- `RELIABLE_LEVEL_REJECTION_UP`
- `RELIABLE_LEVEL_REJECTION_DOWN`
- `LEVEL_BREAK_ACCEPTANCE_UP`
- `LEVEL_BREAK_ACCEPTANCE_DOWN`
- `FALSE_BREAK_RECLAIM_UP`
- `FALSE_BREAK_RECLAIM_DOWN`
- `REPEATED_TEST_PRESSURE_UP`
- `REPEATED_TEST_PRESSURE_DOWN`
- `STRUCTURAL_COMPRESSION`
- `OPEN_TRAVEL_CORRIDOR_UP`
- `OPEN_TRAVEL_CORRIDOR_DOWN`

When supported by supplied event-time inputs, add auxiliary evidence groups:

- `ORDER_FLOW_PRESSURE_UP`
- `ORDER_FLOW_PRESSURE_DOWN`
- `LIQUIDITY_FRAGILITY`

### 23.4 Optional equilibrium features

The former `MIDPOINT_*` family is renamed as optional `EQUILIBRIUM_*` exploratory features.

They may describe:

- lower half
- equilibrium area
- upper half
- equilibrium acceptance, rejection, or recross

Rules:

- optional for implementation and acceptance
- no direction from equilibrium proximity alone
- no expansion forecast from equilibrium proximity alone
- no privileged ranking or proposal gate
- no production use in M1
- remove from later design if it adds no stable out-of-sample value after controlling for reliable levels, volatility state, and activation evidence

### 23.5 Structural pressure contract

If implemented, `structural_pressure` is an explanatory evidence bundle, not a physical stored-energy claim and not an entry permission.

Store evidence groups separately:

- repeated-test evidence
- rejection-distance trend
- close-location concentration
- directional close imbalance
- order-flow/trade imbalance
- aggressive-side participation
- depth imbalance
- liquidity/spread deterioration
- opposing-side failure

The replay must report incremental value by evidence group and must not collapse all inputs into an uninterpretable score as the only output.

### 23.6 Revised baselines

Compare at minimum:

- current notification baseline
- current turning precursor combined policy
- reliable-level rejection baseline
- reliable-level break/acceptance baseline
- false-break/reclaim baseline
- compression-only diagnostic baseline
- reliable-level plus pressure/imbalance candidate
- reliable-level plus acceptance plus open-corridor candidate

Compression-only is a diagnostic comparator and cannot be the preferred proposal merely because it has high recall.

### 23.7 Revised missed-move root causes

Use at least:

- `structure_not_established`
- `reliable_level_missing`
- `level_reliability_miscalibrated`
- `rejection_event_missing`
- `break_acceptance_missing`
- `false_break_reclaim_missing`
- `pressure_or_imbalance_unavailable`
- `pressure_or_imbalance_not_recognized`
- `travel_corridor_not_recognized`
- `volatility_regime_misclassified`
- `precursor_policy_too_strict`
- `correct_no_signal`
- `data_unresolved`

Equilibrium-related root causes are optional diagnostics only.

### 23.8 Revised success criteria

M1 is accepted only when:

- stable reliable levels are produced without future leakage
- reliability uses only prior interactions
- lifecycle outcomes are reproducible
- expansion and direction are measured separately
- activation is not inferred from compression alone
- target travel is tied to the next reliable opposing level
- current baselines are compared on the same independent opportunities
- UP/DOWN, regime, volatility-state, and reliability splits are reported
- optional equilibrium results are clearly isolated
- no production behavior changes

### 23.9 Authorization status

Source implementation remains authorized for M1 within the corrected scope.

Codex must read the research-basis document before implementation. If the original spec and this section conflict, this section and the research-basis document control.


---

## 24. Acceptance record — 2026-07-21

M1 is accepted as a deterministic offline/report-only evidence layer through reported commit `663288b`.

Accepted completion areas:

- stable event-time 1H/4H levels without future leakage
- deterministic level identity and role-aware lifecycle
- prior-only reliability history
- current reliable-level location, target, and obstruction evidence
- separate volatility state, expansion risk, and directional activation
- rejection, break, closed-candle acceptance, reclaim, pressure, and corridor evidence
- independent UP, DOWN, and BOTH opportunity inventory
- per-policy event-time episode deduplication
- same-opportunity metrics and chronological validation gates
- explicit fail-closed missed-move root-cause diagnosis
- deterministic five-output publication with rollback coverage

Reported final validation:

```text
26 macro replay tests passed
4 macro CLI tests passed
bounded FIX-10 replay passed
git diff --check passed
```

ChatGPT directly inspected the final source and focused tests. The reported command execution and commit identity remain Codex-reported evidence; no runtime or production behavior was authorized or changed by acceptance.

M1 acceptance permits only the next separately specified shadow phase.

New active M2 spec:

```text
chatgpt/specs/active/20260721_macro_structure_p8_auxiliary_shadow.md
```

Safety remains report-only / not FORMAL_GO / no automatic order / human decides manually.
