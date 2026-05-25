# 紙実行候補 entry/wait 診断

- 対象 paper_positions: 264件
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-26
- closed: 264件 / opportunity_type: setup_watch_learning=161件, market_map_opportunity=97件, confidence_watch_sweep_lite=5件, formal_execution_candidate=1件
- closed 全体: 勝率=7.6% / 平均R=0.33 / 簡易PF=1.82 / 終了=sl_hit=121件, missed_opportunity=98件, tp2_hit=20件, timeout=14件, entry_not_reached=11件
- market_map_opportunity: 97件 / 勝率=10.3% / 平均R=0.36 / 簡易PF=1.97 / 終了=sl_hit=48件, missed_opportunity=34件, tp2_hit=10件, timeout=5件
- その他 opportunity: 167件 / 勝率=6.0% / 平均R=0.31 / 簡易PF=1.75

## 判断
- 主な失敗は missed より SL 側に寄っており、入口を広げるより entry 発火または SL/TP 条件の精査を優先する。
- `support_to_resistance_flip` などの flag 自体は有効でも、紙ポジション化する entry / wait 条件がまだ粗い。

## confidence 帯別
- direction<60: 27件 / 勝率=3.7% / 平均R=0.11 / 簡易PF=1.21 / 終了=sl_hit=14件, missed_opportunity=11件, tp2_hit=1件, timeout=1件
- direction>=60: 70件 / 勝率=12.9% / 平均R=0.46 / 簡易PF=2.46 / 終了=sl_hit=34件, missed_opportunity=23件, tp2_hit=9件, timeout=4件
- execution<24: 66件 / 勝率=9.1% / 平均R=0.10 / 簡易PF=1.22 / 終了=sl_hit=40件, missed_opportunity=15件, tp2_hit=6件, timeout=5件
- execution>=24: 31件 / 勝率=12.9% / 平均R=0.91 / 簡易PF=5.72 / 終了=missed_opportunity=19件, sl_hit=8件, tp2_hit=4件
- wait>=60: 39件 / 勝率=12.8% / 平均R=-0.16 / 簡易PF=0.74 / 終了=sl_hit=28件, tp2_hit=5件, missed_opportunity=5件, timeout=1件
- wait<60: 58件 / 勝率=8.6% / 平均R=0.71 / 簡易PF=4.75 / 終了=missed_opportunity=29件, sl_hit=20件, tp2_hit=5件, timeout=4件

## setup reason 別
- confidence_below_min: 78件 / 勝率=9.0% / 平均R=0.35 / 簡易PF=1.91 / 終了=sl_hit=38件, missed_opportunity=30件, tp2_hit=7件, timeout=3件
- entry_zone_not_reached: 5件 / 勝率=0.0% / 平均R=0.33 / 簡易PF=1.81 / 終了=missed_opportunity=2件, sl_hit=2件, timeout=1件
- inside_entry_zone_with_trigger: 5件 / 勝率=20.0% / 平均R=0.18 / 簡易PF=1.45 / 終了=sl_hit=3件, tp2_hit=1件, timeout=1件
- near_entry_zone_waiting_trigger: 9件 / 勝率=22.2% / 平均R=0.60 / 簡易PF=3.70 / 終了=sl_hit=5件, missed_opportunity=2件, tp2_hit=2件

## side 別
- long: 18件 / 勝率=5.6% / 平均R=-0.51 / 簡易PF=0.29 / 終了=sl_hit=15件, tp2_hit=1件, timeout=1件, missed_opportunity=1件
- short: 79件 / 勝率=11.4% / 平均R=0.56 / 簡易PF=2.92 / 終了=sl_hit=33件, missed_opportunity=33件, tp2_hit=9件, timeout=4件

## market_map flag 別
- short_into_major_support: 86件 / 勝率=9.3% / 平均R=0.27 / 簡易PF=1.68 / 終了=sl_hit=46件, missed_opportunity=27件, tp2_hit=8件, timeout=5件
- support_to_resistance_flip: 69件 / 勝率=11.6% / 平均R=0.62 / 簡易PF=3.27 / 終了=missed_opportunity=31件, sl_hit=26件, tp2_hit=8件, timeout=4件
- support_to_resistance_retest_confirmed: 69件 / 勝率=11.6% / 平均R=0.62 / 簡易PF=3.27 / 終了=missed_opportunity=31件, sl_hit=26件, tp2_hit=8件, timeout=4件
- long_into_major_resistance: 67件 / 勝率=10.4% / 平均R=0.10 / 簡易PF=1.23 / 終了=sl_hit=42件, missed_opportunity=14件, tp2_hit=7件, timeout=4件
- trend_flip_confirmed_down: 48件 / 勝率=12.5% / 平均R=0.60 / 簡易PF=3.05 / 終了=missed_opportunity=20件, sl_hit=19件, tp2_hit=6件, timeout=3件
- major_resistance_rejection: 39件 / 勝率=12.8% / 平均R=0.07 / 簡易PF=1.15 / 終了=sl_hit=25件, missed_opportunity=7件, tp2_hit=5件, timeout=2件
- trend_flip_early_down: 34件 / 勝率=8.8% / 平均R=0.27 / 簡易PF=1.65 / 終了=sl_hit=18件, missed_opportunity=12件, tp2_hit=3件, timeout=1件
- failed_breakout_down_reversal: 27件 / 勝率=14.8% / 平均R=0.01 / 簡易PF=1.02 / 終了=sl_hit=18件, tp2_hit=4件, missed_opportunity=3件, timeout=2件
- major_support_rejection: 26件 / 勝率=3.8% / 平均R=0.47 / 簡易PF=2.56 / 終了=missed_opportunity=13件, sl_hit=10件, timeout=2件, tp2_hit=1件
- resistance_to_support_flip: 24件 / 勝率=8.3% / 平均R=-0.21 / 簡易PF=0.63 / 終了=sl_hit=18件, missed_opportunity=3件, tp2_hit=2件, timeout=1件
- resistance_to_support_retest_confirmed: 24件 / 勝率=8.3% / 平均R=-0.21 / 簡易PF=0.63 / 終了=sl_hit=18件, missed_opportunity=3件, tp2_hit=2件, timeout=1件
- failed_breakout_up_reversal: 13件 / 勝率=7.7% / 平均R=0.54 / 簡易PF=2.76 / 終了=missed_opportunity=6件, sl_hit=5件, tp2_hit=1件, timeout=1件
- trend_flip_early_up: 8件 / 勝率=12.5% / 平均R=0.27 / 簡易PF=1.75 / 終了=sl_hit=4件, missed_opportunity=2件, tp2_hit=1件, timeout=1件
- trend_flip_confirmed_up: 7件 / 勝率=0.0% / 平均R=-0.71 / 簡易PF=0.00 / 終了=sl_hit=7件

## opportunity reason 別
- market_map:support_to_resistance_flip: 69件 / 勝率=11.6% / 平均R=0.62 / 簡易PF=3.27 / 終了=missed_opportunity=31件, sl_hit=26件, tp2_hit=8件, timeout=4件
- market_map:failed_breakout_down_reversal: 27件 / 勝率=14.8% / 平均R=0.01 / 簡易PF=1.02 / 終了=sl_hit=18件, tp2_hit=4件, missed_opportunity=3件, timeout=2件
- market_map:resistance_to_support_flip: 24件 / 勝率=8.3% / 平均R=-0.21 / 簡易PF=0.63 / 終了=sl_hit=18件, missed_opportunity=3件, tp2_hit=2件, timeout=1件

## 弱い代表例
- 20260525_070500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=84.0 / exec=18.0 / wait=75.2 / R=-1.00
- 20260525_030500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=90.0 / exec=18.0 / wait=67.2 / R=-1.00
- 20260524_230500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / dir=77.0 / exec=18.0 / wait=75.2 / R=-1.00
- 20260524_150500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_support_rejection,trend_flip_confirmed_down / dir=50.0 / exec=28.0 / wait=59.2 / R=1.30
- 20260524_060500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=56.0 / exec=18.0 / wait=67.2 / R=-1.00
- 20260524_040500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_early_down / dir=55.0 / exec=18.0 / wait=67.2 / R=-1.00
- 20260523_230500: sl_hit / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_support_rejection,trend_flip_early_down / dir=52.0 / exec=28.0 / wait=59.2 / R=-1.00
- 20260523_210500: sl_hit / side=long / setup=inside_entry_zone_with_trigger / flags=short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_confirmed_up / dir=83.0 / exec=34.0 / wait=49.6 / R=-1.00
- 20260523_160500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_down / dir=54.0 / exec=23.0 / wait=59.2 / R=-1.00
- 20260523_060500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=76.0 / exec=23.0 / wait=59.2 / R=1.30
- 20260523_030500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=69.0 / exec=28.0 / wait=51.2 / R=1.30
- 20260522_230500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=69.0 / exec=28.0 / wait=51.2 / R=1.30
- 20260522_200500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_confirmed_down / dir=54.0 / exec=38.0 / wait=51.2 / R=1.30
- 20260522_190500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_confirmed_down / dir=76.0 / exec=28.0 / wait=51.2 / R=1.30
- 20260522_180500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=77.0 / exec=23.0 / wait=59.2 / R=1.30
- 20260522_030500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / dir=61.0 / exec=15.0 / wait=80.0 / R=-1.00
- 20260521_140500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=64.0 / exec=23.0 / wait=59.2 / R=1.30
- 20260521_120500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=59.0 / exec=28.0 / wait=59.2 / R=0.00
- 20260521_020500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_early_down / dir=60.0 / exec=18.0 / wait=67.2 / R=-1.00
- 20260520_210500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_early_down / dir=52.0 / exec=20.0 / wait=64.0 / R=-1.00

## 次に触る候補
- src/trade/opportunity_gate.py
- src/trade/paper_position.py
- src/analysis/market_map.py
- tools/log_feedback.py
