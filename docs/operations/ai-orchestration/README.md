# AI Orchestration

This directory separates project setup, AI routing, accepted state, stable controls, implementation contracts, and history.

## Canonical route

```text
ChatGPT Project prompt: INITIAL_PROMPT.md
→ AGENTS.md
→ START_HERE.md
→ request-specific CURRENT_STATE / NEXT_ACTION / active spec
→ AI_WORKFLOW.md for execution or review
```

Same-thread work reads only the new report, changed files, matching tests, and relevant artifacts. Stable docs are not reread for every FIX.

## Canonical files

| File | Responsibility |
|---|---|
| `INITIAL_PROMPT.md` | ChatGPT Project initial prompt source |
| `AGENTS.md` | Codex worker rules and repo boundary |
| `START_HERE.md` | role-aware startup router |
| `AI_WORKFLOW.md` | analysis, implementation, review, and acceptance flow |
| `CURRENT_STATE.md` | accepted state and current blocker |
| `NEXT_ACTION.md` | exactly one current work item |
| `CONTROL.md` | stable safety, git, runtime, and validation controls |
| `MILESTONES.md` | accepted major checkpoints |
| `DECISIONS.md` | durable product/design decisions |
| active spec | current detailed implementation contract |
| `TASK_LEDGER.md` | historical Work ID lookup only |

## Current post-M5 route

M5 is accepted. The next orchestration improvement is the task-manifest foundation.

Design references:

- `AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md`
- `MACRO_REPLAY_AND_AI_ACCEPTANCE_SIMPLIFICATION_PLAN_20260721.md`

Sequence:

```text
AI orchestration docs checkpoint
→ A1 contract foundation
→ A2 low-risk pilot
→ A3 canonical activation
→ optional A4 CWT integration
```

Replay-stage/cache redesign is a later, separate route and is not part of A1.

## Compatibility files

These preserve old entry points but are not independent sources of truth:

- `PROMPTS.md`
- `MINI_CODEX_RULES.md`
- `PROMPT_PREFLIGHT_CHECKLIST.md`
- `CHATGPT_COMMANDER_PROMPT.md`
- `RESUME.md`

Do not read them together.

## Update rules

### Normal implementation or FIX

- do not update `CURRENT_STATE.md`, `CONTROL.md`, `MILESTONES.md`, or `TASK_LEDGER.md`
- add only a short factual active-spec note when pending contract evidence changes

### Acceptance or posture change

1. archive the active spec
2. update `CURRENT_STATE.md`
3. replace `NEXT_ACTION.md` with one next item
4. update `CONTROL.md` only if stable rules changed
5. add a milestone only for a major accepted checkpoint

### Project prompt change

- update only `INITIAL_PROMPT.md` as the canonical source
- keep execution detail in `AI_WORKFLOW.md`
- keep stable repo rules in `CONTROL.md`
- never add current Work IDs or task history to the project prompt

## History

Pre-optimization copies are preserved under:

- `history/record-optimization-20260721/`
- `history/ai-routing-optimization-20260721/`

Historical files are not default reads.
