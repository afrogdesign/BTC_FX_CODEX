# AI_WORKFLOW

This file is the canonical shared process for ChatGPT and Codex. Do not combine it with the legacy prompt documents.

## 1. Roles

### ChatGPT

- inspect repo reality first
- separate report claims from directly verified facts
- make product, trading, safety, scope, validation, and acceptance decisions
- choose the smallest execution route
- identify exact files and the minimum evidence needed
- issue a delta prompt when Codex retains thread context
- review source, tests, CLI, and artifacts through MCP where possible
- authorize heavy acceptance validation only after the implementation is review-ready
- choose acceptance, one minimal FIX, or human judgment

### Codex

- execute only the fixed scope
- choose implementation details inside the accepted contract
- inspect named files, direct callers, nearby helpers, matching tests, and current diff/status
- edit, run lightweight development validation, commit, and report
- autonomously remove duplicate computation and add contract-preserving cache/fixtures
- stop before product/safety/runtime/acceptance judgment or broad exploration

### Human

- approve production policy, gates, thresholds, notification, runtime, and order-adjacent changes
- make the final trading decision

## 2. Core principle

Use this ownership split:

```text
ChatGPT owns what must be true and what evidence is sufficient.
Codex owns how to implement it efficiently inside the allowed scope.
Heavy real-data validation occurs only after ChatGPT review.
```

Do not use Codex as a broad investigator or as an acceptance committee.
Do not micromanage helper structure, caching, fixture shape, or edit order when the contract is already fixed.

## 3. ChatGPT workflow

### Step A: decide whether state inspection is needed

Use the full fresh-state route only when:

- a new thread starts
- the active task or branch may have changed
- the repo premise is unknown
- a Codex report claims a milestone/acceptance boundary
- conflicting state is suspected

In the same thread and same task, inspect only the delta:

- changed source
- matching tests
- actual CLI route when relevant
- fresh generated artifact
- active-spec note

Do not reread stable policy docs after every FIX.

### Step B: classify the work

| Class | Action |
|---|---|
| A | ChatGPT answers or reviews only |
| B | ChatGPT performs deterministic Markdown/spec/state edits through MCP |
| C | Codex executes one coherent, fully decided implementation task |
| D | ChatGPT creates/corrects an active spec before implementation |

Choose class C only when goal, behavior, files, development validation, and safety boundaries are already resolved.

### Step C: freeze the contract, not the implementation mechanics

ChatGPT determines:

- one goal
- exact observable behavior
- files Codex may edit
- narrowly necessary inspection
- acceptance-critical invariants
- development validation budget
- whether a later heavy acceptance run will be needed
- stop conditions
- commit/push behavior

ChatGPT should not prescribe every helper, loop, cache, or internal call sequence unless that detail is itself part of the contract.

Codex may decide:

- helper decomposition
- deterministic fixtures
- cache placement
- duplicate-work elimination
- local edit/test order
- obvious in-scope bug fixes

Codex may not change the product meaning, reduce the evidence set, weaken fail-closed behavior, or substitute an easier acceptance condition.

### Step D: choose direct MCP work versus Codex

Use ChatGPT direct MCP work for:

- short deterministic Markdown creation or correction
- current-state routing cleanup
- active-spec wording that does not require code execution
- source/test/CLI/artifact review
- acceptance/state transitions already supported by direct evidence

Use Codex when local source editing, tests, CLI execution, git commit, or generated artifact creation is needed.

Do not spend a Codex task only to rewrite a small Markdown file or perform a review ChatGPT can complete through MCP.

### Step E: split implementation from acceptance by default

Default sequence:

```text
Implementation pass
→ ChatGPT review gate
→ Heavy acceptance run only if still needed
→ Acceptance transition
```

#### Implementation pass

Codex performs:

- source/test edits
- matching unit tests
- small deterministic fixture E2E when needed
- task-scoped diff check
- local commit

The implementation pass does not run the full local bundle or repeated full replay unless explicitly authorized.

#### ChatGPT review gate

ChatGPT inspects:

- changed source
- matching tests
- actual CLI route
- fixture evidence
- active-spec contract
- safety and scope

If the implementation is not review-ready, issue one minimal FIX before spending credits on a full replay.

#### Acceptance run

Authorize only when source and focused tests are review-ready and real-data execution adds evidence not available through static/fixture review.

A normal acceptance run should contain:

- targeted tests once, only if related code changed since their last accepted pass
- one full bounded command
- output/artifact inspection
- a second full run only when byte determinism is acceptance-critical and no cheaper publication-only check proves it

Do not allow implementation redesign during an acceptance-only run. On failure, report and return to ChatGPT for the next decision.

### Step F: issue a compact prompt

When Codex is in the same thread, omit unchanged repo history, accepted phases, full safety boilerplate, complete CLI argument lists, and repeated report templates.

Minimum delta prompt:

```text
AUTO_SEND

WORK_ID: <id>
MODE: BOUNDED_CODEX

Goal
- <one result>

Edit
- <files>

Autonomy
- contract-preserving helper/cache/fixture choices are Codex-owned
- obvious in-scope bugs may be fixed without another round trip

Do
1. <task-specific change>
2. <task-specific regression>

Validation budget
- <targeted tests / small fixture only>
- no full bundle unless explicitly authorized

Stop
- <task-specific blocker>
- do not touch unrelated files

Commit / Push
- <commit instruction>
- push: none | explicit checkpoint

Report
- compact report
- response.txt exactly one write
```

Add `Known state`, `Allowed read`, detailed CLI/output contracts, or heavy-run authorization only when new, changed, or needed to prevent ambiguity.

### Step G: review Codex output efficiently

Review in this order:

1. **Report triage** — identify claimed files, tests, commit, artifact, blocker, and any heavy run.
2. **Direct repo review** — inspect only the changed implementation, matching tests, CLI route, generated output, and active-spec note that determine acceptance.
3. **Validation sufficiency** — decide whether existing static/fixture evidence is enough or one heavy acceptance run is still necessary.
4. **Boundary review** — confirm no production/runtime/notification/mail/order change and no unrelated tracked data.
5. **Decision** — accept, authorize one acceptance run, issue one minimal FIX, or stop for human judgment.

The report is a locator, not proof of implementation correctness.

Do not:

- repeat broad source review after the same area was already accepted
- request another test solely because the same test passed previously and no related code changed
- retask for minor report formatting or wording differences
- treat unrelated dirty files as blockers
- issue multiple review-only tasks when one bounded implementation task can fix and validate the issue
- authorize full replay while acceptance-critical source defects remain

### Step H: acceptance transition

Only at acceptance or a real posture change:

1. archive the active spec
2. update `CURRENT_STATE.md`
3. replace `NEXT_ACTION.md` with one next item
4. update `CONTROL.md` only if stable rules changed
5. add one major milestone when appropriate
6. create the next active spec only after its scope is decided

During FIX work, keep state docs unchanged and add only a short factual note to the active spec when needed.

## 4. Codex workflow

### Fresh context

Read `AGENTS.md`, `START_HERE.md`, the prompt, and named files. Read additional state docs only if required or inconsistent.

### Retained context

Use the prompt as a delta. Do not reread stable docs or previously inspected files unless they changed or the new task depends on them.

### Implementation execution

1. one initial status for edit/commit tasks
2. bounded inspection
3. edit allowed files only
4. run targeted unit/fixture validation once
5. task-scoped diff check
6. stage only task files
7. local commit when instructed
8. compact report and one outbox write

Codex may autonomously optimize implementation and validation inside the declared budget, but must not escalate to a heavy acceptance run without authorization.

### Heavy-run guard

Treat a command as heavy when it is expected to perform any of these:

- more than 10 replay/evaluation units
- a full bundle across multiple candidates or dates
- a second complete replay for determinism
- a long-running background process

Before an authorized heavy run, report the planned work units in one short line.

Rules:

- no duplicate background run
- no unchanged rerun after failure
- no repeated interrupt/edit/replay loop
- no full-bundle run during implementation unless explicitly authorized
- no second full replay unless explicitly authorized
- prefer fixture, cache, invariant-input reuse, or publication-only checks when equivalent
- on unexpected cost or runtime expansion, stop with a partial report rather than redesigning validation policy

### Dirty tree

- overlapping task changes: inspect and integrate only when safe
- unrelated independent changes: preserve and continue
- unknown potentially conflicting changes: stop
- never reset, restore, checkout, clean, or manipulate stash state to remove existing work

## 5. Modes

Use only these normal modes:

- `BOUNDED_CODEX`: fixed implementation, default
- `REVIEW_ONLY`: narrow fact check, no edit
- `CHECKPOINT_PUSH`: explicit push checkpoint
- `RUNTIME_TASK`: explicitly authorized runtime operation

Do not create separate LIGHT/NORMAL/SYNC/HANDOFF modes. Express scope with files, actions, and validation budget instead.

## 6. Validation defaults

| Change | Development validation | Later acceptance evidence |
|---|---|---|
| docs-only | task-scoped `git diff --check` | normally none |
| Python source/test | matching unittest | full suite only for shared-foundation risk |
| CLI/report | matching CLI test plus small fixture command | one real bounded command when needed |
| deterministic multi-output | fixture determinism where possible | second full run only if critical and authorized |
| checkpoint push | local checkpoint checks | remote HEAD/status checks |

Avoid redundant compile/test combinations, repeated status, unchanged full-suite reruns, and duplicate artifact generation.

## 7. Record discipline

- `CURRENT_STATE.md`: accepted current state and active blocker
- `NEXT_ACTION.md`: exactly one current task
- `CONTROL.md`: stable rules
- active spec: detailed implementation contract and pending FIX notes
- `MILESTONES.md`: accepted major checkpoints
- `TASK_LEDGER.md`: historical lookup only
- git and compact reports: commit/test evidence

Do not copy the same task history into several current files.

## 8. Retask threshold

Retask only for:

- incorrect implementation
- missing acceptance behavior
- insufficient or invalid regression coverage
- failed validation
- unsafe or out-of-scope change
- wrong artifact or source lineage
- missing information needed for the next task

Do not retask for:

- cosmetic report ordering
- equivalent wording
- unrelated dirty files
- no push in a non-push task
- an omitted validation that adds no new evidence

## 9. Safety boundary

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no secrets, private/account/order endpoints
- no unapproved production mutation, runtime restart, launchd, mail, or notification change
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration
- no unsupported gate, scoring, threshold, classifier, or phase promotion
