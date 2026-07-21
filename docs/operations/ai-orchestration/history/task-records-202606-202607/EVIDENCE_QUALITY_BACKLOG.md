# EVIDENCE_QUALITY_BACKLOG

## Purpose

intraperiod evidence の穴を優先順に閉じて、実用改善に直結する次の作業を local/report-only で並べる。

## Source of truth

- MCP-primary repo is the current source of truth
- old runtime pull is not needed unless explicitly reopened
- no old runtime repo access was performed
- no runtime action was performed

## Evidence basis

- dashboard parity is complete
- evidence phase is current
- intraperiod diagnostic decision is `ready_for_evidence_quality_backlog`
- no_ohlcv coverage is the largest interpretation blocker
- entry-reached sample is 76 rows across the reviewed reports
- TP1 first is 35, SL first is 39, timeout is 2, TP2 first is 0 in the reviewed evidence
- no profitability claim is made

## Priority backlog

| Priority | Backlog item | Evidence reason | Safe next action | Stop condition |
|---:|---|---|---|---|
| 1 | `no_ohlcv coverage / denominator quality` | no_ohlcv が 91%超で解釈を支配している | valid sample の分母と除外条件を report-only で明示する | 分母が明示され、no_ohlcv 率の扱いが固定されたら止める |
| 2 | `valid-sample win-rate excluding no_ohlcv` | win-rate を見る前に有効母数が必要 | no_ohlcv 除外の win-rate 指標を report-only で定義する | 有効母数付きの win-rate 定義が確定したら止める |
| 3 | `entry-reached outcome distribution` | entry reached は 76 rows で固定的 | entry 到達後の outcome 分布を report-only で整理する | entry 後の outcome 分布が見えるようになったら止める |
| 4 | `candidate_type / side / active_primary_action breakdown` | candidate と side の切り口が必要 | 3 軸の breakdown を report-only で確認する | 3 軸の分布が同じ基準で出たら止める |
| 5 | `potential_fakeout and false-positive review candidates` | fakeout 候補の再確認が必要 | false-positive 候補を report-only で洗い出す | 候補一覧が human review 用に揃ったら止める |
| 6 | `potential_missed_turn and missed-opportunity review candidates` | missed turn 候補の再確認が必要 | missed-opportunity 候補を report-only で洗い出す | 候補一覧が human review 用に揃ったら止める |
| 7 | `bad-entry-timing / timeout review candidates` | timeout と bad timing が残っている | timeout 系の再確認候補を report-only で整理する | 2 件の timeout の扱いが明確になったら止める |
| 8 | `TP2-first / same-bar tp2_first tracking` | TP2 first は 0 で継続追跡が必要 | same-bar `tp2_first` の追跡を report-only で維持する | TP2 first の追跡方針が固定されたら止める |
| 9 | `report/test coverage for evidence metrics` | metric の再発防止に必要 | レポートとテストのカバレッジを report-only で補強する | 指標が再現可能になったら止める |

## Recommended next implementation task

- `BTCFX-20260630-NO-OHLCV-COVERAGE-DIAGNOSTIC`
- Goal: diagnose why no_ohlcv dominates the intraperiod reports and add safe local/report-only checks or tests that make the valid sample denominator explicit, without changing trading logic.
- Mode: `NORMAL_CODEX`

no_ohlcv は reviewed reports の全てで 91%超なので、ここが最優先の解釈ブロッカーです。

## Deferred tasks

- `BTCFX-20260630-VALID-SAMPLE-WINRATE-REPORT`
- `BTCFX-20260630-ENTRY-REACHED-OUTCOME-BREAKDOWN`
- `BTCFX-20260630-CANDIDATE-TYPE-SIDE-BREAKDOWN`
- `BTCFX-20260630-MAJOR-TURN-CANDIDATE-REVIEW`
- `BTCFX-20260630-MANUAL-SURFACE-QUALITY-BACKLOG`

## Human-check triggers

- need to change trading rules
- need to fetch exchange data
- need to touch private/account/order endpoints
- need to run live/runtime actions
- need to send notifications
- need to claim profitability
- need to expand beyond listed evidence files
- report counts remain inconsistent after correction

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
