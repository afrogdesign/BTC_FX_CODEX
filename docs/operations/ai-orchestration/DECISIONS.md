# AI Decisions

## DEC-20260608-001: Ver03-v2 begins with AI operation anchors

Date: 2026-06-08
Status: accepted
Related work: BTCFX-20260608-048

### Decision

Ver03-v2 starts by rebuilding ChatGPT / Codex / future-agent operation anchors before returning to trading-system implementation.

### Reason

The previous workflow became too expensive because each Codex task repeated long context, created many detailed logs, and required frequent placeholder hash updates.

The new workflow fixes this by placing stable context in repository files:

- `AGENTS.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/TASK_LEDGER.md`
- `docs/operations/ai-orchestration/PROMPTS.md`

### Consequences

- Codex prompts should become short.
- Codex reports should be compact.
- ChatGPT must confirm repository state before issuing tasks.
- Product implementation resumes after the AI operation anchors are stable.
