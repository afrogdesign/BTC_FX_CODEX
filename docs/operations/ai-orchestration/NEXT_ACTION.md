# NEXT_ACTION

- current_work_id: `BTCFX-20260701-CANONICAL-RUNTIME-REPO-SWITCH`
- mode: `CANONICAL_REPO_SWITCH`

## Current goal

`/Users/marupro/CODEX/100_MCP_Server/btc_monitor` を唯一の正本・実行元として固定し、`/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` を frozen old runtime として扱う。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/CANONICAL_REPO_SWITCH_20260701.md`, `docs/operations/ai-orchestration/DEVELOPMENT_TO_RUNTIME_HANDOFF_CHECKPOINT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/CANONICAL_REPO_SWITCH_20260701.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | canonical repo switch を文書化して唯一の正本・実行元を固定する |
| Tests | `git diff --check`, old-path audit after edits, repo-owned entrypoint syntax checks if executable files changed, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | canonical switch の区切りとして docs / runbook 変更のみ 1 commit |
| Stop | old repo must be modified、old repo source/test/docs/tools/scripts/config must be copied、ambiguous recently updated old-runtime file looks important、external system files must be edited、source/test changes become necessary、trading logic changes become necessary、OHLCV fetch becomes necessary、private/account/order/live execution becomes necessary、live start/restart is needed、rescued generated/log/local artifacts would need to be committed、progress HTML or CURRENT_PROGRESS.md needs to be edited、unresolved old active execution path remains in a current run/start/config file、any validation fails、unexpected uncommitted changes exist before editing and are not clearly unrelated |

## Next recommended follow-up

- `BTCFX-20260701-CANONICAL-RUNTIME-SMOKE-CHECK`
- Goal: run safe report-only smoke checks from the canonical repo and confirm active surfaces work without touching frozen old runtime or live execution.
