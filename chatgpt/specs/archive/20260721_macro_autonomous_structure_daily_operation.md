# Macro Autonomous Structure Daily Operation

## Metadata

- work_id: `BTCFX-20260721-MACRO-AUTONOMOUS-STRUCTURE-DAILY-OPERATION`
- phase: `M-OPS1`
- status: approved for bounded source implementation
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- parent_plan: `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`
- accepted_foundation: M1, M2, M3, M4, M5
- safety: report-only / not `FORMAL_GO` / no automatic order / no runtime apply in this task

## 1. Objective

Implement one dedicated report-only command that automatically builds a current higher-timeframe structure snapshot from public market data and publishes confidence-labelled support/resistance artifacts.

This task operationalizes already accepted M1/M4 capabilities. It does not wait for M5 challenger eligibility and does not require private actual-trade inputs.

The observable result must answer:

1. What higher-timeframe structure is knowable now?
2. Which support and resistance zones are currently defensible?
3. How reliable is each zone based only on prior interactions?
4. Where is current price relative to those zones?
5. What is the first reliable target and intervening obstruction on each side?
6. Is evidence current, stale, discontinuous, or insufficient?

## 2. Non-goals

This task must not:

- edit the frozen runtime repo;
- edit launchd, plist, cron, installed schedules, or runtime startup files;
- send mail or notifications;
- alter live notification selection;
- alter production structural-priority, Big Chance, scoring, thresholds, gates, or classifiers;
- run M5 or create an M6 proposal;
- use private exchange, account, position, order, or actual-trade inputs;
- create automatic orders or entry permission;
- claim certainty or profitability;
- replace accepted M1 reliability semantics with a new score.

## 3. Accepted logic to reuse

Reuse accepted source or pure helpers from:

- `src/feedback/macro_structure_volatility_replay.py`
- accepted public market-data fetch paths
- accepted M4 chart-first/view-model ideas when safe

Do not duplicate or fork the following semantics:

- event-time pivot confirmation
- stable level identity
- level lifecycle
- prior-only reliability
- structure/location classification
- volatility state
- expansion-versus-direction separation
- target and obstruction
- fail-closed data-quality behavior

If the accepted implementation lacks a reusable current-snapshot callable, factor the smallest pure helper without changing replay outputs or accepted policy behavior.

## 4. Command contract

Add one dedicated report-only route named:

```text
run-macro-structure-daily
```

Preferred location is the existing feedback CLI unless a small dedicated wrapper is cleaner while still reusing accepted implementation.

Required behavior:

- explicit symbol and public timeframe configuration through accepted defaults or explicit arguments;
- obtain bounded public 15m, 1h, and 4h OHLCV through the accepted fetcher;
- use latest eligible closed candles only;
- derive one deterministic current snapshot cutoff;
- run accepted structure/reliability logic;
- publish one complete date/time-scoped artifact set;
- atomically update a compact latest summary;
- output compact JSON status to stdout;
- preserve previous complete artifacts on failure.

The command must not scan arbitrary directories or infer private files.

## 5. Output root

Use:

```text
local/reports/macro_structure/
```

Generated files remain local and uncommitted.

A successful run creates one timestamp- or date-scoped directory. Minimum outputs:

- `macro_structure_snapshot.json`
- `macro_structure_snapshot.md`
- `macro_level_reliability.csv`
- `run_manifest.json`

A self-contained HTML artifact may be included only if it remains bounded and reuses accepted M4 safety rules. HTML is desirable but not required for M-OPS1 acceptance if adding it would materially enlarge the task.

Update atomically:

- `local/reports/macro_structure/latest.json`

`latest.json` is a compact pointer/summary, not a copy of raw rows.

## 6. Snapshot schema

Minimum top-level fields:

- `method_version`
- `schema_version`
- `snapshot_id`
- `as_of_utc`
- `as_of_jst`
- `symbol`
- `current_price`
- `input_coverage`
- `input_fingerprints`
- `structure_state`
- `price_location`
- `location_percentile`
- `nearest_reliable_support`
- `nearest_reliable_resistance`
- `support_zones`
- `resistance_zones`
- `next_upside_target`
- `next_downside_target`
- `upside_obstruction`
- `downside_obstruction`
- `volatility_state`
- `expansion_risk`
- `directional_activation`
- `data_quality_status`
- `stale_status`
- `reason_codes`
- `safety_boundary`

Each published zone must include:

- stable `level_id`
- side and current role
- low, high, and center
- source timeframes
- first seen and last confirmed times
- touch, rejection, break, acceptance, and reclaim evidence available at cutoff
- reliability score
- reliability band: `high`, `medium`, `low`, or `insufficient`
- distance from current price in percent and event-time ATR when available
- reason codes

Do not publish a high/medium zone when required geometry or prior-only reliability is unavailable.

## 7. Current snapshot boundary

The run is a current market snapshot, not a signal outcome replay.

Rules:

- choose one deterministic cutoff from the latest common closed-candle coverage;
- no candle later than the cutoff may affect structure or reliability;
- future outcomes are not required;
- no synthetic favorable interaction may be created;
- no level confirmed after the cutoff may be shown;
- current-only snapshot identity must not collide with historical signal IDs;
- if accepted replay helpers require an event record, use an explicit current-snapshot adapter with tested no-future semantics rather than writing fake trading facts.

## 8. Reliability and fail-closed rules

Nearest is not equivalent to reliable.

Required behavior:

- preserve accepted prior-only reliability calculations;
- sort zones deterministically by side, reliability, structural relevance, and distance using an explicit order;
- expose at most a bounded operator-facing set while retaining the complete generated level CSV;
- mark missing, stale, discontinuous, or one-sided evidence explicitly;
- return a successful `insufficient` snapshot when market data is valid but no defensible structure exists;
- return failure only for malformed inputs, fetch/coverage failure, publication failure, or contract violation.

A valid `insufficient` result is not an implementation failure.

## 9. Human-readable report

The Markdown must begin with a compact operator summary:

- snapshot time
- current structure
- current location
- high/medium support zones
- high/medium resistance zones
- first target and obstruction on both sides
- volatility and activation state
- stale/insufficient warning

Then include the evidence breakdown and limitations.

Labels must state:

- evidence confidence, not execution permission
- report-only
- human decides manually

## 10. Atomicity and privacy

Required:

- temporary staging before promotion;
- complete-set replacement only;
- previous successful latest summary preserved on failure;
- no raw private path or secret in stdout or latest summary;
- no account, order, position, or actual-trade data;
- deterministic sorting and stable JSON serialization;
- generated outputs ignored/uncommitted.

## 11. Allowed implementation files

Default bounded scope:

- `src/feedback/macro_structure_volatility_replay.py`
- new `src/feedback/macro_structure_daily_operation.py`
- `tools/log_feedback.py`
- optional new `tools/run_macro_structure_daily.py`
- new `tests/test_macro_structure_daily_operation.py`
- `tests/test_macro_structure_volatility_replay.py` only for required helper regressions
- `tests/test_log_feedback.py` only for parser/dispatch coverage
- this active spec for short implementation notes

Do not edit P8 classifier/evaluator semantics, production analysis, notification, mail, deploy, runtime, account, position, or order files.

If another file is required, stop and report the exact reason unless it is a clearly matching small test fixture.

## 12. Required focused tests

Cover at minimum:

- latest common closed-candle cutoff;
- no future-confirmed pivot or level use;
- accepted stable level identity and prior-only reliability reuse;
- high/medium/low/insufficient classification;
- nearest-but-unreliable level is not promoted;
- mirrored support/resistance handling;
- deterministic bounded zone ordering;
- current price location and target/obstruction;
- stale and discontinuous coverage;
- valid insufficient snapshot;
- public-only input boundary;
- no private/actual-trade dependency;
- atomic complete-set publication and rollback;
- deterministic repeat output for fixed inputs;
- compact latest summary;
- actual CLI parser and dispatch;
- no mail, notification, runtime, gate, scoring, classifier, or order mutation.

## 13. Validation budget

Run once after implementation:

```text
matching daily-operation unittest module
matching M1 regression subset
matching CLI parser/dispatch tests
one small deterministic fixture smoke
scoped git diff --check
```

Do not run:

- full test suite;
- M5 31-unit bundle;
- repeated public fetch loops;
- installed runtime or schedule;
- frozen runtime repo;
- mail or notification tests.

One bounded live-public-data smoke may be proposed only after deterministic tests pass and ChatGPT explicitly approves it. Fixture evidence is sufficient for the implementation task unless the source contract cannot otherwise be verified.

## 14. Completion criteria

M-OPS1 source is complete when:

1. the command exists and is report-only;
2. it needs no private actual-trade input;
3. it builds one current cutoff-safe snapshot;
4. it publishes confidence-labelled support/resistance zones;
5. it fails closed to `insufficient` when appropriate;
6. it creates the complete local artifact set atomically;
7. latest summary is compact and deterministic;
8. focused tests and one fixture smoke pass;
9. no runtime, notification, mail, policy, gate, or order behavior changes;
10. one local source commit and compact Codex report are produced.

## 15. Next phases

After ChatGPT accepts source and fixture evidence:

- M-OPS2 adds/validates chronological history continuity and reliability change reporting if not already complete;
- M-OPS3 produces the chart-first operator artifact;
- M-OPS4 is a separate explicit runtime/schedule task;
- M5 refresh remains a later periodic improvement task and does not block these phases.
