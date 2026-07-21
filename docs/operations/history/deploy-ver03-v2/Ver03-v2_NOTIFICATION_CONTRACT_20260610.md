# Ver03-v2 notification contract

## Notification Purpose
- This notification supports human BTC trading decisions.
- This notification is report-only.
- This notification is not FORMAL_GO.
- This notification is not an automatic order.
- The notification is meant to help a human decide whether to trade manually.

## Required Header Fields
- `generated_at_jst`: when the notification was produced, in JST.
- `data_freshness`: how recent the source data is, relative to the generated time.
- `symbol`: BTC symbol covered by the notification.
- `timeframe`: timeframe used for the intraperiod evidence.
- `data_source`: source label for the market data.
- `report_mode`: must indicate report-only diagnostic mode.
- `formal_go_status`: must indicate not FORMAL_GO.
- `auto_order_status`: must indicate no automatic order.
- `detail_report_path`: path or link to the detailed report for review.

## Required Market Summary Fields
- `market_status_summary`: concise market context and current evaluation state.
- `active_plan_label`: the Active Plan action label, such as ACTIVE_LIMIT_RETEST.
- `side`: long or short.
- `entry_mode`: how the entry is intended to be taken.
- `entry_condition`: the condition that must be met before entry is valid.
- `tp_plan`: take-profit target plan.
- `sl_or_invalidation`: stop-loss or invalidation condition.
- `timeout_or_wait_limit`: time limit or wait limit before the setup expires.
- `intraperiod_evidence_summary`: concise summary of entry / TP / SL / timeout evidence.
- `pending_caveat`: any unresolved or pending caveat that lowers confidence.

## Human Action Interpretation
- A human may use the notification to decide whether to inspect the detailed report, review the market, or consider a manual trade.
- A human must still decide the trade manually.
- ACTIVE_* labels are action guidance, not formal execution permission.
- pending or unresolved outcomes reduce confidence and should be called out clearly.
- The notification must not be read as permission for automatic trading.

## Example Notification Skeleton
```text
Generated at: {generated_at_jst}
Freshness: {data_freshness}
Symbol / timeframe / source: {symbol} / {timeframe} / {data_source}
Mode: {report_mode}; FORMAL_GO: {formal_go_status}; Auto order: {auto_order_status}
Market summary: {market_status_summary}
Active Plan: {active_plan_label}
Side: {side}
Entry: {entry_mode} | {entry_condition}
TP plan: {tp_plan}
SL / invalidation: {sl_or_invalidation}
Timeout / wait limit: {timeout_or_wait_limit}
Evidence: {intraperiod_evidence_summary}
Caveat: {pending_caveat}
Detail report: {detail_report_path}
```

## Still Prohibited
- no email sending implementation in this task
- no daily-sync execution
- no runtime/deploy
- no main.py
- no run_cycle
- no API keys/secrets/private/account/order endpoints
- no live trading
- no automatic orders
- no paper_positions.csv integration
- no evaluator semantic changes
- no trading logic changes

## Conservative Next Step
- If ChatGPT accepts this contract, the smallest safe next task is minimal report-only notification formatting implementation.
- If the contract needs wording adjustment, the next task should be a docs fix.
- No runtime/deploy/trading integration is approved by this document.
