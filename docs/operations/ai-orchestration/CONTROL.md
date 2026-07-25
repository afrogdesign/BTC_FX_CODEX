# AI Orchestration Control

last_updated: 2026-07-21

This file contains stable controls only. Current phase and Work ID belong in `CURRENT_STATE.md` and `NEXT_ACTION.md`.

## Repo control

| Label | Path | Rule |
|---|---|---|
| canonical repository | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | only development/source/runtime-source repo; normal read/edit/test/git |
| installed runtime/delivery target | operational target | explicit named `RUNTIME_TASK` only; never a second repository |

- branch is confirmed with `git status --short --branch`
- push requires explicit `CHECKPOINT_PUSH`
- normal work uses local validation and local commit
- ChatGPT uses `AFROG_MCP` for primary inspection
- history/archive is historical and non-binding, and is excluded from normal current-state search unless historical research is explicit
- old repositories are not searched, compared, synchronized, or used as fallback

## Responsibility control

ChatGPT owns:

- repo diagnosis
- product/trading/safety judgment
- active-spec design
- scope and acceptance criteria
- validation design and heavy-run authorization
- Codex prompt
- direct source/test/CLI/artifact review
- acceptance and next-task selection

Codex owns:

- fixed-scope implementation
- contract-preserving helper/cache/fixture design
- matching tests and lightweight bounded commands
- obvious in-scope bug fixes
- local commit
- compact report

Human approval is required for production policy, gates, thresholds, notifications, runtime, and order-adjacent changes.

## Context control

- fresh context uses `AGENTS.md` and `START_HERE.md`
- same-thread work uses delta prompts and delta inspection
- stable docs are not reread after every FIX
- contradictory Work ID, active spec, branch, or scope must be resolved before implementation
- `TASK_LEDGER.md`, handoffs, history, logs, and generated outputs are not default reads

Detailed process: `AI_WORKFLOW.md`.

## Normal compact-report route

New `BOUNDED_CODEX`, `REVIEW_ONLY`, `CHECKPOINT_PUSH`, and `RUNTIME_TASK` work normally follows `ChatGPT compact prompt → bounded Codex execution → compact text report → ChatGPT MCP review`.

Task manifests, `validate-task`, `render-prompt`, `json_v1`, and `validate-report` are optional strict tooling used only when ChatGPT explicitly determines that machine alignment adds material evidence. Normal tasks do not create or self-validate JSON reports; user-visible reports and `response.txt` use the existing compact report format. Optional strict tooling preserves all scope, safety, validation, approval, reporting, and outbox controls.

For committed-task review, default to one `get_workspace_repo_status` call followed
by one commit-scoped `get_workspace_repo_diff` call. Ignore unrelated dirty and
untracked entries; do not enumerate or investigate them. Optional log, file-range,
or other MCP calls require one explicit unresolved acceptance question. Duplicate
evidence gathering is prohibited, and review must stop once the acceptance facts
are sufficient. Detailed mechanics remain canonical in `AI_WORKFLOW.md` Step G.

## Git and dirty tree

- one initial status for edit/commit tasks
- preserve unrelated changes
- stage only task files
- use task-scoped diff checks
- never reset, restore, checkout, clean, or apply/pop/drop stash to remove existing work
- file count alone is not a blocker when the allowed files form one coherent task

## Validation ownership

Validation is split into two stages.

### Development validation

Codex runs only the smallest evidence needed to support implementation:

- matching unittest
- small deterministic fixture/smoke when needed
- task-scoped `git diff --check`

### Acceptance validation

ChatGPT first reviews source, tests, CLI, and artifacts through MCP.
Only after the implementation is review-ready may ChatGPT authorize:

- a full local bundle
- multi-candidate or multi-date replay
- a long-running background command
- a second complete run for determinism

Do not combine implementation debugging and heavy acceptance replay in the same loop.

## Heavy-run control

A command is heavy when it is expected to perform any of these:

- more than 10 replay/evaluation units
- a full bundle across multiple candidates or dates
- a second full replay solely for determinism
- a long-running background process

Stable rules:

- heavy runs require explicit prompt authorization
- state expected work units before starting
- do not launch duplicate background runs
- do not rerun an unchanged failed heavy command
- one full acceptance run is the default maximum
- a second full run requires an acceptance-critical determinism contract and explicit authorization
- prefer fixture tests, caching, invariant-input reuse, or publication-only checks when equivalent
- unexpected cost expansion produces a partial/blocked report, not an autonomous validation redesign

## Validation defaults

- docs-only: task-scoped `git diff --check`
- Python: matching unittest
- CLI/report development: matching CLI test plus small fixture command
- real bounded CLI: acceptance stage only unless explicitly included in implementation scope
- repeat execution: only when determinism is acceptance-critical and authorized
- full suite: only for shared-foundation risk or explicit instruction
- do not run redundant checks that prove the same fact

## Record control

- `CURRENT_STATE.md`: accepted state and blocker
- `NEXT_ACTION.md`: one current task
- `CONTROL.md`: stable rules
- active spec: current detailed contract and pending FIX notes
- `MILESTONES.md`: accepted major checkpoints
- `DECISIONS.md`: durable decisions
- `TASK_LEDGER.md`: historical lookup only
- git and compact reports: implementation/test evidence

Do not duplicate one task history across several current files.

## Safety control

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no API keys, secrets, private/account/order endpoints
- no unapproved runtime restart, launchd, mail, notification, production mutation, or order operation
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration

Explicit approval is required before changing:

- `trade_execution_gate`
- `phase1b_lite_gate`
- `opportunity_gate`
- scoring, thresholds, or classifiers
- notification trigger or real mail sending
- runtime schedule
- production API/account/order behavior

## Reporting control

Codex compact reports must include Work ID, status, branch, changed files, validation, commit, and push state.

When local filesystem access exists, write the same report exactly once to:

`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`

Do not read, verify, retry, recreate, monitor, or watch after writing.


## Development completion and cost guardrail

This section supersedes `Canonical task route` where they conflict.

Priority order:

1. complete the product system and increase observable user value
2. preserve safety, scope, and acceptance integrity
3. minimize Codex credits, elapsed time, and repeated validation
4. improve orchestration neatness or machine-readable formatting

Stable rules:

- the normal route is a compact prompt, one bounded Codex implementation pass, a compact text report, and direct ChatGPT MCP review
- task manifests and JSON reports are optional strict tools, not the default
- strict tooling requires a stated material reason such as heavy acceptance, reviewed-commit binding, checkpoint push, runtime work, or a genuinely multi-stage contract
- deterministic Markdown, spec, state, and review work is performed directly by ChatGPT through MCP when local execution is unnecessary
- one coherent implementation, its matching tests, required fixture, short docs, validation, and commit are bundled into one Codex task
- do not create a Codex review task when ChatGPT can inspect the same evidence through MCP
- do not create or self-validate a report only to satisfy an optional report schema
- report formatting, field order, equivalent wording, or other non-material report differences cause zero retasks
- one minimal FIX is allowed only for broken implementation, failed relevant validation, unsafe or out-of-scope changes, or missing acceptance-critical behavior
- if a second orchestration-only correction would be needed, stop that route and simplify the process before spending more credits
- if orchestration work is expected to equal or exceed the underlying product change, use the simpler route
- a pilot that increases operational cost does not justify promoting that mechanism to the default route

Acceptance decisions prioritize direct source, test, CLI, artifact, and safety evidence. Reports remain locators rather than proof.
