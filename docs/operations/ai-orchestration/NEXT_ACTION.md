# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-AUTONOMOUS-STRUCTURE-DAILY-OPERATION`
- mode: `BOUNDED_CODEX_IMPLEMENTATION`
- branch: `Ver04-v3`; confirm from local git before execution
- active_spec: `chatgpt/specs/active/20260721_macro_autonomous_structure_daily_operation.md`
- status: ready for source implementation
- push: none

## Current action

Implement M-OPS1: one dedicated report-only current macro structure operation route.

This is the current primary M task. Do not wait for an M5 refresh trigger.

## Required product behavior

The new route must:

1. use accepted public 15m, 1h, and 4h market-data paths;
2. require no private actual-trade data;
3. choose one deterministic latest common closed-candle cutoff;
4. reuse accepted M1 structure, level identity, lifecycle, and prior-only reliability semantics;
5. produce a current structure snapshot;
6. publish confidence-labelled support/resistance zones;
7. report current price location, next reliable targets, and obstruction;
8. expose stale, discontinuous, and `insufficient` states explicitly;
9. write a complete date/time-scoped local artifact set under `local/reports/macro_structure/`;
10. atomically update a compact `latest.json` summary;
11. remain report-only and independent from M5, mail, notification, and runtime.

## Implementation boundary

Follow the active spec exactly.

Default allowed implementation area:

- `src/feedback/macro_structure_volatility_replay.py`
- new `src/feedback/macro_structure_daily_operation.py`
- `tools/log_feedback.py`
- optional new `tools/run_macro_structure_daily.py`
- focused matching tests
- short factual notes in the active spec

Do not edit production analysis, notification, mail, deploy, runtime, gate, threshold, scoring, classifier, account, position, or order files.

## Validation

Use only:

- matching daily-operation unittest module
- matching M1 regression subset
- matching CLI parser/dispatch tests
- one small deterministic fixture smoke
- task-scoped `git diff --check`

Do not run the M5 full bundle, full test suite, installed schedule, or frozen runtime repo.

## Expected outputs

Minimum generated local files:

```text
local/reports/macro_structure/<run-id>/macro_structure_snapshot.json
local/reports/macro_structure/<run-id>/macro_structure_snapshot.md
local/reports/macro_structure/<run-id>/macro_level_reliability.csv
local/reports/macro_structure/<run-id>/run_manifest.json
local/reports/macro_structure/latest.json
```

Generated outputs remain uncommitted.

## Acceptance path

After Codex reports completion, ChatGPT reviews:

- changed source
- focused tests
- actual CLI parser/dispatch
- deterministic fixture artifact metadata
- event-time cutoff and no-future boundary
- confidence labels and valid `insufficient` behavior
- atomic publication and privacy boundary
- scope and safety

If accepted:

```text
M-OPS1 accepted
→ decide whether M-OPS2 history continuity is already complete or needs one bounded follow-up
→ M-OPS3 chart-first artifact
→ explicit human-approved M-OPS4 runtime/schedule task
```

## P and M5 boundaries

- P readiness remains parked on the private MEXC export batch; do not repeat the accepted review.
- M5 remains accepted and secondary; do not rerun it during M-OPS1.
- M6 remains unauthorized.

## Safety

- report-only
- no automatic order
- no private/account/order endpoints
- no actual-trade requirement
- no mail or notification change
- no runtime, launchd, plist, or schedule change
- no production gate, threshold, scoring, classifier, or policy change
- no frozen runtime repo access
