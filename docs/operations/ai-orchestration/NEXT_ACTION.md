# NEXT_ACTION

- current_work_id: `BTCFX-20260721-P8-ISSUE-LIFECYCLE-ALIGNMENT`
- mode: `BOUNDED_CODEX`
- branch: confirm from local git state; expected documentation line is `Ver04-v3`
- active_spec: `chatgpt/specs/active/20260721_p8_issue_lifecycle_alignment.md`
- status: approved for bounded implementation
- push: none

## Current action

Align the deterministic P8 issue-summary lifecycle with already accepted operator-surface behavior.

Required result:

- preserve `P8-ISSUE-001` as an evidence-driven open hypothesis
- mark seeded UI issues 002–004 as resolved
- add deterministic accepted-implementation resolution basis metadata
- keep all evaluation counts, P9 readiness, classifier, gates, thresholds, notification, mail, and runtime behavior unchanged
- add matching unit regressions
- create one local commit

## Validation budget

- `tests.test_manual_operator_trial_evidence`
- one task-scoped `git diff --check`
- no full bundle or real-data replay

## Acceptance boundary

After Codex completion, ChatGPT reviews the changed source, matching tests, scope, and commit report through `AFROG_Business_MCP`.

Only after acceptance will ChatGPT:

- update `P8_P9_ISSUE_REGISTER.md`
- archive the active spec
- update accepted current state and select the next task

## Safety

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no classifier, gate, threshold, scoring, notification, mail, runtime, API, account, position, or order change
