# BTCFX Ver03-v2 Fetch-to-Local Diagnostic Implementation

## Purpose

This task implements the first standalone automatic public 15m OHLCV fetch-to-local-diagnostic CSV tool.
The goal is to prepare a safe, local-only path from public market data to a diagnostic CSV that can later feed the intraperiod outcome builder.

## Command Shape

```bash
./.venv312/bin/python tools/fetch_active_plan_market_data.py \
  --interval 15m \
  --limit 500 \
  --output-csv logs/csv/active_plan_intraperiod_ohlcv.csv
```

## Output CSV Contract

The tool writes:

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

Contract notes:

- `source` is `exchange-auto-public`
- `interval` is `15m`
- `symbol` defaults to `BTC_USDT`
- The downstream builder only requires `timestamp_jst`, `high`, and `low`

## What Was Implemented

- Added `tools/fetch_active_plan_market_data.py` as a standalone CLI tool.
- The tool imports and reuses `src.data.fetcher.FetchConfig` and `fetch_klines`.
- The tool accepts safe public-data CLI arguments with `15m` as the only allowed interval for this task.
- The tool converts fetched OHLCV rows into a local diagnostic CSV.
- The tool creates the output parent directory if needed.
- The tool prints a compact summary with output path, row count, timestamp range, source label, interval, and symbol.

## Tests Run

Mocked/unit tests were added in `tests/test_fetch_active_plan_market_data.py`.

Validation commands:

```bash
./.venv312/bin/python -m unittest tests.test_fetch_active_plan_market_data
./.venv312/bin/python tools/fetch_active_plan_market_data.py --help
git diff --check
```

Test coverage:

- Mocked `fetch_klines` behavior only
- No real external market fetch
- CSV schema conversion
- Parent directory creation
- Source / interval / symbol propagation

## Current Limitations

- 15m only
- Latest-window only
- No historical backfill
- No rolling persistence
- No builder auto-run
- No report auto-run
- No daily-sync integration
- No runtime integration
- No deployment integration

## Non-Commitment of Generated Outputs

Any generated CSV or report outputs remain local workspace artifacts and are not committed by this task.

## Next Recommended Task

Review this implementation, then decide whether to permit one controlled public 15m fetch run.

Do not move to deployment or automatic trading at this step.
