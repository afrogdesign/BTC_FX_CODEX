# BTCFX-20260608-033 active_trade_plan diagnostics

## 作業番号

- `BTCFX-20260608-033`

## 目的

- `logs/csv/active_plan_candidates.csv` を日次確認できる診断レポートへ接続する。
- `BTCFX-20260608-032` 作業ログの commit hash placeholder を補正する。

## 変更ファイル

- `tools/log_feedback.py`
- `tests/test_active_trade_plan_diagnostics_report.py`
- `運用資料/作業ログ/BTCFX-20260608-032_active_plan_candidate_logging.md`
- `運用資料/作業ログ/BTCFX-20260608-033_active_trade_plan_diagnostics.md`

## 実装したレポート

- `運用資料/reports/analysis/active_trade_plan_diagnostics_YYYYMMDD.md`

## CLI

- `python tools/log_feedback.py --build-active-trade-plan-diagnostics --active-plan-report-date 20260608`

## 検証コマンド

- `git diff --check`
- `python -m unittest tests.test_active_trade_plan_diagnostics_report tests.test_active_plan_candidate_logging tests.test_active_trade_plan`
- `python tools/log_feedback.py --build-active-trade-plan-diagnostics --active-plan-report-date 20260608`

## テスト結果

- `./.venv312/bin/python -m unittest tests.test_active_trade_plan_diagnostics_report tests.test_active_plan_candidate_logging tests.test_active_trade_plan` は `15 tests OK`
- `./.venv312/bin/python tools/log_feedback.py --build-active-trade-plan-diagnostics --active-plan-report-date 20260608` は `active_trade_plan_diagnostics_20260608.md` を生成

## commit hash

- commit後に確定

## 未解決事項

- candidate outcomes / daily-sync への downstream 接続は今回未実施
