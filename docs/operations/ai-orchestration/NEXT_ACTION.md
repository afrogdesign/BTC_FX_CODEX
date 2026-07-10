# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-P8-HUMAN-MANUAL-TRIAL-DECISION`
- mode: `HUMAN_CHECK`
- task_type: `PRODUCT / TRADING / SAFETY DECISION`
- previous_work_id: `BTCFX-20260710-MTP-P7-CLOSEOUT`
- previous_status: `P7 COMPLETE / CHECKPOINTED / RUNTIME-APPLIED`

## Current state

P7 operator shadow surface is complete, accepted, checkpointed, and runtime-applied.

Archived source of truth:

`chatgpt/specs/archive/20260710_manual_operator_shadow_surface.md`

No P8 active spec exists.

## Human decision required

Before any executable P8 task, the human must approve a bounded manual-trial contract covering:

- trial objective and duration
- which `A_FORMAL`, `B_CHECK_15M`, `C_WATCH_ZONE`, and `STOP_OR_EXIT` observations are included
- required 15-minute chart checks
- how human decisions, skips, exits, avoided losses, and missed opportunities are recorded
- success, failure, and stop criteria
- privacy boundary for manual records
- confirmation that no automatic order or unapproved live extra mail is introduced

## Prohibited until approval

- no P8 source implementation
- no production gate, scoring, or threshold tuning
- no automatic order
- no live extra notification sending
- no runtime or launchd change
- no API, account, private endpoint, or order endpoint work
- no `paper_positions.csv` integration
- no new active spec

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually

Do not include a Codex implementation instruction inside NEXT_ACTION.
