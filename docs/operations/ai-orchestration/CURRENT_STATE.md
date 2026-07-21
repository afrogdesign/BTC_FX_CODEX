# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- recorded branch: `Ver04-v2`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- accepted macro phase: M5 bounded offline champion/challenger proposal engine
- accepted macro checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- M5 result: winner `none`; recommendation `continue_shadow_collection`
- A1 task-manifest foundation: accepted
- A2 low-risk manifest pilot: accepted
- A2 checkpoint: `95840ef4de0aa7d88972f35df37b7dac9f078f65`
- active spec: `chatgpt/specs/active/20260721_ai_task_manifest_a3_canonical_routing.md`
- active manifest: `chatgpt/tasks/active/20260721_a3_canonical_routing.implementation.json`
- current route: A3 canonical task-manifest routing activation
- M6: not started and not authorized

Git objects are confirmed by local git at task start. MCP verifies file content but does not expose `.git`; reported hashes remain locators until local verification.

## Product posture

The objective remains manual 15-minute-chart trading support after notification triage.

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- existing production, runtime, notification, data-privacy, and gate controls remain unchanged

## A1 acceptance

A1 provides strict task/report JSON validation, canonical SHA-256, compact prompt rendering, stage separation, fail-closed report alignment, reviewed-commit binding for acceptance, and the write-once outbox contract.

Accepted spec:

`chatgpt/specs/archive/20260721_ai_task_manifest_acceptance_gate_a1.md`

## A2 acceptance

A2 exercised the A1 flow on one docs-only correction.

- implementation manifest SHA: `250a51807a470a17619d6ee85f3019af782577a41c40a436f5e14e3ef7022660`
- implementation checkpoint: `95840ef4de0aa7d88972f35df37b7dac9f078f65`
- exact three-file implementation scope
- no heavy validation
- revision-3 read-only report validated successfully
- no product or runtime posture change

Archived contracts:

- `chatgpt/specs/archive/20260721_ai_task_manifest_a2_milestones_alignment.md`
- `chatgpt/tasks/archive/20260721_a2_milestones_alignment.implementation.json`
- `chatgpt/tasks/archive/20260721_a2_milestones_alignment.review.json`

A2 proves the bounded manifest/report flow but does not itself activate the default route.

## Current A3 route

A3 updates exactly:

- `AGENTS.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/AI_WORKFLOW.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/INITIAL_PROMPT.md`

The validated manifest and rendered launcher become the default Codex route. Hand-written prompts remain an explicit fallback. A3 does not automate execution, acceptance, next-task selection, optional transport integration, replay redesign, M6, or production behavior.

## Navigation

- exact task: `NEXT_ACTION.md`
- active A3 spec: `chatgpt/specs/active/20260721_ai_task_manifest_a3_canonical_routing.md`
- active A3 manifest: `chatgpt/tasks/active/20260721_a3_canonical_routing.implementation.json`
- stable rules: `CONTROL.md`
- parent design: `AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md`
- accepted checkpoints: `MILESTONES.md`
