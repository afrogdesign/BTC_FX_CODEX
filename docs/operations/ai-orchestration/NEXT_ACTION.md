# NEXT_ACTION

- current_work_id: `BTCFX-20260722-MACRO-STRUCTURE-AUTONOMOUS-HEALTH-STATUS-FIX-02`
- mode: `BOUNDED_CODEX_FIX`
- branch: `Ver04-v3`; confirm from local git before execution
- implementation_base: `58c1e80`
- runtime_implementation_commit: `690c014`
- operator_runtime_fix_commit: `a9b3d46`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_autonomous_health_status.md`
- status: M-OPS5 not accepted; final audit-consistency FIX required
- installed_target: `com.afrog.btc-macro-structure`
- push: none

## Current action

Complete the final M-OPS5 consistency boundary without changing M-OPS1–M-OPS4 or installed runtime behavior.

Required:

1. validate identity fields and duplicated status fields inside snapshot/history/operator `latest.json`;
2. require runtime status to agree with snapshot/history/operator source values for result, stale, continuity, and data quality;
3. require exact public-source strings in each accepted artifact manifest;
4. omit or reject stale IDs for stages that did not complete successfully;
5. validate success return codes and timestamp ordering/future evidence;
6. expand focused contradiction coverage;
7. retain exactly six review cases, one health artifact and one canonical CLI result per case.

## Preserve

- health-state precedence;
- six JST schedule entries and 60-minute grace;
- deterministic atomic v1 publication;
- direct-child and complete-set validation;
- valid `insufficient` as `healthy_insufficient`;
- report-only/no-private/no-order boundary;
- no launchctl, live fetch, runtime, delivery, policy, or execution mutation.

## Validation

Use only focused M-OPS5 tests, matching CLI tests, deterministic fixture smokes, one identical repeat, and task-scoped `git diff --check`.

Do not run the full suite, launchctl, installed runtime, live fetch, M5/M6, mail/notification tests, or frozen-repo commands.

## Acceptance path

After the FIX report, ChatGPT directly reviews source, tests, CLI, six retained cases, state/spec, and safety. If accepted, M-OPS5 source and the autonomous M implementation plan are complete. Automatic recurring generation of M-OPS5 remains a separate explicit `RUNTIME_TASK`.
