# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-STRUCTURE-CHRONOLOGICAL-HISTORY-CONTINUITY`
- mode: `BOUNDED_CODEX_IMPLEMENTATION`
- branch: `Ver04-v3`; confirm from local git before execution
- accepted_base: `89bd338`
- active_spec: `chatgpt/specs/active/20260721_macro_structure_chronological_history_continuity.md`
- status: ready for source implementation
- push: none

## Current action

Implement M-OPS2: one deterministic report-only chronological history operation over complete immutable M-OPS1 artifacts.

M-OPS1 is accepted. Do not reopen its structure, reliability, cutoff, symbol, freshness, identity, or publication semantics unless a concrete input-contract defect is demonstrated.

## Required product behavior

The new route must:

1. read only direct-child complete M-OPS1 `run_*` artifact directories from an explicit snapshot root;
2. isolate one explicit symbol;
3. validate source run identity, manifest, timestamps, public-only/report-only boundary, and level schema;
4. preserve every evaluation run chronologically;
5. distinguish freshness-only reevaluations from unique structural checkpoints;
6. prove stable `level_id` continuity across checkpoints;
7. expose reliability score/band, role, lifecycle, and evidence-count changes;
8. expose absence and reappearance without inventing permanent retirement;
9. expose structure, location, target, obstruction, volatility, activation, stale, continuity, and data-quality changes;
10. write a complete immutable history artifact set;
11. atomically update a compact history `latest.json`;
12. remain independent from live fetch, private trade inputs, M5, delivery, runtime, and execution behavior.

## Command and outputs

Command:

```text
run-macro-structure-history
```

Default output root:

```text
local/reports/macro_structure/history/
```

Minimum generated files:

```text
<history-run>/macro_structure_history.json
<history-run>/macro_structure_history.md
<history-run>/macro_snapshot_history.csv
<history-run>/macro_level_history.csv
<history-run>/macro_structure_changes.csv
<history-run>/run_manifest.json
latest.json
```

Generated outputs remain uncommitted.

## Implementation boundary

Follow the active spec.

Default allowed implementation area:

- new `src/feedback/macro_structure_history_operation.py`
- `tools/log_feedback.py`
- new `tests/test_macro_structure_history_operation.py`
- matching M-OPS2 CLI tests in `tests/test_log_feedback.py`
- the active and archived M-OPS specs and current state documents already changed by ChatGPT
- one small deterministic fixture helper when clearly needed

Do not edit accepted M1 or M-OPS1 source unless an input-contract defect is demonstrated and reported first.

Do not edit production analysis, delivery, runtime, gate, threshold, scoring, classifier, account, position, or order files.

## Validation

Use only:

- matching history-operation unittest module
- matching M-OPS2 CLI parser/dispatch tests
- one bounded deterministic multi-date fixture smoke
- task-scoped `git diff --check`

Do not run full suite, live public fetch, M5, broad replay, installed runtime/schedule, or frozen runtime repo.

## Acceptance path

After Codex reports completion, ChatGPT reviews:

- changed source
- focused tests
- actual CLI parser/dispatch
- complete multi-date history artifacts
- evaluation versus structural-checkpoint deduplication
- level identity, transitions, absence, and reappearance
- no-future chronological behavior
- atomicity, determinism, privacy, scope, and safety

If accepted:

```text
M-OPS2 accepted
→ M-OPS3 chart-first operator artifact
→ explicit human-approved M-OPS4 runtime/schedule task
```

## P and M5 boundaries

- P readiness remains parked on the absent complete MEXC export batch; do not repeat the accepted review.
- M5 remains accepted and secondary; do not rerun it during M-OPS2.
- M6 remains unauthorized.

## Safety

- report-only
- no automatic order
- no private/account/order endpoints
- no live fetch required
- no mail or notification change
- no runtime, launchd, plist, cron, or schedule change
- no production gate, threshold, scoring, classifier, or policy change
- no frozen runtime repo access
