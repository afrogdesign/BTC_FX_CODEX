# soft risk collateral damage

## 概要

- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-06-07
- closed 全体件数: `376件`
- joined closed 件数: `376件`
- missing_shadow_join: `0件`
- B/C soft risk 対象件数: `14件`
- A hard 含み件数: `43件`

## group table

| group | count | entered_count | entered_sl_hit | entered_sl_hit_rate | entered_tp2_hit | entered_tp2_hit_rate | entered_timeout | entered_avg_R | non_entered_count | missed_opportunity | entry_not_reached | non_entered_avg_R | collateral_damage_score | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B only | 12 | 2 | 1 | 50.0% | 1 | 50.0% | 0 | 0.70 | 10 | 9 | 1 | 1.19 | 10.75 | monitor_only |
| C only | 2 | 1 | 1 | 100.0% | 0 | 0.0% | 0 | -1.00 | 1 | 1 | 0 | 1.30 | 0.50 | monitor_only |
| B+C | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.00 | 0 | 0 | 0 | 0.00 | 0.00 | monitor_only |
| A+B | 14 | 11 | 8 | 72.7% | 1 | 9.1% | 2 | -0.58 | 3 | 3 | 0 | 1.30 | 1.00 | keep_soft |
| A+C | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.00 | 0 | 0 | 0 | 0.00 | 0.00 | monitor_only |
| A+B+C | 5 | 5 | 5 | 100.0% | 0 | 0.0% | 0 | -0.60 | 0 | 0 | 0 | 0.00 | -2.50 | monitor_only |
| B/C soft risk 全体 | 14 | 3 | 2 | 66.7% | 1 | 33.3% | 0 | 0.13 | 11 | 10 | 1 | 1.20 | 11.25 | monitor_only |
| A hard 含み全体 | 43 | 36 | 29 | 80.6% | 5 | 13.9% | 2 | -0.38 | 7 | 7 | 0 | 1.30 | 2.50 | keep_soft |
| guard非該当全体 | 319 | 160 | 114 | 71.2% | 26 | 16.2% | 20 | -0.10 | 159 | 149 | 10 | 1.25 | 146.50 | avoid_hardening |
| closed全体 | 376 | 199 | 145 | 72.9% | 32 | 16.1% | 22 | -0.14 | 177 | 166 | 11 | 1.25 | 160.25 | avoid_hardening |

## representative examples

### B only
- 20260523_140500: tp2_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=91.0 / execution=30.0 / wait=64.0 / realized_r=2.40
- 20260521_010500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=59.0 / execution=32.0 / wait=60.8 / realized_r=1.30
- 20260502_210500: sl_hit / side=long / setup=confidence_below_min / flags=["phase1b_lite_gate_pass", "soft_risk:suppress_long_high_wait"] / direction=55.0 / execution=25.0 / wait=80.0 / realized_r=-1.00
- 20260501_160500: entry_not_reached / side=long / setup=entry_zone_not_reached / flags=["phase1_observation_gate_pass", "soft_risk:suppress_long_high_wait"] / direction=83.0 / execution=25.0 / wait=64.0 / realized_r=0.20
- 20260429_120500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=["phase1_observation_gate_pass", "soft_risk:suppress_long_high_wait"] / direction=76.0 / execution=29.0 / wait=65.6 / realized_r=1.30

### C only
- 20260523_210500: sl_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=83.0 / execution=34.0 / wait=49.6 / realized_r=-1.00
- 20260514_180500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=83.0 / execution=34.0 / wait=49.6 / realized_r=1.30

### B+C
- 該当なし

### A+B
- 20260522_030500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=61.0 / execution=15.0 / wait=80.0 / realized_r=-1.00
- 20260517_190500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / direction=56.0 / execution=21.0 / wait=62.4 / realized_r=-1.00
- 20260515_170500: timeout / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,major_support_rejection,trend_flip_early_up / direction=55.0 / execution=12.0 / wait=84.8 / realized_r=-0.85
- 20260515_100500: sl_hit / side=long / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_confirmed_down / direction=53.0 / execution=19.0 / wait=81.6 / realized_r=-1.00
- 20260515_030500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_up / direction=71.0 / execution=12.0 / wait=84.8 / realized_r=-1.00

### A+C
- 該当なし

### A+B+C
- 20260517_180500: sl_hit / side=long / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=74.0 / execution=22.0 / wait=76.8 / realized_r=0.00
- 20260515_190500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,major_resistance_rejection,major_support_rejection,trend_flip_confirmed_up / direction=55.0 / execution=22.0 / wait=68.8 / realized_r=-1.00
- 20260515_010500: sl_hit / side=long / setup=entry_zone_not_reached / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=85.0 / execution=22.0 / wait=76.8 / realized_r=-1.00
- 20260514_190500: sl_hit / side=long / setup=entry_zone_not_reached / flags=resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=75.0 / execution=20.0 / wait=72.0 / realized_r=-1.00
- 20260514_150500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=68.0 / execution=16.0 / wait=86.4 / realized_r=0.00

### B/C soft risk 全体
- 20260523_210500: sl_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=83.0 / execution=34.0 / wait=49.6 / realized_r=-1.00
- 20260523_140500: tp2_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=91.0 / execution=30.0 / wait=64.0 / realized_r=2.40
- 20260521_010500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=59.0 / execution=32.0 / wait=60.8 / realized_r=1.30
- 20260514_180500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=83.0 / execution=34.0 / wait=49.6 / realized_r=1.30
- 20260502_210500: sl_hit / side=long / setup=confidence_below_min / flags=["phase1b_lite_gate_pass", "soft_risk:suppress_long_high_wait"] / direction=55.0 / execution=25.0 / wait=80.0 / realized_r=-1.00

### A hard 含み全体
- 20260525_070500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / direction=84.0 / execution=18.0 / wait=75.2 / realized_r=-1.00
- 20260525_040500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=90.0 / execution=21.0 / wait=62.4 / realized_r=-1.00
- 20260525_030500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=90.0 / execution=18.0 / wait=67.2 / realized_r=-1.00
- 20260524_230500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / direction=77.0 / execution=18.0 / wait=75.2 / realized_r=-1.00
- 20260524_060500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / direction=56.0 / execution=18.0 / wait=67.2 / realized_r=-1.00

### guard非該当全体
- 20260606_130500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=long_into_major_resistance,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / direction=100.0 / execution=30.0 / wait=32.0 / realized_r=1.30
- 20260606_010500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_confirmed_down / direction=100.0 / execution=23.0 / wait=43.2 / realized_r=1.30
- 20260605_190501: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=100.0 / execution=45.0 / wait=16.0 / realized_r=1.30
- 20260605_160500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_support_rejection,trend_flip_confirmed_down / direction=100.0 / execution=28.0 / wait=43.2 / realized_r=1.30
- 20260605_150500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=100.0 / execution=25.0 / wait=56.0 / realized_r=1.30

### closed全体
- 20260606_130500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=long_into_major_resistance,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / direction=100.0 / execution=30.0 / wait=32.0 / realized_r=1.30
- 20260606_010500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_confirmed_down / direction=100.0 / execution=23.0 / wait=43.2 / realized_r=1.30
- 20260605_190501: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=100.0 / execution=45.0 / wait=16.0 / realized_r=1.30
- 20260605_160500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_support_rejection,trend_flip_confirmed_down / direction=100.0 / execution=28.0 / wait=43.2 / realized_r=1.30
- 20260605_150500: missed_opportunity / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=100.0 / execution=25.0 / wait=56.0 / realized_r=1.30

## interpretation
- B/C 単独 soft risk は現時点では hard blocker 化しない。
- この report は guard 条件変更のための材料であり、即時変更ではない。
- missed_opportunity / entry_not_reached は約定後損益ではない。
- trend_flip_confirmed_up は強評価へ戻さない。
- trade_execution_gate / phase1b_lite_gate / opportunity_gate は変更しない。
