# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- current branch: `Ver04-v3` (reported by bounded local git execution)
- accepted repository-cleanup checkpoint: `bff7669`
- accepted Product checkpoint: `0eeb26b`
- accepted P state checkpoint: `b9ca3f6`
- accepted P/M planning checkpoint: `ee68e94`
- accepted M5 implementation checkpoint: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- accepted M-OPS1 checkpoint: `89bd338`
- accepted M-OPS2 checkpoint: `dea0e33`
- accepted M-OPS3 checkpoint: `09330b9`
- accepted M-OPS4 source fix: `a9b3d46`
- accepted M-OPS4 runtime implementation: `690c014`
- accepted M-OPS4 state checkpoint: `61e07a9`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: `chatgpt/specs/active/20260722_macro_structure_autonomous_health_status.md`
- current transition: M-OPS5 source implementation
- installed target: `com.afrog.btc-macro-structure`
- safety: report-only / human-decided / no automatic order
- push: none

MCP does not independently expose git branch, HEAD, commit objects, or live `launchctl` state. Branch/commit/loaded-state locators come from bounded local execution reports. Acceptance-critical source, tests, compact runtime status, specs, state paths, and generated artifacts are reviewed directly through MCP.

## Product / P state

- P1–P8 accepted
- P9 blocked pending adequate actual-backed evidence and human approval

Confirmed blocker:

- no complete private MEXC Trade History / Order History / Position History batch under `local/manual_trade_imports/YYYYMMDD/`
- no generated actual-trade episode/link pair
- eligible actual-backed evidence remains 0

Do not repeat importer, episode-builder, signal-linker, CLI, or P8 readiness review unless one reopening trigger is true:

1. a complete private export batch appears;
2. relevant source/tests change;
3. a contradictory artifact appears;
4. the user explicitly requests re-verification.

Canonical decision: `DEC-20260721-012`.

## Macro / M purpose

The primary M objective is autonomous higher-timeframe market-structure understanding from public data for human 15-minute manual-trading judgment.

```text
public 15m / 1h / 4h OHLCV
→ stable support/resistance identity
→ prior-only reliability and lifecycle
→ current structural location
→ confidence-labelled zones
→ chronological evidence history
→ chart-first operator artifact
→ installed report-only cadence
→ autonomous health/status
```

Private actual-trade evidence is not a prerequisite for macro structure calculation. It remains separate evidence for outcome evaluation and production adoption.

Canonical plan:

- `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- decision `DEC-20260721-014`

## Accepted macro foundation

- M1 accepted: event-time levels, lifecycle, prior-only reliability, location, volatility, activation, target/obstruction, outcomes
- M2 accepted: opt-in public-data auxiliary shadow
- M3 accepted: tactical and next-regime separation
- M4 accepted: chart-first local render shadow at `ea89e61`
- M5 accepted: bounded champion/challenger proposal engine
- M6 not started and not authorized

Accepted M5 result remains:

- winner: `none`
- recommendation: `continue_shadow_collection`
- production mutation: none

## Accepted M-OPS1

Accepted at `89bd338`.

Command:

- `run-macro-structure-daily`

Provides public-only cutoff-safe current snapshots, confidence-labelled zones, structure/location, targets/obstruction, volatility/activation, freshness/continuity, valid `insufficient`, immutable artifacts, and atomic latest status.

Reviewed evidence:

- `local/reports/macro_structure/mops1_final_review/`

## Accepted M-OPS2

Accepted at `dea0e33`.

Command:

- `run-macro-structure-history`

Provides deterministic v2 evaluation/structural-checkpoint history, stable level continuity, reliability/role/lifecycle/geometry changes, absence/reappearance, legacy-v1 preservation, immutable artifacts, and atomic latest status.

Reviewed evidence:

- `local/reports/macro_structure/mops2_review/history/`

## Accepted M-OPS3

Accepted source checkpoint: `09330b9`.

Runtime compatibility fix: `a9b3d46`.

Command:

- `render-macro-structure-operator`

Provides deterministic self-contained v2 HTML/SVG, JSON, Markdown, manifest, 96 closed 15-minute candles, all high/medium zones, strict displayed-zone evidence, optional-reference absence handling, categorized history, truthful source traces, visible stale/continuity/data-quality/insufficient state, and macro-only safety.

Reviewed fixture evidence:

- `local/reports/macro_structure/mops3_review/`

## Accepted M-OPS4

Accepted at state checkpoint `61e07a9`.

Implementation:

- runtime wrapper commit: `690c014`
- M-OPS3/runtime-status fix commit: `a9b3d46`
- target label: `com.afrog.btc-macro-structure`
- installed plist SHA-256: `5e99a8538cbcc267cbbff89394b5c4d2aa06ff2ffb2bf315379d8557eea167cb`
- schedule JST: `01:10`, `05:10`, `09:10`, `13:10`, `17:10`, `21:10`
- primary repo Python/wrapper/working/log paths
- no `RunAtLoad`
- no `KeepAlive`

One bounded bootstrap and one launchd kickstart produced a complete successful public pipeline:

- runtime status: `logs/runtime/macro_structure_service_last_result.json`
- snapshot: `run_bc49b15e01e3c2d49d64`
- snapshot ID: `macro_snapshot_bc49b15e01e3c2d49d64`
- history: `history_e0fa3fd0ebc25b781c5f`
- operator: `operator_128b44f88c8a1e02b350`
- snapshot result: `insufficient` (valid)
- history result: `ok`
- stale: `current`
- continuity: `continuous`
- data quality: `ok`
- report-only: true
- private actual-trade input: false
- automatic order allowed: false

Direct artifact review confirmed:

- runtime IDs agree with all three latest pointers;
- operator artifact is complete and `macro_structure_operator_artifact.v2`;
- five high/medium support zones and zero resistance zones are published without fabricating absent references;
- source fingerprints and safety manifests agree.

Archived runtime spec:

- `chatgpt/specs/archive/20260721_macro_structure_runtime_service_enable.md`

Do not repeat M-OPS4 activation or live acceptance without a concrete reopening trigger such as source/plist change, unloaded target evidence, schedule contradiction, failed scheduled cycle, or user-requested verification.

## Current M route

```text
M-OPS1 current snapshot — accepted
→ M-OPS2 chronological history — accepted
→ M-OPS3 chart-first operator artifact — accepted
→ M-OPS4 installed recurring service — accepted
→ M-OPS5 autonomous health and stale-data status — current source task
```

## Current selected action

Implement M-OPS5 under:

- work ID: `BTCFX-20260722-MACRO-STRUCTURE-AUTONOMOUS-HEALTH-STATUS`
- active spec: `chatgpt/specs/active/20260722_macro_structure_autonomous_health_status.md`

M-OPS5 must read existing runtime status, latest pointers, manifests, and the repository plist without rerunning the pipeline or changing runtime. It must distinguish healthy, healthy-insufficient, degraded, failed, overdue, inconsistent, and unavailable states and publish deterministic local JSON/Markdown health artifacts.

Installed automatic health generation is not authorized by the M-OPS5 source task. Any later runtime integration requires a separate explicit `RUNTIME_TASK`.

## Human involvement boundary

No recurring human input is required for the installed public macro pipeline.

Explicit human approval remains required for:

- any new runtime/schedule integration, including automatic M-OPS5 generation;
- live mail or notification integration;
- production gates, thresholds, scoring, classifiers, or policy;
- M6 adoption;
- automatic order behavior;
- phase/version promotion.

## Version and safety policy

- remain on `Ver04-v3`
- runtime activation does not declare `Ver05`
- generated evidence remains ignored and uncommitted under `local/`
- no raw exchange export commit
- no automatic order
- no private/account/order endpoints
- no unapproved mail, notification, policy, or unrelated LaunchAgent change
