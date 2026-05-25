# 運用フォーカス分析

- 対象 shadow 行数: 717 / 全体 1537
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-18

## AI backlog
- 未処理 backlog 候補: 40件
- 年齢分布: 4-7日=17件, 8日以上=13件, 2-3日=10件
- phase1 観測タイプ: blocked=33件, setup_watch_learning=7件
- setup status: watch=22件, invalid=18件
- prelabel: SWEEP_WAIT=16件, NO_TRADE_CANDIDATE=15件, RISKY_ENTRY=8件, ENTRY_OK=1件
- signal_tier: normal=40件
- 直近 backlog 例:
  - 20260516_060500: 2026-05-16 15:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260516_030500: 2026-05-16 12:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260516_020500: 2026-05-16 11:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260515_230500: 2026-05-16 08:05 / invalid/near_entry_zone_waiting_trigger / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260515_210500: 2026-05-16 06:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked

## Phase1 観測
- pass: 142件 / blocked: 575件
- pass 内訳: setup_watch_learning=136件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=385件, no_trade_candidate=207件, no_directional_setup=78件, watch_conditions_not_met=46件, setup_not_observable=1件
- setup_watch_learning: 136件 / 平均 execution=31.0 / 平均 wait=39.9
- setup_watch の主な reason: entry_zone_not_reached=89件, near_entry_zone_waiting_trigger=35件, inside_entry_zone_with_trigger=12件
- setup_watch の主な risk_flags: sweep_incomplete=99件, lower_liquidity_close=84件, orderbook_ask_heavy=36件, long_flush_exhaustion=23件, upper_liquidity_close=19件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 385件
  - prelabel: SWEEP_WAIT=191件, NO_TRADE_CANDIDATE=142件, RISKY_ENTRY=52件
  - setup status: invalid=194件, watch=191件
  - setup reason: confidence_below_min=385件
  - risk_flags: sweep_incomplete=330件, lower_liquidity_close=258件, orderbook_ask_heavy=129件, ask_wall_close=127件
  - 代表例: 20260517_170500, 20260517_160500, 20260517_150500
- no_trade_candidate: 207件
  - prelabel: NO_TRADE_CANDIDATE=207件
  - setup status: invalid=207件
  - setup reason: confidence_below_min=142件, near_entry_zone_waiting_trigger=33件, entry_zone_not_reached=27件, inside_entry_zone_with_trigger=4件
  - risk_flags: sweep_incomplete=198件, lower_liquidity_close=162件, ask_wall_close=135件, orderbook_ask_heavy=92件
  - 代表例: 20260517_170500, 20260517_130500, 20260517_120500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 224件 / 平均 execution=13.4 / 平均 wait=88.6
  - 補助flag: orderbook_ask_heavy=102件, ask_wall_close=96件, long_flush_exhaustion=74件, 補助flagなし=48件
- no_trade_candidate: 154件 / 平均 execution=11.1 / 平均 wait=82.0
  - 補助flag: ask_wall_close=127件, orderbook_ask_heavy=85件, long_flush_exhaustion=64件, 補助flagなし=1件

## 緩和候補の少数群
- 20260515_080500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_030500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=84.8
- 20260514_210500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=19.0 / wait=73.6
- 20260513_050501: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=73.6
- 20260513_040501: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=73.6

## Phase 1B 昇格候補
- 候補件数: 6件 / 平均 direction=59.8 / 平均 execution=23.0 / 平均 wait=75.2
- prelabel: SWEEP_WAIT=6件
- 20260509_212745: confidence_below_min / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
- 20260507_190500: confidence_below_min / prelabel=SWEEP_WAIT / direction=68.0 / execution=25.0 / wait=56.0
- 20260503_120500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=84.8
- 20260502_210500: confidence_below_min / prelabel=SWEEP_WAIT / direction=55.0 / execution=25.0 / wait=80.0
- 20260424_130500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
