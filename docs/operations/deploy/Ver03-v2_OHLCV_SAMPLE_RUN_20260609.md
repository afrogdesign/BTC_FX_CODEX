# BTCFX Ver03-v2 OHLCV Sample Run

## 1. Purpose

This task proves that the Ver03-v2 Active Plan intraperiod verification path can escape `no_ohlcv` using a minimal local OHLCV sample.

## 2. Scope

- Uses only a local, hand-authored OHLCV sample.
- Does not fetch external OHLCV.
- Does not change evaluator semantics.
- Does not change trading logic.
- Does not connect Active Plan candidates to `paper_positions.csv`.
- Does not archive, clean, delete, or move generated reports.

## 3. Selected candidate

- `candidate_id`: `20260608_110501:active_limit_retest:long`
- `source_signal_id`: `20260608_110501`
- `timestamp_jst`: `2026-06-08T20:05:01.033760+09:00`
- `side`: `long`
- `entry_mode`: `limit_zone_mid`
- `entry_price`: `62920.85`
- `entry_zone_low`: `62836.09`
- `entry_zone_high`: `63005.61`
- `stop_loss`: `62469.23`
- `tp1`: `63507.96`
- `tp2`: `64004.74`

This candidate was sufficient for evaluation because it had a valid timestamp, side, entry zone, stop loss, and TP values.

## 4. Local OHLCV sample

Allowed local file:

- `logs/csv/active_plan_intraperiod_ohlcv.csv`

Sample rows:

| timestamp_jst | open | high | low | close |
|---|---:|---:|---:|---:|
| `2026-06-08T20:05:01.033760+09:00` | 62900.00 | 62990.00 | 62850.00 | 62940.00 |
| `2026-06-08T20:06:01.033760+09:00` | 62940.00 | 63520.00 | 62920.00 | 63500.00 |

The first bar touched the candidate entry band.
The second bar reached `tp1` while staying above the stop.

## 5. Commands run

```bash
cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor
git status --short --branch --untracked-files=all
./.venv312/bin/python - <<'PY'
import pandas as pd
from pathlib import Path
p = Path("logs/csv/active_plan_paper_candidates.csv")
print("exists=", p.exists())
if p.exists():
    df = pd.read_csv(p)
    print("rows=", len(df))
    print("columns=", list(df.columns))
    print(df.head(5).to_string(index=False))
PY
./.venv312/bin/python tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes \
  --candidates-path logs/csv/active_plan_paper_candidates.csv \
  --ohlcv-path logs/csv/active_plan_intraperiod_ohlcv.csv \
  --output-csv logs/csv/active_plan_candidate_intraperiod_outcomes.csv
./.venv312/bin/python - <<'PY'
import pandas as pd
from pathlib import Path
p = Path("logs/csv/active_plan_candidate_intraperiod_outcomes.csv")
print("exists=", p.exists())
df = pd.read_csv(p)
print("rows=", len(df))
print("outcome_counts=")
print(df["outcome"].value_counts(dropna=False).to_string())
print("non_no_ohlcv_rows=")
print(df[df["outcome"].astype(str) != "no_ohlcv"].head(10).to_string(index=False))
PY
./.venv312/bin/python tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes-report \
  --intraperiod-outcomes-path logs/csv/active_plan_candidate_intraperiod_outcomes.csv \
  --output-md "運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md"
```

## 6. Outcome counts

- total rows: 30
- `no_ohlcv`: 28
- `tp1_first`: 1
- `entry_reached`: 1

## 7. Non-`no_ohlcv` result summary

At least one non-`no_ohlcv` outcome appeared.

Observed non-`no_ohlcv` outcomes:

- `tp1_first`
- `entry_reached`

Not observed in this sample:

- `sl_first`
- `timeout`
- `not_entered`

## 8. Limitations of the artificial local sample

- The sample covers only one long candidate.
- It is intentionally synthetic and does not represent market breadth.
- It is enough to prove the path can escape `no_ohlcv`, but it is not enough to validate production behavior.
- It is report-only and does not imply live-trading readiness.

## 9. Next recommendation

The next step should define a safe local OHLCV supply path or manual import workflow so the sample can be replaced with a maintained local input source.

That follow-up should remain local and should not fetch external OHLCV.

## 10. Safety confirmations

- No external OHLCV fetch.
- No API key access.
- No runtime restart.
- No `main.py` execution.
- No `run_cycle` execution.
- No live trading.
- No automatic order execution.
- No `paper_positions.csv` integration.
- No evaluator semantics changes.
- No trading logic changes.
- No archive or cleanup work.

## 11. Non-changes in this task

- Only the allowed local OHLCV sample file was created/overwritten.
- Generated outputs were left local and were not staged or committed.
