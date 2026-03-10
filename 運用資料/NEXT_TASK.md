# NEXT TASK TRACKER

## 現在の状況
- 常駐実行は `launchd` で動作中。
- 定時実行は毎時 `:05` に変更済み。
- 通知条件は 2026-03-10 に「気づき重視」へ調整済み。
- AI判定は `ai_error` が継続中だったが、API実接続テスト成功を確認し、`AI_TIMEOUT_SEC=5` / `AI_RETRY_COUNT=3` へ修正済み。
- 要約生成は `AI_SUMMARY_TIMEOUT_SEC=10` に延長済み。
- 常駐プロセスは再起動済みで、`monitor.pid` と `launchctl` の PID 同期も修正済み。
- 次回以降は AI 失敗時の詳細が `logs/errors/*ai_*_error.log` に残るよう対応済み。
- メール本文は、数値の羅列より意味が伝わる日本語へ改善中。
- 現在の通知しきい値:
  - `CONFIDENCE_LONG_MIN=60`
  - `CONFIDENCE_SHORT_MIN=65`
  - `CONFIDENCE_ALERT_CHANGE=7`
  - `ALERT_COOLDOWN_MINUTES=30`

## 次のタスク
- 1. 常駐再起動後に、毎時 `:05` 実行が反映された状態で `logs/heartbeat.txt` と `logs/last_result.json` の更新頻度を確認する。
- 2. 次回サイクル後に `logs/last_result.json` の `ai_advice` が `null` から復帰するか確認する。
- 3. `logs/errors/` に `ai_advice_error` または `ai_summary_error` が新規発生するか確認する。特に要約側タイムアウトが再発しないかを見る。
- 4. 次回メール本文が、数値の意味を日本語で自然に伝える形になっているか確認する。
- 5. 通知が来たら `logs/last_notified.json` の `reason_for_notification` を見て、増え方が多すぎないか確認する。
- 6. 通知が多すぎる場合は `CONFIDENCE_ALERT_CHANGE` を 8 か 9 に戻して再調整する。

## 完了条件
- 設定修正後の常駐実行で AI判定が復帰するか、または失敗理由がログで明確になること。
