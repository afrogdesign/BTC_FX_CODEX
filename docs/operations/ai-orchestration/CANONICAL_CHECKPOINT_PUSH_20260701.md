# CANONICAL_CHECKPOINT_PUSH_20260701

## Purpose
canonical repo の checkpoint push 前の内容を固定し、後から user が GitHub 経由で manual pull できる状態へ送る準備を記録する。

## Canonical repo
- `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- ここが現在の canonical repo であり、唯一の push target である

## Branch / upstream
- branch: `Ver03-v4`
- upstream: `origin/Ver03-v4`
- pre-push status: ahead of upstream

## Pre-push HEAD
- `85f61ee` - `docs: prepare canonical checkpoint push`

## Outgoing commits summary
- `bd09cc1` - `ops: switch canonical runtime repo`
- `59b3ba6` - `docs: smoke canonical runtime repo`
- `85f61ee` - `docs: prepare canonical checkpoint push`

## Local-only files not pushed
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260701.md`
- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260701.md`
- `運用資料/reports/feedback_daily_sync_20260701.md`
- existing untracked progress files remain local and are not part of this push

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no OHLCV fetch
- no trading logic change
- no runtime restart / live execution
- frozen old runtime repo は触らない

## What was not run
- frozen old runtime repo への編集 / sync / pull
- launchctl / cron
- external LaunchAgents
- live start / restart
- progress HTML / `CURRENT_PROGRESS.md` の編集
- generated report commit

## Push command planned
```bash
git push origin Ver03-v4
```

## User manual pull note
- この push の後、user は必要な runtime 環境へ GitHub 経由で手動 pull できる
- その時点までは canonical repo `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` を local 正本として扱う
- frozen old runtime repo `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` は開発対象にしない

## Post-push verification plan
- `git status --short --branch`
- `git log --oneline --decorate -n 5`
- branch が `origin/Ver03-v4` と一致すること、または Git が報告する ahead/behind state を記録する

## Next action
- `BTCFX-20260701-CANONICAL-CHECKPOINT-PUSH`
- Goal: canonical checkpoint branch を GitHub に push して、後から user が clean checkpoint を manual pull できるようにする
