# market_map 有効性レポート

- 対象 shadow 行数: 168 / 全体 1585
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-20
- market_map 記録あり: 164件
- primary_state: confirmed_down=65件, early_down=53件, confirmed_up=18件, early_up=16件, near_major_resistance=11件, near_major_support=1件
- market_map_flags: short_into_major_support=138件, long_into_major_resistance=129件, support_to_resistance_flip=94件, support_to_resistance_retest_confirmed=94件, major_resistance_rejection=66件, trend_flip_confirmed_down=65件, trend_flip_early_down=53件, resistance_to_support_flip=50件, resistance_to_support_retest_confirmed=50件, major_support_rejection=48件
- level_flip_state: support_to_resistance_confirmed=94件, resistance_to_support_confirmed=50件
- failed_breakout_state: down_reversal=40件, up_reversal=24件
- trend_flip_state: confirmed_down=65件, early_down=53件, confirmed_up=18件, early_up=16件

## flag別成績
- short_into_major_support: 勝率=61.9%, wrong_rate=10.9%, 平均MFE24h=6.40, 平均MAE24h=5.95 (n=138)
  代表例: 20260519_180500, 20260519_170500, 20260519_160500, 20260519_140500, 20260519_130500
- long_into_major_resistance: 勝率=55.3%, wrong_rate=10.9%, 平均MFE24h=5.89, 平均MAE24h=6.91 (n=129)
  代表例: 20260519_180500, 20260519_170500, 20260519_140500, 20260519_130500, 20260519_120500
- support_to_resistance_flip: 勝率=71.4%, wrong_rate=11.7%, 平均MFE24h=8.15, 平均MAE24h=4.89 (n=94)
  代表例: 20260519_160500, 20260519_150500, 20260519_120500, 20260519_100500, 20260519_040500
- trend_flip_confirmed_down: 勝率=61.1%, wrong_rate=13.8%, 平均MFE24h=8.07, 平均MAE24h=5.05 (n=65)
  代表例: 20260519_170500, 20260519_160500, 20260519_150500, 20260519_120500, 20260519_030500
- resistance_to_support_flip: 勝率=41.2%, wrong_rate=12.0%, 平均MFE24h=3.10, 平均MAE24h=9.20 (n=50)
  代表例: 20260519_180500, 20260519_170500, 20260519_140500, 20260519_130500, 20260519_110500
- failed_breakout_down_reversal: 勝率=36.4%, wrong_rate=7.5%, 平均MFE24h=7.16, 平均MAE24h=4.94 (n=40)
  代表例: 20260519_170500, 20260519_090500, 20260519_080500, 20260519_070500, 20260519_040500
- failed_breakout_up_reversal: 勝率=50.0%, wrong_rate=25.0%, 平均MFE24h=4.45, 平均MAE24h=7.91 (n=24)
  代表例: 20260519_150500, 20260518_030500, 20260517_230500, 20260517_010500, 20260516_140500
- trend_flip_confirmed_up: 勝率=44.4%, wrong_rate=33.3%, 平均MFE24h=1.57, 平均MAE24h=13.60 (n=18)
  代表例: 20260518_230500, 20260518_220500, 20260517_180500, 20260517_100500, 20260516_020500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
