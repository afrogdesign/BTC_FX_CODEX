# BTCFX-20260608-037 active_plan runtime check runbook

## 作業番号

- `BTCFX-20260608-037`

## 目的

- `BTCFX-20260608-036` 作業ログの commit hash placeholder を補正する。
- `active_plan_candidates.csv` の runtime 生成確認と、診断再生成の運用手順書を作成する。

## 変更ファイル

- `運用資料/作業ログ/BTCFX-20260608-036_untracked_file_disposition.md`
- `運用資料/計画/Ver03-v1_ActivePlan_runtime確認手順_20260608.md`
- `運用資料/NEXT_TASK.md`
- `運用資料/作業ログ/BTCFX-20260608-037_active_plan_runtime_check_runbook.md`

## 作成した手順書

- `運用資料/計画/Ver03-v1_ActivePlan_runtime確認手順_20260608.md`

## NEXT_TASK 更新内容

- `ChatGPT が最初に開くレポート` 付近の注記に runtime確認手順の参照を追加

## 検証コマンド

- `git diff --check`
- `git diff -- "運用資料/作業ログ/BTCFX-20260608-036_untracked_file_disposition.md" "運用資料/計画/Ver03-v1_ActivePlan_runtime確認手順_20260608.md" "運用資料/NEXT_TASK.md" "運用資料/作業ログ/BTCFX-20260608-037_active_plan_runtime_check_runbook.md"`
- `git status --short --branch`

## テスト実行有無

- Markdown / 運用資料更新のみのため未実行

## commit hash

- commit後に確定

## 未解決事項

- `active_plan_candidates.csv` の runtime 生成確認自体は今回行っていない
- 監視サイクル後に実データで再確認する必要がある
