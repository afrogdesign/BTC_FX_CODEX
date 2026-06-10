# Ver03-v2 Notification Preview Output Review

## Purpose

Review the actual report-only notification preview output produced by `write_active_plan_notification_preview` before any later email, daily-sync, runtime, deploy, or trading integration step.

This is a docs-only review.

This is not an email implementation task.

This is not a daily-sync execution task.

This is not a deploy/runtime/trading task.

## Preview Generation Method

Fixture values from `tests/test_active_plan_notification_formatting.py` were used as the sample input:

- `generated_at_jst = 2026-06-10T12:34:56+09:00`
- `data_freshness = 15m latest-window exchange-auto-public`
- `symbol = BTC_USDT`
- `timeframe = 15m`
- `data_source = exchange-auto-public`
- `detail_report_path = 運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md`
- `market_status_summary = intraperiod evidence shows mixed TP1 / SL / pending outcomes`
- `active_plan_label = ACTIVE_LIMIT_RETEST`
- `side = long`
- `entry_mode = limit_zone_mid`
- `entry_condition = entry zone must be touched before consideration`
- `tp_plan = TP1 63507.96, TP2 64004.74`
- `sl_or_invalidation = SL 62469.23`
- `timeout_or_wait_limit = timeout after 4h`
- `intraperiod_evidence_summary = 88 outcomes with 35 tp1_first, 39 sl_first, 12 pending`
- `pending_caveat = 12 pending rows remain and reduce confidence`

A temporary directory path was used for the preview write.

No repo generated report or CSV artifacts were created or committed.

## Generated Preview Output

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

The preview visibly contains all required contract fields:

- `generated_at_jst`
- `data_freshness`
- `symbol`
- `timeframe`
- `data_source`
- `report_mode`
- `formal_go_status`
- `auto_order_status`
- `detail_report_path`
- `market_status_summary`
- `active_plan_label`
- `side`
- `entry_mode`
- `entry_condition`
- `tp_plan`
- `sl_or_invalidation`
- `timeout_or_wait_limit`
- `intraperiod_evidence_summary`
- `pending_caveat`

## Human Trading Support Review

The preview is usable for human BTC trading support.

It is easy to see that:

- this is report-only
- this is not FORMAL_GO
- this is not an automatic order
- ACTIVE_* is guidance only
- entry condition is visible
- TP / SL / timeout are visible
- pending caveat is visible
- detailed report path is visible

The preview is not phrased as an automatic execution instruction.

## Gaps Before Real Email Delivery

The output is readable and contract-complete, but real email use would still need:

- delivery formatting suitable for email clients
- message subject / header policy for the actual sender
- a final boundary for how and where preview text is surfaced
- later integration approval before any sending path exists

No blocking wording gap was found in the preview body itself.

## Conservative Next Step

Proceed with `BTCFX-20260610-094` only if a later docs-only boundary is needed for minimal report-only preview CLI / manual-output handling.

If a wording change is later requested, that should be a small docs fix rather than an integration change.

## What Was Not Run

- no fetch
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

Generated CSV/report outputs remain local and uncommitted.

No preview output file was committed.

No repo generated report or CSV artifacts were created for this review.
