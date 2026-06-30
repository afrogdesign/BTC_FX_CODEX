# NEXT_ACTION

- current_work_id: `BTCFX-20260701-CANONICAL-CHECKPOINT-PUSH`
- mode: `CHECKPOINT_PUSH`

## Current goal

canonical repo `Ver03-v4` を GitHub に checkpoint push し、user が後から manual pull できる状態にする。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/CANONICAL_REPO_SWITCH_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_RUNTIME_SMOKE_CHECK_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_PREP_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | canonical checkpoint を GitHub に push する前提の内容を文書化し、手動 pull 可能な状態にする |
| Tests | `pwd -P`, `git status --short --branch`, branch/upstream confirmation, outgoing commit range confirmation, deploy plist canonical path confirmation, old-path audit, `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | checkpoint push の区切りとして docs 2ファイルのみ 1 commit |
| Stop | branch/upstream が不明、expected checkpoint commits が欠ける、old repo must be touched、old repo source/test/docs/tools/scripts/config must be copied、external system files must be edited、source/test changes become necessary、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order/live execution becomes necessary、live start/restart is needed、rescued generated/log/local artifacts would need to be committed、progress HTML or CURRENT_PROGRESS.md needs to be edited、runtime repo reflection is needed、any validation fails、unexpected uncommitted changes exist before editing and are not clearly unrelated |

## Next recommended follow-up

- `USER_MANUAL_PULL_READY`
- Goal: user can manually pull the pushed canonical checkpoint from GitHub into the desired runtime environment when ready.
