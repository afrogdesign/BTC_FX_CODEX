# AI Task Manifest and Acceptance Gate Specification

last_updated: 2026-07-21
status: approved design reference; ready for bounded A1 active spec
scope: ChatGPT-to-Codex task contract, short prompt rendering, report validation, and heavy-run authorization
parent_plan: `MACRO_REPLAY_AND_AI_ACCEPTANCE_SIMPLIFICATION_PLAN_20260721.md`

## 1. Purpose

Replace long hand-written Codex prompts and thread-carried state with a small, versioned, machine-readable task contract.

Target flow:

```text
Human request
→ ChatGPT judgment and repo review
→ task manifest
→ short rendered Codex prompt
→ Codex implementation plus lightweight validation
→ machine-readable report
→ ChatGPT MCP review
→ separate acceptance manifest only when a heavy run is still needed
```

This design must reduce repeated context and validation loops without weakening product, trading, safety, fail-closed, future-isolation, acceptance, or human-approval boundaries.

## 2. Activation status

M5 was accepted at implementation checkpoint `3c7f01d` with:

- winner: `none`
- recommendation: `continue_shadow_collection`
- no production, runtime, notification, mail, gate, threshold, or order change

The M5 active spec is archived. This document no longer has an M5/FIX boundary.

The next permitted implementation step is a separate Phase A1 active spec. A1 must not include CWT integration, replay-pipeline redesign, persistent M1/M3 cache, M6, or production work.

## 3. Ownership

### ChatGPT owns

- product, trading, and safety judgment
- task scope and contract references
- allowed-file ownership
- acceptance evidence and validation sufficiency
- heavy-run authorization
- acceptance and next-task selection

### Codex owns

Inside allowed files and the accepted contract:

- helper structure
- deterministic fixture design
- contract-preserving cache or duplicate-work removal
- edit/test order
- obvious in-scope bug fixes
- omission of redundant validation that proves no additional fact

Codex may not reduce periods, candidates, thresholds, gates, fail-closed rules, evidence requirements, or safety boundaries.

### CWT/worktree tooling owns

Transport only:

- worktree/session selection
- rendered prompt delivery
- report collection

It does not decide scope, validation, acceptance, or next phase.

## 4. Canonical files

Phase A1 creates:

```text
chatgpt/tasks/
  README.md
  schemas/
    task_manifest.schema.json
    task_report.schema.json
  examples/
    implementation_task.example.json
    acceptance_task.example.json
    task_report.example.json

tools/
  ai_task_contract.py

tests/
  test_ai_task_contract.py
```

Rules:

- manifests and reports use JSON
- paths inside contracts are repo-relative, except the fixed repo and outbox paths
- no secret, account, raw exchange, raw row, or address-formatted contact data
- schemas, examples, tool, and tests are tracked
- execution reports are transport artifacts and are not committed by default

## 5. Task manifest v1

Required top-level structure:

```json
{
  "schema_version": "1.0",
  "work_id": "BTCFX-...",
  "revision": 1,
  "stage": "implementation",
  "mode": "BOUNDED_CODEX",
  "goal": "One coherent result",
  "repo": {},
  "contract_refs": [],
  "allowed": {},
  "autonomy": {},
  "requirements": [],
  "validation": {},
  "commit": {},
  "stop_codes": [],
  "report": {}
}
```

Unknown fields fail validation.

### 5.1 Identity

- `work_id` is immutable after execution starts
- `revision` starts at 1
- pre-execution corrections increment revision
- material scope or acceptance changes require a new Work ID
- Codex reports the exact manifest revision and canonical SHA-256

### 5.2 Stages

Allowed values:

| stage | mode | purpose |
|---|---|---|
| `implementation` | `BOUNDED_CODEX` | edit, focused tests, diff check, local commit |
| `acceptance` | `BOUNDED_CODEX` | one authorized heavy evidence run; no source repair |
| `review` | `REVIEW_ONLY` | bounded read-only fact check |
| `checkpoint` | `CHECKPOINT_PUSH` | explicit checkpoint validation and push |
| `runtime` | `RUNTIME_TASK` | explicitly approved runtime operation |

### 5.3 Repo

```json
{
  "working_dir": "/Users/marupro/CODEX/100_MCP_Server/btc_monitor",
  "expected_branch": "Ver04-v2",
  "expected_base_commit": null
}
```

Actual branch and HEAD come from repo state. Mismatch blocks execution. The frozen runtime repo is invalid unless `stage=runtime`.

### 5.4 Contract references

```json
[
  {
    "path": "chatgpt/specs/active/example.md",
    "clauses": ["AC-01", "SC-01", "VAL-01"]
  }
]
```

New active specs should use stable clause IDs:

- `IO-xx`: input/output
- `AC-xx`: acceptance behavior
- `SC-xx`: safety
- `VAL-xx`: validation

The manifest references clauses; the rendered prompt does not repeat their prose.

### 5.5 Allowed files

```json
{
  "read": ["repo/relative/path"],
  "edit": ["repo/relative/path"],
  "inspect": ["git_status", "task_diff", "target_definition", "direct_callers", "nearby_helpers", "matching_tests"]
}
```

Rules:

- implementation requires non-empty `edit`
- acceptance and review require empty tracked-file `edit`
- no absolute paths or traversal in allowed file lists
- changed tracked files must be a subset of `allowed.edit`
- broad exploration is never implied

### 5.6 Autonomy

```json
{
  "helper_design": true,
  "cache_design": true,
  "fixture_design": true,
  "execution_order": true,
  "obvious_in_scope_bugfix": true,
  "remove_redundant_validation": true
}
```

All fields default false. Enabled autonomy never overrides the task contract or allowed files.

### 5.7 Validation

Implementation example:

```json
{
  "unit_tests": ["./.venv312/bin/python -m unittest tests.test_target"],
  "fixture_e2e": {"required": true, "location": "tests.test_target"},
  "diff_check_files": ["src/target.py", "tests/test_target.py"],
  "heavy": {"authorized": false, "planned_work_units": 0, "max_full_runs": 0, "commands": []}
}
```

Acceptance example:

```json
{
  "unit_tests": [],
  "fixture_e2e": {"required": false, "location": null},
  "diff_check_files": [],
  "heavy": {"authorized": true, "planned_work_units": 31, "max_full_runs": 1, "commands": ["<exact bounded command>"]}
}
```

Hard rules:

- implementation cannot authorize heavy validation
- acceptance must explicitly authorize heavy validation
- acceptance defaults to one full run
- background commands are rejected
- command lists are exact and may not be widened
- a second full run requires an explicit acceptance clause showing why publication-only verification is insufficient

### 5.8 Commit and report

```json
{
  "commit": {"enabled": true, "message": "fix example", "push": false},
  "report": {
    "format": "json_v1",
    "outbox": "/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt",
    "write_once": true
  }
}
```

Push is valid only for checkpoint stage. Task files only are staged.

## 6. Contract tool

Implement:

```text
tools/ai_task_contract.py
```

Commands:

```bash
./.venv312/bin/python tools/ai_task_contract.py validate-task --task <path>
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context fresh
./.venv312/bin/python tools/ai_task_contract.py render-prompt --task <path> --context delta
./.venv312/bin/python tools/ai_task_contract.py validate-report --task <path> --report <path>
```

Use the Python standard library unless a future active spec explicitly approves an existing dependency.

Canonical manifest SHA-256 uses UTF-8, sorted keys, compact separators, and no insignificant whitespace.

## 7. Rendered prompt

Fresh prompt target: at most 20 non-empty lines.
Delta prompt target: at most 14 non-empty lines.
Hard maximum: 30 non-empty lines.

Fresh form:

```text
AUTO_SEND

WORK_ID: <id>
MODE: <mode>
TASK_MANIFEST: <repo-relative path>
TASK_REVISION: <revision>
TASK_SHA256: <sha256>
CONTEXT: fresh

Read AGENTS.md, START_HERE.md, and the task manifest.
Validate the manifest before editing.
Execute exactly the manifest contract with allowed-file autonomy.
Do not expand validation or scope.
Return the json_v1 report and write it to the configured outbox exactly once.
```

The renderer must not expand active-spec prose, stable safety boilerplate, accepted history, dirty-tree paragraphs, full report templates, or unchanged CLI descriptions.

## 8. Task report v1

```json
{
  "schema_version": "1.0",
  "work_id": "BTCFX-...",
  "task_revision": 1,
  "task_sha256": "...",
  "status": "done",
  "branch": "Ver04-v2",
  "base_commit": "...",
  "changed_files": [],
  "requirements": {},
  "tests": [],
  "heavy_validation": {},
  "commit": null,
  "push": null,
  "notes": null
}
```

Allowed status values: `done`, `partial`, `blocked`, `failed`.

Requirement evidence is a compact locator, not a transcript.

The report validator rejects:

- Work ID, revision, or SHA mismatch
- changed files outside `allowed.edit`
- unlisted test commands
- unauthorized heavy validation
- `done` with required test or requirement not passing
- missing required commit
- unauthorized push
- raw IDs, raw rows, secrets, or private/account/order data

The exact validated JSON is written once to the fixed outbox. No read, existence check, retry, polling, or recreation follows.

## 9. Acceptance gate

After implementation:

1. validate the report against the manifest
2. ChatGPT directly reviews source, tests, CLI, fixture evidence, and spec notes through MCP
3. accept from existing evidence, create one minimal FIX manifest, or create a separate acceptance manifest

An acceptance manifest must:

- use `stage=acceptance`
- name the reviewed implementation commit
- allow no tracked source edits
- contain one exact heavy command by default
- declare planned work units
- prohibit implementation repair
- define compact artifact evidence

If the command fails, Codex reports and stops. It does not rerun unchanged or repair source in the acceptance task.

## 10. Worktree ownership

The manifest is the ownership lease for `allowed.edit`.

- ChatGPT does not concurrently edit leased files
- Codex does not edit unleased orchestration files
- overlapping leases are prohibited
- unrelated dirty changes are preserved
- separate worktrees are preferred only when concurrent ownership could overlap
- small sequential tasks may use one working tree

After execution starts, the manifest is immutable. A bounded correction requires a new revision and rendered prompt; a material change requires a new Work ID.

## 11. Phase plan

### A1 — contract foundation

Implement only:

- task schema
- report schema
- examples
- validator and prompt renderer
- focused tests
- task README

No CWT integration, replay changes, runtime work, or canonical startup activation.

### A2 — low-risk pilot

Use the manifest flow for one bounded docs-only or single-module low-risk task.

Success requires:

- prompt at most 30 non-empty lines
- validated report
- changes inside scope
- no heavy validation
- no repeated stable boilerplate

### A3 — canonical routing activation

After the pilot succeeds, update:

- `AGENTS.md`
- `START_HERE.md`
- `AI_WORKFLOW.md`
- `CONTROL.md`
- `INITIAL_PROMPT.md`

Rendered manifest prompts then become the default. The manual route remains a fallback.

### A4 — optional CWT integration

Only after A1–A3 work without CWT. The repo contract must remain independently usable.

### Separate follow-on

Replay stages, intermediate schemas, persistent fingerprints, and cache invalidation require a different active spec based on the parent simplification plan.

## 12. A1 allowed files

A future A1 active spec should normally allow only:

```text
chatgpt/tasks/README.md
chatgpt/tasks/schemas/task_manifest.schema.json
chatgpt/tasks/schemas/task_report.schema.json
chatgpt/tasks/examples/implementation_task.example.json
chatgpt/tasks/examples/acceptance_task.example.json
chatgpt/tasks/examples/task_report.example.json
tools/ai_task_contract.py
tests/test_ai_task_contract.py
docs/operations/ai-orchestration/AI_TASK_MANIFEST_AND_ACCEPTANCE_GATE_SPEC_20260721.md
```

Canonical startup docs are A3 work, not A1 work.

## 13. A1 acceptance criteria

A1 is review-ready when:

1. valid implementation and acceptance manifests pass
2. unknown fields, traversal, invalid stage/mode, and scope violations fail closed
3. implementation heavy-run authorization is rejected
4. acceptance source edits are rejected
5. canonical SHA is deterministic
6. fresh and delta prompts meet the line limits
7. prompts do not expand active-spec prose or stable boilerplate
8. report changed files, tests, heavy runs, commit, and push are validated against the manifest
9. all focused tests pass
10. no external dependency is added
11. no production/runtime/notification/mail/order behavior changes
12. the manual prompt route remains available until A3

## 14. Non-goals

This specification does not authorize:

- trading logic, scoring, threshold, gate, or classifier changes
- replay-pipeline redesign or persistent replay cache
- automatic Codex execution or automatic acceptance
- automatic next-task selection
- CWT integration during A1
- runtime, notification, mail, API, account, position, or order changes
- production adoption
- M6

## 15. Archive rule

This is a stable design reference, not an active implementation spec.

Create one bounded A1 active spec after the AI orchestration docs checkpoint is committed. Archive A1 normally after ChatGPT accepts its implementation. A2 and A3 receive separate active specs or bounded contract sections; do not combine all phases into one Codex task.
