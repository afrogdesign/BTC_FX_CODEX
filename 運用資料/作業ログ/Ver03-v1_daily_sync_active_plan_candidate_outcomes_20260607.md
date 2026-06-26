# Ver03-v1 daily-sync Active Plan candidate outcomes 接続ログ

作業番号: BTCFX-20260607-046  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `daily_sync()` で `build_active_plan_candidate_outcomes()` を呼ぶようにした。
- `daily_sync()` の戻り値に `active_plan_candidate_outcomes_path` を追加した。
- `daily-sync` CLI 実行時に `active_plan_candidate_outcomes_path=...` が出力される土台を作った。
- Active Plan candidate outcomes は `active_plan_paper_candidates.csv` と `signal_outcomes.csv` を join する方針を維持した。
- daily-sync が Active Plan candidate outcomes builder を呼ぶことを unittest で固定した。

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
- intraperiod TP / SL 到達判定
- candidate outcomes レポート
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、Active Plan candidate outcomes が daily-sync の標準成果物になった。

これにより、日次同期のたびに以下が順番に更新される。

1. `logs/csv/active_plan_paper_candidates.csv`
2. `logs/csv/active_plan_candidate_outcomes.csv`

ただし、candidate outcomes はまだ forward close ベースの暫定評価である。  
intraperiod の TP / SL 到達判定や、既存 `paper_positions.csv` への接続は後続作業で行う。

## 検証

- `python -m unittest tests.test_daily_sync_active_plan_candidate_outcomes`
- `python -m unittest tests.test_active_plan_candidate_outcomes`
- `python -m unittest tests.test_daily_sync_active_plan_candidates`
- `python -m unittest tests.test_active_plan_paper_candidates`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
