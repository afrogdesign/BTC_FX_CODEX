# btc_monitor Master Plan

last_updated: 2026-07-21
status: canonical overall plan

## 1. Product objective

`btc_monitor` の最上位目的は、notification mailを受け取った人間が15分足を確認し、manual trading判断を行うための支援システムを完成させることである。

現段階では次を維持する。

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order

自動売買、production tuning、runtime変更は本計画の通常経路ではない。

## 2. 全体構造

このrepoには、同格の3計画があるわけではない。

```text
本体Product計画
├─ P1〜P9: 本体機能と自己改善loopを完成させる実行Phase
├─ M1〜M6: マクロ構造・次regime・operator判断を補強する追加計画
└─ A1〜A4: ChatGPT/Codex運用を軽量化するために行った補助実験
```

優先順位は常に次の順である。

1. 本体Productを完成させ、利用者に観測可能な価値を増やす
2. safety、scope、acceptance integrityを守る
3. Codex credit、作業時間、重複validationを節約する
4. orchestrationや記録形式を整える

運用整備が本体変更と同等以上の負担になった場合は、運用改善を停止してcompact routeへ戻る。

## 3. 現在の計画状態

### 3.1 Product / P route

本体計画の現在地は次のとおり。

| Phase | 内容 | 状態 |
|---|---|---|
| P1 | actual trade importer contract | accepted |
| P2 | actual trade importer implementation | accepted |
| P3 | trade-to-signal/scenario linking | accepted |
| P4 | scenario identity、coverage、decision events | accepted |
| P5 | offline A/B/C/STOP classifier | accepted |
| P6 | historical replay | accepted |
| P7 | shadow surface | accepted |
| P8 | deterministic evidence pipeline and operating cycle | accepted and collecting evidence |
| P9 | evidence-backed tuning proposal and human review | blocked pending adequate evidence |

現在の主要な不足は、コードの未実装よりも、actual-backed ground truthが不足していることである。

```text
actual trade export
→ importer / episode builder
→ signal / scenario linking
→ proxyとactual PnLの照合
→十分なsample
→ P9 proposal
```

P9 readinessはproduction変更権限ではない。最初にproposalを作り、人間承認後にだけbounded implementationへ進む。

P actual-evidence readiness review is accepted and is a no-repeat boundary. The route is parked until a complete private MEXC Trade History / Order History / Position History batch appears under the ignored canonical input directory, relevant source changes, a contradictory artifact appears, or the user explicitly requests re-verification.

正本:

- `PRODUCT_IMPLEMENTATION_ROUTE.md`
- `CURRENT_STATE.md`
- `DEC-20260721-012` in `DECISIONS.md`
- `docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`

### 3.2 Macro / M route

M計画は本体の15分足判断を、上位足構造、信頼できるsupport/resistance、volatility、next-regime情報で補強する計画である。

| Phase | 内容 | 状態 |
|---|---|---|
| M1 | macro structure evidence layer | accepted |
| M2 | P8 auxiliary shadow | accepted |
| M3 | next-regime offline shadow | accepted |
| M4 | operator hierarchy render shadow | accepted |
| M5 | champion/challenger proposal engine | accepted |
| M6 | human-reviewed runtime proposal | not started and not authorized |

M5の結果:

- winner: `none`
- recommendation: `continue_shadow_collection`
- actual-backed evidence: missing

M5 is already implemented. The next M work is a bounded evidence refresh after a gate-relevant input change, not an engine rewrite.

M6 remains conditional. It starts only after M5 identifies one proposal-eligible challenger and the user explicitly approves one bounded proposal. Source-only shadow, validation, human adoption, and runtime apply are separate tasks.

正本:

- `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md`
- `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md`
- `docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`
- `DEC-20260721-013` in `DECISIONS.md`
- accepted M specs under `chatgpt/specs/archive/`

### 3.3 AI operations / A route

A計画はproduct機能ではなく、長いCodex prompt、重複validation、report確認コストを減らすための運用実験だった。

| Phase | 内容 | 状態 |
|---|---|---|
| A1 | manifest schema / validator / renderer | accepted |
| A2 | low-risk pilot | accepted |
| A3 | manifest/JSON routeを標準化 | superseded and archived |
| A4 | optional CWT integration | not planned |

結論:

- 問題認識は正しかった
- A1 toolingは技術的に有効
- 通常taskへ標準適用すると運用コストが高すぎる
- compact prompt / compact reportが通常経路
- manifest / JSON toolingはheavy、runtime、checkpoint、厳密なmulti-stage taskでのみoptional

A計画は進行中のproduct backlogではない。再開しない限り、新しいA phaseを作らない。

正本:

- `AI_OPERATIONS_STATUS.md`
- `AI_WORKFLOW.md`
- `CONTROL.md`

## 4. 現在の実行方針

P route is parked on human private input. Do not repeat the accepted readiness review.

While the P blocker remains, proceed on the M route only through the accepted evidence-gated sequence:

```text
wait for a gate-relevant M5 input change
→ create one active M5 refresh spec
→ one bounded M5 engine execution
→ ChatGPT MCP review
→ no candidate: park and continue collection
→ one eligible candidate: create one M6 proposal package
→ explicit human approval
→ source-only disabled-by-default shadow
→ matching validation
→ explicit human adoption decision
→ separate runtime apply when approved
```

The default M5 refresh trigger is at least seven new eligible JST dates after the accepted 2026-07-21 cutoff, new P8 actual evidence, an accepted M1/M3 comparison-basis change, or explicit user instruction. This is a replay-cost trigger, not an eligibility threshold.

次を行わない。

- 新しいorchestration frameworkの作成
- A3/A4の再開
- M5 engineの根拠のない再実装
- proposal-eligible candidateなしでのM6開始
- evidence不足のままP9 tuning
- source変更とruntime applyの同一task化
- product変更を細かな複数Codex taskへ分割
- report形式だけを理由とするretask

## 5. AIの標準読取導線

新しいChatGPT threadまたはcontext不明時:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. planningまたはnext-task判断なら `MASTER_PLAN.md`
4. 現在地が必要なら `CURRENT_STATE.md` と `NEXT_ACTION.md`
5. 対象routeだけ読む
   - Product: `PRODUCT_IMPLEMENTATION_ROUTE.md`
   - Macro: `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md`
   - M5/M6 execution: `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md`
   - AI execution: `AI_WORKFLOW.md` と必要時だけ `CONTROL.md`
6. implementation時だけ `chatgpt/specs/active/` の1本を読む

同じthread、同じtaskではstable docsを再読しない。

## 6. 文書の役割

| 文書 | 役割 |
|---|---|
| `MASTER_PLAN.md` | 全体設計、3軸の関係、現在の優先順位 |
| `PRODUCT_IMPLEMENTATION_ROUTE.md` | 本体Productの現在地と次Phase条件 |
| `MACRO_IMPLEMENTATION_ROUTE.md` | M1〜M6の現在地とM6境界 |
| `M5_M6_EXECUTION_PLAN_20260721.md` | M5 evidence refreshからM6 runtimeまでの分離実行計画 |
| `AI_OPERATIONS_STATUS.md` | A計画の結論とoptional toolingの扱い |
| `CURRENT_STATE.md` | 受理済み現在地、blocker、no-repeat boundary |
| `NEXT_ACTION.md` | 現在の作業またはevidence triggerを1件だけ記載 |
| `AI_WORKFLOW.md` | ChatGPT/Codexの実行手順 |
| `CONTROL.md` | stable safety、git、runtime、validation rules |
| `MILESTONES.md` | major accepted checkpoints |
| `DECISIONS.md` | durable decisions and supersession records |

## 7. Archive policy

次は現行導線から外し、archiveへ保存する。

- completedまたはsuperseded plan
- 古いPhase route
- 過去のorchestration experiment
- 一時的なcheckpoint、smoke、review記録

次は削除せず残す。

- accepted active/archive specs
- product/evaluation contract
- research basis
- runtime runbook
- implementation evidence
- git historyとtask reports

Historical fileは調査対象が明確な場合だけ読む。新しいAIはhistoryや`TASK_LEDGER.md`を広く探索しない。

## 8. Safety and approval boundary

人間承認なしで変更しない。

- production policy
- gate、threshold、classifier、scoring
- notification trigger、mail behavior
- runtime、launchd
- API、account、position、order関連
- M6開始
- Phase昇格
- production adoption

最終的なmanual trading判断は人間が行う。

## 9. Version and branch policy

### Ver04-v3

`Ver04-v3` is the current repository and Product/Macro planning line.

Its scope includes accepted repository cleanup, bounded report-only Product corrections, and evidence-gated Macro work without production promotion.

### Ver05 promotion gate

Do not create or declare `Ver05` merely because M1–M5 are accepted or because an M6 shadow source change exists.

`Ver05` promotion requires all of the following:

1. an M6 proposal satisfies the M6 entry gate
2. the selected M6 change is implemented in a bounded scope
3. matching tests and required evidence pass
4. no material Product/P8 contradiction remains hidden
5. human approval is explicit
6. any runtime apply is separately approved and verified when runtime adoption is part of the proposal
7. ChatGPT acceptance is recorded
8. source, tests, current plans, and operator-facing documentation agree on the adopted behavior

Until those conditions are met, the development line remains Ver04.x.
