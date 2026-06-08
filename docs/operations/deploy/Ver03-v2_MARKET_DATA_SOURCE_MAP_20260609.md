# BTCFX Ver03-v2 Market Data Source Map

## 1. True purpose

Translate winning-trade criteria into concrete market-data requirements.

Map those requirements to existing exchange/public market data capabilities.

Define the automatic fetch-to-local-diagnostic design before implementation.

Keep execution and deployment paused.

## 2. Inputs from 075

Required path-based outcomes:

- entry reached
- not entered
- TP1 first
- TP2 first
- SL first
- timeout
- ambiguous same-bar TP/SL
- no_ohlcv / insufficient data

Required metrics:

- time to entry
- MFE / MAE
- MFE_R / MAE_R
- planned RR
- realized path quality

## 3. Required market information to source mapping

| Required information | Used for | Existing source / capability | Proposed standard path | Gap / design issue | First implementation priority |
|---|---|---|---|---|---|
| 15m OHLCV | entry touch, TP / SL first touch, timeout, MFE / MAE, intraperiod path | `src/data/fetcher.py::fetch_klines()` supports `15m`; `config.py` contains public MEXC defaults such as base URL and symbol | public exchange 15m OHLCV → local diagnostic OHLCV CSV | Need a durable local output format and clear candidate timestamp coverage rule | Highest |
| 1h OHLCV | setup context, trend / structure, retest context | `src/data/fetcher.py::fetch_klines()` supports `1h` | public exchange 1h OHLCV → local context snapshot or diagnostic context file | Need context-file shape and freshness policy | High |
| 4h OHLCV | regime / macro trend, major support / resistance context | `src/data/fetcher.py::fetch_klines()` supports `4h` | public exchange 4h OHLCV → local context snapshot or diagnostic context file | Need consistent context labeling and lookback boundary | High |
| funding rate | long / short carrying pressure, directional risk context | `src/data/fetcher.py::fetch_funding_rate()` exists | public funding rate → local diagnostic context | Need a stable annotation field and stale-data rule | Medium |
| orderbook, optional later | microstructure / liquidity context | Not required by current path; may exist in exchange/public capability set later | public orderbook snapshot → optional diagnostic enrichment | Only add if OHLCV-based validation shows a real need | Low |
| liquidation, optional later | squeeze / forced-flow context | Not required by current path; optional later | public liquidation feed → optional diagnostic enrichment | Only add if OHLCV-based validation shows a real need | Low |
| OI / CVD, optional later | participation / positioning context | Not required by current path; optional later | public OI / CVD feed → optional diagnostic enrichment | Only add if OHLCV-based validation shows a real need | Low |

## 4. Existing source capability notes

- `src/data/fetcher.py` has public kline fetch capability through `fetch_klines()`.
- `fetch_klines()` supports `4h`, `1h`, and `15m`.
- `fetch_funding_rate()` exists for funding-rate retrieval.
- `config.py` contains public MEXC defaults such as base URL and symbol.
- This task documents those facts only; it does not edit or run code.

## 5. Initial design decision

- First automatic supply target: `15m` OHLCV.
- Use public exchange market data only.
- No order endpoints.
- No exchange API key.
- No automatic trading.
- No runtime / `main.py` / `run_cycle` execution.
- No deployment.

## 6. Fetch-to-local-diagnostic design

Future intended flow:

```text
public exchange 15m OHLCV
→ local diagnostic OHLCV CSV
→ active_plan_candidate_intraperiod_outcomes builder
→ outcome CSV
→ report
```

Context flow:

```text
public exchange 1h / 4h OHLCV
→ local context snapshot or diagnostic context file
→ future report context
```

Funding flow:

```text
public funding rate
→ local diagnostic context
→ directional risk annotation
```

## 7. Candidate timestamp coverage issue

- Current latest-window fetching may be enough for recent candidates.
- Older candidates require either a larger lookback limit if supported, or rolling local OHLCV persistence.
- Do not decide to implement historical backfill yet.
- First implementation should target recent candidates only unless the existing public endpoint safely supports the required window.

## 8. Data source labeling

Required labels:

- synthetic
- manual-fallback
- exchange-auto-public
- missing
- partial

Standard future runs should use `exchange-auto-public`.

Manual OHLCV remains fallback/reference only.

## 9. Minimum acceptance for first automatic diagnostic implementation

- Does not require API keys.
- Uses public market data only.
- Fetches or prepares 15m OHLCV automatically.
- Writes local diagnostic OHLCV input for the builder.
- Does not commit generated CSV / report outputs.
- Builder can run against the generated OHLCV.
- Result can report whether non-`no_ohlcv` rows exist.
- Source label is `exchange-auto-public`.
- No deployment and no runtime integration.

## 10. Explicit non-goals

- No live trading.
- No automatic order execution.
- No order endpoint.
- No account / private endpoint.
- No API keys.
- No `paper_positions.csv` integration.
- No evaluator semantic changes.
- No trading logic changes.
- No runtime / `main.py` / `run_cycle`.
- No daily-sync.
- No deploy.
- No archive / cleanup.

## 11. Next recommended task

`NEXT BTCFX-20260608-077`

Goal: Design the exact safe implementation boundary for automatic public 15m OHLCV fetch-to-local-diagnostic output.

The next task should still be design/spec unless all implementation boundaries are clear.

Do not recommend execution or deploy yet.

Do not recommend automatic trading.

## 12. Safety boundary

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

## 13. Non-changes in this task

- No code changes.
- No script changes.
- No execution.
- No generated diagnostics were staged or committed.
- No archive / cleanup work was performed.
