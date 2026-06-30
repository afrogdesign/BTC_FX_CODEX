# NEXT_ACTION

- current_work_id: `BTCFX-20260701-CANONICAL-CHECKPOINT-PUSH-PREP`
- mode: `CHECKPOINT_PUSH_PREP`

## Current goal

canonical repo switch 後の状態を GitHub 経由で user が後から pull できる checkpoint package として整理する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/CANONICAL_REPO_SWITCH_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_RUNTIME_SMOKE_CHECK_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_PREP_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/CANONICAL_CHECKPOINT_PUSH_PREP_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | canonical repo の checkpoint push 用 package を整理し、user-managed pull に渡せる状態を文書化する |
| Tests | `pwd -P`, `git status --short --branch`, deploy plist canonical path confirmation, old-path audit, `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | checkpoint push prep の区切りとして docs 2ファイルのみ 1 commit |
| Stop | old repo must be touched、old repo source/test/docs/tools/scripts/config must be copied、external system files must be edited、source/test changes become necessary、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order/live execution becomes necessary、live start/restart is needed、rescued generated/log/local artifacts would need to be committed、progress HTML or CURRENT_PROGRESS.md needs to be edited、runtime repo reflection is needed、any validation fails、unexpected uncommitted changes exist before editing and are not clearly unrelated |

## Next recommended follow-up

- `BTCFX-20260701-CANONICAL-CHECKPOINT-PUSH`
- Goal: push the canonical checkpoint branch to GitHub so the user can manually pull the clean checkpoint later.
