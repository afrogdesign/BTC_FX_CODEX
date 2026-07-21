# A2 Low-Risk Manifest Pilot — Milestones Alignment

last_updated: 2026-07-21
status: active implementation contract
spec_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A2-PILOT-SPEC-01`
implementation_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A2-MILESTONES-PILOT-IMPL-01`
parent_contract: `docs/operations/ai-orchestration/AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md`
manifest: `chatgpt/tasks/active/20260721_a2_milestones_alignment.implementation.json`

## 1. Objective

Exercise the accepted A1 task-manifest, compact-prompt, machine-report, and review flow with one deterministic docs-only correction.

The current `MILESTONES.md` still says the next checkpoint is the A1 foundation even though A1 is accepted and the canonical current route is A2. Align that file without changing product posture or starting M6.

## 2. Ownership and exact files

ChatGPT owns and has supplied:

- `chatgpt/specs/active/20260721_ai_task_manifest_a2_milestones_alignment.md`
- `chatgpt/tasks/active/20260721_a2_milestones_alignment.implementation.json`

Codex must preserve both supplied files byte-for-byte. They may be staged and committed as new task-owned files but their content must not be edited after execution starts.

Codex may change content only in:

- `docs/operations/ai-orchestration/MILESTONES.md`

The exact commit scope is the three paths above. No other tracked file may be edited, staged, or committed.

## 3. Observable contract

### IO-01 — Immutable supplied contract files

Before editing, validate the implementation manifest with `tools/ai_task_contract.py`. The active spec and manifest must remain byte-identical to their supplied state throughout execution.

The manifest canonical SHA-256 is:

`250a51807a470a17619d6ee85f3019af782577a41c40a436f5e14e3ef7022660`

### AC-01 — Record A1 as one accepted milestone

Add one concise major milestone entry to `MILESTONES.md` for the accepted A1 task-manifest contract foundation.

The entry must:

- record final accepted commit locator `13527dc69bfc3b2b17fc96ab2ab6f5a8d8ef495f`
- summarize strict task/report validation, canonical SHA, compact rendering, fail-closed report alignment, reviewed-commit binding, and write-once outbox
- state that focused static evidence was sufficient and no heavy run was required
- state that A1 does not activate A3, CWT, automatic execution/acceptance, M6, runtime, notification, mail, or production behavior
- avoid FIX-by-FIX history, matching the milestone-file doctrine

### AC-02 — Replace the stale transition

Replace the stale `Current transition` text so it states:

- M5 remains accepted with recommendation `continue_shadow_collection`
- A1 is accepted and archived
- the current immediate route is one bounded A2 low-risk manifest pilot
- M6 remains not started and not authorized

Do not rewrite accepted M1–M5 evidence.

### SC-01 — Safety and scope

This task is documentation-only.

Do not change:

- product or trading logic
- scoring, thresholds, gates, or classifiers
- runtime, notification, mail, API, account, position, or order behavior
- accepted M5 evidence or recommendation
- canonical routing activation
- CWT or worktree integration
- M6 authorization

Preserve unrelated dirty files. Do not reset, restore, checkout, clean, or apply/pop/drop stash state.

## 4. Validation

### VAL-01 — Exact bounded validation

Run only the manifest validation and the canonical diff check:

```text
./.venv312/bin/python tools/ai_task_contract.py validate-task --task chatgpt/tasks/active/20260721_a2_milestones_alignment.implementation.json
git diff --check -- chatgpt/specs/active/20260721_ai_task_manifest_a2_milestones_alignment.md chatgpt/tasks/active/20260721_a2_milestones_alignment.implementation.json docs/operations/ai-orchestration/MILESTONES.md
```

No unit suite, heavy run, replay, network, background process, runtime action, notification action, or mail action is authorized.

The machine-readable report must validate against the manifest before ChatGPT review. The report must use the canonical write-once outbox contract.

## 5. Stop conditions

Stop without editing when:

- actual branch is not `Ver04-v2`
- manifest validation fails or its SHA differs from IO-01
- either supplied contract file was already modified
- an overlapping change exists in `MILESTONES.md` and safe preservation is unclear
- completing the task requires another tracked file
- any product, runtime, notification, mail, API, account, position, order, replay, CWT, A3, or M6 action would be required

## 6. Acceptance and archive

A2 is review-ready when:

- the validated report is returned
- the three-file scope is respected
- `MILESTONES.md` satisfies AC-01 and AC-02
- the active spec and manifest are unchanged
- the exact diff check passes
- one local task-only commit exists
- push is none

After ChatGPT accepts the pilot, move this spec and its manifest to corresponding archive locations and select A3 separately. A2 acceptance does not automatically activate A3.
