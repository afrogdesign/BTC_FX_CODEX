---
title: M-EVENT1・4時間足構造イベント実装仕様
date: 2026-07-22
tags:
  - btc_monitor
  - macro-structure
  - structural-events
  - report-only
---

> [!abstract]
> M-VIS1の水平ゾーンとM-LINE1の表示対象ラインを、確定4時間足だけで読み取れる構造イベントへ変換する。接近、接触、反発、突破、終値定着、リテスト、失敗、リクレイム、確定スイング更新を少数の再現可能なイベントとして表示し、確率・売買許可・波動番号は導入しない。

## 目的

ユーザーが4時間足チャートを見たとき、単に線があるだけでなく、現在までに何が起きたかを同じobject IDで追跡できるようにする。

```text
水平zone / 斜めline
→ approach
→ touch
→ clean rejection または break
→ closed-candle acceptance または false-break reclaim
→ retest
→ retest hold または retest failure
```

確定4H pivot列からは、次の構造更新も生成する。

- higher high
- higher low
- lower high
- lower low

このmoduleはmanual judgment supportであり、entry signalではない。

## 入力契約

### 4H candles

- M-VIS1で検証済みの公開4H OHLCVを再利用する
- snapshot cutoff以前に終了したclosed candleだけを使用する
- 最大240本
- 新しいfetchを行わない
- timestamp、OHLC、symbol、intervalの検証は既存M-VIS1契約を維持する

### 水平object

対象はoperatorに表示されるhigh / medium zoneだけとする。

- object_kind: `horizontal_zone`
- object_id: 既存`level_id`
- geometry: `low`, `high`, `center`
- expected reaction direction:
  - role=support → `UP`
  - role=resistance → `DOWN`
- availability time: `last_confirmed_at`
- availability timeより前のbarへ現在geometryやroleを遡及適用しない

同じlevel IDがreferenceとzoneの双方に現れる場合は1 objectへdeduplicateする。

### 斜めobject

対象はM-LINE1の`displayed_line_ids`に含まれるlineだけとする。

- object_kind: `trendline`
- object_id: `line_id`
- kind:
  - `ascending_support` → expected reaction `UP`, break direction `DOWN`
  - `descending_resistance` → expected reaction `DOWN`, break direction `UP`
- availability time: line `confirmation_timestamp`
- `invalidated`または`insufficient` lineは対象外
- channel boundaryはM-EVENT1対象外

### 構造pivot

既存のevent-time pivot契約を再利用する。

```text
confirmed_pivots(candles, "4h", left=2, right=2)
```

pivot eventは`confirmation_timestamp`より前へ遡及しない。

## 共通数値契約

判定bar時点までの14本ATRを使用する。

- ATR fallback: `max(current_price * 0.001, 1e-9)`
- approach distance: `0.75 ATR`
- touch tolerance for trendline: `0.25 ATR`
- wrong-side close break: `0.35 ATR`
- clean rejection distance: `0.50 ATR`
- reclaim / retest failure return margin: `0.10 ATR`
- touch cluster separation: 2 bars
- clean rejection confirmation window: touch後2 bars以内
- false-break reclaim window: break後3 bars以内、acceptance前
- retest search window: acceptance後12 bars以内
- retest resolution window: retest後2 bars以内
- structural pivot equality tolerance: `0.10 ATR`

閾値はM-EVENT1内で固定し、既存水平zone reliability、M-LINE1 geometry、gate、score、classifierを変更しない。

## object geometry

### horizontal zone

bar index時点でもgeometryは`low` / `high`の固定rangeとして扱う。

- intersects: `bar.high >= zone.low and bar.low <= zone.high`
- break UP: `close > zone.high + 0.35 ATR`
- break DOWN: `close < zone.low - 0.35 ATR`
- reclaim after UP break: `close <= zone.high - 0.10 ATR`
- reclaim after DOWN break: `close >= zone.low + 0.10 ATR`

break directionは現在roleに対するwrong sideだけを対象にする。

- support → DOWN break only
- resistance → UP break only

### trendline

line valueはM-LINE1と同じ4H bar index geometryから計算する。別の傾きを再計算しない。

- touch: expected wickとline valueの距離が`0.25 ATR`以内
- ascending support break: `close < line - 0.35 ATR`
- descending resistance break: `close > line + 0.35 ATR`
- reclaimはlineの元側へ`0.10 ATR`戻るclose

## イベント契約

### approach

最新closed barだけから生成するongoing event。

- objectとwickが交差していない
- closeからnearest boundary / lineまでの距離が`0.75 ATR`以内
- event_status: `ongoing`
- confirmation timeではなく、評価cutoff時点のcurrent stateであることを明示する

### touch

- horizontal zone: wickがrangeとintersect
- trendline: expected wickがlineから`0.25 ATR`以内
- 2 bars未満で連続する接触は同じcluster
- clusterの最初のbar endpointをevent timeとする
- anchor touchを含め、availability time以後だけ評価する
- `interaction_count`へobject内のtouch cluster通番を記録する
- event_status: `confirmed`

### clean_rejection

touch後2 bars以内に、breakまたはacceptanceより先に次を満たした最初のcloseで確定する。

- support / ascending support: relevant upper boundary / lineより`0.50 ATR`上
- resistance / descending resistance: relevant lower boundary / lineより`0.50 ATR`下
- event_status: `confirmed`
- parent_event_id: touch event ID

### break

availability time後、wrong sideへ`0.35 ATR`を超えた最初の4H closeで生成する。

- event_status: `confirmed`
- sequence_status:
  - resolution未確定: `pending`
  - acceptance成立後: `accepted`
  - false-break reclaim成立後: `reclaimed`
- 同一active sequenceでbreakを重複生成しない

### closed_candle_acceptance

break barを含む2本連続の4H closeが同じbreak sideへ`0.35 ATR`を超えた場合、2本目endpointで確定する。

- event_type: `closed_candle_acceptance`
- event_status: `confirmed`
- parent_event_id: break event ID
- direction: break direction

### false_break_reclaim

acceptance成立前、break後3 bars以内に元側へ`0.10 ATR`戻るcloseがある場合、そのendpointで確定する。

- event_type: `false_break_reclaim`
- event_status: `confirmed`
- parent_event_id: break event ID
- direction: expected reaction direction
- 同じbreak sequenceからacceptanceとreclaimを同時生成しない

### retest

acceptance後12 bars以内に、break側からobjectへ最初に再接触したclusterで確定する。

- event_type: `retest`
- event_status: `confirmed`
- parent_event_id: acceptance event ID
- channel boundaryは対象外

### retest_hold

retest後2 bars以内に、break方向へ再度`0.35 ATR`以上離れてcloseした場合に確定する。

- event_type: `retest_hold`
- event_status: `confirmed`
- parent_event_id: retest event ID
- direction: original break direction

### retest_failure

retest後2 bars以内に、元側へ`0.10 ATR`戻ってcloseした場合に確定する。

- event_type: `retest_failure`
- event_status: `confirmed`
- parent_event_id: retest event ID
- direction: expected reaction direction

同じretestからholdとfailureを同時生成しない。先に確定したものを採用する。

### structural pivot events

同じsideの直前confirmed pivotと比較する。

- current high > previous high + `0.10 ATR` → `higher_high`
- current high < previous high - `0.10 ATR` → `lower_high`
- current low > previous low + `0.10 ATR` → `higher_low`
- current low < previous low - `0.10 ATR` → `lower_low`
- tolerance内はeventを生成しない
- event time: current pivot `confirmation_timestamp`
- object_kind: `pivot_structure`
- object_id: current pivot ID
- related_object_id: previous same-side pivot ID

## sequenceとrearm

各horizontal / trendline objectは1つのactive break sequenceだけを持つ。

- neutral → break pending
- pending → acceptance または false_break_reclaim
- acceptance → retest待ち、最大12 bars
- retest → retest_hold または retest_failure待ち、最大2 bars
- sequence終了後、少なくとも1本のcloseが元側にある場合だけ次のbreak sequenceをrearmする
- unresolved window終了はeventとして追加せず、model内のsequence statusだけを終了する

このstate machineにより同じcloseや同じtouchを重複計上しない。

## stable event ID

```text
event_id = sha256(
  "macro_structure_structural_events.v1|"
  "<object_kind>|<object_id>|<event_type>|"
  "<event_timestamp_utc>|<direction>|<parent_event_id>"
)[:20]
```

同じ入力から同じID、順序、parent relationを生成する。

ID collisionでgeometryまたはevent payloadが異なる場合はfail closedする。

## model契約

operatorへ次を追加する。

```text
structural_event_model:
  schema_version
  method_version
  cutoff_utc
  status
  objects_evaluated
  events
  current_events
  displayed_event_ids
  reason_codes
```

method/version:

```text
macro_structure_structural_events.v1
```

### event必須field

- `event_id`
- `event_type`
- `event_status`
- `sequence_status`
- `event_timestamp_utc`
- `object_kind`
- `object_id`
- `related_object_id`
- `parent_event_id`
- `direction`
- `price`
- `object_value_low`
- `object_value_high`
- `distance_atr`
- `interaction_count`
- `reason_codes`

### 保持と表示

- modelは最新48 eventsまで保持する
- structural pivot eventsは最新8件まで
- chart/list表示は合計最大12 events
- 優先順位:
  1. ongoing approach
  2. pending break sequence
  3. cutoff前12 bars以内のconfirmed event
  4. event time descending
  5. event_id ascending
- chart markerは最大8件
- event listとchart markerは同じevent IDを表示する

### status

- 1件以上のeventまたはcurrent eventがある: `ok`
- objectは評価できたがeventがない: `insufficient`
- 4Hまたはobject入力不整合: renderer全体をfail closed

`insufficient`は正常成果物として公開し、推測eventを作らない。

## operator表示契約

4H chartの下に`Structural events` panelを追加する。

最低限表示する。

- event time
- event type
- ongoing / confirmed
- object kind / object ID
- direction
- sequence status
- parent event ID
- touch interaction count

4H chartには最大8件の短いevent markerを追加する。

- marker label: event type + event ID先頭8文字
- markerと一覧は同じevent IDを参照する
- 既存horizontal zones、trendline/channel、15m supplemental viewを維持する

表示文言は次を維持する。

- report-only
- no automatic order
- human decides manually
- structural event is evidence, not execution permission

## artifact identity

- operator全体のschema/methodはhealth互換の`macro_structure_operator_artifact.v2`を維持する
- 4H inputがある場合だけoperator digestとmanifest model identityへ`macro_structure_structural_events.v1`を追加する
- 4H inputがない既存callerのdigest、artifact ID、出力内容を変更しない
- M-LINE1 method tokenも維持する

## Fail-closed

次の場合は既存`latest.json`を更新しない。

- non-monotonic / non-finite 4H input
- object ID欠落または重複payload不一致
- zone geometry reversal
- line geometry / confirmation inconsistency
- future event timestamp
- event ID collision with different payload
- parent event参照不整合
- publication failure

候補event不足は失敗ではなく`insufficient`とする。

## matching validation

最低限証明する。

1. 同一入力でevent ID、順序、parent relationが一致する
2. availability / confirmation前へeventをbackdateしない
3. approachは最新barのongoing stateだけ
4. touch clusterを重複計上しない
5. clean rejectionをtouch後2 bars以内で確定する
6. wrong-side 0.35 ATR closeでbreakを1回だけ生成する
7. 2 consecutive closesでacceptanceを生成する
8. acceptance前3 bars以内のreturnでfalse-break reclaimを生成する
9. acceptance後12 bars以内のretestを生成する
10. retest holdとfailureを排他的に生成する
11. HH / HL / LH / LLをpivot confirmation時刻で生成する
12. tolerance内pivotはeventにしない
13. horizontalとtrendlineが同じmodelで処理される
14. event listとchart markerが同じIDを参照する
15. M-VIS1 zone、M-LINE1 overlay、15m view、安全境界を維持する
16. invalid inputはprevious latestを維持する
17. no-4H callerは既存互換を維持する

## bounded smoke

既存local inputを再利用し、fetchやpipeline再実行なしで1回だけ生成する。

```text
snapshot root: local/reports/macro_structure
history root: local/reports/macro_structure/history
15m input: local/runtime/macro_structure_inputs/latest/ohlcv_15m.csv
4h input: local/runtime/macro_structure_inputs/latest/ohlcv_4h.csv
output root: local/reports/macro_structure/mevent1_review/operator
```

確認する。

- complete HTML artifact
- primary 4H chart
- structural event statusまたはinsufficient表示
- eventがある場合、ID、type、time、object ID、statusが読める
- horizontal zoneとdiagonal statusが残る
- supplemental 15mとreport-only表示が残る

## 対象外

- Elliott Wave / numbered wave
- probability / historical win rate
- scenario generation
- entry / SL / TP
- channel boundary event
- runtime / launchd / schedule
- mail / notification
- existing gate / score / threshold / classifier変更
- private/account/order data
- automatic order

## Acceptance

- currentとconfirmedを区別できる
- touch、break、acceptance、reclaim、retestが重複せず追跡できる
- horizontal zoneとtrendlineが同じevent ID契約で表示される
- confirmed pivot structureがevent-time correctである
- chartと一覧が同じIDを参照する
- event不足時に推測しない
- matching tests、small fixture、1回のbounded smoke、diff checkが通る

M-EVENT1 acceptance後だけM-HYP1を開始する。
