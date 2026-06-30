# EVIDENCE_QUALITY_SUMMARY_E2E_SMOKE

## Purpose

`evidence_quality_summary` が manual surface の export / check 経路で実際に出力されることを smoke 確認する。

## Commands run

- `./.venv312/bin/python tools/log_feedback.py describe-current-manual-delivery-app-contract --stdout-json`
- `./.venv312/bin/python tools/log_feedback.py export-current-manual-delivery-app-surface`
- `./.venv312/bin/python tools/log_feedback.py check-current-manual-delivery-app-surface --stdout-json`

## Checked artifacts

- app contract stdout-json
- exported `local/manual_delivery_app_surface/app-contract.json`
- exported `local/manual_delivery_app_surface/app-dashboard.html`
- exported `local/manual_delivery_app_surface/app-ready.json`
- exported `local/manual_delivery_app_surface/app-snapshot.json`
- exported `local/manual_delivery_app_surface/app-snapshot-status.json`
- exported `local/manual_delivery_app_surface/app-surface-manifest.json`

## Result

- `evidence_quality_summary` が app contract stdout-json と exported artifacts に出力された。
- `valid_sample_definition`
- `no_ohlcv_rows`
- `valid_sample_rows`
- `entry_reached_rows`
- `potential_fakeout`
- `potential_missed_turn`
- `bad_entry_timing`
- `safety_note`
- safety boundary は report-only / not `FORMAL_GO` / no automatic order / human decides manually のまま。

## Generated file handling

- 生成物は commit していない。
- `local/manual_delivery_app_surface/` の tracked 差分は残していない。

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Next recommendation

- `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-CAUSE-DIAGNOSTIC`
- Goal: diagnose why `no_ohlcv` dominates and identify the next report-only coverage improvement without changing trading logic.

## Out of scope

- trading logic 変更
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- profitability claim
