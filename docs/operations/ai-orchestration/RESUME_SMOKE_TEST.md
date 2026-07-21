# RESUME_SMOKE_TEST

## Purpose

Confirm that a fresh AI context can resume safely without reading redundant orchestration files.

## Required checks

| Check | Expected result |
|---|---|
| `AGENTS.md` names the primary and frozen repos | pass |
| `AGENTS.md` distinguishes fresh context from retained context | pass |
| `START_HERE.md` has separate ChatGPT and Codex routes | pass |
| same-thread work is explicitly delta-only | pass |
| `AI_WORKFLOW.md` contains ChatGPT classification, Codex execution, review, and acceptance | pass |
| `CURRENT_STATE.md` contains current accepted state rather than full history | pass |
| `NEXT_ACTION.md` contains one current Work ID | pass |
| `CONTROL.md` contains stable rules rather than current-task history | pass |
| active implementation has at most one active spec | pass |
| `TASK_LEDGER.md`, handoffs, history, logs, and generated outputs are non-default reads | pass |
| prompt modes are limited to `BOUNDED_CODEX`, `REVIEW_ONLY`, `CHECKPOINT_PUSH`, and `RUNTIME_TASK` | pass |
| Codex reporting requires one `response.txt` write with no readback | pass |

## Pass route

Fresh ChatGPT:

```text
AGENTS.md
→ START_HERE.md
→ CURRENT_STATE.md
→ NEXT_ACTION.md
→ active spec
→ AI_WORKFLOW.md
```

Fresh Codex:

```text
AGENTS.md
→ START_HERE.md
→ task prompt
→ named files
```

Same-thread ChatGPT/Codex:

```text
new delta
→ changed or named files only
```

A smoke test fails if it requires reading `PROMPTS.md`, `MINI_CODEX_RULES.md`, and `PROMPT_PREFLIGHT_CHECKLIST.md` together.
