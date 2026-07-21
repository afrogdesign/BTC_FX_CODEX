# Ver03-v1 Active Plan report family registry 固定ログ

作業番号: BTCFX-20260607-049  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `REPORT_FAMILY_SPECS` に Active Plan 系 report family が登録されていることをテストで固定した。
- `active_trade_plan_diagnostics` の登録を固定した。
- `active_trade_plan_effectiveness` の登録を固定した。
- `active_plan_candidate_outcomes` の登録を固定した。
- 各 report family の `pattern`、`date_pattern`、`search_roots`、`section` をテストで固定した。
- 各 report family の `label` と `purpose` が空ではないことをテストで固定した。

## 変更しなかったもの

- `tools/log_feedback.py`
- `main.py`
- `src/storage/csv_logger.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `CSV_HEADER`
- `SHADOW_HEADER`
- `build_shadow_log()`
- `daily_sync()`
- report builder の中身
- report hub の生成ロジック
- `paper_positions.csv`
- 既存 paper order 生成条件
- intraperiod TP / SL 到達判定
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業は、Active Plan 系レポートが report family registry から落ちないようにする安全ガードである。

Active Plan 系は、通知、HTML、CSV、diagnostics、effectiveness、candidate CSV、candidate outcomes、daily-sync report まで接続済みになった。

次の段階では、Ver03-v1 の Active Plan 実装全体を棚卸しし、intraperiod TP / SL 到達判定へ進む前に、現状レビューと残課題を Markdown で固定する。

## 検証

- `python -m unittest tests.test_active_plan_report_family_registry`
- `python -m unittest tests.test_daily_sync_active_plan_candidate_outcomes_report`
- `python -m unittest tests.test_active_plan_candidate_outcomes_report`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
