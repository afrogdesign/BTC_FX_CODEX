# MINI_CODEX_RULES

Compatibility entry only.

Codex rules are canonical in:

1. `AGENTS.md`
2. `START_HERE.md`
3. `AI_WORKFLOW.md`

Same-thread Codex work should not reread these files unless context was lost or the new prompt conflicts with repo state. Use the prompt as a delta, inspect only named files and matching tests, run minimum validation, preserve unrelated changes, and return one compact report.
