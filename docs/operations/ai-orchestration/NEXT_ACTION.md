# NEXT_ACTION

- current_work_id: `BTCFX-20260722-MACRO-STRUCTURE-AUTONOMOUS-HEALTH-STATUS`
- mode: `BOUNDED_CODEX_IMPLEMENTATION`
- branch: `Ver04-v3`; confirm from local git before execution
- accepted_base: `61e07a9`
- runtime_implementation_commit: `690c014`
- operator_runtime_fix_commit: `a9b3d46`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_autonomous_health_status.md`
- status: ready for M-OPS5 source implementation
- installed_target: `com.afrog.btc-macro-structure`
- push: none

## Current action

Implement one read-only deterministic macro service health/status operation.

Inputs:

- `logs/runtime/macro_structure_service_last_result.json`
- snapshot/history/operator `latest.json` and referenced manifests
- repository plist `deploy/com.afrog.btc-macro-structure.plist`
- explicit or current aware evaluation time

The operation must not rerun the public-data pipeline or call `launchctl`.

## Accepted runtime state

M-OPS4 is accepted.

Installed contract:

- label: `com.afrog.btc-macro-structure`
- schedule JST: `01:10`, `05:10`, `09:10`, `13:10`, `17:10`, `21:10`
- primary repo Python/wrapper/working/log paths
- no `RunAtLoad` or `KeepAlive`

Accepted live result:

- snapshot: `run_bc49b15e01e3c2d49d64`
- snapshot ID: `macro_snapshot_bc49b15e01e3c2d49d64`
- history: `history_e0fa3fd0ebc25b781c5f`
- operator: `operator_128b44f88c8a1e02b350`
- snapshot result: `insufficient` (valid)
- history result: `ok`
- stale: `current`
- continuity: `continuous`
- data quality: `ok`
- report-only / no private input / no automatic order

Do not repeat M-OPS4 activation or live acceptance without a documented reopening trigger.

## Required health states

Distinguish:

- `healthy`
- `healthy_insufficient`
- `degraded`
- `failed`
- `overdue`
- `inconsistent`
- `unavailable`

`insufficient` is a valid result, not a service failure.

## Required checks

1. parse and validate the six-time repository plist contract;
2. calculate last and next scheduled time in JST/UTC;
3. apply a deterministic 60-minute schedule grace period;
4. validate runtime timestamps, step order, public fingerprints, IDs, statuses, and safety;
5. require runtime IDs to agree with all three latest pointers;
6. require complete direct-child immutable artifact sets;
7. require accepted snapshot/history/operator versions and manifest safety;
8. expose stale, continuity, data quality, result status, and displayed zone counts;
9. publish deterministic JSON, Markdown, manifest, and atomic latest health summary;
10. preserve prior latest on conflict or publication failure.

## Implementation boundary

Default files:

- new `src/feedback/macro_structure_health_status.py`
- `tools/log_feedback.py`
- new `tests/test_macro_structure_health_status.py`
- `tests/test_log_feedback.py` only for matching M-OPS5 CLI coverage
- active spec for one factual implementation note
- one small matching fixture helper when useful

Do not edit:

- M1 or M-OPS1–M-OPS4 semantics;
- runtime wrapper or plist;
- installed LaunchAgent;
- production UI, mail, notification, policy, account, position, or order code;
- frozen runtime repo.

## Validation

Use only:

- matching M-OPS5 unittest module;
- matching CLI test class;
- one deterministic healthy fixture smoke;
- one deterministic overdue or failed fixture smoke;
- one identical healthy repeat for idempotence;
- task-scoped `git diff --check`.

Do not run full suite, live public fetch, launchctl, installed runtime, M5/M6, mail/notification tests, or frozen-repo commands.

## Acceptance path

After Codex reports completion, ChatGPT reviews:

- source and health-state precedence;
- schedule calculation;
- status/latest/artifact consistency;
- direct-child and complete-set validation;
- deterministic publication;
- retained M-OPS5 review fixtures;
- safety and scope.

If accepted, the autonomous M source plan is complete through M-OPS5. Automatic recurring generation of the health artifact remains a separately approved runtime integration.

## Safety

- report-only
- no automatic order
- no private/account/position/order endpoint
- no mail or notification integration
- no launchd or schedule mutation
- no production policy mutation
- no M5/M6
- no version promotion
- no push
