# DEVELOPMENT_TO_RUNTIME_HANDOFF_PREP

## Purpose
development repo の evidence-quality / OHLCV coverage visibility phase を、後で runtime / execution repo に反映するための report-only handoff package として整理する。

## Handoff status
- development repo checkpoint only
- runtime repo not touched
- no push
- no generated file commit
- no `FORMAL_GO`
- no automatic order
- no trading logic change
- no OHLCV fetch

## What is ready to reflect later
- report-only evidence quality summary builder / surface
- report-only OHLCV source coverage summary
- report-only OHLCV range freshness fields
- report-only stale OHLCV operator warning
- summary text display
- detail HTML display
- app contract / stdout-json / exported surface exposure
- tests covering helper / surface / export behavior
- docs explaining evidence quality state and limits

## File/change groups
### Core evidence / coverage logic
- `src/trade/active_plan_intraperiod.py`

### Manual surface / text / HTML
- `src/ai/summary.py`
- `src/notification/detail_page.py`

### App contract / export path
- `tools/log_feedback.py`

### Tests
- `tests/test_active_plan_candidate_intraperiod_outcomes.py`
- `tests/test_active_plan_notification_formatting.py`
- `tests/test_summary_format.py`
- `tests/test_notification_detail_page.py`
- `tests/test_log_feedback.py`

### Handoff docs / audit trail
- `docs/operations/ai-orchestration/*.md`

## Required validation commands before reflection
```bash
./.venv312/bin/python -m unittest tests.test_active_plan_candidate_intraperiod_outcomes tests.test_active_plan_notification_formatting tests.test_summary_format tests.test_notification_detail_page tests.test_log_feedback
./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json
./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface
./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json
git diff --check -- docs/operations/ai-orchestration/DEVELOPMENT_TO_RUNTIME_HANDOFF_PREP.md docs/operations/ai-orchestration/NEXT_ACTION.md
git status --short --branch
```

## Runtime reflection exclusions
- do not copy generated files from `local/manual_delivery_app_surface/`
- do not copy logs/csv outputs as source of truth
- do not add OHLCV fetch
- do not start runtime process
- do not add notification sending
- do not add private/account/order endpoint
- do not change trading decision logic
- do not interpret current stale evidence as performance approval
- do not reflect to runtime repo without explicit user approval

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Known blockers / limits
- `ohlcv_range_freshness_status`: `stale_before_latest_candidate`
- `candidate_rows`: 1418
- `ohlcv_valid_rows`: 499
- `window_covered_rows`: 88
- `window_missing_rows`: 1330
- `window_missing_rate`: about 93.8%
- `candidate_max_after_ohlcv_end_hours`: about 479.8
- performance interpretation remains weak until OHLCV coverage is refreshed or otherwise handled outside trading logic

## Suggested reflection order
1. First reflect tests and helper logic in a controlled branch or patch.
2. Then reflect summary/detail surface changes.
3. Then reflect app contract/export path.
4. Then run validation commands.
5. Then inspect generated artifacts manually.
6. Stop before any runtime/deploy/send/trade action.

## Stop conditions
- runtime repo reflection would be required
- OHLCV fetch would be required
- trading logic change would be required
- generated/logs commit would be required
- runtime / old runtime / private / order / notification access would be required
- validation commands fail
- allowed-outside docs edits would be required

## Next task
- `BTCFX-20260630-DEVELOPMENT-TO-RUNTIME-HANDOFF-CHECKPOINT`
- Goal: review the handoff package and stop at a clean development-repo checkpoint, ready for explicit user approval before any runtime repo reflection.

## Out of scope
- runtime repo edits
- source/test edits
- generated file commit
- progress HTML / `CURRENT_PROGRESS.md` updates
- trading logic changes
- OHLCV fetch
- profitability claim
