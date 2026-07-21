# IMAC_RUNTIME_LAUNCHD_CANONICAL_SWITCH_20260701

## Purpose
この iMac 上で実際に起動している btc_monitor 系 runtime / launchd / 実行ファイル参照を canonical repo に統一した記録である。

## User approval
- user は iMac runtime systems を新しい canonical repo に統一することを明示的に許可した
- restart が必要なら許可された

## Canonical repo
- `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- iMac runtime launchd references はこの repo を参照する前提へ揃えた

## Frozen old runtime boundary
- `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` は frozen old runtime repo
- frozen old runtime repo は development target にしていない
- frozen old runtime repo は modify していない

## Labels audited
- `com.afrog.btc-monitor`
- `com.afrog.btc-review-form`
- `com.afrog.btc-ai-post-reviews`
- `com.afrog.btc-feedback-daily-sync`

## Installed LaunchAgents before state
- 4 本とも `~/Library/LaunchAgents/` に存在していた
- launchctl 上の program / working directory / stdout / stderr は frozen old runtime を指していた
- `com.afrog.btc-monitor` と `com.afrog.btc-review-form` は running
- `com.afrog.btc-ai-post-reviews` と `com.afrog.btc-feedback-daily-sync` は loaded だが not running

## Files changed under `~/Library/LaunchAgents/`
- `~/Library/LaunchAgents/com.afrog.btc-monitor.plist`
- `~/Library/LaunchAgents/com.afrog.btc-review-form.plist`
- `~/Library/LaunchAgents/com.afrog.btc-ai-post-reviews.plist`
- `~/Library/LaunchAgents/com.afrog.btc-feedback-daily-sync.plist`

## Backups created
- `~/Library/LaunchAgents/_btc_monitor_backup_20260701/com.afrog.btc-monitor.plist`
- `~/Library/LaunchAgents/_btc_monitor_backup_20260701/com.afrog.btc-review-form.plist`
- `~/Library/LaunchAgents/_btc_monitor_backup_20260701/com.afrog.btc-ai-post-reviews.plist`
- `~/Library/LaunchAgents/_btc_monitor_backup_20260701/com.afrog.btc-feedback-daily-sync.plist`

## Reload / restart actions taken
- changed 4 本を canonical repo の deploy plist で置換した
- `launchctl bootout gui/$(id -u) <plist>` を 4 本に対して実行した
- `launchctl bootstrap gui/$(id -u) <plist>` を 4 本に対して実行した
- その結果、running label は canonical repo path で再起動された

## Post-change verification
- `launchctl print gui/$(id -u)/com.afrog.btc-monitor` は canonical repo path を表示した
- `launchctl print gui/$(id -u)/com.afrog.btc-review-form` は canonical repo path を表示した
- `launchctl print gui/$(id -u)/com.afrog.btc-ai-post-reviews` は canonical repo path を表示した
- `launchctl print gui/$(id -u)/com.afrog.btc-feedback-daily-sync` は canonical repo path を表示した
- installed target plist から `/Users/marupro/CODEX/01_active/BTC_FX_CODEX` は消え、`/Users/marupro/CODEX/100_MCP_Server/btc_monitor` が入っていることを確認した

## Remaining old path references, if any
- この 4 本の installed LaunchAgent には残っていない
- frozen old runtime を説明する docs / history には旧 path が残るが、これは許容される履歴参照である

## Processes still pointing to old runtime, if any
- launchctl print 上では none
- 4 ラベルはいずれも canonical repo path を参照している

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no trading logic change
- no OHLCV fetch
- no unrelated launchd service edit
- no progress HTML / `CURRENT_PROGRESS.md` edit

## What was not run
- frozen old runtime repo への変更
- launchctl 以外の runtime 操作
- 手動での `main.py` / `log_feedback.py` / `run_daily_feedback_sync.sh` / `run_ai_post_reviews.sh` 実行
- trading / order / private endpoint 操作
- OHLCV fetch
- progress HTML 更新

## Next recommendation
- `BTCFX-20260701-IMAC-RUNTIME-CANONICAL-VERIFY`
- Goal: one normal launchd cycle 後に iMac runtime outputs/logs が canonical repo から出ていることを確認する
