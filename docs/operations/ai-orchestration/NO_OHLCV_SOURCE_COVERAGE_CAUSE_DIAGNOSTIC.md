# NO_OHLCV_SOURCE_COVERAGE_CAUSE_DIAGNOSTIC

## Purpose

`no_ohlcv` が支配的になる原因を、candidate timestamp と OHLCV coverage の観点で report-only に診断する。

## Helper

- `summarize_intraperiod_ohlcv_source_coverage(candidates_df, ohlcv_df, timeout_hours=24.0)`

## Diagnostic fields

- `candidate_rows`
- `ohlcv_input_rows`
- `ohlcv_valid_rows`
- `candidate_timestamp_rows`
- `missing_candidate_timestamp_rows`
- `window_covered_rows`
- `window_missing_rows`
- `no_global_ohlcv_risk_rows`
- `window_missing_rate`
- `ohlcv_start`
- `ohlcv_end`
- `coverage_note`
- `safety_note`

## Interpretation

- candidate timestamp が読めるのに window が埋まらない場合は、source coverage の空白を疑う。
- `ohlcv_valid_rows == 0` なら、全候補が global な `no_ohlcv` リスクになる。
- これは report-only の原因診断であり、取引許可や profitability を示さない。

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Tests

- `tests/test_active_plan_candidate_intraperiod_outcomes.py`
- parseable timestamp の window coverage と、OHLCV なしの global risk を確認した。

## Next recommendation

- `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-SURFACE-WIRING`
- Goal: surface the OHLCV source coverage cause summary on the manual/app report path without changing trading logic.

## Out of scope

- trading logic 変更
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- profitability claim
