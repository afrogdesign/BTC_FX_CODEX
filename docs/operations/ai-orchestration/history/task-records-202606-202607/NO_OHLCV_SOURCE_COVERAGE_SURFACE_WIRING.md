# NO_OHLCV_SOURCE_COVERAGE_SURFACE_WIRING

## Purpose

`summarize_intraperiod_ohlcv_source_coverage` を manual surface / app contract / stdout-json 側へ report-only で露出する。

## Wiring path

- `tools/log_feedback.py` の current manual delivery app contract / surface 出力に `ohlcv_source_coverage_summary` を追加する。
- `src/ai/summary.py` と `src/notification/detail_page.py` で同じ key を表示する。
- 既存の candidate / OHLCV 入力があるときだけ生成し、無ければ report-only fallback を使う。

## Surface fields

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

## Fallback behavior

- candidate / OHLCV の両方が無い場合は zero / empty の report-only summary を返す。
- market data fetch はしない。
- runtime action はしない。
- coverage を outcomes だけから捏造しない。

## Tests

- `tests/test_log_feedback.py`
- `tests/test_active_plan_notification_formatting.py`
- `tests/test_summary_format.py`
- `tests/test_notification_detail_page.py`

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Next recommendation

- `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-E2E-SMOKE`
- Goal: run the manual surface export/check smoke path and confirm `ohlcv_source_coverage_summary` appears without committing generated files.

## Out of scope

- trading logic 変更
- OHLCV fetch
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- profitability claim
