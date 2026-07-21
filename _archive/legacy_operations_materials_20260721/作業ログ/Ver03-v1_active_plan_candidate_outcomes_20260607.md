# Ver03-v1 Active Plan candidate outcomes 追加ログ

作業番号: BTCFX-20260607-045  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `tools/log_feedback.py` に `ACTIVE_PLAN_CANDIDATE_OUTCOME_HEADER` を追加した。
- `tools/log_feedback.py` に `build_active_plan_candidate_outcomes()` を追加した。
- `logs/csv/active_plan_paper_candidates.csv` と `logs/csv/signal_outcomes.csv` を join できるようにした。
- 候補ごとに 12h / 24h forward close ベースの暫定 delta を出せるようにした。
- 候補ごとに `candidate_result_12h` / `candidate_result_24h` を出せるようにした。
- 24h終値ベースで `tp1_close_reached_24h`、`tp2_close_reached_24h`、`sl_close_reached_24h` を出せるようにした。
- CLI subcommand `build-active-plan-candidate-outcomes` を追加した。
- long / short 候補、outcomeなし、日付絞り込み、output_csv 指定をテストで固定した。

## 重要な注意

今回の評価は forward close ベースであり、intraperiod の高値/安値による TP / SL 到達判定ではない。

そのため、以下はまだ未実装。

- 実際に entry zone に到達したか
- TP1 / TP2 / SL に途中到達したか
- MFE / MAE を候補 entry price 基準で再計算すること
- timeout 判定
- 既存 `paper_positions.csv` への接続

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
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、Active Plan candidates に対して最低限の outcome join ができるようになった。

これは候補別の本格的な紙検証ではなく、forward close を使った暫定評価である。  
次の段階では、この candidate outcomes を daily-sync に接続し、その後に候補別レポートを作る。

## 検証

- `python -m unittest tests.test_active_plan_candidate_outcomes`
- `python -m unittest tests.test_daily_sync_active_plan_candidates`
- `python -m unittest tests.test_active_plan_paper_candidates`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
