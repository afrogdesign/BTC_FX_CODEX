# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-STRUCTURE-CHART-FIRST-OPERATOR-ARTIFACT`
- mode: `BOUNDED_CODEX_IMPLEMENTATION`
- branch: `Ver04-v3`; confirm from local git before execution
- accepted_base: `dea0e33`
- active_spec: `chatgpt/specs/active/20260721_macro_structure_chart_first_operator_artifact.md`
- status: ready for source implementation
- push: none

## Current action

Implement M-OPS3: one deterministic self-contained chart-first local operator artifact.

M-OPS1 and M-OPS2 are accepted. Do not reopen their analysis, reliability, identity, freshness, chronology, or publication semantics unless a concrete source/input-contract contradiction is demonstrated.

## Required product behavior

The new route must:

1. resolve one complete latest M-OPS1 direct-child immutable snapshot;
2. resolve one complete latest M-OPS2 v2 direct-child immutable history artifact;
3. verify that history contains the selected current snapshot run;
4. read one explicit local public 15-minute OHLCV CSV;
5. exclude candles after the snapshot cutoff;
6. verify the latest eligible 15-minute close against snapshot current price;
7. render a self-contained chart-first HTML with inline SVG;
8. show high/medium macro support and resistance zones with level identity, role, reliability, and lifecycle;
9. show current structure/location, targets, obstruction, volatility, activation, freshness, and continuity;
10. show bounded recent history changes with stable level IDs;
11. keep stale, discontinuous, and insufficient states prominent;
12. publish one complete deterministic immutable artifact set and atomic latest summary;
13. remain macro-only, report-only, and independent from delivery, runtime, policy, and execution behavior.

## Command and outputs

Command:

```text
render-macro-structure-operator
```

Default output root:

```text
local/reports/macro_structure/operator/
```

Minimum generated files:

```text
<operator-id>/macro_structure_operator.html
<operator-id>/macro_structure_operator.json
<operator-id>/macro_structure_operator.md
<operator-id>/run_manifest.json
latest.json
```

Generated outputs remain uncommitted.

## Implementation boundary

Follow the active spec.

Default implementation area:

- new `src/feedback/macro_structure_operator_artifact.py`
- minimal parser/dispatch wiring in `tools/log_feedback.py`
- new focused M-OPS3 test module
- matching M-OPS3 CLI tests in `tests/test_log_feedback.py`
- the active spec for one short factual implementation note
- one small deterministic fixture helper when clearly needed

The accepted M4 renderer may be read and pure SVG/layout patterns reused. Do not depend on M3 inputs, tactical candidate inputs, or signal IDs.

Do not edit accepted M1, M-OPS1, or M-OPS2 source unless an input-contract defect is demonstrated and reported first.

Do not edit production analysis, production UI, notification, mail, delivery, runtime, gate, threshold, scoring, classifier, account, position, or order files.

## Validation

Use only:

- matching M-OPS3 unittest module
- matching M-OPS3 CLI parser/dispatch tests
- one bounded deterministic fixture smoke
- one identical repeat for idempotence
- task-scoped `git diff --check`

Do not run full suite, live fetch, M5, broad replay, installed runtime/schedule, browser automation, screenshot comparison, or frozen runtime repo.

## Acceptance path

After Codex reports completion, ChatGPT reviews:

- changed source
- focused tests
- actual CLI parser/dispatch
- exact snapshot/history selection
- M-OPS2 v2 and current-snapshot inclusion
- 15-minute closed-candle/no-future behavior
- chart-first HTML order
- reliable zone geometry and evidence labels
- stale/discontinuous/insufficient visibility
- chronological change panel
- deterministic complete artifact publication
- privacy, scope, and safety

If accepted:

```text
M-OPS3 accepted
→ request explicit human approval before M-OPS4 runtime/schedule enablement
```

M-OPS4 is a separate `RUNTIME_TASK`. Source acceptance does not authorize installed execution.

## P and M5 boundaries

- P readiness remains parked on the absent complete MEXC export batch; do not repeat the accepted review.
- M5 remains accepted and secondary; do not rerun it during M-OPS3.
- M6 remains unauthorized.

## Safety

- report-only
- no automatic order
- no private/account/order endpoints
- no live fetch
- no tactical execution implication
- no mail or notification change
- no runtime, launchd, plist, cron, or schedule change
- no production gate, threshold, scoring, classifier, or policy change
- no frozen runtime repo access
