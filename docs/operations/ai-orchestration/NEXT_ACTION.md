# NEXT_ACTION

- current_work_id: `BTCFX-20260701-CANONICAL-RUNTIME-SMOKE-CHECK`
- mode: `CANONICAL_REPO_SMOKE`

## Current goal

canonical repo の report-only smoke を確認し、主要 surface と rescued runtime-generated reports が使える状態を記録する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/CANONICAL_REPO_SWITCH_20260701.md`, `docs/operations/ai-orchestration/CANONICAL_RUNTIME_SMOKE_CHECK_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/CANONICAL_RUNTIME_SMOKE_CHECK_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | canonical repo の report-only smoke を記録し、主要 surface と rescued runtime-generated reports が使えることを確認する |
| Tests | `pwd -P`, `git status --short --branch`, deploy plist validation, report-only smoke commands, `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | smoke 記録の区切りとして docs 2ファイルのみ 1 commit |
| Stop | old repo must be touched、old repo source/test/docs/tools/scripts/config must be copied、external system files must be edited、source/test changes become necessary、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order/live execution becomes necessary、live start/restart is needed、rescued generated/log/local artifacts would need to be committed、progress HTML or CURRENT_PROGRESS.md needs to be edited、any validation fails、unexpected uncommitted changes exist before editing and are not clearly unrelated |

## Next recommended follow-up

- `BTCFX-20260701-CANONICAL-CHECKPOINT-PUSH-PREP`
- Goal: prepare a final checkpoint push package so the user can later manually pull the canonical repo state into the runtime environment via GitHub.
