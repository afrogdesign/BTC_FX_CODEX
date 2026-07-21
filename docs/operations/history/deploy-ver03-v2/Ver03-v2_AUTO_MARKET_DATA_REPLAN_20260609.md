# BTCFX Ver03-v2 Auto Market Data Replan

## 1. True purpose

The project is not to maintain manual OHLCV files.

The project is to define what a winning BTC trade means, determine the required market information, then use exchange/public market data APIs to collect that information automatically.

Manual OHLCV work from BTCFX-20260608-071 to BTCFX-20260608-073 is only a temporary proof that the intraperiod path can escape `no_ohlcv`.

## 2. User decision

- The user does not have time to maintain manual OHLCV.
- No deployment is needed until automatic exchange-data acquisition is ready.
- Do not start the execution entrypoint again until the automatic market-data path is designed and approved.
- Automatic trading remains the final stage only.

## 3. Reclassified prior work

- BTCFX-20260608-071: input contract proof and temporary safety step.
- BTCFX-20260608-072: synthetic sample proved non-`no_ohlcv` is possible.
- BTCFX-20260608-073: manual import workflow documented, but now downgraded to fallback/reference only.
- Archive / cleanup remains deferred.
- Local coverage checker is no longer the next step.

## 4. Correct Ver03-v2 sequence from here

1. Define "winning trade" criteria for Active Plan candidates.
2. Define required market information.
3. Map required information to available exchange/public market data sources.
4. Design automatic OHLCV/data acquisition for intraperiod verification.
5. Implement a safe fetch-to-local-diagnostic pipeline.
6. Run first execution only after the automatic market-data path exists.
7. Iterate on Active Plan quality from observed results.
8. Safety systems.
9. Automatic trading only after explicit user permission.

## 5. Winning trade definition areas to be specified next

- entry zone reached or not
- time to entry
- TP1 / TP2 / SL first-touch order
- timeout
- MFE / MAE from candidate entry
- RR quality
- `ACTIVE_LIMIT_RETEST` performance
- `ACTIVE_MARKET_SMALL` overtrading risk
- `ACTIVE_BREAKOUT_FOLLOW` confirmation quality
- `ACTIVE_COUNTER_SCALP` as exit / warning support
- `NO_ACTION` as expected-value filter

## 6. Required information areas

- 15m OHLCV for entry / TP / SL / MFE / MAE
- 1h OHLCV for setup context
- 4h OHLCV for regime / trend context
- funding rate
- optional later: orderbook, liquidation, OI / CVD if needed

First priority remains OHLCV path-based verification.

## 7. Exchange-auto market data boundary

- Use public market data only at this stage.
- No order endpoints.
- No exchange API keys.
- No account/private endpoints.
- No automatic trading.
- No paper_positions.csv integration yet.
- Existing MEXC fetcher may be referenced as an existing capability, but code is not edited in this task.

## 8. Deployment / execution pause

- No deployment until automatic market-data acquisition is designed and approved.
- Do not run `scripts/run_btcfx_ver03_v2_reports.sh` as the next task.
- Do not run daily-sync.
- Do not run runtime / `main.py` / `run_cycle`.
- The next tasks should be planning/spec tasks, then a small implementation task for automatic public-market-data supply.

## 9. Next recommended task

Replace the current coverage-checker recommendation with:

`NEXT BTCFX-20260608-075`

Goal: Define winning-trade criteria and required market information for Ver03-v2 Active Plan intraperiod verification.

This should be docs-only.

## 10. Safety boundary

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

## 11. Non-changes in this task

- No code changes.
- No script changes.
- No execution entrypoint run.
- No generated diagnostics were staged or committed.
- No archive / cleanup work was performed.
