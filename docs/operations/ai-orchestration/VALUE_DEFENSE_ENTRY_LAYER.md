# Value Defense Entry Layer

## Purpose

Ver04-v2 では、単に long / short の bias を弱めるのではなく、entry の深さを現実的に扱う。

核心は次の通り。

- bias が valid でも、最初の提示 entry が shallow すぎることがある
- BTC/FX では shallow retest を sweep して、より深い support / defense で反応することがある
- SL に近い support は、破綻線だけではなく value defense entry の候補でもある
- したがって、方向の正しさと entry depth の妥当性は分けて評価する

## Safety Boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order endpoints
- no notification sending behavior change by default

## Problem Seen In Observation

観測では、long bias 自体はまだ plausibility があるのに、初回の shallow long retest zone が高すぎた。

- shallow zone ではなく、より深い 61,300 近辺の defense が実用的だった
- その後に defense されて bounce したため、単純に「long bias が wrong」とは言えない
- 問題は bias の有無より、entry depth の選び方だった
- self-review は direction quality と entry depth quality を分ける必要がある

## New Concept Model

### market_entry

- meaning: いま成行で入る前提の扱い
- when it appears: 直近の反応が早く、再待機よりも即時性が高い時
- what the human should do: 即時執行の可否を確認する
- what it must not mean: 方向 bias が自動的に正しいという意味ではない

### shallow_retest_entry

- meaning: 近い足・浅い押し戻しを拾う entry
- when it appears: 直近の支持/抵抗が近く、反応が早い時
- what the human should do: 深い defense が残っていないかを見る
- what it must not mean: その価格帯だけが本命という意味ではない

### value_defense_entry

- meaning: SL-near support / resistance が defended した時の本命 entry
- when it appears: shallow retest が sweep され、より深い defense で止まった時
- what the human should do: defense が本当に維持されるか確認する
- what it must not mean: 逆張りの無謀な拾いではない

### invalidation_zone

- meaning: その仮説が壊れる価格帯
- when it appears: support / resistance が明確に破られる時
- what the human should do: それ以上は追わず、シナリオを切る
- what it must not mean: TP の延長線上ではない

### reclaim_trigger

- meaning: 一度失った水準を再び取り戻すきっかけ
- when it appears: defense 後に価格が元の帯域へ戻る時
- what the human should do: 反転確認の条件として扱う
- what it must not mean: ただのノイズ回帰ではない

### continuation_trigger

- meaning: defense が維持された後の継続確認条件
- when it appears: defense zone が守られ、流れが伸びる時
- what the human should do: continuation の可能性を再評価する
- what it must not mean: 初動の勢いだけで決め打ちすることではない

## Long Scenario Example

Observation example only. These are not hardcoded future thresholds.

- current / reference price: around 61,567
- shallow retest zone: 61,467-61,555
- value defense zone: 61,280-61,350
- invalidation: around 61,200-61,219 clear break
- reclaim trigger: around 61,400
- continuation trigger: around 61,500
- TP references: around 61,864 / 62,173

Interpretation:

- shallow retest is still valid as a quick check
- if price sweeps lower into the defense zone and holds, that may be the more practical entry
- if the invalidation zone breaks clearly, the scenario is invalid
- if reclaim / continuation triggers print after defense, the human can re-evaluate the earlier bias

## Scenario Lifecycle

### Long side

- `long_bias`: direction bias exists
- `pullback_wait`: price is pulling back and we wait
- `shallow_retest_risk`: shallow entry is possible, but depth may be too shallow
- `support_test`: price is testing support
- `defense_zone_touched`: value defense zone is touched
- `support_defended`: defense holds
- `reclaim_wait`: wait for reclaim confirmation
- `continuation_candidate`: continuation after defense is plausible
- `invalidated`: support broke clearly

### Short side

- `short_bias`: direction bias exists
- `rebound_wait`: price is rebounding and we wait
- `shallow_retest_risk`: shallow short entry is possible, but depth may be too shallow
- `resistance_test`: price is testing resistance
- `defense_zone_touched`: value defense zone is touched
- `resistance_defended`: defense holds
- `breakdown_wait`: wait for breakdown confirmation
- `continuation_candidate`: continuation after defense is plausible
- `invalidated`: resistance broke clearly

## Display Requirements

Notification / detail HTML should eventually present this in a human-readable order:

- direction bias is not an entry instruction
- show `今すぐ成行` separately from `浅い押し目` and `本命押し目`
- mark shallow entry as higher-risk if value defense zone is still below
- show invalidation and reclaim trigger before TP emphasis
- chart should prioritize defense / reclaim / invalidation over decorative TP / SL clutter

## Payload Proposal

Report-only payload shape proposal:

```text
value_defense_entry_layer
  - schema_version
  - side
  - lifecycle_state
  - market_entry_status
  - shallow_retest_zone
  - shallow_retest_risk
  - value_defense_zone
  - defense_zone_basis
  - invalidation_zone
  - reclaim_trigger
  - continuation_trigger
  - operator_guidance
  - safety_boundary
```

This is proposal only.

## Self-Review Extension

New review dimensions:

- `direction_quality`
- `execution_gate_quality`
- `entry_depth_quality`
- `scenario_lifecycle_result`
- `value_defense_result`

Possible values:

- `direction_quality`: `good` / `weak` / `wrong` / `unresolved`
- `entry_depth_quality`: `good` / `too_shallow` / `too_deep` / `missed_value_entry` / `unresolved`
- `scenario_lifecycle_result`: `support_defended` / `reclaim_pending` / `scenario_validated` / `scenario_invalidated` / `unresolved`
- `value_defense_result`: `value_entry_validated` / `defense_failed` / `not_touched` / `unresolved`

The key distinction is:

- direction_quality says whether the bias itself was reasonable
- entry_depth_quality says whether the first entry was shallow or practical
- scenario_lifecycle_result says whether the defense / reclaim / continuation path actually played out
- value_defense_result says whether the deeper defense entry was the better one

## Implementation Plan

### Phase 1

- derive report-only value defense fields from existing setup / support / resistance / current price data
- no scoring change
- no notification sending change

### Phase 2

- surface fields in detail HTML and operator guidance
- keep shallow / current entry visible but label it correctly

### Phase 3

- update self-review to score entry depth separately from direction

### Phase 4

- only after observations, consider scoring / gate tuning

## Non-Goals

- no auto order
- no formal go
- no live AI trading judgment
- no runtime change in this design task
- no threshold tuning yet
- no generated artifact commit
