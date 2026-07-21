# BTCFX Ver03-v2 Controlled Report Run

## Purpose

Record the first controlled Markdown report generation from exchange-auto-public intraperiod outcomes.

This verifies only report generation from the controlled builder output.

This does not run daily-sync.

This does not run runtime, deploy, or trading.

## Inputs

- Outcome CSV: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- Report output: `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md`
- OHLCV lineage: `exchange-auto-public 15m OHLCV from BTCFX-20260610-080`
- Builder lineage: controlled builder run from BTCFX-20260610-081

## Commands Executed

Exact precheck commands:

```bash
cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor
git status --short --branch --untracked-files=all
test -f logs/csv/active_plan_candidate_intraperiod_outcomes.csv
```

Exact report command, run exactly once:

```bash
./.venv312/bin/python tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes-report \
  --intraperiod-outcomes-path logs/csv/active_plan_candidate_intraperiod_outcomes.csv \
  --output-md 運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md
```

Exact Markdown inspection command:

```bash
./.venv312/bin/python - <<'PY'
from pathlib import Path

path = Path("運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md")
print(f"exists={path.exists()}")
if not path.exists():
    raise SystemExit(1)

text = path.read_text(encoding="utf-8")
lines = text.splitlines()
print(f"line_count={len(lines)}")
print(f"char_count={len(text)}")
for needle in [
    "Active Plan",
    "intraperiod",
    "tp1_first",
    "sl_first",
    "timeout",
]:
    print(f"contains_{needle}={needle in text}")

print("first_20_lines_begin")
for line in lines[:20]:
    print(line)
print("first_20_lines_end")
PY
```

## Report Result

- Command success: yes
- Report file exists: yes
- Line count: `88`
- Char count: `7327`
- Expected markers present:
  - `Active Plan`: yes
  - `intraperiod`: yes
  - `tp1_first`: yes
  - `sl_first`: yes
  - `timeout`: yes
- First visible headings / summary:
  - `# BTCFX Ver03-v2 Active Plan 候補別 intraperiod 評価`
  - `## 1. まず結論`
  - The first section states it is not a trading decision, not formal GO, and report-only diagnostics.
- Caveat: the generated report includes a `pending` bucket, so this is still diagnostic evidence rather than trading-performance proof.

## Generated Output Policy

- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md` is generated local output.
- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv` is generated local output from 081.
- `logs/csv/active_plan_intraperiod_ohlcv.csv` is generated local output from 080.
- Do not stage or commit generated reports or generated CSVs.
- Leave existing generated report dirtiness untouched.

## What Was Not Run

- no new external fetch
- no builder rerun
- no daily-sync
- no report hub generation
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

The controlled report generation succeeded.

This proves the exchange-auto-public fetch-to-builder-to-report path works manually under controlled commands.

This does not authorize daily-sync, runtime, deploy, or trading integration.

Do not claim trading performance validity yet.

## Next Recommended Task

Review report quality and candidate coverage before any wiring.

Suggested next work ID: `BTCFX-20260610-083`.

Goal: Review exchange-auto-public intraperiod report quality and decide next integration boundary.

Do not recommend daily-sync integration yet unless specifically approved after report review.
