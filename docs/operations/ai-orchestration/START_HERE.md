# START_HERE

This is the shortest role-aware entrypoint for `btc_monitor` AI work.

The ChatGPT Project initial prompt is maintained in `INITIAL_PROMPT.md`. This file routes repo reads after that prompt is applied.

## Choose the route first

### ChatGPT: fresh thread or changed repo premise

Always read:

1. `AGENTS.md`
2. `START_HERE.md`

Then read only what the request needs:

- current state or next-task decision: `CURRENT_STATE.md` and `NEXT_ACTION.md`
- implementation, FIX, or acceptance: the one active spec under `chatgpt/specs/active/`
- action selection, Codex prompt, or acceptance flow: `AI_WORKFLOW.md`
- stable safety, git, dirty-tree, or validation rules: `CONTROL.md`
- product direction: the relevant product/strategy route

Do not load state, spec, workflow, and product docs for a simple explanation that does not depend on repo state.

### ChatGPT: same thread and same task

Do not reread stable docs. Inspect only the new report, changed source, matching tests, CLI route, fresh artifacts, and the relevant spec note.

### Codex: fresh thread or lost context

Read:

1. `AGENTS.md`
2. `START_HERE.md`
3. the task prompt or rendered task-manifest launcher
4. files explicitly named by the task

Read state docs and active spec only when named, required, or inconsistent with the task.

### Codex: retained context

Treat the new prompt as a delta. Do not reopen stable orchestration or product docs unless required by a changed contract or contradiction.

## Repo boundary

| Purpose | Path | Rule |
|---|---|---|
| primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | normal read/edit/test/git |
| frozen old runtime repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | explicit `RUNTIME_TASK` only |

ChatGPT uses `AFROG_Business_MCP` as the primary repo inspection path. Branch is confirmed from repo state, not chat history.

## Task routing

| Route | Use |
|---|---|
| ChatGPT answer/review | explanation, diagnosis, comparison, source/test/artifact review |
| ChatGPT direct MCP work | deterministic Markdown/spec/state edits requiring no local test or git operation |
| `BOUNDED_CODEX` | fixed implementation with known files, behavior, and validation |
| spec-first | unresolved trading logic, gates, thresholds, schemas, multi-module design, safety, runtime, or competing choices |

Do not send Codex work while material product or safety judgment remains unresolved.

The canonical route for new `BOUNDED_CODEX`, `REVIEW_ONLY`, `CHECKPOINT_PUSH`, and `RUNTIME_TASK` work is:

```text
active manifest → validate-task → render-prompt → bounded task → json_v1 report → validate-report → ChatGPT review
```

The manifest becomes immutable once execution starts. A manual hand-written prompt is an explicit, reason-recorded fallback only when the contract tool or manifest cannot be used, or when a bounded legacy task is already in flight and conversion would add risk. It is not the default route.

## Source-of-truth order

```text
repo files and generated artifacts
→ active spec
→ task manifest when activated for that task
→ CURRENT_STATE.md and NEXT_ACTION.md
→ CONTROL.md and product route
→ accepted milestones and git history
→ TASK_LEDGER / handoff / historical docs
→ chat history
```

## Record roles

| File | Responsibility |
|---|---|
| `INITIAL_PROMPT.md` | ChatGPT Project initial prompt source |
| `CURRENT_STATE.md` | accepted state and current blocker |
| `NEXT_ACTION.md` | exactly one current work item |
| `CONTROL.md` | stable safety, git, runtime, and validation rules |
| `AI_WORKFLOW.md` | shared ChatGPT/Codex process |
| `MILESTONES.md` | accepted major checkpoints |
| `DECISIONS.md` | durable product/design decisions |
| active spec | current detailed implementation contract |
| `TASK_LEDGER.md` | historical lookup only |

## Task-specific reads

Read only when relevant:

- product direction: `PRODUCT_IMPLEMENTATION_ROUTE.md`
- macro route: `docs/operations/strategy/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md`
- checkpoint push: `CHECKPOINT_RUNBOOK.md`
- runtime handoff: `RUNTIME_PULL_HANDOFF.md`
- accepted history: `MILESTONES.md`
- old Work ID: search `TASK_LEDGER.md`; do not read it in full

Do not scan the orchestration directory wholesale to discover context.

## Validation routing

### Implementation

Codex receives implementation freedom inside allowed files and runs only:

- matching unit tests
- a small deterministic fixture/smoke when needed
- task-scoped diff check

Do not authorize a full local bundle or repeated replay during implementation.

### Review

ChatGPT reviews changed source, matching tests, CLI routing, fixture evidence, artifacts, and the active spec through MCP.

### Acceptance

Only after ChatGPT determines the implementation is review-ready may Codex receive an explicit heavy acceptance task. One full bounded run is the default maximum. A second full run requires an acceptance-critical determinism reason and explicit authorization.

Canonical details: `AI_WORKFLOW.md` and `CONTROL.md`.

## Current post-M5 improvement route

M5 is accepted and its spec is archived. M6 is not active.

The current route is:

```text
AI orchestration docs checkpoint
→ A1 task-manifest contract foundation
→ A2 low-risk pilot
→ A3 canonical manifest routing (active)
→ optional A4 CWT integration
```

For A1 planning and implementation, read:

```text
AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md
```

For later replay-pipeline, cache, or publication-determinism work, read:

```text
MACRO_REPLAY_AND_AI_ACCEPTANCE_SIMPLIFICATION_PLAN_20260721.md
```

Do not combine A1 with replay-stage/cache work, M6, runtime, or production changes.

## Safety baseline

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no secrets or private/account/order endpoints
- no unapproved runtime, launchd, mail, or notification change
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration
- no unsupported gate, scoring, threshold, or classifier relaxation

## MCP request privacy

Do not place address-formatted contacts or sensitive identifiers in MCP request bodies. Use redacted placeholders and inspect by safe filename, symbol, section, or abstract summary.

## Compatibility files

`PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHATGPT_COMMANDER_PROMPT.md`, and `RESUME.md` are compatibility pointers only. Do not read them together.

Canonical route:

```text
INITIAL_PROMPT.md
→ START_HERE.md
→ AI_WORKFLOW.md
```
