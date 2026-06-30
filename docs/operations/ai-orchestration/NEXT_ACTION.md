# NEXT_ACTION

- current_work_id: `BTCFX-20260701-CANONICAL-REPO-CLEANUP-VERIFY`
- mode: `CLEANUP_VERIFY`

## Current goal

`_archive/cleanup_20260701/` への cleanup archive 後に、canonical repo が安全に動作することを確認する。

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `README.md`, `docs/operations/ai-orchestration/START_HERE.md`, `docs/operations/ai-orchestration/RESUME.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md`, `docs/operations/ai-orchestration/REPO_MAP.md` |
| Edit | `docs/operations/ai-orchestration/CANONICAL_REPO_CLEANUP_VERIFY_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | archive 直後の canonical repo を verify し、active entrypoints と report-only surface が壊れていないことを確認する |
| Tests | `pwd -P`, `git status --short --branch`, archive path existence checks, active entrypoint existence checks, `git diff --check`, `git diff --name-only`, `git status --short --branch`, after staging docs only diff checks, smoke commands `describe-current-manual-delivery-app-contract --stdout-json`, `check-current-manual-delivery-app-surface --stdout-json`, `export-current-manual-delivery-app-surface`, deploy plist canonical path confirmation |
| Commit policy | verify docs と NEXT_ACTION を 1 checkpoint にまとめる |
| Stop | current directory が違う、archived files are missing unexpectedly、active entrypoints are missing、report-only smoke fails、evidence/safety fields are missing from expected surfaces、deploy plist validation fails、active deploy/run/config points to frozen old runtime、frozen old runtime repo must be touched、additional archive move becomes necessary、source/test/tools/scripts/deploy edits become necessary、runtime process / launchctl / cron / external LaunchAgents are needed、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order endpoint access becomes necessary、generated/log/local artifacts would need to be committed unexpectedly、progress HTML or CURRENT_PROGRESS.md needs editing、validation fails、untracked files cannot be safely classified、allowed外ファイルがstageされる |

## Next recommended follow-up

- `USER_DECISION_REQUIRED`
- Goal: wait for user decision before further cleanup, runtime work, or Phase G/product work.
