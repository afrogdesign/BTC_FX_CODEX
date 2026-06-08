# BTCFX-20260608-032 active_plan candidate logging

## 作業番号

- `BTCFX-20260608-032`

## 目的

- `active_trade_plan` の候補を候補別 CSV `logs/csv/active_plan_candidates.csv` に記録する最小実装を追加する。

## 変更ファイル

- `src/storage/csv_logger.py`
- `main.py`
- `tests/test_active_plan_candidate_logging.py`
- `運用資料/作業ログ/BTCFX-20260608-032_active_plan_candidate_logging.md`

## 実装したCSV

- `logs/csv/active_plan_candidates.csv`

## 候補生成ルール

- `market_entry_status == "allowed"` のとき `market`
- `limit_entry_status == "allowed"` のとき `limit_retest`
- `breakout_status in {"armed", "watch"}` のとき `breakout_follow`
- `counter_scalp_status == "conditional"` のとき `counter_scalp`
- `candidate_id` は `<source_signal_id>:<side>:<candidate_type>`
- `signal_id` が空のときは `unknown_signal`
- 同一 `candidate_id` は重複追記しない

## 検証コマンド

- `git diff --check`
- `python -m pytest tests/test_active_plan_candidate_logging.py tests/test_active_trade_plan.py`

## テスト結果

- `./.venv312/bin/python -m pytest tests/test_active_plan_candidate_logging.py tests/test_active_trade_plan.py` は `No module named pytest` で未実行
- `./.venv312/bin/python -m unittest tests.test_active_plan_candidate_logging tests.test_active_trade_plan` は `12 tests OK`

## commit hash

- 実行後に追記

## 未解決事項

- `active_plan_candidates.csv` を downstream report / daily-sync に接続する作業は今回未実施
