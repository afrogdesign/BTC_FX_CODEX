# Macro Structure / Expansion Research Basis

## Metadata

- created_at: `2026-07-20`
- purpose: correct the M1 design before source implementation
- scope: reliable support/resistance, structural location, volatility state, order-flow pressure, break/acceptance, and next-level travel
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Decision

The earlier midpoint-centered wording is not accepted as a production or primary research hypothesis.

A range midpoint may be retained only as one descriptive location feature and an optional offline hypothesis. It must not receive privileged weight, become a required trigger, or be described as a proven cause of volatility expansion.

The mandatory M1 foundation is:

1. stable higher-timeframe support/resistance identity
2. event-time level reliability history
3. current location relative to reliable structural levels
4. measurable volatility state
5. measurable supply/demand or order-flow pressure where data exists
6. closed-candle rejection, break, acceptance, and false-break/reclaim behavior
7. distance and obstruction to the next reliable opposing level
8. chronological outcome validation

## 2. Research-supported observations

### 2.1 Support and resistance can contain information, but their quality varies

Carol Osler's Federal Reserve Bank of New York studies found that professionally supplied support/resistance levels helped predict intraday trend interruptions in foreign exchange, while predictive strength varied across currencies and firms. A related order-level study provided a microstructure explanation: take-profit and stop-loss orders cluster near commonly watched levels and round numbers; reversals may occur near a level, while momentum may intensify after a level is crossed.

Design consequence:

- do not treat every pivot or nearest line as reliable
- preserve stable level identity
- measure touches, clean rejections, breaks, acceptance, false breaks, reaction size, recency, and cross-timeframe confluence
- evaluate each level family chronologically

### 2.2 Price movement is linked to order-flow imbalance and available depth

Evans and Lyons showed that order flow contains substantial information for exchange-rate changes. Cont, Kukanov, and Stoikov found that short-horizon price changes are strongly related to order-flow imbalance and that price impact is larger when market depth is lower.

Design consequence:

- the phrase `directional power is accumulating` must be translated into observable variables
- candidate variables include order-flow imbalance, aggressive buy/sell pressure, depth asymmetry, spread/liquidity deterioration, repeated one-sided tests, and directional close imbalance
- simple volume alone is not sufficient
- if the necessary data is absent, the evidence group must be marked unavailable rather than inferred as favorable

### 2.3 Volatility is persistent and regime dependent; low volatility does not guarantee immediate expansion

Realized-volatility research by Andersen, Bollerslev, Diebold, and coauthors documents strong temporal dependence and forecastability in realized volatility. Their jump research also distinguishes persistent continuous variation from less-persistent jump components.

Design consequence:

- `compression -> immediate expansion` is not a rule
- low-volatility conditions may persist
- compression is only a state variable
- expansion risk requires additional evidence such as structural boundary interaction, imbalance, liquidity fragility, break/acceptance, or a regime transition
- jump-like moves and continuous volatility expansion must be measured separately when data permits

### 2.4 Bitcoin jumps have identifiable microstructure precursors, but not a guaranteed direction

High-frequency Bitcoin research found frequent clustered jumps and reported that order-flow imbalance, aggressive-trader participation, and spread widening predicted jump occurrence in the studied sample.

Design consequence:

- M1 should estimate `expansion risk` separately from `direction`
- directional activation should require separate evidence
- liquidity fragility and order-flow pressure are relevant auxiliary evidence groups
- findings from another Bitcoin venue and period are not assumed to transfer to MEXC BTC_USDT; local walk-forward validation is required

### 2.5 Technical structure must be algorithmic and statistically validated

Lo, Mamaysky, and Wang showed that some automatically recognized technical patterns contained incremental information in their historical sample, while emphasizing the subjectivity problem of visual chart interpretation.

Design consequence:

- no discretionary-looking pattern may enter M1 without an explicit event-time algorithm
- no future-confirmed pivot may be backdated
- parameter candidates must be evaluated using chronological calibration, validation, and holdout windows

## 3. Corrected conceptual model

The corrected model is not `midpoint power`. It is:

```text
Reliable structural map
+ current location
+ volatility state
+ pressure / imbalance evidence
+ level interaction
+ closed-candle activation
+ open or obstructed path to the next reliable level
= expansion-risk and directional-travel hypotheses
```

### 3.1 Structural map

Use confirmed 1H and 4H pivots and event-time clustering to create stable zones.

Required outputs:

- stable `level_id`
- support / resistance / role-flip state
- timeframe sources
- touch, rejection, break, acceptance, and reclaim history
- reaction magnitude in ATR
- recency
- confluence
- reliability score and band

### 3.2 Volatility state

Candidate measurements:

- realized range percentile
- realized volatility percentile
- ATR percentile and slope
- short-window versus longer-window realized volatility
- candle-body and range contraction
- persistence of the current volatility regime
- jump or discontinuity diagnostics when measurable

Output describes state only:

- compressed
- ordinary
- expanding
- jump-like / discontinuous
- insufficient

### 3.3 Structural pressure

`Pressure` is an evidence bundle, not a physical quantity and not an entry signal.

Candidate evidence groups:

- repeated tests of one reliable boundary
- decreasing rejection distance from that boundary
- increasing close concentration near the boundary
- directional close imbalance
- order-flow or trade imbalance
- aggressive-side participation
- order-book depth asymmetry
- spread or liquidity deterioration
- failed attempts from the opposing side

Each group must be stored independently so replay can determine which groups add information.

### 3.4 Activation

Direction is not assigned from compression alone.

Directional activation candidates:

- clean rejection from a reliable level
- false break and reclaim
- break followed by closed-candle acceptance
- break, retest, and hold
- directional imbalance agreeing with the accepted side

Activation thresholds are replay parameters only.

### 3.5 Travel corridor

After activation, measure whether price has a relatively unobstructed path to the next reliable opposing level.

Candidate fields:

- target `level_id`
- distance in ATR and percent
- intervening level count
- maximum intervening reliability
- historical travel behavior in similar structures

An open corridor may improve target confidence, but it is not evidence that a break will occur.

## 4. Position of midpoint / equilibrium

Midpoint is retained only as an optional descriptive feature:

- lower half
- equilibrium area
- upper half

Optional hypotheses may test whether equilibrium acceptance, rejection, or recross behavior adds out-of-sample information after controlling for reliable levels, volatility state, and activation evidence.

Rules:

- midpoint is not mandatory for M1 success
- midpoint cannot generate direction by itself
- midpoint cannot generate expansion risk by itself
- midpoint cannot affect production score, gate, notification, or UI in M1
- if it adds no stable validation value, it is removed from later design

## 5. Revised M1 priority order

### Mandatory core

1. event-time confirmed pivot construction
2. stable structural-level clustering and identity
3. level lifecycle and reliability
4. current location relative to reliable levels
5. rejection / break / acceptance / false-break outcomes
6. next reliable target and intervening obstruction
7. realized-volatility state and regime
8. independent large-move and jump-like move inventory
9. missed-move root-cause diagnostics
10. walk-forward validation

### Auxiliary evidence when available

- order-flow imbalance
- aggressive-side participation
- depth imbalance
- spread/liquidity fragility
- CVD and OI context
- compression features
- optional equilibrium/midpoint features

### Deferred

- production Big Chance changes
- production structural-priority changes
- HTML changes
- notification changes
- automatic tuning or application

## 6. Revised event families

Primary event families:

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
- `LIQUIDITY_FRAGILITY`
- `ORDER_FLOW_PRESSURE_UP`
- `ORDER_FLOW_PRESSURE_DOWN`
- `OPEN_TRAVEL_CORRIDOR_UP`
- `OPEN_TRAVEL_CORRIDOR_DOWN`

Optional exploratory event families:

- `EQUILIBRIUM_APPROACH`
- `EQUILIBRIUM_ACCEPTANCE_UP`
- `EQUILIBRIUM_ACCEPTANCE_DOWN`
- `EQUILIBRIUM_REJECTION_UP`
- `EQUILIBRIUM_REJECTION_DOWN`

## 7. Forecast separation

M1 must output separate forecasts:

```text
structural direction
volatility / expansion risk
directional activation
first reliable target
next-regime risk
```

Examples:

- structural direction Long, expansion risk low, activation none
- structural direction Long, expansion risk high, Short activation not confirmed
- structural direction balanced, expansion risk high, Up acceptance confirmed

This prevents `large move possible` from being mistaken for `Short` or `Long` permission.

## 8. Evidence standard

A later proposal is permitted only when:

- level identity and reliability remain stable across chronological windows
- both upward and downward cases are represented
- multiple structure and volatility states are represented
- the result is not dependent on one example
- expansion and direction are evaluated separately
- false warning, opposite movement, whipsaw, and notification burden are reported
- current baseline and challenger use the same independent opportunities

## 9. Primary references

- Osler, C. L. (2000), `Support for Resistance: Technical Analysis and Intraday Exchange Rates`, Federal Reserve Bank of New York Economic Policy Review, 6(2).
- Osler, C. L. (2001 working paper; 2003 published), `Currency Orders and Exchange-Rate Dynamics: Explaining the Success of Technical Analysis`, Federal Reserve Bank of New York Staff Report 125; Journal of Finance 58(5), 1791-1819.
- Evans, M. D. D. and Lyons, R. K. (1999 working paper; 2002 published), `Order Flow and Exchange Rate Dynamics`, NBER Working Paper 7317; Journal of Political Economy 110(1), 170-180.
- Cont, R., Kukanov, A., and Stoikov, S. (2014), `The Price Impact of Order Book Events`, Journal of Financial Econometrics 12(1), 47-88.
- Andersen, T. G., Bollerslev, T., Diebold, F. X., and Labys, P. (2001 working paper; 2003 published), `Modeling and Forecasting Realized Volatility`, NBER Working Paper 8160; Econometrica 71(2), 579-625.
- Andersen, T. G., Bollerslev, T., and Diebold, F. X. (2005 working paper; 2007 published), `Roughing It Up: Including Jump Components in the Measurement, Modeling, and Forecasting of Return Volatility`, NBER Working Paper 11775; Review of Economics and Statistics 89(4), 701-720.
- Scaillet, O., Treccani, A., and Trevisan, C. (2020), `High-Frequency Jump Analysis of the Bitcoin Market`, Journal of Financial Econometrics 18(2), 209-232.
- Lo, A. W., Mamaysky, H., and Wang, J. (2000), `Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation`, Journal of Finance 55(4), 1705-1765.

## 10. Safety boundary

- report-only
- not FORMAL_GO
- no automatic order
- no private/account/order endpoints
- no production score, gate, threshold, notification, mail, or runtime change
- human decides manually
