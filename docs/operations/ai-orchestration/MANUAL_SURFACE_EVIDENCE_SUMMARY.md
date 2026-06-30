## Purpose
手動 trading surface に `evidence_quality_summary` を report-only で表示し、検証中の evidence quality を人間が確認しやすくする。

## Surface fields
表示する項目は `valid_sample_definition`, `total_rows`, `no_ohlcv_rows`, `valid_sample_rows`, `entry_reached_rows`, `win_like_rows`, `loss_like_rows`, `unresolved_entry_rows`, `potential_fakeout`, `potential_missed_turn`, `bad_entry_timing`, `safety_note`。

## Safety boundary
report-only / not FORMAL_GO / no automatic order / human decides manually。trading logic は変えない。

## Tests
`tests/test_summary_format.py` と `tests/test_notification_detail_page.py` で summary と detail HTML の両方を確認する。

## Next recommendation
`BTCFX-20260630-MANUAL-SURFACE-EVIDENCE-SUMMARY-APP-CONTRACT`

## Out of scope
自動発注、通知送信追加、private/account/order endpoint、runtime action、profitability claim は対象外。
