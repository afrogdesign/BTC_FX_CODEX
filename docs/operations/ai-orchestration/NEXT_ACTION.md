# NEXT_ACTION

- current_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A1-SPEC-01`
- mode: `SPEC_FIRST`
- branch: confirm from repo state
- status: ready for new ChatGPT thread
- active_spec: none; create one bounded A1 spec
- acceptance: not applicable
- push: none

## Goal

Create one bounded active specification for Phase A1 of the AI task-manifest and acceptance-gate foundation.

Parent contract:

```text
docs/operations/ai-orchestration/AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md
```

## A1 scope

The active spec may authorize only:

- `chatgpt/tasks/README.md`
- `chatgpt/tasks/schemas/task_manifest.schema.json`
- `chatgpt/tasks/schemas/task_report.schema.json`
- `chatgpt/tasks/examples/implementation_task.example.json`
- `chatgpt/tasks/examples/acceptance_task.example.json`
- `chatgpt/tasks/examples/task_report.example.json`
- `tools/ai_task_contract.py`
- `tests/test_ai_task_contract.py`
- the A1 active spec itself

## Required A1 behavior

- validate task and report JSON contracts fail-closed
- compute deterministic canonical JSON SHA-256
- render compact fresh and delta Codex prompts
- prohibit heavy validation in implementation manifests
- prohibit source edits in acceptance manifests
- validate changed-file, test-command, heavy-run, commit, push, Work ID, revision, and SHA alignment in reports
- use the canonical response outbox contract
- require no new external dependency by default
- provide focused unit tests and valid/invalid examples

## A1 non-goals

- no CWT integration
- no worktree automation
- no replay-stage or persistent-cache redesign
- no conversion of all historical tasks
- no automatic Codex execution
- no automatic acceptance or next-task selection
- no product, trading, scoring, threshold, gate, classifier, runtime, notification, mail, API, account, position, or order change
- no M6 work

## ChatGPT work in the new thread

1. read the canonical startup docs and this current action
2. inspect the parent contract only as needed
3. create a concise A1 active spec with stable clause IDs
4. define exact allowed files and focused validation
5. directly review the spec for scope and safety
6. produce one short bounded Codex implementation prompt

Do not start Codex implementation before the A1 active spec exists and is internally consistent.

## Boundaries

- preserve unrelated dirty files
- do not alter accepted M5 records
- do not edit source outside the A1 tool/test scope
- do not reset, restore, checkout, clean, or manipulate stash state
- push remains unauthorized

This file contains one current task only. Replace it after the A1 spec is created and the implementation task is fixed.
