# Phase 1B 昇格候補レポート

- 対象 shadow 行数: 669 / 全体 1489
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-16
- 条件: watch + confidence_below_min + SWEEP_WAIT/RISKY_ENTRY + sweep_incomplete + lower_liquidity_close + 補助 hard flag なし
- 昇格観測条件: direction>=55 / execution>=18 / wait<=85
- 候補件数: 6件
- prelabel: SWEEP_WAIT=6件
- risk_flags: lower_liquidity_close=6件, sweep_incomplete=6件, cvd_bearish_divergence=3件, short_cover_risk=3件
- 勝率=50.0% / TP1先行=100.0% / 近似PF=1.26
- 平均 direction=59.8 / 平均 execution=23.0 / 平均 wait=75.2
- 平均MFE=6.95 / 平均MAE=5.50

## 候補一覧
- 20260509_212745: 2026-05-10 06:27 / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
- 20260507_190500: 2026-05-08 04:05 / prelabel=SWEEP_WAIT / direction=68.0 / execution=25.0 / wait=56.0
- 20260503_120500: 2026-05-03 21:05 / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=84.8
- 20260502_210500: 2026-05-03 06:05 / prelabel=SWEEP_WAIT / direction=55.0 / execution=25.0 / wait=80.0
- 20260424_130500: 2026-04-24 22:05 / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
- 20260420_130500: 2026-04-20 22:05 / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
