# OHLCV_STALE_COVERAGE_OPERATOR_WARNING

## Purpose
`ohlcv_range_freshness_status == stale_before_latest_candidate` のとき、operator / manual surface 上で stale OHLCV coverage を見落とせない report-only warning を表示する記録。

## Trigger condition
- `ohlcv_source_coverage_summary.ohlcv_range_freshness_status == stale_before_latest_candidate`

## Warning surfaces
- `src/ai/summary.py` の OHLCV source coverage summary
- `src/notification/detail_page.py` の HTML warning block
- app contract / stdout-json / exported artifacts の既存 summary 表示

## Safety wording
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- `stale_before_latest_candidate` を明示
- `candidate_max_after_ohlcv_end_hours` を明示

## Tests
- `tests/test_summary_format.py`
- `tests/test_notification_detail_page.py`
- `tests/test_active_plan_notification_formatting.py`

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Next recommendation
- `BTCFX-20260630-OHLCV-STALE-COVERAGE-WARNING-E2E-SMOKE`
- Goal: run report-only export/check smoke and confirm stale OHLCV warning appears without committing generated files.

## Out of scope
- trading logic 変更
- OHLCV fetch
- runtime / old runtime / private / order / notification
- generated file commit
- profitability claim
