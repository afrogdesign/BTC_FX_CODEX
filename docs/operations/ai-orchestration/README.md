# AI Orchestration

This directory is the operating anchor for ChatGPT / Codex / future agents.

## Purpose

Reduce Codex cost and prevent context drift.

ChatGPT handles:

- repository review
- planning
- task decomposition
- design decisions
- final review

Codex handles:

- editing specified files
- running specified validation
- commit / push
- compact reporting

## Files

| File | Role |
|---|---|
| `CONTROL.md` | Current objective, constraints, next task |
| `TASK_LEDGER.md` | Work ID ledger |
| `DECISIONS.md` | Durable design decisions |
| `REPO_MAP.md` | Repository map for AI readers |
| `PROMPTS.md` | Short prompt templates |
| `handoffs/CURRENT_HANDOFF.md` | Thread handoff anchor |

## Rule

Do not put long project history in prompts.

Use:

```text
NEXT <WORK_ID>
Goal: ...
Read: ...
Edit: ...
Test: ...
Stop: ...
Report: compact
```
