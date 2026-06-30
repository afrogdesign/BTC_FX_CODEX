# MAJOR_TURN_CANDIDATE_REVIEW

## Purpose

既存 intraperiod reports の `potential_fakeout` / `potential_missed_turn` / `bad_entry_timing` を report-only で整理する。

## Evidence source

- `docs/operations/ai-orchestration/INTRAPERIOD_WINRATE_DIAGNOSTIC_PASS.md`
- `docs/operations/ai-orchestration/EVIDENCE_QUALITY_BACKLOG.md`
- `docs/operations/ai-orchestration/CANDIDATE_TYPE_SIDE_BREAKDOWN.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260624.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260630.md`

## Review counts

- `potential_missed_turn`: 35
- `potential_fakeout`: 39
- `bad_entry_timing`: 2
- `inconclusive`: very large
- `no_ohlcv`: above 91%

## Interpretation

- major-turn は未確定である。
- `potential_fakeout` と `potential_missed_turn` は近い水準だが、`inconclusive` が大きく、ここから確定判断はしない。
- `bad_entry_timing` は小さいが、entry timing の見直し候補として残る。
- これは profitability claim ではない。

## Human review candidates

- fakeout review: `potential_fakeout`
- missed opportunity review: `potential_missed_turn`
- timing review: `bad_entry_timing`

## Safety boundary

- report-only / not FORMAL_GO / no automatic order / human decides manually
- trading logic unchanged

## Next recommendation

- `BTCFX-20260630-MANUAL-SURFACE-QUALITY-BACKLOG`
- Goal: report-only evidence improvements を manual trading surface backlog にまとめる。

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
