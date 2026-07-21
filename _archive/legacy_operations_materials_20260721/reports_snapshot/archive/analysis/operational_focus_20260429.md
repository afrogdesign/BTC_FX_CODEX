# 運用フォーカス分析

- 対象 shadow 行数: 265 / 全体 1085
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-04-29

## AI backlog
- 未処理 backlog 候補: 18件
- 年齢分布: 8日以上=9件, 4-7日=5件, 2-3日=4件
- phase1 観測タイプ: blocked=14件, setup_watch_learning=4件
- setup status: watch=12件, invalid=6件
- prelabel: SWEEP_WAIT=9件, NO_TRADE_CANDIDATE=6件, RISKY_ENTRY=2件, ENTRY_OK=1件
- signal_tier: normal=18件
- 直近 backlog 例:
  - 20260427_170500: 2026-04-28 02:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260427_160500: 2026-04-28 01:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260426_230500: 2026-04-27 08:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked
  - 20260426_200500: 2026-04-27 05:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260426_040500: 2026-04-26 13:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked

## Phase1 観測
- pass: 33件 / blocked: 232件
- pass 内訳: setup_watch_learning=32件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=147件, no_trade_candidate=81件, no_directional_setup=46件, watch_conditions_not_met=18件
- setup_watch_learning: 32件 / 平均 execution=31.8 / 平均 wait=42.6
- setup_watch の主な reason: entry_zone_not_reached=18件, near_entry_zone_waiting_trigger=10件, inside_entry_zone_with_trigger=4件
- setup_watch の主な risk_flags: sweep_incomplete=24件, lower_liquidity_close=21件, orderbook_ask_heavy=12件, long_flush_exhaustion=5件, upper_liquidity_close=4件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 147件
  - prelabel: SWEEP_WAIT=71件, NO_TRADE_CANDIDATE=60件, RISKY_ENTRY=16件
  - setup status: invalid=76件, watch=71件
  - setup reason: confidence_below_min=147件
  - risk_flags: sweep_incomplete=128件, lower_liquidity_close=116件, ask_wall_close=58件, orderbook_ask_heavy=57件
  - 代表例: 20260428_180500, 20260428_170500, 20260428_160500
- no_trade_candidate: 81件
  - prelabel: NO_TRADE_CANDIDATE=81件
  - setup status: invalid=81件
  - setup reason: confidence_below_min=60件, entry_zone_not_reached=11件, near_entry_zone_waiting_trigger=7件, inside_entry_zone_with_trigger=2件
  - risk_flags: sweep_incomplete=78件, lower_liquidity_close=72件, ask_wall_close=59件, orderbook_ask_heavy=41件
  - 代表例: 20260428_170500, 20260428_140500, 20260428_090500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 102件 / 平均 execution=13.2 / 平均 wait=91.0
  - 補助flag: orderbook_ask_heavy=45件, ask_wall_close=43件, long_flush_exhaustion=36件, 補助flagなし=23件
- no_trade_candidate: 69件 / 平均 execution=10.8 / 平均 wait=85.3
  - 補助flag: ask_wall_close=56件, orderbook_ask_heavy=39件, long_flush_exhaustion=28件, 補助flagなし=1件

## 緩和候補の少数群
- 20260427_170500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=30.0 / wait=64.0
- 20260427_110500: confidence_below_min / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=81.6
- 20260427_100500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=17.0 / wait=84.8
- 20260426_210500: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=15.0 / wait=88.0
- 20260426_180501: confidence_below_min / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=17.0 / wait=92.8

## Phase 1B 昇格候補
- 候補件数: 2件 / 平均 direction=59.0 / 平均 execution=22.0 / 平均 wait=76.8
- prelabel: SWEEP_WAIT=2件
- 20260424_130500: confidence_below_min / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
- 20260420_130500: confidence_below_min / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
