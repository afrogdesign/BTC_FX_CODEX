# BTCFX Ver03-v2 Report Quality / Candidate Coverage Review

## Purpose

Review the first exchange-auto-public intraperiod Markdown report quality and candidate coverage.

Decide the next integration boundary.

This task does not generate data, run builder, generate reports, wire daily-sync, deploy, runtime, or trading.

## Inputs Reviewed

- OHLCV CSV: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- Outcome CSV: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- Markdown report: `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md`

Lineage:

- 080 controlled public fetch
- 081 controlled builder run
- 082 controlled report generation

## Commands Executed

Exact local inspection commands:

```bash
cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor
git status --short --branch --untracked-files=all
test -f logs/csv/active_plan_intraperiod_ohlcv.csv
test -f logs/csv/active_plan_candidate_intraperiod_outcomes.csv
test -f 運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md
```

No generator command was run.

No new fetch, builder rerun, or report rerun occurred.

## OHLCV Coverage Review

- OHLCV row count: `499`
- OHLCV timestamp min/max JST:
  - min: `2026-06-04T22:45:00+09:00`
  - max: `2026-06-10T03:15:00+09:00`
- OHLCV timestamp min/max UTC:
  - min: `2026-06-04T13:45:00+00:00`
  - max: `2026-06-09T18:15:00+00:00`
- source values: `['exchange-auto-public']`
- interval values: `['15m']`
- symbol values: `['BTC_USDT']`
- coverage caveat: this is a latest-window sample, not a full historical backfill.

## Outcome Coverage Review

- outcome row count: `88`
- outcome counts:
  - `entry_reached`: 1
  - `pending`: 12
  - `sl_first`: 39
  - `timeout`: 1
  - `tp1_first`: 35
- candidate_type counts:
  - `active_counter_scalp`: 22
  - `active_limit_retest`: 64
  - `active_market_small`: 2
- active_primary_action counts:
  - `ACTIVE_LIMIT_RETEST`: 6
  - `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP`: 66
  - `NO_ACTION`: 16
- side counts:
  - `long`: 47
  - `short`: 41
- entry_mode counts:
  - `limit_zone_mid`: 64
  - `market`: 2
  - `market_conditional`: 22
- candidate_status counts:
  - `candidate`: 66
  - `conditional`: 22
- candidate timestamp min/max:
  - min: `2026-06-08T20:05:01.033760+09:00`
  - max: `2026-06-10T03:05:00.119594+09:00`
- non-`no_ohlcv` rows exist: yes
- pending bucket caveat: 12 rows remain `pending`, so the set is not fully resolved.
- sample-row caveat: the first rows show mixed `NO_ACTION`/path outcomes, so this is path-validation evidence rather than performance proof.

## Report Quality Review

- report line count: `88`
- report char count: `7327`
- expected markers present:
  - `BTCFX Ver03-v2`: yes
  - `Active Plan`: yes
  - `intraperiod`: yes
  - `report-only`: yes
  - `FORMAL_GO`: no
  - `tp1_first`: yes
  - `sl_first`: yes
  - `timeout`: yes
  - `pending`: yes
  - `no_ohlcv`: yes
- visible headings:
  - `# BTCFX Ver03-v2 Active Plan 候補別 intraperiod 評価`
  - `## 1. まず結論`
  - `## 2. 集計条件`
  - `## 3. outcome別集計`
  - `## 4. candidate_type別集計`
  - `## 5. active_primary_action別集計`
  - `## 6. side別集計`
  - `## 7. entry到達 / TP1先行 / TP2先行 / SL先行 / timeout / ambiguous / no_ohlcv / pending`
  - `## 8. MFE/MAE/Rの概要`
  - `## 9. 代表例`
  - `## 10. 未解決事項`
- the report clearly states report-only / not FORMAL_GO / not trading decision: yes
- the report is useful for human review: yes
- visible wording/structure issue: it includes `pending` in the summary, which is a caveat rather than a defect.

## Integration Boundary Decision

Decision: `NEXT_MANUAL_REPORT_REVIEW`

Rationale:

- The report quality is clear enough to review manually.
- The coverage is strong enough to inspect without wiring.
- The presence of `pending` rows means this is still diagnostic evidence, not a final integration signal.
- The conservative path is to have a human-facing review of the generated report output before any wiring design.

## What Was Not Run

- no new external fetch
- no builder rerun
- no report regeneration
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

## Generated Output Policy

- Generated CSV/report outputs remain local and uncommitted.
- Do not stage or commit generated CSVs or generated reports.
- Leave existing generated report dirtiness untouched.

## Next Recommended Task

Suggested next work ID: `BTCFX-20260610-084`

Goal: Human-facing review checklist for the generated exchange-auto-public intraperiod report.

Do not recommend daily-sync integration, deployment, runtime, or automatic trading unless explicitly approved after this review.
