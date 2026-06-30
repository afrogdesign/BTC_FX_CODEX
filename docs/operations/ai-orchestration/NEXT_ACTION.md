# NEXT_ACTION

- current_work_id: `BTCFX-20260701-CANONICAL-REPO-CLEANUP-ARCHIVE`
- mode: `CLEANUP_ARCHIVE`

## Current goal

canonical repo 内の不要・旧式・重複・実行不要になったファイルを安全に `_archive/cleanup_20260701/` へ移して整理する。

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `README.md`, `docs/operations/ai-orchestration/START_HERE.md`, `docs/operations/ai-orchestration/RESUME.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `docs/operations/ai-orchestration/REPO_MAP.md` |
| Edit | `docs/operations/ai-orchestration/CANONICAL_REPO_CLEANUP_ARCHIVE_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | safe archive candidates を棚卸しし、明らかに安全な古い docs / reference material を `_archive/cleanup_20260701/` へ move する |
| Tests | `pwd -P`, `git status --short --branch`, targeted reference checks, `git diff --check`, `git diff --name-only`, `git status --short --branch`, after staging docs only diff checks, smoke commands `describe-current-manual-delivery-app-contract --stdout-json` and `check-current-manual-delivery-app-surface --stdout-json`, deploy plist canonical path confirmation |
| Commit policy | archive moves と docs を 1 checkpoint としてまとめる |
| Stop | current directory が違う、candidate is ambiguous and important、moving a candidate would break current references、archive target conflict、frozen old runtime repo must be touched、active source/test/tools/scripts/deploy need edits、active orchestration entrypoints would need archiving、runtime process / launchctl / cron / external LaunchAgents are needed、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order endpoint access becomes necessary、generated/log/local artifacts would need to be committed unexpectedly、progress HTML or CURRENT_PROGRESS.md needs editing、validation fails、untracked files cannot be safely classified、allowed外ファイルがstageされる |

## Next recommended follow-up

- `BTCFX-20260701-CANONICAL-REPO-CLEANUP-VERIFY`
- Goal: verify safe report-only checks after archived cleanup and decide whether any `needs_user_decision` files should be archived later.
