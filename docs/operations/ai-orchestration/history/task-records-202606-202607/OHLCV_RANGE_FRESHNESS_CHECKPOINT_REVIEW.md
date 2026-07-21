# OHLCV_RANGE_FRESHNESS_CHECKPOINT_REVIEW

## Purpose
OHLCV range freshness visibility path を一区切りとして review し、次の report-only product-quality task を決める。

## Completed path
- `summarize_intraperiod_ohlcv_source_coverage`
- `ohlcv_source_coverage_summary`
- freshness fields:
  - `candidate_timestamp_min`
  - `candidate_timestamp_max`
  - `candidate_max_after_ohlcv_end_hours`
  - `stale_threshold_hours`
  - `ohlcv_range_freshness_status`
  - `freshness_note`
- summary text display
- detail HTML display
- app contract / stdout-json / exported artifacts exposure
- E2E smoke confirmation
- no generated file commit

## Accepted outputs
- report-only の OHLCV range freshness / staleness visibility
- manual surface への summary 表示
- app contract / stdout-json への summary 露出
- exported artifacts への summary 露出

## Current freshness values
- `candidate_timestamp_min`: `2026-06-08T20:05:01.033760+09:00`
- `candidate_timestamp_max`: `2026-06-30T03:05:00.923983+09:00`
- `candidate_max_after_ohlcv_end_hours`: `479.83358999527775`
- `stale_threshold_hours`: `24.0`
- `ohlcv_range_freshness_status`: `stale_before_latest_candidate`
- `freshness_note`: `latest candidate is 479.8h after OHLCV end; old OHLCV coverage can silently dominate no_ohlcv`

## Remaining limits
- report-only
- no profitability claim
- visibility is complete, but OHLCV data itself is still stale
- no OHLCV fetch added
- no trading logic changed
- human review still required
- automatic trading not started

## Product-quality interpretation
Current status is `stale_before_latest_candidate`. 最新 candidate timestamp は OHLCV end から約 480 時間後で、dominant blocker は unknown coverage ではなく stale / too-short な OHLCV range だと分かる。次に有効なのは、この stale OHLCV 条件を operator / manual surface 上で見落とせないようにすることだが、fetch や execution affordance は追加しない。

## Next task
- `BTCFX-20260630-OHLCV-STALE-COVERAGE-OPERATOR-WARNING`
- Goal: add a prominent report-only operator warning when `ohlcv_range_freshness_status == stale_before_latest_candidate`, so stale OHLCV coverage cannot be mistaken for usable evidence.

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Out of scope
- trading logic 変更
- OHLCV fetch
- runtime / old runtime / private / order / notification
- generated file commit
- profitability claim
