# BTCFX Ver03-v2 Temporary Execution / Deploy Note

## 1. Purpose

This note defines a temporary manual execution boundary for Ver03-v2 diagnostics and report generation.

## 2. What this entrypoint does

- Runs the safe report-generation flow for the Active Plan intraperiod outcome CSV.
- Builds the intraperiod outcome CSV only from existing local files when the candidate CSV is present.
- Generates the Markdown analysis report for `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`.
- Refreshes the report hub after the diagnostic outputs are written.

## 3. What it explicitly does not do

- This is not live trading.
- This is not automatic order execution.
- This does not restart runtime.
- This does not confirm or use exchange API keys.
- This does not modify `paper_positions.csv`.
- This does not make `ACTIVE_*` a formal GO.
- This does not wire into daily-sync.

## 4. Manual command

```bash
scripts/run_btcfx_ver03_v2_reports.sh
```

Preflight-only check:

```bash
scripts/run_btcfx_ver03_v2_reports.sh --preflight-only
```

The preflight-only mode checks repository readiness, input availability, and output parent writability without generating or modifying report / CSV files.

## 5. Expected outputs

- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_YYYYMMDD.md`
- `運用資料/reports/report_hub_latest.md`
- The script passes the report hub path to the CLI as an absolute repo-root path while displaying it as `運用資料/reports/report_hub_latest.md`.

## 6. Preflight

- `--preflight-only` runs readiness checks and exits without generating report / CSV outputs.
- Missing `logs/csv/active_plan_paper_candidates.csv` is a warning, not a failure. The report can still emit a missing/empty notice.
- Missing `logs/csv/active_plan_intraperiod_ohlcv.csv` is a warning, not a failure. The normal execution path will use `no_ohlcv` behavior.
- Required hard failures are limited to repository-root problems, missing or non-executable `PYTHON_BIN`, missing `tools/log_feedback.py`, or output parent directories that cannot be created or are not writable.

## 7. Preconditions

- Run from the local iMac repo at `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.
- The temporary report flow must remain diagnostic only.
- The shell environment should have `./.venv312/bin/python` available, or `PYTHON_BIN` should be set explicitly.
- The candidate CSV may be absent; in that case the script should skip the CSV build and still run the report generation path.

## 8. Stop conditions

- Stop if runtime restart is required.
- Stop if live trading or automatic order execution is required.
- Stop if exchange API keys are required.
- Stop if `paper_positions.csv` would need to change.
- Stop if daily-sync integration is being added here.
- Stop if the flow would need to change trading logic.

## 9. Label / email subject audit

- Required temporary prefix: `BTCFX Ver03-v2`
- Reports created in this Ver03-v2 path should use `BTCFX Ver03-v2` in titles where applicable.
- Future email subject prefixes must use `BTCFX Ver03-v2`.
- Current email subject code: not changed in this task / follow-up required.

## 10. Next steps after this temporary deploy prep

- Review the generated diagnostics output.
- Decide whether the temporary execution path should stay manual or be wired into daily-sync in a separate task.
- Keep this boundary outside live trading until a later explicit approval.
