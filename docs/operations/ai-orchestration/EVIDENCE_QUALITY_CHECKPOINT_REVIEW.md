## Purpose
evidence-quality surface path が一区切りまで到達したかを確認し、次の product-quality task を決める。

## Completed path
- no_ohlcv coverage diagnostic
- valid sample winrate summary
- entry-reached outcome breakdown
- candidate_type / side / active_primary_action breakdown
- major-turn candidate review
- manual surface backlog
- manual surface evidence summary
- app contract / stdout-json exposure

## Accepted outputs
- report-only の evidence quality summaries が manual surface に載った
- app contract / stdout-json に `evidence_quality_summary` が露出した
- summary / detail HTML で表示確認ができた
- manual surface と app contract の docs がそろった

## Remaining limits
- report-only
- no profitability claim
- high no_ohlcv still limits confidence
- human review still required
- automatic trading not started

## Product-quality interpretation
evidence quality の見える化は一区切りだが、解釈の中心は依然として report-only の説明であり、売買判断や自動化の根拠にはしない。

## Next task
`BTCFX-20260630-EVIDENCE-QUALITY-SMOKE-EXPORT`
Goal: run the existing manual surface export/check path and confirm `evidence_quality_summary` appears in exported surface artifacts without committing generated files.

## Safety boundary
report-only / not FORMAL_GO / no automatic order / human decides manually。trading logic は変えない。

## Out of scope
trading logic 変更、自動発注、通知送信、runtime action、generated file commit、profitability claim は対象外。
