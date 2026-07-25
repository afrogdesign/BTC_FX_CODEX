# AGENTS.md

## Role

Codex is the fixed-scope implementation worker for this repository.
ChatGPT performs repo review, product/trading/safety judgment, scope selection, validation design, acceptance, and next-task selection.

## Canonical task route

For new `BOUNDED_CODEX`, `REVIEW_ONLY`, `CHECKPOINT_PUSH`, and `RUNTIME_TASK` work, the default route is a compact ChatGPT prompt:

```text
ChatGPT compact prompt → bounded Codex execution → compact text report → ChatGPT MCP review
```

Task manifests, `validate-task`, `render-prompt`, `json_v1`, and `validate-report` are optional strict tooling used only when ChatGPT explicitly determines that machine alignment adds material evidence. Normal tasks do not create or self-validate JSON reports. The user-visible report and `response.txt` use the existing compact report format. When strict tooling is selected, its immutability and validation rules apply.

## Context rule

### Fresh thread or lost context

Read only:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. the task prompt
4. files explicitly named by the task

Read `CURRENT_STATE.md`, `NEXT_ACTION.md`, `CONTROL.md`, or the active spec only when the task requires them or the prompt is inconsistent with repo state.

### Same Codex thread with retained context

Do not reread stable orchestration docs.
Use the new prompt as a delta and read only newly named files, changed files, nearby helpers, and matching tests.

If work IDs, active spec, branch, or scope conflict, stop rather than guessing.

## Repo boundary

- canonical repository: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- this is the only development, source, and runtime-source repository
- installed runtime, launchd, schedule, mail, and public delivery targets are operational targets, not repositories
- `RUNTIME_TASK` authorizes only the explicitly named installed operation and never authorizes a second repository
- history/archive material is historical and non-binding; exclude it from normal current-state search unless historical research is explicit
- do not search, compare, synchronize, or use old repositories as fallback
- branch is read from `git status --short --branch`; do not infer it from chat or old docs
- push only for an explicit `CHECKPOINT_PUSH`

## Implementation autonomy

Within the allowed files and accepted contract, Codex may autonomously:

- add or reorganize nearby helpers
- add deterministic fixtures and focused regressions
- remove duplicate calculations
- add caching that preserves semantics
- choose the order of bounded edits and tests
- fix obvious in-scope bugs found during implementation
- skip redundant checks that add no new evidence

Codex must not autonomously:

- shrink or reinterpret the product contract
- reduce candidate counts, date ranges, thresholds, gates, or fail-closed rules
- replace an acceptance requirement with an easier proxy
- choose whether production/runtime/mail/order behavior should change
- broaden the task into unrelated cleanup or redesign

Implementation method is Codex-owned. Product meaning and acceptance evidence are ChatGPT-owned.

## Standard execution

For an edit/commit task:

1. Run `git status --short --branch` once.
2. Read only task-named files and necessary nearby code/tests.
3. Modify only allowed files.
4. Run the smallest task-specific development validation.
5. Run task-scoped `git diff --check -- <task files>`.
6. Stage only task files and commit when the task requests or the change is a meaningful checkpoint.
7. Return one compact report.

Do not add repeated status, compile, test, or diff commands that prove the same fact.
Do not full-scan the repo, `TASK_LEDGER.md`, logs, generated outputs, or historical notes.

## Validation budget

The default Codex task is an implementation pass, not a full acceptance campaign.

During implementation, use:

- matching unit tests
- a small deterministic fixture or smoke path
- one task-scoped diff check

Do not run the full local data bundle, all candidates, all dates, repeated full replay, or other heavy acceptance validation unless the prompt explicitly authorizes an acceptance run.

Treat a command as heavy when it is expected to perform any of the following:

- more than 10 replay/evaluation units
- a full production-like local bundle across multiple candidates or dates
- a second complete replay solely for determinism
- a long-running background process

Before an explicitly authorized heavy run, state the expected work units in one short line.

Heavy-run rules:

- do not launch duplicate background runs
- do not rerun the same heavy command after failure without a relevant code/input change
- do not combine implementation debugging and acceptance replay in one loop
- if a heavy run fails, report the failure and stop unless the prompt explicitly allows an obvious local fix
- a second full run requires an acceptance-critical determinism contract and explicit authorization
- prefer fixture tests, cached invariant inputs, or publication-only checks when they prove the same fact

## Allowed inspection

Unless the prompt narrows it further, bounded inspection may include:

- current status/diff
- task-named files
- the target symbol and its direct callers
- nearby helpers in the same module
- matching tests by class, function, CLI, or module name

Broad exploration, product redesign, acceptance design, and next-phase selection remain ChatGPT work.

## Stop conditions

Stop with a compact `blocked` or `partial` report when:

- required files are missing
- the prompt conflicts with the active spec or repo state
- allowed files are insufficient
- product, trading, safety, runtime, or acceptance judgment is still required
- unrelated changes overlap the task and cannot be safely separated
- validation fails outside an obvious in-scope fix
- an unapproved heavy acceptance run would be required
- secret/private/raw data would enter the diff
- runtime, notification, mail, API, account, position, or order operations are required but not explicitly authorized

Do not stop only because the task touches many files when those files are explicitly allowed and form one coherent change.

Never use reset, restore, checkout, clean, or stash apply/pop/drop to remove existing work.

## Safety

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no API keys, secrets, private/account/order endpoints
- no unapproved runtime restart, launchd, mail, or notification behavior change
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration
- do not relax `trade_execution_gate`, `phase1b_lite_gate`, or `opportunity_gate` without explicit approval

## ChatGPT MCP review

For a routine committed-task review, start with `AFROG_MCP`'s
`get_workspace_repo_status`, then the commit-scoped
`get_workspace_repo_diff(scope="commit", commit="<reported commit>")`.
Ignore unrelated dirty/untracked entries; use log or targeted file reads only for
one unresolved acceptance question, and stop when the acceptance facts are sufficient.
See `docs/operations/ai-orchestration/AI_WORKFLOW.md` Step G for the detailed contract.

## Reporting

```text
WORK_ID: <id>
STATUS: done | partial | blocked | failed
BRANCH: <branch>
CHANGED:
- <file or none>
TESTS:
- <command> => pass | fail | not run
COMMIT: <hash or none>
PUSH: origin/<branch> | none
NOTES: <one line only when needed>
```

When local filesystem access exists, write the same final compact report exactly once to:

`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`

Do not read, check, retry, recreate, monitor, or watch that file after writing.

## Canonical references

- role-aware entrypoint: `docs/operations/ai-orchestration/START_HERE.md`
- shared ChatGPT/Codex process: `docs/operations/ai-orchestration/AI_WORKFLOW.md`
- stable safety/git/validation rules: `docs/operations/ai-orchestration/CONTROL.md`
