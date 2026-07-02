# Daily Proxy Evaluator

## 1. Safety Boundary
- report-only
- not FORMAL_GO
- no automatic order
- no private/account/order endpoints
- human decides manually
- MEXC raw exports are not imported in this task

## 2. Input Status
- report_date: `20260702`
- lookback_days: `7`
- selected_window: `2026-06-26 -> 2026-07-02`
- report_path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/運用資料/reports/post_eval/daily_proxy_evaluator_20260702.md`

- `signal_outcomes`: status=read_ok / rows=605 / selected_rows=32 / parse_warning_rows=0 / latest_timestamp=2026-07-01T23:05:00.957689+09:00
- `active_plan_candidate_outcomes`: status=read_ok / rows=1515 / selected_rows=374 / parse_warning_rows=0 / latest_timestamp=2026-07-02T03:05:00.984223+09:00
- `active_plan_candidate_intraperiod_outcomes`: status=read_ok / rows=1515 / selected_rows=374 / parse_warning_rows=0 / latest_timestamp=2026-07-02T03:05:00.984223+09:00
- `user_reviews`: status=read_ok / rows=436 / selected_rows=0 / parse_warning_rows=0 / latest_timestamp=2026-06-11T02:05:00.437198+09:00

## 3. Signal Outcome Proxy
- selected rows: 32
- bias: short=29件, long=3件
- prelabel: NO_TRADE_CANDIDATE=15件, RISKY_ENTRY=7件, SWEEP_WAIT=6件, ENTRY_OK=4件
- direction_outcome: correct=17件, wrong=10件, unclear=4件, pending=1件
- entry_outcome: not_applicable=28件, poor_entry=3件, good_entry=1件
- wait_outcome: not_applicable=26件, wait_was_good=5件, unclear=1件
- skip_outcome: not_applicable=17件, unclear=9件, skip_too_strict=5件, skip_was_good=1件
- outcome: win=20件, loss=11件, expired=1件
- skip_too_strict count: 5
- good_entry count: 1

## 4. Active Plan Candidate Proxy
- selected rows: 374
- side: long=233件, short=141件
- candidate_type: active_limit_retest=270件, active_counter_scalp=101件, active_market_small=3件
- active_primary_action: ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP=303件, ACTIVE_LIMIT_RETEST=46件, NO_ACTION=16件, ACTIVE_MARKET_SMALL=9件
- candidate_status: candidate=273件, conditional=101件
- outcome_direction_outcome: blank=287件, correct=45件, wrong=29件, unclear=10件, pending=3件
- tp1_close_reached_24h true count: 21
- sl_close_reached_24h true count: 22

## 5. Intraperiod Proxy
- selected rows: 374
- side: long=233件, short=141件
- candidate_type: active_limit_retest=270件, active_counter_scalp=101件, active_market_small=3件
- active_primary_action: ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP=303件, ACTIVE_LIMIT_RETEST=46件, NO_ACTION=16件, ACTIVE_MARKET_SMALL=9件
- outcome: no_ohlcv=374件
- first_exit_reason: blank=374件
- tp1_first count: 0
- sl_first count: 0
- timeout count: 0
- no_ohlcv count: 374
- average mfe_r: 0.00
- average mae_r: 0.00

## 6. User Review Proxy
- selected rows: 0
- review_status: なし
- user_verdict: なし
- would_trade: なし
- review_source: なし
- average usefulness_1to5: 0.00
- defensive wording count: 0

## 7. Daily Proxy Recommendations
- `NO_TRADE_SPLIT_CANDIDATE`: skip_too_strict=5 / proxy-only / not trading permission

## 8. Limitations
- no actual human PnL yet
- MEXC raw exports are not imported in this task
- daily proxy is not ground truth
- biweekly actual trade import will calibrate proxy vs actual later
