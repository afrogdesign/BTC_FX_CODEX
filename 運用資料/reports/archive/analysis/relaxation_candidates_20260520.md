# 緩和候補レポート

- 対象 shadow 行数: 765 / 全体 1585
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-20
- 条件: blocked + confidence_below_min + sweep_incomplete + lower_liquidity_close + 補助 hard flag なし
- 候補件数: 49件
- prelabel: SWEEP_WAIT=32件, RISKY_ENTRY=16件, NO_TRADE_CANDIDATE=1件
- setup reason: confidence_below_min=49件
- phase1 reasons: confidence_below_min=49件, no_trade_candidate=1件
- risk_flags: lower_liquidity_close=49件, sweep_incomplete=49件, short_cover_risk=20件, cvd_bearish_divergence=8件, long_into_major_resistance=6件
- 平均 execution=18.6 / 平均 wait=83.9

## 候補一覧
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
- 20260503_170500: 2026-05-04 02:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=17.0 / wait=84.8
- 20260503_140500: 2026-05-03 23:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=20.0 / wait=80.0
