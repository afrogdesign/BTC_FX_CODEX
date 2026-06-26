# entry / wait / price-distance 再設計仕様

## 目的

paper entry / wait / price-distance の再設計を実装する。  
目的は、紙候補の entry 発火を雑に増やすことではなく、`sl_hit` に偏っている `market_map_opportunity` の候補品質を改善すること。

特に以下を改善対象にする。

- high wait による late entry / late wait SL
- low execution による弱い発火
- long 側の弱さ
- trend_flip_confirmed_up の弱さ
- entry_not_reached / missed_opportunity を約定後損益と混同しないこと

## 背景

`paper_entry_sl_wait_redesign_20260601.md` では以下が出ている。

- `high_wait_sl_risk: triggered`
- `low_execution_sl_risk: triggered`
- `long_side_sl_risk: triggered`
- `trend_flip_up_sl_risk: triggered`
- `sl_too_tight_review_risk: triggered`
- `entry_delay_review_risk: triggered`

`soft_risk_collateral_damage_20260601.md` では B/C 単独 soft risk は `monitor_only` であり、現時点では hard blocker 化しない。  
`quality_guard_effectiveness_20260601.md` では A hard 含みは失敗寄りが強く、`A=require_execution_for_high_wait` 系は hard blocker 維持が妥当。

したがって次回実装は gate 緩和ではなく、paper candidate の entry / wait / price-distance 側を段階的に調整する。

## 対象ブランチ

`ver02.6-v2`

## 実装対象

主対象:

- `src/trade/opportunity_gate.py`

必要に応じて:

- `tests/test_phase1_trade_plans.py`
- `tests/test_log_feedback.py`
- `運用資料/NEXT_TASK.md`
- `運用資料/reports/report_hub_latest.md`

## 実装方針

### 1. high wait recheck

`market_map_opportunity` 候補で `wait>=60` の場合、即 entry 扱いを避ける。  
ただし一律除外ではなく、以下のいずれかを満たす場合だけ paper candidate として維持する。

- `execution>=24`
- setup reason が `near_entry_zone_waiting_trigger`
- 15分足執行チェックが `wait_only` ではなく、entry 側に寄っている
- `failed_breakout_down_reversal` / `support_to_resistance_flip` のような short continuation 系があり、`side=short`

満たさない場合は paper candidate を抑制し、reason に `entry_recheck_required_high_wait` を追加する。

### 2. low execution recheck

`execution<24` の `market_map_opportunity` は、paper candidate 化を一段抑制する。  
ただし以下の条件を満たす場合は観測候補として残す。

- `direction>=70`
- `wait<60`
- `side=short`
- `support_to_resistance_flip` または `trend_flip_confirmed_down` を含む

満たさない場合は paper candidate を抑制し、reason に `entry_recheck_required_low_execution` を追加する。

### 3. long side stricter confirmation

`side=long` は現状弱いため、`market_map_opportunity` の long 候補は一段厳しくする。  
long 候補では以下のいずれかが必要。

- `execution>=28`
- `wait<55`
- `resistance_to_support_flip` かつ `resistance_to_support_retest_confirmed`
- `major_support_rejection` があり、`trend_flip_confirmed_up` 単独ではない

満たさない場合は paper candidate を抑制し、reason に `entry_recheck_required_long_weakness` を追加する。

### 4. trend_flip_confirmed_up suppress

`trend_flip_confirmed_up` は強評価へ戻さない。  
`trend_flip_confirmed_up` を含む long 候補は、以下を満たさない限り paper candidate を抑制する。

- `execution>=30`
- `wait<55`
- `resistance_to_support_flip` または `major_support_rejection` を伴う
- `long_into_major_resistance` を同時に含まない

満たさない場合は reason に `entry_recheck_required_trend_flip_up` を追加する。

### 5. price-distance / entry zone 再確認

`entry_zone_not_reached` または `near_entry_zone_waiting_trigger` の候補は、価格距離が遠いまま paper candidate 化されないようにする。  
既存で entry distance / price-distance 系の値が取れる場合はそれを使う。  
取れない場合は、今回はロジック変更ではなく `price_distance_missing` を reason に出すだけにする。  
無理に新しい価格距離計算を作らない。

## 重要な制約

- `trade_execution_gate` は変更しない
- `phase1b_lite_gate` は変更しない
- `opportunity_gate` の既存 hard quality guard は緩和しない
- B/C 単独 soft risk は hard blocker 化しない
- `A=require_execution_for_high_wait` 系は hard blocker 維持
- `trend_flip_confirmed_up` を強評価へ戻さない
- `paper_orders planned` を増やす目的の変更はしない
- 実弾発注はしない
- 取引所 API 送信はしない
- 秘密鍵連携はしない

## 出力・記録要件

次回実装では、該当候補に以下の reason を出せるようにする。

- `entry_recheck_required_high_wait`
- `entry_recheck_required_low_execution`
- `entry_recheck_required_long_weakness`
- `entry_recheck_required_trend_flip_up`
- `price_distance_missing`

出力先は既存の `opportunity_reasons` / paper candidate reason の流儀に合わせる。  
新しい CSV を増やさない。

## テスト要件

`tests/test_phase1_trade_plans.py` に以下を追加する。

- `wait>=60` かつ `execution<24` の候補が `entry_recheck_required_high_wait` で抑制される
- `execution<24` かつ direction が弱い候補が `entry_recheck_required_low_execution` で抑制される
- long 候補が条件不足なら `entry_recheck_required_long_weakness` で抑制される
- `trend_flip_confirmed_up` long 候補が条件不足なら `entry_recheck_required_trend_flip_up` で抑制される
- `side=short` かつ `support_to_resistance_flip + execution>=24` の候補は過剰抑制されない
- B/C 単独 soft risk が hard blocker 化されていない
- `trade_execution_gate` / `phase1b_lite_gate` の既存テストが壊れない

## 検証コマンド

```bash
./.venv312/bin/python -m unittest tests.test_phase1_trade_plans
./.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback
./.venv312/bin/python tools/log_feedback.py --paper-entry-sl-wait-redesign
./.venv312/bin/python tools/log_feedback.py --soft-risk-collateral-damage
./.venv312/bin/python tools/log_feedback.py --report-hub
git diff --check
```

## 完了条件

- high wait / low execution / long weak / trend_flip_confirmed_up の再確認 reason が出る
- paper candidate の品質改善が目的であり、planned を増やす目的ではない
- B/C 単独 soft risk は hard blocker 化していない
- `trade_execution_gate` / `phase1b_lite_gate` は変更していない
- report hub / `NEXT_TASK.md` は必要最小限更新
- active spec は実装後に archive へ移動する
