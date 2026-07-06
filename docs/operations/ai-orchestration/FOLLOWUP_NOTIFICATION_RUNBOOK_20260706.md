# FOLLOWUP_NOTIFICATION_RUNBOOK_20260706

## Purpose

Followup notifications cover the gap where a prior manual-trading notice had a visible validity window but no forced reevaluation after expiry or thesis weakening.

## Why this was added

The system now emits a report-only followup when a prior notice expires or weakens, so operators do not keep treating stale evidence as current.

## Trigger model

- notification kind: `followup`
- baseline selection: latest prior main or attention notification
- the previous followup itself is never reused as the next baseline
- repeated followups are suppressed for the same baseline signal

## State files

- `logs/last_followup_notified.json`
- `logs/last_notified.json`
- `logs/last_attention_notified.json`

## Notification behavior

- public label: `⏱️ 期限切れ・再評価`
- title: `BTCFX Manual Trading Report`
- path slug: `manual-trading`
- subject and detail HTML include the previous signal, valid-until time, reason codes, human message, and safety boundary

## Repeat suppression

- one baseline produces at most one followup until a new baseline appears
- expiry alone does not create endless repeats
- `followup_for_signal_id` blocks duplicates for the same prior signal

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order endpoint access
- no scoring, gate, or threshold tuning
- Phase4 status does not change here

## Rollback files

- `config.py`
- `main.py`
- `src/ai/summary.py`
- `src/notification/detail_page.py`
- `src/notification/followup.py`
- `src/notification/trigger.py`
- `src/storage/json_store.py`
- `tests/test_notification_followup.py`
- `tests/test_notification_trigger_followup.py`

## Observation checklist

- verify followup only appears after expiry or thesis weakening
- verify the same baseline does not produce repeated followups
- verify `logs/last_followup_notified.json` is written after the first natural followup
- verify subject and detail HTML render the followup section correctly
- verify notification frequency does not become noisy
- verify no scoring, gate, or threshold tuning occurred
