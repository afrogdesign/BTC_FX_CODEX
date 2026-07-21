# Ver03-v1 Active Trade Plan effectiveness 追加ログ

作業番号: BTCFX-20260607-042  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `tools/log_feedback.py` に `build_active_trade_plan_effectiveness_report()` を追加した。
- `logs/csv/trades.csv` と `logs/csv/signal_outcomes.csv` を `signal_id` で直接 join する有効性検証レポートを追加した。
- action 別に direction 正解率、TP1先行率、平均MFE24h、平均MAE24h を確認できるようにした。
- output_md 書き出し、outcome 未評価、日付絞り込み、Active Plan 記録なしをテストで固定した。
- CLI subcommand `build-active-trade-plan-effectiveness-report` を追加した。
- `REPORT_FAMILY_SPECS` に `active_trade_plan_effectiveness` を追加した。

## 変更しなかったもの

- `main.py`
- `src/storage/csv_logger.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `build_shadow_log()`
- `SHADOW_HEADER`
- CSV schema
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

今回の effectiveness は、Active Plan の「出方」ではなく、実際の値動き結果との関係を見るための第一段階である。

まだ active plan 別の紙ポジションは作らない。  
まず以下を確認する。

- `ACTIVE_MARKET_SMALL` の MAE が大きすぎないか
- `ACTIVE_LIMIT_RETEST` の TP1先行率が高いか
- `ACTIVE_COUNTER_SCALP` が反発/反落警告として機能しているか
- `NO_ACTION` 後に大きな MFE が出ていないか

Active Plan 別の紙検証レーンは後続作業で行う。

## 検証

- `python -m unittest tests.test_active_trade_plan_effectiveness`
- `python -m unittest tests.test_active_trade_plan_diagnostics`
- `python -m unittest tests.test_csv_logger_active_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
