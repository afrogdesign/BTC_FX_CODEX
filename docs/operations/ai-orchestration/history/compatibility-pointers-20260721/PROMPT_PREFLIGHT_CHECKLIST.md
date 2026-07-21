# PROMPT_PREFLIGHT_CHECKLIST

Compatibility checklist. The canonical process is `AI_WORKFLOW.md`.

Before sending Codex work, ChatGPT confirms:

1. one coherent goal
2. product/trading/safety judgment already resolved
3. observable contract and allowed edit files known
4. Codex has freedom over helper/cache/fixture mechanics
5. minimum development validation is known
6. full bundle or heavy replay is excluded unless this is an explicit acceptance run
7. runtime/push/order boundary is explicit when relevant

Heavy-run preflight:

- Is the implementation already review-ready?
- Does real-data execution prove something MCP/static/fixture review cannot?
- Is one full run sufficient?
- Is a second full run truly acceptance-critical?
- Are expected replay/evaluation work units stated?

For the same Codex thread, omit unchanged history and stable boilerplate. Add `Known state`, `Allowed read`, detailed contracts, and heavy-run authorization only when they changed or prevent ambiguity.

Use `AUTO_SEND` only after these checks pass. Otherwise keep the decision in ChatGPT and do not issue an executable prompt.
