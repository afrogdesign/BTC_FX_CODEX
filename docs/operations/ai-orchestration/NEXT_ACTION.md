# NEXT_ACTION

- current_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A3-ROUTING-FIX-01`
- mode: `BOUNDED_CODEX`
- expected_branch: `Ver04-v2`
- active_spec: `chatgpt/specs/active/20260721_ai_task_manifest_a3_canonical_routing.md`
- status: ready for one compact-report routing correction
- push: none

## Goal

Keep the useful A3 routing cleanup while restoring compact hand-written prompts and compact text reports as the normal route. Manifest and JSON validation remain optional strict tooling only when explicitly justified.

## Allowed content edits

- `AGENTS.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/AI_WORKFLOW.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/INITIAL_PROMPT.md`

The active spec and this `NEXT_ACTION.md` were prepared by ChatGPT. Stage them unchanged with the five routing documents.

## Required behavior

- normal tasks use the existing compact prompt template
- Codex returns the compact text report
- `response.txt` receives the same compact report exactly once
- manifest, `validate-task`, `render-prompt`, `json_v1`, and `validate-report` are optional strict tools, not the normal requirement
- no report-format-only review loop
- preserve role, dirty-tree, validation-budget, acceptance, and safety boundaries

## Validation

- one task-scoped `git diff --check` across the seven scoped files
- no JSON report generation or self-validation
- no tests, heavy validation, replay, runtime, network, mail, or notification action

## Commit

- message: `docs(ai): keep compact reporting default`
- stage only the five routing documents, the active spec, and this `NEXT_ACTION.md`
- push: none

This file contains exactly one current task.
