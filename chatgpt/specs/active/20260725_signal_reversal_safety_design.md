---
title: "BTC Monitor 方向反転誤判定・実行表示安全化 改善設計書"
date: 2026-07-25
tags:
  - btc-monitor
  - design
  - safety
  - market-map
  - scoring
  - operator-ui
status: design-fixed
work_id: P-SAFETY-REVERSAL-1
target_branch: Ver04-v4
---

> [!abstract]
> 2026-07-24 21:05 JST の通知で、内部の方向スコアが `LONG 100 / SHORT 2` まで反転した一方、同じレポート内では `WAIT`、実行スコア35、15分足ショート、ショート優先、両側 `STOP_OR_EXIT` が成立していた。
> 本設計書は、単発の15分足反発を「確認済み上昇転換」へ過大昇格した判定、同一イベントの重複加点、数値スコアと実行可否の表示混同を、最小かつ一貫した修正で解消する実装契約である。
> 目的は後知恵で21:05を強制的にショートへ書き換えることではない。**誤った反転確定、スコアの過剰増幅、実行不可なのに数値が売買許可に見える状態を再発させないこと**を確実なゴールとする。

## 📋 目次

- [1. 設計書の位置づけ](#1-設計書の位置づけ)
- [2. 事故の再現事実](#2-事故の再現事実)
- [3. 根本原因](#3-根本原因)
- [4. 改善の基本原則](#4-改善の基本原則)
- [5. 用語と判定優先順位](#5-用語と判定優先順位)
- [6. 改善設計](#6-改善設計)
- [7. 変更対象と変更禁止範囲](#7-変更対象と変更禁止範囲)
- [8. 受け入れ条件](#8-受け入れ条件)
- [9. テスト設計](#9-テスト設計)
- [10. CODEX実行コストの制約](#10-codex実行コストの制約)
- [11. 実装順序](#11-実装順序)
- [12. 停止条件](#12-停止条件)
- [13. 完了報告](#13-完了報告)
- [14. 次スレッドへの引き継ぎ](#14-次スレッドへの引き継ぎ)
- [15. 完了定義](#15-完了定義)

---

## 1. 設計書の位置づけ

| 項目 | 内容 |
|---|---|
| Work ID | `P-SAFETY-REVERSAL-1` |
| 対象リポジトリ | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` |
| 対象ブランチ | `Ver04-v4` |
| 調査時のHEAD locator | `f08a815` |
| 設計状態 | `design-fixed / implementation-pending` |
| 実装方式 | 1回の bounded CODEX task |
| 想定モデル | `GPT-5.4-mini Medium` |
| 本番変更 | 未承認・禁止 |
| 自動注文 | 禁止 |
| Push | 禁止 |

> [!info]
> 本設計書は `P-SAFETY-REVERSAL-1` の原因、修正範囲、判定契約、受け入れ条件を固定する。
> CODEXは実装方法や小さな純粋関数の配置を選べるが、ここに記載した意味、優先順位、安全境界、検証上限を変更してはならない。

### 1.1 既存状態の扱い

- 作業開始時点のリポジトリには、本件と無関係な未コミット変更が存在する。
- CODEXは既存の変更を消去、整理、退避、復元してはならない。
- `reset`、`restore`、`checkout`、`clean`、stashのapply/pop/dropは禁止する。
- 本件に必要なファイルだけを読み、変更し、stageする。
- `CURRENT_STATE.md`、`NEXT_ACTION.md`、既存active specは、本件実装では自動更新しない。
- 本設計書は他のMacro・Delivery系specを置き換えない。本件の方向判定と表示安全化だけを制御する。

### 1.2 本タスクで行わないこと

本設計書の作成時点では、ソース修正、テスト実行、runtime再起動、通知送信、公開ページ更新は行わない。
次スレッドで、ここに固定した内容を1回の実装タスクとしてCODEXへ渡す。

---

## 2. 事故の再現事実

### 2.1 20:05と21:05の比較

| 項目 | 2026-07-24 20:05 | 2026-07-24 21:05 |
|---|---:|---:|
| signal_id | `20260724_110500` | `20260724_120500` |
| 現在値 | 64,926.3 | 65,045.7 |
| 1時間の価格変化 | - | +119.4、約+0.18% |
| 4時間足 signal | `wait` | `wait` |
| 1時間足 signal | `wait` | `wait` |
| 15分足 signal | `short` | `short` |
| score bias | `short` | `long` |
| Long raw score | -16.0 | 55.0 |
| Short raw score | 36.0 | -28.0 |
| display score | Long 18 / Short 82 | Long 100 / Short 2 |
| score gap | -64 | +98 |
| market_map | `confirmed_down` | `confirmed_up` |
| detail page | `WAIT` | `WAIT` |
| 実行スコア | 23 | 35 |
| side-aware優先 | Short | Short |
| shadow operator class | 両側 `STOP_OR_EXIT` | 両側 `STOP_OR_EXIT` |

価格が約0.18%上昇した1回の更新で、score gapは `-64` から `+98` へ合計162点反転した。
これは連続的な相場評価ではなく、Market Mapの方向フラグが境界をまたいだことで発生した不連続な状態遷移である。

### 2.2 21:05のユーザー向け矛盾

21:05レポートには、同時に次の情報が表示されていた。

- 結論は `WAIT`
- 通常監視・実行不可
- 実行スコア35
- 15分足 signal は `short`
- side-aware表示は「ショート優先：15分足で戻りを確認」
- ショート優先度は高
- ロング優先度は低
- Long・Shortともに `STOP_OR_EXIT`
- それにもかかわらず、Longカードに「短期実行スコア 100」と大きく表示

> [!danger]
> 数値の計算だけでなく、**表示上の意味付けが事故要因**である。
> `100`が勝率や実行許可ではないとしても、「短期実行スコア」という名称と視覚的な強調により、ユーザーがロング実行の根拠として解釈するのは自然だった。
> 修正は判定ロジックと表示階層の両方に必要である。

### 2.3 今回の主因ではないもの

| 候補 | 判定 | 理由 |
|---|---|---|
| 未確定15分足 | 主因ではない | `fetch_klines`はサーバー時刻より後に終了する未確定足を除外する |
| AI文章生成だけの誤読 | 主因ではない | 元JSONの時点で `bias=long`、`long_raw_score=55`、`display=100` |
| 注文板だけの誤判定 | 主因ではない | 反転の主成分はMarket Map、EMA、1H構造、重複加点 |
| 後から価格が下がったこと | 修正根拠にしない | 後知恵で特定方向へ最適化すると別の誤判定を作る |

---

## 3. 根本原因

### 3.1 原因一覧

| ID | 原因 | 直接影響 |
|---|---|---|
| C1 | ロール転換判定に厳格な時系列がない | breakとretestが同じ足、逆順、または不十分な並びでもconfirmedになり得る |
| C2 | 単発のfailed breakoutを1H構造だけでconfirmedへ昇格 | 15Mがshortのままでも`confirmed_up`になった |
| C3 | 同一反発イベントを複数の独立根拠として加点 | Long加点とShort減点が同時に過剰増幅 |
| C4 | 同一位置リスクをgeneric判定とMarket Mapで二重減点 | 主要サポート・レジスタンス接近の影響が重複 |
| C5 | 過大なMarket Mapフラグが方向トリガーへ伝播 | setup生成と実行候補にも誤方向の影響が連鎖 |
| C6 | raw scoreの表示正規化が上限に飽和 | raw 55が100、raw -28が2となり確定値のように見えた |
| C7 | 数値スコアがSTOP・WAITより強く表示 | 内部では実行不可でもユーザーには実行推奨に見えた |

### 3.2 C1：ロール転換の時系列不足

現状は、最近の複数足に対して概ね次のような条件で判定している。

```text
broke = 期間内のどこかにブレイク終値がある
retested = 期間内のどこかに再接触・新しい側での終値がある
broke and retested => confirmed
```

この方式では以下を区別できない。

- retestがbreakより前に発生した
- breakとretestが同じ足で成立した
- 一度だけ上へ戻ったが、その後保持していない
- 過去の古いbreakと直近の別イベントを結合した

本来必要なのは、`break < retest < hold` の順序である。

### 3.3 C2：上位構造による過大昇格

21:05では次が同時に成立していた。

```text
signals_4h = wait
signals_1h = wait
signals_15m = short
structure_1h = hh_hl
failed_breakout_state = up_reversal
```

現状のtrend flip判定は、上方向トリガーと `structure_1h=hh_hl` があれば `confirmed_up` まで昇格できる。
15分足signalが明示的に反対の `short` であることは、confirmedへの昇格を止めていない。

### 3.4 C3：同一反発イベントの重複加点

21:05では、ほぼ同じ下抜け失敗・支持化イベントから以下が同時に生成された。

```text
failed_breakout_up_reversal
major_support_rejection
resistance_to_support_flip
resistance_to_support_retest_confirmed
trend_flip_confirmed_up
```

これらが独立した証拠として加算され、同一イベントだけで概ね次の差が生じた。

```text
Long側  大幅加点
Short側 大幅減点
```

フラグを説明用に複数保持すること自体は問題ではない。
問題は、相関が高い同一系列のフラグを、独立事象としてすべてスコアへ加算したことである。

### 3.5 C4：位置リスクの二重計上

次の組み合わせは同じ位置情報を表す。

- Long側：`near_resistance_penalty` と `long_into_major_resistance`
- Short側：`near_support_penalty` と `short_into_major_support`

現在は両方が加算されるため、同じサポート・レジスタンス接近が二重に効く。

### 3.6 C5：方向トリガーへの連鎖

Market Mapの`*_flip`系フラグは、スコアだけでなく方向トリガー判定にも使用される。
したがって誤ったearly/confirmed判定は、次へ連鎖する。

```text
Market Map誤判定
→ directional trigger
→ setup trigger_ready
→ candidate / action表示
```

表示だけを直しても、内部候補生成への誤方向伝播が残るため不十分である。

### 3.7 C6：表示スコアの飽和

表示値は概ね次の式で正規化される。

```text
display = clamp((raw + 30) / 80 * 100, 0, 100)
```

21:05では次の結果になった。

```text
Long raw 55  → 106.25 → clamp 100
Short raw -28 → 2.5 → 約2
```

`100`は勝率・確率・実行適性ではなく、表示範囲の上限に達した値である。

### 3.8 C7：判定の優先順位が画面で逆転

本来の優先順位は以下である。

```text
STOP / gate / WAIT
→ side-aware 15M行動
→ 実行しやすさ
→ 中期構造・方向スコア
```

実際の画面では、方向スコア100が大きく表示され、STOP・WAIT・実行不可が分散していた。
このため人間が一つの数値だけを行動指示として読む余地が生まれた。

---

## 4. 改善の基本原則

### 4.1 後知恵で方向を固定しない

21:05以降に価格が下落した事実だけを理由に、21:05を必ずShortへ変換するルールは作らない。
修正対象は以下である。

1. 不十分な証拠を`confirmed`へ昇格しない
2. 同一イベントを重複加点しない
3. 方向スコアを実行許可として表示しない
4. 方向が競合する時はfail-closedでWAITにする

### 4.2 方向・実行・安全を分離する

- 方向スコア：市場構造上の相対的な傾き
- 実行判断：15分足、価格帯、setup状態
- 安全判断：gate、STOP、no-trade、競合

これらを一つの数値へ混ぜない。

### 4.3 genuine reversalを消さない

厳格化によって本物の転換を完全に見失わないよう、状態を段階化する。

```text
event / early
→ ordered retest
→ hold
→ confirmed
```

証拠不足は`early`として残し、実行トリガーだけを止める。

### 4.4 新しい閾値を増やさない

- 既存のATR break thresholdを維持する
- 既存のretest toleranceを維持する
- 既存のスコア重みを原則維持する
- 既存のgate thresholdを変更しない
- 新しい機械学習モデルを導入しない

今回変えるのは、**順序、成熟段階、重複排除、表示意味**である。

### 4.5 計算量と運用コストを増やさない

- 既存の短い15分足window内だけを走査する
- ネットワーク取得を追加しない
- 新しいDBや状態ファイルを作らない
- 複数サイクルの常駐状態機械は作らない
- AI API呼び出しを追加しない
- runtime health監視を追加しない

> [!tip]
> cross-cycleの複雑なヒステリシスではなく、同一の確定足window内で `break < retest < hold` を要求する。
> これにより、永続状態を増やさず反転の安定性を上げる。

---

## 5. 用語と判定優先順位

### 5.1 固定用語

| 用語 | 本設計での意味 | 売買許可か |
|---|---|---|
| raw score | 個別要素を加算した内部方向値 | いいえ |
| display score | raw scoreを0–100へ変換した表示値 | いいえ |
| structural priority | 4H / 1Hの中期構造優先度 | いいえ |
| execution readiness | 15M・価格帯・setupから見た実行しやすさ | 単独では不可 |
| operator class | `STOP_OR_EXIT`、`B_CHECK_15M`等の人間向け分類 | 安全判断の一部 |
| operator decision | 方向、実行、gate、競合を統合したユーザー向け最終表示状態 | 最上位の表示情報 |
| early | 反転イベントはあるが確認手順が未完了 | 不可 |
| confirmed | 順序・保持・時間足整合を満たした状態 | それでもgate確認が必要 |

### 5.2 ユーザー向け判定の優先順位

| 優先 | 情報 | 表示上の扱い |
|---:|---|---|
| 1 | no-trade、trade gate、STOP | 新規見送りを最優先表示 |
| 2 | operator decision | `WAIT`、方向競合、15M確認等を決定 |
| 3 | side-aware primary side | 監視する側を示す |
| 4 | execution readiness | 入りやすさを補助表示 |
| 5 | structural priority | 中期背景として表示 |
| 6 | raw/display score | 診断値として小さく表示 |

> [!warning]
> 数値が100でも、優先順位1～3が見送りなら実行不可である。
> この優先順位をHTML、件名、要約で統一する。

---

## 6. 改善設計

### 6.1 Market Mapのロール転換を時系列化する

#### 6.1.1 confirmedの必須順序

上方向へのレジスタンス→サポート転換は、同一の対象レベルについて以下をすべて満たす場合だけconfirmedとする。

1. `break_idx`
   - 終値がレジスタンス上端を既存break threshold以上上回る
2. `retest_idx > break_idx`
   - 後続の別足が対象レベルへ戻る
   - 安値が既存retest tolerance内へ接触する
   - 終値はレジスタンス上端より上を維持する
3. `hold_idx > retest_idx`
   - さらに後続の別足が対象レベル上で終値を維持する

下方向へのサポート→レジスタンス転換は対称条件とする。

```text
break_idx < retest_idx < hold_idx
```

同一足が複数段階を兼ねることは禁止する。

#### 6.1.2 earlyの扱い

| 観測状態 | 出力 |
|---|---|
| breakのみ | `*_early` |
| break後にretestしたがhold未完了 | `*_early` |
| break・retest・holdが順序通り | `*_confirmed` |
| retestがbreakより前 | 判定材料にしない |
| 同じ足でbreakとretest | confirmed禁止 |
| 反対側へ終値が戻った | early失効またはconflict |

#### 6.1.3 診断メタデータ

`level_flip_reference`には、既存レベル情報に加え、少なくとも次の証拠を持たせる。

```text
confirmation_stage: early | confirmed
break_index
retest_index
hold_index
```

indexは使用したbounded window内の相対indexでよい。
新しい永続ファイルやtimestamp DBは作らない。

#### 6.1.4 決定性

- 候補レベルの既存優先順を維持する
- 同じ入力では同じレベル・同じindex列を返す
- window全体を何度も再走査せず、候補ごとに前方走査する
- 計算量は既存の候補数と短いwindowに対するbounded `O(levels × bars)` とする

### 6.2 failed breakoutとMTF確認を段階化する

#### 6.2.1 failed breakoutの意味

`failed_breakout_up_reversal` / `failed_breakout_down_reversal` は、直近足で反転イベントが観測されたことを示す。
これだけで`confirmed_up` / `confirmed_down`へ昇格してはならない。

#### 6.2.2 per_tf_inputsへsignalを渡す

`main.py`でMarket Mapへ渡す各時間足のpayloadに、既存の`structure`だけでなく既存計算済みの`signal`を追加する。

```text
4h: structure + signal
1h: structure + signal
15m: structure + signal
```

新しい指標計算やデータ取得は行わない。

#### 6.2.3 confirmed_up

`confirmed_up`は、少なくとも以下を満たす場合だけ許可する。

- 上方向のordered role flipがconfirmed
- 15分足signalが`long`
- 1時間足が以下のいずれかで上方向を支持
  - signalが`long`
  - structureが`hh_hl`
- 反対方向のMarket Map conflictがない

#### 6.2.4 confirmed_down

`confirmed_down`は対称条件とする。

- 下方向のordered role flipがconfirmed
- 15分足signalが`short`
- 1時間足signalが`short`、またはstructureが`lh_ll`
- 反対方向のMarket Map conflictがない

#### 6.2.5 明示的な時間足競合

次の場合はconfirmedへ昇格させず、earlyとconflictを記録する。

```text
上方向候補 and signals_15m=short
下方向候補 and signals_15m=long
```

追加するreason / conflict codeは意味が明確な固定名とする。
推奨名：

```text
opposite_15m_signal_conflict
```

4H・1Hがともに`wait`で、15Mが反対方向の場合は、ユーザー向けoperator decisionを必ずWAITにする。

### 6.3 Market Mapから方向トリガーへの伝播を制限する

Market Mapだけでdirectional triggerを起動できるのは、confirmed証拠に限定する。

#### Up triggerに使用可能

```text
resistance_to_support_retest_confirmed
trend_flip_confirmed_up
```

#### Down triggerに使用可能

```text
support_to_resistance_retest_confirmed
trend_flip_confirmed_down
```

#### 単独ではtriggerに使用しない

```text
resistance_to_support_flip
support_to_resistance_flip
failed_breakout_up_reversal
failed_breakout_down_reversal
major_support_rejection
major_resistance_rejection
trend_flip_early_up
trend_flip_early_down
```

これらはwatch・warning・early evidenceとして保持する。

明示的な`breakout_up/down`や、既存の方向付き高出来高ローソク条件は維持する。

### 6.4 相関する反転スコアを一つの証拠ファミリーへ圧縮する

#### 6.4.1 Up reversal family

```text
failed_breakout_up_reversal
major_support_rejection
resistance_to_support_flip
resistance_to_support_retest_confirmed
trend_flip_early_up
trend_flip_confirmed_up
```

#### 6.4.2 Down reversal family

```text
failed_breakout_down_reversal
major_resistance_rejection
support_to_resistance_flip
support_to_resistance_retest_confirmed
trend_flip_early_down
trend_flip_confirmed_down
```

#### 6.4.3 加点ルール

- 元の各フラグと既存weightは説明・候補計算のため保持する
- 同じfamily内では、sideごとに絶対値が最大の1要素だけをraw scoreへ適用する
- 残りは説明用フラグとして保持するが、raw scoreへ再加算しない
- `top_positive_factors` / `top_negative_factors`には適用済み要素だけを含める
- suppressed要素を診断できる小さなメタデータを返す

推奨出力：

```text
score_evidence_families
score_correlation_suppressed
```

実装上の具体的な辞書形状はCODEXが選べるが、以下は必須である。

- family名
- side
- applied code
- applied delta
- suppressed codes

#### 6.4.4 両方向familyが同時成立した場合

- Up・Down両familyの方向加点を適用しない
- `market_map_direction_conflict`をwarningまたはno-trade診断へ追加する
- operator decisionはWAITにする
- どちらか一方を任意に選ばない

### 6.5 位置リスクの二重計上を止める

#### Long側

| 意味 | 候補要素 | 適用上限 |
|---|---|---:|
| サポート接近の利点 | `near_support` | 1回 |
| レジスタンス接近の不利 | `near_resistance_penalty` / `long_into_major_resistance` | 合計1回 |

#### Short側

| 意味 | 候補要素 | 適用上限 |
|---|---|---:|
| レジスタンス接近の利点 | `near_resistance` | 1回 |
| サポート接近の不利 | `near_support_penalty` / `short_into_major_support` | 合計1回 |

サポートとレジスタンスが近接しているレンジでは、利点と不利が一つずつ共存してよい。
同じ不利要素をgenericとMarket Mapで二重に引くことだけを禁止する。

### 6.6 display scoreの飽和を明示する

このタスクではdisplay正規化式と既存thresholdを変更しない。
代わりに次を実施する。

- raw値が表示上限・下限でclampされたことを診断可能にする
- 0または100を確率として説明しない
- UIでは`方向スコア`として表示する
- 上限到達時は「上限値」または同等の注記を付ける
- STOP / WAIT時は数値を視覚的に弱める

推奨診断名：

```text
long_display_saturated
short_display_saturated
```

### 6.7 operator decisionをユーザー向けの唯一の行動ソースにする

#### 6.7.1 目的

内部の`bias`を直ちに全下流ロジックから除去するのではなく、互換性を維持したまま、ユーザー向け表示に一つの正規化された判定を追加する。

`bias`は「score bias」として残す。
売買行動の表示は、新しい`operator_decision`を使用する。

#### 6.7.2 生成タイミング

`main.py`で以下の後、通知判定・要約生成の前に生成する。

```text
_attach_side_aware_mtf_action
_attach_structural_priority
→ attach operator_decision
→ should_notify
→ notification/display/summary
```

通知の発火条件、cooldown、重複抑止、送信先、送信回数は変更しない。

#### 6.7.3 入力

- score bias
- Long / Short display score
- 4H / 1H / 15M signal
- side-aware primary side
- side-aware action class / state
- trade execution gate
- no-trade flags
- primary setup status
- Market Map conflict

#### 6.7.4 必須出力

```text
schema_version: operator_decision.v1
state: blocked | direction_conflict | check_15m | watch_zone | conditional_candidate | wait
primary_side: long | short | none
score_bias: long | short | wait
new_entry_blocked: true | false
direction_conflict: true | false
reason_codes: [...]
```

#### 6.7.5 primary_sideの決め方

1. 有効なside-aware primary side
2. なければ15M signal
3. それもなければ、競合がない場合のみscore bias
4. 判断できなければ`none`

#### 6.7.6 direction_conflict

次のいずれかでtrueとする。

- score biasとside-aware primary sideが反対
- score biasと15M signalが反対で、4H・1Hがscore biasを明示確認していない
- Up/DownのMarket Map familyが同時成立
- opposite 15M conflictが存在

#### 6.7.7 stateの優先順位

1. gate blocked、no-trade、STOP相当なら`blocked`
2. hard blockがなく方向競合なら`direction_conflict`
3. `B_CHECK_15M`なら`check_15m`
4. `C_WATCH_ZONE`なら`watch_zone`
5. `A_FORMAL`相当でも`conditional_candidate`
6. その他は`wait`

`A_FORMAL`でも正式GOや自動注文ではない。

#### 6.7.8 21:05で期待するoperator decision

```text
state = blocked
primary_side = short
score_bias = long
new_entry_blocked = true
direction_conflict = true
```

reasonには少なくとも次の意味を含める。

```text
trade_execution_gate_blocked
score_vs_execution_side_conflict
score_vs_15m_signal_conflict
```

### 6.8 HTML・件名・要約の表示契約

#### 6.8.1 Hero

- `blocked`または`direction_conflict`は必ず`WAIT`
- 21:05相当では「方向スコアはLong、15分足実行はShortで競合。新規見送り」の意味を表示
- `100`を結論文へ使用しない

#### 6.8.2 Long / Shortサイドカード

現在の表示：

```text
短期実行スコア / 100
```

修正後：

```text
方向スコア / 100
```

または同義の明確な名称とする。

- `STOP_OR_EXIT`またはoperator decision blocked時は、カード上部に`実行不可` / `新規見送り`を数値より強く表示
- 数値は補助情報として小さく表示
- clamp 100の場合は上限値であることを注記
- primary cardはscore biasではなくoperator decision primary sideに従う

#### 6.8.3 中期構造表示

`4H / 1H STRUCTURAL PRIORITY`は維持する。
ただし以下を明記する。

- 中期背景である
- 15M実行方向ではない
- entry permissionではない

#### 6.8.4 件名

21:05相当で、raw biasだけを使った`上方向監視`を出してはならない。
以下のいずれかの意味にする。

```text
方向競合 / 実行不可
ショート監視 / 実行不可
方向確認待ち / 実行不可
```

どの文言を採用する場合も、`operator_decision`を唯一の根拠にする。

#### 6.8.5 要約本文

- deterministic fallbackとAI summaryの両方でoperator decisionを優先する
- AIへ新しいリクエストを追加しない
- model、timeout、retryを変更しない
- raw biasとoperator decisionが競合する場合、raw biasを実行方向として文章化しない

`src/ai/summary.py`は、既存コードがoperator decisionを無視してraw biasを直接文章化することがfocused testで確認された場合だけ変更する。

---

## 7. 変更対象と変更禁止範囲

### 7.1 原則変更対象

| ファイル | 目的 |
|---|---|
| `src/analysis/market_map.py` | ordered break/retest/hold、MTF整合、early/confirmed分離 |
| `src/analysis/scoring.py` | 反転family圧縮、位置重複排除、saturation診断 |
| `main.py` | per-TF signal受け渡し、operator decisionのattach |
| `src/presentation/sanitize.py` | operator decisionを使った件名・display context |
| `src/notification/detail_page.py` | スコア名称、STOP優先、競合表示 |
| `tests/test_market_map.py` | ordered sequenceとMTF conflict回帰 |
| `tests/test_directional_volume_trigger.py` | early flagのtrigger伝播禁止 |
| `tests/test_signal_reversal_safety.py` | incident型の統合された純粋回帰 |

### 7.2 条件付き変更対象

| ファイル | 条件 |
|---|---|
| `src/ai/summary.py` | operator decisionを無視するraw bias leakがfocused testで確認された場合のみ |
| 既存のsummary/detail page test | 本件の直接出力を検証する最小範囲のみ |

### 7.3 変更禁止

- `.env`、API key、secret
- LaunchAgent、plist、cron、schedule
- frozen runtime repo
- SMTP、SSH、rsync、公開先設定
- notification cooldown、duplicate suppression、recipient、send count
- `trade_execution_gate`のthresholdやpass条件の緩和
- `phase1b_lite_gate`のthresholdやpass条件の緩和
- `opportunity_gate`のthresholdやpass条件の緩和
- classifier全体の再設計
- paper positionやactual trade importer
- Macro runtime、Macro health、public delivery
- raw exchange exportのcommit
- 本件と無関係なcleanup、rename、formatting

> [!danger]
> 本件を理由に、既存gateを通りやすくする変更を行ってはならない。
> 安全側へWAITに倒すことは許可するが、実行許可を広げる変更は別承認が必要である。

---

## 8. 受け入れ条件

### 8.1 Incident acceptance matrix

| Case | 入力の要点 | 必須結果 |
|---|---|---|
| A：20:05型 | 4H wait / 1H wait / 15M short / score short | operator primary sideはShort、Longへ反転しない、WAITまたはno-chaseを維持 |
| B：21:05型 | 4H wait / 1H wait / 15M short / score bias long / side-aware short / gate blocked | `confirmed_up`禁止、operator state blocked、primary side short、direction conflict true、Long実行強調なし |
| C：正しい上転換 | ordered break→retest→hold / 15M long / 1H上構造 | `confirmed_up`を許可、Up familyは1回だけ加点 |
| D：正しい下転換 | ordered break→retest→hold / 15M short / 1H下構造 | `confirmed_down`を許可、Down familyは1回だけ加点 |
| E：両方向競合 | UpとDown familyが同時成立 | 両方を加点せずWAIT、conflictを記録 |

### 8.2 Market Map

- retest-before-breakでconfirmedにならない
- same-bar break/retestでconfirmedにならない
- break→retestだけでholdがなければearly
- ordered break→retest→holdでconfirmed
- 15Mが反対signalならconfirmedにならない
- bullish / bearishが完全対称
- 同一入力で決定的に同一結果

### 8.3 Scoring

- Up reversal familyはsideごとに最大1要素だけ適用
- Down reversal familyも同様
- suppressed codeを診断可能
- generic位置ペナルティとMarket Map位置ペナルティは合計1回
- `top_positive_factors` / `top_negative_factors`に抑止済み要素を出さない
- 既存のweight値とlong/short差thresholdは変更しない

### 8.4 Directional trigger

- early flip単独ではtriggerを立てない
- failed breakout単独ではtriggerを立てない
- confirmed retest / trendのみMarket Map由来triggerに使用
- 明示的breakoutと方向付き高出来高ローソクの既存動作を維持

### 8.5 Operator display

21:05型fixtureのHTML・表示contextで以下を満たす。

- `WAIT`が最上位
- `実行不可`または`新規見送り`を明示
- primary sideはShortまたは方向競合
- Longカードをprimaryにしない
- `短期実行スコア / 100`という文言が存在しない
- `100`を勝率・確率・実行許可と説明しない
- subjectに`上方向監視`だけを出さない
- safety文言を維持

### 8.6 Safety

以下を変更しない。

```text
report-only
not FORMAL_GO
human-decided
no automatic order
```

### 8.7 性能

- 新規ネットワーク呼び出し0
- 新規AI呼び出し0
- 新規常駐処理0
- 新規runtime health処理0
- 新規永続状態ファイル0
- Market Map追加処理はbounded window内
- HTML生成時に同じ安全contextを不必要に複数再計算しない

---

## 9. テスト設計

### 9.1 Fixture方針

実際の巨大なsignal JSONやHTMLをそのままtest fixtureとしてcommitしない。
必要なフィールドだけを持つsanitizedな最小dict fixtureを作る。

#### 20:05型の必須フィールド

```text
bias=short
signals_4h=wait
signals_1h=wait
signals_15m=short
long_display_score=18
short_display_score=82
side_aware primary=short
trade gate=blocked
```

#### 21:05型の必須フィールド

```text
bias=long
signals_4h=wait
signals_1h=wait
signals_15m=short
long_display_score=100
short_display_score=2
side_aware primary=short
trade gate=blocked
operator STOP相当
```

### 9.2 Market Map unit tests

最低限、次を追加する。

1. break前のretestはconfirmedにならない
2. same candleはbreakとretestを兼ねない
3. break→retestのみはearly
4. break→retest→holdはconfirmed
5. ordered up sequenceでも15M shortならearly/conflict
6. ordered down sequenceでも15M longならearly/conflict
7. genuine up/downの対称性

### 9.3 Scoring unit tests

1. Up familyの5フラグが同時でも1回だけ適用
2. Down familyの5フラグが同時でも1回だけ適用
3. Long resistance penaltyは1回
4. Short support penaltyは1回
5. Up/Down同時は加点せずconflict
6. saturation診断がrawと整合

### 9.4 Directional trigger tests

1. plain `resistance_to_support_flip`単独ではUp trigger false
2. plain `support_to_resistance_flip`単独ではDown trigger false
3. confirmed retestは対応方向trigger true
4. explicit breakoutは既存通り
5. directional high-volume candleは既存通り
6. 明示的な両方向breakoutの既存仕様は維持

### 9.5 Presentation tests

1. 21:05型でoperator decisionがblocked / short / conflict
2. 21:05型HTMLがLong 100を実行許可として強調しない
3. `短期実行スコア`がHTMLにない
4. 件名がraw biasだけの`上方向監視`にならない
5. 20:05型はShort監視・no-chaseを維持
6. genuine aligned Longは、gateが許可する場合だけ条件付き候補として表示
7. safety footerとREPORT ONLY表示を維持

### 9.6 許可する検証コマンド

推奨する最小検証は以下である。

```text
.venv312/bin/python -m unittest \
  tests.test_market_map \
  tests.test_directional_volume_trigger \
  tests.test_signal_reversal_safety
```

既存のdetail page testへ追加した場合は、その1モジュールだけを加える。

最後にtask filesだけへ実行する。

```text
git diff --check -- <task files>
```

### 9.7 1回だけ許可するfixture smoke

- sanitized 21:05型dictからHTMLを一時ディレクトリへ生成
- 文字列assertまたはローカルfile確認だけ
- publish関数を呼ばない
- SMTP、SSH、rsyncを呼ばない
- 公開URLへアクセスしない

---

## 10. CODEX実行コストの制約

> [!warning]
> 本件は原因と修正範囲が既に特定されている。
> CODEXに広域調査、長時間replay、health確認、runtime確認を繰り返させない。

### 10.1 読み取り上限

CODEXが最初に読むものは以下だけとする。

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. 本設計書
4. 本設計書の変更対象ファイル
5. 直接対応するtest
6. 必要なら20:05 / 21:05 signal JSONの該当部分だけ

以下を広域scanしない。

- `TASK_LEDGER.md`
- `history/`
- `_archive/`
- 全logs
- 全local reports
- 全spec
- frozen runtime repo

### 10.2 実行禁止

- `main.py`のlive cycle
- runtime kickstart
- launchctl / plist / cron確認
- SMTP test
- notification送信
- detail page publish
- SSH / rsync
- public URL verification
- Macro runtime実行
- Macro health artifact生成
- health状態のpolling
- `tail -f`やwatcher
- 全日・全候補・全期間replay
- full local data bundle
- full test suite
- 同じ重いコマンドの再実行
- acceptance目的の2回目の完全実行

### 10.3 test回数

- 実装中は対象unit testだけ
- 失敗時は原因に関係するコードを変更してから再実行
- 変更なしで同じ失敗コマンドを繰り返さない
- focused testsが通れば、健康確認目的の追加testは行わない
- full suiteは共有基盤破損を示す具体的証拠が出た場合のみ、ChatGPTの別承認を必要とする

### 10.4 git操作

- `git status --short --branch`は開始時に1回
- task外のdirty filesを変更しない
- task filesだけstage
- 1つの意味あるlocal commitへまとめる
- pushしない
- completion後に追加のstatus監視やpollingをしない

### 10.5 reportとoutbox

完了時は同じcompact reportを以下へ**1回だけ**書く。

```text
/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt
```

- createまたはoverwriteを直接1回
- read backしない
- 存在確認しない
- retryしない
- recreateしない
- watcherを使わない
- 別processが直後に移動・削除しても正常とする

---

## 11. 実装順序

### Step 1：境界確認

- branchとdirty treeを1回確認
- task filesと既存差分の重なりを確認
- 重なりが安全に分離できない場合は停止

### Step 2：Market Map修正

- ordered break/retest/hold
- per-TF signal参照
- early/confirmed分離
- conflict記録
- matching unit tests

### Step 3：trigger伝播修正

- confirmed flagだけをMap由来triggerに使用
- existing breakout / directional volume挙動を維持
- matching tests

### Step 4：scoring修正

- reversal family compression
- location duplicate suppression
- saturation diagnostic
- factor breakdown整合
- matching tests

### Step 5：operator decision修正

- side-aware attach後にpure contextを生成
- notify triggerは変更しない
- display context、subject、detail pageをoperator decisionへ統一
- 21:05型・20:05型test

### Step 6：最小検証

- focused unittestを1回まとめて実行
- sanitized HTML smokeを1回
- task-scoped `git diff --check`

### Step 7：commitと報告

- task filesだけstage
- local commitを1つ作成
- pushなし
- compact reportを返す
- `response.txt`へ同じ内容を1回だけ書く

---

## 12. 停止条件

次の場合、推測で進めず`partial`または`blocked`で停止する。

- task対象ファイルに分離不能な既存変更がある
- 本設計を満たすためにgate threshold変更が必要になる
- 本設計を満たすためにruntime・mail・schedule変更が必要になる
- raw signalのprivate情報をtestへcommitする必要が生じる
- operator decisionを追加すると既存notification trigger変更が避けられない
- sourceと本設計の前提が具体的に矛盾する
- focused test外の大規模replayが必要になる
- full suiteなしでは判断できない共有基盤問題が見つかる

停止時は、何が不足し、どの人間判断が必要かを1行で明記する。

---

## 13. 完了報告

CODEXの最終報告は以下のcompact formatを使う。

```text
WORK_ID: P-SAFETY-REVERSAL-1
STATUS: done | partial | blocked | failed
BRANCH: <branch>
CHANGED:
- <file>
TESTS:
- <command> => pass | fail | not run
COMMIT: <hash or none>
PUSH: none
NOTES: <必要な場合のみ1行>
```

報告には以下を含める。

- Market Mapのordered確認を実装したか
- reversal family重複を抑止したか
- 21:05型がblocked / conflictになったか
- `短期実行スコア`を除去したか
- live/runtime/mail/publishを実行していないこと

---

## 14. 次スレッドへの引き継ぎ

次スレッドでは、ChatGPTは以下を行う。

1. `AFROG_Business_MCP`で本設計書の存在と内容を確認
2. 必要なsourceとtestだけを再確認
3. 本設計を1つのbounded CODEX promptへまとめる
4. CODEXに実装・focused test・commit・compact reportを1回で行わせる
5. CODEX報告後、ChatGPTがsource、test、diff、fixture結果をMCPで直接review
6. accept、1回のmaterial FIX、またはhuman judgmentを決定

> [!note]
> 次スレッドのCODEXには、本設計の原因調査を最初から繰り返させない。
> 実装は本設計を前提とし、ローカル編集とfocused validationへ集中させる。

### 14.1 CODEXの裁量

許可する。

- 小さなpure helperの追加
- 近接コードの整理
- sanitized inline fixture
- matching regression test
- 重複計算の除去
- bounded window内の一回走査への最適化

許可しない。

- ゴールの再解釈
- threshold・weightの独自変更
- acceptance条件の簡略化
- runtime検証の追加
- broad cleanup
- 別phaseへの拡張

---

## 15. 完了定義

| 完了条件 | 確認方法 | 必須 |
|---|---|---:|
| break・retest・holdが順序付き | Market Map unit test | 必須 |
| 15M反対signalでconfirmed禁止 | conflict unit test | 必須 |
| genuine up/down confirmedを維持 | 対称fixture | 必須 |
| reversal familyの重複加点なし | scoring breakdown test | 必須 |
| 位置ペナルティ重複なし | scoring unit test | 必須 |
| early Map flagがtriggerへ伝播しない | directional trigger test | 必須 |
| 21:05型がblocked / short primary / conflict | operator decision test | 必須 |
| 20:05型のShort監視を維持 | incident regression test | 必須 |
| `短期実行スコア`が消える | HTML文字列test | 必須 |
| 件名がraw biasだけで`上方向監視`にならない | subject test | 必須 |
| REPORT ONLY等の安全文言を維持 | HTML test | 必須 |
| 新規network・AI・runtime処理なし | source diff review | 必須 |
| focused tests pass | unittest結果 | 必須 |
| task-scoped diff check pass | `git diff --check` | 必須 |
| full replay・health監視なし | CODEX report | 必須 |
| local commit1つ、pushなし | commit report | 必須 |

### 最終結論

| 問題 | 本設計の対策 | 完成時の状態 |
|---|---|---|
| 単発反発をconfirmed化 | ordered break→retest→holdと15M整合 | 不十分な反転はearly止まり |
| 同一イベントの多重加点 | reversal family圧縮 | 1イベントはsideごとに1回だけ |
| 同じ位置の二重減点 | location family上限 | genericとMapの重複なし |
| false Mapからsetupへ連鎖 | confirmed flagだけtriggerへ使用 | earlyイベントは監視のみ |
| Long 100が実行許可に見える | operator decision優先・名称変更 | WAIT / 実行不可が最上位 |
| 方向と15Mが競合 | direction conflictを明示 | 21:05型は新規見送り |
| CODEXコスト過多 | focused tests・runtime禁止・1 task | 無駄なreplayやhealth確認なし |

本設計の完成条件は、特定の1回をShortへ後付けすることではない。
**本物の反転検出能力を残しながら、不十分な反発を確定扱いせず、同一証拠を増幅せず、実行不可を数値より明確に伝えること**である。
