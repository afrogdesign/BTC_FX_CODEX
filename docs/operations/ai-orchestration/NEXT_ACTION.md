# NEXT_ACTION

- current_work_id: `BTCFX-20260723-VER04-V4-M-DELIVERY1-RUNTIME-DECOUPLE`
- mode: `RUNTIME_TASK`
- primary branch: `Ver04-v4`
- accepted core runtime source locator: `bc61478`
- accepted M-STATS1 evaluator report locator: `68ed430`
- accepted M-STATS1 runtime-shadow report locator: `c4d9a4a`
- active spec: `chatgpt/specs/active/20260723_macro_structure_runtime_publication_decouple.md`
- status: implementation approved; fixed public URL currently updates only inside approved notification sends
- push: none

## Objective

- move fixed macro publication from the notification-send branch to the scheduled macro runtime
- publish once after successful snapshot -> history -> operator
- keep publication failure non-blocking for core success, scenario stats, and health
- make notification integration read the recorded publication result without SSH or rsync
- preserve notification decisions, email subjects, recipients, duplicate suppression, schedule, plist, gates, thresholds, scores, classifiers, and order behavior

## Validation budget

- matching unit tests only
- one dry-run
- task-scoped diff check
- exactly one macro target kickstart after commit
- exactly one bounded runtime-status review and one HTTPS GET
- no notification cycle, SMTP test, notification reload, repeated health cycle, replay, or unchanged retry
