# soft risk collateral damage

## 概要

- closed 全体件数: `505件`
- joined closed 件数: `505件`
- missing_shadow_join: `0件`
- B/C soft risk 対象件数: `22件`
- A hard 含み件数: `104件`

## group table

| group | count | entered_count | entered_sl_hit | entered_sl_hit_rate | entered_tp2_hit | entered_tp2_hit_rate | entered_timeout | entered_avg_R | non_entered_count | missed_opportunity | entry_not_reached | non_entered_avg_R | collateral_damage_score | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B only | 15 | 2 | 1 | 50.0% | 1 | 50.0% | 0 | 0.70 | 13 | 9 | 4 | 4.47 | 11.50 | monitor_only |
| C only | 6 | 2 | 2 | 100.0% | 0 | 0.0% | 0 | -1.00 | 4 | 4 | 0 | 1.30 | 3.00 | monitor_only |
| B+C | 1 | 1 | 0 | 0.0% | 1 | 100.0% | 0 | 2.40 | 0 | 0 | 0 | 0.00 | 2.00 | monitor_only |
| A+B | 56 | 9 | 7 | 77.8% | 1 | 11.1% | 1 | -0.50 | 47 | 4 | 43 | 17.05 | 13.25 | monitor_only |
| A+C | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.00 | 0 | 0 | 0 | 0.00 | 0.00 | monitor_only |
| A+B+C | 3 | 3 | 3 | 100.0% | 0 | 0.0% | 0 | -0.67 | 0 | 0 | 0 | 0.00 | -1.50 | monitor_only |
| B/C soft risk 全体 | 22 | 5 | 3 | 60.0% | 2 | 40.0% | 0 | 0.36 | 17 | 13 | 4 | 3.73 | 16.50 | monitor_only |
| A hard 含み全体 | 104 | 55 | 50 | 90.9% | 4 | 7.3% | 1 | -0.70 | 49 | 6 | 43 | 16.40 | -0.25 | harden_candidate |
| guard非該当全体 | 379 | 204 | 163 | 79.9% | 21 | 10.3% | 20 | -0.38 | 175 | 106 | 69 | 7.28 | 83.75 | keep_soft |
| closed全体 | 505 | 264 | 216 | 81.8% | 27 | 10.2% | 21 | -0.43 | 241 | 125 | 116 | 8.88 | 100.00 | keep_soft |

## representative examples

### B only
- 20260523_140500: tp2_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=91.0 / execution=30.0 / wait=64.0 / realized_r=2.40
- 20260521_010500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=59.0 / execution=32.0 / wait=60.8 / realized_r=1.30
- 20260502_210500: sl_hit / side=long / setup=confidence_below_min / flags=["phase1b_lite_gate_pass", "soft_risk:suppress_long_high_wait"] / direction=55.0 / execution=25.0 / wait=80.0 / realized_r=-1.00
- 20260501_160500: entry_not_reached / side=long / setup=entry_zone_not_reached / flags=["phase1_observation_gate_pass", "soft_risk:suppress_long_high_wait"] / direction=83.0 / execution=25.0 / wait=64.0 / realized_r=0.20
- 20260429_120500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=["phase1_observation_gate_pass", "soft_risk:suppress_long_high_wait"] / direction=76.0 / execution=29.0 / wait=65.6 / realized_r=1.30

### C only
- 20260523_210500: sl_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=83.0 / execution=34.0 / wait=49.6 / realized_r=-1.00
- 20260520_070500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=long_into_major_resistance,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=63.0 / execution=39.0 / wait=33.6 / realized_r=1.30
- 20260514_180500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=83.0 / execution=34.0 / wait=49.6 / realized_r=1.30
- 20260514_170500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=long_into_major_resistance,resistance_to_support_flip,resistance_to_support_retest_confirmed,major_support_rejection,trend_flip_confirmed_up / direction=90.0 / execution=42.0 / wait=28.8 / realized_r=1.30
- 20260514_160500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=long_into_major_resistance,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=86.0 / execution=35.0 / wait=48.0 / realized_r=1.30

### B+C
- 20260526_130500: tp2_hit / side=long / setup=confidence_below_min / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=59.0 / execution=27.0 / wait=60.8 / realized_r=2.40

### A+B
- 20260522_030500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=61.0 / execution=15.0 / wait=80.0 / realized_r=-1.00
- 20260517_190500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / direction=56.0 / execution=21.0 / wait=62.4 / realized_r=-1.00
- 20260515_100500: sl_hit / side=long / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_confirmed_down / direction=53.0 / execution=19.0 / wait=81.6 / realized_r=-1.00
- 20260515_030500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_up / direction=71.0 / execution=12.0 / wait=84.8 / realized_r=-1.00
- 20260514_230500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / direction=51.0 / execution=19.0 / wait=73.6 / realized_r=-1.00

### A+C
- 該当なし

### A+B+C
- 20260517_180500: sl_hit / side=long / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=74.0 / execution=22.0 / wait=76.8 / realized_r=0.00
- 20260515_190500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,major_resistance_rejection,major_support_rejection,trend_flip_confirmed_up / direction=55.0 / execution=22.0 / wait=68.8 / realized_r=-1.00
- 20260515_010500: sl_hit / side=long / setup=entry_zone_not_reached / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=85.0 / execution=22.0 / wait=76.8 / realized_r=-1.00

### B/C soft risk 全体
- 20260526_130500: tp2_hit / side=long / setup=confidence_below_min / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=59.0 / execution=27.0 / wait=60.8 / realized_r=2.40
- 20260523_210500: sl_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=83.0 / execution=34.0 / wait=49.6 / realized_r=-1.00
- 20260523_140500: tp2_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=91.0 / execution=30.0 / wait=64.0 / realized_r=2.40
- 20260521_010500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / direction=59.0 / execution=32.0 / wait=60.8 / realized_r=1.30
- 20260520_070500: missed_opportunity / side=long / setup=entry_zone_not_reached / flags=long_into_major_resistance,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / direction=63.0 / execution=39.0 / wait=33.6 / realized_r=1.30

### A hard 含み全体
- 20260525_070500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / direction=84.0 / execution=18.0 / wait=75.2 / realized_r=-1.00
- 20260525_040500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=90.0 / execution=21.0 / wait=62.4 / realized_r=-1.00
- 20260525_030500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=90.0 / execution=18.0 / wait=67.2 / realized_r=-1.00
- 20260524_230500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / direction=77.0 / execution=18.0 / wait=75.2 / realized_r=-1.00
- 20260524_060500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / direction=56.0 / execution=18.0 / wait=67.2 / realized_r=-1.00

### guard非該当全体
- 20260601_000500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_down / direction=76.0 / execution=18.0 / wait=59.2 / realized_r=-1.00
- 20260531_220501: sl_hit / side=short / setup=inside_entry_zone_with_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / direction=100.0 / execution=18.0 / wait=51.2 / realized_r=-1.00
- 20260531_210501: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / direction=100.0 / execution=31.0 / wait=46.4 / realized_r=-1.00
- 20260531_200500: sl_hit / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=100.0 / execution=25.0 / wait=48.0 / realized_r=-1.00
- 20260531_180500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_up / direction=76.0 / execution=31.0 / wait=54.4 / realized_r=-1.00

### closed全体
- 20260601_000500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_down / direction=76.0 / execution=18.0 / wait=59.2 / realized_r=-1.00
- 20260531_220501: sl_hit / side=short / setup=inside_entry_zone_with_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / direction=100.0 / execution=18.0 / wait=51.2 / realized_r=-1.00
- 20260531_210501: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / direction=100.0 / execution=31.0 / wait=46.4 / realized_r=-1.00
- 20260531_200500: sl_hit / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / direction=100.0 / execution=25.0 / wait=48.0 / realized_r=-1.00
- 20260531_180500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_up / direction=76.0 / execution=31.0 / wait=54.4 / realized_r=-1.00

## interpretation
- B/C 単独 soft risk は現時点では hard blocker 化しない。
- この report は guard 条件変更のための材料であり、即時変更ではない。
- missed_opportunity / entry_not_reached は約定後損益ではない。
- trend_flip_confirmed_up は強評価へ戻さない。
- trade_execution_gate / phase1b_lite_gate / opportunity_gate は変更しない。
