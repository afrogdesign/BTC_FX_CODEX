# 緩和候補レポート

- 対象 shadow 行数: 265 / 全体 1085
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-04-29
- 条件: blocked + confidence_below_min + sweep_incomplete + lower_liquidity_close + 補助 hard flag なし
- 候補件数: 23件
- prelabel: SWEEP_WAIT=16件, RISKY_ENTRY=6件, NO_TRADE_CANDIDATE=1件
- setup reason: confidence_below_min=23件
- phase1 reasons: confidence_below_min=23件, no_trade_candidate=1件
- risk_flags: lower_liquidity_close=23件, sweep_incomplete=23件, short_cover_risk=10件, cvd_bearish_divergence=3件, cvd_bullish_divergence=2件
- 平均 execution=18.5 / 平均 wait=84.8

## 候補一覧
- 20260427_170500: 2026-04-28 02:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=30.0 / wait=64.0
- 20260427_110500: 2026-04-27 20:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=81.6
- 20260427_100500: 2026-04-27 19:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=17.0 / wait=84.8
- 20260426_210500: 2026-04-27 06:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=15.0 / wait=88.0
- 20260426_180501: 2026-04-27 03:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=17.0 / wait=92.8
- 20260426_090500: 2026-04-26 18:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=24.0 / wait=73.6
- 20260426_030500: 2026-04-26 12:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=89.6
- 20260425_040501: 2026-04-25 13:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=100.0
- 20260425_000505: 2026-04-25 09:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=17.0 / wait=92.8
- 20260424_202207: 2026-04-25 05:22 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=19.0 / wait=89.6
- 20260424_130500: 2026-04-24 22:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=22.0 / wait=76.8
- 20260421_140500: 2026-04-21 23:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260421_060500: 2026-04-21 15:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=19.0 / wait=81.6
- 20260421_020500: 2026-04-21 11:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=65.6
- 20260420_180500: 2026-04-21 03:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260420_140500: 2026-04-20 23:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=22.0 / wait=76.8
- 20260420_130500: 2026-04-20 22:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=22.0 / wait=76.8
- 20260420_020500: 2026-04-20 11:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=92.8
- 20260419_220500: 2026-04-20 07:05 / prelabel=RISKY_ENTRY / setup=confidence_below_min / execution=29.0 / wait=73.6
- 20260419_200500: 2026-04-20 05:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=12.0 / wait=100.0
