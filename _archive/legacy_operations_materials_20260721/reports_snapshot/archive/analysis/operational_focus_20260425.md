# 運用フォーカス分析

- 対象 shadow 行数: 171 / 全体 991
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-04-25

## AI backlog
- 未処理 backlog 候補: 20件
- 年齢分布: 2-3日=13件, 4-7日=5件, 0-1日=2件
- phase1 観測タイプ: blocked=13件, setup_watch_learning=7件
- setup status: watch=14件, invalid=6件
- prelabel: SWEEP_WAIT=10件, NO_TRADE_CANDIDATE=6件, RISKY_ENTRY=3件, ENTRY_OK=1件
- signal_tier: normal=20件
- 直近 backlog 例:
  - 20260423_160501: 2026-04-24 01:05 / watch/near_entry_zone_waiting_trigger / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260423_150500: 2026-04-24 00:05 / watch/near_entry_zone_waiting_trigger / prelabel=RISKY_ENTRY / phase1=setup_watch_learning
  - 20260423_130500: 2026-04-23 22:05 / watch/near_entry_zone_waiting_trigger / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260423_100500: 2026-04-23 19:05 / watch/near_entry_zone_waiting_trigger / prelabel=SWEEP_WAIT / phase1=setup_watch_learning
  - 20260423_060500: 2026-04-23 15:05 / watch/near_entry_zone_waiting_trigger / prelabel=SWEEP_WAIT / phase1=blocked

## Phase1 観測
- pass: 27件 / blocked: 144件
- pass 内訳: setup_watch_learning=26件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=84件, no_trade_candidate=59件, no_directional_setup=22件, watch_conditions_not_met=18件
- setup_watch_learning: 26件 / 平均 execution=32.8 / 平均 wait=38.8
- setup_watch の主な reason: entry_zone_not_reached=16件, near_entry_zone_waiting_trigger=8件, inside_entry_zone_with_trigger=2件
- setup_watch の主な risk_flags: lower_liquidity_close=19件, sweep_incomplete=19件, orderbook_ask_heavy=9件, long_flush_exhaustion=5件, ask_wall_close=3件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 84件
  - prelabel: NO_TRADE_CANDIDATE=39件, SWEEP_WAIT=38件, RISKY_ENTRY=7件
  - setup status: invalid=46件, watch=38件
  - setup reason: confidence_below_min=84件
  - risk_flags: sweep_incomplete=76件, lower_liquidity_close=74件, orderbook_ask_heavy=39件, ask_wall_close=32件
  - 代表例: 20260424_180500, 20260424_170500, 20260424_160500
- no_trade_candidate: 59件
  - prelabel: NO_TRADE_CANDIDATE=59件
  - setup status: invalid=59件
  - setup reason: confidence_below_min=39件, entry_zone_not_reached=10件, near_entry_zone_waiting_trigger=7件, inside_entry_zone_with_trigger=2件
  - risk_flags: sweep_incomplete=57件, lower_liquidity_close=56件, ask_wall_close=46件, orderbook_ask_heavy=31件
  - 代表例: 20260424_150500, 20260424_070500, 20260424_050500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 67件 / 平均 execution=12.7 / 平均 wait=91.4
  - 補助flag: orderbook_ask_heavy=33件, long_flush_exhaustion=27件, ask_wall_close=27件, 補助flagなし=13件
- no_trade_candidate: 54件 / 平均 execution=11.6 / 平均 wait=82.2
  - 補助flag: ask_wall_close=44件, orderbook_ask_heavy=29件, long_flush_exhaustion=21件, 補助flagなし=1件

## 緩和候補の少数群
- 20260424_130500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=22.0 / wait=76.8
- 20260421_140500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260421_060500: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=81.6
- 20260421_020500: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=65.6
- 20260420_180500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
