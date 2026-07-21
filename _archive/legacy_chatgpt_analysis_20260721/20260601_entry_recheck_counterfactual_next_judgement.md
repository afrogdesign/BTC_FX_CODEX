# 20260601 entry recheck counterfactual 次判断メモ

## 目的

`paper_entry_sl_wait_redesign_20260601.md` の `entry recheck counterfactual impact` を読み、次の実装判断を整理する。  
今回は実装を行わず、次回の active spec 化対象を明確化する。

## 前提

- `entry recheck reason impact`（logged）は過去ログに reason 未保存のため `entry_recheck_any=0件`。
- `entry recheck counterfactual impact` は BTCFX-08 条件の後付け再計算であり、過去候補への影響を推定する材料。
- この集計は実弾 gate 変更材料ではなく、紙候補品質の再設計材料として扱う。

## 評価

### entry_recheck_required_high_wait

- `count=13 / entered_count=12 / sl_hit_rate=91.7% / tp2_hit_rate=0.0% / judgement=risk_confirmed`。
- 高 wait は失敗寄りが明確で、危険候補として有力。
- ただし単独 hard blocker 化は即断せず、`entry_recheck_none` 側の巻き込みを合わせて判断する。

### entry_recheck_required_low_execution

- `count=55 / entered_count=41 / sl_hit_rate=82.9% / tp2_hit_rate=9.8% / judgement=risk_confirmed`。
- 母数が多く、`sl_hit` 偏重も強い。危険候補として高優先度。
- 高 wait と同様、閾値の即時強化より先に collateral damage を再評価する。

### entry_recheck_required_long_weakness

- `count=0 / judgement=insufficient_n`。
- 現ロジック上で該当が立っていないため、まず条件定義とデータ適合を確認する段階。
- この理由だけを根拠にした gate 変更は現時点で不可。

### entry_recheck_required_trend_flip_up

- `count=7 / entered_count=7 / sl_hit_rate=85.7% / tp2_hit_rate=14.3% / judgement=insufficient_n`。
- 件数は少ないが失敗率は高い。監視継続は必要。
- `trend_flip_confirmed_up` を強評価へ戻す根拠にはならない。

### price_distance_missing

- `count=17 / entered_count=13 / sl_hit_rate=69.2% / tp2_hit_rate=15.4% / judgement=monitor_only`。
- 距離情報欠損は品質確認上の warning として扱う。
- `price_distance_missing` は non-blocking を維持し、blocking reason へは上げない。

### entry_recheck_none の collateral damage risk

- `count=50 / entered_count=26 / tp2_hit_rate=19.2% / missed_opportunity=24 / judgement=collateral_damage_risk`。
- recheck 非該当群にも missed 側の巻き込みが大きく、単純な hard blocker 強化は副作用リスクが高い。
- 結論として、high_wait / low_execution の危険性を認めつつも、直ちに全体 hard 化しない。

## すぐ実装へ進まない理由

- counterfactual は後付け再計算であり、実運用時に出た reason ではない。
- `entry_recheck_none` に collateral damage risk が出ており、単純な抑制強化で機会損失を増やす可能性がある。
- `entry_recheck_required_long_weakness` が 0 件で、long 条件の見直しは定義検証が先。
- まず「どの条件をどの閾値で微調整するか」を仕様化してから実装すべき。

## 今回の結論（固定）

- 今回は `gate / score / opportunity_gate` を変更しない。
- high_wait と low_execution は危険候補として有力。
- ただし `entry_recheck_none` の collateral damage risk があるため、単純な hard blocker 化はしない。
- `price_distance_missing` は blocking reason にしない。
- `trend_flip_confirmed_up` は強評価へ戻さない。
- Phase 1B 昇格判断には使わない。

## 次に active spec 化する候補

1. `entry recheck 条件微調整 active spec`
   - high_wait / low_execution の keep 条件と閾値を局所的に調整する。
   - `entry_recheck_none` 巻き込みを抑える条件を同時に定義する。
2. `collateral damage 追加診断 active spec`
   - `entry_recheck_none` を side / wait / execution / setup reason 単位で追加分解する。
   - hard 化前に missed/opportunity 巻き込みの発生源を特定する。
