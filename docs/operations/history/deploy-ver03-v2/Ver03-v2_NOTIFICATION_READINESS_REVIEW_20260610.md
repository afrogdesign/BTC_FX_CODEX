# Ver03-v2 notification readiness review

## Purpose
- Human BTC trading support 向けの、report-only 通知レディネスを確認する。
- これはメール実装ではない。
- これは daily-sync 実行ではない。
- これは deploy/runtime/trading の作業ではない。
- 既存の intraperiod report が、人間の trading decision を補助する通知素材として十分かを点検する。

## Report under review
- Generated report path: `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md`
- Outcome CSV lineage: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- OHLCV lineage: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- Source: `exchange-auto-public`
- Lineage tasks:
  - `BTCFX-20260610-080` controlled public fetch
  - `BTCFX-20260610-081` controlled builder run
  - `BTCFX-20260610-082` controlled report generation
  - `BTCFX-20260610-083` report quality / coverage review
  - `BTCFX-20260610-084` human checklist
  - `BTCFX-20260610-085` candidate coverage / window review
  - `BTCFX-20260610-086` pending reason classification review
  - `BTCFX-20260610-087` wiring boundary design

## Minimum Human-Actionable Notification Contract
Future notification must contain at least:
- generated time / data freshness
- BTC symbol / timeframe / data source
- market status summary
- Active Plan action label
- side
- entry mode / entry condition
- TP / SL / invalidation or timeout
- evidence summary from intraperiod outcomes
- caveats including pending
- explicit report-only / not FORMAL_GO / no automatic order wording
- link or path to detailed report

## Current Readiness Findings
- The current report is human-readable and clearly states report-only diagnostics.
- The current report explicitly says Active Plan is not FORMAL_GO and not an automatic order candidate.
- The current report includes aggregate evidence for entry reached, TP1 first, SL first, timeout, and pending.
- The current report includes representative rows that expose side, action label, entry mode, entry/exit timing, and MFE/MAE values.
- The current report is sufficient as evidence for human review, but it is not yet packaged as a notification-ready contract.
- Report size is stable enough for review: 88 lines and 7327 characters.

## Gaps Before Useful Human Email
- Generated time and freshness are not surfaced as a dedicated notification header field.
- BTC symbol, timeframe, and data source are not yet assembled into a concise notification contract.
- `entry_mode` appears in representative evidence, but not as a dedicated notification summary field.
- The report is readable, but it is not yet normalized into a short email/report notification structure.
- A human-facing notification still needs an explicit concise market status summary line.
- The report path is available, but a future notification should present it as a direct reference field.

## Conservative Next Step
- Recommended next step is a docs wording fix for the notification contract before any implementation task is approved.
- If a later review explicitly approves it, the smallest implementation step should be minimal report-only email/notification formatting.
- No runtime/deploy/trading integration is approved yet.

## What Was Not Run
- no new fetch
- no builder rerun
- no report regeneration
- no daily-sync
- no report hub generation
- no deploy
- no runtime
- no main.py
- no run_cycle
- no API keys
- no private/account/order endpoints
- no live trading
- no automatic orders
- no paper_positions.csv integration
- no evaluator semantic changes
- no trading logic changes
- no archive/cleanup

## Generated Output Policy
- Generated CSV/report outputs remain local and uncommitted.
- Do not stage or commit generated CSVs or generated reports.
- Leave existing generated report dirtiness untouched.
