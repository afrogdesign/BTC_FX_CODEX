# BTCFX-20260608-036 untracked file disposition

## 作業番号

- `BTCFX-20260608-036`

## 目的

- `BTCFX-20260608-035` 作業ログの commit hash placeholder を補正する。
- 既知の未追跡ファイル 3 件の扱いを確定し、今後の作業開始時に同じ未追跡ファイルで停止しない状態へ整理する。

## 変更ファイル

- `運用資料/作業ログ/BTCFX-20260608-035_untracked_file_inventory.md`
- `運用資料/計画/Ver03-v1_未追跡ファイル扱い決定_20260608.md`
- `運用資料/NEXT_TASK.md`
- `運用資料/作業ログ/BTCFX-20260608-036_untracked_file_disposition.md`
- `運用資料/参考資料/BTC自動トレードシステムの理想条件まとめ_06-02.md`

## repo 外へ退避したファイル

- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260608.md`
- `運用資料/reports/feedback_daily_sync_20260608.md`

## repo に採用したファイル

- `運用資料/参考資料/BTC自動トレードシステムの理想条件まとめ_06-02.md`

## NEXT_TASK 更新内容

- `## 次にやること` の未追跡ファイル項目を扱い決定済みへ更新
- 生成レポート候補2件は repo 外退避、参考資料1件は repo 採用と明記

## 検証コマンド

- `git diff --check`
- `git diff -- "運用資料/作業ログ/BTCFX-20260608-035_untracked_file_inventory.md" "運用資料/計画/Ver03-v1_未追跡ファイル扱い決定_20260608.md" "運用資料/NEXT_TASK.md" "運用資料/作業ログ/BTCFX-20260608-036_untracked_file_disposition.md" "運用資料/参考資料/BTC自動トレードシステムの理想条件まとめ_06-02.md"`
- `git status --short --branch`

## テスト実行有無

- Markdown / 運用資料更新のみのため未実行

## commit hash

- commit後に確定

## 未解決事項

- `active_plan_candidate_outcomes` / `feedback_daily_sync_20260608` の正本化は今回行っていない
- repo 外へ退避した2件を将来採用するかどうかは別作業で判断する
