# A3 Canonical Task-Manifest Routing Activation

last_updated: 2026-07-21
status: active implementation contract
spec_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A3-ROUTING-SPEC-01`
implementation_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A3-ROUTING-IMPL-01`
parent_contract: `docs/operations/ai-orchestration/AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md`
accepted_A1: `chatgpt/specs/archive/20260721_ai_task_manifest_acceptance_gate_a1.md`
accepted_A2: `chatgpt/specs/archive/20260721_ai_task_manifest_a2_milestones_alignment.md`
manifest: `chatgpt/tasks/active/20260721_a3_canonical_routing.implementation.json`

## 1. Objective

Make the accepted A1 task-manifest flow the default ChatGPT-to-Codex execution route after the successful A2 pilot.

The default flow becomes:

```text
ChatGPT fixes scope and evidence
→ create or revise an A1-valid task manifest
→ validate-task
→ render-prompt
→ Codex executes the bounded contract
→ Codex produces json_v1 report
→ validate-report
→ ChatGPT MCP review and acceptance decision
```

This is routing activation only. It does not automate Codex execution, acceptance, next-task selection, heavy-run authorization, runtime, notification, mail, trading, or production behavior.

## 2. Exact ownership and commit scope

### Codex content-edit ownership

Codex may edit content only in:

- `AGENTS.md`
- `docs/operations/ai-orchestration/START_HERE.md`
- `docs/operations/ai-orchestration/AI_WORKFLOW.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/INITIAL_PROMPT.md`

### ChatGPT supplied transition files

The following files were prepared by ChatGPT and must be preserved byte-for-byte while being staged in the same task commit:

- `chatgpt/specs/active/20260721_ai_task_manifest_a3_canonical_routing.md`
- `chatgpt/tasks/active/20260721_a3_canonical_routing.implementation.json`
- `chatgpt/specs/archive/20260721_ai_task_manifest_a2_milestones_alignment.md`
- `chatgpt/tasks/archive/20260721_a2_milestones_alignment.implementation.json`
- `chatgpt/tasks/archive/20260721_a2_milestones_alignment.review.json`
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/MILESTONES.md`

The removed pre-archive A2 paths are part of the same move and must be staged as deletions:

- `chatgpt/specs/active/20260721_ai_task_manifest_a2_milestones_alignment.md`
- `chatgpt/tasks/active/20260721_a2_milestones_alignment.implementation.json`
- `chatgpt/tasks/active/20260721_a2_milestones_alignment.review.json`

No other tracked file may be edited, staged, or committed.

## 3. Observable contract

### IO-01 — Canonical manifest route

All five routing documents must agree that normal Codex work starts from an A1-valid manifest under `chatgpt/tasks/active/`.

Before execution:

1. ChatGPT creates or revises the manifest.
2. A pre-execution correction increments `revision`; a material scope change uses a new Work ID.
3. `tools/ai_task_contract.py validate-task` must pass.
4. `render-prompt` produces the compact launcher.
5. The manifest becomes immutable once execution starts.

The rendered launcher references the manifest and does not repeat active-spec prose, stable safety boilerplate, accepted history, full report templates, or unchanged CLI documentation.

### IO-02 — Machine report route

Manifest-driven tasks use `json_v1` reports.

The report must:

- match Work ID, revision, canonical task SHA, branch, and expected base commit
- remain inside `allowed.edit`
- report only listed validation commands
- match heavy, commit, and push authorization
- validate with `validate-report` before ChatGPT acceptance review
- be written exactly once to the canonical outbox without read-back, retry, recreation, polling, loop, or watcher

ChatGPT continues to treat the report as a locator and directly reviews acceptance-critical files and evidence through MCP.

### AC-01 — Default versus fallback

The manifest route is the default for new `BOUNDED_CODEX`, `REVIEW_ONLY`, `CHECKPOINT_PUSH`, and `RUNTIME_TASK` work.

A manual hand-written prompt remains an explicit fallback only when:

- the task-contract tool or manifest file cannot be used, or
- a bounded legacy task is already in flight and conversion would add risk without adding evidence.

Fallback does not weaken scope, safety, validation, dirty-tree, reporting, approval, or outbox rules. The reason for fallback must be stated in the prompt or task record.

### AC-02 — Role and read discipline

The five documents must preserve:

- ChatGPT ownership of scope, product/trading/safety judgment, validation sufficiency, heavy authorization, acceptance, and next-task selection
- Codex ownership of bounded implementation mechanics inside allowed files
- fresh-context reads limited to `AGENTS.md`, `START_HERE.md`, the rendered launcher, the manifest, and named files
- delta-context reads limited to changed manifest/named files and necessary direct code/tests
- no broad repo exploration or automatic phase selection

### AC-03 — Stage and validation separation

The routing documents must preserve:

- implementation manifest: lightweight development validation and no unauthorized heavy run
- ChatGPT MCP review gate after implementation
- separate acceptance manifest only when heavy evidence remains necessary
- acceptance manifest bound to the exact reviewed implementation commit
- one full bounded acceptance run by default
- no unchanged heavy rerun after failure
- no implementation repair during acceptance-only work

### AC-04 — Manual route compatibility

Existing manual prompt instructions remain available as fallback guidance. They must no longer be described as the normal/default route after A3.

Compatibility pointer documents are not edited in A3.

### SC-01 — Safety and non-goals

A3 must not:

- automatically execute Codex
- automatically validate acceptance or select the next task
- activate CWT/worktree integration
- start replay/cache redesign
- start M6
- change product/trading logic, scoring, threshold, gate, classifier, runtime, launchd, notification, mail, API, account, position, or order behavior
- weaken report-only, not `FORMAL_GO`, human-decided, or no-automatic-order posture

Preserve unrelated dirty files. Never reset, restore, checkout, clean, or manipulate stash state.

## 4. Validation

### VAL-01 — Exact bounded validation

Run only the commands listed by the implementation manifest:

- validate the A3 implementation manifest
- create the final json_v1 report after the task commit
- self-validate that report exactly once
- run one task-scoped `git diff --check` across the exact commit scope

No unit suite, full suite, heavy run, replay, network, background process, runtime action, notification action, or mail action is authorized.

### VAL-02 — Direct review evidence

ChatGPT acceptance review will verify:

- all five documents designate the manifest route as default
- `validate-task`, `render-prompt`, and `validate-report` responsibilities are consistent
- revision, immutability, stage separation, and reviewed-commit binding remain fail-closed
- manual fallback remains available and explicitly exceptional
- no automatic execution/acceptance/next-task behavior is introduced
- all ChatGPT supplied transition files remained unchanged

## 5. Stop conditions

Stop without editing when:

- actual branch is not `Ver04-v2`
- actual HEAD differs from the manifest expected base commit
- manifest validation or canonical SHA fails
- a ChatGPT supplied transition file differs from its supplied state
- an overlapping change in one of the five content-edit files cannot be safely preserved
- another tracked file is required
- implementation would require CWT, replay, M6, runtime, notification, mail, API, account, position, order, or production action

## 6. Acceptance and next route

A3 is review-ready when:

- the five documents satisfy IO-01 through AC-04
- all changes remain inside the exact commit scope
- the manifest and supplied transition files are unchanged
- the final machine report validates against the manifest
- one local task-only commit exists
- push is none

After ChatGPT accepts A3:

1. archive this spec and implementation manifest
2. update `CURRENT_STATE.md`, `NEXT_ACTION.md`, and `MILESTONES.md`
3. keep the manual prompt route as fallback
4. select optional A4 CWT integration or the separate replay-simplification route only through a new active spec

A3 acceptance does not by itself authorize A4, replay/cache work, M6, or production changes.
