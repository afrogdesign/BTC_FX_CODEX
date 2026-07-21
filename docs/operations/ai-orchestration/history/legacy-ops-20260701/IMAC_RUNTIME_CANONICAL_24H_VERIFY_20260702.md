# IMAC_RUNTIME_CANONICAL_24H_VERIFY_20260702

## Purpose
iMac runtime / launchd を canonical repo に統一してから 24 時間以上経過した時点で、実際の効果が出ているかを read-only で確認した記録である。

## Verification time
- `2026-07-02 01:58:27 +0900`

## Canonical repo
- `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

## Frozen old runtime boundary
- `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- frozen old runtime repo は開発対象にしない
- read-only comparison だけを行い、変更はしていない

## Repo-owned deploy plist result
- 4 本すべて `plutil -lint` 成功
- 4 本すべての `ProgramArguments` / `WorkingDirectory` / `StandardOutPath` / `StandardErrorPath` は canonical repo を参照していた
- `/Users/marupro/CODEX/01_active/BTC_FX_CODEX` を指す active deploy plist は見つからなかった

## Installed LaunchAgents result
- `~/Library/LaunchAgents/com.afrog.btc-monitor.plist`
- `~/Library/LaunchAgents/com.afrog.btc-review-form.plist`
- `~/Library/LaunchAgents/com.afrog.btc-ai-post-reviews.plist`
- `~/Library/LaunchAgents/com.afrog.btc-feedback-daily-sync.plist`
- 4 本すべて `plutil -lint` 成功
- 4 本すべて canonical repo を指していた
- 4 本すべてに frozen old runtime の path は含まれていなかった

## launchd current state
- `com.afrog.btc-monitor` は running
- `com.afrog.btc-review-form` は running
- `com.afrog.btc-ai-post-reviews` は not running
- `com.afrog.btc-feedback-daily-sync` は not running
- `launchctl print` 上の program / working directory / stdout / stderr は canonical repo を指していた
- `ps aux` は sandbox 権限制約で実行できなかったため、process の実態確認は `launchctl print` と runtime logs で補完した

## Process state
- launchd 上の 4 ラベルは canonical repo 指向で loaded / scheduled されている
- frozen old runtime を指す実行中 process は確認できなかった
- old-path 実行が必要な process は見つからなかった

## Canonical runtime log evidence
- `logs/runtime/monitor.out` の最新行は canonical startup_status path を指していた
- `logs/runtime/review_form.out` は `http://127.0.0.1:8765/` を継続出力していた
- `logs/runtime/feedback_daily_sync.out` には canonical CSV / report path が出ていた
- `logs/runtime/monitor.err` / `review_form.err` / `ai_post_reviews.err` / `feedback_daily_sync.err` は 0 bytes
- canonical logs の最新更新時刻は 2026-07-01 を含み、switch 後の canonical 側出力が継続していることを示した

## Canonical output/report evidence
- `logs/csv/active_plan_candidates.csv` は 2026-07-02 01:05 更新
- `logs/csv/trades.csv` は 2026-07-02 01:05 更新
- `logs/csv/observation_paper_orders.csv` / `paper_positions.csv` は 2026-07-02 00:05 更新
- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260701.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260701.md`
- `運用資料/reports/feedback_daily_sync_20260701.md`
- report-only surface smoke でも evidence fields は継続して見えていた

## Frozen old runtime read-only comparison
- old repo の最新観測ファイルは 2026-07-01 までで止まっていた
- 2026-07-02 の新規更新は確認できなかった
- old repo 側に新規出力を書いた証拠は見つからなかった
- historical old-path lines は old / current の accumulated logs に残っているが、最新行は canonical path だった

## Report-only smoke result
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json` 成功
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json` 成功
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface` は current surface を出力した

## Evidence/safety fields result
- `evidence_quality_summary`
- `ohlcv_source_coverage_summary`
- `ohlcv_range_freshness_status`
- `candidate_max_after_ohlcv_end_hours`
- `report-only`
- `not FORMAL_GO`
- `no automatic order`
- `human decides manually`

## Failures or warnings
- `ps aux` は sandbox 権限制約で読めなかった
- schedule-only labels は現在 not running だが、エラーや old-path 書き込みは確認できなかった
- `monitor.out` などに historical old-path lines は残るが、最新観測は canonical path だった

## Conclusion
PASS_WITH_NOTE: canonical runtime effect confirmed after 24h

## Next recommendation
- `USER_DECISION_REQUIRED`
- cleanup / runtime work / Phase G / product work は user decision まで止める
