# Macro Implementation Route

last_updated: 2026-07-21
status: canonical macro route

## Purpose

M計画は、本体のmanual 15-minute trading supportを、上位足構造とnext-regime情報で補強する追加routeである。

本体Product計画を置き換えない。M計画だけを進めても、actual-backed ground truthやP9 tuning readinessは完成しない。

## Product gap addressed

M計画が扱う問題:

- 信頼できるhigher-timeframe support / resistance
- broader structure内の現在位置
- volatility expansion risk
- tactical biasとnext-regime riskの分離
- Big Chance解釈の明確化
- chart中心のoperator information hierarchy
- bounded champion/challenger proposal

研究上の優先順:

```text
reliable level map
→ level reliability history
→ current structural location
→ volatility state
→ pressure / activation evidence
→ next reliable target
→ outcome resolution
→ champion/challenger proposal
```

midpointやcompressionは補助変数であり、単独triggerや方向signalとして扱わない。

## Phase status

| Phase | Result | Status |
|---|---|---|
| M1 | reliable macro levels、lifecycle、event-time replay | accepted |
| M2 | optional disabled-by-default P8 auxiliary shadow | accepted |
| M3 | tactical biasとnext-regime riskを分離したoffline shadow | accepted |
| M4 | chart-first hierarchyのrender-only comparison | accepted |
| M5 | bounded champion/challenger proposal engine | accepted |
| M6 | approved proposalのruntime適用 | not started / not authorized |

## M5 accepted result

- accepted checkpoint locator: `3c7f01d90c3f5cc126cedd9aed294cf67a602c42`
- champion: 1
- challengers: 4
- chronological snapshot dates: 6
- winner: `none`
- recommendation: `continue_shadow_collection`
- actual-backed evidence: missing
- production mutation: none

M5 acceptanceはengineとevidence contractの受理であり、challenger採用ではない。

## M6 entry gate

M6は次をすべて満たした場合だけ検討する。

1. proposal-eligibleな候補が存在する
2. comparison basisとvalidation windowが十分である
3. long / short、regime、false warning、missed moveへのmaterial damageがない
4. actual-backed evidenceとの重大な矛盾がない、または矛盾が明示されている
5. bounded UIまたはpolicy proposalが1件に限定されている
6. human approvalがある

M6では次を一括で行わない。

- source変更とruntime apply
-複数proposalの同時採用
- gate / threshold / scoringの広範変更
- mail / notification / launchd変更
- automatic production adoption

## Current action

M route単独のnext implementationはない。

現在はP8 evidence collectionとProduct routeを優先する。新しいmacro evidenceがM5の結論を変える場合にだけ、M6 proposal判断を再開する。

## Canonical references

- overall plan: `docs/operations/ai-orchestration/MASTER_PLAN.md`
- research basis: `MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- accepted M implementation contracts: `chatgpt/specs/archive/20260720_macro_*` and `chatgpt/specs/archive/20260721_macro_*`
- accepted checkpoint summary: `docs/operations/ai-orchestration/MILESTONES.md`
- historical full design: `archive/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md`

## Safety

- report-only
- not `FORMAL_GO`
- no automatic order
- no automatic production mutation
- no automatic threshold or gate application
- no runtime、mail、notification change without separate approval
- human decides all trades and all adoption

## Version promotion boundary

M1–M5 acceptance does not qualify the repository for `Ver05`.

`Ver05` may be proposed only after an M6 change passes the documented entry gate, receives explicit human approval, is implemented and validated in bounded scope, and is accepted by ChatGPT. Until then, macro work remains within the Ver04.x development line.
