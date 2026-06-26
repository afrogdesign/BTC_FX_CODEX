# Ver03-v1 Active Plan paper candidates 追加ログ

作業番号: BTCFX-20260607-043  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `tools/log_feedback.py` に `ACTIVE_PLAN_PAPER_CANDIDATE_HEADER` を追加した。
- `tools/log_feedback.py` に `build_active_plan_paper_candidates()` を追加した。
- `logs/csv/trades.csv` の `active_trade_plan_json` から Active Plan 候補を抽出できるようにした。
- `logs/csv/active_plan_paper_candidates.csv` を生成できるようにした。
- `active_market_small`、`active_limit_retest`、`active_counter_scalp` の候補を抽出できるようにした。
- `ACTIVE_COUNTER_SCALP` は `conditional` 候補として保存するようにした。
- CLI subcommand `build-active-plan-paper-candidates` を追加した。
- JSON不正、Active Plan 未設定、日付絞り込み、output_csv 指定をテストで固定した。

## 変更しなかったもの

- `main.py`
- `src/storage/csv_logger.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `build_shadow_log()`
- `SHADOW_HEADER`
- `CSV_HEADER`
- `paper_positions.csv`
- 既存 `build_paper_positions()`
- 既存 paper order 生成条件
- `paper_order_status`
- `trade_execution_gate`
- `opportunity_gate`
- 通知件名
- HTML hero
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業は、Active Plan 別の紙検証レーンの第一段階である。

既存の `paper_positions.csv` にはまだ接続しない。  
まずは `active_plan_paper_candidates.csv` として候補を分離保存する。

後続作業で、候補の entry 到達、TP/SL 到達、MFE/MAE、timeout を検証する。

## 検証

- `python -m unittest tests.test_active_plan_paper_candidates`
- `python -m unittest tests.test_active_trade_plan_effectiveness`
- `python -m unittest tests.test_active_trade_plan_diagnostics`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
