---
title: M計画・実践的マクロ構造可視化プロダクト計画
date: 2026-07-22
tags:
  - btc_monitor
  - macro-structure
  - product-plan
  - manual-trading
  - report-only
---

> [!abstract]
> 既存のM-OPS分析基盤を再利用し、実際の公開市場データから4時間足中心の大局チャート、信頼度付きレジサポ、トレンドライン、構造イベント、検証可能な仮説を段階的に提供する。最終的に固定された最新画面と既存HTMLメール通知を接続する。完成と実用性を優先し、長時間replay、過剰な健康監査、不要な基盤再設計は行わない。

## 📋 目次

1. [目的](#-目的)
2. [プロダクト判断](#-プロダクト判断)
3. [完成イメージ](#-完成イメージ)
4. [実装原則](#-実装原則)
5. [モジュール構成](#-モジュール構成)
6. [各モジュールの契約](#-各モジュールの契約)
7. [検証方針](#-検証方針)
8. [AI作業導線](#-ai作業導線)
9. [安全境界](#-安全境界)
10. [完成条件](#-完成条件)
11. [現在の次作業](#-現在の次作業)
12. [結論](#-結論)

---

## 🎯 目的

`btc_monitor`の最上位目的は、notification mailを受け取った人間が最新の大局観と15分足を確認し、manual trading判断を行える状態を完成させることである。

この計画のユーザー導線は次の通り。

```text
公開15m / 1h / 4h OHLCVを自動取得
→ 最新の大局構造を計算
→ 4時間足中心の実践的チャートを生成
→ 固定された入口から最新画面を開く
→ 水平レジサポ、斜めライン、構造イベント、仮説を確認
→ 15分足を確認
→ 人間がmanual trading判断
→ 最終段階で既存HTMLメール通知と接続
```

自動注文は行わない。

---

## ✅ プロダクト判断

### 最初に問うこと

> この作業は、ユーザーが実際に利用できる状態に直接影響するか？

直接影響しない作業は、原則として後回しまたは中止する。

### 優先順位

1. 実際に開いて判断に使える画面を完成させる
2. 既存の安全境界と分析契約を守る
3. 小さなモジュール単位で完成させる
4. Codexクレジットと検証時間を節約する
5. 記録や監査形式を必要最小限に保つ

### 完成優先ルール

- 内部metadataの完全性より、画面が正しく開いて読めることを優先する
- 大規模な将来拡張を理由に、現在不要な抽象化を追加しない
- 既存のM-OPS1〜M-OPS5を再実装しない
- 既存の信頼度計算、gate、threshold、classifierを承認なしで変更しない
- 1つのモジュールをacceptしてから次へ進む
- process-onlyの追加FIXを繰り返さない

> [!warning]
> 「より厳密な監査が可能」「将来使える」だけでは実装理由にしない。ユーザー画面の正確性、可読性、利用導線、安全性に直接寄与する場合だけ採用する。

---

## 🖥️ 完成イメージ

最終的なoperator画面は、次の順序で情報を表示する。

```text
1. health / 更新時刻 / report-only表示
2. 4時間足の大局チャート
3. 1H・4H由来の信頼度付き水平レジサポ
4. 確定4Hピボット由来のトレンドライン・チャネル
5. 現在の構造状態と重要イベント
6. 成立条件と否定条件を持つシナリオ仮説
7. 15分足確認エリア
8. 根拠、限界、データ不足表示
```

画面はTradingViewを完全再現するものではない。manual judgmentに必要な大局構造を、最新の実データから自動描画することを目的とする。

---

## 🧩 実装原則

### モジュール分割

各機能は独立したobservable contractを持つモジュールとして実装する。

```text
既存M-OPS基盤
→ M-VIS1
→ M-LINE1
→ M-EVENT1
→ M-HYP1
→ M-ENTRY1
→ M-DELIVERY1
```

前のモジュールがacceptされるまで、次のモジュールを同時実装しない。

### 既存基盤の再利用

再利用するもの。

- public 15m / 1h / 4h OHLCV
- event-time confirmed 1H / 4H pivots
- stable level identity
- horizontal zone clustering
- lifecycle / reliability score / reliability band
- chronological history
- current snapshot
- existing operator HTML
- existing health status
- existing runtime cadence

### 時系列の正しさ

- future-confirmed pivotを過去時点へ遡及表示しない
- ラインや構造イベントには確認可能時刻を持たせる
- 後から都合よく線を引き直さない
- 既存line / zone IDは可能な限り維持する
- broken、failed、invalidatedを消さず、状態として残す

### 表示と分析の分離

- まず既存の分析値を正しく可視化する
- 新しい分析ロジックは別モジュールにする
- UI修正のために信頼度計算を変更しない
- 仮説表示をexecution permissionとして扱わない

---

## 🗂️ モジュール構成

| Module | ユーザー価値 | 主な成果物 | 状態 |
|---|---|---|---|
| M-VIS1 | 4時間足で大局と水平レジサポを直感的に確認 | 4H macro chart HTML | next |
| M-LINE1 | 斜めのトレンドラインとチャネルを確認 | line/channel model + overlay | not started |
| M-EVENT1 | 接触、突破、リテスト、失敗を構造イベントとして確認 | structural event model | not started |
| M-HYP1 | 現在の成立条件・否定条件を持つ仮説を確認 | scenario panel | not started |
| M-ENTRY1 | 毎回同じpathから最新画面を開く | atomic fixed latest entry | not started |
| M-DELIVERY1 | 既存HTMLメールから最新画面へ移動 | approved mail integration | not authorized |
| M-STATS1 | 類似事例の参考頻度を表示 | bounded evidence summary | optional shadow |

M-STATS1は、十分な履歴が蓄積していない場合にプロダクト完成をblockしない。画面には`insufficient evidence`を表示する。

---

## 📐 各モジュールの契約

### M-VIS1：4時間足マクロチャート

#### 目的

最新の4時間足を主表示にし、既存の1H・4H由来レジサポを大局観として理解できる画面を作る。

#### 最小scope

- 4時間足ローソクを主チャートとして表示
- 現在価格を表示
- 既存のhigh / medium水平ゾーンを表示
- 各ゾーンへ`4H`または`1H+4H`を明示
- support / resistance、reliability band、lifecycleを明示
- 更新時刻、cutoff、health、report-onlyを表示
- 15分足は補助確認エリアとして残すか、既存画面への明確な導線を付ける
- immutable artifactを維持
- 生成失敗時に正常な既存artifactを壊さない

#### 対象外

- トレンドライン
- 波動番号
- 統計確率
- mail変更
- runtime変更
- 既存信頼度ロジック変更

#### acceptance

- 4時間足が主チャートであることが一目で分かる
- 水平ゾーンが15分足由来に見えない
- zone source timeframeが読める
- 最新実データとartifactのcutoffが一致する
- 1回のsmall deterministic smokeで表示確認できる

---

### M-LINE1：トレンドライン・チャネル

#### 目的

確定済み4Hスイングから、再現可能な斜めラインとチャネル候補を描画する。

#### 最小scope

- confirmed 4H swing lowから上昇サポートライン候補を作る
- confirmed 4H swing highから下降レジスタンスライン候補を作る
- anchor、confirmation time、slope、touch countを保持
- active / tested / broken / invalidatedを区別
- line IDを安定維持
- 現在価格との距離を表示

#### 対象外

- 人間が自由に引いた線の完全再現
- Elliott Wave自動認定
- 自動売買判断
- 大量parameter探索

#### acceptance

- 同じ入力から同じラインが生成される
- future pivotを使用しない
- anchorとconfirmation timeを追跡できる
- broken lineを正常lineとして表示しない
- 視覚的に過密な場合は重要候補だけを表示する

---

### M-EVENT1：構造イベント

#### 目的

ラインやゾーンへの反応を、人間が読みやすい構造イベントへ変換する。

#### 最小scope

- approach
- touch / test count
- clean rejection
- break
- closed-candle acceptance
- retest
- retest hold / failure
- false break / reclaim
- higher high / higher low
- lower high / lower low

イベントは、水平ゾーンと斜めラインの双方を対象にできる設計とする。

#### acceptance

- event timeが明示される
- 同じ事象を重複計上しない
- 現在進行中と確定済みを区別する
- chart overlayとイベント一覧が同じIDを参照する

---

### M-HYP1：シナリオ仮説

#### 目的

現在の構造から、成立条件・否定条件を持つ少数のシナリオを表示する。

#### 表示例

```text
Continuation candidate
- 条件: 4H終値で上側ラインを維持
- 次確認: retest hold
- 否定: 4H終値で旧レンジへ回帰

Failed breakout candidate
- 条件: 上抜け後にゾーン内へ回帰
- 次確認: reclaim-down継続
- 否定: 再度4H終値で上側定着
```

#### ルール

- 最大3シナリオ程度に制限
- probabilityと断定しない
- 条件、確認、否定を必須にする
- データ不足時は`insufficient evidence`
- manual decision supportでありentry signalではない

#### acceptance

- 仮説が現在のline / zone / event IDに紐づく
- 否定条件が必ず表示される
- 同時に矛盾する断定を出さない
- execution permissionに見える表現を避ける

---

### M-ENTRY1：固定latest入口

#### 目的

ユーザーが毎回同じpathを開き、最新のcomplete operator画面を確認できるようにする。

#### 予定path

```text
local/reports/macro_structure/operator/latest.html
```

または同等の固定path。

#### ルール

- completed artifactだけを公開対象にする
- atomic replacement
- immutable artifactを維持
- failed / inconsistent / unavailable時に古い正常画面を無条件で「最新正常」と誤認させない
- `open <fixed-path>`で開ける
- JavaScript fetch依存を避ける

M-VIS1の実装方式によっては、固定入口を同時に最低限作ることを許容する。ただし、mailやruntime変更は含めない。

---

### M-DELIVERY1：HTMLメール統合

#### 開始条件

以下がacceptされた後に、別の明示承認taskとして開始する。

- M-VIS1
- M-LINE1
- M-EVENT1
- M-HYP1
- M-ENTRY1

#### 決定事項

- 受信端末が分析Macと同一か別か
- local file linkを使用できるか
- 画像埋め込み、添付、ローカルWeb配信のどれを使うか
- health stateごとの送信条件
- duplicate suppression
- failed / inconsistent時の通知

> [!danger]
> M-DELIVERY1までは、既存mail、notification、LaunchAgent、scheduleを変更しない。

---

### M-STATS1：類似事例の参考評価

M-STATS1はshadowで蓄積し、ユーザー画面完成を待たせない。

想定出力。

- structure type
- line / zone test count
- break / retest状態
- 6H / 12H / 24Hのその後
- continuation / rejection / indeterminate
- sample count
- evidence strength

少数事例では比率を強調せず、`insufficient evidence`とする。

---

## 🧪 検証方針

### 通常モジュール

- matching unittest
- 必要なsmall deterministic fixture
- 1回のbounded smoke
- task-scoped `git diff --check`
- 生成artifactの最小目視確認

### 完了条件にしないもの

- full test suite
- 全期間replay
- 複数parameterの大規模探索
- 2回目の同一heavy replay
- 長時間background process
- runtimeを何度も起動してhealthを観測すること
- metadata、fingerprint、review bundleの完全性だけを目的とする追加作業

### Heavy validation

次の作業は、ChatGPTがacceptance-criticalと判断し、明示承認した場合だけ行う。

- 10件を超えるreplay / evaluation unit
- 複数candidate、複数dateのfull bundle
- 2回目のfull replay
- 長時間background process
- installed runtime / launchdの検証cycle

### バグ対応

- material defectのみ1回のFIXを基本とする
- report形式、文言、順序の軽微な差だけで再task化しない
- 2回目のprocess-only修正が必要なら方式を簡素化する

> [!tip]
> 各モジュールのacceptanceは、内部証跡の量ではなく「実データで期待する画面・状態が観測できるか」を中心に判断する。

---

## 🤖 AI作業導線

### 新しいChatGPT thread

最初に読む。

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `docs/operations/ai-orchestration/CURRENT_STATE.md`
4. `docs/operations/ai-orchestration/NEXT_ACTION.md`
5. `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`

必要な場合だけ読む。

- 対象moduleのsource
- matching tests
- current artifact
- `MACRO_IMPLEMENTATION_ROUTE.md`
- `AI_WORKFLOW.md`
- `CONTROL.md`

### ChatGPTの役割

- ユーザー価値の確認
- 現在moduleのscope固定
- observable contractの固定
- product / trading / safety判断
- source、test、artifactのMCP review
- acceptance判断
- 次moduleへの移行判断
- plan、state、specの小さなMarkdown更新

### Codexの役割

- 固定scope内のsource実装
- matching tests
- small deterministic smoke
- task-scoped validation
- task filesだけのlocal commit
- compact report

Codexへproduct判断、broad exploration、次module選択、mail/runtime判断をさせない。

### 通常経路

```text
ChatGPTが現在moduleのscopeを固定
→ 1回のbounded Codex implementation
→ matching tests + small smoke
→ local commit
→ compact report
→ ChatGPTがchanged source / tests / artifactをMCP review
→ accept またはmaterial FIX 1回
→ CURRENT_STATE / NEXT_ACTIONを更新
```

### 読み直し制限

同じthread、同じmoduleではstable docsを再読しない。確認対象は次だけにする。

- 新しいCodex report
- changed source
- matching tests
- CLI route
- fresh artifact
- task-related diff

---

## 🔒 安全境界

必ず維持する。

- report-only
- human decides manually
- no automatic order
- no API keys or secrets
- no private / account / order endpoints
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration
- no unapproved runtime / launchd / mail / notification change
- no gate / scoring / threshold / classifier change without approval
- no automatic phase promotion or production adoption
- no future-confirmed pivot backdating

---

## 🏁 完成条件

### Product v1 completion

次を満たした時点で、M計画のユーザー向けvisual product v1を完成とする。

- 4時間足が主役の最新大局チャートが生成される
- 1H・4H由来の水平レジサポが明確に読める
- 重要なトレンドライン / チャネルが再現可能に描画される
- 接触、突破、リテスト、失敗が構造イベントとして読める
- 少数の条件付き仮説と否定条件が表示される
- データ不足は明示される
- 固定pathから最新complete画面を開ける
- immutable artifactとatomic publicationが維持される
- 15分足manual判断への導線がある
- no automatic order

M-STATS1の十分なsample蓄積は、Product v1 completionをblockしない。

### Delivery completion

Product v1 acceptance後、別承認のM-DELIVERY1で次を満たす。

- HTMLメールから最新画面または埋め込みチャートへ移動できる
- health stateが利用者に分かる
- duplicate送信を防止する
- failed / inconsistent時に誤った正常通知をしない

---

## ▶️ 現在の次作業

次のimplementation moduleは`M-VIS1`とする。

```text
既存のM-OPS1 snapshotとoperator sourceを再利用
→ 4H macro chart modelを追加
→ 1H / 4H水平ゾーンの生成元を明示
→ 実用的な4H-first HTMLを生成
→ matching unit test
→ small deterministic smoke
→ local commit
```

実装時に変更してよい範囲は、ChatGPTがsourceとtestsを確認してからbounded taskとして固定する。

M-LINE1以降、runtime、schedule、mail、notificationはM-VIS1 taskへ含めない。

---

## 📌 結論

| 項目 | 決定 |
|---|---|
| 最優先 | 実データから生成する4時間足中心の大局チャート |
| 実装方式 | 小さなmoduleを1つずつacceptして進める |
| 既存分析 | M-OPS1〜M-OPS5を再利用し、不要に再実装しない |
| 検証 | matching test、small fixture、1回のbounded smoke |
| 長時間作業 | 原則禁止。明示承認されたacceptance-critical runのみ |
| 仮説 | 条件・確認・否定を持つreport-only scenario |
| 統計 | sample不足を明示し、完成をblockしない |
| 固定入口 | complete artifactだけをatomicに公開 |
| メール統合 | visual product v1完成後の別承認task |
| 注文 | 自動注文なし。人間がmanual判断 |
