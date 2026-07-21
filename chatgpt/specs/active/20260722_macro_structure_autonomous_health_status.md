# Macro Structure Autonomous Health Status

## Metadata

- work_id: `BTCFX-20260722-MACRO-STRUCTURE-AUTONOMOUS-HEALTH-STATUS`
- phase: `M-OPS5`
- mode: `BOUNDED_CODEX_IMPLEMENTATION`
- status: approved for source implementation only
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- accepted_base: `61e07a9`
- accepted_runtime_source: `690c014`
- accepted_operator_fix: `a9b3d46`
- installed_label: `com.afrog.btc-macro-structure`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Objective

Implement one deterministic, read-only health/status operation for the installed macro service.

It must answer:

1. Did the most recent service run complete successfully?
2. Is the result overdue relative to the accepted six-time schedule?
3. Do runtime snapshot/history/operator IDs match the current latest pointers?
4. Are referenced immutable artifacts complete and contract-valid?
5. Is the latest market evidence current, stale, discontinuous, insufficient, failed, or unavailable?
6. Where are the current operator artifact and runtime logs?

M-OPS5 does not rerun the market pipeline. It observes accepted status and artifacts only.

## 2. Accepted inputs

Default inputs:

- `logs/runtime/macro_structure_service_last_result.json`
- `local/reports/macro_structure/latest.json`
- `local/reports/macro_structure/history/latest.json`
- `local/reports/macro_structure/operator/latest.json`
- `deploy/com.afrog.btc-macro-structure.plist`

The operation may read referenced direct-child immutable artifact manifests to verify complete sets and safety flags.

Do not read:

- account, position, or order data;
- private trade exports;
- secrets or `.env`;
- mail or notification state;
- frozen runtime repo;
- arbitrary recursive directories.

## 3. Command

Preferred dedicated command:

```text
check-macro-structure-health
```

Add it to the existing feedback CLI unless a small dedicated wrapper is materially cleaner. It must support compact JSON stdout.

Required arguments:

- `--runtime-status`
- `--snapshot-root`
- `--history-root`
- `--operator-root`
- `--plist`
- `--output-root`
- `--evaluation-time-utc`
- `--stdout-json`

Defaults:

- runtime status: `logs/runtime/macro_structure_service_last_result.json`
- snapshot root: `local/reports/macro_structure/`
- history root: `local/reports/macro_structure/history/`
- operator root: `local/reports/macro_structure/operator/`
- plist: `deploy/com.afrog.btc-macro-structure.plist`
- output root: `local/reports/macro_structure/health/`

`--evaluation-time-utc` is optional for normal use and required in deterministic tests/fixtures. It must be timezone-aware when supplied.

## 4. Schedule contract

Parse the repository plist and require the accepted target contract:

- label `com.afrog.btc-macro-structure`;
- six `StartCalendarInterval` entries:
  - 01:10
  - 05:10
  - 09:10
  - 13:10
  - 17:10
  - 21:10
- primary-repo Python and wrapper paths;
- primary WorkingDirectory;
- expected stdout/stderr paths;
- no `RunAtLoad`;
- no `KeepAlive`.

Do not call `launchctl`, bootstrap, kickstart, bootout, or mutate the installed plist.

Compute:

- most recent scheduled time at or before evaluation time;
- next scheduled time after evaluation time;
- age since the runtime result finished;
- whether the result is overdue.

Use a deterministic grace period of 60 minutes after the most recent scheduled time. A run is overdue when no successful or failed runtime status finished within that expected window.

## 5. Health states

Top-level health state must be one of:

- `healthy`
- `healthy_insufficient`
- `degraded`
- `failed`
- `overdue`
- `inconsistent`
- `unavailable`

Precedence:

1. malformed/missing required input → `unavailable`;
2. IDs, versions, paths, or artifact contracts contradict → `inconsistent`;
3. overdue schedule window → `overdue`;
4. latest runtime status is failed → `failed`;
5. runtime success with stale/discontinuous/non-ok data quality → `degraded`;
6. runtime success and coherent artifacts with snapshot result `insufficient` → `healthy_insufficient`;
7. otherwise → `healthy`.

`insufficient` is a valid operator result, not a service failure.

Do not reinterpret or recalculate market structure, reliability, zones, lifecycle, or history.

## 6. Runtime-status validation

Validate at minimum:

- service schema/method versions are present;
- aware start, finish, and evaluation timestamps;
- `symbol` is present;
- `status` is `success`, `failed`, or `already_running`;
- safety flags:
  - report-only true;
  - private actual-trade input false;
  - automatic order allowed false;
- public input fingerprints are present for 15m, 1h, and 4h when a run reached input staging;
- step order is snapshot → history → operator;
- each step has status and return code;
- successful upstream identities remain visible after a later failure.

`already_running` is not a completed scheduled result. It may be shown as a transient detail but must not replace the last completed health evidence when no persistent completed status exists.

## 7. Artifact consistency

For a successful runtime status, require exact agreement:

- runtime snapshot run ID and snapshot ID ↔ snapshot latest;
- runtime history ID ↔ history latest;
- runtime operator artifact ID ↔ operator latest;
- operator latest selected snapshot/history IDs ↔ the same runtime identities;
- snapshot/history/operator symbols agree;
- result, stale, continuity, and data-quality statuses agree where duplicated.

Validate direct-child path confinement and complete immutable output sets:

### Snapshot

- `macro_structure_snapshot.json`
- `macro_structure_snapshot.md`
- `macro_level_reliability.csv`
- `run_manifest.json`

### History

- `macro_structure_history.json`
- `macro_structure_history.md`
- `macro_snapshot_history.csv`
- `macro_level_history.csv`
- `macro_structure_changes.csv`
- `run_manifest.json`

### Operator

- `macro_structure_operator.html`
- `macro_structure_operator.json`
- `macro_structure_operator.md`
- `run_manifest.json`

Require accepted versions:

- snapshot `macro_structure_daily_operation.v1`;
- history `macro_structure_history_operation.v2`;
- operator `macro_structure_operator_artifact.v2`.

Require public/report-only/no-private/no-order source boundaries from manifests.

## 8. Output contract

Publish one deterministic health artifact for the supplied evaluation time.

Each immutable health directory contains:

- `macro_structure_health.json`
- `macro_structure_health.md`
- `run_manifest.json`

Atomically update:

- `output-root/latest.json`

Use schema/method:

- `macro_structure_health_status.v1`

Minimum JSON fields:

- schema version;
- method version;
- health artifact ID;
- health state;
- severity: `ok`, `warning`, or `error`;
- evaluation UTC/JST;
- last scheduled UTC/JST;
- next scheduled UTC/JST;
- grace minutes;
- runtime started/finished/evaluation times;
- runtime status and first failed step/error when applicable;
- runtime age minutes;
- overdue flag;
- symbol;
- snapshot run ID and snapshot ID;
- history ID;
- operator artifact ID;
- snapshot/history/operator result statuses;
- stale status and stale timeframes;
- continuity status;
- data-quality status;
- support/resistance displayed counts;
- public input fingerprints;
- repo-relative artifact and log locations;
- contract-check results;
- reason codes;
- source fingerprints;
- safety flags and boundary.

The Markdown must begin with an operator summary and clearly state:

- service health;
- last and next expected schedule;
- latest evidence cutoff/evaluation;
- stale/discontinuous/insufficient warning;
- current operator HTML relative path;
- report-only/no automatic order.

Do not include absolute local paths, secrets, raw stdout/stderr, account data, or order data.

## 9. Determinism and publication

For fixed inputs and fixed evaluation time:

- health artifact ID is stable;
- sorting and JSON serialization are stable;
- output bytes are identical;
- existing same-ID differing bytes fail closed;
- complete temporary staging precedes publication;
- previous valid latest remains on failure.

Health identity must include:

- schema/method versions;
- evaluation time;
- runtime status fingerprint;
- three latest-pointer fingerprints;
- plist fingerprint;
- deterministic health rules.

## 10. Exit behavior

Suggested exit codes:

- `0`: `healthy` or `healthy_insufficient`;
- `2`: `degraded` or `overdue`;
- `3`: `failed`, `inconsistent`, or `unavailable`.

A health artifact should still be published for well-formed degraded/failed/overdue states. Malformed unsafe inputs may fail without replacing prior latest.

## 11. Allowed files

- new `src/feedback/macro_structure_health_status.py`
- `tools/log_feedback.py`
- new `tests/test_macro_structure_health_status.py`
- `tests/test_log_feedback.py` only for matching CLI coverage
- this active spec for a short factual implementation note
- one small deterministic fixture helper when useful

Do not edit:

- M1 or M-OPS1–M-OPS4 semantics;
- runtime wrapper or launchd plist;
- installed LaunchAgent;
- mail or notification;
- production UI;
- gates, thresholds, scoring, classifiers, or policy;
- account, position, or order code;
- frozen runtime repo.

If another source file is materially required, stop and report the exact reason.

## 12. Focused tests

Cover at minimum:

1. healthy coherent success;
2. healthy insufficient success;
3. stale success is degraded;
4. discontinuous success is degraded;
5. non-ok data quality is degraded;
6. failed runtime status is failed;
7. overdue relative to six-time schedule;
8. missing runtime status is unavailable;
9. malformed runtime JSON is unavailable/fail-closed;
10. snapshot ID mismatch is inconsistent;
11. history ID mismatch is inconsistent;
12. operator ID mismatch is inconsistent;
13. operator selected-source mismatch is inconsistent;
14. incomplete snapshot artifact is inconsistent;
15. incomplete history artifact is inconsistent;
16. incomplete operator artifact is inconsistent;
17. version mismatch is inconsistent;
18. safety-boundary mismatch is inconsistent;
19. direct-child confinement;
20. exact schedule parsing;
21. missing or altered schedule entry is inconsistent;
22. no RunAtLoad/KeepAlive;
23. deterministic last/next schedule calculation across JST midnight;
24. support/resistance counts;
25. source fingerprints and relative paths;
26. compact stdout JSON;
27. stable identity and byte-identical repeat;
28. same-ID conflict preserves previous latest;
29. failed publication preserves previous latest;
30. actual CLI parser and dispatch.

## 13. Retained review artifact

Create a fixture-only review bundle under:

`local/reports/macro_structure/mops5_review/`

It must demonstrate at least:

- healthy success;
- healthy insufficient;
- degraded stale or discontinuous;
- failed runtime;
- overdue;
- inconsistent ID mismatch.

Retain one published health output for each case in clearly separated fixture roots. Generated fixtures remain uncommitted.

## 14. Validation budget

Run once:

1. `./.venv312/bin/python -m unittest tests.test_macro_structure_health_status`
2. matching M-OPS5 CLI test class only
3. one deterministic healthy fixture CLI smoke
4. one deterministic overdue or failed fixture CLI smoke
5. one identical healthy repeat for idempotence
6. task-scoped `git diff --check`

Do not run:

- full test suite;
- live public fetch;
- launchctl or installed runtime commands;
- M5 or M6;
- mail or notification tests;
- frozen runtime repo.

## 15. Completion criteria

M-OPS5 source is complete when:

- one read-only health command exists;
- schedule, status, pointers, artifacts, versions, and safety are checked;
- healthy/insufficient/degraded/failed/overdue/inconsistent/unavailable are distinguishable;
- deterministic JSON/Markdown/manifests and atomic latest are published;
- focused tests and retained fixtures prove the contract;
- no runtime, delivery, policy, private, or execution behavior changes;
- one local commit and compact report are produced.

Installed automatic generation of the M-OPS5 health artifact is not authorized by this source task. Any later runtime integration requires a separate explicit `RUNTIME_TASK`.

## Implementation note

M-OPS5 is implemented as the read-only `check-macro-structure-health` route with deterministic v1 health artifacts, schedule/status/latest-pointer validation, atomic publication, and focused fixture coverage. It does not invoke M-OPS1–M-OPS4, launchctl, live fetch, or runtime mutation.
