# NEXT_ACTION

- current_work_id: `BTCFX-20260722-MACRO-STRUCTURE-AUTONOMOUS-HEALTH-STATUS-FIX-01`
- mode: `BOUNDED_CODEX_FIX`
- branch: `Ver04-v3`; confirm from local git before execution
- implementation_base: `fa0f734`
- runtime_implementation_commit: `690c014`
- operator_runtime_fix_commit: `a9b3d46`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_autonomous_health_status.md`
- status: M-OPS5 source implemented but not accepted; focused audit-contract FIX required
- installed_target: `com.afrog.btc-macro-structure`
- push: none

## Current action

Fix three bounded M-OPS5 acceptance defects without changing M-OPS1–M-OPS4 or installed runtime behavior.

1. Generate the current operator HTML path from the validated operator artifact directory/ID. The reviewed output incorrectly contains `local/reports/macro_structure/operator/None/macro_structure_operator.html`.
2. Accept a well-formed ordered runtime-step prefix when the service stopped after an early snapshot or history failure. Such a completed failed status must publish `failed`, not `inconsistent` or `unavailable`. Successful runtime still requires all three successful steps.
3. Namespace source fingerprints by artifact type and filename so snapshot/history/operator manifests and all three latest pointers are individually retained in health identity and output.

Regenerate `local/reports/macro_structure/mops5_review/` so each required health case has one clearly designated final health output and no ambiguous intermediate review roots.

## Preserve

- health-state precedence;
- six-time schedule and 60-minute grace;
- direct-child and complete-set validation;
- accepted versions and safety boundaries;
- deterministic atomic publication;
- no runtime, launchctl, live fetch, mail, notification, policy, private endpoint, or order change.

## Validation

Use only:

- `tests.test_macro_structure_health_status`;
- matching M-OPS5 CLI test class;
- one deterministic healthy/healthy-insufficient smoke;
- early snapshot-failure and early history-failure fixture checks;
- one identical repeat;
- task-scoped `git diff --check`.

Do not run the full suite, launchctl, installed runtime, live fetch, M5/M6, mail/notification tests, or frozen-repo commands.

## Acceptance path

After the FIX report, ChatGPT directly reviews source, focused tests, CLI, final six-state review artifacts, state/spec transition, and safety. If accepted, M-OPS5 source is complete. Automatic recurring health generation remains a separate explicitly approved runtime task.
