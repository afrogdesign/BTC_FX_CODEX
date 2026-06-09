# BTCFX Ver03-v2 Controlled Builder Run

## Purpose

Record the first controlled intraperiod builder run using generated exchange-auto-public 15m OHLCV.

This verifies only builder compatibility with generated OHLCV.

This does not run report generation.

This does not run daily-sync, runtime, deploy, or trading.

## Inputs

- Candidate CSV: `logs/csv/active_plan_paper_candidates.csv`
- OHLCV CSV: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- OHLCV source: `exchange-auto-public`
- Builder output CSV: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`

## Commands Executed

Exact precheck commands:

```bash
cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor
git status --short --branch --untracked-files=all
./.venv312/bin/python -m unittest tests.test_fetch_active_plan_market_data
test -f logs/csv/active_plan_intraperiod_ohlcv.csv
test -f logs/csv/active_plan_paper_candidates.csv
```

Exact builder command, run exactly once:

```bash
./.venv312/bin/python tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes \
  --candidates-path logs/csv/active_plan_paper_candidates.csv \
  --ohlcv-path logs/csv/active_plan_intraperiod_ohlcv.csv \
  --output-csv logs/csv/active_plan_candidate_intraperiod_outcomes.csv
```

Exact CSV inspection command:

```bash
./.venv312/bin/python - <<'PY'
import csv
from collections import Counter
from pathlib import Path

path = Path("logs/csv/active_plan_candidate_intraperiod_outcomes.csv")
print(f"exists={path.exists()}")
if not path.exists():
    raise SystemExit(1)

with path.open("r", newline="", encoding="utf-8") as fp:
    reader = csv.DictReader(fp)
    rows = list(reader)

print(f"columns={reader.fieldnames}")
print(f"row_count={len(rows)}")

outcome_keys = [
    "entry_reached",
    "not_entered",
    "tp1_first",
    "tp2_first",
    "sl_first",
    "timeout",
    "ambiguous_same_bar",
    "no_ohlcv",
]
for key in outcome_keys:
    if key in (reader.fieldnames or []):
        print(f"{key}={sum(1 for row in rows if str(row.get(key, "")).lower() in {'1', 'true', 'yes'})}")

if "outcome" in (reader.fieldnames or []):
    counts = Counter(row.get("outcome", "") for row in rows)
    print(f"outcome_counts={dict(sorted(counts.items()))}")

if rows:
    for key in ["timestamp_jst", "candidate_timestamp_jst", "plan_type", "active_plan_type"]:
        if key in rows[0]:
            print(f"first_{key}={rows[0].get(key)}")
PY
```

## Builder Result

- Command success: yes
- Output CSV exists: yes
- Output row count: `88`
- Important columns:
  - `candidate_id`
  - `signal_id`
  - `timestamp_jst`
  - `candidate_type`
  - `active_primary_action`
  - `side`
  - `entry_mode`
  - `entry_price`
  - `stop_price`
  - `tp1_price`
  - `tp2_price`
  - `outcome`
  - `entry_reached_time`
  - `first_exit_time`
  - `first_exit_reason`
  - `mfe_price`
  - `mae_price`
  - `mfe_r`
  - `mae_r`
  - `notes`
  - `source_signal_id`
  - `candidate_status`
  - `entry_zone_low`
  - `entry_zone_high`
  - `stop_loss`
  - `tp1`
  - `tp2`
  - `rr_current_tp1`
  - `rr_current_tp2`
  - `rr_zone_mid_tp1`
  - `rr_zone_mid_tp2`
  - `market_entry_status`
  - `limit_entry_status`
  - `counter_scalp_status`
  - `breakout_status`
  - `active_subject_label`
  - `active_headline`
  - `next_condition`
- Outcome counts:
  - `entry_reached`: 1
  - `pending`: 12
  - `sl_first`: 39
  - `timeout`: 1
  - `tp1_first`: 35
- Non-`no_ohlcv` rows exist: yes
- Caveat: there is still a `pending` bucket in the CSV, so this is path-validation evidence, not trading-performance proof.

## Generated Output Policy

- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv` is generated local output.
- `logs/csv/active_plan_intraperiod_ohlcv.csv` remains generated local output from 080.
- Do not stage or commit generated CSVs.
- Do not stage or commit generated reports.
- Leave existing generated report dirtiness untouched.

## What Was Not Run

- no new external fetch
- no report generation
- no markdown report generation
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

The controlled builder run succeeded.

This proves the generated exchange-auto-public OHLCV CSV can feed the intraperiod builder.

This does not authorize report/daily-sync/runtime/deploy/trading integration.

Because non-`no_ohlcv` rows exist, the generated OHLCV can produce path-based outcomes for at least some current candidates.

This does not yet claim trading performance validity.

## Next Recommended Task

Review this builder run, then decide whether to generate one markdown report from this outcome CSV.

Suggested next work ID: `BTCFX-20260610-082`.

Goal: Controlled report generation from exchange-auto-public intraperiod outcomes, with no daily-sync, deploy, runtime, or trading.
