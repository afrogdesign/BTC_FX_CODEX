# OHLCV_STALE_COVERAGE_CHECKPOINT_REVIEW

## Purpose
completed stale OHLCV operator warning path を review し、次の report-only product-quality task を決める。

## Completed path
- `evidence_quality_summary`
- `ohlcv_source_coverage_summary`
- `ohlcv_range_freshness_status`
- `OHLCV stale coverage warning`
- summary text display
- detail HTML display
- app contract / stdout-json / exported artifacts freshness fields
- direct summary/detail render confirmation
- E2E smoke confirmation
- no generated file commit

## Accepted outputs
- report-only の stale OHLCV warning visibility
- manual surface への warning 表示
- app contract / stdout-json への freshness fields 露出
- exported artifacts への freshness fields 露出

## Current evidence-quality state
- `candidate_rows`: 1418
- `ohlcv_valid_rows`: 499
- `window_covered_rows`: 88
- `window_missing_rows`: 1330
- `window_missing_rate`: about 93.8%
- `candidate_timestamp_max`: `2026-06-30T03:05:00.923983+09:00`
- `ohlcv_end`: `2026-06-10T03:15:00+09:00`
- `candidate_max_after_ohlcv_end_hours`: about 479.8
- `ohlcv_range_freshness_status`: `stale_before_latest_candidate`

## Remaining limits
- report-only
- no profitability claim
- stale OHLCV is visible and warned, but OHLCV data itself is still stale
- no OHLCV fetch added
- no trading logic changed
- human review still required
- automatic trading not started

## Product-quality interpretation
この system は stale OHLCV が usable evidence に見えてしまうことを防ぐようになった。次の bottleneck は visibility ではなく、次に取るべき安全な product-quality step の判断だ。OHLCV が stale のままでは performance interpretation は弱く、coverage を refresh するか、現状の coverage gap を trading logic 以外で扱う必要がある。次の task は report-only の phase checkpoint に留めるべきで、trading logic に進めない。

## Next task
- `BTCFX-20260630-EVIDENCE-QUALITY-PHASE-CHECKPOINT`
- Goal: summarize the completed evidence-quality / OHLCV coverage visibility phase and choose the next product-quality direction without adding fetch, trading logic, or execution affordance.

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
