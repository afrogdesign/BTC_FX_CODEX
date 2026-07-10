# NEXT_ACTION

- current_work_id: `BTCFX-20260711-MTP-P8-EVIDENCE-PIPELINE`
- mode: `BOUNDED_CODEX`
- task_type: `P8 SOURCE IMPLEMENTATION / REPORT-ONLY`
- previous_work_id: `BTCFX-20260710-MTP-P8-HUMAN-MANUAL-TRIAL-DECISION`
- previous_status: `PRODUCT DECISION COMPLETE / P8 CONTRACT APPROVED`

## Current state

P7 operator shadow surface is complete, checkpointed, and runtime-applied.

P8 product decision is now fixed:

- P8 is not full manual logging.
- market-path outcomes are evaluated automatically.
- actual trades are imported from local exchange exports and linked automatically.
- human input is limited to ambiguous intent and exceptional cases.
- AI explains and proposes; it does not automatically mutate production behavior.
- P9 remains proposal-first and requires explicit human approval.

## Active sources of truth

Operating specification:

`docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`

Issue register:

`docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md`

Active implementation specification:

`chatgpt/specs/active/20260711_manual_operator_trial_evidence_pipeline.md`

## Next exact task

Implement the bounded P8 evidence pipeline described by the active specification.

The implementation must:

- reuse P2-P7 accepted evidence semantics
- build deterministic trial facts and a human exception queue
- compare prediction, market-path outcome, and eligible actual trades
- measure the global-STOP/opposite-side-opportunity hypothesis without changing classifier behavior
- produce reproducible P9 readiness fields
- keep all outputs report-only

## Prohibited

- no P5 classifier threshold change
- no production side-specific STOP change
- no gate/scoring change
- no notification/mail behavior change
- no public HTML redesign in the P8 source task
- no runtime or launchd change
- no exchange API, account, private, or order endpoint
- no secrets or raw export commit
- no `paper_positions.csv` integration
- no automatic recommendation application
- no P9 implementation in the same task

## Validation

```text
./.venv312/bin/python -m unittest <targeted P8 and directly affected feedback tests>
<relevant sanitized CLI smoke once>
git diff --check
```

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually
