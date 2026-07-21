# Macro Structure Chronological History and Continuity

## Metadata

- work_id: `BTCFX-20260721-MACRO-STRUCTURE-CHRONOLOGICAL-HISTORY-CONTINUITY`
- phase: `M-OPS2`
- status: approved for bounded source implementation
- accepted_input_checkpoint: `89bd338`
- accepted_input_command: `run-macro-structure-daily`
- parent_plan: `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- safety: report-only / human-decided / no runtime apply

## Objective

Build one deterministic chronological rollup from complete immutable M-OPS1 runs. The result must make stable level identity, reliability changes, role/lifecycle changes, absence/reappearance, snapshot changes, stale state, and continuity auditable without changing M1 or M-OPS1 semantics.

## Input contract

Default snapshot root:

```text
local/reports/macro_structure/
```

Read only direct child directories named `run_*` containing:

- `macro_structure_snapshot.json`
- `macro_structure_snapshot.md`
- `macro_level_reliability.csv`
- `run_manifest.json`

Do not recursively scan review roots, history output, or unrelated directories.

Accept an explicit symbol, defaulting to `BTC_USDT`. Do not combine symbols.

Validate each included run:

- directory name, `run_id`, and `snapshot_id` agree;
- symbol matches;
- required files are complete and readable;
- schema/method versions and aware timestamps are present;
- manifest declares public OHLCV source and report-only behavior;
- level CSV contains accepted identity, lifecycle, evidence, and reliability fields.

A malformed eligible `run_*` is a contract failure. Preserve the previous complete history and latest pointer on failure.

## Command

Add:

```text
run-macro-structure-history
```

Minimum arguments:

- `--snapshot-root`
- `--output-root`
- `--symbol`
- `--stdout-json`

Default output root:

```text
local/reports/macro_structure/history/
```

The operation must never edit M-OPS1 source runs.

## Evaluation runs and structural checkpoints

Record every valid run in deterministic order:

1. `as_of_utc`
2. `evaluated_at_utc`
3. `run_id`

Multiple runs may represent the same market-data checkpoint with different freshness evaluation times. Define structural checkpoint identity from:

- symbol
- `as_of_utc`
- M1 method version
- input fingerprints

Runs sharing that identity are reevaluations. Keep all in evaluation history, but emit structure and level transitions only once per structural checkpoint. Select the canonical structural source by earliest `evaluated_at_utc`, then `run_id`.

## Level continuity

For each canonical checkpoint, retain complete accepted level fields including:

- `level_id`, original side, current role
- geometry and source timeframes
- first-seen and last-confirmed times
- touch, rejection, break, and reclaim evidence
- lifecycle
- reliability score and band
- distance and reason fields

Compare a level only with its previous observation for the same symbol and `level_id`.

Expose:

- first observation
- continued
- absent from checkpoint
- reappeared
- reliability score delta
- band transition
- role transition
- lifecycle transition
- evidence-count deltas
- geometry-change indicator

Absence does not prove permanent retirement. Use `absent_from_checkpoint` and `absent_from_latest`; use `reappeared` when applicable. Report retirement as `not_established` unless an accepted source field explicitly establishes it.

Do not recalculate reliability, lifecycle, role, or geometry.

## Snapshot changes

For consecutive canonical checkpoints expose changes in:

- structure state and price location
- location percentile and current price
- nearest support/resistance IDs
- target and obstruction IDs
- volatility, expansion risk, and activation
- stale, continuity, and data-quality status
- reliability-band counts

A first checkpoint has no prior transition. A valid history with one checkpoint succeeds with `insufficient_history`.

## Outputs

Each successful rollup creates one immutable history directory with:

- `macro_structure_history.json`
- `macro_structure_history.md`
- `macro_snapshot_history.csv`
- `macro_level_history.csv`
- `macro_structure_changes.csv`
- `run_manifest.json`

Atomically update:

```text
local/reports/macro_structure/history/latest.json
```

The compact latest summary must include history ID, symbol, source counts, evaluation count, checkpoint count, first/latest cutoff, latest evaluation, latest structure/location/status, reliability-band counts, continuity/result status, source digest, and safety boundary.

## Determinism and no-future boundary

- Recompute an auditable rollup from explicit immutable inputs; do not create a mutable learning database.
- History identity uses stable versions, symbol, and ordered validated source identities or hashes.
- Sorting and serialization are deterministic.
- Stage complete output before promotion.
- Identical existing output is reusable; conflicting same-ID output fails closed.
- Preserve previous `latest.json` on failure.
- Each checkpoint row comes only from that checkpoint's snapshot and level CSV.
- Later checkpoints must not rewrite earlier role, band, lifecycle, geometry, or evidence.
- A multi-date fixture must prove earlier checkpoint rows remain unchanged after adding a later checkpoint.

## Scope

Default implementation area:

- new `src/feedback/macro_structure_history_operation.py`
- `tools/log_feedback.py`
- new `tests/test_macro_structure_history_operation.py`
- matching M-OPS2 CLI tests in `tests/test_log_feedback.py`
- this spec for a short factual implementation note
- one small deterministic fixture helper when needed

Do not edit accepted M1 or M-OPS1 source unless an input-contract defect is demonstrated and reported first. Do not change runtime, delivery, production policy, or execution behavior.

## Required focused tests

Cover:

- direct-child complete-run discovery and validation;
- symbol isolation;
- chronological evaluation ordering;
- structural checkpoint deduplication for freshness-only reevaluations;
- stable level identity;
- reliability upgrade/downgrade;
- role/lifecycle transitions;
- absence and reappearance without invented retirement;
- evidence deltas;
- structure/location/target/obstruction changes;
- stale and discontinuous history;
- one-checkpoint `insufficient_history`;
- deterministic repeat and no-future multi-date behavior;
- malformed/incomplete input failure;
- atomic publication and previous-latest preservation;
- compact latest summary;
- actual CLI parser and dispatch;
- report-only public-artifact boundary.

## Validation budget

Run once:

```text
matching history-operation unittest module
matching M-OPS2 CLI tests
one bounded deterministic multi-date fixture smoke
task-scoped git diff --check
```

Do not run full suite, live public fetch, M5, broad replay, installed runtime, or frozen runtime repo.

## Completion

M-OPS2 is complete when the command consumes only complete M-OPS1 artifacts, distinguishes evaluations from structural checkpoints, reports deterministic chronological level and snapshot changes, safely handles insufficient history, atomically publishes complete history outputs, passes focused validation, and produces one local source commit.

## Implementation note

The bounded implementation adds `run-macro-structure-history` as a report-only direct-child M-OPS1 artifact rollup with deterministic continuity and atomic publication.

After acceptance, M-OPS3 connects the accepted snapshot and history summary to a chart-first local operator artifact. Runtime enablement remains a separate approval task.
