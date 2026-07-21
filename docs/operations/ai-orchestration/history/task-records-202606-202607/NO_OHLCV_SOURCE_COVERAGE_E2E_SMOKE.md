# NO_OHLCV_SOURCE_COVERAGE_E2E_SMOKE

## Purpose
`ohlcv_source_coverage_summary` が manual surface の export/check 経路で生成・露出されることを smoke 確認した記録。

## Commands run
- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json`
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface`
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json`

## Checked artifacts
- stdout-json の `ohlcv_source_coverage_summary`
- export 後の `local/manual_delivery_app_surface/app-contract.json`
- export 後の `local/manual_delivery_app_surface/app-dashboard.html`
- export 後の `local/manual_delivery_app_surface/app-snapshot.json`
- export 後の `local/manual_delivery_app_surface/app-snapshot-status.json`

## Result
`ohlcv_source_coverage_summary` は contract / stdout-json / exported artifacts に出力された。
確認した主な字段は `candidate_rows`, `ohlcv_input_rows`, `ohlcv_valid_rows`, `candidate_timestamp_rows`, `window_covered_rows`, `window_missing_rows`, `no_global_ohlcv_risk_rows`, `window_missing_rate`, `coverage_note`, `safety_note`。

## Generated file handling
`local/manual_delivery_app_surface/` 配下は生成物として扱い、commit 対象にしない。差分が残る場合は verification 後に戻す前提で扱う。

## Safety boundary
report-only / not FORMAL_GO / no automatic order / human decides manually。private/account/order/runtime execution affordance は追加しない。

## Next recommendation
`BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-CHECKPOINT-REVIEW`

## Out of scope
trading logic 変更、generated files の commit、runtime / old runtime / private / order / notification の追加、OHLCV fetch の追加はしない。
