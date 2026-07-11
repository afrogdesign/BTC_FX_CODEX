# NEXT_ACTION

- current_work_id: `BTCFX-20260711-MTP-P8-OPERATING-EVIDENCE-COLLECTION`
- mode: `HUMAN_CHECK`
- task_type: `P8 OPERATING TRIAL / EVIDENCE COLLECTION`
- previous_work_id: `BTCFX-20260711-MTP-P8-EVIDENCE-PIPELINE-ACCEPTANCE-TESTS`
- previous_status: `DONE / ACCEPTED / ARCHIVED`

## Current state

P8 evidence-pipeline implementation is complete and accepted.

Accepted implementation chain:

```text
850ab24
759370b
29e0a39
0397fa8
```

The implementation spec is archived at:

```text
chatgpt/specs/archive/20260711_manual_operator_trial_evidence_pipeline.md
```

`chatgpt/specs/active/` is intentionally empty except for `.gitkeep`.

## What P8 now does

- evaluates market-path outcomes deterministically
- preserves P6 outcome semantics separately from P8 comparison status
- joins eligible actual trade episodes using high/medium link evidence
- excludes unresolved, no-OHLCV, low-confidence, and ambiguous evidence from performance claims
- measures global no-trade STOP versus opposite-side B/C opportunities offline
- produces an exception-only human review queue
- reports reproducibility metadata and P9 readiness
- never applies automatic tuning

## Current exact next action

Operate P8 through `run-p8-operating-cycle` and collect evidence. Do not manually reconstruct candidate, signal, OHLCV, P4, P5, or P8 lineage. Do not begin P9 implementation yet.

The corrected baseline was recorded on 2026-07-11 using current-candidate lineage and fresh public 15-minute OHLCV. On the next meaningful evidence window, run the single runner with the same deterministic inputs; add episode/link inputs only when both validate. Compare coverage, ISSUE-001, and readiness metrics; do not modify thresholds, gates, classifier behavior, notifications, runtime, or orders.

## P9 entry rule

P9 remains blocked until the P8 report demonstrates the required readiness evidence.

Initial proposal eligibility requires at least:

- 100 resolved events
- 30 unique eligible actual trade episodes
- all four operator classes represented
- Long and Short represented
- non-empty regime and setup segmentation
- reproducibility metadata present

Practical readiness also requires a distinct validation window and explicit human approval.

A readiness result authorizes only a P9 proposal. It never authorizes production changes.

## Active sources of truth

- `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md`
- `chatgpt/specs/archive/20260711_manual_operator_trial_evidence_pipeline.md`

## Prohibited

- no automatic tuning
- no P5 classifier mutation
- no threshold, scoring, or gate change
- no notification or mail behavior change
- no runtime or launchd change
- no exchange API, private, account, or order endpoint
- no secrets or raw exchange export commit
- no `paper_positions.csv` integration
- no automatic order

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually
