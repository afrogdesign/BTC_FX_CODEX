# CANONICAL_CHECKPOINT_PUSH_PREP_20260701

## Purpose
canonical repo switch 後の状態を、後で user-managed GitHub pull に渡せる checkpoint package として整理する。ここでは push しない。

## Current canonical repo
- `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- 以後の local canonical repo はここで固定する

## Frozen old runtime boundary
- `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` は frozen old runtime repo
- 旧 repo を development target にしない
- 旧 repo source / tests / docs / scripts / config はコピーしない
- 旧 repo への pull / push / sync / runtime 起動はしない

## Current branch
- `Ver03-v4`
- upstream: `origin/Ver03-v4`
- current status: ahead of upstream by 40 commits

## Current HEAD
- `59b3ba6` - `docs: smoke canonical runtime repo`
- previous checkpoint commit: `bd09cc1` - `ops: switch canonical runtime repo`

## Commits included in this checkpoint window
- `bd09cc1 ops: switch canonical runtime repo`
- `59b3ba6 docs: smoke canonical runtime repo`

## Files changed since canonical switch phase
- docs / runbook updates for canonical switch
- deploy plist path updates to canonical repo
- smoke record doc for canonical runtime smoke
- NEXT_ACTION updates for the smoke and prep steps

## Local-only generated / rescued files that must not be committed
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260701.md`
- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260701.md`
- `運用資料/reports/feedback_daily_sync_20260701.md`
- existing untracked progress files remain untouched and outside this checkpoint

## Deploy plist canonical path confirmation
- `deploy/com.afrog.btc-monitor.plist`
- `deploy/com.afrog.btc-review-form.plist`
- `deploy/com.afrog.btc-ai-post-reviews.plist`
- `deploy/com.afrog.btc-feedback-daily-sync.plist`
- all point to `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

## Report-only smoke confirmation
- `describe-current-manual-delivery-app-contract --stdout-json`
- `export-current-manual-delivery-app-surface`
- `check-current-manual-delivery-app-surface --stdout-json`
- report-only surface path passed in the canonical repo

## Evidence-quality status summary
- `evidence_quality_summary` is present
- `ohlcv_source_coverage_summary` is present
- `ohlcv_range_freshness_status` is `stale_before_latest_candidate`
- `candidate_max_after_ohlcv_end_hours` is about `479.8`
- `candidate_rows` 1418, `ohlcv_valid_rows` 499, `window_missing_rows` 1330
- stale OHLCV coverage is visible; evidence interpretation is still limited by stale range

## Known caveat
- `OHLCV stale coverage warning` was not present as a separate literal in the checked app artifacts for this smoke
- however, freshness fields/status/note were present and the stale state was still visible

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no OHLCV fetch
- no trading logic change
- no runtime restart / live execution

## Manual user pull model
- After the next explicit checkpoint push, the user can manually pull from GitHub into the desired runtime environment
- Until then, `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` remains the local canonical repo
- `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` remains frozen and should not be used as a development target

## Validation commands
```bash
pwd -P
git status --short --branch
git diff --check -- docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_PREP_20260701.md docs/operations/ai-orchestration/NEXT_ACTION.md
git diff --name-only
git status --short --branch
git diff --cached --check
git diff --cached --name-only
git diff --cached --stat
```

## Next action
- `BTCFX-20260701-CANONICAL-CHECKPOINT-PUSH`
- Goal: push the canonical checkpoint branch to GitHub so the user can manually pull the clean checkpoint later.
