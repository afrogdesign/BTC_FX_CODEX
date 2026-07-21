# BTCFX-20260608-045 active_plan candidate outcomes

## 作業番号

- `BTCFX-20260608-045`

## 目的

- `active_plan_candidate_outcomes` builder / CLI を正本化する。
- `BTCFX-20260608-044` 作業ログの commit hash placeholder を補正する。
- 今回は `tools/log_feedback.py` とテスト追加が主作業。

## 変更ファイル

- `tools/log_feedback.py`
- `tests/test_active_plan_candidate_outcomes_report.py`
- `運用資料/作業ログ/BTCFX-20260608-044_auto_submit_healthcheck.md`
- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260608.md`
- `運用資料/NEXT_TASK.md`
- `運用資料/作業ログ/BTCFX-20260608-045_active_plan_candidate_outcomes.md`

## builder / CLI生成report

- `candidate rows: 0`
- `trade rows: 2079`
- `active_plan_candidates.csv: header only`
- `trades.csv: rows=2079`
- `provisional verdict: 候補なし`
- CLI 実行は成功し、`運用資料/reports/analysis/active_plan_candidate_outcomes_20260608.md` が生成された。

## テスト結果

- `candidates / trades` が missing でも Markdown を生成できるようにした。
- `candidates` が header only でも `candidate rows: 0` になることを確認できる。
- 複数行の候補データで `candidate_type` / `candidate_status` / `side` / `entry_mode` の件数が出るようにした。
- `report_date=\"20260608\"` で `active_plan_candidate_outcomes_20260608.md` を生成するようにした。
- CLI 相当の builder 呼び出しで例外が出ない構成にした。

## commit hash

- commit後に確定
