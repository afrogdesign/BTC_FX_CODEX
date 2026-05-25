# 運用フォーカス分析

- 対象 shadow 行数: 906 / 全体 1726
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-26

## AI backlog
- 未処理 backlog 候補: 38件
- 年齢分布: 8日以上=29件, 2-3日=8件, 0-1日=1件
- phase1 観測タイプ: blocked=29件, setup_watch_learning=9件
- setup status: watch=21件, invalid=16件, ready=1件
- prelabel: SWEEP_WAIT=14件, NO_TRADE_CANDIDATE=13件, RISKY_ENTRY=8件, ENTRY_OK=3件
- signal_tier: normal=38件
- 直近 backlog 例:
  - 20260524_150500: 2026-05-25 00:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260524_130500: 2026-05-24 22:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260524_100500: 2026-05-24 19:05 / invalid/confidence_below_min / prelabel=RISKY_ENTRY / phase1=blocked
  - 20260524_080500: 2026-05-24 17:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260524_030500: 2026-05-24 12:05 / invalid/confidence_below_min / prelabel=RISKY_ENTRY / phase1=blocked

## Phase1 観測
- pass: 167件 / blocked: 739件
- pass 内訳: setup_watch_learning=161件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=519件, no_trade_candidate=263件, no_directional_setup=99件, watch_conditions_not_met=50件, setup_not_observable=3件
- setup_watch_learning: 161件 / 平均 execution=31.0 / 平均 wait=41.1
- setup_watch の主な reason: entry_zone_not_reached=102件, near_entry_zone_waiting_trigger=45件, inside_entry_zone_with_trigger=14件
- setup_watch の主な risk_flags: sweep_incomplete=114件, lower_liquidity_close=85件, orderbook_ask_heavy=38件, upper_liquidity_close=37件, support_to_resistance_flip=36件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 519件
  - prelabel: SWEEP_WAIT=249件, NO_TRADE_CANDIDATE=195件, RISKY_ENTRY=75件
  - setup status: invalid=270件, watch=249件
  - setup reason: confidence_below_min=519件
  - risk_flags: sweep_incomplete=438件, lower_liquidity_close=280件, upper_liquidity_close=201件, short_into_major_support=192件
  - 代表例: 20260525_140500, 20260525_130500, 20260525_090500
- no_trade_candidate: 263件
  - prelabel: NO_TRADE_CANDIDATE=263件
  - setup status: invalid=263件
  - setup reason: confidence_below_min=195件, near_entry_zone_waiting_trigger=35件, entry_zone_not_reached=28件, inside_entry_zone_with_trigger=4件
  - risk_flags: sweep_incomplete=250件, lower_liquidity_close=173件, ask_wall_close=142件, orderbook_ask_heavy=100件
  - 代表例: 20260525_140500, 20260525_130500, 20260525_110500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 241件 / 平均 execution=13.3 / 平均 wait=88.9
  - 補助flag: orderbook_ask_heavy=111件, ask_wall_close=104件, long_flush_exhaustion=78件, 補助flagなし=51件
- no_trade_candidate: 164件 / 平均 execution=11.1 / 平均 wait=82.8
  - 補助flag: ask_wall_close=133件, orderbook_ask_heavy=92件, long_flush_exhaustion=67件, 補助flagなし=2件

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
