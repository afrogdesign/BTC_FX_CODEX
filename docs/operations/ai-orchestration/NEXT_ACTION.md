# NEXT_ACTION

- current_work_id: `BTCFX-20260702-IMAC-RUNTIME-CANONICAL-24H-VERIFY`
- mode: `RUNTIME_24H_VERIFY`

## Current goal

canonical repo に統一した iMac runtime / launchd が 24 時間以上経過後も canonical path を使い続けているかを read-only で確認する。

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `docs/operations/ai-orchestration/IMAC_RUNTIME_LAUNCHD_CANONICAL_SWITCH_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_REPO_CLEANUP_VERIFY_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `deploy/com.afrog.btc-monitor.plist`, `deploy/com.afrog.btc-review-form.plist`, `deploy/com.afrog.btc-ai-post-reviews.plist`, `deploy/com.afrog.btc-feedback-daily-sync.plist`, current runtime logs, current reports, old runtime logs/reports read-only` |
| Edit | `docs/operations/ai-orchestration/IMAC_RUNTIME_CANONICAL_24H_VERIFY_20260702.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | canonical launchd / process / logs / outputs / old-repo comparison を read-only で確認し、24h 効果を記録する |
| Tests | `pwd -P`, `date '+%Y-%m-%d %H:%M:%S %z'`, `git status --short --branch`, deploy plist validation and path checks, installed LaunchAgents path checks, `launchctl list` / `launchctl print` read-only, process audit read-only, runtime log mtime/tail checks, old repo mtime comparison, smoke commands `describe-current-manual-delivery-app-contract --stdout-json`, `check-current-manual-delivery-app-surface --stdout-json`, `git diff --check`, `git diff --name-only`, `git status --short --branch`, after staging docs only diff checks |
| Commit policy | 24h verify docs と NEXT_ACTION を 1 checkpoint にまとめる |
| Stop | current directory が違う、installed LaunchAgents point to frozen old runtime、a running process still points to old runtime、old runtime repo has fresh writes after switch、report-only smoke fails、evidence/safety fields are missing from expected surfaces、source/test/tools/scripts/deploy edits become necessary、runtime restart / launchctl modification becomes necessary、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order endpoint access becomes necessary、generated/log/local artifacts would need to be committed unexpectedly、progress HTML or CURRENT_PROGRESS.md needs editing、validation fails、untracked files cannot be safely classified、allowed外ファイルがstageされる |

## Next recommended follow-up

- `USER_DECISION_REQUIRED`
- Goal: wait for user decision before further cleanup, runtime work, or Phase G/product work after 24h verification.
