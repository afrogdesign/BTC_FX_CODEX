# CANONICAL_REPO_CLEANUP_ARCHIVE_20260701

## Purpose
canonical repo 内の明らかに安全な旧式・重複・実行不要ファイルを `_archive/cleanup_20260701/` へ移して整理した記録である。削除はしていない。

## Canonical repo
- `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

## Archive root
- `_archive/cleanup_20260701/`

## Cleanup policy
- active source / tests / tools / deploy / current orchestration entrypoints は壊さない
- 旧式の歴史資料、旧構想、legacy-only docs、current flow から外れた reference material だけを archive する
- move only, delete しない
- 既存 archive 先に上書きしない

## What was archived
- `docs/operations/ai-orchestration/legacy/chatgpt_AGENT_GITHUB_LEGACY.md` -> `_archive/cleanup_20260701/docs/operations/ai-orchestration/legacy/chatgpt_AGENT_GITHUB_LEGACY.md`
- `docs/operations/deploy/Ver02_6_v2_MBP2020_FROZEN_RUNNER_20260609.md` -> `_archive/cleanup_20260701/docs/operations/deploy/Ver02_6_v2_MBP2020_FROZEN_RUNNER_20260609.md`
- `運用資料/参考資料/旧構想/` -> `_archive/cleanup_20260701/運用資料/参考資料/旧構想/`
- `運用資料/参考資料/SNS向け情報整理/` -> `_archive/cleanup_20260701/運用資料/参考資料/SNS向け情報整理/`

## What was kept active
- current orchestration docs and checkpoint docs
- `docs/operations/deploy/Ver03-v2_*` historical deploy docs referenced by current docs/tests/tools
- `運用資料/reports/Ver02.3のレポート/` and `運用資料/reports/Ver02までのレポート/` because current tools/tests still reference their README anchors
- `chatgpt/README.md` で案内される current chatgpt scaffold files
- `Branch_Command/` helpers

## What needs user decision
- none in this cleanup pass

## What was intentionally ignored
- untracked progress HTML
- `CURRENT_PROGRESS.md`
- rescued runtime-generated reports
- `.DS_Store`
- caches / `.venv*/`
- frozen old runtime repo

## Reference checks performed
- current orchestration docs and strategy docs
- `AGENTS.md`
- `README.md`
- `docs/operations/ai-orchestration/*.md`
- `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`
- `tests/`
- `tools/`
- `src/`
- `scripts/`
- `deploy/`
- `main.py`
- `.env.example`
- `.gitignore`
- targeted `rg` checks for the archived basenames and directories

## Validation commands
```bash
pwd -P
git status --short --branch
git diff --check
./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json
./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json
plutil -lint deploy/com.afrog.btc-monitor.plist
plutil -lint deploy/com.afrog.btc-review-form.plist
plutil -lint deploy/com.afrog.btc-ai-post-reviews.plist
plutil -lint deploy/com.afrog.btc-feedback-daily-sync.plist
```

## Safety boundary
- no trading logic change
- no OHLCV fetch
- no private/account/order endpoint
- no runtime restart
- no frozen old runtime modification
- no progress HTML update

## Recovery note
- archived files were moved, not deleted, and can be restored from `_archive/cleanup_20260701/`

## Next recommendation
- `BTCFX-20260701-CANONICAL-REPO-CLEANUP-VERIFY`
- Goal: verify safe report-only checks after archived cleanup and decide whether any `needs_user_decision` files should be archived later
