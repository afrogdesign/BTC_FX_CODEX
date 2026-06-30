# OHLCV_RANGE_FRESHNESS_GUARD

## Purpose
`no_ohlcv` を old OHLCV coverage が silently 支配しないように、report-only の OHLCV range freshness / staleness  visibility を追加した記録。

## Added fields
- `candidate_timestamp_min`
- `candidate_timestamp_max`
- `candidate_max_after_ohlcv_end_hours`
- `stale_threshold_hours`
- `ohlcv_range_freshness_status`
- `freshness_note`

## Freshness status definitions
- `no_candidate_timestamps`: parseable candidate timestamp がない。
- `no_valid_ohlcv`: valid OHLCV rows がない。
- `stale_before_latest_candidate`: latest candidate が stale_threshold を超えて OHLCV end より後ろにある。
- `fresh_for_latest_candidate`: latest candidate までの freshness が保たれている。

## Surface path
- `summarize_intraperiod_ohlcv_source_coverage(...)` が freshness fields を返す。
- `tools/log_feedback.py` の contract / stdout-json / export surface に同じ summary が乗る。
- `src/ai/summary.py` と `src/notification/detail_page.py` が表示する。

## Tests
- `tests/test_active_plan_candidate_intraperiod_outcomes.py`
- `tests/test_active_plan_notification_formatting.py`
- `tests/test_summary_format.py`
- `tests/test_notification_detail_page.py`
- `tests/test_log_feedback.py`

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Next recommendation
- `BTCFX-20260630-OHLCV-RANGE-FRESHNESS-E2E-SMOKE`
- Goal: run report-only export/check smoke and confirm OHLCV range freshness fields appear without committing generated files.

## Out of scope
- trading logic 変更
- OHLCV fetch
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- profitability claim
