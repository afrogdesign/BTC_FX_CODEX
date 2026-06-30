# NEXT_ACTION

- current_work_id: `BTCFX-20260630-ORCHESTRATION-CHECKPOINT-PUSH-DESIGN`
- mode: `LIGHT_CODEX`

## Current goal

MCP-primary / no-routine-push を repo-local default にし、軽い current-control と legacy/reference の分離を進める。

## Current summary

| Field | Value |
|---|---|
| Read | `AGENTS.md`, `README.md`, `docs/operations/ai-orchestration/*` の指定ファイル、`docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` |
| Edit | `AGENTS.md`, `chatgpt/README.md`, `CONTROL.md`, `MILESTONES.md`, `CLEANUP_CANDIDATES.md`, `START_HERE.md`, `CURRENT_STATE.md`, `NEXT_ACTION.md`, `README.md`, `RESUME.md`, `PROMPTS.md`, `REPO_MAP.md`, `legacy/chatgpt_AGENT_GITHUB_LEGACY.md` |
| Do not | `src/`, `tools/`, `tests/`, `scripts/`, `logs/`, `local/`, `.venv312/`, generated outputs, `TASK_LEDGER.md`, `CURRENT_HANDOFF.md`, old runtime execution repo |
| Test | `git diff --check`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Stop | git repo でない、unexpected uncommitted changes、scope 外編集が必要、runtime/source/generated edit が必要、deletion が必要、test/check fail、push required |

## Next recommended follow-up

- `BTCFX-20260630-ORCHESTRATION-CLEANUP-AUDIT-PASS`
- Goal: review cleanup candidates and classify what can be archived later, without deleting files.
