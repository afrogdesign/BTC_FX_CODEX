# NO_OHLCV_COVERAGE_DIAGNOSTIC

## Purpose

intraperiod reports で `no_ohlcv` が支配的な理由を切り分け、valid sample denominator を local/report-only で明示する。

## Source of truth

- MCP-primary repo is the current source of truth
- old runtime pull is not needed unless explicitly reopened
- no old runtime repo access was performed
- no runtime action was performed

## Diagnostic result

- `no_ohlcv` は reviewed reports の全日で 91%超
- これは戦略の負けではなく data coverage / denominator issue
- profitable / unprofitable の判断はここではしない

## Added helper

- `summarize_intraperiod_outcome_coverage`
- 入力は `outcomes_df: pandas DataFrame`
- 返却値は total rows / no_ohlcv rows / valid sample rows / entry reached rows / rates / valid sample definition

## Valid sample denominator

- exact: `rows excluding outcome == no_ohlcv`
- valid sample を先に明示してから、report-only の win-rate を扱う

## Next recommendation

- `BTCFX-20260630-VALID-SAMPLE-WINRATE-REPORT`
- Goal: valid sample denominator を使って、no_ohlcv 除外の report-only win-rate metrics を整える。
- Mode: `NORMAL_CODEX`

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
