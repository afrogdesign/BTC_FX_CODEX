# 運用フォーカス分析

- 対象 shadow 行数: 669 / 全体 1489
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-16

## AI backlog
- 未処理 backlog 候補: 34件
- 年齢分布: 2-3日=14件, 8日以上=13件, 4-7日=5件, 0-1日=2件
- phase1 観測タイプ: blocked=25件, setup_watch_learning=9件
- setup status: watch=20件, invalid=14件
- prelabel: SWEEP_WAIT=12件, NO_TRADE_CANDIDATE=11件, RISKY_ENTRY=10件, ENTRY_OK=1件
- signal_tier: normal=34件
- 直近 backlog 例:
  - 20260514_160500: 2026-05-15 01:05 / watch/entry_zone_not_reached / prelabel=RISKY_ENTRY / phase1=setup_watch_learning
  - 20260514_150500: 2026-05-15 00:05 / invalid/confidence_below_min / prelabel=RISKY_ENTRY / phase1=blocked
  - 20260514_110500: 2026-05-14 20:05 / invalid/inside_entry_zone_with_trigger / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260514_080500: 2026-05-14 17:05 / watch/entry_zone_not_reached / prelabel=RISKY_ENTRY / phase1=setup_watch_learning
  - 20260514_050500: 2026-05-14 14:05 / invalid/confidence_below_min / prelabel=RISKY_ENTRY / phase1=blocked

## Phase1 観測
- pass: 137件 / blocked: 532件
- pass 内訳: setup_watch_learning=131件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=350件, no_trade_candidate=192件, no_directional_setup=77件, watch_conditions_not_met=42件, setup_not_observable=1件
- setup_watch_learning: 131件 / 平均 execution=31.0 / 平均 wait=40.0
- setup_watch の主な reason: entry_zone_not_reached=84件, near_entry_zone_waiting_trigger=35件, inside_entry_zone_with_trigger=12件
- setup_watch の主な risk_flags: sweep_incomplete=95件, lower_liquidity_close=84件, orderbook_ask_heavy=36件, long_flush_exhaustion=20件, ask_wall_close=19件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 350件
  - prelabel: SWEEP_WAIT=172件, NO_TRADE_CANDIDATE=130件, RISKY_ENTRY=48件
  - setup status: invalid=178件, watch=172件
  - setup reason: confidence_below_min=350件
  - risk_flags: sweep_incomplete=300件, lower_liquidity_close=255件, orderbook_ask_heavy=126件, ask_wall_close=125件
  - 代表例: 20260515_180500, 20260515_170500, 20260515_160500
- no_trade_candidate: 192件
  - prelabel: NO_TRADE_CANDIDATE=192件
  - setup status: invalid=192件
  - setup reason: confidence_below_min=130件, near_entry_zone_waiting_trigger=31件, entry_zone_not_reached=26件, inside_entry_zone_with_trigger=4件
  - risk_flags: sweep_incomplete=184件, lower_liquidity_close=160件, ask_wall_close=133件, orderbook_ask_heavy=90件
  - 代表例: 20260515_180500, 20260515_170500, 20260515_160500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 221件 / 平均 execution=13.4 / 平均 wait=88.8
  - 補助flag: orderbook_ask_heavy=100件, ask_wall_close=94件, long_flush_exhaustion=73件, 補助flagなし=48件
- no_trade_candidate: 152件 / 平均 execution=11.1 / 平均 wait=82.0
  - 補助flag: ask_wall_close=125件, orderbook_ask_heavy=83件, long_flush_exhaustion=64件, 補助flagなし=1件

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
