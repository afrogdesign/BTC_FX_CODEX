# NO_OHLCV_SOURCE_COVERAGE_CHECKPOINT_REVIEW

## Purpose
`no_ohlcv` source coverage visibility path を一区切りとして review し、次の report-only product-quality task を決める。

## Completed path
- `summarize_intraperiod_ohlcv_source_coverage`
- `ohlcv_source_coverage_summary`
- manual surface / app contract / stdout-json exposure
- text summary display
- detail HTML display
- E2E smoke confirmation
- no generated file commit

## Accepted outputs
- report-only summary が app contract と exported artifacts に露出した。
- `candidate_rows`, `ohlcv_input_rows`, `ohlcv_valid_rows`, `candidate_timestamp_rows`, `window_covered_rows`, `window_missing_rows`, `no_global_ohlcv_risk_rows`, `window_missing_rate`, `coverage_note`, `safety_note` を確認した。

## Remaining limits
- report-only
- no profitability claim
- visibility は complete だが、実際の最新 coverage values は operator snapshot がまだ必要
- no OHLCV fetch added
- no trading logic changed
- human review still required
- automatic trading not started

## Product-quality interpretation
この phase で `no_ohlcv` の原因は visible になったが、coverage 自体は fix していない。次に有用なのは、既存 export/check path から current actual coverage values を記録し、blocker が global missing OHLCV なのか timestamp mismatch なのか per-window gaps なのかを切り分けること。

## Next task
- `BTCFX-20260630-NO-OHLCV-COVERAGE-ACTUAL-SNAPSHOT`
- Goal: run the existing report-only export/check/contract path and document the current actual `ohlcv_source_coverage_summary` values without committing generated files.

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Out of scope
- trading logic 変更
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- profitability claim
