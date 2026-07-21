# NEXT_ACTION

- current_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A3-ROUTING-IMPL-01`
- mode: `BOUNDED_CODEX`
- revision: `1`
- expected_branch: `Ver04-v2`
- expected_base_commit: `95840ef4de0aa7d88972f35df37b7dac9f078f65`
- active_spec: `chatgpt/specs/active/20260721_ai_task_manifest_a3_canonical_routing.md`
- manifest: `chatgpt/tasks/active/20260721_a3_canonical_routing.implementation.json`
- task_sha256: `ba2129a0bcdbd410d1589bbe111acd634e67ddae5dc87401648034e6e29156ec`
- status: ready for A3 implementation
- push: none

## Goal

Activate the accepted task-manifest flow as the default ChatGPT-to-Codex route while retaining hand-written prompts as an explicit fallback.

## Content edit files

- `AGENTS.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/AI_WORKFLOW.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/INITIAL_PROMPT.md`

Only these five files may receive content edits. The A2 archive transition, state files, milestone file, A3 active spec, and A3 manifest are ChatGPT supplied and must remain byte-for-byte unchanged while being staged in the same commit.

## Required behavior

- validated manifests under `chatgpt/tasks/active/` are the normal route for new Codex tasks
- `validate-task` precedes execution
- `render-prompt` provides the compact launcher
- the manifest is immutable after execution starts
- pre-execution corrections increment revision; material scope changes use a new Work ID
- manifest-driven reports use `json_v1` and pass `validate-report` before ChatGPT review
- ChatGPT retains direct MCP review and acceptance authority
- acceptance remains a separate reviewed-commit-bound stage when heavy evidence is needed
- hand-written prompts remain an explicit reason-recorded fallback

## Boundaries

- no automatic execution, acceptance, or next-task selection
- no optional transport integration
- no replay redesign or M6
- no production or runtime posture change
- no heavy validation
- preserve unrelated dirty files
- no reset, restore, checkout, clean, or stash manipulation

## Commit and report

- commit message: `docs(ai): activate manifest routing`
- stage exactly the sixteen manifest paths
- create `/tmp/btc_monitor_a3_implementation_report.json` after the commit
- report every manifest requirement and every listed validation command in manifest order
- self-validate the final report exactly once
- write the identical validated JSON once to the canonical outbox
- push: none

This file contains exactly one current task.
