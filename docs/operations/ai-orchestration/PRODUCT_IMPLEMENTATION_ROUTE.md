# Product Implementation Route

last_updated: 2026-07-25
status: canonical product route

## 1. Objective

notification mailを受け取った人間が15分足を確認し、manual trading判断を行うための支援システムを完成させる。

```text
notification triage
→ 15m chart check
→ human action: enter / wait / watch / stop / exit
→ deterministic outcome evaluation
→ actual trade ground truth
→ evidence-backed improvement proposal
```

現段階はreport-onlyであり、自動注文システムではない。

## 2. Product doctrine

- mailはtriage / chart-check trigger
- chartとpublic HTMLが主要operator surface
- mail / HTML / dashboardはsingle-source doctrineを守る
- A/B/C/STOPはoperator action layerであり、formal gateの置換ではない
- signal rowと独立scenarioを区別する
- proxy outcomeとactual PnLを区別する
- tuningはproposal-first、human-approved、reversible

既存gate、threshold、classifier、scoringを承認なしで変更しない。

## 3. Current phase status

| Phase | Scope | Status |
|---|---|---|
| P0 | planning and routing | completed |
| P1 | actual trade importer contract | accepted |
| P2 | importer implementation and hardening | accepted |
| P3 | trade episode and signal/scenario linkage | accepted |
| P4 | scenario identity、coverage、decision events | accepted |
| P5 | offline A/B/C/STOP classifier | accepted |
| P6 | historical replay | accepted |
| P7 | shadow surface | accepted |
| P8 | automated evidence collection and exception review | accepted / operating evidence collection |
| P9 | evidence-backed tuning review | blocked pending readiness and human approval |

P1〜P7を新規実装taskとして再開しない。修正が必要な場合は、現行sourceとaccepted archive specを確認してbounded FIXとして扱う。

## 4. Current product gap

現在の不足はactual-backed ground truthの不存在ではなく、量、side/setup coverage、confidence、validation windowである。canonical actual inputはprovidedであり、episodes/linksは149/149、current eligible rowsは2（high 0、medium 2）である。

実装済み基盤:

- actual trade importer
- fillからposition episodeを作るbuilder
- actual tradeとsignal/scenarioのlinker
- scenario normalization / duplicate compression
- A/B/C/STOP offline classifier
- historical replay
- P8 deterministic operating cycle
- issue register and review queue

不足しているもの:

- 継続的なactual trade export
- actual episodeの十分な件数
- high / medium confidence link coverage
- proxy outcomeとactual PnLの比較sample
- side / regime / setup別の安定したvalidation window
- P9 proposalを判断できるevidence量

actual tradeとmarket-path proxyは引き続き分離する。resolved proxy 40、unresolved proxy 4はactual PnLの代替ではない。

Product P9は`program=P`, `phase=P9`。Macroの`macro_p9_proposal_engine.v1`は`program=M`のM5/M6 improvement proposalであり、本routeのP9ではない。

## 5. P8 operating route

```text
event-time prediction snapshot
→ scenario identity
→ public OHLCV outcome resolution
→ trial fact view
→ issue detection
→ actual trade import when available
→ episode / signal link
→ proxy-vs-actual calibration
→ exception-only human review
```

人間へ全件入力を求めない。人間確認はambiguous link、重要なno-trade理由、UI誤解など自動判定できない例外に限定する。

正本:

`docs/operations/strategy/P8_P9_EVIDENCE_TUNING_OPERATING_SPEC_20260711.md`

## 6. P9 entry boundary

P9は次を満たした場合だけproposal作成へ進む。

- deterministic evidenceが十分
- data leakage、future contamination、duplicate countingがない
- side / regime / setup別sampleが評価可能
- actual-backed evidenceが存在する、または不足が明示される
- candidate changeがoffline replay可能
- human approval boundaryが明確

P9 readinessは次を許可しない。

- automatic tuning
- production mutation
- gate / threshold変更
- runtime、mail、notification変更
- automatic phase promotion

## 7. Current next-task selection

WP0はaccepted。WP1はFIX1と、既存内容を保持した`NEXT_ACTION.md`のprecedence reconciliationを完了してacceptedである。

`WP2 — Semantic Identity and Versioning`が唯一のauthorized next packageである。WP2はreport-only/spec-firstとしてidentity、generation、schema/method version、legacy separation、comparison boundariesを定義する。production behavior、gate、classifier decisions、thresholds、scoring、notifications、mail、runtime、Product P9 state、ordersは変更しない。

## 8. Related routes

- overall plan: `MASTER_PLAN.md`
- macro support route: `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md`
- current state: `CURRENT_STATE.md`
- immediate task: `NEXT_ACTION.md`
- accepted implementation contracts: `chatgpt/specs/archive/`
- historical P plans: `history/plan-archive-20260721/` and `docs/operations/strategy/archive/`

## 9. Safety

- report-only
- not `FORMAL_GO`
- human-decided
- no automatic order
- no private/account/order endpoints
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration
- no gate、threshold、scoring、classifier変更 without human approval
- no runtime、launchd、mail、notification変更 without explicit task and approval
