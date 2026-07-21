# BTCFX Ver03-v2 Winning Trade Criteria

## 1. True purpose

Define what a "winning trade" means for BTC Active Plan candidates.

This is the basis for deciding what data must be automatically collected from exchange/public market sources.

Do not start from available APIs; start from trade quality criteria.

## 2. Scope

- Applies to Ver03-v2 Active Plan intraperiod verification.
- Covers candidate evaluation, required market information, and future data acquisition needs.
- Does not cover implementation, execution, deployment, exchange fetch runs, order APIs, or automatic trading.

## 3. Core winning-trade definition

A candidate is useful only if it can be judged against the actual price path after the signal.

Minimum required outcomes:

- entry reached
- not entered
- TP1 first
- TP2 first
- SL first
- timeout
- ambiguous same-bar TP/SL
- no_ohlcv / insufficient data

A "winning" candidate should not mean merely "price later moved in the intended direction."

It should mean the plan's actionable path was valid: entry condition, risk, target, and timing were reasonable.

## 4. Required judgment metrics

Define the following metrics:

- entry zone reached or not
- time to entry
- first exit reason: TP1 / TP2 / SL / timeout / ambiguous
- MFE after entry
- MAE after entry
- MFE_R
- MAE_R
- planned RR
- realized path quality
- `timeout_hours`
- whether the candidate was actionable for a human trader

## 5. Active Plan type criteria

### ACTIVE_MARKET_SMALL

- Does immediate entry avoid overtrading?
- Does TP / SL path justify market execution?
- Is MAE tolerable?

### ACTIVE_LIMIT_RETEST

- Does price actually return to the entry zone?
- Does retest entry improve RR and reduce MAE?
- Is waiting too slow or useful?

### ACTIVE_BREAKOUT_FOLLOW

- Does breakout follow-through occur after entry?
- Is false breakout / immediate reversal frequent?
- Does TP hit before SL?

### ACTIVE_COUNTER_SCALP

- Treat primarily as short-term counter / warning / exit-support candidate, not automatic order candidate.
- Check whether it helps avoid holding through reversal.

### POSITION_MANAGEMENT

- Evaluate whether hold / reduce / exit guidance matched actual path.

### NO_ACTION

- Evaluate as an expected-value filter.
- Good `NO_ACTION` means avoiding low-quality or dangerous setups.

## 6. Required market information

### 15m OHLCV

Used for:

- entry touch
- TP / SL first touch
- timeout
- MFE / MAE
- intraperiod path

### 1h OHLCV

Used for:

- setup context
- trend / structure
- retest context

### 4h OHLCV

Used for:

- regime / macro trend
- major support / resistance context

### funding rate

Used for:

- long / short carrying pressure
- directional risk context

### optional later

- orderbook
- liquidation
- OI / CVD

Only add these if OHLCV-based validation shows they are needed.

## 7. Minimum dataset needed before first useful automatic run

- Active Plan candidates exist.
- Exchange/public 15m OHLCV covers candidate timestamp through evaluation window.
- 1h and 4h context are available or explicitly marked unavailable.
- Funding rate is available or explicitly marked unavailable.
- The run can label data source as `exchange-auto-public`.
- No manual OHLCV should be required for the standard path.

## 8. Evaluation boundaries

- Do not treat `ACTIVE_*` as automatic order candidates.
- Do not mix Active Plan candidates into `paper_positions.csv` yet.
- Do not infer live-trading readiness from small samples.
- Do not count `no_ohlcv` as bad strategy; it is data insufficiency.
- Do not call a candidate "winning" unless entry / exit path can be evaluated.

## 9. Future automatic data acquisition implications

- First automatic supply target should be 15m OHLCV for intraperiod verification.
- Reuse existing public exchange fetch capability where appropriate.
- No private / account / order endpoint needed.
- No exchange API key needed for public market-data stage.
- First implementation after docs should be fetch-to-local-diagnostic, not deploy.

## 10. Next recommended task

`NEXT BTCFX-20260608-076`

Goal: Map the required market information to existing exchange/public data sources and design the automatic fetch-to-local-diagnostic data flow.

This should still be docs/spec first.

Do not recommend execution, deployment, archive, cleanup, or automatic trading.

## 11. Safety boundary

- No external market data fetch in this task.
- No API keys.
- No runtime restart.
- No `main.py` execution.
- No `run_cycle` execution.
- No daily-sync.
- No deployment.
- No live trading.
- No automatic orders.
- No evaluator semantics changes.
- No trading logic changes.
- No `paper_positions.csv` integration.

## 12. Non-changes in this task

- No code changes.
- No script changes.
- No execution.
- No generated diagnostics were staged or committed.
- No archive / cleanup work was performed.
