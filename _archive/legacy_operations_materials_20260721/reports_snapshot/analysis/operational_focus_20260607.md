# 運用フォーカス分析

- 対象 shadow 行数: 1190 / 全体 2010
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-06-07

## AI backlog
- 未処理 backlog 候補: 18件
- 年齢分布: 8日以上=9件, 2-3日=8件, 0-1日=1件
- phase1 観測タイプ: blocked=11件, setup_watch_learning=7件
- setup status: watch=12件, invalid=6件
- prelabel: SWEEP_WAIT=8件, NO_TRADE_CANDIDATE=6件, ENTRY_OK=2件, RISKY_ENTRY=2件
- signal_tier: normal=18件
- 直近 backlog 例:
  - 20260605_170500: 2026-06-06 02:05 / invalid/near_entry_zone_waiting_trigger / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260605_140500: 2026-06-05 23:05 / watch/entry_zone_not_reached / prelabel=ENTRY_OK / phase1=setup_watch_learning
  - 20260605_120500: 2026-06-05 21:05 / watch/entry_zone_not_reached / prelabel=SWEEP_WAIT / phase1=setup_watch_learning
  - 20260605_080500: 2026-06-05 17:05 / watch/entry_zone_not_reached / prelabel=SWEEP_WAIT / phase1=setup_watch_learning
  - 20260605_050500: 2026-06-05 14:05 / watch/inside_entry_zone_with_trigger / prelabel=SWEEP_WAIT / phase1=blocked

## Phase1 観測
- pass: 265件 / blocked: 925件
- pass 内訳: setup_watch_learning=259件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=594件, no_trade_candidate=359件, no_directional_setup=116件, watch_conditions_not_met=79件, setup_not_observable=3件
- setup_watch_learning: 259件 / 平均 execution=31.7 / 平均 wait=39.3
- setup_watch の主な reason: entry_zone_not_reached=180件, near_entry_zone_waiting_trigger=61件, inside_entry_zone_with_trigger=18件
- setup_watch の主な risk_flags: sweep_incomplete=189件, support_to_resistance_flip=114件, support_to_resistance_retest_confirmed=113件, upper_liquidity_close=111件, trend_flip_confirmed_down=91件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 594件
  - prelabel: SWEEP_WAIT=281件, NO_TRADE_CANDIDATE=226件, RISKY_ENTRY=87件
  - setup status: invalid=313件, watch=281件
  - setup reason: confidence_below_min=594件
  - risk_flags: sweep_incomplete=499件, lower_liquidity_close=292件, upper_liquidity_close=257件, short_into_major_support=252件
  - 代表例: 20260604_210500, 20260604_200500, 20260604_170500
- no_trade_candidate: 359件
  - prelabel: NO_TRADE_CANDIDATE=359件
  - setup status: invalid=359件
  - setup reason: confidence_below_min=226件, entry_zone_not_reached=74件, near_entry_zone_waiting_trigger=52件, inside_entry_zone_with_trigger=6件
  - risk_flags: sweep_incomplete=341件, upper_liquidity_close=181件, lower_liquidity_close=178件, short_into_major_support=154件
  - 代表例: 20260606_180500, 20260606_170500, 20260606_100500

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
