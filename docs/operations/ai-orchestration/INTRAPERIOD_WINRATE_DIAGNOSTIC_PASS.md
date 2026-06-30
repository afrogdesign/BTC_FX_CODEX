# INTRAPERIOD_WINRATE_DIAGNOSTIC_PASS

## Purpose

利用可能な intraperiod outcome reports から、実用改善に効く evidence gap と次の metrics / tests を機械的に整理する。

## Source of truth

- MCP-primary repo is the current source of truth
- old runtime pull is not needed unless explicitly reopened
- no old runtime repo access was performed
- no runtime action was performed

## Evidence files reviewed

- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260624.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260625.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260626.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260627.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260628.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260629.md`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260630.md`

## Extracted report metrics

| Date | Rows | Entry reached | TP1 first | TP2 first | SL first | Timeout | No OHLCV | Entry rate | No OHLCV rate | Avg MFE/R | Avg MAE/R | Turn diagnostic summary |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2026-06-24 | 1067 | 76 | 35 | 0 | 39 | 2 | 979 | 7.1% | 91.8% | 0.98 | 0.88 | `potential_missed_turn` 35, `potential_fakeout` 39, `bad_entry_timing` 2, `inconclusive` 991 |
| 2026-06-25 | 1149 | 76 | 35 | 0 | 39 | 2 | 1061 | 6.6% | 92.3% | 0.98 | 0.88 | `potential_missed_turn` 35, `potential_fakeout` 39, `bad_entry_timing` 2, `inconclusive` 1010 |
| 2026-06-26 | 1215 | 76 | 35 | 0 | 39 | 2 | 1127 | 6.3% | 92.8% | 0.98 | 0.88 | `potential_missed_turn` 35, `potential_fakeout` 39, `bad_entry_timing` 2, `inconclusive` 1073 |
| 2026-06-27 | 1277 | 76 | 35 | 0 | 39 | 2 | 1189 | 6.0% | 93.1% | 0.98 | 0.88 | `potential_missed_turn` 35, `potential_fakeout` 39, `bad_entry_timing` 2, `inconclusive` 1201 |
| 2026-06-28 | 1277 | 76 | 35 | 0 | 39 | 2 | 1189 | 6.0% | 93.1% | 0.98 | 0.88 | `potential_missed_turn` 35, `potential_fakeout` 39, `bad_entry_timing` 2, `inconclusive` 1201 |
| 2026-06-29 | 1348 | 76 | 35 | 0 | 39 | 2 | 1260 | 5.6% | 93.5% | 0.98 | 0.88 | `potential_missed_turn` 35, `potential_fakeout` 39, `bad_entry_timing` 2, `inconclusive` 1272 |
| 2026-06-30 | 1418 | 76 | 35 | 0 | 39 | 2 | 1330 | 5.4% | 93.8% | 0.98 | 0.88 | `potential_missed_turn` 35, `potential_fakeout` 39, `bad_entry_timing` 2, `inconclusive` 1342 |

Metric correction note: values were re-read from each dated source report and corrected where the previous table had shifted values.

## Cross-report observations

- `no_ohlcv` が 91.8% から 93.8% の範囲で非常に大きく、win-rate 解釈は強く制限される。
- entry reached は 76 行で固定だが rows が増えるため、entry rate は 7.1% から 5.4% へ低下して見える。
- entry 後は TP1 first 35 / SL first 39 / timeout 2 で、TP1 と SL は近いが sample は小さい。
- timeout は entry reached に対して 2.6% と小さいが、bad entry timing の再確認候補としては残る。
- `potential_missed_turn` 35 と `potential_fakeout` 39 は拮抗しており、`inconclusive` が大きいので major-turn 判断には進めない。
- 平均 MFE/R 0.98 と平均 MAE/R 0.88 は近いが、`no_ohlcv` が支配的なので単独で良否は言えない。

## Evidence gaps

- `no_ohlcv` coverage が高く、全体解釈を制限している。
- entry-reached sample size は 76 行で固定のため、改善判断にはまだ限定的である。
- `TP2 first` は全報告で 0 で、検出が未成立か稀少かを切り分ける追加確認が必要である。
- `timeout` / `ambiguous` / `pending` は follow-up が必要だが、特に `timeout` は継続確認が必要である。
- `tp2_first` は現報告では 0 のままだが、同一バー TP1+TP2 without SL の追跡は継続すべきである。

## Metrics needed next

- valid-sample win-rate excluding `no_ohlcv`
- entry-reached subset outcome distribution
- candidate_type outcome distribution
- side outcome distribution
- active_primary_action outcome distribution
- expectancy proxy using MFE/R and MAE/R
- false-positive review candidates
- missed-opportunity review candidates
- bad-entry-timing review candidates
- no_ohlcv coverage ratio and cause

## Tests or tooling needed next

- test or report check for valid sample denominator
- test or report check for no_ohlcv ratio
- test or report check for candidate_type breakdown
- test or report check for side breakdown
- test or report check for major-turn diagnostic categories
- no private/account/order endpoints
- no trading logic change

## Decision

- `ready_for_evidence_quality_backlog`

## Next recommendation

- `BTCFX-20260630-EVIDENCE-QUALITY-BACKLOG`
- Goal: 今回の診断で見えた evidence gaps を優先順 backlog に落とし込み、次の検証対象を local/report-only で確定する。

## Out of scope

- no trading logic change
- no auto order
- no private/account/order endpoint
- no notification sending
- no runtime action
- no generated file commit
- no source edit
- no test edit
- no profitability claim without sufficient evidence
- no old runtime repo access

## Stop / human-check triggers

- missing evidence reports
- inconsistent report counts
- need to change trading rules
- need to fetch exchange data
- need to touch private/account/order endpoints
- need to run live/runtime actions
- need to send notifications
- need to claim profitability
- need to expand beyond listed evidence files
