# BTCFX Ver03-v2 Controlled Public Fetch Run

## Purpose

Record the first controlled real public 15m OHLCV fetch run for Ver03-v2.

This task verifies only the standalone fetch-to-local diagnostic path.

This task does not run the intraperiod builder.

This task does not run reports, daily-sync, runtime, deploy, or trading.

## Command Executed

Exact fetch command:

```bash
./.venv312/bin/python tools/fetch_active_plan_market_data.py \
  --interval 15m \
  --limit 500 \
  --output-csv logs/csv/active_plan_intraperiod_ohlcv.csv
```

This was the only real external fetch command allowed in this task.

## Preconditions

- `./.venv312/bin/python -m unittest tests.test_fetch_active_plan_market_data` passed.
- `./.venv312/bin/python tools/fetch_active_plan_market_data.py --help` displayed usage and did not fetch data.
- No code changes were made before the fetch.

## Fetch Result

- Command success: yes
- Output path: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- Row count: `499`
- Timestamp min/max in JST:
  - min: `2026-06-04T22:45:00+09:00`
  - max: `2026-06-10T03:15:00+09:00`
- Timestamp min/max in UTC:
  - min: `2026-06-04T13:45:00+00:00`
  - max: `2026-06-09T18:15:00+00:00`
- Source values: `['exchange-auto-public']`
- Interval values: `['15m']`
- Symbol values: `['BTC_USDT']`
- CSV columns:
  - `timestamp_jst`
  - `timestamp_utc`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`
  - `source`
  - `interval`
  - `symbol`

## CSV Contract Check

The generated CSV columns are exactly:

`timestamp_jst,timestamp_utc,open,high,low,close,volume,source,interval,symbol`

## Generated Output Policy

- `logs/csv/active_plan_intraperiod_ohlcv.csv` is generated local output.
- Do not stage or commit it.
- Do not stage or commit generated reports.
- Leave existing generated report dirtiness untouched.

## What Was Not Run

- no builder run
- no report generation
- no daily-sync
- no deploy
- no runtime
- no `main.py`
- no `run_cycle`
- no API keys
- no private/account/order endpoints
- no live trading
- no automatic orders
- no `paper_positions.csv` integration
- no evaluator semantic changes
- no trading logic changes
- no archive/cleanup

## Result Interpretation

The fetch succeeded and rows exist, so the standalone public 15m OHLCV fetch-to-local CSV path works.

This does not yet prove builder compatibility on current candidates.

This does not yet prove non-`no_ohlcv` outcomes.

This does not authorize daily-sync, deploy, runtime, or trading integration.

## Next Recommended Task

Review this fetch run, then decide whether to permit one controlled intraperiod builder run against the generated exchange-auto-public OHLCV CSV.

Suggested next work ID after review: `BTCFX-20260610-081`.

Goal: Controlled builder run using generated exchange-auto-public OHLCV, with no daily-sync, deploy, runtime, or trading.
