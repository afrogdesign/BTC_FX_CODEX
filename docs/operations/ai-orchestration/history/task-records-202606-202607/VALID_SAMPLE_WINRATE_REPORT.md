# VALID_SAMPLE_WINRATE_REPORT

## Purpose

`no_ohlcv` を除外した valid sample を明示し、report-only の win-rate 指標を安全に定義する。

## Source of truth

- MCP-primary repo is the current source of truth
- old runtime pull is not needed unless explicitly reopened
- no old runtime repo access was performed
- no runtime action was performed

## Added helper

- `summarize_intraperiod_valid_sample_winrate`
- 入力は `outcomes_df: pandas DataFrame | None`
- trading logic は変えていない

## Valid sample denominator

- exact: `rows excluding outcome == no_ohlcv`
- `no_ohlcv` は denominator から除外する
- `not_entered` と `pending` は valid sample に含めるが entry reached ではない

## Report-only win-rate definition

- win-like は `tp1_first` / `tp2_first`
- loss-like は `sl_first`
- `timeout` / `ambiguous` / `entry_reached` は unresolved
- これは profitability claim ではない

## Safety boundary

- report-only / not FORMAL_GO / no automatic order / human decides manually
- trading logic unchanged

## Next recommendation

- `BTCFX-20260630-ENTRY-REACHED-OUTCOME-BREAKDOWN`
- Goal: report-only valid sample を前提に entry-reached outcomes を分解する。

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
