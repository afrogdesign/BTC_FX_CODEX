# NEXT_ACTION

- current_work_id: `BTCFX-20260712-P8-TURNING-VOLATILITY-PRECURSOR-REPLAY`
- mode: `BOUNDED_CODEX`
- task_type: `P8 OFFLINE EVIDENCE / TURNING AND VOLATILITY PRECURSOR REPLAY`
- previous_work_id: `BTCFX-20260712-P8-DAILY-CYCLE-SCHEDULED-VERIFY`
- previous_status: `DONE / VERIFIED / ARCHIVED`

## Current state

P8 evidence collection remains active. The daily operating-cycle automation completed its first scheduled 11:30 JST run successfully on 2026-07-12.

Verified scheduled result:

- candidate rows: 207
- candidate signals: 107
- scenarios: 84
- resolved: 74
- unresolved: 10
- no-OHLCV: 0
- ISSUE-001 qualified rows: 38
- P9 readiness: false
- error codes: none

The completed automation spec is archived at:

```text
chatgpt/specs/archive/20260711_p8_daily_operating_cycle_automation.md
```

## New observed issue

The 2026-07-12 07:05 JST signal remained strongly Long-biased and sent no notification, despite reversal-risk and major-resistance rejection evidence before a material downward move. A later Short attention arrived after the main move.

This is recorded as:

```text
P8-ISSUE-008 — Turning / volatility precursor alert is late or absent
```

This single case is not sufficient for production tuning.

## Current exact next action

HUMAN_CHECK / ChatGPT review of corrected turning / volatility precursor replay.

- corrected replay is recorded in local generated outputs and the archived spec
- pre-correction metrics are invalid and discarded
- recommendation is `continue_shadow_collection`; no production proposal is authorized
- no further replay or public fetch occurs without a separately approved task

## P9 entry rule

P9 remains blocked.

This replay may conclude only:

- `insufficient_evidence`
- `continue_shadow_collection`
- `eligible_for_notification_proposal`

Even an eligible result authorizes only a separate proposal. It does not authorize production code or configuration changes.

## Active sources of truth

- `chatgpt/specs/archive/20260712_turning_volatility_precursor_replay.md`
- `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md`
- `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`

## Prohibited

- no scoring or market-map tuning
- no threshold or gate change
- no notification trigger or mail behavior change
- no runtime or launchd change
- no automatic tuning
- no exchange API, private, account, or order endpoint
- no raw export commit
- no `paper_positions.csv` integration
- no automatic order

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually
