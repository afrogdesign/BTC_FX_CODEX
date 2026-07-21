## Purpose
既存 manual surface export/check path を smoke 実行し、`evidence_quality_summary` が exported artifacts に出ることを確認する。

## Commands run
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json`
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface`
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json`

## Checked artifacts
- `local/manual_delivery_app_surface/app-contract.json`
- `local/manual_delivery_app_surface/app-dashboard.html`
- `local/manual_delivery_app_surface/app-ready.json`
- `local/manual_delivery_app_surface/app-snapshot.json`
- `local/manual_delivery_app_surface/app-snapshot-status.json`
- `local/manual_delivery_app_surface/app-surface-manifest.json`

## Result
`describe-current-manual-delivery-app-contract --stdout-json` に `evidence_quality_summary` が出た。`app-contract.json` にも `evidence_quality_summary`, `valid_sample_definition`, `safety_note` が出た。`check-current-manual-delivery-app-surface --stdout-json` は report-only 安全境界のまま通過した。

## Generated file handling
生成物は local/manual_delivery_app_surface/ に出力したが、Git には stage せず commit しない。差分管理対象は docs のみ。

## Safety boundary
report-only / not FORMAL_GO / no automatic order / human decides manually。trading logic は変えない。

## Next recommendation
`BTCFX-20260630-PRODUCT-QUALITY-NEXT-DECISION`

## Out of scope
trading logic 変更、自動発注、通知送信、runtime action、generated file commit、profitability claim は対象外。
