# ChatGPT Directory

This directory stores implementation contracts and historical analysis. It is not the project entrypoint.

## Canonical entrypoint

Read:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

Then follow the request-specific route defined there.

## Directory roles

| Path | Role |
|---|---|
| `chatgpt/specs/active/` | exactly one current detailed implementation contract when needed |
| `chatgpt/specs/archive/` | accepted or historical implementation contracts |
| `chatgpt/analysis/` | historical analysis; non-default read |
| `chatgpt/templates/` | optional templates |
| `chatgpt/tasks/` | optional strict task-contract tooling |

## Rules

- Do not use `chatgpt/analysis/` to select the current task.
- Do not use archived specs as active requirements unless a current task names one for evidence.
- Current plan and state live under `docs/operations/ai-orchestration/`.
- Generated reports use `local/reports/` and remain local/uncommitted.
- Historical settings formerly stored in the retired operations area are archived under `_archive/legacy_operations_materials_20260721/`.

## Current sources of truth

- overall plan: `docs/operations/ai-orchestration/MASTER_PLAN.md`
- current state: `docs/operations/ai-orchestration/CURRENT_STATE.md`
- next action: `docs/operations/ai-orchestration/NEXT_ACTION.md`
- workflow: `docs/operations/ai-orchestration/AI_WORKFLOW.md`
- controls: `docs/operations/ai-orchestration/CONTROL.md`
