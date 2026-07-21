# CANDIDATE_TYPE_SIDE_BREAKDOWN

## Purpose

`candidate_type` / `side` / `active_primary_action` ごとの report-only 内訳を明示する。

## Added helper

- `summarize_intraperiod_candidate_dimension_breakdowns`
- 入力は `outcomes_df: pandas DataFrame | None`
- trading logic は変えていない

## Breakdown dimensions

- `candidate_type`
- `side`
- `active_primary_action`
- blank / NaN は `"(blank)"` にまとめる

## Report-only interpretation

- 各グループは `summarize_intraperiod_valid_sample_winrate` をそのまま再利用する
- これは profitability claim ではない

## Safety boundary

- report-only / not FORMAL_GO / no automatic order / human decides manually
- trading logic unchanged

## Next recommendation

- `BTCFX-20260630-MAJOR-TURN-CANDIDATE-REVIEW`
- Goal: report-only evidence で potential_fakeout と potential_missed_turn を確認する。

## Out of scope

- no trading logic change
- no auto order
- no private/account/order endpoint
- no notification sending
- no runtime action
- no generated file commit
- no source edit
- no test edit
- no profitability claim
- no old runtime repo access
