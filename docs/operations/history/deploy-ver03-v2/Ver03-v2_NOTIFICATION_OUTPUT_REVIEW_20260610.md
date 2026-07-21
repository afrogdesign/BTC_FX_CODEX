# Ver03-v2 notification output review

## Purpose
- Review the current formatted report-only notification output for human BTC trading support.
- This is not an email implementation task.
- This is not a daily-sync execution task.
- This is not a deploy/runtime/trading task.
- The goal is to check whether the formatted notification is readable enough for human BTC trading support.

## Sample Notification Output
```text
BTCFX Ver03-v2 report-only notification

Notification Purpose
- This notification supports human BTC trading decisions.
- This notification is report-only.
- This notification is not FORMAL_GO.
- This notification is not an automatic order.
- The notification is meant to help a human decide whether to trade manually.

Required Header Fields
generated_at_jst: 2026-06-10T12:34:56+09:00
data_freshness: 15m latest-window exchange-auto-public
symbol: BTC_USDT
timeframe: 15m
data_source: exchange-auto-public
report_mode: report-only diagnostic
formal_go_status: not FORMAL_GO
auto_order_status: no automatic order
detail_report_path: 運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md

Required Market Summary Fields
market_status_summary: intraperiod evidence shows mixed TP1 / SL / pending outcomes
active_plan_label: ACTIVE_LIMIT_RETEST
side: long
entry_mode: limit_zone_mid
entry_condition: entry zone must be touched before consideration
tp_plan: TP1 63507.96, TP2 64004.74
sl_or_invalidation: SL 62469.23
timeout_or_wait_limit: timeout after 4h
intraperiod_evidence_summary: 88 outcomes with 35 tp1_first, 39 sl_first, 12 pending
pending_caveat: 12 pending rows remain and reduce confidence

Human Action Interpretation
- A human may use this notification to decide whether to inspect the detailed report, review the market, or consider a manual trade.
- A human must still decide the trade manually.
- ACTIVE_* is action guidance only.
- pending or unresolved outcomes reduce confidence and should be called out clearly.
- The notification must not be read as permission for automatic trading.
```

## Contract Coverage
- `generated_at_jst`: yes
- `data_freshness`: yes
- `symbol`: yes
- `timeframe`: yes
- `data_source`: yes
- `report_mode`: yes
- `formal_go_status`: yes
- `auto_order_status`: yes
- `detail_report_path`: yes
- `market_status_summary`: yes
- `active_plan_label`: yes
- `side`: yes
- `entry_mode`: yes
- `entry_condition`: yes
- `tp_plan`: yes
- `sl_or_invalidation`: yes
- `timeout_or_wait_limit`: yes
- `intraperiod_evidence_summary`: yes
- `pending_caveat`: yes

## Human Trading Support Review
- report-only is explicit.
- not FORMAL_GO is explicit.
- not an automatic order is explicit.
- ACTIVE_* is action guidance only is explicit.
- entry condition and risk boundaries are visible.
- pending / unresolved caveat is visible.
- detailed report path is visible.
- A human can quickly tell that this is a support artifact, not execution permission.

## Gaps Before Real Email Use
- The output is readable, but it is still plain text rather than a polished email template.
- The header labels are explicit, but the body could be shortened if later human review wants a more compact preview.
- The output is suitable for review, but a later email implementation would still need a delivery channel and integration policy.
- No obvious wording ambiguity blocks human review.

## Conservative Next Step
- minimal report-only notification preview generation

## What Was Not Run
- no email sending
- no daily-sync
- no deploy
- no runtime
- no main.py
- no run_cycle
- no fetch
- no builder rerun
- no report regeneration
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
