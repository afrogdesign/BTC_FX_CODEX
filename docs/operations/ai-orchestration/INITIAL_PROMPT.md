You are working in repo `afrogdesign/BTC_FX_CODEX`.

Primary MCP/Codex working repo:
`/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

Frozen old runtime execution repo:
`/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`

Use repo-local docs as source of truth over chat history.
Read the current branch from repo state and `CONTROL.md`.

Tier 0: always read
1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

Tier 1: read when current state is needed
3. `docs/operations/ai-orchestration/CURRENT_STATE.md`
4. `docs/operations/ai-orchestration/NEXT_ACTION.md`
5. `docs/operations/ai-orchestration/CONTROL.md`

Tier 2: read only by task type
- `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- relevant strategy docs
- `docs/operations/ai-orchestration/PROMPTS.md`
- `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`
- `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`
- `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md`
- `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md`

Do not read these by default at startup:
- `docs/operations/ai-orchestration/TASK_LEDGER.md`
- `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`

Rules:
- do not start implementation until the user explicitly asks
- during normal MCP orchestration tasks, do not edit, run, inspect, or sync the frozen old runtime execution repo
- use the lightest read set that is enough for the current task
- prefer `BOUNDED_CODEX` when fixed-scope implementation is requested

Then report one of:
- `READY`
- `BLOCKED: <one specific question>`
- `NEEDS_REVIEW: <one short reason>`

Write the final compact report to:
`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`
only when the acting AI is Codex or otherwise has local filesystem access.
