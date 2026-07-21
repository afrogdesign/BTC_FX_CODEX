# Active Plan 候補別暫定評価

## 1. 概要
- report_date: `20260608`
- candidates_path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/logs/csv/active_plan_candidates.csv`
- trades_path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/logs/csv/trades.csv`
- date_from: `all`
- date_to: `all`
- candidate rows: 0
- trade rows: 2079

## 2. 入力状態
- active_plan_candidates.csv: header only
- trades.csv: rows=2079
- entry/tp/sl columns present: yes
- trades has active_primary_action column: yes
- candidates with complete entry/tp/sl values: 0/0
- candidates with followup trade rows: 0/0

## 3. 候補タイプ別件数
- なし

## 4. candidate_status別件数
- なし

## 5. side別件数
- なし

## 6. entry_mode別件数
- なし

## 7. 暫定outcome
- candidates with complete entry/tp/sl values: 0/0
- candidates with followup trade rows: 0/0
- provisional verdict: 候補なし

## 8. 代表候補
- なし

## 9. 未解決事項
- このレポートは暫定版で、TP/SL 到達の厳密判定はまだ行っていない。
- 後続trade行の有無は timestamp_jst の後続行で簡易判定している。
- `active_plan_candidates.csv` が header only の場合は、候補行が発生するまで再評価を待つ。