# NEXT_ACTION

- current_work_id: `BTCFX-20260710-MTP-P7-SHADOW-SURFACE-CHECKPOINT-PUSH`
- mode: `CHECKPOINT_PUSH`
- task_type: `GIT CHECKPOINT PUSH ONLY`
- previous_work_id: `BTCFX-20260710-MTP-P7-SHADOW-SURFACE-IMPLEMENTATION`
- previous_status: `P7 IMPLEMENTATION COMMITTED / PUSH NONE`

## Goal

Checkpoint push only for the completed P7 operator shadow-surface implementation.

Source of truth:

`chatgpt/specs/active/20260710_manual_operator_shadow_surface.md`

This next task performs no source edits. Runtime apply remains blocked until checkpoint push and separate runtime-target verification.

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually

Do not change gates, scoring, thresholds, notifications, runtime, launchd, APIs, account/order behavior, secrets, or publish routing.
