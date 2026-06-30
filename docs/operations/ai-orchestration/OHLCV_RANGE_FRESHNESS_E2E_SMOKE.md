# OHLCV_RANGE_FRESHNESS_E2E_SMOKE

## Purpose
report-only export/check smoke を走らせ、`ohlcv_source_coverage_summary` の freshness fields が exported artifacts に出ることを確認した記録。

## Commands run
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json`
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface`
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json`

## Checked artifacts
- `local/manual_delivery_app_surface/app-contract.json`
- `local/manual_delivery_app_surface/app-dashboard.html`
- `local/manual_delivery_app_surface/app-snapshot.json`
- `local/manual_delivery_app_surface/index.html`

## Result
確認できた。`ohlcv_source_coverage_summary` に freshness fields が含まれ、exported artifacts 側でも同じ項目が表示された。

## Current freshness values
- `candidate_timestamp_min`: `2026-06-08T20:05:01.033760+09:00`
- `candidate_timestamp_max`: `2026-06-30T03:05:00.923983+09:00`
- `candidate_max_after_ohlcv_end_hours`: `479.83358999527775`
- `stale_threshold_hours`: `24.0`
- `ohlcv_range_freshness_status`: `stale_before_latest_candidate`

## Generated file handling
`local/manual_delivery_app_surface/` は確認のみで扱い、commit しない。必要なら検証後に tracked 差分が残らないよう戻す前提とした。

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Next recommendation
- `BTCFX-20260630-OHLCV-RANGE-FRESHNESS-CHECKPOINT-REVIEW`
- Goal: review completed OHLCV freshness visibility path and decide the next report-only product-quality task.

## Out of scope
- trading logic 変更
- OHLCV fetch
- runtime / old runtime / private / order / notification
- generated file commit
- profitability claim
