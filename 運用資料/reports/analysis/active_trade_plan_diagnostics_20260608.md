# Active Trade Plan 診断

## 1. 概要
- report_date: `20260608`
- candidates_path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/logs/csv/active_plan_candidates.csv`
- trades_path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/logs/csv/trades.csv`
- date_from: `all`
- date_to: `all`
- candidate rows: 0
- trade rows: 2078

## 2. active_primary_action 分布
- trades `blank`: 2077 件
- trades `NO_ACTION`: 1 件
- candidate action distribution: no rows

## 3. 候補タイプ別件数
- なし

## 4. side別件数
- なし

## 5. candidate_status別件数
- なし

## 6. entry_mode別件数
- なし

## 7. NO_ACTION 比率
- total trades: 2078
- `NO_ACTION`: 1 件 (0.0%)
- blank action: 2077 件 (100.0%)
- active_plan_version counts: blank=2077件, active_trade_plan_v1=1件
- market entry status: long=blank=2077件, blocked=1件 / short=blank=2077件, blocked=1件
- limit retest status: long=blank=2077件, allowed=1件 / short=blank=2077件, allowed=1件
- counter scalp status: long=blank=2077件, blocked=1件 / short=blank=2077件, blocked=1件

## 8. 代表候補
- なし

## 9. 未解決事項
- Active Plan の判定ロジック自体は今回変更していない。
- candidate outcomes / daily-sync 接続は今回対象外。