You are working in repo `afrogdesign/BTC_FX_CODEX`.

MCP/Codex working repo:
`/Users/marupro/CODEX/100_MCP_Server/btc_monitor`

Old runtime execution repo:
`/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`

Use repo-local `START_HERE.md` and `CONTROL.md` as source of truth.
Use repo正本 over chat history.
Read the current branch from repo state and `CONTROL.md`; do not hardcode an old branch from chat memory.

Read, in this order:
1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `docs/operations/ai-orchestration/RESUME.md`
4. `docs/operations/ai-orchestration/CURRENT_STATE.md`
5. `docs/operations/ai-orchestration/NEXT_ACTION.md`
6. `docs/operations/ai-orchestration/CONTROL.md`
7. `docs/operations/ai-orchestration/PROMPTS.md`
8. `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
9. `docs/operations/ai-orchestration/TASK_LEDGER.md` only as needed, preferably the latest rows

Rules:
- do not start implementation until the user explicitly asks
- old runtime execution repo is separate and is updated later by GitHub pull only
- do not edit or run the old runtime execution repo during normal MCP orchestration tasks

Then report one of:
- `READY`
- `BLOCKED: <one specific question>`
- `NEEDS_REVIEW: <one short reason>`

Also write the final compact report to:
`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`
if the new AI is Codex or has local filesystem access.
ChatGPT-only web threads without local filesystem access do not need to write that file.
