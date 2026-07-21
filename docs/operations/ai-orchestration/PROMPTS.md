# PROMPTS

Compatibility entry only. The canonical prompt and execution rules are in `AI_WORKFLOW.md`.

Do not read this file together with `MINI_CODEX_RULES.md` or `PROMPT_PREFLIGHT_CHECKLIST.md`.

## Default same-thread implementation prompt

```text
AUTO_SEND

WORK_ID: <id>
MODE: BOUNDED_CODEX

Goal
- <one result>

Edit
- <files>

Autonomy
- helper/cache/fixture choices inside the accepted contract are Codex-owned
- obvious in-scope bugs may be fixed without another round trip

Do
1. <change>
2. <focused regression>

Validation budget
- matching tests and small fixture only
- no full bundle or repeated full replay unless explicitly authorized

Stop
- <task-specific blocker>
- preserve unrelated changes

Commit / Push
- <commit instruction>
- push: none | explicit checkpoint

Report
- compact report
- response.txt exactly one write
```

## Acceptance-run prompt

Use a separate task after ChatGPT review.

```text
AUTO_SEND

WORK_ID: <acceptance id>
MODE: BOUNDED_CODEX

Goal
- validate the reviewed implementation with one bounded real-data run

Validation budget
- one full bounded command
- no implementation redesign
- no unchanged rerun after failure
- second full run only when explicitly authorized for critical determinism

Commit / Push
- source edit: none unless separately authorized
- push: none
```

Add detailed known state, read scope, safety boundaries, CLI/output contracts, or heavy-run authorization only when new or materially changed.

Supported modes:

- `BOUNDED_CODEX`
- `REVIEW_ONLY`
- `CHECKPOINT_PUSH`
- `RUNTIME_TASK`

Full process: `AI_WORKFLOW.md`.
