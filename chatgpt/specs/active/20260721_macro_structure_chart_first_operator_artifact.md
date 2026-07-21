# Macro Structure Chart-First Operator Artifact

## Metadata

- work_id: `BTCFX-20260721-MACRO-STRUCTURE-CHART-FIRST-OPERATOR-ARTIFACT`
- phase: `M-OPS3`
- status: approved for bounded source implementation
- accepted_snapshot_checkpoint: `89bd338`
- accepted_history_checkpoint: `dea0e33`
- accepted_snapshot_command: `run-macro-structure-daily`
- accepted_history_command: `run-macro-structure-history`
- branch: `Ver04-v3`
- safety: report-only / human-decided / no runtime or delivery apply

## Objective

Create one deterministic self-contained local operator artifact that lets a human inspect the latest accepted macro structure directly on a 15-minute chart before making a manual trading decision.

The artifact must combine:

- one complete accepted M-OPS1 latest snapshot;
- one complete accepted M-OPS2 v2 latest history artifact that includes the selected snapshot run;
- one explicit local public 15-minute OHLCV file.

It must not rerun M1 analysis, infer new support/resistance, select a trade, or mutate delivery/runtime behavior.

## Command

Add:

```text
render-macro-structure-operator
```

Minimum CLI arguments:

- `--snapshot-root`
- `--history-root`
- `--ohlcv-15m-csv`
- `--output-root`
- `--symbol`
- `--stdout-json`

Default roots:

```text
snapshot: local/reports/macro_structure/
history:  local/reports/macro_structure/history/
output:   local/reports/macro_structure/operator/
```

The command must not fetch live data. All inputs are explicit local public artifacts.

## Source selection and validation

### Snapshot

Read `snapshot-root/latest.json`, then resolve exactly one direct-child immutable `run_*` directory.

Validate:

- latest `run_id` and `artifact_dir` identify the same direct child;
- complete M-OPS1 file set exists;
- snapshot and manifest identities agree;
- symbol matches;
- source is public OHLCV only;
- report-only is true;
- automatic order is false;
- private actual-trade input is false;
- aware UTC `as_of_utc` and `evaluated_at_utc` are present;
- required structure, zone, target, obstruction, volatility, freshness, continuity, reason, and safety fields are present.

Do not recursively search review or history directories.

### History

Read `history-root/latest.json`, then resolve exactly one direct-child immutable `history_*` directory.

Require M-OPS2 v2:

- schema version `macro_structure_history_operation.v2`;
- method version `macro_structure_history_operation.v2`.

Validate:

- latest history ID and artifact directory agree;
- complete M-OPS2 output set exists;
- history JSON, manifest, and latest identity agree;
- symbol matches the selected snapshot;
- manifest remains public-artifact only, report-only, non-private, and non-ordering;
- the selected M-OPS1 run ID is listed in history `source_runs`;
- history `latest_as_of_utc` equals snapshot `as_of_utc`;
- history latest evaluation for that structural checkpoint includes the selected snapshot run.

If the history does not include the selected current snapshot, fail closed with a stable error such as `history_missing_current_snapshot`.

### 15-minute OHLCV

Read one explicit CSV using accepted timestamp semantics.

Require:

- timestamp, open, high, low, close;
- interval is 15m when interval metadata is present;
- symbol matches when symbol metadata is non-empty;
- aware timestamps;
- strictly increasing unique timestamps;
- finite valid OHLC values and valid high/low relationships.

Use only candles whose 15-minute endpoint is at or before snapshot `as_of_utc`.

The final eligible close must match snapshot `current_price` within a small deterministic numeric tolerance. Otherwise fail closed with `snapshot_price_ohlcv_mismatch`.

Do not display candles after the snapshot cutoff.

## Operator hierarchy

The self-contained HTML must display information in this order:

1. status and safety banner;
2. primary 15-minute candlestick chart;
3. reliable support/resistance zones;
4. current structure and price location;
5. next targets and obstruction;
6. volatility, activation, freshness, and continuity;
7. recent chronological changes;
8. evidence details and limitations.

The chart is primary. Raw JSON or tables must not appear before it.

## Primary 15-minute chart

Render one inline SVG with no external JavaScript, image, font, stylesheet, or network dependency.

Default visible window:

- latest 96 eligible closed 15-minute candles;
- use all available eligible candles when fewer than 96 exist.

Required overlays:

- current price line;
- all published high/medium support zones;
- all published high/medium resistance zones;
- nearest reliable support and resistance when present;
- next upside and downside target geometry when present;
- obstruction geometry when represented by a level object.

Deduplicate geometry by stable `level_id` and attach deterministic semantic labels.

Each macro zone label must expose:

- level ID;
- support or resistance role;
- reliability band;
- lifecycle.

Do not fabricate geometry for `none`, `insufficient`, blank, or non-object references.

The surface is macro-only in M-OPS3. It must state visibly that tactical Entry / SL / TP overlays are not included. Any later tactical overlay integration requires a separate contract and must remain visually distinct from macro zones.

## Status and fail-closed display

The following accepted states are valid rendered outcomes and must remain prominent:

- `current`;
- `stale`;
- `continuous`;
- `discontinuous`;
- `ok`;
- `insufficient`;
- `insufficient_history`.

Do not hide weak evidence. Do not convert stale, discontinuous, low-confidence, or insufficient states into positive action wording.

The top banner must show:

- symbol;
- snapshot cutoff UTC and JST;
- evaluation UTC and JST;
- current price;
- structure state;
- price location;
- stale status;
- continuity status;
- source snapshot result status;
- history result status;
- report-only safety boundary.

## Reliable zone evidence

For every displayed zone retain accepted M-OPS1 values only:

- `level_id`;
- original `side`;
- current `role`;
- low/high/center;
- source timeframes;
- first-seen and last-confirmed times;
- touch, rejection, break, and reclaim counts;
- lifecycle;
- reliability score and band;
- distance from price;
- reason codes.

Do not recalculate reliability or lifecycle.

Low-reliability and insufficient levels must not be visually promoted as reliable chart zones. When relevant, list their absence or exclusion in limitations.

## Current structure panel

Show:

- structure state;
- price location and percentile;
- nearest reliable support and resistance;
- next upside and downside targets;
- upside and downside obstruction;
- volatility state;
- expansion risk;
- directional activation.

Use evidence-confidence language only. Directional activation is not execution permission.

## Chronological change panel

Use accepted M-OPS2 v2 outputs. Do not recompute transitions.

Show a deterministic bounded set, preferably the latest 10 relevant rows, including:

- structure/location changes;
- reliability upgrades or downgrades with level ID;
- role changes with level ID;
- lifecycle changes with level ID;
- geometry changes with level ID;
- absence from latest;
- reappearance;
- latest stale or discontinuous reevaluations.

When no matching event exists, display `none`.

The selected snapshot and latest history must remain traceable by run/history IDs.

## Canonical view model

Create a versioned JSON view model, for example:

`macro_structure_operator_artifact.v1`

Minimum top-level fields:

- schema and method version;
- operator artifact ID;
- symbol;
- selected snapshot run and snapshot ID;
- selected history ID;
- snapshot/history/OHLCV fingerprints;
- snapshot cutoff and evaluation times;
- chart model;
- zone model;
- structure panel model;
- freshness and continuity model;
- chronological change model;
- missing/insufficient flags;
- source trace map;
- safety boundary.

Every displayed fact must be traceable to:

- M-OPS1 snapshot or level CSV;
- M-OPS2 history/change artifact;
- explicit 15-minute OHLCV input;
- a deterministic presentation rule.

Do not include private paths, raw exchange rows, future outcomes, or order fields.

## Output contract

Each successful immutable operator directory must contain:

- `macro_structure_operator.html`
- `macro_structure_operator.json`
- `macro_structure_operator.md`
- `run_manifest.json`

Atomically update:

```text
local/reports/macro_structure/operator/latest.json
```

The compact latest summary must include:

- schema and method version;
- operator artifact ID and directory;
- symbol;
- selected snapshot run/snapshot ID;
- selected history ID;
- cutoff and evaluation times;
- current structure/location/status;
- displayed support/resistance counts by band;
- stale and continuity status;
- source digest;
- safety boundary.

The Markdown is a compact human review guide with:

- selected source identities;
- hierarchy order;
- visible status;
- displayed zone summary;
- recent history summary;
- limitations;
- safety boundary.

## Determinism and publication

Artifact identity must use only:

- schema/method versions;
- symbol;
- selected snapshot immutable identity/content hash;
- selected history immutable identity/content hash;
- explicit OHLCV content hash;
- deterministic display contract.

Required:

- stable sorting;
- stable JSON serialization;
- deterministic SVG and HTML;
- complete staging before promotion;
- byte-identical idempotent reuse;
- same-ID differing-byte conflict failure;
- previous valid latest preservation on failure;
- no wall clock;
- no randomness;
- no process ID;
- no file modification time;
- no machine-specific absolute path in generated artifacts.

## Safety and scope

This task is local rendering only.

It does not authorize:

- live fetch;
- notification or mail changes;
- runtime, launchd, plist, cron, or schedule changes;
- production UI integration;
- tactical signal selection;
- scoring, gate, threshold, classifier, or policy changes;
- private/account/position/order endpoints;
- automatic orders;
- `FORMAL_GO`;
- M6;
- `Ver05` promotion.

Do not edit accepted M1, M-OPS1, M-OPS2, notification, production analysis, or runtime source unless a concrete input-contract defect is first reported.

## Default implementation area

- new `src/feedback/macro_structure_operator_artifact.py`;
- `tools/log_feedback.py` for minimal parser/dispatch wiring;
- new focused test module;
- matching CLI tests in `tests/test_log_feedback.py`;
- this active spec for a short factual implementation note;
- one small deterministic fixture helper only when clearly necessary.

The accepted M4 renderer may be read and its pure self-contained SVG/layout patterns reused, but M-OPS3 must not depend on M3, tactical candidates, or signal IDs.

## Focused validation

Cover at minimum:

- exact latest snapshot/history resolution;
- path confinement to direct-child immutable artifacts;
- M-OPS2 v2 requirement;
- history contains current snapshot;
- symbol and source-boundary validation;
- 15m timestamp/interval/symbol/numeric validation;
- no candle after snapshot cutoff;
- current-price and final-close agreement;
- chart-first HTML order;
- deterministic 96-candle window;
- macro zone deduplication and labels;
- high/medium display and no low-confidence promotion;
- target and obstruction handling;
- stale/discontinuous/insufficient visible states;
- chronological event rendering with stable level IDs;
- source trace coverage;
- no tactical or execution implication;
- deterministic repeat;
- same-ID conflict failure;
- publication rollback/latest preservation;
- actual CLI parser/dispatch.

Use one bounded fixture-only smoke. Do not use browser automation, screenshot comparison, live data, full suite, M5, runtime, delivery, or frozen repo.

## Completion

M-OPS3 is complete when the actual CLI produces a deterministic self-contained chart-first local artifact from accepted current snapshot/history and explicit 15-minute OHLCV, all weak/stale/insufficient states remain visible, complete publication is atomic, focused validation passes, and no production or runtime behavior changes.

After M-OPS3 acceptance, M-OPS4 runtime/schedule enablement remains a separate explicit human-approved `RUNTIME_TASK`.

## Bounded implementation note

The bounded implementation adds the local `render-macro-structure-operator` parser route and deterministic report-only artifact publisher without runtime or delivery integration.

FIX-01 extends the accepted chart-first view model and publication identity to `macro_structure_operator_artifact.v2`, including complete high/medium zone evidence, checkpoint/status visibility, categorized M-OPS2 events, and display-level source traceability.
