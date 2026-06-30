# ENTRY_REACHED_OUTCOME_BREAKDOWN

## Purpose

entry reached 後の outcome 内訳を report-only で明示する。

## Source of truth

- MCP-primary repo is the current source of truth
- old runtime pull is not needed unless explicitly reopened
- no old runtime repo access was performed
- no runtime action was performed

## Added helper

- `summarize_intraperiod_entry_reached_outcomes`
- 入力は `outcomes_df: pandas DataFrame | None`
- trading logic は変えていない

## Entry-reached denominator

- exact: `tp1_first, tp2_first, sl_first, timeout, ambiguous, entry_reached`
- `no_ohlcv`, `not_entered`, `pending` は entry reached denominator ではない

## Outcome breakdown

- resolved exits は `tp1_first`, `tp2_first`, `sl_first`
- unresolved entries は `timeout`, `ambiguous`, `entry_reached`
- report-only の内訳であり、profitability claim ではない

## Safety boundary

- report-only / not FORMAL_GO / no automatic order / human decides manually
- trading logic unchanged

## Next recommendation

- `BTCFX-20260630-CANDIDATE-TYPE-SIDE-BREAKDOWN`
- Goal: report-only で candidate_type / side / active_primary_action の内訳を整理する。

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
