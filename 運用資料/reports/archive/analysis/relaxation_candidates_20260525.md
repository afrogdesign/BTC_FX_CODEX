# 緩和候補レポート

- 対象 shadow 行数: 885 / 全体 1705
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-25
- 条件: blocked + confidence_below_min + sweep_incomplete + lower_liquidity_close + 補助 hard flag なし
- 候補件数: 51件
- prelabel: SWEEP_WAIT=33件, RISKY_ENTRY=16件, NO_TRADE_CANDIDATE=2件
- setup reason: confidence_below_min=51件
- phase1 reasons: confidence_below_min=51件, no_trade_candidate=2件
- risk_flags: lower_liquidity_close=51件, sweep_incomplete=51件, short_cover_risk=21件, cvd_bearish_divergence=9件, long_into_major_resistance=8件
- 平均 execution=18.2 / 平均 wait=84.2

## 候補一覧
- 20260522_030500: 2026-05-22 12:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=15.0 / wait=80.0
- 20260520_050500: 2026-05-20 14:05 / prelabel=NO_TRADE_CANDIDATE / setup=confidence_below_min / execution=5.0 / wait=100.0
- 20260517_220500: 2026-05-18 07:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_080500: 2026-05-15 17:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260515_030500: 2026-05-15 12:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=84.8
- 20260514_210500: 2026-05-15 06:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=19.0 / wait=73.6
- 20260513_050501: 2026-05-13 14:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=73.6
- 20260513_040501: 2026-05-13 13:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=73.6
- 20260512_150500: 2026-05-13 00:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=24.0 / wait=73.6
- 20260511_070500: 2026-05-11 16:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=89.6
- 20260510_230500: 2026-05-11 08:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=32.0 / wait=76.8
- 20260510_100500: 2026-05-10 19:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=81.6
- 20260510_020500: 2026-05-10 11:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260510_010500: 2026-05-10 10:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260509_200500: 2026-05-10 05:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=14.0 / wait=89.6
- 20260509_191901: 2026-05-10 04:19 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=14.0 / wait=89.6
- 20260509_050500: 2026-05-09 14:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=81.6
- 20260509_040500: 2026-05-09 13:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260508_160500: 2026-05-09 01:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260504_030500: 2026-05-04 12:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=42.0 / wait=52.8
