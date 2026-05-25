# 運用フォーカス分析

- 対象 shadow 行数: 885 / 全体 1705
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-25

## AI backlog
- 未処理 backlog 候補: 37件
- 年齢分布: 8日以上=30件, 2-3日=4件, 4-7日=2件, 0-1日=1件
- phase1 観測タイプ: blocked=29件, setup_watch_learning=8件
- setup status: watch=21件, invalid=15件, ready=1件
- prelabel: SWEEP_WAIT=15件, NO_TRADE_CANDIDATE=13件, RISKY_ENTRY=7件, ENTRY_OK=2件
- signal_tier: normal=37件
- 直近 backlog 例:
  - 20260523_150500: 2026-05-24 00:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260523_140500: 2026-05-23 23:05 / ready/inside_entry_zone_with_trigger / prelabel=ENTRY_OK / phase1=blocked
  - 20260523_050500: 2026-05-23 14:05 / invalid/confidence_below_min / prelabel=NO_TRADE_CANDIDATE / phase1=blocked
  - 20260523_040500: 2026-05-23 13:05 / watch/near_entry_zone_waiting_trigger / prelabel=SWEEP_WAIT / phase1=setup_watch_learning
  - 20260522_180500: 2026-05-23 03:05 / watch/confidence_below_min / prelabel=SWEEP_WAIT / phase1=blocked

## Phase1 観測
- pass: 163件 / blocked: 722件
- pass 内訳: setup_watch_learning=157件, confidence_watch_learning=5件, direction_rr_learning=1件
- 主な blocked 理由: confidence_below_min=507件, no_trade_candidate=254件, no_directional_setup=98件, watch_conditions_not_met=48件, setup_not_observable=3件
- setup_watch_learning: 157件 / 平均 execution=31.0 / 平均 wait=40.8
- setup_watch の主な reason: entry_zone_not_reached=101件, near_entry_zone_waiting_trigger=42件, inside_entry_zone_with_trigger=14件
- setup_watch の主な risk_flags: sweep_incomplete=113件, lower_liquidity_close=85件, orderbook_ask_heavy=38件, upper_liquidity_close=33件, support_to_resistance_flip=32件
- direction_rr_learning: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## blocked 上位理由の内訳
- confidence_below_min: 507件
  - prelabel: SWEEP_WAIT=247件, NO_TRADE_CANDIDATE=188件, RISKY_ENTRY=72件
  - setup status: invalid=260件, watch=247件
  - setup reason: confidence_below_min=507件
  - risk_flags: sweep_incomplete=428件, lower_liquidity_close=278件, upper_liquidity_close=192件, short_into_major_support=180件
  - 代表例: 20260524_180500, 20260524_160500, 20260524_150500
- no_trade_candidate: 254件
  - prelabel: NO_TRADE_CANDIDATE=254件
  - setup status: invalid=254件
  - setup reason: confidence_below_min=188件, near_entry_zone_waiting_trigger=33件, entry_zone_not_reached=28件, inside_entry_zone_with_trigger=4件
  - risk_flags: sweep_incomplete=242件, lower_liquidity_close=171件, ask_wall_close=141件, orderbook_ask_heavy=98件
  - 代表例: 20260524_180500, 20260524_140501, 20260524_130500

## sweep+lower_liquidity の補助flag内訳
- confidence_below_min: 239件 / 平均 execution=13.3 / 平均 wait=88.8
  - 補助flag: orderbook_ask_heavy=109件, ask_wall_close=103件, long_flush_exhaustion=77件, 補助flagなし=51件
- no_trade_candidate: 162件 / 平均 execution=11.0 / 平均 wait=82.7
  - 補助flag: ask_wall_close=132件, orderbook_ask_heavy=90件, long_flush_exhaustion=66件, 補助flagなし=2件

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
