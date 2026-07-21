---
title: M-HYP1・条件／確認／否定シナリオ実装仕様
date: 2026-07-22
tags:
  - btc_monitor
  - macro-structure
  - scenarios
  - report-only
---

> [!abstract]
> M-EVENT1で確定した4時間足構造イベントから、現在確認すべき少数の条件付きシナリオを決定的に生成する。各シナリオは成立条件、次の確認、否定条件を必須とし、確率、勝率、売買許可、Entry / SL / TP、自動注文を導入しない。

## 目的

最新operatorで「何が起きたか」だけでなく、「次に何を確認し、何が起きたら仮説を捨てるか」を短く読めるようにする。

```text
M-EVENT1 structural events
+ accepted horizontal zone / trendline IDs
→ current scenario candidates
→ condition
→ next confirmation
→ invalidation
→ 最大3件のreport-only仮説
```

シナリオは予測断定ではない。人間が4H大局を確認し、15mでmanual判断するための観測手順である。

## 入力契約

### 必須入力

- snapshot cutoff
- current price
- current `structure_state`
- current `price_location`
- operatorで表示中のhigh / medium horizontal zones
- M-LINE1 `trendline_model`
- M-EVENT1 `structural_event_model`

### データ境界

- 既存の検証済み4H inputから生成されたmodelだけを使う
- 新しいfetchを行わない
- future / unclosed candleを推測しない
- structural eventのtimestampがcutoffを超える場合はfail closed
- scenario生成のために既存zone reliability、line geometry、event thresholdを変更しない

### object参照

scenarioが参照できるobjectは次だけ。

- `horizontal_zone`: operatorで表示中の既存`level_id`
- `trendline`: M-LINE1 `displayed_line_ids`
- `pivot_structure`: M-EVENT1 eventが持つconfirmed pivot ID

channel boundaryはscenarioのprimary objectにしない。

### event参照

- M-EVENT1のretained `events`だけを使う
- supporting event IDは必ずretained eventへ解決できること
- parent chainを辿る場合、全parent IDがretained model内で解決できること
- 同一event IDでpayloadが異なる場合はfail closed

## method identity

```text
schema_version = macro_structure_scenarios.v1
method_version = macro_structure_scenarios.v1
```

## 共通時間契約

- 1 bar = 4 hours
- object interaction scenarioはcutoff前12 bars以内のeventだけをcandidate triggerにする
- `approach`はongoingである限り常にcandidateにできる
- pivot-structure pairはcutoff前24 bars以内に両方がある場合だけcandidateにする
- trigger timestampより前へscenarioをbackdateしない

## scenario families

M-HYP1で生成するfamilyは次の5種類だけとする。

### 1. `break_resolution_watch`

対象:

- objectの最新active sequenceが`break`
- break `sequence_status=pending`

方向:

- root break eventのdirection

status:

- `watch`

condition:

- 次のclosed 4Hがbreak sideを維持する

next confirmation:

- 同じbreak sequenceの`closed_candle_acceptance`

invalidation:

- 同じbreak sequenceの`false_break_reclaim`
- または元側へ戻るclosed 4H

このscenarioはbreak継続候補であり、acceptance成立前に「突破確定」と表示しない。

### 2. `accepted_break_continuation`

対象:

objectの最新sequence stateが次のいずれか。

- `closed_candle_acceptance`
- resolution未確定の`retest`
- `retest_hold`

方向:

- parent chainのroot break direction

status:

- `active`

condition:

- closed 4Hがaccepted break sideを維持する

next confirmation:

- `retest_hold`
- または同方向のconfirmed pivot structure更新
  - UP: `higher_high`または`higher_low`
  - DOWN: `lower_high`または`lower_low`

invalidation:

- 同objectの`retest_failure`
- 同objectの`false_break_reclaim`
- 反対側への新しい`closed_candle_acceptance`

`retest` event自身のdirectionではなく、parent chainのroot break directionを使う。

### 3. `failed_break_reversal`

対象:

objectの最新sequence resolutionが次のいずれか。

- `false_break_reclaim`
- `retest_failure`

方向:

- resolution eventのdirection

status:

- `active`

condition:

- closed 4Hがreclaimed original sideを維持する

next confirmation:

- 同objectの`clean_rejection`
- または同方向のconfirmed pivot structure更新

invalidation:

- 元のbreak方向への新しい`closed_candle_acceptance`

### 4. `boundary_reaction_watch`

対象:

objectの最新interactionが次のいずれか。

- ongoing `approach`
- `touch`
- `clean_rejection`

ただし、同objectにより新しいbreak-sequence eventがある場合は生成しない。

方向:

- event direction

status:

- approach / touch: `watch`
- clean rejection: `active`

condition:

- horizontal zoneまたはtrendlineがexpected reaction sideでclosed 4Hを維持する

next confirmation:

- `clean_rejection`
- または同方向のconfirmed pivot structure更新

invalidation:

- 同objectのwrong-side `break`
- または`closed_candle_acceptance`

### 5. `pivot_structure_continuation`

UP candidate:

- latest retained pivot eventsに`higher_high`と`higher_low`がある
- 両方がcutoff前24 bars以内

DOWN candidate:

- latest retained pivot eventsに`lower_high`と`lower_low`がある
- 両方がcutoff前24 bars以内

方向:

- UP pair → `UP`
- DOWN pair → `DOWN`

status:

- `active`

condition:

- 次のconfirmed pivotsが同方向sequenceを維持する

next confirmation:

- UP: 新しい`higher_high`または`higher_low`
- DOWN: 新しい`lower_high`または`lower_low`

invalidation:

- UP: より新しい`lower_high`と`lower_low`のpair
- DOWN: より新しい`higher_high`と`higher_low`のpair

supporting eventはpairを構成する2 event IDとする。

## objectごとの最新状態

同じobjectから古い相反scenarioを同時生成しない。

1. retained eventsをevent timestamp ascending、event ID ascendingで処理する
2. objectごとに最新のrelevant stateを選ぶ
3. 最新stateの優先解釈は次の通り

```text
pending break
→ retest_hold / retest_failure / false_break_reclaim
→ retest / closed_candle_acceptance
→ clean_rejection
→ touch
→ ongoing approach
```

同timestampの場合は上記順序を優先する。

例:

- 古いacceptanceの後にretest_failureがある場合、`failed_break_reversal`だけをcandidateにする
- 古いtouchの後にpending breakがある場合、`break_resolution_watch`だけをcandidateにする

## parent-chain方向

次のscenarioはparent chainをroot `break`まで辿り、break directionを使う。

- `break_resolution_watch`
- `accepted_break_continuation`

parent cycle、missing parent、root break不在はfail closed。

## stable scenario ID

```text
scenario_id = sha256(
  "macro_structure_scenarios.v1|"
  "<scenario_type>|<direction>|"
  "<primary_object_kind>|<primary_object_id>|"
  "<trigger_timestamp_utc>|"
  "<sorted supporting_event_ids comma-joined>"
)[:20]
```

同じ入力から同じID、順序、文言、参照を生成する。

scenario ID collisionでpayloadが異なる場合はfail closedする。

## scenario model

operatorへ次を追加する。

```text
scenario_model:
  schema_version
  method_version
  cutoff_utc
  status
  dominant_direction
  scenarios
  suppressed_candidate_count
  reason_codes
```

### scenario必須field

- `scenario_id`
- `scenario_type`
- `scenario_status`: `watch` / `active`
- `direction`: `UP` / `DOWN`
- `trigger_timestamp_utc`
- `primary_object_kind`
- `primary_object_id`
- `related_object_ids`
- `supporting_event_ids`
- `condition_code`
- `condition_text`
- `next_confirmation_code`
- `next_confirmation_text`
- `invalidation_code`
- `invalidation_text`
- `reason_codes`

### structured codes

固定codeを使い、自由生成しない。

condition codes:

- `maintain_break_side_close`
- `maintain_accepted_side_close`
- `maintain_reclaimed_side_close`
- `object_holds_expected_side`
- `preserve_confirmed_pivot_sequence`

next confirmation codes:

- `closed_candle_acceptance`
- `retest_hold_or_same_direction_pivot`
- `clean_rejection_or_same_direction_pivot`
- `next_same_direction_pivot`

invalidation codes:

- `false_break_reclaim_or_original_side_return`
- `retest_failure_reclaim_or_opposite_acceptance`
- `new_acceptance_in_original_break_direction`
- `wrong_side_break_or_acceptance`
- `opposite_confirmed_pivot_pair`

表示textはscenario type、direction、object ID、上記codeから固定templateで生成する。

## candidate ranking

ascending sort keyを次で固定する。

1. family priority
   - `break_resolution_watch`
   - `accepted_break_continuation`
   - `failed_break_reversal`
   - `boundary_reaction_watch`
   - `pivot_structure_continuation`
2. trigger timestamp descending
3. scenario status: `active` before `watch`はfamily priorityが同じ場合だけ適用
4. primary object kind ascending
5. primary object ID ascending
6. scenario ID ascending

同じ`scenario_type + primary_object_kind + primary_object_id + direction`は最新1件だけ保持する。

## conflict suppressionと表示上限

- candidateは最大3 scenariosだけ表示する
- 最上位candidateのdirectionを`dominant_direction`とする
- 追加scenarioはdominant directionと同じ方向だけ選ぶ
- 反対方向candidateは`suppressed_candidate_count`へ数え、表示しない
- 同じscenario typeは最大1件
- 同じsupporting event IDを共有するcandidateは上位1件だけ
- candidate不足時に推測scenarioを作らない

このルールにより、同じ画面でUP継続とDOWN継続を同時断定しない。

## status

- 1件以上scenarioがある: `ok`
- valid inputだがscenarioなし: `insufficient`
- input / reference / parent / identity不整合: renderer全体をfail closed

insufficient時は次を表示する。

```text
Scenario hypotheses: insufficient current structural evidence
```

## 禁止表現

modelおよびHTML scenario panelで次を使わない。

- probability / 確率
- win rate / 勝率
- confidence percentage
- buy / sell
- long / short
- entry
- stop loss / SL
- take profit / TP
- order permission

方向は`UP` / `DOWN`だけを使う。

## operator表示契約

4H chart、Diagonal evidence、Structural eventsの後、15m supplemental viewの前に`Scenario hypotheses` panelを追加する。

scenarioごとに最低限表示する。

- scenario type
- watch / active
- direction
- primary object kind / ID
- trigger time
- condition
- next confirmation
- invalidation
- supporting event IDs

表示文言を必ず含める。

```text
scenario is conditional evidence, not execution permission
report-only / no automatic order / human decides manually
```

既存Structural events panelとscenarioのevent ID参照が一致すること。

## artifact identity

- operator schema/methodは`macro_structure_operator_artifact.v2`を維持する
- 4H inputがある場合だけdigestとmanifest model identityへ`macro_structure_scenarios.v1`を追加する
- M-LINE1とM-EVENT1のmethod tokenを維持する
- 4H inputなしcallerのdigest、artifact ID、出力内容を変更しない

## fail-closed

次の場合はprevious `latest.json`を更新しない。

- structural event timestamp > cutoff
- duplicate event ID with conflicting payload
- supporting event ID missing
- parent chain missing / cycle
- primary object ID missing
- scenario ID collision with conflicting payload
- invalid direction / status / code
- non-deterministic unresolved reference
- publication failure

scenario不足はfailureではなく`insufficient`とする。

## matching validation

最低限証明する。

1. 同一inputでscenario ID、order、text、referencesが一致
2. pending breakから`break_resolution_watch`
3. acceptance / retest / retest holdからroot break方向の`accepted_break_continuation`
4. false reclaim / retest failureから`failed_break_reversal`
5. approach / touch / rejectionから`boundary_reaction_watch`
6. HH+HL / LH+LLから`pivot_structure_continuation`
7. objectの最新stateが古い相反candidateを抑止
8. parent chainからroot break directionを正しく取得
9. opposite direction candidateをglobal conflict suppressionで表示しない
10. scenario type重複とsupporting event重複を抑止
11. 最大3件
12. 全supporting event IDがretained eventへ解決
13. primary object IDが有効objectへ解決
14. condition / next confirmation / invalidationが全scenarioに存在
15. 禁止表現がmodelとHTMLに存在しない
16. scenario不足はexplicit insufficient
17. M-VIS1、M-LINE1、M-EVENT1、15m view、安全境界を維持
18. invalid inputはprevious latestを維持
19. no-4H caller互換を維持

## bounded smoke

既存local inputを使い、fetchやpipeline再実行なしで1回だけ生成する。

```text
snapshot root: local/reports/macro_structure
history root: local/reports/macro_structure/history
15m input: local/runtime/macro_structure_inputs/latest/ohlcv_15m.csv
4h input: local/runtime/macro_structure_inputs/latest/ohlcv_4h.csv
output root: local/reports/macro_structure/mhyp1_review/operator
```

確認する。

- complete HTML artifact
- 4H chartが主表示
- Scenario hypotheses panelがStructural events後、15m前
- scenarioまたはexplicit insufficient表示
- scenarioがある場合、condition / next confirmation / invalidationが読める
- supporting event IDsがStructural events model内に存在
- opposite direction scenarioが同時表示されない
- 禁止表現がscenario panelにない
- report-only / no automatic order / human decides manuallyが残る

## 対象外

- probability / historical win rate
- M-STATS1
- Elliott Wave / numbered wave
- Entry / SL / TP
- automatic order
- target price optimization
- runtime / launchd / schedule
- mail / notification
- fixed latest entry
- horizontal reliability変更
- line geometry変更
- event threshold変更
- gate / score / classifier変更
- private/account/order data

## Acceptance

- 最大3件のcondition / confirmation / invalidation仮説が読める
- scenarioがcurrent event/object IDへ追跡可能
- 相反方向を同時断定しない
- probabilityやexecution permissionに見えない
- insufficient時に推測しない
- matching tests、small fixture、1回のbounded smoke、diff checkが通る

M-HYP1 acceptance後だけM-ENTRY1を開始する。
