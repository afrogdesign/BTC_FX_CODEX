# market_map 有効性レポート

- 対象 shadow 行数: 216 / 全体 1633
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-22
- market_map 記録あり: 212件
- primary_state: early_down=78件, confirmed_down=76件, confirmed_up=25件, early_up=20件, near_major_resistance=12件, near_major_support=1件
- market_map_flags: short_into_major_support=180件, long_into_major_resistance=175件, support_to_resistance_flip=129件, support_to_resistance_retest_confirmed=128件, major_resistance_rejection=83件, trend_flip_early_down=78件, trend_flip_confirmed_down=76件, resistance_to_support_flip=61件, resistance_to_support_retest_confirmed=61件, major_support_rejection=58件
- level_flip_state: support_to_resistance_confirmed=128件, resistance_to_support_confirmed=61件, support_to_resistance_early=1件
- failed_breakout_state: down_reversal=50件, up_reversal=29件
- trend_flip_state: early_down=78件, confirmed_down=76件, confirmed_up=25件, early_up=20件

## flag別成績
- short_into_major_support: 勝率=56.4%, wrong_rate=10.6%, 平均MFE24h=5.87, 平均MAE24h=5.90 (n=180)
  代表例: 20260521_180500, 20260521_170500, 20260521_160501, 20260521_150501, 20260521_140500
- long_into_major_resistance: 勝率=49.1%, wrong_rate=9.7%, 平均MFE24h=5.41, 平均MAE24h=6.58 (n=175)
  代表例: 20260521_180500, 20260521_170500, 20260521_160501, 20260521_150501, 20260521_140500
- support_to_resistance_flip: 勝率=63.2%, wrong_rate=10.9%, 平均MFE24h=7.11, 平均MAE24h=4.92 (n=129)
  代表例: 20260521_180500, 20260521_170500, 20260521_160501, 20260521_150501, 20260521_140500
- trend_flip_confirmed_down: 勝率=52.2%, wrong_rate=14.5%, 平均MFE24h=7.18, 平均MAE24h=5.43 (n=76)
  代表例: 20260521_160501, 20260521_150501, 20260521_140500, 20260521_070500, 20260520_150500
- resistance_to_support_flip: 勝率=39.1%, wrong_rate=11.5%, 平均MFE24h=3.15, 平均MAE24h=8.80 (n=61)
  代表例: 20260521_130500, 20260521_080500, 20260521_040500, 20260521_010500, 20260520_200500
- failed_breakout_down_reversal: 勝率=38.5%, wrong_rate=6.0%, 平均MFE24h=7.14, 平均MAE24h=5.25 (n=50)
  代表例: 20260521_180500, 20260521_160501, 20260521_120500, 20260520_160500, 20260520_150500
- failed_breakout_up_reversal: 勝率=41.7%, wrong_rate=24.1%, 平均MFE24h=4.34, 平均MAE24h=7.55 (n=29)
  代表例: 20260521_100500, 20260521_070500, 20260521_060500, 20260520_120500, 20260520_020500
- trend_flip_confirmed_up: 勝率=38.5%, wrong_rate=24.0%, 平均MFE24h=2.18, 平均MAE24h=11.04 (n=25)
  代表例: 20260521_130500, 20260521_040500, 20260520_200500, 20260520_080500, 20260520_070500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
