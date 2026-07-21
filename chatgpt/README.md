# ChatGPT Directory

This directory stores implementation contracts, templates, and optional strict task tooling. It is not the project entrypoint.

## Canonical entrypoint

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

Then follow only the route required by the current task.

## Directory roles

| Path | Role |
|---|---|
| `chatgpt/specs/active/` | exactly one current detailed implementation contract when needed |
| `chatgpt/specs/archive/` | accepted or superseded implementation contracts |
| `chatgpt/templates/` | optional specification templates |
| `chatgpt/tasks/` | optional strict manifest/report tooling; not the normal route |

Historical May 2026 analysis notes were moved to:

`_archive/legacy_chatgpt_analysis_20260721/`

## Rules

- Do not select work from archived analysis or archived specs.
- Current plan and state live under `docs/operations/ai-orchestration/`.
- Active implementation requirements live in `chatgpt/specs/active/` only when a spec exists.
- Generated reports use `local/reports/` and remain local/uncommitted.
- A1 manifest tooling is used only when strict machine alignment adds material evidence.
