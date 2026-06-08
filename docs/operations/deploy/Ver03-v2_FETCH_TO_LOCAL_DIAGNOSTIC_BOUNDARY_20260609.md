# BTCFX Ver03-v2 Fetch-to-Local Diagnostic Boundary

## 1. True purpose

Define the implementation boundary for the first automatic market-data step.

The goal is not full execution, deployment, daily-sync, or trading.

The goal is only to prepare a safe, standalone path from public 15m OHLCV to a local diagnostic CSV.

## 2. Boundary decision

- Next implementation should add a standalone diagnostic tool.
- Preferred future tool path: `tools/fetch_active_plan_market_data.py`
- First output path: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- First data source: existing public MEXC kline capability through `src/data/fetcher.py::fetch_klines()` with interval `15m`
- Do not edit `main.py`.
- Do not edit `run_cycle`.
- Do not connect to daily-sync.
- Do not connect to deploy/runtime.
- Do not connect to `paper_positions.csv`.

`src/data/fetcher.py` should be imported and reused, not edited, unless a later reviewed task explicitly approves changing it.

## 3. Allowed future implementation files

For the next implementation task only, allow:

- `tools/fetch_active_plan_market_data.py`
- `tests/test_fetch_active_plan_market_data.py`
- `docs/operations/deploy/Ver03-v2_FETCH_TO_LOCAL_DIAGNOSTIC_IMPLEMENTATION_20260609.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/TASK_LEDGER.md`

## 4. Disallowed future implementation files

Explicitly disallow editing:

- `main.py`
- `scripts/run_btcfx_ver03_v2_reports.sh`
- `tools/log_feedback.py`
- `src/trade/*`
- `src/storage/csv_logger.py`
- `logs/csv/paper_positions.csv`
- daily-sync wiring
- deploy/runtime configuration

## 5. Future command shape

The target command for the future implementation should be:

```bash
./.venv312/bin/python tools/fetch_active_plan_market_data.py \
  --interval 15m \
  --limit 500 \
  --output-csv logs/csv/active_plan_intraperiod_ohlcv.csv
```

Optional future flags may include:

- `--symbol BTC_USDT`
- `--source-label exchange-auto-public`
- `--candidate-csv logs/csv/active_plan_paper_candidates.csv`
- `--print-coverage-summary`

Do not implement these flags in this task.

## 6. Output CSV contract

Future implementation should write:

```text
timestamp_jst,timestamp_utc,open,high,low,close,volume,source,interval,symbol
```

Required meaning:

- `timestamp_jst`: human/operator-facing and builder-compatible timestamp
- `timestamp_utc`: source-normalized UTC timestamp
- `open/high/low/close`: OHLC path data
- `volume`: retained for future diagnostics
- `source`: `exchange-auto-public`
- `interval`: `15m`
- `symbol`: `BTC_USDT` unless configured otherwise

The builder requires at least `timestamp_jst`, `high`, and `low`.

## 7. First implementation acceptance criteria

Future 078 implementation should pass only if:

- It is standalone.
- It uses public market data only.
- It requires no API keys.
- It writes the local diagnostic OHLCV CSV.
- It does not commit generated CSV / report outputs.
- It does not call the builder automatically unless a later task explicitly approves that.
- It does not generate reports automatically.
- It does not connect to daily-sync.
- It does not connect to runtime / `main.py` / `run_cycle`.
- It does not connect to `paper_positions.csv`.
- It does not use private / account / order endpoints.
- It does not create live trading or automatic orders.
- It has mock / unit tests for conversion and CSV schema without requiring real network access.

## 8. Candidate coverage rule

- Initial implementation targets recent candidates only.
- Latest-window OHLCV may be enough for recent candidates.
- Older candidate full backfill is out of scope.
- Rolling local OHLCV persistence is out of scope for the first implementation.
- A future coverage summary may show whether candidate timestamps fall inside the OHLCV min/max range.
- Do not require complete historical coverage in first implementation.

## 9. Execution pause and review checkpoint

- After this boundary document, stop for human / ChatGPT review.
- Do not proceed directly to implementation.
- Do not run a fetch command.
- Do not run builder.
- Do not run report generation.
- Do not deploy.
- The next task should be discussed before issuing Codex work.

## 10. Proposed next task after review

`BTCFX-20260608-078`

Goal: Implement standalone automatic public 15m OHLCV fetch-to-local-diagnostic CSV tool.

This should only happen after review / meeting.

Do not recommend deployment.

Do not recommend automatic trading.

Do not recommend daily-sync connection yet.

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
- No archive / cleanup.

## 12. Non-changes in this task

- No code changes.
- No script changes.
- No execution.
- No generated diagnostics were staged or committed.
- No archive / cleanup work was performed.
