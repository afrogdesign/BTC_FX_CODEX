# NEXT_ACTION

- current_work_id: `BTCFX-20260721-AI-ORCHESTRATION-DOCS-CHECKPOINT-01`
- mode: `BOUNDED_CODEX`
- branch: confirm from repo state
- status: ready for docs-only validation and commit
- active_spec: none
- acceptance: not applicable
- push: none

## Goal

Commit the reviewed AI-orchestration routing, M5 acceptance records, task-manifest design, and preserved pre-optimization history as one docs-only checkpoint.

## Reviewed scope

- `AGENTS.md`
- M5 spec move from `chatgpt/specs/active/` to `chatgpt/specs/archive/`
- canonical orchestration docs: `START_HERE.md`, `AI_WORKFLOW.md`, `CONTROL.md`, `INITIAL_PROMPT.md`
- current records: `CURRENT_STATE.md`, `NEXT_ACTION.md`, `MILESTONES.md`, `DECISIONS.md`
- compatibility pointers: `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHATGPT_COMMANDER_PROMPT.md`, `RESUME.md`, `RESUME_SMOKE_TEST.md`
- navigation docs: `README.md`, `REPO_MAP.md`, `handoffs/CURRENT_HANDOFF.md`
- design docs: `AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md`, `MACRO_REPLAY_AND_AI_ACCEPTANCE_SIMPLIFICATION_PLAN_20260721.md`
- preserved history under `history/record-optimization-20260721/` and `history/ai-routing-optimization-20260721/`

## Validation

- confirm actual branch and starting HEAD
- inspect current status and docs-only diff
- verify no source, test, local artifact, runtime, or unrelated file is staged
- verify active specs contain only `.gitkeep`
- verify the archived M5 spec exists
- run task-scoped `git diff --check` on reviewed docs
- stage only reviewed docs and commit

## Commit

```text
docs: streamline AI routing and acceptance workflow
```

Push: none.

## After checkpoint

ChatGPT directly verifies the commit and then starts a new ChatGPT thread for bounded A1 active-spec creation.

A1 must remain limited to task/report schemas, examples, validator, prompt renderer, focused tests, and task README. Do not start CWT integration, replay-stage/cache work, M6, runtime, or production changes.

## Boundaries

- do not edit source or tests
- do not commit `local/` outputs
- do not change product/trading behavior
- do not reset, restore, checkout, clean, or manipulate stash state
- preserve all unrelated dirty changes

This file contains one current task only. Replace it after the docs checkpoint is accepted.
