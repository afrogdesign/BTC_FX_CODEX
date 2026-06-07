# Ver03-v1 Active Trade Plan CSV logging 追加ログ

作業番号: BTCFX-20260607-040  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `src/storage/csv_logger.py` の `CSV_HEADER` に Active Plan 列を追加した。
- `trades.csv` に `active_plan_version` を保存できるようにした。
- `trades.csv` に `active_primary_action` を保存できるようにした。
- `trades.csv` に `active_subject_label` を保存できるようにした。
- `trades.csv` に `active_headline` を保存できるようにした。
- `trades.csv` に成行・指値/戻り待ち・ブレイク追随・逆方向短期の long/short status を保存できるようにした。
- `trades.csv` に保有中処理メッセージを保存できるようにした。
- `trades.csv` に `active_trade_plan_json` を保存できるようにした。
- Active Plan が未設定または壊れた値でも CSV 出力が落ちないテストを追加した。

## 変更しなかったもの

- `main.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `tools/log_feedback.py`
- 通知件名
- HTML hero
- paper order 生成条件
- `trade_execution_gate`
- `opportunity_gate`
- `paper_order_status`
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、Active Trade Plan の判定結果が `trades.csv` に保存されるようになった。

これにより、後続作業で `active_trade_plan_diagnostics` を作成し、以下を集計できる土台ができる。

- `ACTIVE_MARKET_SMALL` が多すぎないか
- `ACTIVE_LIMIT_RETEST` が主戦場として機能しているか
- `ACTIVE_COUNTER_SCALP` が conditional に留まっているか
- `NO_ACTION` が期待値フィルターとして機能しているか

## 検証

- `python -m unittest tests.test_csv_logger_active_plan`
- `python -m unittest tests.test_detail_page_active_plan_hero`
- `python -m unittest tests.test_summary_active_plan_subject`
- `python -m unittest tests.test_active_trade_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
