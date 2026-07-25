# <Specification Title>

- created_at: YYYY-MM-DD
- work_id: `<WORK_ID>`
- status: active implementation contract
- mode: `BOUNDED_CODEX | REVIEW_ONLY | CHECKPOINT_PUSH | RUNTIME_TASK`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- expected branch: `<verify from local git>`
- push: `none` unless explicitly approved

## Goal

Describe one observable result.

## Known state

List only facts that are current and material to this task. Do not repeat stable repo rules already covered by `AGENTS.md`, `START_HERE.md`, or `CONTROL.md`.

## Observable contract

State what must be true after implementation from the user, CLI, file, or report perspective.

## Allowed scope

### Read

- `<path>`

### Edit

- `<path>`

### Inspect only

- `<path>`

## Required work

1. `<bounded change>`
2. `<matching regression coverage>`
3. `<small deterministic smoke when needed>`

## Autonomy

Codex may choose small helpers, fixtures, and internal structure inside the accepted contract. Product, trading, safety, acceptance, and phase decisions remain with ChatGPT and the human operator.

## Validation budget

- matching tests
- one small deterministic fixture or smoke when needed
- task-scoped `git diff --check`
- no heavy replay or repeated full run unless explicitly authorized

## Stop conditions

- material ambiguity outside the contract
- installed runtime, launchd, schedule, mail, or delivery operation required but not explicitly authorized
- safety boundary would change
- unrelated dirty changes overlap the task files

## Safety

- no automatic order
- no secrets or private/account/order endpoints
- no unapproved runtime, launchd, mail, or notification change
- no unapproved gate, threshold, scoring, or classifier change
- preserve unrelated changes
- no reset, restore, checkout, clean, or stash manipulation

## Commit and report

- stage only task files
- create one local commit when requested
- push: none unless explicitly approved
- return the compact report defined by `AI_WORKFLOW.md`
- write the same report exactly once to the required outbox when local filesystem access is available
