# BTCFX Ver03-v2 OHLCV Manual Import Workflow

## 1. True purpose

This workflow exists to move Ver03-v2 Active Plan intraperiod verification from a synthetic OHLCV sample to a maintained local OHLCV input.

The goal is to support verification against actual 15m price paths while keeping the workflow local, report-only, and free of archive/cleanup drift.

## 2. Scope

- Applies only to Ver03-v2 intraperiod verification.
- Replaces the synthetic sample with a manually maintained local OHLCV file.
- Does not fetch external OHLCV.
- Does not change evaluator semantics.
- Does not change trading logic.
- Does not connect Active Plan candidates to `paper_positions.csv`.
- Does not archive, clean, delete, move, stage, or commit generated diagnostics.

## 3. Current proof from BTCFX-20260608-072

- Selected candidate escaped `no_ohlcv`.
- Outcome counts:
  - `no_ohlcv=28`
  - `tp1_first=1`
  - `entry_reached=1`
- The synthetic sample proved the path can work, but it remained artificial and covered only one long candidate.

## 4. Manual OHLCV input contract

- Destination path: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- Required columns: `timestamp_jst`, `high`, `low`
- Recommended columns: `timestamp_jst`, `open`, `high`, `low`, `close`
- Accepted timestamp alternatives: `timestamp_utc`, `timestamp`, `datetime`, `dt`
- Timestamp coverage must include candidate timestamps and the following evaluation window.
- 15m bars are preferred, but evaluator semantics must not be changed in this task.

## 5. Safe manual import procedure

1. Operator exports or pastes OHLCV externally by hand.
2. Save it locally as `logs/csv/active_plan_intraperiod_ohlcv.csv`.
3. Run preflight.
4. Run the existing intraperiod builder.
5. Inspect outcome counts.
6. Optionally build the report.
7. Leave generated outputs local unless an explicit future task approves otherwise.

Suggested commands:

```bash
cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor
./scripts/run_btcfx_ver03_v2_reports.sh --show-input-contract
./scripts/run_btcfx_ver03_v2_reports.sh --preflight-only
./.venv312/bin/python tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes \
  --candidates-path logs/csv/active_plan_paper_candidates.csv \
  --ohlcv-path logs/csv/active_plan_intraperiod_ohlcv.csv \
  --output-csv logs/csv/active_plan_candidate_intraperiod_outcomes.csv
./.venv312/bin/python tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes-report \
  --intraperiod-outcomes-path logs/csv/active_plan_candidate_intraperiod_outcomes.csv \
  --output-md "運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md"
```

## 6. Minimum acceptance for usable but unfinished

- `active_plan_paper_candidates.csv` exists.
- `active_plan_intraperiod_ohlcv.csv` exists.
- The builder exits `0`.
- At least one non-`no_ohlcv` row appears.
- The report states whether the evidence is synthetic, manually imported, or real-maintained-local.
- No trading-performance conclusion is made until sample size is meaningful.

## 7. Evidence labeling rule

Any report or follow-up note should explicitly label the evidence source as one of:

- synthetic
- manually imported
- real-maintained-local

This avoids confusing a one-off local sample with operational evidence.

## 8. Next recommendation

The next recommended task is to add a small safe coverage or quality checker for local OHLCV input.

If a maintained local OHLCV file is later supplied, a separate task can run the manual workflow with that larger local file.

Do not recommend archive as the next step.

## 9. Safety boundary

- No external OHLCV fetch.
- No API keys.
- No runtime restart.
- No `main.py` execution.
- No `run_cycle` execution.
- No live trading.
- No automatic order execution.
- No `paper_positions.csv` integration.
- No evaluator semantics changes.
- No trading logic changes.
- No archive or cleanup work.

## 10. Non-changes in this task

- No generated diagnostics were staged or committed.
- No archive / cleanup action was performed.
- No source behavior was changed.
- This document only defines the safe maintained-local workflow boundary.
