# OHLCV_STALE_COVERAGE_WARNING_E2E_SMOKE

## Purpose
report-only export/check smoke を走らせ、stale OHLCV warning が確認可能かを記録した。

## Commands run
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json`
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface`
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json`
- direct render check: `build_summary_body(...)` and `build_notification_detail_html(...)`

## Checked artifacts
- `local/manual_delivery_app_surface/app-contract.json`
- `local/manual_delivery_app_surface/app-dashboard.html`
- `local/manual_delivery_app_surface/app-snapshot.json`
- `local/manual_delivery_app_surface/index.html`
- direct render output for summary text
- direct render output for detail HTML

## Result
確認できた。contract / check の stdout-json と exported app surface artifacts で freshness fields を確認し、summary / detail の direct render で stale warning 文字列も確認した。

## Warning text confirmed
- `OHLCV stale coverage warning`
- `stale_before_latest_candidate`
- `candidate_max_after_ohlcv_end_hours`
- `report-only`
- `not FORMAL_GO`
- `no automatic order`
- `human decides manually`

## Freshness fields confirmed
- `ohlcv_source_coverage_summary`
- `candidate_timestamp_min`
- `candidate_timestamp_max`
- `candidate_max_after_ohlcv_end_hours`
- `stale_threshold_hours`
- `ohlcv_range_freshness_status`
- `freshness_note`

## Generated file handling
`local/manual_delivery_app_surface/` は確認のみで扱い、commit しない。必要なら検証後に tracked 差分が残らないよう戻す前提とした。

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Next recommendation
- `BTCFX-20260630-OHLCV-STALE-COVERAGE-CHECKPOINT-REVIEW`
- Goal: review completed stale OHLCV operator warning path and decide the next report-only product-quality task.

## Out of scope
- trading logic 変更
- OHLCV fetch
- runtime / old runtime / private / order / notification
- generated file commit
- profitability claim
