# NEXT_ACTION

- current_work_id: `BTCFX-20260721-VER04-V3-REPO-CLEANUP-CHECKPOINT`
- mode: `BOUNDED_CODEX`
- source_branch: `Ver04-v3` (created from cleanup base `3db0399`)
- target_branch: `Ver04-v3`
- active_spec: `chatgpt/specs/active/20260721_ver04_v3_repo_structure_cleanup_checkpoint.md`
- status: ready for ChatGPT MCP review
- push: none

## Goal

Review the completed MCP repository cleanup checkpoint on `Ver04-v3` through ChatGPT MCP acceptance, without starting Product or M6 work.

## Required result

- actual branch and cleanup commit recorded from local git
- unrelated dirty working tree preserved
- duplicate decision heading corrected to `DEC-20260721-010`
- active removed-path search and canonical path checks pass
- bounded shell and focused unit-test validation recorded
- generated `local/` and `logs/` artifacts remain unstaged
- one local cleanup commit is ready for review
- push remains none

## Scope

Repository structure, documentation, history placement, README accuracy, and cleanup checkpoint only.

Do not change Product logic, trading behavior, gates, scoring, thresholds, classifiers, runtime, launchd, mail, notifications, private endpoints, or M6 authorization.

## Read

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. active spec
4. current git branch, HEAD, status, and cleanup diff

## Completion

The compact report is returned and written exactly once to the required outbox. ChatGPT performs the final MCP acceptance review.

This thread remains dedicated to repository cleanup.
