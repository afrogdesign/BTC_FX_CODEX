# BTCFX Ver03-v2 OHLCV Input Contract

## 1. Purpose

This task locks down a purpose-specific OHLCV input contract for Ver03-v2 Active Plan intraperiod verification.

The bottleneck we are currently trying to unblock is `no_ohlcv`.

This document records the safe contract view, the expected local OHLCV file shape, and the next intended non-archive step.

## 2. Scope

- Applies only to Ver03-v2 Active Plan intraperiod verification.
- Does not change evaluator semantics.
- Does not fetch external OHLCV.
- Does not connect Active Plan candidates to `paper_positions.csv`.
- Does not run live trading or automatic orders.
- Does not archive, clean, delete, or move generated diagnostics.

## 3. Current no_ohlcv bottleneck

- The current intraperiod diagnostic path can reach `no_ohlcv` when the OHLCV input file is absent.
- That outcome is diagnostic only.
- It does not imply a trading signal, a live execution condition, or a paper-position integration step.

## 4. Expected OHLCV input contract

- Candidate CSV path: `logs/csv/active_plan_paper_candidates.csv`
- OHLCV CSV path: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- Accepted OHLCV timestamp column names: `timestamp_jst`, `timestamp_utc`, `timestamp`, `datetime`, `dt`
- Required OHLCV price columns: `high`, `low`
- Recommended OHLCV columns for human-maintained input: `timestamp_jst`, `open`, `high`, `low`, `close`
- Output CSV path: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- Output report pattern: `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_<YYYYMMDD>.md`

## 5. Safe contract view

Run the entrypoint with the new contract flag when you want to inspect the expected input surface without generating reports:

```bash
./scripts/run_btcfx_ver03_v2_reports.sh --show-input-contract
```

Behavior:

- Runs repository/path/PYTHON_BIN preflight checks first.
- Prints the locked input contract.
- Exits `0`.
- Does not build reports.
- Does not write generated CSV or Markdown outputs.

## 6. Preflight-only mode

Use the existing preflight-only path when you only want repository and writable-path checks:

```bash
./scripts/run_btcfx_ver03_v2_reports.sh --preflight-only
```

Behavior:

- Runs preflight checks.
- Prints the preflight summary.
- Exits `0`.
- Does not build reports.
- Does not write generated CSV or Markdown outputs.

## 7. Next intended task

The next intended step is to create or supply a minimal local OHLCV CSV, then run the existing intraperiod builder so at least one outcome can avoid `no_ohlcv`.

That follow-up task should stay local and report-only.

It should not fetch external OHLCV.

It should not touch `paper_positions.csv`.

It should not change evaluator semantics.

## 8. Explicitly deferred archive / cleanup

- Archive work is deferred.
- Cleanup work is deferred.
- This task does not delete, move, or archive generated outputs.
- This task only documents the input contract needed to unblock the next verification step.

## 9. Safety boundary

- No live trading.
- No automatic order execution.
- No API key access.
- No runtime restart.
- No `main.py` execution.
- No `run_cycle` execution.
- No external OHLCV fetch.
- No `paper_positions.csv` integration.
- No trading logic changes.
- No evaluator semantics changes.

## 10. Non-changes in this task

- No generated diagnostics were staged or committed.
- No archive or cleanup action was performed.
- No source behavior was changed beyond the safe contract view flag.
- No report-generation behavior was changed for `--preflight-only`.
