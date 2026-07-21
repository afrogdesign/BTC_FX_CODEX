# Ver03-v1 formal candidate hard quality blocker 化ログ

作業番号: BTCFX-20260607-058  
更新日: 2026-06-07 JST  
対象ブランチ: Ver03-v1

## 実施内容

- `formal_execution_candidate` が hard quality reason を持つ場合、`opportunity_gate=blocked` になるようにした。
- `trade_execution_gate=pass` でも、`require_execution_for_high_wait` などの hard quality reason がある場合は pass させないようにした。
- soft quality reason は formal candidate の non-blocking conflict reason として残した。
- non-formal candidate の hard quality blocker 挙動は維持した。
- 回帰テストを追加した。
- 既存の formal candidate 回帰が `tests/test_phase1_trade_plans.py` にあったため、期待値も合わせて更新した。

## 変更しなかったもの

- `main.py`
- `tools/log_feedback.py`
- `src/storage/csv_logger.py`
- `src/trade/paper_position.py`
- `src/trade/active_plan.py`
- `src/analysis/result_flags.py`
- `src/analysis/confidence.py`
- `CSV_HEADER`
- `SHADOW_HEADER`
- `PAPER_POSITION_HEADER`
- filled-only 集計
- volume trigger
- `short_reversal_risk`
- Active Plan intraperiod report
- daily-sync
- 実弾発注 API
- 取引所 API キー
- 自動注文送信

## 位置づけ

今回の修正は P1-1 である。

P0-2 の実データ確認では、filled-only 成績が all closed 成績と大きく乖離していることが確認された。  
そのため、formal candidate であっても hard quality conflict を通すべきではない。

この修正により、`trade_execution_gate=pass` が出ていても、hard quality reason がある場合は opportunity 側では blocked となる。

## 検証

- `python -m unittest tests.test_opportunity_gate`
- `python -m unittest discover -s tests -p 'test*.py'`
- `git diff --check`
