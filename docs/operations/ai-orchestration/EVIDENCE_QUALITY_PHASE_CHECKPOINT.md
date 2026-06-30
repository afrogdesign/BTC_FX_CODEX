# EVIDENCE_QUALITY_PHASE_CHECKPOINT

## Purpose
completed evidence-quality / OHLCV coverage visibility phase をまとめ、次の product-quality direction を決める。

## Phase summary
この phase は、trading-logic の前に evidence quality を visible にした checkpoint である。profitability は主張しない。FORMAL_GO には進まない。automatic order も有効化しない。development repo 側の checkpoint として、runtime repo reflection の前に整理した。

## Completed capabilities
- `evidence_quality_summary`
- valid sample / entry reached / win-like / loss-like / unresolved summary
- candidate dimension breakdowns
- major-turn candidate review
- `ohlcv_source_coverage_summary`
- actual OHLCV coverage snapshot
- OHLCV window gap audit
- `ohlcv_range_freshness_status`
- `OHLCV stale coverage warning`
- summary text display
- detail HTML display
- app contract / stdout-json / exported artifacts freshness fields
- direct summary/detail render confirmation
- smoke confirmation
- no generated file commit

## Current evidence-quality state
- `candidate_rows`: 1418
- `ohlcv_valid_rows`: 499
- `window_covered_rows`: 88
- `window_missing_rows`: 1330
- `window_missing_rate`: about 93.8%
- `candidate_timestamp_max`: `2026-06-30T03:05:00.923983+09:00`
- `ohlcv_end`: `2026-06-10T03:15:00+09:00`
- `candidate_max_after_ohlcv_end_hours`: about 479.8
- `ohlcv_range_freshness_status`: `stale_before_latest_candidate`

## What is now safe to trust
- system can identify that OHLCV evidence is stale / insufficient
- operator/manual surface can show stale warning
- evidence fields are visible in report-only surfaces
- `no_ohlcv` is no longer an unexplained black box

## What is still not safe to trust
- performance interpretation based on stale OHLCV coverage
- win-rate / expectancy as trading approval
- Phase G score/gate relaxation based on current stale coverage
- automatic trading readiness
- runtime reflection without a separate checkpoint

## Product-quality interpretation
旧 phase table では Phase F late stage: `Active Plan intraperiod 実データ確認` に相当する。Phase G は未着手。今の good stopping point は、evidence-quality visibility は phase checkpoint として十分だが、trading logic の変更にはまだ進まないということだ。runtime/execution 側へ反映する前に、development repo 側で「何が safe で、何が safe でなく、次に何をしてよいか」を 1 つの handoff 文書にまとめるべきである。

## Recommended next direction
- `BTCFX-20260630-DEVELOPMENT-TO-RUNTIME-HANDOFF-PREP`
- Goal: prepare a report-only handoff package for reflecting the development repo state to the runtime/execution repo later, without touching the runtime repo yet.
- This should include file/change groups, safety boundaries, validation commands, and explicit exclusions.

## Safety boundary
- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance

## Out of scope
- trading logic 変更
- OHLCV fetch
- runtime / old runtime / private / order / notification
- generated file commit
- profitability claim
