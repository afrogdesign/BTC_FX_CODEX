# EVIDENCE_QUALITY_SUMMARY_SURFACE_WIRING

## Purpose

`build_intraperiod_evidence_quality_summary` を既存の manual surface / app snapshot / app contract 経路へ配線し、`evidence_quality_summary` を intraperiod outcomes から生成して表示する。

## Wiring path

- `tools/log_feedback.py`
- `describe-current-manual-delivery-app-contract --stdout-json`
- `refresh-current-manual-delivery-app --export-app-surface`
- `export-current-manual-delivery-app-surface`
- `check-current-manual-delivery-app-surface --stdout-json`

## Generated fields

- `evidence_quality_summary`
- `valid_sample_definition`
- `total_rows`
- `no_ohlcv_rows`
- `valid_sample_rows`
- `entry_reached_rows`
- `win_like_rows`
- `loss_like_rows`
- `unresolved_entry_rows`
- `potential_fakeout`
- `potential_missed_turn`
- `bad_entry_timing`
- `safety_note`

## Tests

- `tests/test_log_feedback.py`
- `tests/test_active_plan_notification_formatting.py`
- CLI 側で generated summary が app contract / export / check に反映されることを確認した。

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order endpoint

## Next recommendation

- `BTCFX-20260630-EVIDENCE-QUALITY-SUMMARY-E2E-SMOKE`
- Goal: manual surface export/check の smoke path を走らせ、generated `evidence_quality_summary` が exported artifacts に出ることを確認する。

## Out of scope

- trading logic 変更
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- profitability claim
