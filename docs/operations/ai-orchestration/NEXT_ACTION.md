# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-P7-SHADOW-SURFACE-CHECKPOINT-PUSH`
- mode: `CHECKPOINT_PUSH`
- task_type: `GIT CHECKPOINT PUSH ONLY`
- previous_work_id: `BTCFX-20260710-MTP-P7-SHADOW-SURFACE-ACCEPTANCE-FIX-1`
- previous_status: `P7 IMPLEMENTATION ACCEPTANCE FIX COMMITTED / PUSH NONE`

## Goal

Checkpoint push only for the completed P7 operator shadow-surface implementation and its acceptance corrective commit.

Source of truth:

`chatgpt/specs/active/20260710_manual_operator_shadow_surface.md`

The checkpoint push contains the implementation commit plus the corrective commit and performs no source edits. Runtime apply remains blocked until checkpoint push and separate runtime-target verification. The active spec remains active; do not archive it or write local commit hashes here.

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually

Do not change gates, scoring, thresholds, notifications, runtime, launchd, APIs, account/order behavior, secrets, or publish routing.
