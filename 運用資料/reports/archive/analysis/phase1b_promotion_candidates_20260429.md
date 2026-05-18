# Phase 1B 昇格候補レポート

- 対象 shadow 行数: 265 / 全体 1085
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-04-29
- 条件: watch + confidence_below_min + SWEEP_WAIT/RISKY_ENTRY + sweep_incomplete + lower_liquidity_close + 補助 hard flag なし
- 昇格観測条件: direction>=55 / execution>=18 / wait<=85
- 候補件数: 2件
- prelabel: SWEEP_WAIT=2件
- risk_flags: lower_liquidity_close=2件, sweep_incomplete=2件, cvd_bearish_divergence=1件, short_cover_risk=1件
- 勝率=0.0% / TP1先行=0.0% / 近似PF=0.12
- 平均 direction=59.0 / 平均 execution=22.0 / 平均 wait=76.8
- 平均MFE=0.67 / 平均MAE=5.38

## 候補一覧
- 20260424_130500: 2026-04-24 22:05 / prelabel=SWEEP_WAIT / direction=58.0 / execution=22.0 / wait=76.8
- 20260420_130500: 2026-04-20 22:05 / prelabel=SWEEP_WAIT / direction=60.0 / execution=22.0 / wait=76.8
