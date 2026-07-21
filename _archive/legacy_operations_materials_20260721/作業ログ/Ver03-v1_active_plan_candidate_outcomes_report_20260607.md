# Ver03-v1 Active Plan candidate outcomes report 追加ログ

作業番号: BTCFX-20260607-047  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `tools/log_feedback.py` に `build_active_plan_candidate_outcomes_report()` を追加した。
- `logs/csv/active_plan_candidate_outcomes.csv` を読む Markdown レポートを追加した。
- candidate type 別に 24h favorable、TP1 close、SL close、平均deltaを集計できるようにした。
- side 別に候補数、24h favorable、平均deltaを集計できるようにした。
- output_md 書き出し、記録なし、日付絞り込みをテストで固定した。
- CLI subcommand `build-active-plan-candidate-outcomes-report` を追加した。
- `REPORT_FAMILY_SPECS` に `active_plan_candidate_outcomes` を追加した。

## 重要な注意

このレポートは forward close ベースの暫定評価である。

以下はまだ未実装。

- intraperiod の高値/安値による TP / SL 到達判定
- 実際に entry zone に到達したか
- 候補 entry price 基準の MFE / MAE 再計算
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
- daily-sync
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の作業で、Active Plan candidate outcomes を人間が確認できる Markdown レポートにできるようになった。

次の段階では、この report builder を `daily-sync` か report hub に接続するかを判断する。  
ただし、候補別の本格紙検証はまだ行わない。

## 検証

- `python -m unittest tests.test_active_plan_candidate_outcomes_report`
- `python -m unittest tests.test_active_plan_candidate_outcomes`
- `python -m unittest tests.test_daily_sync_active_plan_candidate_outcomes`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
