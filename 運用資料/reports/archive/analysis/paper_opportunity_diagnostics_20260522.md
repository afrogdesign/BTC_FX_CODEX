# 紙実行候補 entry/wait 診断

- 対象 paper_positions: 112件
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-22
- closed: 112件 / opportunity_type: market_map_opportunity=80件, setup_watch_learning=32件
- closed 全体: 勝率=8.0% / 平均R=0.31 / 簡易PF=1.82 / 終了=sl_hit=56件, missed_opportunity=40件, tp2_hit=9件, timeout=7件
- market_map_opportunity: 80件 / 勝率=10.0% / 平均R=0.36 / 簡易PF=2.04 / 終了=sl_hit=40件, missed_opportunity=27件, tp2_hit=8件, timeout=5件
- その他 opportunity: 32件 / 勝率=3.1% / 平均R=0.16 / 簡易PF=1.37

## 判断
- 主な失敗は missed より SL 側に寄っており、入口を広げるより entry 発火または SL/TP 条件の精査を優先する。
- `support_to_resistance_flip` などの flag 自体は有効でも、紙ポジション化する entry / wait 条件がまだ粗い。

## confidence 帯別
- direction<60: 21件 / 勝率=4.8% / 平均R=0.20 / 簡易PF=1.43 / 終了=sl_hit=10件, missed_opportunity=9件, tp2_hit=1件, timeout=1件
- direction>=60: 59件 / 勝率=11.9% / 平均R=0.42 / 簡易PF=2.38 / 終了=sl_hit=30件, missed_opportunity=18件, tp2_hit=7件, timeout=4件
- execution<24: 57件 / 勝率=8.8% / 平均R=0.13 / 簡易PF=1.32 / 終了=sl_hit=34件, missed_opportunity=13件, tp2_hit=5件, timeout=5件
- execution>=24: 23件 / 勝率=13.0% / 平均R=0.93 / 簡易PF=6.35 / 終了=missed_opportunity=14件, sl_hit=6件, tp2_hit=3件
- wait>=60: 32件 / 勝率=9.4% / 平均R=-0.19 / 簡易PF=0.69 / 終了=sl_hit=23件, missed_opportunity=5件, tp2_hit=3件, timeout=1件
- wait<60: 48件 / 勝率=10.4% / 平均R=0.73 / 簡易PF=5.40 / 終了=missed_opportunity=22件, sl_hit=17件, tp2_hit=5件, timeout=4件

## setup reason 別
- confidence_below_min: 64件 / 勝率=9.4% / 平均R=0.34 / 簡易PF=1.90 / 終了=sl_hit=32件, missed_opportunity=23件, tp2_hit=6件, timeout=3件
- entry_zone_not_reached: 5件 / 勝率=0.0% / 平均R=0.33 / 簡易PF=1.81 / 終了=missed_opportunity=2件, sl_hit=2件, timeout=1件
- inside_entry_zone_with_trigger: 3件 / 勝率=0.0% / 平均R=-0.17 / 簡易PF=0.49 / 終了=sl_hit=2件, timeout=1件
- near_entry_zone_waiting_trigger: 8件 / 勝率=25.0% / 平均R=0.80 / 簡易PF=7.40 / 終了=sl_hit=4件, missed_opportunity=2件, tp2_hit=2件

## side 別
- long: 16件 / 勝率=0.0% / 平均R=-0.66 / 簡易PF=0.11 / 終了=sl_hit=14件, timeout=1件, missed_opportunity=1件
- short: 64件 / 勝率=12.5% / 平均R=0.62 / 簡易PF=3.48 / 終了=missed_opportunity=26件, sl_hit=26件, tp2_hit=8件, timeout=4件

## market_map flag 別
- short_into_major_support: 70件 / 勝率=8.6% / 平均R=0.26 / 簡易PF=1.71 / 終了=sl_hit=38件, missed_opportunity=21件, tp2_hit=6件, timeout=5件
- long_into_major_resistance: 59件 / 勝率=10.2% / 平均R=0.15 / 簡易PF=1.38 / 終了=sl_hit=36件, missed_opportunity=13件, tp2_hit=6件, timeout=4件
- support_to_resistance_flip: 55件 / 勝率=12.7% / 平均R=0.68 / 簡易PF=3.89 / 終了=missed_opportunity=24件, sl_hit=20件, tp2_hit=7件, timeout=4件
- support_to_resistance_retest_confirmed: 55件 / 勝率=12.7% / 平均R=0.68 / 簡易PF=3.89 / 終了=missed_opportunity=24件, sl_hit=20件, tp2_hit=7件, timeout=4件
- trend_flip_confirmed_down: 38件 / 勝率=13.2% / 平均R=0.51 / 簡易PF=2.61 / 終了=sl_hit=17件, missed_opportunity=13件, tp2_hit=5件, timeout=3件
- major_resistance_rejection: 35件 / 勝率=14.3% / 平均R=0.20 / 簡易PF=1.46 / 終了=sl_hit=21件, missed_opportunity=7件, tp2_hit=5件, timeout=2件
- trend_flip_early_down: 29件 / 勝率=10.3% / 平均R=0.48 / 簡易PF=2.56 / 終了=sl_hit=13件, missed_opportunity=12件, tp2_hit=3件, timeout=1件
- failed_breakout_down_reversal: 25件 / 勝率=16.0% / 平均R=0.09 / 簡易PF=1.19 / 終了=sl_hit=16件, tp2_hit=4件, missed_opportunity=3件, timeout=2件
- resistance_to_support_flip: 22件 / 勝率=4.5% / 平均R=-0.30 / 簡易PF=0.49 / 終了=sl_hit=17件, missed_opportunity=3件, tp2_hit=1件, timeout=1件
- resistance_to_support_retest_confirmed: 22件 / 勝率=4.5% / 平均R=-0.30 / 簡易PF=0.49 / 終了=sl_hit=17件, missed_opportunity=3件, tp2_hit=1件, timeout=1件
- major_support_rejection: 20件 / 勝率=0.0% / 平均R=0.40 / 簡易PF=2.36 / 終了=missed_opportunity=10件, sl_hit=8件, timeout=2件
- failed_breakout_up_reversal: 9件 / 勝率=0.0% / 平均R=0.34 / 簡易PF=2.01 / 終了=missed_opportunity=4件, sl_hit=4件, timeout=1件
- trend_flip_early_up: 7件 / 勝率=0.0% / 平均R=-0.04 / 簡易PF=0.91 / 終了=sl_hit=4件, missed_opportunity=2件, timeout=1件
- trend_flip_confirmed_up: 6件 / 勝率=0.0% / 平均R=-0.67 / 簡易PF=0.00 / 終了=sl_hit=6件

## opportunity reason 別
- market_map:support_to_resistance_flip: 55件 / 勝率=12.7% / 平均R=0.68 / 簡易PF=3.89 / 終了=missed_opportunity=24件, sl_hit=20件, tp2_hit=7件, timeout=4件
- market_map:failed_breakout_down_reversal: 25件 / 勝率=16.0% / 平均R=0.09 / 簡易PF=1.19 / 終了=sl_hit=16件, tp2_hit=4件, missed_opportunity=3件, timeout=2件
- market_map:resistance_to_support_flip: 22件 / 勝率=4.5% / 平均R=-0.30 / 簡易PF=0.49 / 終了=sl_hit=17件, missed_opportunity=3件, tp2_hit=1件, timeout=1件

## 弱い代表例
- 20260522_030500: sl_hit / side=long / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / dir=61.0 / exec=15.0 / wait=80.0 / R=-1.00
- 20260521_140500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=64.0 / exec=23.0 / wait=59.2 / R=1.30
- 20260521_120500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=59.0 / exec=28.0 / wait=59.2 / R=0.00
- 20260521_020500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_early_down / dir=60.0 / exec=18.0 / wait=67.2 / R=-1.00
- 20260520_210500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_early_down / dir=52.0 / exec=20.0 / wait=64.0 / R=-1.00
- 20260520_110500: sl_hit / side=short / setup=confidence_below_min / flags=support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=71.0 / exec=23.0 / wait=59.2 / R=-1.00
- 20260520_000500: missed_opportunity / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=95.0 / exec=18.0 / wait=59.2 / R=1.30
- 20260519_230500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / dir=95.0 / exec=15.0 / wait=64.0 / R=-1.00
- 20260519_220500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / dir=52.0 / exec=23.0 / wait=51.2 / R=1.30
- 20260519_100500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_support_rejection,trend_flip_early_down / dir=76.0 / exec=18.0 / wait=59.2 / R=0.00
- 20260519_070500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=60.0 / exec=18.0 / wait=59.2 / R=-1.00
- 20260518_180500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=66.0 / exec=21.0 / wait=70.4 / R=-1.00
- 20260518_160500: missed_opportunity / side=short / setup=confidence_below_min / flags=support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=55.0 / exec=31.0 / wait=54.4 / R=1.30
- 20260518_150500: missed_opportunity / side=short / setup=confidence_below_min / flags=support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=55.0 / exec=38.0 / wait=43.2 / R=1.30
- 20260518_140500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=71.0 / exec=18.0 / wait=67.2 / R=1.30
- 20260518_130500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=62.0 / exec=31.0 / wait=54.4 / R=1.30
- 20260518_110500: sl_hit / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=61.0 / exec=16.0 / wait=70.4 / R=-1.00
- 20260518_050500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / dir=82.0 / exec=15.0 / wait=72.0 / R=-1.00
- 20260518_010500: missed_opportunity / side=short / setup=confidence_below_min / flags=support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=62.0 / exec=22.0 / wait=68.8 / R=1.30
- 20260518_000500: missed_opportunity / side=short / setup=confidence_below_min / flags=support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=60.0 / exec=35.0 / wait=48.0 / R=1.30

## 次に触る候補
- src/trade/opportunity_gate.py
- src/trade/paper_position.py
- src/analysis/market_map.py
- tools/log_feedback.py
