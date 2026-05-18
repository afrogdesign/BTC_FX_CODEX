# 緩和候補レポート

- 対象 shadow 行数: 171 / 全体 991
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-04-25
- 条件: blocked + confidence_below_min + sweep_incomplete + lower_liquidity_close + 補助 hard flag なし
- 候補件数: 13件
- prelabel: SWEEP_WAIT=9件, RISKY_ENTRY=3件, NO_TRADE_CANDIDATE=1件
- setup reason: confidence_below_min=13件
- phase1 reasons: confidence_below_min=13件, no_trade_candidate=1件
- risk_flags: lower_liquidity_close=13件, sweep_incomplete=13件, short_cover_risk=6件, cvd_bullish_divergence=2件, cvd_bearish_divergence=1件
- 平均 execution=18.2 / 平均 wait=84.1

## 候補一覧
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
- 20260419_170500: 2026-04-20 02:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=15.0 / wait=88.0
- 20260418_200500: 2026-04-19 05:05 / prelabel=SWEEP_WAIT / setup=confidence_below_min / execution=22.0 / wait=76.8
- 20260417_200500: 2026-04-18 05:05 / prelabel=NO_TRADE_CANDIDATE / setup=confidence_below_min / execution=8.0 / wait=99.2
