# NEXT_ACTION

- current_work_id: `BTCFX-20260701-IMAC-RUNTIME-LAUNCHD-CANONICAL-SWITCH`
- mode: `IMAC_RUNTIME_SWITCH`

## Current goal

iMac 上の btc_monitor 系 runtime / launchd / 実行ファイル参照を canonical repo に統一する。

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `docs/operations/ai-orchestration/CANONICAL_REPO_SWITCH_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_RUNTIME_SMOKE_CHECK_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_PREP_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/IMAC_RUNTIME_LAUNCHD_CANONICAL_SWITCH_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | iMac runtime launchd の 4 ラベルを canonical repo に統一し、必要なら `~/Library/LaunchAgents/` を更新する |
| Tests | `pwd -P`, `git status --short --branch`, repo-owned deploy plist canonical path confirmation, launchctl list/print audit, installed LaunchAgents audit, `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | runtime switch の記録として docs 2ファイルのみ 1 commit |
| Stop | current directory が違う、repo-owned deploy plist still points to frozen old runtime、installed LaunchAgent differs in non-path behavior from repo-owned plist、unrelated LaunchAgent would need editing、a running old-runtime process cannot be mapped to the four approved labels、frozen old runtime repo must be modified、source/test/trading files need changes、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order endpoint access becomes necessary、unrelated runtime/live process must be started、generated/log/local artifacts would need to be committed、progress HTML or CURRENT_PROGRESS.md needs editing、validation fails、allowed外ファイルがstageされる |

## Next recommended follow-up

- `BTCFX-20260701-IMAC-RUNTIME-CANONICAL-VERIFY`
- Goal: verify after one normal launchd cycle that iMac runtime outputs/logs are being produced from the canonical repo without touching frozen old runtime.
