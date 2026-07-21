# 運用フォーカス分析

- 対象 shadow 行数: 813 / 全体 1633
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-22

## AI backlog
- 未処理 backlog 候補: 38件
- 年齢分布: 8日以上=30件, 2-3日=5件, 4-7日=3件
- phase1 観測タイプ: blocked=29件, setup_watch_learning=9件
- setup status: watch=22件, invalid=16件
- prelabel: SWEEP_WAIT=15件, NO_TRADE_CANDIDATE=14件, RISKY_ENTRY=7件, ENTRY_OK=2件
- signal_tier: normal=38件
- 直近 backlog 例:
  - 20260520_130500: 2026-05-20 22:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260520_090500: 2026-05-20 18:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260520_070500: 2026-05-20 16:05 / watch/entry_zone_not_reached / prelabel=ENTRY_OK / phase1=setup_watch_learning
  - 20260520_020500: 2026-05-20 11:05 / invalid/entry_zone_not_reached / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260519_190500: 2026-05-20 04:05 / watch/near_entry_zone_waiting_trigger / prelabel=SWEEP_WAIT / phase1=setup_watch_learning

## Phase1 観測
- pass: 153件 / blocked: 660件
- pass 内訳: setup_watch_learning=147件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=458件, no_trade_candidate=235件, no_directional_setup=87件, watch_conditions_not_met=48件, setup_not_observable=1件
- setup_watch_learning: 147件 / 平均 execution=30.9 / 平均 wait=40.4
- setup_watch の主な reason: entry_zone_not_reached=95件, near_entry_zone_waiting_trigger=39件, inside_entry_zone_with_trigger=13件
- setup_watch の主な risk_flags: sweep_incomplete=107件, lower_liquidity_close=84件, orderbook_ask_heavy=38件, upper_liquidity_close=28件, long_flush_exhaustion=24件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 458件
  - prelabel: SWEEP_WAIT=227件, NO_TRADE_CANDIDATE=169件, RISKY_ENTRY=62件
  - setup status: invalid=231件, watch=227件
  - setup reason: confidence_below_min=458件
  - risk_flags: sweep_incomplete=393件, lower_liquidity_close=270件, upper_liquidity_close=155件, short_into_major_support=136件
  - 代表例: 20260521_180500, 20260521_170500, 20260521_160501
- no_trade_candidate: 235件
  - prelabel: NO_TRADE_CANDIDATE=235件
  - setup status: invalid=235件
  - setup reason: confidence_below_min=169件, near_entry_zone_waiting_trigger=33件, entry_zone_not_reached=28件, inside_entry_zone_with_trigger=4件
  - risk_flags: sweep_incomplete=225件, lower_liquidity_close=167件, ask_wall_close=139件, orderbook_ask_heavy=94件
  - 代表例: 20260521_180500, 20260521_160501, 20260521_130500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 234件 / 平均 execution=13.4 / 平均 wait=88.8
  - 補助flag: orderbook_ask_heavy=106件, ask_wall_close=101件, long_flush_exhaustion=75件, 補助flagなし=50件
- no_trade_candidate: 159件 / 平均 execution=11.1 / 平均 wait=82.4
  - 補助flag: ask_wall_close=131件, orderbook_ask_heavy=87件, long_flush_exhaustion=64件, 補助flagなし=2件

## 緩和候補の少数群
- 20260520_050500: confidence_below_min / prelabel=NO_TRADE_CANDIDATE / setup=confidence_below_min / execution=5.0 / wait=100.0
- 20260517_220500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_080500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_030500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=84.8
- 20260514_210500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=19.0 / wait=73.6

## Phase 1B 昇格候補
- 候補件数: 6件 / 平均 direction=59.8 / 平均 execution=23.0 / 平均 wait=75.2
- prelabel: SWEEP_WAIT=6件
- 20260509_212745: confidence_below_min / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
- 20260507_190500: confidence_below_min / prelabel=SWEEP_WAIT / direction=68.0 / execution=25.0 / wait=56.0
- 20260503_120500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=84.8
- 20260502_210500: confidence_below_min / prelabel=SWEEP_WAIT / direction=55.0 / execution=25.0 / wait=80.0
- 20260424_130500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
