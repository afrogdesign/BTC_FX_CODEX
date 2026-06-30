## Purpose
`evidence_quality_summary` を既存 app contract / stdout-json に report-only で露出し、manual surface 側の確認をそろえる。

## Contract fields
`valid_sample_definition`, `total_rows`, `no_ohlcv_rows`, `valid_sample_rows`, `entry_reached_rows`, `win_like_rows`, `loss_like_rows`, `unresolved_entry_rows`, `potential_fakeout`, `potential_missed_turn`, `bad_entry_timing`, `safety_note`。

## Safety boundary
report-only / not FORMAL_GO / no automatic order / human decides manually。runtime execution affordance、private/account/order endpoint は追加しない。

## Tests
`tests/test_log_feedback.py` で app contract JSON と stdout-json の露出を確認する。

## Next recommendation
`BTCFX-20260630-EVIDENCE-QUALITY-CHECKPOINT-REVIEW`

## Out of scope
trading logic 変更、自動発注、通知送信、runtime action、profitability claim は対象外。
