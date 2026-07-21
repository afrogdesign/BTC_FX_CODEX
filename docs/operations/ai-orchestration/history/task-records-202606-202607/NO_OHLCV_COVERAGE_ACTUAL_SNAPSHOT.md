# NO_OHLCV_COVERAGE_ACTUAL_SNAPSHOT

## Purpose
既存 report-only export/check/contract path から、現在の実際の `ohlcv_source_coverage_summary` values を記録する。

## Commands run
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json`
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface`
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json`

## Actual summary values
- `candidate_rows`: 1418
- `ohlcv_input_rows`: 499
- `ohlcv_valid_rows`: 499
- `candidate_timestamp_rows`: 1418
- `missing_candidate_timestamp_rows`: 0
- `window_covered_rows`: 88
- `window_missing_rows`: 1330
- `no_global_ohlcv_risk_rows`: 0
- `window_missing_rate`: 0.9379407616361072
- `ohlcv_start`: `2026-06-04T22:45:00+09:00`
- `ohlcv_end`: `2026-06-10T03:15:00+09:00`
- `coverage_note`: `report-only coverage summary from candidate timestamps and valid OHLCV bars; missing windows indicate source coverage gaps, not trading logic`
- `safety_note`: `report-only / not FORMAL_GO / no automatic order / human decides manually`

## Blocker classification
`per_window_ohlcv_gap`

## Interpretation
candidate timestamp は全件読めている。`ohlcv_valid_rows` は 0 ではないため global missing ではない。`window_missing_rows` が大きいため、現在の支配的要因は per-window の OHLCV gap とみなせる。これは report-only の診断であり、profitability や trading permission を示さない。

## Generated file handling
`local/manual_delivery_app_surface/` などの generated files は commit しない。差分が残る場合は verification 後に戻す前提で扱う。

## Safety boundary
report-only / not `FORMAL_GO` / no automatic order / human decides manually。private/account/order/runtime execution affordance は追加しない。

## Next recommendation
- `BTCFX-20260630-OHLCV-WINDOW-GAP-AUDIT`
- Goal: inspect why many candidate windows remain uncovered and identify the next safe coverage-improvement direction without changing trading logic.

## Out of scope
- trading logic 変更
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- OHLCV fetch の追加
- profitability claim
