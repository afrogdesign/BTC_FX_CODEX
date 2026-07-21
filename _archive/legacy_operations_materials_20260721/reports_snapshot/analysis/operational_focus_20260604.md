# 運用フォーカス分析

- 対象 shadow 行数: 1134 / 全体 1954
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-06-04

## AI backlog
- 未処理 backlog 候補: 17件
- 年齢分布: 8日以上=14件, 0-1日=2件, 2-3日=1件
- phase1 観測タイプ: blocked=12件, setup_watch_learning=5件
- setup status: watch=9件, invalid=8件
- prelabel: NO_TRADE_CANDIDATE=8件, SWEEP_WAIT=5件, RISKY_ENTRY=3件, ENTRY_OK=1件
- signal_tier: normal=17件
- 直近 backlog 例:
  - 20260603_010500: 2026-06-03 10:05 / invalid/entry_zone_not_reached / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260602_190500: 2026-06-03 04:05 / invalid/entry_zone_not_reached / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260601_180500: 2026-06-02 03:05 / invalid/near_entry_zone_waiting_trigger / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260510_190500: 2026-05-11 04:05 / watch/near_entry_zone_waiting_trigger / prelabel=RISKY_ENTRY / phase1=setup_watch_learning
  - 20260425_220500: 2026-04-26 07:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked

## Phase1 観測
- pass: 240件 / blocked: 894件
- pass 内訳: setup_watch_learning=234件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=591件, no_trade_candidate=338件, no_directional_setup=114件, watch_conditions_not_met=72件, setup_not_observable=3件
- setup_watch_learning: 234件 / 平均 execution=31.7 / 平均 wait=39.8
- setup_watch の主な reason: entry_zone_not_reached=162件, near_entry_zone_waiting_trigger=54件, inside_entry_zone_with_trigger=18件
- setup_watch の主な risk_flags: sweep_incomplete=169件, support_to_resistance_flip=91件, support_to_resistance_retest_confirmed=90件, upper_liquidity_close=89件, lower_liquidity_close=85件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 591件
  - prelabel: SWEEP_WAIT=280件, NO_TRADE_CANDIDATE=224件, RISKY_ENTRY=87件
  - setup status: invalid=311件, watch=280件
  - setup reason: confidence_below_min=591件
  - risk_flags: sweep_incomplete=496件, lower_liquidity_close=292件, upper_liquidity_close=254件, short_into_major_support=249件
  - 代表例: 20260601_050500, 20260601_010501, 20260601_000500
- no_trade_candidate: 338件
  - prelabel: NO_TRADE_CANDIDATE=338件
  - setup status: invalid=338件
  - setup reason: confidence_below_min=224件, entry_zone_not_reached=59件, near_entry_zone_waiting_trigger=49件, inside_entry_zone_with_trigger=5件
  - risk_flags: sweep_incomplete=322件, lower_liquidity_close=178件, upper_liquidity_close=160件, ask_wall_close=146件
  - 代表例: 20260604_040500, 20260604_010500, 20260603_190500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 251件 / 平均 execution=13.3 / 平均 wait=88.9
  - 補助flag: orderbook_ask_heavy=115件, ask_wall_close=107件, long_flush_exhaustion=82件, 補助flagなし=53件
- no_trade_candidate: 168件 / 平均 execution=10.9 / 平均 wait=83.2
  - 補助flag: ask_wall_close=136件, orderbook_ask_heavy=94件, long_flush_exhaustion=69件, 補助flagなし=2件

## 緩和候補の少数群
- 20260530_230500: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=81.6
- 20260527_160500: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=73.6
- 20260522_030500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=15.0 / wait=80.0
- 20260520_050500: confidence_below_min / prelabel=NO_TRADE_CANDIDATE / setup=confidence_below_min / execution=5.0 / wait=100.0
- 20260517_220500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8

## Phase 1B 昇格候補
- 候補件数: 6件 / 平均 direction=59.8 / 平均 execution=23.0 / 平均 wait=75.2
- prelabel: SWEEP_WAIT=6件
- 20260509_212745: confidence_below_min / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
- 20260507_190500: confidence_below_min / prelabel=SWEEP_WAIT / direction=68.0 / execution=25.0 / wait=56.0
- 20260503_120500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=84.8
- 20260502_210500: confidence_below_min / prelabel=SWEEP_WAIT / direction=55.0 / execution=25.0 / wait=80.0
- 20260424_130500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
