# Ver03-v1 Active Trade Plan diagnostics 追加ログ

作業番号: BTCFX-20260607-041  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `tools/log_feedback.py` に `build_active_trade_plan_diagnostics_report()` を追加した。
- `logs/csv/trades.csv` の Active Plan 列を直接読む診断レポートを追加した。
- `active_primary_action` 別件数を集計できるようにした。
- 成行、指値/戻り待ち、ブレイク追随、逆方向短期の long/short status を集計できるようにした。
- `NO_ACTION` 比率と `ACTIVE_MARKET_SMALL` の偏りを確認できるようにした。
- CLI subcommand `build-active-trade-plan-diagnostics-report` を追加した。
- `REPORT_FAMILY_SPECS` に `active_trade_plan_diagnostics` を追加した。
- Active Plan 記録なし、日付絞り込み、output_md 書き出しをテストで固定した。

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

今回の diagnostics は、Active Plan の出方を確認するための第一段階である。

まだ勝敗や MFE / MAE とは結合しない。  
まずは以下を確認する。

- `ACTIVE_MARKET_SMALL` が多すぎないか
- `ACTIVE_LIMIT_RETEST` が主戦場として出ているか
- `ACTIVE_COUNTER_SCALP` が conditional に留まっているか
- `NO_ACTION` が期待値フィルターとして一定数出ているか

Active Plan 別の紙検証や MFE / MAE 結合は後続作業で行う。

## 検証

- `python -m unittest tests.test_active_trade_plan_diagnostics`
- `python -m unittest tests.test_csv_logger_active_plan`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
