# P8 Operating Cycle Runner — Active Specification

## Metadata

- work_id: `BTCFX-20260711-MTP-P8-OPERATING-CYCLE-RUNNER`
- status: completed / accepted by bounded validation
- phase: P8 operating evidence collection
- parent operating spec: `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`
- accepted corrected baseline documentation commit: `b199522`
- accepted P5 structured-level fix commits: `00c227d`, `0bd5d76`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Goal

Add one deterministic local CLI, `run-p8-operating-cycle`, that executes the accepted P8 evidence cycle without manually reconstructing lineage. The runner is report-only, never applies tuning, and keeps the accepted P4/P5/P8 semantics as the only decision source.

## 2. Inputs and options

The command accepts `--date YYYYMMDD`, `--candidates`, `--signal-context`, `--ohlcv`, `--output-root`, optional `--decision-events`, paired `--actual-episodes`/`--actual-links`, `--fetch-public-ohlcv`, `--ohlcv-limit`, `--max-ohlcv-lag-minutes`, `--dry-run`, `--replace-output`, and `--stdout-json`. Defaults refer to the current candidate source, `trades.csv`, and the existing active-plan OHLCV path. Actual episode/link inputs are supplied together or omitted together; raw exchange exports and `paper_positions.csv` are never read.

## 3. Ordered stages

Each cycle selects and sorts current candidate rows, selects only referenced signal rows while preserving structured major-level JSON, validates fresh monotonic 15-minute OHLCV, builds intraperiod outcomes, calls the accepted scenario normalizer, calls the accepted P5 classifier, and calls the accepted P8 trial-evidence builder. No stage is invoked through a shell subprocess, and no P4/P5/P8 rule is reimplemented.

## 4. Lineage and freshness

Candidate IDs and supplied values remain unchanged. Candidates must be within the OHLCV window or no more than the configured lag beyond the newest closed candle; a larger gap fails closed. Signal IDs must be present, required P5 headers must exist, structured major-level objects must remain intact, exact duplicate identities are accepted, and conflicts or missing referenced signals fail closed. Every outcome, scenario event, classification, and selected trial fact must resolve to the preceding stage identity. Source fingerprints and candidate/OHLCV min/max timestamps are recorded.

## 5. Transaction and outputs

All candidate slice, signal-context slice, intraperiod outcome, scenario, event, classifier CSV/JSON/Markdown, trial facts, exception queue, cycle manifest, and compact summary outputs are written beneath a temporary cycle directory. They are promoted as one rollback-safe transaction only after all stages, identities, manifests, and serializations validate. Existing outputs require `--replace-output`; `--dry-run` leaves no final or temporary residue.

## 6. Manifest and privacy

The manifest records schema/method versions, report date, generated timestamp, source/output SHA-256 fingerprints, freshness, stage statuses, counts, class/side/comparison distributions, ISSUE-001, actual-evidence status, review queue, P9 readiness, `no_automatic_tuning: true`, and the safety boundary. Compact stdout JSON contains only counts, statuses, fingerprints, and relative output names. It contains no rows, candle payloads, structured-level payloads, notes, private paths, or identifiers.

## 7. Public fetch boundary

Public OHLCV is fetched only when `--fetch-public-ohlcv` is explicit, through the existing public market-data route. Explicit OHLCV input never calls the network. No account, private, order, mail, runtime, notification, gate, scoring, or threshold behavior is changed.

## 8. Validation contract

Expected input and freshness failures return a compact non-traceback JSON error. Atomic replacement failure restores every prior output. A successful summary contains resolved/unresolved/no-OHLCV, A/B/C/STOP, Long/Short, comparison, actual-evidence, ISSUE-001, review queue, and initial/practical P9 readiness metrics. P9 remains blocked until its existing evidence thresholds and explicit human approval are satisfied.

## 9. Acceptance record

Implementation uses `src/feedback/manual_operator_operating_cycle.py`, the bounded `tools/log_feedback.py` route, and `tests/test_manual_operator_operating_cycle.py`. Local no-fetch smoke uses the accepted corrected baseline inputs.

### Completion record

- implementation: `src/feedback/manual_operator_operating_cycle.py`
- CLI route: `run-p8-operating-cycle`
- targeted tests: 26 operating-cycle tests; 25 P5 tests; 23 P8 tests; 63 directly affected P4/intraperiod tests
- local smoke: pass with corrected baseline counts (206 candidates, 108 signals, 97 trial facts, 84 resolved, no-OHLCV 0)
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually
- production classifier, gates, thresholds, notification, runtime, and order behavior: unchanged
- implementation commit: recorded by the closeout commit
