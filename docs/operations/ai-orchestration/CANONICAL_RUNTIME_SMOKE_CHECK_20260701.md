# CANONICAL_RUNTIME_SMOKE_CHECK_20260701

## Purpose
canonical repo `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` だけを使って report-only smoke を確認し、主要 surface と rescued runtime-generated reports が使えることを記録する。

## Canonical repo checked
- canonical repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- frozen old runtime repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- old runtime repo は触っていない

## Frozen old runtime boundary
- frozen old runtime repo は参照用の境界として扱う
- 旧 repo へコピー元 source/test/docs/scripts/config を戻す作業はしない
- live execution / runtime restart / launchctl / cron は実行しない

## Commands run
- `pwd -P`
- `git status --short --branch`
- `plutil -p deploy/com.afrog.btc-monitor.plist`
- `plutil -p deploy/com.afrog.btc-review-form.plist`
- `plutil -p deploy/com.afrog.btc-ai-post-reviews.plist`
- `plutil -p deploy/com.afrog.btc-feedback-daily-sync.plist`
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json`
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface`
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json`

## Deploy plist validation
- 4 本の deploy plist は canonical repo path を指していた
- `WorkingDirectory` / 実行 path は `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

## Rescued report presence check
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260701.md`
- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260701.md`
- `運用資料/reports/feedback_daily_sync_20260701.md`
- いずれも canonical repo 側で存在を確認した

## Report-only smoke result
- `describe-current-manual-delivery-app-contract --stdout-json` は成功
- `export-current-manual-delivery-app-surface` は成功
- `check-current-manual-delivery-app-surface --stdout-json` は成功
- canonical surface の report-only contract / dashboard / snapshot path は動作していた
- `OHLCV stale coverage warning` は checked artifacts では separate literal としては見えず、stale 状態は `ohlcv_range_freshness_status` と `freshness_note` で確認した

## Evidence fields confirmed
- `evidence_quality_summary`
- `ohlcv_source_coverage_summary`
- `ohlcv_range_freshness_status`
- `candidate_max_after_ohlcv_end_hours`
- `ohlcv_source_coverage_summary.candidate_timestamp_min`
- `ohlcv_source_coverage_summary.candidate_timestamp_max`
- `ohlcv_source_coverage_summary.freshness_note`
- `ohlcv_source_coverage_summary.safety_note`
- `ohlcv_source_coverage_summary.ohlcv_range_freshness_status` は `stale_before_latest_candidate`

## Safety wording confirmed
- `report-only`
- `not FORMAL_GO`
- `no automatic order`
- `human decides manually`

## Generated file handling
- `local/manual_delivery_app_surface/` などの生成物は commit していない
- rescue した runtime-generated reports も commit していない
- smoke 後の生成物は確認のみで、必要なら後続で個別に整理する

## What was not run
- frozen old runtime repo への反映
- live execution
- runtime restart
- launchctl / cron
- private/account/order endpoint
- OHLCV fetch
- progress HTML / CURRENT_PROGRESS.md の更新

## Next recommendation
- `BTCFX-20260701-CANONICAL-CHECKPOINT-PUSH-PREP`
- Goal: canonical repo の現状を、後で user-managed GitHub pull に渡せる checkpoint package として整理する
