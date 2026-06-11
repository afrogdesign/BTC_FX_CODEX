You are working in repo `afrogdesign/BTC_FX_CODEX` on branch `Ver03-v3` at `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.

Use repo正本 over chat history.

Read, in this order:
1. `AGENTS.md`
2. `docs/operations/ai-orchestration/RESUME.md`
3. `docs/operations/ai-orchestration/CONTROL.md`
4. `docs/operations/ai-orchestration/PROMPTS.md`
5. `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
6. `docs/operations/ai-orchestration/TASK_LEDGER.md` only as needed, preferably the latest rows

Then report one of:
- `READY`
- `BLOCKED: <one specific question>`
- `NEEDS_REVIEW: <one short reason>`

Do not start implementation until the user explicitly asks.

Also write the final compact report to: `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` if the new AI is Codex or has local filesystem access.
ChatGPT-only web threads without local filesystem access do not need to write that file.
