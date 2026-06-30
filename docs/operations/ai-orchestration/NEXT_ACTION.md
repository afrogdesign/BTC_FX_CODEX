# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ORCHESTRATION-MCP-OPS-OPTIMIZE`
- mode: `LIGHT_CODEX`

## Current goal

MCP primary workflow に合わせて AI orchestration docs を整理し、resume を速く安全にする。

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `README.md`, `docs/operations/ai-orchestration/*` の指定ファイル、`docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` |
| Edit | `AGENTS.md`, `START_HERE.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md`, `README.md`, `RESUME.md`, `INITIAL_PROMPT.md`, `PROMPTS.md`, `REPO_MAP.md` |
| Do not | `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `TASK_LEDGER.md`, `CONTROL.md`, `CURRENT_HANDOFF.md`, old runtime execution repo |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、test/check fail、branch/push ambiguity |

## Next recommended follow-up

- `BTCFX-20260630-ORCHESTRATION-CONTROL-SPLIT`
- Goal: split long `CONTROL.md` history into lighter current-control and milestone/history files without changing product behavior.
