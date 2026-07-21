# Macro Structure / Volatility / Self-Improvement Plan

## Metadata

- created_at: `2026-07-20`
- status: product design approved for planning; source implementation requires the active specification and a separate bounded task
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- scope: higher-timeframe structure, reliable support/resistance, volatility-expansion detection, Big Chance interpretation, operator information hierarchy, and automated evidence-backed improvement proposals
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Human operating feedback

The current notification HTML is useful in live manual trading, but it lacks one decisive integrated view.

The operator primarily uses:

1. the chart and the 15-minute Entry / SL / TP layers
2. the Big Chance / failed-thesis block as an approximate next-regime cue
3. the actual exchange chart for the broader support/resistance structure

The large operator-action block is currently difficult to scan and does not communicate enough decision value. Its redesign is deferred so that the product does not add more presentation complexity before the underlying macro evidence is improved.

The important observed gap is:

```text
The system can describe short-term direction and execution zones,
but it does not reliably show where price sits inside the broader market structure,
which higher-timeframe levels are genuinely reliable,
or when an equilibrium / midpoint region is likely to release into a large move.
```

The operator's practical interpretation of the current Big Chance block is approximately:

```text
The market is still Long for the next several hours.
However, the Long thesis is weakening.
A failed Long thesis may make Short effective later.
The current 15-minute trade direction and the next macro regime are not the same thing.
```

That interpretation is useful, but the current system does not state it clearly or validate it as a separate forecast contract.

## 2. Current architecture diagnosis

### 2.1 Structural priority is a trend vote, not a complete macro map

`src/analysis/structural_priority.py` calculates `structural_priority.v1` from fixed 4H trend / EMA / structure factors and a smaller 1H structure contribution.

It currently does not directly model:

- a stable higher-timeframe range envelope
- the range high, range low, midpoint, or quartiles
- price location inside that envelope
- the reliability history of each support/resistance level
- the empty travel corridor to the next major level
- compression near equilibrium
- expected volatility expansion after acceptance or rejection
- separate forecasts for the current tactical move and the next structural regime

A result such as `Long 78 / Short 22` therefore means that the weighted trend factors are Long-dominant. It does not mean that the current price is a safe Long location or that a broader Short transition is unlikely.

### 2.2 Existing support/resistance context is too local

`src/analysis/sr_context.py` selects the nearest levels by timeframe, distance, and supplied strength.

It does not currently produce a unified higher-timeframe structure with:

- cross-timeframe clustering
- stable level identity
- touch / rejection / break / reclaim lifecycle
- historical hold rate
- false-break frequency
- reaction magnitude
- range midpoint and balance region
- next-level travel distance

The nearest level is useful for local execution, but nearest is not always the most structurally important level.

### 2.3 Big Chance is useful but under-anchored

`src/analysis/big_chance.py` evaluates failed-thesis flags, role flips, 1H/15M alignment, current zones, and other evidence.

It does not yet make the following distinction explicit:

```text
current tactical bias
versus
current structural thesis
versus
next-regime risk
```

Its grade can therefore appear decisive even when the higher-timeframe location and level geometry are ambiguous.

### 2.4 Existing precursor replay does not cover the reported miss class

The current turning / volatility precursor replay measures material moves over 1H / 2H / 4H using major-level and thesis-stress flags.

It does not yet evaluate:

- broad range midpoint crossings
- equilibrium acceptance or rejection
- low-resistance travel corridors
- move-to-next-major-level probability
- whether the selected major level was historically reliable
- multi-horizon macro forecasts beyond four hours

The reported repeated misses around the midpoint of major support/resistance structures are therefore not directly represented in the current evidence contract.

## 3. Product decision

Do not solve this first by rearranging HTML or changing production thresholds.

The correct sequence is:

```text
build a deterministic macro structure model
→ evaluate it offline against future market paths
→ connect it to Big Chance as a separate next-regime forecast
→ simplify the operator hierarchy around the chart
→ let an offline AI proposal engine test improvements automatically
→ require human approval before production mutation
```

The main chart remains the primary operator surface.

The product must clearly separate three layers:

### Layer A: Macro structure

Answers:

- What is the broader range or directional structure?
- Where is price inside it?
- Which support and resistance levels are reliable?
- Is price near an edge, midpoint, balance zone, or open travel corridor?
- Is volatility expansion risk rising?

Expected horizon:

- several hours to several days

### Layer B: Tactical execution

Answers:

- What can be traded over the next 15 minutes to several hours?
- Which side is tactically preferred now?
- What are Entry, invalidation, SL, TP1, and TP2?
- What must be confirmed on the 15-minute chart?

Expected horizon:

- 15 minutes to several hours

### Layer C: Next-regime / failed-thesis risk

Answers:

- Which currently dominant thesis is weakening?
- What would confirm a regime transition?
- Which opposite side may become effective later?
- What is the first structural target if expansion begins?

Expected horizon:

- one hour to twelve hours initially

These layers may disagree. Disagreement is information, not an error.

Example:

```text
Macro structure: Long trend, but price is near equilibrium and below major resistance.
Tactical execution: Short retest is preferred for the next few hours.
Next-regime risk: A clean midpoint loss may accelerate toward lower structural support.
```

## 4. Target macro structure schema

Create a future report-only schema `macro_structure_map.v1`.

Minimum fields:

- `structure_state`
  - `trend_up`
  - `trend_down`
  - `range`
  - `transition`
  - `insufficient`
- `structure_window`
  - explicit start and end timestamps
  - data source and fingerprints
- `range_low`
- `range_high`
- `range_midpoint`
- `lower_quartile`
- `upper_quartile`
- `price_location`
  - `below_structure`
  - `near_lower_edge`
  - `lower_half`
  - `near_midpoint`
  - `upper_half`
  - `near_upper_edge`
  - `above_structure`
- `location_percentile`
- `major_support_levels`
- `major_resistance_levels`
- `balance_pivots`
- `nearest_reliable_support`
- `nearest_reliable_resistance`
- `next_upside_structural_target`
- `next_downside_structural_target`
- `upside_travel_distance_atr`
- `downside_travel_distance_atr`
- `compression_state`
- `expansion_risk`
  - `low`
  - `medium`
  - `high`
  - `extreme`
- `expansion_side`
  - `up`
  - `down`
  - `both`
  - `none`
- `reason_codes`
- `safety_boundary`

All fields must be event-time deterministic. Future candles may only be used for outcome evaluation.

## 5. Reliable support/resistance model

A level is not reliable merely because it is nearest.

Each level candidate must have a stable identity and an evidence breakdown.

Candidate sources may include:

- confirmed 4H swing highs and lows
- 1H swing clusters that overlap 4H structure
- repeated rejection zones
- support/resistance role flips
- high-volume reaction areas when current source data supports them
- prior failed-break and reclaim zones

A future `level_reliability.v1` record should include:

- `level_id`
- `side`: support / resistance / balance
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
- `reliability_band`: low / medium / high
- `reason_codes`

The first implementation must use bounded deterministic rules. The reliability score is an offline comparison value and must not change production gates.

## 6. Midpoint and volatility-expansion hypothesis

The operator reports a repeated miss pattern:

```text
When price is around the midpoint of a broad support/resistance structure,
volatility can expand sharply and the current small-scale model often misses it.
```

This must be treated as a hypothesis, not accepted as a production fact.

Create explicit event families:

- `MIDPOINT_APPROACH`
- `MIDPOINT_COMPRESSION`
- `MIDPOINT_REJECTION_UP`
- `MIDPOINT_REJECTION_DOWN`
- `MIDPOINT_ACCEPTANCE_UP`
- `MIDPOINT_ACCEPTANCE_DOWN`
- `RANGE_EDGE_REJECTION`
- `RANGE_EDGE_BREAK_ACCEPTANCE`
- `OPEN_TRAVEL_CORRIDOR_UP`
- `OPEN_TRAVEL_CORRIDOR_DOWN`

Possible event-time evidence groups:

- price distance to range midpoint in ATR
- repeated closes around midpoint
- narrowing realized range before release
- direction of acceptance closes
- failed reclaim or failed breakdown
- distance to next reliable level
- higher-timeframe trend and role-flip context
- current tactical side and its fragility

The system must evaluate whether these events precede a material move rather than assuming that midpoint proximity alone is predictive.

## 7. Forecast contracts

The new evidence layer must issue separate forecast records.

### 7.1 Macro-location forecast

Predicts:

- expected next structural destination
- expected direction to the next reliable level
- whether price remains balanced

Horizons:

- 3H
- 6H
- 12H
- optional 24H when data coverage is sufficient

### 7.2 Volatility-expansion forecast

Predicts:

- expansion versus no expansion
- likely expansion side
- time-to-expansion band

Outcome measures:

- maximum favorable and adverse excursion
- realized range expansion versus event-time ATR
- first time a structural target is reached
- false expansion
- whipsaw
- unresolved

### 7.3 Level-behavior forecast

For each reliable level, predict:

- hold / rejection
- clean break and acceptance
- false break and reclaim
- no test within horizon

### 7.4 Next-regime forecast

Predicts separately from current tactical execution:

- current dominant thesis
- weakening thesis
- candidate opposite regime
- activation condition
- invalidation condition
- first structural target

Big Chance should later consume this contract rather than infer the whole macro story from short-term flags alone.

## 8. Automated evidence and self-improvement loop

The target is maximum AI automation without automatic production mutation.

### Daily automatic loop

```text
build event-time macro map
→ record macro, tactical, and next-regime forecasts
→ obtain future public OHLCV
→ resolve level, direction, target, and expansion outcomes
→ record misses and false warnings
→ update deterministic metrics
```

No human trade export is required for this market-prediction loop.

Actual trade evidence remains optional and separately answers whether the human converted useful forecasts into profitable decisions.

### Weekly automatic diagnosis

AI produces a compact issue list:

- reliable level missed
- false major level
- midpoint expansion missed
- wrong next-regime side
- correct macro thesis but poor 15M timing
- correct tactical trade but wrong macro narrative
- over-defensive STOP
- Big Chance too early
- Big Chance too late
- excessive ambiguity

### Offline challenger generation

The proposal engine may vary only bounded, declared parameters and policy templates, such as:

- swing lookback
- level clustering width
- minimum touch count
- recency decay
- cross-timeframe confluence weight
- midpoint corridor width
- compression requirement
- acceptance-close count
- open-corridor distance requirement
- Big Chance evidence weights and grade boundaries

It must not write arbitrary production code or mutate production configuration automatically.

### Champion / challenger evaluation

```text
champion = current accepted policy
challenger = one deterministic candidate parameter set
```

Each challenger is tested with chronological walk-forward evaluation.

Required comparison dimensions:

- directional precision and recall
- expansion precision and recall
- missed large-move rate
- false-warning rate
- opposite-move rate
- whipsaw rate
- median lead time
- target-hit rate
- level hold / break calibration
- Long / Short split
- trend / range / transition split
- midpoint / edge / outside-structure split
- notification burden estimate

The AI report ranks challengers and recommends:

- reject
- continue shadow collection
- eligible for human-reviewed proposal

### Proposal-quality gates

A challenger is not proposal-eligible when:

- validation is not established
- either direction has insufficient resolved events
- results depend on one pinned example
- improvement exists only in calibration and disappears in validation
- missed-move recall improves by creating excessive false warnings
- level reliability is unstable across time windows
- one regime improves while materially damaging another without an explicit regime-specific policy
- data coverage is incomplete
- proxy and actual-backed evidence materially conflict

P9 readiness remains proposal eligibility only.

## 9. Target operator information hierarchy

Do not redesign the large operator-action block first.

The preferred future hierarchy is:

### Primary: chart and execution

The chart remains the largest and first practical decision surface.

Always visible:

- current price
- 15M candles
- reliable macro support/resistance overlays
- range midpoint / balance pivot
- shallow Entry and main Entry zones
- invalidation
- SL
- TP1
- TP2

The chart must visually distinguish:

- macro structural levels
- tactical Entry/SL/TP levels

### Secondary: compact macro strip

Place close to the chart, not as a large abstract score block.

Suggested content:

```text
大局: range / transition
現在地: midpoint付近・上半分
信頼できる支持: 63,xxx–63,xxx / high
信頼できる抵抗: 64,xxx–64,xxx / high
拡大型リスク: down / high
次の構造目標: 63,xxx
```

The current 78/22 structural score may remain as secondary evidence, but it must not be the only macro summary.

### Tertiary: next-regime card

Replace ambiguous interpretation with explicit separation:

```text
現在の数時間: Long継続
大局の弱点: Long thesis weakening near balance pivot
次の候補: midpoint lossでShort expansion
起動条件: 1H acceptance below midpoint + 15M failed reclaim
無効化: midpoint reclaim and hold
最初の目標: next reliable support
```

The grade must be labeled as evidence confidence, not execution permission.

### Deferred: large operator-action block

The current block may later be collapsed, summarized, or moved below the chart.

Do not increase its content before the new macro and next-regime contracts are validated.

## 10. Phased route

### M0: Planning and active specification

- create this strategy plan
- create one active offline evidence specification
- no source or runtime change

### M1: Offline macro structure and volatility evidence

Build deterministic replay-only outputs for:

- stable macro range and levels
- level reliability
- midpoint / balance events
- expansion events
- multi-horizon outcomes
- missed-move diagnostics

No UI, notification, scoring, gate, or runtime changes.

### M2: Daily P8 auxiliary shadow integration

After M1 acceptance:

- reuse existing public market-data fetching where possible
- add the macro evidence run as an optional, disabled-by-default P8 auxiliary shadow
- no live notification change
- no normal monitor change

### M3: Big Chance next-regime contract

After sufficient M1/M2 evidence:

- separate tactical bias from next-regime risk
- anchor Big Chance to reliable levels, structure position, and explicit activation/invalidation
- replay old and new contracts offline
- do not change live UI yet

### M4: Operator hierarchy shadow UI

Render-only comparison:

- chart first
- macro structure overlay and compact strip
- explicit next-regime card
- existing operator-action block retained but visually secondary

No mail or notification behavior change.

### M5: P9 automatic proposal engine

- deterministic bounded challenger generation
- rolling champion/challenger replay
- AI issue diagnosis and proposal ranking
- no automatic production mutation

### M6: Human-reviewed runtime proposal

Only after evidence and explicit approval:

- choose one bounded UI or policy proposal
- validate source and shadow artifact
- apply runtime separately

## 11. First active task

The first active task is M1 only:

```text
BTCFX-20260720-MACRO-STRUCTURE-VOLATILITY-EVIDENCE-SPEC
```

It must define the offline input, schema, level identity, midpoint events, outcome horizons, replay metrics, deterministic tests, and proposal gates.

It must not implement the UI redesign, Big Chance production change, notification change, scoring change, or automatic tuning.

## 12. Success criteria

The plan succeeds when the system can answer, with evidence:

1. Which higher-timeframe levels repeatedly hold or break?
2. Where is current price inside the broader structure?
3. Does midpoint / equilibrium behavior genuinely precede large moves?
4. What side and target are likely over 3H / 6H / 12H?
5. Is the current tactical trade aligned with or opposed to the next-regime risk?
6. Which recurring large moves are currently missed?
7. Which bounded challenger improves recall without excessive noise?
8. Can the operator understand the answer mainly from the chart and one compact next-regime card?

## 13. Safety and prohibitions

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys, secrets, private, account, position, or order endpoints
- public market-data fetch only through existing accepted paths
- no automatic production mutation
- no automatic threshold application
- no gate relaxation
- no notification behavior change without separate approval
- no runtime restart during M1–M5 planning and offline work
- no tuning from the supplied screenshots or one current market example
- human decides all trades and all production adoption


---

## 2026-07-20 research correction: reliable levels first

This section supersedes any midpoint-centered or `compression automatically precedes expansion` interpretation elsewhere in this plan.

Research basis:

`docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`

Corrected product decision:

- reliable higher-timeframe support/resistance is the mandatory foundation
- stable level identity, lifecycle, and reliability must be established before directional or expansion proposals
- volatility compression is a state variable, not a directional signal and not proof of imminent expansion
- expansion risk and direction must be estimated separately
- measurable order-flow, aggressive-side, depth, liquidity, repeated-test, rejection, break, acceptance, and reclaim evidence are the preferred mechanism candidates
- the path to the next reliable opposing level is measured after activation, not used as proof that activation will occur
- midpoint/equilibrium is optional exploratory location context only
- midpoint has no privileged score, trigger, proposal gate, or UI commitment
- if midpoint features do not add stable out-of-sample value after controlling for reliable levels and activation evidence, they are removed

Revised primary sequence:

```text
reliable level map
→ level reliability history
→ current structural location
→ volatility state
→ pressure / imbalance evidence
→ rejection, break, acceptance, or reclaim activation
→ next reliable target and obstruction
→ future outcome resolution
→ missed-move root-cause analysis
→ champion/challenger proposal
```

The M1 implementation must follow the research-basis document and the precedence correction in the active specification.
