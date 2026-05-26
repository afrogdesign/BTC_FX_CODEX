# 運用フォーカス分析

- 対象 shadow 行数: 917 / 全体 1737
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-26

## AI backlog
- 未処理 backlog 候補: 33件
- 年齢分布: 8日以上=29件, 0-1日=3件, 2-3日=1件
- phase1 観測タイプ: blocked=24件, setup_watch_learning=9件
- setup status: watch=20件, invalid=13件
- prelabel: SWEEP_WAIT=13件, NO_TRADE_CANDIDATE=11件, RISKY_ENTRY=8件, ENTRY_OK=1件
- signal_tier: normal=33件
- 直近 backlog 例:
  - 20260525_020500: 2026-05-25 11:05 / watch/near_entry_zone_waiting_trigger / prelabel=RISKY_ENTRY / phase1=setup_watch_learning
  - 20260524_200500: 2026-05-25 05:05 / invalid/confidence_below_min / prelabel=RISKY_ENTRY / phase1=blocked
  - 20260524_180500: 2026-05-25 03:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260523_190500: 2026-05-24 04:05 / watch/near_entry_zone_waiting_trigger / prelabel=SWEEP_WAIT / phase1=setup_watch_learning
  - 20260514_030500: 2026-05-14 12:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked

## Phase1 観測
- pass: 168件 / blocked: 749件
- pass 内訳: setup_watch_learning=162件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=528件, no_trade_candidate=268件, no_directional_setup=100件, watch_conditions_not_met=50件, setup_not_observable=3件
- setup_watch_learning: 162件 / 平均 execution=31.0 / 平均 wait=41.0
- setup_watch の主な reason: entry_zone_not_reached=103件, near_entry_zone_waiting_trigger=45件, inside_entry_zone_with_trigger=14件
- setup_watch の主な risk_flags: sweep_incomplete=115件, lower_liquidity_close=85件, orderbook_ask_heavy=38件, support_to_resistance_flip=37件, support_to_resistance_retest_confirmed=37件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 528件
  - prelabel: SWEEP_WAIT=252件, NO_TRADE_CANDIDATE=200件, RISKY_ENTRY=76件
  - setup status: invalid=276件, watch=252件
  - setup reason: confidence_below_min=528件
  - risk_flags: sweep_incomplete=446件, lower_liquidity_close=282件, upper_liquidity_close=207件, short_into_major_support=201件
  - 代表例: 20260526_030500, 20260526_020500, 20260526_010501
- no_trade_candidate: 268件
  - prelabel: NO_TRADE_CANDIDATE=268件
  - setup status: invalid=268件
  - setup reason: confidence_below_min=200件, near_entry_zone_waiting_trigger=35件, entry_zone_not_reached=28件, inside_entry_zone_with_trigger=4件
  - risk_flags: sweep_incomplete=255件, lower_liquidity_close=174件, ask_wall_close=143件, long_flush_exhaustion=100件
  - 代表例: 20260526_020500, 20260526_000500, 20260525_220500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 243件 / 平均 execution=13.3 / 平均 wait=88.9
  - 補助flag: orderbook_ask_heavy=111件, ask_wall_close=105件, long_flush_exhaustion=79件, 補助flagなし=51件
- no_trade_candidate: 165件 / 平均 execution=11.0 / 平均 wait=82.9
  - 補助flag: ask_wall_close=134件, orderbook_ask_heavy=92件, long_flush_exhaustion=67件, 補助flagなし=2件

## 緩和候補の少数群
- 20260522_030500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=15.0 / wait=80.0
- 20260520_050500: confidence_below_min / prelabel=NO_TRADE_CANDIDATE / setup=confidence_below_min / execution=5.0 / wait=100.0
- 20260517_220500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_080500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_030500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=84.8

## Phase 1B 昇格候補
- 候補件数: 6件 / 平均 direction=59.8 / 平均 execution=23.0 / 平均 wait=75.2
- prelabel: SWEEP_WAIT=6件
- 20260509_212745: confidence_below_min / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
- 20260507_190500: confidence_below_min / prelabel=SWEEP_WAIT / direction=68.0 / execution=25.0 / wait=56.0
- 20260503_120500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=84.8
- 20260502_210500: confidence_below_min / prelabel=SWEEP_WAIT / direction=55.0 / execution=25.0 / wait=80.0
- 20260424_130500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
