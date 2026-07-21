# A1 AI Task Manifest and Acceptance Gate Contract

last_updated: 2026-07-21
status: active implementation contract
spec_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A1-SPEC-01`
implementation_work_id: `BTCFX-20260721-AI-TASK-MANIFEST-ACCEPTANCE-GATE-A1-IMPL-01`
parent_contract: `docs/operations/ai-orchestration/AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md`

## 1. Objective and evidence

Create only the A1 standalone contract foundation for versioned task manifests, compact prompt rendering, machine-readable task reports, and fail-closed report alignment.

Verified through `AFROG_Business_MCP` before this spec was created:

- M5 is accepted; M6 is not authorized.
- `chatgpt/specs/active/` contained only `.gitkeep`.
- the eight A1 implementation paths did not exist.
- the parent contract, `CURRENT_STATE.md`, and `NEXT_ACTION.md` all route to bounded A1.

Reported checkpoint hashes remain report locators. Local branch and HEAD must be read from git at implementation start. The recorded expected branch is `Ver04-v2`; mismatch blocks execution rather than being guessed.

## 2. Exact file ownership

### Active spec

- `chatgpt/specs/active/20260721_ai_task_manifest_acceptance_gate_a1.md`

ChatGPT owns its content. Codex must not modify it, but must include the supplied file unchanged in the task-scoped diff check, stage, and local A1 commit.

### Codex editable files

- `chatgpt/tasks/README.md`
- `chatgpt/tasks/schemas/task_manifest.schema.json`
- `chatgpt/tasks/schemas/task_report.schema.json`
- `chatgpt/tasks/examples/implementation_task.example.json`
- `chatgpt/tasks/examples/acceptance_task.example.json`
- `chatgpt/tasks/examples/task_report.example.json`
- `tools/ai_task_contract.py`
- `tests/test_ai_task_contract.py`

The exact commit scope is these eight files plus the unchanged active spec. No other tracked file may be edited, staged, or committed.

## 3. Input and output contract

### IO-01 — Strict JSON and canonical SHA

Task and report files are strict UTF-8 JSON objects. Reject malformed JSON, invalid UTF-8, duplicate keys at any depth, non-object roots, and non-finite numbers.

Canonical task SHA-256 is computed from the parsed object using UTF-8 JSON with sorted keys, compact separators, `ensure_ascii=false`, and no insignificant whitespace. Equivalent formatting and key order produce the same lowercase hexadecimal SHA.

### IO-02 — Manifest v1

`task_manifest.schema.json` and the Python validator must implement parent-contract section 5 with these required top-level fields:

`schema_version`, `work_id`, `revision`, `stage`, `mode`, `goal`, `repo`, `contract_refs`, `allowed`, `autonomy`, `requirements`, `validation`, `commit`, `stop_codes`, `report`.

Required rules:

- `schema_version` is exactly `1.0`; `revision` is an integer at least 1.
- unknown fields fail at every object depth.
- stage/mode pairs are exactly: implementation/`BOUNDED_CODEX`, acceptance/`BOUNDED_CODEX`, review/`REVIEW_ONLY`, checkpoint/`CHECKPOINT_PUSH`, runtime/`RUNTIME_TASK`.
- `requirements` is an array of unique `{id, description}` objects.
- autonomy allows only the six booleans named by the parent contract; omitted values mean false.
- `repo.expected_branch` is non-empty; `expected_base_commit` is null or a 40-character lowercase hexadecimal hash.
- the primary working directory is exactly `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`.
- the frozen runtime repo is valid only for `stage=runtime`.
- the report format is exactly `json_v1`.
- the outbox is exactly `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` with `write_once=true`.

Contract refs, allowed paths, diff-check paths, and report changed files are unique normalized repo-relative POSIX paths. Reject absolute paths, empty paths, backslashes, `.` or `..` components, traversal, and paths resolving outside the repo.

The schemas use JSON Schema Draft 2020-12 with `additionalProperties:false` for every fixed-shape object. The standard-library Python validator is the authoritative A1 semantic validator; A1 does not implement a general-purpose JSON Schema engine.

### IO-03 — Report v1

`task_report.schema.json` and the Python validator require:

`schema_version`, `work_id`, `task_revision`, `task_sha256`, `status`, `branch`, `base_commit`, `changed_files`, `requirements`, `tests`, `heavy_validation`, `commit`, `push`, `notes`.

Required nested shapes:

- requirement evidence: `{status, evidence}` keyed exactly by manifest requirement ID
- test evidence: `{command, status, evidence}`
- heavy evidence: `{authorized, planned_work_units, full_runs, commands}`
- heavy command evidence: `{command, status, evidence}`
- commit: null or `{hash, message}`
- push: null or `{remote, branch, commit}`

Task status is `done`, `partial`, `blocked`, or `failed`. Evidence status is `pass`, `fail`, or `not_run`. Report `base_commit` always records the actual pre-edit 40-character lowercase hexadecimal HEAD.

### IO-04 — CLI

Implement only:

```text
./.venv312/bin/python tools/ai_task_contract.py validate-task --task <path>
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context fresh
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context delta
./.venv312/bin/python tools/ai_task_contract.py validate-report --task <path> --report <path>
```

Success exits 0. Usage, I/O, parsing, shape, or semantic failure exits non-zero with concise stderr. Validation commands print one compact success line; `render-prompt` validates first and prints only the prompt.

## 4. Observable behavior

### AC-01 — Fail-closed stage separation

Implementation requires non-empty `allowed.edit` and exactly:

- `heavy.authorized=false`
- `planned_work_units=0`
- `max_full_runs=0`
- `commands=[]`

Acceptance requires:

- `allowed.edit=[]`
- `heavy.authorized=true`
- `planned_work_units>0`
- `max_full_runs=1`
- exactly one heavy command
- no tracked source repair

Review also requires `allowed.edit=[]`. Push is valid only for checkpoint stage. A1 v1 rejects more than one acceptance full run.

### AC-02 — Exact foreground commands

Manifest commands are exact, single-line foreground commands. Reject newline and shell/background forms containing `&`, `;`, `|`, backticks, `$(`, `nohup`, `disown`, `setsid`, `tmux`, or `screen`.

Allowed development commands are exact `validation.unit_tests` strings plus the canonical command:

```text
git diff --check -- <diff_check_files in manifest order>
```

If fixture E2E is required, at least one listed unit-test command must reference its declared location.

### AC-03 — Compact renderer

The first non-empty line is `AUTO_SEND`. The prompt contains only Work ID, mode, repo-relative manifest path, revision, canonical SHA, context, and short read/validate/execute/no-expansion/report instructions.

- fresh: read `AGENTS.md`, `docs/operations/ai-orchestration/START_HERE.md`, and the manifest; at most 20 non-empty lines
- delta: read only the changed manifest and named files; at most 14 non-empty lines
- hard maximum: 30 non-empty lines

Do not expand active-spec prose, stable safety text, history, dirty-tree paragraphs, full report templates, or unchanged CLI documentation.

### AC-04 — Report alignment

Reject mismatch in Work ID, revision, task SHA, expected branch, or specified expected base commit.

Also reject:

- changed files outside `allowed.edit`
- duplicate changed files
- unlisted, duplicate, widened, or substituted test commands
- unauthorized or mismatched heavy runs
- missing required commit
- unauthorized push
- requirement keys differing from manifest requirements

A `done` report requires every requirement and every required development command to pass with evidence. A `done` acceptance report requires the one exact heavy command to pass once.

If commit is enabled, `done` requires the exact configured message and a 40-character lowercase hexadecimal hash. If disabled, commit is null. Push is null unless checkpoint push is authorized; a reported push commit equals the local commit.

### AC-05 — Canonical outbox

The exact validated report JSON is written once to the fixed outbox. README and examples must state:

- exactly one write operation
- no read-back or existence check
- no retry or recreation
- no polling, loop, or watcher
- immediate move or deletion is normal

The validator verifies the contract but does not write the file.

### AC-06 — Sensitive-data rejection

Reject obvious private material in task/report objects, including sensitive keys for API credentials, tokens, private keys, account/order/position IDs, or raw rows; PEM private-key headers; obvious `sk-`, `xoxb-`, or `AKIA` token prefixes; and address-formatted contact strings.

Approved paths, task SHA values, and commit hashes remain valid.

### AC-07 — Examples and README

Provide one valid implementation manifest, one valid acceptance manifest, and one valid report that validates against the implementation example. Invalid examples are created by mutating valid fixtures inside `tests/test_ai_task_contract.py`; no additional fixture files are authorized.

README documents versioning, commands, hashing, stage separation, report alignment, outbox behavior, and that the manual prompt route remains available until A3.

## 5. Focused validation

### VAL-01 — Test coverage

The standard-library unittest covers:

- strict JSON, duplicate keys, non-finite values, and unknown fields
- stage/mode and path rules
- implementation-heavy and acceptance-edit rejection
- one-run acceptance rule
- canonical SHA stability
- fresh/delta line limits and no prose expansion
- all three valid examples
- Work ID, revision, SHA, branch, base commit, changed files, requirements, commands, heavy run, commit, and push mismatches
- sensitive-data rejection
- subprocess coverage of all four CLI routes

### VAL-02 — Exact development commands

Run only:

```text
./.venv312/bin/python -m unittest tests.test_ai_task_contract
git diff --check -- chatgpt/specs/active/20260721_ai_task_manifest_acceptance_gate_a1.md chatgpt/tasks/README.md chatgpt/tasks/schemas/task_manifest.schema.json chatgpt/tasks/schemas/task_report.schema.json chatgpt/tasks/examples/implementation_task.example.json chatgpt/tasks/examples/acceptance_task.example.json chatgpt/tasks/examples/task_report.example.json tools/ai_task_contract.py tests/test_ai_task_contract.py
```

The unittest must exercise CLI behavior with temporary files and the tracked examples. No `py_compile`, full suite, replay, full bundle, network, background process, runtime action, mail, or notification action is authorized.

### VAL-03 — Dependencies

Use only the Python standard library. Do not install packages or change dependency files.

## 6. Safety and responsibility

### SC-01 — Non-goals

A1 does not include CWT integration, worktree automation, replay-stage/cache redesign, historical conversion, automatic Codex execution, automatic acceptance, automatic next-task selection, canonical startup activation, M6, or product/trading/runtime/notification/mail/API/account/position/order changes.

### SC-02 — Authority

ChatGPT retains scope, safety, validation sufficiency, heavy-run authorization, acceptance, and next-task selection. Codex owns implementation details only inside the eight editable files. Human approval remains required for production, gates, thresholds, notifications, runtime, and order-adjacent changes.

### SC-03 — Dirty tree and git

Codex starts with one `git status --short --branch` and reads actual HEAD. Branch mismatch, missing active spec, changed active-spec content, or overlapping changes in an editable file block execution unless safe preservation is clear.

Unrelated dirty changes remain untouched. Stage exactly the nine-file commit scope. Never reset, restore, checkout, clean, or apply/pop/drop stash. Create one local task-only commit. Push is none.

## 7. Success and archive condition

Implementation is review-ready only when all nine scoped files are in the local commit, both schemas and the Python validator implement the same v1 contract, valid examples pass, invalid contracts fail closed, renderer and report alignment tests pass, focused validation passes, and no external dependency, heavy run, or out-of-scope behavior is introduced.

ChatGPT then directly reviews through `AFROG_Business_MCP`:

- all nine scoped files
- schema/tool alignment
- examples and invalid-case tests
- CLI parser and dispatch
- focused-test report
- commit locator
- scope and safety

Archive only after ChatGPT accepts the implementation. Move this file to:

`chatgpt/specs/archive/20260721_ai_task_manifest_acceptance_gate_a1.md`

Then update `CURRENT_STATE.md` and replace `NEXT_ACTION.md` with one next item. A2, A3, CWT, replay redesign, M6, and production work are not activated automatically.


## 8. Acceptance-lineage correction

### AC-08 — Reviewed implementation commit binding

An acceptance manifest must set `repo.expected_base_commit` to the exact 40-character lowercase hexadecimal commit that ChatGPT reviewed and approved for the acceptance run. `null` is invalid for `stage=acceptance`.

The acceptance report `base_commit` must equal that manifest value. This binds heavy evidence to the reviewed implementation and prevents running acceptance against an unspecified or changed source state.

The acceptance example, JSON Schema conditional rules, Python validator, and focused tests must enforce this requirement. No heavy run is authorized by this correction.

A1 cannot be accepted or archived until AC-08 passes focused validation and direct MCP review.
