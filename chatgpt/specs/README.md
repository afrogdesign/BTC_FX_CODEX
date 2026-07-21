# Implementation Specs

This directory contains detailed implementation contracts for bounded Codex work.

## Structure

- `active/`: zero or one current implementation contract
- `archive/`: accepted, completed, canceled, or superseded contracts

## Rules

- Planning and current-task selection happen under `docs/operations/ai-orchestration/`.
- Only a sufficiently fixed implementation contract is placed in `active/`.
- Codex reads the named active spec and the files explicitly required by the task.
- ChatGPT performs acceptance review and moves the spec to `archive/` after acceptance.
- An empty `active/` directory means there is no authorized implementation task.
- Archived specs are historical evidence and never override current source, tests, or canonical planning documents.
