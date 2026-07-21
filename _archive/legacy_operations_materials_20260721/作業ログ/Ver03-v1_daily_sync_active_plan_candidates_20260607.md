# Ver03-v1 daily-sync Active Plan paper candidates 接続ログ

作業番号: BTCFX-20260607-044  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `daily_sync()` で `build_active_plan_paper_candidates()` を呼ぶようにした。
- `daily_sync()` の戻り値に `active_plan_paper_candidates_path` を追加した。
- `daily-sync` CLI 実行時に `active_plan_paper_candidates_path=...` が出力される土台を作った。
- Active Plan paper candidates は `shadow_log.csv` ではなく `trades.csv` を直接読む方針を維持した。
- daily-sync が Active Plan candidates builder を呼ぶことを unittest で固定した。

## 変更しなかったもの

- `main.py`
- `src/storage/csv_logger.py`
- `src/trade/active_plan.py`
- `src/presentation/sanitize.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `CSV_HEADER`
- `SHADOW_HEADER`
- `build_shadow_log()`
- `paper_positions.csv`
- 既存 `build_paper_positions()`
- 既存 paper order 生成条件
- `paper_order_status`
- `trade_execution_gate`
- `opportunity_gate`
- 通知件名
- HTML hero
- Active Plan core の判定ロジック
- Active Plan 候補の TP / SL / MFE / MAE 評価
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、Active Plan paper candidates が daily-sync の標準成果物になった。

これにより、日次同期のたびに `logs/csv/active_plan_paper_candidates.csv` が更新され、後続で候補ごとの entry 到達、TP/SL 到達、MFE/MAE、timeout を検証できる。

ただし、まだ既存 `paper_positions.csv` とは接続しない。  
Active Plan candidates は独立した検証レーンとして扱う。

## 検証

- `python -m unittest tests.test_daily_sync_active_plan_candidates`
- `python -m unittest tests.test_active_plan_paper_candidates`
- `python -m unittest tests.test_active_trade_plan_effectiveness`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
