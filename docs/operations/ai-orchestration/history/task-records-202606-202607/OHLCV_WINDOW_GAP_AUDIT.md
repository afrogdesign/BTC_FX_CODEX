# OHLCV_WINDOW_GAP_AUDIT

## Purpose
`per_window_ohlcv_gap` の原因を report-only で監査し、candidate timestamp range と OHLCV coverage range のズレを確認する。

## Inputs inspected
- `docs/operations/ai-orchestration/NO_OHLCV_COVERAGE_ACTUAL_SNAPSHOT.md`
- `docs/operations/ai-orchestration/NO_OHLCV_SOURCE_COVERAGE_CHECKPOINT_REVIEW.md`
- `docs/operations/deploy/Ver03-v2_CANDIDATE_COVERAGE_WINDOW_REVIEW_20260610.md`
- `docs/operations/deploy/Ver03-v2_OHLCV_INPUT_CONTRACT_20260609.md`
- `docs/operations/deploy/Ver03-v2_CONTROLLED_BUILDER_RUN_20260610.md`
- `docs/specs/active-plan-intraperiod-outcomes.md`
- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`

## Current actual coverage snapshot
- `candidate_rows`: 1418
- `ohlcv_input_rows`: 499
- `ohlcv_valid_rows`: 499
- `candidate_timestamp_rows`: 1418
- `missing_candidate_timestamp_rows`: 0
- `window_covered_rows`: 88
- `window_missing_rows`: 1330
- `no_global_ohlcv_risk_rows`: 0
- `window_missing_rate`: 0.9379407616361072
- `ohlcv_start`: `2026-06-04T22:45:00+09:00`
- `ohlcv_end`: `2026-06-10T03:15:00+09:00`

## Candidate/OHLCV range comparison
- candidate timestamp min: `2026-06-08T20:05:01.033760+09:00`
- candidate timestamp max: `2026-06-30T03:05:00.923983+09:00`
- candidate span extends far beyond `ohlcv_end`
- OHLCV coverage span ends more than 20 days before the latest candidate rows

## Gap classification
`ohlcv_range_stale_or_too_short`

## Product-quality interpretation
report-only の visibility では `no_ohlcv` の原因は見えるようになったが、現在の実値は OHLCV range が candidate span に追随していないことを示す。したがって次の安全な改善方向は、coverage 増強そのものではなく、OHLCV range の freshness / staleness を可視化して古い OHLCV が silently 支配しないようにすること。

## Recommended next task
- `BTCFX-20260630-OHLCV-RANGE-FRESHNESS-GUARD`
- Goal: add report-only OHLCV range freshness/staleness visibility so old OHLCV coverage cannot silently dominate `no_ohlcv`.

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Out of scope
- trading logic 変更
- runtime action
- old runtime repo access
- notification sending
- generated file commit
- OHLCV fetch の追加
- profitability claim
