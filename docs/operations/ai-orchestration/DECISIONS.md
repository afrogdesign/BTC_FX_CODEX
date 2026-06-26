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

## DEC-20260608-002: First Ver03-v2 implementation target is Active Plan intraperiod outcome specification

Date: 2026-06-08
Status: accepted
Related work: BTCFX-20260608-051

### Decision

After AI orchestration anchors and NEXT_TASK simplification, Ver03-v2 should resume product work by specifying Active Plan intraperiod outcomes before writing source code.

### Reason

The roadmap shows that the current candidate outcome coverage is still insufficient because it does not verify intraperiod high/low, entry zone reach, TP/SL first touch, or MFE/MAE.

The next useful step is to freeze the specification before implementing helper functions, tests, builder logic, and CLI wiring.

### Consequences

- Do not implement source code in 051.
- Next task 052 is a docs/spec task.
- daily-sync connection remains out of scope until helper, test, and builder layers are stable.
