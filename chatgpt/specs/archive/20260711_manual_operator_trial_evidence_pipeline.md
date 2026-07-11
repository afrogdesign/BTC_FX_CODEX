# P8 Manual Operator Trial Evidence Pipeline — Active Specification

## Metadata

- work_id: `BTCFX-20260711-MTP-P8-EVIDENCE-PIPELINE`
- status: active / approved for bounded implementation
- phase: P8 human manual trial
- parent operating spec: `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Goal

既存のP2〜P7資産を再利用し、P8を「人間が全件手書きする試験」ではなく、予測・市場結果・実取引を自動照合し、例外だけを人間へ返すevidence pipelineとして実装する。

P8はproduction classifier、gate、threshold、notification triggerを変更しない。

## 2. Product decisions fixed by this spec

1. 市場pathの結果評価はdeterministic systemが行う。
2. 実取引はlocal exchange exportからimportし、episode/linkerで自動照合する。
3. 人間入力はambiguous link、非取引理由、UI confusionなどの例外だけに限定する。
4. AIはweekly qualitative reviewを行うが、数値計算とproduction mutationの主役ではない。
5. P9はproposal-first / human-approvedであり、自動再調整しない。
6. single exampleからclassifierやproduction設定を変更しない。

## 3. Known accepted baseline

Read and reuse these existing modules instead of rebuilding them.

- `src/feedback/manual_actual_trade_importer.py`
- existing manual trade episode builder
- existing manual trade signal/scenario linker
- existing manual trade ground-truth report
- `src/feedback/manual_decision_events.py`
- existing scenario normalizer / coverage builder
- `src/feedback/manual_operator_classifier.py`
- `src/feedback/manual_operator_historical_replay.py`
- P7 shadow-surface adapter and tests

Codex must locate the exact existing episode/linker/report module names from nearby imports/tests only. Broad repo exploration is not allowed.

## 4. Required inputs

The pipeline must accept explicit paths for existing generated artifacts.

Required logical inputs:

- normalized scenarios
- scenario events
- P5 classifications
- signal/candidate context needed by existing replay
- market-path outcomes or existing resolved outcome artifacts

Optional logical inputs:

- manual decision events
- actual trade episodes
- episode-to-signal/scenario links
- actual ground-truth report inputs

Missing optional actual-trade inputs must not fail the proxy trial report. The output must state `actual_evidence_status=missing` or equivalent.

## 5. Required outputs

### 5.1 Trial facts CSV

Preferred path concept:

```text
logs/csv/manual_operator_trial_facts.csv
```

This is generated/local evidence and is not committed by default.

One row represents one selected scenario-side-event evaluation unit.

Minimum logical fields:

- schema_version
- trial_fact_id
- scenario_id
- scenario_event_id
- signal_id
- candidate_id
- event timestamp
- side
- setup family
- regime
- operator class
- classifier method/version
- gate snapshot
- reason/warning/no-trade/risk snapshots
- entry zone / invalidation / TP1 / TP2
- outcome status
- TP1-first / SL-first where available
- MFE / MAE where available
- zone result
- direction result
- comparison label
- actual episode ID if eligible
- actual link confidence
- actual net PnL / R where eligible
- evidence tier
- issue flags

Do not duplicate raw private identifiers or account data.

### 5.2 Human review queue CSV

Preferred path concept:

```text
logs/csv/manual_operator_trial_review_queue.csv
```

Queue only cases requiring human intent or ambiguity resolution.

Minimum categories:

- ambiguous actual-trade link
- competing signal/scenario link
- high-value missed-opportunity proxy without actual trade
- STOP versus opposite-side opportunity conflict
- UI hierarchy confusion candidate
- missing human intent that materially changes evaluation

Each queue row must include a compact question type and safe selectable options. Do not require free-text by default.

### 5.3 Deterministic JSON report

Must include:

- input status/fingerprints
- evaluated cutoff
- row counts
- resolved/unresolved/no_ohlcv/ambiguous counts
- class distribution
- side/regime/setup breakdown
- aligned / too_defensive / too_aggressive / wrong_side counts
- zone useful/failed counts
- STOP useful/false-alarm proxy counts
- actual evidence coverage
- link confidence coverage
- issue flag counts
- review queue size
- P9 readiness fields
- safety boundary

### 5.4 Markdown operator report

Must explain, in human-readable language:

- what was evaluated
- what remains unresolved
- strongest recurring issues
- proxy-only versus actual-backed evidence
- Long/Short separation
- P9 readiness and missing requirements
- no automatic tuning statement

## 6. Deterministic comparison semantics

Use existing outcome semantics where available. Do not create a conflicting second definition of TP1-first, SL-first, MFE, MAE, scenario selection, or actual trade eligibility.

Minimum comparison labels:

- `aligned`
- `too_defensive`
- `too_aggressive`
- `wrong_side`
- `zone_useful`
- `zone_failed`
- `stop_useful_proxy`
- `stop_false_alarm_proxy`
- `big_chance_failed` only when existing evidence supports that named auxiliary hypothesis
- `unresolved`

A row may carry more than one issue flag, but exactly one primary comparison status should be selected deterministically.

The implementation must document precedence and test it.

## 7. Side-specific STOP evidence

Do not change P5 classifier behavior in P8.

P8 must instead measure the hypothesis:

```text
global no-trade STOP may suppress a valid opportunity on the opposite side
```

Required report fields or issue flags:

- global STOP present
- candidate side
- opposite-side candidate availability
- opposite-side zone outcome
- whether the opposite side would have met current B/C non-STOP evidence except for the global STOP

This is offline evidence only. It must not authorize side-specific production STOP behavior.

## 8. Actual trade eligibility

Use episode-level evidence as the primary actual trade unit.

Do not count fills as independent trades.

Only eligible link confidence may enter actual-backed aggregate metrics:

- high
- medium
- manual-confirmed equivalent if supported by the existing schema

Low or ambiguous links remain descriptive and enter the review queue.

Actual trade absence does not prove skip/watch/no-view intent.

## 9. Issue register output

The P8 report must emit or update a deterministic issue summary view. It does not need to mutate a handwritten source document automatically.

Required initial issue keys:

- `P8-ISSUE-001_GLOBAL_STOP_MASKS_SIDE_OPPORTUNITY`
- `P8-ISSUE-002_MAIN_VS_BIG_CHANCE_HIERARCHY`
- `P8-ISSUE-003_RAW_CLASSIFIER_PAYLOAD_EXPOSED`
- `P8-ISSUE-004_STOP_CARD_SIDE_IDENTITY`

Minimum fields:

- issue key
- first/last evidence timestamp
- occurrence count
- resolved evidence count
- actual-backed count
- affected side/regime/setup counts
- severity
- evidence confidence
- tuning eligibility
- status

UI issues may be seeded as known observations but must be clearly separated from automatically detected trading-performance issues.

## 10. P9 readiness computation

Report both initial and practical readiness.

Initial readiness minimum:

- resolved scenario/decision-equivalent events >= 100
- actual entry episodes >= 30
- A/B/C/STOP split available
- Long/Short split available
- unresolved/no_ohlcv separated
- eligible actual link policy enforced
- reproducible version/cutoff/fingerprint metadata

Practical readiness minimum:

- resolved scenario/decision-equivalent events >= 200
- actual entry episodes >= 50
- Long/Short/regime/setup segmentation available
- newest validation window exists
- explicit human approval remains required

Do not encode PF/R targets as automatic pass-to-production. They are report targets only.

## 11. CLI

Add one bounded CLI route under the existing feedback CLI, following current naming conventions.

Suggested semantic name:

```text
build-manual-operator-trial-report
```

The exact command name may follow an established nearby pattern.

Required behavior:

- explicit input/output paths
- `--dry-run`
- `--replace-output` or equivalent existing transaction policy
- compact `--stdout-json`
- no raw rows in stdout
- deterministic output
- atomic multi-output replacement
- safe failure on schema mismatch, identity conflict, future context, invalid numeric/timestamp, output transaction failure

## 12. Tests

Add targeted tests covering at least:

1. fully resolved proxy-only trial facts
2. missing optional actual evidence
3. eligible actual episode/link inclusion
4. low/ambiguous link excluded from actual aggregate and queued
5. no_ohlcv/unresolved excluded from win-loss metrics
6. duplicate scenario/candidate evidence not double counted
7. future outcome leakage rejected
8. deterministic comparison precedence
9. global STOP/opposite-side opportunity issue flag
10. P9 initial readiness false below thresholds
11. P9 initial readiness true at thresholds using fixtures
12. atomic output rollback
13. dry-run writes nothing
14. privacy-safe stdout and generated summaries
15. exact rerun determinism/idempotency

Reuse sanitized fixtures. Do not use real exchange exports.

## 13. Documentation updates in implementation task

Update only the minimum necessary docs:

- CLI/help documentation if current project convention requires it
- this active spec only for implementation notes if necessary

Do not update broad orchestration state in the source implementation commit. Closeout is a separate review decision.

## 14. Prohibited

- no P5 classifier threshold change
- no side-specific STOP production implementation
- no gate/scoring change
- no notification/mail change
- no public HTML redesign in this task
- no runtime restart
- no exchange API
- no account/order endpoint
- no secrets
- no raw export commit
- no `paper_positions.csv` integration
- no automatic recommendation application
- no P9 implementation in the same task

## 15. Validation

Run the targeted new trial-pipeline tests plus directly affected existing feedback tests only.

```text
./.venv312/bin/python -m unittest <targeted test modules>
git diff --check
```

Run the relevant CLI once with sanitized fixtures if a CLI route is added.

## 16. Completion criteria

P8 implementation is complete when:

1. existing P2-P7 evidence is joined without redefining accepted semantics.
2. prediction versus market outcome is evaluated automatically.
3. eligible actual trades are incorporated automatically.
4. human review queue contains only ambiguous/intent-dependent exceptions.
5. current known issues are measurable in the generated report.
6. P9 readiness is deterministic and reproducible.
7. no production behavior changes.
8. tests and diff check pass.
9. implementation is locally committed.
10. this spec remains active until ChatGPT review and closeout.


---

## Closeout — 2026-07-11

- status: completed / accepted / archived
- initial implementation commit: `850ab24`
- correction commits: `759370b`, `29e0a39`
- acceptance-test commit: `0397fa8`
- reported final validation: `80` directly affected tests passed; P8 acceptance module `23` tests; `git diff --check` passed
- accepted capabilities:
  - deterministic prediction / market-path / eligible actual-trade evidence joining
  - P6 outcome semantics preserved separately from P8 comparison semantics
  - exception-only human review queue
  - global no-trade STOP versus opposite-side B/C counterfactual measurement using the accepted P5 classifier
  - unique episode-based actual evidence
  - reproducibility fingerprints and method metadata
  - initial/practical P9 readiness reporting
  - atomic output replacement, rollback, dry-run, deterministic rerun, and privacy-safe summaries
- safety unchanged: report-only / not `FORMAL_GO` / no automatic order / human decides manually
- production classifier, gates, thresholds, notification behavior, runtime, API, account, and order behavior were not changed
- P8 implementation is complete; P8 operating evidence collection continues
- P9 remains blocked until readiness evidence and explicit human approval
