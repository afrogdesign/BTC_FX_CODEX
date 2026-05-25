# 運用フォーカス分析

- 対象 shadow 行数: 765 / 全体 1585
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-20

## AI backlog
- 未処理 backlog 候補: 42件
- 年齢分布: 4-7日=18件, 8日以上=18件, 2-3日=6件
- phase1 観測タイプ: blocked=34件, setup_watch_learning=8件
- setup status: watch=25件, invalid=17件
- prelabel: SWEEP_WAIT=18件, NO_TRADE_CANDIDATE=14件, RISKY_ENTRY=8件, ENTRY_OK=2件
- signal_tier: normal=42件
- 直近 backlog 例:
  - 20260518_130500: 2026-05-18 22:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260518_040500: 2026-05-18 13:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260518_030500: 2026-05-18 12:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260518_000500: 2026-05-18 09:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260517_010500: 2026-05-17 10:05 / watch/entry_zone_not_reached / prelabel=ENTRY_OK / phase1=setup_watch_learning

## Phase1 観測
- pass: 148件 / blocked: 617件
- pass 内訳: setup_watch_learning=142件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=421件, no_trade_candidate=218件, no_directional_setup=84件, watch_conditions_not_met=46件, setup_not_observable=1件
- setup_watch_learning: 142件 / 平均 execution=30.9 / 平均 wait=40.2
- setup_watch の主な reason: entry_zone_not_reached=92件, near_entry_zone_waiting_trigger=37件, inside_entry_zone_with_trigger=13件
- setup_watch の主な risk_flags: sweep_incomplete=103件, lower_liquidity_close=84件, orderbook_ask_heavy=36件, upper_liquidity_close=25件, long_flush_exhaustion=23件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 421件
  - prelabel: SWEEP_WAIT=211件, NO_TRADE_CANDIDATE=153件, RISKY_ENTRY=57件
  - setup status: watch=211件, invalid=210件
  - setup reason: confidence_below_min=421件
  - risk_flags: sweep_incomplete=364件, lower_liquidity_close=266件, orderbook_ask_heavy=133件, ask_wall_close=132件
  - 代表例: 20260519_160500, 20260519_140500, 20260519_130500
- no_trade_candidate: 218件
  - prelabel: NO_TRADE_CANDIDATE=218件
  - setup status: invalid=218件
  - setup reason: confidence_below_min=153件, near_entry_zone_waiting_trigger=33件, entry_zone_not_reached=27件, inside_entry_zone_with_trigger=4件
  - risk_flags: sweep_incomplete=209件, lower_liquidity_close=165件, ask_wall_close=138件, orderbook_ask_heavy=94件
  - 代表例: 20260519_160500, 20260519_060500, 20260519_030500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 231件 / 平均 execution=13.4 / 平均 wait=88.7
  - 補助flag: orderbook_ask_heavy=105件, ask_wall_close=100件, long_flush_exhaustion=75件, 補助flagなし=49件
- no_trade_candidate: 157件 / 平均 execution=11.1 / 平均 wait=82.3
  - 補助flag: ask_wall_close=130件, orderbook_ask_heavy=87件, long_flush_exhaustion=64件, 補助flagなし=1件

## 緩和候補の少数群
- 20260517_220500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_080500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_030500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=84.8
- 20260514_210500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=19.0 / wait=73.6
- 20260513_050501: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=73.6

## Phase 1B 昇格候補
- 候補件数: 6件 / 平均 direction=59.8 / 平均 execution=23.0 / 平均 wait=75.2
- prelabel: SWEEP_WAIT=6件
- 20260509_212745: confidence_below_min / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
- 20260507_190500: confidence_below_min / prelabel=SWEEP_WAIT / direction=68.0 / execution=25.0 / wait=56.0
- 20260503_120500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=84.8
- 20260502_210500: confidence_below_min / prelabel=SWEEP_WAIT / direction=55.0 / execution=25.0 / wait=80.0
- 20260424_130500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
