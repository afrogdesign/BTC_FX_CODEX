---
title: M-LINE1・4時間足トレンドラインとチャネル実装仕様
date: 2026-07-22
tags:
  - btc_monitor
  - macro-structure
  - trendline
  - channel
  - report-only
---

> [!abstract]
> M-VIS1で完成した4時間足中心の大局チャートへ、確定済み4時間足ピボットだけを使った再現可能な斜めトレンドラインと平行チャネルを追加する。表示を少数の重要候補に限定し、未来情報、主観的な引き直し、確率断定、自動注文を導入しない。

## 📋 目次

1. [目的](#-目的)
2. [ユーザー価値](#-ユーザー価値)
3. [入力と再利用](#-入力と再利用)
4. [トレンドライン契約](#-トレンドライン契約)
5. [チャネル契約](#-チャネル契約)
6. [モデル契約](#-モデル契約)
7. [表示契約](#-表示契約)
8. [Fail-closed契約](#-fail-closed契約)
9. [検証契約](#-検証契約)
10. [対象外](#-対象外)
11. [Acceptance](#-acceptance)

---

## 🎯 目的

最新の公開4時間足データから、次の斜め構造を自動生成する。

```text
確定4Hスイング安値
→ 上昇サポートライン候補

確定4Hスイング高値
→ 下降レジスタンスライン候補

選択された基準ライン
＋ 反対側の確定4Hピボット
→ 平行チャネル候補
```

このmoduleは大局構造の視覚化であり、entry signal、売買許可、確率予測ではない。

---

## 👤 ユーザー価値

- 水平レジサポだけでは分かりにくい上昇・下降の傾きを確認できる
- どの確定スイングを結んだ線か確認できる
- ラインが生きているか、既に破られたかを区別できる
- チャネル内の現在位置を確認できる
- 人間が4時間足の大局観を確認してから15分足判断へ進める

> [!warning]
> ラインを多く表示するほど実用性が上がるわけではない。重要候補だけを表示し、候補不足時は線を推測しない。

---

## 📥 入力と再利用

### 入力

M-VIS1で明示的に渡される公開4H OHLCVだけを使う。

- snapshot cutoff以前に終端した4H足だけ
- 最大240本
- timestampは単調増加
- symbolとintervalは既存M-VIS1契約を維持
- 新しいfetchは行わない

### ピボット

既存のevent-time契約を再利用する。

```text
confirmed_pivots(candles, "4h", left=2, right=2)
```

ピボットの使用可能時刻は`confirmation_timestamp`である。

- pivot_timestampへ確認結果を遡及しない
- confirmation_timestampがsnapshot cutoffを超えるピボットは使用しない
- 既存ピボット判定の意味、left/right、ATR計算を変更しない

---

## 📐 トレンドライン契約

### 候補種別

M-LINE1で生成する基準ラインは2種類だけとする。

| kind | anchor | 条件 |
|---|---|---|
| `ascending_support` | 2つの確定4H swing low | 後の安値が前の安値より高い |
| `descending_resistance` | 2つの確定4H swing high | 後の高値が前の高値より低い |

水平線、下降support、上昇resistanceはM-LINE1では生成しない。

### 候補探索範囲

- 各sideの直近12ピボットだけを候補探索に使う
- anchor 1はanchor 2より前
- anchor間隔は3本以上120本以下の4H bar
- 同一anchor pairから生成する候補は1つだけ

### 傾き

```text
slope_per_4h_bar = (anchor_2_price - anchor_1_price) / anchor_bar_distance
```

geometryは4H bar indexを基準に計算する。表示時刻の差から別の傾きを再計算しない。

### 安定したID

```text
line_id = sha256(
  "macro_structure_trendline.v1|<kind>|<anchor_1_pivot_id>|<anchor_2_pivot_id>"
)[:20]
```

同じanchor pairは、後続データが追加されても同じIDと基準geometryを維持する。

### 確認時刻

```text
line_confirmation_timestamp = max(
  anchor_1_confirmation_timestamp,
  anchor_2_confirmation_timestamp
)
```

この時刻より前のartifactや状態へラインを表示しない。

### ATR

接触・逸脱判定には既存と同じ14本ATRを使う。

- 判定対象bar時点までのclosed 4H candlesのみ
- ATRが0の場合は`max(current_price * 0.001, 1e-9)`をfallbackにする

### anchor間の妥当性

anchor 1からanchor 2までの区間で、終値が基準ラインを誤方向へ`0.35 ATR`より大きく超えた候補は`invalidated`とする。

- ascending support: closeがlineより`0.35 ATR`超下
- descending resistance: closeがlineより`0.35 ATR`超上
- wickだけの逸脱ではinvalidatedにしない
- invalidated候補は表示候補へ入れない

### 接触

対応するwickとラインの距離が`0.25 ATR`以内ならtouch候補とする。

- ascending supportはbar lowを使う
- descending resistanceはbar highを使う
- anchor 1とanchor 2はtouchに含める
- 2本未満の間隔で連続するtouchは同一clusterとして数える
- 誤方向へ`0.35 ATR`を超えて終値breakしたbarはtouchに数えない

### 現在状態

| state | 定義 |
|---|---|
| `active` | invalidatedでもbrokenでもなく、distinct touch clusterが2 |
| `tested` | invalidatedでもbrokenでもなく、distinct touch clusterが3以上 |
| `broken` | line確認後、誤方向へ`0.35 ATR`を超える最初の4H終値がある |
| `invalidated` | anchor間の妥当性を満たさない |

brokenは後からactiveへ戻さない。reclaimやretestはM-EVENT1で別イベントとして扱う。

### 距離

cutoff時点で次を計算する。

- `current_line_value`
- `distance_from_price`
- `distance_from_price_pct`
- `distance_from_price_atr`

### 候補順位

順位は次のtupleで固定する。

```text
state priority: tested → active → broken
→ touch_count descending
→ anchor_2_confirmation_timestamp descending
→ anchor_span_bars descending
→ distance_from_price_atr ascending
→ line_id ascending
```

### 保持数と表示数

- JSON modelではkindごとに上位3候補まで保持
- chart表示はkindごとに次の最大2本
  - 最上位の`tested`または`active`を最大1本
  - breakがcutoff前12本以内の最上位`broken`を最大1本
- 合計表示本数は最大4本
- live候補もrecent broken候補もない場合、そのkindは`insufficient`

---

## 📏 チャネル契約

### 生成元

各kindの最上位`tested`または`active`基準ラインからだけ、最大1チャネルを生成する。

### ascending channel

- base: `ascending_support`
- anchor 1以降にある確定4H swing highを対象
- 各high pivotとbase lineとの差を計算
- 正の差が最大のpivotをopposite anchorとする
- base lineをその差だけ上へ平行移動しupper boundaryとする

### descending channel

- base: `descending_resistance`
- anchor 1以降にある確定4H swing lowを対象
- 各low pivotとbase lineとの差を計算
- 負の差の絶対値が最大のpivotをopposite anchorとする
- base lineをその差だけ下へ平行移動しlower boundaryとする

### channel confirmation

```text
channel_confirmation_timestamp = max(
  base_line_confirmation_timestamp,
  opposite_anchor_confirmation_timestamp
)
```

cutoff時点で未確認なら生成しない。

### 幅の制約

cutoff時点のchannel widthが次を満たす場合だけ採用する。

```text
0.75 ATR <= channel_width <= 12 ATR
```

範囲外は`insufficient`として生成しない。

### 安定したID

```text
channel_id = sha256(
  "macro_structure_channel.v1|<base_line_id>|<opposite_anchor_pivot_id>"
)[:20]
```

### channel model

- `channel_id`
- `kind`: `ascending_channel` / `descending_channel`
- `base_line_id`
- `opposite_anchor_pivot_id`
- `confirmation_timestamp`
- `lower_value_at_cutoff`
- `upper_value_at_cutoff`
- `width_at_cutoff`
- `width_atr`
- `current_position_percent`
- `state`: base lineの`active`または`tested`

表示はascending最大1、descending最大1とする。

---

## 🧱 モデル契約

既存`chart_model_4h`を壊さず、次を追加する。

```text
trendline_model:
  schema_version
  method_version
  pivot_method
  cutoff_utc
  status
  lines
  displayed_line_ids
  channels
  displayed_channel_ids
  reason_codes
```

### line必須field

- `line_id`
- `kind`
- `state`
- `anchor_1_pivot_id`
- `anchor_1_timestamp`
- `anchor_1_price`
- `anchor_1_confirmation_timestamp`
- `anchor_2_pivot_id`
- `anchor_2_timestamp`
- `anchor_2_price`
- `anchor_2_confirmation_timestamp`
- `confirmation_timestamp`
- `slope_per_4h_bar`
- `anchor_span_bars`
- `touch_count`
- `touch_timestamps`
- `break_timestamp`
- `current_line_value`
- `distance_from_price_pct`
- `distance_from_price_atr`

### status

- 1本以上の表示lineまたはchannelがある: `ok`
- 計算は正常だが表示候補がない: `insufficient`
- 入力不正・内部不整合: renderer全体をfail closed

`insufficient`は正常な成果物として公開し、理由を表示する。

---

## 🖥️ 表示契約

### 4H chart

既存の水平zoneを維持したまま、斜めoverlayを追加する。

- tested / active line: solid
- recent broken line: dashed
- brokenをactive support/resistanceとして表現しない
- ascending supportとdescending resistanceをラベルで明示
- channelは薄いbandと平行boundaryで表示
- ラベルへ最低限次を表示
  - kind
  - state
  - touch count
  - anchor 1 / anchor 2の日付

### evidence panel

4H chart直後または既存zone evidence近傍に、次の表を追加する。

- line/channel ID
- kind
- state
- anchors
- confirmation time
- slope
- touch count
- break time
- current distance ATR

### insufficient表示

候補不足時は次を表示する。

```text
Diagonal structure: insufficient confirmed 4H evidence
```

推測線や0値lineを描画しない。

### 既存表示

次を維持する。

- 4H-first hierarchy
- 1H / 4H horizontal zones
- supplemental 15m view
- cutoff / evaluation / stale / continuity / data quality
- report-only / no automatic order / human decides manually

---

## 🛑 Fail-closed契約

次の場合は成果物生成を失敗させ、既存`latest.json`を更新しない。

- 4H input validation failure
- non-monotonic timestamp
- pivot timestamp / confirmation timestamp inconsistency
- line ID collision with different geometry
- non-finite slope、price、ATR、distance
- channel boundary reversal
- output staging failure

候補不足は失敗ではなく`insufficient`とする。

---

## 🧪 検証契約

### matching unittest

最低限、次を証明する。

1. 同じ入力から同じline IDとgeometryが生成される
2. confirmation前のlineは表示されない
3. ascending supportが確定swing lowから生成される
4. descending resistanceが確定swing highから生成される
5. 0.25 ATR touch clusteringが再現可能
6. 0.35 ATR close breachでbrokenになる
7. anchor間breachはinvalidatedになり表示されない
8. recent brokenだけが破線表示候補になる
9. 平行channelのboundaryとIDが決定的
10. 候補不足は`insufficient`で正常成果物になる
11. 水平zone、15m補助表示、安全境界が維持される
12. 不正入力では既存latestが維持される

### bounded smoke

既存local inputを使い、fetchやpipeline再実行なしで1回だけ生成する。

```text
snapshot root: local/reports/macro_structure
history root: local/reports/macro_structure/history
15m input: local/runtime/macro_structure_inputs/latest/ohlcv_15m.csv
4h input: local/runtime/macro_structure_inputs/latest/ohlcv_4h.csv
output root: local/reports/macro_structure/mline1_review/operator
```

確認するもの。

- complete HTML artifactが1つ生成される
- 4H chartが主表示
- trendline statusまたはinsufficient表示がある
- 表示lineがある場合、anchor、state、touch countが読める
- horizontal zonesとreport-only表示が残る

### 実行しないもの

- full test suite
- full replay
- parameter探索
- network fetch
- runtime / launchd実行
- repeated health cycle
- long background validation

---

## 🚫 対象外

- Elliott Waveや波番号
- wave countによる方向断定
- touch、break、retest、reclaimの時系列event model
- breakout acceptance scenario
- probabilityや類似事例統計
- runtime serviceへの4H引数追加
- schedule、mail、notification
- horizontal zone reliability変更
- gate、score、threshold、classifier変更
- private/account/order data
- automatic order

---

## ✅ Acceptance

| 項目 | 条件 |
|---|---|
| 再現性 | 同一入力でID、geometry、順位が一致 |
| event-time | confirmation前へ遡及しない |
| 実用性 | 表示line最大4、channel最大2 |
| line根拠 | anchors、confirmation、touchが読める |
| state | active/testedとbrokenを誤認しない |
| channel | 平行境界が決定的で幅制約内 |
| insufficient | 推測せず明示する |
| 互換性 | M-VIS1水平zoneと15m viewを維持 |
| 安全性 | report-only、manual judgment、no automatic order |
| 検証 | matching test、small fixture、bounded smoke、diff check |

M-LINE1 acceptance後だけ、M-EVENT1を開始する。

---

## 🔑 4H成果物のidentity追加契約

M-LINE1は4H inputを含む成果物の内容を変更するため、M-VIS1と同じinput fingerprintでも同じartifact IDを再利用してはならない。

- operator全体の`schema_version`と`method_version`は既存health互換の`macro_structure_operator_artifact.v2`を維持する
- `trendline_model`は独自の`schema_version` / `method_version`として`macro_structure_trendline.v1`を持つ
- 4H inputが供給された場合だけ、operator artifact digestへ`macro_structure_trendline.v1`を追加する
- run manifestのinput/model identityへtrendline method versionを記録する
- 4H inputがない既存callerのdigest、artifact ID、出力内容は変更しない

これにより、既存runtimeの15m-only互換性を維持しながら、M-VIS1の4H artifactとM-LINE1 artifactのimmutable directory衝突を防ぐ。
